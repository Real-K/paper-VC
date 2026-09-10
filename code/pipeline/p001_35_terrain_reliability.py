# -*- coding: utf-8 -*-
"""p001_35 — terrain 성분의 반분 신뢰도(Spearman–Brown) 와 감쇠 보정(반분 IV)

[왜] terrain 성분은 파트너당 ≥5개 딜의 셀 벤치마크 평균이다. 측정오차가 있으면 OLS 계수는 신뢰도 ρ 만큼
 감쇠한다(β_OLS ≈ ρ·β). P001-30 R2/R3 의 t_cs 가 하한 −0.008/−0.007 로 경계에 걸린 것이 감쇠된 더 큰 계수의
 그림자인지, 원래 그 크기인지를 잰다. 반분(홀수·짝수 번째 딜) 은 같은 파트너의 독립 측정치 두 개를 준다:
 상관 r 은 반분 신뢰도, ρ_SB = 2r/(1+r) 은 전장 신뢰도. 반분 B 를 반분 A 의 도구로 쓰면 고전적 측정오차
 하에서 일치 추정량이다(도구 = 같은 대상의 독립 재측정).

[Panel]
 A. 반분 신뢰도: t_v, t_s, t_cs, terrain, adj 각 corr(A,B), ρ_SB, 감쇠 보정 배율 1/ρ_SB
 B. 2SLS: post_adj ~ [t_v_A, t_s_A, t_cs_A] (도구 [t_v_B, t_s_B, t_cs_B]) + adj + ln_n + fp (+TEN)
    A↔B 를 바꾼 판도 계산해 평균 (군집 부트 400, 회사)
 C. 참조 OLS: 반분 A 의 성분으로 같은 회귀 (감쇠의 실측 대비)

[사전 예측] (2026-09-08, 결과 조회 전)
 A: t_cs 반분 상관 0.35–0.60 → ρ_SB 0.50–0.75; adj 의 신뢰도는 그보다 낮다(잔차 평균은 더 잡음).
 B: IV t_cs 점추정은 P001-30 R2 t_cs(+0.151) 의 1.3–2배, CI 는 더 넓어 0 포함 가능.
 진단 스크립트 — status OK. 단독으로 주장을 복원하지 않는다; 감쇠가 크면 R2/R3 경계 결과의 해석에 병기한다.
"""
import numpy as np
import pandas as pd

from p001_rescue_common import (COMMON_SHA, TC, TEN, add_post, add_tenure, boot, emit, load_deals, log, partner_pre,
                                qci, show)

rng = np.random.default_rng(20260935)
NB = 400
OUT = {}
dn = load_deals(with_exit_dt=False)
P, h = partner_pre(dn, "exit_ever")
P = add_post(P, dn, "exit_ever")
P = add_tenure(P)

# ── 반분: 파트너 내 날짜순 홀·짝 ──────────────────────────────────────────
hh = h[h["partner_uuid"].isin(P["partner_uuid"])].sort_values(["partner_uuid", "dt", "funding_round_uuid"]).copy()
hh["pos"] = hh.groupby("partner_uuid").cumcount()
hh["half"] = np.where(hh["pos"] % 2 == 0, "A", "B")
agg = hh.groupby(["partner_uuid", "half"]).agg(t_v=("t_v", "mean"), t_s=("t_s", "mean"), t_cs=("t_cs", "mean"),
                                                adj=("r", "mean"), raw=("exit_ever", "mean"), k=("r", "size"))
agg["terrain"] = agg["raw"] - agg["adj"]
wide = agg.unstack("half")
wide.columns = [f"{a}_{b}" for a, b in wide.columns]
P = P.join(wide, on="partner_uuid")
ok = P["k_A"].notna() & P["k_B"].notna()
log(f"[반분] 파트너 {int(ok.sum()):,} 양쪽 존재 · 반분 크기 중위 A {P['k_A'].median():.0f} / B {P['k_B'].median():.0f}")

A = {"n": int(ok.sum())}
for c in TC + ["terrain", "adj"]:
    r = float(P.loc[ok, [f"{c}_A", f"{c}_B"]].corr().iloc[0, 1])
    sb = 2 * r / (1 + r) if r > -1 else np.nan
    A[c] = {"r_half": round(r, 4), "rho_SB": round(sb, 4), "disattenuation": round(1 / sb, 3) if sb > 0 else None}
    log(f"  {c:<8} 반분 상관 {r:+.3f}  ρ_SB {sb:.3f}  보정 배율 {1 / sb if sb > 0 else float('nan'):.2f}")
OUT["A_reliability"] = A


# ── 2SLS ────────────────────────────────────────────────────────────────────
def tsls(s, y, endog, instr, exog):
    X = np.column_stack([s[c].to_numpy(float) for c in endog + exog] + [np.ones(len(s))])
    Z = np.column_stack([s[c].to_numpy(float) for c in instr + exog] + [np.ones(len(s))])
    yv = s[y].to_numpy(float)
    Xh = Z @ np.linalg.lstsq(Z, X, rcond=None)[0]
    return np.linalg.lstsq(Xh, yv, rcond=None)[0]


