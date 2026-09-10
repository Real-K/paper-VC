# -*- coding: utf-8 -*-
"""p001_57 — P001-54 후속: 파트너 내 결과 검정의 결과 구성물 분해 — 같은 창(딜 ≤2017-10)에서 exit3 · exit6 · exit_ever · fon, 그리고 창(≤2017-10 vs ≤2020-10) 의 분리

[왜] P001-54: 고정 36개월 지평(exit3, 딜 ≤2020-10)에서 β_int +0.48 [−1.82, +2.79] (±5 안), fon −1.28 [−4.57, +2.04]; 그러나 **exit_ever(딜 ≤2017-10)** 에서 β_int
 −6.51 [−11.77, −0.54] — 검출된 결손. 예측([−4, +3])을 벗어났다. 두 결과는 (i) 결과 구성물(개방 지평 vs 고정 지평)과 (ii) 표본 창(≤2017-10: 파트너 1,998 vs
 ≤2020-10: 3,448)이 동시에 다르다. 같은 창(≤2017-10)에서 exit3(36m)·exit6(72m; 2023-10 까지 완결)·exit_ever·fon 을 나란히 재면 구성물 효과와 창 효과가 분리된다.
 exit6 은 P001-33 에서 "완결된 긴 지평" 으로 쓴 구성물이다. 이 하네스는 해석을 위한 분해이며 결과를 고르기 위한 것이 아니다 — 전부 보고.

[구성] P001-54 와 동일(파트너 FE·딜 통제·파트너 군집 부트 400; 회사 사전 특성 없음). 창 A: 딜 ≤2017-10 — y ∈ {exit3, exit6, exit_ever, fon}. 창 B: 딜 ≤2020-10 — y ∈ {exit3, fon}
 (P001-54 재현). 추가: 창 A 의 exit_ever 를 "36개월 후 출구"(late = exit_ever − exit3)로도 재어 개방 지평 결손이 어느 구간에서 오는지 본다. 2015+ 분할 n 기록(교훈 71).
[사전 예측] (2026-09-09, 결과 조회 전; P001-54 결과는 알고 있음)
 창 A exit3: β_int ∈ [−3, +2], CI 0 포함 (구성물 효과라면 고정 지평은 같은 창에서도 0 근처).
 창 A exit6: β_int ∈ [−5, +1]; exit_ever 재현 −6.5 ± 0.1; late(36m 이후 출구) β_int ∈ [−6, −1] (개방 지평 결손은 늦은 출구에서).
 창 B exit3 재현 +0.48 ± 0.05. 창 A 의 파트너 1,998 / 여성 206 재현.
[판정] 분해 — status OK. 창 A exit3 상단 < 0 이면 "고정 지평도 창 A 에서 결손" → 표본 창 효과(구성물 아님) → §4 서술 강화 필요(재개).
"""
import numpy as np
import pandas as pd

from p001_rescue_common import COMMON_SHA, CTX, CUT, END, END_FON, boot, build, emit, load_deals, log
from p001_v6_common import V6_SHA

