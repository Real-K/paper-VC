# -*- coding: utf-8 -*-
"""p001_31 — R2 결정 검정(P001-30)의 검정력 진단: 게이트가 R1 크기의 효과를 검출할 수 있었는가

[왜] P001-30 의 회사 FE 게이트(R4)는 t_cs 점추정을 거의 바꾸지 않고(+0.160 → +0.116) 구간만 두 배로
 벌렸다(표본 2164→1624, 회사 990→450). "게이트 실패"가 '효과 부재'인지 '검출 불가'인지는 MDE 로 갈린다
 (power-rescue F.22). 같은 회사 파트너들이 섹터 발자국을 공유하면 회사 내 demean 이 t_cs 의 분산을
 지워 버린다 — 그 비중을 잰다. R1 에서 성분 3개 중 1개만 유의한 것은 다중성 문제이므로 max-|t| 로 보정한다.

[Panel]
 A. P001-30 R1–R7 의 SE=(CI폭/3.92) → MDE80=2.8·SE, R1 점추정 대비 배율
 B. 공용 모듈 포팅 검산: R1t 총 terrain 점추정 +0.09772 재현; 같은 seed 로 R1 을 먼저 돌려 CI 재현
 C. R4 표본(사후기 有 · 회사 내 파트너 ≥2)에서 t_v/t_s/t_cs/terrain/adj 의 within-firm 분산 비중
 D. R1 성분 3개 max-|t| 단일단계 보정 p(부트 중심화) · t_cs 단측(방향 가설) 미보정 p

[사전 예측] (2026-09-08, 결과 조회 전)
 A: R4 의 t_cs MDE ≥ 0.30 (R1 0.160 의 ≥1.9배); R4t 총 terrain MDE ≥ 0.20 (R1t 0.098 의 ≥2배).
 C: t_cs 의 within-firm 분산 비중 ≤ 0.35.
 D: R1 t_cs 보정 양측 p ∈ [0.05, 0.15] (3-성분 다중성에 살아남지 못함); 단측 미보정 p < 0.025.
[판정] 진단 스크립트 — status OK. 어떤 주장도 단독으로 복원하지 않는다.
"""
import json
import os

import numpy as np

from p001_rescue_common import (COMMON_SHA, TC, TEN, add_post, add_tenure, boot, emit, load_deals, log,
                                partner_pre, show, strip_draws)

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(20260908)  # P001-30 과 동일 seed → R1 을 첫 호출로 두면 CI 재현
OUT = {}

# ── A. P001-30 산출물에서 MDE ──────────────────────────────────────────────
p30 = json.load(open(os.path.join(os.environ.get("P001_ARTIFACTS", os.path.join(HERE, "..", "..", "artifacts")), "P00130.json"), encoding="utf-8"))["estimates"]
ref = {"t_cs": p30["R1_decomp"]["t_cs"]["coef"], "t_s": p30["R1_decomp"]["t_s"]["coef"],
       "t_v": p30["R1_decomp"]["t_v"]["coef"], "terrain": p30["R1t_total"]["terrain"]["coef"],
       "terrain_fon": p30["R1t_total"]["terrain"]["coef"]}
A = {}
log("=" * 100 + "\n[A] P001-30 사양별 SE · MDE80 · R1 점추정 대비 배율\n" + "=" * 100)
for spec in ("R1_decomp", "R2_tenure", "R3_firm_ctrl", "R4_firm_FE", "R1t_total", "R2t_total_tenure",
             "R4t_total_firmFE", "R5_fixed_horizon"):
    A[spec] = {"n": p30[spec]["n"]}
    for k in ("t_v", "t_s", "t_cs", "terrain", "terrain_fon"):
        if k in p30[spec]:
            lo, hi = p30[spec][k]["ci95"]
            se = (hi - lo) / 3.92
            mde = 2.8 * se
            A[spec][k] = {"coef": p30[spec][k]["coef"], "se": round(se, 4), "mde80": round(mde, 4),
                          "mde_over_R1": round(mde / abs(ref[k]), 2) if ref[k] else None}
            log(f"  {spec:<18} {k:<11} coef {p30[spec][k]['coef']:+.4f}  se {se:.4f}  MDE80 {mde:.3f}  "
                f"(R1 점추정 {ref[k]:+.3f} 의 {mde / abs(ref[k]):.2f}배)")
OUT["A_mde"] = A

# ── B. 포팅 검산 ───────────────────────────────────────────────────────────
dn = load_deals(with_exit_dt=False)
P, h = partner_pre(dn, "exit_ever")
P = add_post(P, dn, "exit_ever")
P = add_tenure(P)
log("\n" + "=" * 100 + "\n[B] 포팅 검산 — R1(첫 부트 호출) 및 R1t 점추정\n" + "=" * 100)
R1 = boot(P, "post_adj", TC + ["adj", "ln_n", "fp"], TC + ["adj"], rng, return_draws=True)
show("R1 재현", R1, TC + ["adj"])
R1t_b = boot(P.dropna(subset=["post_adj"]), "post_adj", ["terrain", "adj", "ln_n", "fp"], ["terrain"], rng, nb=2)
chk = {"R1_t_cs_coef_match": bool(abs(R1["t_cs"]["coef"] - p30["R1_decomp"]["t_cs"]["coef"]) < 1e-6),
       "R1_t_cs_ci_match": bool(np.allclose(R1["t_cs"]["ci95"], p30["R1_decomp"]["t_cs"]["ci95"], atol=1e-5)),
       "R1t_terrain_coef": R1t_b["terrain"]["coef"], "R1t_terrain_p30": p30["R1t_total"]["terrain"]["coef"],
       "R1t_match": bool(abs(R1t_b["terrain"]["coef"] - p30["R1t_total"]["terrain"]["coef"]) < 1e-6),
       "n_post": int(P["post_adj"].notna().sum()), "n_all": int(len(P))}
