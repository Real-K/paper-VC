# -*- coding: utf-8 -*-
"""p001_39 — CP-1: 재직연차·직급을 jobs 테이블의 관측 합류일·직함으로 직접 측정 (첫 귀속 딜 대리 교체)

[왜] R3 식별 심판 CP-1: §6 의 연공 대리(첫 귀속 딜)는 귀속 커버리지에 좌측 절단되고 빈티지 성분과 0.60 상관한다 — R2 MAJOR 의
 원인. 그런데 CTX.jobs(person_uuid, org_uuid, started_on, ended_on, title)가 이미 로드되어 §5 의 사건 일자에 쓰이고 있고,
 심판 계산으로 표본 파트너 2,686 중 2,631 이 홈 회사 job 행을, 2,351(87.5%)이 started_on 을 갖는다. 검증 후 교체 재추정한다.
 이는 PitchBook pull3 의 1순위 사유를 대부분 제거한다(스펙 v2 §1 행 1).

[구성] 파트너 p · 홈 회사 f (사전기 최다 귀속 회사). jobs 에서 (p, f) 행 중 가장 이른 started_on = 합류일.
 tenure_j = (기준일 − 합류일)/365.25 (기준일 CUT; 딜 수준은 딜일). rank ← title 정규화:
   senior = partner/general partner/managing partner/managing director/founder/co-founder/president/ceo/chief …
   mid    = principal/vice president/director(단독)/investment director
   junior = associate/analyst/senior associate
   venture= venture partner/operating partner/advisor/board … · other = 그 외/결측
 검산: (첫 귀속 딜 − 합류일) 분포(음수 비중 = 합류 전 귀속) · corr(tenure_j, tenure_첫딜).
[Panel]
 A. 커버리지·검산
 B. 개방지평(P001-30 R2/R2t 사양) — 매칭 부분표본에서 (i) TEN 판 (ii) jobs 판(tenure_j, tenure_j², rank FE) → 차이는 측정 때문
 C. 고정지평(P001-33 A F2/F2t/F3) — jobs 판; F3(회사 FE)+jobs
 D. 성별: fp → 성분·terrain | jobs 연공·직급 (P001-36 G2 유사물)
 E. 관측 선택: has_post ← 성분 + tenure_j + rank (R7 유사물) — 빈티지 성분 적재의 이동
[사전 예측] (2026-09-09, 결과 조회 전)
 A: 합류일 커버리지 ≥ 80%; corr(tenure_j, tenure_첫딜) 0.5–0.7; 합류 전 귀속(음수) < 15%.
 B: jobs 판 총 terrain ∈ [0.05, 0.12], CI 0 포함 가능(개방지평의 빈티지 교란은 측정 교체로 안 사라짐).
 C: 고정지평 jobs 판 F2t ∈ [0.20, 0.32], 하한 > 0; F3+jobs 는 여전히 0 포함(MDE 큼).
 D: fp → terrain | jobs ∈ [−0.03, 0], CI 0 포함; 직급 통제가 연공 통제와 같은 방향으로 격차를 줄인다.
 E: 선택의 빈티지 성분 적재 |t_v| 가 R7 의 2.19 에서 줄지만 남는다(빈티지 = 은퇴 서명은 연공 측정과 무관한 부분 포함).
[판정] 진단·교체 재추정 — status OK.
"""
import re

import numpy as np
import pandas as pd

from p001_rescue_common import (COMMON_SHA, CTX, CUT, END_FON, TC, TEN, add_post, add_tenure, boot, emit, first_deal_dates, fmt,
                                load_deals, log, partner_pre, show)

rng = np.random.default_rng(20260939)
OUT = {}
dn = load_deals(with_exit_dt=True)
first = first_deal_dates()

