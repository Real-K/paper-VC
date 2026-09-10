# -*- coding: utf-8 -*-
"""p001_56 — R5-5 (c)(d)(e): 라운드 내 재참여 설계 v2 — 리드 플래그 합집합·파트너 연공 통제·글로벌+24개월 창·전남성 위약 풀·재참여↔출구 보정

[왜] P001-51 은 ±5pp 밴드가 처치 정의에 의존함을 보였다. 설계 심판 R5-5: CB 안에서 남은 레버는 (a) 표본(글로벌·24개월 창: Σx̃² +24%) — 그래도 female-only
 MDE 6.5 → ≈5.8 로 밴드 밖일 것(설계의 천장 진술), (c) 리드 플래그를 `funding_rounds.lead_investor_uuids` 와 합집합으로 → 커버 58% → ≈90%(둘이 겹치는 곳
 일치 100%), (d) 라운드 내 파트너 연공 격차(여성 귀속 −1.7년)가 통제에 없다 → 추가; 전남성 FF 라운드 12,833 개에서 "하급 파트너 투자자" 가짜 처치로 연공이
 재참여를 얼마나 움직이는지 보정, (e) 재참여는 출구와 약하게만 연관(Δ 2–5pp; 혼성 라운드 안 ≈0) → 밴드는 "출구 대리" 가 아니라 "딜 고정 계속투자 결정" 진술.

[구성] P001-42/51 표본 구성 함수화(scope: NAEU/GLOBAL; 창 종점; 다음 라운드 지평). lead_u = is_lead_investor(있으면) else lead_investor_uuids 포함 여부.
 tenure = 귀속 파트너의 첫 귀속 딜(전 표본)부터 라운드까지 경과년의 최소값. 위약 풀 = 귀속 투자자 ≥2, 전부 남성 파트너, FF, 다음 라운드 지평 안: junior = 라운드 중위 연공 미만.
 회귀는 P001-51 ffreg 와 동일(y1 ~ fp + 통제, 라운드 내 demean, 기업 군집 부트 400).
[사전 예측] (2026-09-09, 결과 조회 전; 설계 심판 probe 의 n·커버리지는 알고 있음)
 (c) lead_u 커버 ≥ 0.88; 겹치는 곳 일치 ≥ 0.98; lead_u 라운드 내 fp 차(FF) ∈ [−0.08, +0.02], CI 0 포함.
 (d) 라운드 내 연공 격차 F−M ∈ [−2.5, −1.0]년(검출); 연공 통제 시 b(any-female) 이동 < 0.8pp; 위약: junior b ∈ [−4, 0]pp, CI 0 배제.
 (e) GLOBAL ≤2020-10/36m: FF 조건 라운드 580–610; GLOBAL ≤2021-10/24m: 640–690, female-only b ∈ [−4, +1]pp, MDE80 5.5–6.2 → 밴드 밖.
 보정: 혼성 라운드(≤2017-10)에서 P(재참여|출구) − P(재참여|비출구) ∈ [−0.02, +0.03]; 6.25pp 출구 격차의 함의 재참여 격차 |Δ| < 0.5pp.
[판정] 천장 진술 — status OK. female-only 가 어느 창에서도 ±5 안이면 "밴드 회복" 으로 보고(예측 위반이지만 GO 가 아님 — 정의 의존은 남음).
"""
import os

import numpy as np
import pandas as pd

from p001_v6_common import (CTX, CUT, HERE, RESCUE_SHA, V6_SHA, boot, emit, equity_rounds, exit_dates, investor_experience, investor_rows, load_sample, log,
                            org_maps, partner_gender_rows)

rng = np.random.default_rng(20260956)
NB = 400
OUT = {}
W0 = pd.Timestamp("2010-01-01")
lead_list = CTX.rounds.set_index("uuid")["lead_investor_uuids"] if "lead_investor_uuids" in CTX.rounds.columns else None
rdt_all = pd.to_datetime(CTX.rounds.set_index("uuid")["announced_on"], errors="coerce")
pt_all = partner_gender_rows(None)
pt_all["rdt"] = pt_all["funding_round_uuid"].map(rdt_all)
first_dt = pt_all.dropna(subset=["rdt"]).groupby("partner_uuid")["rdt"].min().to_dict()


