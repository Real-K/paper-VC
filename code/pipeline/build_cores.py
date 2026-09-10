# -*- coding: utf-8 -*-
"""cores_v1 — Crunchbase 원본에서 하네스가 쓰는 열만 뽑아 parquet 으로 고정한다.
원자료는 편집하지 않는다(rules/02). 재현: python build_cores.py  → shared/data/processed/cores_v1/*.parquet + MANIFEST"""
import os, sys, time, json, hashlib
import pyarrow as pa, pyarrow.csv as pc, pyarrow.parquet as pq

RAW = os.environ.get("CRUNCHBASE_RAW", "/path/to/crunchbase_csv_dump")  # licensed; see DATA_ACCESS.md
OUT = os.environ.get("P001_CORES", "/path/to/cores_v1")
os.makedirs(OUT, exist_ok=True)

SPEC = {
 "organizations": ["uuid","name","country_code","state_code","region","city","status","primary_role",
                   "category_list","category_groups_list","founded_on","closed_on","employee_count",
                   "num_funding_rounds","total_funding_usd","domain","created_at"],
 "funding_rounds": ["uuid","org_uuid","org_name","announced_on","investment_type","raised_amount_usd",
                    "post_money_valuation_usd","investor_count","country_code","state_code","city",
                    "lead_investor_uuids","created_at"],
 "investments": ["funding_round_uuid","investor_uuid","investor_name","investor_type","is_lead_investor"],
 "investors": ["uuid","name","country_code","city","investor_types","roles","founded_on","closed_on",
               "investment_count","domain"],
 "acquisitions": ["acquiree_uuid","acquirer_uuid","acquired_on","acquisition_type","price_usd",
                  "acquiree_country_code","acquirer_country_code","acquirer_name","acquiree_name"],
 "ipos": ["org_uuid","went_public_on","stock_exchange_symbol","stock_symbol","country_code"],
 "funds": ["uuid","entity_uuid","entity_name","announced_on","raised_amount_usd","name"],
 "people": ["uuid","name","gender","country_code","featured_job_organization_uuid"],
 "jobs": ["person_uuid","org_uuid","started_on","ended_on","is_current","title","job_type"],
 "degrees": ["person_uuid","institution_uuid","institution_name","degree_type","completed_on"],
 "events": ["uuid","name","started_on","country_code","city","event_roles"],
 "event_appearances": ["event_uuid","participant_uuid","participant_type","appearance_type"],
 "investment_partners": ["funding_round_uuid","investor_uuid","investor_name","partner_uuid","partner_name"],
 "org_parents": ["uuid","parent_uuid"],
}

manifest = {}
for t, cols in SPEC.items():
    t0 = time.time(); src = os.path.join(RAW, t + ".csv")
    tbl = pc.read_csv(src,
        convert_options=pc.ConvertOptions(include_columns=cols, strings_can_be_null=True),
        parse_options=pc.ParseOptions(newlines_in_values=True),
        read_options=pc.ReadOptions(block_size=1 << 25))
    dst = os.path.join(OUT, t + ".parquet")
    pq.write_table(tbl, dst, compression="zstd")
    h = hashlib.sha256(open(dst, "rb").read()).hexdigest()[:16]
    manifest[t] = {"rows": tbl.num_rows, "cols": cols, "sha256_16": h,
                   "mb": round(os.path.getsize(dst)/1048576, 1), "sec": round(time.time()-t0, 1)}
    print(f"{t:<22} rows={tbl.num_rows:>9,} {manifest[t]['mb']:>7} MB  {manifest[t]['sec']}s", flush=True)
    del tbl

json.dump(manifest, open(os.path.join(OUT, "MANIFEST.json"), "w", encoding="utf-8"), indent=1)
print("cores_v1 complete →", OUT)
