# -*- coding: utf-8 -*-
"""ch_fetch_officers.py — Companies House 공개 데이터 API(REST 키)로 영국 VC 운용사의 임원(LLP 멤버·이사) 임명·사임 일자를 수집한다.

키: 환경변수 CH_API_KEY (값을 코드·문서에 적지 않는다). 인증 = HTTP Basic, 사용자명 = 키, 비밀번호 공란.
한도: 600 요청 / 5 분 → 요청 간격 0.55 초(안전 마진). 429 시 60 초 대기 후 재시도.
입력: CB 영국 운용사 목록 CSV (uuid, name, city) — 기본: papers/P001_gender_screening/05_data/public_sources/ch_targets_uk_firms.csv (build_ch_targets.py 가 만든다)
출력(파생 v1): shared/data/processed/ch_officers_v1/{firm_search.parquet, officers.parquet, manifest.json}
단계: (1) /search/companies?q=<정규화 이름> 상위 5 후보 저장(company_number·title·status·SIC·주소) (2) 후보 1순위(이름 정규화 완전 일치 우선, 없으면 최고 점수·활성)에 대해
      /company/{no}/officers (items_per_page=100, start_index 페이지네이션) → name·officer_role·appointed_on·resigned_on·nationality·occupation·date_of_birth(연/월)·links.officer.appointments.
매칭 정밀도 검수(200건)는 별도 노트북/스크립트에서.
사용: python ch_fetch_officers.py [--limit N] [--resume]
"""
import argparse
import base64
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(os.environ.get("P001_PROJECT_ROOT", "/path/to/project-root"), "shared")
OUT = os.path.join(ROOT, "data", "processed", "ch_officers_v1")
TARGETS = os.environ.get("CH_TARGETS", "/path/to/ch_targets_uk_firms.csv")  # UK investor-firm target list (firm names; not redistributed)   # ROOT = shared/
API = "https://api.company-information.service.gov.uk"
KEY = os.environ.get("CH_API_KEY", "")
GAP = 0.55
STOP = {"llp", "ltd", "limited", "plc", "lp", "the", "partners", "partnership", "capital", "ventures", "management", "uk", "&", "and"}


def norm(s):
    s = re.sub(r"[^a-z0-9& ]", " ", str(s).lower()); return " ".join(w for w in s.split() if w not in STOP)


def get(path, params=None):
    if not KEY:
        raise SystemExit("CH_API_KEY 환경변수가 없습니다.")
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={"Authorization": "Basic " + base64.b64encode((KEY + ":").encode()).decode(), "Accept": "application/json"})
    for a in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                time.sleep(GAP); return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as ex:
            if ex.code == 429: time.sleep(60); continue
            if ex.code == 404: time.sleep(GAP); return None
            time.sleep(5 * (a + 1))
        except Exception:
            time.sleep(5 * (a + 1))
    return None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=0); ap.add_argument("--resume", action="store_true"); a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    tg = pd.read_csv(TARGETS, dtype=str)
    if a.limit: tg = tg.head(a.limit)
    sp = os.path.join(OUT, "firm_search.parquet"); op = os.path.join(OUT, "officers.parquet")
    search = pd.read_parquet(sp).to_dict("records") if (a.resume and os.path.exists(sp)) else []
    officers = pd.read_parquet(op).to_dict("records") if (a.resume and os.path.exists(op)) else []
    done = {r["investor_uuid"] for r in search}
    for i, row in tg.iterrows():
        if row["investor_uuid"] in done: continue
        q = norm(row["name"]); res = get("/search/companies", {"q": row["name"], "items_per_page": 5}) or {"items": []}
        cands = []
        for k, it in enumerate(res.get("items", [])[:5]):
            rec = {"investor_uuid": row["investor_uuid"], "cb_name": row["name"], "rank": k, "company_number": it.get("company_number"), "title": it.get("title"), "company_status": it.get("company_status"),
                   "company_type": it.get("company_type"), "date_of_creation": it.get("date_of_creation"), "address": json.dumps(it.get("address", {}), ensure_ascii=False), "norm_exact": norm(it.get("title", "")) == q,
                   "sic_codes": "", "selected": False, "select_reason": ""}
            search.append(rec); cands.append(rec)
        # 선택 규칙: (1) 정규화 이름 완전 일치 중 가장 오래된 것 (2) 없으면 상위 3 후보의 프로필 SIC 가 펀드운용(64303/64301/64999/66300/66190/70100)이면 그중 가장 오래된 것 (3) 그 외 미선택(검수 대상)
        best = None
        exact = [c for c in cands if c["norm_exact"] and c["company_number"]]
        if exact:
            best = sorted(exact, key=lambda c: c["date_of_creation"] or "9999")[0]; best["select_reason"] = "exact_norm"
        else:
            FUND_SIC = {"64303", "64301", "64304", "64999", "66300", "66190", "70100", "64209", "64205"}
            for c in [c for c in cands if c["company_number"]][:3]:
                prof = get(f"/company/{c['company_number']}") or {}
                c["sic_codes"] = ",".join(prof.get("sic_codes", []) or [])
            fund = [c for c in cands[:3] if c["company_number"] and set(c["sic_codes"].split(",")) & FUND_SIC]
            if fund:
                best = sorted(fund, key=lambda c: c["date_of_creation"] or "9999")[0]; best["select_reason"] = "sic_fund_mgmt"
        if best:
            best["selected"] = True
        if best and best["company_number"]:
            start = 0
            while True:
                o = get(f"/company/{best['company_number']}/officers", {"items_per_page": 100, "start_index": start})
                if not o: break
                for it in o.get("items", []):
                    officers.append({"investor_uuid": row["investor_uuid"], "company_number": best["company_number"], "name": it.get("name"), "officer_role": it.get("officer_role"),
                                     "appointed_on": it.get("appointed_on"), "resigned_on": it.get("resigned_on"), "nationality": it.get("nationality"), "occupation": it.get("occupation"),
                                     "dob_year": (it.get("date_of_birth") or {}).get("year"), "dob_month": (it.get("date_of_birth") or {}).get("month"),
                                     "appointments_link": (it.get("links") or {}).get("officer", {}).get("appointments")})
                start += 100
                if start >= int(o.get("total_results", 0)): break
        done.add(row["investor_uuid"])
        if len(done) % 25 == 0:
            pd.DataFrame(search).to_parquet(sp, index=False); pd.DataFrame(officers).to_parquet(op, index=False); print(f"{len(done)} firms · officers {len(officers):,}", flush=True)
    pd.DataFrame(search).to_parquet(sp, index=False); pd.DataFrame(officers).to_parquet(op, index=False)
    json.dump({"built_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "n_firms": int(len(done)), "n_search_rows": len(search), "n_officer_rows": len(officers), "targets": TARGETS},
              io.open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"), indent=1)
    print(f"done: firms {len(done)} · officer rows {len(officers):,} -> {OUT}")


if __name__ == "__main__":
    sys.exit(main())