def load_scope(scope):
    if scope == "NAEU":
        return load_sample()
    d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v1.parquet")); d["dt"] = pd.to_datetime(d["dt"]); return d


def build_sample(scope, window_end, horizon_days):
    d = load_scope(scope); om = org_maps(d); R = equity_rounds(set(d["org_uuid"]))
    R0 = R[(R["rdt"] >= W0) & (R["rdt"] <= window_end)].copy(); R0["ff"] = R0["org_uuid"].map(om["ff"])
    R0["nextH"] = ((R0["next_dt"] - R0["rdt"]).dt.days <= horizon_days).fillna(False).astype(float)
    I = investor_rows(R0["uuid"]); pt = partner_gender_rows(R0["uuid"])
    pa = pt.groupby(["funding_round_uuid", "investor_uuid"]).agg(fp=("fp", "max"), fp_min=("fp", "min"), partners=("partner_uuid", lambda s: frozenset(s))).reset_index()
    X = I.merge(pa, on=["funding_round_uuid", "investor_uuid"], how="inner").merge(R0[["uuid", "org_uuid", "rdt", "ff", "next_uuid", "nextH"]], left_on="funding_round_uuid", right_on="uuid")
    X = X.merge(investor_experience(), on=["funding_round_uuid", "investor_uuid"], how="left"); X["ln_exp"] = np.log1p(X["exp_before"].fillna(0))
    inv_next = investor_rows(set(R0["next_uuid"].dropna())).groupby("funding_round_uuid")["investor_uuid"].agg(set).to_dict()
    X["y1"] = [1.0 if (isinstance(nu, str) and inv in inv_next.get(nu, set())) else 0.0 for nu, inv in zip(X["next_uuid"], X["investor_uuid"])]
    X["lead_a"] = X["is_lead_investor"].map({True: 1.0, False: 0.0})
    if lead_list is not None:
        ll = X["funding_round_uuid"].map(lead_list)
        X["lead_b"] = [(1.0 if isinstance(l, str) and inv in l else (0.0 if isinstance(l, str) and len(l) > 0 else np.nan)) for l, inv in zip(ll, X["investor_uuid"])]
    else:
        X["lead_b"] = np.nan
    X["lead_u"] = X["lead_a"].where(X["lead_a"].notna(), X["lead_b"])
    X["tenure"] = [min([(t - first_dt[q]).days / 365.25 for q in ps if q in first_dt] or [np.nan]) for t, ps in zip(X["rdt"], X["partners"])]
    X["tenure_m"] = X["tenure"].isna().astype(float); X["tenure_f"] = X["tenure"].fillna(0)
    X["lead_m"] = X["lead_u"].isna().astype(float); X["lead_f"] = X["lead_u"].fillna(0)
    X["firm"] = X["org_uuid"]; X["fo"] = ((X["fp"] == 1) & (X["fp_min"] == 1)).astype(float); X["mx"] = ((X["fp"] == 1) & (X["fp_min"] == 0)).astype(float)
    return R0, X


def mixed_ff(X, cond=True):
    g = X.groupby("funding_round_uuid")["fp"].agg(["mean", "size"]); mixed = g.index[(g["mean"] > 0) & (g["mean"] < 1) & (g["size"] >= 2)]
    M = X[X["funding_round_uuid"].isin(mixed)]
    if cond: M = M[M["nextH"] == 1]
    return M[M["ff"] == 1].copy()


def fo_sample(FF):
    fo = FF[~((FF["fp"] == 1) & (FF["fp_min"] == 0))]
    g = fo.groupby("funding_round_uuid")["fp"].agg(["mean", "size"]); keep = g.index[(g["mean"] > 0) & (g["mean"] < 1) & (g["size"] >= 2)]
    return fo[fo["funding_round_uuid"].isin(keep)].copy()


def band(v, pm=0.05):
    v = dict(v); v["within_pm0.05"] = bool(v["ci95"][0] >= -pm and v["ci95"][1] <= pm); v["margin_lo_pp"] = round((v["ci95"][0] + pm) * 100, 2); return v


