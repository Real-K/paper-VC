# -*- coding: utf-8 -*-
"""p001_46 — P8: Rothstein 유사물 — 헤드라인 셀 안에서 사전 배정 기업 특성의 균형 검정 (크기 보정 포함)

[왜] §1 은 Rothstein(2010) 의 반증 검정의 가장 가까운 유사물을 "셀 내 사전 배정 공변량 균형 검정"이라 했고, R2 Track A′·R3 CP-11·
 설계 제안 P8 이 이를 요구했다. 헤드라인 셀(회사×연×섹터, +단계) 안에서 여성 파트너 딜과 남성 파트너 딜이 **딜 이전에 정해진**
 기업 특성에서 균형인지 잰다. 결합 검정은 셀 내 fp 순열 귀무분포 위에서, 그리고 **검정의 크기를 먼저 보정**한다(교훈 25: 명목 5% 에서
 실제 32% 를 기각한 게이트가 있었다). 관측 균형은 비관측(창업자 사적 정보) 균형을 증명하지 못한다 — 검정은 기각할 수 있을 뿐 인증할
 수 없다. 그 경계 안에서만 서술한다.

[구성] 모집단 = Table 3 (sample_v1 NAEU, ff==1, dt ≤ 2017-10-31). 셀 = cell_cat(회사×연×섹터) / cell_stage. 혼합 셀(fp 변동)만 기여.
 사전 배정 공변량(딜 이전에 정해짐): 기업 연령(founded_on) · log1p 이전 지분형 라운드 수 · log1p 이전 조달액 · 직원수 밴드(1–9) ·
 이전 라운드 투자자 수 · 창업자 수 · 여성 창업자 수 · 창업자 학위 보유 비중 · 연쇄창업 비중 · HQ 미국.
 사후/공동 결정 공변량(양성 대조군): log 당 라운드 규모 · log 다음 라운드 규모.
 각 공변량: 셀 내 demean OLS on fp → 계수·표준화 차(계수/공변량 sd)·회사 군집 부트 CI·MDE80.
 결합: Mahalanobis(β̂, 부트 공분산) vs 셀 내 fp 순열 귀무(500) → p. 크기 보정: fp 를 셀 내 무작위 재배정한 200 개 가짜 표본 각각에
 순열 200 으로 p 를 구해 명목 5% 기각률을 측정.
 전 딜(ff 무관) 혼합 셀에서도 반복(정보량 큰 판).
[사전 예측] (2026-09-09, 결과 조회 전)
 FF cell_cat 결합 p > 0.10; 개별 표준화 차 |d| < 0.25 (430 딜에서 MDE 는 크다 — 0.3~0.5 sd). 전 딜 cell_stage 결합 p > 0.05.
 크기 보정 기각률 ∈ [0.02, 0.09]. 양성 대조: 전 딜 cell_cat 에서 log 라운드 규모 fp 차 검출(p < 0.05; 여성 파트너 딜이 초기단계) —
 cell_stage 에서는 약해짐.
[판정] 진단 — status OK. 결합 p < 0.05 인 FF 판이 나오면 "균형 실패" 로 표에 명기.

[정정 2026-09-09 — 1차 실행 중단] 1차 코드는 FF 필터를 빠뜨려 "FF" 패널이 전 딜(n≈4,200)로 돌았다 → 중단·수정. 크기 보정 루프는 100×100 으로 축소.
"""
import numpy as np
import pandas as pd

from p001_v6_common import (CTX, CUT, EMP_BAND, RESCUE_SHA, V6_SHA, emit, equity_rounds, fit, founders_by_org, load_sample, log, qci)

rng = np.random.default_rng(20260946)
NB, NPERM, NCAL, NPERM_CAL = 400, 500, 100, 100
OUT = {}
d = load_sample()
R = equity_rounds(set(d["org_uuid"]))
orgs = CTX.orgs.set_index("uuid")
fnd = founders_by_org()

