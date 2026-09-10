# -*- coding: utf-8 -*-
"""p001_12 (Track D, P-2+P-3) E2 공변량 조정 배터리 + 이산시간 해저드

[왜] 지금까지 셀 FE 만 사용 — 딜 수준 공변량(라운드 규모·기업 연령·선행 라운드·신디케이트)을
쓰지 않아 잔차 분산을 방치했고, 신디케이트 교란 공격에도 무방비. 또 6년 이진 출구는 시간
정보를 버리고 고정지평×스테이지의 기계성 비판(리뷰 DA#8)에 노출. 공변량은 전부 딜 시점
특성(사후 처치 통제 아님).
[설계] sample_v1 NA+EU, ff=1 딜. 셀 = 투자사×연도×섹터×스테이지 (기준 유지).
  공변량 X: log1p(raised_usd)+결측, 기업연령(년, 절단 0-50)+결측, 선행 라운드 수(log1p),
  log1p(investor_count)+결측, 공동투자자 경험(타 투자자 딜수 log1p 평균)+결측.
  (a) 조정 배터리: 셀 demean 후 y·fp 를 X(동일 demean) 에 잔차화 → β_fp. 5개 결과.
  (b) 원 격차 정밀화: 섹터 셀 exit_ever 동일 조정 (동기 전시물의 CI 조임).
  (c) 해저드: 딜×경과년(1..6) 패널, y=해당 연 출구, FE=셀×경과년, x=fp (+X). 연평균 해저드 격차.
  부트 = 투자사 군집 400 (조정 전 과정 재실행).
[사전 예측] (결과 전 — POWER_UPGRADE_PLAN P-2·P-3)
  P1 fon·exit_ever CI 폭 10~25% 축소, 점추정 ±1pp 내 안정 (이동하면 교란 발견 — 그것도 기록).
  P2 해저드 격차 이진 결과와 동부호·유의 격차 부재 (연 기저 해저드 대비 ±25% 배제 지향).
  P3 원 격차(섹터 셀) 조정 후에도 음의 점추정 유지 (동기 사실의 견고성).
[판정] P1 → 조정 사양을 본문 표준으로 (무조정은 robustness — rule 10). 이동 시 원인 규명 전 교체 금지.
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
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR",
      "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}
NAEU = EU | {"USA", "CAN"}

d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v2.parquet"))
d = d[d["country_code"].isin(NAEU)].copy()
d["dt"] = pd.to_datetime(d["dt"])

r = CTX.rounds[["uuid", "raised_amount_usd", "investor_count", "org_uuid", "announced_on"]].copy()
r["rdt"] = pd.to_datetime(r["announced_on"], errors="coerce")
d = d.merge(r[["uuid", "raised_amount_usd", "investor_count"]],
            left_on="funding_round_uuid", right_on="uuid", how="left", suffixes=("", "_r"))
orgs = CTX.orgs[["uuid", "founded_on"]].copy()
orgs["fy"] = pd.to_datetime(orgs["founded_on"], errors="coerce").dt.year
d["age"] = (d["dt"].dt.year - d["org_uuid"].map(orgs.set_index("uuid")["fy"])).clip(0, 50)
# 선행 라운드 수
ro = r.dropna(subset=["org_uuid", "rdt"]).sort_values(["org_uuid", "rdt"])
org_dates = {o: g["rdt"].to_numpy() for o, g in ro.groupby("org_uuid")}
d["prior"] = [np.searchsorted(org_dates.get(o, np.array([], dtype="datetime64[ns]")),
                              np.datetime64(t)) for o, t in zip(d["org_uuid"], d["dt"])]
# 공동투자자 경험
inv = CTX.inv.dropna(subset=["funding_round_uuid", "investor_uuid"])
icnt = inv.groupby("investor_uuid").size()
ie = inv.copy()
ie["lc"] = np.log1p(ie["investor_uuid"].map(icnt))
rs = ie.groupby("funding_round_uuid")["lc"].agg(["sum", "count"])
d = d.merge(rs, left_on="funding_round_uuid", right_index=True, how="left")
own_lc = np.log1p(d["investor_uuid"].map(icnt).fillna(0))
d["coexp"] = np.where(d["count"] > 1, (d["sum"] - own_lc) / (d["count"] - 1), np.nan)

d["x_amt"] = np.log1p(pd.to_numeric(d["raised_amount_usd"], errors="coerce"))
d["x_ic"] = np.log1p(pd.to_numeric(d["investor_count"], errors="coerce"))
COVS = []
for c in ("x_amt", "age", "coexp", "x_ic"):
    d[c + "_m"] = d[c].isna().astype(float)
    d[c] = d[c].fillna(0)
    COVS += [c, c + "_m"]
d["x_prior"] = np.log1p(d["prior"])
COVS.append("x_prior")


def adj_gap(df, y, cell, use_cov=True, nb=NB):
    cols = [y, "fp", cell, "investor_uuid"] + COVS
    dd = df[cols].reset_index(drop=True)
    def est(sub):
        g = sub[cell]
        yv = sub[y].astype(float) - sub[y].astype(float).groupby(g).transform("mean")
        xv = sub["fp"].astype(float) - sub["fp"].astype(float).groupby(g).transform("mean")
        if use_cov:
            Z = np.column_stack([(sub[c] - sub[c].groupby(g).transform("mean")).to_numpy()
                                 for c in COVS])
            b, *_ = np.linalg.lstsq(Z, xv.to_numpy(), rcond=None)
            xv = xv.to_numpy() - Z @ b
            b2, *_ = np.linalg.lstsq(Z, yv.to_numpy(), rcond=None)
            yv = yv.to_numpy() - Z @ b2
        else:
            xv, yv = xv.to_numpy(), yv.to_numpy()
        sxx = (xv * xv).sum()
        return float((xv * yv).sum() / sxx) if sxx > 0 else np.nan
    b0 = est(dd)
    grp = {c: g.index.to_numpy() for c, g in dd.groupby("investor_uuid")}
    keys = list(grp)
    bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(keys), len(keys))
        sub = dd.loc[np.concatenate([grp[keys[i]] for i in pick])].reset_index(drop=True)
        v = est(sub)
        if np.isfinite(v):
            bs.append(v)
    return round(b0, 4), qci(bs), int(len(dd))


dff = d[d["ff"] == 1.0]
out = {}
for y, dfy in (("fon", dff[dff["dt"] <= "2020-10-31"]),
               ("exit_ever", dff[dff["dt"] <= "2017-10-31"]),
               ("ipo6", dff[dff["dt"] <= "2017-10-31"]),
               ("acqp6", dff[dff["dt"] <= "2017-10-31"]),
               ("closed6", dff[dff["dt"] <= "2017-10-31"])):
    out[y] = {"adj": adj_gap(dfy, y, "cell_stage", True),
              "unadj": adj_gap(dfy, y, "cell_stage", False, nb=200)}
raw_adj = adj_gap(dff[dff["dt"] <= "2017-10-31"], "exit_ever", "cell_cat", True)

# 해저드: 딜×경과년 (출구 시점 근사 — exit6/exit_ever 만으로는 연도별 불가 → exit_dt 재구축)
acq = CTX.acq.dropna(subset=["acquiree_uuid", "acquired_on"]).copy()
acq["adt"] = pd.to_datetime(acq["acquired_on"], errors="coerce")
ip = CTX.ipos.dropna(subset=["org_uuid", "went_public_on"]).copy()
ip["idt"] = pd.to_datetime(ip["went_public_on"], errors="coerce")
exit_dt = pd.concat([acq.groupby("acquiree_uuid")["adt"].min(),
                     ip.groupby("org_uuid")["idt"].min()], axis=1).min(axis=1)
h = dff[dff["dt"] <= "2017-10-31"].copy().reset_index(drop=True)
h["edt"] = h["org_uuid"].map(exit_dt)
h["eyr"] = ((h["edt"] - h["dt"]).dt.days / 365.25)
rows = []
for t in range(1, 7):
    sub = h[(h["eyr"].isna()) | (h["eyr"] > t - 1)].copy()
    sub["yh"] = ((sub["eyr"] > t - 1) & (sub["eyr"] <= t)).fillna(False).astype(float)
    sub["cellt"] = sub["cell_stage"] + "|t" + str(t)
    rows.append(sub[["yh", "fp", "cellt", "investor_uuid"] + COVS])
H = pd.concat(rows, ignore_index=True)
base_haz = float(H["yh"].mean())
b_h, ci_h, n_h = adj_gap(H.rename(columns={"yh": "y"}), "y", "cellt", True, nb=300)

fon_w_new = (out["fon"]["adj"][1][1] - out["fon"]["adj"][1][0]) * 100
fon_w_old = (out["fon"]["unadj"][1][1] - out["fon"]["unadj"][1][0]) * 100
ex_w_new = (out["exit_ever"]["adj"][1][1] - out["exit_ever"]["adj"][1][0]) * 100
ex_w_old = (out["exit_ever"]["unadj"][1][1] - out["exit_ever"]["unadj"][1][0]) * 100
shrink_fon = 1 - fon_w_new / fon_w_old
shrink_ex = 1 - ex_w_new / ex_w_old
stable = all(abs(out[y]["adj"][0] - out[y]["unadj"][0]) <= 0.011 for y in out)
haz_rel_excl = (abs(b_h) + 1.96 * 0)  # 표시용 — 상세는 CI
p2 = (ci_h[0] > -0.25 * base_haz) and (ci_h[1] < 0.25 * base_haz)
status = "GO" if ((shrink_fon > 0.05 or shrink_ex > 0.05) and stable) else "PARTIAL"
verdict = (f"조정 fon={out['fon']['adj'][0]*100:+.2f} {out['fon']['adj'][1]} (폭 {fon_w_new:.1f}pp, "
           f"축소 {shrink_fon*100:.0f}%); exit_ever={out['exit_ever']['adj'][0]*100:+.2f} "
           f"{out['exit_ever']['adj'][1]} (축소 {shrink_ex*100:.0f}%); 점추정 안정={stable}; "
           f"원 격차(섹터셀) 조정 {raw_adj[0]*100:+.2f} {raw_adj[1]}; "
           f"해저드 격차={b_h*100:+.3f}pp/년 {ci_h} (기저 {base_haz*100:.2f}%/년, "
           f"±25% 등가 {'배제' if p2 else '미배제'})")

emit("P001-12", "E2 공변량 조정 배터리 + 이산시간 해저드 (Track D, P-2·P-3)", status,
     {"battery_adj": {k: [round(v['adj'][0]*100, 2), v['adj'][1], v['adj'][2]] for k, v in out.items()},
      "battery_unadj_ref": {k: [round(v['unadj'][0]*100, 2), v['unadj'][1]] for k, v in out.items()},
      "ci_shrink": {"fon": round(shrink_fon, 3), "exit_ever": round(shrink_ex, 3)},
      "point_stable_within_1pp": bool(stable),
      "raw_gap_sectorcell_adj": [round(raw_adj[0]*100, 2), raw_adj[1], raw_adj[2]],
      "hazard_gap_per_yr": [round(b_h*100, 3), ci_h, n_h], "hazard_base": round(base_haz, 4),
      "hazard_equiv_25pct": bool(p2)},
     prediction="CI 폭 10~25% 축소·점추정 ±1pp 안정; 해저드 동부호·±25% 등가 지향; 원 격차 음 유지",
     verdict=verdict, kill_met=False, n=out["fon"]["adj"][2],
     extra={"stage": 5, "feeds": "Track D P-2·P-3 / E2 본문 사양 후보", "slug": "covadj_hazard"})
print("done")
