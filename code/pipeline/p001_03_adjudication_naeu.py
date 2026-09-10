# -*- coding: utf-8 -*-
"""p001_03 판별 배터리 확정 (E2) — NA+EU·스테이지 셀·5개 결과 + MDE 표 (sample_v1)

[왜] E2(호의 vs 선별)를 동결 지리(D007)·동결 셀(투자사×연도×섹터×스테이지)로 확정하고,
판별 불능 마진의 정직 보고용 MDE 표를 산출 (PRE_ANALYSIS_PLAN 3번).
[설계] sample_v1 NA+EU, ff=1 딜. y ∈ {fon(≤2020-10), exit_ever·ipo6·acqp6·closed6(≤2017-10)}.
  SESOI = ff 기저율의 25% (하방 closed6 은 +25%); fon 절대 하한 −5pp 도 병기. 부트 500 → MDE80=2.8·SE.
[사전 예측] (결과 전) P1 fon 하한 > −5pp 유지 (글로벌 I-80 +0.84 [−1.66,+3.34] 와 유사).
  P2 exit_ever 스테이지 셀에서 0 포함 (글로벌 −1.75 ns 와 유사). P3 유의한 물질 열위 미검출.
[판정] P1 유지 → E2 확정 (GO). P1 실패 → 판별 재검토 (PARTIAL). 전 결과 원장 §8.
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

d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v1.parquet"))
d = d[d["country_code"].isin(NAEU) & (d["ff"] == 1.0)].copy()
d["dt"] = pd.to_datetime(d["dt"])


def gap(df, y, nb=NB):
    dd = df[[y, "fp", "cell_stage", "investor_uuid"]].reset_index(drop=True)
    yr = (dd[y] - dd[y].groupby(dd["cell_stage"]).transform("mean")).to_numpy()
    xr = (dd["fp"] - dd["fp"].groupby(dd["cell_stage"]).transform("mean")).to_numpy()
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
    base = float(dd[y].mean())
    se = float(np.nanstd(np.asarray(bs, float)))
    return beta, qci(bs), base, round(2.8 * se * 100, 2), int(len(dd))


out = {}
for y, downside, dfy in (("fon", False, d[d["dt"] <= "2020-10-31"]),
                         ("exit_ever", False, d[d["dt"] <= "2017-10-31"]),
                         ("ipo6", False, d[d["dt"] <= "2017-10-31"]),
                         ("acqp6", False, d[d["dt"] <= "2017-10-31"]),
                         ("closed6", True, d[d["dt"] <= "2017-10-31"])):
    b, ci, base, mde, n = gap(dfy, y)
    sesoi = 0.25 * base
    excluded = (ci[1] < sesoi) if downside else (ci[0] > -sesoi)
    out[y] = {"gap_ff": round(b, 4), "ci": ci, "base": round(base, 4),
              "sesoi": round(sesoi, 4), "mde80_pp": mde, "excluded": bool(excluded), "n": n}

p1 = out["fon"]["ci"][0] > -0.05
p3 = not any((v["ci"][1] < 0 and -v["gap_ff"] >= v["sesoi"]) for k, v in out.items() if k != "closed6")
status = "GO" if p1 else "PARTIAL"
verdict = ("; ".join(f"{k} {v['gap_ff']:+.4f} {v['ci']} (MDE {v['mde80_pp']}pp, "
                     f"{'배제' if v['excluded'] else '미배제'})" for k, v in out.items())
           + (" — E2 확정: 후속 마진 호의 배제 유지" if p1 else " — fon 하한 붕괴: 판별 재검토"))

emit("P001-03", "판별 배터리 확정 + MDE 표 (E2, NA+EU 스테이지 셀)", status,
     {**out, "p1_fon_floor": bool(p1), "p3_no_material_deficit": bool(p3)},
     prediction="fon 하한 > −5pp; exit_ever CI 0 포함; 유의 물질 열위 미검출",
     verdict=verdict, kill_met=False, n=out["fon"]["n"],
     extra={"stage": 3, "feeds": "E2 확정 / MDE 표", "slug": "adjudication_naeu",
            "inputs": "sample_v1 (NA+EU, ff=1)"})
print("done")
