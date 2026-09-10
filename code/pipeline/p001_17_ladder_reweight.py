# -*- coding: utf-8 -*-
"""p001_17 (Track C-⑤) Table 8 판정가능성 재가중 + 다수-여성 정의 (측정 #2, DA#7)

[왜] 사다리(P(fp|ff,stage))는 단계별 판정가능성(+18pp/단계)이 다른 표본 위 — 판정가능 딜의
(국가×연도) 구성을 단계 내 전체 딜 구성에 맞춰 재가중해 선택 강도 차를 중화. 추가로 ff=any
가 혼성팀 위주라는 공격에 다수-여성 정의 사다리 병행.
[사전 예측] (결과 전, 2026-09-04) P1 재가중 후 차등 경사 +3.91 의 절반 이상 유지·CI 0 배제.
P2 다수-여성 정의에서 동부호 경사 (크기는 기저 축소 비례).
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
EQ_EXCL = {"grant", "debt_financing", "post_ipo_debt", "post_ipo_equity", "non_equity_assistance"}
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

# 판정가능성 재가중: 전체 귀속 딜(판정 불문) 의 (sgrp×국가×연도) 분포로 판정가능 딜 재가중
pt = CTX.partners.dropna(subset=["funding_round_uuid", "investor_uuid", "partner_uuid"])
r = CTX.rounds.dropna(subset=["announced_on", "org_uuid"])[
    ["uuid", "org_uuid", "announced_on", "country_code", "investment_type"]]
r = r[~r["investment_type"].isin(EQ_EXCL)]
rd = pt.merge(r, left_on="funding_round_uuid", right_on="uuid")
rd = rd[(rd["announced_on"] >= "2010-01-01") & (rd["announced_on"] <= "2023-10-31")
        & rd["country_code"].isin(NAEU)].copy()
rd["sgrp"] = np.where(rd["investment_type"].isin(EARLY), "early",
                      np.where(rd["investment_type"] == "series_a", "series_a",
                               np.where(rd["investment_type"].isin(LATE), "b_plus", "other")))
rd = rd[rd["sgrp"] != "other"]
rd["yr"] = rd["announced_on"].str[:4]
all_dist = rd.groupby(["sgrp", "country_code", "yr"]).size().rename("n_all")
d["yr"] = d["year"]
det_dist = d.groupby(["sgrp", "country_code", "yr"]).size().rename("n_det")
W = pd.concat([all_dist, det_dist], axis=1).fillna(0)
W["w"] = np.where(W["n_det"] > 0, W["n_all"] / W["n_det"], 0)
d = d.merge(W["w"], left_on=["sgrp", "country_code", "yr"], right_index=True, how="left")
d["w"] = d["w"].fillna(0)

people = CTX.people[["uuid", "gender"]]
g_map = people[people["gender"].isin(["male", "female"])].set_index("uuid")["gender"]
jobs = CTX.jobs
fj = jobs[jobs["title"].fillna("").str.lower().str.contains("founder", regex=False)][
    ["person_uuid", "org_uuid"]].dropna()
fj["fg"] = fj["person_uuid"].map(g_map)
fj = fj[fj["fg"].notna()]
org_fmaj = (fj["fg"] == "female").groupby(fj["org_uuid"]).mean() >= 0.5
d["ffm2"] = d["org_uuid"].map(org_fmaj).fillna(False).astype(float)


def slope(df, ffcol, wcol=None, nb=NB):
    def calc(sub):
        out = []
        for ff in (1.0, 0.0):
            for sg in ("early", "b_plus"):
                s = sub[(sub[ffcol] == ff) & (sub["sgrp"] == sg)]
                if len(s) < 30:
                    return np.nan
                w = s[wcol].to_numpy() if wcol else np.ones(len(s))
                out.append(np.average(s["fp"].to_numpy(), weights=w))
        return (out[0] - out[1]) - (out[2] - out[3])
    b0 = calc(df)
    grp = {c: g.index.to_numpy() for c, g in df.groupby("investor_uuid")}
    keys = list(grp)
    bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(keys), len(keys))
        v = calc(df.loc[np.concatenate([grp[keys[i]] for i in pick])])
        if np.isfinite(v):
            bs.append(v)
    return round(float(b0), 4), qci(bs)


b_rw, ci_rw = slope(d, "ff", "w")
b_mf, ci_mf = slope(d, "ffm2", None)
b_base, ci_base = slope(d, "ff", None)

p1 = (not np.isnan(b_rw)) and (ci_rw[0] > 0) and (b_rw >= 0.5 * 0.0391)
p2 = (not np.isnan(b_mf)) and (b_mf > 0)
status = "GO" if (p1 and p2) else "PARTIAL"
verdict = (f"차등 경사(early−B+): 기준 재현 {b_base*100:+.2f} {ci_base}; **판정가능성 재가중 "
           f"{b_rw*100:+.2f} {ci_rw}** ({'유지' if p1 else '감쇠/미배제'}); 다수-여성 정의 "
           f"{b_mf*100:+.2f} {ci_mf} ({'동부호' if p2 else '부호 이탈'})")

emit("P001-17", "Table 8 판정가능성 재가중 + 다수-여성 (Track C-⑤)", status,
     {"slope_base": [b_base, ci_base], "slope_reweighted": [b_rw, ci_rw],
      "slope_majority_female": [b_mf, ci_mf], "n": int(len(d))},
     prediction="재가중 후 경사 절반 이상 유지·CI 배제; 다수-여성 동부호",
     verdict=verdict, kill_met=False, n=int(len(d)),
     extra={"stage": 5, "feeds": "측정#2·DA#7 / Table 8 주석", "slug": "ladder_reweight"})
print("done")
