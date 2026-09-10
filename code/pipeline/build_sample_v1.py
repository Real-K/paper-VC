# -*- coding: utf-8 -*-
"""P001 정본 표본 v1 동결 — 파트너 귀속 딜 수준 분석 표본 (I-73~I-80 의 공통 구축을 단일 산출물로)

입력: shared/data/processed/cores_v1/*.parquet (MANIFEST.json 참조)
출력: papers/P001_gender_screening/05_data/sample_v1.parquet + 콘솔에 sha256_16·행수·기저율
      → 값은 05_data/data_manifest.yaml 과 루트 CLAUDE.md 에 수기 고정

구축 규칙 (하네스 I-73/I-78/I-80 과 동일 — 변경 시 새 버전 폴더, 조용한 덮어쓰기 금지):
  - 라운드: announced_on 2010-01-01~2023-10-31, 그랜트·부채·post-IPO·non-equity 제외
  - 단위: investment_partners 의 (round × investor × partner) 귀속 행
  - fp: 파트너 성별 female (people.gender ∈ {male,female} 만 판정)
  - ff: founder 직함 jobs × gender — 여성 창업자 ≥1 (판정 가능 = 성별 관측 창업자 ≥1)
  - 결과: fon(후속 36m) · exit6/ipo6/acqp6(72m) · exit_ever · closed6
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
fj = jobs[jobs["title"].fillna("").str.lower().str.contains("founder", regex=False)][
    ["person_uuid", "org_uuid"]].dropna()
fj["fg"] = fj["person_uuid"].map(g_map)
fj = fj[fj["fg"].notna()]
org_ff = (fj["fg"] == "female").groupby(fj["org_uuid"]).max()
org_fmaj = (fj["fg"] == "female").groupby(fj["org_uuid"]).mean() >= 0.5
orgs = CTX.orgs
topcat = dict(zip(orgs["uuid"], orgs["category_groups_list"].fillna("NA").str.split(",").str[0].str.strip()))
closed_map = pd.to_datetime(orgs.dropna(subset=["closed_on"]).set_index("uuid")["closed_on"],
                            errors="coerce")

pt = CTX.partners.dropna(subset=["funding_round_uuid", "investor_uuid", "partner_uuid"])
d = pt.merge(rounds[["uuid", "org_uuid", "dt", "country_code", "investment_type"]],
             left_on="funding_round_uuid", right_on="uuid")
d["pg"] = d["partner_uuid"].map(g_map)
d["ff_raw"] = d["org_uuid"].map(org_ff)
d = d[d["pg"].notna() & d["ff_raw"].notna()].copy()
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

acq = CTX.acq.dropna(subset=["acquiree_uuid", "acquired_on"]).copy()
acq["adt"] = pd.to_datetime(acq["acquired_on"], errors="coerce")
acq["priced"] = pd.to_numeric(acq["price_usd"], errors="coerce") > 0
ip = CTX.ipos.dropna(subset=["org_uuid", "went_public_on"]).copy()
ip["idt"] = pd.to_datetime(ip["went_public_on"], errors="coerce")
first_ipo = ip.groupby("org_uuid")["idt"].min()
first_acq = acq.groupby("acquiree_uuid")["adt"].min()
first_acqp = acq[acq["priced"]].groupby("acquiree_uuid")["adt"].min()
exit_any = pd.concat([first_acq, first_ipo], axis=1).min(axis=1)
for col, m in (("ipo_dt", first_ipo), ("acqp_dt", first_acqp), ("exit_dt", exit_any),
               ("cl_dt", closed_map)):
    d[col] = d["org_uuid"].map(m)
d["ipo6"] = ((d["ipo_dt"] - d["dt"]).dt.days <= 365 * 6).fillna(False).astype(float)
d["acqp6"] = ((d["acqp_dt"] - d["dt"]).dt.days <= 365 * 6).fillna(False).astype(float)
d["exit6"] = ((d["exit_dt"] - d["dt"]).dt.days <= 365 * 6).fillna(False).astype(float)
d["exit_ever"] = d["exit_dt"].notna().astype(float)
d["closed6"] = ((d["cl_dt"] - d["dt"]).dt.days <= 365 * 6).fillna(False).astype(float)

keep = ["funding_round_uuid", "investor_uuid", "partner_uuid", "org_uuid", "dt", "year",
        "country_code", "cat", "stage", "fp", "ff", "ffm", "solo_attr",
        "cell0", "cell_cat", "cell_stage", "fon", "exit6", "ipo6", "acqp6", "exit_ever", "closed6"]
out = d[keep].sort_values(["investor_uuid", "dt", "funding_round_uuid", "partner_uuid"]).reset_index(drop=True)
p = os.environ.get("P001_SAMPLE_V1", "/path/to/sample_v1.parquet")
out.to_parquet(p, index=False)
with open(p, "rb") as f:
    sha = hashlib.sha256(f.read()).hexdigest()[:16]
print(f"rows={len(out)}  sha256_16={sha}")
print(f"base_ff={out['ff'].mean():.4f}  base_fp={out['fp'].mean():.4f}  "
      f"n_fp_ff={int(((out.fp==1)&(out.ff==1)).sum())}")
print(f"span={out['dt'].min().date()}..{out['dt'].max().date()}")