# ── 공변량 구성 (딜 = sample_v1 행) ─────────────────────────────────────────
ALLb = d[d["dt"] <= CUT].copy()
base = ALLb  # 공변량은 전 딜에 만든 뒤 FF 로 자른다 (아래)
base["founded"] = pd.to_datetime(base["org_uuid"].map(orgs["founded_on"]), errors="coerce")
base["age"] = (base["dt"] - base["founded"]).dt.days / 365.25
base["emp_band"] = base["org_uuid"].map(orgs["employee_count"]).map(EMP_BAND)
base["hq_us"] = (base["country_code"] == "USA").astype(float)
# 이전 라운드 수·조달액·이전 투자자 수 (라운드 시퀀스에서 해당 라운드의 seq)
rr = R.set_index("uuid")
base["seq"] = base["funding_round_uuid"].map(rr["seq"])
base["ln_prior_rounds"] = np.log1p(base["seq"])
cum_amt = R.assign(a=R["amt"].fillna(0)).groupby("org_uuid")["a"].cumsum() - R["amt"].fillna(0)
rr_cum = pd.Series(cum_amt.to_numpy(), index=R["uuid"])
base["ln_prior_capital"] = np.log1p(base["funding_round_uuid"].map(rr_cum))
prev_ic = R.set_index("uuid")["prev_uuid"].map(rr["investor_count"]) if "investor_count" in rr.columns else None
base["prev_investor_count"] = pd.to_numeric(base["funding_round_uuid"].map(prev_ic), errors="coerce") if prev_ic is not None else np.nan
for c in ("n_founders", "n_female_founders", "founder_degree_share", "serial_share"):
    base[c] = base["org_uuid"].map(fnd[c])
base["ln_round_size"] = np.log1p(pd.to_numeric(base["funding_round_uuid"].map(rr["amt"]), errors="coerce"))
nxt_amt = rr["next_uuid"].map(rr["amt"])
base["ln_next_round_size"] = np.log1p(pd.to_numeric(base["funding_round_uuid"].map(nxt_amt), errors="coerce"))
PRE = ["age", "ln_prior_rounds", "ln_prior_capital", "emp_band", "prev_investor_count", "n_founders", "n_female_founders", "founder_degree_share", "serial_share", "hq_us"]
POST = ["ln_round_size", "ln_next_round_size"]
ALLb = base
base = ALLb[ALLb["ff"] == 1].copy()   # 1차 실행 정정: FF 딜만 (Table 3 모집단)
cov = {c: round(float(base[c].notna().mean()), 3) for c in PRE + POST}
log(f"[커버리지] {cov}")
OUT["coverage"] = cov


def within_coef(dd, y, cell):
    yr = (dd[y] - dd[y].groupby(dd[cell]).transform("mean")).to_numpy()
    xr = (dd["fp"] - dd["fp"].groupby(dd[cell]).transform("mean")).to_numpy()
    sxx = float((xr * xr).sum())
    return float((xr * yr).sum() / sxx) if sxx > 0 else np.nan


