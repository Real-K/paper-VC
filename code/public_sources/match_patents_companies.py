# -*- coding: utf-8 -*-
"""match_patents_companies.py — PatentsView 양수인(assignee_dim) ↔ P001 표본 회사(CB organizations) 매칭 → 딜 이전 출원·등록 수.

매칭(1차, 결정적): 회사명 정규화(법인 접미사·구두점 제거) 완전 일치 + 국가 일치(US/비US) + (미국이면) 주 일치 또는 도시 일치. 후보가 하나면 'exact_loc';
 이름만 일치하고 위치 불일치/결측이면 'exact_name_only'(검수 대상); 이름 어근이 여러 양수인에 걸리면 'ambiguous'.
산출: shared/data/processed/patents_v1/company_match.parquet (org_uuid, assignee_id, method), deal_pre_round_patents.parquet (funding_round_uuid, org_uuid, dt, n_app_before, n_grant_before,
 n_app_before_24m, any_patent_before, first_filing_gap_yrs), review_sample_200.csv, match_summary.json.
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
SAMPLE = os.environ.get("P001_SAMPLE", "/path/to/sample_v1.parquet")
CB = os.path.join(ROOT, "..", "data", "crunchbase")
SUF = {"inc", "incorporated", "llc", "l l c", "ltd", "limited", "corp", "corporation", "co", "company", "plc", "gmbh", "ag", "sa", "sas", "bv", "b v", "nv", "oy", "ab", "as", "aps", "kk", "pty", "lp", "llp",
       "the", "holdings", "holding", "group", "technologies", "technology", "tech", "labs", "laboratories", "laboratory", "systems", "solutions", "software", "international", "usa", "us", "america"}


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    toks = [t for t in s.split() if t not in SUF]
    return " ".join(toks)


def main():
    dim = pd.read_parquet(os.path.join(D, "assignee_dim.parquet")); dim["key"] = dim["organization"].map(norm); dim = dim[dim["key"].str.len() >= 3]
    ev = pd.read_parquet(os.path.join(D, "assignee_events.parquet"), columns=["assignee_id", "application_id", "filing_date", "grant_date", "source"])
    s = pd.read_parquet(SAMPLE, columns=["funding_round_uuid", "org_uuid", "dt", "country_code"]).drop_duplicates(["funding_round_uuid", "org_uuid"]); s["dt"] = pd.to_datetime(s["dt"])
    orgs = pd.read_csv(os.path.join(CB, "organizations.csv"), usecols=["uuid", "name", "legal_name", "country_code", "state_code", "city"], low_memory=False)
    orgs = orgs[orgs["uuid"].isin(s["org_uuid"].unique())].copy()
    orgs["key"] = orgs["name"].map(norm); orgs["key_legal"] = orgs["legal_name"].map(lambda x: norm(x) if isinstance(x, str) else "")
    dim["us"] = dim["country"].eq("US"); orgs["us"] = orgs["country_code"].eq("USA")
    dim["city_n"] = dim["city"].fillna("").map(norm); orgs["city_n"] = orgs["city"].fillna("").map(norm)
    kcount = dim.groupby("key")["assignee_id"].nunique()
    rows = []
    idx = {k: g for k, g in dim.groupby("key")}
    for o in orgs.itertuples():
        cands = pd.concat([idx.get(o.key, dim.iloc[0:0]), idx.get(o.key_legal, dim.iloc[0:0]) if o.key_legal and o.key_legal != o.key else dim.iloc[0:0]])
        if cands.empty:
            rows.append((o.uuid, None, "none", 0)); continue
        same_ctry = cands[cands["us"] == o.us]
        loc_ok = same_ctry[(same_ctry["state"].fillna("") == (o.state_code if isinstance(o.state_code, str) else "")) | (same_ctry["city_n"] == o.city_n)] if o.us else same_ctry
        if len(loc_ok) == 1:
            rows.append((o.uuid, loc_ok["assignee_id"].iat[0], "exact_loc", 1))
        elif len(loc_ok) > 1:
            rows.append((o.uuid, loc_ok.sort_values("n_events", ascending=False)["assignee_id"].iat[0], "ambiguous_loc", int(len(loc_ok))))
        elif len(cands) == 1:
            rows.append((o.uuid, cands["assignee_id"].iat[0], "exact_name_only", 1))
        else:
            rows.append((o.uuid, None, "ambiguous_name", int(len(cands))))
    m = pd.DataFrame(rows, columns=["org_uuid", "assignee_id", "match_method", "n_candidates"]).merge(orgs[["uuid", "name", "country_code", "state_code", "city"]], left_on="org_uuid", right_on="uuid", how="left").drop(columns=["uuid"])
    m = m.merge(dim[["assignee_id", "organization", "city", "state", "country", "n_events"]].rename(columns={"city": "pv_city", "state": "pv_state", "country": "pv_country"}), on="assignee_id", how="left")
    m.to_parquet(os.path.join(D, "company_match.parquet"), index=False)
    ok = m[m["match_method"].isin(["exact_loc", "ambiguous_loc"])]
    # 딜 이전 출원·등록 수
    evk = ev[ev["assignee_id"].isin(ok["assignee_id"])].merge(ok[["assignee_id", "org_uuid"]], on="assignee_id")
    evk = evk.sort_values(["org_uuid", "filing_date"])
    byorg = {k: (g["filing_date"].to_numpy(), g["grant_date"].to_numpy(), g["source"].to_numpy()) for k, g in evk.groupby("org_uuid")}
    out = []
    for r in s.itertuples():
        b = byorg.get(r.org_uuid)
        if b is None:
            out.append((r.funding_round_uuid, r.org_uuid, r.dt, 0, 0, 0, 0.0, np.nan, 0.0)); continue
        fd, gd, src = b; t = np.datetime64(r.dt)
        napp = int((fd <= t).sum()); n24 = int(((fd <= t) & (fd > t - np.timedelta64(730, "D"))).sum())
        ngr = int(((gd <= t) & ~pd.isna(gd)).sum())
        gap = float((t - fd.min()) / np.timedelta64(365, "D")) if napp else np.nan
        out.append((r.funding_round_uuid, r.org_uuid, r.dt, napp, ngr, n24, float(napp > 0), gap, 1.0))
    dp = pd.DataFrame(out, columns=["funding_round_uuid", "org_uuid", "dt", "n_app_before", "n_grant_before", "n_app_before_24m", "any_patent_before", "first_filing_gap_yrs", "matched_assignee"])
    dp.to_parquet(os.path.join(D, "deal_pre_round_patents.parquet"), index=False)
    summ = {"built_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "n_sample_companies": int(len(orgs)), "by_method": m["match_method"].value_counts().to_dict(),
            "matched_share_companies": round(float(m["match_method"].isin(["exact_loc", "ambiguous_loc"]).mean()), 4), "matched_share_us_companies": round(float(m.loc[m["country_code"].eq("USA"), "match_method"].isin(["exact_loc", "ambiguous_loc"]).mean()), 4),
            "deals": int(len(dp)), "deals_any_patent_before": round(float(dp["any_patent_before"].mean()), 4), "deals_any_patent_before_us": round(float(dp.loc[dp["org_uuid"].isin(orgs.loc[orgs["us"], "uuid"]), "any_patent_before"].mean()), 4),
            "median_n_app_before_given_any": float(dp.loc[dp["any_patent_before"] == 1, "n_app_before"].median()) if (dp["any_patent_before"] == 1).any() else None}
    json.dump(summ, io.open(os.path.join(D, "match_summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    parts = [m[m["match_method"].eq(k)].sample(min(n, int((m["match_method"] == k).sum())), random_state=20260909) for k, n in (("exact_loc", 100), ("ambiguous_loc", 40), ("exact_name_only", 60))]
    rev = pd.concat(parts)[["name", "country_code", "state_code", "city", "organization", "pv_city", "pv_state", "pv_country", "n_events", "match_method"]].copy(); rev["reviewer_verdict (Y/N/?)"] = ""
    rev.to_csv(os.path.join(D, "review_sample_200.csv"), index=False, encoding="utf-8-sig")
    print(json.dumps(summ, ensure_ascii=False))


if __name__ == "__main__":
    main()