rng = np.random.default_rng(20260957)
NB = 400
OUT = {}
dn = load_deals(with_exit_dt=True)
days = (dn["exit_dt"] - dn["dt"]).dt.days
dn["exit6"] = (days <= 365 * 6).fillna(False).astype(float) if "exit6" not in dn.columns else dn["exit6"]
dn["late_exit"] = ((dn["exit_ever"] == 1) & (dn["exit3"] == 0)).astype(float)   # 36개월 이후의 출구(개방 지평)
# P001-12 딜 통제 (P001-54 와 동일)
r_ = CTX.rounds[["uuid", "raised_amount_usd", "investor_count", "org_uuid", "announced_on"]].copy(); r_["rdt"] = pd.to_datetime(r_["announced_on"], errors="coerce")
dn = dn.merge(r_[["uuid", "raised_amount_usd", "investor_count"]], left_on="funding_round_uuid", right_on="uuid", how="left", suffixes=("", "_r"))
orgs = CTX.orgs[["uuid", "founded_on"]].copy(); orgs["fy"] = pd.to_datetime(orgs["founded_on"], errors="coerce").dt.year
dn["age"] = (dn["dt"].dt.year - dn["org_uuid"].map(orgs.set_index("uuid")["fy"])).clip(0, 50)
ro = r_.dropna(subset=["org_uuid", "rdt"]).sort_values(["org_uuid", "rdt"]); org_dates = {o: g["rdt"].to_numpy() for o, g in ro.groupby("org_uuid")}
dn["prior"] = [np.searchsorted(org_dates.get(o, np.array([], dtype="datetime64[ns]")), np.datetime64(t)) for o, t in zip(dn["org_uuid"], dn["dt"])]
inv = CTX.inv.dropna(subset=["funding_round_uuid", "investor_uuid"]); icnt = inv.groupby("investor_uuid").size()
ie = inv.copy(); ie["lc"] = np.log1p(ie["investor_uuid"].map(icnt)); rs = ie.groupby("funding_round_uuid")["lc"].agg(["sum", "count"])
dn = dn.merge(rs, left_on="funding_round_uuid", right_index=True, how="left"); own_lc = np.log1p(dn["investor_uuid"].map(icnt).fillna(0))
dn["coexp"] = np.where(dn["count"] > 1, (dn["sum"] - own_lc) / (dn["count"] - 1), np.nan)
dn["x_amt"] = np.log1p(pd.to_numeric(dn["raised_amount_usd"], errors="coerce")); dn["x_ic"] = np.log1p(pd.to_numeric(dn["investor_count"], errors="coerce"))
COVS = []
for c in ("x_amt", "age", "coexp", "x_ic"):
    dn[c + "_m"] = dn[c].isna().astype(float); dn[c] = dn[c].fillna(0); COVS += [c, c + "_m"]
dn["x_prior"] = np.log1p(dn["prior"]); COVS.append("x_prior")
dn["ffp"] = dn["ff"] * dn["fp"]


def sample(y, end):
    s = build(dn[dn["dt"] <= end].copy(), y)
    both = s.groupby("partner_uuid")["ff"].agg(["min", "max"]); keep = both.index[(both["min"] == 0) & (both["max"] == 1)]
    return s[s["partner_uuid"].isin(keep)].dropna(subset=["r"]).copy()


def run(s, tag):
    res = boot(s, "r", ["ff", "ffp"] + COVS, ["ff", "ffp"], rng, nb=NB, demean="partner_uuid", cluster="partner_uuid", min_n=500)
    sd = float(s["r"].std())
    for k in ("ff", "ffp"):
        v = res[k]; v["beta_std"] = round(v["coef"] / sd, 4); v["within_pm0.05"] = bool(v["ci95"][0] >= -0.05 and v["ci95"][1] <= 0.05)
    res.update({"sd_r": round(sd, 5), "n_partners": int(s["partner_uuid"].nunique()), "n_female_partners": int(s.loc[s["fp"] == 1, "partner_uuid"].nunique()), "n_deals_2015plus": int((s["dt"] >= "2015-01-01").sum())})
    log(f"  {tag:<34} β_int {res['ffp']['coef']*100:+.2f}pp [{res['ffp']['ci95'][0]*100:+.2f},{res['ffp']['ci95'][1]*100:+.2f}] MDE {res['ffp']['mde80']*100:.2f} ({res['ffp']['beta_std']:+.3f} sd) · β_FF {res['ff']['coef']*100:+.2f} [{res['ff']['ci95'][0]*100:+.2f},{res['ff']['ci95'][1]*100:+.2f}] · n {res['n']:,} · 파트너 {res['n_partners']:,} (여 {res['n_female_partners']})")
    return res


