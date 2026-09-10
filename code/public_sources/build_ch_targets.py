# -*- coding: utf-8 -*-
"""build_ch_targets.py — Companies House 조회 대상: P001 표본에 등장하는 영국(GBR) HQ 운용사 목록 (uuid, name, city, n_sample_deals, n_partners, n_female_partners).
출력: papers/P001_gender_screening/05_data/public_sources/ch_targets_uk_firms.csv (원자료 읽기만)."""
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("P001_PROJECT_ROOT", "/path/to/project-root")   # holds shared/data/processed (derived, not redistributed)
P001 = os.path.join(ROOT, "papers", "P001_gender_screening")
s = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v1.parquet"), columns=["investor_uuid", "partner_uuid", "fp"])
inv = pd.read_csv(os.path.join(ROOT, "..", "data", "crunchbase", "investors.csv"), usecols=["uuid", "name", "country_code", "city", "investor_types"], low_memory=False)
uk = inv[inv["country_code"].eq("GBR") & inv["uuid"].isin(s["investor_uuid"].unique())].copy()
g = s[s["investor_uuid"].isin(uk["uuid"])].groupby("investor_uuid").agg(n_sample_deals=("partner_uuid", "size"), n_partners=("partner_uuid", "nunique"))
gf = s[s["investor_uuid"].isin(uk["uuid"]) & (s["fp"] == 1)].groupby("investor_uuid")["partner_uuid"].nunique().rename("n_female_partners")
out = uk.rename(columns={"uuid": "investor_uuid"}).merge(g, left_on="investor_uuid", right_index=True).merge(gf, left_on="investor_uuid", right_index=True, how="left").fillna({"n_female_partners": 0})
out = out.sort_values("n_sample_deals", ascending=False)
dest = os.environ.get("CH_TARGETS", "/path/to/ch_targets_uk_firms.csv")  # UK investor-firm target list (firm names; not redistributed); out.to_csv(dest, index=False, encoding="utf-8")
print(f"UK firms {len(out):,} · partners {int(out['n_partners'].sum()):,} · female {int(out['n_female_partners'].sum()):,} -> {dest}")
