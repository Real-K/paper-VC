# -*- coding: utf-8 -*-
"""p001_01b 헤드라인 계단식 — ff 딜의 exit_ever 격차: 셀 사다리 (E2 의 전시물 재구성)

[왜] P001-01: GMWX 형 전체-딜 격차는 NA+EU·2010+ 에서 애초에 부재 (불리 기록 완료). 그러나
우리 헤드라인(I-78 글로벌: ff 딜 exit_ever −6.25pp 유의 → 배치 통제 시 소멸)의 계단식은
아직 NA+EU 로 제시되지 않았다. 동결 estimand E2 를 사다리 셀로 제시하는 전시물 구성 —
새 estimand 아님 (e1_decomposition_ladder 논리의 E2 적용).
[설계] sample_v1 NA+EU, ff=1 딜, y=exit_ever (dt≤2017-10). 셀 사다리:
  연도만 → 투자사×연도 → +섹터 → +스테이지 (끝점은 P001-03 의 −1.02 ns 와 일치해야 함 — 재현 체크).
[사전 예측] (결과 전) P1 연도만·투자사×연도에서 음(−3~−7pp)·CI 0 배제 (I-78 글로벌 −6.25 와
  동방향), P2 사다리를 내려가며 단조 감쇠, 끝점 P001-03 일치.
[판정] P1+P2 → 1막 전시물 성립 (GO). 연도만에서 이미 null → NA+EU 에는 원 격차 자체가 없음 —
  헤드라인을 글로벌 표본 서술로 조정 (PARTIAL, 정직 기록).
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["HARNESS_OUT"] = os.environ.get("P001_OUT", os.path.join(HERE, "out"))  # set P001_* / CRUNCHBASE_RAW to your local copies (licensed inputs; see DATA_ACCESS.md)
sys.path.insert(0, HERE)  # gates.py / emit_contract.py sit alongside in code/pipeline
from emit_contract import emit, qci  # noqa: E402

rng = np.random.default_rng(42)
NB = 500
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR",
      "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}
NAEU = EU | {"USA", "CAN"}

d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v2.parquet"))
d["dt"] = pd.to_datetime(d["dt"])
d = d[d["country_code"].isin(NAEU) & (d["ff"] == 1.0) & (d["dt"] <= "2017-10-31")].copy()
d["cell_year"] = d["year"]


def gap(df, cell, nb=NB):
    dd = df[["exit_ever", "fp", cell, "investor_uuid"]].reset_index(drop=True)
    yr = (dd["exit_ever"] - dd["exit_ever"].groupby(dd[cell]).transform("mean")).to_numpy()
    xr = (dd["fp"] - dd["fp"].groupby(dd[cell]).transform("mean")).to_numpy()
    sxx = (xr * xr).sum()
    beta = float((xr * yr).sum() / sxx) if sxx else float("nan")
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


lad = {}
for name, cell in (("S0_year", "cell_year"), ("S1_invyear", "cell0"),
                   ("S2_pluscat", "cell_cat"), ("S3_plusstage", "cell_stage")):
    lad[name] = list(gap(d, cell))

s0sig = lad["S0_year"][1][1] < 0
s1sig = lad["S1_invyear"][1][1] < 0
endpoint_ok = abs(lad["S3_plusstage"][0] - (-0.0102)) < 0.005
status = "GO" if (s0sig or s1sig) else "PARTIAL"
verdict = (f"exit_ever(ff 딜): 연도만 {lad['S0_year'][0]:+.4f} {lad['S0_year'][1]} → 투자사×연도 "
           f"{lad['S1_invyear'][0]:+.4f} {lad['S1_invyear'][1]} → +섹터 {lad['S2_pluscat'][0]:+.4f} "
           f"{lad['S2_pluscat'][1]} → +스테이지 {lad['S3_plusstage'][0]:+.4f} {lad['S3_plusstage'][1]}"
           f" (P001-03 재현 {'일치' if endpoint_ok else '불일치!'})"
           + (" — 1막 전시물 성립" if (s0sig or s1sig)
              else " — NA+EU 에 원 격차 부재: 헤드라인 서술 조정 필요 (정직 기록)"))

emit("P001-01b", "헤드라인 계단식 — ff 딜 exit_ever 셀 사다리 (E2 전시물, NA+EU)", status,
     {"ladder": lad, "endpoint_matches_p00103": bool(endpoint_ok), "n": int(len(d))},
     prediction="연도만·투자사×연도 −3~−7pp CI 배제; 단조 감쇠; 끝점 P001-03 일치",
     verdict=verdict, kill_met=False, n=int(len(d)),
     extra={"stage": 3, "feeds": "1막 전시물 (E2 사다리)", "slug": "headline_staircase",
            "inputs": "sample_v1 (NA+EU, ff=1)"})
print("done")
