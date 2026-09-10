# -*- coding: utf-8 -*-
"""p001_16 (Track C-④·⑥) 딜 수준 귀속 진단 + 스테이지 라벨 품질 (리뷰 DA#3·측정 #8)

[왜] (④) 귀속 중립성의 기존 근거는 회사 수준 상관뿐 — 위협은 딜 수준 살리언스("여성 파트너
×여성 창업 딜일수록 언론이 파트너를 호명"). 검정: 투자사×연도 FE 하에서
P(라운드 귀속) ~ ff + fp_share + ff×fp_share. 살리언스 위협의 지문 = 상호작용 > 0.
(⑥) investment_type 의 generic 라벨(series_unknown 95k)이 성별과 상관하면 스테이지층이
라벨링 인공물일 수 있음 — fp 별 generic 비중 + generic 제외 E1 스테이지층 재추정.
[사전 예측] (결과 전, 2026-09-04) P1 상호작용 CI ⊂ ±3pp (살리언스 지문 없음 지향 — 등가 서술).
P2 generic 비중의 fp 격차 < 2pp; 제외 후 E1 스테이지층 잔여(+0.66 부근) 유지.
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
NB = 300
EQ_EXCL = {"grant", "debt_financing", "post_ipo_debt", "post_ipo_equity", "non_equity_assistance"}
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR",
      "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}
NAEU = EU | {"USA", "CAN"}
GENERIC = {"series_unknown", "undisclosed", "NA"}

sv = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v1.parquet"))
# ④ 딜 수준 귀속 모형 — 표본: NA+EU 투자사의 판정가능 라운드 전체 (귀속 여부 불문)
people = CTX.people[["uuid", "gender"]]
g_map = people[people["gender"].isin(["male", "female"])].set_index("uuid")["gender"]
jobs = CTX.jobs
fj = jobs[jobs["title"].fillna("").str.lower().str.contains("founder", regex=False)][
    ["person_uuid", "org_uuid"]].dropna()
fj["fg"] = fj["person_uuid"].map(g_map)
fj = fj[fj["fg"].notna()]
org_ff = (fj["fg"] == "female").groupby(fj["org_uuid"]).max()
r = CTX.rounds.dropna(subset=["announced_on", "org_uuid"]).copy()
r = r[~r["investment_type"].isin(EQ_EXCL)]
r = r[(r["announced_on"] >= "2010-01-01") & (r["announced_on"] <= "2023-10-31")]
inv = CTX.inv.dropna(subset=["funding_round_uuid", "investor_uuid"])
vc_country = dict(zip(CTX.investors["uuid"], CTX.investors["country_code"]))
iv = inv[inv["investor_uuid"].map(vc_country).isin(NAEU)]
iv = iv.merge(r[["uuid", "org_uuid", "announced_on"]], left_on="funding_round_uuid", right_on="uuid")
iv["ff"] = iv["org_uuid"].map(org_ff)
iv = iv[iv["ff"].notna()].copy()
iv["ff"] = iv["ff"].astype(float)
pt = CTX.partners.dropna(subset=["funding_round_uuid", "investor_uuid"])
attr_set = set(zip(pt["funding_round_uuid"], pt["investor_uuid"]))
iv["attr"] = [(fr, i) in attr_set for fr, i in zip(iv["funding_round_uuid"], iv["investor_uuid"])]
iv["attr"] = iv["attr"].astype(float)
fp_share = sv.groupby("investor_uuid")["fp"].mean()
iv["fps"] = iv["investor_uuid"].map(fp_share)
iv = iv[iv["fps"].notna()].copy()
iv["yr"] = iv["announced_on"].str[:4]
iv["cell"] = iv["investor_uuid"] + "|" + iv["yr"]
iv["inter"] = iv["ff"] * (iv["fps"] - iv["fps"].mean())


def fwl_multi(dd, y, xs, nb=NB):
    dd = dd.reset_index(drop=True)
    g = dd["cell"]
    Y = (dd[y] - dd[y].groupby(g).transform("mean")).to_numpy()
    X = np.column_stack([(dd[x] - dd[x].groupby(g).transform("mean")).to_numpy() for x in xs])
    b = np.linalg.lstsq(X, Y, rcond=None)[0]
    grp = {c: gg.index.to_numpy() for c, gg in dd.groupby("investor_uuid")}
    keys = list(grp)
    bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(keys), len(keys))
        rows_ = np.concatenate([grp[keys[i]] for i in pick])
        try:
            bs.append(np.linalg.lstsq(X[rows_], Y[rows_], rcond=None)[0])
        except Exception:
            pass
    bs = np.array(bs)
    return b, [qci(bs[:, i]) for i in range(len(xs))]


b, cis = fwl_multi(iv, "attr", ["ff", "inter"])
b_ff, ci_ff = round(float(b[0]), 4), cis[0]
b_int, ci_int = round(float(b[1]), 4), cis[1]

# ⑥ 라벨 품질
sv2 = sv[sv["country_code"].isin(NAEU)].copy()
sv2["generic"] = sv2["stage"].isin(GENERIC)
gen_fp = float(sv2.loc[sv2["fp"] == 1, "generic"].mean())
gen_mp = float(sv2.loc[sv2["fp"] == 0, "generic"].mean())
sv3 = sv2[~sv2["generic"]].reset_index(drop=True)
yr_ = (sv3["ff"] - sv3["ff"].groupby(sv3["cell_stage"]).transform("mean")).to_numpy()
xr_ = (sv3["fp"] - sv3["fp"].groupby(sv3["cell_stage"]).transform("mean")).to_numpy()
b_e1 = float((xr_ * yr_).sum() / (xr_ * xr_).sum())
grp = {c: g.index.to_numpy() for c, g in sv3.groupby("investor_uuid")}
keys = list(grp)
bs = []
for _ in range(300):
    pick = rng.integers(0, len(keys), len(keys))
    rows_ = np.concatenate([grp[keys[i]] for i in pick])
    x2, y2 = xr_[rows_], yr_[rows_]
    s = (x2 * x2).sum()
    if s:
        bs.append((x2 * y2).sum() / s)
ci_e1 = qci(bs)

p1 = (ci_int[0] > -0.03) and (ci_int[1] < 0.03)
p2 = abs(gen_fp - gen_mp) < 0.02
status = "GO" if (p1 and p2) else "PARTIAL"
verdict = (f"딜 수준 귀속: ff 주효과 {b_ff*100:+.2f}pp {ci_ff}, **ff×fp_share 상호작용 "
           f"{b_int*100:+.2f}pp {ci_int}** ({'살리언스 지문 없음(±3pp 등가)' if p1 else '지문 존재 — ceiling 반영'}); "
           f"generic 라벨 fp {gen_fp*100:.1f}% vs mp {gen_mp*100:.1f}% ({'중립' if p2 else '격차'}); "
           f"generic 제외 E1 스테이지층 {b_e1*100:+.2f}pp {ci_e1} (기준 +0.66 과 비교)")

emit("P001-16", "딜 수준 귀속 진단 + 스테이지 라벨 품질 (Track C-④·⑥)", status,
     {"attr_ff_main": [b_ff, ci_ff], "attr_ff_x_fpshare": [b_int, ci_int], "n_rounds": int(len(iv)),
      "generic_share_fp": round(gen_fp, 4), "generic_share_mp": round(gen_mp, 4),
      "e1_stage_excl_generic": [round(b_e1, 4), ci_e1, int(len(sv3))],
      "p1_no_salience": bool(p1), "p2_label_neutral": bool(p2)},
     prediction="상호작용 CI ⊂ ±3pp; generic 격차 <2pp; 제외 후 E1 잔여 유지",
     verdict=verdict, kill_met=False, n=int(len(iv)),
     extra={"stage": 5, "feeds": "DA#3·측정#8 방어 / Table 9 확장", "slug": "meas_diags2"})
print("done")
