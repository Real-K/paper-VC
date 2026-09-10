# -*- coding: utf-8 -*-
"""I-74 동류교배 게이트 — 섹터·국가 구성 교란과 측정 강건성 (K-3 위협 검증)

[왜] I-73 GO: 동류교배 +6.67pp [5.56, 7.95] (투자사×연도 demean). 최대 위협 = 구성 교란:
여성 파트너가 여성 창업자가 많은 섹터(소비자·헬스·에드테크)나 국가에 배치되어 있으면
개인 매칭이 아니라 배치의 산물. 측정 위협 = ff 정의(여성 1명 vs 다수), 귀속 노이즈(다중 파트너).
[설계] (전부 I-73 표본·추정기 재사용)
  G1 셀 강화: 투자사×연도×대분류 카테고리 demean — 섹터 배치 교란 흡수.
  G2 셀 강화: 투자사×연도×기업국가 demean — 지리 배치 교란 흡수.
  G3 귀속 정밀: 단독 귀속 파트너 라운드만 (다중 파트너 딜의 귀속 노이즈 제거).
  G4 측정 강건: ff_maj = 성별 관측 창업자 중 여성 ≥ 50%.
  G5 순열 위약: 투자사×연도 셀 내 fp 무작위 재배열 200회 — 관측 효과의 순열 p.
[사전 예측] (결과 전, 2026-09-03)
  P1 G1·G2 후에도 효과 ≥ 기준(+6.67pp)의 절반(+3.3pp), CI 0 배제.
  P2 G3 단독 귀속에서 유지 또는 강화 (귀속 노이즈는 감쇠 방향이므로).
  P3 G4 ff_maj 에서 동부호·유의 (크기는 작아질 수 있음 — 기저 하락).
  P4 G5 순열 p < 0.005.
[판정] (사전 등록) P1 실패(카테고리/국가 셀에서 절반 미만 또는 CI 0 포함) → 구성 교란 —
  K-3 를 PARTIAL 로 강등하고 배치(assignment) 연구로 재설계. P1 통과 → GO 확정, 충격 레이어
  (여성 파트너 영입·이탈, I-29 재활용)로 진행.
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
org_fmaj = (fj["fg"] == "female").groupby(fj["org_uuid"]).mean() >= 0.5

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
d["ffm"] = d["org_uuid"].map(org_fmaj).astype(float)
d["year"] = d["dt"].dt.year.astype(str)
d["cat"] = d["org_uuid"].map(topcat)
d["cell0"] = d["investor_uuid"] + "|" + d["year"]
d["cell_cat"] = d["cell0"] + "|" + d["cat"].fillna("NA")
d["cell_cty"] = d["cell0"] + "|" + d["country_code"].fillna("NA")
n_per_round = pt.groupby("funding_round_uuid")["partner_uuid"].nunique()
d["solo"] = d["funding_round_uuid"].map(n_per_round) == 1


def fwl(df, y, x, cell, nb=NB):
    dd = df[[y, x, cell, "investor_uuid"]].reset_index(drop=True)
    yr = (dd[y] - dd[y].groupby(dd[cell]).transform("mean")).to_numpy()
    xr = (dd[x] - dd[x].groupby(dd[cell]).transform("mean")).to_numpy()
    sxx = (xr * xr).sum()
    if sxx == 0 or len(dd) < 500:
        return float("nan"), [float("nan")] * 2, int(len(dd))
    beta = float((xr * yr).sum() / sxx)
    grp = {c: g.index.to_numpy() for c, g in dd.groupby("investor_uuid")}
    keys = list(grp)
    bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(keys), len(keys))
        rows_ = np.concatenate([grp[keys[i]] for i in pick])
        x2, y2 = xr[rows_], yr[rows_]
        s = (x2 * x2).sum()
        if s:
            bs.append((x2 * y2).sum() / s)
    return beta, qci(bs), int(len(dd))


BASE = 0.0667
b1, ci1, n1 = fwl(d, "ff", "fp", "cell_cat")     # G1 섹터 셀
b2, ci2, n2 = fwl(d, "ff", "fp", "cell_cty")     # G2 국가 셀
b3, ci3, n3 = fwl(d[d["solo"]], "ff", "fp", "cell0")  # G3 단독 귀속
b4, ci4, n4 = fwl(d, "ffm", "fp", "cell0")       # G4 ff_maj

# G5 순열: cell0 내 fp 재배열
dd = d[["ff", "fp", "cell0"]].reset_index(drop=True)
yr = (dd["ff"] - dd["ff"].groupby(dd["cell0"]).transform("mean")).to_numpy()
xr0 = (dd["fp"] - dd["fp"].groupby(dd["cell0"]).transform("mean")).to_numpy()
obs = float((xr0 * yr).sum() / (xr0 * xr0).sum())
cells = dd.groupby("cell0").indices
perm_stats = []
fp_arr = dd["fp"].to_numpy()
for _ in range(200):
    fp_p = fp_arr.copy()
    for idx in cells.values():
        fp_p[idx] = fp_p[rng.permutation(idx)]
    xp = fp_p - pd.Series(fp_p).groupby(dd["cell0"]).transform("mean").to_numpy()
    s = (xp * xp).sum()
    perm_stats.append((xp * yr).sum() / s if s else np.nan)
perm_p = float(np.mean(np.abs(np.array(perm_stats)) >= abs(obs)))

g1_pass = (not np.isnan(b1)) and (b1 >= 0.5 * BASE) and (ci1[0] > 0)
g2_pass = (not np.isnan(b2)) and (b2 >= 0.5 * BASE) and (ci2[0] > 0)
composition_confound = not (g1_pass and g2_pass)
status = "PARTIAL" if composition_confound else "GO"
verdict = (f"섹터셀={b1:+.4f} {ci1}; 국가셀={b2:+.4f} {ci2}; 단독귀속={b3:+.4f} {ci3} (n={n3}); "
           f"ff_maj={b4:+.4f} {ci4}; 순열 p={perm_p:.4f} (관측 {obs:+.4f})"
           + (" — 구성 교란: PARTIAL 강등" if composition_confound
              else " — 구성 교란 배제, GO 확정 → 충격 레이어로"))

emit("I-74", "동류교배 게이트 — 섹터·국가 구성 교란과 측정 강건성 (K-3)", status,
     {"cell_cat": [None if np.isnan(b1) else round(b1, 4), ci1, n1],
      "cell_cty": [None if np.isnan(b2) else round(b2, 4), ci2, n2],
      "solo_attr": [None if np.isnan(b3) else round(b3, 4), ci3, n3],
      "ff_majority": [None if np.isnan(b4) else round(b4, 4), ci4, n4],
      "perm_p": perm_p, "obs_beta": round(obs, 4), "baseline_i73": BASE,
      "g1_pass": bool(g1_pass), "g2_pass": bool(g2_pass)},
     prediction="섹터·국가 셀에서 ≥ +3.3pp CI 0 배제; 단독 귀속 유지·강화; ff_maj 동부호 유의; 순열 p<0.005",
     verdict=verdict, kill_met=False, n=n1,
     extra={"stage": 2, "feeds": "I-73 게이트", "slug": "gender_gates"})
print("done")
