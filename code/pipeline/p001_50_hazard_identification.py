# -*- coding: utf-8 -*-
"""p001_50 — Table 4 해저드의 식별 변이 점검: 셀×경과년 안에서 공동귀속(단일 라운드) 비중·결과 변이·희석, 다중 라운드 셀만의 해저드 격차

[왜] P001-49 는 Table 3 셀 내 추정량의 혼합 셀 65–87% 가 같은 라운드의 공동귀속 쌍(결과 상수 → 희석)임을 보였다. Table 4 의 이산시간
 해저드는 같은 cell_stage 를 경과년(1..6)과 교차한 FE 를 쓰므로 구조를 상속한다. 원고는 "해저드가 정밀도를 진다" 고 쓰는데, 그 정밀도가
 교차 딜 비교에서 오는지 공동귀속 쌍의 분모 확장에서 오는지 점검한다. PI 지시(2026-09-09).

[구성] P001-12 의 해저드 패널을 그대로 복제(NAEU, ff==1, dt ≤ 2017-10; exit_dt 재구축; 경과년 t=1..6 위험집합; y=그 해 출구; cellt=cell_stage|t;
 공변량 X = log 조달액·기업연령·공동투자자 경험·log 투자자수(+결측 지표)·log1p 선행 라운드; 셀 내 demean 후 X 에 잔차화; 투자사 군집 부트).
 A 셀 분류: fp 변동 cellt 수 / 단일 라운드 cellt(공동귀속만) / 결과(yh) 변이>0 cellt / Σx̃²(공변량 잔차화 전·후) 중 단일 라운드 비중
 B 해저드 격차: 전체(P001-12 재현) · **다중 라운드 cellt 만** · 결과 변이>0 cellt 만(참고 — 결과 기반 선택이라 편향 가능) — 각 CI·MDE·±25% 등가 판정
[사전 예측] (2026-09-09, 결과 조회 전)
 A: fp 변동 cellt 600–900; 단일 라운드 비중 0.80–0.90; 결과 변이>0 cellt 5–12%; Σx̃² 희석 0.75–0.90.
 B: 전체 −0.24 [−0.81,+0.26] 재현(P001-12); 다중 라운드만 β ∈ [−1.5, +0.5] pp/yr, CI 반폭 ≥ 1.2 → ±25%(±1.55pp) 등가 **실패 예상**; MDE ≥ 2.
[판정] 감사 — status OK. 다중 라운드 셀에서 ±25% 등가가 유지되면 verdict 에 "정밀도는 교차 딜 비교에서 온다", 아니면 "Table 4 의 경계는 희석 추정량의 경계".
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["HARNESS_OUT"] = os.environ.get("P001_OUT", os.path.join(HERE, "out"))  # set P001_* / CRUNCHBASE_RAW to your local copies (licensed inputs; see DATA_ACCESS.md)
sys.path.insert(0, HERE)  # gates.py / emit_contract.py sit alongside in code/pipeline
from emit_contract import emit, qci, sha16  # noqa: E402
from gates import CTX  # noqa: E402

rng = np.random.default_rng(20260950)
NB = 300
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR", "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}
NAEU = EU | {"USA", "CAN"}
OUT = {}

# ── P001-12 패널 복제 ────────────────────────────────────────────────────────
d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v1.parquet"))
d = d[d["country_code"].isin(NAEU)].copy(); d["dt"] = pd.to_datetime(d["dt"])
r = CTX.rounds[["uuid", "raised_amount_usd", "investor_count", "org_uuid", "announced_on"]].copy(); r["rdt"] = pd.to_datetime(r["announced_on"], errors="coerce")
d = d.merge(r[["uuid", "raised_amount_usd", "investor_count"]], left_on="funding_round_uuid", right_on="uuid", how="left", suffixes=("", "_r"))
orgs = CTX.orgs[["uuid", "founded_on"]].copy(); orgs["fy"] = pd.to_datetime(orgs["founded_on"], errors="coerce").dt.year
d["age"] = (d["dt"].dt.year - d["org_uuid"].map(orgs.set_index("uuid")["fy"])).clip(0, 50)
ro = r.dropna(subset=["org_uuid", "rdt"]).sort_values(["org_uuid", "rdt"]); org_dates = {o: g["rdt"].to_numpy() for o, g in ro.groupby("org_uuid")}
d["prior"] = [np.searchsorted(org_dates.get(o, np.array([], dtype="datetime64[ns]")), np.datetime64(t)) for o, t in zip(d["org_uuid"], d["dt"])]
inv = CTX.inv.dropna(subset=["funding_round_uuid", "investor_uuid"]); icnt = inv.groupby("investor_uuid").size()
ie = inv.copy(); ie["lc"] = np.log1p(ie["investor_uuid"].map(icnt)); rs = ie.groupby("funding_round_uuid")["lc"].agg(["sum", "count"])
d = d.merge(rs, left_on="funding_round_uuid", right_index=True, how="left")
own_lc = np.log1p(d["investor_uuid"].map(icnt).fillna(0)); d["coexp"] = np.where(d["count"] > 1, (d["sum"] - own_lc) / (d["count"] - 1), np.nan)
d["x_amt"] = np.log1p(pd.to_numeric(d["raised_amount_usd"], errors="coerce")); d["x_ic"] = np.log1p(pd.to_numeric(d["investor_count"], errors="coerce"))
COVS = []
for c in ("x_amt", "age", "coexp", "x_ic"):
    d[c + "_m"] = d[c].isna().astype(float); d[c] = d[c].fillna(0); COVS += [c, c + "_m"]
d["x_prior"] = np.log1p(d["prior"]); COVS.append("x_prior")
dff = d[d["ff"] == 1.0]
acq = CTX.acq.dropna(subset=["acquiree_uuid", "acquired_on"]).copy(); acq["adt"] = pd.to_datetime(acq["acquired_on"], errors="coerce")
ip = CTX.ipos.dropna(subset=["org_uuid", "went_public_on"]).copy(); ip["idt"] = pd.to_datetime(ip["went_public_on"], errors="coerce")
exit_dt = pd.concat([acq.groupby("acquiree_uuid")["adt"].min(), ip.groupby("org_uuid")["idt"].min()], axis=1).min(axis=1)
h = dff[dff["dt"] <= "2017-10-31"].copy().reset_index(drop=True)
h["edt"] = h["org_uuid"].map(exit_dt); h["eyr"] = ((h["edt"] - h["dt"]).dt.days / 365.25)
rows = []
for t in range(1, 7):
    sub = h[(h["eyr"].isna()) | (h["eyr"] > t - 1)].copy()
    sub["yh"] = ((sub["eyr"] > t - 1) & (sub["eyr"] <= t)).fillna(False).astype(float)
    sub["cellt"] = sub["cell_stage"] + "|t" + str(t); sub["t"] = t
    rows.append(sub[["yh", "fp", "cellt", "investor_uuid", "funding_round_uuid", "t"] + COVS])
H = pd.concat(rows, ignore_index=True)
base = float(H["yh"].mean())


def est(sub, cell="cellt", use_cov=True):
    g = sub[cell]
    yv = sub["yh"] - sub["yh"].groupby(g).transform("mean"); xv = sub["fp"] - sub["fp"].groupby(g).transform("mean")
    if use_cov:
        Z = np.column_stack([(sub[c] - sub[c].groupby(g).transform("mean")).to_numpy() for c in COVS])
        b, *_ = np.linalg.lstsq(Z, xv.to_numpy(), rcond=None); xv = xv.to_numpy() - Z @ b
        b2, *_ = np.linalg.lstsq(Z, yv.to_numpy(), rcond=None); yv = yv.to_numpy() - Z @ b2
    else:
        xv, yv = xv.to_numpy(), yv.to_numpy()
    sxx = float((xv * xv).sum()); return float((xv * yv).sum() / sxx) if sxx > 0 else np.nan


def boot(df, nb=NB, use_cov=True):
    dd = df.reset_index(drop=True); b0 = est(dd, use_cov=use_cov)
    grp = {c: g.index.to_numpy() for c, g in dd.groupby("investor_uuid")}; keys = list(grp); bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(keys), len(keys)); sub = dd.loc[np.concatenate([grp[keys[i]] for i in pick])].reset_index(drop=True)
        v = est(sub, use_cov=use_cov)
        if np.isfinite(v): bs.append(v)
    lo, hi = qci(bs); se = float(np.std(bs, ddof=1))
    return {"coef_pp": round(b0 * 100, 3), "ci95_pp": [round(lo * 100, 3), round(hi * 100, 3)], "mde80_pp": round(2.8 * se * 100, 3), "n_rows": int(len(dd)), "n_cells": int(dd["cellt"].nunique()),
            "within_quarter_of_base": bool(lo > -0.25 * base and hi < 0.25 * base)}


# ── A. 셀 분류 ──────────────────────────────────────────────────────────────
g = H.groupby("cellt").agg(fp_mean=("fp", "mean"), n=("fp", "size"), n_rounds=("funding_round_uuid", "nunique"), y_var=("yh", "var"))
g["y_var"] = g["y_var"].fillna(0)
mixed = g.index[(g["fp_mean"] > 0) & (g["fp_mean"] < 1)]
gm = g.loc[mixed]
single = set(gm.index[gm["n_rounds"] == 1]); multi = set(gm.index[gm["n_rounds"] >= 2]); varpos = set(gm.index[gm["y_var"] > 0])
Hm = H[H["cellt"].isin(mixed)].copy()
xr2 = (Hm["fp"] - Hm.groupby("cellt")["fp"].transform("mean")) ** 2
A = {"n_rows_panel": int(len(H)), "n_cells_panel": int(len(g)), "base_hazard": round(base, 4), "n_mixed_cells": int(len(mixed)), "n_rows_mixed": int(len(Hm)),
     "n_single_round_cells": len(single), "share_single_round_cells": round(len(single) / max(len(mixed), 1), 4), "n_multi_round_cells": len(multi), "n_rows_multi": int(Hm["cellt"].isin(multi).sum()),
     "n_cells_outcome_var_pos": len(varpos), "share_cells_outcome_var_pos": round(len(varpos) / max(len(mixed), 1), 4), "n_rows_outcome_var_pos": int(Hm["cellt"].isin(varpos).sum()),
     "dilution_share_sxx_single_round": round(float(xr2[Hm["cellt"].isin(single)].sum() / xr2.sum()), 4),
     "n_exit_events_mixed": int(Hm["yh"].sum()), "n_exit_events_varpos": int(Hm.loc[Hm["cellt"].isin(varpos), "yh"].sum())}
print(f"[A] 패널 {A['n_rows_panel']:,} 행 · cellt {A['n_cells_panel']:,} · fp 변동 셀 {A['n_mixed_cells']:,} ({A['n_rows_mixed']:,} 행) · 단일 라운드 {A['n_single_round_cells']:,} ({A['share_single_round_cells']:.2f}) · "
      f"결과 변이>0 {A['n_cells_outcome_var_pos']} ({A['share_cells_outcome_var_pos']:.2f}; {A['n_rows_outcome_var_pos']} 행, 출구 사건 {A['n_exit_events_varpos']}) · Σx̃² 희석 {A['dilution_share_sxx_single_round']:.2f} · 기저 {base*100:.2f}%/yr", flush=True)
OUT["A_cells"] = A

# ── B. 해저드 격차 ──────────────────────────────────────────────────────────
B = {"full": boot(H)}
B["multi_round_cells"] = boot(H[H["cellt"].isin(multi)]) if len(multi) >= 8 else None
B["outcome_var_cells_reference"] = boot(H[H["cellt"].isin(varpos)]) if len(varpos) >= 8 else None
B["full_unadj"] = boot(H, nb=200, use_cov=False)
for k, v in B.items():
    if v: print(f"  {k:<28} β {v['coef_pp']:+.3f} pp/yr [{v['ci95_pp'][0]:+.3f},{v['ci95_pp'][1]:+.3f}] MDE {v['mde80_pp']:.3f} · n {v['n_rows']:,}/{v['n_cells']:,} 셀 · ±25% 등가 {v['within_quarter_of_base']}", flush=True)
OUT["B_hazard_gap"] = B
OUT["quarter_of_base_pp"] = round(0.25 * base * 100, 3)

pred = {"A_mixed_600_900": 600 <= A["n_mixed_cells"] <= 900, "A_single_share_0.80_0.90": 0.80 <= A["share_single_round_cells"] <= 0.90,
        "A_varpos_share_0.05_0.12": 0.05 <= A["share_cells_outcome_var_pos"] <= 0.12, "A_dilution_0.75_0.90": 0.75 <= A["dilution_share_sxx_single_round"] <= 0.90,
        "B_full_reproduces_-0.24": abs(B["full"]["coef_pp"] - (-0.24)) < 0.05,
        "B_multi_in_[-1.5,0.5]": bool(B["multi_round_cells"] and -1.5 <= B["multi_round_cells"]["coef_pp"] <= 0.5),
        "B_multi_halfwidth_ge_1.2": bool(B["multi_round_cells"] and (B["multi_round_cells"]["ci95_pp"][1] - B["multi_round_cells"]["ci95_pp"][0]) / 2 >= 1.2),
        "B_multi_equiv_fails": bool(B["multi_round_cells"] and not B["multi_round_cells"]["within_quarter_of_base"])}
pred = {k: bool(v) for k, v in pred.items()}
OUT["prediction_check"] = pred
m = B["multi_round_cells"]
call = ("다중 라운드 셀에서도 ±25% 등가 유지 — 정밀도는 교차 딜 비교에서 온다" if (m and m["within_quarter_of_base"]) else
        "Table 4 의 ±25% 경계는 희석 추정량의 경계 — 교차 딜 셀만으로는 등가 미성립(MDE 병기)")
verdict = (f"해저드 패널 fp 변동 셀 {A['n_mixed_cells']:,} 중 단일 라운드(공동귀속) {A['share_single_round_cells']:.0%} · 결과 변이>0 {A['n_cells_outcome_var_pos']} ({A['share_cells_outcome_var_pos']:.0%}) · Σx̃² 희석 {A['dilution_share_sxx_single_round']:.0%} | "
           f"전체 {B['full']['coef_pp']:+.3f} [{B['full']['ci95_pp'][0]:+.2f},{B['full']['ci95_pp'][1]:+.2f}] (±25% {B['full']['within_quarter_of_base']}) → 다중 라운드 셀만 "
           f"{m['coef_pp'] if m else float('nan'):+.3f} [{m['ci95_pp'][0] if m else float('nan'):+.2f},{m['ci95_pp'][1] if m else float('nan'):+.2f}] MDE {m['mde80_pp'] if m else float('nan'):.2f} (±25%={OUT['quarter_of_base_pp']:.2f}pp; 등가 {m['within_quarter_of_base'] if m else None}) — {call} (예측 적중 {sum(pred.values())}/{len(pred)})")
emit("P001-50", "Table 4 해저드의 식별 변이: 공동귀속 셀 비중·결과 변이·희석, 다중 라운드 셀만의 해저드 격차", "OK", OUT,
     prediction="fp 변동 cellt 600–900; 단일 라운드 0.80–0.90; 결과 변이>0 5–12%; 희석 0.75–0.90; 전체 −0.24 재현; 다중 β∈[−1.5,0.5] 반폭≥1.2, ±25% 등가 실패",
     verdict=verdict, kill_met=False, n=int(len(H)),
     extra={"stage": 7, "feeds": "§4 Table 4 분업 서술 · Table 9 Panel E", "slug": "hazard_identification", "builds_on": "P001-12/49", "p001_12_sha256_16": sha16(os.path.join(HERE, "p001_12_covadj_hazard.py"))})
print("done")
