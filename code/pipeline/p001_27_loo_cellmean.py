# -*- coding: utf-8 -*-
"""p001_27 — 셀평균 잡음 검정: β_raw|adj 가 기계적 인공물인가 (D050)

[왜 필수인가] 새 프레임의 근거 계수가 `P001-25` B1 의 **+0.0973** (`adj_pct` 통제 하 `raw_pct`
계수, 결과 = 사후기 조정성과)이다. 그런데 `adj = exit_ever − 셀평균` 이고 **셀평균에 자기 딜이
포함된다.** 기계적 편의의 방향이 명확하다:

 작은 셀의 파트너는 자기 딜이 셀평균을 밀어올려 → `adj` 가 0 으로 수축 →
 `terrain = raw − adj` 가 자기 `raw` 쪽으로 당겨진다 → **terrain 과 raw 의 상관이 인공적으로 상승**
 → raw 가 사후기 성과를 예측하는 지속성 때문에 **β_raw|adj 가 인공적으로 양수가 된다.**

[처방] **leave-one-out 셀평균**: 딜 i 의 잔차를 `y_i − (셀합 − y_i)/(n_c − 1)` 로 만든다.
자기 딜이 벤치마크에서 빠지므로 위 경로가 차단된다. 사전기·사후기 **양쪽 모두** LOO 로 만든다.
보조로 **셀 관측수 하한**(10·30)을 걸어 잡음 자체를 줄인 사양도 본다.

[사양]  y = 사후기 조정성과,  x = raw_pct,  통제 = adj_pct + ln(딜수) + fp,  군집 = 투자사
  A naive (P001-25 재현. 기대 +0.0973)
  B LOO
  C LOO + 셀 관측수 ≥ 10
  D LOO + 셀 관측수 ≥ 30
[함께 재확인] D048 의 성별 결과가 LOO 에서도 유지되는가 (fp→wedge 음수 · fp→사후기 성과 ns).

[사전 예측] (결과 조회 전, 2026-09-08)
 L1 naive 재현 성공 (+0.09~+0.10).
 L2 **LOO 에서 계수가 줄어든다.** 기계적 성분이 있으므로. 다만 **부호가 유지되고 CI 가 0 을
    배제하면 프레임은 산다.** 절반 이상 줄어들면 "기계적 성분이 지배"로 판정한다.
 L3 셀 하한을 올리면 LOO 계수가 안정된다 (잡음 감소).
 L4 성별 결과(D048)는 LOO 에서도 유지된다 — fp 는 셀 구성으로 정의되지 않으므로.
[게이트] **LOO 사양에서 CI 가 0 을 배제하고 naive 대비 50% 이상 남아야** 프레임의 근거로 쓴다.
 미달이면 "조정이 정보를 걷어낸다"는 주장을 철회하고 그렇게 기록한다 (rules/00).
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["HARNESS_OUT"] = os.environ.get("P001_OUT", os.path.join(HERE, "out"))  # set P001_* / CRUNCHBASE_RAW to your local copies (licensed inputs; see DATA_ACCESS.md)
sys.path.insert(0, HERE)  # gates.py / emit_contract.py sit alongside in code/pipeline
from emit_contract import emit, qci  # noqa: E402

rng = np.random.default_rng(20260908)
NB = 500
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR",
      "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}
NAEU = EU | {"USA", "CAN"}
CUT = pd.Timestamp("2017-10-31")
END = pd.Timestamp("2023-10-31")


def log(*a):
    print(*a, flush=True)


d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v2.parquet"))
d["dt"] = pd.to_datetime(d["dt"])
dn = d[d["country_code"].isin(NAEU)].copy()
dn["mcell"] = dn["year"] + "|" + dn["cat"] + "|" + dn["stage"]


def resid(df, loo, minc):
    """셀 잔차. loo=True 면 자기 딜을 벤치마크에서 제외한다."""
    g = df.groupby("mcell")["exit_ever"]
    s, n = g.transform("sum"), g.transform("size")
    if loo:
        bm = np.where(n > 1, (s - df["exit_ever"]) / np.maximum(n - 1, 1), np.nan)
    else:
        bm = s / n
    out = df["exit_ever"].to_numpy(float) - np.asarray(bm, float)
    keep = np.asarray(n, float) >= minc
    out = np.where(keep, out, np.nan)
    return out, np.asarray(bm, float), keep


def build(loo, minc):
    h = dn[dn["dt"] <= CUT].copy()
    h["r"], h["bm"], k = resid(h, loo, minc)
    h = h[k & np.isfinite(h["r"])]
    P = h.groupby("partner_uuid").agg(
        raw=("exit_ever", "mean"), adj=("r", "mean"), n=("exit_ever", "size"),
        fp=("fp", "first"),
        firm=("investor_uuid", lambda s: s.mode().iloc[0])).reset_index()
    P = P[P["n"] >= 5].reset_index(drop=True)
    P["raw_pct"] = P["raw"].rank(pct=True)
    P["adj_pct"] = P["adj"].rank(pct=True)
    P["wedge"] = P["raw_pct"] - P["adj_pct"]
    P["ln_n"] = np.log(P["n"])
    p = dn[(dn["dt"] > CUT) & (dn["dt"] <= END)].copy()
    p["r"], _, k2 = resid(p, loo, minc)
    p = p[k2 & np.isfinite(p["r"])]
    pa = p.groupby("partner_uuid").agg(post_adj=("r", "mean"), post_n=("r", "size"))
    return P.join(pa, on="partner_uuid")


def fit(s, y, xc):
    X = np.column_stack([s[c].to_numpy(float) for c in xc] + [np.ones(len(s))])
    return np.linalg.lstsq(X, s[y].to_numpy(float), rcond=None)[0]


def boot(df, y, xc, k=0, nb=NB):
    dd = df.dropna(subset=[y] + xc)
    if len(dd) < 200:
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
    return {"coef": round(b0, 5), "ci95": [round(lo, 5), round(hi, 5)],
            "n": int(len(dd)), "n_firms": int(dd["firm"].nunique()),
            "sig": bool(lo > 0 or hi < 0)}


XC = ["raw_pct", "adj_pct", "ln_n", "fp"]
SPECS = [("A naive (P001-25 재현)", False, 1), ("B LOO", True, 1),
         ("C LOO + 셀≥10", True, 10), ("D LOO + 셀≥30", True, 30)]
OUT = {}
log("=" * 100)
log("[핵심] 사후기 조정성과 ← raw_pct (adj_pct 통제).  기계적 성분이 얼마나 남는가")
log("=" * 100)
base = None
for nm, loo, mc in SPECS:
    P = build(loo, mc)
    rr = boot(P, "post_adj", XC)
    if rr is None:
        log(f"  {nm:<24} 표본 부족")
        continue
    if base is None:
        base = rr["coef"]
    share = rr["coef"] / base if base else np.nan
    OUT[nm] = dict(rr, n_partners=int(len(P)), share_of_naive=round(float(share), 3))
    log(f"  {nm:<24} β(raw|adj)={rr['coef']:+.5f} [{rr['ci95'][0]:+.5f},{rr['ci95'][1]:+.5f}] "
        f"{'유의' if rr['sig'] else 'ns'}  naive 대비 {share * 100:>5.1f}%  "
        f"(파트너 {len(P):,}, 회사 {rr['n_firms']:,})")

log("\n" + "=" * 100)
log("[성별 결과 재확인 — D048 이 LOO 에서도 유지되는가]")
log("=" * 100)
GEN = {}
for nm, loo, mc in (("naive", False, 1), ("LOO", True, 1), ("LOO+셀≥10", True, 10)):
    P = build(loo, mc)
    g1 = boot(P, "wedge", ["fp", "ln_n"])
    g2 = boot(P, "post_adj", ["fp", "ln_n"])
    GEN[nm] = {"fp_to_wedge": g1, "fp_to_post_adj": g2}
    if g1 and g2:
        log(f"  {nm:<10} fp→wedge {g1['coef']:+.5f} [{g1['ci95'][0]:+.4f},{g1['ci95'][1]:+.4f}] "
            f"{'유의' if g1['sig'] else 'ns'}  |  fp→사후성과 {g2['coef']:+.5f} "
            f"[{g2['ci95'][0]:+.4f},{g2['ci95'][1]:+.4f}] {'유의' if g2['sig'] else 'ns'}")
OUT["gender_recheck"] = GEN

loo = OUT.get("B LOO")
c10 = OUT.get("C LOO + 셀≥10")
gate = bool(loo and loo["sig"] and loo["share_of_naive"] >= 0.5)
status = "GO" if gate else "KILL"
if gate:
    call = (f"**LOO 에서 계수가 {loo['coef']:+.5f} (naive 의 {loo['share_of_naive'] * 100:.0f}%) 로 "
            f"유지되고 CI 가 0 을 배제한다. 기계적 성분이 지배하지 않는다 — "
            f"'조정이 정보를 걷어낸다'를 프레임의 근거로 쓸 수 있다**")
else:
    why = ("CI 가 0 을 포함" if (loo and not loo["sig"])
           else f"naive 의 {loo['share_of_naive'] * 100:.0f}% 만 남음" if loo else "표본 부족")
    call = (f"**LOO 에서 게이트 실패 ({why}). 셀평균 잡음이 기계적으로 만든 성분이었다. "
            f"'조정이 정보를 걷어낸다'는 주장을 철회하고 그대로 기록한다**")
verdict = ("  |  ".join(f"{k}: β={v['coef']:+.5f} [{v['ci95'][0]:+.4f},{v['ci95'][1]:+.4f}] "
                        f"naive의 {v['share_of_naive'] * 100:.0f}%"
                        for k, v in OUT.items() if isinstance(v, dict) and "coef" in v)
           + " — " + call)
emit("P001-27", "셀평균 잡음 검정 — leave-one-out 벤치마크 하에서 β_raw|adj 가 남는가",
     status, OUT,
     prediction="naive 재현 · LOO 에서 계수 감소하나 부호·유의성 유지 · 셀 하한 올리면 안정 · "
                "성별 결과는 LOO 에서도 유지",
     verdict=verdict, kill_met=(not gate), n=int(len(build(True, 1))),
     extra={"stage": 7, "feeds": "P001 원고 프레임의 근거 계수 타당성", "slug": "loo_cellmean",
            "resolves": "D050"})
log("done")
