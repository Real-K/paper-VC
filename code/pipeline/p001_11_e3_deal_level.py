# -*- coding: utf-8 -*-
"""p001_11 (Track D, P-1) E3 딜 수준 스택 회귀 — 사건-집계의 정보 손실 제거

[왜] P001-04b 는 사건×반기 '비중'을 사건 동일가중 평균 — 소형 회사의 잡음 비중과 대형 회사를
동일 취급해 딜 수준 정보를 버림. 딜을 관측치로 바꾸면 (FF딜 ~ 여성사건×사후, 사건 FE +
상대반기 FE) 정보량이 사건 수천 → 딜 수만. knife-edge 였던 오염제외 하한(L1 −0.09)과
동료-딜 마진(−0.03)을 직접 겨냥. 스택 구조(사건별 짧은 창 + 동시기 반대성별 대조)라
Goodman-Bacon 형 오염은 구조적으로 회피 — Sun-Abraham 정신의 사건별 포화는 event FE 가 수행.
[설계] 사건 = P001-04b 와 동일 (깨끗한 영입·이탈, NA+EU 투자사, 2012–2023; 오염 남성 대조
  제외; 남성 사건 재가중 w). 관측치 = 사건 창(상대반기 −4..+3) 내 회사의 판정가능 신규 딜.
  β_join = FWL[ y=ff ~ fem×post | event FE + rel-half FE, 가중 w ] (영입 스택)
  β_exit = 동일 (이탈 스택) · 결합 대비 = β_join − β_exit (회사 군집 부트 300, 공동 재표집)
  동료-딜 버전: 사건 파트너 본인 귀속 org 의 딜 제외 후 동일 추정.
  동학: 영입 스택의 fem×rel_k 경로 (k=−1 기준) — 감도 곡선(p001_14) 입력.
[사전 예측] (결과 전, 2026-09-03 — POWER_UPGRADE_PLAN P-1)
  P1 결합 대비 +1.5~+3pp, CI 폭 ≤ 3pp (04b 의 4.3pp 대비 축소).
  P2 동료-딜 결합이 0 에서 명확히 분리 (하한 > +0.3pp 또는 상한 < 0 — 어느 쪽이든 판별).
  P3 사전 경로 (k=−4..−2) 계수 CI 가 0 포함.
[판정] P1+P2(양의 분리)+P3 → E3 승격 조건 ① 의 딜 수준 성립 — 본문 사양 교체 후보
  (04b 는 robustness 로 강등, SUPERSEDED 아님 — 집계 수준 다름). 실패 시 04b 유지·기록.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["HARNESS_OUT"] = os.environ.get("P001_OUT", os.path.join(HERE, "out"))  # set P001_* / CRUNCHBASE_RAW to your local copies (licensed inputs; see DATA_ACCESS.md)
sys.path.insert(0, HERE)  # gates.py / emit_contract.py sit alongside in code/pipeline
from emit_contract import emit, qci  # noqa: E402
from gates import CTX  # noqa: E402

rng = np.random.default_rng(42)
NB = 300
EQ_EXCL = {"grant", "debt_financing", "post_ipo_debt", "post_ipo_equity", "non_equity_assistance"}
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR",
      "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}
NAEU = EU | {"USA", "CAN"}
KS = list(range(-4, 4))

people = CTX.people[["uuid", "gender"]]
g_map = people[people["gender"].isin(["male", "female"])].set_index("uuid")["gender"]
rounds = CTX.rounds.dropna(subset=["announced_on", "org_uuid"]).copy()
rounds = rounds[~rounds["investment_type"].isin(EQ_EXCL)]
rounds["dt"] = pd.to_datetime(rounds["announced_on"], errors="coerce")
rounds = rounds.dropna(subset=["dt"])
inv = CTX.inv.dropna(subset=["funding_round_uuid", "investor_uuid"])
pt = CTX.partners.dropna(subset=["funding_round_uuid", "investor_uuid", "partner_uuid"])
jobs = CTX.jobs
vc_country = dict(zip(CTX.investors["uuid"], CTX.investors["country_code"]))

pv = inv.merge(rounds[["uuid", "org_uuid", "dt"]], left_on="funding_round_uuid", right_on="uuid")
fd = pv.groupby(["investor_uuid", "org_uuid"])["dt"].min().rename("fdt").reset_index()
_acq = CTX.acq.dropna(subset=["acquiree_uuid", "acquired_on"]); _ip = CTX.ipos.dropna(subset=["org_uuid", "went_public_on"])
_fe = pd.concat([pd.to_datetime(_acq["acquired_on"], errors="coerce").groupby(_acq["acquiree_uuid"]).min(), pd.to_datetime(_ip["went_public_on"], errors="coerce").groupby(_ip["org_uuid"]).min()], axis=1).min(axis=1)
_ex = fd["org_uuid"].map(_fe); fd = fd[~(_ex.notna() & (_ex <= fd["fdt"]))].copy()   # D067 population rule: no exit on/before the deal
fj = jobs[jobs["title"].fillna("").str.lower().str.contains("founder", regex=False)][
    ["person_uuid", "org_uuid"]].dropna()
fj["fg"] = fj["person_uuid"].map(g_map)
fj = fj[fj["fg"].notna()]
org_ff = (fj["fg"] == "female").groupby(fj["org_uuid"]).max()
fd["ff"] = fd["org_uuid"].map(org_ff)
fd = fd[fd["ff"].notna()]
fd["ff"] = fd["ff"].astype(float)
fd["half"] = fd["fdt"].dt.year * 2 + (fd["fdt"].dt.month > 6).astype(int)
fd_by_v = {v: g.sort_values("half") for v, g in fd.groupby("investor_uuid")}

pa = pt.merge(rounds[["uuid", "dt"]], left_on="funding_round_uuid", right_on="uuid")
first_attr = pa.groupby(["partner_uuid", "investor_uuid"])["dt"].min().rename("fa")
own_orgs = pt.merge(rounds[["uuid", "org_uuid"]], left_on="funding_round_uuid", right_on="uuid") \
    .groupby(["partner_uuid", "investor_uuid"])["org_uuid"].agg(set)
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
ev = pd.concat([arr[["partner_uuid", "investor_uuid", "t", "kind"]], dep], ignore_index=True)
ev["pg"] = ev["partner_uuid"].map(g_map)
ev = ev[ev["pg"].notna()]
ev = ev[ev["investor_uuid"].map(vc_country).isin(NAEU)].reset_index(drop=True)
ev["h0"] = ev["t"].dt.year * 2 + (ev["t"].dt.month > 6).astype(int)
ev["fem"] = (ev["pg"] == "female").astype(float)
# 오염 남성 대조 제외 (04b 규칙)
by_inv = {v: g for v, g in ev.groupby("investor_uuid")}
keep = []
for i, e in ev.iterrows():
    if e["fem"] == 1:
        keep.append(True)
        continue
    g = by_inv[e["investor_uuid"]]
    keep.append(not ((g["fem"] == 1) & (abs(g["h0"] - e["h0"]) <= 4)).any())
ev = ev[pd.Series(keep, index=ev.index)].reset_index(drop=True)
ev["event_id"] = np.arange(len(ev))

# 사건별 딜 프레임 + 사전 특성(재가중용: 사전 ff·규모)
frames = []
pre_ff, pre_n = {}, {}
for e in ev.itertuples():
    g = fd_by_v.get(e.investor_uuid)
    if g is None:
        continue
    sub = g[(g["half"] >= e.h0 - 4) & (g["half"] <= e.h0 + 3)]
    if len(sub) < 6:
        continue
    pre = sub[sub["half"] < e.h0]
    post = sub[sub["half"] >= e.h0]
    if len(pre) < 3 or len(post) < 3:
        continue
    pre_ff[e.event_id] = pre["ff"].mean()
    pre_n[e.event_id] = len(sub)
    own = own_orgs.get((e.partner_uuid, e.investor_uuid), set())
    frames.append(pd.DataFrame({
        "event_id": e.event_id, "firm": e.investor_uuid, "kind": e.kind, "fem": e.fem,
        "rel": sub["half"].to_numpy() - e.h0, "y": sub["ff"].to_numpy(),
        "own": sub["org_uuid"].isin(own).to_numpy()}))
D = pd.concat(frames, ignore_index=True)
D["post"] = (D["rel"] >= 0).astype(float)
# 재가중 셀 (04b): 3년 bin × 사전 ff 3분위 × 규모 3분위 — 사건 가중을 딜에 상속
evk = ev[ev["event_id"].isin(pre_ff)].copy()
evk["pre_ff"] = evk["event_id"].map(pre_ff)
evk["size"] = evk["event_id"].map(pre_n)
evk["cal"] = (evk["h0"] // 6).astype(str)
evk["ffq"] = pd.qcut(evk["pre_ff"].rank(method="first"), 3, labels=False).astype(str)
evk["szq"] = pd.qcut(evk["size"].rank(method="first"), 3, labels=False).astype(str)
evk["cw"] = evk["kind"] + "|" + evk["cal"] + "|" + evk["ffq"] + "|" + evk["szq"]
wmap = {}
for cw, g in evk.groupby("cw"):
    nf, nm = (g["fem"] == 1).sum(), (g["fem"] == 0).sum()
    r = nf / nm if nm else 0.0
    for eid, fem in zip(g["event_id"], g["fem"]):
        wmap[eid] = 1.0 if fem == 1 else r
D["w"] = D["event_id"].map(wmap).fillna(0)
D = D[D["w"] > 0].reset_index(drop=True)


def wdemean(v, g, w):
    sw = pd.Series(w).groupby(g).transform("sum").to_numpy()
    m = pd.Series(v * w).groupby(g).transform("sum").to_numpy() / sw
    return v - m


def beta_stack(df):
    """가중 FWL: y ~ fem*post | event FE + rel FE."""
    y = df["y"].to_numpy(float)
    x = (df["fem"] * df["post"]).to_numpy(float)
    w = df["w"].to_numpy(float)
    ge = df["event_id"].to_numpy()
    gr = df["rel"].to_numpy()
    for _ in range(8):
        y = wdemean(y, ge, w)
        x = wdemean(x, ge, w)
        y = wdemean(y, gr, w)
        x = wdemean(x, gr, w)
    sxx = (w * x * x).sum()
    return float((w * x * y).sum() / sxx) if sxx > 0 else np.nan


def contrast(df):
    bj = beta_stack(df[df["kind"] == "join"])
    be = beta_stack(df[df["kind"] == "exit"])
    return bj, be, (bj - be if not (np.isnan(bj) or np.isnan(be)) else np.nan)


bj0, be0, bc0 = contrast(D)
Dc = D[~D["own"]].reset_index(drop=True)
bjc, bec, bcc = contrast(Dc)

# 동학 경로 (영입 스택, 딜 수준): fem×rel_k, k=−1 기준
DJ = D[D["kind"] == "join"].reset_index(drop=True)
path = {}
for k in KS:
    if k == -1:
        continue
    sub = DJ[DJ["rel"].isin([k, -1])].copy()
    sub["post"] = (sub["rel"] == k).astype(float)
    path[k] = beta_stack(sub)

firms = D["firm"].unique()
fidx = {f: g.index.to_numpy() for f, g in D.groupby("firm")}
fidx_c = {f: g.index.to_numpy() for f, g in Dc.groupby("firm")}
bs = {"c": [], "cc": [], "j": [], "e": []}
bs_path = {k: [] for k in KS if k != -1}                      # v2: per-period bootstrap intervals for the arrival path (Figure 2)
for _ in range(NB):
    pick = firms[rng.integers(0, len(firms), len(firms))]
    rows_ = np.concatenate([fidx[f] for f in pick])
    Db = D.loc[rows_].reset_index(drop=True)
    bj, be, bc = contrast(Db)
    DJb = Db[Db["kind"] == "join"]
    for k in bs_path:
        subk = DJb[DJb["rel"].isin([k, -1])].copy(); subk["post"] = (subk["rel"] == k).astype(float)
        vk = beta_stack(subk)
        if np.isfinite(vk): bs_path[k].append(vk)
    rows_c = np.concatenate([fidx_c[f] for f in pick if f in fidx_c])
    _, _, bc2 = contrast(Dc.loc[rows_c].reset_index(drop=True))
    if np.isfinite(bc):
        bs["c"].append(bc)
        bs["j"].append(bj)
        bs["e"].append(be)
    if np.isfinite(bc2):
        bs["cc"].append(bc2)
ci_c, ci_cc = qci(bs["c"]), qci(bs["cc"])
ci_j, ci_e = qci(bs["j"]), qci(bs["e"])
# v2 (2026-09-10, external review §6): (a) mirror-reversal test needs β_join + β_exit (= 0 under exact reversal), from the same joint draws;
# (b) the mechanical own-deal channel is s·(p_own − p_colleagues) on post-event deals of female arrivals — the inputs are reported, not assumed;
# (c) whether a female arrival is the firm's first female partner / a female departure removes its last one (descriptive).
bsum0 = bj0 + be0; ci_sum = qci(np.array(bs["j"]) + np.array(bs["e"]))
DJf = D[(D["kind"] == "join") & (D["fem"] == 1) & (D["post"] == 1)]
s_own = float(DJf["own"].mean()); p_own = float(DJf.loc[DJf["own"], "y"].mean()); p_col = float(DJf.loc[~DJf["own"], "y"].mean())
mech = s_own * (p_own - p_col)
act = pj.copy(); act["s"] = pd.to_datetime(act["started_on"], errors="coerce"); act["e"] = pd.to_datetime(act["ended_on"], errors="coerce")
act["pg"] = act["partner_uuid"].map(g_map); actf = act[act["pg"] == "female"]
def other_female_active(row):
    g = actf[(actf["investor_uuid"] == row["investor_uuid"]) & (actf["partner_uuid"] != row["partner_uuid"])]
    return bool(((g["s"].isna() | (g["s"] <= row["t"])) & (g["e"].isna() | (g["e"] > row["t"]))).any())
evf = ev[(ev["fem"] == 1) & ev["event_id"].isin(D["event_id"].unique())].copy()
evf["other_female"] = evf.apply(other_female_active, axis=1)
first_female_share = float(1 - evf.loc[evf["kind"] == "join", "other_female"].mean()); last_female_share = float(1 - evf.loc[evf["kind"] == "exit", "other_female"].mean())

pre_ok = all(abs(path.get(k, 0) or 0) < 0.02 for k in (-4, -3, -2))
width = (ci_c[1] - ci_c[0]) * 100
p1 = (ci_c[0] > 0) and (width <= 3.0)
p2 = (ci_cc[0] > 0.003) or (ci_cc[1] < 0)
status = "GO" if (ci_c[0] > 0 and p2 and pre_ok) else "PARTIAL"
verdict = (f"결합 대비(딜 수준)={bc0*100:+.2f}pp {ci_c} (폭 {width:.1f}pp; 04b 4.3pp); "
           f"영입={bj0*100:+.2f} {ci_j}·이탈={be0*100:+.2f} {ci_e}; "
           f"동료-딜 결합={bcc*100:+.2f} {ci_cc}; "
           f"사전 경로 k=-4..-2: {[round((path.get(k) or 0)*100,2) for k in (-4,-3,-2)]}; "
           f"딜 관측치 {len(D):,} (사건 {D['event_id'].nunique():,})"
           + (" — 딜 수준에서 E3 성립·동료 마진 판별" if (ci_c[0] > 0 and p2)
              else " — 부분: 04b 와 병기, 원장 기록"))

emit("P001-11", "E3 딜 수준 스택 회귀 — 정보 손실 제거 (Track D, P-1)", status,
     {"joint_contrast": [round(bc0 * 100, 2), ci_c], "join": [round(bj0 * 100, 2), ci_j],
      "exit": [round(be0 * 100, 2), ci_e],
      "colleague_joint": [round(bcc * 100, 2), ci_cc],
      "join_plus_exit": [round(bsum0 * 100, 2), ci_sum],                       # v2: = 0 under exact mirror reversal
      "mechanical_own_channel": {"own_share_post_female_join": round(s_own, 4), "ff_share_own_deals": round(p_own, 4), "ff_share_colleague_deals": round(p_col, 4),
                                 "direct_composition_pp": round(mech * 100, 2), "n_post_deals": int(len(DJf))},
      "female_events": {"n_join": int((evf["kind"] == "join").sum()), "share_first_female_partner": round(first_female_share, 4),
                        "n_exit": int((evf["kind"] == "exit").sum()), "share_last_female_partner": round(last_female_share, 4)},
      "path_join": {str(k): round((v or np.nan) * 100, 2) for k, v in path.items()},
      "path_join_ci": {str(k): [round(x * 100, 2) for x in qci(v)] for k, v in bs_path.items() if len(v) > 10},   # v2: per-period 95% bootstrap intervals (pp)
      "ci_width_pp": round(width, 2), "n_deal_obs": int(len(D)),
      "n_events": int(D["event_id"].nunique()),
      "p1_width": bool(p1), "p2_colleague_separated": bool(p2), "p3_pre_ok": bool(pre_ok)},
     prediction="결합 +1.5~+3pp·폭 ≤3pp; 동료 마진 0 에서 분리; 사전 경로 0 포함",
     verdict=verdict, kill_met=False, n=int(len(D)),
     extra={"stage": 5, "feeds": "Track D P-1 / E3 본문 사양 후보", "slug": "e3_deal_level"})
print("done")
