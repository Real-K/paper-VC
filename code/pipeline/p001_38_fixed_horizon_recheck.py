# -*- coding: utf-8 -*-
"""p001_38 — R3 식별 심판의 결정 검정(파트너 수준) — 고정 출구지평 표본에서 한 번에

[왜] R3 식별 심판(09_review/R3_recheck/ident.md)은 P001-33/36 의 분석은 건전하나 §6 의 결론이 근거를 넘는다고 했다.
 F-1 "회사 간에 위치" — 지지 추정치 없음(W1 between 0 포함; W3 총 terrain 은 within > between). F-3 성별 경계가 개방지평
 계수로 계산됨(고정지평 계수는 2–3배). F-4 "시드 셀 후속률 높음"은 무근거·반쪽 거짓. R-4 고정지평 IPW 미실시. R-13 딜 이전
 출구 포함. R-3/R-7 표준화 비교 불일치. CP-3 사전기가 순위 시점에 관측 불가(49% 미완결). 결정 검정 #1–#5·#8 을 한 하네스에.

[표본] P001-33 A 조합과 동일: 사전 exit3(≤2017-10) · 사후 exit3(2017-11~2020-10) · LOO 셀 벤치마크 · n≥5 · 연공 TEN.
[Panel]
 A. 단계별 기저율(사전기 NAEU): fon / exit3 / exit_ever by stage(≥500딜) + 셀(yss) 수준 fon-벤치마크 vs exit3-벤치마크 가중 상관 → F-4 의 근거
 B. 고정지평 Mundlak: 섹터 성분(dev/fm/대비)·총 terrain(dev/fm/대비), TEN 포함 → F-1 (결정 검정 #2)
 C. 고정지평 함의 상쇄: Σ_k β(fp→k|TEN)·β(k→post_adj|TEN), 같은 재표본; 성분별; ±0.02/±0.01 밴드 → F-3 (결정 검정 #3)
 D. Ex-ante 창: 사전기 ≤ 2014-10-31(36m 창이 분할 전 완결) F2/F2t · 거울 반쪽(2014-11~2017-10) F2/F2t → CP-3 (결정 검정 #1)
 E. 중복 기업만(사후기 = 사전기 투자 기업의 후속 딜) F2t ↔ F4t 대비 → 결정 검정 #4
 F. 고정지평 IPW: has_post ← 성분+adj+ln_n+fp+TEN (로짓, IRLS) → 1/p̂ 가중 F2t → R-4
 G. days ≥ 0 판: exit3 를 딜 이후 출구로 한정 → 기저율 이동 · F2t 재추정 → R-13
 H. 표준화 계수(같은 회귀): 고정 F1t/F2t 의 terrain·adj, 개방 R1t 의 terrain·adj → R-3/R-7
 I. exit3 성분의 반분 일치도(반분이 벤치마크를 공유 — 상한) → 결정 검정 #5

[사전 예측] (2026-09-09, 결과 조회 전)
 A: fon 은 단계 간 평탄(PE 제외 범위 < 0.08), exit3 는 단계와 함께 상승; 셀 수준 corr(fon, exit3 벤치마크) < 0.3.
 B: 총 terrain within ≈ between (차이 CI 0 포함) — **위치 미결정**. 섹터 성분도 대비 CI 0 포함.
 C: 총 함의 ∈ [−0.008, −0.002]; 하한 ∈ [−0.015, −0.006]; ±0.02 안, **±0.01 은 불확실(실패 예상)**.
 D: ex-ante F2t 점추정 ∈ [0.10, 0.30] (F2t 0.278 의 ≥50% 유지), CI 0 포함 가능(MDE ≈ 0.39); 거울 반쪽도 같은 부호·유사 크기.
    look-ahead 인공물 판정: ex-ante < 0.05 이고 거울 > 0.25.
 E: 중복 기업만 계수 > F4t(0.193) — 지속성 경로가 기여; [0.3, 0.6].
 F: IPW F2t 가 0.278 의 ±15% 안.  G: 사후 기저 0.145 → ≈0.138; F2t ±10%.  H: 고정 F2t 표준화 terrain 0.083 < 표준화 adj.
 I: exit3 t_cs 일치도 0.4–0.5.
[판정] 진단·재검 스크립트 — status OK. B 의 대비 CI 가 0 을 배제하면 verdict 에 "위치 결정" 표기.
"""
import numpy as np
import pandas as pd

