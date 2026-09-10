# -*- coding: utf-8 -*-
"""I-79 충격 레이어의 결합 검정 + 추세 조정 (K-3 인과층 최종)

[왜] I-76: 영입 DiD +1.02pp [−0.07, +2.13]·이탈 DiD −1.44pp [−3.06, +0.31] — 두 독립 마진이
모두 예측 방향으로 경계에 걸림 → 레버 12(결합 검정)의 정당 적용. 동시에 run-up +2.2pp
(여성 영입 전 ff 상승 추세)가 수준 평행추세를 깨므로 추세 조정(2차 차분, I-68 형)을 병기.
주의: run-up 이 일시적(평균회귀)이면 2차 차분은 하향 과잉조정 — 원 DiD 와 조정 DiD 를 함께
보고하고 둘 사이가 효과의 정직한 범위다.
[설계] I-76 사건·창 재사용.
  (a) 결합 대비 = (영입 DiD) − (이탈 DiD) — 대칭 가설("여성 파트너 존재가 ff 신규딜을 올림")
      하에서 두 마진을 하나의 통계량으로. 군별 독립 부트 500 결합.
  (b) 추세 조정 영입 DiD = 2차 차분 [(post−pre) − (pre−pre2)] 의 여−남 차. pre2 관측 사건만.
  (c) 추세 조정 이탈 DiD = 동일.
[사전 예측] (결과 전, 2026-09-03)
  P1 결합 대비 = +1.5~+4.5pp, CI 0 배제.
  P2 추세 조정 영입 DiD ≥ 0 (run-up 평균회귀 시 하향 편의로 0 포함 가능 — 그래도 기록).
  P3 추세 조정 이탈 DiD ≤ 0 유지.
[판정] (사전 등록) GO = P1 성립 그리고 추세 조정 영입 DiD 가 유의하게 음이 아님.
  PARTIAL = P1 실패 또는 조정치 유의 음 — 충격층은 '시사적'으로 원고 기록(연관+판별로 성립).
  결과와 무관하게 원 DiD·조정 DiD·결합 대비 전부 원장 §4 에 기록.
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
arr = arr[arr["fa"].notna() & (arr["fa"] >= arr["t"])]
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


def wshare(g, lo, hi):
    w = g[(g["fdt"] >= lo) & (g["fdt"] < hi)]
    return float(w["ff"].mean()) if len(w) >= MIN_DEALS else np.nan


rows = []
for ev in events.itertuples():
    g = fd_by_v.get(ev.investor_uuid)
    if g is None:
        continue
    pre = wshare(g, ev.t - W, ev.t)
    post = wshare(g, ev.t, ev.t + W + pd.Timedelta(days=1))
    if np.isnan(pre) or np.isnan(post):
        continue
    pre2 = wshare(g, ev.t - 2 * W, ev.t - W)
    rows.append({"kind": ev.kind, "pg": ev.pg, "d1": post - pre,
                 "d2": (post - pre) - (pre - pre2) if not np.isnan(pre2) else np.nan})
E = pd.DataFrame(rows)


def bsm(x, nb=NB):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if len(x) < 50:
        return float("nan"), [], 0
    return float(x.mean()), [x[rng.integers(0, len(x), len(x))].mean() for _ in range(nb)], len(x)


g_ = {(k, p, c): bsm(E[(E["kind"] == k) & (E["pg"] == p)][c])
      for k in ("join", "exit") for p in ("female", "male") for c in ("d1", "d2")}


def contrast(spec):
    """spec = [(key, sign), ...] — 평균의 선형 결합 + 결합 부트."""
    b = sum(s * g_[k][0] for k, s in spec)
    m = min(len(g_[k][1]) for k, _ in spec)
    if m < 50 or np.isnan(b):
        return float("nan"), [float("nan")] * 2
    bs = np.zeros(m)
    for k, s in spec:
        bs = bs + s * np.asarray(g_[k][1][:m])
    return b, qci(bs)


jd1, cjd1 = contrast([(("join", "female", "d1"), 1), (("join", "male", "d1"), -1)])
ed1, ced1 = contrast([(("exit", "female", "d1"), 1), (("exit", "male", "d1"), -1)])
joint, cjoint = contrast([(("join", "female", "d1"), 1), (("join", "male", "d1"), -1),
                          (("exit", "female", "d1"), -1), (("exit", "male", "d1"), 1)])
jd2, cjd2 = contrast([(("join", "female", "d2"), 1), (("join", "male", "d2"), -1)])
ed2, ced2 = contrast([(("exit", "female", "d2"), 1), (("exit", "male", "d2"), -1)])
n_j2 = g_[("join", "female", "d2")][2]

p1 = (not np.isnan(cjoint[0])) and (cjoint[0] > 0)
adj_sig_neg = (not np.isnan(cjd2[1])) and (cjd2[1] < 0)
status = "GO" if (p1 and not adj_sig_neg) else "PARTIAL"
verdict = (f"결합 대비(영입−이탈 DiD)={joint:+.4f} {cjoint}; 원 DiD 영입={jd1:+.4f} {cjd1}·"
           f"이탈={ed1:+.4f} {ced1}; 추세조정 영입={jd2:+.4f} {cjd2} (n={n_j2})·이탈={ed2:+.4f} {ced2}"
           + (" — 결합 수준에서 충격 효과 성립, 조정치 비모순" if (p1 and not adj_sig_neg)
              else " — 충격층은 시사적: 연관+판별로 논문 성립, 충격은 보조 증거"))

emit("I-79", "충격 레이어 결합 검정 + 추세 조정 (K-3 인과층 최종)", status,
     {"joint_contrast": None if np.isnan(joint) else round(joint, 4), "joint_ci": cjoint,
      "join_did_d1": [round(jd1, 4), cjd1], "exit_did_d1": [round(ed1, 4), ced1],
      "join_did_trendadj": [None if np.isnan(jd2) else round(jd2, 4), cjd2, n_j2],
      "exit_did_trendadj": [None if np.isnan(ed2) else round(ed2, 4), ced2],
      "p1_joint": bool(p1), "adj_sig_neg": bool(adj_sig_neg)},
     prediction="결합 대비 +1.5~+4.5pp CI 배제; 조정 영입 ≥0(0 포함 가능); 조정 이탈 ≤0",
     verdict=verdict, kill_met=False, n=n_j2,
     extra={"stage": 2, "feeds": "RESULTS_LEDGER_K3.md §4 인과층", "slug": "shock_joint"})
print("done")