def ffreg(df, y="y1", x="fp", extra=("ln_exp",), tag=""):
    r = boot(df, y, [x] + list(extra), [x], rng, nb=NB, demean="funding_round_uuid", cluster="firm", min_n=50)
    if not r: log(f"  {tag}: 표본 부족"); return None
    o = {x: band(r[x]), "n": r["n"], "n_clusters": r["n_firms"], "n_rounds": int(df["funding_round_uuid"].nunique()), "controls": list(extra)}
    v = o[x]; log(f"  {tag:<56} b {v['coef']*100:+.2f}pp [{v['ci95'][0]*100:+.2f},{v['ci95'][1]*100:+.2f}] MDE {v['mde80']*100:.2f} ±5 {v['within_pm0.05']} n={r['n']:,} 라운드 {o['n_rounds']}")
    return o


# ── (e) 표본·창 사다리 ────────────────────────────────────────────────────────
log("\n" + "=" * 100 + "\n[E] 표본·창 사다리 — any-female · female-only\n" + "=" * 100)
E = {}
samples = {}
for key, scope, we, hz in (("NAEU_2020_36m", "NAEU", pd.Timestamp("2020-10-31"), 1095), ("GLOBAL_2020_36m", "GLOBAL", pd.Timestamp("2020-10-31"), 1095),
                           ("NAEU_2021_24m", "NAEU", pd.Timestamp("2021-10-31"), 730), ("GLOBAL_2021_24m", "GLOBAL", pd.Timestamp("2021-10-31"), 730)):
    R0, X = build_sample(scope, we, hz); FF = mixed_ff(X); fo = fo_sample(FF); samples[key] = (R0, X, FF, fo)
    E[key] = {"scope": scope, "deals_through": str(we.date()), "horizon_days": hz, "n_ff_cond_rounds": int(FF["funding_round_uuid"].nunique()), "n_rows": int(len(FF)),
              "any_female": ffreg(FF, tag=f"{key} any-female"), "female_only": ffreg(fo, tag=f"{key} female-only")}
OUT["E_scope_window"] = E

# ── (c) 리드 플래그 합집합 · (d) 연공 — NAEU 기준 표본 ─────────────────────────
R0, X, FF, fo = samples["NAEU_2020_36m"]
log("\n" + "=" * 100 + "\n[C] 리드 플래그 합집합 (NAEU ≤2020-10, 혼성 FF 조건 라운드)\n" + "=" * 100)
both = FF["lead_a"].notna() & FF["lead_b"].notna()
C = {"cov_is_lead_investor": round(float(FF["lead_a"].notna().mean()), 4), "cov_round_lead_list": round(float(FF["lead_b"].notna().mean()), 4), "cov_union": round(float(FF["lead_u"].notna().mean()), 4),
     "agreement_where_both": round(float((FF.loc[both, "lead_a"] == FF.loc[both, "lead_b"]).mean()), 4) if both.any() else None, "lead_rate_union": round(float(FF["lead_u"].mean()), 4)}
log(f"  커버: is_lead {C['cov_is_lead_investor']} · 라운드 리드 목록 {C['cov_round_lead_list']} · 합집합 {C['cov_union']} · 일치 {C['agreement_where_both']} · 리드율 {C['lead_rate_union']}")
C["lead_u_within_round_fp"] = ffreg(FF.dropna(subset=["lead_u"]), y="lead_u", tag="C y=lead_u ← fp (Table 10 A 리드 행 재추정)")
C["reup_plus_lead_any"] = ffreg(FF, extra=("ln_exp", "lead_f", "lead_m"), tag="C 재참여 + lead_u 통제 any-female")
C["reup_plus_lead_fo"] = ffreg(fo, extra=("ln_exp", "lead_f", "lead_m"), tag="C 재참여 + lead_u 통제 female-only")
OUT["C_lead_union"] = C

