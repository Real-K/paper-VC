# -*- coding: utf-8 -*-
"""p001_00 — 정본 표본(v2)의 집계 카운트만 JSON 으로 고정한다 (Table 1 이 표본 파케이 대신 이 파일을 읽도록; 복제 저장소에서 표를 마이크로데이터 없이 재생성하기 위함).
출력: 07_analysis/out/P00100.json — n_deals(전 표본), n_naeu(북미·유럽 본표본), 표본 sha256_16. 값은 05_data/data_manifest.yaml 의 동결 수치와 일치해야 한다."""
import hashlib
import json
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.abspath(os.path.join(HERE, ".."))
SAMPLE = os.environ.get("P001_SAMPLE", os.environ.get("P001_SAMPLE", "/path/to/sample_v2.parquet"))
OUT = os.environ.get("P001_OUT", os.path.join(HERE, "out"))
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR",
      "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}
d = pd.read_parquet(SAMPLE, columns=["country_code"])
sha = hashlib.sha256(open(SAMPLE, "rb").read()).hexdigest()[:16]
d_all = pd.read_parquet(SAMPLE, columns=["country_code", "funding_round_uuid", "org_uuid", "investor_uuid", "partner_uuid"])
est = {"n_deals": int(len(d)), "n_naeu": int(d["country_code"].isin(EU | {"USA", "CAN"}).sum()), "sample_sha256_16": sha,
       "unique_rounds": int(d_all["funding_round_uuid"].nunique()), "unique_companies": int(d_all["org_uuid"].nunique()), "unique_investor_firms": int(d_all["investor_uuid"].nunique()), "unique_partners": int(d_all["partner_uuid"].nunique()),
       "v1_rows": 154123, "excluded_pre_exit_rows": 1111, "excluded_pre_exit_rows_naeu": 933}
assert est["n_deals"] == 153012 and sha == "3acfb38d12559791", est   # sample_v2 (D067)
json.dump({"id": "P001-00", "title": "정본 표본 집계 카운트 (Table 1 입력)", "status": "OK", "estimates": est, "code": "06_code/p001_00_sample_counts.py"},
          open(os.path.join(OUT, "P00100.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(est)
