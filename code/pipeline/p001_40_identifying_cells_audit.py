# -*- coding: utf-8 -*-
"""p001_40 — P2: 헤드라인(Table 3 사다리)의 식별 변이·동료 가용성 감사

[왜] R3 설계 제안 P2: 회사×연×섹터 FE 아래에서 fp 가 변하지 않는 셀은 추정에 기여하지 않는다. 보고된 n(7,103)은 −4.55/−6.25 를
 식별하는 관측 수를 한 자릿수 과대 표시한다. 제안자의 probe: NA+EU FF 딜에서 혼합 셀 174 / 딜 430 (6.1%); 여성 파트너 FF 딜의
 23.7% 만 같은 셀에 남성 동료 딜이 있음; 여성 파트너 326 중 90 만 동료 비교가 존재. 이를 정본 스크립트로 재계산하고,
 (i) 혼합 셀 부분표본에서 헤드라인이 정확히 재현되는지(검산), (ii) leave-one-cell-out 잭나이프, (iii) 같은 셀 구조에서 fp 를
 셀 내 무작위 재배정한 위약 분포(잡음 바닥)를 낸다. "동료 비교 인공물"을 사양 사다리의 추론에서 파트너 명부의 구조적 사실로.

[구성] P001-10 과 동일: ff==1 · dt ≤ 2017-10-31 · 결과 exit_ever · 셀 4단(cell_year, cell0, cell_cat, cell_stage) · 셀 내 demean OLS.
 범위 GLOBAL / NAEU. 위약 400회, 잭나이프는 혼합 셀 전부.
[사전 예측] (2026-09-09, 결과 조회 전)
 NAEU cell_cat: 혼합 셀 ≈174, 딜 ≈430, FP-FF 딜의 동료 가용 ≈24%, 여성 파트너 가용 ≈90/326. 혼합 셀 부분표본 계수 = 전체 계수(정확).
 잭나이프: 어떤 셀을 빼도 헤드라인이 자기 CI 밖으로 나가지 않는다(단일 셀 의존 없음). 위약 p95|β| ≈ 5~7pp (NAEU) — 헤드라인 −4.55 는
 잡음 바닥 안, GLOBAL −6.25 는 바닥 근처(GLOBAL 은 셀이 더 많아 바닥 낮음).
[판정] 진단 — status OK.
"""
import numpy as np
import pandas as pd

from p001_rescue_common import COMMON_SHA, NAEU, emit, log, qci

rng = np.random.default_rng(20260940)
NB, NPL = 500, 400
import os
HERE = os.path.dirname(os.path.abspath(__file__))
d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v2.parquet"))
d["dt"] = pd.to_datetime(d["dt"])
d = d[(d["ff"] == 1.0) & (d["dt"] <= "2017-10-31")].copy()
d["cell_year"] = d["year"]
d["reg"] = np.where(d["country_code"].isin(NAEU), "NAEU", "OTHER")
CELLS = [("year", "cell_year"), ("invyear", "cell0"), ("pluscat", "cell_cat"), ("plusstage", "cell_stage")]
OUT = {}


def within_beta(dd, cell):
    yr = (dd["exit_ever"] - dd["exit_ever"].groupby(dd[cell]).transform("mean")).to_numpy()
    xr = (dd["fp"] - dd["fp"].groupby(dd[cell]).transform("mean")).to_numpy()
    sxx = float((xr * xr).sum())
    return float((xr * yr).sum() / sxx) if sxx > 0 else np.nan


def boot_ci(dd, cell, nb=NB):
    grp = {c: g.index.to_numpy() for c, g in dd.groupby("investor_uuid")}
    kl = list(grp); bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(kl), len(kl))
        s = dd.loc[np.concatenate([grp[kl[i]] for i in pick])]
        b = within_beta(s, cell)
        if np.isfinite(b): bs.append(b)
    return qci(np.array(bs))


