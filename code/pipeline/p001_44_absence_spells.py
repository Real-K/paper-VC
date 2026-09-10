# -*- coding: utf-8 -*-
"""p001_44 — P4: 부재 스펠 — 파트너 채널의 가역적(on/off/on) 처치

[왜] §5 의 이탈 마진은 "오차가 대상의 5배"(RESULTS_LEDGER §14). 설계 제안 P4: 파트너가 회사에 남아 있으면서 ≥18개월 귀속 딜이 없는
 내부 공백(gap)을 처치로 쓰면 여성 처치 단위가 ≈130 명(정년 이탈 8건의 16배). 채널이 실재하면 그녀의 부재 동안 동료들의 여성창업 비중이
 내려가고 복귀 후 회복해야 한다 — 채용 추세(hiring-on-trend)는 한 파트너의 재직 안에서 두 번 반전하지 않는다.
 공백은 외생이 아니다(휴직·펀드 조성·기록 누락·회사의 섹터 후퇴). 그래서 "부재 = inactive at the firm" 로만 서술하고, 기록 위약과
 남성 부재 대조를 하중으로 삼는다. "parental leave" 라 부르지 않는다.

[구성] sample_v1 NAEU. 파트너: 귀속 딜 ≥10, 첫~마지막 ≥5년. (파트너, 회사) 스펠 안 연속 귀속 딜 간격 ≥18m(및 24m) 이 공백.
 고용 연속성: jobs 에 (파트너, 회사) 행이 있고 started_on ≤ 공백 시작, ended_on ≥ 공백 끝(또는 결측/현직) → cont=1; jobs 행 없음 → cont=NaN.
 패널: 파트너×회사×반기, 스펠 첫 딜 반기 ~ 마지막 딜 반기. 결과 = 그 반기 그 회사의 **동료** 귀속 딜(focal 제외) 중 ff 비중 (동료 딜 ≥1).
 absent = 반기가 공백 창 안에 완전히 포함. 사양: y = a_pf + g_t + b·absent (+ b_f·absent×female) — (파트너,회사) 내 demean + 반기 더미.
 군집 = 회사 부트 300. 위약: 동료 딜 수 log · 회사 귀속률(귀속 딜/전체 지분 딜, 표본 기업) · 공백 전 4반기 사건시간 계수(결합 max|t|).
 용량: 18m / 24m / 36m.
[사전 예측] (2026-09-09, 결과 조회 전)
 파트너 ≈ 1,500–1,650 with ≥18m 공백 (여성 ≈ 120–140); 사용 가능 스펠 ≈ 1,200–1,400.
 b_female ∈ [−0.03, 0], b_male ∈ [−0.01, +0.01]; 차 CI 0 포함, MDE ≈ 1.5–2.5pp → 경계로 서술. 기록 위약 |b| < 0.02; 동료 딜 수 위약 |b| < 0.1.
 용량: 18 → 24 → 36m 단조(b_female 더 음)면 채널 정합.
[판정] 차(b_f − b_m) 하한 < −0.01 이고 상단 < 0 → GO(채널 검출); CI ⊂ ±0.015 → GO(등가: ±1.5pp 안); 그 외 PARTIAL(MDE).

[정정 2026-09-09 — 1차 실행 후] 기록 위약이 실패했다(공백 중 회사 귀속률 여성 −0.17 / 남성 −0.21) — 귀속 딜 기준 결과는 오염 가능.
 제안서가 요구한 **전체 신규 딜 기준 결과**(CTX.inv × rounds, 표본 기업, focal 파트너 귀속 라운드 제외) 를 B2 로 추가한다. 예측(결과 조회 전):
 B2 여성 ∈ [−0.03, +0.01], 남성 ∈ [−0.01, +0.01], 차 CI 0 포함(MDE ≈ 3–4pp). 1차 B/C/D 수치는 불변(같은 seed 순서 — 새 회귀는 뒤에 추가).
"""
import numpy as np
import pandas as pd

from p001_v6_common import (RESCUE_SHA, V6_SHA, emit, fit, half_index, jobs_spells, load_sample, log, qci)

