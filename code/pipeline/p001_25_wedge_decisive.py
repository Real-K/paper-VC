# -*- coding: utf-8 -*-
"""p001_25 — ① 의 결정적 검정: wedge 가 장래 성과를 예측하지 않는데도 평가자가 보상하는가

[논리] `P001-23` 이 두 가지를 확립했다.
 (1) `P001-22` 의 P1 은 **terrain 계수**를 검정했으므로 철회 판정은 **무효**다.
 (2) 평가자 쪽을 올바르게 겨냥한 두 검정이 **wedge 양수**다 (펀드조성 +0.374 · 수용사품질
     +1.047, 개별 ns).
그러나 그것만으로는 ① 이 서지 않는다. **wedge 가 장래 실력을 담고 있으면 평가자는 속는 것이
아니라 합리적**이다. ① 이 서려면 둘이 동시에 필요하다:
  (a) **wedge 가 장래 조정성과를 예측하지 않는다** ← 이 스크립트의 B1. **해석을 가른다.**
  (b) **그런데도 평가자가 wedge 를 보상한다** ← B2 로 검정력을 확보한다.

wedge = raw_pct − adj_pct. `adj = raw − 셀평균` 이므로 wedge 는 **파트너가 투자한 셀들의
기저 출구율**(유리한 terrain)을 잰다. "원시 랭크가 조정이 정당화하는 것보다 부풀려진 정도."

────────────────────────────────────────────────────────────────────────────
B1 — wedge 가 장래 조정성과를 예측하는가 (해석 검정, 결정적)
────────────────────────────────────────────────────────────────────────────
사전기(≤2017-10) 로 raw/adj/wedge 를 만들고, **사후기(2017-11~) 딜로 조정성과를 다시 계산**한다.
  y = 사후기 조정 출구율(post_adj) = mean(exit_ever − 사후기 셀평균)
  x = 사전기 wedge, 통제 = 사전기 adj_pct + ln(딜수) + fp
**β_wedge ≈ 0 이고 CI 가 좁으면**: wedge 는 장래 실력 정보를 담지 않는다 → 평가자가 그것을
보상하는 것은 **오염된 신호에 반응하는 것**이다. ① 의 전제가 확립된다.
**β_wedge > 0 유의면**: wedge 는 실력 신호다 → 평가자는 합리적 → **① 은 죽는다.** 그렇게 쓴다.

────────────────────────────────────────────────────────────────────────────
B2 — 평가자 보상의 결합 검정 (레버 12) + 조성액 연속 결과
────────────────────────────────────────────────────────────────────────────
P001-23 의 두 결과는 개별 ns 였다. 결과 벡터를 결합한다:
  y1 신생회사 펀드 조성 여부 (스핀아웃 380, 조성 221)
  y2 **log 조성액** (185건 — 이분보다 정보량이 크다. P001-23 에서 미사용)
  y3 수용사 사전 딜수 log1p (이동 712)
**하나의 위약 치환마다 세 결과를 모두 재추정**해 귀무 상관을 보존하고 Mahalanobis RI 로 결합.
위약 = 파트너 안에서 wedge 를 치환할 수 없으므로(파트너당 1행) **wedge 를 무작위 재배정**한다.

────────────────────────────────────────────────────────────────────────────
B3 — 표본 확대 (레버 B-5). **레버를 쌓지 않는다** — B1/B2 와 별개 팔로만 보고한다
────────────────────────────────────────────────────────────────────────────
MIN_DEALS 5 → 3. 랭크 모집단이 바뀌므로 별개 사양이다.

[사전 예측] (결과 조회 전, 2026-09-08)
 C1 **β_wedge(장래 조정성과) ≈ 0** 이고 CI 가 ±0.05 안 — wedge 는 실력 정보를 담지 않는다.
    (근거: adj 는 셀평균을 뺀 것이므로 terrain 은 정의상 실력이 아니다. 단 terrain 선택 자체가
     실력의 신호일 수 있으므로 검정해야 한다.)
 C2 결합 RI p < 0.10 이나 0.05 는 넘지 못할 것 (개별 ns 3개의 결합).
 C3 조성액(연속)이 이분 결과보다 계수 t 가 크다.
 C4 표본 확대로 CI 가 10~20% 좁아지나 부호는 유지.
[게이트] ① 재개 = **C1 성립(β_wedge 장래성과 ≈ 0, CI 좁음) AND B2 결합 RI p < 0.05**.
 하나라도 실패하면 재개하지 않고 그대로 기록한다 (가드레일 §1·§7).
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
NB, NPLAC = 400, 400
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR",
      "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}
NAEU = EU | {"USA", "CAN"}
EARLY = {"seed", "angel", "pre_seed", "equity_crowdfunding", "convertible_note"}
CUT = pd.Timestamp("2017-10-31")
END = pd.Timestamp("2023-10-31")


def log(*a):
    print(*a, flush=True)


d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v1.parquet"))
d["dt"] = pd.to_datetime(d["dt"])
dn = d[d["country_code"].isin(NAEU)].copy()
dn["mcell"] = dn["year"] + "|" + dn["cat"] + "|" + dn["stage"]
dn["early"] = dn["stage"].isin(EARLY).astype(float)

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
fund_any = set(F["entity_uuid"])
fund_amt = F.groupby("entity_uuid")["famt"].max()


def build(min_deals):
    hist = dn[dn["dt"] <= CUT].copy()
    hist["resid"] = hist["exit_ever"] - hist.groupby("mcell")["exit_ever"].transform("mean")
    P = hist.groupby("partner_uuid").agg(
        raw=("exit_ever", "mean"), adj=("resid", "mean"), n=("exit_ever", "size"),
        fp=("fp", "first"), early_sh=("early", "mean"), ncat=("cat", "nunique"),
        firm=("investor_uuid", lambda s: s.mode().iloc[0])).reset_index()
    P = P[P["n"] >= min_deals].reset_index(drop=True)
    P["raw_pct"] = P["raw"].rank(pct=True)
    P["adj_pct"] = P["adj"].rank(pct=True)
    P["wedge"] = P["raw_pct"] - P["adj_pct"]
    P["ln_n"] = np.log(P["n"])
    # 사후기 조정성과
    post = dn[(dn["dt"] > CUT) & (dn["dt"] <= END)].copy()
    post["presid"] = post["exit_ever"] - post.groupby("mcell")["exit_ever"].transform("mean")
    pa = post.groupby("partner_uuid").agg(post_adj=("presid", "mean"), post_n=("presid", "size"))
    P = P.join(pa, on="partner_uuid")
    # 평가자 쪽 결과
    mv, sp, lp_any, lp_amt, recv = [], [], [], [], []
    hm = dict(zip(P["partner_uuid"], P["firm"]))
    for pid in P["partner_uuid"]:
        fs = fut_firms.get(pid, set()) - {hm[pid]}
        mv.append(1.0 if fs else 0.0)
        nf = [f for f in fs if firm_first.get(f, pd.Timestamp("1900-01-01")) > CUT]
        sp.append(1.0 if nf else 0.0)
        got = [f for f in nf if f in fund_any]
        lp_any.append(1.0 if got else (0.0 if nf else np.nan))
        am = [fund_amt.get(f, np.nan) for f in got]
        am = [x for x in am if x == x and x > 0]
        lp_amt.append(np.log(max(am)) if am else np.nan)
        recv.append(np.log1p(max([pre_n.get(f, 0) for f in fs] + [0])) if fs else np.nan)
    P["move"], P["spin"] = mv, sp
    P["lp_any"], P["lp_amt"], P["recv_q"] = lp_any, lp_amt, recv
    return P


CTRL = ["adj_pct", "ln_n", "fp"]


def fit(s, ycol, xc):
    X = np.column_stack([s[c].to_numpy(float) for c in xc] + [np.ones(len(s))])
    return np.linalg.lstsq(X, s[ycol].to_numpy(float), rcond=None)[0]


def boot(df, ycol, xc, nb=NB, gcol="firm"):
    dd = df.dropna(subset=[ycol] + xc)
    if dd["firm"].nunique() < 40 or len(dd) < 100:
        return None
    b0 = float(fit(dd, ycol, xc)[0])
    grp = {c: g.index.to_numpy() for c, g in dd.groupby(gcol)}
    keys = list(grp)
    bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(keys), len(keys))
        s = dd.loc[np.concatenate([grp[keys[i]] for i in pick])]
        try:
            bs.append(float(fit(s, ycol, xc)[0]))
        except Exception:
            pass
    lo, hi = qci(np.array(bs))
    return {"coef": round(b0, 5), "ci95": [round(lo, 5), round(hi, 5)],
            "n": int(len(dd)), "n_firms": int(dd["firm"].nunique()),
            "sig": bool(lo > 0 or hi < 0)}


P = build(5)
log(f"[구성] 파트너 {len(P):,} · 사후기 관측 {int(P['post_adj'].notna().sum()):,} · "
    f"스핀아웃 {int(P['spin'].sum())} · lp_any 관측 {int(P['lp_any'].notna().sum())} · "
    f"lp_amt {int(P['lp_amt'].notna().sum())} · recv_q {int(P['recv_q'].notna().sum())}")

OUT = {}
# ══ B1 해석 검정 ═══════════════════════════════════════════════════════════
log("\n" + "=" * 96)
log("[B1] wedge 가 **장래 조정성과**를 예측하는가 — ① 의 해석을 가르는 검정")
log("=" * 96)
B1 = boot(P, "post_adj", ["wedge"] + CTRL)
if B1:
    log(f"  사후기 조정성과 ← wedge   β={B1['coef']:+.5f} [{B1['ci95'][0]:+.5f},{B1['ci95'][1]:+.5f}] "
        f"{'유의' if B1['sig'] else 'ns'}  (n={B1['n']:,}, 회사={B1['n_firms']:,})")
    half = (B1["ci95"][1] - B1["ci95"][0]) / 2
    log(f"  CI 반폭 {half:.5f}  → {'좁다 (±0.05 안)' if half <= 0.05 else '넓다'}")
    B1["ci_halfwidth"] = round(half, 5)
    B1["informative_null"] = bool(not B1["sig"] and half <= 0.05)
# 대조: adj_pct 는 장래 성과를 예측해야 한다 (검정력 확인)
B1b = boot(P, "post_adj", ["adj_pct", "ln_n", "fp"])
if B1b:
    log(f"  (대조) 사후기 조정성과 ← adj_pct  β={B1b['coef']:+.5f} "
        f"[{B1b['ci95'][0]:+.5f},{B1b['ci95'][1]:+.5f}] {'유의' if B1b['sig'] else 'ns'}")
    log("  → adj 가 장래를 예측하는데 wedge 는 안 하면, wedge 는 실력이 아니다 (검정력 확보 증거)")
OUT["B1_wedge_predicts_future"] = B1
OUT["B1b_control_adj_predicts_future"] = B1b

# ══ B2 결합 검정 ═══════════════════════════════════════════════════════════
log("\n" + "=" * 96)
log("[B2] 평가자 보상의 결합 RI (레버 12) — 개별 ns 3개를 결합")
log("=" * 96)
YC = ["lp_any", "lp_amt", "recv_q"]
ind = {}
for y in YC:
    rr = boot(P, y, ["wedge"] + CTRL)
    ind[y] = rr
    if rr:
        log(f"  {y:<8} ← wedge  β={rr['coef']:+.5f} [{rr['ci95'][0]:+.5f},{rr['ci95'][1]:+.5f}] "
            f"{'유의' if rr['sig'] else 'ns'}  (n={rr['n']:,})")
    else:
        log(f"  {y:<8} 표본 부족")


def vec(df):
    out = []
    for y in YC:
        dd = df.dropna(subset=[y, "wedge"] + CTRL)
        if len(dd) < 100:
            out.append(np.nan)
            continue
        out.append(float(fit(dd, y, ["wedge"] + CTRL)[0]))
    return np.array(out)


act = vec(P)
PL = []
for i in range(NPLAC):
    Q = P.copy()
    Q["wedge"] = rng.permutation(Q["wedge"].to_numpy())
    PL.append(vec(Q))
    if (i + 1) % 100 == 0:
        log(f"    위약 {i + 1}/{NPLAC}")
PL = np.array(PL)
ok = ~np.isnan(PL).any(axis=1)
PLo = PL[ok]
mu, Sg = PLo.mean(axis=0), np.cov(PLo.T)
Si = np.linalg.pinv(Sg)
mah = lambda v: float((v - mu) @ Si @ (v - mu))  # noqa: E731
m_act = mah(act)
m_pl = np.array([mah(v) for v in PLo])
p_joint = float((m_pl >= m_act).mean())
nalign = int(np.nansum(act > 0))
log(f"\n  관측 벡터 " + " · ".join(f"{n}={v:+.4f}" for n, v in zip(YC, act)))
log(f"  예측방향(양수) 일치 {nalign}/{len(YC)}")
log(f"  Mahalanobis 관측 {m_act:.3f} · 위약 중위 {np.median(m_pl):.3f} · "
    f"위약 95% {np.percentile(m_pl, 95):.3f}")
log(f"  **결합 RI p = {p_joint:.4f}**  ({len(PLo)} 유효 위약)  {'통과' if p_joint < 0.05 else '실패'}")
OUT["B2_joint_RI"] = {"outcomes": YC, "coefs": {n: round(float(v), 6) for n, v in zip(YC, act)},
                      "n_aligned": nalign, "mahalanobis": round(m_act, 4),
                      "placebo_median": round(float(np.median(m_pl)), 4),
                      "placebo_p95": round(float(np.percentile(m_pl, 95)), 4),
                      "joint_RI_p": round(p_joint, 4), "n_placebo": int(len(PLo)),
                      "individual": ind, "pass": bool(p_joint < 0.05)}

# ══ B3 표본 확대 (별개 팔) ═════════════════════════════════════════════════
log("\n" + "=" * 96)
log("[B3] 표본 확대 MIN_DEALS 5→3 (별개 사양. 레버 미적층)")
log("=" * 96)
P3 = build(3)
log(f"  파트너 {len(P):,} → {len(P3):,}")
B3 = {}
for y in ["post_adj"] + YC:
    rr = boot(P3, y, ["wedge"] + CTRL)
    B3[y] = rr
    if rr:
        log(f"  {y:<8} ← wedge  β={rr['coef']:+.5f} [{rr['ci95'][0]:+.5f},{rr['ci95'][1]:+.5f}] "
            f"{'유의' if rr['sig'] else 'ns'}  (n={rr['n']:,})")
OUT["B3_expanded_min3"] = dict(B3, n_partners=int(len(P3)))

c1 = bool(B1 and B1.get("informative_null"))
c2 = bool(p_joint < 0.05)
revive = c1 and c2
status = "GO" if revive else "PARTIAL"
if revive:
    call = ("**① 재개 근거 확보: wedge 는 장래 조정성과를 예측하지 않는데(정보적 null) "
            "평가자는 wedge 를 보상한다(결합 RI 유의). 오염된 신호에 반응하는 평가자를 찾았다**")
elif c1 and not c2:
    call = (f"**wedge 는 장래 성과를 예측하지 않는다(정보적 null) — ① 의 전제는 성립. "
            f"그러나 평가자 보상의 결합 RI p={p_joint:.4f} 로 검정력 미달. "
            f"① 은 '전제 성립·귀결 미검출' 로 기록한다**")
elif not c1:
    call = (f"**wedge 가 장래 성과를 예측하거나 CI 가 넓다 → ① 의 해석 전제가 성립하지 않는다. "
            f"평가자가 wedge 를 보상해도 '속는 것'이라 부를 수 없다**")
else:
    call = "**두 게이트 모두 실패**"
verdict = (f"B1 wedge→장래성과 β={B1['coef'] if B1 else None} CI반폭={B1.get('ci_halfwidth') if B1 else None} "
           f"(대조 adj β={B1b['coef'] if B1b else None}) | B2 결합 RI p={p_joint:.4f} "
           f"방향일치 {nalign}/3 | B3 확대 파트너 {len(P3):,} — " + call)
emit("P001-25", "① 결정 검정 — wedge 가 장래성과 미예측 & 평가자 보상(결합 RI)", status, OUT,
     prediction="wedge→장래성과 ≈0 CI±0.05 · 결합 RI p<0.10 이나 0.05 미달 예상 · "
                "조성액이 이분보다 강함 · 확대로 CI 10~20% 축소",
     verdict=verdict, kill_met=False, n=int(len(P)),
     extra={"stage": 7, "feeds": "① 재개 가부", "slug": "wedge_decisive",
            "skill": "academics:power-rescue", "builds_on": "P001-23"})
log("done")