# ── jobs 매핑 ───────────────────────────────────────────────────────────────
J = CTX.jobs
cols = {c.lower(): c for c in J.columns}
pc, oc, sc, ec, tc = cols.get("person_uuid"), cols.get("org_uuid"), cols.get("started_on"), cols.get("ended_on"), cols.get("title")
J = J.dropna(subset=[pc, oc]).copy()
J["sdt"] = pd.to_datetime(J[sc], errors="coerce")
J["edt"] = pd.to_datetime(J[ec], errors="coerce") if ec else pd.NaT
J["title_l"] = J[tc].fillna("").astype(str).str.lower() if tc else ""


def rank_of(s):
    s = s.strip()
    if not s:
        return "other"
    if re.search(r"venture partner|operating partner|advisor|adviser|board|mentor|entrepreneur in residence|eir", s):
        return "venture"
    if re.search(r"general partner|managing partner|managing director|founding partner|co-?founder|founder|president|chief|ceo|cio|coo|cfo|partner|head of", s):
        return "senior"
    if re.search(r"principal|vice president|\bvp\b|investment director|\bdirector\b", s):
        return "mid"
    if re.search(r"associate|analyst|intern", s):
        return "junior"
    return "other"


J["rank"] = J["title_l"].map(rank_of)


def attach_jobs(P, ref):
    key = P[["partner_uuid", "firm"]]
    m = key.merge(J, left_on=["partner_uuid", "firm"], right_on=[pc, oc], how="left")
    m = m.sort_values(["partner_uuid", "sdt"])
    agg = m.groupby("partner_uuid").agg(has_job=(oc, lambda s: s.notna().any()), join_dt=("sdt", "min"),
                                        rank=("rank", lambda s: s.dropna().iloc[0] if s.notna().any() else "other"))
    # 직급은 합류일 기준 첫 행 대신 '가장 높은 직급' 을 채택 (동일 회사 승진 이력)
    order = {"senior": 4, "mid": 3, "junior": 2, "venture": 1, "other": 0}
    top = m.groupby("partner_uuid")["rank"].agg(lambda s: max(s.dropna(), key=lambda x: order[x]) if s.notna().any() else "other")
    P = P.join(agg[["has_job", "join_dt"]], on="partner_uuid").join(top.rename("rank_top"), on="partner_uuid")
    P["tenure_j"] = (ref - P["join_dt"]).dt.days / 365.25
    P["tenure_j2"] = P["tenure_j"] ** 2
    for r_ in ("mid", "junior", "venture", "other"):
        P[f"rk_{r_}"] = (P["rank_top"] == r_).astype(float)
    return P


JOBS = ["tenure_j", "tenure_j2", "rk_mid", "rk_junior", "rk_venture", "rk_other"]

# ── A. 커버리지·검산 (개방지평 패널 기준) ──────────────────────────────────
Po, _ = partner_pre(dn, "exit_ever"); Po = add_post(Po, dn, "exit_ever"); Po = add_tenure(Po, first=first); Po = attach_jobs(Po, CUT)
A = {"n_partners": int(len(Po)), "has_home_job_row": int(Po["has_job"].fillna(False).sum()), "has_join_date": int(Po["join_dt"].notna().sum()),
     "share_join_date": round(float(Po["join_dt"].notna().mean()), 4),
     "rank_dist": {k: int(v) for k, v in Po.loc[Po["join_dt"].notna(), "rank_top"].value_counts().items()}}
gap = (Po["first_dt"] - Po["join_dt"]).dt.days / 365.25
A["first_deal_minus_join_years"] = {"median": round(float(gap.median()), 2), "p10": round(float(gap.quantile(0.1)), 2), "p90": round(float(gap.quantile(0.9)), 2),
                                    "share_negative": round(float((gap < 0).mean()), 4)}
