# -*- coding: utf-8 -*-
"""p001_58 — 공개 소스 변수 투입: (1) 라운드 내 재참여의 투자자 펀드 통제(CB funds · Form D T1) (2) §6 회사 간 연관(Mundlak between)의 펀드 규모·순번 분해
 (3) 특허(PatentsView v2) — 식별 셀 위 균형 공변량 · 파트너 내 결과 검정의 회사 통제

[왜] R5 식별 심판 F-3: 재참여는 준비금·펀드 주기의 결정이기도 하다 → 펀드 나이·규모·순번을 통제. 설계 심판 R5-4/R5-1: 식별 셀 위 균형과 파트너 내 검정에 회사 사전 품질(특허)을 넣어라.
 §6: 구성 성분의 성과 예측은 회사 간(fm_terrain +0.435 [0.177, 0.694], P001-38 B3)에 있다 — 그 정체가 회사의 자본 규모·성숙도(펀드 순번·누적 모집액)인지 본다(pull4 의 CB·Form D 선행판).
 공개 소스 게이트: CB funds(내부), Form D T1(PI 검수 0.973/0.99), PatentsView v2(검수 exact_loc 0.95·도시 일치 1.00 반영 규칙). Companies House 는 본 하네스에 없음(부분집합·별도 설계).

[구성]
 P1 P001-51 NAEU 표본(혼성 FF 라운드·다음 라운드 36m; any-female / female-only). 투자자 변수(딜 시점 이전 정보만):
    CB: fund_age(최근 펀드 공시 후 경과년)·ln_fund_size·fund_seq·has_prior_fund (+결측 지시자) — funds.csv 직접 계산(cb_funds_v1 와 같은 규칙).
    Form D T1: fd_n_before(딜 이전 T1 신규 공시 수)·fd_age(최근 T1 빈티지: SALE_DATE, 없으면 FILING_DATE)·ln_fd_amount(딜 이전 누적 모집액)·fd_any.
    사양: y1 ~ fp + ln_exp [+ CB] [+ FormD] [+ 둘], 라운드 내 demean, 기업 군집 부트 400. + 라운드 내 fp 차(투자자 펀드 변수 균형) + 양성 대조(변수 → y1).
 P2 P001-38 패널(partner_pre exit3 ≤2017-10 · add_post ≤2020-10 · TEN · firm means). 회사 변수(CUT=2017-10-31 시점): fund_seq_cut·ln_cum_usd_cut·fund_age_cut·any_fund ; fd_n_cut·ln_fd_amount_cut·fd_any.
    사양: post_adj ~ dev_terrain + fm_terrain + adj + ln_n + fp + TEN [+ 회사 변수]; 대비(within − between). 보조: fm_terrain ~ 회사 변수 (회사 군집 부트; R²).
 P3 (a) FF cat 다중 라운드 셀(P001-52 정의)에서 any_patent_before·ln1p(n_app_before)·matched_assignee 의 fp 차 — 투자사 군집 부트, sd 단위, MDE.
    (b) P001-54 exit3 사양(파트너 FE·딜 통제·파트너 군집) + 특허 통제(any_patent_before, ln1p n_app_before, matched) → β_int; any_patent_before → r 의 계수(양성 대조).
[사전 예측] (2026-09-09, 결과 조회 전)
 P1: CB 통제로 any-female b 이동 < 0.6pp, female-only < 0.8pp; Form D 통제도 같음; FF 조건 행의 Form D 커버(fd_any) 0.25–0.45; fund_age → y1 음(−0.03~−0.01/yr, 검출), fund_seq·ln_fund_size 는 |b| < 0.02, 미검출.
 P2: 기준 fm_terrain 0.435 재현(±0.01); 회사 변수 투입 후 fm_terrain ∈ [0.30, 0.50](감소 < 30%), 대비 여전히 0 배제; fm_terrain ~ 회사 변수 R² < 0.10; fund_seq_cut 계수 양 소폭.
 P3: (a) any_patent_before fp 차 ∈ [−0.10, +0.10], 미검출(MDE 0.25–0.45 sd); (b) β_int 이동 < 0.3pp(+0.48 대비), any_patent_before → r +0.02~+0.06 검출.
[판정] 진단 — status OK. P2 에서 fm_terrain 이 회사 변수로 절반 이상 줄면 §6 "회사 속성" 서술을 "자본 규모·성숙도" 로 구체화(재개 아님).

[코드 검토 정정 2026-09-09 — 1차 실행 후 재실행] (1) FORMDSUBMISSION.FILING_DATE 혼합 형식 → format="mixed"(1차는 T1 공시 34% 탈락; P2·P3 무영향, P1 Form D 행 소폭)
 (2) fund_age_m·fund_age_cut_m·fd_age_m 완전 공선 제거 (3) ln_fd_amount 를 수정 공시 포함 파일번호별 최대 모집액 합산으로 재측정. 1차 결과: any-female −0.38→−0.21(both), female-only −1.54→−1.53, fm_terrain 0.435→0.430, β_int 0.48→0.53 — 예측 그대로.
"""
import json
import os

