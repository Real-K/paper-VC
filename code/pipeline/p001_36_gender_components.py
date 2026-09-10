# -*- coding: utf-8 -*-
"""p001_36 — 성별 × 성분: 여성 파트너는 어느 성분을 기울이며, 함의 상쇄량은 성분별로 얼마인가

[왜] v5 §6 은 성별 상쇄를 산술로 처리했다(fp→wedge −0.048 × wedge→post +0.097 ≈ −0.005; 직접 추정 CI ±0.041
 이라 검출 불가). 성분으로 쪼개면 더 날카로운 진술이 가능하다: 정보를 담는 성분(P001-30 에서 t_cs)과 여성이
 기울어진 성분(단계 t_s 또는 빈티지 t_v)이 **다른 성분**이면, 구성 경로가 여성 파트너의 장래 셀 내 성과
 격차에 기여하는 양은 구조적으로 0 에 가깝고, 그 CI 는 직접 추정보다 훨씬 좁다(작은 두 수의 곱).

[Panel]
 G1  t_k ~ fp + ln_n                      (k = t_v, t_s, t_cs, terrain, adj) — 여성의 성분 기울기
 G2  G1 + TEN                             — 연공을 고정한 뒤의 기울기
 G3  post_adj ~ fp + ln_n · post_adj ~ fp + 성분 + adj + ln_n + TEN   — 장래 셀 내 성과의 성별 격차(원·조건부)
 G4  함의 상쇄량: Σ_k β(fp→k | TEN) × β(k→post_adj | TEN) — 같은 부트 재표본에서 두 회귀를 함께 적합해 곱의 CI
     (β(k→post_adj) 는 P001-30 R2 사양을 같은 재표본에서 재적합)

[사전 예측] (2026-09-08, 결과 조회 전)
 G1: fp→t_s 음(−0.02 ~ −0.05) 유의; fp→t_v 음(여성이 최근 빈티지에 집중) 유의; fp→t_cs ≈ 0 [−0.01, +0.01].
 G2: t_v 기울기는 연공 통제로 소멸, t_s 기울기는 절반 이상 잔존.
 G4: 총 함의 상쇄 ∈ [−0.010, +0.005], CI ⊂ ±0.02 → 구성 경로는 여성 파트너의 장래 셀 내 성과를 2pp 이상 움직일 수 없다.
 메커니즘 서술 스크립트 — status OK.
"""
import numpy as np

from p001_rescue_common import (COMMON_SHA, TC, TEN, add_post, add_tenure, boot, emit, fit, fmt, load_deals, log,
                                partner_pre, qci, show)

rng = np.random.default_rng(20260936)
NB = 400
OUT = {}
dn = load_deals(with_exit_dt=False)
P, h = partner_pre(dn, "exit_ever")
P = add_post(P, dn, "exit_ever")
P = add_tenure(P)
KS = TC + ["terrain", "adj"]

log("=" * 100 + "\n[G1/G2] 여성 파트너의 성분 기울기\n" + "=" * 100)
G1, G2 = {}, {}
for k in KS:
    G1[k] = boot(P, k, ["fp", "ln_n"], ["fp"], rng)
    G2[k] = boot(P, k, ["fp", "ln_n"] + TEN, ["fp"], rng)
    log(f"  fp → {k:<8} G1 {fmt(G1[k], 'fp')}   G2(+연공) {fmt(G2[k], 'fp')}   n={G1[k]['n']:,}")
OUT["G1_fp_to_component"] = G1
OUT["G2_fp_to_component_tenure"] = G2
OUT["sd_components"] = {k: round(float(P[k].std()), 4) for k in KS}

log("\n" + "=" * 100 + "\n[G3] 장래 셀 내 성과의 성별 격차\n" + "=" * 100)
G3a = boot(P, "post_adj", ["fp", "ln_n"], ["fp"], rng); show("post_adj ← fp", G3a, ["fp"])
G3b = boot(P, "post_adj", ["fp"] + TC + ["adj", "ln_n"] + TEN, ["fp"] + TC, rng); show("post_adj ← fp | 성분+연공", G3b, ["fp"] + TC)
OUT.update({"G3_raw_gap": G3a, "G3_conditional_gap": G3b})

