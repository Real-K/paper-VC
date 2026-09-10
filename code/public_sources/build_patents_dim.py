# -*- coding: utf-8 -*-
"""build_patents_dim.py — assignee_events.parquet(build_patents_v1 의 산출) → assignee_dim.parquet + manifest.json (벡터화; 모드 대신 '가장 흔한 값' 을 value_counts 로).
build_patents_v1.py 의 마지막 단계(파이썬 람다 집계)가 수백만 양수인에서 지나치게 느려 분리했다."""
import io
import json
import os
from datetime import datetime, timezone

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("P001_PROJECT_ROOT", "/path/to/project-root")   # holds shared/data/processed (derived, not redistributed)
OUT = os.path.join(ROOT, "shared", "data", "processed", "patents_v1")
ev = pd.read_parquet(os.path.join(OUT, "assignee_events.parquet"), columns=["assignee_id", "organization", "city", "state", "country", "application_id", "source", "filing_date"])
print("events", f"{len(ev):,}", "| assignees", f"{ev['assignee_id'].nunique():,}", flush=True)


def top_value(df, col):
    c = df.dropna(subset=[col]).groupby(["assignee_id", col]).size().reset_index(name="n").sort_values(["assignee_id", "n"], ascending=[True, False])
    return c.drop_duplicates("assignee_id").set_index("assignee_id")[col]


dim = ev.groupby("assignee_id").agg(n_events=("application_id", "size"), first_filing=("filing_date", "min"), last_filing=("filing_date", "max"))
dim["n_grants"] = ev[ev["source"].eq("grant")].groupby("assignee_id").size().reindex(dim.index).fillna(0).astype(int)
for col in ("organization", "city", "state", "country"):
    dim[col] = top_value(ev, col).reindex(dim.index)
    print("dim", col, flush=True)
dim = dim.reset_index()[["assignee_id", "organization", "city", "state", "country", "n_events", "n_grants", "first_filing", "last_filing"]]
dim.to_parquet(os.path.join(OUT, "assignee_dim.parquet"), index=False)
json.dump({"built_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "raw_manifest": "raw_manifest.csv", "n_events": int(len(ev)), "n_assignees": int(len(dim)),
           "share_us_events": round(float(ev["country"].eq("US").mean()), 4), "share_grant_events": round(float(ev["source"].eq("grant").mean()), 4),
           "filters": "organization nonblank; filing_date >= 1995-01-01; dedup on (assignee_id, application_id) grant-first (see build_patents_v1.py)"},
          io.open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"), indent=1)
print("done: assignees", f"{len(dim):,}", "| US share of events", round(float(ev["country"].eq("US").mean()), 3))