import numpy as np
import pandas as pd

from p001_rescue_common import (COMMON_SHA, CTX, CUT, END_FON, TC, TEN, add_firm_means, add_post, add_tenure, boot, build, emit, first_deal_dates, fit, load_deals, log,
                                partner_pre, qci, strip_draws)
from p001_v6_common import V6_SHA, equity_rounds, investor_experience, investor_rows, load_sample, org_maps, partner_gender_rows

rng = np.random.default_rng(20260958)
NB = 400
OUT = {}
HERE = os.path.dirname(os.path.abspath(__file__))
SF = os.path.abspath(os.path.join(HERE, "..", "..", ".."))            # startup_finance/
FORMD = os.path.join(SF, "shared", "data", "processed", "formd_v1"); PAT = os.path.join(SF, "shared", "data", "processed", "patents_v1")
FUNDS = os.path.join(SF, "..", "data", "crunchbase", "funds.csv")

# ── 투자사 수준 소스: CB funds · Form D T1 ─────────────────────────────────────
F = pd.read_csv(FUNDS, usecols=["entity_uuid", "announced_on", "raised_amount_usd"], low_memory=False).dropna(subset=["entity_uuid"])
F["fdt"] = pd.to_datetime(F["announced_on"], errors="coerce"); F = F.dropna(subset=["fdt"]).sort_values(["entity_uuid", "fdt"]); F["amt"] = pd.to_numeric(F["raised_amount_usd"], errors="coerce")
FUND = {k: (g["fdt"].to_numpy(), g["amt"].to_numpy(float)) for k, g in F.groupby("entity_uuid")}
fv = pd.read_parquet(os.path.join(FORMD, "fund_vehicle_to_investor_v2.parquet"))
sub = pd.read_parquet(os.path.join(FORMD, "FORMDSUBMISSION.parquet"), columns=["ACCESSIONNUMBER", "FILING_DATE", "FILE_NUM"])
# [코드 검토 정정 2026-09-09] FILING_DATE 는 2020Q3 부터 '30-SEP-2020' 형식 — format="mixed" 로 파싱하지 않으면 34% 가 NaT 로 탈락했다.
sub["fdt"] = pd.to_datetime(sub["FILING_DATE"], errors="coerce", format="mixed")
assert sub["fdt"].notna().mean() > 0.999, f"FILING_DATE 파싱 실패율 {1 - sub['fdt'].notna().mean():.4f}"
t1all = fv[fv["tier"].eq("T1_use")].merge(sub, on="ACCESSIONNUMBER", how="left")
t1all["amt"] = pd.to_numeric(t1all["TOTALAMOUNTSOLD"], errors="coerce")
t1 = t1all[~t1all["is_amend"]].copy()
t1["vdt"] = pd.to_datetime(t1["SALE_DATE"], errors="coerce", format="mixed").fillna(t1["fdt"])
assert t1["vdt"].notna().all(), "T1 신규 공시의 빈티지 일자 결측"
t1 = t1.sort_values(["investor_uuid", "vdt"])
FD = {k: g["vdt"].to_numpy() for k, g in t1.groupby("investor_uuid")}
# 모집액: 수정 공시 포함, 발행사 파일번호(FILE_NUM)별로 시점 t 까지 보고된 최대 TOTALAMOUNTSOLD 를 합산 (최초 공시는 60% 가 0 — 검토 지적)
t1all = t1all.dropna(subset=["fdt"]).sort_values(["investor_uuid", "fdt"])
FDA = {k: (g["fdt"].to_numpy(), g["FILE_NUM"].to_numpy(), g["amt"].fillna(0).to_numpy(float)) for k, g in t1all.groupby("investor_uuid")}


def fd_amount(inv, t64):
    if inv not in FDA: return 0.0
    dts, fn, am = FDA[inv]; k = int(np.searchsorted(dts, t64, side="right"))
    if k == 0: return 0.0
    return float(pd.Series(am[:k]).groupby(fn[:k]).max().sum())


