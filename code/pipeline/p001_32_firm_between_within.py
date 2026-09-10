# -*- coding: utf-8 -*-
"""p001_32 — 회사 교란의 between/within 분해 (Mundlak 장치) + Hausman 형 대비

[왜] 심판이 요구한 회사 FE(P001-30 R4)는 회사 내 편차만 쓴다. 같은 회사 파트너들은 섹터 발자국을 공유하므로
 t_cs 의 회사 내 편차는 작고(P001-31 C) 구간이 벌어진다. 회사 평균을 회귀에 넣는 Mundlak 장치는 편차 계수
 (= within) 와 회사평균 계수(= between) 를 **같은 회귀에서** 준다. 회사 평균은 사후기가 없는 파트너까지
 포함한 사전기 표본 전체로 측정한다(사후기 有 파트너만으로 재는 R4 보다 회사 발자국이 정확).
 둘의 차이(Hausman 형 대비)가 0 에 가깝고 정밀하면 풀 추정치가 회사 교란 없이 해석 가능하고,
 차이가 크면 between 은 회사 품질이다. 이 스크립트는 **진단**이다: within 이 부정확하면 등가는 주장할 수 없다(rules/11).

[사양] (레벨, 군집 = 홈 회사, 부트 400, 연공 통제 포함)
 W1  post_adj ~ dev_t_v + dev_t_s + dev_t_cs + fm_t_v + fm_t_s + fm_t_cs + adj + ln_n + fp + TEN
     (dev_x = x − 회사평균(fm_x); fm_x 는 표본 내 전 파트너 평균 — 단독 파트너 회사는 dev=0)
 W2  같은 사양을 자신 제외 회사평균(fmp_x, dev2 = x − fmp_x) 로 — 표본은 회사 내 파트너 ≥2 (사전기 기준)
 W3  총 terrain 판: post_adj ~ dev_terrain + fm_terrain + adj + ln_n + fp + TEN
 대비: dev − fm 의 부트 CI (W1·W3)

[사전 예측] (2026-09-08, 결과 조회 전)
 W1 dev_t_cs ∈ [0.08, 0.16] 구간 0 포함; fm_t_cs 양(+) 구간 0 포함; 대비 CI 폭 ≥ 0.5 (등가 판정 불가).
 W3 dev_terrain ≈ R4t(+0.10) 구간 0 포함; fm_terrain ∈ [0.05, 0.20].
 **PARTIAL 예상** ("회사 교란은 보이지도 배제되지도 않음"). KILL: W1 dev_t_cs 상단 < 0.05 (within 이 정밀하게 0).
 GO: W1 dev_t_cs 하한 > 0.
"""
import numpy as np

from p001_rescue_common import (COMMON_SHA, TC, TEN, add_firm_means, add_post, add_tenure, boot, emit, fmt,
                                load_deals, log, partner_pre, qci, show, strip_draws)

rng = np.random.default_rng(20260932)
OUT = {}

dn = load_deals(with_exit_dt=False)
P, h = partner_pre(dn, "exit_ever")
P = add_post(P, dn, "exit_ever")
P = add_tenure(P)
P = add_firm_means(P, TC + ["terrain", "adj"])
for c in TC + ["terrain"]:
    P[f"dev2_{c}"] = P[c] - P[f"fmp_{c}"]
log(f"[구성] 파트너 {len(P):,} · 사후기 有 {int(P['has_post'].sum()):,} · 회사 {P['firm'].nunique():,} · "
    f"회사 내 ≥2 파트너인 파트너 {int((P['fm_k'] >= 2).sum()):,}")
OUT["counts"] = {"n_partners": int(len(P)), "n_post": int(P["has_post"].sum()), "n_firms": int(P["firm"].nunique()),
                 "n_multi_firm_partners": int((P["fm_k"] >= 2).sum()),
                 "n_post_multi": int(((P["fm_k"] >= 2) & (P["has_post"] == 1)).sum())}


def contrast(res, a, b):
    d = res["_draws"][:, res["_xc"].index(a)] - res["_draws"][:, res["_xc"].index(b)]
    pt = res["_b"][res["_xc"].index(a)] - res["_b"][res["_xc"].index(b)]
    lo, hi = qci(d)
    return {"coef": round(float(pt), 5), "ci95": [round(lo, 5), round(hi, 5)], "width": round(hi - lo, 4)}


