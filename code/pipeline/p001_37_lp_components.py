# -*- coding: utf-8 -*-
"""p001_37 — Panel C 재검: LP·시장 결과 ← terrain 성분 (섹터 성분은 단계와 직교) + 후기단계 비중

[왜] 내부리뷰 R2 는 Panel C(총 composition → 스핀아웃 펀드 조성·규모·수용 회사 질) 가 "후기단계 펀드는 원래
 크다"는 기계성과 분리되지 않는다고 했고, P001-29 는 late_sh 통제 시 lp_amt 가 −73% 로 유의를 잃음을 확인했다.
 성분으로 쪼개면 기계성 주장은 **단계 성분(t_s)** 에만 해당한다. 섹터 성분(t_cs) 은 연도×단계 안에서의
 섹터 배치이므로 단계와 직교한다 — t_cs 가 LP 결과를 예측하면 그것은 펀드 크기의 기계성으로 설명되지 않는다.
 반대로 t_cs 가 예측하지 못하면 Panel C 의 composition 신호는 전부 단계 기계성이었다는 판정이 된다.

[구성] P001-25/29 와 동일한 결과: move(회사 이동) · spin(신생사 이동) · lp_any(신생사 펀드 조성) · lp_amt(log 최대
 펀드 규모) · recv_q(수용 회사 사전기 딜수 log1p). 사후기 2017-11 ~ 2023-10, 펀드 ≤ 2024-12.
[사양] (레벨, 군집 회사, 부트 400)
 L1  y ~ t_v + t_s + t_cs + adj + ln_n + fp
 L2  L1 + late_sh
 L3  L2 + TEN
[사전 예측] (2026-09-08, 결과 조회 전)
 lp_amt: t_s 양(+) 이며 late_sh 투입 시 ≥40% 감소(기계성). t_cs 는 lp_any 에 양(+) 이나 부정확(n≈380) — PARTIAL 예상.
 recv_q: t_s 가 지배. spin: t_s 음(초기단계 특화자가 스핀아웃), t_cs ≈ 0.
 GO: L3 에서 lp_any 의 t_cs 하한 > 0. KILL: L3 에서 lp_any·lp_amt 의 t_cs 점추정이 모두 ≤ 0. 그 외 PARTIAL.
"""
import numpy as np
import pandas as pd

from p001_rescue_common import (COMMON_SHA, CTX, CUT, END, TC, TEN, add_post, add_tenure, boot, emit, fmt, load_deals,
                                log, partner_pre, show)

rng = np.random.default_rng(20260937)
OUT = {}
dn = load_deals(with_exit_dt=False)
P, h = partner_pre(dn, "exit_ever")
P = add_post(P, dn, "exit_ever")
P = add_tenure(P)

# ── LP·시장 결과 (P001-25 그대로) ─────────────────────────────────────────
pt = CTX.partners.dropna(subset=["funding_round_uuid", "investor_uuid", "partner_uuid"])
r = CTX.rounds.dropna(subset=["announced_on"])[["uuid", "announced_on"]].copy()
r["rdt"] = pd.to_datetime(r["announced_on"], errors="coerce")
A = pt.merge(r, left_on="funding_round_uuid", right_on="uuid").dropna(subset=["rdt"])
firm_first = A.groupby("investor_uuid")["rdt"].min()
fut_firms = A[(A["rdt"] > CUT) & (A["rdt"] <= END)].groupby("partner_uuid")["investor_uuid"].agg(set)
pre_n = A[A["rdt"] <= CUT].groupby("investor_uuid").size()
F = CTX.funds.dropna(subset=["entity_uuid", "announced_on"]).copy()
F["fdt"] = pd.to_datetime(F["announced_on"], errors="coerce")
F["famt"] = pd.to_numeric(F["raised_amount_usd"], errors="coerce")
F = F[(F["fdt"] > CUT) & (F["fdt"] <= pd.Timestamp("2024-12-31"))]
fund_any = set(F["entity_uuid"])
fund_amt = F.groupby("entity_uuid")["famt"].max()
mv, sp, lp_any, lp_amt, recv = [], [], [], [], []
hm = dict(zip(P["partner_uuid"], P["firm"]))
for pid in P["partner_uuid"]:
    fs = fut_firms.get(pid, set()) - {hm[pid]}
    mv.append(1.0 if fs else 0.0)
    nf = [f for f in fs if firm_first.get(f, pd.Timestamp("1900-01-01")) > CUT]
    sp.append(1.0 if nf else 0.0)
    got = [f for f in nf if f in fund_any]
    lp_any.append(1.0 if got else (0.0 if nf else np.nan))
    am = [fund_amt.get(f, np.nan) for f in got]
    am = [x for x in am if x == x and x > 0]
    lp_amt.append(np.log(max(am)) if am else np.nan)
    recv.append(np.log1p(max([pre_n.get(f, 0) for f in fs] + [0])) if fs else np.nan)
