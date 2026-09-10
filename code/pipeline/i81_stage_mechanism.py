# -*- coding: utf-8 -*-
"""I-81 스테이지 skew 의 메커니즘 배터리 — 창업자 경로·연차·커리어 동학·Becker 검정 (P001 2막)

[왜] I-80: 여성 파트너 딜의 초기단계 비중 +3.84pp [2.60, 5.00] (투자사×연도 셀). 이것이
(M-A) 창업자 경로의 부산물인지, (M-B) 연차·코호트인지, (M-C 배정 vs M-D 선호)의 잔여인지 분해.
POSITIONING_NOTE 3막 구조의 2막 — 어느 결과가 나와도 기록하고, M-C/M-D 는 직접 분리 불가를
전제로 Becker 한방향 검정(제약이면 밀어넣어진 구간에서 양의 선택 → 성과 우위)까지만 간다.
[데이터] papers/P001_gender_screening/05_data/sample_v2.parquet (정본) + 연차 프록시는
cores_v1 partners×rounds 전체 이력(2010 이전 포함)의 (파트너,투자사)별 첫 귀속 시점 — 혼합 입력 명시.
[설계]
  G0 기술: 남녀 파트너의 연차 분포 (평균·중위).
  M-A 검정: β(early ~ fp | 투자사×연도), ff=0 딜만 / ff=1 딜만 / 전체(재현).
  M-B 검정: 셀 = 투자사×연도×연차빈(0-2,2-5,5-10,10+). 감쇠율 = 1 − β_tenure/β_base.
  동학: 파트너×투자사 demean 후 early ~ 연차(년) 기울기, 남녀 별도 + 차이 (파트너 군집 부트).
  Becker: 초기단계 딜 전체(창업자 성별 불문)에서 β(fon36 ~ fp | 투자사×연도×대분류)
          및 β(exit_ever ~ fp | 동일). fon 은 dt ≤ 2020-10, exit_ever 는 dt ≤ 2017-10.
[사전 예측] (결과 전, 2026-09-03)
  P1 M-A: ff=0 딜에서도 β ≥ +2pp CI 0 배제 (창업자 경로만으로는 설명 안 됨).
  P2 M-B: 여성 파트너 평균 연차가 1~3년 짧음; 연차 셀 후 β 는 30~60% 감쇠하되 CI 0 배제 유지.
  P3 동학: 남녀 졸업 기울기(연차→후기 이동) 차이의 CI 가 0 포함(코호트 정합) —
     여성이 유의하게 평평하면 정체(배정/선호 잔존) 증거.
  P4 Becker: 초기단계 fp 성과 ≥ 0; fon +2pp 이상 CI 배제면 제약(배정) 방향의 한방향 증거.
[판정] (사전 등록)
  ff=0 β CI 0 포함 → M-A 가 1차 설명 (스토리: 매칭의 부산물) — GO(서사 단순화).
  연차 감쇠 >70% 그리고 잔여 CI 0 포함 → M-B 가 1차 설명 (스토리: 파이프라인/코호트) — GO.
  둘 다 아니면 잔여 스타일 실재 — Becker 부호로 방향 증거만 기록, "결정 주체 판별 불가" 명시 — GO.
  (이 배터리에 KILL 없음 — 어느 가지도 3막을 무너뜨리지 않는다. 전 결과 원장 기록.)
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emit_contract import emit, qci  # noqa: E402
from gates import CTX  # noqa: E402

rng = np.random.default_rng(42)
NB = 500
EARLY = {"seed", "angel", "pre_seed", "equity_crowdfunding", "convertible_note"}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE = os.environ.get("P001_SAMPLE", "/path/to/sample_v2.parquet")
if not os.path.exists(SAMPLE):
    SAMPLE = os.path.abspath(os.environ.get("P001_SAMPLE", "/path/to/sample_v2.parquet"))

d = pd.read_parquet(SAMPLE)
d["early"] = d["stage"].isin(EARLY).astype(float)
d["dt"] = pd.to_datetime(d["dt"])

# 연차 프록시: 전체 이력(2010 이전 포함) 첫 귀속
pt = CTX.partners.dropna(subset=["funding_round_uuid", "investor_uuid", "partner_uuid"])
rr = CTX.rounds.dropna(subset=["announced_on"])[["uuid", "announced_on"]].copy()
rr["rdt"] = pd.to_datetime(rr["announced_on"], errors="coerce")
pa = pt.merge(rr, left_on="funding_round_uuid", right_on="uuid")
first_attr = pa.groupby(["partner_uuid", "investor_uuid"])["rdt"].min().rename("fa")
d = d.merge(first_attr, left_on=["partner_uuid", "investor_uuid"], right_index=True, how="left")
d["tenure"] = ((d["dt"] - d["fa"]).dt.days / 365.25).clip(lower=0)
d["tbin"] = pd.cut(d["tenure"], [-0.01, 2, 5, 10, 99], labels=["t0_2", "t2_5", "t5_10", "t10p"]).astype(str)
d["cell_t"] = d["cell0"] + "|" + d["tbin"]

ten_f = float(d.loc[d["fp"] == 1, "tenure"].mean())
ten_m = float(d.loc[d["fp"] == 0, "tenure"].mean())


def fwl(df, y, x, cell, cl, nb=NB):
    dd = df[[y, x, cell, cl]].reset_index(drop=True)
    yr = (dd[y] - dd[y].groupby(dd[cell]).transform("mean")).to_numpy()
    xr = (dd[x] - dd[x].groupby(dd[cell]).transform("mean")).to_numpy()
    sxx = (xr * xr).sum()
    if sxx == 0 or len(dd) < 500:
        return float("nan"), [float("nan")] * 2, int(len(dd))
    beta = float((xr * yr).sum() / sxx)
    grp = {c: g.index.to_numpy() for c, g in dd.groupby(cl)}
    keys = list(grp)
    bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(keys), len(keys))
        rows_ = np.concatenate([grp[keys[i]] for i in pick])
        x2, y2 = xr[rows_], yr[rows_]
        s = (x2 * x2).sum()
        if s:
            bs.append((x2 * y2).sum() / s)
    return beta, qci(bs), int(len(dd))


# 기준 + M-A + M-B
b0, ci0, n0 = fwl(d, "early", "fp", "cell0", "investor_uuid")
bA0, ciA0, nA0 = fwl(d[d["ff"] == 0], "early", "fp", "cell0", "investor_uuid")
bA1, ciA1, nA1 = fwl(d[d["ff"] == 1], "early", "fp", "cell0", "investor_uuid")
bB, ciB, nB = fwl(d, "early", "fp", "cell_t", "investor_uuid")
atten = 1 - bB / b0 if b0 else float("nan")

# 동학: 파트너×투자사 demean, early ~ tenure 기울기 남녀 (군집 = 파트너)
d["pgrp"] = d["partner_uuid"] + "|" + d["investor_uuid"]


def slope(df, nb=NB):
    dd = df[["early", "tenure", "pgrp", "partner_uuid"]].dropna().reset_index(drop=True)
    yr = (dd["early"] - dd["early"].groupby(dd["pgrp"]).transform("mean")).to_numpy()
    xr = (dd["tenure"] - dd["tenure"].groupby(dd["pgrp"]).transform("mean")).to_numpy()
    sxx = (xr * xr).sum()
    if sxx == 0 or len(dd) < 500:
        return float("nan"), [], 0
    beta = float((xr * yr).sum() / sxx)
    grp = {c: g.index.to_numpy() for c, g in dd.groupby("partner_uuid")}
    keys = list(grp)
    bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(keys), len(keys))
        rows_ = np.concatenate([grp[keys[i]] for i in pick])
        x2, y2 = xr[rows_], yr[rows_]
        s = (x2 * x2).sum()
        if s:
            bs.append((x2 * y2).sum() / s)
    return beta, bs, int(len(dd))


sf, bsf, nf = slope(d[d["fp"] == 1])
sm, bsm, nm = slope(d[d["fp"] == 0])
m = min(len(bsf), len(bsm)) if bsf and bsm else 0
sd = sf - sm if not (np.isnan(sf) or np.isnan(sm)) else float("nan")
cisd = qci(np.array(bsf[:m]) - np.array(bsm[:m])) if m >= 50 else [float("nan")] * 2

# Becker: 초기단계 딜 전체 성과
de = d[d["early"] == 1].copy()
de["cell_c"] = de["cell0"] + "|" + de["cat"]
bF, ciF, nFo = fwl(de[de["dt"] <= "2020-10-31"], "fon", "fp", "cell_c", "investor_uuid")
bE, ciE, nEx = fwl(de[de["dt"] <= "2017-10-31"], "exit_ever", "fp", "cell_c", "investor_uuid")

ma_primary = (not np.isnan(ciA0[0])) and (ciA0[0] <= 0 <= ciA0[1])
mb_primary = (not np.isnan(atten)) and (atten > 0.70) and (ciB[0] <= 0 <= ciB[1])
stuck = (not np.isnan(cisd[0])) and (cisd[0] > 0)  # 여성 기울기가 유의하게 덜 음(=졸업 느림)
becker_pos = (not np.isnan(ciF[0])) and (ciF[0] > 0.02)
if ma_primary:
    branch = "M-A 창업자 경로가 1차 설명"
elif mb_primary:
    branch = "M-B 연차·코호트가 1차 설명"
else:
    branch = ("잔여 스타일 실재 — " + ("졸업 정체(배정/선호 잔존) + " if stuck else "졸업 속도 남녀 유사 + ")
              + ("Becker 성과우위 → 제약(배정) 방향 증거" if becker_pos else "Becker 미검출 → 방향 미결"))
verdict = (f"기준 β={b0:+.4f} {ci0}; M-A ff=0 β={bA0:+.4f} {ciA0} (n={nA0})·ff=1 β={bA1:+.4f} {ciA1}; "
           f"M-B 연차셀 β={bB:+.4f} {ciB} (감쇠 {atten*100:.0f}%; 연차 여 {ten_f:.1f} vs 남 {ten_m:.1f}년); "
           f"동학 기울기 여 {sf:+.5f} vs 남 {sm:+.5f}, 차 {sd:+.5f} {cisd}; "
           f"Becker(초기딜) fon={bF:+.4f} {ciF}·exit_ever={bE:+.4f} {ciE} — {branch}")

emit("I-81", "스테이지 skew 메커니즘 배터리 — 창업자 경로·연차·동학·Becker (P001 2막)", "GO",
     {"base": [round(b0, 4), ci0, n0],
      "ma_ff0": [round(bA0, 4), ciA0, nA0], "ma_ff1": [round(bA1, 4), ciA1, nA1],
      "mb_tenurecell": [round(bB, 4), ciB, nB], "mb_attenuation": round(float(atten), 3),
      "tenure_mean_f": round(ten_f, 2), "tenure_mean_m": round(ten_m, 2),
      "slope_f": [None if np.isnan(sf) else round(sf, 5), nf],
      "slope_m": [None if np.isnan(sm) else round(sm, 5), nm],
      "slope_diff": [None if np.isnan(sd) else round(sd, 5), cisd],
      "becker_fon": [round(bF, 4), ciF, nFo], "becker_exit": [round(bE, 4), ciE, nEx],
      "branch": branch},
     prediction="ff=0 β≥+2pp 배제; 연차 감쇠 30~60% 후 잔존; 기울기 차 CI 0 포함; Becker fon ≥0",
     verdict=verdict, kill_met=False, n=n0,
     extra={"stage": 2, "feeds": "P001 2막 (POSITIONING_NOTE)", "slug": "stage_mechanism",
            "inputs": "sample_v2.parquet + cores_v1 first_attr(연차)"})
print("done")