from p001_rescue_common import (COMMON_SHA, CUT, END_FON, TC, TEN, add_firm_means, add_post, add_tenure, boot, build, emit,
                                first_deal_dates, fit, fmt, load_deals, log, partner_pre, qci, show, strip_draws)

rng = np.random.default_rng(20260938)
NB = 400
OUT = {}
dn = load_deals(with_exit_dt=True)
first = first_deal_dates()
pre = dn["dt"] <= CUT
X2 = TC + ["adj", "ln_n", "fp"] + TEN
XT = ["terrain", "adj", "ln_n", "fp"] + TEN

# ── A. 단계별 기저율 · 셀 벤치마크 상관 ─────────────────────────────────────
log("=" * 100 + "\n[A] 단계별 기저율 (사전기 NAEU) · yss 셀 벤치마크 상관\n" + "=" * 100)
h0 = dn[pre]
g = h0.groupby("stage").agg(n=("fon", "size"), fon=("fon", "mean"), exit3=("exit3", "mean"), exit_ever=("exit_ever", "mean"))
g = g[g["n"] >= 500].sort_values("exit_ever")
A = {"by_stage": {s: {"n": int(r.n), "fon": round(float(r.fon), 4), "exit3": round(float(r.exit3), 4), "exit_ever": round(float(r.exit_ever), 4)}
                  for s, r in g.iterrows()}}
non_pe = g.drop(index=[s for s in g.index if s == "private_equity"], errors="ignore")
A["fon_range_excl_pe"] = round(float(non_pe["fon"].max() - non_pe["fon"].min()), 4)
A["exit3_range_excl_pe"] = round(float(non_pe["exit3"].max() - non_pe["exit3"].min()), 4)
cell = h0.groupby("yss").agg(n=("fon", "size"), fon=("fon", "mean"), exit3=("exit3", "mean"), exit_ever=("exit_ever", "mean"))
cell = cell[cell["n"] >= 5]
wmean = lambda x, w: float(np.sum(x * w) / np.sum(w))
def wcorr(x, y, w):
    mx, my = wmean(x, w), wmean(y, w)
    return float(np.sum(w * (x - mx) * (y - my)) / np.sqrt(np.sum(w * (x - mx) ** 2) * np.sum(w * (y - my) ** 2)))
A["cell_corr_fon_exit3_weighted"] = round(wcorr(cell["fon"].to_numpy(), cell["exit3"].to_numpy(), cell["n"].to_numpy()), 4)
A["cell_corr_fon_exit_ever_weighted"] = round(wcorr(cell["fon"].to_numpy(), cell["exit_ever"].to_numpy(), cell["n"].to_numpy()), 4)
A["cell_corr_exit3_exit_ever_weighted"] = round(wcorr(cell["exit3"].to_numpy(), cell["exit_ever"].to_numpy(), cell["n"].to_numpy()), 4)
A["n_cells"] = int(len(cell))
for s, r in A["by_stage"].items():
    log(f"  {s:<16} n={r['n']:>6,}  fon {r['fon']:.3f}  exit3 {r['exit3']:.3f}  exit_ever {r['exit_ever']:.3f}")
log(f"  fon 범위(PE 제외) {A['fon_range_excl_pe']:.3f} · exit3 범위 {A['exit3_range_excl_pe']:.3f} · 셀 corr(fon, exit3) {A['cell_corr_fon_exit3_weighted']:+.3f} · corr(fon, exit_ever) {A['cell_corr_fon_exit_ever_weighted']:+.3f}")
OUT["A_stage_rates"] = A

# ── 고정지평 파트너 패널 (P001-33 A 와 동일) ───────────────────────────────
P, h = partner_pre(dn, "exit3")
P = add_post(P, dn, "exit3", end=END_FON)
P = add_tenure(P, first=first)
P = add_firm_means(P, TC + ["terrain", "adj"])
log(f"\n[패널] 파트너 {len(P):,} · 사후기 有 {int(P['has_post'].sum()):,}")