A["corr_tenure_j_vs_first_deal"] = round(float(Po[["tenure_j", "tenure"]].corr().iloc[0, 1]), 4)
A["corr_tenure_j_vs_t_v"] = round(float(Po[["tenure_j", "t_v"]].corr().iloc[0, 1]), 4)
A["corr_tenure_j_vs_terrain"] = round(float(Po[["tenure_j", "terrain"]].corr().iloc[0, 1]), 4)
A["median_tenure_j"] = round(float(Po["tenure_j"].median()), 2); A["median_tenure_firstdeal"] = round(float(Po["tenure"].median()), 2)
log(f"[A] 파트너 {A['n_partners']:,} · 홈 회사 job 행 {A['has_home_job_row']:,} · 합류일 {A['has_join_date']:,} ({A['share_join_date']:.1%}) · 직급 {A['rank_dist']}")
log(f"    첫딜−합류 중위 {A['first_deal_minus_join_years']['median']} y (음수 {A['first_deal_minus_join_years']['share_negative']:.1%}) · corr(tenure_j, 첫딜 tenure) {A['corr_tenure_j_vs_first_deal']:+.3f} · "
    f"corr(tenure_j, t_v) {A['corr_tenure_j_vs_t_v']:+.3f} · corr(tenure_j, terrain) {A['corr_tenure_j_vs_terrain']:+.3f} · 중위 연차 jobs {A['median_tenure_j']} vs 첫딜 {A['median_tenure_firstdeal']}")
OUT["A_coverage"] = A

# ── B. 개방지평, 매칭 부분표본: TEN 판 vs jobs 판 ───────────────────────────
log("\n" + "=" * 100 + "\n[B] 개방지평 — 매칭 부분표본에서 TEN 판 vs jobs 판\n" + "=" * 100)
Pm = Po[Po["join_dt"].notna()].copy()
B = {"n_matched": int(len(Pm)), "n_post": int(Pm["has_post"].sum())}
B["R2_TEN"] = boot(Pm, "post_adj", TC + ["adj", "ln_n", "fp"] + TEN, TC, rng); show("B R2 TEN(부분표본)", B["R2_TEN"], TC)
B["R2_jobs"] = boot(Pm, "post_adj", TC + ["adj", "ln_n", "fp"] + JOBS, TC + ["tenure_j"], rng); show("B R2 jobs", B["R2_jobs"], TC + ["tenure_j"])
B["R2_both"] = boot(Pm, "post_adj", TC + ["adj", "ln_n", "fp"] + TEN + JOBS, TC, rng); show("B R2 TEN+jobs", B["R2_both"], TC)
B["R2t_TEN"] = boot(Pm, "post_adj", ["terrain", "adj", "ln_n", "fp"] + TEN, ["terrain"], rng); show("B R2t TEN", B["R2t_TEN"], ["terrain"])
B["R2t_jobs"] = boot(Pm, "post_adj", ["terrain", "adj", "ln_n", "fp"] + JOBS, ["terrain"], rng); show("B R2t jobs", B["R2t_jobs"], ["terrain"])
B["R2t_both"] = boot(Pm, "post_adj", ["terrain", "adj", "ln_n", "fp"] + TEN + JOBS, ["terrain"], rng); show("B R2t TEN+jobs", B["R2t_both"], ["terrain"])
OUT["B_open_horizon"] = B