log(f"[소스] CB funds 운용사 {len(FUND):,} · Form D T1 운용사 {len(FD):,} · T1 신규 공시 {len(t1):,} (수정 포함 {len(t1all):,})")


def fund_state(df, inv_col="investor_uuid", dt_col="dt"):
    """딜 시점 이전 정보만: CB 펀드 상태 + Form D T1 상태 (결측 지시자 포함)."""
    a, sz, sq, cum, fdn, fda, fdm = [], [], [], [], [], [], []
    for inv, t in zip(df[inv_col], df[dt_col]):
        t64 = np.datetime64(t)
        if inv in FUND:
            dts, amts = FUND[inv]; k = int(np.searchsorted(dts, t64, side="right"))
            a.append((t64 - dts[k - 1]) / np.timedelta64(365, "D") if k else np.nan); sz.append(amts[k - 1] if k else np.nan); sq.append(k); cum.append(float(np.nansum(amts[:k])) if k else 0.0)
        else:
            a.append(np.nan); sz.append(np.nan); sq.append(0); cum.append(0.0)
        if inv in FD:
            dts = FD[inv]; k = int(np.searchsorted(dts, t64, side="right"))
            fdn.append(k); fda.append((t64 - dts[k - 1]) / np.timedelta64(365, "D") if k else np.nan)
        else:
            fdn.append(0); fda.append(np.nan)
        fdm.append(fd_amount(inv, t64))
    o = df.copy()
    o["fund_age"] = np.array(a, float); o["fund_age_m"] = o["fund_age"].isna().astype(float); o["fund_age_f"] = o["fund_age"].fillna(0)
    o["ln_fund_size"] = np.log1p(np.array(sz, float)); o["fund_size_m"] = o["ln_fund_size"].isna().astype(float); o["ln_fund_size_f"] = o["ln_fund_size"].fillna(0)
    o["fund_seq"] = np.array(sq, float); o["has_prior_fund"] = (o["fund_seq"] > 0).astype(float); o["ln_cum_fund"] = np.log1p(np.array(cum, float))
    o["fd_n_before"] = np.array(fdn, float); o["fd_any"] = (o["fd_n_before"] > 0).astype(float)
    o["fd_age"] = np.array(fda, float); o["fd_age_m"] = o["fd_age"].isna().astype(float); o["fd_age_f"] = o["fd_age"].fillna(0); o["ln_fd_amount"] = np.log1p(np.array(fdm, float))
    return o


# [코드 검토 정정] fund_age_m ≡ 1 − has_prior_fund, fd_age_m ≡ 1 − fd_any (완전 공선) → 결측 지시자는 보유 지시자로 대체
CBV = ["fund_age_f", "ln_fund_size_f", "fund_size_m", "fund_seq", "has_prior_fund"]
FDV = ["fd_n_before", "fd_age_f", "ln_fd_amount", "fd_any"]

# ══════════════════════════ P1 라운드 내 재참여 + 투자자 펀드 통제 ══════════════════════════
log("\n" + "=" * 100 + "\n[P1] 라운드 내 재참여 — 투자자 펀드 통제 (CB funds · Form D T1)\n" + "=" * 100)
d = load_sample(); om = org_maps(d); R = equity_rounds(set(d["org_uuid"]))
R0 = R[(R["rdt"] >= "2010-01-01") & (R["rdt"] <= "2020-10-31")].copy(); R0["ff"] = R0["org_uuid"].map(om["ff"]); R0["next36"] = ((R0["next_dt"] - R0["rdt"]).dt.days <= 1095).fillna(False).astype(float)
I = investor_rows(R0["uuid"]); pt = partner_gender_rows(R0["uuid"])
pa = pt.groupby(["funding_round_uuid", "investor_uuid"]).agg(fp=("fp", "max"), fp_min=("fp", "min")).reset_index()
X = I.merge(pa, on=["funding_round_uuid", "investor_uuid"], how="inner").merge(R0[["uuid", "org_uuid", "rdt", "ff", "next_uuid", "next36"]], left_on="funding_round_uuid", right_on="uuid")
X = X.merge(investor_experience(), on=["funding_round_uuid", "investor_uuid"], how="left"); X["ln_exp"] = np.log1p(X["exp_before"].fillna(0))
inv_next = investor_rows(set(R0["next_uuid"].dropna())).groupby("funding_round_uuid")["investor_uuid"].agg(set).to_dict()
X["y1"] = [1.0 if (isinstance(nu, str) and inv in inv_next.get(nu, set())) else 0.0 for nu, inv in zip(X["next_uuid"], X["investor_uuid"])]
g = X.groupby("funding_round_uuid")["fp"].agg(["mean", "size"]); mixed = g.index[(g["mean"] > 0) & (g["mean"] < 1) & (g["size"] >= 2)]
M = X[X["funding_round_uuid"].isin(mixed) & (X["next36"] == 1)].copy(); M["firm"] = M["org_uuid"]
FF = fund_state(M[M["ff"] == 1].copy(), dt_col="rdt")
fo = FF[~((FF["fp"] == 1) & (FF["fp_min"] == 0))]; gr = fo.groupby("funding_round_uuid")["fp"].agg(["mean", "size"]); fo = fo[fo["funding_round_uuid"].isin(gr.index[(gr["mean"] > 0) & (gr["mean"] < 1) & (gr["size"] >= 2)])].copy()
log(f"  FF 조건 행 {len(FF):,} (라운드 {FF['funding_round_uuid'].nunique()}) · CB 펀드 기록 {FF['has_prior_fund'].mean():.3f} · Form D T1 커버 {FF['fd_any'].mean():.3f}")


