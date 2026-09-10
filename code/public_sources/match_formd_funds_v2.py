# -*- coding: utf-8 -*-
"""match_formd_funds_v2.py — PI 검수(200건, 2026-09-09) 반영: Form D 펀드 비히클 ↔ CB 운용사 매칭의 2차 규칙(티어).

검수 결과(review_sample_200_reviewed_v1.csv): exact_stem 정밀도 0.833 · exact_stem_multi 0.325 · fuzzy 0.825(국가 미기록으로 재평가 불가).
오탐 패턴: (a) 흔한 한 단어 어근(Monitor·Jupiter·Eagle·Barn·Green·CLP·DVC·EVP·ECP) (b) 국가 불일치(미국 펀드 ↔ 인도·홍콩·브라질·두바이·영국·호주 운용사).
검수 표본 위에서 규칙 B = [발행사 미국 주] & [CB 운용사 USA] & [어근 토큰 ≥2 또는 단일 토큰 길이 ≥6] & [주 일치 or 도시 일치 or CB 주 결측] → 정밀도 0.973 (n=75).
티어: T1_use(규칙 B) / T2_hold_loc(국가 OK·어근 OK·위치 불일치) / T3_hold_generic(어근 약함) / T4_country_mismatch / T5_nonus_unverified(발행사 비미국: 국가코드 매핑 전) / T6_multi / T7_fuzzy / none.
사용 규칙: 하네스 투입은 T1 만. 출력: fund_vehicle_to_investor_v2.parquet, fund_match_summary_v2.json, review_confirm_100.csv(T1 무작위 100 — 확인용, 게이트는 이미 충족).
"""
import io
import json
import os
from datetime import datetime, timezone

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("P001_PROJECT_ROOT", "/path/to/project-root")   # holds shared/data/processed (derived, not redistributed)
D = os.path.join(ROOT, "shared", "data", "processed", "formd_v1")
CB = os.path.join(ROOT, "..", "data", "crunchbase")
US = set("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC PR".split())

m = pd.read_parquet(os.path.join(D, "fund_vehicle_to_investor.parquet"))
orgs = pd.read_csv(os.path.join(CB, "organizations.csv"), usecols=["uuid", "state_code", "city"], low_memory=False).set_index("uuid")
m["cb_state"] = m["investor_uuid"].map(orgs["state_code"]); m["cb_city_org"] = m["investor_uuid"].map(orgs["city"])
m["issuer_us"] = m["STATEORCOUNTRY"].isin(US)
m["cb_us"] = m["cb_country"].eq("USA")
m["ntok"] = m["stem"].fillna("").str.split().str.len(); m["tok_len"] = m["stem"].fillna("").str.replace(" ", "").str.len()
m["stem_ok"] = (m["ntok"] >= 2) | (m["tok_len"] >= 6)
city_ok = m["CITY"].fillna("").str.lower().str.strip() == m["cb_city_org"].fillna("").str.lower().str.strip()
m["loc_ok"] = (m["STATEORCOUNTRY"] == m["cb_state"]) | city_ok | m["cb_state"].isna()
tier = np.full(len(m), "none", dtype=object)
ex = m["match_method"].eq("exact_stem")
tier[ex & m["issuer_us"] & m["cb_us"] & m["stem_ok"] & m["loc_ok"]] = "T1_use"
tier[ex & m["issuer_us"] & m["cb_us"] & m["stem_ok"] & ~m["loc_ok"]] = "T2_hold_loc"
tier[ex & m["issuer_us"] & m["cb_us"] & ~m["stem_ok"]] = "T3_hold_generic"
tier[ex & m["issuer_us"] & ~m["cb_us"]] = "T4_country_mismatch"
tier[ex & ~m["issuer_us"]] = "T5_nonus_unverified"
tier[m["match_method"].eq("exact_stem_multi")] = "T6_multi"
tier[m["match_method"].eq("fuzzy")] = "T7_fuzzy"
m["tier"] = tier
m.to_parquet(os.path.join(D, "fund_vehicle_to_investor_v2.parquet"), index=False)
new = m[~m["is_amend"]]
t1 = new[new["tier"].eq("T1_use")]
summ = {"built_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "review_basis": "review_sample_200_reviewed_v1.csv (PI, 2026-09-09): exact 0.833 / multi 0.325 / fuzzy 0.825; rule B 0.973 (n=75)",
        "by_tier_new_notices": new["tier"].value_counts().to_dict(), "T1_filings": int(len(t1)), "T1_vc_filings": int(t1["INVESTMENTFUNDTYPE"].eq("Venture Capital Fund").sum()),
        "T1_cb_firms": int(t1["investor_uuid"].nunique()), "T1_cb_firms_vc": int(t1.loc[t1["INVESTMENTFUNDTYPE"].eq("Venture Capital Fund"), "investor_uuid"].nunique()),
        "T1_amount_sold_known": round(float(pd.to_numeric(t1["TOTALAMOUNTSOLD"], errors="coerce").notna().mean()), 3) if len(t1) else None,
        "T1_sale_date_known": round(float(t1["SALE_DATE"].notna().mean()), 3) if len(t1) else None}
json.dump(summ, io.open(os.path.join(D, "fund_match_summary_v2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
rev = t1.sample(min(100, len(t1)), random_state=20260910)[["ACCESSIONNUMBER", "ENTITYNAME", "STATEORCOUNTRY", "CITY", "INVESTMENTFUNDTYPE", "SALE_DATE", "cb_name", "cb_state", "cb_city_org", "stem", "tier"]].copy()
rev["reviewer_verdict (Y/N/?)"] = ""; rev.to_csv(os.path.join(D, "review_confirm_100.csv"), index=False, encoding="utf-8-sig")
print(json.dumps(summ, ensure_ascii=False))