def balance_panel(df, cell, tag, covs, joint=True):
    g = df.groupby(cell)["fp"].agg(["mean", "size"])
    mixed = g.index[(g["mean"] > 0) & (g["mean"] < 1)]
    m = df[df[cell].isin(mixed)].copy()
    res = {"n_mixed_cells": int(len(mixed)), "n_deals": int(len(m)), "by_cov": {}}
    grp = {c: g_.index.to_numpy() for c, g_ in m.groupby("investor_uuid")}
    kl = list(grp)
    betas, draws_all = {}, {}
    for c in covs:
        dd = m.dropna(subset=[c])
        if len(dd) < 50 or dd[cell].nunique() < 10:
            res["by_cov"][c] = None; continue
        b = within_coef(dd, c, cell)
        bs = []
        for _ in range(NB):
            pick = rng.integers(0, len(kl), len(kl))
            s = m.loc[np.concatenate([grp[kl[i]] for i in pick])].dropna(subset=[c])
            v = within_coef(s, c, cell)
            if np.isfinite(v): bs.append(v)
        bs = np.array(bs); lo, hi = qci(bs); se = float(np.std(bs, ddof=1))
        sd = float(dd[c].std())
        res["by_cov"][c] = {"coef": round(b, 5), "ci95": [round(lo, 5), round(hi, 5)], "std_diff": round(b / sd, 4) if sd > 0 else None, "se_boot": round(se, 5),
                            "mde80_std": round(2.8 * se / sd, 3) if sd > 0 else None, "n": int(len(dd)), "sig": bool(lo > 0 or hi < 0)}
        betas[c] = b; draws_all[c] = bs
        log(f"  {tag:<22} {c:<22} β {b:+.4f} [{lo:+.4f},{hi:+.4f}] d {res['by_cov'][c]['std_diff'] if sd > 0 else float('nan'):+.3f} MDE(sd) {res['by_cov'][c]['mde80_std']} n={len(dd):,}")
    if joint and len(betas) >= 3:
        # 결합: 완비 공변량 표본에서 Mahalanobis vs 셀 내 순열 귀무
        ks = [c for c in covs if c in betas]
        mm = m.dropna(subset=ks).copy()
        Bv = np.array([within_coef(mm, c, cell) for c in ks])
        # 부트 공분산 (완비 표본)
        bs = []
        grp2 = {c: g_.index.to_numpy() for c, g_ in mm.groupby("investor_uuid")}; kl2 = list(grp2)
        for _ in range(NB):
            pick = rng.integers(0, len(kl2), len(kl2)); s = mm.loc[np.concatenate([grp2[kl2[i]] for i in pick])]
            bs.append([within_coef(s, c, cell) for c in ks])
        S = np.cov(np.array(bs).T) + 1e-10 * np.eye(len(ks)); Sinv = np.linalg.inv(S)
        maha = float(Bv @ Sinv @ Bv)

        def perm_stat(df_):
            fpp = df_.groupby(cell)["fp"].transform(lambda s: pd.Series(rng.permutation(s.to_numpy()), index=s.index))
            df2 = df_.assign(fp=fpp)
            bv = np.array([within_coef(df2, c, cell) for c in ks])
            return float(bv @ Sinv @ bv)
        null = np.array([perm_stat(mm) for _ in range(NPERM)])
        p_joint = float(np.mean(null >= maha))
        # 크기 보정: 가짜 처치 표본 NCAL 개, 각각 순열 NPERM_CAL
        rej = 0
        for _ in range(NCAL):
            fake = mm.assign(fp=mm.groupby(cell)["fp"].transform(lambda s: pd.Series(rng.permutation(s.to_numpy()), index=s.index)))
            bv = np.array([within_coef(fake, c, cell) for c in ks]); st = float(bv @ Sinv @ bv)
            nl = np.array([perm_stat(fake) for _ in range(NPERM_CAL)])
            rej += int(np.mean(nl >= st) < 0.05)
        res["joint"] = {"covariates": ks, "n_complete": int(len(mm)), "mahalanobis": round(maha, 3), "p_perm": round(p_joint, 4), "n_perm": NPERM,
                        "null_p95": round(float(np.percentile(null, 95)), 3), "size_calibration_reject_rate": round(rej / NCAL, 3), "n_cal": NCAL}
        log(f"  {tag:<22} 결합 Mahalanobis {maha:.2f} · 순열 p {p_joint:.3f} · 귀무 p95 {res['joint']['null_p95']:.2f} · 크기 보정 기각률 {rej / NCAL:.3f} (n {len(mm):,})")
    return res


log("\n" + "=" * 100 + "\n[FF 딜, 회사×연×섹터 셀] 사전 배정 공변량\n" + "=" * 100)
OUT["FF_cell_cat_pre"] = balance_panel(base, "cell_cat", "FF cat", PRE)
log("\n[FF 딜, 회사×연×섹터 셀] 양성 대조(사후/공동 결정)")
OUT["FF_cell_cat_post"] = balance_panel(base, "cell_cat", "FF cat POST", POST, joint=False)
log("\n" + "=" * 100 + "\n[FF 딜, +단계 셀] 사전 배정 공변량\n" + "=" * 100)
OUT["FF_cell_stage_pre"] = balance_panel(base, "cell_stage", "FF stage", PRE)
log("\n" + "=" * 100 + "\n[전 딜, +단계 셀] 사전 배정 공변량 · 양성 대조\n" + "=" * 100)
OUT["ALL_cell_stage_pre"] = balance_panel(ALLb, "cell_stage", "ALL stage", PRE)
OUT["ALL_cell_cat_post"] = balance_panel(ALLb, "cell_cat", "ALL cat POST", POST, joint=False)

