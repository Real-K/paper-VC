# -*- coding: utf-8 -*-
"""p001_59 — R6 식별 심판 후속: 파트너 내 결과 검정의 확장 — 빈티지×지평, 이탈 상태, 회사 군집, leave-one-partner-out, IPO/인수 분해, 다중검정 보정,
 국가 포함 벤치마크, 표본 선택 카운트; 라운드 내 밴드 행의 2,000회 부트 재추정

[왜] R6 ident (09_review/R6_recheck/ident.md): (A) 개방 지평 결손(−6.5)은 어느 빈티지에서 오는가 — probe 는 2010–14 빈티지 −10.5 [−17.9, −3.1], 2015–17 −3.2 [−10.2, +3.8], exit3 는
 2010–14 −3.2 → 2015–17 −0.8 → 2018–20 +3.6*; 이탈 파트너가 결손을 나르는가(활동 파트너 −6.2). (F1) 회사 군집(신디케이트 의존). (F2) 206명 여성 중 몇이 결손을 만드나 — leave-one-partner-out,
 IPO/인수 분해. (F3) Panel B 세 결과의 다중검정 보정 p. (F7) 국가 포함 벤치마크. (F8) 파트너 내 표본 밖의 여성 FF 딜 비중. (D/I-4) female-only 밴드 하단 −6.94 는 400회 부트에서 시드에 따라 −5.4~−5.9 로도 나옴 → 2,000회.

[구성] 파트너 내: P001-54/57 사양(파트너 FE·딜 통제·파트너 군집 400). 빈티지 bin = 딜 연도 {2010–14, 2015–17, 2018–20}. 이탈 상태 = 파트너의 마지막 귀속 딜이 2020-11 이후(활동) vs 이전(이탈·비활동).
 IPO/인수: exit_ever 를 ipo_ever(ipos 기록)·acq_ever(acquisitions 피인수)로 분해. LOO: exit_ever β_int 를 여성 파트너 한 명씩 빼고 재적합(점추정; 최대 이동). 다중검정: 세 결과(exit3·fon·exit_ever)의 부트 양측 p 에 Holm 보정.
 국가 벤치마크: LOO 셀 = 연×섹터×단계×국가. 라운드 내: P001-51 표본 any-female·female-only 를 nb=2000 으로.
[사전 예측] (2026-09-09, 결과 조회 전; 심판 probe 점추정은 알고 있음 — 부트 구간은 미지)
 exit_ever 2010–14 β_int ∈ [−14, −6], 상단 < 0; 2015–17 ∈ [−7, +1], CI 0 포함. exit3 2018–20 ∈ [+1, +6]; 2010–14 ∈ [−6, 0]. 활동 파트너 exit_ever ∈ [−9, −3], 상단 < 0.
 회사 군집 CI 폭은 파트너 군집의 ±25% 안. LOO 최대 이동 < 1.5pp(어느 한 명이 결손을 만들지 않음). IPO/인수: 결손은 인수(acq) 쪽이 더 큼(|β_acq| > |β_ipo|). Holm 보정 후 exit_ever p ∈ [0.03, 0.15].
 국가 벤치마크 β_int(exit3) 이 +0.48 의 ±1pp. 표본 밖 여성 FF 딜 비중 < 0.10. 2,000회: any-female 밴드 안 유지; female-only 하단 ∈ [−7.5, −5.5], 밴드 밖.
[판정] 진단 — status OK. 2015–17 빈티지에서도 상단 < 0 이면 "오래된 창의 늦은 출구" 서술을 "빈티지 전반" 으로 고친다(재개).
[v2 2026-09-10, 코드 검토(R6_recheck/code_review_59.md) 반영] (2) 빈티지 행의 n_partners·n_female_partners 는 빈 안에서 FF 변이가 있는(식별) 파트너만 센다(전체 수는 *_all) (3) 활동 상태는 CTX.partners 전체 귀속 딜(표본 밖 포함)로 정의하고 서술은 기술적(결과 지평과 겹침) (6) 자리표시 제거 (7) IPO/인수 LOO 벤치마크는 파트너 필터 전 전체 창에서 계산 (8) Holm 세 행 nb=2000 (11) 실제 rng 시드 기록.
"""
import numpy as np
import pandas as pd

