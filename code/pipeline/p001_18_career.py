# -*- coding: utf-8 -*-
"""p001_18 (Track C-⑦) 커리어 검정 — 시장은 원시 트랙레코드를 가격에 반영하는가 (finance 심판 #3)

[왜] Table 7(랭킹 왜곡)의 전제 = 시장이 배치-맹 원시 지표를 사용. 직접 검정: 파트너의
**미래 딜플로우**(회사가 파트너에게 배정하는 자본의 프록시) 가 조정 랭크를 통제한 뒤에도
원시 랭크에 반응하는가. β_raw|adj > 0 → 오염된 통계량이 실제로 가격에 반영됨.
[설계] 파트너 (딜 ≥5, dt≤2017-10; P001-05 구성 재사용): raw_pct·adj_pct (P001-05 정의).
  y = log1p(2017-11~2020-10 귀속 딜 수). OLS: y ~ raw_pct + adj_pct + log(n_deals) + fp
  (+ 최빈 투자사 FE 는 표본 축소가 커서 미사용 — 군집만 최빈 투자사). 부트 400.
[사전 예측] (결과 전, 2026-09-04) P1 β_raw|adj > 0, CI 0 배제 (10 백분위점당 미래 딜 +2% 이상).
  P2 β_adj|raw 는 β_raw 보다 작거나 유사 — 시장이 조정 정보를 완전히 쓰지 못함의 지문.
[판정] P1 → Table 7 이 "산술"에서 "가격 반영 증거"로 격상 (§6.1 재작성). 실패 →
  "시장 사용 여부는 미검출" 정직 기록, Table 7 은 측정 따름정리로 제시.
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
NAEU = EU | {"USA", "CAN"}
MIN_DEALS = 5

d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v2.parquet"))
d["dt"] = pd.to_datetime(d["dt"])
dn = d[d["country_code"].isin(NAEU)]
hist = dn[dn["dt"] <= "2017-10-31"].copy()
fut = dn[(dn["dt"] > "2017-10-31") & (dn["dt"] <= "2020-10-31")]
hist["mcell"] = hist["year"] + "|" + hist["cat"] + "|" + hist["stage"]
hist["resid"] = hist["exit_ever"] - hist.groupby("mcell")["exit_ever"].transform("mean")
P = hist.groupby("partner_uuid").agg(raw=("exit_ever", "mean"), adj=("resid", "mean"),
                                     n=("exit_ever", "size"), fp=("fp", "first"),
                                     firm=("investor_uuid", lambda s: s.mode().iloc[0])).reset_index()
P = P[P["n"] >= MIN_DEALS].reset_index(drop=True)
fut_n = fut.groupby("partner_uuid").size()
P["y"] = np.log1p(P["partner_uuid"].map(fut_n).fillna(0))
P["raw_pct"] = P["raw"].rank(pct=True)
P["adj_pct"] = P["adj"].rank(pct=True)
P["ln_n"] = np.log(P["n"])

X_cols = ["raw_pct", "adj_pct", "ln_n", "fp"]


def ols(df):
    X = np.column_stack([df[c].to_numpy(float) for c in X_cols] + [np.ones(len(df))])
    b = np.linalg.lstsq(X, df["y"].to_numpy(float), rcond=None)[0]
    return b[:2]


b0 = ols(P)
grp = {c: g.index.to_numpy() for c, g in P.groupby("firm")}
keys = list(grp)
bs = []
for _ in range(NB):
    pick = rng.integers(0, len(keys), len(keys))
    sub = P.loc[np.concatenate([grp[keys[i]] for i in pick])]
    try:
        bs.append(ols(sub))
    except Exception:
        pass
bs = np.array(bs)
ci_raw, ci_adj = qci(bs[:, 0]), qci(bs[:, 1])
b_raw, b_adj = round(float(b0[0]), 4), round(float(b0[1]), 4)

p1 = ci_raw[0] > 0
status = "GO" if p1 else "PARTIAL"
verdict = (f"미래 딜플로우 ~ 원시랭크 β={b_raw:+.3f} {ci_raw} (조정랭크 통제 하) — "
           + ("**원시 지표가 가격에 반영됨**: Table 7 을 산술→증거로 격상" if p1
              else "가격 반영 미검출 — Table 7 은 측정 따름정리로 제시 (정직 기록)")
           + f"; 조정랭크 β={b_adj:+.3f} {ci_adj}; 파트너 {len(P):,} (여성 {int((P.fp==1).sum())})")

emit("P001-18", "커리어 검정 — 원시 vs 조정 랭크의 미래 딜플로우 가격 반영 (Track C-⑦)", status,
     {"beta_raw_given_adj": [b_raw, ci_raw], "beta_adj_given_raw": [b_adj, ci_adj],
      "n_partners": int(len(P)), "n_female": int((P["fp"] == 1).sum()),
      "mean_future_deals": round(float(np.expm1(P['y']).mean()), 2)},
     prediction="β_raw|adj > 0 CI 배제; β_adj ≤ β_raw",
     verdict=verdict, kill_met=False, n=int(len(P)),
     extra={"stage": 5, "feeds": "finance#3 / §6.1·Table 7 격상 판정", "slug": "career"})
print("done")
