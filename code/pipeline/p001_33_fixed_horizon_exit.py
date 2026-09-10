# -*- coding: utf-8 -*-
"""p001_33 — 고정지평을 출구 기반으로: 빈티지 교란과 구성물 차이를 분리한다

[왜] P001-30 R5 는 "고정지평"을 fon(36개월 후속) 으로 구현했다. 그러나 fon 셀 평균은 exit 셀 평균과 다른
 구성물이다 — 시드 셀은 후속률이 높고 출구율이 낮다. R5 의 +0.035 는 (i) 지평을 고정해서 빈티지가 빠진
 결과인지 (ii) terrain 자체가 다른 물건이 된 결과인지 구분되지 않는다. 출구를 36개월(exit3) 고정지평으로
 재고, 사전·사후 모두 같은 지평을 쓰면 (i) 만 남는다. 사전기 딜은 2017-10 까지이므로 72개월(exit6) 도
 전부 완결 지평이다.

[구성] 사전기 = 딜 ≤ 2017-10-31. 사후기 = 2017-11 ~ 2020-10-31 (36개월 지평이 2023-10 안에 완결).
 (A) 사전 exit3 / 사후 exit3     — 같은 지평, 출구 기반 (핵심)
 (B) 사전 exit6 / 사후 exit3     — 사전기는 완결된 긴 지평, 사후기는 36개월
 (C) 사전 fon   / 사후 fon       — R5 재현 (성분 분해 추가)
 (D) 사전 exit6 / 사후 fon       — 출구 terrain 이 후속 성과를 예측하는가
 각 조합: F1 post_adj ~ t_v + t_s + t_cs + adj + ln_n + fp · F2 = F1 + 연공(TEN) · F1t/F2t 총 terrain 판.
 군집 = 홈 회사, 부트 400. 기저율(exit3/exit6/fon 사전·사후) 기록. 표준화 계수(coef·sd_x/sd_y) 병기.

[사전 예측] (2026-09-08, 결과 조회 전)
 (A) t_cs > 0, 구간 0 포함 가능(exit3 기저 ≈ 0.08 → 잔차 분산 작음); 총 terrain ∈ [0.03, 0.12].
 (B) 같은 부호. (C) 총 terrain ≈ +0.035 재현; t_cs_fon ≈ 0. (D) 양 소폭.
 고정지평에서 t_v(빈티지 성분) 는 ≈ 0 이어야 한다 — 빈티지가 지평 인공물이라는 진단의 직접 검정.
 GO: (A) 또는 (B) 의 F2(연공 통제) 에서 t_cs 또는 총 terrain 하한 > 0.
 KILL: (A)·(B) 모두 F2t 총 terrain 상단 < 0.05 (출구 기반 고정지평에서 구성 정보 부재).
 그 외 PARTIAL — MDE 병기.

[추가 패널 — 1차 실행 후 2026-09-08] 1차 실행은 A/B 에서 GO 조건을 충족한 뒤 JSON 직렬화 오류(numpy bool)로
 emit 직전에 중단됐다(수치는 seed 고정으로 재실행과 동일). GO 를 본 뒤, 심판이 다음에 물을 두 가지를 A/B 에 추가한다.
 예측은 이 패널들의 결과를 보기 전에 썼다.
 F3  회사 FE (P001-30 R4 게이트 사양을 새 구성물에 적용)      — 예측: 점추정 ≈ F2, CI 는 0 포함 가능(MDE ≈ 0.45)
 F4  사후기를 **새 기업**(파트너가 사전기에 투자하지 않은 기업) 딜로 제한 — 같은 기업의 후속 라운드가 사전·사후에
     걸쳐 있으면 그 기업의 출구가 양쪽에 들어가는 지속성 경로가 생긴다. 예측: F2 의 ≥70% 유지, A/B 중 하나는 하한 > 0
 F5  사전 terrain 을 **leave-company-out** 셀 평균으로 (공동귀속 행을 통해 같은 기업의 결과가 벤치마크에 들어가는 경로 차단)
     — 예측: F2 의 ≥80%
 F6  F4 + F5 (둘 다)                                             — 예측: F2 의 ≥60%, CI 0 포함 가능
 지속성 경로 판정: A·B 모두 F4 총 terrain 점추정 < F2 의 30% → GO 를 PARTIAL 로 격하("기계적 지속성").
"""
import numpy as np

from p001_rescue_common import (COMMON_SHA, CUT, END_FON, TC, TEN, add_post, add_tenure, boot, build, emit,
                                first_deal_dates, fmt, load_deals, log, partner_pre, show)