def band(v, pm=0.05):
    v = dict(v); v["within_pm0.05"] = bool(v["ci95"][0] >= -pm and v["ci95"][1] <= pm); return v


def ffreg(df, extra, tag):
    r = boot(df, "y1", ["fp"] + list(extra), ["fp"], rng, nb=NB, demean="funding_round_uuid", cluster="firm", min_n=50)
    if not r: return None
    o = {"fp": band(r["fp"]), "n": r["n"], "n_clusters": r["n_firms"], "controls": list(extra)}
    v = o["fp"]; log(f"  {tag:<44} b {v['coef']*100:+.2f}pp [{v['ci95'][0]*100:+.2f},{v['ci95'][1]*100:+.2f}] MDE {v['mde80']*100:.2f} ±5 {v['within_pm0.05']} n={r['n']:,}")
    return o


P1 = {"coverage": {"n_rows": int(len(FF)), "n_rounds": int(FF["funding_round_uuid"].nunique()), "cb_has_prior_fund": round(float(FF["has_prior_fund"].mean()), 4), "fd_any": round(float(FF["fd_any"].mean()), 4)}}
for lab, extra in (("baseline", ["ln_exp"]), ("cb_funds", ["ln_exp"] + CBV), ("formd", ["ln_exp"] + FDV), ("both", ["ln_exp"] + CBV + FDV)):
    P1[lab] = {"any_female": ffreg(FF, extra, f"P1 {lab} any-female"), "female_only": ffreg(fo, extra, f"P1 {lab} female-only")}
    if lab != "baseline":
        P1[lab]["shift_any_pp"] = round((P1[lab]["any_female"]["fp"]["coef"] - P1["baseline"]["any_female"]["fp"]["coef"]) * 100, 3)
        P1[lab]["shift_fo_pp"] = round((P1[lab]["female_only"]["fp"]["coef"] - P1["baseline"]["female_only"]["fp"]["coef"]) * 100, 3)
P1["balance"] = {}; P1["positive_controls"] = {}
for c in ("fund_age", "ln_fund_size", "fund_seq", "has_prior_fund", "fd_n_before", "fd_any", "ln_fd_amount"):
    dd = FF.dropna(subset=[c])
    rb = boot(dd, c, ["fp"], ["fp"], rng, nb=NB, demean="funding_round_uuid", cluster="firm", min_n=50)
    if rb:
        sd = float(dd[c].std()); rb["fp"]["std_diff"] = round(rb["fp"]["coef"] / sd, 4) if sd > 0 else None; P1["balance"][c] = {"fp": rb["fp"], "n": rb["n"]}
    rp = boot(dd, "y1", [c], [c], rng, nb=NB, demean="funding_round_uuid", cluster="firm", min_n=50)
    if rp:
        P1["positive_controls"][c] = {"coef": rp[c], "n": rp["n"]}
        log(f"  {c:<14} fp 차 {rb['fp']['coef']:+.4f} [{rb['fp']['ci95'][0]:+.4f},{rb['fp']['ci95'][1]:+.4f}] (d {rb['fp']['std_diff']}) · y1 ← {c} {rp[c]['coef']:+.4f} [{rp[c]['ci95'][0]:+.4f},{rp[c]['ci95'][1]:+.4f}] n={rp['n']:,}")