def contrast(res, a, b):
    d = res["_draws"][:, res["_xc"].index(a)] - res["_draws"][:, res["_xc"].index(b)]
    pt = res["_b"][res["_xc"].index(a)] - res["_b"][res["_xc"].index(b)]
    lo, hi = qci(d)
    return {"coef": round(float(pt), 5), "ci95": [round(lo, 5), round(hi, 5)], "sig": bool(lo > 0 or hi < 0)}


# ── B. 고정지평 Mundlak ─────────────────────────────────────────────────────
log("\n" + "=" * 100 + "\n[B] 고정지평 Mundlak (within / between / 대비)\n" + "=" * 100)
DEV, FM = [f"dev_{c}" for c in TC], [f"fm_{c}" for c in TC]
B1 = boot(P, "post_adj", DEV + FM + ["adj", "ln_n", "fp"] + TEN, DEV + FM, rng, return_draws=True)
show("B1 within(dev)", B1, DEV); show("B1 between(fm)", B1, FM)
B3 = boot(P, "post_adj", ["dev_terrain", "fm_terrain", "adj", "ln_n", "fp"] + TEN, ["dev_terrain", "fm_terrain"], rng, return_draws=True)
show("B3 총 terrain", B3, ["dev_terrain", "fm_terrain"])
OUT["B1_mundlak_parts_fixed"] = strip_draws(B1)
OUT["B1_contrast_tcs"] = contrast(B1, "dev_t_cs", "fm_t_cs")
OUT["B3_mundlak_total_fixed"] = strip_draws(B3)
OUT["B3_contrast_terrain"] = contrast(B3, "dev_terrain", "fm_terrain")
log(f"  대비(within − between): t_cs {OUT['B1_contrast_tcs']} · terrain {OUT['B3_contrast_terrain']}")

# ── C. 고정지평 함의 상쇄 ───────────────────────────────────────────────────
log("\n" + "=" * 100 + "\n[C] 고정지평 함의 상쇄 Σ β(fp→k|TEN)·β(k→post_adj|TEN)\n" + "=" * 100)
dd = P.dropna(subset=["post_adj"] + X2).copy()
grp = {c: g_.index.to_numpy() for c, g_ in dd.groupby("firm")}
kl = list(grp)


def products(s):
    b2 = fit(s, "post_adj", X2)
    out = {}
    for j_, k in enumerate(TC):
        b1 = fit(s, k, ["fp", "ln_n"] + TEN)
        out[f"gap_{k}"] = float(b1[0]); out[f"coef_{k}"] = float(b2[j_]); out[k] = float(b1[0] * b2[j_])
    out["total"] = sum(out[k] for k in TC)
    return out


pt = products(dd)
draws = {k: [] for k in pt}
for _ in range(NB):
    pick = rng.integers(0, len(kl), len(kl))
    s = dd.loc[np.concatenate([grp[kl[i]] for i in pick])]
    try:
        pr = products(s)
        for k in draws: draws[k].append(pr[k])
    except Exception:
        pass
C = {"n": int(len(dd))}
for k in pt:
    lo, hi = qci(np.array(draws[k]))
    C[k] = {"coef": round(pt[k], 5), "ci95": [round(lo, 5), round(hi, 5)]}
for k in TC + ["total"]:
    C[k]["within_pm0.02"] = bool(C[k]["ci95"][0] >= -0.02 and C[k]["ci95"][1] <= 0.02)
    C[k]["within_pm0.01"] = bool(C[k]["ci95"][0] >= -0.01 and C[k]["ci95"][1] <= 0.01)
    log(f"  {k:<6} 함의 {C[k]['coef']:+.4f} [{C[k]['ci95'][0]:+.4f},{C[k]['ci95'][1]:+.4f}]  ±0.02 {C[k]['within_pm0.02']}  ±0.01 {C[k]['within_pm0.01']}"
        + (f"   (gap {C['gap_' + k]['coef']:+.4f} × coef {C['coef_' + k]['coef']:+.3f})" if k in TC else ""))
OUT["C_implied_netting_fixed"] = C