rng = np.random.default_rng(20260944)
NB = 300
OUT = {}
d = load_sample()
d["half"] = half_index(d["dt"])
J = jobs_spells()

# ── 파트너·스펠·공백 ────────────────────────────────────────────────────────
pc = d.groupby("partner_uuid").agg(n=("dt", "size"), first=("dt", "min"), last=("dt", "max"), fp=("fp", "first"))
elig = pc.index[(pc["n"] >= 10) & ((pc["last"] - pc["first"]).dt.days >= 365 * 5)]
dd = d[d["partner_uuid"].isin(elig)].sort_values(["partner_uuid", "investor_uuid", "dt"]).copy()
dd["next_dt"] = dd.groupby(["partner_uuid", "investor_uuid"])["dt"].shift(-1)
dd["gap_days"] = (dd["next_dt"] - dd["dt"]).dt.days
G = dd[dd["gap_days"] >= 540][["partner_uuid", "investor_uuid", "dt", "next_dt", "gap_days", "fp"]].rename(columns={"dt": "g_start", "next_dt": "g_end"}).copy()
# 고용 연속성
jj = J.merge(G[["partner_uuid", "investor_uuid"]].drop_duplicates(), left_on=["person_uuid", "org_uuid"], right_on=["partner_uuid", "investor_uuid"])
def cont_flag(row):
    j = jj[(jj["partner_uuid"] == row["partner_uuid"]) & (jj["investor_uuid"] == row["investor_uuid"])]
    if len(j) == 0: return np.nan
    ok = ((j["sdt"].isna() | (j["sdt"] <= row["g_start"])) & (j["edt"].isna() | (j["edt"] >= row["g_end"]))).any()
    return 1.0 if ok else 0.0
G["cont"] = G.apply(cont_flag, axis=1)
G["h_start"] = half_index(G["g_start"]); G["h_end"] = half_index(G["g_end"])
A = {"n_eligible_partners": int(len(elig)), "n_partners_with_gap18": int(G["partner_uuid"].nunique()), "n_female_with_gap18": int(G.groupby("partner_uuid")["fp"].first().sum()),
     "n_gaps18": int(len(G)), "n_gaps24": int((G["gap_days"] >= 730).sum()), "n_gaps36": int((G["gap_days"] >= 1095).sum()),
     "cont_share_of_gaps_with_jobs": round(float(G["cont"].dropna().mean()), 3) if G["cont"].notna().any() else None, "jobs_coverage_of_gaps": round(float(G["cont"].notna().mean()), 3)}
log(f"[A] 적격 파트너 {A['n_eligible_partners']:,} · ≥18m 공백 보유 {A['n_partners_with_gap18']:,} (여성 {A['n_female_with_gap18']}) · 공백 {A['n_gaps18']:,} (24m {A['n_gaps24']:,} · 36m {A['n_gaps36']:,}) · jobs 커버 {A['jobs_coverage_of_gaps']} · 연속 비중 {A['cont_share_of_gaps_with_jobs']}")

# ── 패널: (파트너, 회사, 반기) — 동료 결과 ────────────────────────────────
firm_half = d.groupby(["investor_uuid", "half"]).agg(n_all=("ff", "size"), ff_sum=("ff", "sum")).reset_index()
own_half = dd.groupby(["partner_uuid", "investor_uuid", "half"]).agg(n_own=("ff", "size"), ff_own=("ff", "sum")).reset_index()
spells = dd.groupby(["partner_uuid", "investor_uuid"]).agg(h0=("half", "min"), h1=("half", "max"), fp=("fp", "first"), n=("dt", "size")).reset_index()
spells = spells[spells["n"] >= 5]
gap_keys = set(zip(G["partner_uuid"], G["investor_uuid"]))
spells["has_gap"] = [(p, f) in gap_keys for p, f in zip(spells["partner_uuid"], spells["investor_uuid"])]
spells = spells[spells["has_gap"]]  # 공백 있는 스펠만 (b 는 스펠 내 스위치에서 식별)
rows = []
for _, s in spells.iterrows():
    for h in range(int(s["h0"]), int(s["h1"]) + 1):
        rows.append((s["partner_uuid"], s["investor_uuid"], h, s["fp"]))
