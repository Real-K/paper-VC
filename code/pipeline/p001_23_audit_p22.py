# -*- coding: utf-8 -*-
"""p001_23 — P001-22 사양 전수감사 + LP 측 검정 (power-rescue, PI 지시 2026-09-08)

[왜] `P001-22` 가 사전 등록 규칙 P1(β_raw|adj > 0) 실패로 **주장 ⑤ 의 귀결과 "비가시성"
재프레임을 철회**했다. PI 지시: 되살리기 자체가 목적이 아니라, **그 판정을 낸 사양에 결함이
없었는지 전수검사**한다. 가드레일: 위음성 방지이지 유의성 탐색이 아니다. 결과는 유리·불리
무관하게 전부 기록한다. **원 수치 재현이 선행 조건이다** (재현 실패 시 감사는 무효).

────────────────────────────────────────────────────────────────────────────
의심 1 — 경마 사양의 재모수화 (결정적)
────────────────────────────────────────────────────────────────────────────
`adj = raw − (셀평균의 평균)` 이므로 raw 와 adj 의 차이는 **파트너가 투자한 셀들의 기저
출구율(terrain)** 이다. 두 랭크를 **서로 통제**해 같은 회귀에 넣으면 `β_raw|adj` 는
"원시 신호의 효과"가 아니라 **terrain 의 효과**를 잰다.
검정: (a) ρ(raw_pct, adj_pct) 와 VIF (b) `y ~ adj_pct + wedge`(wedge = raw_pct − adj_pct)로
재모수화해 **β_wedge ≡ β_raw|adj 항등**을 수치로 확인. 항등이 성립하면 P1 은 공선성 하에서
**다른 대상을 검정**한 것이다.

────────────────────────────────────────────────────────────────────────────
의심 2 — 결과변수가 평가자 신념을 식별하지 못한다
────────────────────────────────────────────────────────────────────────────
move·spin 은 **평가자 수요 × 파트너 본인의 선택**의 합작이고, terrain 은 파트너 쪽에 직접
작용한다(초기단계 특화자는 소형 시드 펀드로 독립 가능, 후기단계는 큰 펀드 필요).
따라서 β_raw < 0 은 "평가자가 안 속는다"가 아니라 **독립 가능성**일 수 있다.
원장이 이미 "terrain 효과 — 초기단계 특화자가 스핀아웃을 더 함"이라 적었다.
검정: 원시·조정을 **각각 단독**으로 넣은 사양 + **표본외 예측력 비교**(5겹 CV AUC).
"평가자가 어느 신호를 쓰는가"는 부분계수 문제가 아니라 **예측력 비교** 문제다.

────────────────────────────────────────────────────────────────────────────
의심 3 — P001-22 가 불가능하다고 적은 것이 실제로는 가능하다 (새 레버)
────────────────────────────────────────────────────────────────────────────
P001-22 docstring: "**LP 자본 흐름은 CB 에 없지만** 파트너의 외부 이동은 관측 가능하고…"
→ **틀렸다. `funds` 테이블이 있다** (운용사 28,186 펀드, entity_uuid + raised_amount_usd,
investors.uuid 매칭률 100% — K-01 에서 확인). 스핀아웃한 파트너의 **신생 회사가 실제로
펀드를 조성했는지·얼마나** 가 관측된다. LP 는 **내부 배분을 관측할 수 없는 평가자**이므로
이것이 "오염된 신호에 속는 평가자"의 직접 검정이다.
설계: **스핀아웃한 파트너로 한정**(파트너 공급 측을 조건화) → 신생 회사의
(i) 펀드 조성 여부 (ii) log 조성액 이 raw 를 따르는가 adj 를 따르는가.
보조: **이동한 파트너로 한정** → 수용 회사의 품질(사전 딜수·사전 출구율)이 어느 랭크를 따르는가.

[사전 예측] (결과 조회 전, 2026-09-08)
 A1 재현 성공 (spin: β_raw ≈ −0.158, β_adj ≈ +0.190).
 A2 ρ(raw_pct, adj_pct) ≥ 0.80, VIF ≥ 3 → 경마가 공선성 하에 있다.
 A3 **β_wedge ≡ β_raw|adj 항등 성립** (수치 일치). P1 은 terrain 계수를 검정했다.
 A4 단독 사양에서 raw_pct 와 adj_pct **둘 다 양수**일 것 (둘 다 실력을 담고 있으므로).
    그렇다면 "외부가 원시를 안 쓴다"는 결론은 성립하지 않는다.
 A5 표본외 예측력은 **거의 같을 것**(ρ 0.86) → "어느 신호를 쓰는지 구분 불가"가 정직한 결론.
 A6 LP 측 검정은 **표본 부족으로 무정보일 가능성이 높다**(스핀아웃 파트너 수가 적다).
[판정 규칙] A3 성립 → **P001-22 의 P1 은 유효한 검정이 아니었다**고 기록하고, 철회 판정을
 "검정 무효"로 재분류한다. 단 **그것이 ① 을 되살리지는 않는다** — 되살리려면 A4/A6 에서
 **원시 신호가 평가자 결과를 예측한다는 양의 증거**가 나와야 한다. 없으면 그렇게 쓴다.
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
MIN_DEALS = 5
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR",
      "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}
NAEU = EU | {"USA", "CAN"}
EARLY = {"seed", "angel", "pre_seed", "equity_crowdfunding", "convertible_note"}
CUT = pd.Timestamp("2017-10-31")
END = pd.Timestamp("2023-10-31")


def log(*a):
    print(*a, flush=True)


# ── P001-22 의 파트너 모집단을 그대로 재구성 ────────────────────────────────
d = pd.read_parquet(os.environ.get("P001_SAMPLE", "/path/to/sample_v1.parquet"))
d["dt"] = pd.to_datetime(d["dt"])
dn = d[d["country_code"].isin(NAEU)]
hist = dn[dn["dt"] <= CUT].copy()
hist["mcell"] = hist["year"] + "|" + hist["cat"] + "|" + hist["stage"]
hist["resid"] = hist["exit_ever"] - hist.groupby("mcell")["exit_ever"].transform("mean")
hist["early"] = hist["stage"].isin(EARLY).astype(float)
P = hist.groupby("partner_uuid").agg(
    raw=("exit_ever", "mean"), adj=("resid", "mean"), n=("exit_ever", "size"),
    fp=("fp", "first"), early_sh=("early", "mean"), ncat=("cat", "nunique"),
    firm=("investor_uuid", lambda s: s.mode().iloc[0])).reset_index()
P = P[P["n"] >= MIN_DEALS].reset_index(drop=True)

pt = CTX.partners.dropna(subset=["funding_round_uuid", "investor_uuid", "partner_uuid"])
r = CTX.rounds.dropna(subset=["announced_on"])[["uuid", "announced_on"]].copy()
r["rdt"] = pd.to_datetime(r["announced_on"], errors="coerce")
A = pt.merge(r, left_on="funding_round_uuid", right_on="uuid").dropna(subset=["rdt"])
firm_first = A.groupby("investor_uuid")["rdt"].min()
fut = A[(A["rdt"] > CUT) & (A["rdt"] <= END)]
fut_firms = fut.groupby("partner_uuid")["investor_uuid"].agg(set)
home = dict(zip(P["partner_uuid"], P["firm"]))
mv, sp, newfirms = [], [], []
for pid in P["partner_uuid"]:
    fs = fut_firms.get(pid, set()) - {home[pid]}
    mv.append(1.0 if fs else 0.0)
    nf = [f for f in fs if firm_first.get(f, pd.Timestamp("1900-01-01")) > CUT]
    sp.append(1.0 if nf else 0.0)
    newfirms.append(nf)
P["move"], P["spin"] = mv, sp
P["newfirms"] = newfirms
P["raw_pct"] = P["raw"].rank(pct=True)
P["adj_pct"] = P["adj"].rank(pct=True)
P["ln_n"] = np.log(P["n"])
P["wedge"] = P["raw_pct"] - P["adj_pct"]
CTRL = ["ln_n", "fp", "early_sh", "ncat"]
log(f"[재구성] 파트너 {len(P):,} (여성 {int((P['fp'] == 1).sum())}) · "
    f"move {P['move'].mean():.3f} ({int(P['move'].sum())}건) · "
    f"spin {P['spin'].mean():.3f} ({int(P['spin'].sum())}건)")


def fit(s, ycol, xc):
    X = np.column_stack([s[c].to_numpy(float) for c in xc] + [np.ones(len(s))])
    return np.linalg.lstsq(X, s[ycol].to_numpy(float), rcond=None)[0]


def boot(df, ycol, xc, k, nb=NB, gcol="firm"):
    b0 = fit(df, ycol, xc)[k]
    grp = {c: g.index.to_numpy() for c, g in df.groupby(gcol)}
    keys = list(grp)
    bs = []
    for _ in range(nb):
        pick = rng.integers(0, len(keys), len(keys))
        s = df.loc[np.concatenate([grp[keys[i]] for i in pick])]
        try:
            bs.append(fit(s, ycol, xc)[k])
        except Exception:
            pass
    return round(float(b0), 5), qci(np.array(bs))


OUT = {}
# ── A1 재현 ────────────────────────────────────────────────────────────────
log("\n" + "=" * 96)
log("[A1] 원 수치 재현 (선행 조건). 기대: spin β_raw≈-0.158, β_adj≈+0.190")
log("=" * 96)
XC0 = ["raw_pct", "adj_pct"] + CTRL
rep = {}
for y in ("move", "spin"):
    br, cr = boot(P, y, XC0, 0)
    ba, ca = boot(P, y, XC0, 1)
    rep[y] = {"beta_raw": br, "ci_raw": cr, "beta_adj": ba, "ci_adj": ca}
    log(f"  {y:<5} β_raw={br:+.5f} [{cr[0]:+.4f},{cr[1]:+.4f}]  "
        f"β_adj={ba:+.5f} [{ca[0]:+.4f},{ca[1]:+.4f}]")
ok_rep = (abs(rep["spin"]["beta_raw"] - (-0.158)) < 0.02
          and abs(rep["spin"]["beta_adj"] - 0.190) < 0.02)
log(f"  재현 판정: {'성공' if ok_rep else '** 실패 — 아래 감사는 무효 **'}")
OUT["A1_reproduce"] = dict(rep, reproduced=bool(ok_rep))

# ── A2 공선성 진단 ─────────────────────────────────────────────────────────
log("\n" + "=" * 96)
log("[A2] 경마의 공선성")
log("=" * 96)
rho = float(np.corrcoef(P["raw_pct"], P["adj_pct"])[0, 1])
# VIF(raw_pct) = 1/(1-R2) of raw_pct on 나머지 회귀변수
oth = ["adj_pct"] + CTRL
Xo = np.column_stack([P[c].to_numpy(float) for c in oth] + [np.ones(len(P))])
yv = P["raw_pct"].to_numpy(float)
bb = np.linalg.lstsq(Xo, yv, rcond=None)[0]
r2 = 1 - ((yv - Xo @ bb) ** 2).sum() / ((yv - yv.mean()) ** 2).sum()
vif = 1 / max(1 - r2, 1e-12)
log(f"  ρ(raw_pct, adj_pct) = {rho:.4f}")
log(f"  raw_pct 를 나머지 회귀변수에 회귀한 R² = {r2:.4f} → **VIF = {vif:.2f}**")
log(f"  → 경마 계수는 두 랭크가 불일치하는 잔차 {(1 - r2) * 100:.1f}% 에서만 식별된다")
OUT["A2_collinearity"] = {"rho_raw_adj": round(rho, 4), "R2_raw_on_others": round(r2, 4),
                          "VIF_raw": round(vif, 3),
                          "identifying_share": round(1 - r2, 4)}

# ── A3 재모수화 항등 ───────────────────────────────────────────────────────
log("\n" + "=" * 96)
log("[A3] 재모수화 — y ~ adj_pct + wedge 에서 β_wedge ≡ β_raw|adj 인가")
log("=" * 96)
XCW = ["wedge", "adj_pct"] + CTRL
ident = {}
for y in ("move", "spin"):
    bw = float(fit(P, y, XCW)[0])
    # D053: 미반올림 값으로 비교한다. 초판은 boot() 가 round(b0, 5) 로 저장한 값과 round(bw, 6) 을
    # 비교해 5dp-6dp 차이(~1e-6)가 '항등 불성립'으로 오판됐다 — lstsq 정밀도 문제가 아니었다.
    br = float(fit(P, y, XC0)[0])
    ident[y] = {"beta_wedge": round(bw, 6), "beta_raw_orig": round(br, 6),
                "abs_diff": float(abs(bw - br)), "identical": bool(abs(bw - br) < 1e-8)}
    log(f"  {y:<5} β_wedge={bw:+.6f}  vs  β_raw|adj={br:+.6f}  차={abs(bw - br):.2e}  "
        f"{'**항등 성립**' if abs(bw - br) < 1e-8 else '불일치'}")
log("  → 항등이 성립하면 P1(β_raw>0)은 **terrain(=wedge) 계수**를 검정한 것이다.")
log("     'wedge>0' = 조정이 정당화하는 것보다 원시 랭크가 부풀려진 정도(유리한 terrain).")
OUT["A3_reparam_identity"] = ident

# ── A4 단독 사양 ───────────────────────────────────────────────────────────
log("\n" + "=" * 96)
log("[A4] 단독 사양 — 각 신호가 **홀로** 평가자 결과를 예측하는가")
log("=" * 96)
solo = {}
for y in ("move", "spin"):
    for nm, xc in (("raw 단독", ["raw_pct"] + CTRL), ("adj 단독", ["adj_pct"] + CTRL)):
        b, c = boot(P, y, xc, 0)
        solo[f"{y}|{nm}"] = {"coef": b, "ci95": c, "sig": bool(c[0] > 0 or c[1] < 0)}
        log(f"  {y:<5} {nm:<8} β={b:+.5f} [{c[0]:+.4f},{c[1]:+.4f}] "
            f"{'유의' if (c[0] > 0 or c[1] < 0) else 'ns'}")
OUT["A4_solo"] = solo

# ── A5 표본외 예측력 비교 ──────────────────────────────────────────────────
log("\n" + "=" * 96)
log("[A5] 표본외 예측력 — ' 어느 신호를 쓰는가' 는 부분계수가 아니라 예측력 문제")
log("=" * 96)


def auc(yt, s):
    yt = np.asarray(yt, float)
    s = np.asarray(s, float)
    pos, neg = s[yt == 1], s[yt == 0]
    if not len(pos) or not len(neg):
        return np.nan
    r = pd.Series(s).rank().to_numpy()
    return float((r[yt == 1].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


cv = {}
folds = rng.permutation(len(P)) % 5
for y in ("move", "spin"):
    for nm, xc in (("raw 단독", ["raw_pct"] + CTRL), ("adj 단독", ["adj_pct"] + CTRL),
                   ("둘 다", ["raw_pct", "adj_pct"] + CTRL)):
        aa = []
        for k in range(5):
            tr, te = P[folds != k], P[folds == k]
            b = fit(tr, y, xc)
            Xt = np.column_stack([te[c].to_numpy(float) for c in xc] + [np.ones(len(te))])
            aa.append(auc(te[y].to_numpy(), Xt @ b))
        cv[f"{y}|{nm}"] = round(float(np.nanmean(aa)), 4)
        log(f"  {y:<5} {nm:<8} 5겹 CV AUC = {np.nanmean(aa):.4f}")
OUT["A5_cv_auc"] = cv
d_move = cv["move|raw 단독"] - cv["move|adj 단독"]
d_spin = cv["spin|raw 단독"] - cv["spin|adj 단독"]
log(f"  차이(raw − adj): move {d_move:+.4f} · spin {d_spin:+.4f}  "
    f"→ |차| < 0.02 면 '구분 불가'")

# ── A6 LP 측 검정 (새 레버) ────────────────────────────────────────────────
log("\n" + "=" * 96)
log("[A6] LP 측 검정 — 스핀아웃 신생 회사가 **펀드를 조성했는가**. P001-22 가 불가능하다고 적은 것")
log("=" * 96)
F = CTX.funds.dropna(subset=["entity_uuid", "announced_on"]).copy()
F["fdt"] = pd.to_datetime(F["announced_on"], errors="coerce")
F["famt"] = pd.to_numeric(F["raised_amount_usd"], errors="coerce")
F = F[(F["fdt"] > CUT) & (F["fdt"] <= pd.Timestamp("2024-12-31"))]
fund_any = set(F["entity_uuid"])
fund_amt = F.groupby("entity_uuid")["famt"].max()
S = P[P["spin"] == 1].copy()
S["lp_any"] = [1.0 if any(f in fund_any for f in nf) else 0.0 for nf in S["newfirms"]]
S["lp_amt"] = [np.log(max([fund_amt.get(f, np.nan) for f in nf] + [np.nan]))
               if any((f in fund_any) for f in nf) else np.nan for nf in S["newfirms"]]
log(f"  스핀아웃 파트너 {len(S):,} · 신생회사가 펀드 조성 {int(S['lp_any'].sum())}건 "
    f"({S['lp_any'].mean():.1%}) · 조성액 관측 {int(S['lp_amt'].notna().sum())}건")
A6 = {"n_spinout": int(len(S)), "n_raised": int(S["lp_any"].sum()),
      "rate": round(float(S["lp_any"].mean()), 4), "n_amt": int(S["lp_amt"].notna().sum())}
if len(S) >= 60:
    for nm, xc in (("raw 단독", ["raw_pct"] + CTRL), ("adj 단독", ["adj_pct"] + CTRL),
                   ("wedge+adj", XCW)):
        b, c = boot(S, "lp_any", xc, 0, nb=300)
        A6[f"lp_any|{nm}"] = {"coef": b, "ci95": c, "sig": bool(c[0] > 0 or c[1] < 0)}
        log(f"  펀드조성 ← {nm:<10} β={b:+.5f} [{c[0]:+.4f},{c[1]:+.4f}] "
            f"{'유의' if (c[0] > 0 or c[1] < 0) else 'ns'}")
else:
    log(f"  ** 스핀아웃 {len(S)}건 — 표본 부족으로 LP 회귀 불가 (게이트 60)")
    A6["insufficient"] = True
OUT["A6_LP_side"] = A6

# ── A7 수용 회사 품질 (보조) ───────────────────────────────────────────────
log("\n" + "=" * 96)
log("[A7] 이동한 파트너로 한정 — 수용 회사의 품질이 어느 랭크를 따르는가")
log("=" * 96)
pre = A[A["rdt"] <= CUT]
fq_n = pre.groupby("investor_uuid").size()
M = P[P["move"] == 1].copy()
M["recv_q"] = [np.log1p(max([fq_n.get(f, 0) for f in nf] + [0]))
               if nf else np.nan for nf in M["newfirms"]]
# newfirms 는 신생만 담고 있으므로 이동 전체의 수용사를 다시 계산
recv_all = []
for pid, hm in zip(M["partner_uuid"], M["firm"]):
    fs = fut_firms.get(pid, set()) - {hm}
    recv_all.append(np.log1p(max([fq_n.get(f, 0) for f in fs] + [0])) if fs else np.nan)
M["recv_q"] = recv_all
M2 = M.dropna(subset=["recv_q"])
log(f"  이동 파트너 {len(M2):,} · 수용사 사전 딜수 log1p 중위 {M2['recv_q'].median():.2f}")
A7 = {"n_movers": int(len(M2))}
if len(M2) >= 60:
    for nm, xc in (("raw 단독", ["raw_pct"] + CTRL), ("adj 단독", ["adj_pct"] + CTRL),
                   ("wedge+adj", XCW)):
        b, c = boot(M2, "recv_q", xc, 0, nb=300)
        A7[f"recv_q|{nm}"] = {"coef": b, "ci95": c, "sig": bool(c[0] > 0 or c[1] < 0)}
        log(f"  수용사 품질 ← {nm:<10} β={b:+.5f} [{c[0]:+.4f},{c[1]:+.4f}] "
            f"{'유의' if (c[0] > 0 or c[1] < 0) else 'ns'}")
else:
    A7["insufficient"] = True
OUT["A7_receiving_firm"] = A7

# ── 판정 ───────────────────────────────────────────────────────────────────
ident_ok = all(v["identical"] for v in ident.values())
raw_solo_pos = any(v["sig"] and v["coef"] > 0 for k, v in solo.items() if "raw" in k)
lp_pos = any(isinstance(v, dict) and v.get("sig") and v.get("coef", 0) > 0
             for k, v in A6.items() if k.startswith("lp_any"))
status = "GO" if (raw_solo_pos or lp_pos) else "PARTIAL"
if ident_ok and not (raw_solo_pos or lp_pos):
    call = ("**P001-22 의 P1 은 유효한 검정이 아니었다 (β_raw|adj ≡ β_wedge = terrain 계수). "
            "그러나 단독 사양·LP 측에서도 원시 신호가 평가자 결과를 예측한다는 양의 증거는 없다. "
            "따라서 검정을 '무효'로 재분류하되 ① 은 되살리지 않는다**")
elif raw_solo_pos or lp_pos:
    call = ("**원시 신호가 평가자 결과를 예측하는 양의 증거가 나왔다 — ① 재개 근거. "
            "사양 결함(β_raw|adj ≡ terrain)과 함께 기록하고 재설계한다**")
else:
    call = "**재모수화 항등이 성립하지 않는다 — 내 의심 1 기각. 원 판정 유지**"
verdict = (f"재현 {'성공' if ok_rep else '실패'} | ρ={rho:.3f} VIF={vif:.2f} 식별지분 "
           f"{(1 - r2) * 100:.1f}% | 항등 {ident_ok} | 단독 raw 유의양 {raw_solo_pos} | "
           f"CV AUC 차 move {d_move:+.4f} spin {d_spin:+.4f} | "
           f"LP: 스핀아웃 {A6['n_spinout']} 조성 {A6['n_raised']} — " + call)
emit("P001-23", "P001-22 사양 전수감사 (경마 공선성·재모수화·표본외 예측력) + LP 측 검정",
     status, OUT,
     prediction="재현 성공 · ρ≥0.80 VIF≥3 · β_wedge≡β_raw 항등 성립 · 단독에선 둘 다 양수 · "
                "CV AUC 거의 동일 · LP 측은 표본 부족 가능성 높음",
     verdict=verdict, kill_met=False, n=int(len(P)),
     extra={"stage": 7, "feeds": "주장 ⑤ 귀결 철회의 재검토", "slug": "audit_p22",
            "skill": "academics:power-rescue", "audits": "P001-22"})
log("done")
