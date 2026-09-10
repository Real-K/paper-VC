# -*- coding: utf-8 -*-
"""p001_04b 재가중 스택 — 오염 규칙 구현 정정판 (동결 사양 준수: 오염 "대조"만 제외)

[정정 사유] p001_04 는 오염 제외를 처치(여성 사건)에도 대칭 적용 → 여성 사건 945→212 붕괴,
L3 CI ±12pp. 동결 그리드 문언은 exclude_contaminated_CONTROLS — 남성 사건(대조) 중 ±24m 내
여성 사건이 있는 회사의 것만 제외한다. 여성 사건은 유지. 구현 편차의 정정 — 원판(P001-04)도
원장에 그대로 남긴다.
[원판 docstring 이하 동일]

[왜] E3 는 I-82 로 연관 강등. 승격 사전 조건(ESTIMAND_CARD): 재가중 스택 + 추세강건 결합이 0 배제.
power-rescue 절차 — 레버를 쌓지 않고 **사다리로 분리 보고**: L0 원 스택 → L1 오염 대조 제외 →
L2 재가중 → L3 추세 조정(선형) + 파단 기울기 M̄. 각 단계의 결합 대비(영입−이탈)와 CI.
[설계] 사건: i82 와 동일 정의(깨끗한 영입·마지막 이탈, 2012–2023, jobs.started_on/ended_on),
  투자사 국가 NA+EU (D007). 결과: V 의 반기별 신규 딜 ff 비중 (cores_v1 보조표 — 문서화된 예외:
  분모는 V 의 전체 신규 딜이어야 하므로 sample_v1(귀속 딜)로는 불가). 상대반기 k=−4..+3.
  DiD_k = [ff_f,k − ff_f,pre̅] − [ff_m,k − ff_m,pre̅] (사건 동일가중). 부트 = 사건 재표집 500.
  L1 오염 제외: 반대 성별 사건이 ±24m 내 있는 회사의 사건 제외.
  L2 재가중: 남성 사건을 여성 사건의 (사건 반기 bin × 사전 ff 비중 3분위 × 회사 딜수 3분위) 셀에
  맞춰 재가중 (셀 내 여성/남성 빈도비).
  L3 추세 조정: k=−4..−1 의 DiD_k 에 선형 적합 → 외삽 차감 후 사후 평균; 파단 기울기
  M̄* = (조정 전 사후 평균) / (평균 사후 k−중심) — 효과가 0 이 되는 차등추세 기울기.
  위약: 전원 남성팀 신규 딜 log1p 건수 경로 (동일 L2 가중) · 성별 라벨 순열 200.
[사전 예측] (결과 전 — H9 등록분)
  P1 L0 사후 누적 결합 분기 ≥ +1pp. P2 L2 재가중 후 사전 구간 DiD_k 진폭 축소 (균형 개선).
  P3 L3 조정 결합 CI 가 I-82 (±3.6pp 폭) 보다 좁아짐 — 0 배제 여부가 승격 판정.
  P4 위약(남성팀 건수) 경로 발산 없음 · 순열 p < 0.05.
[판정] P3 에서 0 배제 + P4 청정 → E3 인과 승격 (ESTIMAND_CARD 사전 조건 ①). 아니면 연관 확정 —
  "not detected" 와 "absent" 구분, 파단 M̄* 병기.
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
NB = 500
EQ_EXCL = {"grant", "debt_financing", "post_ipo_debt", "post_ipo_equity", "non_equity_assistance"}
EU = {"GBR", "DEU", "FRA", "NLD", "SWE", "ESP", "ITA", "CHE", "BEL", "AUT", "DNK", "FIN", "NOR",
      "IRL", "PRT", "POL", "CZE", "EST", "LTU", "LVA", "GRC", "HUN", "ROU", "LUX"}
NAEU = EU | {"USA", "CAN"}
K_PRE, K_POST = [-4, -3, -2, -1], [0, 1, 2, 3]
KS = K_PRE + K_POST

people = CTX.people[["uuid", "gender"]]
g_map = people[people["gender"].isin(["male", "female"])].set_index("uuid")["gender"]
rounds = CTX.rounds.dropna(subset=["announced_on", "org_uuid"]).copy()
rounds = rounds[~rounds["investment_type"].isin(EQ_EXCL)]
rounds["dt"] = pd.to_datetime(rounds["announced_on"], errors="coerce")
rounds = rounds.dropna(subset=["dt"])
inv = CTX.inv.dropna(subset=["funding_round_uuid", "investor_uuid"])
pt = CTX.partners.dropna(subset=["funding_round_uuid", "investor_uuid", "partner_uuid"])
jobs = CTX.jobs
vc_country = dict(zip(CTX.investors["uuid"], CTX.investors["country_code"]))

pv = inv.merge(rounds[["uuid", "org_uuid", "dt"]], left_on="funding_round_uuid", right_on="uuid")
fd = pv.groupby(["investor_uuid", "org_uuid"])["dt"].min().rename("fdt").reset_index()
_acq = CTX.acq.dropna(subset=["acquiree_uuid", "acquired_on"]); _ip = CTX.ipos.dropna(subset=["org_uuid", "went_public_on"])
_fe = pd.concat([pd.to_datetime(_acq["acquired_on"], errors="coerce").groupby(_acq["acquiree_uuid"]).min(), pd.to_datetime(_ip["went_public_on"], errors="coerce").groupby(_ip["org_uuid"]).min()], axis=1).min(axis=1)
_ex = fd["org_uuid"].map(_fe); fd = fd[~(_ex.notna() & (_ex <= fd["fdt"]))].copy()   # D067 population rule: no exit on/before the deal
fj = jobs[jobs["title"].fillna("").str.lower().str.contains("founder", regex=False)][
    ["person_uuid", "org_uuid"]].dropna()
fj["fg"] = fj["person_uuid"].map(g_map)
fj = fj[fj["fg"].notna()]
org_ff = (fj["fg"] == "female").groupby(fj["org_uuid"]).max()
fj_all = fj.groupby("org_uuid")["fg"].agg(lambda s: (s == "male").all())  # 전원 남성 (관측 창업자)
fd["ff"] = fd["org_uuid"].map(org_ff)
fd["allm"] = fd["org_uuid"].map(fj_all)
fd = fd[fd["ff"].notna()]
fd["ff"] = fd["ff"].astype(float)
fd["half"] = fd["fdt"].dt.year * 2 + (fd["fdt"].dt.month > 6).astype(int)
# 반기별 (V, half): ff 비중·판정가능 건수·전원남성 건수
vh = fd.groupby(["investor_uuid", "half"]).agg(ffs=("ff", "mean"), n=("ff", "size"),
                                               nallm=("allm", "sum")).reset_index()
vh_map = {(r.investor_uuid, r.half): (r.ffs, r.n, np.log1p(r.nallm)) for r in vh.itertuples()}

pa = pt.merge(rounds[["uuid", "dt"]], left_on="funding_round_uuid", right_on="uuid")
first_attr = pa.groupby(["partner_uuid", "investor_uuid"])["dt"].min().rename("fa")
pj = jobs.merge(pt[["partner_uuid", "investor_uuid"]].drop_duplicates(),
                left_on=["person_uuid", "org_uuid"], right_on=["partner_uuid", "investor_uuid"])
arr = pj[pj["started_on"].notna()].copy()
arr["t"] = pd.to_datetime(arr["started_on"], errors="coerce")
arr = arr.dropna(subset=["t"])
arr = arr[(arr["t"] >= "2012-01-01") & (arr["t"] <= "2023-10-31")]
arr = arr.sort_values("t").groupby(["partner_uuid", "investor_uuid"]).head(1)[
    ["partner_uuid", "investor_uuid", "t"]]
arr = arr.merge(first_attr, left_on=["partner_uuid", "investor_uuid"], right_index=True, how="left")
arr = arr[arr["fa"].notna() & (arr["fa"] >= arr["t"])]
arr["kind"] = "join"
dep = pj[pj["ended_on"].notna()].copy()
dep["t"] = pd.to_datetime(dep["ended_on"], errors="coerce")
dep = dep.dropna(subset=["t"])
dep = dep[(dep["t"] >= "2012-01-01") & (dep["t"] <= "2023-10-31")]
dep = dep.sort_values("t").groupby(["partner_uuid", "investor_uuid"]).tail(1)[
    ["partner_uuid", "investor_uuid", "t"]]
dep["kind"] = "exit"
ev = pd.concat([arr[["partner_uuid", "investor_uuid", "t", "kind"]], dep], ignore_index=True)
ev["pg"] = ev["partner_uuid"].map(g_map)
ev = ev[ev["pg"].notna()]
ev = ev[ev["investor_uuid"].map(vc_country).isin(NAEU)].copy()
ev["h0"] = ev["t"].dt.year * 2 + (ev["t"].dt.month > 6).astype(int)

# 사건별 상대반기 경로 (사전 4반기 중 ≥2, 사후 ≥2 관측 요구)
rows = []
for e in ev.itertuples():
    path, npath, plc = {}, {}, {}
    for k in KS:
        v = vh_map.get((e.investor_uuid, e.h0 + k))
        if v and v[1] >= 2:
            path[k], npath[k], plc[k] = v[0], v[1], v[2]
    if sum(1 for k in K_PRE if k in path) < 2 or sum(1 for k in K_POST if k in path) < 2:
        continue
    pre_m = np.mean([path[k] for k in K_PRE if k in path])
    rows.append({"kind": e.kind, "pg": e.pg, "inv": e.investor_uuid, "h0": e.h0,
                 "pre_ff": pre_m, "size": np.mean(list(npath.values())),
                 **{f"y{k}": path.get(k, np.nan) for k in KS},
                 **{f"p{k}": plc.get(k, np.nan) for k in KS}})
E = pd.DataFrame(rows)
# 오염: 같은 회사에 반대 성별 사건이 ±24m(4반기) 내
cont = set()
by_inv = {v: g for v, g in ev.groupby("investor_uuid")}
for i, e in E.iterrows():
    if e["pg"] != "male":
        continue  # 정정: 오염 제외는 남성 '대조' 사건에만 적용 (동결 사양 문언)
    g = by_inv.get(e["inv"])
    if g is not None and ((g["pg"] == "female") & (abs(g["h0"] - e["h0"]) <= 4)).any():
        cont.add(i)
E["contaminated"] = E.index.isin(cont)
# 재가중 셀: 사건 반기 3년 bin × 사전 ff 3분위 × 규모 3분위
E["cal"] = (E["h0"] // 6).astype(str)
E["ffq"] = pd.qcut(E["pre_ff"], 3, labels=False, duplicates="drop").astype(str)
E["szq"] = pd.qcut(E["size"], 3, labels=False, duplicates="drop").astype(str)
E["cellw"] = E["cal"] + "|" + E["ffq"] + "|" + E["szq"]


def weights(df):
    w = np.ones(len(df))
    for kind in ("join", "exit"):
        sub = df[df["kind"] == kind]
        nf = sub[sub["pg"] == "female"].groupby("cellw").size()
        nm = sub[sub["pg"] == "male"].groupby("cellw").size()
        ratio = (nf / nm).replace([np.inf], np.nan)
        mask = (df["kind"] == kind) & (df["pg"] == "male")
        w[mask.to_numpy()] = df.loc[mask, "cellw"].map(ratio).fillna(0).to_numpy()
    return w


def stack_joint(df, w=None, adjust=False, col="y", rng_=None):
    """결합 대비(영입−이탈)의 사후 평균 DiD; adjust=선형 사전추세 차감. 반환 (값, k경로 dict)."""
    r = rng_ or rng
    did_k = {}
    for k in KS:
        vals = {}
        for kind in ("join", "exit"):
            for pg in ("female", "male"):
                sub = df[(df["kind"] == kind) & (df["pg"] == pg)]
                y = (sub[f"{col}{k}"] - sub[[f"{col}{kk}" for kk in K_PRE]].mean(axis=1)).to_numpy()
                ww = (w[sub.index.to_numpy()] if w is not None else np.ones(len(sub)))
                m_ = np.isfinite(y) & np.isfinite(ww) & (ww > 0)
                vals[(kind, pg)] = np.average(y[m_], weights=ww[m_]) if m_.sum() >= 20 else np.nan
        did_k[k] = ((vals[("join", "female")] - vals[("join", "male")])
                    - (vals[("exit", "female")] - vals[("exit", "male")]))
    if adjust:
        kp = [k for k in K_PRE if np.isfinite(did_k.get(k, np.nan))]
        if len(kp) >= 3:
            x = np.array(kp, float)
            yv = np.array([did_k[k] for k in kp])
            sl = ((x - x.mean()) * (yv - yv.mean())).sum() / ((x - x.mean()) ** 2).sum()
            ic = yv.mean() - sl * x.mean()
            for k in KS:
                if np.isfinite(did_k.get(k, np.nan)):
                    did_k[k] = did_k[k] - (ic + sl * k)
    post = [did_k[k] for k in K_POST if np.isfinite(did_k.get(k, np.nan))]
    return (float(np.mean(post)) if post else np.nan), did_k


def boot(df, w=None, adjust=False, col="y", nb=NB):
    b0, path = stack_joint(df, w, adjust, col)
    keys = df.index.to_numpy()
    bs = []
    for _ in range(nb):
        pick = keys[rng.integers(0, len(keys), len(keys))]
        sub = df.loc[pick]
        sub.index = np.arange(len(sub))
        ww = None
        if w is not None:
            ww = weights(sub)
            ww = np.asarray(ww)
        sub2 = sub.copy()
        v, _ = stack_joint(sub2, ww, adjust, col)
        if np.isfinite(v):
            bs.append(v)
    return b0, qci(bs), path


E = E.reset_index(drop=True)
L0, ciL0, path0 = boot(E)
E1_ = E[~E["contaminated"]].reset_index(drop=True)
L1, ciL1, _ = boot(E1_)
w2 = weights(E1_)
L2, ciL2, path2 = boot(E1_, w=w2)
L3, ciL3, path3 = boot(E1_, w=w2, adjust=True)
# 파단 기울기: 조정 전(L2) 사후 평균이 0 이 되는 차등추세 기울기 = L2 / mean(K_POST 중심거리)
kbar = np.mean([k - np.mean(K_PRE) for k in K_POST])
mbar_star = L2 / kbar if kbar else float("nan")
# 위약: 전원 남성팀 log1p 건수 (L2 가중)
PL, ciPL, _ = boot(E1_, w=w2, col="p")
# 순열: 성별 라벨 (kind 내) 재배열 200
perm = []
for _ in range(200):
    Ep = E1_.copy()
    for kind in ("join", "exit"):
        idx = Ep.index[Ep["kind"] == kind].to_numpy()
        Ep.loc[idx, "pg"] = Ep.loc[rng.permutation(idx), "pg"].to_numpy()
    v, _ = stack_joint(Ep, weights(Ep))
    if np.isfinite(v):
        perm.append(v)
perm_p = float(np.mean(np.abs(perm) >= abs(L2))) if perm else float("nan")

n_f = int((E1_["pg"] == "female").sum())
upgraded = (not np.isnan(ciL3[0])) and (ciL3[0] > 0) and (ciPL[0] <= 0 <= ciPL[1])
status = "GO" if upgraded else "PARTIAL"
verdict = (f"사다리: L0 원 {L0*100:+.2f}pp {ciL0} → L1 오염제외 {L1*100:+.2f} {ciL1} → "
           f"L2 재가중 {L2*100:+.2f} {ciL2} → L3 추세조정 {L3*100:+.2f} {ciL3}; "
           f"파단 M̄*={mbar_star*100:+.3f}pp/반기; 위약(남성팀 건수) {PL:+.4f} {ciPL}; 순열 p={perm_p:.3f}"
           + (" — E3 인과 승격 (사전 조건 ① 충족)" if upgraded
              else " — 승격 실패: 연관 확정, M̄*·MDE 병기 (PB 외생 이탈이 잔여 경로)"))

emit("P001-04b", "재가중 스택 이벤트 스터디 — E3 승격 시도, 수리 사다리 (H9)", status,
     {"L0_raw": [round(L0 * 100, 2), ciL0], "L1_nocontam": [round(L1 * 100, 2), ciL1],
      "L2_reweighted": [round(L2 * 100, 2), ciL2], "L3_trendadj": [round(L3 * 100, 2), ciL3],
      "path_L2": {str(k): None if not np.isfinite(path2.get(k, np.nan)) else round(path2[k] * 100, 2)
                  for k in KS},
      "path_L3": {str(k): None if not np.isfinite(path3.get(k, np.nan)) else round(path3[k] * 100, 2)
                  for k in KS},
      "breakdown_slope_pp_per_half": round(mbar_star * 100, 3),
      "placebo_allmale_counts": [round(PL, 4), ciPL], "perm_p": perm_p,
      "n_events": int(len(E1_)), "n_female_events": n_f,
      "n_contaminated_excluded": int(E["contaminated"].sum()),
      "upgraded": bool(upgraded)},
     prediction="L0 사후 누적 ≥ +1pp; 재가중 후 사전 진폭 축소; L3 CI 폭 < I-82(7.2pp) — 0 배제가 승격 판정; 위약 청정",
     verdict=verdict, kill_met=False, n=n_f,
     extra={"stage": 3, "feeds": "E3 승격 판정 (ESTIMAND_CARD 조건 ①)", "slug": "stacked_event_fix",
            "inputs": "cores_v1 보조표(전체 신규 딜 분모 필요 — 문서화 예외) + jobs 사건"})
print("done")
