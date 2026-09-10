# -*- coding: utf-8 -*-
"""p001_55 — R5-3 + ident 항목 4: Table 3 을 고정 36개월 출구지평·딜 ≤2020-10 로 다시 재고, 교차 딜 셀(다중 라운드)을 추정량으로, 달력 거칠기 사다리와 딜 수준 처치 코딩

[왜] Table 3 의 헤드라인(exit_ever, 딜 ≤2017-10)은 다중 라운드 셀 61개/195 딜에서 MDE 17.5pp(0.35 sd) — 헤드라인 크기(0.125 sd)의 효과를 판별할 수 없다.
 설계 심판 R5-3 probe: 결과를 36개월 고정지평 exit3 로 바꾸고 딜을 2020-10 까지 넓히면 다중 라운드 셀 174/652 딜(naive MDE 7.9pp, 0.20 sd); 달력을 2년·3년으로
 거칠게 하거나 회사×섹터 + 가법 연 FE 로 가면 Σx̃²(결과 변이 셀 기준)가 42.8 → 340 으로 는다 — R3 설계 제안 P2 의 "달력 거칠기는 식별 변이를 사지 않는다" 는
 처치 변이 셀만 센 결론이었다(교훈 74). 식별 심판 항목 4: 파트너 행을 (라운드, 투자사)로 접어 딜을 female-only / mixed / male-only 로 코딩하면 비희석
 추정량이 "셀 선택" 이 아니라 "코딩 선택" 이 된다.

[구성] sample_v1 NAEU FF 딜(load_deals). y = exit3, 딜 ≤ 2020-10(END_FON); 기준 재현 행 = exit_ever, 딜 ≤ 2017-10(P001-49 NAEU). 셀 정의: 회사×연×섹터(cell_cat) ·
 +단계(cell_stage) · 회사×2년×섹터 · 회사×3년×섹터 · 회사×섹터 + 가법 연 FE(두-방향 demean). 각: 혼합 셀·단일 라운드 셀·다중 라운드 셀·결과 변이 셀 수, Σx̃² 희석,
 β 전체, β 다중 라운드(투자사 군집 부트 500, MDE80, 셀 내 재배정 위약 p95 400). 딜 수준 코딩: (라운드, 투자사) 단위, fo/mx/mo; cell_cat 안에서 y ~ fo + mx
 (mo 기준), fo 변이 셀만; 투자사 군집 부트 500.
[사전 예측] (2026-09-09, 결과 조회 전; 설계 심판 probe 는 n·Σx̃²·naive MDE 만)
 cell_cat exit3 다중 라운드: 셀 160–190 / 딜 600–700 · β ∈ [−8, +2]pp, CI 0 포함, MDE80 8–11pp(투자사 군집) · 위약 p95 6–9pp.
 회사×2년×섹터: β 가 연 셀 값과 3pp 이내. +단계 비희석 추정치는 섹터 셀 값의 절반 미만만큼 0 쪽으로 이동(C-2 "약 절반" 정합).
 회사×섹터 + 연 FE: MDE 5–7pp. 딜 수준 코딩(fo vs mo, cell_cat exit3): 변이 셀 150–200, β 가 다중 라운드 β 와 3pp 이내.
[판정] 감사 — status OK (KILL 없음). 다중 라운드 exit3 상단 < 0 이면 첫 교차 딜 결손 검출 → P001-54 결과와 나란히 §4 재검.
"""
import numpy as np
import pandas as pd

from p001_rescue_common import COMMON_SHA, CUT, END_FON, emit, load_deals, log, qci
from p001_v6_common import V6_SHA, partner_gender_rows

