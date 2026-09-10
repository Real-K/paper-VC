# -*- coding: utf-8 -*-
"""p001_60 — [v2 2026-09-10: B2 분할 표본 빈티지 차이(독립 추첨) 추가; sample_v2 (D067) 위에서 post-deal rule 행은 항등 확인 역할]
외부 원고 리뷰(comment/MANUSCRIPT_REVIEW_2026-09-10.md) 가 요구한 소수의 재분석 — 결론을 바꾸지 않고 해석의 결정을 해소하는 것만

[왜] (§3) Table 4B 의 β_int 는 두 FF–other 격차의 차이다. 여성 파트너 자신의 FF–other 격차(β_FF + β_int)의 구간은 두 계수의 공분산이 필요 →
 같은 부트 추첨에서 합을 계산한다. (§4) "결손은 2010–14 빈티지에 집중" 은 점추정 패턴 — 빈티지별 계수 차이의 직접 검정(상호작용) 필요.
 (§7-2) 투자일 이전에 기록된 출구(전 NA+EU 출구 양성의 2.3%; 36m 출구 양성의 3.9%)를 기본 결과에 포함한 것 → "딜 이후 출구" 규칙으로 헤드라인 재추정
 (Table 3 동류 비교 GLOBAL·NA+EU, Table 4B 파트너 내 exit3·exit_ever) 후 전체 재구축은 후속으로 미룸(공개). (§9) Table 4B 의 eligible 49,847 vs
 estimation 49,835, 파트너 3,448/418 vs 3,425/415 를 한 곳에서 계산·설명. (§5-4) 고정지평 Mundlak 에 adjusted rate·ln_n 의 회사 평균/편차를 함께
 넣은 사양(between-firm 서술을 유지할 조건).

[구성] 파트너 내 사양 = P001-54 (파트너 FE·딜 통제·파트너 군집). Table 3 사양 = P001-10 (FF 딜, 회사×연×섹터 셀 demean, 투자사 군집 부트 500).
 Mundlak 패널 = P001-38 B (사전 exit3 ≤2017-10, 사후 2017-11~2020-10, n≥5, TEN).
[사전 예측] (2026-09-10, 결과 조회 전)
 A 여성 자신의 FF–other 격차(exit3, ≤2020) ∈ [−4.5, 0], 구간 0 포함 가능; exit_ever(≤2017) ∈ [−12, −4], 상단 < 0.
 B 빈티지 대비(exit_ever: 2015–17 − 2010–14) 점 ∈ [+3, +11], CI 0 포함(검정력 부족 예상). exit3: 2018–20 − 2010–14 ∈ [+2, +9], CI 0 포함.
 C 딜 이후 출구 규칙: 파트너 내 β_int 이동 < 0.5pp; Table 3 GLOBAL 섹터 셀 −6.25 → 이동 < 1pp, 부호·검출 유지; NA+EU 이동 < 1pp.
 D 확장 Mundlak: fm_terrain 여전히 dev_terrain 보다 크고(> 0.2), 대비 CI 는 넓어져 0 포함 가능.
 E 카운트: eligible−estimation 딜 차이 = 파트너 FE demean 에서 단독 행 파트너 탈락 + 벤치마크 셀 단독 딜(r 결측).
[판정] 진단 — status OK. C 에서 Table 3 GLOBAL 이 검출을 잃으면 verdict 에 "재구축 필요" 표기.
"""
import numpy as np
import pandas as pd

from p001_rescue_common import (COMMON_SHA, CTX, CUT, END_FON, TC, TEN, add_firm_means, add_post, add_tenure, boot, build, emit,
                                first_deal_dates, load_deals, log, loo, partner_pre, qci, strip_draws)

