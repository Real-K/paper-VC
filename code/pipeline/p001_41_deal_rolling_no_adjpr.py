# -*- coding: utf-8 -*-
"""p001_41 — R3 R-9: 딜 수준 회사×연 FE 사양(P001-34 D3/D3t)을 파트너 사전 잔차(adj_pr) 통제 유무로 병기

[왜] R3 식별 심판 R-9: `adj_pr`(파트너의 이전 딜 결과를 담은 통제)이 P001-34 의 모든 사양에 들어가고, D3 표본 딜의 50.6% 가
 반복 기업이다. adj_pr 은 사전 성과이므로 "bad control"은 아니지만, 이전 결과에 조건부인 계수와 무조건 계수를 함께 보여야
 반복 기업 경로와 조건부 해석이 분리된다. P001-34 의 rolling() 을 그대로 복제하고 D2/D3/D3t 를 adj_pr 유·무로 병기한다.
[사전 예측] (2026-09-09, 결과 조회 전)
 adj_pr 제거 시 D3 t_cs_pr 는 ±0.03 이내 이동(0.05 → 0.02~0.08); D3t terrain_pr 도 ±0.03; adj_pr 자체는 +0.24* 유지.
 풀(D2) 에서는 제거 시 계수가 커진다(adj 와 terrain 의 음의 표본 상관: 0.150 → 0.16~0.20).
[판정] 진단 — status OK.
"""
import numpy as np
import pandas as pd

from p001_rescue_common import (COMMON_SHA, END_FON, boot, build, emit, first_deal_dates, fmt, load_deals, log)

rng = np.random.default_rng(20260941)
NB = 300
OUT = {}
dn = load_deals(with_exit_dt=True)
first = first_deal_dates()
dn["yi"] = dn["y"].astype(int)
dn["fy_cell"] = dn["investor_uuid"] + "|" + dn["y"]
dn["tenure_at"] = (dn["dt"] - dn["partner_uuid"].map(first)).dt.days / 365.25
dn["tenure_at2"] = dn["tenure_at"] ** 2
W0, W1 = pd.Timestamp("2013-01-01"), END_FON
TCP = ["t_v_pr", "t_s_pr", "t_cs_pr"]
TENA = ["tenure_at", "tenure_at2"]
YD = [f"yd{yv}" for yv in range(2014, 2021)]


def rolling(df, ycol):
    b = build(df, ycol)
    b = b[np.isfinite(b["r"])].copy()
    g = (b.groupby(["partner_uuid", "yi"]).agg(sv=("t_v", "sum"), ss=("t_s", "sum"), sc=("t_cs", "sum"), sr=("r", "sum"), k=("r", "size"))
         .reset_index().sort_values(["partner_uuid", "yi"]))
    for c in ("sv", "ss", "sc", "sr", "k"):
        g[f"c{c}"] = g.groupby("partner_uuid")[c].cumsum() - g[c]
    m = b.merge(g[["partner_uuid", "yi", "csv", "css", "csc", "csr", "ck"]], on=["partner_uuid", "yi"], how="left")
    m = m[(m["ck"] >= 5) & (m["dt"] >= W0) & (m["dt"] <= W1)].copy()
    m["t_v_pr"], m["t_s_pr"], m["t_cs_pr"] = m["csv"] / m["ck"], m["css"] / m["ck"], m["csc"] / m["ck"]
    m["adj_pr"] = m["csr"] / m["ck"]
    m["terrain_pr"] = m["t_v_pr"] + m["t_s_pr"] + m["t_cs_pr"]
    m["ln_npr"] = np.log(m["ck"])
    for yv in range(2014, 2021):
        m[f"yd{yv}"] = (m["yi"] == yv).astype(float)
    return m


def show(tag, res, keys):
    log(f"  {tag:<28} n={res['n']:,}/{res['n_firms']:,} | " + " · ".join(f"{k} {fmt(res, k)}" for k in keys if k in res))


