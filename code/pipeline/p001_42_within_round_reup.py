# -*- coding: utf-8 -*-
"""p001_42 — P1: 같은 라운드 안의 투자자 수준 결과 검정 — 딜을 문자 그대로 고정한 선별 vs 호의 판별

[왜] §4 의 판별(호의 vs 선별)은 셀 FE 아래 "조건부 미검출"이다. 설계 제안 P1: 한 기업의 한 라운드에 여성 귀속 투자자와
 남성 귀속 투자자가 함께 들어온 경우(혼성 신디케이트), 섹터·단계·빈티지·기업 품질·창업자 성별·라운드 규모·거시가 **구성상 동일**.
 기업 출구는 라운드 공통이므로 결과는 투자자별로 달라지는 것이어야 한다: (y1) 그 투자사가 다음 라운드에 재참여 (y2) 같은 파트너가
 다음 라운드에 재귀속 (y3) 리드 플래그. "기업이 36개월 안에 다음 라운드를 올렸다"는 **라운드 수준 조건**이라 라운드 내 비교를 편향
 시키지 않는다 — 후속 분석의 통상적 선택 문제가 구성상 사라진다. 호의(taste) 는 낮은 초기 문턱 → 후속 시점 사후확률 열위 → 재참여
 열위를 예측한다(방향 가설); 선별은 무차별을 예측한다.

[구성] 모집단: sample_v1 기업(창업자 성별 관측, NAEU 라운드)의 지분형 라운드, 2010-01 ≤ 일자 ≤ 2020-10(36m 창 완결).
 투자자 행 = CTX.inv; 귀속 파트너 성별 = CTX.partners × people; 투자자 행의 fp = 귀속 파트너 중 여성 존재.
 혼성 라운드 = 귀속 투자자 행 ≥2 이고 fp 가 라운드 안에서 변함. ff = 기업(sample_v1). 통제 = 투자자 경험(이전 라운드 수 log1p).
 사양: y = a_round + b_fp·fp + b_int·fp×ff + γ·exp + e (라운드 내 demean; ff 는 라운드 상수). b_FF = b_fp + b_int.
 군집 부트 = 기업(400). 라운드 내 성별 라벨 순열 500 → 양측 p.
[Panel]
 A 표본 구성·기저율(4셀 원시 평균) · 조건화 사건(다음 라운드 36m) 의 4셀 균형
 B y1 재참여(36m, 다음 라운드 有 조건) — FF 라운드 / 비FF 라운드 / 차이 · 순열 p · 등가 밴드 ±5pp(기저 42% 의 12%)
 C y1u 무조건(다음 라운드 없음 = 0)
 D y2 같은 파트너 재귀속(재참여 조건) — 기록 민감 마진
 E y3 리드 플래그(당 라운드) + 커버리지 · 리드 기록률 fp 차
 F 역방향 위약: 이전 라운드 참여 y0 ← fp (관계 이력 선택)
[사전 예측] (2026-09-09, 결과 조회 전)
 A: 혼성 FF 라운드 ≈ 650–720, 투자자-딜 ≈ 2,200–2,400; 다음 라운드 36m 확률 4셀 0.64–0.68.
 B: b_FF ∈ [−0.06, +0.02], CI 0 포함, MDE80 ≈ 4–5pp; 차이(FF−비FF) ∈ [−0.05, +0.02]. 원시 이중차 −3.7pp 는 통제 후 절반 이하.
 D: b_FF(y2|y1) ∈ [−0.08, +0.02]. E: 리드 커버리지 ≈ 60%; 리드 fp 차 ∈ [−0.06, +0.02]. F: |b| < 0.03, CI 0 포함.
[판정] 등가: b_FF CI ⊂ ±0.05 → "±5pp 안에서 차등 재참여 미검출"(rules/11). 결손: 상단 < 0 이고 점추정 < −0.04 → 호의 정합.
 그 외 PARTIAL(MDE 병기). 정보량이 있으면 GO(어느 쪽이든), 아니면 PARTIAL.
"""
import numpy as np
import pandas as pd

from p001_v6_common import (RESCUE_SHA, V6_SHA, boot, emit, equity_rounds, fit, investor_experience, investor_rows, load_sample, log,
                            org_maps, partner_gender_rows, qci)

rng = np.random.default_rng(20260942)
NB, NPERM = 400, 500
OUT = {}
d = load_sample()
om = org_maps(d)
R = equity_rounds(set(d["org_uuid"]))
W0, W1 = pd.Timestamp("2010-01-01"), pd.Timestamp("2020-10-31")
R0 = R[(R["rdt"] >= W0) & (R["rdt"] <= W1)].copy()
R0["ff"] = R0["org_uuid"].map(om["ff"])
R0["next36"] = ((R0["next_dt"] - R0["rdt"]).dt.days <= 1095).fillna(False).astype(float)
log(f"[구성] 표본 기업 지분형 라운드 {len(R):,} · 창 안 {len(R0):,} · 다음 라운드 36m {R0['next36'].mean():.3f}")