rng = np.random.default_rng(20260960)
OUT = {}
dn = load_deals(with_exit_dt=True)
# ── 파트너 내 통제(P001-54/59 와 동일) ─────────────────────────────────────────────────────────────────────────────────────
r_ = CTX.rounds[["uuid", "raised_amount_usd", "investor_count", "org_uuid", "announced_on"]].copy(); r_["rdt"] = pd.to_datetime(r_["announced_on"], errors="coerce")
dn = dn.merge(r_[["uuid", "raised_amount_usd", "investor_count"]], left_on="funding_round_uuid", right_on="uuid", how="left", suffixes=("", "_r"))
orgs = CTX.orgs[["uuid", "founded_on"]].copy(); orgs["fy"] = pd.to_datetime(orgs["founded_on"], errors="coerce").dt.year
dn["age"] = (dn["dt"].dt.year - dn["org_uuid"].map(orgs.set_index("uuid")["fy"])).clip(0, 50)
ro = r_.dropna(subset=["org_uuid", "rdt"]).sort_values(["org_uuid", "rdt"]); org_dates = {o: g["rdt"].to_numpy() for o, g in ro.groupby("org_uuid")}
dn["prior"] = [np.searchsorted(org_dates.get(o, np.array([], dtype="datetime64[ns]")), np.datetime64(t)) for o, t in zip(dn["org_uuid"], dn["dt"])]
inv = CTX.inv.dropna(subset=["funding_round_uuid", "investor_uuid"]); icnt = inv.groupby("investor_uuid").size()
ie = inv.copy(); ie["lc"] = np.log1p(ie["investor_uuid"].map(icnt)); rs = ie.groupby("funding_round_uuid")["lc"].agg(["sum", "count"])
dn = dn.merge(rs, left_on="funding_round_uuid", right_index=True, how="left"); own = np.log1p(dn["investor_uuid"].map(icnt).fillna(0))
dn["coexp"] = np.where(dn["count"] > 1, (dn["sum"] - own) / (dn["count"] - 1), np.nan)
dn["x_amt"] = np.log1p(pd.to_numeric(dn["raised_amount_usd"], errors="coerce")); dn["x_ic"] = np.log1p(pd.to_numeric(dn["investor_count"], errors="coerce"))
COVS = []
for c in ("x_amt", "age", "coexp", "x_ic"):
    dn[c + "_m"] = dn[c].isna().astype(float); dn[c] = dn[c].fillna(0); COVS += [c, c + "_m"]
dn["x_prior"] = np.log1p(dn["prior"]); COVS.append("x_prior"); dn["ffp"] = dn["ff"] * dn["fp"]; dn["firm"] = dn["investor_uuid"]
yr = pd.to_numeric(dn["year"]).astype(int); dn["L15"] = (yr >= 2015).astype(float); dn["L18"] = (yr >= 2018).astype(float)
dn["ff_L15"] = dn["ff"] * dn["L15"]; dn["ffp_L15"] = dn["ffp"] * dn["L15"]; dn["ff_L18"] = dn["ff"] * dn["L18"]; dn["ffp_L18"] = dn["ffp"] * dn["L18"]
# 딜 이후 출구 규칙
post = dn["exit_dt"].notna() & (dn["exit_dt"] > dn["dt"])
dn["exit3_post"] = (dn["exit3"].astype(bool) & post).astype(float); dn["exit_ever_post"] = (dn["exit_ever"].astype(bool) & post).astype(float)


def sample(y, end):
    s = build(dn[dn["dt"] <= end], y)
    both = s.groupby("partner_uuid")["ff"].agg(["min", "max"]); keep = both.index[(both["min"] == 0) & (both["max"] == 1)]
    elig = s[s["partner_uuid"].isin(keep)].copy(); est = elig.dropna(subset=["r"]).copy()
    return elig, est


def run(s, xc, keys, nb=400, cluster="partner_uuid"):
    res = boot(s, "r", xc, keys, rng, nb=nb, demean="partner_uuid", cluster=cluster, min_n=300, return_draws=True)
    sd = float(s["r"].std())
    for k in keys: res[k]["beta_std"] = round(res[k]["coef"] / sd, 4)
    return res