log("\n" + "=" * 100 + "\n[A] 창 ≤2017-10 — 구성물 사다리\n" + "=" * 100)
OUT["A_2017"] = {}
for y in ("exit3", "exit6", "exit_ever", "late_exit", "fon"):
    s = sample(y, CUT); OUT["A_2017"][y] = run(s, f"A ≤2017-10 y={y}"); OUT["A_2017"][y]["base_y"] = round(float(s[y].mean()), 4)
log("\n" + "=" * 100 + "\n[B] 창 ≤2020-10 — exit3 · fon (P001-54 재현)\n" + "=" * 100)
OUT["B_2020"] = {}
for y in ("exit3", "fon"):
    s = sample(y, END_FON); OUT["B_2020"][y] = run(s, f"B ≤2020-10 y={y}"); OUT["B_2020"][y]["base_y"] = round(float(s[y].mean()), 4)

a = OUT["A_2017"]; b = OUT["B_2020"]
pred = {"A_exit3_in_[-3,2]_incl0": -0.03 <= a["exit3"]["ffp"]["coef"] <= 0.02 and not a["exit3"]["ffp"]["sig"], "A_exit6_in_[-5,1]": -0.05 <= a["exit6"]["ffp"]["coef"] <= 0.01,
        "A_exit_ever_reproduces": abs(a["exit_ever"]["ffp"]["coef"] - (-0.0651)) < 0.001, "A_late_in_[-6,-1]": -0.06 <= a["late_exit"]["ffp"]["coef"] <= -0.01,
        "B_exit3_reproduces": abs(b["exit3"]["ffp"]["coef"] - 0.0048) < 0.0005, "A_partners_1998": a["exit_ever"]["n_partners"] == 1998}
pred = {k: bool(v) for k, v in pred.items()}
OUT["prediction_check"] = pred
status = "OK"; call = "구성물 분해 — 전부 보고"
if a["exit3"]["ffp"]["ci95"][1] < 0:
    call = "창 ≤2017-10 에서 고정 지평도 결손 검출 → 표본 창 효과 (§4 서술 강화 필요)"
verdict = (f"≤2017-10: exit3 β_int {a['exit3']['ffp']['coef']*100:+.2f} [{a['exit3']['ffp']['ci95'][0]*100:+.2f},{a['exit3']['ffp']['ci95'][1]*100:+.2f}] · exit6 {a['exit6']['ffp']['coef']*100:+.2f} [{a['exit6']['ffp']['ci95'][0]*100:+.2f},{a['exit6']['ffp']['ci95'][1]*100:+.2f}] · "
           f"exit_ever {a['exit_ever']['ffp']['coef']*100:+.2f} [{a['exit_ever']['ffp']['ci95'][0]*100:+.2f},{a['exit_ever']['ffp']['ci95'][1]*100:+.2f}] · late(36m+) {a['late_exit']['ffp']['coef']*100:+.2f} [{a['late_exit']['ffp']['ci95'][0]*100:+.2f},{a['late_exit']['ffp']['ci95'][1]*100:+.2f}] · fon {a['fon']['ffp']['coef']*100:+.2f} | "
           f"≤2020-10: exit3 {b['exit3']['ffp']['coef']*100:+.2f} · fon {b['fon']['ffp']['coef']*100:+.2f} — {call} (예측 적중 {sum(pred.values())}/{len(pred)})")
emit("P001-57", "P001-54 후속: 파트너 내 결과 검정의 결과 구성물 분해 (같은 창에서 exit3·exit6·exit_ever·36m 이후 출구·fon)", status, OUT,
     prediction="≤2017 exit3∈[−3,+2] CI 0 포함; exit6∈[−5,+1]; exit_ever −6.5 재현; late∈[−6,−1]; ≤2020 exit3 +0.48 재현",
     verdict=verdict, kill_met=False, n=int(a["exit_ever"]["n"]),
     extra={"stage": 7, "feeds": "P001-54 해석 → §4 파트너 내 문단 · Table 4 B", "slug": "within_partner_horizon", "builds_on": "P001-54/33",
            "common_sha256_16": COMMON_SHA, "v6_common_sha256_16": V6_SHA})
log("done")
