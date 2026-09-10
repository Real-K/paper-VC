# -*- coding: utf-8 -*-
"""p001_28 — 리뷰어 선제 검정: 사후기 관측 선택 · 무조건 terrain · 레벨 단위 재확인

[왜] v4 의 핵심 계수(P001-25 B1 / P001-27 B: post_adj ← raw_pct | adj_pct, ≈ +0.10)는
**사후기 딜이 있는 파트너(2,178 / 2,686 = 81%)** 에서만 추정된다. 심사자가 반드시 물을 두 가지:
 (a) **관측 선택** — 사후기에 관측되는지 여부가 composition 과 상관되면 선택 편의.
     검정 = has_post ~ wedge + adj_pct + 통제 (LPM) ; 그 적합확률로 IPW 재추정.
 (b) **무조건 terrain** — P001-26 G4 에서 adj_pct 미통제 시 wedge 기울기가 −0.045 였다.
     조건부(+0.10)와 무조건(−0.045)이 갈리는 것을 CI 와 함께 확정해야 §6 서술이 정확해진다.
 (c) **레벨 단위 재확인** — percentile 이 아니라 level 로 같은 항등 결과가 나오는가.

[사양] LOO 셀 벤치마크(P001-27 B 와 동일 구성). 군집 = 투자사 부트 500.
[사전 예측] (결과 조회 전, 2026-09-08)
 S1 wedge → has_post : |β| < 0.05 (기저 0.81), CI 0 포함 가능성 높음.
 S2 IPW 재추정 계수가 비가중(+0.1027) 대비 **30% 미만 변화**.
 S3 무조건 terrain(level) → post_adj : 0 근처 또는 음(−), CI 가 양(+)을 배제하지 않을 수도.
 S4 level 사양 raw|adj : 양(+) 유의 (percentile 결과와 부호·유의성 일치).
[게이트] S2 변화 < 30% AND (S1 비유의 OR |β_S1| < 0.05) → 선택이 핵심 계수를 만들지 않는다.
 실패하면 §6 에 선택 한계를 명시하고 IPW 추정치를 병기한다 (rules/00).
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
BASE_LOO = 0.10272          # P001-27 'B LOO' 계수 — 비교 기준


def log(*a):
    print(*a, flush=True)


d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v2.parquet"))
d["dt"] = pd.to_datetime(d["dt"])
dn = d[d["country_code"].isin(NAEU)].copy()
dn["mcell"] = dn["year"] + "|" + dn["cat"] + "|" + dn["stage"]


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
    firm=("investor_uuid", lambda s: s.mode().iloc[0])).reset_index()
P = P[P["n"] >= 5].reset_index(drop=True)
P["raw_pct"] = P["raw"].rank(pct=True)
P["adj_pct"] = P["adj"].rank(pct=True)
P["wedge"] = P["raw_pct"] - P["adj_pct"]
P["terrain"] = P["raw"] - P["adj"]            # 레벨: 투자한 셀들의 LOO 기저 출구율
P["ln_n"] = np.log(P["n"])
po = dn[(dn["dt"] > CUT) & (dn["dt"] <= END)].copy()
po["r"] = resid_loo(po)
po = po[np.isfinite(po["r"])]
P = P.join(po.groupby("partner_uuid").agg(post_adj=("r", "mean"), post_n=("r", "size")), on="partner_uuid")
P["has_post"] = P["post_adj"].notna().astype(float)
log(f"[구성] 파트너 {len(P):,} · 사후기 관측 {int(P['has_post'].sum()):,} ({P['has_post'].mean():.1%})")


def fit(s, y, xc, wcol=None):
    X = np.column_stack([s[c].to_numpy(float) for c in xc] + [np.ones(len(s))])
    yy = s[y].to_numpy(float)
    if wcol is None:
        return np.linalg.lstsq(X, yy, rcond=None)[0]
    sw = np.sqrt(s[wcol].to_numpy(float))
    return np.linalg.lstsq(X * sw[:, None], yy * sw, rcond=None)[0]


def boot(df, y, xc, k=0, wcol=None, nb=NB):
    dd = df.dropna(subset=[y] + xc + ([wcol] if wcol else []))
    b0 = float(fit(dd, y, xc, wcol)[k])
    grp = {c: g.index.to_numpy() for c, g in dd.groupby("firm")}
    keys = list(grp)
    bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(keys), len(keys))
        s = dd.loc[np.concatenate([grp[keys[i]] for i in pick])]
        try:
            bs.append(float(fit(s, y, xc, wcol)[k]))
        except Exception:
            pass
    lo, hi = qci(np.array(bs))
    return {"coef": round(b0, 5), "ci95": [round(lo, 5), round(hi, 5)], "n": int(len(dd)),
            "n_firms": int(dd["firm"].nunique()), "sig": bool(lo > 0 or hi < 0)}


OUT = {}
log("\n" + "=" * 92)
log("[S1] 사후기 관측 선택 — has_post ← wedge (adj_pct·통제)")
log("=" * 92)
S1 = boot(P, "has_post", ["wedge", "adj_pct", "ln_n", "fp"])
OUT["S1_selection_on_wedge"] = S1
log(f"  β(wedge)={S1['coef']:+.5f} [{S1['ci95'][0]:+.5f},{S1['ci95'][1]:+.5f}] "
    f"{'유의' if S1['sig'] else 'ns'}  (기저 {P['has_post'].mean():.3f})")
S1b = boot(P, "has_post", ["adj_pct", "ln_n", "fp"])
OUT["S1b_selection_on_adj"] = S1b
log(f"  (참고) β(adj_pct)={S1b['coef']:+.5f} [{S1b['ci95'][0]:+.5f},{S1b['ci95'][1]:+.5f}]")

log("\n" + "=" * 92)
log("[S2] IPW 재추정 — post_adj ← raw_pct | adj_pct, 가중 1/P(관측)")
log("=" * 92)
bp = fit(P, "has_post", ["wedge", "adj_pct", "ln_n", "fp"])
Xp = np.column_stack([P[c].to_numpy(float) for c in ["wedge", "adj_pct", "ln_n", "fp"]] + [np.ones(len(P))])
P["phat"] = np.clip(Xp @ bp, 0.05, 1.0)
P["ipw"] = 1.0 / P["phat"]
UNW = boot(P, "post_adj", ["raw_pct", "adj_pct", "ln_n", "fp"])
IPW = boot(P, "post_adj", ["raw_pct", "adj_pct", "ln_n", "fp"], wcol="ipw")
chg = (IPW["coef"] - UNW["coef"]) / UNW["coef"] if UNW["coef"] else np.nan
OUT["S2_unweighted"] = UNW
OUT["S2_ipw"] = dict(IPW, pct_change_vs_unweighted=round(float(chg) * 100, 1),
                     phat_min=round(float(P["phat"].min()), 3), phat_max=round(float(P["phat"].max()), 3))
log(f"  비가중 β(raw|adj)={UNW['coef']:+.5f} [{UNW['ci95'][0]:+.5f},{UNW['ci95'][1]:+.5f}]  "
    f"(P001-27 B 기준 {BASE_LOO:+.5f})")
log(f"  IPW    β(raw|adj)={IPW['coef']:+.5f} [{IPW['ci95'][0]:+.5f},{IPW['ci95'][1]:+.5f}]  "
    f"변화 {chg * 100:+.1f}%  (p̂ 범위 {P['phat'].min():.3f}–{P['phat'].max():.3f})")

log("\n" + "=" * 92)
log("[S3] 무조건 terrain(level) → post_adj   vs   [S4] 레벨 항등: post_adj ← raw | adj (level)")
log("=" * 92)
S3 = boot(P, "post_adj", ["terrain", "ln_n", "fp"])
S4 = boot(P, "post_adj", ["raw", "adj", "ln_n", "fp"])
S4b = boot(P, "post_adj", ["terrain", "adj", "ln_n", "fp"])
OUT["S3_terrain_unconditional_level"] = S3
OUT["S4_raw_given_adj_level"] = S4
OUT["S4b_terrain_given_adj_level"] = S4b
log(f"  S3 무조건 terrain  β={S3['coef']:+.5f} [{S3['ci95'][0]:+.5f},{S3['ci95'][1]:+.5f}] {'유의' if S3['sig'] else 'ns'}")
log(f"  S4 raw | adj (lvl) β={S4['coef']:+.5f} [{S4['ci95'][0]:+.5f},{S4['ci95'][1]:+.5f}] {'유의' if S4['sig'] else 'ns'}")
log(f"  S4b terrain | adj  β={S4b['coef']:+.5f}  (항등 확인: S4 와 차 {abs(S4['coef'] - S4b['coef']):.2e})")

gate = (abs(chg) < 0.30) and ((not S1["sig"]) or abs(S1["coef"]) < 0.05)
status = "GO" if gate else "PARTIAL"
call = ("**선택이 핵심 계수를 만들지 않는다 — IPW 변화 "
        f"{chg * 100:+.1f}%, 관측선택 β(wedge) {S1['coef']:+.4f}**" if gate else
        f"**선택 게이트 실패 — IPW 변화 {chg * 100:+.1f}% 또는 관측선택 β {S1['coef']:+.4f} 유의. "
        "§6 에 선택 한계 명시 + IPW 병기 필요**")
verdict = (f"S1 has_post←wedge {S1['coef']:+.4f} [{S1['ci95'][0]:+.4f},{S1['ci95'][1]:+.4f}] | "
           f"S2 비가중 {UNW['coef']:+.4f} → IPW {IPW['coef']:+.4f} ({chg * 100:+.1f}%) | "
           f"S3 무조건 terrain {S3['coef']:+.4f} [{S3['ci95'][0]:+.4f},{S3['ci95'][1]:+.4f}] | "
           f"S4 level raw|adj {S4['coef']:+.4f} [{S4['ci95'][0]:+.4f},{S4['ci95'][1]:+.4f}] — " + call)
emit("P001-28", "리뷰어 선제 검정 — 사후기 관측 선택(IPW) · 무조건 terrain · 레벨 항등", status, OUT,
     prediction="S1 |β|<0.05 · S2 변화<30% · S3 0 근처/음 · S4 양 유의",
     verdict=verdict, kill_met=False, n=int(len(P)),
     extra={"stage": 7, "feeds": "P001 §6 서술·Table 9", "slug": "selection_terrain",
            "builds_on": "P001-27"})
log("done")
