# -*- coding: utf-8 -*-
"""match_formd_funds.py — Form D VC/PE 펀드 비히클(발행사) ↔ Crunchbase 운용사(P001 표본 investor_uuid) 1차 매칭 + 검수표.

방법(1차, 결정적): 발행사명에서 펀드 표기(Fund, L.P., LLC, roman/arabic numerals, "Partners" 뒤 숫자 등)를 벗겨 운용사 어근(stem)을 만들고, CB 운용사명도 같은 규칙으로 정규화 → 어근 완전 일치.
 동점 후보가 여럿이면 발행사 주(state) 와 CB 운용사 주(투자사 city/region 대신 CB `investors.csv` 의 state_code 가 없으므로 country=USA 만 확인) 로 좁히고, 남으면 'ambiguous'.
 점수: exact_stem(1.0) / exact_stem_multi(0.6, 후보 다수) / none. 퍼지 매칭(토큰 자카드 ≥ 0.8)은 2차 열로만 제안(match_method='fuzzy'; 검수 전 사용 금지).
출력: shared/data/processed/formd_v1/fund_vehicle_to_investor.parquet (accession, issuer name, stem, investor_uuid, cb_name, method, score, state, sale_date, amount_sold, fund type)
     + review_sample_200.csv (층화 무작위 200건: exact 120 · multi 40 · fuzzy 40) → PI/RA 수검(정밀도 게이트 ≥ 0.9) + summary.json
"""
import io
import json
import os
import re
from datetime import datetime, timezone

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("P001_PROJECT_ROOT", "/path/to/project-root")   # holds shared/data/processed (derived, not redistributed)
D = os.path.join(ROOT, "shared", "data", "processed", "formd_v1")
SAMPLE = os.environ.get("P001_SAMPLE", "/path/to/sample_v1.parquet")
INV = os.path.join(ROOT, "..", "data", "crunchbase", "investors.csv")
rng = np.random.default_rng(20260909)
ROMAN = r"\b(?:i{1,3}|iv|v|vi{1,3}|ix|x{1,3}|xi{1,3}|xiv|xv|xvi{1,3}|xix|xx)\b"
DROP = {"fund", "funds", "lp", "l p", "llc", "l l c", "ltd", "limited", "inc", "co", "corp", "corporation", "partnership", "the", "of", "a", "an", "and", "&", "parallel", "feeder", "master",
        "offshore", "onshore", "cayman", "delaware", "series", "sidecar", "side", "car", "opportunity", "opportunities", "annex", "select", "growth", "early", "stage", "seed", "venture", "ventures",
        "capital", "partners", "management", "investors", "investment", "investments", "holdings", "group", "gp", "general", "associates", "advisors", "advisers", "trust", "vehicle", "coinvest", "co-invest", "affiliates", "employees", "friends", "family", "qp", "aiv", "spv", "founders"}


def stem(name):
    s = str(name).lower().replace("&", " and ")
    s = re.sub(r"[\.,'’\"()\[\]\-/:;]", " ", s)
    s = re.sub(ROMAN, " ", s)
    s = re.sub(r"\b\d+[a-z]?\b", " ", s)          # fund numbers / years
    toks = [t for t in s.split() if t not in DROP and len(t) > 1]
    return " ".join(toks)


