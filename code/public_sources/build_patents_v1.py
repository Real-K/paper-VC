# -*- coding: utf-8 -*-
"""build_patents_v1.py — PatentsView(USPTO Open Data Portal) 8개 TSV.zip(원자료: ../data/USPTO, 읽기 전용) → 회사(양수인) 단위 출원 사건 표.

출력(shared/data/processed/patents_v1/):
  assignee_events.parquet  — 한 행 = (assignee_id, 출원 1건): source ∈ {grant, pgpub}, application_id, filing_date, grant_date(있으면), organization, city, state, country, assignee_type
                             중복 제거: 같은 application_id 가 등록(g_application)과 공개(pg_published_application)에 모두 있으면 grant 행만 남긴다(crosswalk 불필요 — application_id 공통 키).
  assignee_dim.parquet     — assignee_id 별 대표 조직명·위치·사건 수·첫/마지막 출원일 (회사 매칭용)
  manifest.json            — 원자료 sha(raw_manifest.csv), 행수, 필터
필터: organization 비공란(개인 양수인 제외), filing_date ≥ 1995-01-01, 출원일 파싱 가능.
검사(rules/07): 키 형식·중복·행수 로그.
"""
import io
import json
import os
import zipfile
from datetime import datetime, timezone

import pandas as pd

RAW = os.environ.get("USPTO_RAW", "/path/to/patentsview_bulk")  # PatentsView bulk files (public)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("P001_PROJECT_ROOT", "/path/to/project-root")   # holds shared/data/processed (derived, not redistributed)
OUT = os.path.join(ROOT, "shared", "data", "processed", "patents_v1"); os.makedirs(OUT, exist_ok=True)


def read(name, usecols, dtype=str, chunks=False):
    z = zipfile.ZipFile(os.path.join(RAW, name)); mem = [n for n in z.namelist() if not n.endswith("/")][0]
    kw = dict(sep="\t", usecols=usecols, dtype=dtype, quotechar='"', na_values=[""], keep_default_na=False, low_memory=False)
    if chunks:
        return pd.read_csv(z.open(mem), chunksize=2_000_000, **kw)
    return pd.read_csv(z.open(mem), **kw)


def log(*a):
    print(*a, flush=True)


# ── 위치 ─────────────────────────────────────────────────────────────────────
loc = pd.concat([read("g_location_disambiguated.tsv.zip", ["location_id", "disambig_city", "disambig_state", "disambig_country"]),
                 read("pg_location_disambiguated.tsv.zip", ["location_id", "disambig_city", "disambig_state", "disambig_country"])]).drop_duplicates("location_id").set_index("location_id")
log(f"locations {len(loc):,}")
# ── 등록 특허: 출원일·등록일 ────────────────────────────────────────────────
app = read("g_application.tsv.zip", ["application_id", "patent_id", "filing_date"])
pat = read("g_patent.tsv.zip", ["patent_id", "patent_type", "patent_date"])
g = app.merge(pat, on="patent_id", how="left")
g["filing_date"] = pd.to_datetime(g["filing_date"], errors="coerce"); g["grant_date"] = pd.to_datetime(g["patent_date"], errors="coerce")
g = g[g["filing_date"] >= "1995-01-01"].drop(columns=["patent_date"])
log(f"granted with filing ≥1995: {len(g):,} (patent types {g['patent_type'].value_counts().head(4).to_dict()})")
ga_parts = []
for ch in read("g_assignee_disambiguated.tsv.zip", ["patent_id", "assignee_sequence", "assignee_id", "disambig_assignee_organization", "assignee_type", "location_id"], chunks=True):
    ch = ch[ch["disambig_assignee_organization"].notna() & ch["patent_id"].isin(g["patent_id"])]
    ga_parts.append(ch)
ga = pd.concat(ga_parts, ignore_index=True); del ga_parts
ge = ga.merge(g[["patent_id", "application_id", "filing_date", "grant_date", "patent_type"]], on="patent_id", how="inner"); ge["source"] = "grant"; ge["pgpub_id"] = None
log(f"grant assignee-events {len(ge):,} · assignees {ge['assignee_id'].nunique():,}")
# ── 공개 출원 ─────────────────────────────────────────────────────────────────
pub = read("pg_published_application.tsv.zip", ["pgpub_id", "application_id", "filing_date", "patent_type", "published_date"])
pub["filing_date"] = pd.to_datetime(pub["filing_date"], errors="coerce"); pub["published_date"] = pd.to_datetime(pub["published_date"], errors="coerce")
pub = pub[pub["filing_date"] >= "1995-01-01"]
pa_parts = []
for ch in read("pg_assignee_disambiguated.tsv.zip", ["pgpub_id", "assignee_sequence", "assignee_id", "disambig_assignee_organization", "assignee_type", "location_id"], chunks=True):
    ch = ch[ch["disambig_assignee_organization"].notna()]; pa_parts.append(ch)
pa = pd.concat(pa_parts, ignore_index=True); del pa_parts
pe = pa.merge(pub, on="pgpub_id", how="inner"); pe["source"] = "pgpub"; pe["grant_date"] = pd.NaT; pe["patent_id"] = None
log(f"pgpub assignee-events {len(pe):,} · assignees {pe['assignee_id'].nunique():,}")
# ── 결합·중복 제거 (같은 application_id: grant 우선) ─────────────────────────
cols = ["assignee_id", "assignee_sequence", "disambig_assignee_organization", "assignee_type", "location_id", "application_id", "patent_id", "pgpub_id", "filing_date", "grant_date", "published_date", "patent_type", "source"]
ge["published_date"] = pd.NaT
ev = pd.concat([ge[cols], pe[cols]], ignore_index=True)
before = len(ev)
ev = ev.sort_values(["application_id", "source"]).drop_duplicates(["assignee_id", "application_id"], keep="first")   # 'grant' < 'pgpub'
ev = ev.rename(columns={"disambig_assignee_organization": "organization"})
ev = ev.join(loc, on="location_id").rename(columns={"disambig_city": "city", "disambig_state": "state", "disambig_country": "country"})
log(f"events after dedup {len(ev):,} (from {before:,}) · assignees {ev['assignee_id'].nunique():,} · US {ev['country'].eq('US').mean():.3f}")
ev.to_parquet(os.path.join(OUT, "assignee_events.parquet"), index=False)
dim = ev.groupby("assignee_id").agg(organization=("organization", lambda s: s.mode().iat[0]), city=("city", lambda s: s.mode().iat[0] if s.notna().any() else None),
                                   state=("state", lambda s: s.mode().iat[0] if s.notna().any() else None), country=("country", lambda s: s.mode().iat[0] if s.notna().any() else None),
                                   n_events=("application_id", "size"), n_grants=("source", lambda s: int((s == "grant").sum())), first_filing=("filing_date", "min"), last_filing=("filing_date", "max")).reset_index()
dim.to_parquet(os.path.join(OUT, "assignee_dim.parquet"), index=False)
json.dump({"built_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "raw_manifest": "raw_manifest.csv", "n_events": int(len(ev)), "n_events_before_dedup": int(before), "n_assignees": int(len(dim)),
           "share_us": round(float(ev["country"].eq("US").mean()), 4), "filters": "organization nonblank; filing_date ≥ 1995-01-01; dedup on (assignee_id, application_id) grant-first"},
          io.open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"), indent=1)
log("done ->", OUT, "| assignees", f"{len(dim):,}")