# ── G4: 함의 상쇄량 (같은 재표본에서 두 회귀) ──────────────────────────────
log("\n" + "=" * 100 + "\n[G4] 함의 상쇄량 Σ_k β(fp→k) × β(k→post_adj), 연공 통제\n" + "=" * 100)
X2 = TC + ["adj", "ln_n", "fp"] + TEN
dd = P.dropna(subset=["post_adj"] + X2).copy()          # 사후기 有 표본에서 두 회귀 모두 적합 (같은 표본)
grp = {c: g.index.to_numpy() for c, g in dd.groupby("firm")}
kl = list(grp)


def products(s):
    b2 = fit(s, "post_adj", X2)
    out = {}
    for j, k in enumerate(TC):
        b1 = fit(s, k, ["fp", "ln_n"] + TEN)
        out[k] = float(b1[0] * b2[j])
    out["total"] = sum(out[k] for k in TC)
    return out


pt = products(dd)
draws = {k: [] for k in TC + ["total"]}
for _ in range(NB):
    pick = rng.integers(0, len(kl), len(kl))
    s = dd.loc[np.concatenate([grp[kl[i]] for i in pick])]
    try:
        pr = products(s)
        for k in draws:
            draws[k].append(pr[k])
    except Exception:
        pass
G4 = {"n": int(len(dd))}
for k in TC + ["total"]:
    lo, hi = qci(np.array(draws[k]))
    G4[k] = {"coef": round(pt[k], 5), "ci95": [round(lo, 5), round(hi, 5)],
             "within_pm0.02": bool(lo >= -0.02 and hi <= 0.02), "within_pm0.01": bool(lo >= -0.01 and hi <= 0.01)}
    log(f"  {k:<6} 함의 {pt[k]:+.4f} [{lo:+.4f},{hi:+.4f}]  ⊂±0.02 {G4[k]['within_pm0.02']}  ⊂±0.01 {G4[k]['within_pm0.01']}")
OUT["G4_implied_netting"] = G4

pred = {"G1_fp_ts_neg_sig": G1["t_s"]["fp"]["coef"] < 0 and G1["t_s"]["fp"]["sig"],
        "G1_fp_tv_neg_sig": G1["t_v"]["fp"]["coef"] < 0 and G1["t_v"]["fp"]["sig"],
        "G1_fp_tcs_in_pm0.01": abs(G1["t_cs"]["fp"]["coef"]) <= 0.01,
        "G2_tv_gone": not G2["t_v"]["fp"]["sig"],
        "G4_total_ci_in_pm0.02": G4["total"]["within_pm0.02"]}
OUT["prediction_check"] = pred
verdict = (f"fp→ t_v {fmt(G1['t_v'], 'fp')} · t_s {fmt(G1['t_s'], 'fp')} · t_cs {fmt(G1['t_cs'], 'fp')} · terrain {fmt(G1['terrain'], 'fp')} | "
           f"+연공: t_v {fmt(G2['t_v'], 'fp')} · t_s {fmt(G2['t_s'], 'fp')} · t_cs {fmt(G2['t_cs'], 'fp')} | "
           f"post_adj←fp 원 {fmt(G3a, 'fp')} · 조건부 {fmt(G3b, 'fp')} | 함의 상쇄 총 {G4['total']['coef']:+.4f} "
           f"[{G4['total']['ci95'][0]:+.4f},{G4['total']['ci95'][1]:+.4f}] (⊂±0.02 {G4['total']['within_pm0.02']}) — "
           f"예측 적중 {sum(pred.values())}/{len(pred)}")
emit("P001-36", "성별 × terrain 성분 — 기울기 위치와 함의 상쇄량의 성분별 CI", "OK", OUT,
     prediction="fp→t_s 음*, fp→t_v 음*(연공으로 소멸), fp→t_cs≈0 ±0.01; 함의 총 상쇄 ∈[−0.010,+0.005], CI⊂±0.02",
     verdict=verdict, kill_met=False, n=int(len(P)),
     extra={"stage": 7, "feeds": "R2 power-rescue (Panel B/D 메커니즘)", "slug": "gender_components",
            "builds_on": "P001-26/30", "common_sha256_16": COMMON_SHA})
log("done")