from p001_rescue_common import COMMON_SHA, CTX, CUT, END_FON, boot, build, emit, fit, load_deals, log, loo, qci
from p001_v6_common import V6_SHA, equity_rounds, investor_experience, investor_rows, load_sample, org_maps, partner_gender_rows

rng = np.random.default_rng(20260959)
NB = 400
OUT = {}
dn = load_deals(with_exit_dt=True)
# P001-54 통제
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
dn["x_prior"] = np.log1p(dn["prior"]); COVS.append("x_prior"); dn["ffp"] = dn["ff"] * dn["fp"]; dn["firm"] = dn["investor_uuid"]; dn["company"] = dn["org_uuid"]
yr = pd.to_numeric(dn["year"]).astype(int); dn["vbin"] = np.where(yr <= 2014, "2010-14", np.where(yr <= 2017, "2015-17", "2018-20"))
# IPO / 인수 분해
ipo_orgs = set(CTX.ipos.dropna(subset=["org_uuid"])["org_uuid"]); acq_orgs = set(CTX.acq.dropna(subset=["acquiree_uuid"])["acquiree_uuid"])
dn["ipo_ever"] = dn["org_uuid"].isin(ipo_orgs).astype(float); dn["acq_ever"] = (dn["org_uuid"].isin(acq_orgs) & ~dn["org_uuid"].isin(ipo_orgs)).astype(float)
# 파트너 활동 상태: 전 표본에서 마지막 귀속 딜 일자
pt_all = CTX.partners.dropna(subset=["funding_round_uuid", "partner_uuid"]).merge(r_[["uuid", "rdt"]], left_on="funding_round_uuid", right_on="uuid", how="inner")
last_dt = pt_all.groupby("partner_uuid")["rdt"].max(); dn["partner_active_2021"] = (dn["partner_uuid"].map(last_dt) > pd.Timestamp("2020-10-31")).astype(float)  # v2: 전체 귀속 딜 기준


def sample(y, end, key="yss"):
    s = dn[dn["dt"] <= end].copy()
    if key == "yssc":
        s["yssc"] = s["yss"] + "|" + s["country_code"].astype(str); s["r"] = s[y] - loo(s, "yssc", y)
    else:
        s = build(s, y)
    both = s.groupby("partner_uuid")["ff"].agg(["min", "max"]); keep = both.index[(both["min"] == 0) & (both["max"] == 1)]
    return s[s["partner_uuid"].isin(keep)].dropna(subset=["r"]).copy()


def run(s, tag, cluster="partner_uuid", nb=NB, draws=False):
    res = boot(s, "r", ["ff", "ffp"] + COVS, ["ff", "ffp"], rng, nb=nb, demean="partner_uuid", cluster=cluster, min_n=300, return_draws=True)
    if not res:
        log(f"  {tag}: 표본 부족"); return None
    dr = res["_draws"][:, res["_xc"].index("ffp")]
    p_two = float(2 * min(np.mean(dr >= 0), np.mean(dr <= 0)))
    sd = float(s["r"].std()); out = {k: v for k, v in res.items() if not k.startswith("_")}
    out["ffp"]["beta_std"] = round(out["ffp"]["coef"] / sd, 4); out["ffp"]["within_pm0.05"] = bool(out["ffp"]["ci95"][0] >= -0.05 and out["ffp"]["ci95"][1] <= 0.05); out["ffp"]["p_boot_two"] = round(p_two, 4)
    both_s = s.groupby("partner_uuid")["ff"].agg(["min", "max"]); ident = set(both_s.index[(both_s["min"] == 0) & (both_s["max"] == 1)])  # v2: 부표본 안에서 식별에 기여하는 파트너
    out.update({"n_partners": len(ident), "n_female_partners": int(s.loc[(s["fp"] == 1) & s["partner_uuid"].isin(ident), "partner_uuid"].nunique()),
                "n_partners_all": int(s["partner_uuid"].nunique()), "n_female_partners_all": int(s.loc[s["fp"] == 1, "partner_uuid"].nunique()), "sd_r": round(sd, 5)})
    log(f"  {tag:<46} β_int {out['ffp']['coef']*100:+.2f}pp [{out['ffp']['ci95'][0]*100:+.2f},{out['ffp']['ci95'][1]*100:+.2f}] MDE {out['ffp']['mde80']*100:.2f} p {p_two:.3f} · n {out['n']:,} · 여 {out['n_female_partners']}")
    return (out, dr) if draws else out