log(f"  검산: {chk}")
if not (chk["R1_t_cs_coef_match"] and chk["R1t_match"]):
    raise SystemExit("포팅 검산 실패 — 공용 모듈이 P001-30 을 재현하지 못함")
OUT["B_port_check"] = chk

# ── C. R4 표본의 within-firm 분산 비중 ────────────────────────────────────
log("\n" + "=" * 100 + "\n[C] R4 표본(사후기 有 · 회사 내 ≥2)에서 within-firm 분산 비중\n" + "=" * 100)
d4 = P.dropna(subset=["post_adj"] + TC + ["adj", "ln_n", "fp"] + TEN).copy()
cnt = d4.groupby("firm")["firm"].transform("size")
d4 = d4[cnt >= 2].copy()
C = {"n": int(len(d4)), "n_firms": int(d4["firm"].nunique()),
     "partners_per_firm_mean": round(float(d4.groupby("firm").size().mean()), 2)}
for c in TC + ["terrain", "adj", "post_adj", "tenure"]:
    w = d4[c] - d4.groupby("firm")[c].transform("mean")
    C[c] = {"var_total": round(float(d4[c].var()), 6), "within_share": round(float(w.var() / d4[c].var()), 4)}
    log(f"  {c:<9} 총분산 {C[c]['var_total']:.5f}  within 비중 {C[c]['within_share']:.3f}")
# 비교: 전체 사후기 표본(R1)에서 t_cs 분산 (회사 FE 가 버린 between 분산 크기)
C["t_cs_var_R1_sample"] = round(float(P.dropna(subset=["post_adj"])["t_cs"].var()), 6)
OUT["C_within_share"] = C

# ── D. R1 성분 3개 다중성(max-|t|) · t_cs 단측 p ─────────────────────────
log("\n" + "=" * 100 + "\n[D] R1 성분 max-|t| 단일단계 보정 p · t_cs 단측 미보정 p\n" + "=" * 100)
bs, b, xc = R1["_draws"], R1["_b"], R1["_xc"]
idx = [xc.index(k) for k in TC]
se = bs[:, idx].std(axis=0, ddof=1)
t_obs = b[idx] / se
t_star = (bs[:, idx] - b[idx]) / se
max_t = np.abs(t_star).max(axis=1)
D = {}
for j, k in enumerate(TC):
    D[k] = {"t": round(float(t_obs[j]), 3),
            "p_two_unadj": round(float(np.mean(np.abs(t_star[:, j]) >= abs(t_obs[j]))), 4),
            "p_two_maxT_adj": round(float(np.mean(max_t >= abs(t_obs[j]))), 4),
            "p_one_upper_unadj": round(float(np.mean(t_star[:, j] >= t_obs[j])), 4)}
    log(f"  {k:<5} t {t_obs[j]:+.2f}  양측 미보정 p {D[k]['p_two_unadj']:.3f}  max-|t| 보정 p {D[k]['p_two_maxT_adj']:.3f}  "
        f"단측(+) 미보정 p {D[k]['p_one_upper_unadj']:.3f}")
OUT["D_multiplicity_R1"] = D
OUT["R1_repro"] = strip_draws(R1)

# ── 판정 (진단) ───────────────────────────────────────────────────────────
r4 = A["R4_firm_FE"]["t_cs"]
r4t = A["R4t_total_firmFE"]["terrain"]
pred = {"A_R4_tcs_mde_ge_0.30": r4["mde80"] >= 0.30, "A_R4t_terrain_mde_ge_0.20": r4t["mde80"] >= 0.20,
        "C_tcs_within_share_le_0.35": C["t_cs"]["within_share"] <= 0.35,
        "D_tcs_adj_p_in_[0.05,0.15]": 0.05 <= D["t_cs"]["p_two_maxT_adj"] <= 0.15,
        "D_tcs_one_sided_lt_0.025": D["t_cs"]["p_one_upper_unadj"] < 0.025}
OUT["prediction_check"] = pred
verdict = (f"R4 t_cs MDE80 {r4['mde80']:.3f} (R1 점추정의 {r4['mde_over_R1']:.1f}배) · R4t 총 terrain MDE80 {r4t['mde80']:.3f} "
           f"({r4t['mde_over_R1']:.1f}배) · R4 표본 t_cs within-firm 분산 비중 {C['t_cs']['within_share']:.2f} "
           f"(terrain {C['terrain']['within_share']:.2f}) · R1 t_cs max-|t| 보정 p {D['t_cs']['p_two_maxT_adj']:.3f}, "
           f"단측 미보정 p {D['t_cs']['p_one_upper_unadj']:.3f} — 예측 적중 {sum(pred.values())}/{len(pred)}")
emit("P001-31", "R2 게이트 검정력 진단 — MDE · within-firm 분산 비중 · 성분 다중성", "OK", OUT,
     prediction="R4 t_cs MDE≥0.30(R1 의 ≥1.9배) · R4t MDE≥0.20 · t_cs within 비중≤0.35 · R1 t_cs 보정 p∈[0.05,0.15], 단측 p<0.025",
     verdict=verdict, kill_met=False, n=int(len(P)),
     extra={"stage": 7, "feeds": "R2 power-rescue (POWER_RESCUE_R2.md)", "slug": "gate_power",
            "builds_on": "P001-30", "common_sha256_16": COMMON_SHA})
log("done")
