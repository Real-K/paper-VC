# -*- coding: utf-8 -*-
"""I-75 판별의 섹터 셀 재추정 — 선별 vs 호의, 구성 교란 통제 하 (K-3 최종 게이트)

[왜] I-74: 원 동류교배 +6.67pp 의 절반이 섹터 배치(섹터 셀 +3.03pp) → estimand 를 "섹터 내"로
이동(rules/11 §6: 근소 실패 시 주장 문턱 상향). 그러면 I-73 의 판별(H2: gap_ff, gap_mf)도
섹터별 출구율 차이가 교란할 수 있어 투자사×연도×대분류 셀로 재추정해야 일관된다.
[설계] I-73 의 gaps() 를 cell = investor|year|topcat 으로 재실행. 결과 = 출구 72m(라운드
2010–2017-10) · 후속 36m(2010–2020-10). 공동 투자사 부트 500.
[사전 예측] (결과 전, 2026-09-03)
  P1 후속 gap_ff 하한 > −5pp (호의의 물질적 성과 열위 배제 유지).
  P2 출구 gap_ff 하한 > −10pp.
  P3 판별자(gap_ff − gap_mf) CI 가 −10pp 이하 배제.
[판정] (사전 등록) P1·P2 유지 → K-3 GO 복귀: 논문 골격 = 2층 분류(섹터 배치 + 섹터 내 매칭)
  × 성과 무열위(선별 방향) + 충격 레이어(여성 파트너 영입·이탈). P1 또는 P2 실패(하한 붕괴)
  → 호의 방향 재검토, K-3 는 PARTIAL 유지.
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
EQ_EXCL = {"grant", "debt_financing", "post_ipo_debt", "post_ipo_equity", "non_equity_assistance"}

people = CTX.people[["uuid", "gender"]]
g_map = people[people["gender"].isin(["male", "female"])].set_index("uuid")["gender"]

rounds = CTX.rounds.dropna(subset=["announced_on", "org_uuid"]).copy()
rounds = rounds[~rounds["investment_type"].isin(EQ_EXCL)]
rounds["dt"] = pd.to_datetime(rounds["announced_on"], errors="coerce")
rounds = rounds.dropna(subset=["dt"])
rounds = rounds[(rounds["dt"] >= "2010-01-01") & (rounds["dt"] <= "2023-10-31")]

jobs = CTX.jobs
fj = jobs[jobs["title"].fillna("").str.lower().str.contains("founder", regex=False)][
    ["person_uuid", "org_uuid"]].dropna()
fj["fg"] = fj["person_uuid"].map(g_map)
fj = fj[fj["fg"].notna()]
org_ff = (fj["fg"] == "female").groupby(fj["org_uuid"]).max()
orgs = CTX.orgs
topcat = dict(zip(orgs["uuid"], orgs["category_groups_list"].fillna("NA").str.split(",").str[0].str.strip()))

pt = CTX.partners.dropna(subset=["funding_round_uuid", "investor_uuid", "partner_uuid"])
d = pt.merge(rounds[["uuid", "org_uuid", "dt", "country_code"]],
             left_on="funding_round_uuid", right_on="uuid")
d["pg"] = d["partner_uuid"].map(g_map)
d["ff"] = d["org_uuid"].map(org_ff)
d = d[d["pg"].notna() & d["ff"].notna()].copy()
d["fp"] = (d["pg"] == "female").astype(float)
d["ff"] = d["ff"].astype(float)
d["year"] = d["dt"].dt.year.astype(str)
d["cell"] = d["investor_uuid"] + "|" + d["year"] + "|" + d["org_uuid"].map(topcat).fillna("NA")

r_org = rounds[["org_uuid", "dt"]].sort_values(["org_uuid", "dt"]).copy()
r_org["next_dt"] = r_org.groupby("org_uuid")["dt"].shift(-1)
next_map = r_org.drop_duplicates(["org_uuid", "dt"]).set_index(["org_uuid", "dt"])["next_dt"]
d["next_dt"] = pd.Series(list(zip(d["org_uuid"], d["dt"]))).map(next_map).to_numpy()
d["fon"] = ((pd.to_datetime(d["next_dt"]) - d["dt"]).dt.days <= 365 * 3).fillna(False).astype(float)
acq = CTX.acq.dropna(subset=["acquiree_uuid", "acquired_on"]).copy()
acq["adt"] = pd.to_datetime(acq["acquired_on"], errors="coerce")
ip = CTX.ipos.dropna(subset=["org_uuid", "went_public_on"]).copy()
ip["idt"] = pd.to_datetime(ip["went_public_on"], errors="coerce")
exit_dt = pd.concat([acq.groupby("acquiree_uuid")["adt"].min(),
                     ip.groupby("org_uuid")["idt"].min()], axis=1).min(axis=1)
d["exit_dt"] = d["org_uuid"].map(exit_dt)
d["exit6"] = ((d["exit_dt"] - d["dt"]).dt.days <= 365 * 6).fillna(False).astype(float)


def gaps(df, y, nb=NB):
    sub = {s: df[df["ff"] == s][[y, "fp", "cell", "investor_uuid"]].reset_index(drop=True)
           for s in (1.0, 0.0)}
    res, arrs = {}, {}
    for s, dd in sub.items():
        yr = (dd[y] - dd[y].groupby(dd["cell"]).transform("mean")).to_numpy()
        xr = (dd["fp"] - dd["fp"].groupby(dd["cell"]).transform("mean")).to_numpy()
        arrs[s] = (yr, xr, {c: g.index.to_numpy() for c, g in dd.groupby("investor_uuid")})
        sxx = (xr * xr).sum()
        res[s] = float((xr * yr).sum() / sxx) if sxx else float("nan")
    bs = {1.0: [], 0.0: [], "diff": []}
    keys = {s: list(arrs[s][2]) for s in arrs}
    for _ in range(nb):
        cur = {}
        for s in (1.0, 0.0):
            yr, xr, grp = arrs[s]
            ks = keys[s]
            pick = rng.integers(0, len(ks), len(ks))
            rows_ = np.concatenate([grp[ks[i]] for i in pick])
            x2, y2 = xr[rows_], yr[rows_]
            sx = (x2 * x2).sum()
            cur[s] = (x2 * y2).sum() / sx if sx else np.nan
            bs[s].append(cur[s])
        bs["diff"].append(cur[1.0] - cur[0.0])
    return (res[1.0], qci(bs[1.0]), res[0.0], qci(bs[0.0]),
            res[1.0] - res[0.0], qci(bs["diff"]),
            int((df["ff"] == 1).sum()), int((df["ff"] == 0).sum()))


gff_e, ciff_e, gmf_e, cimf_e, dj_e, cidj_e, nf_e, nm_e = gaps(d[d["dt"] <= "2017-10-31"], "exit6")
gff_f, ciff_f, gmf_f, cimf_f, dj_f, cidj_f, nf_f, nm_f = gaps(d[d["dt"] <= "2020-10-31"], "fon")

p1 = (not np.isnan(ciff_f[0])) and (ciff_f[0] > -0.05)
p2 = (not np.isnan(ciff_e[0])) and (ciff_e[0] > -0.10)
p3 = (not np.isnan(cidj_e[0])) and (cidj_e[0] > -0.10) and (cidj_f[0] > -0.10)
status = "GO" if (p1 and p2) else "PARTIAL"
verdict = (f"섹터셀 출구 gap_ff={gff_e:+.4f} {ciff_e} vs gap_mf={gmf_e:+.4f} {cimf_e}, "
           f"판별자={dj_e:+.4f} {cidj_e}; 후속 gap_ff={gff_f:+.4f} {ciff_f}, 판별자={dj_f:+.4f} {cidj_f}"
           + (" — 성과 무열위 유지: K-3 GO 복귀 (2층 분류 + 선별 방향)" if (p1 and p2)
              else " — 하한 붕괴: 호의 재검토, PARTIAL 유지"))

emit("I-75", "판별의 섹터 셀 재추정 — 선별 vs 호의 (K-3 최종 게이트)", status,
     {"exit_gap_ff": [round(gff_e, 4), ciff_e, nf_e], "exit_gap_mf": [round(gmf_e, 4), cimf_e, nm_e],
      "exit_adjudicator": [round(dj_e, 4), cidj_e],
      "fon_gap_ff": [round(gff_f, 4), ciff_f, nf_f], "fon_gap_mf": [round(gmf_f, 4), cimf_f, nm_f],
      "fon_adjudicator": [round(dj_f, 4), cidj_f],
      "p1_fon_floor": bool(p1), "p2_exit_floor": bool(p2), "p3_adjud_floor": bool(p3)},
     prediction="후속 gap_ff 하한 > −5pp; 출구 하한 > −10pp; 판별자 −10pp 배제",
     verdict=verdict, kill_met=False, n=nf_f,
     extra={"stage": 2, "feeds": "I-73/I-74 최종 게이트", "slug": "gender_adjud_cells"})
print("done")