# ── A. 빈티지 × 지평 ─────────────────────────────────────────────────────────
log("\n" + "=" * 100 + "\n[A] 빈티지 × 지평\n" + "=" * 100)
A = {}
sE = sample("exit_ever", CUT); s3 = sample("exit3", END_FON)
A["exit_ever_2017"] = {"all": run(sE, "exit_ever ≤2017 전체 (nb=2000)", nb=2000)}
for vb in ("2010-14", "2015-17"):
    A["exit_ever_2017"][vb] = run(sE[sE["vbin"] == vb], f"exit_ever ≤2017 빈티지 {vb}")
A["exit3_2020"] = {"all": run(s3, "exit3 ≤2020 전체 (nb=2000)", nb=2000)}
for vb in ("2010-14", "2015-17", "2018-20"):
    A["exit3_2020"][vb] = run(s3[s3["vbin"] == vb], f"exit3 ≤2020 빈티지 {vb}")
# 이탈 상태
A["exit_ever_2017_active_partners"] = run(sE[sE["partner_active_2021"] == 1], "exit_ever ≤2017 활동 파트너(2021+ 귀속 딜)")
A["exit_ever_2017_inactive_partners"] = run(sE[sE["partner_active_2021"] == 0], "exit_ever ≤2017 비활동 파트너")
OUT["A_vintage_horizon"] = A

# ── B. 회사 군집 · 국가 벤치마크 ─────────────────────────────────────────────
log("\n" + "=" * 100 + "\n[B] 회사 군집 · 국가 포함 벤치마크\n" + "=" * 100)
Bp = {"exit3_company_cluster": run(s3, "exit3 회사 군집", cluster="company"), "exit_ever_company_cluster": run(sE, "exit_ever 회사 군집", cluster="company")}
s3c = sample("exit3", END_FON, key="yssc"); Bp["exit3_country_benchmark"] = run(s3c, "exit3 연×섹터×단계×국가 벤치마크")
OUT["B_clusters_benchmark"] = Bp

# ── C. leave-one-partner-out · IPO/인수 분해 · 다중검정 ───────────────────────
log("\n" + "=" * 100 + "\n[C] LOO(여성 파트너) · IPO/인수 · Holm\n" + "=" * 100)
def demeaned_fit(s):
    dd = s.copy(); cnt = dd.groupby("partner_uuid")["r"].transform("size"); dd = dd[cnt >= 2].copy()
    for c in ["r", "ff", "ffp"] + COVS: dd[c] = dd[c] - dd.groupby("partner_uuid")[c].transform("mean")
    return fit(dd, "r", ["ff", "ffp"] + COVS)[1]
base = demeaned_fit(sE); shifts = []
fem = sE.loc[sE["fp"] == 1, "partner_uuid"].unique()
for p in fem:
    shifts.append(demeaned_fit(sE[sE["partner_uuid"] != p]) - base)
shifts = np.array(shifts)
C = {"exit_ever_loo_female": {"base_coef": round(float(base), 5), "n_female": int(len(fem)), "max_abs_shift": round(float(np.abs(shifts).max()), 5), "shift_toward_zero_max": round(float(shifts.max()), 5),
                             }}
