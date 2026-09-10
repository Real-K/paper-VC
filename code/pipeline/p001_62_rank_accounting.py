# -*- coding: utf-8 -*-
"""p001_62 — 트랙레코드 평가의 회계와 벤치마크 불확실성 (c1 §4 · c2 §3·§5 · c3 §5): 같은 파트너 표본·같은 성과기간에서
 raw = component + adjusted 의 성별 차 분해, 성별별 평균 순위(조정 전후), 고정 horizon(36m·72m) 순위 이동, 벤치마크 3단(연·연+단계·연+섹터+단계)별 순위 이동,
 벤치마크 재계산 부트, 고유 라운드 벤치마크, 회사 제외 벤치마크.

[왜] Table 7A 의 +4.43 은 sample-end exit 기반이고 P001-05 부트는 벤치마크를 고정한 채 파트너를 재표집한다. 리뷰어는 (i) 수준 항등식 raw−adj = component 를 공통 표본에서 성별 차로 보여주고
 (ii) 순위 결과가 고정 horizon 에서도 유지되는지 (iii) 순위 CI 가 벤치마크 추정 불확실성을 포함하는지 (iv) 같은 라운드가 여러 번 귀속될 때 벤치마크 가중치 문제(고유 라운드 벤치마크)를 요구했다.
[구성] sample_v2 NA+EU. 파트너 = 딜 ≥5 (기준 표본: dt ≤ 2017-10, 성과 = exit_ever; P001-05 와 동일). 벤치마크 = 시장 셀(연×섹터×단계) 평균(P001-05 정의; 전체 평균 — LOO 아님, P001-05 재현).
  A 회계: 성별 평균 raw·component·adjusted (수준) 과 차이, 파트너 재표집 500. 성별별 평균 raw/adj 백분위와 이동.
  B 벤치마크 단계: 연 / 연+단계 / 연+섹터+단계 벤치마크 각각의 여성 평균 백분위 이동(sample-end).
  C 고정 horizon: exit3 (dt ≤ 2020-10; 딜 ≥5) · exit6 (dt ≤ 2017-10) 로 순위 이동 재계산(3단 벤치마크).
  D 벤치마크 불확실성: (D1) 고정 벤치마크·파트너 재표집(P001-05 방식) vs (D2) 재표집마다 벤치마크(셀 평균)·순위를 다시 계산(딜은 파트너 단위로 재표집되고 셀 평균은 재표집 딜로 계산).
  E 벤치마크 가중치: (E1) 고유 라운드 기준 셀 평균(같은 라운드의 다중 귀속 행을 하나로) (E2) 회사 제외(leave-company-out) 셀 평균.
[사전 예측] (2026-09-10, 결과 조회 전)
  A: 여성−남성 raw 차 ∈ [−0.06, −0.02]; component 차 ∈ [−0.05, −0.02]; adjusted 차 ∈ [−0.03, +0.01]; 여성 평균 raw 백분위 < 남성, 조정 후 차이 축소(이동 +3~+5점).
  B: 연 벤치마크만으로 이동의 절반 이상. C: exit3 기준 이동 ∈ [+1, +5]; exit6 ∈ [+2, +5]. D2 CI 폭은 D1 의 1.0–1.5배. E1·E2 이동은 기준 ±1점 안.
[판정] 진단 — status OK.
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

rng = np.random.default_rng(20260962)
NB = 500
MIN_DEALS = 5
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR", "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}
d0 = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v2.parquet")); d0["dt"] = pd.to_datetime(d0["dt"]); d0 = d0[d0["country_code"].isin(EU | {"USA", "CAN"})].copy()
acq = CTX.acq.dropna(subset=["acquiree_uuid", "acquired_on"]); ip = CTX.ipos.dropna(subset=["org_uuid", "went_public_on"])
fe = pd.concat([pd.to_datetime(acq["acquired_on"], errors="coerce").groupby(acq["acquiree_uuid"]).min(), pd.to_datetime(ip["went_public_on"], errors="coerce").groupby(ip["org_uuid"]).min()], axis=1).min(axis=1)
d0["exit_dt"] = d0["org_uuid"].map(fe); days = (d0["exit_dt"] - d0["dt"]).dt.days
d0["exit3"] = (days <= 365 * 3).fillna(False).astype(float)
d0["c_y"] = d0["year"]; d0["c_ys"] = d0["year"] + "|" + d0["stage"]; d0["c_yss"] = d0["year"] + "|" + d0["cat"] + "|" + d0["stage"]
OUT = {}


def partners(df, y, cell="c_yss", bench=None):
    """파트너 패널: raw·adj(=y − 벤치마크)·component. bench: 'full'(셀 평균, P001-05) | 'unique_round' | 'leave_company'."""
    df = df.copy()
    if bench in (None, "full"):
        b = df.groupby(cell)[y].transform("mean")
    elif bench == "unique_round":
        u = df.drop_duplicates(["funding_round_uuid", cell]).groupby(cell)[y].mean(); b = df[cell].map(u)
    elif bench == "leave_company":
        s = df.groupby(cell)[y].transform("sum"); n = df.groupby(cell)[y].transform("size")
        cs = df.groupby([cell, "org_uuid"])[y].transform("sum"); cn = df.groupby([cell, "org_uuid"])[y].transform("size")
        b = ((s - cs) / (n - cn)).where(n > cn)
    df["resid"] = df[y] - b; df = df.dropna(subset=["resid"])
    P = df.groupby("partner_uuid").agg(raw=(y, "mean"), adj=("resid", "mean"), n=(y, "size"), fp=("fp", "first")).reset_index()
    P = P[P["n"] >= MIN_DEALS].reset_index(drop=True); P["comp"] = P["raw"] - P["adj"]; return P


def pct(P):
    return P["raw"].rank(pct=True) * 100, P["adj"].rank(pct=True) * 100


def shift(P):
    r, a = pct(P); f = P["fp"] == 1
    return {"female_raw_pct": float(r[f].mean()), "female_adj_pct": float(a[f].mean()), "male_raw_pct": float(r[~f].mean()), "male_adj_pct": float(a[~f].mean()),
            "female_shift": float(a[f].mean() - r[f].mean()), "male_shift": float(a[~f].mean() - r[~f].mean()),
            "gap_raw": float(P.loc[f, "raw"].mean() - P.loc[~f, "raw"].mean()), "gap_comp": float(P.loc[f, "comp"].mean() - P.loc[~f, "comp"].mean()), "gap_adj": float(P.loc[f, "adj"].mean() - P.loc[~f, "adj"].mean())}


def boot_partners(P, nb=NB):
    keys = ["female_shift", "male_shift", "gap_raw", "gap_comp", "gap_adj", "female_raw_pct", "female_adj_pct", "male_raw_pct", "male_adj_pct"]
    bs = {k: [] for k in keys}
    for _ in range(nb):
        s = P.iloc[rng.integers(0, len(P), len(P))].reset_index(drop=True); v = shift(s)
        for k in keys: bs[k].append(v[k])
    pt = shift(P); return {k: {"coef": round(pt[k], 4), "ci95": [round(x, 4) for x in qci(bs[k])]} for k in keys} | {"n_partners": int(len(P)), "n_female": int((P["fp"] == 1).sum())}


# ── A. 회계 · 성별별 평균 순위 (기준 표본: ≤2017-10, exit_ever, 연×섹터×단계) ──────────────────────────────────────────────────
base = d0[d0["dt"] <= "2017-10-31"]
PA = partners(base, "exit_ever"); OUT["A_accounting_sample_end"] = boot_partners(PA)
A = OUT["A_accounting_sample_end"]
print(f"[A] n {A['n_partners']:,} (여 {A['n_female']}) · gap raw {A['gap_raw']['coef']:+.4f} = comp {A['gap_comp']['coef']:+.4f} + adj {A['gap_adj']['coef']:+.4f} · 여성 pct {A['female_raw_pct']['coef']:.1f} → {A['female_adj_pct']['coef']:.1f} (이동 {A['female_shift']['coef']:+.2f} [{A['female_shift']['ci95'][0]:+.2f},{A['female_shift']['ci95'][1]:+.2f}]) · 남성 {A['male_raw_pct']['coef']:.1f} → {A['male_adj_pct']['coef']:.1f}", flush=True)
OUT["A_identity_check_max_abs"] = round(float(np.abs(PA["raw"] - PA["comp"] - PA["adj"]).max()), 12)

# ── B. 벤치마크 3단 (sample-end) ──────────────────────────────────────────────────────────────────────────────────────────────
OUT["B_benchmark_levels_sample_end"] = {}
for lab, cell in (("year", "c_y"), ("year_stage", "c_ys"), ("year_sector_stage", "c_yss")):
    OUT["B_benchmark_levels_sample_end"][lab] = boot_partners(partners(base, "exit_ever", cell=cell), nb=300)
    v = OUT["B_benchmark_levels_sample_end"][lab]; print(f"[B] {lab:<18} 여성 이동 {v['female_shift']['coef']:+.2f} [{v['female_shift']['ci95'][0]:+.2f},{v['female_shift']['ci95'][1]:+.2f}] · comp gap {v['gap_comp']['coef']:+.4f}", flush=True)

# ── C. 고정 horizon ──────────────────────────────────────────────────────────────────────────────────────────────────────────
OUT["C_fixed_horizon"] = {}
for lab, y, end in (("exit3_deals_to_2020_10", "exit3", "2020-10-31"), ("exit6_deals_to_2017_10", "exit6", "2017-10-31")):
    sub = d0[d0["dt"] <= end]; OUT["C_fixed_horizon"][lab] = {}
    for cl, cell in (("year", "c_y"), ("year_stage", "c_ys"), ("year_sector_stage", "c_yss")):
        OUT["C_fixed_horizon"][lab][cl] = boot_partners(partners(sub, y, cell=cell), nb=300)
    v = OUT["C_fixed_horizon"][lab]["year_sector_stage"]; print(f"[C] {lab:<24} 여성 이동 {v['female_shift']['coef']:+.2f} [{v['female_shift']['ci95'][0]:+.2f},{v['female_shift']['ci95'][1]:+.2f}] (n {v['n_partners']:,}) · raw gap {v['gap_raw']['coef']:+.4f} · adj gap {v['gap_adj']['coef']:+.4f}", flush=True)

# ── D. 벤치마크 불확실성: 고정(D1) vs 재계산(D2) ──────────────────────────────────────────────────────────────────────────────
D1 = A["female_shift"]
pids = base["partner_uuid"].unique(); idx = {p: g.index.to_numpy() for p, g in base.groupby("partner_uuid")}
bs2 = []
for _ in range(NB):
    pick = pids[rng.integers(0, len(pids), len(pids))]; s = base.loc[np.concatenate([idx[p] for p in pick])]
    s = s.copy(); s["partner_uuid"] = np.repeat(np.arange(len(pick)), [len(idx[p]) for p in pick])   # resampled partners are distinct units
    Pb = partners(s, "exit_ever")
    if (Pb["fp"] == 1).sum() >= 20: bs2.append(shift(Pb)["female_shift"])
OUT["D_benchmark_uncertainty"] = {"D1_fixed_benchmark_partner_resampling": D1, "D2_benchmark_recomputed_each_replication": {"coef": D1["coef"], "ci95": [round(x, 4) for x in qci(bs2)], "nb": len(bs2)},
                                  "width_ratio_D2_over_D1": round((qci(bs2)[1] - qci(bs2)[0]) / (D1["ci95"][1] - D1["ci95"][0]), 3)}
print(f"[D] 고정 벤치마크 [{D1['ci95'][0]:+.2f},{D1['ci95'][1]:+.2f}] vs 재계산 [{qci(bs2)[0]:+.2f},{qci(bs2)[1]:+.2f}] (폭 비 {OUT['D_benchmark_uncertainty']['width_ratio_D2_over_D1']})", flush=True)

# ── E. 벤치마크 가중치 변형 ──────────────────────────────────────────────────────────────────────────────────────────────────
OUT["E_benchmark_variants"] = {"unique_round": boot_partners(partners(base, "exit_ever", bench="unique_round"), nb=300), "leave_company_out": boot_partners(partners(base, "exit_ever", bench="leave_company"), nb=300)}
for k, v in OUT["E_benchmark_variants"].items(): print(f"[E] {k:<18} 여성 이동 {v['female_shift']['coef']:+.2f} [{v['female_shift']['ci95'][0]:+.2f},{v['female_shift']['ci95'][1]:+.2f}] (n {v['n_partners']:,})", flush=True)
# 다중 귀속 라운드의 벤치마크 가중치: 같은 라운드가 셀 평균에 몇 번 들어가나
mult = base.groupby(["c_yss", "funding_round_uuid"]).size(); OUT["E_rows_per_round_in_cells"] = {"share_rounds_multiply_attributed": round(float((mult > 1).mean()), 4), "mean_rows_per_round": round(float(mult.mean()), 3)}

# ── 판정 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
C3 = OUT["C_fixed_horizon"]["exit3_deals_to_2020_10"]["year_sector_stage"]["female_shift"]; C6 = OUT["C_fixed_horizon"]["exit6_deals_to_2017_10"]["year_sector_stage"]["female_shift"]
Bv = OUT["B_benchmark_levels_sample_end"]
pred = {"A_gap_raw_in_[-6,-2]": -0.06 <= A["gap_raw"]["coef"] <= -0.02, "A_gap_comp_in_[-5,-2]": -0.05 <= A["gap_comp"]["coef"] <= -0.02, "A_gap_adj_in_[-3,1]": -0.03 <= A["gap_adj"]["coef"] <= 0.01,
        "A_shift_in_[3,5]": 3 <= A["female_shift"]["coef"] <= 5, "B_year_ge_half": Bv["year"]["female_shift"]["coef"] >= 0.5 * Bv["year_sector_stage"]["female_shift"]["coef"],
        "C_exit3_in_[1,5]": 1 <= C3["coef"] <= 5, "C_exit6_in_[2,5]": 2 <= C6["coef"] <= 5, "D_width_ratio_1_to_1.5": 1.0 <= OUT["D_benchmark_uncertainty"]["width_ratio_D2_over_D1"] <= 1.5,
        "E_within_1pt": all(abs(v["female_shift"]["coef"] - A["female_shift"]["coef"]) <= 1 for v in OUT["E_benchmark_variants"].values())}
pred = {k: bool(v) for k, v in pred.items()}; OUT["prediction_check"] = pred
verdict = (f"회계(n {A['n_partners']:,}): raw gap {A['gap_raw']['coef']*100:+.2f}pp = comp {A['gap_comp']['coef']*100:+.2f} + adj {A['gap_adj']['coef']*100:+.2f}; 여성 백분위 {A['female_raw_pct']['coef']:.1f}→{A['female_adj_pct']['coef']:.1f} ({A['female_shift']['coef']:+.2f} [{A['female_shift']['ci95'][0]:+.2f},{A['female_shift']['ci95'][1]:+.2f}]) · "
           f"벤치마크 3단 이동 {Bv['year']['female_shift']['coef']:+.2f}/{Bv['year_stage']['female_shift']['coef']:+.2f}/{Bv['year_sector_stage']['female_shift']['coef']:+.2f} · 고정 horizon exit3 {C3['coef']:+.2f} [{C3['ci95'][0]:+.2f},{C3['ci95'][1]:+.2f}] · exit6 {C6['coef']:+.2f} [{C6['ci95'][0]:+.2f},{C6['ci95'][1]:+.2f}] · "
           f"벤치마크 재계산 CI 폭 비 {OUT['D_benchmark_uncertainty']['width_ratio_D2_over_D1']} · 고유 라운드 {OUT['E_benchmark_variants']['unique_round']['female_shift']['coef']:+.2f} · 회사 제외 {OUT['E_benchmark_variants']['leave_company_out']['female_shift']['coef']:+.2f} (예측 적중 {sum(pred.values())}/{len(pred)})")
emit("P001-62", "트랙레코드 회계(raw = component + adjusted, 성별 차)·성별별 평균 순위·벤치마크 3단·고정 horizon 순위 이동·벤치마크 재계산 부트·고유 라운드/회사 제외 벤치마크", "OK", OUT,
     prediction="gap raw∈[−6,−2]pp; comp∈[−5,−2]; adj∈[−3,+1]; 이동 +3~+5; 연 벤치마크 ≥ 절반; exit3 이동 [1,5]; exit6 [2,5]; 재계산 폭비 1–1.5; 변형 ±1점", verdict=verdict, kill_met=False, n=int(A["n_partners"]),
     extra={"stage": 8, "feeds": "Table 7 (v9) · Figure 2 (rank change) · §3", "slug": "rank_accounting", "builds_on": "P001-05/36", "rng_seed": 20260962, "sample": "sample_v2"})
print("done")