# ── D. Ex-ante 창 · 거울 반쪽 ────────────────────────────────────────────────
log("\n" + "=" * 100 + "\n[D] Ex-ante 사전기(≤2014-10) vs 거울 반쪽(2014-11~2017-10)\n" + "=" * 100)
D = {}
for tag, lo_, hi_ in (("exante_le_2014_10", None, pd.Timestamp("2014-10-31")), ("mirror_2014_11_to_2017_10", pd.Timestamp("2014-10-31"), CUT)):
    sub = dn[(dn["dt"] <= hi_) & ((dn["dt"] > lo_) if lo_ is not None else True)]
    Pd, _ = partner_pre(sub, "exit3", cut=hi_)
    Pd = add_post(Pd, dn, "exit3", end=END_FON)
    Pd = add_tenure(Pd, first=first)
    F2 = boot(Pd, "post_adj", X2, TC, rng); F2t = boot(Pd, "post_adj", XT, ["terrain", "adj"], rng)
    show(f"{tag} F2", F2, TC); show(f"{tag} F2t", F2t, ["terrain", "adj"])
    D[tag] = {"n_partners": int(len(Pd)), "n_post": int(Pd["has_post"].sum()), "F2": F2, "F2t": F2t,
              "pct_of_full_F2t": round(F2t["terrain"]["coef"] / 0.27817 * 100, 1) if F2t else None}
OUT["D_exante_window"] = D

# ── E. 중복 기업만 (F4 의 보완) ─────────────────────────────────────────────
log("\n" + "=" * 100 + "\n[E] 사후기 = 사전기 투자 기업의 후속 딜만\n" + "=" * 100)
pre_pairs = set(zip(dn.loc[pre, "partner_uuid"], dn.loc[pre, "org_uuid"]))
po = build(dn[(dn["dt"] > CUT) & (dn["dt"] <= END_FON)], "exit3"); po = po[np.isfinite(po["r"])]
rep = np.array([(p_, o_) in pre_pairs for p_, o_ in zip(po["partner_uuid"], po["org_uuid"])])
P = P.join(po[rep].groupby("partner_uuid").agg(post_adj_rep=("r", "mean"), post_n_rep=("r", "size")), on="partner_uuid")
E_t = boot(P, "post_adj_rep", XT, ["terrain", "adj"], rng); show("E 중복만 F2t", E_t, ["terrain", "adj"])
E_c = boot(P, "post_adj_rep", X2, TC, rng); show("E 중복만 F2", E_c, TC)
OUT["E_overlap_only"] = {"F2t": E_t, "F2": E_c, "n_partners_with_rep": int(P["post_adj_rep"].notna().sum()), "share_rep_rows": round(float(rep.mean()), 4)}

# ── F. 고정지평 IPW ─────────────────────────────────────────────────────────
log("\n" + "=" * 100 + "\n[F] 고정지평 IPW (has_post ← 성분·adj·ln_n·fp·TEN, 로짓)\n" + "=" * 100)


def logit_fit(X, y, it=25):
    b = np.zeros(X.shape[1])
    for _ in range(it):
        p = 1 / (1 + np.exp(-X @ b)); W = p * (1 - p) + 1e-9
        step = np.linalg.solve(X.T @ (X * W[:, None]) + 1e-8 * np.eye(X.shape[1]), X.T @ (y - p))
        b += step
        if np.max(np.abs(step)) < 1e-8: break
    return b


sel = P.dropna(subset=TC + ["adj", "ln_n", "fp"] + TEN).copy()
Xs = np.column_stack([sel[c].to_numpy(float) for c in X2] + [np.ones(len(sel))])
bl = logit_fit(Xs, sel["has_post"].to_numpy(float))
ph = 1 / (1 + np.exp(-Xs @ bl)); ph = np.clip(ph, np.quantile(ph, 0.01), np.quantile(ph, 0.99))
sel["w_ipw"] = 1 / ph
sel_p = sel.dropna(subset=["post_adj"])
S1 = boot(sel, "has_post", X2, TC + ["tenure"], rng); show("F 선택(LPM)", S1, TC + ["tenure"])


def wfit(s, y, xc):
    X = np.column_stack([s[c].to_numpy(float) for c in xc] + [np.ones(len(s))]); w = np.sqrt(s["w_ipw"].to_numpy(float))
    return np.linalg.lstsq(X * w[:, None], s[y].to_numpy(float) * w, rcond=None)[0]