def draw_sum(res, terms, signs):
    d = sum(sg * res["_draws"][:, res["_xc"].index(t)] for t, sg in zip(terms, signs)); pt = sum(sg * res["_b"][res["_xc"].index(t)] for t, sg in zip(terms, signs))
    lo, hi = qci(d); return {"coef": round(float(pt), 5), "ci95": [round(lo, 5), round(hi, 5)], "se_boot": round(float(np.std(d, ddof=1)), 5), "sig": bool(lo > 0 or hi < 0)}


def counts(elig, est):
    both = est.groupby("partner_uuid")["ff"].agg(["min", "max"]); ident = set(both.index[(both["min"] == 0) & (both["max"] == 1)])
    cnt = est.groupby("partner_uuid")["r"].transform("size"); est2 = est[cnt >= 2]
    return {"deals_eligible": int(len(elig)), "deals_estimation": int(len(est2)), "deals_dropped_singleton_benchmark_cell": int(elig["r"].isna().sum()),
            "deals_dropped_single_row_partner": int(len(est) - len(est2)),
            "partners_eligible": int(elig["partner_uuid"].nunique()), "female_partners_eligible": int(elig.loc[elig["fp"] == 1, "partner_uuid"].nunique()),
            "partners_identifying": len(ident), "female_partners_identifying": int(est.loc[(est["fp"] == 1) & est["partner_uuid"].isin(ident), "partner_uuid"].nunique())}


X0 = ["ff", "ffp"] + COVS
# ── A. 여성 파트너 자신의 FF–other 격차 (β_FF + β_int), 같은 추첨 · E. 카운트 ─────────────────────────────────────────────
log("=" * 100 + "\n[A/E] 여성 자신의 FF–other 격차 · eligible vs estimation 카운트\n" + "=" * 100)
A = {}
for y, end, nb in (("exit3", END_FON, 2000), ("fon", END_FON, 2000), ("exit_ever", CUT, 2000)):
    elig, est = sample(y, end); res = run(est, X0, ["ff", "ffp"], nb=nb)
    A[y] = {"window_end": str(end.date()), "nb": nb, "ff": res["ff"], "ffp": res["ffp"], "female_own_gap_ff_plus_ffp": draw_sum(res, ["ff", "ffp"], [1, 1]), "n": res["n"], "sd_r": round(float(est["r"].std()), 5), "counts": counts(elig, est)}
    g = A[y]["female_own_gap_ff_plus_ffp"]
    log(f"  {y:<9} ≤{end.date()}  β_FF {res['ff']['coef']*100:+.2f} [{res['ff']['ci95'][0]*100:+.2f},{res['ff']['ci95'][1]*100:+.2f}] · β_int {res['ffp']['coef']*100:+.2f} [{res['ffp']['ci95'][0]*100:+.2f},{res['ffp']['ci95'][1]*100:+.2f}] · "
        f"여성 자신 FF−other {g['coef']*100:+.2f} [{g['ci95'][0]*100:+.2f},{g['ci95'][1]*100:+.2f}] · n {res['n']:,} · counts {A[y]['counts']}")
OUT["A_female_own_gap"] = A