OUT["P1_within_round_fund_controls"] = P1

# ══════════════════════════ P2 회사 간 연관의 분해 ══════════════════════════
log("\n" + "=" * 100 + "\n[P2] §6 Mundlak between(fm_terrain) — 회사 펀드 규모·순번 통제\n" + "=" * 100)
dn = load_deals(with_exit_dt=True); first = first_deal_dates()
P, h = partner_pre(dn, "exit3"); P = add_post(P, dn, "exit3", end=END_FON); P = add_tenure(P, first=first); P = add_firm_means(P, TC + ["terrain", "adj"])
P["dt"] = CUT; P = fund_state(P, inv_col="firm", dt_col="dt")
P = P.rename(columns={"fund_age_f": "fund_age_cut_f", "fund_age_m": "fund_age_cut_m", "ln_cum_fund": "ln_cum_usd_cut", "fund_seq": "fund_seq_cut", "has_prior_fund": "any_fund_cut", "fd_n_before": "fd_n_cut", "ln_fd_amount": "ln_fd_amount_cut", "fd_any": "fd_any_cut"})
FIRM_CB = ["fund_seq_cut", "ln_cum_usd_cut", "fund_age_cut_f", "any_fund_cut"]; FIRM_FD = ["fd_n_cut", "ln_fd_amount_cut", "fd_any_cut"]   # fund_age_cut_m 제거(≡ 1 − any_fund_cut)
P2 = {"n_partners": int(len(P)), "n_firms": int(P["firm"].nunique()), "firm_cb_any_fund": round(float(P["any_fund_cut"].mean()), 4), "firm_fd_any": round(float(P["fd_any_cut"].mean()), 4)}
log(f"  파트너 {len(P):,} · 회사 {P['firm'].nunique():,} · CB 펀드 있음 {P2['firm_cb_any_fund']:.3f} · Form D T1 있음 {P2['firm_fd_any']:.3f}")


def contrast(res, a, b):
    dd = res["_draws"][:, res["_xc"].index(a)] - res["_draws"][:, res["_xc"].index(b)]; pt_ = res["_b"][res["_xc"].index(a)] - res["_b"][res["_xc"].index(b)]
    lo, hi = qci(dd); return {"coef": round(float(pt_), 5), "ci95": [round(lo, 5), round(hi, 5)], "sig": bool(lo > 0 or hi < 0)}


base_x = ["dev_terrain", "fm_terrain", "adj", "ln_n", "fp"] + TEN
for lab, extra in (("baseline", []), ("firm_cb", FIRM_CB), ("firm_formd", FIRM_FD), ("firm_both", FIRM_CB + FIRM_FD)):
    r = boot(P, "post_adj", base_x + extra, ["dev_terrain", "fm_terrain"] + extra, rng, nb=NB, return_draws=True)
    P2[lab] = strip_draws(r); P2[lab]["contrast_within_minus_between"] = contrast(r, "dev_terrain", "fm_terrain")
    log(f"  {lab:<10} fm_terrain {r['fm_terrain']['coef']:+.3f} [{r['fm_terrain']['ci95'][0]:+.3f},{r['fm_terrain']['ci95'][1]:+.3f}] · dev {r['dev_terrain']['coef']:+.3f} · 대비 {P2[lab]['contrast_within_minus_between']['coef']:+.3f} {P2[lab]['contrast_within_minus_between']['ci95']} · n {r['n']:,}"
        + ("" if not extra else " · " + " ".join(f"{c} {r[c]['coef']:+.3f}{'*' if r[c]['sig'] else ''}" for c in extra)))
Pf = P.drop_duplicates("firm").copy(); Pf["one"] = 1.0
rf = boot(Pf, "fm_terrain", FIRM_CB + FIRM_FD, FIRM_CB + FIRM_FD, rng, nb=NB, cluster="firm", min_n=100)
b_ = fit(Pf, "fm_terrain", FIRM_CB + FIRM_FD); Xm = np.column_stack([Pf[c].to_numpy(float) for c in FIRM_CB + FIRM_FD] + [np.ones(len(Pf))]); yhat = Xm @ b_
r2 = 1 - float(((Pf["fm_terrain"] - yhat) ** 2).sum() / ((Pf["fm_terrain"] - Pf["fm_terrain"].mean()) ** 2).sum())
P2["fm_terrain_on_firm_vars"] = {"r2": round(r2, 4), "n_firms": int(len(Pf)), "coefs": {c: rf[c] for c in FIRM_CB + FIRM_FD}}
log(f"  fm_terrain ~ 회사 변수: R² {r2:.4f} · " + " ".join(f"{c} {rf[c]['coef']:+.4f}{'*' if rf[c]['sig'] else ''}" for c in FIRM_CB + FIRM_FD))
P2["fm_terrain_drop_share_both"] = round(1 - P2["firm_both"]["fm_terrain"]["coef"] / P2["baseline"]["fm_terrain"]["coef"], 4) if P2["baseline"]["fm_terrain"]["coef"] else None
OUT["P2_between_firm_decomposition"] = P2