def wboot(df, y, xc, keys):
    dd_ = df.dropna(subset=[y] + xc)
    b = wfit(dd_, y, xc); g2 = {c: g_.index.to_numpy() for c, g_ in dd_.groupby("firm")}; k2 = list(g2); bs = []
    for _ in range(NB):
        pick = rng.integers(0, len(k2), len(k2)); s = dd_.loc[np.concatenate([g2[k2[i]] for i in pick])]
        try: bs.append(wfit(s, y, xc))
        except Exception: pass
    bs = np.array(bs); out = {"n": int(len(dd_)), "n_firms": int(dd_["firm"].nunique())}
    for k in keys:
        i = xc.index(k); lo, hi = qci(bs[:, i]); se = float(np.std(bs[:, i], ddof=1))
        out[k] = {"coef": round(float(b[i]), 5), "ci95": [round(lo, 5), round(hi, 5)], "sig": bool(lo > 0 or hi < 0), "se_boot": round(se, 5), "mde80": round(2.8 * se, 4)}
    return out


F_ipw = wboot(sel_p, "post_adj", XT, ["terrain", "adj"]); show("F IPW F2t", F_ipw, ["terrain", "adj"])
F_ipw_c = wboot(sel_p, "post_adj", X2, TC); show("F IPW F2", F_ipw_c, TC)
OUT["F_ipw_fixed"] = {"selection_lpm": S1, "F2t_ipw": F_ipw, "F2_ipw": F_ipw_c, "share_observed": round(float(sel["has_post"].mean()), 4),
                      "pct_change_vs_F2t": round((F_ipw["terrain"]["coef"] / 0.27817 - 1) * 100, 1)}

# ── G. days ≥ 0 판 ─────────────────────────────────────────────────────────
log("\n" + "=" * 100 + "\n[G] exit3 를 딜 이후 출구로 한정 (days ≥ 0)\n" + "=" * 100)
days = (dn["exit_dt"] - dn["dt"]).dt.days
dn["exit3_pos"] = ((days >= 0) & (days <= 365 * 3)).fillna(False).astype(float)
post_m = (dn["dt"] > CUT) & (dn["dt"] <= END_FON)
G = {"base_pre": round(float(dn.loc[pre, "exit3"].mean()), 4), "base_pre_pos": round(float(dn.loc[pre, "exit3_pos"].mean()), 4),
     "base_post": round(float(dn.loc[post_m, "exit3"].mean()), 4), "base_post_pos": round(float(dn.loc[post_m, "exit3_pos"].mean()), 4),
     "share_negative_lag_among_exit3_pre": round(float(1 - dn.loc[pre & (dn["exit3"] == 1), "exit3_pos"].mean()), 4),
     "share_negative_lag_among_exit3_post": round(float(1 - dn.loc[post_m & (dn["exit3"] == 1), "exit3_pos"].mean()), 4)}
Pg, _ = partner_pre(dn, "exit3_pos"); Pg = add_post(Pg, dn, "exit3_pos", end=END_FON); Pg = add_tenure(Pg, first=first)
G_t = boot(Pg, "post_adj", XT, ["terrain", "adj"], rng); show("G days≥0 F2t", G_t, ["terrain", "adj"])
G_c = boot(Pg, "post_adj", X2, TC, rng); show("G days≥0 F2", G_c, TC)
G.update({"F2t": G_t, "F2": G_c, "pct_of_F2t": round(G_t["terrain"]["coef"] / 0.27817 * 100, 1)})
log(f"  기저율 사전 {G['base_pre']:.4f}→{G['base_pre_pos']:.4f} · 사후 {G['base_post']:.4f}→{G['base_post_pos']:.4f} · 음의 시차 비중 사전 {G['share_negative_lag_among_exit3_pre']:.3f} 사후 {G['share_negative_lag_among_exit3_post']:.3f}")
OUT["G_days_ge0"] = G

# ── H. 표준화 계수 (같은 회귀) ──────────────────────────────────────────────
log("\n" + "=" * 100 + "\n[H] 표준화 계수 — 고정 F1t/F2t · 개방 R1t (같은 회귀의 terrain·adj)\n" + "=" * 100)


