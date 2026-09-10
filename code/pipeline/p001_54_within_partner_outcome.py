# -*- coding: utf-8 -*-
"""p001_54 — R5-1: 파트너 내 결과 검정 — 같은 파트너의 FF 딜 vs 비FF 딜, 파트너 성별로 (Cook–Marx–Yimfor 형 Becker 결과 검정의 파트너 판)

[왜] Table 3/4 의 교차 딜 비교는 같은 회사·해·섹터에 남성 파트너의 FF 딜이 있어야 성립해 여성 파트너 326 중 50 만 식별에 들어가고(P001-40/49), 다중 라운드
 셀만의 MDE 는 17.5pp(exit_ever)·11.3pp/yr(해저드)다. R5 설계 심판 R5-1: 파트너 고정효과 아래 **같은 파트너의 FF 딜과 비FF 딜**의 시장 벤치마크 잔차 차이를
 파트너 성별로 비교하면, 필요한 것은 파트너가 두 종류의 딜을 다 가졌다는 것뿐이라 415 명(exit3 창)의 여성 파트너가 식별에 들어간다 — 헤드라인 크기(0.125 sd)에
 닿는 첫 교차 딜 설계(naive MDE 0.10 sd). 호의(taste)는 여성 파트너의 FF 딜이 자기 벤치마크보다 더 낮은 성과 → β_int < 0; 선별은 β_int ≈ 0.

[구성] sample_v1 NAEU 딜(load_deals). 결과 r = y − LOO(연×섹터×단계) 셀 평균 (build()). y: exit3(딜 ≤ 2020-10; 36m 완결) 1차, fon(≤2020-10), exit_ever(≤2017-10).
 회귀: r = α_partner + β_FF·ff + β_int·ff×fp + X'γ + e, 파트너 FE(demean), X = P001-12 딜 통제(log 라운드 규모·회사 나이·log 선행 라운드·log 투자자 수·공동투자자 경험; 결측 지시자).
 표본: 창 안에서 FF 딜과 비FF 딜을 모두 가진 파트너. 군집 부트 400: 파트너(1차) · 투자사(강건성).
 변형: (V1) 투자사×연 FE(fp 를 회귀에 포함) · (V2) 파트너×2년 FE · (V3) 딜 ≥5 파트너 · (V4) 2015+ 빈티지(PI 커버리지 규범) · (V5) + 회사 사전 특성(창업자 수·여성 창업자 수·학위 비중·연쇄창업 비중·직원 밴드·log 선행 조달).
 등가 밴드(사전 확정): exit3 ±5pp (≈ 0.15 sd; 헤드라인 6.25pp 는 0.125 sd) — CI ⊂ ±5 이면 "파트너 자기 기록 안에서 FF 특유 선별 결손 미검출·헤드라인 규모 배제".
 표준화 계수 = β / sd(r) 병기. 2015+ 분할은 첫 로그 줄에 n 을 기록(교훈 71).
[사전 예측] (2026-09-09, 결과 조회 전; 설계 심판의 probe 는 n·Σx̃²·naive MDE 만 — 점추정 없음)
 표본: FF·비FF 둘 다 가진 파트너 3,300–3,600, 여성 380–450 (exit3 창); 딜 45,000–52,000.
 β_int(exit3) ∈ [−2.0, +2.0]pp, CI 0 포함, 파트너 군집 MDE80 3.5–5.0pp; β_FF(남성 파트너의 파트너 내 FF 격차) ∈ [−3, −1]pp.
 β_int(fon) ∈ [−3, +2]; β_int(exit_ever) ∈ [−4, +3]. V1·V2 는 β_int 를 1.5pp 미만 이동. V4(2015+) 는 부호 동일.
[판정] β_int(exit3) 상단 < 0 이고 점 < −3pp → 호의 정합(§4 판정·제목 재검; KILL 아님, 재개). CI ⊂ ±5 → 등가 GO. 그 외 PARTIAL(MDE 병기).
"""
import numpy as np
import pandas as pd

from p001_rescue_common import COMMON_SHA, CTX, CUT, END_FON, boot, build, emit, load_deals, log
from p001_v6_common import EMP_BAND, V6_SHA, equity_rounds, founders_by_org

rng = np.random.default_rng(20260954)
NB = 400
OUT = {}
dn = load_deals(with_exit_dt=True)