# ── B. 빈티지 대비 (상호작용) ────────────────────────────────────────────────────────────────────────────────────────────
log("\n" + "=" * 100 + "\n[B] 빈티지 대비: ffp × 후기 더미\n" + "=" * 100)
B = {}
_, sE = sample("exit_ever", CUT)
resE = run(sE, ["ff", "ffp", "ff_L15", "ffp_L15"] + COVS, ["ffp", "ffp_L15"], nb=1000)
B["exit_ever_2017"] = {"beta_int_2010_14": resE["ffp"], "contrast_2015_17_minus_2010_14": resE["ffp_L15"], "beta_int_2015_17": draw_sum(resE, ["ffp", "ffp_L15"], [1, 1]), "n": resE["n"]}
log(f"  exit_ever ≤2017: β_int(2010–14) {resE['ffp']['coef']*100:+.2f} · 대비(2015–17 − 2010–14) {resE['ffp_L15']['coef']*100:+.2f} [{resE['ffp_L15']['ci95'][0]*100:+.2f},{resE['ffp_L15']['ci95'][1]*100:+.2f}]")
_, s3 = sample("exit3", END_FON)
res3 = run(s3, ["ff", "ffp", "ff_L15", "ffp_L15", "ff_L18", "ffp_L18"] + COVS, ["ffp", "ffp_L15", "ffp_L18"], nb=1000)
B["exit3_2020"] = {"beta_int_2010_14": res3["ffp"], "contrast_2015_17_minus_2010_14": res3["ffp_L15"], "contrast_2018_20_minus_2015_17": res3["ffp_L18"],
                   "contrast_2018_20_minus_2010_14": draw_sum(res3, ["ffp_L15", "ffp_L18"], [1, 1]), "beta_int_2018_20": draw_sum(res3, ["ffp", "ffp_L15", "ffp_L18"], [1, 1, 1]), "n": res3["n"]}
log(f"  exit3 ≤2020: β_int(2010–14) {res3['ffp']['coef']*100:+.2f} · 대비(2015–17−2010–14) {res3['ffp_L15']['coef']*100:+.2f} [{res3['ffp_L15']['ci95'][0]*100:+.2f},{res3['ffp_L15']['ci95'][1]*100:+.2f}] · "
    f"대비(2018–20−2010–14) {B['exit3_2020']['contrast_2018_20_minus_2010_14']['coef']*100:+.2f} [{B['exit3_2020']['contrast_2018_20_minus_2010_14']['ci95'][0]*100:+.2f},{B['exit3_2020']['contrast_2018_20_minus_2010_14']['ci95'][1]*100:+.2f}]")
# B2 (c3 §4-third): the split-sample estimates of Table 5B are separate regressions per vintage; their difference is tested with draws from the two
# independent subsamples (variance adds; draws paired arbitrarily). This is a different object from the pooled interaction, which imposes common partner
# effects and control slopes across vintages — both are reported.
sE10, sE15 = sE[sE["L15"] == 0], sE[sE["L15"] == 1]
r10 = run(sE10, X0, ["ffp"], nb=1000); r15 = run(sE15, X0, ["ffp"], nb=1000)
d10, d15 = r10["_draws"][:, r10["_xc"].index("ffp")], r15["_draws"][:, r15["_xc"].index("ffp")]; m_ = min(len(d10), len(d15))
lo, hi = qci(d15[:m_] - d10[:m_])
B["exit_ever_2017"]["split_sample"] = {"beta_int_2010_14": strip_draws(r10)["ffp"], "beta_int_2015_17": strip_draws(r15)["ffp"], "n_2010_14": r10["n"], "n_2015_17": r15["n"],
                                       "difference_2015_17_minus_2010_14_independent_draws": {"coef": round(float(r15["ffp"]["coef"] - r10["ffp"]["coef"]), 5), "ci95": [round(lo, 5), round(hi, 5)], "sig": bool(lo > 0 or hi < 0)}}
log(f"  분할 표본: 2010–14 {r10['ffp']['coef']*100:+.2f} · 2015–17 {r15['ffp']['coef']*100:+.2f} · 차이(독립 추첨) {(r15['ffp']['coef']-r10['ffp']['coef'])*100:+.2f} [{lo*100:+.2f},{hi*100:+.2f}]")
OUT["B_vintage_contrast"] = B