log(f"  LOO 여성 {len(fem)}명: 기준 {base*100:+.2f}pp · 최대 |이동| {np.abs(shifts).max()*100:.2f}pp · 0 쪽 최대 이동 {shifts.max()*100:+.2f}pp")
for y in ("ipo_ever", "acq_ever"):
    s0 = dn[dn["dt"] <= CUT].copy(); s0["r"] = s0[y] - loo(s0, "yss", y)  # v2: 벤치마크는 파트너 필터 전 전체 창에서(exit_ever 행과 동일)
    sy = s0[s0["partner_uuid"].isin(set(sE["partner_uuid"]))].dropna(subset=["r"]).copy()
    C[y] = run(sy, f"{y} ≤2017 (분해)")
# Holm across the three Panel B outcomes (exit3 ≤2020, fon ≤2020, exit_ever ≤2017)
sF = sample("fon", END_FON); rF = run(sF, "fon ≤2020 전체 (nb=2000)", nb=2000)
ps = {"exit3": A["exit3_2020"]["all"]["ffp"]["p_boot_two"], "fon": rF["ffp"]["p_boot_two"], "exit_ever": A["exit_ever_2017"]["all"]["ffp"]["p_boot_two"]}
order = sorted(ps, key=ps.get); m = len(ps); holm = {}; running = 0.0
for i, k in enumerate(order):
    running = max(running, min(1.0, (m - i) * ps[k])); holm[k] = round(running, 4)
C["holm_adjusted_p"] = {"raw": ps, "holm": holm}
log(f"  부트 양측 p {ps} → Holm {holm}")
OUT["C_influence_decomposition_multiplicity"] = C

# ── D. 표본 선택 카운트 ──────────────────────────────────────────────────────
ffF = dn[(dn["dt"] <= END_FON) & (dn["ff"] == 1) & (dn["fp"] == 1)]
in_sample = ffF["partner_uuid"].isin(set(s3["partner_uuid"]))
OUT["D_selection"] = {"female_partner_ff_deals_2020": int(len(ffF)), "share_outside_within_partner_sample": round(float(1 - in_sample.mean()), 4), "female_partners_ff_only": int(ffF.loc[~in_sample, "partner_uuid"].nunique())}
log(f"  여성 파트너 FF 딜 {len(ffF):,} 중 파트너 내 표본 밖 {1 - in_sample.mean():.3f} (FF 만 가진 여성 파트너 {OUT['D_selection']['female_partners_ff_only']})")

# ── E. 라운드 내 밴드 행 2,000회 ────────────────────────────────────────────
log("\n" + "=" * 100 + "\n[E] 라운드 내 any-female · female-only, nb=2000\n" + "=" * 100)
d = load_sample(); om = org_maps(d); R = equity_rounds(set(d["org_uuid"]))
R0 = R[(R["rdt"] >= "2010-01-01") & (R["rdt"] <= "2020-10-31")].copy(); R0["ff"] = R0["org_uuid"].map(om["ff"]); R0["next36"] = ((R0["next_dt"] - R0["rdt"]).dt.days <= 1095).fillna(False).astype(float)
I = investor_rows(R0["uuid"]); pt = partner_gender_rows(R0["uuid"])
pa = pt.groupby(["funding_round_uuid", "investor_uuid"]).agg(fp=("fp", "max"), fp_min=("fp", "min")).reset_index()
X = I.merge(pa, on=["funding_round_uuid", "investor_uuid"], how="inner").merge(R0[["uuid", "org_uuid", "ff", "next_uuid", "next36"]], left_on="funding_round_uuid", right_on="uuid")
X = X.merge(investor_experience(), on=["funding_round_uuid", "investor_uuid"], how="left"); X["ln_exp"] = np.log1p(X["exp_before"].fillna(0))
inv_next = investor_rows(set(R0["next_uuid"].dropna())).groupby("funding_round_uuid")["investor_uuid"].agg(set).to_dict()
X["y1"] = [1.0 if (isinstance(nu, str) and inv_ in inv_next.get(nu, set())) else 0.0 for nu, inv_ in zip(X["next_uuid"], X["investor_uuid"])]
g = X.groupby("funding_round_uuid")["fp"].agg(["mean", "size"]); mixed = g.index[(g["mean"] > 0) & (g["mean"] < 1) & (g["size"] >= 2)]
M = X[X["funding_round_uuid"].isin(mixed) & (X["next36"] == 1) & (X["ff"] == 1)].copy(); M["firm"] = M["org_uuid"]
fo = M[~((M["fp"] == 1) & (M["fp_min"] == 0))]; gr = fo.groupby("funding_round_uuid")["fp"].agg(["mean", "size"]); fo = fo[fo["funding_round_uuid"].isin(gr.index[(gr["mean"] > 0) & (gr["mean"] < 1) & (gr["size"] >= 2)])].copy()
E = {}
for lab, df in (("any_female", M), ("female_only", fo)):
    r = boot(df, "y1", ["fp", "ln_exp"], ["fp"], rng, nb=2000, demean="funding_round_uuid", cluster="firm", min_n=50)
    v = dict(r["fp"]); v["within_pm0.05"] = bool(v["ci95"][0] >= -0.05 and v["ci95"][1] <= 0.05); v["margin_lo_pp"] = round((v["ci95"][0] + 0.05) * 100, 2)
    E[lab] = {"fp": v, "n": r["n"], "n_clusters": r["n_firms"], "nb": 2000}
    log(f"  {lab:<12} nb=2000 b {v['coef']*100:+.2f}pp [{v['ci95'][0]*100:+.2f},{v['ci95'][1]*100:+.2f}] MDE {v['mde80']*100:.2f} ±5 {v['within_pm0.05']} (하단 여유 {v['margin_lo_pp']:+.2f}) n={r['n']:,}")
