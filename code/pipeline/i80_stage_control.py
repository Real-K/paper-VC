# -*- coding: utf-8 -*-
"""I-80 스테이지 구성 교란 점검 — exit-ever 유의 열위의 판별 (K-3 판별 최종)

[왜] I-78 불리 발견: exit_ever gap_ff = −6.25pp [−11.5, −1.4] 유의(기저 46.4%), ipo6 도 방향 불리.
결론 전 필수 위협: **딜 스테이지 구성** — 여성 파트너가 시드·초기 단계 딜에 상대적으로 많이
배치되면(배치 또는 선호) 같은 투자사×연도×섹터 셀 안에서도 장기 출구율이 기계적으로 낮다.
불리한 추정치에도 동일 강도의 교란 점검을 적용한다(rules/00 — 방향 무관 대칭 검증).
[설계] I-78 표본(2010–2017-10) 재사용, 셀 = 투자사×연도×섹터×**스테이지**(investment_type).
  결과 3종 재추정: exit_ever · ipo6 · fon(후속 36m, 라운드 2010–2020-10 표본) — 유리·불리 함께.
  진단: fp 와 스테이지의 연관 — 여성 파트너 딜의 시드 비중 vs 남성 (구성 차이 크기 자체를 보고).
[사전 예측] (결과 전, 2026-09-03)
  P1 여성 파트너 딜은 시드·엔젤 비중이 +2~+8pp 높다 (스테이지 구성 차이 존재).
  P2 스테이지 셀 후 exit_ever gap_ff 는 절대값 축소 (−6.25 → −2~−4pp), 유의성 소멸 가능.
  P3 fon 판별(호의 배제, 하한 > −5pp) 은 스테이지 셀에서도 유지.
[판정] (사전 등록)
  exit_ever 열위가 스테이지 셀 후 CI 0 포함 → 스테이지 구성이 설명 — "출구 판별 미결(MDE 병기)"
  로 확정, fon 판별로 논문 성립 (GO).
  열위가 유의 잔존 → **실재하는 장기 출구 열위** — 호의 방향 증거로 원고에 기록하고, 서사를
  '조건부 판별'(자금조달 마진 무열위 · 출구 마진 열위)로 재구성 (그것도 발견 — GO, 방향 명기).
  P3 실패 → K-3 판별 전체 재검토 (PARTIAL).
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
EARLY = {"seed", "angel", "pre_seed", "equity_crowdfunding", "convertible_note"}

people = CTX.people[["uuid", "gender"]]
g_map = people[people["gender"].isin(["male", "female"])].set_index("uuid")["gender"]
rounds = CTX.rounds.dropna(subset=["announced_on", "org_uuid"]).copy()
rounds = rounds[~rounds["investment_type"].isin(EQ_EXCL)]
rounds["dt"] = pd.to_datetime(rounds["announced_on"], errors="coerce")
rounds = rounds.dropna(subset=["dt"])
rounds = rounds[(rounds["dt"] >= "2010-01-01") & (rounds["dt"] <= "2023-10-31")]

jobs = CTX.jobs
fj = jobs[jobs["title"].fillna("").str.lower().str.contains("founder", regex=False)][
    ["person_uuid", "org_uuid"]].dropna()
fj["fg"] = fj["person_uuid"].map(g_map)
fj = fj[fj["fg"].notna()]
org_ff = (fj["fg"] == "female").groupby(fj["org_uuid"]).max()
orgs = CTX.orgs
topcat = dict(zip(orgs["uuid"], orgs["category_groups_list"].fillna("NA").str.split(",").str[0].str.strip()))

pt = CTX.partners.dropna(subset=["funding_round_uuid", "investor_uuid", "partner_uuid"])
d = pt.merge(rounds[["uuid", "org_uuid", "dt", "investment_type"]],
             left_on="funding_round_uuid", right_on="uuid")
d["pg"] = d["partner_uuid"].map(g_map)
d["ff"] = d["org_uuid"].map(org_ff)
d = d[d["pg"].notna() & d["ff"].notna()].copy()
d["fp"] = (d["pg"] == "female").astype(float)
d["ff"] = d["ff"].astype(float)
d["year"] = d["dt"].dt.year.astype(str)
d["stage"] = d["investment_type"].fillna("NA")
d["early"] = d["stage"].isin(EARLY).astype(float)
d["cell"] = (d["investor_uuid"] + "|" + d["year"] + "|"
             + d["org_uuid"].map(topcat).fillna("NA") + "|" + d["stage"])
d["cell_nostage"] = d["investor_uuid"] + "|" + d["year"]

acq = CTX.acq.dropna(subset=["acquiree_uuid", "acquired_on"]).copy()
acq["adt"] = pd.to_datetime(acq["acquired_on"], errors="coerce")
ip = CTX.ipos.dropna(subset=["org_uuid", "went_public_on"]).copy()
ip["idt"] = pd.to_datetime(ip["went_public_on"], errors="coerce")
first_ipo = ip.groupby("org_uuid")["idt"].min()
exit_any = pd.concat([acq.groupby("acquiree_uuid")["adt"].min(), first_ipo], axis=1).min(axis=1)
d["exit_ever"] = d["org_uuid"].map(exit_any).notna().astype(float)
d["ipo6"] = ((d["org_uuid"].map(first_ipo) - d["dt"]).dt.days <= 365 * 6).fillna(False).astype(float)
r_org = rounds[["org_uuid", "dt"]].sort_values(["org_uuid", "dt"]).copy()
r_org["next_dt"] = r_org.groupby("org_uuid")["dt"].shift(-1)
next_map = r_org.drop_duplicates(["org_uuid", "dt"]).set_index(["org_uuid", "dt"])["next_dt"]
d["next_dt"] = pd.Series(list(zip(d["org_uuid"], d["dt"]))).map(next_map).to_numpy()
d["fon"] = ((pd.to_datetime(d["next_dt"]) - d["dt"]).dt.days <= 365 * 3).fillna(False).astype(float)


def gap_ff(df, y, cell, nb=NB):
    dd = df[df["ff"] == 1.0][[y, "fp", cell, "investor_uuid"]].reset_index(drop=True)
    yr = (dd[y] - dd[y].groupby(dd[cell]).transform("mean")).to_numpy()
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
    return beta, qci(bs), int(len(dd))


# P1 진단: fp ~ early (투자사×연도 셀 — 스테이지 구성 차이의 크기)
b_early, ci_early, _ = gap_ff(d.assign(ff=1.0), "early", "cell_nostage")  # 전체 딜에서 fp-early 연관
d_exit = d[d["dt"] <= "2017-10-31"]
d_fon = d[d["dt"] <= "2020-10-31"]
b_ev, ci_ev, n_ev = gap_ff(d_exit, "exit_ever", "cell")
b_ip, ci_ip, _ = gap_ff(d_exit, "ipo6", "cell")
b_fo, ci_fo, n_fo = gap_ff(d_fon, "fon", "cell")

stage_explains = (not np.isnan(ci_ev[0])) and (ci_ev[0] <= 0 <= ci_ev[1])
deficit_real = (not np.isnan(ci_ev[1])) and (ci_ev[1] < 0)
p3 = (not np.isnan(ci_fo[0])) and (ci_fo[0] > -0.05)
status = "GO" if ((stage_explains or deficit_real) and p3) else "PARTIAL"
verdict = (f"fp-초기단계 연관={b_early:+.4f} {ci_early}; 스테이지 셀 exit_ever gap_ff={b_ev:+.4f} {ci_ev} "
           f"(I-78 −0.0625 [−0.115,−0.0138] 대비); ipo6={b_ip:+.4f} {ci_ip}; fon={b_fo:+.4f} {ci_fo}"
           + (" — 스테이지 구성이 설명: 출구 판별 미결(MDE 병기)로 확정, fon 판별로 성립"
              if (stage_explains and p3) else
              (" — 열위 잔존: 조건부 판별(자금 무열위·출구 열위)로 서사 재구성" if (deficit_real and p3)
               else " — P3 실패 또는 미결: 판별 재검토")))

emit("I-80", "스테이지 구성 교란 점검 — exit-ever 열위 판별 (K-3 판별 최종)", status,
     {"fp_early_assoc": [round(b_early, 4), ci_early],
      "exit_ever_stagecell": [round(b_ev, 4), ci_ev, n_ev],
      "ipo6_stagecell": [round(b_ip, 4), ci_ip],
      "fon_stagecell": [round(b_fo, 4), ci_fo, n_fo],
      "i78_exit_ever_ref": [-0.0625, [-0.115, -0.0138]],
      "stage_explains": bool(stage_explains), "deficit_real": bool(deficit_real), "p3_fon": bool(p3)},
     prediction="fp 시드 비중 +2~+8pp; 스테이지 셀 후 exit_ever 축소(−2~−4pp)·유의성 소멸 가능; fon 하한 > −5pp 유지",
     verdict=verdict, kill_met=False, n=n_ev,
     extra={"stage": 2, "feeds": "RESULTS_LEDGER_K3.md §4 판별", "slug": "stage_control"})
print("done")