OUT["ALL_cell_stage_post"] = balance_panel(ALLb, "cell_stage", "ALL stage POST", POST, joint=False)

# ── 판정 ────────────────────────────────────────────────────────────────────
ffc, ffs, alls = OUT["FF_cell_cat_pre"], OUT["FF_cell_stage_pre"], OUT["ALL_cell_stage_pre"]
def maxd(r):
    return max((abs(v["std_diff"]) for v in r["by_cov"].values() if v and v["std_diff"] is not None), default=float("nan"))
pred = {"FF_cat_joint_p_gt_0.10": bool(ffc.get("joint") and ffc["joint"]["p_perm"] > 0.10), "FF_cat_max_absd_lt_0.25": maxd(ffc) < 0.25,
        "ALL_stage_joint_p_gt_0.05": bool(alls.get("joint") and alls["joint"]["p_perm"] > 0.05),
        "size_calibration_in_[0.02,0.09]": bool(ffc.get("joint") and 0.02 <= ffc["joint"]["size_calibration_reject_rate"] <= 0.09),
        "positive_control_ALL_cat_round_size_sig": bool(OUT["ALL_cell_cat_post"]["by_cov"].get("ln_round_size") and OUT["ALL_cell_cat_post"]["by_cov"]["ln_round_size"]["sig"])}
pred = {k: bool(v) for k, v in pred.items()}
OUT["prediction_check"] = pred
fail = [k for k, r in (("FF_cat", ffc), ("FF_stage", ffs), ("ALL_stage", alls)) if r.get("joint") and r["joint"]["p_perm"] < 0.05]
verdict = (f"FF 회사×연×섹터: 혼합 셀 {ffc['n_mixed_cells']} · 딜 {ffc['n_deals']} · 결합 p {ffc['joint']['p_perm'] if ffc.get('joint') else 'NA'} · 최대 |d| {maxd(ffc):.2f} · 크기 보정 기각률 {ffc['joint']['size_calibration_reject_rate'] if ffc.get('joint') else 'NA'} | "
           f"FF +단계: 결합 p {ffs['joint']['p_perm'] if ffs.get('joint') else 'NA'} | 전 딜 +단계: 셀 {alls['n_mixed_cells']} · 딜 {alls['n_deals']} · 결합 p {alls['joint']['p_perm'] if alls.get('joint') else 'NA'} · 최대 |d| {maxd(alls):.2f} | "
           f"양성 대조(전 딜 cat) log 라운드 규모 {OUT['ALL_cell_cat_post']['by_cov']['ln_round_size']['coef'] if OUT['ALL_cell_cat_post']['by_cov'].get('ln_round_size') else float('nan'):+.3f} sig {pred['positive_control_ALL_cat_round_size_sig']} — "
           f"균형 실패 판: {fail if fail else '없음'} (예측 적중 {sum(pred.values())}/{len(pred)})")
emit("P001-46", "P8: 헤드라인 셀 내 사전 배정 공변량 균형 검정 (Rothstein 유사물) — 결합 순열 p · 크기 보정 · 양성 대조 · MDE", "OK", OUT,
     prediction="FF cat 결합 p>0.10, |d|<0.25; 전 딜 stage p>0.05; 크기 보정 0.02–0.09; 양성 대조(전 딜 cat 라운드 규모) 검출",
     verdict=verdict, kill_met=False, n=int(ffc["n_deals"]),
     extra={"stage": 7, "feeds": "v6 설계 제안 P8 / R2 Track A′ 균형검정", "slug": "balance_rothstein", "builds_on": "P001-10/40",
            "common_sha256_16": RESCUE_SHA, "v6_common_sha256_16": V6_SHA})
log("done")