P = pd.DataFrame(rows, columns=["partner_uuid", "investor_uuid", "half", "fp"])
P = P.merge(firm_half, on=["investor_uuid", "half"], how="left").merge(own_half, on=["partner_uuid", "investor_uuid", "half"], how="left")
P[["n_all", "ff_sum", "n_own", "ff_own"]] = P[["n_all", "ff_sum", "n_own", "ff_own"]].fillna(0)
P["n_col"] = P["n_all"] - P["n_own"]; P["ff_col"] = P["ff_sum"] - P["ff_own"]
P["y"] = np.where(P["n_col"] >= 1, P["ff_col"] / P["n_col"].replace(0, np.nan), np.nan)
P["ln_ncol"] = np.log1p(P["n_col"])
for L, days in (("18", 540), ("24", 730), ("36", 1095)):
    gg = G[G["gap_days"] >= days]
    key = {}
    for p, f, hs, he in zip(gg["partner_uuid"], gg["investor_uuid"], gg["h_start"], gg["h_end"]):
        key.setdefault((p, f), []).append((hs, he))
    P[f"abs{L}"] = [1.0 if any(hs < h < he for hs, he in key.get((p, f), [])) else 0.0 for p, f, h in zip(P["partner_uuid"], P["investor_uuid"], P["half"])]
P["pf"] = P["partner_uuid"] + "|" + P["investor_uuid"]
P["firm"] = P["investor_uuid"]
halves = sorted(P["half"].unique()); HD = [f"h{h}" for h in halves[1:]]
for h in halves[1:]:
    P[f"h{h}"] = (P["half"] == h).astype(float)
A["n_panel_rows"] = int(len(P)); A["n_panel_rows_with_colleague_deals"] = int(P["y"].notna().sum()); A["n_spells_in_panel"] = int(P["pf"].nunique())
A["n_absent_rows_18"] = int(P["abs18"].sum()); A["n_female_spells"] = int(spells["fp"].sum())
log(f"    패널 {A['n_panel_rows']:,} 행 · 동료 딜 있는 행 {A['n_panel_rows_with_colleague_deals']:,} · 스펠 {A['n_spells_in_panel']:,} (여성 {A['n_female_spells']}) · 부재 행(18m) {A['n_absent_rows_18']:,}")
OUT["A_sample"] = A


def twfe(df, y, treat, nb=NB, extra=()):
    """(파트너,회사) 내 demean + 반기 더미. treat 와 treat×female 을 함께. 회사 군집 부트."""
    cols = [y, treat] + list(extra) + HD
    dd_ = df.dropna(subset=[y]).copy()
    dd_["tf"] = dd_[treat] * dd_["fp"]
    cols = cols + ["tf"]
    for c in cols:
        dd_[c] = dd_[c] - dd_.groupby("pf")[c].transform("mean")
    xc = [treat, "tf"] + list(extra) + HD
    b = fit(dd_, y, xc); grp = {c: g.index.to_numpy() for c, g in dd_.groupby("firm")}; kl = list(grp); bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(kl), len(kl)); s = dd_.loc[np.concatenate([grp[kl[i]] for i in pick])]
        try: bs.append(fit(s, y, xc))
        except Exception: pass
    bs = np.array(bs); out = {"n": int(len(dd_)), "n_firms": int(dd_["firm"].nunique())}
    i, j = xc.index(treat), xc.index("tf")
    for name, dr, pt in (("b_male", bs[:, i], b[i]), ("diff_female_minus_male", bs[:, j], b[j]), ("b_female", bs[:, i] + bs[:, j], b[i] + b[j])):
        lo, hi = qci(dr); se = float(np.std(dr, ddof=1))
        out[name] = {"coef": round(float(pt), 5), "ci95": [round(lo, 5), round(hi, 5)], "sig": bool(lo > 0 or hi < 0), "se_boot": round(se, 5), "mde80": round(2.8 * se, 4),
                     "within_pm0.015": bool(lo >= -0.015 and hi <= 0.015)}
    return out


