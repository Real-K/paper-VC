# -*- coding: utf-8 -*-
"""p001_30 — 내부리뷰 R2 결정 검정: composition 성분 분해 · 연공 · 회사 · 고정지평 · leave-partner-out

[왜] 라운드 2 에서 식별·재무·측정·적대 심판 4명이 **독립적으로 같은 결함**을 짚었다.
 §6 의 +0.097 (post_adj ← raw_pct | adj_pct) 이 "구성이 정보를 담는다"인지 다음과 구분되지 않는다:
 (a) **빈티지/연공** — 벤치마크가 연도×섹터×단계이고 exit_ever 가 표본 끝 기준이라 오래된 딜이
     기계적으로 raw 가 높다 → terrain 이 빈티지 믹스(≈재직연차)를 담는다. 연차는 장래 성과·
     펀드조성·관측 이탈(S1 −0.42)을 모두 설명할 수 있다.
 (b) **회사 품질** — 셀에 회사가 없다. 대형 다단계 회사는 후기단계(유리한 terrain)를 하고
     매 기간 셀 내 알파를 갖는다.
 (c) **벤치마크 잡음 공유** — LOO 는 leave-one-row-out; 파트너의 같은 셀 다른 딜과 공동귀속
     행이 벤치마크에 남는다.
 (d) **지평 비대칭** — post_adj 는 2021–23 딜에서 잔차가 ~0 으로 압축된다.
 세 심판이 제시한 결정 검정을 하나의 하네스로 묶는다.

[구성] LOO 셀 벤치마크(P001-27 B). 사전기 딜 i 의 셀 (y, sec, st) 에 대해
   b_year = LOO 연도 평균 · b_ys = LOO (연도,단계) 평균 · b_yss = LOO (연도,섹터,단계) 평균
   b_yss = b_year + (b_ys − b_year) + (b_yss − b_ys)  =  vintage + stage|year + sector|year,stage
 파트너 수준: terrain_v = mean b_year · terrain_s = mean(b_ys−b_year) · terrain_cs = mean(b_yss−b_ys)
 합 = terrain (레벨).  adj = mean(exit_ever − b_yss).
 연공: tenure = 2017-10-31 − 첫 귀속 딜(전 표본, partners 테이블) 연수 · 첫딜연도 구간 FE
 회사: firm_adj_mp = 홈 회사 사전기 LOO 잔차 평균(파트너 p 자신 제외) · ln 회사 사전기 딜수 ·
       회사 FE 버전(파트너 2명+ 회사)
 고정지평: fon(36개월 후속) 을 결과로 — 사전·사후 모두 같은 지평. 사후 창 ≤ 2020-10.
 leave-partner-out: 셀합 − 파트너 p 의 그 셀 딜 전부, 분모 n_c − k_p.

[사양] (전부 레벨, 군집 = 홈 회사, 부트 400)
 R1 post_adj ~ terrain_v + terrain_s + terrain_cs + adj + ln_n + fp        (분해)
 R2 R1 + tenure + tenure² + 첫딜연도 구간 FE                                  (연공)
 R3 R2 + firm_adj_mp + ln_firm_n                                            (회사 통제)
 R4 R3 를 홈 회사 내 demean (파트너 2명+ 회사)                                (회사 FE)
 R5 고정지평: post_fon_adj ~ terrain_fon + adj_fon + ln_n + fp                 (지평)
 R6 leave-partner-out: post_adj_lpo ~ raw_lpo + adj_lpo + ln_n + fp  → β_raw|adj  (잡음 공유)
 R7 has_post ~ terrain_v + terrain_s + terrain_cs + adj + tenure + ln_n + fp   (선택 분해)
 R8 같은 회귀에서의 adj 계수 (40% 비율의 올바른 분모) — R1 의 adj 계수를 그대로 보고

[사전 예측] (결과 조회 전, 2026-09-08)
 정보 가설:  terrain_s 및/또는 terrain_cs > 0, R2·R3·R4 에서 유지(≥50%); terrain_v 는 tenure 투입 후 ≈0.
 연공 가설:  terrain_v 가 적재를 가져가고 tenure 투입 후 총효과가 0 쪽으로 붕괴; R7 에서 terrain_v·tenure 가 −0.42 를 설명.
 회사 가설:  R3·R4 에서 총효과 붕괴, firm_adj_mp 가 적재.
 R5 부호 유지 · R6 은 +0.10 의 ±30%.
 **내 사전 판단**: 연공 성분이 상당할 것(§3 이 tenure 가 단계 편중의 47% 라 했다). terrain_s 가
 살아남으면 프레임 유지(단계 선택이 정보), terrain_v 만 남으면 REFRAME (연공이지 구성이 아님).
[게이트] R4(회사 FE) 에서 terrain_s 또는 terrain_cs 가 CI 0 배제 → "구성 정보" 유지.
 둘 다 실패하고 terrain_v/tenure 만 남으면 → §6 을 "연공·회사 품질이 걷어내진다"로 REFRAME.
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
NB = 400
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR",
      "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}
NAEU = EU | {"USA", "CAN"}
CUT = pd.Timestamp("2017-10-31")
END = pd.Timestamp("2023-10-31")
END_FON = pd.Timestamp("2020-10-31")


def log(*a):
    print(*a, flush=True)


d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v2.parquet"))
d["dt"] = pd.to_datetime(d["dt"])
dn = d[d["country_code"].isin(NAEU)].copy()
dn["y"] = dn["year"].astype(str)
dn["ys"] = dn["y"] + "|" + dn["stage"]
dn["yss"] = dn["y"] + "|" + dn["cat"] + "|" + dn["stage"]


def loo(df, key, ycol):
    g = df.groupby(key)[ycol]
    s, n = g.transform("sum"), g.transform("size")
    return np.where(n > 1, (s - df[ycol]) / np.maximum(n - 1, 1), np.nan)


def lpo(df, key, ycol):
    """leave-partner-out: 셀합에서 파트너 p 의 그 셀 딜 전부를 뺀다."""
    g = df.groupby(key)[ycol]
    s, n = g.transform("sum"), g.transform("size")
    gp = df.groupby([key, "partner_uuid"])[ycol]
    sp, np_ = gp.transform("sum"), gp.transform("size")
    den = n - np_
    return np.where(den > 0, (s - sp) / np.maximum(den, 1), np.nan)


def build(df, ycol):
    out = df.copy()
    out["b_year"] = loo(out, "y", ycol)
    out["b_ys"] = loo(out, "ys", ycol)
    out["b_yss"] = loo(out, "yss", ycol)
    out["b_lpo"] = lpo(out, "yss", ycol)
    out["r"] = out[ycol] - out["b_yss"]
    out["r_lpo"] = out[ycol] - out["b_lpo"]
    out["t_v"] = out["b_year"]
    out["t_s"] = out["b_ys"] - out["b_year"]
    out["t_cs"] = out["b_yss"] - out["b_ys"]
    return out


# ── 사전기 (exit_ever) ─────────────────────────────────────────────────────
h = build(dn[dn["dt"] <= CUT], "exit_ever")
h = h[np.isfinite(h["r"])]
P = h.groupby("partner_uuid").agg(
    raw=("exit_ever", "mean"), adj=("r", "mean"), n=("exit_ever", "size"), fp=("fp", "first"),
    t_v=("t_v", "mean"), t_s=("t_s", "mean"), t_cs=("t_cs", "mean"),
    raw_lpo=("exit_ever", "mean"), adj_lpo=("r_lpo", "mean"),
    firm=("investor_uuid", lambda s: s.mode().iloc[0])).reset_index()
P = P[P["n"] >= 5].reset_index(drop=True)
P["terrain"] = P["raw"] - P["adj"]
P["ln_n"] = np.log(P["n"])
log(f"[분해 검산] terrain − (t_v+t_s+t_cs) 최대차 {np.max(np.abs(P['terrain'] - (P['t_v'] + P['t_s'] + P['t_cs']))):.2e}")

# 연공: 전 표본 첫 귀속 딜
pt = CTX.partners.dropna(subset=["funding_round_uuid", "partner_uuid"])
r = CTX.rounds.dropna(subset=["announced_on"])[["uuid", "announced_on"]].copy()
r["rdt"] = pd.to_datetime(r["announced_on"], errors="coerce")
A = pt.merge(r, left_on="funding_round_uuid", right_on="uuid").dropna(subset=["rdt"])
first = A.groupby("partner_uuid")["rdt"].min()
P["first_dt"] = P["partner_uuid"].map(first)
P["tenure"] = (CUT - P["first_dt"]).dt.days / 365.25
P["tenure2"] = P["tenure"] ** 2
P["fy"] = P["first_dt"].dt.year.clip(lower=2005)
P["fy_bin"] = pd.cut(P["fy"], [0, 2008, 2011, 2013, 2015, 2100], labels=False)
for b in range(1, 5):
    P[f"fyb{b}"] = (P["fy_bin"] == b).astype(float)
log(f"[연공] tenure 관측 {P['tenure'].notna().mean():.1%} · 중위 {P['tenure'].median():.1f}년 · "
    f"corr(tenure, t_v)={P[['tenure', 't_v']].corr().iloc[0, 1]:+.3f} · corr(tenure, terrain)={P[['tenure', 'terrain']].corr().iloc[0, 1]:+.3f}")

# 회사: 파트너 p 제외 홈 회사 사전기 잔차 평균 + 회사 규모
h2 = h[h["partner_uuid"].isin(P["partner_uuid"])]
fs = h2.groupby("investor_uuid")["r"].agg(["sum", "size"])
ps = h2.groupby(["investor_uuid", "partner_uuid"])["r"].agg(["sum", "size"])
fam, fn = [], []
for p_, f_ in zip(P["partner_uuid"], P["firm"]):
    S, N = fs.loc[f_, "sum"], fs.loc[f_, "size"]
    if (f_, p_) in ps.index:
        S -= ps.loc[(f_, p_), "sum"]; N -= ps.loc[(f_, p_), "size"]
    fam.append(S / N if N > 0 else np.nan); fn.append(N)
P["firm_adj_mp"] = fam
P["ln_firm_n"] = np.log1p(fn)

# 사후기
po = build(dn[(dn["dt"] > CUT) & (dn["dt"] <= END)], "exit_ever")
po = po[np.isfinite(po["r"])]
P = P.join(po.groupby("partner_uuid").agg(post_adj=("r", "mean"), post_adj_lpo=("r_lpo", "mean")), on="partner_uuid")
P["has_post"] = P["post_adj"].notna().astype(float)

# 고정지평 (fon: 36개월 후속) — 사전·사후 동일 지평, 사후 창 ≤ 2020-10
hf = build(dn[(dn["dt"] <= CUT) & dn["fon"].notna()], "fon")
hf = hf[np.isfinite(hf["r"])]
Pf = hf.groupby("partner_uuid").agg(raw_fon=("fon", "mean"), adj_fon=("r", "mean"), n_fon=("fon", "size"))
Pf["terrain_fon"] = Pf["raw_fon"] - Pf["adj_fon"]
pf2 = build(dn[(dn["dt"] > CUT) & (dn["dt"] <= END_FON) & dn["fon"].notna()], "fon")
pf2 = pf2[np.isfinite(pf2["r"])]
Pf = Pf.join(pf2.groupby("partner_uuid").agg(post_fon_adj=("r", "mean")))
P = P.join(Pf, on="partner_uuid")
log(f"[구성] 파트너 {len(P):,} · post_adj {int(P['post_adj'].notna().sum()):,} · "
    f"고정지평 post_fon_adj {int(P['post_fon_adj'].notna().sum()):,} · LPO post {int(P['post_adj_lpo'].notna().sum()):,}")


def fit(s, y, xc):
    X = np.column_stack([s[c].to_numpy(float) for c in xc] + [np.ones(len(s))])
    return np.linalg.lstsq(X, s[y].to_numpy(float), rcond=None)[0]


def boot(df, y, xc, keys, nb=NB, demean_firm=False):
    dd = df.dropna(subset=[y] + xc).copy()
    if demean_firm:
        cnt = dd.groupby("firm")["firm"].transform("size")
        dd = dd[cnt >= 2].copy()
        for c in [y] + xc:
            dd[c] = dd[c] - dd.groupby("firm")[c].transform("mean")
    if len(dd) < 150:
        return None
    b = fit(dd, y, xc)
    grp = {c: g.index.to_numpy() for c, g in dd.groupby("firm")}
    kl = list(grp)
    bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(kl), len(kl))
        s = dd.loc[np.concatenate([grp[kl[i]] for i in pick])]
        try:
            bs.append(fit(s, y, xc))
        except Exception:
            pass
    bs = np.array(bs)
    out = {"n": int(len(dd)), "n_firms": int(dd["firm"].nunique())}
    for k in keys:
        i = xc.index(k)
        lo, hi = qci(bs[:, i])
        out[k] = {"coef": round(float(b[i]), 5), "ci95": [round(lo, 5), round(hi, 5)],
                  "sig": bool(lo > 0 or hi < 0)}
    return out


def show(tag, res, keys):
    if not res:
        log(f"  {tag}: 표본 부족"); return
    parts = [f"{k}={res[k]['coef']:+.4f} [{res[k]['ci95'][0]:+.3f},{res[k]['ci95'][1]:+.3f}]{'*' if res[k]['sig'] else ''}"
             for k in keys if k in res]
    log(f"  {tag:<28} n={res['n']:,} | " + " · ".join(parts))


OUT = {}
TC = ["t_v", "t_s", "t_cs"]
log("\n" + "=" * 100)
log("[R1–R4] post_adj ← terrain 분해 (+adj) → +연공 → +회사 통제 → 회사 FE")
log("=" * 100)
R1 = boot(P, "post_adj", TC + ["adj", "ln_n", "fp"], TC + ["adj"]); show("R1 분해", R1, TC + ["adj"]); OUT["R1_decomp"] = R1
TEN = ["tenure", "tenure2", "fyb1", "fyb2", "fyb3", "fyb4"]
R2 = boot(P, "post_adj", TC + ["adj", "ln_n", "fp"] + TEN, TC + ["adj", "tenure"]); show("R2 +연공", R2, TC + ["tenure"]); OUT["R2_tenure"] = R2
R3 = boot(P, "post_adj", TC + ["adj", "ln_n", "fp"] + TEN + ["firm_adj_mp", "ln_firm_n"], TC + ["firm_adj_mp"]); show("R3 +회사통제", R3, TC + ["firm_adj_mp"]); OUT["R3_firm_ctrl"] = R3
R4 = boot(P, "post_adj", TC + ["adj", "ln_n", "fp"] + TEN, TC, demean_firm=True); show("R4 회사 FE", R4, TC); OUT["R4_firm_FE"] = R4
# 총 terrain 도 같은 사다리로
R1t = boot(P, "post_adj", ["terrain", "adj", "ln_n", "fp"], ["terrain", "adj"]); show("R1t 총terrain", R1t, ["terrain", "adj"]); OUT["R1t_total"] = R1t
R2t = boot(P, "post_adj", ["terrain", "adj", "ln_n", "fp"] + TEN, ["terrain"]); show("R2t 총 +연공", R2t, ["terrain"]); OUT["R2t_total_tenure"] = R2t
R4t = boot(P, "post_adj", ["terrain", "adj", "ln_n", "fp"] + TEN, ["terrain"], demean_firm=True); show("R4t 총 회사FE", R4t, ["terrain"]); OUT["R4t_total_firmFE"] = R4t

log("\n" + "=" * 100)
log("[R5] 고정지평 (fon 36m, 사후 ≤2020-10) · [R6] leave-partner-out")
log("=" * 100)
R5 = boot(P, "post_fon_adj", ["terrain_fon", "adj_fon", "ln_n", "fp"], ["terrain_fon", "adj_fon"]); show("R5 고정지평", R5, ["terrain_fon", "adj_fon"]); OUT["R5_fixed_horizon"] = R5
R6 = boot(P, "post_adj_lpo", ["raw_lpo", "adj_lpo", "ln_n", "fp"], ["raw_lpo", "adj_lpo"]); show("R6 LPO raw|adj", R6, ["raw_lpo", "adj_lpo"]); OUT["R6_leave_partner_out"] = R6

log("\n" + "=" * 100)
log("[R7] 사후기 관측 선택의 분해 — has_post ← terrain 성분 + 연공")
log("=" * 100)
R7 = boot(P, "has_post", TC + ["adj", "ln_n", "fp"], TC); show("R7 선택(분해)", R7, TC); OUT["R7_selection_decomp"] = R7
R7b = boot(P, "has_post", TC + ["adj", "ln_n", "fp"] + TEN, TC + ["tenure"]); show("R7b 선택 +연공", R7b, TC + ["tenure"]); OUT["R7b_selection_tenure"] = R7b

# 원고가 인용하는 상관 — 산출물에 기록해 검증 가능하게 (verify_draft 화이트리스트 사용 금지)
OUT["corr_tenure_terrain"] = round(float(P[["tenure", "terrain"]].corr().iloc[0, 1]), 4)
OUT["corr_tenure_vintage"] = round(float(P[["tenure", "t_v"]].corr().iloc[0, 1]), 4)

# ── 판정 ────────────────────────────────────────────────────────────────────
def sig(res, k):
    return bool(res and k in res and res[k]["sig"])
info_R4 = sig(R4, "t_s") or sig(R4, "t_cs")
info_R2 = sig(R2, "t_s") or sig(R2, "t_cs")
v_dom = sig(R1, "t_v") and not (sig(R1, "t_s") or sig(R1, "t_cs"))
tot_survive_firmFE = sig(R4t, "terrain")
if info_R4:
    call = "**정보 가설 유지 — 회사 FE 하에서도 단계/섹터 성분이 장래 셀 내 성과를 예측**"
    status = "GO"
elif info_R2 and not info_R4:
    call = "**부분 — 연공 통제엔 살지만 회사 FE 에서 소멸: 구성 정보의 상당 부분이 회사 수준. §6 을 '회사 품질' 쪽으로 REFRAME**"
    status = "PARTIAL"
elif v_dom:
    call = "**REFRAME — 적재는 빈티지 성분(연공)에 있다. '구성이 정보'가 아니라 '연공이 걷어내진다'**"
    status = "PARTIAL"
else:
    call = "**REFRAME — 분해·연공·회사 통제 후 어느 성분도 유의하지 않다. §6 의 정보 주장 철회**"
    status = "KILL"
verdict = (f"R1 t_v/t_s/t_cs = " + "/".join(f"{R1[k]['coef']:+.3f}{'*' if R1[k]['sig'] else ''}" for k in TC) +
           f" · adj {R1['adj']['coef']:+.3f} | R2(+연공) " + "/".join(f"{R2[k]['coef']:+.3f}{'*' if R2[k]['sig'] else ''}" for k in TC) +
           f" tenure {R2['tenure']['coef']:+.4f}{'*' if R2['tenure']['sig'] else ''} | R4(회사FE) " +
           "/".join(f"{R4[k]['coef']:+.3f}{'*' if R4[k]['sig'] else ''}" for k in TC) +
           f" | 총terrain: R1t {R1t['terrain']['coef']:+.3f}{'*' if R1t['terrain']['sig'] else ''} → R2t {R2t['terrain']['coef']:+.3f}{'*' if R2t['terrain']['sig'] else ''} → R4t {R4t['terrain']['coef']:+.3f}{'*' if R4t['terrain']['sig'] else ''}"
           f" | R5 고정지평 terrain {R5['terrain_fon']['coef']:+.3f}{'*' if R5['terrain_fon']['sig'] else ''} | R6 LPO {R6['raw_lpo']['coef']:+.3f}{'*' if R6['raw_lpo']['sig'] else ''}"
           f" | R7 선택 t_v {R7['t_v']['coef']:+.3f}{'*' if R7['t_v']['sig'] else ''} tenure {R7b['tenure']['coef']:+.4f}{'*' if R7b['tenure']['sig'] else ''} — " + call)
emit("P001-30", "R2 결정 검정 — terrain 분해(빈티지/단계/섹터) · 연공 · 회사 FE · 고정지평 · leave-partner-out",
     status, OUT,
     prediction="연공 성분 상당; t_s 생존 시 프레임 유지, t_v 만 남으면 REFRAME; R5 부호 유지; R6 ±30%",
     verdict=verdict, kill_met=(status == "KILL"), n=int(len(P)),
     extra={"stage": 7, "feeds": "내부리뷰 R2 편집 결정", "slug": "terrain_decomp", "builds_on": "P001-27/28/29"})
log("done")
