# -*- coding: utf-8 -*-
"""I-78 출구 판별의 검정력 보강 — 레버 C(결과변수 품질 배터리) (K-3 power-rescue 2/2)

[왜] 레버 B(I-77) 실패: 표본 이득 +9.9%, MDE 8.16pp 미개선. 원인 가설 ②(결과변수 조도)로 이동:
exit6 이진은 acqui-hire·구제 매각과 성공 출구를 합산 → 신호가 노이즈에 희석. 품질별로 분해하면
각 결과의 기저율 대비 상대 SESOI 로 판별 가능(레버 11: 결과대상 배터리). 레버는 이것 하나만.
[설계] I-75 표본(2010–2017-10)·섹터 셀·공동 투자사 부트 500 유지. 결과 배터리:
  y1 ipo6      = IPO 72m (최고 품질 출구)
  y2 acqp6     = 가격 공시 인수 72m (acqui-hire 부분 배제)
  y3 exit_ever = 데이터 종점(2023-10)까지 출구 (지평 연장 — 연도는 셀이 흡수)
  y4 closed6   = 폐업 72m (하방 결과 — 호의라면 fp 선택 ff 딜의 폐업률이 높아야 함)
  SESOI(결과별) = ff 표본 기저율의 25% (상대 문턱; 하방 y4 는 +25%).
[사전 예측] (결과 전, 2026-09-03)
  P1 4개 결과 중 ≥3개에서 물질적 열위(기저율의 25%) 를 CI 로 배제.
  P2 y4 폐업: gap_ff 상한 < 기저율의 +25% (호의의 하방 예측 배제).
  P3 어떤 결과에서도 유의한 물질적 열위 미검출 (검출되면 그것도 발견 — 호의 방향 증거로 기록).
[판정] (사전 등록) GO = P1·P2 충족 (출구 판별 "호의 배제"가 배터리 수준에서 성립) 또는
  유의한 물질적 열위 검출(호의 방향 — 부호 반전 발견). 그 외 PARTIAL: 출구 판별은 최종적으로
  "판별 불능(MDE 병기)"로 원고에 남기고, 후속 마진 판별(I-75)로 논문 성립.
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
EQ_EXCL = {"grant", "debt_financing", "post_ipo_debt", "post_ipo_equity", "non_equity_assistance"}

people = CTX.people[["uuid", "gender"]]
g_map = people[people["gender"].isin(["male", "female"])].set_index("uuid")["gender"]

rounds = CTX.rounds.dropna(subset=["announced_on", "org_uuid"]).copy()
rounds = rounds[~rounds["investment_type"].isin(EQ_EXCL)]
rounds["dt"] = pd.to_datetime(rounds["announced_on"], errors="coerce")
rounds = rounds.dropna(subset=["dt"])
rounds = rounds[(rounds["dt"] >= "2010-01-01") & (rounds["dt"] <= "2023-10-31")]

jobs = CTX.jobs
fj = jobs[jobs["title"].fillna("").str.lower().str.contains("founder", regex=False)][
    ["person_uuid", "org_uuid"]].dropna()
fj["fg"] = fj["person_uuid"].map(g_map)
fj = fj[fj["fg"].notna()]
org_ff = (fj["fg"] == "female").groupby(fj["org_uuid"]).max()
orgs = CTX.orgs
topcat = dict(zip(orgs["uuid"], orgs["category_groups_list"].fillna("NA").str.split(",").str[0].str.strip()))
closed_map = pd.to_datetime(
    orgs.dropna(subset=["closed_on"]).set_index("uuid")["closed_on"], errors="coerce")

pt = CTX.partners.dropna(subset=["funding_round_uuid", "investor_uuid", "partner_uuid"])
d = pt.merge(rounds[["uuid", "org_uuid", "dt"]], left_on="funding_round_uuid", right_on="uuid")
d["pg"] = d["partner_uuid"].map(g_map)
d["ff"] = d["org_uuid"].map(org_ff)
d = d[d["pg"].notna() & d["ff"].notna()].copy()
d["fp"] = (d["pg"] == "female").astype(float)
d["ff"] = d["ff"].astype(float)
d["year"] = d["dt"].dt.year.astype(str)
d["cell"] = d["investor_uuid"] + "|" + d["year"] + "|" + d["org_uuid"].map(topcat).fillna("NA")

acq = CTX.acq.dropna(subset=["acquiree_uuid", "acquired_on"]).copy()
acq["adt"] = pd.to_datetime(acq["acquired_on"], errors="coerce")
acq["priced"] = pd.to_numeric(acq["price_usd"], errors="coerce") > 0
first_acq_p = acq[acq["priced"]].groupby("acquiree_uuid")["adt"].min()
ip = CTX.ipos.dropna(subset=["org_uuid", "went_public_on"]).copy()
ip["idt"] = pd.to_datetime(ip["went_public_on"], errors="coerce")
first_ipo = ip.groupby("org_uuid")["idt"].min()
exit_any = pd.concat([acq.groupby("acquiree_uuid")["adt"].min(), first_ipo], axis=1).min(axis=1)

d["ipo_dt"] = d["org_uuid"].map(first_ipo)
d["acqp_dt"] = d["org_uuid"].map(first_acq_p)
d["exit_dt"] = d["org_uuid"].map(exit_any)
d["cl_dt"] = d["org_uuid"].map(closed_map)
d["ipo6"] = ((d["ipo_dt"] - d["dt"]).dt.days <= 365 * 6).fillna(False).astype(float)
d["acqp6"] = ((d["acqp_dt"] - d["dt"]).dt.days <= 365 * 6).fillna(False).astype(float)
d["exit_ever"] = d["exit_dt"].notna().astype(float)
d["closed6"] = ((d["cl_dt"] - d["dt"]).dt.days <= 365 * 6).fillna(False).astype(float)
d = d[d["dt"] <= "2017-10-31"]


def gap_ff(df, y, nb=NB):
    dd = df[df["ff"] == 1.0][[y, "fp", "cell", "investor_uuid"]].reset_index(drop=True)
    yr = (dd[y] - dd[y].groupby(dd["cell"]).transform("mean")).to_numpy()
    xr = (dd["fp"] - dd["fp"].groupby(dd["cell"]).transform("mean")).to_numpy()
    sxx = (xr * xr).sum()
    beta = float((xr * yr).sum() / sxx) if sxx else float("nan")
    grp = {c: g.index.to_numpy() for c, g in dd.groupby("investor_uuid")}
    keys = list(grp)
    bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(keys), len(keys))
        rows_ = np.concatenate([grp[keys[i]] for i in pick])
        x2, y2 = xr[rows_], yr[rows_]
        s = (x2 * x2).sum()
        if s:
            bs.append((x2 * y2).sum() / s)
    base = float(dd[y].mean())
    se = float(np.nanstd(np.asarray(bs, float)))
    return beta, qci(bs), base, 2.8 * se


out, excl_cnt, sig_deficit = {}, 0, []
for y, downside in (("ipo6", False), ("acqp6", False), ("exit_ever", False), ("closed6", True)):
    b, ci, base, mde = gap_ff(d, y)
    sesoi = 0.25 * base
    if downside:
        excluded = (not np.isnan(ci[1])) and (ci[1] < sesoi)      # 폐업 +25% 배제
        deficit = (not np.isnan(ci[0])) and (ci[0] > 0) and (b >= sesoi)
    else:
        excluded = (not np.isnan(ci[0])) and (ci[0] > -sesoi)     # 열위 −25% 배제
        deficit = (not np.isnan(ci[1])) and (ci[1] < 0) and (-b >= sesoi)
    if excluded:
        excl_cnt += 1
    if deficit:
        sig_deficit.append(y)
    out[y] = {"gap_ff": round(b, 4), "ci": ci, "base_ff": round(base, 4),
              "sesoi": round(sesoi, 4), "mde80_pp": round(mde * 100, 2),
              "material_deficit_excluded": bool(excluded)}

p1 = excl_cnt >= 3
p2 = out["closed6"]["material_deficit_excluded"]
status = "GO" if ((p1 and p2) or sig_deficit) else "PARTIAL"
verdict = ("; ".join(f"{y} gap_ff={v['gap_ff']:+.4f} {v['ci']} (기저 {v['base_ff']:.3f}, "
                     f"SESOI ±{v['sesoi']:.3f}, {'배제' if v['material_deficit_excluded'] else '미배제'})"
                     for y, v in out.items())
           + (f" — 유의 열위 검출: {sig_deficit} (호의 방향)" if sig_deficit
              else (" — 배터리 수준 호의 배제 성립" if (p1 and p2)
                    else " — 판별 불능 지속: 출구는 MDE 병기로 원고 기록, 후속 마진으로 성립")))

emit("I-78", "출구 판별 결과변수 품질 배터리 (K-3 power-rescue 레버 C)", status,
     {**out, "n_ff_deals": int((d["ff"] == 1).sum()),
      "excluded_count": excl_cnt, "sig_deficit": sig_deficit},
     prediction="≥3/4 결과에서 상대 25% 열위 배제; 폐업 +25% 배제; 유의 열위 미검출",
     verdict=verdict, kill_met=False, n=int((d["ff"] == 1).sum()),
     extra={"stage": 2, "feeds": "RESULTS_LEDGER_K3.md §4 레버 C", "slug": "exit_battery"})
print("done")