def show(tag, r):
    log(f"  {tag:<26} n={r['n']:,}/{r['n_firms']:,} | 여성 {r['b_female']['coef']:+.4f} [{r['b_female']['ci95'][0]:+.3f},{r['b_female']['ci95'][1]:+.3f}] · 남성 {r['b_male']['coef']:+.4f} "
        f"[{r['b_male']['ci95'][0]:+.3f},{r['b_male']['ci95'][1]:+.3f}] · 차 {r['diff_female_minus_male']['coef']:+.4f} [{r['diff_female_minus_male']['ci95'][0]:+.3f},{r['diff_female_minus_male']['ci95'][1]:+.3f}] MDE {r['diff_female_minus_male']['mde80']:.3f}")


log("\n" + "=" * 100 + "\n[B] 동료 ff 비중 ← 부재 (18m/24m/36m)\n" + "=" * 100)
B = {L: twfe(P, "y", f"abs{L}") for L in ("18", "24", "36")}
for L in B: show(f"B 부재 ≥{L}m", B[L])
OUT["B_colleague_ff_share"] = B
log("\n" + "=" * 100 + "\n[C] 위약: 동료 딜 수(log) · 고용 연속 스펠만\n" + "=" * 100)
C = {"ln_colleague_deals_18": twfe(P, "ln_ncol", "abs18")}; show("C 동료 딜 수 위약", C["ln_colleague_deals_18"])
cont_keys = set(zip(G.loc[G["cont"] == 1, "partner_uuid"], G.loc[G["cont"] == 1, "investor_uuid"]))
Pc = P[[(p, f) in cont_keys for p, f in zip(P["partner_uuid"], P["investor_uuid"])]]
C["cont_only_18"] = twfe(Pc, "y", "abs18") if len(Pc) > 500 else None
if C["cont_only_18"]: show("C 고용 연속 스펠만", C["cont_only_18"])
OUT["C_placebos"] = C
# 회사 귀속률 위약: 표본 기업 전체 지분 딜 대비 귀속 딜 — sample_v1 은 귀속 딜만 담으므로 전체 딜은 CTX.inv 필요
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # gates.py / emit_contract.py sit alongside
from gates import CTX  # noqa: E402
inv = CTX.inv.dropna(subset=["funding_round_uuid", "investor_uuid"])[["funding_round_uuid", "investor_uuid"]]
rd = CTX.rounds[["uuid", "org_uuid", "announced_on"]].dropna()
rd = rd[rd["org_uuid"].isin(set(d["org_uuid"]))]
m = inv.merge(rd, left_on="funding_round_uuid", right_on="uuid"); m["dt"] = pd.to_datetime(m["announced_on"], errors="coerce"); m = m.dropna(subset=["dt"])
m["half"] = half_index(m["dt"])
all_fh = m.groupby(["investor_uuid", "half"]).size().rename("n_all_deals").reset_index()
P2 = P.merge(all_fh, on=["investor_uuid", "half"], how="left"); P2["n_all_deals"] = P2["n_all_deals"].fillna(0)
P2["attr_rate"] = np.where(P2["n_all_deals"] > 0, P2["n_all"] / P2["n_all_deals"].replace(0, np.nan), np.nan)
C["attribution_rate_18"] = twfe(P2, "attr_rate", "abs18"); show("C 회사 귀속률 위약", C["attribution_rate_18"])
# ── B2. 전체 신규 딜 기준 결과 (귀속 여부 무관; focal 파트너 귀속 라운드 제외) ──
log("\n" + "=" * 100 + "\n[B2] 회사 전체 지분 딜(표본 기업) 의 ff 비중 ← 부재 — 귀속 기록 오염 차단\n" + "=" * 100)
org_ff = d.groupby("org_uuid")["ff"].first()
m["ff"] = m["org_uuid"].map(org_ff)
all_ff = m.groupby(["investor_uuid", "half"]).agg(ff_all=("ff", "sum")).reset_index()
own_r = dd.drop_duplicates(["partner_uuid", "investor_uuid", "funding_round_uuid"]).groupby(["partner_uuid", "investor_uuid", "half"]).agg(n_own_r=("ff", "size"), ff_own_r=("ff", "sum")).reset_index()
P3 = P2.merge(all_ff, on=["investor_uuid", "half"], how="left").merge(own_r, on=["partner_uuid", "investor_uuid", "half"], how="left")
P3[["ff_all", "n_own_r", "ff_own_r"]] = P3[["ff_all", "n_own_r", "ff_own_r"]].fillna(0)
P3["n_all_ex"] = P3["n_all_deals"] - P3["n_own_r"]; P3["ff_all_ex"] = P3["ff_all"] - P3["ff_own_r"]
P3["y_all"] = np.where(P3["n_all_ex"] >= 1, P3["ff_all_ex"] / P3["n_all_ex"].replace(0, np.nan), np.nan)
B2 = {L: twfe(P3, "y_all", f"abs{L}") for L in ("18", "24", "36")}
for L in B2: show(f"B2 전체 딜 부재 ≥{L}m", B2[L])
B2["cont_only_18"] = twfe(P3[[(p, f) in cont_keys for p, f in zip(P3["partner_uuid"], P3["investor_uuid"])]], "y_all", "abs18")
show("B2 전체 딜, 고용 연속만", B2["cont_only_18"])
B2["n_rows_with_all_deals"] = int(P3["y_all"].notna().sum())
OUT["B2_all_deals_ff_share"] = B2
log("\n" + "=" * 100 + "\n[D] 공백 전 사건시간 (−4..−1 반기) 결합 검정\n" + "=" * 100)
g18 = G[G["gap_days"] >= 540]
first_gap = g18.sort_values("h_start").groupby(["partner_uuid", "investor_uuid"])["h_start"].first().to_dict()
for k in range(1, 5):
    P[f"pre{k}"] = [1.0 if first_gap.get((p, f)) == h + k else 0.0 for p, f, h in zip(P["partner_uuid"], P["investor_uuid"], P["half"])]