rng = np.random.default_rng(20260933)
OUT = {}
dn = load_deals(with_exit_dt=True)
first = first_deal_dates()
pre = dn["dt"] <= CUT
post = (dn["dt"] > CUT) & (dn["dt"] <= END_FON)
OUT["base_rates"] = {f"{c}_{w}": round(float(dn.loc[m, c].mean()), 4)
                     for c in ("exit3", "exit6", "exit_ever", "fon") for w, m in (("pre", pre), ("post", post))}
log(f"[기저율] {OUT['base_rates']}")
pre_pairs = set(zip(dn.loc[pre, "partner_uuid"], dn.loc[pre, "org_uuid"]))


def lco(df, key, ycol):
    """leave-company-out: 셀합에서 같은 기업(org_uuid)의 행 전부를 뺀다."""
    g = df.groupby(key)[ycol]
    s, n = g.transform("sum"), g.transform("size")
    go = df.groupby([key, "org_uuid"])[ycol]
    so, no = go.transform("sum"), go.transform("size")
    den = n - no
    return np.where(den > 0, (s - so) / np.maximum(den, 1), np.nan)


def partner_pre_lco(dn, ycol, min_n=5):
    h = dn[dn["dt"] <= CUT].copy()
    h["b_year"], h["b_ys"], h["b_yss"] = lco(h, "y", ycol), lco(h, "ys", ycol), lco(h, "yss", ycol)
    h["r"] = h[ycol] - h["b_yss"]
    h["t_v"], h["t_s"], h["t_cs"] = h["b_year"], h["b_ys"] - h["b_year"], h["b_yss"] - h["b_ys"]
    h = h[np.isfinite(h["r"])]
    P = h.groupby("partner_uuid").agg(raw=(ycol, "mean"), adj=("r", "mean"), n=(ycol, "size"), fp=("fp", "first"),
                                      t_v=("t_v", "mean"), t_s=("t_s", "mean"), t_cs=("t_cs", "mean"),
                                      firm=("investor_uuid", lambda s: s.mode().iloc[0])).reset_index()
    P = P[P["n"] >= min_n].reset_index(drop=True)
    P["terrain"] = P["raw"] - P["adj"]
    P["ln_n"] = np.log(P["n"])
    return P


def add_post_new(P, dn, ycol, end):
    po = build(dn[(dn["dt"] > CUT) & (dn["dt"] <= end)], ycol)
    po = po[np.isfinite(po["r"])]
    new = np.array([(p, o) not in pre_pairs for p, o in zip(po["partner_uuid"], po["org_uuid"])])
    share_rep = 1 - float(new.mean())
    po = po[new]
    agg = po.groupby("partner_uuid").agg(post_adj_new=("r", "mean"), post_n_new=("r", "size"))
    return P.join(agg, on="partner_uuid"), share_rep


def std_beta(P, y, xc, key, coef):
    dd = P.dropna(subset=[y] + xc)
    return round(float(coef * dd[key].std() / dd[y].std()), 4)


def pct(res, ref, k):
    if not res or not ref or k not in res or k not in ref or not ref[k]["coef"]:
        return None
    return round(res[k]["coef"] / ref[k]["coef"] * 100, 1)


COMBOS = {"A_exit3_exit3": ("exit3", "exit3"), "B_exit6_exit3": ("exit6", "exit3"),
          "C_fon_fon": ("fon", "fon"), "D_exit6_fon": ("exit6", "fon")}
