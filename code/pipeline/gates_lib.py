# -*- coding: utf-8 -*-
"""Stage-1 게이트 프리미티브 — 카드 유형별 처치 정의·커버리지·검정력 대리 계산.

모든 함수는 (metrics: dict, gates: list) 를 돌려준다. 날짜는 YYYY-MM-DD 문자열 사전순 비교.
카테고리 매칭은 category_list + category_groups_list 소문자 부분문자열 — Stage 1 존재성 판정용이며,
Stage 2 에서는 카드별 사전 등록 분류를 다시 고정한다.
"""
import pandas as pd

from gates import gate, power_grade


# ── 기본 마스크 ──────────────────────────────────────────────────────────────
def cat_mask(orgs, keywords):
    s = (orgs["category_list"].fillna("") + "|" + orgs["category_groups_list"].fillna("")).str.lower()
    m = pd.Series(False, index=orgs.index)
    for k in keywords:
        m |= s.str.contains(k, regex=False)
    return m


def in_window(col, t0, t1):
    return (col >= t0) & (col <= t1)


def rounds_view(ctx, countries=None, cats=None, t0=None, t1=None, types=None, states=None):
    r = ctx.rounds
    m = pd.Series(True, index=r.index)
    if countries:
        m &= r["country_code"].isin(countries)
    if states:
        m &= r["state_code"].isin(states)
    if t0:
        m &= in_window(r["announced_on"].fillna(""), t0, t1 or "9999")
    if types:
        m &= r["investment_type"].isin(types)
    r = r[m]
    if cats:
        orgs = ctx.orgs
        ok = set(orgs.loc[cat_mask(orgs, cats), "uuid"])
        r = r[r["org_uuid"].isin(ok)]
    return r


def investor_ids(ctx, patterns=None, types_contains=None, roles_contains=None):
    iv = ctx.investors
    m = pd.Series(True, index=iv.index)
    if patterns:
        nm = iv["name"].fillna("").str.lower()
        mm = pd.Series(False, index=iv.index)
        for p in patterns:
            mm |= nm.str.contains(p, regex=False)
        m &= mm
    if types_contains:
        m &= iv["investor_types"].fillna("").str.contains(types_contains, regex=False)
    if roles_contains:
        m &= iv["roles"].fillna("").str.contains(roles_contains, regex=False)
    return iv[m]


# ── 게이트 유형 ──────────────────────────────────────────────────────────────
def rounds_gate(ctx, treated_kw, min_rounds, pre_events, *, countries=None, t0=None, t1=None,
                types=None, states=None, pre_t0=None, pre_t1=None, extra_metrics=None):
    """처치 = 카테고리×국가×기간 라운드. 존재성(hard) + 사전기간 사건수(검정력 대리)."""
    tr = rounds_view(ctx, countries=countries, cats=treated_kw, t0=t0, t1=t1, types=types, states=states)
    pre = rounds_view(ctx, countries=countries, cats=treated_kw, t0=pre_t0, t1=pre_t1, types=types,
                      states=states) if pre_t0 else tr
    metrics = {"n_treated": int(len(tr)), "n_orgs": int(tr["org_uuid"].nunique()),
               "n_pre_events": int(len(pre)),
               "amt_coverage": float(tr["raised_amount_usd"].notna().mean()) if len(tr) else 0.0}
    if extra_metrics:
        metrics.update(extra_metrics(ctx, tr))
    gates = [gate("treated_rounds", len(tr), min_rounds, hard=True)] + power_grade(len(pre), *pre_events)
    return metrics, gates


def investor_exposure_gate(ctx, patterns, min_investors, min_rounds, *, t0=None, t1=None,
                           roles_contains=None, types_contains=None):
    """처치 = 특정 투자자군 참여 라운드 (SVB·크로스오버·SB·액셀 등 사전 등록 명단)."""
    ids = investor_ids(ctx, patterns, types_contains, roles_contains)
    inv = ctx.inv
    part = inv[inv["investor_uuid"].isin(set(ids["uuid"]))]
    r = ctx.rounds[ctx.rounds["uuid"].isin(set(part["funding_round_uuid"]))]
    if t0:
        r = r[in_window(r["announced_on"].fillna(""), t0, t1 or "9999")]
    metrics = {"n_investors_matched": int(len(ids)), "n_treated": int(len(r)),
               "n_orgs": int(r["org_uuid"].nunique()),
               "matched_names": sorted(ids["name"].str.lower().unique())[:20]}
    gates = [gate("investors_matched", len(ids), min_investors, hard=True),
             gate("treated_rounds", len(r), min_rounds, hard=True)] + power_grade(len(r))
    return metrics, gates


def partner_link_gate(ctx, min_partners, min_moves, sample_recall=None):
    """파트너-딜 귀속(282K)과 jobs 의 연결률: 파트너의 투자사 jobs 행 존재 + 이직(종료 후 타사 시작) 관측."""
    pt = ctx.partners
    jobs = ctx.jobs
    partner_set = set(pt["partner_uuid"].dropna())
    pj = jobs[jobs["person_uuid"].isin(partner_set)]
    at_investor = pj.merge(pt[["partner_uuid", "investor_uuid"]].drop_duplicates(),
                           left_on=["person_uuid", "org_uuid"], right_on=["partner_uuid", "investor_uuid"])
    ended = at_investor[at_investor["ended_on"].notna() & (at_investor["ended_on"] > "2005")]
    movers = ended["person_uuid"].nunique()
    link_rate = at_investor["person_uuid"].nunique() / max(len(partner_set), 1)
    metrics = {"n_partners": len(partner_set),
               "n_partner_job_rows": int(len(pj)),
               "n_partners_linked_to_firm": int(at_investor["person_uuid"].nunique()),
               "firm_link_rate": round(float(link_rate), 3),
               "n_treated": int(movers)}
    gates = [gate("partners_linked", at_investor["person_uuid"].nunique(), min_partners, hard=True),
             gate("partner_moves", movers, min_moves, hard=True),
             gate("firm_link_rate", link_rate, 0.25, hard=False)]
    return metrics, gates


def transition_gate(ctx, person_pool_fn, min_pool, min_transitions, describe):
    """사람 전이 설계(스핀아웃·실패 후 경력·재창업): 풀 크기 + 전이 관측 수."""
    pool, transitions, extra = person_pool_fn(ctx)
    metrics = {"pool_desc": describe, "n_pool": int(pool), "n_treated": int(transitions)}
    metrics.update(extra or {})
    gates = [gate("person_pool", pool, min_pool, hard=True),
             gate("transitions_observed", transitions, min_transitions, hard=True)] \
        + power_grade(transitions)
    return metrics, gates


def coverage_gate(ctx, table, col, subset_fn, min_share, min_n, label):
    df = getattr(ctx, table)
    if subset_fn:
        df = subset_fn(df, ctx)
    share = float(df[col].notna().mean()) if len(df) else 0.0
    metrics = {f"{label}_n": int(len(df)), f"{label}_coverage": round(share, 3), "n_treated": int(len(df))}
    gates = [gate(f"{label}_rows", len(df), min_n, hard=True),
             gate(f"{label}_coverage", share, min_share, hard=True)]
    return metrics, gates


def merge_gates(*parts):
    """여러 프리미티브 결과 결합: metrics 는 접두어 없이 병합(선순위 우선), gates 는 연결."""
    metrics, gates = {}, []
    for m, g in parts:
        for k, v in m.items():
            metrics.setdefault(k, v)
        gates += g
    return metrics, gates
