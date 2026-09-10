# -*- coding: utf-8 -*-
"""p001_10 (Track B/C-①) 원 격차 위치의 정본 사다리 — GLOBAL·NA+EU·OTHER × 셀 4단 (D012)

[왜] 리뷰: Table 3 의 축 CI 가 기계 산출물 미추적(인라인 진단 출신) + 표본 불일치 훅.
이 스크립트가 격차 위치의 **유일 정본**: ff 딜 exit_ever 를 지역 3개 × 셀 사다리 4단으로
단일 런에서 산출. C107/C108 재지정 대상.
[사전 예측] (결과 전, 2026-09-04) 글로벌 섹터 셀 −5~−7pp CI 0 배제 (I-78 재현); NA+EU 섹터 셀
음의 점추정·0 미배제 (P001-01b 재현); 스테이지 셀에서 전 지역 0 미배제.
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

d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v1.parquet"))
d["dt"] = pd.to_datetime(d["dt"])
d = d[(d["ff"] == 1.0) & (d["dt"] <= "2017-10-31")].copy()
d["cell_year"] = d["year"]
d["reg"] = np.where(d["country_code"].isin({"USA", "CAN"} | EU), "NAEU", "OTHER")


def gap(df, cell, nb=NB):
    dd = df[["exit_ever", "fp", cell, "investor_uuid"]].reset_index(drop=True)
    yr = (dd["exit_ever"] - dd["exit_ever"].groupby(dd[cell]).transform("mean")).to_numpy()
    xr = (dd["fp"] - dd["fp"].groupby(dd[cell]).transform("mean")).to_numpy()
    sxx = (xr * xr).sum()
    if sxx == 0 or len(dd) < 300:
        return [None, [None, None], int(len(dd))]
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
    return [round(beta, 4), qci(bs), int(len(dd))]


CELLS = [("year", "cell_year"), ("invyear", "cell0"), ("pluscat", "cell_cat"),
         ("plusstage", "cell_stage")]
out = {}
for scope, df in (("GLOBAL", d), ("NAEU", d[d["reg"] == "NAEU"]), ("OTHER", d[d["reg"] == "OTHER"])):
    out[scope] = {name: gap(df, cell) for name, cell in CELLS}

g_cat = out["GLOBAL"]["pluscat"]
n_cat = out["NAEU"]["pluscat"]
p1 = g_cat[1][1] is not None and g_cat[1][1] < 0
status = "GO" if p1 else "PARTIAL"
verdict = (f"GLOBAL: year {out['GLOBAL']['year'][0]} → invyear {out['GLOBAL']['invyear'][0]} → "
           f"+cat {g_cat[0]} {g_cat[1]} → +stage {out['GLOBAL']['plusstage'][0]} "
           f"{out['GLOBAL']['plusstage'][1]}; NAEU +cat {n_cat[0]} {n_cat[1]}; "
           f"OTHER +cat {out['OTHER']['pluscat'][0]} {out['OTHER']['pluscat'][1]} — "
           + ("정본 사다리 확정 (C107/C108 재지정)" if p1 else "글로벌 섹터 셀 미배제 — 훅 재검토"))

emit("P001-10", "원 격차 위치 정본 사다리 — 지역×셀 (D012, Table 3 유일 소스)", status,
     {"ladder": out},
     prediction="글로벌 +cat −5~−7pp CI 배제; NAEU +cat 0 미배제; +stage 전 지역 0 미배제",
     verdict=verdict, kill_met=False, n=int(len(d)),
     extra={"stage": 5, "feeds": "Table 3 정본 / C107·C108", "slug": "gap_ladder"})
print("done")