for tag, (yp, yq) in COMBOS.items():
    log("\n" + "=" * 100 + f"\n[{tag}] 사전 {yp} → 사후 {yq} (사후 ≤ 2020-10)\n" + "=" * 100)
    P, _ = partner_pre(dn, yp)
    P = add_post(P, dn, yq, end=END_FON)
    P = add_tenure(P, first=first)
    res = {"n_partners": int(len(P)), "n_post": int(P["has_post"].sum()),
           "sd_terrain": round(float(P["terrain"].std()), 4), "sd_t_cs": round(float(P["t_cs"].std()), 4),
           "sd_t_v": round(float(P["t_v"].std()), 4), "sd_post_adj": round(float(P["post_adj"].std()), 4)}
    X1, X2 = TC + ["adj", "ln_n", "fp"], TC + ["adj", "ln_n", "fp"] + TEN
    F1 = boot(P, "post_adj", X1, TC + ["adj"], rng); show("F1 분해", F1, TC + ["adj"])
    F2 = boot(P, "post_adj", X2, TC + ["tenure"], rng); show("F2 +연공", F2, TC + ["tenure"])
    F1t = boot(P, "post_adj", ["terrain", "adj", "ln_n", "fp"], ["terrain", "adj"], rng); show("F1t 총", F1t, ["terrain", "adj"])
    F2t = boot(P, "post_adj", ["terrain", "adj", "ln_n", "fp"] + TEN, ["terrain", "adj"], rng); show("F2t 총 +연공", F2t, ["terrain", "adj"])  # adj 키 추가 (R3 재현성 감사: 표의 대조 행은 같은 통제집합에서)
    F2["t_cs"]["beta_std"] = std_beta(P, "post_adj", X2, "t_cs", F2["t_cs"]["coef"])
    F2t["terrain"]["beta_std"] = std_beta(P, "post_adj", ["terrain", "adj", "ln_n", "fp"] + TEN, "terrain", F2t["terrain"]["coef"])
    log(f"  표준화: F2 t_cs {F2['t_cs']['beta_std']:+.3f} sd · F2t terrain {F2t['terrain']['beta_std']:+.3f} sd")
    res.update({"F1": F1, "F2": F2, "F1t": F1t, "F2t": F2t})
    if tag.startswith(("A_", "B_")):
        F3 = boot(P, "post_adj", X2, TC, rng, demean="firm"); show("F3 회사 FE", F3, TC)
        F3t = boot(P, "post_adj", ["terrain", "adj", "ln_n", "fp"] + TEN, ["terrain"], rng, demean="firm"); show("F3t 총 회사 FE", F3t, ["terrain"])
        P, share_rep = add_post_new(P, dn, yq, END_FON)
        log(f"  [F4] 사후기 딜 중 사전기 동일 기업 반복 비중 {share_rep:.3f} · 새 기업 사후기 有 파트너 {int(P['post_adj_new'].notna().sum()):,}")
        F4 = boot(P, "post_adj_new", X2, TC, rng); show("F4 새 기업만 +연공", F4, TC)
        F4t = boot(P, "post_adj_new", ["terrain", "adj", "ln_n", "fp"] + TEN, ["terrain"], rng); show("F4t 총 새 기업만", F4t, ["terrain"])
        P5 = partner_pre_lco(dn, yp)
        P5 = add_post(P5, dn, yq, end=END_FON)
        P5 = add_tenure(P5, first=first)
        F5 = boot(P5, "post_adj", X2, TC, rng); show("F5 LCO terrain +연공", F5, TC)
        F5t = boot(P5, "post_adj", ["terrain", "adj", "ln_n", "fp"] + TEN, ["terrain"], rng); show("F5t 총 LCO", F5t, ["terrain"])
        P5, _ = add_post_new(P5, dn, yq, END_FON)
        F6 = boot(P5, "post_adj_new", X2, TC, rng); show("F6 LCO+새 기업", F6, TC)
        F6t = boot(P5, "post_adj_new", ["terrain", "adj", "ln_n", "fp"] + TEN, ["terrain"], rng); show("F6t 총 LCO+새 기업", F6t, ["terrain"])
        res.update({"share_repeat_company_post": round(share_rep, 4), "F3": F3, "F3t": F3t, "F4": F4, "F4t": F4t,
                    "F5": F5, "F5t": F5t, "F6": F6, "F6t": F6t,
                    "pct_of_F2t_terrain": {"F3t": pct(F3t, F2t, "terrain"), "F4t": pct(F4t, F2t, "terrain"),
                                           "F5t": pct(F5t, F2t, "terrain"), "F6t": pct(F6t, F2t, "terrain")},
                    "pct_of_F2_tcs": {"F3": pct(F3, F2, "t_cs"), "F4": pct(F4, F2, "t_cs"),
                                      "F5": pct(F5, F2, "t_cs"), "F6": pct(F6, F2, "t_cs")}})
        log(f"  F2t 대비 총 terrain: {res['pct_of_F2t_terrain']} · F2 대비 t_cs: {res['pct_of_F2_tcs']}")
    OUT[tag] = res


# ── 판정 ────────────────────────────────────────────────────────────────────
def lo(res, k):
    return res[k]["ci95"][0] if res and k in res else np.nan


def hi(res, k):
    return res[k]["ci95"][1] if res and k in res else np.nan