# ══════════════════════════ P3 특허 ══════════════════════════
log("\n" + "=" * 100 + "\n[P3] 특허(PatentsView v2) — 식별 셀 균형 · 파트너 내 검정의 회사 통제\n" + "=" * 100)
pat = pd.read_parquet(os.path.join(PAT, "deal_pre_round_patents_v2.parquet"), columns=["funding_round_uuid", "org_uuid", "n_app_before", "n_grant_before", "any_patent_before", "matched_assignee"])
pat["ln_app_before"] = np.log1p(pat["n_app_before"])
# (a) 식별 셀 위 균형 (P001-52 정의: FF NAEU ≤2017-10, cell_cat 혼합 셀 중 다중 라운드)
ffb = d[(d["ff"] == 1) & (d["dt"] <= CUT)].merge(pat, on=["funding_round_uuid", "org_uuid"], how="left")
for c in ("any_patent_before", "ln_app_before", "matched_assignee"): ffb[c] = ffb[c].fillna(0.0)
gc = ffb.groupby("cell_cat")["fp"].agg(["mean", "size"]); mixed_c = gc.index[(gc["mean"] > 0) & (gc["mean"] < 1)]
mc = ffb[ffb["cell_cat"].isin(mixed_c)]; nr = mc.groupby("cell_cat")["funding_round_uuid"].nunique(); multi = set(nr.index[nr >= 2]); mm = mc[mc["cell_cat"].isin(multi)].copy()
P3 = {"balance_identifying_cells": {"n_cells": int(mm["cell_cat"].nunique()), "n_deals": int(len(mm)), "covs": {}}, "balance_all_mixed_cells": {"n_cells": int(len(mixed_c)), "n_deals": int(len(mc)), "covs": {}}}
for frame_lab, frame in (("balance_identifying_cells", mm), ("balance_all_mixed_cells", mc)):
    for c in ("any_patent_before", "ln_app_before", "matched_assignee"):
        r = boot(frame.assign(firm=frame["investor_uuid"]), c, ["fp"], ["fp"], rng, nb=NB, demean="cell_cat", cluster="firm", min_n=50)
        if r:
            sd = float(frame[c].std()); v = dict(r["fp"]); v["std_diff"] = round(v["coef"] / sd, 4) if sd > 0 else None; v["ci95_sd"] = [round(x / sd, 4) for x in v["ci95"]] if sd > 0 else None; v["mde80_sd"] = round(v["mde80"] / sd, 4) if sd > 0 else None
            P3[frame_lab]["covs"][c] = {"fp": v, "n": r["n"], "mean_male": round(float(frame.loc[frame["fp"] == 0, c].mean()), 4)}
            log(f"  {frame_lab:<26} {c:<18} fp 차 {v['coef']:+.4f} [{v['ci95'][0]:+.4f},{v['ci95'][1]:+.4f}] d {v['std_diff']} MDE(sd) {v['mde80_sd']} n={r['n']:,}")
