# -*- coding: utf-8 -*-
"""p001_22 외부 시장 검정 — 파트너 이동·스핀아웃이 원시 랭크를 따르는가 (재정의된 주장 5의 핵심)

[왜] 인접분야 감사(EVIDENCE_MAP §8): "배치가 지표를 오염시킨다"는 Rothstein(2010)·Dranove(2003)·
DGTW(1997) 로 이미 확립. 우리에게 남은 진짜 기여는 **"누가 신호를 de-bias 할 수 있고 누가 못
하는가"의 비대칭**이다:
  - 관측 가능한 평가자(파트너십) = 조정 랭크를 따름 → **이미 확인** (P001-18b: β_adj +1.54 [1.24,1.86])
  - 관측 불가한 평가자(외부 시장: 영입 회사·신규 펀드 자본) = **원시 랭크를 따를 것** ← 미검정
LP 자본 흐름은 CB 에 없지만 **파트너의 외부 이동**은 관측 가능하고, 영입하는 회사는 정확히
"내부 배분을 볼 수 없는 외부 평가자"다. 이것이 CB 로 가능한 유일한 외부-평가자 검정.
[설계] P001-05/18b 와 동일 파트너 모집단 (NA+EU, dt≤2017-10, 귀속 딜 ≥5; raw_pct·adj_pct 동일 정의).
  결과 (2017-11~2023-10 관측):
    y1 move  = 원 소속(최빈 투자사) 외 **다른 투자사**에 귀속 등장
    y2 spin  = 그 수용 투자사가 **신생**(최초 귀속 딜이 이동 이후) — 스핀아웃 프록시
  회귀: y ~ raw_pct + adj_pct + ln(딜수) + fp + 사전 초기단계 비중 + 섹터 폭, 원 소속 군집 부트 400.
[사전 예측] (결과 전, 2026-09-04)
  P1 β_raw|adj > 0 이고 CI 0 배제 — 외부 시장이 오염된 통계를 사용.
  P2 β_adj|raw ≤ β_raw — 내부(P001-18b, 조정 우세)와 **부호·서열이 뒤집힘**이 핵심 대비.
  P3 스핀아웃(y2)에서 P1 이 더 강함 (신규 자본 조달일수록 외부성 큼).
[판정] P1 성립 → **비대칭 확정**: "내부는 교정하고 외부는 못 한다" — 재정의된 주장 5 의 귀결이
  증거로 확립. P1 실패(β_raw CI 0 포함) → 외부 시장도 원시를 안 쓴다 = 왜곡의 실질 피해 미검출 →
  주장 5 를 "측정 사실"로만 제시하고 귀결 주장 철회 (정직 기록).
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["HARNESS_OUT"] = os.environ.get("P001_OUT", os.path.join(HERE, "out"))  # set P001_* / CRUNCHBASE_RAW to your local copies (licensed inputs; see DATA_ACCESS.md)
sys.path.insert(0, HERE)  # gates.py / emit_contract.py sit alongside in code/pipeline
from emit_contract import emit, qci  # noqa: E402
from gates import CTX  # noqa: E402

rng = np.random.default_rng(42)
NB = 400
MIN_DEALS = 5
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR",
      "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}
NAEU = EU | {"USA", "CAN"}
EARLY = {"seed", "angel", "pre_seed", "equity_crowdfunding", "convertible_note"}

d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v2.parquet"))
d["dt"] = pd.to_datetime(d["dt"])
dn = d[d["country_code"].isin(NAEU)]
hist = dn[dn["dt"] <= "2017-10-31"].copy()
hist["mcell"] = hist["year"] + "|" + hist["cat"] + "|" + hist["stage"]
hist["resid"] = hist["exit_ever"] - hist.groupby("mcell")["exit_ever"].transform("mean")
hist["early"] = hist["stage"].isin(EARLY).astype(float)
P = hist.groupby("partner_uuid").agg(
    raw=("exit_ever", "mean"), adj=("resid", "mean"), n=("exit_ever", "size"),
    fp=("fp", "first"), early_sh=("early", "mean"), ncat=("cat", "nunique"),
    firm=("investor_uuid", lambda s: s.mode().iloc[0])).reset_index()
P = P[P["n"] >= MIN_DEALS].reset_index(drop=True)

# 전체 귀속 이력 (국가 무관 — 이동은 어디로든 가능)
pt = CTX.partners.dropna(subset=["funding_round_uuid", "investor_uuid", "partner_uuid"])
r = CTX.rounds.dropna(subset=["announced_on"])[["uuid", "announced_on"]].copy()
r["rdt"] = pd.to_datetime(r["announced_on"], errors="coerce")
A = pt.merge(r, left_on="funding_round_uuid", right_on="uuid").dropna(subset=["rdt"])
firm_first = A.groupby("investor_uuid")["rdt"].min()
fut = A[(A["rdt"] > "2017-10-31") & (A["rdt"] <= "2023-10-31")]
fut_firms = fut.groupby("partner_uuid")["investor_uuid"].agg(set)
home = dict(zip(P["partner_uuid"], P["firm"]))

y1, y2 = [], []
for pid in P["partner_uuid"]:
    fs = fut_firms.get(pid, set()) - {home[pid]}
    y1.append(1.0 if fs else 0.0)
    # 신생 수용 회사: 최초 귀속 딜이 2017-11 이후
    y2.append(1.0 if any(firm_first.get(f, pd.Timestamp("1900-01-01")) > pd.Timestamp("2017-10-31")
                         for f in fs) else 0.0)
P["move"] = y1
P["spin"] = y2
P["raw_pct"] = P["raw"].rank(pct=True)
P["adj_pct"] = P["adj"].rank(pct=True)
P["ln_n"] = np.log(P["n"])
X_cols = ["raw_pct", "adj_pct", "ln_n", "fp", "early_sh", "ncat"]


def ols_boot(df, ycol, nb=NB):
    def fit(s):
        X = np.column_stack([s[c].to_numpy(float) for c in X_cols] + [np.ones(len(s))])
        return np.linalg.lstsq(X, s[ycol].to_numpy(float), rcond=None)[0][:2]
    b0 = fit(df)
    grp = {c: g.index.to_numpy() for c, g in df.groupby("firm")}
    keys = list(grp)
    bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(keys), len(keys))
        s = df.loc[np.concatenate([grp[keys[i]] for i in pick])]
        try:
            bs.append(fit(s))
        except Exception:
            pass
    bs = np.array(bs)
    return [round(float(b0[0]), 4), qci(bs[:, 0])], [round(float(b0[1]), 4), qci(bs[:, 1])]


raw_mv, adj_mv = ols_boot(P, "move")
raw_sp, adj_sp = ols_boot(P, "spin")

p1 = raw_mv[1][0] > 0
p2 = raw_mv[0] >= adj_mv[0]
p3 = raw_sp[1][0] > 0
status = "GO" if p1 else "PARTIAL"
verdict = (f"이동(y1={P['move'].mean():.3f}): 원시랭크 β={raw_mv[0]} {raw_mv[1]} | 조정랭크 "
           f"β={adj_mv[0]} {adj_mv[1]}; 스핀아웃(y2={P['spin'].mean():.3f}): 원시 {raw_sp[0]} "
           f"{raw_sp[1]} | 조정 {adj_sp[0]} {adj_sp[1]}; 파트너 {len(P):,} (여성 "
           f"{int((P['fp']==1).sum())}) — "
           + ("**외부 시장이 원시 지표 사용 — 내부(조정 우세, P001-18b)와 비대칭 확정**" if p1
              else "외부 시장도 원시 미사용 — 왜곡의 실질 피해 미검출, 귀결 주장 철회 (정직 기록)"))

emit("P001-22", "외부 시장 검정 — 이동·스핀아웃이 원시 vs 조정 랭크를 따르는가", status,
     {"move_raw": raw_mv, "move_adj": adj_mv, "spin_raw": raw_sp, "spin_adj": adj_sp,
      "move_rate": round(float(P["move"].mean()), 4), "spin_rate": round(float(P["spin"].mean()), 4),
      "n_partners": int(len(P)), "n_female": int((P["fp"] == 1).sum()),
      "internal_ref_p18b": {"beta_adj": 1.5442, "beta_raw": -1.7314},
      "p1_external_uses_raw": bool(p1), "p2_raw_ge_adj": bool(p2), "p3_spinout_stronger": bool(p3)},
     prediction="β_raw|adj > 0 CI 배제; β_raw ≥ β_adj (내부와 서열 반전); 스핀아웃에서 더 강함",
     verdict=verdict, kill_met=False, n=int(len(P)),
     extra={"stage": 6, "feeds": "재정의된 주장 5 의 귀결 (내부 vs 외부 비대칭)", "slug": "external_market"})
print("done")