def std_pair(df, y, xc, rng_):
    res = boot(df, y, xc, ["terrain", "adj"], rng_)
    d_ = df.dropna(subset=[y] + xc)
    for k in ("terrain", "adj"):
        res[k]["beta_std"] = round(float(res[k]["coef"] * d_[k].std() / d_[y].std()), 4)
    return res


H = {"fixed_F1t": std_pair(P, "post_adj", ["terrain", "adj", "ln_n", "fp"], rng), "fixed_F2t": std_pair(P, "post_adj", XT, rng)}
Po, _ = partner_pre(dn, "exit_ever"); Po = add_post(Po, dn, "exit_ever"); Po = add_tenure(Po, first=first)
H["open_R1t"] = std_pair(Po, "post_adj", ["terrain", "adj", "ln_n", "fp"], rng)
H["open_R2t"] = std_pair(Po, "post_adj", XT, rng)
for k, v in H.items():
    log(f"  {k:<10} terrain {v['terrain']['coef']:+.3f} (std {v['terrain']['beta_std']:+.3f}) · adj {v['adj']['coef']:+.3f} (std {v['adj']['beta_std']:+.3f})")
    H[k]["ratio_std_terrain_over_adj"] = round(v["terrain"]["beta_std"] / v["adj"]["beta_std"], 3) if v["adj"]["beta_std"] else None
OUT["H_standardized"] = H

# ── I. exit3 성분 반분 일치도 ───────────────────────────────────────────────
log("\n" + "=" * 100 + "\n[I] exit3 성분 반분 일치도 (상한)\n" + "=" * 100)
hh = h[h["partner_uuid"].isin(P["partner_uuid"])].sort_values(["partner_uuid", "dt", "funding_round_uuid"]).copy()
hh["half"] = np.where(hh.groupby("partner_uuid").cumcount() % 2 == 0, "A", "B")
agg = hh.groupby(["partner_uuid", "half"]).agg(t_v=("t_v", "mean"), t_s=("t_s", "mean"), t_cs=("t_cs", "mean"), adj=("r", "mean"), raw=("exit3", "mean"))
agg["terrain"] = agg["raw"] - agg["adj"]
wide = agg.unstack("half"); wide.columns = [f"{a}_{b}" for a, b in wide.columns]
I = {}
for c in TC + ["terrain", "adj"]:
    r_ = float(wide[[f"{c}_A", f"{c}_B"]].dropna().corr().iloc[0, 1]); I[c] = {"r_half": round(r_, 4), "rho_SB": round(2 * r_ / (1 + r_), 4)}
    log(f"  {c:<8} r {r_:+.3f}  ρ_SB {I[c]['rho_SB']:.3f}")
OUT["I_split_half_agreement_exit3"] = I

# ── 판정 ────────────────────────────────────────────────────────────────────
pred = {"A_fon_flat_range_lt_0.08": A["fon_range_excl_pe"] < 0.08, "A_cell_corr_lt_0.3": A["cell_corr_fon_exit3_weighted"] < 0.3,
        "B_total_contrast_incl0": not OUT["B3_contrast_terrain"]["sig"], "B_tcs_contrast_incl0": not OUT["B1_contrast_tcs"]["sig"],
        "C_total_in_[-0.008,-0.002]": -0.008 <= C["total"]["coef"] <= -0.002, "C_within_pm0.02": C["total"]["within_pm0.02"],
        "C_within_pm0.01_predicted_fail": not C["total"]["within_pm0.01"],
        "D_exante_in_[0.10,0.30]": bool(D["exante_le_2014_10"]["F2t"] and 0.10 <= D["exante_le_2014_10"]["F2t"]["terrain"]["coef"] <= 0.30),
        "D_mirror_same_sign": bool(D["mirror_2014_11_to_2017_10"]["F2t"] and D["mirror_2014_11_to_2017_10"]["F2t"]["terrain"]["coef"] > 0),
        "E_overlap_gt_F4t": bool(E_t and E_t["terrain"]["coef"] > 0.19258),
        "F_ipw_within_15pct": abs(OUT["F_ipw_fixed"]["pct_change_vs_F2t"]) <= 15, "G_F2t_within_10pct": abs(G["pct_of_F2t"] - 100) <= 10,
        "H_std_adj_gt_terrain_fixed": H["fixed_F2t"]["adj"]["beta_std"] > H["fixed_F2t"]["terrain"]["beta_std"],
        "I_tcs_agreement_0.4_0.5": 0.4 <= I["t_cs"]["rho_SB"] <= 0.5}
