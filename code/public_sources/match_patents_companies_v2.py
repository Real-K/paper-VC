# -*- coding: utf-8 -*-
"""match_patents_companies_v2.py — PI 검수(200건, 2026-09-09) 반영: PatentsView 양수인 ↔ CB 표본 회사 매칭 2차 규칙.

검수(review_sample_200_reviewed_v1.csv): exact_loc 0.950(n=100; 미국 0.973·비미국 0.885 — 비미국 오탐은 국가 미대조: GBR↔DE, CAN↔CH, TUR↔결측) · ambiguous_loc 0.675(도시 일치 18/18=1.000; 단일 토큰 0.50) · exact_name_only 0.433(제외).
v2 규칙:
  T1_use  : 이름 정규화 완전 일치 후보가 유일하고, [미국] 주 일치 / [비미국] ISO 국가 일치 & (도시 일치 or 주 일치 or PV 위치 결측 아님·도시 결측)  → 실제로는 국가 일치 필수 + (도시 or 주) 일치 요구
  T1b_use : 후보 다수인데 국가 일치 & 도시 일치 후보가 정확히 하나
  T2_hold : 후보 유일·국가 일치·위치 불일치(도시·주 모두 다름) / 후보 다수·도시 불일치·이름 토큰 ≥2
  T3_excl : 이름만 일치(위치 정보 없음), 국가 불일치, 단일 토큰 다중 후보
산출: company_match_v2.parquet, deal_pre_round_patents_v2.parquet (T1∪T1b), match_summary_v2.json, review_confirm_100.csv(T1∪T1b 무작위 100, 선택)
"""
import io
import json
import os
import re
import unicodedata
from datetime import datetime, timezone

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("P001_PROJECT_ROOT", "/path/to/project-root")   # holds shared/data/processed (derived, not redistributed)
D = os.path.join(ROOT, "shared", "data", "processed", "patents_v1")
SAMPLE = os.environ.get("P001_SAMPLE_V1", "/path/to/sample_v1.parquet")
CB = os.path.join(ROOT, "..", "data", "crunchbase")
A3 = {"USA": "US", "GBR": "GB", "CAN": "CA", "DEU": "DE", "FRA": "FR", "ISR": "IL", "CHE": "CH", "NLD": "NL", "SWE": "SE", "ESP": "ES", "ITA": "IT", "IRL": "IE", "BEL": "BE", "DNK": "DK", "FIN": "FI", "NOR": "NO",
      "AUT": "AT", "PRT": "PT", "POL": "PL", "AUS": "AU", "IND": "IN", "CHN": "CN", "JPN": "JP", "KOR": "KR", "SGP": "SG", "BRA": "BR", "MEX": "MX", "TUR": "TR", "ARE": "AE", "NZL": "NZ", "RUS": "RU", "TWN": "TW",
      "HKG": "HK", "ZAF": "ZA", "ARG": "AR", "CHL": "CL", "CZE": "CZ", "EST": "EE", "LTU": "LT", "LVA": "LV", "HUN": "HU", "ROU": "RO", "GRC": "GR", "LUX": "LU", "UKR": "UA", "IDN": "ID", "MYS": "MY", "THA": "TH",
      "VNM": "VN", "PHL": "PH", "NGA": "NG", "KEN": "KE", "EGY": "EG", "SAU": "SA", "ISL": "IS", "SVK": "SK", "SVN": "SI", "HRV": "HR", "BGR": "BG", "SRB": "RS", "PAK": "PK", "BGD": "BD", "LKA": "LK", "COL": "CO", "PER": "PE",
      "CYP": "CY", "MLT": "MT", "LIE": "LI", "MCO": "MC", "QAT": "QA", "BHR": "BH", "KWT": "KW", "JOR": "JO", "LBN": "LB", "MAR": "MA", "TUN": "TN", "GHA": "GH", "URY": "UY", "CRI": "CR", "PAN": "PA", "ECU": "EC", "BOL": "BO",
      "VEN": "VE", "DOM": "DO", "GTM": "GT", "KAZ": "KZ", "GEO": "GE", "ARM": "AM", "AZE": "AZ", "BLR": "BY", "MDA": "MD", "MKD": "MK", "BIH": "BA", "ALB": "AL", "MMR": "MM", "KHM": "KH", "NPL": "NP", "MNG": "MN", "UZB": "UZ"}