# ── C. 고정지평 (P001-33 A) jobs 판 ────────────────────────────────────────
log("\n" + "=" * 100 + "\n[C] 고정 출구지평 — jobs 판 F2/F2t/F3\n" + "=" * 100)
Pf, _ = partner_pre(dn, "exit3"); Pf = add_post(Pf, dn, "exit3", end=END_FON); Pf = add_tenure(Pf, first=first); Pf = attach_jobs(Pf, CUT)
Pfm = Pf[Pf["join_dt"].notna()].copy()
C = {"n_matched": int(len(Pfm)), "n_post": int(Pfm["has_post"].sum())}
C["F2_TEN"] = boot(Pfm, "post_adj", TC + ["adj", "ln_n", "fp"] + TEN, TC, rng); show("C F2 TEN(부분표본)", C["F2_TEN"], TC)
C["F2_jobs"] = boot(Pfm, "post_adj", TC + ["adj", "ln_n", "fp"] + JOBS, TC + ["tenure_j"], rng); show("C F2 jobs", C["F2_jobs"], TC + ["tenure_j"])
C["F2t_TEN"] = boot(Pfm, "post_adj", ["terrain", "adj", "ln_n", "fp"] + TEN, ["terrain", "adj"], rng); show("C F2t TEN", C["F2t_TEN"], ["terrain", "adj"])
C["F2t_jobs"] = boot(Pfm, "post_adj", ["terrain", "adj", "ln_n", "fp"] + JOBS, ["terrain", "adj"], rng); show("C F2t jobs", C["F2t_jobs"], ["terrain", "adj"])
C["F2t_both"] = boot(Pfm, "post_adj", ["terrain", "adj", "ln_n", "fp"] + TEN + JOBS, ["terrain"], rng); show("C F2t TEN+jobs", C["F2t_both"], ["terrain"])
C["F3t_jobs"] = boot(Pfm, "post_adj", ["terrain", "adj", "ln_n", "fp"] + JOBS, ["terrain"], rng, demean="firm"); show("C F3t 회사FE+jobs", C["F3t_jobs"], ["terrain"])
C["F3_jobs"] = boot(Pfm, "post_adj", TC + ["adj", "ln_n", "fp"] + JOBS, TC, rng, demean="firm"); show("C F3 회사FE+jobs", C["F3_jobs"], TC)
OUT["C_fixed_horizon"] = C

# ── D. 성별 격차 | jobs 연공·직급 ───────────────────────────────────────────
log("\n" + "=" * 100 + "\n[D] fp → 성분·terrain | jobs 연공·직급 (개방지평 패널, 매칭 부분표본)\n" + "=" * 100)
D = {}
for k in TC + ["terrain", "adj"]:
    D[k] = {"raw": boot(Pm, k, ["fp", "ln_n"], ["fp"], rng), "TEN": boot(Pm, k, ["fp", "ln_n"] + TEN, ["fp"], rng),
            "jobs": boot(Pm, k, ["fp", "ln_n"] + JOBS, ["fp"], rng), "rank_only": boot(Pm, k, ["fp", "ln_n", "rk_mid", "rk_junior", "rk_venture", "rk_other"], ["fp"], rng)}
    log(f"  fp → {k:<8} raw {fmt(D[k]['raw'], 'fp')} · TEN {fmt(D[k]['TEN'], 'fp')} · jobs {fmt(D[k]['jobs'], 'fp')} · 직급만 {fmt(D[k]['rank_only'], 'fp')}")
D["fp_share_by_rank"] = {r_: round(float(Pm.loc[Pm["rank_top"] == r_, "fp"].mean()), 4) for r_ in ("senior", "mid", "junior", "venture", "other") if (Pm["rank_top"] == r_).any()}
D["rank_gap_female_minus_male_tenure_j"] = round(float(Pm.loc[Pm["fp"] == 1, "tenure_j"].mean() - Pm.loc[Pm["fp"] == 0, "tenure_j"].mean()), 3)
log(f"  여성 비중 by 직급 {D['fp_share_by_rank']} · 여−남 tenure_j 차 {D['rank_gap_female_minus_male_tenure_j']:+.2f} y")
OUT["D_gender_given_jobs"] = D

# ── E. 관측 선택 ────────────────────────────────────────────────────────────
log("\n" + "=" * 100 + "\n[E] has_post ← 성분 + jobs 연공·직급\n" + "=" * 100)
E = {"R7_TEN": boot(Pm, "has_post", TC + ["adj", "ln_n", "fp"] + TEN, TC + ["tenure"], rng),
     "R7_jobs": boot(Pm, "has_post", TC + ["adj", "ln_n", "fp"] + JOBS, TC + ["tenure_j"], rng)}