pred = {k: bool(v) for k, v in pred.items()}
OUT["prediction_check"] = pred
lookahead = bool(D["exante_le_2014_10"]["F2t"] and D["exante_le_2014_10"]["F2t"]["terrain"]["coef"] < 0.05 and D["mirror_2014_11_to_2017_10"]["F2t"]["terrain"]["coef"] > 0.25)
OUT["flags"] = {"location_resolved_fixed": bool(OUT["B3_contrast_terrain"]["sig"] or OUT["B1_contrast_tcs"]["sig"]), "lookahead_artifact": lookahead,
                "gender_bound_within_pm0.01_fixed": C["total"]["within_pm0.01"], "gender_bound_within_pm0.02_fixed": C["total"]["within_pm0.02"]}
verdict = (f"A fon 범위 {A['fon_range_excl_pe']:.3f} / exit3 범위 {A['exit3_range_excl_pe']:.3f}, 셀 corr(fon,exit3) {A['cell_corr_fon_exit3_weighted']:+.2f} | "
           f"B 고정 Mundlak terrain within {fmt(B3, 'dev_terrain')} · between {fmt(B3, 'fm_terrain')} · 대비 {OUT['B3_contrast_terrain']['coef']:+.3f} "
           f"[{OUT['B3_contrast_terrain']['ci95'][0]:+.3f},{OUT['B3_contrast_terrain']['ci95'][1]:+.3f}]; t_cs within {fmt(B1, 'dev_t_cs')} · between {fmt(B1, 'fm_t_cs')} | "
           f"C 고정 함의 총 {C['total']['coef']:+.4f} [{C['total']['ci95'][0]:+.4f},{C['total']['ci95'][1]:+.4f}] ±0.02 {C['total']['within_pm0.02']} ±0.01 {C['total']['within_pm0.01']} | "
           f"D ex-ante F2t {fmt(D['exante_le_2014_10']['F2t'], 'terrain')} (n {D['exante_le_2014_10']['n_post']}) · 거울 {fmt(D['mirror_2014_11_to_2017_10']['F2t'], 'terrain')} | "
           f"E 중복만 {fmt(E_t, 'terrain')} | F IPW {fmt(F_ipw, 'terrain')} ({OUT['F_ipw_fixed']['pct_change_vs_F2t']:+.0f}%) | G days≥0 {fmt(G_t, 'terrain')} ({G['pct_of_F2t']:.0f}%) | "
           f"H std 고정 terrain {H['fixed_F2t']['terrain']['beta_std']:+.3f} vs adj {H['fixed_F2t']['adj']['beta_std']:+.3f}; 개방 {H['open_R1t']['terrain']['beta_std']:+.3f} vs {H['open_R1t']['adj']['beta_std']:+.3f} | "
           f"I exit3 t_cs 일치도 {I['t_cs']['rho_SB']:.2f} — 위치 결정 {OUT['flags']['location_resolved_fixed']} · look-ahead 인공물 {lookahead} (예측 적중 {sum(pred.values())}/{len(pred)})")
emit("P001-38", "R3 결정 검정(파트너 수준, 고정 출구지평): 단계별 기저율 · Mundlak · 성별 함의 · ex-ante 창 · 중복만 · IPW · days≥0 · 표준화 · 반분", "OK", OUT,
     prediction="A fon 평탄·corr<0.3; B 위치 미결정; C 총 ∈[−0.008,−0.002], ±0.02 안·±0.01 실패 예상; D ex-ante ∈[0.10,0.30] 거울 동부호; E>F4t; F ±15%; G ±10%; H std adj>terrain; I 0.4–0.5",
     verdict=verdict, kill_met=False, n=int(len(P)),
     extra={"stage": 7, "feeds": "R3 재심 응답 (ident.md F-1/F-3/F-4, R-3/R-4/R-7/R-13, CP-3, 결정 검정 1–5·8)", "slug": "fixed_horizon_recheck",
            "builds_on": "P001-32/33/35/36", "common_sha256_16": COMMON_SHA})
log("done")