dd_ = P.dropna(subset=["y"]).copy()
cols = ["y", "abs18"] + [f"pre{k}" for k in range(1, 5)] + HD
for c in cols: dd_[c] = dd_[c] - dd_.groupby("pf")[c].transform("mean")
xc = ["abs18"] + [f"pre{k}" for k in range(1, 5)] + HD
b0 = fit(dd_, "y", xc); grp = {c: g.index.to_numpy() for c, g in dd_.groupby("firm")}; kl = list(grp); bs = []
for _ in range(NB):
    pick = rng.integers(0, len(kl), len(kl)); s = dd_.loc[np.concatenate([grp[kl[i]] for i in pick])]
    try: bs.append(fit(s, "y", xc))
    except Exception: pass
bs = np.array(bs); idx = [xc.index(f"pre{k}") for k in range(1, 5)]
se = bs[:, idx].std(axis=0, ddof=1); t_obs = b0[idx] / se; t_star = (bs[:, idx] - b0[idx]) / se
maxt = np.abs(t_star).max(axis=1)
D = {"pre_coefs": {f"pre{k}": {"coef": round(float(b0[i]), 5), "t": round(float(t_obs[j]), 2)} for j, (k, i) in enumerate(zip(range(1, 5), idx))},
     "max_abs_t_obs": round(float(np.max(np.abs(t_obs))), 3), "sup_t_crit95": round(float(np.percentile(maxt, 95)), 3), "joint_p": round(float(np.mean(maxt >= np.max(np.abs(t_obs)))), 4)}
log(f"  사전 계수 {D['pre_coefs']} · max|t| {D['max_abs_t_obs']} vs sup-t 95% {D['sup_t_crit95']} · 결합 p {D['joint_p']}")
OUT["D_pretrend"] = D

# ── 판정 ────────────────────────────────────────────────────────────────────
df18 = B["18"]["diff_female_minus_male"]; bf18 = B["18"]["b_female"]
if df18["ci95"][1] < 0 and df18["ci95"][0] < -0.01:
    status, call = "GO", "여성 파트너 부재 중 동료 ff 비중 하락 검출 (남성 부재 대비)"
elif df18["within_pm0.015"]:
    status, call = "GO", "±1.5pp 안에서 차등 부재 효과 미검출(등가)"
else:
    status, call = "PARTIAL", "차등 부재 효과 검출도 배제도 안 됨 — MDE 병기"
