# -*- coding: utf-8 -*-
"""p001_19 (Track C-③) Snellman–Solal 회사 간 행 — 페널티 재현 후 셀 흡수 (R9)

[왜] 리뷰: "S&S 화해"를 주장하려면 그들의 between-firm 페널티를 먼저 우리 데이터에서 찾고,
그 다음 셀로 흡수됨을 보여야 함. is_lead_investor (374,871 True) 로 리드 식별 가능.
[설계] ff 기업의 첫 VC 라운드 (NA+EU, 2010–2020-10): 리드 투자사의 귀속 파트너 성별 (귀속
  없으면 리드 투자사 fp_share > 중위 로 대체 — 두 정의 병행). 결과 = 36m 후속 라운드.
  (a) S&S 형 raw: 연도 FE 만 (between-firm) — 그들의 페널티(2배↓) 방향이면 음(−).
  (b) + 섹터·스테이지·국가 FE (c) 풀 셀 근사(연도×섹터×스테이지×국가). 리드투자사 군집 부트 400.
[사전 예측] (결과 전, 2026-09-04) P1 raw 에서 음의 점추정 (S&S 방향) — 크기 미상 (그들은 OrgSci
  ·미국·초기 표본). P2 셀 추가로 절반 이상 감쇠. 재현 실패(raw ≈ 0) 도 가치: "우리 표본에는
  between-firm 페널티 자체가 없음" — 어느 쪽이든 §1 문장을 증거 기반으로 교체.
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
EQ_EXCL = {"grant", "debt_financing", "post_ipo_debt", "post_ipo_equity", "non_equity_assistance"}
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR",
      "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}
NAEU = EU | {"USA", "CAN"}

sv = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v2.parquet"))
people = CTX.people[["uuid", "gender"]]
g_map = people[people["gender"].isin(["male", "female"])].set_index("uuid")["gender"]
jobs = CTX.jobs
fj = jobs[jobs["title"].fillna("").str.lower().str.contains("founder", regex=False)][
    ["person_uuid", "org_uuid"]].dropna()
fj["fg"] = fj["person_uuid"].map(g_map)
fj = fj[fj["fg"].notna()]
org_ff = (fj["fg"] == "female").groupby(fj["org_uuid"]).max()

r = CTX.rounds.dropna(subset=["announced_on", "org_uuid"]).copy()
r = r[~r["investment_type"].isin(EQ_EXCL)]
r["rdt"] = pd.to_datetime(r["announced_on"], errors="coerce")
r = r.dropna(subset=["rdt"])
# ff 기업의 첫 라운드 (NA+EU, 2010–2020-10)
r1 = r.sort_values("rdt").groupby("org_uuid").head(1)
r1 = r1[(r1["rdt"] >= "2010-01-01") & (r1["rdt"] <= "2020-10-31")
        & r1["country_code"].isin(NAEU)].copy()
r1["ff"] = r1["org_uuid"].map(org_ff)
r1 = r1[r1["ff"] == True].copy()  # noqa: E712 — 여성 창업 기업만
inv = CTX.inv.dropna(subset=["funding_round_uuid", "investor_uuid"])
lead = inv[inv["is_lead_investor"] == True]  # noqa: E712
lead1 = lead.groupby("funding_round_uuid")["investor_uuid"].first()
r1["lead_inv"] = r1["uuid"].map(lead1)
r1 = r1[r1["lead_inv"].notna()].copy()
# 리드의 파트너 성별 (귀속 시) / fp_share 대체
pt = CTX.partners.dropna(subset=["funding_round_uuid", "investor_uuid", "partner_uuid"])
pt2 = pt.merge(r1[["uuid", "lead_inv"]], left_on=["funding_round_uuid", "investor_uuid"],
               right_on=["uuid", "lead_inv"])
pt2["pg"] = pt2["partner_uuid"].map(g_map)
lead_fp = pt2.dropna(subset=["pg"]).groupby("funding_round_uuid")["pg"] \
    .agg(lambda s: float((s == "female").any()))
r1["lead_fp_attr"] = r1["uuid"].map(lead_fp)
fp_share = sv.groupby("investor_uuid")["fp"].mean()
r1["lead_fps"] = r1["lead_inv"].map(fp_share)
med = r1["lead_fps"].median()
r1["lead_fp_share_hi"] = (r1["lead_fps"] > med).astype(float)
# 후속 36m
ro = r[["org_uuid", "rdt"]].sort_values(["org_uuid", "rdt"])
nxt = ro.groupby("org_uuid").nth(1)  # 두 번째 라운드
r1 = r1.merge(nxt.rename(columns={"rdt": "next_dt"}), on="org_uuid", how="left")
r1["fon"] = ((r1["next_dt"] - r1["rdt"]).dt.days <= 365 * 3).fillna(False).astype(float)
r1["yr"] = r1["rdt"].dt.year.astype(str)
r1["stage"] = r1["investment_type"].fillna("NA")
orgs = CTX.orgs
topcat = dict(zip(orgs["uuid"], orgs["category_groups_list"].fillna("NA").str.split(",").str[0].str.strip()))
r1["cat"] = r1["org_uuid"].map(topcat).fillna("NA")
r1["cell_a"] = r1["yr"]
r1["cell_b"] = r1["yr"] + "|" + r1["cat"] + "|" + r1["stage"] + "|" + r1["country_code"]


def gap(df, x, cell, nb=NB):
    dd = df.dropna(subset=[x]).reset_index(drop=True)
    if len(dd) < 300:
        return [None, [None, None], int(len(dd))]
    yr_ = (dd["fon"] - dd["fon"].groupby(dd[cell]).transform("mean")).to_numpy()
    xr_ = (dd[x].astype(float) - dd[x].astype(float).groupby(dd[cell]).transform("mean")).to_numpy()
    sxx = (xr_ * xr_).sum()
    if sxx == 0:
        return [None, [None, None], int(len(dd))]
    b = float((xr_ * yr_).sum() / sxx)
    grp = {c: g.index.to_numpy() for c, g in dd.groupby("lead_inv")}
    keys = list(grp)
    bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(keys), len(keys))
        rows_ = np.concatenate([grp[keys[i]] for i in pick])
        x2, y2 = xr_[rows_], yr_[rows_]
        s = (x2 * x2).sum()
        if s:
            bs.append((x2 * y2).sum() / s)
    return [round(b, 4), qci(bs), int(len(dd))]


out = {}
for x in ("lead_fp_attr", "lead_fp_share_hi"):
    out[x] = {"raw_yearFE": gap(r1, x, "cell_a"), "cells": gap(r1, x, "cell_b")}

a = out["lead_fp_attr"]["raw_yearFE"]
replicated = a[0] is not None and a[1][1] is not None and a[1][1] < 0
status = "GO"
verdict = (f"S&S 형 raw (리드 귀속 파트너 여성, 연도 FE): {a[0]} {a[1]} (n={a[2]}) — "
           + ("페널티 방향 재현" if replicated else "**between-firm 페널티 미재현**")
           + f"; 셀 추가: {out['lead_fp_attr']['cells'][0]} {out['lead_fp_attr']['cells'][1]}; "
           f"fp_share 정의 raw: {out['lead_fp_share_hi']['raw_yearFE'][0]} "
           f"{out['lead_fp_share_hi']['raw_yearFE'][1]} — §1 화해 문장을 이 증거로 교체")

emit("P001-19", "Snellman–Solal 회사 간 행 — 리드 투자자 성별과 후속 조달 (Track C-③)", status, out,
     prediction="raw 음의 점추정(S&S 방향) 후 셀에서 절반+ 감쇠 — 또는 미재현(그것도 발견)",
     verdict=verdict, kill_met=False, n=a[2] if a[2] else 0,
     extra={"stage": 5, "feeds": "R9 / §1 화해 문장", "slug": "ss_row"})
print("done")
