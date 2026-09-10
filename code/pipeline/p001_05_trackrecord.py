# -*- coding: utf-8 -*-
"""p001_05 귀결 A — 트랙레코드 랭킹 왜곡: 원시 vs 배치조정 파트너 랭킹 (NA+EU, sample_v1)

[왜] 3막 A (GAP_MAP G3): 시장·회사는 파트너를 원시 트랙레코드(내 딜의 출구율)로 평가한다
(E-RK JF 2015: 인적자본이 핵심 자산; I-L JFE 2019: 평가→캐리·펀드레이징). 그런데 1막이 보인
대로 원시 출구율은 배치(연도×섹터×스테이지)에 오염된다 → 평가 지표 자체가 여성 파트너를
체계적으로 낮게 랭킹하는지 정량화. **배치가 차별적이든(배정) 아니든(연차·스타일) 성립하는
귀결** — 2막 결과에 논문이 걸리지 않게 하는 설계 그대로.
[설계] sample_v1 NA+EU, dt≤2017-10(출구 관측 확보), exit_ever. 딜 ≥5 인 파트너.
  원시 점수 = 파트너별 평균 exit_ever.
  조정 점수 = 파트너별 평균 (exit_ever − 시장 셀 평균), 셀 = 연도×섹터×스테이지
  (평가는 회사 간 비교이므로 시장 벤치마크 셀 — 투자사 셀 아님).
  지표: ① 여성 파트너 평균 백분위 (원시 vs 조정, 차이) ② 상위 사분위 내 여성 비중 (원시 vs
  조정) ③ 랭킹 재배열 크기 (Spearman). 부트 = 파트너 재표집 500.
[사전 예측] (결과 전, 2026-09-03)
  P1 여성 평균 백분위: 조정 − 원시 = +1~+5 백분위점, CI 0 배제 (원시 지표가 여성을 하향).
  P2 상위 사분위 여성 비중: 조정에서 상승 (상대 +10% 이상).
  P3 남성 평균 백분위 변화는 반대 부호로 작게 (제로섬).
[판정] P1 통과 → 귀결 A 성립 (GO). CI ⊂ ±1점 → "지표 왜곡 미검출" 정직 기록 (PARTIAL —
  3막 A 는 약화되나 1·2막 성립 불변).
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
MIN_DEALS = 5
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR",
      "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}
NAEU = EU | {"USA", "CAN"}

d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v1.parquet"))
d["dt"] = pd.to_datetime(d["dt"])
d = d[d["country_code"].isin(NAEU) & (d["dt"] <= "2017-10-31")].copy()
d["mcell"] = d["year"] + "|" + d["cat"] + "|" + d["stage"]
d["resid"] = d["exit_ever"] - d.groupby("mcell")["exit_ever"].transform("mean")

pdeals = d.groupby("partner_uuid").agg(raw=("exit_ever", "mean"), adj=("resid", "mean"),
                                       n=("exit_ever", "size"), fp=("fp", "first")).reset_index()
P = pdeals[pdeals["n"] >= MIN_DEALS].reset_index(drop=True)


def metrics(df):
    r_pct = df["raw"].rank(pct=True) * 100
    a_pct = df["adj"].rank(pct=True) * 100
    f = df["fp"] == 1.0
    diff_f = float(a_pct[f].mean() - r_pct[f].mean())
    diff_m = float(a_pct[~f].mean() - r_pct[~f].mean())
    tq_r = float((r_pct[f] > 75).sum() / (r_pct > 75).sum())
    tq_a = float((a_pct[f] > 75).sum() / (a_pct > 75).sum())
    return diff_f, diff_m, tq_r, tq_a


d_f, d_m, tqr, tqa = metrics(P)
sp = float(P["raw"].rank().corr(P["adj"].rank()))  # 순위 Pearson = Spearman (scipy 불요)
bs = {"df": [], "dm": [], "dtq": []}
idx = np.arange(len(P))
for _ in range(NB):
    s = P.iloc[rng.integers(0, len(P), len(P))].reset_index(drop=True)
    a, b, c, e = metrics(s)
    bs["df"].append(a)
    bs["dm"].append(b)
    bs["dtq"].append(e - c)
ci_df, ci_dm, ci_dtq = qci(bs["df"]), qci(bs["dm"]), qci(bs["dtq"])

n_f = int((P["fp"] == 1).sum())
p1 = ci_df[0] > 0
null_a = (ci_df[0] > -1) and (ci_df[1] < 1)
status = "GO" if p1 else "PARTIAL"
verdict = (f"여성 백분위 조정−원시 = {d_f:+.2f}점 {ci_df} (남성 {d_m:+.2f} {ci_dm}); "
           f"상위 사분위 여성 비중 {tqr*100:.1f}%→{tqa*100:.1f}% (Δ {(tqa-tqr)*100:+.2f}pp {ci_dtq}); "
           f"Spearman {sp:.3f}; 파트너 {len(P)} (여성 {n_f})"
           + (" — 귀결 A 성립: 원시 지표가 여성 파트너를 하향 랭킹" if p1
              else (" — 지표 왜곡 미검출 (등가 범위)" if null_a else " — 미결 (CI 0 포함), MDE 병기")))

emit("P001-05", "귀결 A — 트랙레코드 랭킹 왜곡: 원시 vs 배치조정 (NA+EU)", status,
     {"pct_diff_female": [round(d_f, 2), ci_df], "pct_diff_male": [round(d_m, 2), ci_dm],
      "topq_female_share_raw": round(tqr, 4), "topq_female_share_adj": round(tqa, 4),
      "topq_change": [round((tqa - tqr) * 100, 2), ci_dtq], "spearman_raw_adj": round(sp, 3),
      "n_partners": int(len(P)), "n_female": n_f, "min_deals": MIN_DEALS},
     prediction="여성 백분위 +1~+5점 CI 배제; 상위 사분위 여성 비중 상대 +10%; 남성은 반대 부호 소폭",
     verdict=verdict, kill_met=False, n=int(len(P)),
     extra={"stage": 3, "feeds": "3막 A (GAP_MAP G3)", "slug": "trackrecord",
            "inputs": "sample_v1 (NA+EU, dt<=2017-10)"})
print("done")
