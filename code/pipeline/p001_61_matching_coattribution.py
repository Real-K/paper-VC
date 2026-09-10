# -*- coding: utf-8 -*-
"""p001_61 — Table 2 의 비교정보 진단: 매칭 사다리(firm×year → +sector → +stage)에 공동 귀속 분해와 공통 support 재추정을 적용 (c1 §3 · c2 §2 · c3 §10-3)

[왜] Table 4 의 논리(공동 귀속 쌍은 결과가 같아 분모에만 기여 → β_all = (1−d)·β_multi)는 Table 2 에도 적용된다: 같은 라운드의 공동 귀속 파트너는 founder gender 도 공유한다.
 현재 6.96 → 3.21 → 0.66pp 의 감소는 (i) 같은 행에서 구성을 더 세밀히 고려한 몫 (ii) 비교집합(혼합 셀·가중치)의 변화 몫을 섞어 담는다. 리뷰어 세 명이 모두 이 분리를 최우선 추가분석으로 꼽았다.
[구성] 표본: sample_v2 NA+EU 전 딜 (y = ff, x = fp). 셀 3단(cell0, cell_cat, cell_stage). 각 단에서:
  β_all(원 표본; P001-02 재현) · 혼합 셀 수 · 혼합 셀의 고유 라운드 수 · 단일 라운드 셀 수와 그 Σx̃² 비중 d · β_multi(다중 라운드 셀만) · (1−d)·β_multi 항등식 확인.
  공통 support = cell_stage 가 혼합인 행. 그 위에서 cell0·cell_cat·cell_stage 세 단을 재추정(β_cs) — 관측치는 같지만 셀이 넓어지면 고정효과 추정량의 암묵적 가중치는 달라진다(순수 구성 분해가 아님).
  부트: 투자사 군집 500 (같은 추첨을 세 단에 공유 → 단 간 차이의 구간).
[사전 예측] (2026-09-10, 결과 조회 전)
  d 는 셀이 세밀할수록 커진다: cell0 < 0.30, cell_cat 0.3–0.5, cell_stage 0.5–0.8. β_multi 는 β_all 보다 크다(부호 유지). 공통 support 위 사다리(β_cs)는 원 사다리보다 완만: cell0→cell_stage 감소가 원 감소(6.3pp)의 절반 이하.
[판정] 진단 — status OK. "90.5% 가 구성" 문장은 이 결과와 함께 specification-dependent 로 서술(원고는 이미 그렇게 씀).
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["HARNESS_OUT"] = os.environ.get("P001_OUT", os.path.join(HERE, "out"))  # set P001_* / CRUNCHBASE_RAW to your local copies (licensed inputs; see DATA_ACCESS.md)
sys.path.insert(0, HERE)  # gates.py / emit_contract.py sit alongside in code/pipeline
from emit_contract import emit, qci  # noqa: E402

rng = np.random.default_rng(20260961)
NB = 500
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR", "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}
d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v2.parquet"))
d = d[d["country_code"].isin(EU | {"USA", "CAN"})].reset_index(drop=True)
CELLS = [("L0_invyear", "cell0"), ("L1_pluscat", "cell_cat"), ("L2_plusstage", "cell_stage")]


def diag(df, cell):
    """혼합 셀·라운드 수·d(단일 라운드 셀의 Σx̃² 비중)·β_all·β_multi."""
    g = df.groupby(cell)["fp"].agg(["min", "max"]); mixed = g.index[(g["min"] == 0) & (g["max"] == 1)]
    m = df[df[cell].isin(mixed)].copy()
    xr = m["fp"] - m.groupby(cell)["fp"].transform("mean"); yr = m["ff"] - m.groupby(cell)["ff"].transform("mean")
    sxx = float((xr * xr).sum()); beta_all = float((xr * yr).sum() / sxx)
    nr = m.groupby(cell)["funding_round_uuid"].nunique(); single = set(nr.index[nr == 1])
    is_single = m[cell].isin(single).to_numpy()
    dshare = float((xr.to_numpy()[is_single] ** 2).sum() / sxx)
    mm = m[~is_single]; xm = mm["fp"] - mm.groupby(cell)["fp"].transform("mean"); ym = mm["ff"] - mm.groupby(cell)["ff"].transform("mean")
    sm = float((xm * xm).sum()); beta_multi = float((xm * ym).sum() / sm) if sm > 0 else float("nan")
    return {"n_rows_mixed": int(len(m)), "n_mixed_cells": int(len(mixed)), "n_unique_rounds_mixed": int(m["funding_round_uuid"].nunique()), "n_single_round_cells": int(len(single)),
            "share_single_round_cells": round(len(single) / len(mixed), 4), "d_share_sxx_single_round": round(dshare, 4), "beta_all_pp": round(beta_all * 100, 3), "beta_multi_pp": round(beta_multi * 100, 3),
            "identity_check_pp": round((1 - dshare) * beta_multi * 100, 3), "n_multi_round_cells": int(len(mixed) - len(single)), "n_rows_multi": int(len(mm))}


def fwl_beta(df, cell):
    xr = (df["fp"] - df.groupby(cell)["fp"].transform("mean")).to_numpy(); yr = (df["ff"] - df.groupby(cell)["ff"].transform("mean")).to_numpy()
    s = float((xr * xr).sum()); return float((xr * yr).sum() / s) if s > 0 else np.nan


def boot_ladder(df, cells, nb=NB):
    """세 단을 같은 투자사 재표집으로 추정 → 단별 CI 와 단 간 차이 CI."""
    grp = {c: g.index.to_numpy() for c, g in df.groupby("investor_uuid")}; keys = list(grp); draws = {c: [] for _, c in cells}
    for _ in range(nb):
        pick = rng.integers(0, len(keys), len(keys)); rows_ = np.concatenate([grp[keys[i]] for i in pick]); s = df.loc[rows_]
        for _, c in cells: draws[c].append(fwl_beta(s, c))
    out = {}
    for name, c in cells:
        b = fwl_beta(df, c); arr = np.array(draws[c]); arr = arr[np.isfinite(arr)]
        out[name] = {"coef_pp": round(b * 100, 3), "ci95_pp": [round(x * 100, 3) for x in qci(arr)], "n": int(len(df))}
    d0, d2 = np.array(draws["cell0"]), np.array(draws["cell_stage"]); ok = np.isfinite(d0) & np.isfinite(d2)
    out["drop_L0_to_L2_pp"] = {"coef_pp": round((fwl_beta(df, "cell0") - fwl_beta(df, "cell_stage")) * 100, 3), "ci95_pp": [round(x * 100, 3) for x in qci(d0[ok] - d2[ok])]}
    return out


OUT = {"A_diagnostics_by_cell": {name: diag(d, c) for name, c in CELLS}}
for k, v in OUT["A_diagnostics_by_cell"].items(): print(f"  {k:<14} rows {v['n_rows_mixed']:>7,} · mixed cells {v['n_mixed_cells']:>6,} · unique rounds {v['n_unique_rounds_mixed']:>6,} · single-round cells {v['share_single_round_cells']:.2f} · d {v['d_share_sxx_single_round']:.3f} · β_all {v['beta_all_pp']:+.2f} · β_multi {v['beta_multi_pp']:+.2f} · (1−d)β_multi {v['identity_check_pp']:+.2f}", flush=True)
OUT["B_original_ladder"] = boot_ladder(d, CELLS)
g = d.groupby("cell_stage")["fp"].agg(["min", "max"]); mixed_fine = g.index[(g["min"] == 0) & (g["max"] == 1)]
cs = d[d["cell_stage"].isin(mixed_fine)].reset_index(drop=True)
OUT["C_common_support_ladder"] = boot_ladder(cs, CELLS); OUT["C_common_support_ladder"]["support"] = {"rows": int(len(cs)), "share_of_rows": round(len(cs) / len(d), 4), "cells_stage_mixed": int(len(mixed_fine)), "unique_rounds": int(cs["funding_round_uuid"].nunique()), "unique_companies": int(cs["org_uuid"].nunique())}
OUT["C_common_support_ladder"]["multi_round_only"] = {name: diag(cs, c) for name, c in CELLS}
for lab, blk in (("original", OUT["B_original_ladder"]), ("common support", OUT["C_common_support_ladder"])):
    print(f"  {lab:<15} " + " → ".join(f"{blk[n]['coef_pp']:+.2f} [{blk[n]['ci95_pp'][0]:+.2f},{blk[n]['ci95_pp'][1]:+.2f}]" for n, _ in CELLS) + f" · drop L0→L2 {blk['drop_L0_to_L2_pp']['coef_pp']:+.2f} [{blk['drop_L0_to_L2_pp']['ci95_pp'][0]:+.2f},{blk['drop_L0_to_L2_pp']['ci95_pp'][1]:+.2f}]", flush=True)
A = OUT["A_diagnostics_by_cell"]; B = OUT["B_original_ladder"]; C = OUT["C_common_support_ladder"]
pred = {"d_increases": A["L0_invyear"]["d_share_sxx_single_round"] < A["L1_pluscat"]["d_share_sxx_single_round"] < A["L2_plusstage"]["d_share_sxx_single_round"],
        "d_ranges": A["L0_invyear"]["d_share_sxx_single_round"] < 0.30 and 0.3 <= A["L1_pluscat"]["d_share_sxx_single_round"] <= 0.5 and 0.5 <= A["L2_plusstage"]["d_share_sxx_single_round"] <= 0.8,
        "beta_multi_gt_all_all_levels": all(abs(A[k]["beta_multi_pp"]) > abs(A[k]["beta_all_pp"]) for k in A),
        "common_support_drop_le_half": C["drop_L0_to_L2_pp"]["coef_pp"] <= 0.5 * B["drop_L0_to_L2_pp"]["coef_pp"]}
pred = {k: bool(v) for k, v in pred.items()}; OUT["prediction_check"] = pred
verdict = (f"d: {A['L0_invyear']['d_share_sxx_single_round']:.2f}/{A['L1_pluscat']['d_share_sxx_single_round']:.2f}/{A['L2_plusstage']['d_share_sxx_single_round']:.2f} · β_all {A['L0_invyear']['beta_all_pp']:+.2f}/{A['L1_pluscat']['beta_all_pp']:+.2f}/{A['L2_plusstage']['beta_all_pp']:+.2f} · β_multi {A['L0_invyear']['beta_multi_pp']:+.2f}/{A['L1_pluscat']['beta_multi_pp']:+.2f}/{A['L2_plusstage']['beta_multi_pp']:+.2f} | "
           f"공통 support({C['support']['rows']:,}행, {C['support']['share_of_rows']*100:.1f}%) 사다리 {C['L0_invyear']['coef_pp']:+.2f} → {C['L1_pluscat']['coef_pp']:+.2f} → {C['L2_plusstage']['coef_pp']:+.2f} (L0→L2 감소 {C['drop_L0_to_L2_pp']['coef_pp']:+.2f} vs 원 {B['drop_L0_to_L2_pp']['coef_pp']:+.2f}) — 예측 적중 {sum(pred.values())}/{len(pred)}")
emit("P001-61", "Table 2 비교정보 진단: 매칭 사다리의 공동 귀속 분해(d·β_multi)와 공통 support 재추정", "OK", OUT, prediction="d 단조 증가(<0.3, 0.3–0.5, 0.5–0.8); β_multi > β_all; 공통 support 감소 ≤ 원 감소의 절반",
     verdict=verdict, kill_met=False, n=int(len(d)), extra={"stage": 8, "feeds": "Table 2 Panel B · §3/§4 · Figure 1", "slug": "matching_coattribution", "builds_on": "P001-02/49", "rng_seed": 20260961, "sample": "sample_v2"})
print("done")