rng = np.random.default_rng(20260955)
NB, NPL, ITERS = 500, 400, 60
OUT = {}
dn = load_deals(with_exit_dt=True)
ff_all = dn[dn["ff"] == 1].copy()
yr_ = pd.to_numeric(ff_all["year"]).astype(int)
ff_all["c2"] = ff_all["investor_uuid"] + "|" + (yr_ // 2 * 2).astype(str) + "|" + ff_all["cat"]
ff_all["c3"] = ff_all["investor_uuid"] + "|" + (yr_ // 3 * 3).astype(str) + "|" + ff_all["cat"]
ff_all["cfs"] = ff_all["investor_uuid"] + "|" + ff_all["cat"]
CELLS = [("cell_cat", "firm×year×sector"), ("cell_stage", "firm×year×sector×stage"), ("c2", "firm×2yr×sector"), ("c3", "firm×3yr×sector"), ("cfs", "firm×sector + year FE")]


def demean1(v, key):
    return v - pd.Series(v).groupby(key).transform("mean").to_numpy()


def demean2(v, k1, k2, iters=ITERS):
    for _ in range(iters):
        v = demean1(v, k1); v = demean1(v, k2)
    return v


def within_beta(dd, cell, y, twoway=False):
    if twoway:
        yr = demean2(dd[y].to_numpy(float), dd[cell].to_numpy(), dd["y"].to_numpy()); xr = demean2(dd["fp"].to_numpy(float), dd[cell].to_numpy(), dd["y"].to_numpy())
    else:
        yr = demean1(dd[y].to_numpy(float), dd[cell].to_numpy()); xr = demean1(dd["fp"].to_numpy(float), dd[cell].to_numpy())
    sxx = float((xr * xr).sum())
    return (float((xr * yr).sum() / sxx) if sxx > 0 else np.nan), sxx


def boot_ci(dd, cell, y, twoway=False, nb=NB, xcol="fp"):
    grp = {c: g.index.to_numpy() for c, g in dd.groupby("investor_uuid")}; kl = list(grp); bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(kl), len(kl)); s = dd.loc[np.concatenate([grp[kl[i]] for i in pick])]
        v = within_beta(s.rename(columns={xcol: "fp"}) if xcol != "fp" else s, cell, y, twoway)[0]
        if np.isfinite(v): bs.append(v)
    bs = np.array(bs); lo, hi = qci(bs)
    return [round(lo * 100, 2), round(hi * 100, 2)], round(2.8 * float(np.std(bs, ddof=1)) * 100, 2), int(len(bs))


def placebo_p95(m, cell, y, twoway=False, n=NPL):
    mm = m.reset_index(drop=True); pl = []
    for _ in range(n):
        fpp = mm.groupby(cell)["fp"].transform(lambda s: pd.Series(rng.permutation(s.to_numpy()), index=s.index))
        v = within_beta(mm.assign(fp=fpp), cell, y, twoway)[0]
        if np.isfinite(v): pl.append(abs(v) * 100)
    return round(float(np.percentile(pl, 95)), 2) if pl else None


def ladder(ffd, y, tag):
    res = {"y": y, "n_ff_deals": int(len(ffd)), "base_y": round(float(ffd[y].mean()), 4), "sd_y": round(float(ffd[y].std()), 4)}
    for cell, lab in CELLS:
        tw = cell == "cfs"
        g = ffd.groupby(cell)["fp"].agg(["mean", "size"]); mixed = g.index[(g["mean"] > 0) & (g["mean"] < 1)]
        m = ffd[ffd[cell].isin(mixed)].copy()
        nr = m.groupby(cell)["funding_round_uuid"].nunique(); single = set(nr.index[nr == 1]); multi = set(nr.index[nr >= 2])
        yv = m.groupby(cell)[y].var(ddof=0).fillna(0); varpos = set(yv.index[yv > 0])
        xr = demean1(m["fp"].to_numpy(float), m[cell].to_numpy()) ** 2
        dil = float(xr[m[cell].isin(single).to_numpy()].sum() / xr.sum()) if xr.sum() > 0 else np.nan
        bfull, sxx_full = within_beta(ffd, cell, y, tw)
        r = {"label": lab, "n_mixed_cells": int(len(mixed)), "n_deals_mixed": int(len(m)), "n_single_round_cells": len(single), "n_multi_round_cells": len(multi), "n_deals_multi": int(m[cell].isin(multi).sum()),
             "n_cells_var_pos": len(varpos), "n_deals_var_pos": int(m[cell].isin(varpos).sum()), "dilution_share_sxx_single_round": round(dil, 4), "beta_full_pp": round(bfull * 100, 3), "sxx_full": round(sxx_full, 2)}
        mm = m[m[cell].isin(multi)].copy()
        if len(mm) >= 30 and mm[cell].nunique() >= 8:
            b, sxx = within_beta(mm, cell, y, tw); ci, mde, nb_ = boot_ci(mm, cell, y, tw)
            r.update({"beta_multi_pp": round(b * 100, 3), "ci_multi_pp": ci, "mde80_multi_pp": mde, "mde80_multi_sd": round(mde / 100 / res["sd_y"], 3), "sxx_multi": round(sxx, 2), "placebo_p95_multi_pp": placebo_p95(mm, cell, y, tw),
                      "n_boot_ok": nb_, "n_firms_multi": int(mm["investor_uuid"].nunique())})
        else:
            r["beta_multi_pp"] = None
        res[cell] = r
        log(f"  {tag:<12} {lab:<26} 혼합 {r['n_mixed_cells']:>4}/{r['n_deals_mixed']:>5} · 다중 {r['n_multi_round_cells']:>4}/{r['n_deals_multi']:>5} · 변이 {r['n_cells_var_pos']:>3}/{r['n_deals_var_pos']:>4} · 희석 {dil:.2f} · "
            f"β전체 {r['beta_full_pp']:+.2f} · β다중 {r.get('beta_multi_pp')} {r.get('ci_multi_pp')} MDE {r.get('mde80_multi_pp')} ({r.get('mde80_multi_sd')} sd) 위약 {r.get('placebo_p95_multi_pp')}")
    return res


log("\n" + "=" * 100 + "\n[A] exit3 · 딜 ≤ 2020-10 (고정 36m 지평)\n" + "=" * 100)
ffA = ff_all[ff_all["dt"] <= END_FON].reset_index(drop=True)
OUT["A_exit3_2020"] = ladder(ffA, "exit3", "A exit3")
log("\n" + "=" * 100 + "\n[B] exit_ever · 딜 ≤ 2017-10 (Table 3 기준 재현)\n" + "=" * 100)
ffB = ff_all[ff_all["dt"] <= CUT].reset_index(drop=True)
OUT["B_exit_ever_2017"] = ladder(ffB, "exit_ever", "B exit_ever")
log("\n" + "=" * 100 + "\n[C] fon · 딜 ≤ 2020-10\n" + "=" * 100)
OUT["C_fon_2020"] = ladder(ffA, "fon", "C fon")

# ── D 딜 수준 처치 코딩 (female-only / mixed / male-only per (round, investor)) ────────────────────────────────────
log("\n" + "=" * 100 + "\n[D] 딜 수준 코딩 — (라운드, 투자사) 단위, fo vs mo, cell_cat, exit3 ≤2020-10\n" + "=" * 100)
pg = partner_gender_rows(set(ffA["funding_round_uuid"]))
agg = pg.groupby(["funding_round_uuid", "investor_uuid"])["fp"].agg(["min", "max", "size"]).reset_index()
agg["fo"] = ((agg["min"] == 1) & (agg["max"] == 1)).astype(float); agg["mx"] = ((agg["min"] == 0) & (agg["max"] == 1)).astype(float)
deals = ffA.drop_duplicates(["funding_round_uuid", "investor_uuid"])[["funding_round_uuid", "investor_uuid", "org_uuid", "cell_cat", "cell_stage", "y", "exit3", "fon", "exit_ever", "dt"]]
deals = deals.merge(agg[["funding_round_uuid", "investor_uuid", "fo", "mx", "size"]], on=["funding_round_uuid", "investor_uuid"], how="inner")
D = {"n_deal_rows": int(len(deals)), "n_partner_rows": int(len(ffA)), "share_fo": round(float(deals["fo"].mean()), 4), "share_mx": round(float(deals["mx"].mean()), 4)}
for cell in ("cell_cat", "cell_stage"):
    sub = deals[deals["mx"] == 0].copy()              # fo vs mo
    g = sub.groupby(cell)["fo"].agg(["mean", "size"]); mixed = g.index[(g["mean"] > 0) & (g["mean"] < 1)]
    m = sub[sub[cell].isin(mixed)].copy().rename(columns={"fo": "fp"})
    yv = m.groupby(cell)["exit3"].var(ddof=0).fillna(0)
    r = {"n_cells_fo_var": int(len(mixed)), "n_deals": int(len(m)), "n_cells_exit_var_pos": int((yv > 0).sum()), "n_fo_deals": int(m["fp"].sum())}
    if len(m) >= 30 and m[cell].nunique() >= 8:
        b, sxx = within_beta(m, cell, "exit3"); ci, mde, nb_ = boot_ci(m, cell, "exit3")
        r.update({"beta_fo_vs_mo_pp": round(b * 100, 3), "ci_pp": ci, "mde80_pp": mde, "placebo_p95_pp": placebo_p95(m, cell, "exit3"), "sxx": round(sxx, 2)})
        # 3범주 (mixed 포함): y ~ fo + mx within cell — fo 계수 (fo, mx 각각 demean 후 2-회귀)
        sub3 = deals[deals[cell].isin(deals.groupby(cell)["fo"].transform("mean").pipe(lambda s: deals.loc[(s > 0) & (s < 1), cell].unique()))].copy()
        yr = demean1(sub3["exit3"].to_numpy(float), sub3[cell].to_numpy()); X = np.column_stack([demean1(sub3["fo"].to_numpy(float), sub3[cell].to_numpy()), demean1(sub3["mx"].to_numpy(float), sub3[cell].to_numpy())])
        b3 = np.linalg.lstsq(X, yr, rcond=None)[0]
        r["three_cat_fo_pp"] = round(float(b3[0]) * 100, 3); r["three_cat_mx_pp"] = round(float(b3[1]) * 100, 3); r["n_deals_three_cat"] = int(len(sub3))
    else:
        r["beta_fo_vs_mo_pp"] = None
    D[cell] = r
    log(f"  {cell:<10} fo 변이 셀 {r['n_cells_fo_var']} / 딜 {r['n_deals']} (fo {r['n_fo_deals']}) · exit 변이 셀 {r['n_cells_exit_var_pos']} · β fo−mo {r.get('beta_fo_vs_mo_pp')} {r.get('ci_pp')} MDE {r.get('mde80_pp')} 위약 {r.get('placebo_p95_pp')} · 3범주 fo {r.get('three_cat_fo_pp')} mx {r.get('three_cat_mx_pp')}")
OUT["D_deal_level_coding"] = D

A = OUT["A_exit3_2020"]; B = OUT["B_exit_ever_2017"]; a1 = A["cell_cat"]; a2 = A["c2"]; ast = A["cell_stage"]; acfs = A["cfs"]; dd_ = D["cell_cat"]
pred = {"A_cat_multi_cells_160_190": 160 <= a1["n_multi_round_cells"] <= 190, "A_cat_multi_deals_600_700": 600 <= a1["n_deals_multi"] <= 700,
        "A_cat_beta_in_[-8,2]": bool(a1.get("beta_multi_pp") is not None and -8 <= a1["beta_multi_pp"] <= 2), "A_cat_ci_incl0": bool(a1.get("ci_multi_pp") and a1["ci_multi_pp"][0] <= 0 <= a1["ci_multi_pp"][1]),
        "A_cat_mde_8_11": bool(a1.get("mde80_multi_pp") and 8 <= a1["mde80_multi_pp"] <= 11), "A_cat_placebo_6_9": bool(a1.get("placebo_p95_multi_pp") and 6 <= a1["placebo_p95_multi_pp"] <= 9),
        "A_c2_within_3pp_of_cat": bool(a2.get("beta_multi_pp") is not None and a1.get("beta_multi_pp") is not None and abs(a2["beta_multi_pp"] - a1["beta_multi_pp"]) <= 3),
        "A_stage_moves_lt_half": bool(ast.get("beta_multi_pp") is not None and a1.get("beta_multi_pp") is not None and abs(ast["beta_multi_pp"] - a1["beta_multi_pp"]) < 0.5 * abs(a1["beta_multi_pp"])),
        "A_cfs_mde_5_7": bool(acfs.get("mde80_multi_pp") and 5 <= acfs["mde80_multi_pp"] <= 7),
        "D_cells_150_200": 150 <= dd_["n_cells_fo_var"] <= 200, "D_within_3pp_of_multi": bool(dd_.get("beta_fo_vs_mo_pp") is not None and a1.get("beta_multi_pp") is not None and abs(dd_["beta_fo_vs_mo_pp"] - a1["beta_multi_pp"]) <= 3),
        "B_reproduces_p49_multi": bool(B["cell_cat"].get("beta_multi_pp") is not None and abs(B["cell_cat"]["beta_multi_pp"] - (-10.707)) < 0.05)}
pred = {k: bool(v) for k, v in pred.items()}
OUT["prediction_check"] = pred
verdict = (f"exit3 ≤2020-10 firm×year×sector: 다중 라운드 {a1['n_multi_round_cells']} 셀/{a1['n_deals_multi']} 딜 (변이 {a1['n_cells_var_pos']}), 희석 {a1['dilution_share_sxx_single_round']:.2f}; β전체 {a1['beta_full_pp']:+.2f} → β다중 {a1.get('beta_multi_pp')} {a1.get('ci_multi_pp')} MDE {a1.get('mde80_multi_pp')} ({a1.get('mde80_multi_sd')} sd) 위약 {a1.get('placebo_p95_multi_pp')} | "
           f"+stage {ast.get('beta_multi_pp')} {ast.get('ci_multi_pp')} | 2yr {a2.get('beta_multi_pp')} {a2.get('ci_multi_pp')} MDE {a2.get('mde80_multi_pp')} | 3yr {A['c3'].get('beta_multi_pp')} MDE {A['c3'].get('mde80_multi_pp')} | firm×sector+yearFE {acfs.get('beta_multi_pp')} {acfs.get('ci_multi_pp')} MDE {acfs.get('mde80_multi_pp')} | "
           f"딜 수준 fo−mo {dd_.get('beta_fo_vs_mo_pp')} {dd_.get('ci_pp')} MDE {dd_.get('mde80_pp')} (셀 {dd_['n_cells_fo_var']}) | 기준 재현 exit_ever multi {B['cell_cat'].get('beta_multi_pp')} (예측 적중 {sum(pred.values())}/{len(pred)})")
emit("P001-55", "R5-3: Table 3 고정 36m 지평(exit3, 딜 ≤2020-10)·달력 거칠기 사다리·다중 라운드 셀 추정량·딜 수준 처치 코딩", "OK", OUT,
     prediction="cat exit3 다중 160–190 셀/600–700 딜, β∈[−8,+2] CI 0 포함 MDE 8–11 위약 6–9; 2yr 3pp 이내; +stage 이동 < 절반; firm×sector+yearFE MDE 5–7; 딜 코딩 셀 150–200 β 3pp 이내",
     verdict=verdict, kill_met=False, n=int(A["n_ff_deals"]),
     extra={"stage": 7, "feeds": "R5 design R5-3 / ident 항목 4 → Table 3 고정지평 패널 · §4 MDE 문장", "slug": "table3_fixed_horizon_ladder", "builds_on": "P001-10/40/49",
            "common_sha256_16": COMMON_SHA, "v6_common_sha256_16": V6_SHA})
log("done")
