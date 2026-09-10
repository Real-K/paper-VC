# -*- coding: utf-8 -*-
"""build_formd_v1.py — SEC Form D 분기 ZIP(원자료) → 6 테이블 parquet(파생 v1) + manifest.json. 원자료는 읽기만 한다.

입력: shared/data/raw/sec_formd/zips/*.zip (fetch_sec_formd.py 의 manifest.csv 에 status=ok 인 분기만)
출력: shared/data/processed/formd_v1/{FORMDSUBMISSION,ISSUERS,OFFERING,RECIPIENTS,RELATEDPERSONS,SIGNATURES}.parquet, manifest.json
검사(rules/07): 각 ZIP 의 파일 집합 = 6 테이블(누락 시 기록), 컬럼 집합의 분기 간 차이 기록, ACCESSIONNUMBER 형식·중복(FORMDSUBMISSION 단위 유일), 행수 합계 = 분기 행수 합.
"""
import csv
import hashlib
import io
import json
import os
import sys
import zipfile
from datetime import datetime, timezone

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(os.environ.get("P001_PROJECT_ROOT", "/path/to/project-root"), "shared")
RAW = os.path.join(ROOT, "data", "raw", "sec_formd"); ZIPS = os.path.join(RAW, "zips"); MANIFEST = os.path.join(RAW, "manifest.csv")
OUT = os.path.join(ROOT, "data", "processed", "formd_v1")
TABLES = ["FORMDSUBMISSION", "ISSUERS", "OFFERING", "RECIPIENTS", "RELATEDPERSONS", "SIGNATURES"]


def sha16(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""): h.update(chunk)
    return h.hexdigest()[:16]


def read_member(z, name):
    raw = z.read(name)
    for enc in ("utf-8", "latin-1"):
        try:
            txt = raw.decode(enc); break
        except UnicodeDecodeError:
            continue
    first = txt.split("\n", 1)[0]
    sep = "\t" if first.count("\t") >= first.count(",") else ","
    return pd.read_csv(io.StringIO(txt), sep=sep, dtype=str, keep_default_na=False, na_values=[""], engine="c", quoting=csv.QUOTE_MINIMAL, on_bad_lines="warn", low_memory=False)


def main():
    os.makedirs(OUT, exist_ok=True)
    man = [r for r in csv.DictReader(io.open(MANIFEST, encoding="utf-8")) if r["status"] == "ok"]
    frames = {t: [] for t in TABLES}; log = {"quarters": {}, "missing_tables": {}, "column_variants": {t: {} for t in TABLES}}
    for r in sorted(man, key=lambda x: x["quarter"]):
        zp = os.path.join(ZIPS, r["file"])
        if sha16(zp) != r["sha256"][:16]:
            raise RuntimeError(f"sha mismatch vs manifest: {r['file']}")
        with zipfile.ZipFile(zp) as z:
            names = {os.path.splitext(os.path.basename(n))[0].upper(): n for n in z.namelist() if not n.endswith("/")}
            q = {"file": r["file"], "sha256_16": r["sha256"][:16], "rows": {}}
            for t in TABLES:
                key = next((k for k in names if k.startswith(t)), None)
                if key is None:
                    log["missing_tables"].setdefault(r["quarter"], []).append(t); q["rows"][t] = 0; continue
                df = read_member(z, names[key]); df.columns = [c.strip().upper() for c in df.columns]
                df["SRC_QUARTER"] = r["quarter"]
                sig = "|".join(df.columns); log["column_variants"][t].setdefault(sig, []).append(r["quarter"])
                frames[t].append(df); q["rows"][t] = int(len(df))
            log["quarters"][r["quarter"]] = q
        print(f"{r['quarter']} " + " ".join(f"{t[:6]}={q['rows'][t]:,}" for t in TABLES), flush=True)
    out_meta = {"built_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "source_manifest": MANIFEST, "n_quarters": len(man), "tables": {}}
    for t in TABLES:
        if not frames[t]:
            continue
        df = pd.concat(frames[t], ignore_index=True, sort=False)
        if t == "FORMDSUBMISSION" and "ACCESSIONNUMBER" in df.columns:
            dup = int(df["ACCESSIONNUMBER"].duplicated().sum()); bad = int((~df["ACCESSIONNUMBER"].str.match(r"^\d{10}-\d{2}-\d{6}$", na=False)).sum())
            out_meta["tables"][t] = {"dup_accession": dup, "bad_accession_format": bad}
        path = os.path.join(OUT, f"{t}.parquet"); df.to_parquet(path, index=False)
        out_meta["tables"].setdefault(t, {}).update({"rows": int(len(df)), "cols": list(df.columns), "sha256_16": sha16(path), "n_column_variants": len(log["column_variants"][t])})
        print(f"{t}: {len(df):,} rows · {len(df.columns)} cols · variants {len(log['column_variants'][t])}", flush=True)
    out_meta["log"] = log
    json.dump(out_meta, io.open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("done ->", OUT)


if __name__ == "__main__":
    sys.exit(main())
