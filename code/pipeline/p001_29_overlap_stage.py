# -*- coding: utf-8 -*-
"""p001_29 — 리뷰어 선제 검정 II: 기업 중복 제외 · 단계 집중 통제 · 단위 병기

[왜] 내부 리뷰 라운드 2 가 진행 중이다. 악마의 변호인이 반드시 제기할 세 가지를 리뷰와 병행해
미리 잰다. 리뷰 결과에 따라 Table 7·9 의 강건성 행 또는 원고 §6 의 한계 문장이 된다.

 T1 **기업 중복**: 사후기 딜이 사전기에 같은 파트너가 이미 투자한 기업의 후속 라운드라면,
    post_adj 가 사전기 raw 와 **기계적으로** 묶인다. 사전기 투자 기업을 사후기에서 제외한 뒤
    post_adj_excl ← raw_pct | adj_pct 를 다시 잰다.
 T2 **단계 집중의 기계적 경로 (Panel C)**: 후기단계 특화 파트너는 composition 이 유리하고,
    스핀아웃하면 **후기단계 펀드가 원래 크기** 때문에 큰 펀드를 조성한다. 사전기 후기단계 비중
    (late_sh) 을 통제하고 lp_any / lp_amt / recv_q ← composition 을 다시 잰다.
 T3 **단위 병기 (D051)**: 무조건 composition 계수가 레벨(+0.146)과 백분위(−0.045, P001-26 G4)에서
    갈렸다. 같은 LOO 패널에서 둘을 나란히 재서 원고가 **둘 다** 공개할 수 있게 한다.

[사양] LOO 셀 벤치마크(P001-27 B 구성). 군집 = 투자사 부트 500.
[사전 예측] (결과 조회 전, 2026-09-08)
 T1 사후기 딜의 20~40% 가 사전기 기업 후속. 제외 후 계수는 +0.103 의 **50% 이상 유지**, CI 0 배제.
 T2 lp_amt 의 composition 계수는 late_sh 통제 시 **40% 이상 감소** (펀드 크기는 단계와 함께 커진다);
    lp_any·recv_q 는 30% 미만 변화. late_sh 자체는 lp_amt 에 양(+).
 T3 레벨 무조건 +0.146 재현; 백분위 무조건은 0 근처 또는 음(−) — 순위차는 레벨과 다른 변수다.
[게이트] T1: 잔존 ≥50% AND CI 0 배제 → 중복이 동인 아님.
 T2: lp_amt 가 유의를 잃으면 Panel C 의 펀드 크기 행은 "단계 집중과 분리 불가"로 재표기.
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

rng = np.random.default_rng(20260908)
NB = 500
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR",
      "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}
NAEU = EU | {"USA", "CAN"}
EARLY = {"seed", "angel", "pre_seed", "equity_crowdfunding", "convertible_note"}
CUT = pd.Timestamp("2017-10-31")
END = pd.Timestamp("2023-10-31")
BASE = 0.10272  # P001-27 B LOO


def log(*a):
    print(*a, flush=True)


def is_late(s):
    s = str(s)
    return (s.startswith("series_") and s not in ("series_a", "series_unknown")) or s == "private_equity"


d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v2.parquet"))
d["dt"] = pd.to_datetime(d["dt"])
dn = d[d["country_code"].isin(NAEU)].copy()
dn["mcell"] = dn["year"] + "|" + dn["cat"] + "|" + dn["stage"]
dn["late"] = dn["stage"].map(is_late).astype(float)


def resid_loo(df):
    g = df.groupby("mcell")["exit_ever"]
    s, n = g.transform("sum"), g.transform("size")
    bm = np.where(n > 1, (s - df["exit_ever"]) / np.maximum(n - 1, 1), np.nan)
    return df["exit_ever"].to_numpy(float) - np.asarray(bm, float)


h = dn[dn["dt"] <= CUT].copy()
h["r"] = resid_loo(h)
h = h[np.isfinite(h["r"])]
P = h.groupby("partner_uuid").agg(
    raw=("exit_ever", "mean"), adj=("r", "mean"), n=("exit_ever", "size"), fp=("fp", "first"),
    late_sh=("late", "mean"), firm=("investor_uuid", lambda s: s.mode().iloc[0])).reset_index()
P = P[P["n"] >= 5].reset_index(drop=True)
P["raw_pct"] = P["raw"].rank(pct=True)
P["adj_pct"] = P["adj"].rank(pct=True)
P["wedge"] = P["raw_pct"] - P["adj_pct"]
P["terrain"] = P["raw"] - P["adj"]
P["ln_n"] = np.log(P["n"])
pre_orgs = h.groupby("partner_uuid")["org_uuid"].agg(set)

po = dn[(dn["dt"] > CUT) & (dn["dt"] <= END)].copy()
po["r"] = resid_loo(po)
po = po[np.isfinite(po["r"])]
po["overlap"] = [o in pre_orgs.get(p, set()) for p, o in zip(po["partner_uuid"], po["org_uuid"])]
pa_all = po.groupby("partner_uuid").agg(post_adj=("r", "mean"), post_n=("r", "size"))
pa_ex = po[~po["overlap"]].groupby("partner_uuid").agg(post_adj_excl=("r", "mean"), post_n_excl=("r", "size"))
pa_same = po[po["overlap"]].groupby("partner_uuid").agg(post_adj_same=("r", "mean"), post_n_same=("r", "size"))
P = P.join(pa_all, on="partner_uuid").join(pa_ex, on="partner_uuid").join(pa_same, on="partner_uuid")
sh_overlap = float(po.loc[po["partner_uuid"].isin(P["partner_uuid"]), "overlap"].mean())
log(f"[구성] 파트너 {len(P):,} · 사후기 관측 {int(P['post_adj'].notna().sum()):,} · "
    f"사후기 딜 중 사전기 기업 후속 비중 {sh_overlap:.1%} · 제외 후 관측 {int(P['post_adj_excl'].notna().sum()):,}")

# ── 외부 평가자 결과 (p001_25 구성 그대로) ────────────────────────────────
pt = CTX.partners.dropna(subset=["funding_round_uuid", "investor_uuid", "partner_uuid"])
r = CTX.rounds.dropna(subset=["announced_on"])[["uuid", "announced_on"]].copy()
r["rdt"] = pd.to_datetime(r["announced_on"], errors="coerce")
A = pt.merge(r, left_on="funding_round_uuid", right_on="uuid").dropna(subset=["rdt"])
firm_first = A.groupby("investor_uuid")["rdt"].min()
fut_firms = A[(A["rdt"] > CUT) & (A["rdt"] <= END)].groupby("partner_uuid")["investor_uuid"].agg(set)
pre_n = A[A["rdt"] <= CUT].groupby("investor_uuid").size()
F = CTX.funds.dropna(subset=["entity_uuid", "announced_on"]).copy()
F["fdt"] = pd.to_datetime(F["announced_on"], errors="coerce")
F["famt"] = pd.to_numeric(F["raised_amount_usd"], errors="coerce")
F = F[(F["fdt"] > CUT) & (F["fdt"] <= pd.Timestamp("2024-12-31"))]
fund_any, fund_amt = set(F["entity_uuid"]), F.groupby("entity_uuid")["famt"].max()
hm = dict(zip(P["partner_uuid"], P["firm"]))
lp_any, lp_amt, recv = [], [], []
for pid in P["partner_uuid"]:
    fs = fut_firms.get(pid, set()) - {hm[pid]}
    nf = [f for f in fs if firm_first.get(f, pd.Timestamp("1900-01-01")) > CUT]
    got = [f for f in nf if f in fund_any]
    lp_any.append(1.0 if got else (0.0 if nf else np.nan))
    am = [x for x in (fund_amt.get(f, np.nan) for f in got) if x == x and x > 0]
    lp_amt.append(np.log(max(am)) if am else np.nan)
    recv.append(np.log1p(max([pre_n.get(f, 0) for f in fs] + [0])) if fs else np.nan)
P["lp_any"], P["lp_amt"], P["recv_q"] = lp_any, lp_amt, recv


def fit(s, y, xc):
    X = np.column_stack([s[c].to_numpy(float) for c in xc] + [np.ones(len(s))])
    return np.linalg.lstsq(X, s[y].to_numpy(float), rcond=None)[0]


def boot(df, y, xc, k=0, nb=NB):
    dd = df.dropna(subset=[y] + xc)
    if len(dd) < 100:
        return None
    b0 = float(fit(dd, y, xc)[k])
    grp = {c: g.index.to_numpy() for c, g in dd.groupby("firm")}
    keys = list(grp)
    bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(keys), len(keys))
        s = dd.loc[np.concatenate([grp[keys[i]] for i in pick])]
        try:
            bs.append(float(fit(s, y, xc)[k]))
        except Exception:
            pass
    lo, hi = qci(np.array(bs))
    return {"coef": round(b0, 5), "ci95": [round(lo, 5), round(hi, 5)], "n": int(len(dd)),
            "n_firms": int(dd["firm"].nunique()), "sig": bool(lo > 0 or hi < 0)}


OUT = {"share_post_deals_overlapping_pre_companies": round(sh_overlap, 4)}
log("\n" + "=" * 92)
log("[T1] 기업 중복 제외 — post_adj_excl ← raw_pct | adj_pct")
log("=" * 92)
T1 = boot(P, "post_adj_excl", ["raw_pct", "adj_pct", "ln_n", "fp"])
T1s = boot(P, "post_adj_same", ["raw_pct", "adj_pct", "ln_n", "fp"])
OUT["T1_excl_overlap"] = dict(T1, share_of_base=round(T1["coef"] / BASE, 3)) if T1 else None
OUT["T1b_overlap_only"] = T1s
if T1:
    log(f"  제외 후  β={T1['coef']:+.5f} [{T1['ci95'][0]:+.5f},{T1['ci95'][1]:+.5f}] "
        f"{'유의' if T1['sig'] else 'ns'}  기준 대비 {T1['coef'] / BASE * 100:.0f}%  (n={T1['n']:,})")
if T1s:
    log(f"  중복만   β={T1s['coef']:+.5f} [{T1s['ci95'][0]:+.5f},{T1s['ci95'][1]:+.5f}] "
        f"{'유의' if T1s['sig'] else 'ns'}  (n={T1s['n']:,})")

log("\n" + "=" * 92)
log("[T2] Panel C 에 사전기 후기단계 비중(late_sh) 통제 — 펀드 크기의 기계적 경로")
log("=" * 92)
T2 = {}
for y in ("lp_any", "lp_amt", "recv_q"):
    base = boot(P, y, ["wedge", "adj_pct", "ln_n", "fp"])
    ctrl = boot(P, y, ["wedge", "adj_pct", "late_sh", "ln_n", "fp"])
    late = boot(P, y, ["late_sh", "adj_pct", "ln_n", "fp"])
    chg = (ctrl["coef"] - base["coef"]) / base["coef"] if (base and ctrl and base["coef"]) else np.nan
    T2[y] = {"no_late_ctrl": base, "with_late_ctrl": ctrl, "late_sh_own": late,
             "pct_change": round(float(chg) * 100, 1) if chg == chg else None}
    if base and ctrl:
        log(f"  {y:<7} composition: {base['coef']:+.4f} → late_sh 통제 {ctrl['coef']:+.4f} "
            f"[{ctrl['ci95'][0]:+.4f},{ctrl['ci95'][1]:+.4f}] {'유의' if ctrl['sig'] else 'ns'} "
            f"({chg * 100:+.0f}%)   | late_sh 자체 {late['coef']:+.4f} [{late['ci95'][0]:+.4f},{late['ci95'][1]:+.4f}]")
OUT["T2_late_stage_control"] = T2

log("\n" + "=" * 92)
log("[T3] 무조건 composition — 레벨 vs 백분위 (같은 LOO 패널)")
log("=" * 92)
T3l = boot(P, "post_adj", ["terrain", "ln_n", "fp"])
T3p = boot(P, "post_adj", ["wedge", "ln_n", "fp"])
OUT["T3_unconditional_level"] = T3l
OUT["T3_unconditional_percentile"] = T3p
log(f"  레벨   terrain → post_adj  β={T3l['coef']:+.5f} [{T3l['ci95'][0]:+.5f},{T3l['ci95'][1]:+.5f}] {'유의' if T3l['sig'] else 'ns'}")
log(f"  백분위 wedge   → post_adj  β={T3p['coef']:+.5f} [{T3p['ci95'][0]:+.5f},{T3p['ci95'][1]:+.5f}] {'유의' if T3p['sig'] else 'ns'}")

g1 = bool(T1 and T1["sig"] and T1["coef"] / BASE >= 0.5)
amt_ok = bool(T2["lp_amt"]["with_late_ctrl"] and T2["lp_amt"]["with_late_ctrl"]["sig"])
status = "GO" if g1 else "PARTIAL"
call = (f"**T1 통과 — 중복 제외 후 {T1['coef'] / BASE * 100:.0f}% 유지, CI 0 배제. " if g1 else
        f"**T1 실패 — 중복 제외 후 {(T1['coef'] / BASE * 100) if T1 else float('nan'):.0f}%. ") + \
       (f"T2 lp_amt 는 late_sh 통제 후에도 유의**" if amt_ok else
        "T2 lp_amt 는 late_sh 통제 시 유의 상실 → Panel C 펀드 크기 행을 '단계 집중과 분리 불가'로 재표기**")
verdict = (f"중복 비중 {sh_overlap:.1%} | T1 {T1['coef']:+.4f} ({T1['coef'] / BASE * 100:.0f}%) | "
           + " | ".join(f"T2 {y}: {v['no_late_ctrl']['coef']:+.3f}→{v['with_late_ctrl']['coef']:+.3f} ({v['pct_change']:+.0f}%)"
                        for y, v in T2.items() if v["no_late_ctrl"] and v["with_late_ctrl"])
           + f" | T3 레벨 {T3l['coef']:+.4f} vs 백분위 {T3p['coef']:+.4f} — " + call)
emit("P001-29", "리뷰어 선제 검정 II — 기업 중복 제외 · 단계 집중 통제 · 단위 병기", status, OUT,
     prediction="T1 중복 20~40%, 제외 후 ≥50% 유지 · T2 lp_amt ≥40% 감소, lp_any/recv_q <30% · "
                "T3 레벨 +, 백분위 ≈0/−",
     verdict=verdict, kill_met=False, n=int(len(P)),
     extra={"stage": 7, "feeds": "내부리뷰 R2 대응 · Table 7/9", "slug": "overlap_stage", "builds_on": "P001-28"})
log("done")
