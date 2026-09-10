# -*- coding: utf-8 -*-
"""p001_v6_common — v6 설계 제안(P1·P3·P4·P5·P8; 09_review/R3_recheck/design_proposals.md) 공용 구성.

라운드 시퀀스(지분형만, build_sample_v1 의 EQ_EXCL 과 동일) · 투자자 행(CTX.inv) · 귀속 파트너 성별(CTX.partners × people) ·
출구 일자 · 기업 사전 공변량(orgs·jobs·degrees) · 반기 지수. 표본 모집단은 sample_v1 의 기업(창업자 성별 관측 가능, NAEU 라운드).
정본 표본·상수는 p001_rescue_common 에서 가져온다(재타이핑 금지 — 교훈 46).
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from p001_rescue_common import (COMMON_SHA as RESCUE_SHA, CTX, CUT, END, END_FON, NAEU, boot, emit, fit, log, qci,  # noqa: F401
                                sha16)

V6_SHA = sha16(os.path.abspath(__file__))
EQ_EXCL = {"grant", "debt_financing", "post_ipo_debt", "post_ipo_equity", "non_equity_assistance"}
EARLY = {"pre_seed", "seed", "angel", "series_a", "convertible_note"}
LATE = {"series_b", "series_c", "series_d", "series_e", "series_f", "series_g", "series_h", "series_i", "series_j", "private_equity"}


def load_sample():
    d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v2.parquet"))
    d["dt"] = pd.to_datetime(d["dt"])
    return d[d["country_code"].isin(NAEU)].copy()


def org_maps(d):
    g = d.groupby("org_uuid")
    return {"ff": g["ff"].first().to_dict(), "ffm": g["ffm"].first().to_dict(), "cat": g["cat"].first().to_dict()}


def _first_exit():
    """회사별 첫 인수·IPO 일자 (D067 모집단 규칙용)."""
    acq = CTX.acq.dropna(subset=["acquiree_uuid", "acquired_on"]); ip = CTX.ipos.dropna(subset=["org_uuid", "went_public_on"])
    fa = pd.to_datetime(acq["acquired_on"], errors="coerce").groupby(acq["acquiree_uuid"]).min(); fi = pd.to_datetime(ip["went_public_on"], errors="coerce").groupby(ip["org_uuid"]).min()
    return pd.concat([fa, fi], axis=1).min(axis=1)


def equity_rounds(org_set):
    """표본 기업의 지분형 라운드 시퀀스: seq · prev/next uuid·일자."""
    r = CTX.rounds
    r = r[r["org_uuid"].isin(org_set) & ~r["investment_type"].isin(EQ_EXCL)].dropna(subset=["uuid", "announced_on"]).copy()
    r["rdt"] = pd.to_datetime(r["announced_on"], errors="coerce")
    r = r.dropna(subset=["rdt"])
    _ex = r["org_uuid"].map(_first_exit()); r = r[~(_ex.notna() & (_ex <= r["rdt"]))]   # D067 population rule (sample_v2): no exit on/before the round
    r = r.sort_values(["org_uuid", "rdt", "uuid"]).reset_index(drop=True)
    r["seq"] = r.groupby("org_uuid").cumcount()
    r["next_uuid"] = r.groupby("org_uuid")["uuid"].shift(-1)
    r["next_dt"] = r.groupby("org_uuid")["rdt"].shift(-1)
    r["next_type"] = r.groupby("org_uuid")["investment_type"].shift(-1)
    r["prev_uuid"] = r.groupby("org_uuid")["uuid"].shift(1)
    r["amt"] = pd.to_numeric(r["raised_amount_usd"], errors="coerce")
    return r


def investor_rows(round_uuids):
    inv = CTX.inv.dropna(subset=["funding_round_uuid", "investor_uuid"])
    return inv[inv["funding_round_uuid"].isin(set(round_uuids))].copy()


def partner_gender_rows(round_uuids=None):
    pt = CTX.partners.dropna(subset=["funding_round_uuid", "investor_uuid", "partner_uuid"]).copy()
    if round_uuids is not None:
        pt = pt[pt["funding_round_uuid"].isin(set(round_uuids))]
    g = dict(zip(CTX.people["uuid"], CTX.people["gender"]))
    pt["pg"] = pt["partner_uuid"].map(g)
    pt = pt[pt["pg"].isin(["female", "male"])].copy()
    pt["fp"] = (pt["pg"] == "female").astype(float)
    return pt


def exit_dates():
    acq = CTX.acq.dropna(subset=["acquiree_uuid", "acquired_on"]).copy()
    acq["adt"] = pd.to_datetime(acq["acquired_on"], errors="coerce")
    ip = CTX.ipos.dropna(subset=["org_uuid", "went_public_on"]).copy()
    ip["idt"] = pd.to_datetime(ip["went_public_on"], errors="coerce")
    return pd.concat([acq.groupby("acquiree_uuid")["adt"].min(), ip.groupby("org_uuid")["idt"].min()], axis=1).min(axis=1)


def investor_experience(inv_all=None):
    """투자자별 라운드 누적 수(해당 라운드 이전) — 경험 통제."""
    inv = CTX.inv.dropna(subset=["funding_round_uuid", "investor_uuid"])[["funding_round_uuid", "investor_uuid"]] if inv_all is None else inv_all
    r = CTX.rounds[["uuid", "announced_on"]].dropna()
    m = inv.merge(r, left_on="funding_round_uuid", right_on="uuid").drop(columns="uuid")
    m["rdt"] = pd.to_datetime(m["announced_on"], errors="coerce")
    m = m.dropna(subset=["rdt"]).sort_values(["investor_uuid", "rdt"])
    m["exp_before"] = m.groupby("investor_uuid").cumcount()
    return m[["funding_round_uuid", "investor_uuid", "exp_before"]]


def founders_by_org():
    """jobs 의 founder 직함 → 기업별 창업자 수·여성 창업자 수·학위 보유 비중·연쇄창업 비중."""
    J = CTX.jobs.dropna(subset=["person_uuid", "org_uuid"])
    F = J[J["title"].fillna("").str.lower().str.contains("founder", regex=False)][["person_uuid", "org_uuid"]].drop_duplicates()
    g = dict(zip(CTX.people["uuid"], CTX.people["gender"]))
    F["female"] = (F["person_uuid"].map(g) == "female").astype(float)
    deg = set(CTX.degrees.dropna(subset=["person_uuid"])["person_uuid"])
    F["has_degree"] = F["person_uuid"].isin(deg).astype(float)
    n_orgs = F.groupby("person_uuid")["org_uuid"].nunique()
    F["serial"] = (F["person_uuid"].map(n_orgs) > 1).astype(float)
    return F.groupby("org_uuid").agg(n_founders=("person_uuid", "size"), n_female_founders=("female", "sum"),
                                     founder_degree_share=("has_degree", "mean"), serial_share=("serial", "mean"))


EMP_BAND = {"1-10": 1, "11-50": 2, "51-100": 3, "101-250": 4, "251-500": 5, "501-1000": 6, "1001-5000": 7, "5001-10000": 8, "10000+": 9}


def half_index(dt):
    return dt.dt.year * 2 + (dt.dt.month > 6).astype(int)


def jobs_spells():
    J = CTX.jobs.dropna(subset=["person_uuid", "org_uuid"]).copy()
    J["sdt"] = pd.to_datetime(J["started_on"], errors="coerce")
    J["edt"] = pd.to_datetime(J["ended_on"], errors="coerce")
    return J


def demean_within(df, cols, key):
    out = df.copy()
    for c in cols:
        out[c] = out[c] - out.groupby(key)[c].transform("mean")
    return out
