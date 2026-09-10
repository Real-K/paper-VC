# -*- coding: utf-8 -*-
"""I-76 충격 레이어 — 여성 파트너의 깨끗한 영입·이탈과 V 의 여성 창업 신규 딜 (K-3 인과층)

[왜] I-73~75 는 연관(동류교배 +3.0pp 섹터 내)과 판별(후속에서 호의 배제)까지 — 인과층이 남았다.
벤치마크 공식 4요소 중 '인사 이동 충격'. I-71/I-72 인프라 재사용, 단 I-72 교훈 적용:
영입은 **깨끗한 영입**(합류 전 귀속 딜 0건)만, 그리고 평균회귀(연결 기반 채용) 진단을 사전 등록.
[설계]
  사건   = 파트너 영입(jobs 첫 시작, 깨끗한 영입 필터) / 이탈(jobs 마지막 종료), 2012–2023-10,
           파트너 성별 관측(male/female). 사건 파트너 성별로 4군: join_f, join_m, exit_f, exit_m.
  결과   = V 의 신규(첫 참여) 딜 중 여성 창업(ff) 비중: 사전(t−24m,t) vs 사후(t,t+24m],
           분모 = ff 판정 가능 신규 딜, 사건별 각 기간 ≥3건.
  추정   = Δff(사건별) 평균; **DiD = Δ(여성 사건) − Δ(남성 사건)** — 남성 파트너 사건이
           V 수준 추세·구성 변화의 반사실. 사건 부트 500 (군별 독립 재표집 후 차분).
  진단   = 평균회귀: 여성 영입 사건의 사전 ff 추세 Δpre = ff(t−24,t) − ff(t−48,t−24).
           I-72 형 선택("이미 여성 창업에 투자하던 V 가 여성 파트너를 뽑음")이면 Δpre > 0.
[사전 예측] (결과 전, 2026-09-03)
  P1 영입 DiD = +1~+4pp, CI 0 배제 (여성 파트너 영입 → ff 신규딜 비중 상승, 남성 영입 대비).
  P2 이탈 DiD = −1~−3pp (대칭 — 단, I-24/70 의 기관 연속성이 신규 딜에도 미치면 0 가능).
  P3 평균회귀 진단: Δpre CI ⊂ ±2pp (영입 전 상승 추세 없음).
[Kill/판정] (사전 등록)
  K1 검정력: 여성 깨끗한 영입 유효 사건 < 300 → KILL (충격층 불가).
  K2 선택 인공물: Δpre ≥ +2pp CI 0 배제 **이고** 사후 Δff ≤ 0 (상승 후 회귀 패턴) → 충격층 KILL.
  K3 영입·이탈 DiD 모두 CI 0 포함 → 충격층 실패 — K-3 는 연관+판별 논문으로 유지(강등 아님,
     인과 서술만 제외). GO = P1 또는 P2 성립 + K2 청정.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emit_contract import emit, qci  # noqa: E402
from gates import CTX  # noqa: E402

rng = np.random.default_rng(42)
NB = 500
W = pd.Timedelta(days=730)
MIN_DEALS = 3
EQ_EXCL = {"grant", "debt_financing", "post_ipo_debt", "post_ipo_equity", "non_equity_assistance"}

people = CTX.people[["uuid", "gender"]]
g_map = people[people["gender"].isin(["male", "female"])].set_index("uuid")["gender"]

rounds = CTX.rounds.dropna(subset=["announced_on", "org_uuid"]).copy()
rounds = rounds[~rounds["investment_type"].isin(EQ_EXCL)]
rounds["dt"] = pd.to_datetime(rounds["announced_on"], errors="coerce")
rounds = rounds.dropna(subset=["dt"])
inv = CTX.inv.dropna(subset=["funding_round_uuid", "investor_uuid"])
pt = CTX.partners.dropna(subset=["funding_round_uuid", "investor_uuid", "partner_uuid"])
jobs = CTX.jobs

# V 의 신규 딜 + ff
pv = inv.merge(rounds[["uuid", "org_uuid", "dt"]], left_on="funding_round_uuid", right_on="uuid")
first_deal = pv.groupby(["investor_uuid", "org_uuid"])["dt"].min().rename("fdt").reset_index()
fj = jobs[jobs["title"].fillna("").str.lower().str.contains("founder", regex=False)][
    ["person_uuid", "org_uuid"]].dropna()
fj["fg"] = fj["person_uuid"].map(g_map)
fj = fj[fj["fg"].notna()]
org_ff = (fj["fg"] == "female").groupby(fj["org_uuid"]).max()
first_deal["ff"] = first_deal["org_uuid"].map(org_ff)
first_deal = first_deal[first_deal["ff"].notna()]
first_deal["ff"] = first_deal["ff"].astype(float)
fd_by_v = {v: g for v, g in first_deal.groupby("investor_uuid")}

# 사건 (i71/i72 정의 재사용)
pa = pt.merge(rounds[["uuid", "dt"]], left_on="funding_round_uuid", right_on="uuid")
first_attr = pa.groupby(["partner_uuid", "investor_uuid"])["dt"].min().rename("fa")
pj = jobs.merge(pt[["partner_uuid", "investor_uuid"]].drop_duplicates(),
                left_on=["person_uuid", "org_uuid"], right_on=["partner_uuid", "investor_uuid"])

arr = pj[pj["started_on"].notna()].copy()
arr["t"] = pd.to_datetime(arr["started_on"], errors="coerce")
arr = arr.dropna(subset=["t"])
arr = arr[(arr["t"] >= "2012-01-01") & (arr["t"] <= "2023-10-31")]
arr = arr.sort_values("t").groupby(["partner_uuid", "investor_uuid"]).head(1)[
    ["partner_uuid", "investor_uuid", "t"]]
arr = arr.merge(first_attr, left_on=["partner_uuid", "investor_uuid"], right_index=True, how="left")
arr = arr[arr["fa"].notna() & (arr["fa"] >= arr["t"])]  # 깨끗한 영입 (I-72 교훈)
arr["kind"] = "join"

dep = pj[pj["ended_on"].notna()].copy()
dep["t"] = pd.to_datetime(dep["ended_on"], errors="coerce")
dep = dep.dropna(subset=["t"])
dep = dep[(dep["t"] >= "2012-01-01") & (dep["t"] <= "2023-10-31")]
dep = dep.sort_values("t").groupby(["partner_uuid", "investor_uuid"]).tail(1)[
    ["partner_uuid", "investor_uuid", "t"]]
dep["kind"] = "exit"

events = pd.concat([arr[["partner_uuid", "investor_uuid", "t", "kind"]], dep], ignore_index=True)
events["pg"] = events["partner_uuid"].map(g_map)
events = events[events["pg"].notna()]


def window_share(g, lo, hi):
    w = g[(g["fdt"] >= lo) & (g["fdt"] < hi)]
    return (float(w["ff"].mean()), len(w)) if len(w) >= MIN_DEALS else (np.nan, len(w))


rows = []
for ev in events.itertuples():
    g = fd_by_v.get(ev.investor_uuid)
    if g is None:
        continue
    pre, n_pre = window_share(g, ev.t - W, ev.t)
    post, n_post = window_share(g, ev.t, ev.t + W + pd.Timedelta(days=1))
    if np.isnan(pre) or np.isnan(post):
        continue
    pre2, _ = window_share(g, ev.t - 2 * W, ev.t - W)  # 평균회귀 진단용 (없으면 NaN)
    rows.append({"kind": ev.kind, "pg": ev.pg, "delta": post - pre,
                 "dpre": (pre - pre2) if not np.isnan(pre2) else np.nan, "base": pre})
E = pd.DataFrame(rows)


def boot_mean(x, nb=NB):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if len(x) < 50:
        return float("nan"), [float("nan")] * 2, int(len(x)), []
    bs = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(nb)]
    return float(x.mean()), qci(bs), int(len(x)), bs


res = {}
for kind in ("join", "exit"):
    for pg in ("female", "male"):
        res[(kind, pg)] = boot_mean(E[(E["kind"] == kind) & (E["pg"] == pg)]["delta"])

did = {}
for kind in ("join", "exit"):
    bf, _, nf, bsf = res[(kind, "female")]
    bm, _, nm, bsm = res[(kind, "male")]
    if np.isnan(bf) or np.isnan(bm):
        did[kind] = (float("nan"), [float("nan")] * 2, nf, nm)
    else:
        m = min(len(bsf), len(bsm))
        did[kind] = (bf - bm, qci(np.array(bsf[:m]) - np.array(bsm[:m])), nf, nm)

b_dpre, ci_dpre, n_dpre, _ = boot_mean(E[(E["kind"] == "join") & (E["pg"] == "female")]["dpre"])

dj, cij, njf, njm = did["join"]
de, cie, nef, nem = did["exit"]
k1 = njf < 300
runup = (not np.isnan(b_dpre)) and (b_dpre >= 0.02) and (ci_dpre[0] > 0)
k2 = runup and (not np.isnan(res[("join", "female")][0])) and (res[("join", "female")][0] <= 0)
join_hit = (not np.isnan(cij[0])) and (cij[0] > 0)
exit_hit = (not np.isnan(cie[1])) and (cie[1] < 0)
k3 = (not k1) and (not join_hit) and (not exit_hit) \
     and (not np.isnan(cij[0])) and (cij[0] <= 0 <= cij[1]) and (cie[0] <= 0 <= cie[1])
kills = {"K1_power": bool(k1), "K2_selection_runup": bool(k2), "K3_no_shock_effect": bool(k3)}
status = "KILL" if (k1 or k2) else ("GO" if ((join_hit or exit_hit) and not runup) else "PARTIAL")
verdict = (f"영입 DiD(여−남)={dj:+.4f} {cij} (여 {njf}·남 {njm}); "
           f"이탈 DiD={de:+.4f} {cie} (여 {nef}·남 {nem}); "
           f"여성영입 Δff={res[('join','female')][0]:+.4f} {res[('join','female')][1]}; "
           f"평균회귀 Δpre={b_dpre:+.4f} {ci_dpre} (n={n_dpre})")

emit("I-76", "충격 레이어 — 여성 파트너 깨끗한 영입·이탈과 여성 창업 신규 딜 (K-3 인과층)", status,
     {"join_did": None if np.isnan(dj) else round(dj, 4), "join_did_ci": cij,
      "n_join_f": njf, "n_join_m": njm,
      "exit_did": None if np.isnan(de) else round(de, 4), "exit_did_ci": cie,
      "n_exit_f": nef, "n_exit_m": nem,
      "join_f_raw": [round(res[("join", "female")][0], 4), res[("join", "female")][1]],
      "join_m_raw": [round(res[("join", "male")][0], 4), res[("join", "male")][1]],
      "exit_f_raw": [round(res[("exit", "female")][0], 4), res[("exit", "female")][1]],
      "exit_m_raw": [round(res[("exit", "male")][0], 4), res[("exit", "male")][1]],
      "pre_runup_join_f": [None if np.isnan(b_dpre) else round(b_dpre, 4), ci_dpre, n_dpre],
      "kills": kills},
     prediction="영입 DiD +1~+4pp CI 배제; 이탈 DiD −1~−3pp; Δpre ⊂ ±2pp",
     verdict=verdict, kill_met=(k1 or k2), n=njf,
     extra={"stage": 2, "feeds": "K-3 인과층 (RESULTS_LEDGER_K3.md §4)", "slug": "gender_shock"})
print("done")