show("E R7 TEN", E["R7_TEN"], TC + ["tenure"]); show("E R7 jobs", E["R7_jobs"], TC + ["tenure_j"])
OUT["E_selection"] = E

# ── 판정 ────────────────────────────────────────────────────────────────────
pred = {"A_coverage_ge_0.80": A["share_join_date"] >= 0.80, "A_corr_0.5_0.7": 0.5 <= A["corr_tenure_j_vs_first_deal"] <= 0.7,
        "A_negative_lt_0.15": A["first_deal_minus_join_years"]["share_negative"] < 0.15,
        "B_R2t_jobs_in_[0.05,0.12]": 0.05 <= B["R2t_jobs"]["terrain"]["coef"] <= 0.12,
        "C_F2t_jobs_in_[0.20,0.32]_lower_gt0": 0.20 <= C["F2t_jobs"]["terrain"]["coef"] <= 0.32 and C["F2t_jobs"]["terrain"]["ci95"][0] > 0,
        "C_F3t_jobs_incl0": not C["F3t_jobs"]["terrain"]["sig"],
        "D_fp_terrain_jobs_in_[-0.03,0]_incl0": -0.03 <= D["terrain"]["jobs"]["fp"]["coef"] <= 0 and not D["terrain"]["jobs"]["fp"]["sig"],
        "E_tv_loading_smaller_but_sig": abs(E["R7_jobs"]["t_v"]["coef"]) < 2.19 and E["R7_jobs"]["t_v"]["sig"]}
pred = {k: bool(v) for k, v in pred.items()}
OUT["prediction_check"] = pred
verdict = (f"jobs 합류일 커버리지 {A['share_join_date']:.1%} ({A['has_join_date']:,}/{A['n_partners']:,}) · corr(tenure_j, 첫딜) {A['corr_tenure_j_vs_first_deal']:+.2f} · 합류 전 귀속 {A['first_deal_minus_join_years']['share_negative']:.1%} | "
           f"개방 R2t: TEN {fmt(B['R2t_TEN'], 'terrain')} → jobs {fmt(B['R2t_jobs'], 'terrain')} → 둘 다 {fmt(B['R2t_both'], 'terrain')} | "
           f"고정 F2t: TEN {fmt(C['F2t_TEN'], 'terrain')} → jobs {fmt(C['F2t_jobs'], 'terrain')} → 둘 다 {fmt(C['F2t_both'], 'terrain')} · 회사FE+jobs {fmt(C['F3t_jobs'], 'terrain')} | "
           f"fp→terrain: raw {fmt(D['terrain']['raw'], 'fp')} · TEN {fmt(D['terrain']['TEN'], 'fp')} · jobs {fmt(D['terrain']['jobs'], 'fp')} · 직급만 {fmt(D['terrain']['rank_only'], 'fp')} | "
           f"선택 t_v: TEN {fmt(E['R7_TEN'], 't_v')} → jobs {fmt(E['R7_jobs'], 't_v')} (예측 적중 {sum(pred.values())}/{len(pred)})")
emit("P001-39", "CP-1: jobs 합류일·직함으로 재직연차·직급 직접 측정 — 개방·고정지평 재추정, 성별 격차, 관측 선택", "OK", OUT,
     prediction="커버리지≥80%; corr 0.5–0.7; 개방 R2t jobs ∈[0.05,0.12]; 고정 F2t jobs ∈[0.20,0.32] 하한>0; F3t 0 포함; fp→terrain|jobs ∈[−0.03,0] ns; 선택 t_v 축소·유지",
     verdict=verdict, kill_met=False, n=int(A["has_join_date"]),
     extra={"stage": 7, "feeds": "R3 재심 응답 (ident.md CP-1); PB 스펙 v2 pull3 재평가", "slug": "jobs_tenure_rank", "builds_on": "P001-30/33/36",
            "common_sha256_16": COMMON_SHA, "jobs_columns_used": [pc, oc, sc, ec, tc]})
log("done")