for scope in ("GLOBAL", "NAEU"):
    df = (d if scope == "GLOBAL" else d[d["reg"] == "NAEU"]).reset_index(drop=True)
    res = {"n_deals": int(len(df)), "n_fp_deals": int(df["fp"].sum()), "n_female_partners": int(df.loc[df["fp"] == 1, "partner_uuid"].nunique())}
    log("\n" + "=" * 100 + f"\n[{scope}] FF 딜 {len(df):,} · 여성 파트너 딜 {res['n_fp_deals']:,} · 여성 파트너 {res['n_female_partners']:,}\n" + "=" * 100)
    for name, cell in CELLS:
        g = df.groupby(cell)["fp"].agg(["mean", "size"])
        mixed = g.index[(g["mean"] > 0) & (g["mean"] < 1)]
        m = df[df[cell].isin(mixed)]
        beta_full = within_beta(df, cell); beta_mixed = within_beta(m, cell)
        fp_rows = df[df["fp"] == 1]
        fp_peer = fp_rows[cell].isin(mixed)
        fem_with_peer = fp_rows.loc[fp_peer, "partner_uuid"].nunique()
        r = {"n_cells": int(len(g)), "n_mixed_cells": int(len(mixed)), "n_deals_mixed": int(len(m)), "share_deals_mixed": round(len(m) / len(df), 4),
             "share_fp_deals_with_peer": round(float(fp_peer.mean()), 4), "n_female_partners_with_peer": int(fem_with_peer),
             "beta_full_pp": round(beta_full * 100, 4), "beta_mixed_pp": round(beta_mixed * 100, 4), "identical": bool(abs(beta_full - beta_mixed) < 1e-9)}
        log(f"  {name:<10} 셀 {r['n_cells']:>6,} · 혼합 {r['n_mixed_cells']:>5,} · 혼합 딜 {r['n_deals_mixed']:>6,} ({r['share_deals_mixed']:.1%}) · FP딜 동료가용 {r['share_fp_deals_with_peer']:.1%} · "
            f"여성파트너 가용 {fem_with_peer}/{res['n_female_partners']} · β 전체 {r['beta_full_pp']:+.2f} = 혼합 {r['beta_mixed_pp']:+.2f} ({r['identical']})")
        if name in ("pluscat", "plusstage"):
            ci = boot_ci(df, cell); r["ci95_pp"] = [round(ci[0] * 100, 2), round(ci[1] * 100, 2)]
            # 잭나이프: 혼합 셀 하나씩 제외
            jk = []
            for c in mixed:
                jk.append(within_beta(df[df[cell] != c], cell))
            jk = np.array(jk) * 100
            r["jackknife"] = {"n": int(len(jk)), "min_pp": round(float(jk.min()), 3), "max_pp": round(float(jk.max()), 3),
                              "max_abs_shift_pp": round(float(np.max(np.abs(jk - beta_full * 100))), 3),
                              "any_outside_ci": bool((jk < r["ci95_pp"][0]).any() or (jk > r["ci95_pp"][1]).any())}
            # 위약: 혼합 셀 안에서 fp 를 셀 내 무작위 재배정 (셀별 fp 개수 보존)
            pl = []
            mm = m.reset_index(drop=True)
            for _ in range(NPL):
                fp_perm = mm.groupby(cell)["fp"].transform(lambda s: pd.Series(rng.permutation(s.to_numpy()), index=s.index))
                yr = (mm["exit_ever"] - mm["exit_ever"].groupby(mm[cell]).transform("mean")).to_numpy()
                xr = (fp_perm - fp_perm.groupby(mm[cell]).transform("mean")).to_numpy()
                pl.append(float((xr * yr).sum() / (xr * xr).sum()) * 100)
            pl = np.abs(np.array(pl))
            r["placebo"] = {"n": NPL, "p95_abs_pp": round(float(np.percentile(pl, 95)), 3), "p50_abs_pp": round(float(np.percentile(pl, 50)), 3),
                            "share_ge_headline": round(float(np.mean(pl >= abs(beta_full * 100))), 4)}
            log(f"             CI {r['ci95_pp']} · 잭나이프 [{r['jackknife']['min_pp']:+.2f},{r['jackknife']['max_pp']:+.2f}] 최대이동 {r['jackknife']['max_abs_shift_pp']:.2f}pp CI밖 {r['jackknife']['any_outside_ci']} · "
                f"위약 p95|β| {r['placebo']['p95_abs_pp']:.2f}pp · |위약|≥|헤드라인| 비중 {r['placebo']['share_ge_headline']:.3f}")
        res[name] = r
    # 전체 딜(FF 아닌 것 포함)의 동료 가용 — 참고
    OUT[scope] = res

