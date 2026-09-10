# -*- coding: utf-8 -*-
"""match_ch_partners.py — Companies House 임원(ch_officers_v1) ↔ P001 표본의 영국 운용사 파트너(CB people) 이름 매칭 + CB jobs 재직일 일치율.

매칭 단위: 같은 investor_uuid 안에서만(운용사가 이미 매칭됨). 이름 정규화: CH "SURNAME, Given Middle" → (given, surname); CB people first_name/last_name → 소문자·악센트 제거·하이픈 공백.
규칙: (1) given+surname 완전 일치 (2) surname 일치 + given 첫 토큰 일치 (3) surname 일치 + given 이니셜 일치(약한 매칭; 검수 대상). 동명이인이 한 운용사 안에 둘이면 ambiguous.
검증: CB jobs(started_on/ended_on, 해당 investor_uuid 의 job) 가 있는 파트너에 대해 |CH appointed_on − CB started_on| 분포, 사임 여부 일치율(CH resigned_on 유무 vs CB ended_on 유무).
출력: shared/data/processed/ch_officers_v1/partner_match.parquet, partner_match_summary.json, review_sample_100.csv (규칙 2·3 중심)
"""
import io
import json
import os
import re
import unicodedata
from datetime import datetime, timezone

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("P001_PROJECT_ROOT", "/path/to/project-root")   # holds shared/data/processed (derived, not redistributed)
D = os.path.join(ROOT, "shared", "data", "processed", "ch_officers_v1")
SAMPLE = os.environ.get("P001_SAMPLE_V1", "/path/to/sample_v1.parquet")
CB = os.path.join(ROOT, "..", "data", "crunchbase")


def clean(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z ]", " ", s.replace("-", " ")).split()


def split_ch(name):
    if "," in str(name):
        sur, given = [p.strip() for p in str(name).split(",", 1)]
    else:
        toks = str(name).split(); sur, given = (toks[-1], " ".join(toks[:-1])) if toks else ("", "")
    g = [t for t in clean(given) if t not in {"dr", "mr", "mrs", "ms", "sir", "lord", "lady", "prof"}]
    return g, clean(sur)


def main():
    off = pd.read_parquet(os.path.join(D, "officers.parquet"))
    off = off[~off["officer_role"].fillna("").str.contains("secretary")].copy()
    off[["g", "s"]] = pd.DataFrame([split_ch(n) for n in off["name"]], index=off.index)
    s = pd.read_parquet(SAMPLE, columns=["investor_uuid", "partner_uuid", "fp", "dt"]).drop_duplicates(["investor_uuid", "partner_uuid"])
    uk_firms = set(off["investor_uuid"].unique()); s = s[s["investor_uuid"].isin(uk_firms)]
    ppl = pd.read_csv(os.path.join(CB, "people.csv"), usecols=["uuid", "first_name", "last_name", "gender"], low_memory=False)
    ppl = ppl[ppl["uuid"].isin(s["partner_uuid"].unique())]
    p = s.merge(ppl, left_on="partner_uuid", right_on="uuid", how="left")
    p["pg"] = p["first_name"].map(clean); p["ps"] = p["last_name"].map(clean)
    rows = []
    for inv, grp in p.groupby("investor_uuid"):
        o = off[off["investor_uuid"] == inv]
        for r in grp.itertuples():
            if not r.ps: continue
            sur = r.ps[-1]; c = o[o["s"].map(lambda x: bool(x) and x[-1] == sur)]
            if c.empty:
                rows.append((inv, r.partner_uuid, r.fp, "none", None, None, None, None, 0)); continue
            full = c[c["g"].map(lambda g: g == r.pg)]
            first = c[c["g"].map(lambda g: bool(g) and bool(r.pg) and g[0] == r.pg[0])]
            init = c[c["g"].map(lambda g: bool(g) and bool(r.pg) and g[0][0] == r.pg[0][0])]
            for lab, cc in (("full_name", full), ("surname_first", first), ("surname_initial", init)):
                if len(cc):
                    meth = lab if cc["name"].nunique() == 1 else lab + "_ambiguous"
                    x = cc.iloc[0]; rows.append((inv, r.partner_uuid, r.fp, meth, x["name"], x["officer_role"], x["appointed_on"], x["resigned_on"], int(cc["name"].nunique()))); break
    m = pd.DataFrame(rows, columns=["investor_uuid", "partner_uuid", "fp", "match_method", "ch_name", "officer_role", "appointed_on", "resigned_on", "n_candidates"])
    # CB jobs agreement
    jobs = pd.read_csv(os.path.join(CB, "jobs.csv"), usecols=["person_uuid", "org_uuid", "started_on", "ended_on", "job_type"], low_memory=False)
    jobs = jobs[jobs["person_uuid"].isin(m["partner_uuid"]) & jobs["org_uuid"].isin(uk_firms)]
    jobs = jobs.rename(columns={"person_uuid": "partner_uuid", "org_uuid": "investor_uuid"}).drop_duplicates(["partner_uuid", "investor_uuid"])
    mm = m.merge(jobs, on=["partner_uuid", "investor_uuid"], how="left")
    ok = mm[mm["match_method"].isin(["full_name", "surname_first"])].copy()
    ok["app"] = pd.to_datetime(ok["appointed_on"], errors="coerce"); ok["cb_start"] = pd.to_datetime(ok["started_on"], errors="coerce")
    ok["gap_yrs"] = (ok["app"] - ok["cb_start"]).dt.days / 365.25
    both = ok.dropna(subset=["gap_yrs"])
    summ = {"built_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "n_uk_firms_with_officers": len(uk_firms), "n_partners_uk": int(len(m)), "n_female_partners_uk": int(m["fp"].sum()),
            "by_method": m["match_method"].value_counts().to_dict(), "matched_strong_share": round(float(m["match_method"].isin(["full_name", "surname_first"]).mean()), 4),
            "matched_strong_share_female": round(float(m.loc[m["fp"] == 1, "match_method"].isin(["full_name", "surname_first"]).mean()), 4) if (m["fp"] == 1).any() else None,
            "jobs_overlap_n": int(len(both)), "gap_appointed_minus_cbstart_yrs": {"median": round(float(both["gap_yrs"].median()), 2), "p25": round(float(both["gap_yrs"].quantile(.25)), 2), "p75": round(float(both["gap_yrs"].quantile(.75)), 2)} if len(both) else None,
            "resignation_agreement": round(float(((ok["resigned_on"].notna()) == (ok["ended_on"].notna())).mean()), 4) if len(ok) else None,
            "ch_resigned_share_among_matched": round(float(ok["resigned_on"].notna().mean()), 4) if len(ok) else None}
    mm.to_parquet(os.path.join(D, "partner_match.parquet"), index=False)
    rev = mm[mm["match_method"].str.startswith(("surname_first", "surname_initial"))].sample(min(100, int(mm["match_method"].str.startswith(("surname_first", "surname_initial")).sum())), random_state=20260909) if len(mm) else mm
    rev = rev.merge(ppl[["uuid", "first_name", "last_name"]], left_on="partner_uuid", right_on="uuid", how="left")[["investor_uuid", "first_name", "last_name", "ch_name", "officer_role", "appointed_on", "resigned_on", "match_method"]]
    rev["reviewer_verdict (Y/N/?)"] = ""; rev.to_csv(os.path.join(D, "review_sample_100.csv"), index=False, encoding="utf-8-sig")
    json.dump(summ, io.open(os.path.join(D, "partner_match_summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(summ, ensure_ascii=False))


if __name__ == "__main__":
    main()