# (b) 파트너 내 결과 검정 exit3 + 특허 통제 (P001-54 사양 재구성)
r_ = CTX.rounds[["uuid", "raised_amount_usd", "investor_count", "org_uuid", "announced_on"]].copy(); r_["rdt"] = pd.to_datetime(r_["announced_on"], errors="coerce")
dn2 = dn.merge(r_[["uuid", "raised_amount_usd", "investor_count"]], left_on="funding_round_uuid", right_on="uuid", how="left", suffixes=("", "_r"))
orgs = CTX.orgs[["uuid", "founded_on"]].copy(); orgs["fy"] = pd.to_datetime(orgs["founded_on"], errors="coerce").dt.year
dn2["age"] = (dn2["dt"].dt.year - dn2["org_uuid"].map(orgs.set_index("uuid")["fy"])).clip(0, 50)
ro = r_.dropna(subset=["org_uuid", "rdt"]).sort_values(["org_uuid", "rdt"]); org_dates = {o: g_["rdt"].to_numpy() for o, g_ in ro.groupby("org_uuid")}
dn2["prior"] = [np.searchsorted(org_dates.get(o, np.array([], dtype="datetime64[ns]")), np.datetime64(t)) for o, t in zip(dn2["org_uuid"], dn2["dt"])]
inv = CTX.inv.dropna(subset=["funding_round_uuid", "investor_uuid"]); icnt = inv.groupby("investor_uuid").size()
ie = inv.copy(); ie["lc"] = np.log1p(ie["investor_uuid"].map(icnt)); rs = ie.groupby("funding_round_uuid")["lc"].agg(["sum", "count"])
dn2 = dn2.merge(rs, left_on="funding_round_uuid", right_index=True, how="left"); own = np.log1p(dn2["investor_uuid"].map(icnt).fillna(0))
dn2["coexp"] = np.where(dn2["count"] > 1, (dn2["sum"] - own) / (dn2["count"] - 1), np.nan)
dn2["x_amt"] = np.log1p(pd.to_numeric(dn2["raised_amount_usd"], errors="coerce")); dn2["x_ic"] = np.log1p(pd.to_numeric(dn2["investor_count"], errors="coerce"))
COVS = []
for c in ("x_amt", "age", "coexp", "x_ic"):
    dn2[c + "_m"] = dn2[c].isna().astype(float); dn2[c] = dn2[c].fillna(0); COVS += [c, c + "_m"]
dn2["x_prior"] = np.log1p(dn2["prior"]); COVS.append("x_prior"); dn2["ffp"] = dn2["ff"] * dn2["fp"]
dn2 = dn2.merge(pat, on=["funding_round_uuid", "org_uuid"], how="left")
for c in ("any_patent_before", "ln_app_before", "matched_assignee"): dn2[c] = dn2[c].fillna(0.0)
s = build(dn2[dn2["dt"] <= END_FON].copy(), "exit3"); both = s.groupby("partner_uuid")["ff"].agg(["min", "max"]); s = s[s["partner_uuid"].isin(both.index[(both["min"] == 0) & (both["max"] == 1)])].dropna(subset=["r"]).copy()
PATV = ["any_patent_before", "ln_app_before", "matched_assignee"]
W = {}
for lab, extra in (("baseline", []), ("patents", PATV)):
    r = boot(s, "r", ["ff", "ffp"] + COVS + extra, ["ff", "ffp"] + extra, rng, nb=NB, demean="partner_uuid", cluster="partner_uuid", min_n=500)
    sd = float(s["r"].std()); r["ffp"]["beta_std"] = round(r["ffp"]["coef"] / sd, 4); r["ffp"]["within_pm0.05"] = bool(r["ffp"]["ci95"][0] >= -0.05 and r["ffp"]["ci95"][1] <= 0.05)
    W[lab] = r; log(f"  P3b {lab:<9} β_int {r['ffp']['coef']*100:+.2f}pp [{r['ffp']['ci95'][0]*100:+.2f},{r['ffp']['ci95'][1]*100:+.2f}] MDE {r['ffp']['mde80']*100:.2f} · β_FF {r['ff']['coef']*100:+.2f} · n {r['n']:,}"
                  + ("" if not extra else " · " + " ".join(f"{c} {r[c]['coef']*100:+.2f}pp{'*' if r[c]['sig'] else ''}" for c in extra)))
W["shift_pp"] = round((W["patents"]["ffp"]["coef"] - W["baseline"]["ffp"]["coef"]) * 100, 3)
W["deal_coverage"] = {"matched_assignee": round(float(s["matched_assignee"].mean()), 4), "any_patent_before": round(float(s["any_patent_before"].mean()), 4)}
P3["within_partner_exit3"] = W
OUT["P3_patents"] = P3

