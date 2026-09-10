# -*- coding: utf-8 -*-
"""I-77 출구 판별의 검정력 보강 — 레버 B(표본 소급 2005+) (K-3 power-rescue 1/2)

[왜] I-75 출구 판별 미결: gap_ff −4.0pp [−9.8, +1.1], 판별자 −5.2 [−12.0, +1.0] — P3 실패.
power-rescue 레버 순서(반사실→표본→결과변수)에서 반사실은 이미 셀 강화 완료 → **표본 레버**:
출구 창(72m) 확보 가능한 라운드를 2010→2005 년으로 소급해 ff 딜 표본을 늘린다. 레버는 이것
하나만(가드레일 5: 쌓지 않는다). MDE(80%) 를 전후 병기해 "미검출 vs 볼 수 없음"을 구분한다.
[설계] I-75 와 동일(섹터 셀, 공동 투자사 부트 500), 표본만 라운드 2005-01~2017-10.
  진단: 2005–2009 파트너 귀속 딜 수(소급 이득), 시대 혼합 점검(연도는 셀에 포함되어 흡수).
[사전 예측] (결과 전, 2026-09-03)
  P1 ff 출구 표본 ≥ +15% (8,058 → 9,300+).
  P2 gap_ff 점추정은 [−6pp, +2pp] 에 잔류 (표본 추가가 부호를 뒤집지 않음).
  P3 MDE(80%) 가 I-75 의 ~7.8pp 에서 ≤ 7pp 로 축소.
[판정] (사전 등록) 판별 성립 = gap_ff 하한 > −5pp (호의 배제, 후속과 동일 문턱) 또는
  상한 < 0 (실제 열위 검출 — 이것도 발견이다). 둘 다 아니면 PARTIAL: 결과변수 레버(i78)로.
  표본 이득 < +10% 면 레버 실패로 기록하고 i78 로.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emit_contract import emit, qci  # noqa: E402
from gates import CTX  # noqa: E402

rng = np.random.default_rng(42)
NB = 500
EQ_EXCL = {"grant", "debt_financing", "post_ipo_debt", "post_ipo_equity", "non_equity_assistance"}

people = CTX.people[["uuid", "gender"]]
g_map = people[people["gender"].isin(["male", "female"])].set_index("uuid")["gender"]

rounds = CTX.rounds.dropna(subset=["announced_on", "org_uuid"]).copy()
rounds = rounds[~rounds["investment_type"].isin(EQ_EXCL)]
rounds["dt"] = pd.to_datetime(rounds["announced_on"], errors="coerce")
rounds = rounds.dropna(subset=["dt"])
rounds = rounds[(rounds["dt"] >= "2005-01-01") & (rounds["dt"] <= "2023-10-31")]

jobs = CTX.jobs
fj = jobs[jobs["title"].fillna("").str.lower().str.contains("founder", regex=False)][
    ["person_uuid", "org_uuid"]].dropna()
fj["fg"] = fj["person_uuid"].map(g_map)
fj = fj[fj["fg"].notna()]
org_ff = (fj["fg"] == "female").groupby(fj["org_uuid"]).max()
orgs = CTX.orgs
topcat = dict(zip(orgs["uuid"], orgs["category_groups_list"].fillna("NA").str.split(",").str[0].str.strip()))

pt = CTX.partners.dropna(subset=["funding_round_uuid", "investor_uuid", "partner_uuid"])
d = pt.merge(rounds[["uuid", "org_uuid", "dt"]], left_on="funding_round_uuid", right_on="uuid")
d["pg"] = d["partner_uuid"].map(g_map)
d["ff"] = d["org_uuid"].map(org_ff)
d = d[d["pg"].notna() & d["ff"].notna()].copy()
d["fp"] = (d["pg"] == "female").astype(float)
d["ff"] = d["ff"].astype(float)
d["year"] = d["dt"].dt.year.astype(str)
d["cell"] = d["investor_uuid"] + "|" + d["year"] + "|" + d["org_uuid"].map(topcat).fillna("NA")

acq = CTX.acq.dropna(subset=["acquiree_uuid", "acquired_on"]).copy()
acq["adt"] = pd.to_datetime(acq["acquired_on"], errors="coerce")
ip = CTX.ipos.dropna(subset=["org_uuid", "went_public_on"]).copy()
ip["idt"] = pd.to_datetime(ip["went_public_on"], errors="coerce")
exit_dt = pd.concat([acq.groupby("acquiree_uuid")["adt"].min(),
                     ip.groupby("org_uuid")["idt"].min()], axis=1).min(axis=1)
d["exit_dt"] = d["org_uuid"].map(exit_dt)
d["exit6"] = ((d["exit_dt"] - d["dt"]).dt.days <= 365 * 6).fillna(False).astype(float)

d_exit = d[d["dt"] <= "2017-10-31"]
n_pre2010 = int((d_exit["dt"] < "2010-01-01").sum())
nf_new = int((d_exit["ff"] == 1).sum())
gain = nf_new / 8058 - 1


def gaps(df, y, nb=NB):
    sub = {s: df[df["ff"] == s][[y, "fp", "cell", "investor_uuid"]].reset_index(drop=True)
           for s in (1.0, 0.0)}
    res, arrs = {}, {}
    for s, dd in sub.items():
        yr = (dd[y] - dd[y].groupby(dd["cell"]).transform("mean")).to_numpy()
        xr = (dd["fp"] - dd["fp"].groupby(dd["cell"]).transform("mean")).to_numpy()
        arrs[s] = (yr, xr, {c: g.index.to_numpy() for c, g in dd.groupby("investor_uuid")})
        sxx = (xr * xr).sum()
        res[s] = float((xr * yr).sum() / sxx) if sxx else float("nan")
    bs = {1.0: [], 0.0: [], "diff": []}
    keys = {s: list(arrs[s][2]) for s in arrs}
    for _ in range(nb):
        cur = {}
        for s in (1.0, 0.0):
            yr, xr, grp = arrs[s]
            ks = keys[s]
            pick = rng.integers(0, len(ks), len(ks))
            rows_ = np.concatenate([grp[ks[i]] for i in pick])
            x2, y2 = xr[rows_], yr[rows_]
            sx = (x2 * x2).sum()
            cur[s] = (x2 * y2).sum() / sx if sx else np.nan
            bs[s].append(cur[s])
        bs["diff"].append(cur[1.0] - cur[0.0])
    return res, bs


res, bs = gaps(d_exit, "exit6")
gff, gmf = res[1.0], res[0.0]
ciff, cimf, cidj = qci(bs[1.0]), qci(bs[0.0]), qci(np.array(bs[1.0]) - np.array(bs[0.0]))
dj = gff - gmf
se_ff = float(np.nanstd(np.asarray(bs[1.0], float)))
mde80 = 2.8 * se_ff  # 80% 검정력·5% 양측 근사 (2.8×SE)

favor_excl = (not np.isnan(ciff[0])) and (ciff[0] > -0.05)
deficit_found = (not np.isnan(ciff[1])) and (ciff[1] < 0)
lever_fail = gain < 0.10
status = "GO" if (favor_excl or deficit_found) else "PARTIAL"
verdict = (f"2005+ 소급: ff 출구 딜 8,058→{nf_new} (+{gain*100:.1f}%, 2005–09 귀속 {n_pre2010}건); "
           f"gap_ff={gff:+.4f} {ciff} (MDE80 {mde80*100:.1f}pp; I-75 대비), gap_mf={gmf:+.4f} {cimf}, "
           f"판별자={dj:+.4f} {cidj}"
           + (" — 호의 배제 성립(출구)" if favor_excl
              else (" — 실제 열위 검출" if deficit_found
                    else (" — 레버 이득 부족, i78 결과변수 레버로" if lever_fail
                          else " — 미결 지속, i78 결과변수 레버로"))))

emit("I-77", "출구 판별 검정력 보강 — 표본 소급 2005+ (K-3 power-rescue 레버 B)", status,
     {"exit_gap_ff": [round(gff, 4), ciff], "exit_gap_mf": [round(gmf, 4), cimf],
      "exit_adjudicator": [round(dj, 4), cidj],
      "n_ff_exit": nf_new, "n_mf_exit": int((d_exit["ff"] == 0).sum()),
      "sample_gain_pct": round(gain * 100, 1), "n_attr_2005_09": n_pre2010,
      "mde80_pp": round(mde80 * 100, 2), "i75_ref": {"gap_ff": -0.0397, "ci": [-0.0979, 0.011]},
      "favoritism_excluded": bool(favor_excl), "deficit_found": bool(deficit_found),
      "lever_failed_gain": bool(lever_fail)},
     prediction="표본 +15%+; gap_ff ∈ [−6,+2]pp 잔류; MDE80 ≤ 7pp",
     verdict=verdict, kill_met=False, n=nf_new,
     extra={"stage": 2, "feeds": "RESULTS_LEDGER_K3.md §4 레버 B", "slug": "exit_power_sample"})
print("done")