# ── C. 딜 이후 출구 규칙 ────────────────────────────────────────────────────────────────────────────────────────────────
log("\n" + "=" * 100 + "\n[C] 딜 이후 출구 규칙 (exit_dt > 딜일)\n" + "=" * 100)
C = {}
pre_rows = dn[dn["exit_dt"].notna() & (dn["exit_dt"] <= dn["dt"])]
acq = CTX.acq.dropna(subset=["acquiree_uuid", "acquired_on"]).copy(); acq["adt"] = pd.to_datetime(acq["acquired_on"], errors="coerce")
ip = CTX.ipos.dropna(subset=["org_uuid", "went_public_on"]).copy(); ip["idt"] = pd.to_datetime(ip["went_public_on"], errors="coerce")
fi, fa = ip.groupby("org_uuid")["idt"].min(), acq.groupby("acquiree_uuid")["adt"].min()
pi_, pa_ = pre_rows["org_uuid"].map(fi), pre_rows["org_uuid"].map(fa)
ipo_b = pi_.notna() & (pi_ <= pre_rows["dt"]); acq_b = pa_.notna() & (pa_ <= pre_rows["dt"])
gap = (pre_rows["dt"] - pre_rows["exit_dt"]).dt.days
# v2 (D067): sample_v2 excludes companies with an acquisition/IPO on or before the round date at construction, so pre_rows is empty by design;
# the excluded counts are read from the sample manifest and the block below degrades gracefully.
import yaml as _yaml, os
_man = _yaml.safe_load(open(os.environ.get("P001_SAMPLE_MANIFEST", "/path/to/sample_v2_manifest.yaml"), encoding="utf-8"))
C["population_rule_sample_v2"] = {"rule": "rows of companies with an acquisition or IPO dated on or before the round date are excluded at construction (same-day excluded)",
                                  "manifest": {k: ({kk: (vv if isinstance(vv, (int, float, str, bool, list, dict, type(None))) else str(vv)) for kk, vv in v.items()} if isinstance(v, dict) else (v if isinstance(v, (int, float, str, bool, list, type(None))) else str(v))) for k, v in _man.items() if k != "columns"}}
C["pre_deal_exit_records"] = {"n_rows_naeu": int(len(pre_rows)), "share_of_exit_ever_positives": round(float(len(pre_rows) / dn["exit_ever"].sum()), 4),
                              "acquisition_before_deal": int((acq_b & ~ipo_b).sum()), "ipo_before_deal": int((ipo_b & ~acq_b).sum()), "both": int((ipo_b & acq_b).sum()),
                              "days_deal_after_exit_q10_q50_q90": ([int(gap.quantile(q)) for q in (0.1, 0.5, 0.9)] if len(pre_rows) else None), "same_day": int((gap == 0).sum()),
                              "top_stages": {k: int(v) for k, v in pre_rows["stage"].value_counts().head(5).items()},
                              "share_of_exit3_positives_2020": round(float(((dn["dt"] <= END_FON) & (dn["exit3"] == 1) & (dn["exit_dt"] <= dn["dt"])).sum() / ((dn["dt"] <= END_FON) & (dn["exit3"] == 1)).sum()), 4),
                              "share_of_exit_ever_positives_2017": round(float(((dn["dt"] <= CUT) & (dn["exit_ever"] == 1) & (dn["exit_dt"] <= dn["dt"])).sum() / ((dn["dt"] <= CUT) & (dn["exit_ever"] == 1)).sum()), 4)}
log(f"  이전 출구 행 {C['pre_deal_exit_records']}")
for y, end in (("exit3", END_FON), ("exit_ever", CUT)):
    _, s_orig = sample(y, end); _, s_post = sample(y + "_post", end)
    r_o = run(s_orig, X0, ["ffp"], nb=400); r_p = run(s_post, X0, ["ffp"], nb=400)
    C[f"within_partner_{y}"] = {"original": strip_draws(r_o)["ffp"], "post_deal_rule": strip_draws(r_p)["ffp"], "n_original": r_o["n"], "n_post_rule": r_p["n"],
                                "base_original": round(float(s_orig[y].mean()), 4), "base_post_rule": round(float(s_post[y + "_post"].mean()), 4)}
    log(f"  파트너 내 {y}: 원 {r_o['ffp']['coef']*100:+.2f} [{r_o['ffp']['ci95'][0]*100:+.2f},{r_o['ffp']['ci95'][1]*100:+.2f}] → 딜 이후 규칙 {r_p['ffp']['coef']*100:+.2f} [{r_p['ffp']['ci95'][0]*100:+.2f},{r_p['ffp']['ci95'][1]*100:+.2f}]")