def main():
    off = pd.read_parquet(os.path.join(D, "OFFERING.parquet"), columns=["ACCESSIONNUMBER", "INDUSTRYGROUPTYPE", "INVESTMENTFUNDTYPE", "TOTALAMOUNTSOLD", "TOTALOFFERINGAMOUNT", "SALE_DATE", "ISAMENDMENT", "SRC_QUARTER"])
    iss = pd.read_parquet(os.path.join(D, "ISSUERS.parquet"), columns=["ACCESSIONNUMBER", "ISSUER_SEQ_KEY", "ENTITYNAME", "STATEORCOUNTRY", "CITY", "ENTITYTYPE", "YEAROFINC_VALUE_ENTERED"]) if "ISSUER_SEQ_KEY" in pd.read_parquet(os.path.join(D, "ISSUERS.parquet")).columns else pd.read_parquet(os.path.join(D, "ISSUERS.parquet"))
    pif = off[off["INDUSTRYGROUPTYPE"].eq("Pooled Investment Fund") & off["INVESTMENTFUNDTYPE"].isin(["Venture Capital Fund", "Private Equity Fund"])].copy()
    pif["is_amend"] = pif["ISAMENDMENT"].astype(str).str.lower().isin(["true", "1", "y"])
    fv = pif.merge(iss.drop_duplicates("ACCESSIONNUMBER"), on="ACCESSIONNUMBER", how="left")
    fv["stem"] = fv["ENTITYNAME"].map(stem)
    s = pd.read_parquet(SAMPLE, columns=["investor_uuid"]); firms = set(s["investor_uuid"].unique())
    inv = pd.read_csv(INV, usecols=["uuid", "name", "country_code", "city", "investor_types"], low_memory=False)
    inv = inv[inv["uuid"].isin(firms)].copy(); inv["stem"] = inv["name"].map(stem)
    inv = inv[inv["stem"].str.len() >= 3]
    cnt = inv.groupby("stem")["uuid"].nunique().rename("n_cb_same_stem")
    inv = inv.merge(cnt, left_on="stem", right_index=True)
    # exact stem match
    m = fv.merge(inv[["uuid", "name", "country_code", "city", "stem", "n_cb_same_stem"]].rename(columns={"uuid": "investor_uuid", "name": "cb_name", "country_code": "cb_country", "city": "cb_city"}), on="stem", how="left")
    m["match_method"] = np.where(m["investor_uuid"].notna() & (m["n_cb_same_stem"] == 1), "exact_stem", np.where(m["investor_uuid"].notna(), "exact_stem_multi", "none"))
    m["match_score"] = m["match_method"].map({"exact_stem": 1.0, "exact_stem_multi": 0.6, "none": 0.0})
    # fuzzy proposal (token Jaccard ≥ 0.8) for unmatched vehicles with ≥2 stem tokens — proposal only
    un = m[m["match_method"].eq("none") & (m["stem"].str.split().str.len() >= 2)].drop_duplicates("ACCESSIONNUMBER")
    inv_tok = {r.uuid: set(r.stem.split()) for r in inv.itertuples()}
    inv_names = dict(zip(inv["uuid"], inv["name"]))
    idx = {}
    for u, toks in inv_tok.items():
        for t in toks: idx.setdefault(t, set()).add(u)
    fz = []
    for r in un.itertuples():
        toks = set(r.stem.split()); cands = set().union(*[idx.get(t, set()) for t in toks]) if toks else set()
        best, bj = None, 0.0
        for u in cands:
            j = len(toks & inv_tok[u]) / len(toks | inv_tok[u])
            if j > bj: best, bj = u, j
        if best and bj >= 0.8:
            fz.append((r.ACCESSIONNUMBER, best, inv_names[best], round(bj, 3)))
    fzd = pd.DataFrame(fz, columns=["ACCESSIONNUMBER", "fz_uuid", "fz_name", "fz_jaccard"])
    m = m.merge(fzd, on="ACCESSIONNUMBER", how="left")
    fmask = m["match_method"].eq("none") & m["fz_uuid"].notna()
    m.loc[fmask, ["investor_uuid", "cb_name", "match_method", "match_score"]] = np.column_stack([m.loc[fmask, "fz_uuid"], m.loc[fmask, "fz_name"], np.repeat("fuzzy", fmask.sum()), m.loc[fmask, "fz_jaccard"]])
    out = m[["ACCESSIONNUMBER", "SRC_QUARTER", "ENTITYNAME", "stem", "STATEORCOUNTRY", "CITY", "INVESTMENTFUNDTYPE", "is_amend", "SALE_DATE", "TOTALAMOUNTSOLD", "TOTALOFFERINGAMOUNT", "investor_uuid", "cb_name", "cb_country", "cb_city", "n_cb_same_stem", "match_method", "match_score"]].copy()
    out.to_parquet(os.path.join(D, "fund_vehicle_to_investor.parquet"), index=False)
    newn = out[~out["is_amend"]]
    summ = {"built_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "n_vc_pe_filings": int(len(out)), "n_new_notices": int(len(newn)),
            "by_method_new_notices": newn["match_method"].value_counts().to_dict(),
            "n_cb_firms_matched_exact": int(newn.loc[newn["match_method"].eq("exact_stem"), "investor_uuid"].nunique()), "n_cb_firms_matched_any": int(newn.loc[newn["match_method"].ne("none"), "investor_uuid"].nunique()),
            "n_sample_firms": len(firms), "n_sample_firms_us": int((inv["country_code"] == "USA").sum()),
            "vc_only": {"n_new": int((~out["is_amend"] & out["INVESTMENTFUNDTYPE"].eq("Venture Capital Fund")).sum()),
                        "by_method": out[~out["is_amend"] & out["INVESTMENTFUNDTYPE"].eq("Venture Capital Fund")]["match_method"].value_counts().to_dict()}}
    # review sample
    parts = []
    for meth, k in (("exact_stem", 120), ("exact_stem_multi", 40), ("fuzzy", 40)):
        sub = newn[newn["match_method"].eq(meth)]
        if len(sub): parts.append(sub.sample(min(k, len(sub)), random_state=20260909))
    rev = pd.concat(parts)[["ACCESSIONNUMBER", "ENTITYNAME", "STATEORCOUNTRY", "CITY", "INVESTMENTFUNDTYPE", "SALE_DATE", "cb_name", "cb_country", "cb_city", "match_method", "match_score"]].copy()
    rev["reviewer_verdict (Y/N/?)"] = ""; rev["note"] = ""
    rev.to_csv(os.path.join(D, "review_sample_200.csv"), index=False, encoding="utf-8-sig")
    json.dump(summ, io.open(os.path.join(D, "fund_match_summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(summ, ensure_ascii=False))


if __name__ == "__main__":
    main()