A, B, C = OUT["A_exit3_exit3"], OUT["B_exit6_exit3"], OUT["C_fon_fon"]
go = any(lo(x["F2"], "t_cs") > 0 or lo(x["F2t"], "terrain") > 0 for x in (A, B))
kill = all(hi(x["F2t"], "terrain") < 0.05 for x in (A, B))
persist = all((x["pct_of_F2t_terrain"]["F4t"] or 0) < 30 for x in (A, B))
if go and not persist:
    status, call = "GO", "출구 기반 고정지평에서 연공 통제 후에도 구성(섹터 성분·총 terrain) 이 장래 셀 내 성과를 예측; 새 기업 제한에서 유지"
elif go and persist:
    status, call = "PARTIAL", "F2 는 GO 이나 새 기업 제한(F4)에서 30% 미만으로 붕괴 — 기계적 지속성 경로"
elif kill:
    status, call = "KILL", "출구 기반 고정지평에서 구성 정보 부재 (총 terrain 상단 < 0.05, 두 조합 모두)"
else:
    status, call = "PARTIAL", "출구 기반 고정지평에서 검출도 배제도 안 됨 — MDE 병기"
pred = {"A_tcs_pos": bool(A["F1"]["t_cs"]["coef"] > 0),
        "A_terrain_in_[0.03,0.12]": bool(0.03 <= A["F1t"]["terrain"]["coef"] <= 0.12),
        "B_same_sign_as_A": bool(np.sign(B["F1"]["t_cs"]["coef"]) == np.sign(A["F1"]["t_cs"]["coef"])),
        "C_terrain_near_R5": bool(abs(C["F1t"]["terrain"]["coef"] - 0.035) < 0.03),
        "A_tv_abs_lt_0.10": bool(abs(A["F1"]["t_v"]["coef"]) < 0.10),
        "added_F4_ge70pct_A_or_B": bool(any((x["pct_of_F2t_terrain"]["F4t"] or 0) >= 70 for x in (A, B))),
        "added_F5_ge80pct_A_and_B": bool(all((x["pct_of_F2t_terrain"]["F5t"] or 0) >= 80 for x in (A, B)))}
OUT["prediction_check"] = pred
OUT["flags"] = {"go_prereg": bool(go), "kill_prereg": bool(kill), "persistence_downgrade": bool(persist)}
verdict = (f"A exit3/exit3: F2 t_cs {fmt(A['F2'], 't_cs')} · F2t terrain {fmt(A['F2t'], 'terrain')} (표준화 {A['F2t']['terrain']['beta_std']:+.2f}sd, MDE80 {A['F2t']['terrain']['mde80']:.3f}) · "
           f"F3t 회사FE {fmt(A['F3t'], 'terrain')} · F4t 새기업 {fmt(A['F4t'], 'terrain')} ({A['pct_of_F2t_terrain']['F4t']}%) · F5t LCO {fmt(A['F5t'], 'terrain')} · F6t {fmt(A['F6t'], 'terrain')} | "
           f"B exit6/exit3: F2 t_cs {fmt(B['F2'], 't_cs')} · F2t {fmt(B['F2t'], 'terrain')} · F4t {fmt(B['F4t'], 'terrain')} ({B['pct_of_F2t_terrain']['F4t']}%) · F5t {fmt(B['F5t'], 'terrain')} | "
           f"C fon/fon: F1t {fmt(C['F1t'], 'terrain')} · t_cs {fmt(C['F1'], 't_cs')} | D exit6/fon: F2t {fmt(OUT['D_exit6_fon']['F2t'], 'terrain')} | "
           f"A t_v {fmt(A['F1'], 't_v')} (sd {A['sd_t_v']}) — {call} (예측 적중 {sum(pred.values())}/{len(pred)})")
emit("P001-33", "고정지평(출구 기반 exit3/exit6) 에서의 구성 성분 → 장래 셀 내 성과 (+회사 FE·새 기업·leave-company-out)", status, OUT,
     prediction="A t_cs>0 구간 0 포함 가능, 총 terrain∈[0.03,0.12]; C 는 R5 재현; 고정지평에서 t_v≈0; GO=A/B F2 하한>0; KILL=A·B F2t 상단<0.05; 추가 F4≥70%·F5≥80%",
     verdict=verdict, kill_met=(status == "KILL"), n=int(A["n_partners"]),
     extra={"stage": 7, "feeds": "R2 power-rescue", "slug": "fixed_horizon_exit", "builds_on": "P001-30 R5",
            "common_sha256_16": COMMON_SHA})
log("done")
