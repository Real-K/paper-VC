# -*- coding: utf-8 -*-
"""p001_15 (Track C-②) 가법 통제 vs 완전 셀 — ff 딜 헤드라인 사양의 문자 그대로 대비 (R8)

[왜] 리뷰: "additive ≠ cells" 주장을 자기 데이터에서 문자 그대로 보여야 GMWX 접속이 성립.
P001-01 은 전체-딜(그들 estimand)에서 격차 자체가 부재 — 여기서는 **우리 헤드라인**(ff 딜
exit_ever)을 가법 FE(투자사+연도+섹터+스테이지 각각) vs 완전 상호작용 셀로 대비.
[사전 예측] (결과 전, 2026-09-04) 글로벌: 가법 −3~−6pp (섹터셀 −6.25 와 동방향·유의 가능),
완전 셀 −1~−2pp·0 미배제 — "가법 통제는 배치를 못 잡는다"의 직접 증거. NA+EU 동일 패턴·약하게.
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
NB = 400
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR",
      "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}

d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v1.parquet"))
d["dt"] = pd.to_datetime(d["dt"])
d = d[(d["ff"] == 1.0)].copy()
d["reg"] = np.where(d["country_code"].isin({"USA", "CAN"} | EU), "NAEU", "OTHER")
d["g_inv"], d["g_yr"], d["g_cat"], d["g_stg"] = d["investor_uuid"], d["year"], d["cat"], d["stage"]


def fwl(df, y, mode, nb=NB):
    dd = df.reset_index(drop=True)
    yv = dd[y].astype(float).copy()
    xv = dd["fp"].astype(float).copy()
    if mode == "additive":
        for _ in range(10):
            for g in ("g_inv", "g_yr", "g_cat", "g_stg"):
                yv = yv - yv.groupby(dd[g]).transform("mean")
                xv = xv - xv.groupby(dd[g]).transform("mean")
    else:
        yv = yv - yv.groupby(dd["cell_stage"]).transform("mean")
        xv = xv - xv.groupby(dd["cell_stage"]).transform("mean")
    yr, xr = yv.to_numpy(), xv.to_numpy()
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
    return [round(beta, 4), qci(bs), int(len(dd))]


out = {}
for scope, df0 in (("GLOBAL", d), ("NAEU", d[d["reg"] == "NAEU"])):
    de = df0[df0["dt"] <= "2017-10-31"]
    dfo = df0[df0["dt"] <= "2020-10-31"]
    out[scope] = {"exit_additive": fwl(de, "exit_ever", "additive"),
                  "exit_fullcell": fwl(de, "exit_ever", "cell"),
                  "fon_additive": fwl(dfo, "fon", "additive"),
                  "fon_fullcell": fwl(dfo, "fon", "cell")}

ga = out["GLOBAL"]["exit_additive"]
gc = out["GLOBAL"]["exit_fullcell"]
contrast_holds = (ga[1][1] < 0) and (gc[1][0] <= 0 <= gc[1][1])
status = "GO" if contrast_holds else "PARTIAL"
verdict = (f"GLOBAL exit: 가법 {ga[0]} {ga[1]} vs 완전셀 {gc[0]} {gc[1]}; "
           f"NAEU exit: 가법 {out['NAEU']['exit_additive'][0]} {out['NAEU']['exit_additive'][1]} vs "
           f"셀 {out['NAEU']['exit_fullcell'][0]} {out['NAEU']['exit_fullcell'][1]}"
           + (" — '가법 잔존·셀 소멸' 문자 그대로 성립 (R8 해명 전시물)" if contrast_holds
              else " — 대비 부분 성립: 정직 기록"))

emit("P001-15", "가법 통제 vs 완전 셀 — ff 딜 계단식 (Track C-②, R8)", status, out,
     prediction="글로벌 가법 −3~−6 유의 가능; 완전 셀 0 미배제; NAEU 동일 패턴 약하게",
     verdict=verdict, kill_met=False, n=ga[2],
     extra={"stage": 5, "feeds": "R8 / §4 전시물", "slug": "gmwx_staircase_ff"})
print("done")