# 투자자 행 + 귀속 성별
I = investor_rows(R0["uuid"])
pt = partner_gender_rows(R0["uuid"])
pa = pt.groupby(["funding_round_uuid", "investor_uuid"]).agg(fp=("fp", "max"), n_p=("fp", "size"), partners=("partner_uuid", lambda s: frozenset(s))).reset_index()
X = I.merge(pa, on=["funding_round_uuid", "investor_uuid"], how="inner")
X = X.merge(R0[["uuid", "org_uuid", "rdt", "investment_type", "ff", "next_uuid", "next_dt", "next36", "prev_uuid"]], left_on="funding_round_uuid", right_on="uuid")
exp = investor_experience()
X = X.merge(exp, on=["funding_round_uuid", "investor_uuid"], how="left")
X["ln_exp"] = np.log1p(X["exp_before"].fillna(0))
# 다음 라운드 참여·재귀속, 이전 라운드 참여
inv_all = investor_rows(set(R0["next_uuid"].dropna()) | set(R0["prev_uuid"].dropna()))
next_inv = inv_all.groupby("funding_round_uuid")["investor_uuid"].agg(set).to_dict()
pt_next = partner_gender_rows(set(R0["next_uuid"].dropna()))
next_part = pt_next.groupby(["funding_round_uuid", "investor_uuid"])["partner_uuid"].agg(frozenset).to_dict()
X["y1"] = [1.0 if (isinstance(nu, str) and inv in next_inv.get(nu, set())) else 0.0 for nu, inv in zip(X["next_uuid"], X["investor_uuid"])]
X["y2"] = [1.0 if (isinstance(nu, str) and len(next_part.get((nu, inv), frozenset()) & ps) > 0) else 0.0
           for nu, inv, ps in zip(X["next_uuid"], X["investor_uuid"], X["partners"])]
X["y0"] = [1.0 if (isinstance(pu, str) and inv in next_inv.get(pu, set())) else 0.0 for pu, inv in zip(X["prev_uuid"], X["investor_uuid"])]
X["lead"] = X["is_lead_investor"].map({True: 1.0, False: 0.0})
X["lead_rec"] = X["lead"].notna().astype(float)
# 혼성 라운드
g = X.groupby("funding_round_uuid")["fp"].agg(["mean", "size"])
mixed = g.index[(g["mean"] > 0) & (g["mean"] < 1) & (g["size"] >= 2)]
M = X[X["funding_round_uuid"].isin(mixed)].copy()
M["fpff"] = M["fp"] * M["ff"]
M["firm"] = M["org_uuid"]  # boot() 의 군집 열 이름 규약: 'firm' = 기업(company)
Mc = M[M["next36"] == 1].copy()
A = {"n_rounds_window": int(len(R0)), "n_investor_rows_attributed": int(len(X)), "n_mixed_rounds": int(len(mixed)), "n_mixed_rows": int(len(M)),
     "n_mixed_ff_rounds": int(M.loc[M["ff"] == 1, "funding_round_uuid"].nunique()), "n_companies_mixed": int(M["org_uuid"].nunique()),
     "n_cond_rounds": int(Mc["funding_round_uuid"].nunique()), "n_cond_ff_rounds": int(Mc.loc[Mc["ff"] == 1, "funding_round_uuid"].nunique()),
     "n_cond_ff_rows": int((Mc["ff"] == 1).sum()), "n_cond_companies": int(Mc["org_uuid"].nunique()), "n_cond_firms": int(Mc["investor_uuid"].nunique())}
cells = M.groupby(["fp", "ff"]).agg(next36=("next36", "mean"), y1u=("y1", "mean"), n=("y1", "size"))
cells_c = Mc.groupby(["fp", "ff"]).agg(y1=("y1", "mean"), y2=("y2", "mean"), n=("y1", "size"))
A["four_cell_next36"] = {f"fp{int(a)}_ff{int(b)}": round(float(v), 4) for (a, b), v in cells["next36"].items()}
A["four_cell_reup_cond"] = {f"fp{int(a)}_ff{int(b)}": round(float(v), 4) for (a, b), v in cells_c["y1"].items()}
A["four_cell_repartner_cond"] = {f"fp{int(a)}_ff{int(b)}": round(float(v), 4) for (a, b), v in cells_c["y2"].items()}
A["raw_dd_reup_cond"] = round(float((cells_c["y1"][(1, 1)] - cells_c["y1"][(0, 1)]) - (cells_c["y1"][(1, 0)] - cells_c["y1"][(0, 0)])), 4)
A["base_reup_cond_ff"] = round(float(Mc.loc[Mc["ff"] == 1, "y1"].mean()), 4)
log(f"[A] 혼성 라운드 {A['n_mixed_rounds']:,} (FF {A['n_mixed_ff_rounds']:,}) · 행 {A['n_mixed_rows']:,} · 조건(다음 36m) FF 라운드 {A['n_cond_ff_rounds']:,} / 행 {A['n_cond_ff_rows']:,} · "
    f"4셀 next36 {A['four_cell_next36']} · 4셀 재참여 {A['four_cell_reup_cond']} · 원시 DD {A['raw_dd_reup_cond']:+.4f}")