log("\n" + "=" * 100 + "\n[D] 파트너 연공 — 라운드 내 격차·통제·전남성 위약 풀\n" + "=" * 100)
D = {"tenure_coverage": round(float(FF["tenure"].notna().mean()), 4), "mean_tenure": round(float(FF["tenure"].mean()), 3)}
D["tenure_gap_within_round"] = ffreg(FF.dropna(subset=["tenure"]), y="tenure", extra=(), tag="D 연공 ← fp (F−M, 년)")
D["reup_plus_tenure_any"] = ffreg(FF, extra=("ln_exp", "tenure_f", "tenure_m"), tag="D 재참여 + 연공 any-female")
D["reup_plus_tenure_fo"] = ffreg(fo, extra=("ln_exp", "tenure_f", "tenure_m"), tag="D 재참여 + 연공 female-only")
D["reup_plus_lead_tenure_any"] = ffreg(FF, extra=("ln_exp", "lead_f", "lead_m", "tenure_f", "tenure_m"), tag="D 재참여 + lead_u + 연공 any-female")
D["reup_plus_lead_tenure_fo"] = ffreg(fo, extra=("ln_exp", "lead_f", "lead_m", "tenure_f", "tenure_m"), tag="D 재참여 + lead_u + 연공 female-only")
# 위약 풀: 전남성, 귀속 ≥2, FF, nextH
g = X.groupby("funding_round_uuid")["fp"].agg(["max", "size"]); allm = g.index[(g["max"] == 0) & (g["size"] >= 2)]
PM = X[X["funding_round_uuid"].isin(allm) & (X["ff"] == 1) & (X["nextH"] == 1)].dropna(subset=["tenure"]).copy()
med = PM.groupby("funding_round_uuid")["tenure"].transform("median"); PM["junior"] = (PM["tenure"] < med).astype(float)
gj = PM.groupby("funding_round_uuid")["junior"].agg(["mean", "size"]); keep = gj.index[(gj["mean"] > 0) & (gj["mean"] < 1) & (gj["size"] >= 2)]
PM = PM[PM["funding_round_uuid"].isin(keep)]
D["placebo_pool"] = {"n_all_male_ff_cond_rounds": int(len(keep)), "n_rows": int(len(PM)), "tenure_gap_junior_minus_senior": round(float(PM.loc[PM["junior"] == 1, "tenure"].mean() - PM.loc[PM["junior"] == 0, "tenure"].mean()), 3)}
D["placebo_junior"] = ffreg(PM, x="junior", tag="D 위약: 재참여 ← junior (전남성 FF 라운드)")
D["placebo_junior_ctrl"] = ffreg(PM, x="junior", extra=("ln_exp", "lead_f", "lead_m"), tag="D 위약 + ln_exp·lead_u")
OUT["D_tenure"] = D

# ── (e-2) 재참여 ↔ 출구 보정 ─────────────────────────────────────────────────
log("\n" + "=" * 100 + "\n[F] 보정 — 혼성 라운드(≤2017-10) 재참여와 기업 출구의 연관\n" + "=" * 100)
ex = exit_dates(); ex = ex if isinstance(ex, dict) else (ex.to_dict() if hasattr(ex, "to_dict") else dict(ex))
Mx = mixed_ff(X, cond=True); Mx = Mx[Mx["rdt"] <= CUT].copy(); Mx["exit"] = Mx["org_uuid"].map(lambda o: 1.0 if ex.get(o) is not None and pd.notna(ex.get(o)) else 0.0)
if Mx["exit"].std() > 0:
    r = boot(Mx, "y1", ["exit"], ["exit"], rng, nb=NB, demean=None, cluster="firm", min_n=50)
    F = {"n_rows": int(len(Mx)), "P_reup_exit": round(float(Mx.loc[Mx["exit"] == 1, "y1"].mean()), 4), "P_reup_noexit": round(float(Mx.loc[Mx["exit"] == 0, "y1"].mean()), 4),
         "slope_reup_on_exit": r["exit"] if r else None, "implied_reup_gap_for_6.25pp_exit_gap_pp": round(r["exit"]["coef"] * 6.25, 3) if r else None}
    log(f"  {F}")
else:
    F = {"n_rows": int(len(Mx)), "note": "exit 변이 없음"}
OUT["F_calibration"] = F