# ── P001-12 딜 통제 ─────────────────────────────────────────────────────────
r_ = CTX.rounds[["uuid", "raised_amount_usd", "investor_count", "org_uuid", "announced_on"]].copy()
r_["rdt"] = pd.to_datetime(r_["announced_on"], errors="coerce")
dn = dn.merge(r_[["uuid", "raised_amount_usd", "investor_count"]], left_on="funding_round_uuid", right_on="uuid", how="left", suffixes=("", "_r"))
orgs = CTX.orgs[["uuid", "founded_on", "employee_count"]].copy(); orgs["fy"] = pd.to_datetime(orgs["founded_on"], errors="coerce").dt.year
dn["age"] = (dn["dt"].dt.year - dn["org_uuid"].map(orgs.set_index("uuid")["fy"])).clip(0, 50)
ro = r_.dropna(subset=["org_uuid", "rdt"]).sort_values(["org_uuid", "rdt"])
org_dates = {o: g["rdt"].to_numpy() for o, g in ro.groupby("org_uuid")}
dn["prior"] = [np.searchsorted(org_dates.get(o, np.array([], dtype="datetime64[ns]")), np.datetime64(t)) for o, t in zip(dn["org_uuid"], dn["dt"])]
inv = CTX.inv.dropna(subset=["funding_round_uuid", "investor_uuid"]); icnt = inv.groupby("investor_uuid").size()
ie = inv.copy(); ie["lc"] = np.log1p(ie["investor_uuid"].map(icnt)); rs = ie.groupby("funding_round_uuid")["lc"].agg(["sum", "count"])
dn = dn.merge(rs, left_on="funding_round_uuid", right_index=True, how="left")
own_lc = np.log1p(dn["investor_uuid"].map(icnt).fillna(0))
dn["coexp"] = np.where(dn["count"] > 1, (dn["sum"] - own_lc) / (dn["count"] - 1), np.nan)
dn["x_amt"] = np.log1p(pd.to_numeric(dn["raised_amount_usd"], errors="coerce")); dn["x_ic"] = np.log1p(pd.to_numeric(dn["investor_count"], errors="coerce"))
COVS = []
for c in ("x_amt", "age", "coexp", "x_ic"):
    dn[c + "_m"] = dn[c].isna().astype(float); dn[c] = dn[c].fillna(0); COVS += [c, c + "_m"]
dn["x_prior"] = np.log1p(dn["prior"]); COVS.append("x_prior")
# 회사 사전 특성 (V5)
fnd = founders_by_org(); R = equity_rounds(set(dn["org_uuid"])); rr = R.set_index("uuid")
cum_amt = R.assign(a=R["amt"].fillna(0)).groupby("org_uuid")["a"].cumsum() - R["amt"].fillna(0)
dn["ln_prior_capital"] = np.log1p(dn["funding_round_uuid"].map(pd.Series(cum_amt.to_numpy(), index=R["uuid"])))
dn["emp_band"] = dn["org_uuid"].map(orgs.set_index("uuid")["employee_count"]).map(EMP_BAND)
for c in ("n_founders", "n_female_founders", "founder_degree_share", "serial_share"):
    dn[c] = dn["org_uuid"].map(fnd[c])
CCOV = []
for c in ("ln_prior_capital", "emp_band", "n_founders", "n_female_founders", "founder_degree_share", "serial_share"):
    dn[c + "_m"] = dn[c].isna().astype(float); dn[c] = dn[c].fillna(0); CCOV += [c, c + "_m"]