OUT["A_sample"] = A


def within_round(df, y, extra=("ln_exp",)):
    """y ~ fp + fp×ff + extra, 라운드 내 demean, 기업 군집 부트. b_FF = fp + fpff (같은 draws)."""
    xc = ["fp", "fpff"] + list(extra)
    res = boot(df, y, xc, ["fp", "fpff"], rng, nb=NB, demean="funding_round_uuid", cluster="firm", min_n=50, return_draws=True)
    if not res:
        return None
    i, j = res["_xc"].index("fp"), res["_xc"].index("fpff")
    dr = res["_draws"][:, i] + res["_draws"][:, j]
    lo, hi = qci(dr)
    se = float(np.std(dr, ddof=1))
    res["b_FF"] = {"coef": round(float(res["_b"][i] + res["_b"][j]), 5), "ci95": [round(lo, 5), round(hi, 5)], "sig": bool(lo > 0 or hi < 0), "se_boot": round(se, 5), "mde80": round(2.8 * se, 4),
                   "within_pm0.05": bool(lo >= -0.05 and hi <= 0.05)}
    res["b_other"] = res["fp"]
    res["b_diff"] = res["fpff"]
    return {k: v for k, v in res.items() if not k.startswith("_")}


def perm_p(df, y, obs, extra=("ln_exp",), n=NPERM):
    """라운드 내 fp 라벨 순열 → FF 라운드 b_FF 의 양측 p."""
    dd = df[df["ff"] == 1].dropna(subset=[y, "fp"] + list(extra)).copy()
    xc = ["fp"] + list(extra)
    stats = []
    for _ in range(n):
        dd["fp_p"] = dd.groupby("funding_round_uuid")["fp"].transform(lambda s: pd.Series(rng.permutation(s.to_numpy()), index=s.index))
        dm = dd.copy()
        for c in [y, "fp_p"] + list(extra):
            dm[c] = dm[c] - dm.groupby("funding_round_uuid")[c].transform("mean")
        stats.append(float(fit(dm, y, ["fp_p"] + list(extra))[0]))
    stats = np.array(stats)
    return {"n_perm": n, "p_two": round(float(np.mean(np.abs(stats) >= abs(obs))), 4), "null_p95_abs": round(float(np.percentile(np.abs(stats), 95)), 4)}


def show(tag, r):
    if not r:
        log(f"  {tag}: 표본 부족"); return
    b = r["b_FF"]
    log(f"  {tag:<24} n={r['n']:,}/{r['n_firms']:,} | b_FF {b['coef']:+.4f} [{b['ci95'][0]:+.3f},{b['ci95'][1]:+.3f}] MDE {b['mde80']:.3f} ±5pp {b['within_pm0.05']} · "
        f"b_other {r['b_other']['coef']:+.4f} [{r['b_other']['ci95'][0]:+.3f},{r['b_other']['ci95'][1]:+.3f}] · diff {r['b_diff']['coef']:+.4f} [{r['b_diff']['ci95'][0]:+.3f},{r['b_diff']['ci95'][1]:+.3f}]")


log("\n" + "=" * 100 + "\n[B] y1 재참여(36m), 다음 라운드 有 조건 — 라운드 내\n" + "=" * 100)
B = within_round(Mc, "y1"); show("B 재참여", B)
B_perm = perm_p(Mc, "y1", B["b_FF"]["coef"]) if B else None
log(f"  순열 p(FF) {B_perm}")
OUT["B_reup_conditional"] = {"reg": B, "perm_FF": B_perm}
log("\n" + "=" * 100 + "\n[C] y1u 무조건(다음 라운드 없음 = 0)\n" + "=" * 100)
C = within_round(M, "y1"); show("C 재참여 무조건", C); OUT["C_reup_unconditional"] = C
log("\n" + "=" * 100 + "\n[D] y2 같은 파트너 재귀속 (재참여 조건)\n" + "=" * 100)
Md = Mc[Mc["y1"] == 1].copy()
D = within_round(Md, "y2"); show("D 재귀속|재참여", D)
D_all = within_round(Mc, "y2"); show("D 재귀속(무조건)", D_all)
OUT["D_repartner"] = {"cond_on_reup": D, "unconditional": D_all, "n_rows_cond": int(len(Md))}
log("\n" + "=" * 100 + "\n[E] y3 리드 플래그 · 커버리지\n" + "=" * 100)
E = {"lead_recorded_share": round(float(M["lead_rec"].mean()), 4),
     "lead_recorded_fp_minus_mp": round(float(M.loc[M["fp"] == 1, "lead_rec"].mean() - M.loc[M["fp"] == 0, "lead_rec"].mean()), 4)}