m1 = rolling(dn, "exit3")
fy = m1.groupby("fy_cell")["partner_uuid"].nunique()
m1m = m1[m1["fy_cell"].map(fy) >= 2].copy()
OUT["corr_adjpr_terrainpr"] = round(float(m1[["adj_pr", "terrain_pr"]].corr().iloc[0, 1]), 4)
OUT["corr_adjpr_tcspr"] = round(float(m1[["adj_pr", "t_cs_pr"]].corr().iloc[0, 1]), 4)
log(f"[구성] 딜 {len(m1):,} · 회사×연(파트너≥2) 딜 {len(m1m):,} · corr(adj_pr, terrain_pr) {OUT['corr_adjpr_terrainpr']:+.3f}")
for tag, ctrl in (("with_adjpr", ["adj_pr", "ln_npr", "fp"]), ("no_adjpr", ["ln_npr", "fp"])):
    log("\n" + "=" * 100 + f"\n[{tag}]\n" + "=" * 100)
    D2 = boot(m1, "r", TCP + ctrl + TENA + YD, TCP + (["adj_pr"] if "adj_pr" in ctrl else []), rng, nb=NB, cluster="investor_uuid"); show("D2 풀 +연공+연도", D2, TCP + ["adj_pr"])
    D3 = boot(m1m, "r", TCP + ctrl + TENA, TCP + (["adj_pr"] if "adj_pr" in ctrl else []), rng, nb=NB, demean="fy_cell", cluster="investor_uuid"); show("D3 회사×연 FE", D3, TCP + ["adj_pr"])
    D3t = boot(m1m, "r", ["terrain_pr"] + ctrl + TENA, ["terrain_pr"], rng, nb=NB, demean="fy_cell", cluster="investor_uuid"); show("D3t 총 회사×연 FE", D3t, ["terrain_pr"])
    D2t = boot(m1, "r", ["terrain_pr"] + ctrl + TENA + YD, ["terrain_pr"], rng, nb=NB, cluster="investor_uuid"); show("D2t 총 풀", D2t, ["terrain_pr"])
    OUT[tag] = {"D2": D2, "D2t": D2t, "D3": D3, "D3t": D3t}
w, n_ = OUT["with_adjpr"], OUT["no_adjpr"]
OUT["delta_no_minus_with"] = {"D3_tcs": round(n_["D3"]["t_cs_pr"]["coef"] - w["D3"]["t_cs_pr"]["coef"], 5), "D3t_terrain": round(n_["D3t"]["terrain_pr"]["coef"] - w["D3t"]["terrain_pr"]["coef"], 5),
                              "D2_tcs": round(n_["D2"]["t_cs_pr"]["coef"] - w["D2"]["t_cs_pr"]["coef"], 5), "D2t_terrain": round(n_["D2t"]["terrain_pr"]["coef"] - w["D2t"]["terrain_pr"]["coef"], 5)}
pred = {"D3_tcs_shift_le_0.03": abs(OUT["delta_no_minus_with"]["D3_tcs"]) <= 0.03, "D3t_shift_le_0.03": abs(OUT["delta_no_minus_with"]["D3t_terrain"]) <= 0.03,
        "adjpr_sig_D3": bool(w["D3"]["adj_pr"]["sig"]), "D2_tcs_rises_without_adjpr": OUT["delta_no_minus_with"]["D2_tcs"] > 0}
pred = {k: bool(v) for k, v in pred.items()}
OUT["prediction_check"] = pred
verdict = (f"D3 t_cs: adj_pr 有 {fmt(w['D3'], 't_cs_pr')} → 無 {fmt(n_['D3'], 't_cs_pr')} (Δ {OUT['delta_no_minus_with']['D3_tcs']:+.3f}) · D3t: {fmt(w['D3t'], 'terrain_pr')} → {fmt(n_['D3t'], 'terrain_pr')} · "
           f"D2 t_cs: {fmt(w['D2'], 't_cs_pr')} → {fmt(n_['D2'], 't_cs_pr')} · adj_pr(D3) {fmt(w['D3'], 'adj_pr')} · corr(adj_pr, terrain_pr) {OUT['corr_adjpr_terrainpr']:+.2f} (예측 적중 {sum(pred.values())}/{len(pred)})")
emit("P001-41", "딜 수준 회사×연 FE — 파트너 사전 잔차(adj_pr) 통제 유·무 병기 (R3 R-9)", "OK", OUT,
     prediction="adj_pr 제거 시 D3 t_cs·D3t 이동 ≤0.03; adj_pr +0.24*; 풀 D2 는 제거 시 상승",
     verdict=verdict, kill_met=False, n=int(len(m1m)),
     extra={"stage": 7, "feeds": "R3 재심 응답 (ident.md R-9)", "slug": "deal_rolling_no_adjpr", "builds_on": "P001-34", "common_sha256_16": COMMON_SHA})
log("done")
