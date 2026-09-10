# -*- coding: utf-8 -*-
"""p001_24 — 주장 ③ S&S 대조 **필수 재실행** (EVIDENCE_MAP §7 지정 사양)

[왜 재실행인가] §7 신규성 감사가 `P001-19` 를 **표적 오조준**으로 판정했다.
 - `lead_fp_attr` 가 "리드의 귀속 파트너 중 **여성이 한 명이라도** 있으면 1" 이라
   **여성-전용과 혼성을 풀링**했다. 그런데 **혼성은 S&S 의 최고 성과 셀**이다
   (그들 Table 4: 여성VC×여성창업 기업의 IPO 확률 ~3배 높음).
 - `lead_fp_share_hi`(회사 수준 fp_share > 중위)는 더 거칠다.
 - 결과변수가 36개월 후속조달 **LPM** 이었다. S&S 의 대상은 **출구**이고 이론도 출구를 예측한다.
§7 이 지정한 재실행 사양: **여성-전용 파트너 · 첫 라운드 · US · Seed/A · 2010–18 · Cox.**

[설계]
 표본  미국 · **여성 창업** 기업의 **첫 라운드** · `seed`/`series_a` · 2010-01~2018-12
 처치  리드 투자사의 귀속 파트너가 **전원 여성**(=1) vs **전원 남성**(=0). **혼성은 제외**
       (오조준의 원인을 제거한다 — 혼성을 포함하면 S&S 의 최고 성과 셀이 처치군에 섞인다)
 기간  첫 라운드일 → min(출구일, 2024-12-31).  사건 = 인수 또는 IPO
 추정  Cox 비례위험 (Breslow 동시발생 처리), 공변량 = 처치 + 연도 + 섹터 + 단계
 추론  리드 투자사 군집 부트스트랩
 자체검사 (1) 부분우도 기울기가 최적점에서 0 (2) 처치 단독 사양의 계수를
       log(위험비)와 대조되는 단순 비율 검정과 부호 일치 (3) 공변량 없는 Cox 를
       Nelson-Aalen 기반 조군 비교와 부호 대조

[사전 예측] (결과 조회 전, 2026-09-08)
 P1 여성전용 리드의 계수가 **양(+)** — S&S 방향(여성VC 백킹 여성창업의 출구 유리).
    §7 이 "그들 이론도 출구 null 예측"이라 했으므로 **0 근처일 수도 있다**. 어느 쪽이든 보고한다.
 P2 표본이 작아 CI 가 넓을 것 — **표본 게이트 (사건 40건) 미달 가능성이 실질 위험**이다.
 P3 혼성을 **포함**한 사양(구 정의 재현)과 **제외**한 사양의 부호·크기가 갈린다.
    갈리면 §7 의 오조준 판정이 수치로 확인된다.
[게이트] 사건 40건 이상. 미달 시 KILL 하고 "CB 로 이 대조는 검정 불가"로 기록한다.
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
EQ_EXCL = {"grant", "debt_financing", "post_ipo_debt", "post_ipo_equity", "non_equity_assistance"}
STAGES = {"seed", "series_a"}
T_END = pd.Timestamp("2024-12-31")


def log(*a):
    print(*a, flush=True)


# ── 창업자 성별 · 기업 ─────────────────────────────────────────────────────
ppl = CTX.people[["uuid", "gender"]]
g_map = ppl[ppl["gender"].isin(["male", "female"])].set_index("uuid")["gender"]
jb = CTX.jobs
fj = jb[jb["title"].fillna("").str.lower().str.contains("founder", regex=False)][
    ["person_uuid", "org_uuid"]].dropna()
fj["fg"] = fj["person_uuid"].map(g_map)
fj = fj[fj["fg"].notna()]
org_ff = (fj["fg"] == "female").groupby(fj["org_uuid"]).max()

r = CTX.rounds.dropna(subset=["announced_on", "org_uuid"]).copy()
r = r[~r["investment_type"].isin(EQ_EXCL)]
r["rdt"] = pd.to_datetime(r["announced_on"], errors="coerce")
r = r.dropna(subset=["rdt"])
r1 = r.sort_values("rdt").groupby("org_uuid").head(1)
r1 = r1[(r1["rdt"] >= "2010-01-01") & (r1["rdt"] <= "2018-12-31")
        & (r1["country_code"] == "USA")
        & (r1["investment_type"].isin(STAGES))].copy()
r1["ff"] = r1["org_uuid"].map(org_ff)
r1 = r1[r1["ff"] == True].copy()  # noqa: E712
log(f"[표본] 미국·여성창업·첫라운드·Seed/A·2010-18 = {len(r1):,}")

# ── 리드 투자사 · 귀속 파트너 성별 구성 ────────────────────────────────────
inv = CTX.inv.dropna(subset=["funding_round_uuid", "investor_uuid"])
lead = inv[inv["is_lead_investor"] == True]  # noqa: E712
lead1 = lead.groupby("funding_round_uuid")["investor_uuid"].first()
r1["lead_inv"] = r1["uuid"].map(lead1)
r1 = r1[r1["lead_inv"].notna()].copy()
log(f"  리드 식별 {len(r1):,}")

pt = CTX.partners.dropna(subset=["funding_round_uuid", "investor_uuid", "partner_uuid"])
pt2 = pt.merge(r1[["uuid", "lead_inv"]], left_on=["funding_round_uuid", "investor_uuid"],
               right_on=["uuid", "lead_inv"], suffixes=("", "_r"))
pt2["pg"] = pt2["partner_uuid"].map(g_map)
pt2 = pt2.dropna(subset=["pg"])
comp = pt2.groupby("funding_round_uuid")["pg"].agg(
    nf=lambda s: int((s == "female").sum()), nm=lambda s: int((s == "male").sum()))
r1 = r1.join(comp, on="uuid")
r1 = r1[r1[["nf", "nm"]].notna().all(axis=1)].copy()
r1["allf"] = ((r1["nf"] > 0) & (r1["nm"] == 0)).astype(float)
r1["allm"] = ((r1["nm"] > 0) & (r1["nf"] == 0)).astype(float)
r1["mixed"] = ((r1["nf"] > 0) & (r1["nm"] > 0)).astype(float)
log(f"  귀속 성별 관측 {len(r1):,} — 전원여성 {int(r1['allf'].sum())} · "
    f"전원남성 {int(r1['allm'].sum())} · 혼성 {int(r1['mixed'].sum())}")

# ── 출구 시점 ──────────────────────────────────────────────────────────────
ac = CTX.acq.copy()
acol = [c for c in ac.columns if "acquiree" in c and "uuid" in c]
ac["adt"] = pd.to_datetime(ac.get("acquired_on"), errors="coerce")
ex1 = ac.dropna(subset=["adt"]).groupby(acol[0])["adt"].min() if acol else pd.Series(dtype="datetime64[ns]")
ip = CTX.ipos.copy()
icol = [c for c in ip.columns if "org" in c and "uuid" in c]
ip["idt"] = pd.to_datetime(ip.get("went_public_on"), errors="coerce")
ex2 = ip.dropna(subset=["idt"]).groupby(icol[0])["idt"].min() if icol else pd.Series(dtype="datetime64[ns]")
exit_dt = pd.concat([ex1, ex2]).groupby(level=0).min()
r1["xdt"] = r1["org_uuid"].map(exit_dt)
r1["event"] = ((r1["xdt"].notna()) & (r1["xdt"] > r1["rdt"]) & (r1["xdt"] <= T_END)).astype(float)
r1["dur"] = np.where(r1["event"] == 1, (r1["xdt"] - r1["rdt"]).dt.days,
                     (T_END - r1["rdt"]).dt.days)
r1 = r1[r1["dur"] > 0].copy()
r1["yr"] = r1["rdt"].dt.year.astype(int)
orgs = CTX.orgs
topcat = dict(zip(orgs["uuid"],
                  orgs["category_groups_list"].fillna("NA").str.split(",").str[0].str.strip()))
r1["cat"] = r1["org_uuid"].map(topcat).fillna("NA")
log(f"  기간·사건 구성 후 {len(r1):,} · 출구사건 {int(r1['event'].sum())} "
    f"({r1['event'].mean():.1%}) · 기간 중위 {r1['dur'].median():.0f}일")


# ── Cox 부분우도 (Breslow) ─────────────────────────────────────────────────
def cox(X, dur, ev, iters=60, tol=1e-10):
    """Breslow 동시발생 처리. 시간 내림차순으로 위험집합 누적."""
    o = np.argsort(-dur)
    X, dur, ev = X[o], dur[o], ev[o]
    n, k = X.shape
    b = np.zeros(k)
    for _ in range(iters):
        eta = np.clip(X @ b, -50, 50)
        w = np.exp(eta)
        S0 = np.cumsum(w)
        S1 = np.cumsum(X * w[:, None], axis=0)
        S2 = np.cumsum(np.einsum("ij,ik,i->ijk", X, X, w), axis=0)
        # 동시발생 시각의 위험집합은 그 시각의 마지막 인덱스를 쓴다
        idx = np.zeros(n, dtype=int)
        last = 0
        for i in range(n):
            if i > 0 and dur[i] != dur[i - 1]:
                last = i
            idx[i] = None if False else last
        # 위험집합 = dur >= t  → 내림차순이므로 [0 .. 그 시각 마지막 인덱스]
        end = np.zeros(n, dtype=int)
        i = 0
        while i < n:
            j = i
            while j + 1 < n and dur[j + 1] == dur[i]:
                j += 1
            end[i:j + 1] = j
            i = j + 1
        m = ev == 1
        if m.sum() == 0:
            return b, np.zeros(k), False
        s0 = S0[end[m]]
        s1 = S1[end[m]]
        s2 = S2[end[m]]
        g = (X[m] - s1 / s0[:, None]).sum(axis=0)
        H = -(s2 / s0[:, None, None]
              - np.einsum("ij,ik->ijk", s1 / s0[:, None], s1 / s0[:, None])).sum(axis=0)
        try:
            step = np.linalg.solve(H - 1e-10 * np.eye(k), g)
        except np.linalg.LinAlgError:
            return b, g, False
        b = b - step
        if np.max(np.abs(step)) < tol:
            eta = np.clip(X @ b, -50, 50)
            w = np.exp(eta)
            S0 = np.cumsum(w)
            S1 = np.cumsum(X * w[:, None], axis=0)
            s0 = S0[end[m]]
            s1 = S1[end[m]]
            g = (X[m] - s1 / s0[:, None]).sum(axis=0)
            return b, g, True
    return b, g, False


def design(df, extra_cells=True):
    cols = [df["allf"].to_numpy(float)]
    names = ["allf"]
    if extra_cells:
        for c, pref in (("yr", "y"), ("cat", "c")):
            lv = sorted(df[c].astype(str).unique())[1:]
            for v in lv:
                cols.append((df[c].astype(str) == v).to_numpy(float))
                names.append(f"{pref}:{v}")
        cols.append((df["investment_type"] == "series_a").to_numpy(float))
        names.append("series_a")
    return np.column_stack(cols), names


OUT = {}
# 사양 1: 혼성 제외 (§7 지정)
D1 = r1[(r1["allf"] == 1) | (r1["allm"] == 1)].copy()
nev1 = int(D1["event"].sum())
log("\n" + "=" * 92)
log(f"[사양 1 — §7 지정] 혼성 제외. n={len(D1):,} 사건={nev1}")
log("=" * 92)
gate = nev1 >= 40
if not gate:
    log(f"  ** 사건 {nev1}건 < 게이트 40 — 검정 불가")
else:
    for nm, cells in (("처치 단독", False), ("+연도·섹터·단계", True)):
        X, names = design(D1, cells)
        b, g, conv = cox(X, D1["dur"].to_numpy(float), D1["event"].to_numpy(float))
        gmax = float(np.max(np.abs(g)))
        keys = {c: gg.index.to_numpy() for c, gg in D1.reset_index(drop=True).groupby("lead_inv")}
        kl = list(keys)
        bs = []
        # 수렴하지 않은 사양은 부트스트랩하지 않는다 — 비수렴 점추정의 재표집은 의미가 없다 (D045)
        for _ in range(NB if conv else 0):
            pick = rng.integers(0, len(kl), len(kl))
            rows = np.concatenate([keys[kl[i]] for i in pick])
            s = D1.reset_index(drop=True).iloc[rows]
            try:
                Xs, _ = design(s, cells)
                bb, _, cc = cox(Xs, s["dur"].to_numpy(float), s["event"].to_numpy(float), iters=40)
                if cc:
                    bs.append(float(bb[0]))
            except Exception:
                pass
        lo, hi = qci(np.array(bs)) if len(bs) > 30 else (np.nan, np.nan)
        OUT[f"S1|{nm}"] = {"beta_allf": round(float(b[0]), 5), "hazard_ratio": round(float(np.exp(b[0])), 4),
                           "ci95_beta": [round(lo, 5), round(hi, 5)], "converged": bool(conv),
                           "grad_max": gmax, "n": int(len(D1)), "n_event": nev1, "n_boot": len(bs),
                           "sig": bool(lo > 0 or hi < 0)}
        log(f"  {nm:<16} β(전원여성)={float(b[0]):+.5f}  HR={np.exp(b[0]):.3f}  "
            f"[{lo:+.4f},{hi:+.4f}] {'유의' if (lo > 0 or hi < 0) else 'ns'}  "
            f"수렴={conv} |∇|max={gmax:.2e}")

# 사양 2: 혼성 포함 (구 정의 재현 — 오조준의 수치 확인)
D2 = r1[(r1["allf"] == 1) | (r1["mixed"] == 1) | (r1["allm"] == 1)].copy()
D2["anyf"] = ((D2["allf"] == 1) | (D2["mixed"] == 1)).astype(float)
log("\n" + "=" * 92)
log("[사양 2 — 구 정의 재현] '여성 한 명이라도' = 전원여성+혼성 풀링. §7 오조준 판정의 수치 확인")
log("=" * 92)
if int(D2["event"].sum()) >= 40:
    D2b = D2.rename(columns={"allf": "_allf_orig", "anyf": "allf"})
    X, names = design(D2b, True)
    b, g, conv = cox(X, D2b["dur"].to_numpy(float), D2b["event"].to_numpy(float))
    OUT["S2|구정의(혼성포함)"] = {"beta_anyf": round(float(b[0]), 5),
                              "hazard_ratio": round(float(np.exp(b[0])), 4),
                              "converged": bool(conv), "n": int(len(D2b)),
                              "n_event": int(D2b["event"].sum())}
    log(f"  β(여성 한 명이라도)={float(b[0]):+.5f}  HR={np.exp(b[0]):.3f}  수렴={conv}  "
        f"(n={len(D2b):,}, 사건={int(D2b['event'].sum())})")
    s1 = OUT.get("S1|+연도·섹터·단계", {}).get("beta_allf")
    if s1 is not None:
        log(f"  → 전원여성 {s1:+.5f} vs 여성한명이라도 {float(b[0]):+.5f} "
            f"차={abs(s1 - float(b[0])):.5f}  "
            f"{'**부호 갈림 — 오조준 확인**' if s1 * float(b[0]) < 0 else '부호 동일'}")
else:
    log(f"  사건 {int(D2['event'].sum())}건 — 불가")

# 혼성 단독 (S&S 최고 성과 셀 확인)
D3 = r1[(r1["mixed"] == 1) | (r1["allm"] == 1)].copy()
D3["allf"] = D3["mixed"]
log("\n[보조] 혼성 vs 전원남성 (S&S 의 최고 성과 셀인지 확인)")
if int(D3["event"].sum()) >= 40:
    X, _ = design(D3, True)
    b, g, conv = cox(X, D3["dur"].to_numpy(float), D3["event"].to_numpy(float))
    OUT["S3|혼성vs전원남성"] = {"beta_mixed": round(float(b[0]), 5),
                             "hazard_ratio": round(float(np.exp(b[0])), 4),
                             "converged": bool(conv), "n": int(len(D3)),
                             "n_event": int(D3["event"].sum())}
    log(f"  β(혼성)={float(b[0]):+.5f}  HR={np.exp(b[0]):.3f}  수렴={conv} "
        f"(사건={int(D3['event'].sum())})")
else:
    log(f"  사건 {int(D3['event'].sum())}건 — 불가")

OUT["counts"] = {"n_allf": int(r1["allf"].sum()), "n_allm": int(r1["allm"].sum()),
                 "n_mixed": int(r1["mixed"].sum()), "n_events": int(r1["event"].sum()),
                 "n_total": int(len(r1))}
status = "GO" if gate else "KILL"
main = OUT.get("S1|+연도·섹터·단계", {})
if not gate:
    call = (f"**출구 사건 {nev1}건 < 게이트 40 — §7 이 지정한 대조는 CB 로 검정 불가. "
            f"주장 ③ 은 S&S 와의 수치 대조 없이 서술해야 한다**")
elif main.get("sig"):
    call = (f"**전원여성 리드의 출구 위험비 {main['hazard_ratio']} (유의) — S&S 방향 "
            f"{'확인' if main['beta_allf'] > 0 else '반대'}. 주장 ③ 을 이 수치로 재서술**")
else:
    call = (f"**전원여성 리드의 출구 위험비 {main.get('hazard_ratio')} 이나 CI 가 0 을 포함 — "
            f"미검출. §7 의 오조준은 교정했으나 대조 자체는 무정보**")
verdict = (f"표본 {len(r1):,} (전원여성 {int(r1['allf'].sum())}/전원남성 {int(r1['allm'].sum())}/"
           f"혼성 {int(r1['mixed'].sum())}) 사건 {int(r1['event'].sum())} | "
           + " | ".join(f"{k}: β={v.get('beta_allf', v.get('beta_anyf', v.get('beta_mixed')))} "
                        f"HR={v.get('hazard_ratio')}" for k, v in OUT.items())
           + " — " + call)
emit("P001-24", "주장 ③ S&S 대조 필수 재실행 — 여성전용 리드·첫라운드·US·Seed/A·2010-18·Cox",
     status, OUT,
     prediction="전원여성 계수 양(+) 또는 0 근처 · 표본 부족이 실질 위험 · "
                "혼성 포함/제외에서 부호 갈리면 §7 오조준 확인",
     verdict=verdict, kill_met=(not gate), n=int(len(r1)),
     extra={"stage": 7, "feeds": "주장 ③ 서술 확정", "slug": "ss_rerun_cox",
            "supersedes": "P001-19 의 S&S 대조 (표적 오조준)"})
log("done")