# Table 3 동류 비교 (P001-10 사양): FF 딜 ≤2017-10, exit_ever, 회사×연×섹터 셀 demean, 투자사 군집 부트 500 — GLOBAL 은 표본 파케이 전체
import os
HERE = os.path.dirname(os.path.abspath(__file__))
allx = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v2.parquet")); allx["dt"] = pd.to_datetime(allx["dt"])
exit_any = pd.concat([fa, fi], axis=1).min(axis=1); allx["exit_dt"] = allx["org_uuid"].map(exit_any)
assert float((allx["exit_dt"].notna().astype(float) == allx["exit_ever"]).mean()) > 0.999
allx["exit_ever_post"] = (allx["exit_ever"].astype(bool) & allx["exit_dt"].notna() & (allx["exit_dt"] > allx["dt"])).astype(float); allx["firm"] = allx["investor_uuid"]
NAEU_ = set(dn["country_code"].unique())


def peer(df, y, nb=500):
    s = df[(df["ff"] == 1) & (df["dt"] <= CUT)].copy()
    g = s.groupby("cell_cat")["fp"].agg(["min", "max"]); mixed = g.index[(g["min"] == 0) & (g["max"] == 1)]
    s = s[s["cell_cat"].isin(mixed)].copy()
    res = boot(s, y, ["fp"], ["fp"], rng, nb=nb, demean="cell_cat", cluster="firm", min_n=100)
    return {"fp": res["fp"], "n": res["n"], "n_cells": int(s["cell_cat"].nunique()), "base": round(float(s[y].mean()), 4)}


for scope, df in (("GLOBAL", allx), ("NAEU", allx[allx["country_code"].isin(NAEU_)])):
    o, p_ = peer(df, "exit_ever"), peer(df, "exit_ever_post")
    C[f"table3_peer_{scope}"] = {"original": o, "post_deal_rule": p_}
    log(f"  Table 3 {scope}: 원 {o['fp']['coef']*100:+.2f} [{o['fp']['ci95'][0]*100:+.2f},{o['fp']['ci95'][1]*100:+.2f}] (n {o['n']:,}, 셀 {o['n_cells']}) → 딜 이후 규칙 {p_['fp']['coef']*100:+.2f} [{p_['fp']['ci95'][0]*100:+.2f},{p_['fp']['ci95'][1]*100:+.2f}]")
OUT["C_post_deal_exit_rule"] = C