# ══════════════════════════ 판정 ══════════════════════════
b0a, b0f = P1["baseline"]["any_female"]["fp"]["coef"], P1["baseline"]["female_only"]["fp"]["coef"]
pred = {"P1_cb_shift_any_lt_0.6": abs(P1["cb_funds"]["shift_any_pp"]) < 0.6, "P1_cb_shift_fo_lt_0.8": abs(P1["cb_funds"]["shift_fo_pp"]) < 0.8,
        "P1_fd_shift_any_lt_0.6": abs(P1["formd"]["shift_any_pp"]) < 0.6, "P1_fd_cov_0.25_0.45": 0.25 <= P1["coverage"]["fd_any"] <= 0.45,
        "P1_fund_age_neg_detected": bool(P1["positive_controls"].get("fund_age") and P1["positive_controls"]["fund_age"]["coef"]["sig"] and P1["positive_controls"]["fund_age"]["coef"]["coef"] < 0),
        "P1_fund_seq_size_not_detected": all(not P1["positive_controls"][c]["coef"]["sig"] for c in ("fund_seq", "ln_fund_size") if c in P1["positive_controls"]),
        "P2_baseline_reproduces_0.435": abs(P2["baseline"]["fm_terrain"]["coef"] - 0.43452) < 0.01, "P2_fm_both_in_[0.30,0.50]": 0.30 <= P2["firm_both"]["fm_terrain"]["coef"] <= 0.50,
        "P2_contrast_still_sig": bool(P2["firm_both"]["contrast_within_minus_between"]["sig"]), "P2_r2_lt_0.10": P2["fm_terrain_on_firm_vars"]["r2"] < 0.10,
        "P3a_any_patent_diff_in_pm0.10_ns": bool(P3["balance_identifying_cells"]["covs"].get("any_patent_before") and -0.10 <= P3["balance_identifying_cells"]["covs"]["any_patent_before"]["fp"]["coef"] <= 0.10 and not P3["balance_identifying_cells"]["covs"]["any_patent_before"]["fp"]["sig"]),
        "P3b_shift_lt_0.3pp": abs(W["shift_pp"]) < 0.3, "P3b_any_patent_pos_detected": bool(W["patents"]["any_patent_before"]["sig"] and 0.02 <= W["patents"]["any_patent_before"]["coef"] <= 0.06)}
pred = {k: bool(v) for k, v in pred.items()}
OUT["prediction_check"] = pred
verdict = (f"P1: any-female {b0a*100:+.2f} → CB {P1['cb_funds']['any_female']['fp']['coef']*100:+.2f} · FormD {P1['formd']['any_female']['fp']['coef']*100:+.2f} · both {P1['both']['any_female']['fp']['coef']*100:+.2f}; female-only {b0f*100:+.2f} → both {P1['both']['female_only']['fp']['coef']*100:+.2f} (밴드 {P1['both']['female_only']['fp']['within_pm0.05']}); Form D 커버 {P1['coverage']['fd_any']:.2f} | "
           f"P2: fm_terrain {P2['baseline']['fm_terrain']['coef']:+.3f} → 회사 변수 투입 {P2['firm_both']['fm_terrain']['coef']:+.3f} [{P2['firm_both']['fm_terrain']['ci95'][0]:+.3f},{P2['firm_both']['fm_terrain']['ci95'][1]:+.3f}] (감소 {P2['fm_terrain_drop_share_both']}), 대비 {P2['firm_both']['contrast_within_minus_between']['coef']:+.3f} sig {P2['firm_both']['contrast_within_minus_between']['sig']}, R² {P2['fm_terrain_on_firm_vars']['r2']:.3f} | "
           f"P3: 식별 셀 any_patent fp 차 {P3['balance_identifying_cells']['covs']['any_patent_before']['fp']['coef']:+.3f} (d {P3['balance_identifying_cells']['covs']['any_patent_before']['fp']['std_diff']}); β_int {W['baseline']['ffp']['coef']*100:+.2f} → {W['patents']['ffp']['coef']*100:+.2f} · any_patent → r {W['patents']['any_patent_before']['coef']*100:+.2f}pp (예측 적중 {sum(pred.values())}/{len(pred)})")
emit("P001-58", "공개 소스 변수 투입: 라운드 내 펀드 통제(CB funds·Form D T1) · §6 between 분해 · 특허 균형/통제(PatentsView v2)", "OK", OUT,
     prediction="P1 이동<0.6/0.8pp, fd 커버 0.25–0.45, fund_age 음 검출; P2 fm 0.435 재현, 회사 변수 후 [0.30,0.50], 대비 유지, R²<0.10; P3 any_patent 차 ±0.10 미검출, β_int 이동<0.3, any_patent→r +2~6pp",
     verdict=verdict, kill_met=False, n=int(len(FF)),
     extra={"stage": 7, "feeds": "R5 F-3/R5-4/R5-1 후속 · §4 ¶3 · §6 · Table 10 A/B · Table 4 B", "slug": "public_sources_controls", "builds_on": "P001-51/56/38/52/54; cb_funds_v1; formd_v1 T1; patents_v1 v2",
            "common_sha256_16": COMMON_SHA, "v6_common_sha256_16": V6_SHA})
log("done")
