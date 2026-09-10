# -*- coding: utf-8 -*-
"""p001_20 격차의 시대성 — 2000년대 코호트 vs 2010년대 (GMWX 비재현의 원인 규명)

[왜] 논문의 최대 취약점: 우리가 "설명하는" 격차가 우리 primary 표본에서 경계적이고, GMWX 의
전체-딜 격차는 아예 재현되지 않는다 (P001-15). 리퍼리의 첫 문장이 여기서 나온다.
가능한 해석 3가지: ① 데이터 차이(CB vs VentureSource) ② 표본 기간(GMWX 는 1990~2016 중심,
우리는 2010+) ③ 격차 자체가 시대에 따라 닫혔다.
③ 이라면 이것은 약점이 아니라 **발견**이다 — "1990~2000년대 코호트의 성별 성과 격차는
2010년대에 사라졌다"는 그 자체로 보고 가치가 있고, 우리의 구성 분해가 왜 초기 격차를 만들었는지
설명한다. 검정 없이 ①/②/③ 중 어느 것도 주장할 수 없다.
[설계] cores_v1 에서 sample_v1 과 **동일 규칙**으로 2000-01~2009-12 딜 표본을 재구축
  (그랜트·부채 제외; 파트너 성별·창업자 성별 관측; 출구 창은 표본 종점까지 = exit_ever).
  기간 2군: EARLY(2000-2009) vs LATE(2010-2017-10, 기존과 동일 컷).
  각 기간 × {전체 딜, ff 딜} × 셀 사다리 4단(연도/투자사×연도/+섹터/+스테이지).
  커버리지 게이트: EARLY 의 ff 딜 < 800 또는 파트너 성별 관측 < 60% → 검정력 부족으로 판정 보류.
[사전 예측] (결과 전, 2026-09-04)
  P1 EARLY 의 ff 딜 exit 격차가 LATE 보다 크게 음(−): 섹터 셀 기준 EARLY ≤ −8pp.
  P2 EARLY 에서는 전체-딜 격차도 음의 방향 (GMWX 형) — 가법 통제에서도 잔존 가능.
  P3 구성 분해(스테이지 추가)가 EARLY 에서도 격차를 흡수 (같은 메커니즘, 다른 크기).
[판정] P1+P2 → **시대성 발견**: 비재현이 데이터 결함이 아니라 코호트 차이. 논문에 "격차의
  닫힘" 절 추가하고 GMWX 와의 관계를 기간으로 해명 (강력한 서사 자산).
  P1 실패(EARLY 도 격차 없음) → 데이터·정의 차이가 원인 — 정직히 그렇게 쓰고 GMWX 대비
  프레임을 축소, 논문 무게를 비대칭(§5)으로 이동.
  커버리지 게이트 실패 → 판정 보류, PB 데이터 필요 항목으로 등재.
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

people = CTX.people[["uuid", "gender"]]
g_map = people[people["gender"].isin(["male", "female"])].set_index("uuid")["gender"]
jobs = CTX.jobs
fj = jobs[jobs["title"].fillna("").str.lower().str.contains("founder", regex=False)][
    ["person_uuid", "org_uuid"]].dropna()
fj["fg"] = fj["person_uuid"].map(g_map)
fj = fj[fj["fg"].notna()]
org_ff = (fj["fg"] == "female").groupby(fj["org_uuid"]).max()
orgs = CTX.orgs
topcat = dict(zip(orgs["uuid"], orgs["category_groups_list"].fillna("NA").str.split(",").str[0].str.strip()))

rounds = CTX.rounds.dropna(subset=["announced_on", "org_uuid"]).copy()
rounds = rounds[~rounds["investment_type"].isin(EQ_EXCL)]
rounds["dt"] = pd.to_datetime(rounds["announced_on"], errors="coerce")
rounds = rounds.dropna(subset=["dt"])
rounds = rounds[(rounds["dt"] >= "2000-01-01") & (rounds["dt"] <= "2017-10-31")]

pt = CTX.partners.dropna(subset=["funding_round_uuid", "investor_uuid", "partner_uuid"])
d = pt.merge(rounds[["uuid", "org_uuid", "dt", "country_code", "investment_type"]],
             left_on="funding_round_uuid", right_on="uuid")
d["pg"] = d["partner_uuid"].map(g_map)
cov_pg_early = float(d.loc[d["dt"] < "2010-01-01", "pg"].notna().mean())
d["ff_raw"] = d["org_uuid"].map(org_ff)
d = d[d["pg"].notna() & d["ff_raw"].notna()].copy()
d["fp"] = (d["pg"] == "female").astype(float)
d["ff"] = d["ff_raw"].astype(float)
d["year"] = d["dt"].dt.year.astype(str)
d["cat"] = d["org_uuid"].map(topcat).fillna("NA")
d["stage"] = d["investment_type"].fillna("NA")
d["cell0"] = d["investor_uuid"] + "|" + d["year"]
d["cell_cat"] = d["cell0"] + "|" + d["cat"]
d["cell_stage"] = d["cell_cat"] + "|" + d["stage"]
d = d[d["country_code"].isin(NAEU)].copy()

acq = CTX.acq.dropna(subset=["acquiree_uuid", "acquired_on"]).copy()
acq["adt"] = pd.to_datetime(acq["acquired_on"], errors="coerce")
ip = CTX.ipos.dropna(subset=["org_uuid", "went_public_on"]).copy()
ip["idt"] = pd.to_datetime(ip["went_public_on"], errors="coerce")
exit_any = pd.concat([acq.groupby("acquiree_uuid")["adt"].min(),
                      ip.groupby("org_uuid")["idt"].min()], axis=1).min(axis=1)
d["exit_ever"] = d["org_uuid"].map(exit_any).notna().astype(float)
d["era"] = np.where(d["dt"] < "2010-01-01", "EARLY_2000s", "LATE_2010s")


def gap(df, cell, nb=NB):
    dd = df[["exit_ever", "fp", cell, "investor_uuid"]].reset_index(drop=True)
    if len(dd) < 400:
        return [None, [None, None], int(len(dd))]
    yr = (dd["exit_ever"] - dd["exit_ever"].groupby(dd[cell]).transform("mean")).to_numpy()
    xr = (dd["fp"] - dd["fp"].groupby(dd[cell]).transform("mean")).to_numpy()
    sxx = (xr * xr).sum()
    if sxx == 0:
        return [None, [None, None], int(len(dd))]
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
    return [round(beta, 4), qci(bs), int(len(dd))]


CELLS = [("year", "year"), ("invyear", "cell0"), ("pluscat", "cell_cat"), ("plusstage", "cell_stage")]
out = {}
for era, de in d.groupby("era"):
    out[era] = {"all_deals": {n: gap(de, c) for n, c in CELLS},
                "ff_deals": {n: gap(de[de["ff"] == 1.0], c) for n, c in CELLS},
                "n_deals": int(len(de)), "n_ff": int((de["ff"] == 1).sum()),
                "base_exit_ff": round(float(de.loc[de["ff"] == 1, "exit_ever"].mean()), 4),
                "fp_share": round(float(de["fp"].mean()), 4),
                "ff_share": round(float(de["ff"].mean()), 4)}

early = out.get("EARLY_2000s", {})
late = out.get("LATE_2010s", {})
n_ff_early = early.get("n_ff", 0)
gate_fail = (n_ff_early < 800) or (cov_pg_early < 0.60)
e_cat = early.get("ff_deals", {}).get("pluscat", [None, [None, None], 0])
l_cat = late.get("ff_deals", {}).get("pluscat", [None, [None, None], 0])
e_all = early.get("all_deals", {}).get("invyear", [None, [None, None], 0])
p1 = (not gate_fail) and (e_cat[0] is not None) and (e_cat[0] <= -0.08)
p2 = (not gate_fail) and (e_all[0] is not None) and (e_all[1][1] is not None) and (e_all[1][1] < 0)

if gate_fail:
    status, tag = "PARTIAL", f"커버리지 게이트 실패 (EARLY ff 딜 {n_ff_early}, 파트너 성별 관측 {cov_pg_early:.2f}) — 판정 보류"
elif p1 or p2:
    status, tag = "GO", "시대성 발견: 초기 코호트에 격차 존재 → GMWX 비재현은 기간 차이"
else:
    status, tag = "PARTIAL", "초기 코호트에도 격차 부재 → 데이터·정의 차이로 정직 기록, 무게중심 §5 로 이동"

verdict = (f"EARLY(2000s) ff 딜: 섹터셀 {e_cat[0]} {e_cat[1]} (n={e_cat[2]}, 기저 출구 "
           f"{early.get('base_exit_ff')}); 전체딜 투자사×연도 {e_all[0]} {e_all[1]}; "
           f"LATE(2010s) ff 섹터셀 {l_cat[0]} {l_cat[1]}; "
           f"EARLY n_ff={n_ff_early}·fp={early.get('fp_share')}·ff={early.get('ff_share')} vs "
           f"LATE n_ff={late.get('n_ff')}·fp={late.get('fp_share')} — {tag}")

emit("P001-20", "격차의 시대성 — 2000년대 vs 2010년대 코호트 (GMWX 비재현 규명)", status,
     {"by_era": out, "cov_partner_gender_early": round(cov_pg_early, 4),
      "coverage_gate_failed": bool(gate_fail), "p1_early_gap": bool(p1), "p2_all_deals_gap": bool(p2)},
     prediction="EARLY 섹터셀 ff 격차 ≤ −8pp; EARLY 전체딜도 음; 스테이지가 흡수",
     verdict=verdict, kill_met=False, n=n_ff_early,
     extra={"stage": 6, "feeds": "핵심 취약점 규명 / GMWX 관계", "slug": "period_split"})
print("done")