OUT["E_within_round_2000"] = E

# ── 판정 ────────────────────────────────────────────────────────────────────
a1, a2 = A["exit_ever_2017"]["2010-14"], A["exit_ever_2017"]["2015-17"]; e18 = A["exit3_2020"]["2018-20"]; e10 = A["exit3_2020"]["2010-14"]; act = A["exit_ever_2017_active_partners"]
w_p, w_c = A["exit3_2020"]["all"]["ffp"]["ci95"], Bp["exit3_company_cluster"]["ffp"]["ci95"]
pred = {"A_ev_2010_14_in_[-14,-6]_upper_lt0": bool(a1 and -0.14 <= a1["ffp"]["coef"] <= -0.06 and a1["ffp"]["ci95"][1] < 0), "A_ev_2015_17_in_[-7,1]_incl0": bool(a2 and -0.07 <= a2["ffp"]["coef"] <= 0.01 and a2["ffp"]["ci95"][0] <= 0 <= a2["ffp"]["ci95"][1]),
        "A_e3_2018_20_in_[1,6]": bool(e18 and 0.01 <= e18["ffp"]["coef"] <= 0.06), "A_e3_2010_14_in_[-6,0]": bool(e10 and -0.06 <= e10["ffp"]["coef"] <= 0.0),
        "A_active_in_[-9,-3]_upper_lt0": bool(act and -0.09 <= act["ffp"]["coef"] <= -0.03 and act["ffp"]["ci95"][1] < 0),
        "B_company_cluster_width_pm25pct": abs((w_c[1] - w_c[0]) / (w_p[1] - w_p[0]) - 1) <= 0.25, "B_country_bench_within_1pp": abs(Bp["exit3_country_benchmark"]["ffp"]["coef"] - A["exit3_2020"]["all"]["ffp"]["coef"]) < 0.01,
        "C_loo_max_shift_lt_1.5pp": C["exit_ever_loo_female"]["max_abs_shift"] < 0.015, "C_acq_larger_than_ipo": bool(C["acq_ever"] and C["ipo_ever"] and abs(C["acq_ever"]["ffp"]["coef"]) > abs(C["ipo_ever"]["ffp"]["coef"])),
        "C_holm_ev_in_[0.03,0.15]": 0.03 <= holm["exit_ever"] <= 0.15, "D_outside_share_lt_0.10": OUT["D_selection"]["share_outside_within_partner_sample"] < 0.10,
        "E_any_inside": E["any_female"]["fp"]["within_pm0.05"], "E_fo_lower_in_[-7.5,-5.5]_outside": -0.075 <= E["female_only"]["fp"]["ci95"][0] <= -0.055 and not E["female_only"]["fp"]["within_pm0.05"]}
