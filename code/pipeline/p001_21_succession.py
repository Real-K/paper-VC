# -*- coding: utf-8 -*-
"""p001_21 승계 검정 — 여성 파트너가 떠난 뒤 그 딜 채널을 누가 이어받는가

[왜] §5 의 비대칭(영입 +2.81 / 이탈 무반전)이 논문에서 가장 새롭고 반직관적인 사실이지만,
지금은 "회사 수준 비중이 안 떨어졌다"는 관측일 뿐 **메커니즘이 비어 있다**. 회사 비중이 유지되는
경로는 셋뿐이다:
  (A) 잔류 동료(특히 남성)가 ff 딜을 이어받음 → **개인 자본의 조직 자본 전환** (진짜 발견;
      Ewens-Rhodes-Kropf JF 2015 의 "파트너 인적자본 우위" 및 관계금융 문헌(담당자 이탈=관계 단절,
      JFQA 2025 동문 파트너 퇴직 시 딜 감소)과 정면 대비)
  (B) 신규 채용(특히 여성 대체 채용)이 자리를 메움 → "회사가 성별 구성을 유지한다"는 다른 이야기
  (C) 떠난 파트너의 딜이 애초에 회사 딜플로우의 미미한 부분 → 비대칭이 사소해짐
어느 경로인지 데이터가 답할 수 있다. 이 검정 없이 "doors stay open" 서사는 해석이지 증거가 아니다.
[설계] 사건 = 파트너 마지막 이탈 (P,V,t), NA+EU 투자사, 2012-01~2021-10 (사후 24m 관측 확보).
  창 = 사전 (t−24m, t) / 사후 [t, t+24m). 판정가능 딜만.
  분류 = 사후 딜의 귀속 파트너가 (i) 잔류 동료(사전 창에 V 에서 귀속 이력 있음, P 제외),
        (ii) 신규 파트너(사전 창 귀속 없음), 성별 별도.
  주 결과 y_inc = **잔류 동료 귀속 딜의 ff 비중** (사전 vs 사후), DiD = 여성 이탈 − 남성 이탈.
  보조: (a) 신규 파트너 귀속 딜의 ff 비중 (b) 24m 내 여성 파트너 신규 귀속 발생률(대체 채용 프록시)
       (c) 떠난 파트너의 사전 딜 점유율(경로 C 크기).
  추론: 투자사 군집 부트 400.
[사전 예측] (결과 전, 2026-09-04)
  P1 잔류 동료 ff 비중 DiD ≥ 0 (경로 A 지지). 특히 **남성 잔류 동료**에서 ≥ 0 이면 강한 증거.
  P2 여성 대체 채용률의 DiD 가 작음(< +10pp) — 경로 B 가 단독 설명이 아님.
  P3 떠난 파트너의 사전 딜 점유율 10~25% (경로 C 배제 — 미미하지 않음).
[판정] P1(하한 > −1pp) + P2 → **승계 증거**: §5 를 "채널의 조직 이전"으로 승격, 논문 무게중심을
  비대칭·조직자본으로 이동 가능. P1 실패(잔류 동료 ff 비중 유의 하락) → 회사 수준 무반전은
  대체 채용의 산물 — 서사를 그렇게 정정. 어느 쪽이든 원장 기록.
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
NB = 400
W = pd.Timedelta(days=730)
EQ_EXCL = {"grant", "debt_financing", "post_ipo_debt", "post_ipo_equity", "non_equity_assistance"}
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR",
      "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}
NAEU = EU | {"USA", "CAN"}
MIN_SIDE = 3

people = CTX.people[["uuid", "gender"]]
g_map = people[people["gender"].isin(["male", "female"])].set_index("uuid")["gender"]
jobs = CTX.jobs
fj = jobs[jobs["title"].fillna("").str.lower().str.contains("founder", regex=False)][
    ["person_uuid", "org_uuid"]].dropna()
fj["fg"] = fj["person_uuid"].map(g_map)
fj = fj[fj["fg"].notna()]
org_ff = (fj["fg"] == "female").groupby(fj["org_uuid"]).max()

rounds = CTX.rounds.dropna(subset=["announced_on", "org_uuid"]).copy()
rounds = rounds[~rounds["investment_type"].isin(EQ_EXCL)]
rounds["dt"] = pd.to_datetime(rounds["announced_on"], errors="coerce")
rounds = rounds.dropna(subset=["dt"])
pt = CTX.partners.dropna(subset=["funding_round_uuid", "investor_uuid", "partner_uuid"])
A = pt.merge(rounds[["uuid", "org_uuid", "dt"]], left_on="funding_round_uuid", right_on="uuid")
A["ff"] = A["org_uuid"].map(org_ff)
A = A[A["ff"].notna()].copy()
A["ff"] = A["ff"].astype(float)
A["pg"] = A["partner_uuid"].map(g_map)
A_by_v = {v: g.sort_values("dt") for v, g in A.groupby("investor_uuid")}

vc_country = dict(zip(CTX.investors["uuid"], CTX.investors["country_code"]))
pj = jobs.merge(pt[["partner_uuid", "investor_uuid"]].drop_duplicates(),
                left_on=["person_uuid", "org_uuid"], right_on=["partner_uuid", "investor_uuid"])
dep = pj[pj["ended_on"].notna()].copy()
dep["t"] = pd.to_datetime(dep["ended_on"], errors="coerce")
dep = dep.dropna(subset=["t"])
dep = dep[(dep["t"] >= "2012-01-01") & (dep["t"] <= "2021-10-31")]
dep = dep.sort_values("t").groupby(["partner_uuid", "investor_uuid"]).tail(1)[
    ["partner_uuid", "investor_uuid", "t"]]
dep["pg"] = dep["partner_uuid"].map(g_map)
dep = dep[dep["pg"].notna()]
dep = dep[dep["investor_uuid"].map(vc_country).isin(NAEU)].reset_index(drop=True)

rows = []
for e in dep.itertuples():
    g = A_by_v.get(e.investor_uuid)
    if g is None:
        continue
    pre = g[(g["dt"] >= e.t - W) & (g["dt"] < e.t)]
    post = g[(g["dt"] >= e.t) & (g["dt"] < e.t + W)]
    if len(pre) < MIN_SIDE or len(post) < MIN_SIDE:
        continue
    incumbents = set(pre["partner_uuid"]) - {e.partner_uuid}
    if not incumbents:
        continue
    pre_inc = pre[pre["partner_uuid"].isin(incumbents)]
    post_inc = post[post["partner_uuid"].isin(incumbents)]
    if len(pre_inc) < MIN_SIDE or len(post_inc) < MIN_SIDE:
        continue
    # 남성 잔류 동료만
    inc_m = {p for p in incumbents if g_map.get(p) == "male"}
    pre_m = pre_inc[pre_inc["partner_uuid"].isin(inc_m)]
    post_m = post_inc[post_inc["partner_uuid"].isin(inc_m)]
    # 신규 파트너 귀속 딜
    post_new = post[~post["partner_uuid"].isin(set(pre["partner_uuid"]))]
    # 여성 신규 파트너 등장 여부 (대체 채용 프록시)
    new_fem = float(any(g_map.get(p) == "female" for p in set(post_new["partner_uuid"])))
    own_share = float((pre["partner_uuid"] == e.partner_uuid).mean())
    rows.append({
        "fem": 1.0 if e.pg == "female" else 0.0, "firm": e.investor_uuid,
        "d_inc": float(post_inc["ff"].mean() - pre_inc["ff"].mean()),
        "d_inc_m": (float(post_m["ff"].mean() - pre_m["ff"].mean())
                    if (len(pre_m) >= MIN_SIDE and len(post_m) >= MIN_SIDE) else np.nan),
        "new_ff": float(post_new["ff"].mean()) if len(post_new) >= MIN_SIDE else np.nan,
        "new_fem_hire": new_fem, "own_share": own_share,
        "n_post_new": int(len(post_new))})
E = pd.DataFrame(rows)


def did(col, nb=NB):
    sub = E[["fem", "firm", col]].dropna().reset_index(drop=True)
    nf = int((sub["fem"] == 1).sum())
    nm = int((sub["fem"] == 0).sum())
    if nf < 40 or nm < 40:
        return [None, [None, None], nf, nm]
    b0 = float(sub.loc[sub["fem"] == 1, col].mean() - sub.loc[sub["fem"] == 0, col].mean())
    grp = {c: g.index.to_numpy() for c, g in sub.groupby("firm")}
    keys = list(grp)
    bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(keys), len(keys))
        s = sub.loc[np.concatenate([grp[keys[i]] for i in pick])]
        if (s["fem"] == 1).sum() >= 10 and (s["fem"] == 0).sum() >= 10:
            bs.append(float(s.loc[s["fem"] == 1, col].mean() - s.loc[s["fem"] == 0, col].mean()))
    return [round(b0, 4), qci(bs), nf, nm]


inc = did("d_inc")
inc_m = did("d_inc_m")
newff = did("new_ff")
hire = did("new_fem_hire")
own_f = float(E.loc[E["fem"] == 1, "own_share"].mean()) if len(E) else float("nan")
raw_f = float(E.loc[E["fem"] == 1, "d_inc"].mean()) if len(E) else float("nan")
raw_m = float(E.loc[E["fem"] == 0, "d_inc"].mean()) if len(E) else float("nan")

p1 = (inc[0] is not None) and (inc[1][0] is not None) and (inc[1][0] > -0.01)
p2 = (hire[0] is not None) and (hire[0] < 0.10)
p3 = (not np.isnan(own_f)) and (0.05 <= own_f <= 0.40)
if inc[0] is None:
    status, tag = "PARTIAL", "표본 부족 — 판정 보류"
elif p1 and p2:
    status, tag = "GO", "승계 증거: 잔류 동료가 채널을 이어받음 (경로 A) — §5 를 조직자본 전환으로 승격 가능"
elif not p1:
    status, tag = "PARTIAL", "잔류 동료 ff 비중 하락 — 회사 수준 무반전은 신규 채용의 산물 (경로 B): 서사 정정 필요"
else:
    status, tag = "PARTIAL", "혼합 경로 — 대체 채용이 상당 부분 설명"

verdict = (f"잔류 동료 ff 비중 DiD(여−남 이탈) = {inc[0]} {inc[1]} (여 {inc[2]}·남 {inc[3]} 사건; "
           f"원 변화 여 {raw_f:+.4f} vs 남 {raw_m:+.4f}); **남성 잔류 동료만** {inc_m[0]} {inc_m[1]}; "
           f"신규 파트너 딜 ff 비중 DiD {newff[0]} {newff[1]}; 여성 신규 귀속 발생 DiD {hire[0]} {hire[1]}; "
           f"떠난 여성 파트너의 사전 딜 점유율 {own_f:.3f} — {tag}")

emit("P001-21", "승계 검정 — 이탈 후 채널을 누가 이어받는가 (§5 메커니즘)", status,
     {"incumbent_ff_did": inc, "incumbent_male_only_did": inc_m,
      "new_partner_ff_did": newff, "female_replacement_did": hire,
      "departing_own_share_pre": round(own_f, 4) if not np.isnan(own_f) else None,
      "raw_change_female_dep": round(raw_f, 4) if not np.isnan(raw_f) else None,
      "raw_change_male_dep": round(raw_m, 4) if not np.isnan(raw_m) else None,
      "n_events": int(len(E)), "p1_inheritance": bool(p1), "p2_not_replacement": bool(p2),
      "p3_own_share_material": bool(p3)},
     prediction="잔류 동료 DiD 하한 > −1pp; 여성 대체 채용 DiD < +10pp; 사전 점유율 10~25%",
     verdict=verdict, kill_met=False, n=int(len(E)),
     extra={"stage": 6, "feeds": "§5 비대칭의 메커니즘 (논문 최대 novelty 후보)", "slug": "succession"})
print("done")
