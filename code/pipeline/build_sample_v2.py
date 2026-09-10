# -*- coding: utf-8 -*-
"""P001 정본 표본 v2 — 파트너 귀속 딜 수준 분석 표본, **첫 출구 위험집합** 정의 (D067; 외부 리뷰 2026-09-10 §7-2·§3 및 후속 코멘트 c1 §6·c2 §5)

v1 과의 차이 하나: 라운드 일자 이전 또는 당일에 인수·IPO 가 기록된 회사의 라운드는 **표본에서 제외**한다(결과를 0 으로 재코딩하지 않음).
 이유: 연구 대상은 "VC 딜 이후 회사의 첫 출구" 이므로, 이미 출구한 회사의 후속 자금조달(인수된 회사의 PE·secondary·unlabelled 라운드,
 상장사의 미표기 라운드)은 위험집합에 속하지 않는다. 같은 날 기록된 출구도 "딜 이후" 가 아니므로 제외한다(그 라운드가 출구 거래 자체일 가능성).
 따라서 v2 에서는 모든 출구 결과(exit3·exit6·ipo6·acqp6·exit_ever·closed6)가 구성상 딜 이후 사건이다.

입력: shared/data/processed/cores_v1/*.parquet (MANIFEST.json 참조)
출력: 05_data/sample_v2.parquet + 05_data/sample_v2_manifest.yaml (행수·sha256_16·제외 행수·기저율)

구축 규칙 (v1 과 동일, 제외 규칙만 추가):
  - 라운드: announced_on 2010-01-01~2023-10-31, 그랜트·부채·post-IPO·non-equity 제외
  - 단위: investment_partners 의 (round × investor × partner) 귀속 행
  - fp: 파트너 성별 female (people.gender ∈ {male,female} 만 판정)
  - ff: founder 직함 jobs × gender — 여성 창업자 ≥1 (판정 가능 = 성별 관측 창업자 ≥1)
  - **제외: 회사의 첫 인수일 또는 첫 IPO 일 ≤ 라운드 일자**
  - 결과: fon(후속 36m) · exit6/ipo6/acqp6(72m) · exit_ever · closed6 (모두 딜 이후)
  - 셀: cell0(투자사×연도) · cell_cat(+대분류) · cell_stage(+investment_type)
"""
import hashlib
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)  # gates.py / emit_contract.py sit alongside in code/pipeline
from gates import CTX  # noqa: E402

EQ_EXCL = {"grant", "debt_financing", "post_ipo_debt", "post_ipo_equity", "non_equity_assistance"}

people = CTX.people[["uuid", "gender"]]
g_map = people[people["gender"].isin(["male", "female"])].set_index("uuid")["gender"]
rounds = CTX.rounds.dropna(subset=["announced_on", "org_uuid"]).copy()
rounds = rounds[~rounds["investment_type"].isin(EQ_EXCL)]
rounds["dt"] = pd.to_datetime(rounds["announced_on"], errors="coerce")
rounds = rounds.dropna(subset=["dt"])
rounds = rounds[(rounds["dt"] >= "2010-01-01") & (rounds["dt"] <= "2023-10-31")]

jobs = CTX.jobs
fj = jobs[jobs["title"].fillna("").str.lower().str.contains("founder", regex=False)][["person_uuid", "org_uuid"]].dropna()
fj["fg"] = fj["person_uuid"].map(g_map)
fj = fj[fj["fg"].notna()]
org_ff = (fj["fg"] == "female").groupby(fj["org_uuid"]).max()
org_fmaj = (fj["fg"] == "female").groupby(fj["org_uuid"]).mean() >= 0.5
orgs = CTX.orgs
topcat = dict(zip(orgs["uuid"], orgs["category_groups_list"].fillna("NA").str.split(",").str[0].str.strip()))
closed_map = pd.to_datetime(orgs.dropna(subset=["closed_on"]).set_index("uuid")["closed_on"], errors="coerce")

pt = CTX.partners.dropna(subset=["funding_round_uuid", "investor_uuid", "partner_uuid"])
d = pt.merge(rounds[["uuid", "org_uuid", "dt", "country_code", "investment_type"]], left_on="funding_round_uuid", right_on="uuid")
d["pg"] = d["partner_uuid"].map(g_map)
d["ff_raw"] = d["org_uuid"].map(org_ff)
d = d[d["pg"].notna() & d["ff_raw"].notna()].copy()
n_v1_rows = len(d)                                                     # = v1 population (154,123 expected)

# exit dates (first acquisition / first IPO) — computed before the population rule
acq = CTX.acq.dropna(subset=["acquiree_uuid", "acquired_on"]).copy()
acq["adt"] = pd.to_datetime(acq["acquired_on"], errors="coerce")
acq["priced"] = pd.to_numeric(acq["price_usd"], errors="coerce") > 0
ip = CTX.ipos.dropna(subset=["org_uuid", "went_public_on"]).copy()
ip["idt"] = pd.to_datetime(ip["went_public_on"], errors="coerce")
first_ipo = ip.groupby("org_uuid")["idt"].min()
first_acq = acq.groupby("acquiree_uuid")["adt"].min()
first_acqp = acq[acq["priced"]].groupby("acquiree_uuid")["adt"].min()
exit_any = pd.concat([first_acq, first_ipo], axis=1).min(axis=1)
for col, m in (("ipo_dt", first_ipo), ("acqp_dt", first_acqp), ("exit_dt", exit_any), ("cl_dt", closed_map)):
    d[col] = d["org_uuid"].map(m)