# ── D. 확장 Mundlak (고정지평) ──────────────────────────────────────────────────────────────────────────────────────────
log("\n" + "=" * 100 + "\n[D] 고정지평 Mundlak — adjusted rate·ln_n·연공의 회사 평균/편차 동시 투입\n" + "=" * 100)
P, h = partner_pre(dn, "exit3"); P = add_post(P, dn, "exit3", end=END_FON); P = add_tenure(P, first=first_deal_dates())
P = add_firm_means(P, ["terrain", "adj", "ln_n", "fp"] + TEN)
D = {}
base = boot(P, "post_adj", ["dev_terrain", "fm_terrain", "adj", "ln_n", "fp"] + TEN, ["dev_terrain", "fm_terrain"], rng, return_draws=True)
D["baseline_partial_mundlak"] = {"dev_terrain": base["dev_terrain"], "fm_terrain": base["fm_terrain"], "contrast_dev_minus_fm": draw_sum(base, ["dev_terrain", "fm_terrain"], [1, -1]), "n": base["n"]}
XF = ["dev_terrain", "fm_terrain", "dev_adj", "fm_adj", "dev_ln_n", "fm_ln_n", "fp"] + TEN
full = boot(P, "post_adj", XF, ["dev_terrain", "fm_terrain", "dev_adj", "fm_adj"], rng, return_draws=True)
D["full_mundlak_adj_lnn"] = {k: full[k] for k in ("dev_terrain", "fm_terrain", "dev_adj", "fm_adj")}; D["full_mundlak_adj_lnn"].update({"contrast_dev_minus_fm": draw_sum(full, ["dev_terrain", "fm_terrain"], [1, -1]), "n": full["n"]})
XF2 = ["dev_terrain", "fm_terrain", "dev_adj", "fm_adj", "dev_ln_n", "fm_ln_n", "dev_fp", "fm_fp"] + [f"dev_{c}" for c in TEN] + [f"fm_{c}" for c in TEN]
full2 = boot(P, "post_adj", XF2, ["dev_terrain", "fm_terrain"], rng, return_draws=True)
D["full_mundlak_all_within_between"] = {"dev_terrain": full2["dev_terrain"], "fm_terrain": full2["fm_terrain"], "contrast_dev_minus_fm": draw_sum(full2, ["dev_terrain", "fm_terrain"], [1, -1]), "n": full2["n"]}
D["n_partners"] = int(len(P)); D["n_single_partner_firms"] = int((P["fm_k"] == 1).sum()); D["corr_fm_terrain_fm_adj"] = round(float(P[["fm_terrain", "fm_adj"]].corr().iloc[0, 1]), 4)
for k in ("baseline_partial_mundlak", "full_mundlak_adj_lnn", "full_mundlak_all_within_between"):
    v = D[k]; log(f"  {k:<34} within {v['dev_terrain']['coef']:+.3f} [{v['dev_terrain']['ci95'][0]:+.3f},{v['dev_terrain']['ci95'][1]:+.3f}] · between {v['fm_terrain']['coef']:+.3f} [{v['fm_terrain']['ci95'][0]:+.3f},{v['fm_terrain']['ci95'][1]:+.3f}] · 대비 {v['contrast_dev_minus_fm']['coef']:+.3f} [{v['contrast_dev_minus_fm']['ci95'][0]:+.3f},{v['contrast_dev_minus_fm']['ci95'][1]:+.3f}]")
OUT["D_mundlak_extended"] = D

# ── 판정 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
ga, ge = A["exit3"]["female_own_gap_ff_plus_ffp"], A["exit_ever"]["female_own_gap_ff_plus_ffp"]
cE, c3 = B["exit_ever_2017"]["contrast_2015_17_minus_2010_14"], B["exit3_2020"]["contrast_2018_20_minus_2010_14"]
w3, wE = C["within_partner_exit3"], C["within_partner_exit_ever"]; tg = C["table3_peer_GLOBAL"]; tn = C["table3_peer_NAEU"]
pred = {"A_exit3_own_in_[-4.5,0]": -0.045 <= ga["coef"] <= 0, "A_exit_ever_own_in_[-12,-4]_upper_lt0": -0.12 <= ge["coef"] <= -0.04 and ge["ci95"][1] < 0,
        "B_ev_contrast_in_[3,11]_incl0": 0.03 <= cE["coef"] <= 0.11 and cE["ci95"][0] <= 0 <= cE["ci95"][1], "B_e3_contrast_in_[2,9]_incl0": 0.02 <= c3["coef"] <= 0.09 and c3["ci95"][0] <= 0 <= c3["ci95"][1],
        "C_within_shift_lt_0.5pp": abs(w3["post_deal_rule"]["coef"] - w3["original"]["coef"]) < 0.005 and abs(wE["post_deal_rule"]["coef"] - wE["original"]["coef"]) < 0.005,
        "C_table3_global_shift_lt_1pp_detected": abs(tg["post_deal_rule"]["fp"]["coef"] - tg["original"]["fp"]["coef"]) < 0.01 and tg["post_deal_rule"]["fp"]["ci95"][1] < 0,
        "C_table3_naeu_shift_lt_1pp": abs(tn["post_deal_rule"]["fp"]["coef"] - tn["original"]["fp"]["coef"]) < 0.01,
        "D_between_gt_0.2_and_gt_within": D["full_mundlak_adj_lnn"]["fm_terrain"]["coef"] > 0.2 and D["full_mundlak_adj_lnn"]["fm_terrain"]["coef"] > D["full_mundlak_adj_lnn"]["dev_terrain"]["coef"]}
