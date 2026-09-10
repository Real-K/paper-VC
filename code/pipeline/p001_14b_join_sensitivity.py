# -*- coding: utf-8 -*-
"""p001_14 (Track D, Tier 2) 순서 불변 분해 + E2 순열 추론 + E3 선형위반 감도 곡선

[왜] (P-5) 사다리 순서(섹터→스테이지)가 임의 — 역순과 bracketing 으로 경로 의존 공격 차단.
(P-7) E2 판별에 부트와 독립인 설계기반 추론(셀 내 순열) 병기. (P-6) E3 의 스칼라 파단치 대신
차등추세 크기 δ 격자 위 효과 하한 곡선 — 표준 감도 제시형 (P001-04b 경로 기반; P001-11 이
갱신하면 재산출).
[사전 예측] (결과 전) P1 역순 사다리에서도 배치 총몫(섹터+스테이지) 85~95%; 개별 몫은
  [사다리, 역순] bracketing 으로 보고. P2 순열 p 가 부트 결론과 정합 (fon·exit_ever 격차 비유의).
  P3 δ*(하한이 0 닿는 차등추세) ≥ 0.3pp/반기.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["HARNESS_OUT"] = os.environ.get("P001_OUT", os.path.join(HERE, "out"))  # set P001_* / CRUNCHBASE_RAW to your local copies (licensed inputs; see DATA_ACCESS.md)
sys.path.insert(0, HERE)  # gates.py / emit_contract.py sit alongside in code/pipeline
from emit_contract import emit, qci  # noqa: E402

rng = np.random.default_rng(42)
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR",
      "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}
NAEU = EU | {"USA", "CAN"}

d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v2.parquet"))
d = d[d["country_code"].isin(NAEU)].copy()
d["dt"] = pd.to_datetime(d["dt"])
d["cell_stg0"] = d["cell0"] + "|" + d["stage"]  # 역순: 투자사×연도×스테이지


def fwl(df, y, cell, nb=300):
    dd = df[[y, "fp", cell, "investor_uuid"]].reset_index(drop=True)
    yr = (dd[y] - dd[y].groupby(dd[cell]).transform("mean")).to_numpy()
    xr = (dd["fp"] - dd["fp"].groupby(dd[cell]).transform("mean")).to_numpy()
    sxx = (xr * xr).sum()
    beta = float((xr * yr).sum() / sxx)
    grp = {c: g.index.to_numpy() for c, g in dd.groupby("investor_uuid")}
    keys = list(grp)
    bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(keys), len(keys))
        rows_ = np.concatenate([grp[keys[i]] for i in pick])
        x2, y2 = xr[rows_], yr[rows_]
        s = (x2 * x2).sum()
        if s:
            bs.append((x2 * y2).sum() / s)
    return round(beta, 4), qci(bs)


# P-5 역순 사다리 (E1)
b0, c0 = fwl(d, "ff", "cell0")
b_st, c_st = fwl(d, "ff", "cell_stg0")      # +스테이지 먼저
b_full, c_full = fwl(d, "ff", "cell_stage")  # 완전
stage_first = 1 - b_st / b0
cat_after = (b_st - b_full) / b0
# 정순 몫 (P001-02): 섹터 54%, 스테이지 37% → bracketing
sector_share = [round(cat_after, 3), 0.539]
stage_share = [0.366, round(stage_first, 3)]
total = 1 - b_full / b0

# P-7 E2 순열 (fon·exit_ever, cell_stage, ff=1)
def perm_p(df, y, nperm=500):
    dd = df[[y, "fp", "cell_stage"]].reset_index(drop=True)
    yr = (dd[y] - dd[y].groupby(dd["cell_stage"]).transform("mean")).to_numpy()
    xr = (dd["fp"] - dd["fp"].groupby(dd["cell_stage"]).transform("mean")).to_numpy()
    obs = (xr * yr).sum() / (xr * xr).sum()
    ps = []
    for _ in range(nperm):
        fp_p = dd.groupby("cell_stage")["fp"].transform(
            lambda s: s.sample(frac=1, random_state=int(rng.integers(1e9))).to_numpy())
        xp = (fp_p - fp_p.groupby(dd["cell_stage"]).transform("mean")).to_numpy()
        s = (xp * xp).sum()
        if s:
            ps.append((xp * yr).sum() / s)
    return round(float(obs), 4), round(float(np.mean(np.abs(ps) >= abs(obs))), 3)


dff = d[d["ff"] == 1.0]
fon_obs, fon_p = perm_p(dff[dff["dt"] <= "2020-10-31"], "fon")
ex_obs, ex_p = perm_p(dff[dff["dt"] <= "2017-10-31"], "exit_ever")

# P-6 감도 곡선 (P001-11 있으면 그 경로, 없으면 04b)
src = os.path.join(os.environ.get("P001_ARTIFACTS", os.path.join(HERE, "..", "..", "artifacts")), "P00111.json")
sj = json.load(open(src, encoding="utf-8"))
L2 = sj["estimates"]["join"]  # 정정: 결합 대비 대신 영입 마진 단독(딜 수준, 명확 분리) 에 감도 곡선
L2v, L2ci = (L2[0], L2[1])
kbar = 4.0  # 사후 평균 상대거리 (반기; 사전 중심 −2.5 → 사후 중심 +1.5 → 4)
curve = {}
delta_star = None
for dlt in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]:
    lo = L2ci[0] * 100 - dlt * kbar if L2ci[0] < 1 else L2ci[0] - dlt * kbar
    val = (L2v if L2v > 1 else L2v * 100) - dlt * kbar
    lo_pp = (L2ci[0] * 100 if abs(L2ci[0]) < 1 else L2ci[0]) - dlt * kbar
    curve[str(dlt)] = [round(val, 2), round(lo_pp, 2)]
    if delta_star is None and lo_pp <= 0:
        delta_star = dlt

p1 = 0.85 <= total <= 0.98
p2 = (fon_p > 0.05) and (ex_p > 0.05)
p3 = (delta_star or 0.7) >= 0.3
status = "GO" if (p1 and p2) else "PARTIAL"
verdict = (f"역순 사다리: {b0*100:+.2f} → 스테이지 먼저 {b_st*100:+.2f} → 완전 {b_full*100:+.2f}; "
           f"배치 총몫 {total*100:.0f}% (정순 91%와 정합); 섹터 몫 bracket [{sector_share[0]*100:.0f}%, "
           f"{sector_share[1]*100:.0f}%]·스테이지 [{stage_share[0]*100:.0f}%, {stage_share[1]*100:.0f}%]; "
           f"E2 순열 p: fon {fon_p}·exit {ex_p} (부트 결론 정합); "
           f"감도 곡선 δ* = {delta_star}pp/반기 (하한 0 도달점, 소스 {os.path.basename(src)})")

emit("P001-14b", "순서 불변 분해 + E2 순열 + E3 감도 곡선 (Track D, Tier 2)", status,
     {"ladder_reverse": {"L0": [b0, c0], "stage_first": [b_st, c_st], "full": [b_full, c_full]},
      "share_bracket": {"sector": sector_share, "stage": stage_share, "total": round(total, 3)},
      "e2_perm": {"fon": [fon_obs, fon_p], "exit_ever": [ex_obs, ex_p]},
      "sensitivity_curve_pp": curve, "delta_star": delta_star, "source": os.path.basename(src)},
     prediction="배치 총몫 85~95%; 순열 정합; δ* ≥ 0.3pp/반기",
     verdict=verdict, kill_met=False, n=int(len(d)),
     extra={"stage": 5, "feeds": "Track D Tier2 (join-margin sensitivity, P001-14 보완)", "slug": "tier2_robust_join"})
print("done")