P["move"], P["spin"], P["lp_any"], P["lp_amt"], P["recv_q"] = mv, sp, lp_any, lp_amt, recv
OUT["counts"] = {"n_partners": int(len(P)), "move": int(P["move"].sum()), "spin": int(P["spin"].sum()),
                 "lp_any_obs": int(P["lp_any"].notna().sum()), "lp_any_pos": int(np.nansum(P["lp_any"])),
                 "lp_amt_obs": int(P["lp_amt"].notna().sum()), "recv_q_obs": int(P["recv_q"].notna().sum())}
log(f"[구성] {OUT['counts']}")

YS = ["move", "spin", "lp_any", "lp_amt", "recv_q"]
for y in YS:
    log("\n" + "=" * 100 + f"\n[{y}] ← 성분\n" + "=" * 100)
    L1 = boot(P, y, TC + ["adj", "ln_n", "fp"], TC + ["adj"], rng); show("L1", L1, TC + ["adj"])
    L2 = boot(P, y, TC + ["adj", "ln_n", "fp", "late_sh"], TC + ["late_sh"], rng); show("L2 +late_sh", L2, TC + ["late_sh"])
    L3 = boot(P, y, TC + ["adj", "ln_n", "fp", "late_sh"] + TEN, TC + ["tenure"], rng); show("L3 +연공", L3, TC + ["tenure"])
    res = {"L1": L1, "L2": L2, "L3": L3}
    if L1 and L2 and L1["t_s"]["coef"]:
        res["t_s_pct_change_L1_to_L2"] = round((L2["t_s"]["coef"] - L1["t_s"]["coef"]) / abs(L1["t_s"]["coef"]) * 100, 1)
    OUT[y] = res

la, lm = OUT["lp_any"]["L3"], OUT["lp_amt"]["L3"]
if la and la["t_cs"]["ci95"][0] > 0:
    status, call = "GO", "섹터 성분(단계와 직교) 이 스핀아웃 펀드 조성을 예측 — 펀드 크기 기계성으로 설명되지 않음"
elif la and lm and la["t_cs"]["coef"] <= 0 and lm["t_cs"]["coef"] <= 0:
    status, call = "KILL", "섹터 성분은 LP 결과를 예측하지 않음 — Panel C 의 composition 신호는 단계 기계성"
else:
    status, call = "PARTIAL", "섹터 성분의 LP 예측은 검출도 배제도 안 됨 (n 소표본) — MDE 병기"
pred = {"lp_amt_ts_pos": bool(OUT["lp_amt"]["L1"] and OUT["lp_amt"]["L1"]["t_s"]["coef"] > 0),
        "lp_amt_ts_drop_ge40": bool(OUT["lp_amt"].get("t_s_pct_change_L1_to_L2", 0) <= -40),
        "lp_any_tcs_pos": bool(la and la["t_cs"]["coef"] > 0),
        "spin_ts_neg": bool(OUT["spin"]["L1"] and OUT["spin"]["L1"]["t_s"]["coef"] < 0)}
OUT["prediction_check"] = pred
verdict = (" | ".join(f"{y}: L3 t_s {fmt(OUT[y]['L3'], 't_s')} · t_cs {fmt(OUT[y]['L3'], 't_cs')}" for y in YS if OUT[y]["L3"]) +
           f" | lp_amt t_s L1→L2 {OUT['lp_amt'].get('t_s_pct_change_L1_to_L2')}% — {call} (예측 적중 {sum(pred.values())}/{len(pred)})")
emit("P001-37", "Panel C 재검 — LP·시장 결과 ← terrain 성분 + late_sh", status, OUT,
     prediction="lp_amt t_s 양·late_sh 로 ≥40% 감소; lp_any t_cs 양 부정확(PARTIAL); spin t_s 음; GO=lp_any t_cs 하한>0; KILL=lp_any·lp_amt t_cs ≤0",
     verdict=verdict, kill_met=(status == "KILL"), n=int(len(P)),
     extra={"stage": 7, "feeds": "R2 power-rescue (Panel C)", "slug": "lp_components", "builds_on": "P001-25/29/30",
            "common_sha256_16": COMMON_SHA})
log("done")
