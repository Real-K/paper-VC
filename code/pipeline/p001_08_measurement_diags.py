# -*- coding: utf-8 -*-
"""p001_08 측정 진단 (W4) — 귀속 선택(R2)·결측 선택(R4)·커버리지 드리프트·세분 스테이지 Becker

[위협→검정 매핑]
  R2 귀속 선택: investment_partners 기재 자체가 내생일 위협.
     검정 ① 회사 수준: 귀속률(회사 라운드 중 파트너 기재 비중) ~ 회사 여성 파트너 비중 상관.
     검정 ② 드리프트: 연도별 귀속률 × 귀속 파트너 여성 비중 경로 (커버리지×성별 상호작용).
     예상(위협 성립 시): 강한 양(+) 상관·여성 비중과 귀속률의 동행 추세.
  R4 결측 선택: 창업자 성별 판정가능(83%)이 비무작위일 위협.
     검정: 판정가능 vs 불능 딜의 특성 비교 (연도·초기단계 비중·US 비중·투자사 규모).
     예상(위협 성립 시): 큰 격차 (예: 판정불능이 특정 연도·지역 집중).
  I-81 플래그: Becker(초기딜 fp 성과 fon −1.6 [−3.6,+0.005])가 초기 내 미세 단계 구성일 위협.
     검정: 초기 딜 내 정확 스테이지 셀(투자사×연도×섹터×investment_type)로 재추정.
     예상(구성이면): 0 으로 수렴. 잔존하면 초기딜 내 실재 격차로 기록.
[사전 예측] (결과 전, 2026-09-03)
  P1 귀속률~여성비중 상관 |r| < 0.10 (귀속이 성별 중립).
  P2 판정가능/불능 특성 차: 초기단계 비중 차 < 10pp, US 비중 차 < 15pp (문서화 수준).
  P3 세분 스테이지 후 Becker fon 이 0 방향 수렴 (|계수| 축소).
[판정] P1~P3 → 측정 위협 완화로 기록 (GO). 실패 항목은 claim ceiling 반영 + negative_results.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["HARNESS_OUT"] = os.environ.get("P001_OUT", os.path.join(HERE, "out"))  # set P001_* / CRUNCHBASE_RAW to your local copies (licensed inputs; see DATA_ACCESS.md)
sys.path.insert(0, HERE)  # gates.py / emit_contract.py sit alongside in code/pipeline
from emit_contract import emit, qci  # noqa: E402
from gates import CTX  # noqa: E402

rng = np.random.default_rng(42)
NB = 400
EQ_EXCL = {"grant", "debt_financing", "post_ipo_debt", "post_ipo_equity", "non_equity_assistance"}
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR",
      "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}
NAEU = EU | {"USA", "CAN"}
EARLY = {"seed", "angel", "pre_seed", "equity_crowdfunding", "convertible_note"}

d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v1.parquet"))
d["dt"] = pd.to_datetime(d["dt"])
dn = d[d["country_code"].isin(NAEU)].copy()

# R2① 회사 수준 귀속률 ~ 여성 파트너 비중
rounds = CTX.rounds.dropna(subset=["announced_on", "org_uuid"]).copy()
rounds = rounds[~rounds["investment_type"].isin(EQ_EXCL)]
rounds = rounds[(rounds["announced_on"] >= "2010-01-01") & (rounds["announced_on"] <= "2023-10-31")]
inv = CTX.inv.dropna(subset=["funding_round_uuid", "investor_uuid"])
inv = inv[inv["funding_round_uuid"].isin(set(rounds["uuid"]))]
tot = inv.groupby("investor_uuid")["funding_round_uuid"].nunique().rename("n_rounds")
att = d.groupby("investor_uuid")["funding_round_uuid"].nunique().rename("n_attr")
fshare = d.groupby("investor_uuid")["fp"].mean().rename("fp_share")
F = pd.concat([tot, att, fshare], axis=1).dropna()
F = F[F["n_rounds"] >= 10]
F["attr_rate"] = (F["n_attr"] / F["n_rounds"]).clip(upper=1)
r2_corr = float(F["attr_rate"].corr(F["fp_share"]))
bs = [float(F.sample(len(F), replace=True, random_state=None).pipe(
      lambda s: s["attr_rate"].corr(s["fp_share"]))) for _ in range(300)]
ci_r2 = qci(bs)

# R2② 드리프트: 연도별 귀속률·여성 비중
yr_attr = {}
rounds["yr"] = rounds["announced_on"].str[:4]
inv_y = inv.merge(rounds[["uuid", "yr"]], left_on="funding_round_uuid", right_on="uuid")
tot_y = inv_y.groupby("yr")["funding_round_uuid"].nunique()
att_y = d.groupby(d["year"])["funding_round_uuid"].nunique()
fp_y = d.groupby(d["year"])["fp"].mean()
for y in sorted(set(tot_y.index) & set(att_y.index)):
    yr_attr[y] = [round(float(att_y[y] / tot_y[y]), 3), round(float(fp_y.get(y, np.nan)), 3)]
drift = np.corrcoef([v[0] for v in yr_attr.values()], [v[1] for v in yr_attr.values()])[0, 1]

# R4 결측 선택: 판정가능 vs 불능 (전체 귀속 딜 기준 — sample_v1 은 판정가능만이라 cores 재구성)
pt = CTX.partners.dropna(subset=["funding_round_uuid", "investor_uuid", "partner_uuid"])
rd = pt.merge(CTX.rounds.dropna(subset=["announced_on", "org_uuid"])[
    ["uuid", "org_uuid", "announced_on", "country_code", "investment_type"]],
    left_on="funding_round_uuid", right_on="uuid")
rd = rd[~rd["investment_type"].isin(EQ_EXCL)]
rd = rd[(rd["announced_on"] >= "2010-01-01") & (rd["announced_on"] <= "2023-10-31")]
det = set(d["org_uuid"])
rd["determinable"] = rd["org_uuid"].isin(det)
rd["early"] = rd["investment_type"].isin(EARLY)
rd["us"] = rd["country_code"] == "USA"
rd["yr"] = rd["announced_on"].str[:4].astype(int)
cmp = rd.groupby("determinable").agg(early=("early", "mean"), us=("us", "mean"),
                                     yr=("yr", "mean"), n=("uuid", "size"))
r4 = {"early_diff_pp": round(float(cmp.loc[True, "early"] - cmp.loc[False, "early"]) * 100, 1),
      "us_diff_pp": round(float(cmp.loc[True, "us"] - cmp.loc[False, "us"]) * 100, 1),
      "year_diff": round(float(cmp.loc[True, "yr"] - cmp.loc[False, "yr"]), 2),
      "n_det": int(cmp.loc[True, "n"]), "n_undet": int(cmp.loc[False, "n"])}

# 세분 스테이지 Becker 재검 (초기 딜, 정확 investment_type 셀)
de = dn[dn["stage"].isin(EARLY) & (dn["dt"] <= "2020-10-31")].copy()
dd = de[["fon", "fp", "cell_stage", "investor_uuid"]].reset_index(drop=True)
yr_ = (dd["fon"] - dd["fon"].groupby(dd["cell_stage"]).transform("mean")).to_numpy()
xr_ = (dd["fp"] - dd["fp"].groupby(dd["cell_stage"]).transform("mean")).to_numpy()
b_bk = float((xr_ * yr_).sum() / (xr_ * xr_).sum())
g_ = {c: g.index.to_numpy() for c, g in dd.groupby("investor_uuid")}
keys = list(g_)
bsb = []
for _ in range(NB):
    pick = rng.integers(0, len(keys), len(keys))
    rows_ = np.concatenate([g_[keys[i]] for i in pick])
    x2, y2 = xr_[rows_], yr_[rows_]
    s = (x2 * x2).sum()
    if s:
        bsb.append((x2 * y2).sum() / s)
ci_bk = qci(bsb)

p1 = abs(r2_corr) < 0.10
p2 = (abs(r4["early_diff_pp"]) < 10) and (abs(r4["us_diff_pp"]) < 15)
p3 = abs(b_bk) < 0.016  # I-81 의 −1.6pp 대비 축소
status = "GO" if (p1 and p2) else "PARTIAL"
verdict = (f"R2 귀속률~여성비중 r={r2_corr:+.3f} {ci_r2} ({'중립' if p1 else '상관 존재 — ceiling 반영'}); "
           f"드리프트 상관 {drift:+.2f}; R4 판정가능−불능: 초기 {r4['early_diff_pp']:+.1f}pp·"
           f"US {r4['us_diff_pp']:+.1f}pp·연도 {r4['year_diff']:+.2f} ({'허용' if p2 else '선택 존재'}); "
           f"세분 Becker fon={b_bk:+.4f} {ci_bk} ({'0 수렴 — 구성 확인' if p3 else '잔존 — 초기딜 내 실재 격차로 기록'})")

emit("P001-08", "측정 진단 — 귀속 선택·결측 선택·드리프트·세분 Becker (W4)", status,
     {"r2_attr_fp_corr": [round(r2_corr, 3), ci_r2, int(len(F))],
      "attr_rate_by_year": yr_attr, "drift_corr": round(float(drift), 3),
      "r4_missingness": r4,
      "becker_fon_finestage": [round(b_bk, 4), ci_bk, int(len(dd))],
      "p1_attr_neutral": bool(p1), "p2_missing_ok": bool(p2), "p3_becker_converge": bool(p3)},
     prediction="|r|<0.10; 초기 차<10pp·US 차<15pp; 세분 셀에서 Becker 0 수렴",
     verdict=verdict, kill_met=False, n=int(len(F)),
     extra={"stage": 4, "feeds": "ROBUSTNESS_MATRIX.md / THREATS R2·R4", "slug": "measurement_diags",
            "inputs": "sample_v1 + cores_v1(전체 라운드 분모)"})
print("done")
