# -*- coding: utf-8 -*-
"""p001_rescue_common — 내부리뷰 R2 power-rescue 배터리(P001-31~37) 공용 구성.

P001-30 의 표본·LOO 셀 벤치마크·성분 분해·연공·회사 변수를 그대로 옮겼다. 포팅 검산은 P001-31 이 한다:
R1t 총 terrain 점추정 +0.09772 가 재현되어야 하고(결정적 계산), 같은 seed 로 R1 을 먼저 돌리면 CI 도 같아야 한다.
새 구성: exit_dt 재계산(build_sample_v1 과 동일 논리) → exit3(36개월 출구) 고정지평 결과 · 회사 평균(CRE) ·
연공(기준일 가변). 산출물에 기업 식별자를 넣지 않는다.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("HARNESS_OUT", os.environ.get("P001_OUT", os.path.join(HERE, "out")))  # set P001_* / CRUNCHBASE_RAW to your local copies (licensed inputs; see DATA_ACCESS.md)
sys.path.insert(0, HERE)  # gates.py / emit_contract.py sit alongside in code/pipeline
from emit_contract import emit, qci, sha16  # noqa: E402
from gates import CTX  # noqa: E402

COMMON_SHA = sha16(os.path.abspath(__file__))
NB = 400
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR",
      "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}
NAEU = EU | {"USA", "CAN"}
CUT = pd.Timestamp("2017-10-31")
END = pd.Timestamp("2023-10-31")
END_FON = pd.Timestamp("2020-10-31")
TC = ["t_v", "t_s", "t_cs"]
TEN = ["tenure", "tenure2", "fyb1", "fyb2", "fyb3", "fyb4"]


def log(*a):
    print(*a, flush=True)


def is_late(s):
    s = str(s)
    return (s.startswith("series_") and s not in ("series_a", "series_unknown")) or s == "private_equity"


def load_deals(with_exit_dt=True):
    d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v1.parquet"))
    d["dt"] = pd.to_datetime(d["dt"])
    dn = d[d["country_code"].isin(NAEU)].copy()
    dn["y"] = dn["year"].astype(str)
    dn["ys"] = dn["y"] + "|" + dn["stage"]
    dn["yss"] = dn["y"] + "|" + dn["cat"] + "|" + dn["stage"]
    dn["late"] = dn["stage"].map(is_late).astype(float)
    if with_exit_dt:
        acq = CTX.acq.dropna(subset=["acquiree_uuid", "acquired_on"]).copy()
        acq["adt"] = pd.to_datetime(acq["acquired_on"], errors="coerce")
        ip = CTX.ipos.dropna(subset=["org_uuid", "went_public_on"]).copy()
        ip["idt"] = pd.to_datetime(ip["went_public_on"], errors="coerce")
        first_ipo = ip.groupby("org_uuid")["idt"].min()
        first_acq = acq.groupby("acquiree_uuid")["adt"].min()
        exit_any = pd.concat([first_acq, first_ipo], axis=1).min(axis=1)
        dn["exit_dt"] = dn["org_uuid"].map(exit_any)
        agree = float((dn["exit_dt"].notna().astype(float) == dn["exit_ever"]).mean())
        if agree < 0.999:
            raise RuntimeError(f"exit_dt 재계산이 exit_ever 와 불일치: 일치율 {agree:.4f}")
        days = (dn["exit_dt"] - dn["dt"]).dt.days
        dn["exit3"] = (days <= 365 * 3).fillna(False).astype(float)
        log(f"[공용] NAEU 딜 {len(dn):,} · exit_dt 일치율 {agree:.4f} · exit3 기저 {dn['exit3'].mean():.4f} · "
            f"exit6 {dn['exit6'].mean():.4f} · exit_ever {dn['exit_ever'].mean():.4f} · fon {dn['fon'].mean():.4f}")
    return dn


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
    """LOO 셀 벤치마크와 성분: b_yss = b_year + (b_ys - b_year) + (b_yss - b_ys)."""
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


def partner_pre(dn, ycol="exit_ever", min_n=5, cut=CUT):
    """사전기 파트너 패널 (P001-30 과 동일). 반환: (P, h) — h 는 잔차가 유한한 사전기 딜."""
    h = build(dn[dn["dt"] <= cut], ycol)
    h = h[np.isfinite(h["r"])]
    P = h.groupby("partner_uuid").agg(
        raw=(ycol, "mean"), adj=("r", "mean"), n=(ycol, "size"), fp=("fp", "first"),
        t_v=("t_v", "mean"), t_s=("t_s", "mean"), t_cs=("t_cs", "mean"),
        raw_lpo=(ycol, "mean"), adj_lpo=("r_lpo", "mean"), late_sh=("late", "mean"),
        firm=("investor_uuid", lambda s: s.mode().iloc[0])).reset_index()
    P = P[P["n"] >= min_n].reset_index(drop=True)
    P["terrain"] = P["raw"] - P["adj"]
    P["ln_n"] = np.log(P["n"])
    return P, h


def add_post(P, dn, ycol="exit_ever", end=END, cut=CUT, suffix=""):
    po = build(dn[(dn["dt"] > cut) & (dn["dt"] <= end)], ycol)
    po = po[np.isfinite(po["r"])]
    agg = po.groupby("partner_uuid").agg(**{f"post_adj{suffix}": ("r", "mean"),
                                            f"post_n{suffix}": ("r", "size"),
                                            f"post_adj_lpo{suffix}": ("r_lpo", "mean")})
    P = P.join(agg, on="partner_uuid")
    P[f"has_post{suffix}"] = P[f"post_adj{suffix}"].notna().astype(float)
    return P


def first_deal_dates():
    pt = CTX.partners.dropna(subset=["funding_round_uuid", "partner_uuid"])
    r = CTX.rounds.dropna(subset=["announced_on"])[["uuid", "announced_on"]].copy()
    r["rdt"] = pd.to_datetime(r["announced_on"], errors="coerce")
    A = pt.merge(r, left_on="funding_round_uuid", right_on="uuid").dropna(subset=["rdt"])
    return A.groupby("partner_uuid")["rdt"].min()


def add_tenure(P, first=None, ref=CUT):
    first = first_deal_dates() if first is None else first
    P["first_dt"] = P["partner_uuid"].map(first)
    P["tenure"] = (ref - P["first_dt"]).dt.days / 365.25
    P["tenure2"] = P["tenure"] ** 2
    P["fy"] = P["first_dt"].dt.year.clip(lower=2005)
    P["fy_bin"] = pd.cut(P["fy"], [0, 2008, 2011, 2013, 2015, 2100], labels=False)
    for b in range(1, 5):
        P[f"fyb{b}"] = (P["fy_bin"] == b).astype(float)
    return P


def add_firm(P, h):
    """홈 회사 사전기 LOO 잔차 평균(파트너 p 자신 제외) + ln 회사 사전기 딜수 (P001-30 R3)."""
    h2 = h[h["partner_uuid"].isin(P["partner_uuid"])]
    fs = h2.groupby("investor_uuid")["r"].agg(["sum", "size"])
    ps = h2.groupby(["investor_uuid", "partner_uuid"])["r"].agg(["sum", "size"])
    fam, fn = [], []
    for p_, f_ in zip(P["partner_uuid"], P["firm"]):
        S, N = fs.loc[f_, "sum"], fs.loc[f_, "size"]
        if (f_, p_) in ps.index:
            S -= ps.loc[(f_, p_), "sum"]
            N -= ps.loc[(f_, p_), "size"]
        fam.append(S / N if N > 0 else np.nan)
        fn.append(N)
    P["firm_adj_mp"] = fam
    P["ln_firm_n"] = np.log1p(fn)
    return P


def add_firm_means(P, cols):
    """회사 평균(Mundlak/CRE). fm_ = 표본 내 전 파트너 평균(사후기 없는 파트너 포함), fmp_ = 자신 제외 평균."""
    g = P.groupby("firm")
    k = g["firm"].transform("size")
    P["fm_k"] = k
    for c in cols:
        s = g[c].transform("sum")
        P[f"fm_{c}"] = s / k
        P[f"fmp_{c}"] = np.where(k > 1, (s - P[c]) / np.maximum(k - 1, 1), np.nan)
        P[f"dev_{c}"] = P[c] - P[f"fm_{c}"]
    return P


def fit(s, y, xc):
    X = np.column_stack([s[c].to_numpy(float) for c in xc] + [np.ones(len(s))])
    return np.linalg.lstsq(X, s[y].to_numpy(float), rcond=None)[0]


def boot(df, y, xc, keys, rng, nb=NB, demean=None, cluster="firm", min_n=150, return_draws=False):
    """군집 부트스트랩. demean=열이름 이면 그 단위 내 demean(≥2 관측 단위만). se_boot·mde80 을 함께 낸다."""
    dd = df.dropna(subset=[y] + xc).copy()
    if demean is not None:
        cnt = dd.groupby(demean)[demean].transform("size")
        dd = dd[cnt >= 2].copy()
        for c in [y] + xc:
            dd[c] = dd[c] - dd.groupby(demean)[c].transform("mean")
    if len(dd) < min_n:
        return None
    b = fit(dd, y, xc)
    grp = {c: g.index.to_numpy() for c, g in dd.groupby(cluster)}
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
    out = {"n": int(len(dd)), "n_firms": int(dd[cluster].nunique())}
    for k in keys:
        i = xc.index(k)
        lo, hi = qci(bs[:, i])
        se = float(np.std(bs[:, i], ddof=1))
        out[k] = {"coef": round(float(b[i]), 5), "ci95": [round(lo, 5), round(hi, 5)],
                  "sig": bool(lo > 0 or hi < 0), "se_boot": round(se, 5), "mde80": round(2.8 * se, 4)}
    if return_draws:
        out["_draws"] = bs
        out["_b"] = b
        out["_xc"] = list(xc)
    return out


def strip_draws(res):
    if not res:
        return res
    return {k: v for k, v in res.items() if not k.startswith("_")}


def show(tag, res, keys):
    if not res:
        log(f"  {tag}: 표본 부족")
        return
    parts = [f"{k}={res[k]['coef']:+.4f} [{res[k]['ci95'][0]:+.3f},{res[k]['ci95'][1]:+.3f}]{'*' if res[k]['sig'] else ''}"
             for k in keys if k in res]
    log(f"  {tag:<30} n={res['n']:,}/{res['n_firms']:,} | " + " · ".join(parts))


def fmt(res, k):
    if not res or k not in res:
        return "NA"
    r = res[k]
    return f"{r['coef']:+.3f} [{r['ci95'][0]:+.3f},{r['ci95'][1]:+.3f}]{'*' if r['sig'] else ''}"