# 참고: 전 딜(ff 무관)에서 여성 파트너 딜의 동료 가용 (NAEU, cell_cat)
d_all = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v2.parquet"))
d_all["dt"] = pd.to_datetime(d_all["dt"])
d_all = d_all[(d_all["dt"] <= "2017-10-31") & d_all["country_code"].isin(NAEU)]
g = d_all.groupby("cell_cat")["fp"].mean()
mixed_all = g.index[(g > 0) & (g < 1)]
OUT["NAEU_all_deals_fp_peer_share_cell_cat"] = round(float(d_all.loc[d_all["fp"] == 1, "cell_cat"].isin(mixed_all).mean()), 4)
OUT["NAEU_female_partners_ge5_ff_deals"] = int((d[(d["reg"] == "NAEU") & (d["fp"] == 1)].groupby("partner_uuid").size() >= 5).sum())

n = OUT["NAEU"]["pluscat"]
pred = {"NAEU_mixed_cells_170_180": 170 <= n["n_mixed_cells"] <= 180, "NAEU_mixed_deals_420_440": 420 <= n["n_deals_mixed"] <= 440,
        "NAEU_fp_peer_share_0.22_0.26": 0.22 <= n["share_fp_deals_with_peer"] <= 0.26, "identical_all": all(OUT[s][c]["identical"] for s in ("GLOBAL", "NAEU") for c, _ in CELLS),
        "NAEU_jackknife_none_outside": not n["jackknife"]["any_outside_ci"], "NAEU_placebo_p95_5_7": 5 <= n["placebo"]["p95_abs_pp"] <= 7,
        "GLOBAL_placebo_p95_lt_NAEU": OUT["GLOBAL"]["pluscat"]["placebo"]["p95_abs_pp"] < n["placebo"]["p95_abs_pp"]}
pred = {k: bool(v) for k, v in pred.items()}
OUT["prediction_check"] = pred
gl = OUT["GLOBAL"]["pluscat"]
verdict = (f"NAEU 회사×연×섹터: 혼합 셀 {n['n_mixed_cells']}/{n['n_cells']:,} · 딜 {n['n_deals_mixed']}/{OUT['NAEU']['n_deals']:,} ({n['share_deals_mixed']:.1%}) · FP-FF 딜 동료 가용 {n['share_fp_deals_with_peer']:.1%} · "
           f"여성 파트너 {n['n_female_partners_with_peer']}/{OUT['NAEU']['n_female_partners']} · β 전체=혼합 {n['identical']} · 잭나이프 최대이동 {n['jackknife']['max_abs_shift_pp']:.2f}pp (CI밖 {n['jackknife']['any_outside_ci']}) · "
           f"위약 p95 {n['placebo']['p95_abs_pp']:.2f}pp vs |β| {abs(n['beta_full_pp']):.2f} | GLOBAL: 혼합 셀 {gl['n_mixed_cells']} · 딜 {gl['n_deals_mixed']} ({gl['share_deals_mixed']:.1%}) · 위약 p95 {gl['placebo']['p95_abs_pp']:.2f}pp vs |β| {abs(gl['beta_full_pp']):.2f} · "
           f"잭나이프 CI밖 {gl['jackknife']['any_outside_ci']} (예측 적중 {sum(pred.values())}/{len(pred)})")
emit("P001-40", "P2: 헤드라인의 식별 변이(혼합 셀·딜) · 동료 가용성 · 잭나이프 · 셀 내 재배정 위약", "OK", OUT,
     prediction="NAEU cell_cat 혼합 ≈174/430, FP 동료가용 ≈24%, 여성 ≈90/326; 혼합=전체 정확; 잭나이프 CI 안; 위약 p95 5~7pp",
     verdict=verdict, kill_met=False, n=int(OUT["NAEU"]["n_deals"]),
     extra={"stage": 7, "feeds": "R3 설계 제안 P2 → §4 서술 강화", "slug": "identifying_cells_audit", "builds_on": "P001-10", "common_sha256_16": COMMON_SHA})
log("done")