mono = B["18"]["b_female"]["coef"] >= B["24"]["b_female"]["coef"] >= B["36"]["b_female"]["coef"]
pred = {"A_partners_1500_1650": 1500 <= A["n_partners_with_gap18"] <= 1650, "A_female_120_140": 120 <= A["n_female_with_gap18"] <= 140,
        "B_bf_in_[-0.03,0]": -0.03 <= bf18["coef"] <= 0, "B_bm_in_pm0.01": abs(B["18"]["b_male"]["coef"]) <= 0.01, "B_diff_incl0": not df18["sig"],
        "B_diff_mde_1.5_2.5pp": 0.015 <= df18["mde80"] <= 0.025, "C_attr_rate_lt_0.02": abs(C["attribution_rate_18"]["b_female"]["coef"]) < 0.02,
        "C_lncol_lt_0.1": abs(C["ln_colleague_deals_18"]["b_female"]["coef"]) < 0.1, "dose_monotone": mono, "D_pretrend_joint_p_gt_0.05": D["joint_p"] > 0.05,
        "B2_bf_in_[-0.03,0.01]": -0.03 <= B2["18"]["b_female"]["coef"] <= 0.01, "B2_diff_incl0": not B2["18"]["diff_female_minus_male"]["sig"]}
OUT["flags"] = {"recording_placebo_failed": bool(C["attribution_rate_18"]["b_female"]["sig"] or C["attribution_rate_18"]["b_male"]["sig"])}
pred = {k: bool(v) for k, v in pred.items()}
OUT["prediction_check"] = pred
verdict = (f"공백 파트너 {A['n_partners_with_gap18']:,} (여성 {A['n_female_with_gap18']}) · 스펠 {A['n_spells_in_panel']:,} | 18m: 여성 {bf18['coef']:+.4f} [{bf18['ci95'][0]:+.3f},{bf18['ci95'][1]:+.3f}] · 남성 {B['18']['b_male']['coef']:+.4f} · "
           f"차 {df18['coef']:+.4f} [{df18['ci95'][0]:+.3f},{df18['ci95'][1]:+.3f}] MDE {df18['mde80']:.3f} | 24m 여성 {B['24']['b_female']['coef']:+.4f} · 36m {B['36']['b_female']['coef']:+.4f} (단조 {mono}) | "
           f"위약: 귀속률 {C['attribution_rate_18']['b_female']['coef']:+.4f} · 동료 딜수 {C['ln_colleague_deals_18']['b_female']['coef']:+.3f} · 사전추세 결합 p {D['joint_p']} | "
           f"전체 딜 기준 18m: 여성 {B2['18']['b_female']['coef']:+.4f} [{B2['18']['b_female']['ci95'][0]:+.3f},{B2['18']['b_female']['ci95'][1]:+.3f}] · 차 {B2['18']['diff_female_minus_male']['coef']:+.4f} "
           f"[{B2['18']['diff_female_minus_male']['ci95'][0]:+.3f},{B2['18']['diff_female_minus_male']['ci95'][1]:+.3f}] MDE {B2['18']['diff_female_minus_male']['mde80']:.3f} — {call}"
           f"{' · 기록 위약 실패(귀속률 하락)' if OUT['flags']['recording_placebo_failed'] else ''} (예측 적중 {sum(pred.values())}/{len(pred)})")
emit("P001-44", "P4: 부재 스펠 — 동료 ff 비중 ← 파트너 부재(18/24/36m), 여성−남성 차, 기록·규모 위약, 사전추세", status, OUT,
     prediction="공백 파트너 1,500–1,650(여성 120–140); b_f∈[−0.03,0], b_m≈0, 차 CI 0 포함 MDE 1.5–2.5pp; 위약 |b|<0.02/0.1; 용량 단조; 사전추세 p>0.05",
     verdict=verdict, kill_met=False, n=int(A["n_spells_in_panel"]),
     extra={"stage": 7, "feeds": "v6 설계 제안 P4 → §5 비대칭 문단 대체 마진", "slug": "absence_spells", "builds_on": "P001-04b/21b", "common_sha256_16": RESCUE_SHA, "v6_common_sha256_16": V6_SHA})
log("done")