SUF = {"inc", "incorporated", "llc", "l l c", "ltd", "limited", "corp", "corporation", "co", "company", "plc", "gmbh", "ag", "sa", "sas", "bv", "b v", "nv", "oy", "ab", "as", "aps", "kk", "pty", "lp", "llp",
       "the", "holdings", "holding", "group", "technologies", "technology", "tech", "labs", "laboratories", "laboratory", "systems", "solutions", "software", "international", "usa", "us", "america"}


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower().replace("&", " and ")
    return " ".join(t for t in re.sub(r"[^a-z0-9 ]", " ", s).split() if t not in SUF)


def main():
    dim = pd.read_parquet(os.path.join(D, "assignee_dim.parquet")); dim["key"] = dim["organization"].map(norm); dim = dim[dim["key"].str.len() >= 3].copy()
    dim["city_n"] = dim["city"].fillna("").map(norm); dim["state"] = dim["state"].fillna(""); dim["country"] = dim["country"].fillna("")
    ev = pd.read_parquet(os.path.join(D, "assignee_events.parquet"), columns=["assignee_id", "application_id", "filing_date", "grant_date", "source"])
    s = pd.read_parquet(SAMPLE, columns=["funding_round_uuid", "org_uuid", "dt"]).drop_duplicates(["funding_round_uuid", "org_uuid"]); s["dt"] = pd.to_datetime(s["dt"])
    orgs = pd.read_csv(os.path.join(CB, "organizations.csv"), usecols=["uuid", "name", "legal_name", "country_code", "state_code", "city"], low_memory=False)
    orgs = orgs[orgs["uuid"].isin(s["org_uuid"].unique())].copy()
    orgs["key"] = orgs["name"].map(norm); orgs["key_legal"] = orgs["legal_name"].map(lambda x: norm(x) if isinstance(x, str) else "")
    orgs["c2"] = orgs["country_code"].map(A3).fillna(""); orgs["city_n"] = orgs["city"].fillna("").map(norm); orgs["state_code"] = orgs["state_code"].fillna("")
    idx = {k: g for k, g in dim.groupby("key")}
    rows = []
    for o in orgs.itertuples():
        cands = pd.concat([idx.get(o.key, dim.iloc[0:0]), idx.get(o.key_legal, dim.iloc[0:0]) if (o.key_legal and o.key_legal != o.key) else dim.iloc[0:0]]).drop_duplicates("assignee_id")
        if cands.empty:
            rows.append((o.uuid, None, "none", 0, "no name match")); continue
        ntok = len(o.key.split())
        cc = cands[cands["country"] == o.c2] if o.c2 else cands.iloc[0:0]
        city_ok = cc[(cc["city_n"] == o.city_n) & (o.city_n != "")]
        state_ok = cc[(cc["state"] == o.state_code) & (o.state_code != "")] if o.c2 == "US" else cc.iloc[0:0]
        loc_ok = pd.concat([city_ok, state_ok]).drop_duplicates("assignee_id")
        if len(cands) == 1:
            c = cands.iloc[0]
            if len(loc_ok) == 1: rows.append((o.uuid, c["assignee_id"], "T1_use", 1, "unique name; country+city/state agree"))
            elif len(cc) == 1: rows.append((o.uuid, c["assignee_id"], "T2_hold", 1, "unique name; country agrees; location differs or missing"))
            elif not o.c2 or c["country"] == "": rows.append((o.uuid, c["assignee_id"], "T3_excl", 1, "country unknown"))
            else: rows.append((o.uuid, c["assignee_id"], "T3_excl", 1, "country mismatch"))
        else:
            if len(city_ok) == 1: rows.append((o.uuid, city_ok["assignee_id"].iat[0], "T1b_use", int(len(cands)), "multiple names; unique country+city"))
            elif len(loc_ok) == 1: rows.append((o.uuid, loc_ok["assignee_id"].iat[0], "T2_hold", int(len(cands)), "multiple names; unique country+state only"))
            elif len(loc_ok) > 1: rows.append((o.uuid, loc_ok.sort_values("n_events", ascending=False)["assignee_id"].iat[0], "T2_hold", int(len(cands)), "multiple names; several location-consistent"))
            elif len(cc) >= 1 and ntok >= 2: rows.append((o.uuid, cc.sort_values("n_events", ascending=False)["assignee_id"].iat[0], "T2_hold", int(len(cands)), "multiple names; country only; multi-token"))
            else: rows.append((o.uuid, None, "T3_excl", int(len(cands)), "multiple names; no location agreement"))
    m = pd.DataFrame(rows, columns=["org_uuid", "assignee_id", "tier", "n_candidates", "reason"]).merge(orgs[["uuid", "name", "country_code", "state_code", "city"]], left_on="org_uuid", right_on="uuid", how="left").drop(columns=["uuid"])
    m = m.merge(dim[["assignee_id", "organization", "city", "state", "country", "n_events"]].rename(columns={"city": "pv_city", "state": "pv_state", "country": "pv_country"}), on="assignee_id", how="left")
    m.to_parquet(os.path.join(D, "company_match_v2.parquet"), index=False)
    use = m[m["tier"].isin(["T1_use", "T1b_use"])]
    evk = ev[ev["assignee_id"].isin(use["assignee_id"])].merge(use[["assignee_id", "org_uuid"]], on="assignee_id").sort_values(["org_uuid", "filing_date"])
    byorg = {k: (g["filing_date"].to_numpy(), g["grant_date"].to_numpy()) for k, g in evk.groupby("org_uuid")}
    out = []
    for r in s.itertuples():
        b = byorg.get(r.org_uuid)
        if b is None:
            out.append((r.funding_round_uuid, r.org_uuid, r.dt, 0, 0, 0, 0.0, np.nan, float(r.org_uuid in set(use["org_uuid"])))); continue
        fd, gd = b; t = np.datetime64(r.dt)
        napp = int((fd <= t).sum()); n24 = int(((fd <= t) & (fd > t - np.timedelta64(730, "D"))).sum()); ngr = int(((gd <= t) & ~pd.isna(gd)).sum())
        out.append((r.funding_round_uuid, r.org_uuid, r.dt, napp, ngr, n24, float(napp > 0), float((t - fd.min()) / np.timedelta64(365, "D")) if napp else np.nan, 1.0))
    dp = pd.DataFrame(out, columns=["funding_round_uuid", "org_uuid", "dt", "n_app_before", "n_grant_before", "n_app_before_24m", "any_patent_before", "first_filing_gap_yrs", "matched_assignee"])
    dp.to_parquet(os.path.join(D, "deal_pre_round_patents_v2.parquet"), index=False)
    us_orgs = set(orgs.loc[orgs["country_code"].eq("USA"), "uuid"])
    summ = {"built_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "review_basis": "review_sample_200_reviewed_v1.csv (PI): exact_loc 0.950 (US 0.973, non-US 0.885 due to unchecked country), ambiguous_loc 0.675 (city-agree 18/18), name_only 0.433",
            "n_sample_companies": int(len(orgs)), "by_tier": m["tier"].value_counts().to_dict(), "use_share_companies": round(float(m["tier"].isin(["T1_use", "T1b_use"]).mean()), 4),
            "use_share_us_companies": round(float(m.loc[m["country_code"].eq("USA"), "tier"].isin(["T1_use", "T1b_use"]).mean()), 4),
            "deals": int(len(dp)), "deals_matched_company": round(float(dp["matched_assignee"].mean()), 4), "deals_any_patent_before": round(float(dp["any_patent_before"].mean()), 4),
            "deals_any_patent_before_us": round(float(dp.loc[dp["org_uuid"].isin(us_orgs), "any_patent_before"].mean()), 4),
            "median_n_app_before_given_any": float(dp.loc[dp["any_patent_before"] == 1, "n_app_before"].median()) if (dp["any_patent_before"] == 1).any() else None}
    json.dump(summ, io.open(os.path.join(D, "match_summary_v2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    rev = use.sample(min(100, len(use)), random_state=20260910)[["name", "country_code", "state_code", "city", "organization", "pv_city", "pv_state", "pv_country", "n_events", "tier", "reason"]].copy(); rev["reviewer_verdict (Y/N/?)"] = ""
    rev.to_csv(os.path.join(D, "review_confirm_100.csv"), index=False, encoding="utf-8-sig")
    print(json.dumps(summ, ensure_ascii=False))


if __name__ == "__main__":
    main()
