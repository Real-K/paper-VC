# -*- coding: utf-8 -*-
"""fetch_sec_formd.py — SEC Form D 데이터셋(분기 ZIP, 2008Q1~) 수집기. 멱등: 이미 있는 분기는 sha256 을 검증만 하고 건너뛴다.

승인: PI 2026-09-09 ("Form D 저장 승인"). 저장 위치(읽기 전용 원자료): startup_finance/shared/data/raw/sec_formd/zips/  + manifest.csv (파일명·URL·bytes·sha256·수집 시각).
파생물은 shared/data/processed/formd_v1/ 로 (별도 스크립트 build_formd_v1.py).
SEC 공정 접근 정책: 요청 간격 ≥ 1초, 서술적 User-Agent. 연락처는 환경변수 SEC_CONTACT (예: "Name email@domain") 가 있으면 UA 에 붙인다.
사용: python fetch_sec_formd.py [--from 2009q3] [--to 2026q2] [--only 2015q1,2015q2]
"""
import argparse
import csv
import hashlib
import io
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(os.environ.get("P001_PROJECT_ROOT", "/path/to/project-root"), "shared")
RAW = os.path.join(ROOT, "data", "raw", "sec_formd")
ZIPS = os.path.join(RAW, "zips")
MANIFEST = os.path.join(RAW, "manifest.csv")
DOC_URL = "https://www.sec.gov/files/Form_D.pdf"
BASE = "https://www.sec.gov/files/structureddata/data/form-d-data-sets/"
# 페이지(2026-09-09 조회)에 실린 파일명 규칙: 2008q1_d.zip, 2008q2_d_0.zip … 2012q1_d.zip, 2012q2_d_0.zip … 2014q1_d.zip 이후 _d.zip; 2026q2 는 다른 경로.
SUFFIX_0 = {"2008q2", "2008q3", "2008q4", "2009q1", "2009q2", "2009q3", "2009q4", "2010q1", "2010q2", "2010q3", "2010q4", "2011q1", "2011q2", "2011q3", "2011q4",
            "2012q2", "2012q3", "2012q4", "2013q1", "2013q2", "2013q3", "2013q4"}
SPECIAL = {"2026q2": "https://www.sec.gov/files/datastandardsinnovation/data/form-d-data-sets/2026q2_d.zip"}
UA = "startup_finance academic research data collection (Python urllib; PI-supervised; rate-limited 1 req/s)"
if os.environ.get("SEC_CONTACT"):
    UA += " " + os.environ["SEC_CONTACT"]


def quarters(q0, q1):
    y0, k0 = int(q0[:4]), int(q0[5]); y1, k1 = int(q1[:4]), int(q1[5]); out = []
    y, k = y0, k0
    while (y, k) <= (y1, k1):
        out.append(f"{y}q{k}"); k += 1
        if k == 5: y += 1; k = 1
    return out


def url_for(q):
    if q in SPECIAL: return SPECIAL[q]
    return BASE + q + ("_d_0.zip" if q in SUFFIX_0 else "_d.zip")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""): h.update(chunk)
    return h.hexdigest()


def fetch(url, dest, tries=3):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip, deflate", "Host": "www.sec.gov"})
    for a in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            with open(dest, "wb") as f: f.write(data)
            return len(data), None
        except Exception as ex:  # 403(UA 미선언)·429·5xx → 대기 후 재시도
            err = f"{type(ex).__name__}: {ex}"[:200]; time.sleep(5 * (a + 1))
    return 0, err


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--from", dest="q0", default="2008q1"); ap.add_argument("--to", dest="q1", default="2026q2"); ap.add_argument("--only", default="")
    a = ap.parse_args()
    os.makedirs(ZIPS, exist_ok=True)
    rows = {}
    if os.path.exists(MANIFEST):
        for r in csv.DictReader(io.open(MANIFEST, encoding="utf-8")): rows[r["quarter"]] = r
    qs = a.only.split(",") if a.only else quarters(a.q0, a.q1)
    ok = skip = fail = 0
    for q in qs:
        url = url_for(q); dest = os.path.join(ZIPS, os.path.basename(url))
        if q in rows and os.path.exists(dest) and sha256(dest) == rows[q]["sha256"]:
            skip += 1; continue
        n, err = fetch(url, dest)
        if err:
            print(f"FAIL {q} {url} {err}", flush=True); fail += 1
            rows[q] = {"quarter": q, "file": os.path.basename(url), "url": url, "bytes": 0, "sha256": "", "fetched_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "status": "failed: " + err}
        else:
            rows[q] = {"quarter": q, "file": os.path.basename(url), "url": url, "bytes": n, "sha256": sha256(dest), "fetched_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "status": "ok"}
            print(f"OK   {q} {n:>12,} bytes {rows[q]['sha256'][:16]}", flush=True); ok += 1
        time.sleep(1.1)
    # 문서 PDF
    doc = os.path.join(RAW, "Form_D_documentation.pdf")
    if not os.path.exists(doc):
        n, err = fetch(DOC_URL, doc); print(f"{'OK  ' if not err else 'FAIL'} documentation PDF {n:,} bytes {err or ''}", flush=True)
    with io.open(MANIFEST, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["quarter", "file", "url", "bytes", "sha256", "fetched_utc", "status"]); w.writeheader()
        for q in sorted(rows): w.writerow(rows[q])
    print(f"done: ok {ok} · skipped {skip} · failed {fail} · manifest {MANIFEST}")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
