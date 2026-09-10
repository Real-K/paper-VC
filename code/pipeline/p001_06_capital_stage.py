# -*- coding: utf-8 -*-
"""p001_06 귀결 B — 여성 창업자 자본의 단계 구조: 여성 파트너 채널의 단계별 소멸 (NA+EU)

[왜] 3막 B (GAP_MAP G4): E1(매칭은 배치 구조)·E3(여성 파트너 존재가 ff 딜 구성과 결합 수준
연관) 하에서, 여성 파트너가 초기 단계에 몰려 있으면(fp-early +3.8pp) 여성 창업자가 만나는
여성 파트너 채널은 자금조달 사다리를 오를수록 좁아진다 — "후기 절벽"(PitchBook All In:
격차가 후기에서 최대) 의 공급측 미시 구조를 CB 건수로 정량화.
[설계] sample_v1 NA+EU. 단계 3군: early(시드·엔젤 등) / series_a / series_b_plus(B 이후+성장).
  ① fp 채널 폭: P(fp | ff 딜, 단계) — ff 딜이 여성 파트너를 만날 확률의 단계별 경로.
  ② 차등 경사: [P(fp|ff,early) − P(fp|ff,late)] − [P(fp|mf,early) − P(fp|mf,late)]
     — fp 채널의 단계별 축소가 ff 딜에서 더 가파른가 (구성 차등, 투자사 부트 500).
  ③ 재배치 반사실 (회계 항등식): fp 가 단계별로 남성과 동일 분포라면 후기 ff 딜의 fp 접촉
     건수가 몇 % 늘어나는가 — 헤드라인 정량화 (인과 주장 아님, 배치 산술).
[사전 예측] (결과 전, 2026-09-03)
  P1 P(fp|ff) 단계 경로 단조 하락: early > series_a > b_plus, 낙폭 ≥ 3pp.
  P2 차등 경사 > 0 (ff 딜에서 더 가파름), CI 0 배제 — 근거: 동류교배가 배치 구조라면
     fp×ff 결합이 초기 단계에 집중.
  P3 재배치 반사실: 후기 ff-fp 접촉 +15% 이상.
[판정] P1+P2 → 귀결 B 성립 (GO). P2 실패(경사 동일) → "채널 축소는 성별 중립적 배치의 산물"
  로 서술 조정 (PARTIAL — 여전히 보고 가치, 단 ff 특이성 주장 제거).
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
EARLY = {"seed", "angel", "pre_seed", "equity_crowdfunding", "convertible_note"}
LATE = {"series_b", "series_c", "series_d", "series_e", "series_f", "series_g", "series_h",
        "series_i", "series_j", "private_equity", "growth"}

d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v2.parquet"))
d = d[d["country_code"].isin(NAEU)].copy()
d["sgrp"] = np.where(d["stage"].isin(EARLY), "early",
                     np.where(d["stage"] == "series_a", "series_a",
                              np.where(d["stage"].isin(LATE), "b_plus", "other")))
d = d[d["sgrp"] != "other"].reset_index(drop=True)


def boot_stat(fn, nb=NB):
    grp = {c: g.index.to_numpy() for c, g in d.groupby("investor_uuid")}
    keys = list(grp)
    b0 = fn(d)
    bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(keys), len(keys))
        rows_ = np.concatenate([grp[keys[i]] for i in pick])
        v = fn(d.loc[rows_])
        if np.all(np.isfinite(v)):
            bs.append(v)
    bs = np.array(bs)
    return b0, [qci(bs[:, i]) for i in range(len(np.atleast_1d(b0)))]


def path_and_slope(df):
    out = []
    for ff in (1.0, 0.0):
        for sg in ("early", "series_a", "b_plus"):
            sub = df[(df["ff"] == ff) & (df["sgrp"] == sg)]
            out.append(sub["fp"].mean() if len(sub) >= 50 else np.nan)
    p_ff = out[0:3]
    p_mf = out[3:6]
    slope = (p_ff[0] - p_ff[2]) - (p_mf[0] - p_mf[2])
    return np.array(out + [slope])


vals, cis = boot_stat(path_and_slope)
p_ff = vals[0:3]
p_mf = vals[3:6]
slope, ci_slope = float(vals[6]), cis[6]

# 재배치 반사실: fp 의 단계 분포를 남성과 동일하게 — 후기 ff 딜의 fp 접촉 변화율
fp_deals = d[d["fp"] == 1.0]
mp_deals = d[d["fp"] == 0.0]
share_late_fp = float((fp_deals["sgrp"] == "b_plus").mean())
share_late_mp = float((mp_deals["sgrp"] == "b_plus").mean())
n_ff_late_fp = int(((d["ff"] == 1) & (d["fp"] == 1) & (d["sgrp"] == "b_plus")).sum())
cf_gain = (share_late_mp / share_late_fp - 1) if share_late_fp else float("nan")

p1 = (p_ff[0] > p_ff[1] > p_ff[2]) and ((p_ff[0] - p_ff[2]) >= 0.03)
p2 = (not np.isnan(ci_slope[0])) and (ci_slope[0] > 0)
status = "GO" if (p1 and p2) else "PARTIAL"
verdict = (f"P(fp|ff): early {p_ff[0]*100:.1f}% {cis[0]} → A {p_ff[1]*100:.1f}% → B+ {p_ff[2]*100:.1f}% "
           f"{cis[2]}; P(fp|mf): {p_mf[0]*100:.1f}→{p_mf[1]*100:.1f}→{p_mf[2]*100:.1f}%; "
           f"차등 경사 {slope*100:+.2f}pp {ci_slope}; fp 후기 비중 {share_late_fp*100:.1f}% vs 남성 "
           f"{share_late_mp*100:.1f}% → 재배치 반사실 후기 ff-fp 접촉 {cf_gain*100:+.0f}% (현 {n_ff_late_fp}건)"
           + (" — 귀결 B 성립" if (p1 and p2)
              else (" — 채널 축소는 성별 중립적 배치: ff 특이성 주장 제거 (정직 기록)" if p1
                    else " — 경로 비단조: 서술 재검토")))

emit("P001-06", "귀결 B — 여성 창업자 자본의 단계 구조 (fp 채널의 단계별 소멸, NA+EU)", status,
     {"p_fp_given_ff": [[round(float(x) * 100, 2) for x in p_ff], cis[0:3]],
      "p_fp_given_mf": [[round(float(x) * 100, 2) for x in p_mf], cis[3:6]],
      "diff_slope": [round(slope * 100, 2), ci_slope],
      "fp_late_share": round(share_late_fp, 4), "mp_late_share": round(share_late_mp, 4),
      "counterfactual_late_ff_fp_gain_pct": round(cf_gain * 100, 1),
      "n_ff_late_fp_deals": n_ff_late_fp, "n": int(len(d))},
     prediction="P(fp|ff) 단조 하락 낙폭≥3pp; 차등 경사>0 CI 배제; 반사실 +15%+",
     verdict=verdict, kill_met=False, n=int(len(d)),
     extra={"stage": 3, "feeds": "3막 B (GAP_MAP G4)", "slug": "capital_stage",
            "inputs": "sample_v1 (NA+EU)"})
print("done")
