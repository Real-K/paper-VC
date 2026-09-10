# -*- coding: utf-8 -*-
"""build_cb_funds_v1.py — Crunchbase funds.csv(원자료)에서 P001 표본의 (딜, 투자사) 시점 펀드 상태 변수를 만든다. 공개 소스 작업 0단계(외부 수집 0).

변수(딜 일자 dt 기준, 공시일 announced_on ≤ dt 인 펀드만 사용 — 사후 정보 없음):
  fund_age_yrs      최근 펀드 공시 후 경과년 (드라이파우더·투자기 단계 대리)
  ln_fund_size      최근 펀드 규모 log1p(USD) (결측이면 NaN, 지시자 fund_size_missing)
  fund_seq          딜 이전 공시 펀드 수(순번; 운용사 성숙도)
  ln_cum_fund_usd   딜 이전 누적 모집액 log1p
  new_fund_12m      딜 후 12개월 내 새 펀드 공시(펀드레이징 압력; 사후 변수 — 결과 회귀의 통제로 쓰지 말 것, 기술용)
  any_fund_rec      운용사가 CB funds 에 한 건이라도 있음
출력: shared/data/processed/cb_funds_v1/investor_fund_state.parquet (키: funding_round_uuid, investor_uuid) + manifest.json (행수·커버리지·sha).
"""
import hashlib
import io
import json
import os
from datetime import datetime, timezone

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("P001_PROJECT_ROOT", "/path/to/project-root")   # holds shared/data/processed (derived, not redistributed)
OUT = os.path.join(ROOT, "shared", "data", "processed", "cb_funds_v1")
SAMPLE = os.environ.get("P001_SAMPLE", "/path/to/sample_v1.parquet")
FUNDS = os.path.join(ROOT, "..", "data", "crunchbase", "funds.csv")
os.makedirs(OUT, exist_ok=True)
s = pd.read_parquet(SAMPLE, columns=["funding_round_uuid", "investor_uuid", "dt"]).drop_duplicates(["funding_round_uuid", "investor_uuid"])
s["dt"] = pd.to_datetime(s["dt"])
f = pd.read_csv(FUNDS, usecols=["uuid", "entity_uuid", "announced_on", "raised_amount_usd"], low_memory=False).dropna(subset=["entity_uuid"])
f["fdt"] = pd.to_datetime(f["announced_on"], errors="coerce"); f = f.dropna(subset=["fdt"]).sort_values(["entity_uuid", "fdt"])
f["amt"] = pd.to_numeric(f["raised_amount_usd"], errors="coerce")
f = f[f["entity_uuid"].isin(s["investor_uuid"].unique())]
grp = {k: (g["fdt"].to_numpy(), g["amt"].to_numpy(dtype=float)) for k, g in f.groupby("entity_uuid")}
age, size, seq, cum, new12, anyrec = [], [], [], [], [], []
for inv, t in zip(s["investor_uuid"], s["dt"]):
    if inv not in grp:
        age.append(np.nan); size.append(np.nan); seq.append(0); cum.append(0.0); new12.append(np.nan); anyrec.append(0.0); continue
    dts, amts = grp[inv]; k = np.searchsorted(dts, np.datetime64(t), side="right")
    anyrec.append(1.0)
    if k == 0:
        age.append(np.nan); size.append(np.nan); seq.append(0); cum.append(0.0)
    else:
        age.append((np.datetime64(t) - dts[k - 1]) / np.timedelta64(365, "D")); size.append(amts[k - 1]); seq.append(int(k)); cum.append(float(np.nansum(amts[:k])))
    k2 = np.searchsorted(dts, np.datetime64(t) + np.timedelta64(365, "D"), side="right"); new12.append(float(k2 > k))
o = s.copy()
o["fund_age_yrs"] = np.array(age, dtype=float); o["fund_size_usd"] = np.array(size, dtype=float); o["ln_fund_size"] = np.log1p(o["fund_size_usd"]); o["fund_size_missing"] = o["fund_size_usd"].isna().astype(float)
o["fund_seq"] = np.array(seq, dtype=int); o["ln_cum_fund_usd"] = np.log1p(np.array(cum, dtype=float)); o["new_fund_12m"] = np.array(new12, dtype=float); o["any_fund_rec"] = np.array(anyrec, dtype=float)
o["has_prior_fund"] = (o["fund_seq"] > 0).astype(float)
path = os.path.join(OUT, "investor_fund_state.parquet"); o.to_parquet(path, index=False)
sha = hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]
man = {"built_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "rows": int(len(o)), "keys": ["funding_round_uuid", "investor_uuid"], "source": {"sample": SAMPLE, "funds_csv": FUNDS},
       "coverage": {"any_fund_rec": round(float(o["any_fund_rec"].mean()), 4), "has_prior_fund": round(float(o["has_prior_fund"].mean()), 4), "fund_size_known_given_prior": round(float(1 - o.loc[o["has_prior_fund"] == 1, "fund_size_missing"].mean()), 4),
                    "median_fund_age_yrs": round(float(o["fund_age_yrs"].median()), 3), "median_fund_seq_given_prior": float(o.loc[o["has_prior_fund"] == 1, "fund_seq"].median())},
       "sha256_16": sha, "note": "new_fund_12m 은 사후 변수 — 결과 회귀 통제 금지(기술용)."}
json.dump(man, io.open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(man["coverage"], ensure_ascii=False), "rows", len(o), "sha", sha)
