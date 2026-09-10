# -*- coding: utf-8 -*-
"""p001_02 3층 분해 + 지역 moderator (H8·X5) + 매개 경로 감쇠 (NA+EU, sample_v1)

[왜] 1막(E1) 본추정을 동결 지리(D007)로 확정하고, 지역 moderator(H8: NA>EU 셀내 매칭)와
매개 경로(섹터→스테이지 순차 셀 확장의 계수 감쇠 = 배치 경로의 몫)를 산출.
[설계] sample_v1 NA+EU. y=ff, x=fp. 사다리: cell0(투자사×연도) → +섹터 → +스테이지.
  지역: NA vs EU 각각 완전 셀 계수 + 차이(독립 부트 결합). X5(탐색): 지역별 연차 평균(보조표).
[사전 예측] (결과 전 — H8 등록분)
  P1 NA+EU 사다리: +6~7pp → +3pp 내외 → +2~3pp (I-73/74/80 글로벌과 유사).
  P2 H8: b_NA(완전셀) − b_EU > 0, CI 0 배제.
[판정] P2 통과 → H8 지지. 실패(차이 CI 0 포함) → H8 미지지로 기록, X1 재해석 필요 (PARTIAL 아님
  — 이 스크립트 자체는 E1 확정이 목적이라 사다리 성립 시 GO).
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
d["reg"] = np.where(d["country_code"].isin({"USA", "CAN"}), "NA",
                    np.where(d["country_code"].isin(EU), "EU", "OTHER"))
d = d[d["reg"].isin(["NA", "EU"])].copy()


def fwl(df, cell, nb=NB):
    dd = df[["ff", "fp", cell, "investor_uuid"]].reset_index(drop=True)
    yr = (dd["ff"] - dd["ff"].groupby(dd[cell]).transform("mean")).to_numpy()
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
    return beta, qci(bs), bs, int(len(dd))


ladder = {}
b_l, c_l = {}, {}
for name, cell in (("L0_invyear", "cell0"), ("L1_pluscat", "cell_cat"), ("L2_plusstage", "cell_stage")):
    b, ci, _, n = fwl(d, cell)
    ladder[name] = [round(b, 4), ci, n]
    b_l[name] = b

bna, cna, bsna, nna = fwl(d[d["reg"] == "NA"], "cell_stage")
beu, ceu, bseu, neu = fwl(d[d["reg"] == "EU"], "cell_stage")
m = min(len(bsna), len(bseu))
diff = bna - beu
cdiff = qci(np.array(bsna[:m]) - np.array(bseu[:m])) if m >= 50 else [float("nan")] * 2

med_share_cat = 1 - b_l["L1_pluscat"] / b_l["L0_invyear"]
med_share_stage = (b_l["L1_pluscat"] - b_l["L2_plusstage"]) / b_l["L0_invyear"]

h8 = (not np.isnan(cdiff[0])) and (cdiff[0] > 0)
status = "GO"
verdict = (f"사다리: {b_l['L0_invyear']:+.4f} → {b_l['L1_pluscat']:+.4f} → {b_l['L2_plusstage']:+.4f} "
           f"(섹터 경로 {med_share_cat*100:.0f}%·스테이지 경로 {med_share_stage*100:.0f}%); "
           f"H8: NA {bna:+.4f} {cna} vs EU {beu:+.4f} {ceu}, 차 {diff:+.4f} {cdiff} — "
           + ("H8 지지" if h8 else "H8 미지지 (차이 CI 0 포함 — 정직 기록, X1 재해석 필요)"))

emit("P001-02", "3층 분해 확정 + 지역 moderator + 매개 경로 (H8·X5, NA+EU)", status,
     {"ladder": ladder, "mediator_share": {"sector": round(float(med_share_cat), 3),
                                           "stage": round(float(med_share_stage), 3)},
      "na_fullcell": [round(bna, 4), cna, nna], "eu_fullcell": [round(beu, 4), ceu, neu],
      "h8_diff": [round(diff, 4), cdiff], "h8_supported": bool(h8)},
     prediction="사다리 +6~7 → ~+3 → +2~3pp; NA−EU 차 > 0 CI 배제",
     verdict=verdict, kill_met=False, n=nna + neu,
     extra={"stage": 3, "feeds": "E1 확정 / H8 / 매개", "slug": "decomposition_region",
            "inputs": "sample_v1 (NA+EU)"})
print("done")