# ── population rule (v2): the company must not have exited on or before the round date ─────────────────────────────────────
pre_exit = d["exit_dt"].notna() & (d["exit_dt"] <= d["dt"])
excl = d[pre_exit].copy()
n_excl = int(pre_exit.sum()); n_excl_same_day = int((d["exit_dt"] == d["dt"]).sum())
n_excl_acq = int((excl["exit_dt"] == excl["org_uuid"].map(first_acq)).sum()); n_excl_ipo = int((excl["exit_dt"] == excl["org_uuid"].map(first_ipo)).sum())
# later, distinct exit events after the excluded deal (for the record): a second acquisition or an IPO dated after the round
acq_all = acq.groupby("acquiree_uuid")["adt"].apply(lambda s: sorted(s.dropna().tolist()))
def later_event(row):
    later = [t for t in acq_all.get(row["org_uuid"], []) if t > row["dt"]]
    i = first_ipo.get(row["org_uuid"])
    return bool(later) or (pd.notna(i) and i > row["dt"])
n_excl_with_later_event = int(excl.apply(later_event, axis=1).sum()) if len(excl) else 0
d = d[~pre_exit].copy()

d["fp"] = (d["pg"] == "female").astype(float)
d["ff"] = d["ff_raw"].astype(float)
d["ffm"] = d["org_uuid"].map(org_fmaj).astype(float)
d["year"] = d["dt"].dt.year.astype(str)
d["cat"] = d["org_uuid"].map(topcat).fillna("NA")
d["stage"] = d["investment_type"].fillna("NA")
d["cell0"] = d["investor_uuid"] + "|" + d["year"]
d["cell_cat"] = d["cell0"] + "|" + d["cat"]
d["cell_stage"] = d["cell_cat"] + "|" + d["stage"]
n_per_round = pt.groupby("funding_round_uuid")["partner_uuid"].nunique()
d["solo_attr"] = (d["funding_round_uuid"].map(n_per_round) == 1)

r_org = rounds[["org_uuid", "dt"]].sort_values(["org_uuid", "dt"]).copy()
r_org["next_dt"] = r_org.groupby("org_uuid")["dt"].shift(-1)
next_map = r_org.drop_duplicates(["org_uuid", "dt"]).set_index(["org_uuid", "dt"])["next_dt"]
d["next_dt"] = pd.Series(list(zip(d["org_uuid"], d["dt"]))).map(next_map).to_numpy()
d["fon"] = ((pd.to_datetime(d["next_dt"]) - d["dt"]).dt.days <= 365 * 3).fillna(False).astype(float)
d["ipo6"] = ((d["ipo_dt"] - d["dt"]).dt.days <= 365 * 6).fillna(False).astype(float)
d["acqp6"] = ((d["acqp_dt"] - d["dt"]).dt.days <= 365 * 6).fillna(False).astype(float)
d["exit6"] = ((d["exit_dt"] - d["dt"]).dt.days <= 365 * 6).fillna(False).astype(float)
d["exit_ever"] = d["exit_dt"].notna().astype(float)
d["closed6"] = ((d["cl_dt"] - d["dt"]).dt.days <= 365 * 6).fillna(False).astype(float)
assert ((d["exit_dt"].isna()) | (d["exit_dt"] > d["dt"])).all(), "population rule violated"

keep = ["funding_round_uuid", "investor_uuid", "partner_uuid", "org_uuid", "dt", "year", "country_code", "cat", "stage", "fp", "ff", "ffm", "solo_attr",
        "cell0", "cell_cat", "cell_stage", "fon", "exit6", "ipo6", "acqp6", "exit_ever", "closed6"]
out = d[keep].sort_values(["investor_uuid", "dt", "funding_round_uuid", "partner_uuid"]).reset_index(drop=True)
p = os.environ.get("P001_SAMPLE", "/path/to/sample_v2.parquet")
out.to_parquet(p, index=False)
with open(p, "rb") as f:
    sha = hashlib.sha256(f.read()).hexdigest()[:16]
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR", "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}
naeu = out["country_code"].isin(EU | {"USA", "CAN"})
man = f"""# P001 데이터 매니페스트 v2 (D067; 첫 출구 위험집합)
canonical_sample:
  file: 05_data/sample_v2.parquet
  sha256_16: {sha}
  rows: {len(out)}
  rows_naeu: {int(naeu.sum())}
  unit: partner-attributed deal (funding_round x investor x partner)
  span: {out['dt'].min().date()}..{out['dt'].max().date()}
  frozen_at: 2026-09-10
  builder: 06_code/build_sample_v2.py
  population_rule: company has no acquisition or IPO recorded on or before the round date (same-day exits excluded)
  v1_rows: {n_v1_rows}
  excluded_pre_exit_rows: {n_excl}
  excluded_same_day: {n_excl_same_day}
  excluded_first_exit_is_acquisition: {n_excl_acq}
  excluded_first_exit_is_ipo: {n_excl_ipo}
  excluded_rows_with_a_later_distinct_exit_event: {n_excl_with_later_event}
  base_ff: {out['ff'].mean():.4f}
  base_fp: {out['fp'].mean():.4f}
  n_fp_ff: {int(((out.fp == 1) & (out.ff == 1)).sum())}
  unique_rounds: {out['funding_round_uuid'].nunique()}
  unique_companies: {out['org_uuid'].nunique()}
  unique_investor_firms: {out['investor_uuid'].nunique()}
  unique_partners: {out['partner_uuid'].nunique()}
upstream:
  cores_v1: ../../shared/data/processed/cores_v1/  # MANIFEST.json 참조
  predecessor: 05_data/sample_v1.parquet (sha256_16 5b83f6785878d867; 154,123 rows; kept for provenance)
"""
open(os.environ.get("P001_SAMPLE_MANIFEST", os.environ.get("P001_SAMPLE_MANIFEST", "/path/to/sample_v2_manifest.yaml")), "w", encoding="utf-8").write(man)
print(man)
