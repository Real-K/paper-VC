# -*- coding: utf-8 -*-
"""p001_01 GMWX 계단식 (H7) — 전체 딜의 fp 성과 격차: 가법 통제 vs 완전 셀 (NA+EU, sample_v1)

[왜] GAP_MAP G1 / R8: GMWX(JFQA 2022)는 가법 통제(산업·스테이지·회사) 후에도 여성 파트너 딜
성공률 열위를 보고. 우리 주장: 가법 통제는 배치를 못 잡는다 — 완전 상호작용 셀에서 격차 소멸.
계단식 표가 문헌 불일치의 해명 전시물 (1막).
[설계] sample_v1, NA+EU (D007). 전체 딜(창업자 성별 불문). y = exit6 (dt≤2017-10) · fon (≤2020-10).
  s0 연도만 / s1 가법: 연도+투자사+섹터+스테이지 (반복 demean) / s2 완전 셀 투자사×연도×섹터×스테이지.
  투자사 군집 부트 500.
[사전 예측] (결과 전, 2026-09-03 — H7 등록분)
  P1 exit6: s0·s1 에서 fp 격차 −1.5~−4pp, CI 0 배제 (GMWX 방향 재현).
  P2 s2 에서 s1 대비 ≥60% 감쇠, CI 0 포함 가능.
  P3 fon 도 동일 패턴 (크기 작게).
[판정] P1+P2 → H7 지지 (GO). s1 에서 이미 null 이면 GMWX 재현 실패 — 데이터·기간 차이로 정직
  기록 (PARTIAL, 계단식 서사 약화). s2 에서도 유의 잔존 → 배치 서사 수정 필요 (PARTIAL).
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
d = d[d["country_code"].isin(NAEU)].copy()
d["dt"] = pd.to_datetime(d["dt"])
d["g_year"] = d["year"]
d["g_inv"] = d["investor_uuid"]
d["g_cat"] = d["cat"]
d["g_stage"] = d["stage"]


def fwl_multi(df, y, x, groups, nb=NB, iters=8):
    dd = df[[y, x, "investor_uuid"] + groups].reset_index(drop=True)
    yv = dd[y].astype(float).copy()
    xv = dd[x].astype(float).copy()
    for _ in range(iters if len(groups) > 1 else 1):
        for g in groups:
            yv = yv - yv.groupby(dd[g]).transform("mean")
            xv = xv - xv.groupby(dd[g]).transform("mean")
    yr, xr = yv.to_numpy(), xv.to_numpy()
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
    return beta, qci(bs), int(len(dd))


res = {}
for yname, dsub in (("exit6", d[d["dt"] <= "2017-10-31"]), ("fon", d[d["dt"] <= "2020-10-31"])):
    b0, c0, n0 = fwl_multi(dsub, yname, "fp", ["g_year"])
    b1, c1, _ = fwl_multi(dsub, yname, "fp", ["g_year", "g_inv", "g_cat", "g_stage"])
    dsub = dsub.assign(cell=dsub["investor_uuid"] + "|" + dsub["year"] + "|" + dsub["cat"] + "|" + dsub["stage"])
    b2, c2, _ = fwl_multi(dsub, yname, "fp", ["cell"])
    att = (1 - b2 / b1) if (b1 and not np.isnan(b1)) else float("nan")
    res[yname] = {"s0_year": [round(b0, 4), c0], "s1_additive": [round(b1, 4), c1],
                  "s2_fullcell": [round(b2, 4), c2], "attenuation_s1_to_s2": round(float(att), 3),
                  "n": n0}

e = res["exit6"]
p1 = e["s1_additive"][1][1] < 0                       # 가법에서 유의 음
p2 = (not np.isnan(e["attenuation_s1_to_s2"])) and (e["attenuation_s1_to_s2"] >= 0.60 or
      (e["s2_fullcell"][1][0] <= 0 <= e["s2_fullcell"][1][1]))
status = "GO" if (p1 and p2) else "PARTIAL"
verdict = (f"exit6: 연도만 {e['s0_year'][0]:+.4f} {e['s0_year'][1]} → 가법 {e['s1_additive'][0]:+.4f} "
           f"{e['s1_additive'][1]} → 완전셀 {e['s2_fullcell'][0]:+.4f} {e['s2_fullcell'][1]} "
           f"(감쇠 {e['attenuation_s1_to_s2']*100:.0f}%); "
           f"fon: {res['fon']['s1_additive'][0]:+.4f} → {res['fon']['s2_fullcell'][0]:+.4f}"
           + (" — H7 지지: 가법 잔존·셀 소멸 (GMWX 해명 전시물 성립)" if (p1 and p2)
              else " — 계단식 예측 부분 불일치: 정직 기록"))

emit("P001-01", "GMWX 계단식 — 가법 통제 vs 완전 셀 (H7, NA+EU)", status, res,
     prediction="가법에서 −1.5~−4pp 유의; 완전 셀에서 ≥60% 감쇠 또는 CI 0 포함; fon 동일 패턴",
     verdict=verdict, kill_met=False, n=e["n"],
     extra={"stage": 3, "feeds": "H7 / 1막 전시물", "slug": "gmwx_staircase",
            "inputs": "sample_v1 (NA+EU)"})
print("done")