pred = {k: bool(v) for k, v in pred.items()}; OUT["prediction_check"] = pred
rebuild = not (tg["post_deal_rule"]["fp"]["ci95"][1] < 0)
verdict = (f"여성 자신 FF−other: exit3 {ga['coef']*100:+.2f} [{ga['ci95'][0]*100:+.2f},{ga['ci95'][1]*100:+.2f}] · exit_ever {ge['coef']*100:+.2f} [{ge['ci95'][0]*100:+.2f},{ge['ci95'][1]*100:+.2f}] | "
           f"빈티지 대비 exit_ever(15–17 − 10–14) {cE['coef']*100:+.2f} [{cE['ci95'][0]*100:+.2f},{cE['ci95'][1]*100:+.2f}] · exit3(18–20 − 10–14) {c3['coef']*100:+.2f} [{c3['ci95'][0]*100:+.2f},{c3['ci95'][1]*100:+.2f}] | "
           f"딜 이후 규칙: 파트너 내 exit3 {w3['original']['coef']*100:+.2f}→{w3['post_deal_rule']['coef']*100:+.2f} · exit_ever {wE['original']['coef']*100:+.2f}→{wE['post_deal_rule']['coef']*100:+.2f} · Table 3 GLOBAL {tg['original']['fp']['coef']*100:+.2f}→{tg['post_deal_rule']['fp']['coef']*100:+.2f} "
           f"[{tg['post_deal_rule']['fp']['ci95'][0]*100:+.2f},{tg['post_deal_rule']['fp']['ci95'][1]*100:+.2f}] · NA+EU {tn['original']['fp']['coef']*100:+.2f}→{tn['post_deal_rule']['fp']['coef']*100:+.2f} | "
           f"확장 Mundlak between {D['full_mundlak_adj_lnn']['fm_terrain']['coef']:+.3f} · within {D['full_mundlak_adj_lnn']['dev_terrain']['coef']:+.3f} · 대비 {D['full_mundlak_adj_lnn']['contrast_dev_minus_fm']['coef']:+.3f} [{D['full_mundlak_adj_lnn']['contrast_dev_minus_fm']['ci95'][0]:+.3f},{D['full_mundlak_adj_lnn']['contrast_dev_minus_fm']['ci95'][1]:+.3f}] "
           f"— {'재구축 필요(GLOBAL 검출 상실)' if rebuild else '헤드라인 유지'} (예측 적중 {sum(pred.values())}/{len(pred)})")
emit("P001-60", "외부 리뷰 재분석: 여성 자신 FF–other 격차·빈티지 대비·딜 이후 출구 규칙·확장 Mundlak·eligible vs estimation 카운트", "OK", OUT,
     prediction="A exit3 own ∈[−4.5,0]; exit_ever own ∈[−12,−4] 상단<0; B 대비 CI 0 포함; C 이동 <0.5pp(파트너 내)/<1pp(Table 3), GLOBAL 검출 유지; D between>0.2>within",
     verdict=verdict, kill_met=False, n=int(A["exit3"]["n"]),
     extra={"stage": 8, "feeds": "comment/RESPONSE_1.md → §4 ¶F·Table 4B·§2 규칙·IA.1", "slug": "review_reanalyses", "builds_on": "P001-54/59/10/38", "common_sha256_16": COMMON_SHA, "rng_seed": 20260960})
log("done")