Ml = M[M["lead"].notna()].copy()
E["lead_within_round"] = within_round(Ml, "lead"); show("E 리드", E["lead_within_round"])
E["lead_rec_within_round"] = within_round(M, "lead_rec"); show("E 리드 기록 여부", E["lead_rec_within_round"])
OUT["E_lead"] = E
log("\n" + "=" * 100 + "\n[F] 역방향 위약: 이전 라운드 참여 y0\n" + "=" * 100)
Mp = M[M["prev_uuid"].notna()].copy()
F = within_round(Mp, "y0"); show("F 이전 라운드 참여", F); OUT["F_reverse_placebo"] = F

# ── 판정 ────────────────────────────────────────────────────────────────────
b = B["b_FF"]
if b["within_pm0.05"]:
    status, call = "GO", "같은 라운드 안에서 여성 귀속 투자자의 재참여 차등이 ±5pp 안 — 선별 정합, 호의 예측 기각"
elif b["ci95"][1] < 0 and b["coef"] < -0.04:
    status, call = "GO", "같은 라운드 안에서 여성 귀속 투자자의 재참여 결손 검출 — 호의 정합 (§4 판정 재검 필요)"
else:
    status, call = "PARTIAL", "차등 재참여 검출도 배제도 안 됨 — MDE 병기"
pred = {"A_ff_rounds_650_720": 650 <= A["n_cond_ff_rounds"] <= 720, "A_next36_balanced": max(A["four_cell_next36"].values()) - min(A["four_cell_next36"].values()) < 0.04,
        "B_bFF_in_[-0.06,0.02]": -0.06 <= b["coef"] <= 0.02, "B_ci_incl0": b["ci95"][0] <= 0 <= b["ci95"][1], "B_mde_4_5pp": 0.03 <= b["mde80"] <= 0.06,
        "B_diff_in_[-0.05,0.02]": -0.05 <= B["b_diff"]["coef"] <= 0.02,
        "D_bFF_in_[-0.08,0.02]": bool(D and -0.08 <= D["b_FF"]["coef"] <= 0.02), "E_lead_cov_0.5_0.7": 0.5 <= E["lead_recorded_share"] <= 0.7,
        "F_abs_lt_0.03_incl0": bool(F and abs(F["b_FF"]["coef"]) < 0.03 and not F["b_FF"]["sig"])}
pred = {k: bool(v) for k, v in pred.items()}
OUT["prediction_check"] = pred
verdict = (f"혼성 FF 라운드(다음 36m 조건) {A['n_cond_ff_rounds']:,}·행 {A['n_cond_ff_rows']:,}·기업 {A['n_cond_companies']:,} | 재참여 b_FF {b['coef']:+.4f} [{b['ci95'][0]:+.3f},{b['ci95'][1]:+.3f}] "
           f"(MDE {b['mde80']:.3f}; 순열 p {B_perm['p_two']}) · 비FF {B['b_other']['coef']:+.4f} · 차이 {B['b_diff']['coef']:+.4f} [{B['b_diff']['ci95'][0]:+.3f},{B['b_diff']['ci95'][1]:+.3f}] | "
           f"무조건 {C['b_FF']['coef']:+.4f} | 재귀속|재참여 {D['b_FF']['coef'] if D else float('nan'):+.4f} | 리드 {E['lead_within_round']['b_FF']['coef'] if E['lead_within_round'] else float('nan'):+.4f} (커버 {E['lead_recorded_share']:.2f}) | "
           f"역방향 위약 {F['b_FF']['coef'] if F else float('nan'):+.4f} — {call} (예측 적중 {sum(pred.values())}/{len(pred)})")
emit("P001-42", "P1: 라운드 내 투자자 수준 결과 — 재참여·재귀속·리드, 혼성 신디케이트", status, OUT,
     prediction="FF 라운드 650–720; next36 4셀 균형; b_FF ∈[−0.06,+0.02] CI 0 포함 MDE 4–5pp; 차이 ∈[−0.05,+0.02]; 역방향 위약 |b|<0.03",
     verdict=verdict, kill_met=False, n=int(A["n_cond_ff_rows"]),
     extra={"stage": 7, "feeds": "v6 설계 제안 P1 → §4 판별 강화", "slug": "within_round_reup", "builds_on": "P001-12/40",
            "common_sha256_16": RESCUE_SHA, "v6_common_sha256_16": V6_SHA})
log("done")