def boot_iv(df, y, endog, instr, exog, keys, nb=NB):
    dd = df.dropna(subset=[y] + endog + instr + exog).copy()
    b = tsls(dd, y, endog, instr, exog)
    grp = {c: g.index.to_numpy() for c, g in dd.groupby("firm")}
    kl = list(grp)
    bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(kl), len(kl))
        s = dd.loc[np.concatenate([grp[kl[i]] for i in pick])]
        try:
            bs.append(tsls(s, y, endog, instr, exog))
        except Exception:
            pass
    bs = np.array(bs)
    out = {"n": int(len(dd)), "n_firms": int(dd["firm"].nunique())}
    cols = endog + exog
    for k in keys:
        i = cols.index(k)
        lo, hi = qci(bs[:, i])
        se = float(np.std(bs[:, i], ddof=1))
        out[k] = {"coef": round(float(b[i]), 5), "ci95": [round(lo, 5), round(hi, 5)], "sig": bool(lo > 0 or hi < 0),
                  "se_boot": round(se, 5), "mde80": round(2.8 * se, 4)}
    # 1단계 강도: 각 endog 를 instr+exog 에 회귀한 R² 증분 대신 corr 보고 (간이)
    out["first_stage_corr"] = {e: round(float(dd[[e, i_]].corr().iloc[0, 1]), 3) for e, i_ in zip(endog, instr)}
    return out


EA, EB = [f"{c}_A" for c in TC], [f"{c}_B" for c in TC]
log("\n" + "=" * 100 + "\n[B] 2SLS 반분 IV (A ← B 도구) · (B ← A 도구)\n" + "=" * 100)
IV1 = boot_iv(P, "post_adj", EA, EB, ["adj", "ln_n", "fp"], EA); show("IV A←B", IV1, EA)
IV2 = boot_iv(P, "post_adj", EB, EA, ["adj", "ln_n", "fp"], EB); show("IV B←A", IV2, EB)
IV1t = boot_iv(P, "post_adj", EA, EB, ["adj", "ln_n", "fp"] + TEN, EA); show("IV A←B +연공", IV1t, EA)
IV2t = boot_iv(P, "post_adj", EB, EA, ["adj", "ln_n", "fp"] + TEN, EB); show("IV B←A +연공", IV2t, EB)
OUT.update({"B_IV_AfromB": IV1, "B_IV_BfromA": IV2, "B_IV_AfromB_tenure": IV1t, "B_IV_BfromA_tenure": IV2t})
OUT["B_IV_tcs_avg_tenure"] = round((IV1t["t_cs_A"]["coef"] + IV2t["t_cs_B"]["coef"]) / 2, 5)

log("\n" + "=" * 100 + "\n[C] 참조 OLS — 반분 A 성분 (감쇠 실측)\n" + "=" * 100)
C1 = boot(P, "post_adj", EA + ["adj", "ln_n", "fp"], EA, rng); show("OLS A", C1, EA)
C1t = boot(P, "post_adj", EA + ["adj", "ln_n", "fp"] + TEN, EA, rng); show("OLS A +연공", C1t, EA)
C2 = boot(P, "post_adj", EB + ["adj", "ln_n", "fp"] + TEN, EB, rng); show("OLS B +연공", C2, EB)
OUT.update({"C_OLS_A": C1, "C_OLS_A_tenure": C1t, "C_OLS_B_tenure": C2})
ratio = OUT["B_IV_tcs_avg_tenure"] / ((C1t["t_cs_A"]["coef"] + C2["t_cs_B"]["coef"]) / 2) if (C1t["t_cs_A"]["coef"] + C2["t_cs_B"]["coef"]) else np.nan
OUT["IV_over_OLS_tcs_tenure"] = round(float(ratio), 3)

pred = {"A_tcs_r_half_in_[0.35,0.60]": 0.35 <= A["t_cs"]["r_half"] <= 0.60,
        "A_adj_less_reliable_than_tcs": A["adj"]["rho_SB"] < A["t_cs"]["rho_SB"],
        "B_IV_tcs_1.3to2x_R2": 1.3 * 0.15113 <= OUT["B_IV_tcs_avg_tenure"] <= 2.0 * 0.15113}
OUT["prediction_check"] = pred
verdict = (f"반분 신뢰도 ρ_SB: t_v {A['t_v']['rho_SB']:.2f} · t_s {A['t_s']['rho_SB']:.2f} · t_cs {A['t_cs']['rho_SB']:.2f} · terrain "
           f"{A['terrain']['rho_SB']:.2f} · adj {A['adj']['rho_SB']:.2f} | IV(+연공) t_cs A←B {IV1t['t_cs_A']['coef']:+.3f} "
           f"[{IV1t['t_cs_A']['ci95'][0]:+.3f},{IV1t['t_cs_A']['ci95'][1]:+.3f}] · B←A {IV2t['t_cs_B']['coef']:+.3f} "
           f"[{IV2t['t_cs_B']['ci95'][0]:+.3f},{IV2t['t_cs_B']['ci95'][1]:+.3f}] · 평균 {OUT['B_IV_tcs_avg_tenure']:+.3f} "
           f"(반분 OLS 대비 {OUT['IV_over_OLS_tcs_tenure']:.2f}배) — 예측 적중 {sum(pred.values())}/{len(pred)}")
emit("P001-35", "terrain 성분 반분 신뢰도 · 감쇠 보정 IV", "OK", OUT,
     prediction="t_cs 반분 상관 0.35–0.60(ρ_SB 0.50–0.75); adj 신뢰도 더 낮음; IV t_cs 는 R2 의 1.3–2배, CI 넓음",
     verdict=verdict, kill_met=False, n=int(ok.sum()),
     extra={"stage": 7, "feeds": "R2 power-rescue", "slug": "terrain_reliability", "builds_on": "P001-30",
            "common_sha256_16": COMMON_SHA})
log("done")