dn["ffp"] = dn["ff"] * dn["fp"]
dn["firm_year"] = dn["investor_uuid"] + "|" + dn["y"]
dn["partner_2y"] = dn["partner_uuid"] + "|" + (pd.to_numeric(dn["year"]).astype(int) // 2 * 2).astype(str)
dn["firm"] = dn["investor_uuid"]


def sample(y, end):
    s = dn[dn["dt"] <= end].copy()
    s = build(s, y)                      # r = y − LOO 연×섹터×단계 셀 평균
    both = s.groupby("partner_uuid")["ff"].agg(["min", "max"]); keep = both.index[(both["min"] == 0) & (both["max"] == 1)]
    s = s[s["partner_uuid"].isin(keep)].dropna(subset=["r"]).copy()
    return s


def run(s, fe, cluster, extra=(), tag=""):
    xc = ["ff", "ffp"] + (["fp"] if fe != "partner_uuid" and not fe.startswith("partner") else []) + COVS + list(extra)
    res = boot(s, "r", xc, ["ff", "ffp"] + (["fp"] if "fp" in xc else []), rng, nb=NB, demean=fe, cluster=cluster, min_n=500)
    if not res:
        return None
    sd = float(s["r"].std())
    for k in ("ff", "ffp"):
        v = res[k]; v["beta_std"] = round(v["coef"] / sd, 4); v["within_pm0.05"] = bool(v["ci95"][0] >= -0.05 and v["ci95"][1] <= 0.05)
    res["sd_r"] = round(sd, 5); res["n_partners"] = int(s["partner_uuid"].nunique()); res["n_female_partners"] = int(s.loc[s["fp"] == 1, "partner_uuid"].nunique())
    res["fe"] = fe; res["cluster"] = cluster
    log(f"  {tag:<44} β_int {res['ffp']['coef']*100:+.2f}pp [{res['ffp']['ci95'][0]*100:+.2f},{res['ffp']['ci95'][1]*100:+.2f}] MDE {res['ffp']['mde80']*100:.2f} ({res['ffp']['beta_std']:+.3f} sd) ±5 {res['ffp']['within_pm0.05']} · "
        f"β_FF {res['ff']['coef']*100:+.2f} [{res['ff']['ci95'][0]*100:+.2f},{res['ff']['ci95'][1]*100:+.2f}] · n {res['n']:,} · 파트너 {res['n_partners']:,} (여 {res['n_female_partners']})")
    return res


for y, end, lab in (("exit3", END_FON, "A_exit3"), ("fon", END_FON, "B_fon"), ("exit_ever", CUT, "C_exit_ever")):
    s = sample(y, end)
    n15 = int((s["dt"] >= "2015-01-01").sum())
    A = {"y": y, "deals_through": str(end.date()), "n_deals": int(len(s)), "n_deals_2015plus": n15, "n_partners": int(s["partner_uuid"].nunique()),
         "n_female_partners": int(s.loc[s["fp"] == 1, "partner_uuid"].nunique()), "n_ff_deals_female_partners": int(((s["ff"] == 1) & (s["fp"] == 1)).sum()),
         "n_nonff_deals_female_partners": int(((s["ff"] == 0) & (s["fp"] == 1)).sum()), "base_y": round(float(s[y].mean()), 4), "sd_r": round(float(s["r"].std()), 4),
         "raw_within_partner_gap": {}}
    for g_, m in (("female", s["fp"] == 1), ("male", s["fp"] == 0)):
        sub = s[m]; gap = sub.groupby("partner_uuid").apply(lambda q: q.loc[q["ff"] == 1, "r"].mean() - q.loc[q["ff"] == 0, "r"].mean())
        A["raw_within_partner_gap"][g_] = round(float(gap.mean()), 4)
    log("\n" + "=" * 100 + f"\n[{lab}] y={y} ≤{end.date()} · 딜 {A['n_deals']:,} (2015+ {n15:,}) · 파트너 {A['n_partners']:,} (여 {A['n_female_partners']}) · 기저 {A['base_y']:.4f} · 원시 파트너 내 FF 격차 여 {A['raw_within_partner_gap']['female']:+.4f} / 남 {A['raw_within_partner_gap']['male']:+.4f}\n" + "=" * 100)
    O = {"sample": A}
    O["main_partnerFE_clPartner"] = run(s, "partner_uuid", "partner_uuid", tag="파트너 FE · 파트너 군집")
    O["main_partnerFE_clFirm"] = run(s, "partner_uuid", "firm", tag="파트너 FE · 투자사 군집")
    if y == "exit3":
        O["V1_firmYearFE"] = run(s, "firm_year", "firm", tag="V1 투자사×연 FE (fp 포함)")
        O["V2_partner2yFE"] = run(s, "partner_2y", "partner_uuid", tag="V2 파트너×2년 FE")
        cnt = s.groupby("partner_uuid")["ff"].transform("size"); O["V3_partners_ge5"] = run(s[cnt >= 5], "partner_uuid", "partner_uuid", tag="V3 딜 ≥5 파트너")
        O["V4_2015plus"] = run(s[s["dt"] >= "2015-01-01"], "partner_uuid", "partner_uuid", tag="V4 2015+ 빈티지")
        O["V5_company_controls"] = run(s, "partner_uuid", "partner_uuid", extra=CCOV, tag="V5 + 회사 사전 특성")
        O["V6_no_controls"] = run(s.assign(**{c: 0.0 for c in COVS}), "partner_uuid", "partner_uuid", tag="V6 통제 없음(FE 만)") if False else None
    OUT[lab] = O

A_, B_, C_ = OUT["A_exit3"], OUT["B_fon"], OUT["C_exit_ever"]
m = A_["main_partnerFE_clPartner"]; bi = m["ffp"]
pred = {"A_partners_3300_3600": 3300 <= A_["sample"]["n_partners"] <= 3600, "A_female_380_450": 380 <= A_["sample"]["n_female_partners"] <= 450,
        "A_deals_45k_52k": 45000 <= A_["sample"]["n_deals"] <= 52000, "A_bint_in_[-2,2]": -0.02 <= bi["coef"] <= 0.02, "A_bint_ci_incl0": bi["ci95"][0] <= 0 <= bi["ci95"][1],
        "A_mde_3.5_5.0": 0.035 <= bi["mde80"] <= 0.050, "A_bFF_male_in_[-3,-1]": -0.03 <= m["ff"]["coef"] <= -0.01,
        "B_bint_in_[-3,2]": -0.03 <= B_["main_partnerFE_clPartner"]["ffp"]["coef"] <= 0.02, "C_bint_in_[-4,3]": -0.04 <= C_["main_partnerFE_clPartner"]["ffp"]["coef"] <= 0.03,
        "V1_shift_lt_1.5": bool(A_["V1_firmYearFE"] and abs(A_["V1_firmYearFE"]["ffp"]["coef"] - bi["coef"]) < 0.015),
        "V2_shift_lt_1.5": bool(A_["V2_partner2yFE"] and abs(A_["V2_partner2yFE"]["ffp"]["coef"] - bi["coef"]) < 0.015),
        "V4_same_sign": bool(A_["V4_2015plus"] and np.sign(A_["V4_2015plus"]["ffp"]["coef"]) == np.sign(bi["coef"]))}
pred = {k: bool(v) for k, v in pred.items()}
OUT["prediction_check"] = pred
if bi["within_pm0.05"]:
    status, call = "GO", "파트너 자기 기록 안에서 FF 특유 선별 결손 미검출 — CI ⊂ ±5pp(헤드라인 규모 배제)"
elif bi["ci95"][1] < 0 and bi["coef"] < -0.03:
    status, call = "GO", "여성 파트너의 FF 딜이 자기 벤치마크 대비 열위 — 호의 정합 (§4 판정·제목 재검)"
else:
    status, call = "PARTIAL", "검출도 등가도 아님 — MDE 병기"
verdict = (f"exit3 ≤2020-10: 파트너 {A_['sample']['n_partners']:,} (여 {A_['sample']['n_female_partners']}) · 딜 {A_['sample']['n_deals']:,} | β_int {bi['coef']*100:+.2f}pp [{bi['ci95'][0]*100:+.2f},{bi['ci95'][1]*100:+.2f}] "
           f"MDE {bi['mde80']*100:.2f} ({bi['beta_std']:+.3f} sd) · β_FF(남) {m['ff']['coef']*100:+.2f} | 투자사 군집 [{A_['main_partnerFE_clFirm']['ffp']['ci95'][0]*100:+.2f},{A_['main_partnerFE_clFirm']['ffp']['ci95'][1]*100:+.2f}] | "
           f"V1 {A_['V1_firmYearFE']['ffp']['coef']*100:+.2f} · V2 {A_['V2_partner2yFE']['ffp']['coef']*100:+.2f} · V3 {A_['V3_partners_ge5']['ffp']['coef']*100:+.2f} · V4(2015+) {A_['V4_2015plus']['ffp']['coef']*100:+.2f} · V5 {A_['V5_company_controls']['ffp']['coef']*100:+.2f} | "
           f"fon β_int {B_['main_partnerFE_clPartner']['ffp']['coef']*100:+.2f} [{B_['main_partnerFE_clPartner']['ffp']['ci95'][0]*100:+.2f},{B_['main_partnerFE_clPartner']['ffp']['ci95'][1]*100:+.2f}] · "
           f"exit_ever β_int {C_['main_partnerFE_clPartner']['ffp']['coef']*100:+.2f} [{C_['main_partnerFE_clPartner']['ffp']['ci95'][0]*100:+.2f},{C_['main_partnerFE_clPartner']['ffp']['ci95'][1]*100:+.2f}] — {call} (예측 적중 {sum(pred.values())}/{len(pred)})")
emit("P001-54", "R5-1: 파트너 내 결과 검정 — 같은 파트너의 FF vs 비FF 딜의 시장 벤치마크 잔차, 파트너 성별 교차항 (파트너 FE·딜 통제·파트너 군집)", status, OUT,
     prediction="파트너 3,300–3,600(여 380–450); β_int(exit3)∈[−2,+2] CI 0 포함 MDE 3.5–5.0; β_FF(남)∈[−3,−1]; fon∈[−3,+2]; exit_ever∈[−4,+3]; V1/V2 이동<1.5; 2015+ 부호 동일",
     verdict=verdict, kill_met=False, n=int(A_["sample"]["n_deals"]),
     extra={"stage": 7, "feeds": "R5 design R5-1 → §4 교차 딜 판별 · Table 4 새 패널", "slug": "within_partner_outcome", "builds_on": "P001-12/33/49",
            "common_sha256_16": COMMON_SHA, "v6_common_sha256_16": V6_SHA})
log("done")
