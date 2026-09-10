# -*- coding: utf-8 -*-
"""p001_26 — wedge 의 예측력이 성별로 무엇을 함의하는가 (프레임 확정 **전** 필수 검정)

[왜 지금] `P001-25` 가 두 사실을 확립했다.
 (i) 여성 파트너는 초기단계로 기울어 있다(P001 §3: 셀 내 +3.84pp) → **wedge 가 음수**일 것
 (ii) **wedge 가 장래 조정성과를 양으로 예측한다** (+0.0973 [+0.0389,+0.1604])
두 사실을 이으면 *"여성 파트너의 장래 조정성과가 더 낮게 예측된다"* 가 따라온다.
**이것을 검정하지 않고 원고 프레임을 쓰면 심사에서 터진다.** 그리고 사실이라면 논문의
규범적 서술이 완전히 달라진다(재순위가 "교정"이 아니라 "정보 폐기"가 되는 정도가 성별로 다르다).

[검정할 것]
 G1 fp → wedge.  예측: **음수** (여성 파트너의 terrain 이 불리하다)
 G2 fp → 사후기 조정성과 (무조건).  이것이 이 검정의 핵심 결과다.
 G3 fp → 사후기 조정성과 (wedge 통제).  G2 와의 차이가 "terrain 경로"의 크기다.
 G4 wedge × fp 상호작용 — **wedge 의 예측력이 성별로 다른가.**
    다르지 않으면 wedge 는 성별 중립적 신호이고, 재순위의 해석은 유지된다.
    여성에게서 약하면 "같은 terrain 을 골라도 여성은 덜 보상받는다"가 되고 이야기가 달라진다.
 G5 (대조) fp → 사전기 조정성과(adj) — 알려진 사실의 재확인으로 검정력 확인

[사전 예측] (결과 조회 전, 2026-09-08)
 H1 G1 음수 유의 (여성 wedge 낮음).
 H2 **G2 는 0 근처이거나 약한 음수** — 여성 파트너의 사전기 adj 가 남성과 다르지 않다는
    P001 의 주 결과(§4)가 사후기에도 유지된다면 G2 는 0 이어야 한다. G2 가 유의한 음수면
    **P001 의 주 결과와 긴장**하므로 반드시 보고해야 한다.
 H3 G4 상호작용은 미검출 (검정력 부족).
[게이트] G2 가 유의 음수 → 원고 프레임을 그에 맞춰 다시 쓴다(회피하지 않는다, rules/00).
 G2 가 0 근처 → 재순위 해석 유지 + wedge 의 예측력은 성별 중립 신호로 서술.
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

hist = dn[dn["dt"] <= CUT].copy()
hist["resid"] = hist["exit_ever"] - hist.groupby("mcell")["exit_ever"].transform("mean")
P = hist.groupby("partner_uuid").agg(
    raw=("exit_ever", "mean"), adj=("resid", "mean"), n=("exit_ever", "size"),
    fp=("fp", "first"), early_sh=("early", "mean"), ncat=("cat", "nunique"),
    firm=("investor_uuid", lambda s: s.mode().iloc[0])).reset_index()
P = P[P["n"] >= 5].reset_index(drop=True)
P["raw_pct"] = P["raw"].rank(pct=True)
P["adj_pct"] = P["adj"].rank(pct=True)
P["wedge"] = P["raw_pct"] - P["adj_pct"]
P["ln_n"] = np.log(P["n"])

post = dn[(dn["dt"] > CUT) & (dn["dt"] <= END)].copy()
post["presid"] = post["exit_ever"] - post.groupby("mcell")["exit_ever"].transform("mean")
pa = post.groupby("partner_uuid").agg(post_adj=("presid", "mean"), post_n=("presid", "size"))
P = P.join(pa, on="partner_uuid")
P["wedge_c"] = P["wedge"] - P["wedge"].mean()
P["fp_x_wedge"] = P["fp"] * P["wedge_c"]
log(f"[구성] 파트너 {len(P):,} (여성 {int(P['fp'].sum())}, {P['fp'].mean():.1%}) · "
    f"사후기 관측 {int(P['post_adj'].notna().sum()):,}")
log(f"  wedge 평균: 여성 {P.loc[P['fp'] == 1, 'wedge'].mean():+.4f} vs "
    f"남성 {P.loc[P['fp'] == 0, 'wedge'].mean():+.4f}")


def fit(s, ycol, xc):
    X = np.column_stack([s[c].to_numpy(float) for c in xc] + [np.ones(len(s))])
    return np.linalg.lstsq(X, s[ycol].to_numpy(float), rcond=None)[0]


def boot(df, ycol, xc, k=0, nb=NB):
    dd = df.dropna(subset=[ycol] + xc)
    if len(dd) < 200:
        return None
    b0 = float(fit(dd, ycol, xc)[k])
    grp = {c: g.index.to_numpy() for c, g in dd.groupby("firm")}
    keys = list(grp)
    bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(keys), len(keys))
        s = dd.loc[np.concatenate([grp[keys[i]] for i in pick])]
        try:
            bs.append(float(fit(s, ycol, xc)[k]))
        except Exception:
            pass
    lo, hi = qci(np.array(bs))
    return {"coef": round(b0, 5), "ci95": [round(lo, 5), round(hi, 5)],
            "n": int(len(dd)), "n_firms": int(dd["firm"].nunique()),
            "sig": bool(lo > 0 or hi < 0)}


OUT = {}
log("\n" + "=" * 96)
log("[G1] fp → wedge   (여성 파트너의 terrain 이 불리한가)")
log("=" * 96)
G1 = boot(P, "wedge", ["fp", "ln_n"])
OUT["G1_fp_to_wedge"] = G1
if G1:
    log(f"  β(fp)={G1['coef']:+.5f} [{G1['ci95'][0]:+.5f},{G1['ci95'][1]:+.5f}] "
        f"{'유의' if G1['sig'] else 'ns'}  (n={G1['n']:,})")

log("\n" + "=" * 96)
log("[G2] fp → **사후기 조정성과** (무조건). ★ 이 검정의 핵심 ★")
log("=" * 96)
G2 = boot(P, "post_adj", ["fp", "ln_n"])
OUT["G2_fp_to_future_adj"] = G2
if G2:
    log(f"  β(fp)={G2['coef']:+.5f} [{G2['ci95'][0]:+.5f},{G2['ci95'][1]:+.5f}] "
        f"{'**유의**' if G2['sig'] else 'ns'}  (n={G2['n']:,}, 회사={G2['n_firms']:,})")
    half = (G2["ci95"][1] - G2["ci95"][0]) / 2
    OUT["G2_fp_to_future_adj"]["ci_halfwidth"] = round(half, 5)
    log(f"  CI 반폭 {half:.5f}")

log("\n" + "=" * 96)
log("[G3] fp → 사후기 조정성과 (wedge 통제) — G2 와의 차이가 terrain 경로")
log("=" * 96)
G3 = boot(P, "post_adj", ["fp", "wedge", "ln_n"])
OUT["G3_fp_controlling_wedge"] = G3
if G3:
    log(f"  β(fp)={G3['coef']:+.5f} [{G3['ci95'][0]:+.5f},{G3['ci95'][1]:+.5f}] "
        f"{'유의' if G3['sig'] else 'ns'}")
    if G2:
        log(f"  → G2 {G2['coef']:+.5f} vs G3 {G3['coef']:+.5f}  "
            f"terrain 경로 = {G2['coef'] - G3['coef']:+.5f}")
        OUT["terrain_path"] = round(G2["coef"] - G3["coef"], 5)

log("\n" + "=" * 96)
log("[G4] wedge × fp — **wedge 의 예측력이 성별로 다른가**")
log("=" * 96)
G4 = boot(P, "post_adj", ["fp_x_wedge", "fp", "wedge_c", "ln_n"])
OUT["G4_interaction"] = G4
if G4:
    log(f"  β(wedge×fp)={G4['coef']:+.5f} [{G4['ci95'][0]:+.5f},{G4['ci95'][1]:+.5f}] "
        f"{'유의' if G4['sig'] else 'ns'}")
    bm = fit(P.dropna(subset=["post_adj", "fp_x_wedge", "fp", "wedge_c", "ln_n"]),
             "post_adj", ["fp_x_wedge", "fp", "wedge_c", "ln_n"])
    log(f"  → 남성 기울기 {float(bm[2]):+.5f} · 여성 기울기 "
        f"{float(bm[2] + bm[0]):+.5f}")
    OUT["G4_slopes"] = {"male": round(float(bm[2]), 5), "female": round(float(bm[2] + bm[0]), 5)}

log("\n" + "=" * 96)
log("[G5] (대조) fp → 사전기 조정성과 adj — 알려진 결과 재확인 = 검정력 확인")
log("=" * 96)
G5 = boot(P, "adj", ["fp", "ln_n"])
OUT["G5_control_fp_to_pre_adj"] = G5
if G5:
    log(f"  β(fp)={G5['coef']:+.5f} [{G5['ci95'][0]:+.5f},{G5['ci95'][1]:+.5f}] "
        f"{'유의' if G5['sig'] else 'ns'}")

g2sig = bool(G2 and G2["sig"])
g2neg = bool(G2 and G2["coef"] < 0)
status = "PARTIAL" if g2sig else "GO"
if g2sig and g2neg:
    call = ("**G2 가 유의 음수 — 여성 파트너의 사후기 조정성과가 낮다. P001 §4 의 주 결과(조정 후 "
            "격차 미검출)와 긴장한다. 원고 프레임을 이에 맞춰 다시 써야 하며 회피할 수 없다(rules/00)**")
elif g2sig:
    call = "**G2 가 유의 양수 — 여성 파트너의 사후기 조정성과가 높다. 예상 밖이며 그대로 보고한다**"
else:
    call = ("**G2 미검출 — 여성 파트너의 사후기 조정성과는 남성과 구분되지 않는다. "
            "재순위 해석 유지 가능. wedge 의 예측력은 성별 중립 신호로 서술한다**")
verdict = ("  |  ".join(f"{k}: β={v['coef']:+.5f} [{v['ci95'][0]:+.4f},{v['ci95'][1]:+.4f}] "
                        f"{'유의' if v['sig'] else 'ns'}"
                        for k, v in OUT.items() if isinstance(v, dict) and "coef" in v)
           + " — " + call)
emit("P001-26", "wedge 예측력의 성별 함의 — 원고 프레임 확정 전 필수 검정", status, OUT,
     prediction="G1 음수 유의 · G2 0 근처(유의 음수면 §4 와 긴장) · G4 미검출",
     verdict=verdict, kill_met=False, n=int(len(P)),
     extra={"stage": 7, "feeds": "P001 원고 프레임 확정", "slug": "wedge_gender",
            "builds_on": "P001-25"})
log("done")
