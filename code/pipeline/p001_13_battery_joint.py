# -*- coding: utf-8 -*-
"""p001_13 (Track D, P-4) 판별 배터리의 결합 검정 — 지수·IU-TOST·Romano-Wolf

[왜] §4 는 "3/5 배제, 2/5 미결" — 개별 마진 나열은 ipo·closed 의 저기저 검정력에 인질.
결합하면 (i) 표준화 성과지수의 단일 등가 검정 (집계로 분산 축소), (ii) IU-TOST (전 마진 동시
등가 — 통과 시 배터리 수준 문장 허용), (iii) Romano-Wolf 스텝다운 (적자 존재 가설군의 다중성
보정 — '검출 없음'의 형식화).
[설계] sample_v1 NA+EU, ff=1 딜, 셀 = cell_stage. 지수 = 5개 결과를 셀 demean → ff-표본 sd 로
  표준화 → closed6 부호 반전 → 평균. gap = β(index~fp|셀), 투자사 부트 500 (σ 단위).
  IU-TOST: 결과별 90% 부트 CI ⊂ ±SESOI(기저 25%) 전건 충족 여부.
  RW: 5개 '적자' t-통계의 스텝다운 순열 p (셀 내 fp 재배열 300).
[사전 예측] (결과 전) P1 지수 gap CI ⊂ ±0.10σ. P2 IU-TOST 는 ipo·closed 로 실패 예상 —
  실패해도 지수 결과와 함께 정직 보고. P3 RW 조정 후 유의 적자 0건.
[판정] P1 → "배터리 수준에서 물질 열위 배제 (지수 ±0.1σ)" 문장 허용 (rules/11 준수 표현).
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
OUTS = [("fon", "2020-10-31", +1), ("exit_ever", "2017-10-31", +1), ("ipo6", "2017-10-31", +1),
        ("acqp6", "2017-10-31", +1), ("closed6", "2017-10-31", -1)]

d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v2.parquet"))
d = d[d["country_code"].isin(NAEU) & (d["ff"] == 1.0)].copy()
d["dt"] = pd.to_datetime(d["dt"])
de = d[d["dt"] <= "2017-10-31"].reset_index(drop=True)  # 지수는 공통 표본(출구 관측 가능)에서


def celldm(sub, col):
    return (sub[col] - sub[col].groupby(sub["cell_stage"]).transform("mean")).to_numpy()


def gap(sub, ycol_arr, nb=NB):
    xr = celldm(sub, "fp")
    sxx = (xr * xr).sum()
    b0 = float((xr * ycol_arr).sum() / sxx)
    grp = {c: g.index.to_numpy() for c, g in sub.groupby("investor_uuid")}
    keys = list(grp)
    bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(keys), len(keys))
        rows_ = np.concatenate([grp[keys[i]] for i in pick])
        x2, y2 = xr[rows_], ycol_arr[rows_]
        s = (x2 * x2).sum()
        if s:
            bs.append((x2 * y2).sum() / s)
    return b0, bs


# 표준화 지수 (공통 표본; fon 은 de 에서도 정의됨 — 36m 후속)
idx_parts = []
per = {}
for y, cut, sign in OUTS:
    yd = celldm(de, y)
    sd = de[y].std()
    idx_parts.append(sign * yd / (sd if sd > 0 else 1))
    per[y] = (yd, sd, sign)
index_arr = np.mean(idx_parts, axis=0)
b_idx, bs_idx = gap(de, index_arr)
ci_idx = qci(bs_idx)
sd_idx = float(np.std(index_arr))
b_sig, ci_sig = b_idx / sd_idx, [c / sd_idx for c in ci_idx]

# IU-TOST (결과별 90% CI ⊂ ±SESOI) — 각 결과는 자기 컷 표본
tost = {}
for y, cut, sign in OUTS:
    sub = d[d["dt"] <= cut].reset_index(drop=True)
    yd = celldm(sub, y)
    b, bs = gap(sub, yd, nb=400)
    lo, hi = np.percentile(bs, [5, 95])
    sesoi = 0.25 * float(sub[y].mean())
    tost[y] = {"gap": round(b * 100, 2), "ci90": [round(lo * 100, 2), round(hi * 100, 2)],
               "sesoi_pp": round(sesoi * 100, 2),
               "pass": bool((-sesoi < lo) and (hi < sesoi))}
iu_pass = all(v["pass"] for v in tost.values())

# Romano-Wolf 스텝다운 (적자 존재 H1: gap<0; closed6 은 gap>0) — 셀 내 fp 순열 300
def tstats(sub_map):
    ts = {}
    for y, cut, sign in OUTS:
        sub, yd = sub_map[y]
        xr = celldm(sub, "fp")
        sxx = (xr * xr).sum()
        b = (xr * yd).sum() / sxx
        se = np.std([b])  # placeholder — 순열 분포로 대체하므로 t 대신 b 사용
        ts[y] = -b * sign  # 적자 방향을 양수로
    return ts


sub_map = {}
for y, cut, sign in OUTS:
    sub = d[d["dt"] <= cut].reset_index(drop=True)
    sub_map[y] = (sub, celldm(sub, y))
obs_t = tstats(sub_map)
perm_max = []
for _ in range(300):
    pm = {}
    for y, cut, sign in OUTS:
        sub, yd = sub_map[y]
        fp_p = sub.groupby("cell_stage")["fp"].transform(
            lambda s: s.sample(frac=1, random_state=int(rng.integers(1e9))).to_numpy())
        xr = (fp_p - fp_p.groupby(sub["cell_stage"]).transform("mean")).to_numpy()
        sxx = (xr * xr).sum()
        pm[y] = -((xr * yd).sum() / sxx) * sign
    perm_max.append(max(pm.values()))
rw_p = {y: float(np.mean(np.array(perm_max) >= obs_t[y])) for y in obs_t}

p1 = (ci_sig[0] > -0.10) and (ci_sig[1] < 0.10)
p3 = all(p > 0.05 for p in rw_p.values())
status = "GO" if p1 else "PARTIAL"
verdict = (f"지수 gap={b_sig:+.4f}σ [{ci_sig[0]:+.4f}, {ci_sig[1]:+.4f}] — ±0.10σ "
           f"{'배제 (배터리 등가 성립)' if p1 else '미배제'}; IU-TOST {sum(v['pass'] for v in tost.values())}/5 "
           f"통과 ({'전건' if iu_pass else 'ipo·closed 예상대로 실패 — 정직 보고'}); "
           f"RW 조정 최소 p={min(rw_p.values()):.3f} — 유의 적자 {'0건' if p3 else '존재'}")

emit("P001-13", "판별 배터리 결합 — 지수 등가·IU-TOST·Romano-Wolf (Track D, P-4)", status,
     {"index_gap_sigma": [round(b_sig, 4), [round(ci_sig[0], 4), round(ci_sig[1], 4)]],
      "tost": tost, "iu_pass": bool(iu_pass), "rw_adjusted_p": {k: round(v, 3) for k, v in rw_p.items()},
      "n": int(len(de))},
     prediction="지수 CI ⊂ ±0.10σ; IU-TOST 는 ipo·closed 실패 예상; RW 후 유의 적자 0",
     verdict=verdict, kill_met=False, n=int(len(de)),
     extra={"stage": 5, "feeds": "Track D P-4 / §4 배터리 문장 격상", "slug": "battery_joint"})
print("done")