pred = {k: bool(v) for k, v in pred.items()}
OUT["prediction_check"] = pred
reopen = bool(a2 and a2["ffp"]["ci95"][1] < 0)
verdict = (f"exit_ever ≤2017: 2010–14 {a1['ffp']['coef']*100:+.2f} [{a1['ffp']['ci95'][0]*100:+.2f},{a1['ffp']['ci95'][1]*100:+.2f}] · 2015–17 {a2['ffp']['coef']*100:+.2f} [{a2['ffp']['ci95'][0]*100:+.2f},{a2['ffp']['ci95'][1]*100:+.2f}] · 활동 파트너 {act['ffp']['coef']*100:+.2f} [{act['ffp']['ci95'][0]*100:+.2f},{act['ffp']['ci95'][1]*100:+.2f}] | "
           f"exit3 ≤2020: 2010–14 {e10['ffp']['coef']*100:+.2f} · 2015–17 {A['exit3_2020']['2015-17']['ffp']['coef']*100:+.2f} · 2018–20 {e18['ffp']['coef']*100:+.2f} [{e18['ffp']['ci95'][0]*100:+.2f},{e18['ffp']['ci95'][1]*100:+.2f}] | 회사 군집 exit3 [{w_c[0]*100:+.2f},{w_c[1]*100:+.2f}] · 국가 벤치마크 {Bp['exit3_country_benchmark']['ffp']['coef']*100:+.2f} | "
           f"LOO 최대 이동 {C['exit_ever_loo_female']['max_abs_shift']*100:.2f}pp · ipo {C['ipo_ever']['ffp']['coef']*100:+.2f} · acq {C['acq_ever']['ffp']['coef']*100:+.2f} · Holm p {holm} | 표본 밖 여성 FF 딜 {OUT['D_selection']['share_outside_within_partner_sample']:.3f} | "
           f"2000회: any {E['any_female']['fp']['coef']*100:+.2f} [{E['any_female']['fp']['ci95'][0]*100:+.2f},{E['any_female']['fp']['ci95'][1]*100:+.2f}] · fo {E['female_only']['fp']['coef']*100:+.2f} [{E['female_only']['fp']['ci95'][0]*100:+.2f},{E['female_only']['fp']['ci95'][1]*100:+.2f}] ±5 {E['female_only']['fp']['within_pm0.05']} — "
           f"{'2015–17 에서도 결손 검출 → 서술 재검' if reopen else '결손은 2010–14 빈티지'} (예측 적중 {sum(pred.values())}/{len(pred)})")
emit("P001-59", "R6 ident 후속: 파트너 내 검정 확장(빈티지×지평·이탈 상태·회사 군집·LOO·IPO/인수·Holm·국가 벤치마크·선택) + 라운드 내 밴드 2,000회", "OK", OUT,
     prediction="ev 2010–14 ∈[−14,−6] 상단<0; 2015–17 ∈[−7,+1] 0 포함; e3 2018–20 ∈[+1,+6]; 활동 파트너 ∈[−9,−3]; 회사 군집 ±25%; LOO<1.5; acq>ipo; Holm ev ∈[0.03,0.15]; 표본 밖<0.10; 2000회 any 안·fo 하단 ∈[−7.5,−5.5]",
     verdict=verdict, kill_met=False, n=int(A["exit_ever_2017"]["all"]["n"]),
     extra={"stage": 7, "feeds": "R6 ident A/F → §4 ¶F 빈티지 문장 · Table 4 B 행 · Table 10 A 부트 2000", "slug": "within_partner_extensions", "builds_on": "P001-54/57/51",
            "common_sha256_16": COMMON_SHA, "v6_common_sha256_16": V6_SHA, "rng_seed": 20260959, "version": "v2 (code review 59 applied)"})
log("done")
