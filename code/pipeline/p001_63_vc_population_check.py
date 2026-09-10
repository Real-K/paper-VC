# -*- coding: utf-8 -*-
"""p001_63 — 모집단 점검: 'VC partner' 라는 경제적 모집단과 데이터의 귀속 인물 (c1 §6 · c2 §5)

[왜] 표본은 investor type·직책 필터 없이 investment_partners 에 등장한 인물을 쓴다(corporate·PE·angel group 포함). 리뷰어는 (i) 표본의 투자자 유형 구성과 귀속 인물의 직책 구성을 보이고
 (ii) 식별 가능한 VC 조직으로 한정했을 때 핵심 결과(매칭 사다리·동류 비교·파트너 내 검정·순위 이동)가 어떻게 보이는지 작은 검증표를 요구했다. 전체 표본을 버리지 않는다.
[구성] sample_v2. VC 유형 = investors.investor_types 에 venture_capital / micro_vc / corporate_venture_capital 중 하나라도 포함. 딜·회사·파트너 단위 구성 비중.
  직책: jobs 에서 (파트너, 투자사) 쌍의 직함 키워드(partner / general·managing partner / principal / associate·analyst / director·managing director / 기타·결측) — 고유 쌍 기준과 딜 가중.
  VC 한정 핵심 결과: (a) 매칭 사다리 cell0·cell_stage (NA+EU, 투자사 부트 500) (b) 동류 비교 exit_ever ≤2017 cell_cat GLOBAL·NA+EU (c) 파트너 내 β_int exit3 ≤2020 (파트너 FE, 딜 통제 없음, 파트너 군집 400)
  (d) 순위 이동(P001-05 정의, 파트너 재표집 500).
[사전 예측] (2026-09-10, 결과 조회 전) VC 유형 딜 비중 ∈ [0.55, 0.80]; 직함에 'partner' 포함 비중 ∈ [0.45, 0.75]. VC 한정: 사다리 cell_stage 계수 ±1pp 안; 동류 비교 GLOBAL 부호 유지·구간 넓어짐; β_int ∈ [−2, +3]; 순위 이동 ∈ [+2, +6].
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

rng = np.random.default_rng(20260963)
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR", "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}
NAEU = EU | {"USA", "CAN"}; VC = {"venture_capital", "micro_vc", "corporate_venture_capital"}
d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v2.parquet")); d["dt"] = pd.to_datetime(d["dt"])
inv = CTX.investors[["uuid", "investor_types"]].copy(); inv["types"] = inv["investor_types"].fillna("").str.lower().str.split(",")
inv["is_vc"] = inv["types"].apply(lambda ts: any(t.strip() in VC for t in ts)); inv["first_type"] = inv["types"].str[0].str.strip().replace("", "missing")
d = d.merge(inv[["uuid", "is_vc", "first_type"]], left_on="investor_uuid", right_on="uuid", how="left"); d["is_vc"] = d["is_vc"].fillna(False); d["first_type"] = d["first_type"].fillna("missing")
dn = d[d["country_code"].isin(NAEU)].copy()
OUT = {"A_investor_types": {"share_deals_vc_type_naeu": round(float(dn["is_vc"].mean()), 4), "share_deals_vc_type_global": round(float(d["is_vc"].mean()), 4),
                            "share_partners_at_vc_type_firms": round(float(dn.drop_duplicates(["partner_uuid", "investor_uuid"])["is_vc"].mean()), 4),
                            "first_type_shares_naeu": {k: round(float(v), 4) for k, v in dn["first_type"].value_counts(normalize=True).head(10).items()},
                            "share_deals_missing_type_naeu": round(float((dn["first_type"] == "missing").mean()), 4)}}
print("[A]", OUT["A_investor_types"], flush=True)

# ── 직책 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────
jobs = CTX.jobs[["person_uuid", "org_uuid", "title"]].dropna(subset=["title"])
pairs = dn[["partner_uuid", "investor_uuid"]].drop_duplicates()
pj = pairs.merge(jobs, left_on=["partner_uuid", "investor_uuid"], right_on=["person_uuid", "org_uuid"], how="left")
def bucket(t):
    if not isinstance(t, str): return "no job record at the firm"
    s = t.lower()
    if "general partner" in s or "managing partner" in s or "founding partner" in s: return "general/managing/founding partner"
    if "partner" in s: return "partner (other)"
    if "principal" in s: return "principal"
    if "associate" in s or "analyst" in s: return "associate/analyst"
    if "managing director" in s or "director" in s or "vice president" in s or "vp" == s.strip(): return "director/managing director/VP"
    if "founder" in s or "ceo" in s or "chief" in s: return "founder/CEO/chief"
    return "other title"
pj["bucket"] = pj["title"].apply(bucket)
rank_order = ["general/managing/founding partner", "partner (other)", "principal", "director/managing director/VP", "founder/CEO/chief", "associate/analyst", "other title", "no job record at the firm"]
pj["rk"] = pj["bucket"].map({b: i for i, b in enumerate(rank_order)}); best = pj.sort_values("rk").groupby(["partner_uuid", "investor_uuid"]).head(1)
OUT["B_partner_titles"] = {"unique_pairs": int(len(pairs)), "share_by_bucket_pairs": {b: round(float((best["bucket"] == b).mean()), 4) for b in rank_order},
                           "share_any_partner_title_pairs": round(float(best["bucket"].isin(rank_order[:2]).mean()), 4)}
dw = dn.merge(best[["partner_uuid", "investor_uuid", "bucket"]], on=["partner_uuid", "investor_uuid"], how="left")
OUT["B_partner_titles"]["share_by_bucket_deal_weighted"] = {b: round(float((dw["bucket"] == b).mean()), 4) for b in rank_order}
print("[B]", OUT["B_partner_titles"]["share_by_bucket_pairs"], flush=True)

# ── VC 한정 핵심 결과 ───────────────────────────────────────────────────────────────────────────────────────────────────
def fwl_boot(df, y, x, cell, cluster, nb=500):
    g = df.groupby(cell)[x].agg(["min", "max"]); m = df[df[cell].isin(g.index[(g["min"] == 0) & (g["max"] == 1)])].reset_index(drop=True)
    yr = (m[y] - m.groupby(cell)[y].transform("mean")).to_numpy(); xr = (m[x] - m.groupby(cell)[x].transform("mean")).to_numpy()
    b = float((xr * yr).sum() / (xr * xr).sum()); grp = {c: gg.index.to_numpy() for c, gg in m.groupby(cluster)}; keys = list(grp); bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(keys), len(keys)); rows_ = np.concatenate([grp[keys[i]] for i in pick]); s = (xr[rows_] ** 2).sum()
        if s: bs.append((xr[rows_] * yr[rows_]).sum() / s)
    lo, hi = qci(bs); return {"coef_pp": round(b * 100, 3), "ci95_pp": [round(lo * 100, 3), round(hi * 100, 3)], "n": int(len(m)), "n_cells": int(m[cell].nunique())}
vc = dn[dn["is_vc"]].copy(); vcg = d[d["is_vc"]].copy()
C = {"matching_cell0": fwl_boot(vc, "ff", "fp", "cell0", "investor_uuid"), "matching_cell_stage": fwl_boot(vc, "ff", "fp", "cell_stage", "investor_uuid"),
     "peer_exit_ever_2017_cell_cat_NAEU": fwl_boot(vc[(vc["ff"] == 1) & (vc["dt"] <= "2017-10-31")], "exit_ever", "fp", "cell_cat", "investor_uuid"),
     "peer_exit_ever_2017_cell_cat_GLOBAL": fwl_boot(vcg[(vcg["ff"] == 1) & (vcg["dt"] <= "2017-10-31")], "exit_ever", "fp", "cell_cat", "investor_uuid")}
for k, v in C.items(): print(f"[C] {k:<36} {v['coef_pp']:+.2f} [{v['ci95_pp'][0]:+.2f},{v['ci95_pp'][1]:+.2f}] n {v['n']:,} cells {v['n_cells']:,}", flush=True)
# 파트너 내 β_int (exit3 ≤2020; 파트너 FE; 딜 통제 없음)
acq = CTX.acq.dropna(subset=["acquiree_uuid", "acquired_on"]); ip = CTX.ipos.dropna(subset=["org_uuid", "went_public_on"])
fe = pd.concat([pd.to_datetime(acq["acquired_on"], errors="coerce").groupby(acq["acquiree_uuid"]).min(), pd.to_datetime(ip["went_public_on"], errors="coerce").groupby(ip["org_uuid"]).min()], axis=1).min(axis=1)
vc["exit_dt"] = vc["org_uuid"].map(fe); vc["exit3"] = ((vc["exit_dt"] - vc["dt"]).dt.days <= 365 * 3).fillna(False).astype(float)
w = vc[vc["dt"] <= "2020-10-31"].copy(); w["yss"] = w["year"] + "|" + w["cat"] + "|" + w["stage"]
g = w.groupby("yss")["exit3"]; s_, n_ = g.transform("sum"), g.transform("size"); w["r"] = w["exit3"] - (s_ - w["exit3"]) / (n_ - 1); w = w[n_ > 1]
both = w.groupby("partner_uuid")["ff"].agg(["min", "max"]); w = w[w["partner_uuid"].isin(both.index[(both["min"] == 0) & (both["max"] == 1)])].copy(); w["ffp"] = w["ff"] * w["fp"]
cnt = w.groupby("partner_uuid")["r"].transform("size"); w = w[cnt >= 2].reset_index(drop=True)
def fit_p(df):
    M = df[["r", "ff", "ffp"]].to_numpy(float); M = M - pd.DataFrame(M).groupby(df["partner_uuid"].to_numpy()).transform("mean").to_numpy()
    X = np.column_stack([M[:, 1:], np.ones(len(M))]); return np.linalg.lstsq(X, M[:, 0], rcond=None)[0][:2]
b0 = fit_p(w); grp = {c: gg.index.to_numpy() for c, gg in w.groupby("partner_uuid")}; keys = list(grp); bs = []
for _ in range(400):
    pick = rng.integers(0, len(keys), len(keys)); bs.append(fit_p(w.loc[np.concatenate([grp[keys[i]] for i in pick])].reset_index(drop=True)))
bs = np.array(bs); lo, hi = qci(bs[:, 1])
C["within_partner_exit3_2020_no_controls"] = {"ffp": {"coef": round(float(b0[1]), 5), "ci95": [round(lo, 5), round(hi, 5)], "mde80": round(2.8 * float(np.std(bs[:, 1], ddof=1)), 4)}, "ff": {"coef": round(float(b0[0]), 5), "ci95": [round(x, 5) for x in qci(bs[:, 0])]}, "n": int(len(w)), "n_partners": int(w["partner_uuid"].nunique()), "n_female_partners": int(w.loc[w["fp"] == 1, "partner_uuid"].nunique())}
print(f"[C] within-partner exit3 (VC only) β_int {b0[1]*100:+.2f} [{lo*100:+.2f},{hi*100:+.2f}] n {len(w):,}", flush=True)
# 순위 이동 (P001-05 정의)
h = vc[vc["dt"] <= "2017-10-31"].copy(); h["mcell"] = h["year"] + "|" + h["cat"] + "|" + h["stage"]; h["resid"] = h["exit_ever"] - h.groupby("mcell")["exit_ever"].transform("mean")
P = h.groupby("partner_uuid").agg(raw=("exit_ever", "mean"), adj=("resid", "mean"), n=("exit_ever", "size"), fp=("fp", "first")).reset_index(); P = P[P["n"] >= 5].reset_index(drop=True)
def shift(df):
    r, a = df["raw"].rank(pct=True) * 100, df["adj"].rank(pct=True) * 100; f = df["fp"] == 1; return float(a[f].mean() - r[f].mean())
sh0 = shift(P); bsr = [shift(P.iloc[rng.integers(0, len(P), len(P))].reset_index(drop=True)) for _ in range(500)]
C["rank_shift_female_sample_end"] = {"coef": round(sh0, 3), "ci95": [round(x, 3) for x in qci(bsr)], "n_partners": int(len(P)), "n_female": int((P["fp"] == 1).sum())}
print(f"[C] rank shift (VC only) {sh0:+.2f} [{qci(bsr)[0]:+.2f},{qci(bsr)[1]:+.2f}] n {len(P):,}", flush=True)
OUT["C_vc_only_key_results"] = C
pred = {"A_vc_share_in_[0.55,0.80]": 0.55 <= OUT["A_investor_types"]["share_deals_vc_type_naeu"] <= 0.80, "B_partner_title_in_[0.45,0.75]": 0.45 <= OUT["B_partner_titles"]["share_any_partner_title_pairs"] <= 0.75,
        "C_ladder_stage_within_1pp_of_0.66": abs(C["matching_cell_stage"]["coef_pp"] - 0.66) <= 1.0, "C_peer_global_negative": C["peer_exit_ever_2017_cell_cat_GLOBAL"]["coef_pp"] < 0,
        "C_beta_int_in_[-2,3]": -0.02 <= C["within_partner_exit3_2020_no_controls"]["ffp"]["coef"] <= 0.03, "C_rank_shift_in_[2,6]": 2 <= C["rank_shift_female_sample_end"]["coef"] <= 6}
pred = {k: bool(v) for k, v in pred.items()}; OUT["prediction_check"] = pred
verdict = (f"VC 유형 딜 비중 {OUT['A_investor_types']['share_deals_vc_type_naeu']:.2f} · 'partner' 직함 쌍 비중 {OUT['B_partner_titles']['share_any_partner_title_pairs']:.2f} · VC 한정: 사다리 cell_stage {C['matching_cell_stage']['coef_pp']:+.2f} · 동류 GLOBAL {C['peer_exit_ever_2017_cell_cat_GLOBAL']['coef_pp']:+.2f} [{C['peer_exit_ever_2017_cell_cat_GLOBAL']['ci95_pp'][0]:+.2f},{C['peer_exit_ever_2017_cell_cat_GLOBAL']['ci95_pp'][1]:+.2f}] · "
           f"β_int exit3 {C['within_partner_exit3_2020_no_controls']['ffp']['coef']*100:+.2f} · 순위 이동 {C['rank_shift_female_sample_end']['coef']:+.2f} (예측 적중 {sum(pred.values())}/{len(pred)})")
emit("P001-63", "모집단 점검: 투자자 유형·귀속 인물 직책 구성 + VC 유형 한정 핵심 결과 4종", "OK", OUT, prediction="VC 비중 0.55–0.80; partner 직함 0.45–0.75; VC 한정 결과 부호·크기 유지", verdict=verdict, kill_met=False, n=int(len(dn)),
     extra={"stage": 8, "feeds": "Table 1 · §2 모집단 문단 · Appendix Table IA (population check)", "slug": "vc_population_check", "rng_seed": 20260963, "sample": "sample_v2"})
print("done")