log("\n" + "=" * 100 + "\n[W1] Mundlak: 편차(within) + 회사평균(between), 전 표본\n" + "=" * 100)
DEV, FM = [f"dev_{c}" for c in TC], [f"fm_{c}" for c in TC]
W1 = boot(P, "post_adj", DEV + FM + ["adj", "ln_n", "fp"] + TEN, DEV + FM, rng, return_draws=True)
show("W1 within(dev)", W1, DEV)
show("W1 between(fm)", W1, FM)
OUT["W1_mundlak"] = strip_draws(W1)
OUT["W1_contrast_tcs"] = contrast(W1, "dev_t_cs", "fm_t_cs")
OUT["W1_contrast_ts"] = contrast(W1, "dev_t_s", "fm_t_s")
log(f"  대비 dev−fm: t_cs {OUT['W1_contrast_tcs']} · t_s {OUT['W1_contrast_ts']}")

log("\n" + "=" * 100 + "\n[W2] 자신 제외 회사평균, 회사 내 ≥2 표본\n" + "=" * 100)
DEV2, FMP = [f"dev2_{c}" for c in TC], [f"fmp_{c}" for c in TC]
W2 = boot(P, "post_adj", DEV2 + FMP + ["adj", "ln_n", "fp"] + TEN, DEV2 + FMP, rng)
show("W2 within(dev2)", W2, DEV2)
show("W2 colleagues(fmp)", W2, FMP)
OUT["W2_leave_self_out"] = W2

log("\n" + "=" * 100 + "\n[W3] 총 terrain 판\n" + "=" * 100)
W3 = boot(P, "post_adj", ["dev_terrain", "fm_terrain", "adj", "ln_n", "fp"] + TEN, ["dev_terrain", "fm_terrain"], rng,
          return_draws=True)
show("W3 총 terrain", W3, ["dev_terrain", "fm_terrain"])
OUT["W3_total"] = strip_draws(W3)
OUT["W3_contrast"] = contrast(W3, "dev_terrain", "fm_terrain")
log(f"  대비 dev−fm(terrain): {OUT['W3_contrast']}")

# ── 판정 ────────────────────────────────────────────────────────────────────
dc = W1["dev_t_cs"]
if dc["ci95"][0] > 0:
    status, call = "GO", "회사 내 편차만으로 t_cs 가 0 을 배제 — 회사 교란 아님"
elif dc["ci95"][1] < 0.05:
    status, call = "KILL", "회사 내 편차의 t_cs 가 정밀하게 0 — between 은 회사 품질"
else:
    status, call = "PARTIAL", "회사 교란은 보이지도 배제되지도 않음 (within 부정확)"
pred = {"W1_dev_tcs_in_[0.08,0.16]": 0.08 <= dc["coef"] <= 0.16, "W1_dev_tcs_ci_incl0": dc["ci95"][0] <= 0 <= dc["ci95"][1],
        "W1_fm_tcs_pos": W1["fm_t_cs"]["coef"] > 0, "contrast_width_ge_0.5": OUT["W1_contrast_tcs"]["width"] >= 0.5,
        "W3_dev_terrain_ci_incl0": W3["dev_terrain"]["ci95"][0] <= 0 <= W3["dev_terrain"]["ci95"][1]}
OUT["prediction_check"] = pred
verdict = (f"W1 within t_cs {fmt(W1, 'dev_t_cs')} · between t_cs {fmt(W1, 'fm_t_cs')} · 대비 {OUT['W1_contrast_tcs']['coef']:+.3f} "
           f"[{OUT['W1_contrast_tcs']['ci95'][0]:+.3f},{OUT['W1_contrast_tcs']['ci95'][1]:+.3f}] | W2 within {fmt(W2, 'dev2_t_cs')} · "
           f"동료 {fmt(W2, 'fmp_t_cs')} | W3 terrain within {fmt(W3, 'dev_terrain')} · between {fmt(W3, 'fm_terrain')} — {call} "
           f"(예측 적중 {sum(pred.values())}/{len(pred)})")
emit("P001-32", "회사 교란 between/within 분해 (Mundlak) + Hausman 형 대비", status, OUT,
     prediction="W1 dev_t_cs∈[0.08,0.16] 구간 0 포함; fm_t_cs>0 구간 0 포함; 대비 폭≥0.5; PARTIAL 예상",
     verdict=verdict, kill_met=(status == "KILL"), n=int(len(P)),
     extra={"stage": 7, "feeds": "R2 power-rescue", "slug": "firm_between_within", "builds_on": "P001-30/31",
            "common_sha256_16": COMMON_SHA})
log("done")