# ── 판정 ────────────────────────────────────────────────────────────────────
g24 = E["GLOBAL_2021_24m"]; fo24 = g24["female_only"]["fp"] if g24["female_only"] else None
pred = {"C_cov_union_ge_0.88": C["cov_union"] >= 0.88, "C_agreement_ge_0.98": bool(C["agreement_where_both"] is not None and C["agreement_where_both"] >= 0.98),
        "C_lead_fp_in_[-0.08,0.02]_incl0": bool(C["lead_u_within_round_fp"] and -0.08 <= C["lead_u_within_round_fp"]["fp"]["coef"] <= 0.02 and not C["lead_u_within_round_fp"]["fp"]["sig"]),
        "D_tenure_gap_in_[-2.5,-1.0]_sig": bool(D["tenure_gap_within_round"] and -2.5 <= D["tenure_gap_within_round"]["fp"]["coef"] <= -1.0 and D["tenure_gap_within_round"]["fp"]["sig"]),
        "D_tenure_ctrl_shift_lt_0.8": bool(D["reup_plus_tenure_any"] and abs(D["reup_plus_tenure_any"]["fp"]["coef"] - E["NAEU_2020_36m"]["any_female"]["fp"]["coef"]) < 0.008),
        "D_placebo_junior_in_[-4,0]_sig": bool(D["placebo_junior"] and -0.04 <= D["placebo_junior"]["junior"]["coef"] <= 0 and D["placebo_junior"]["junior"]["sig"]),
        "E_global36_rounds_580_610": 580 <= E["GLOBAL_2020_36m"]["n_ff_cond_rounds"] <= 610, "E_global24_rounds_640_690": 640 <= g24["n_ff_cond_rounds"] <= 690,
        "E_global24_fo_in_[-4,1]": bool(fo24 and -0.04 <= fo24["coef"] <= 0.01), "E_global24_fo_mde_5.5_6.2": bool(fo24 and 0.055 <= fo24["mde80"] <= 0.062), "E_global24_fo_outside_band": bool(fo24 and not fo24["within_pm0.05"]),
        "F_delta_in_[-0.02,0.03]": bool(F.get("P_reup_exit") is not None and -0.02 <= F["P_reup_exit"] - F["P_reup_noexit"] <= 0.03)}
pred = {k: bool(v) for k, v in pred.items()}
OUT["prediction_check"] = pred
fo_any_band = [k for k, v in E.items() if v["female_only"] and v["female_only"]["fp"]["within_pm0.05"]]
verdict = (f"lead_u 커버 {C['cov_union']:.2f} (일치 {C['agreement_where_both']}) · 리드 fp 차 {C['lead_u_within_round_fp']['fp']['coef']*100:+.2f}pp | 연공 격차 F−M {D['tenure_gap_within_round']['fp']['coef']:+.2f}년 · 연공 통제 any-female {D['reup_plus_tenure_any']['fp']['coef']*100:+.2f}pp | "
           f"위약 junior {D['placebo_junior']['junior']['coef']*100:+.2f}pp [{D['placebo_junior']['junior']['ci95'][0]*100:+.2f},{D['placebo_junior']['junior']['ci95'][1]*100:+.2f}] ({D['placebo_pool']['n_all_male_ff_cond_rounds']} 라운드) | "
           f"GLOBAL 24m: 라운드 {g24['n_ff_cond_rounds']} · female-only {fo24['coef']*100:+.2f}pp [{fo24['ci95'][0]*100:+.2f},{fo24['ci95'][1]*100:+.2f}] MDE {fo24['mde80']*100:.2f} ±5 {fo24['within_pm0.05']} | "
           f"보정 Δ(재참여|출구−비출구) {F.get('P_reup_exit')}−{F.get('P_reup_noexit')} · 6.25pp 함의 {F.get('implied_reup_gap_for_6.25pp_exit_gap_pp')}pp — female-only 밴드 안 창: {fo_any_band or '없음'} (예측 적중 {sum(pred.values())}/{len(pred)})")
emit("P001-56", "R5-5: 라운드 내 재참여 v2 — 리드 플래그 합집합·파트너 연공·글로벌+24m 창·전남성 위약 풀·재참여↔출구 보정 (설계의 CB 천장)", "OK", OUT,
     prediction="lead_u 커버≥0.88·일치≥0.98; 연공 격차 −1.0~−2.5(검출); 연공 통제 이동<0.8; 위약 junior∈[−4,0] CI 0 배제; GLOBAL24 라운드 640–690, female-only∈[−4,+1] MDE 5.5–6.2 밴드 밖; 보정 Δ∈[−0.02,0.03]",
     verdict=verdict, kill_met=False, n=int(len(FF)),
     extra={"stage": 7, "feeds": "R5 design R5-5 → Table 10 A (리드 행·글로벌 행·추정 대상 각주) · §4 ¶3", "slug": "within_round_v2", "builds_on": "P001-42/51",
            "common_sha256_16": RESCUE_SHA, "v6_common_sha256_16": V6_SHA})
log("done")
