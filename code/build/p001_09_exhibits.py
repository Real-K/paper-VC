# -*- coding: utf-8 -*-
"""p001_09 전시물 렌더 v2 (W5 v2, 2026-09-04) — Table 1–9 + Figure 1–3, 전부 산출 JSON 에서.

v2 변경: T3=P001-10 정본 사다리(+가법 행 P001-15), T4=해저드 주 사양(P001-12)+RW(P001-13)
+순열(P001-14), T6=영입 마진 중심 재구성(P001-11·14b; 구 집계판은 robustness), T7+커리어
(P001-18b), T8+재가중·다수여성(P001-17)+S&S(P001-19), T9+살리언스·라벨(P001-16), 상관 단위
버그 수정(ci 는 pp 전용 — 상관·로그 값은 raw 표시). 수기 편집 금지 — 이 스크립트가 유일 경로.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
A = H = os.environ.get("P001_ARTIFACTS", os.path.join(REPO, "artifacts"))          # aggregate result artifacts (JSON)
OUT_T = os.environ.get("P001_TABLES", os.path.join(REPO, "figures", "tables", "components"))      # regenerated table components (p001_09d_compose_v9.py writes the final tables next to them)
OUT_F = os.environ.get("P001_FIGURES", os.path.join(REPO, "figures"))               # regenerated figures
os.makedirs(OUT_T, exist_ok=True)
os.makedirs(OUT_F, exist_ok=True)


def j(base, name):
    return json.load(open(os.path.join(base, name), encoding="utf-8"))


def w(name, text):
    open(os.path.join(OUT_T, name), "w", encoding="utf-8").write(text)
    print("table:", name)


def pp(c):
    return f"[{c[0]*100:+.2f}, {c[1]*100:+.2f}]"


def raw(c, d=3):
    return f"[{c[0]:+.{d}f}, {c[1]:+.{d}f}]"


i73, i76, i78, i80, i81, i82 = (j(H, f"I{n}.json") for n in (73, 76, 78, 80, 81, 82))
p2, p3, p4b, p5, p6, p7, p8 = (j(A, f"P001{n}.json") for n in ("02", "03", "04b", "05", "06", "07", "08"))
p10, p11, p12, p13, p14, p14b = (j(A, f"P001{n}.json") for n in ("10", "11", "12", "13", "14", "14b"))
p15, p16, p17, p18b, p19 = (j(A, f"P001{n}.json") for n in ("15", "16", "17", "18b", "19"))
p23, p24, p25, p26, p27, p28, p29, p30 = (j(A, f"P001{n}.json") for n in ("23", "24", "25", "26", "27", "28", "29", "30"))
p31, p32, p33, p34, p35, p36, p37 = (j(A, f"P001{n}.json") for n in ("31", "32", "33", "34", "35", "36", "37"))
e31, e32, e33, e34, e35, e36, e37 = (x["estimates"] for x in (p31, p32, p33, p34, p35, p36, p37))
fxA, fxB = e33["A_exit3_exit3"], e33["B_exit6_exit3"]
p38, p39 = (j(A, f"P001{n}.json") for n in ("38", "39"))
e38, e39 = p38["estimates"], p39["estimates"]
fxD, fxJ = e38["D_exante_window"], e39["C_fixed_horizon"]
p40, p41 = (j(A, f"P001{n}.json") for n in ("40", "41"))
e40, e41 = p40["estimates"], p41["estimates"]
q40n, q40g, q40s = e40["NAEU"]["pluscat"], e40["GLOBAL"]["pluscat"], e40["NAEU"]["plusstage"]
p42, p43, p44, p45, p46, p47, p48, p49, p50, p51, p52, p54, p55, p56, p58, p59 = (j(A, f"P001{n}.json") for n in ("42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "54", "55", "56", "58", "59"))
e42, e43, e44, e45, e46, e47, e48, e49, e50, e51, e52, e54, e55, e56, e58, e59 = (x["estimates"] for x in (p42, p43, p44, p45, p46, p47, p48, p49, p50, p51, p52, p54, p55, p56, p58, p59))
p57, p60, p61, p62, p63 = (j(A, f"P001{n}.json") for n in ("57", "60", "61", "62", "63"))
e57, e60, e61, e62, e63 = p57["estimates"], p60["estimates"], p61["estimates"], p62["estimates"], p63["estimates"]
p0 = j(A, "P00100.json")["estimates"]  # sample counts fixed by p001_00 (no microdata needed to render the exhibits)
n_deals, n_naeu = p0["n_deals"], p0["n_naeu"]

e73 = i73["estimates"]
r4 = p8["estimates"]["r4_missingness"]
w("table1.md", f"""# Table 1. Sample and measurement coverage
| | |
|---|---|
| Partner-attributed deals with observable founder gender (global) | {n_deals:,} |
| — excluded at construction (founder gender unobservable) | 34,457 |
| — North America + Europe (primary sample) | {n_naeu:,} |
| Partner gender observed (share of attributed deals) | {e73['cov_partner_gender']*100:.1f}% |
| Founder gender determinable (share of funded companies) | {e73['cov_founder_gender']*100:.1f}% |
| Female-founded (FF) share of deals | {e73['base_ff']*100:.1f}% |
| Female-partner (FP) share of deals | {e73['base_fp']*100:.1f}% |
| Determinability selection: US share diff (det − undet) | {r4['us_diff_pp']:+.1f}pp |
| — early-stage share diff | {r4['early_diff_pp']:+.1f}pp |
| — mean vintage diff (years) | {r4['year_diff']:+.2f} |

*Sources: sample_v2.parquet (sha256₁₆ 3acfb38d12559791; P001-00); I-73; P001-08; P001-63. Population: partner-attributed equity deals, 2010-01 to 2023-10, with observable founder gender, of companies with no acquisition or IPO recorded on or before the round date (Appendix IA.1).*
""")

L = p2["estimates"]["ladder"]
ms = p2["estimates"]["mediator_share"]
rev = p14["estimates"]["ladder_reverse"]
br = p14["estimates"]["share_bracket"]
w("table2.md", f"""# Table 2. Partner–founder gender matching: decomposition ladder (NA+EU)
| Cell specification | FP coefficient (pp) | 95% CI |
|---|---|---|
| Firm × year | {L['L0_invyear'][0]*100:+.2f} | {pp(L['L0_invyear'][1])} |
| + sector | {L['L1_pluscat'][0]*100:+.2f} | {pp(L['L1_pluscat'][1])} |
| + stage (full cells) | {L['L2_plusstage'][0]*100:+.2f} | {pp(L['L2_plusstage'][1])} |
| Reverse order: + stage first | {rev['stage_first'][0]*100:+.2f} | {pp(rev['stage_first'][1])} |
| NA, full cells | {p2['estimates']['na_fullcell'][0]*100:+.2f} | {pp(p2['estimates']['na_fullcell'][1])} |
| EU, full cells | {p2['estimates']['eu_fullcell'][0]*100:+.2f} | {pp(p2['estimates']['eu_fullcell'][1])} |
| NA − EU difference | {p2['estimates']['h8_diff'][0]*100:+.2f} | {pp(p2['estimates']['h8_diff'][1])} |

Composition shares (order-bracketed): total {br['total']*100:.1f}%; sector {min(br['sector'])*100:.0f}–{max(br['sector'])*100:.0f}%; stage {min(br['stage'])*100:.0f}–{max(br['stage'])*100:.0f}%.

*Outcome: deal is female-founded. n = {L['L0_invyear'][2]:,}. Investor-cluster bootstrap. Within-cell permutation of the raw association: p < 0.005 (I-74). Sources: P001-02, P001-14.*
""")

lad = p10["estimates"]["ladder"]
add = p15["estimates"]
def lrow(scope, key):
    v = lad[scope][key]
    return f"{v[0]*100:+.2f} | {pp(v[1])}"
w("table4.md", f"""# Table 4. Where the exit gap lives: female-founded deals
## Panel A. Exit by sample end, deals through October 2017: the location ladder
| Comparison | Global | 95% CI | NA+EU | 95% CI |
|---|---|---|---|---|
| Year effects only | {lrow('GLOBAL','year')} | {lrow('NAEU','year')} |
| Firm × year | {lrow('GLOBAL','invyear')} | {lrow('NAEU','invyear')} |
| Additive firm+year+sector+stage | {add['GLOBAL']['exit_additive'][0]*100:+.2f} | {pp(add['GLOBAL']['exit_additive'][1])} | {add['NAEU']['exit_additive'][0]*100:+.2f} | {pp(add['NAEU']['exit_additive'][1])} |
| **Firm × year × sector (peer comparison)** | **{lrow('GLOBAL','pluscat')}** | {lrow('NAEU','pluscat')} |
| + stage | {lrow('GLOBAL','plusstage')} | {lrow('NAEU','plusstage')} |


## Panel B. Fixed 36-month exit horizon, deals through 2020-10 (NA+EU): the cross-deal comparisons as the estimator
| Cell definition | Mixed cells / deals | Multi-round (cross-deal) cells / deals | Cells with exit variation | Share of Σx̃² from single-round cells (d) | β, all cells (pp) | β, cross-deal cells (pp) | 95% CI | MDE80 (pp; sd) | Placebo 95th pct (pp) |
|---|---|---|---|---|---|---|---|---|---|
| {e55['A_exit3_2020']['cell_cat']['label']} | {e55['A_exit3_2020']['cell_cat']['n_mixed_cells']:,} / {e55['A_exit3_2020']['cell_cat']['n_deals_mixed']:,} | {e55['A_exit3_2020']['cell_cat']['n_multi_round_cells']:,} / {e55['A_exit3_2020']['cell_cat']['n_deals_multi']:,} | {e55['A_exit3_2020']['cell_cat']['n_cells_var_pos']} | {e55['A_exit3_2020']['cell_cat']['dilution_share_sxx_single_round']:.2f} | {e55['A_exit3_2020']['cell_cat']['beta_full_pp']:+.2f} | {(f"{e55['A_exit3_2020']['cell_cat']['beta_multi_pp']:+.2f}" if e55['A_exit3_2020']['cell_cat'].get('beta_multi_pp') is not None else 'not identified')} | {(raw(e55['A_exit3_2020']['cell_cat']['ci_multi_pp'], 2) if e55['A_exit3_2020']['cell_cat'].get('beta_multi_pp') is not None else '—')} | {(f"{e55['A_exit3_2020']['cell_cat']['mde80_multi_pp']:.2f}; {e55['A_exit3_2020']['cell_cat']['mde80_multi_sd']:.2f}" if e55['A_exit3_2020']['cell_cat'].get('beta_multi_pp') is not None else '—')} | {(e55['A_exit3_2020']['cell_cat']['placebo_p95_multi_pp'] if e55['A_exit3_2020']['cell_cat'].get('beta_multi_pp') is not None else '—')} |
| {e55['A_exit3_2020']['cell_stage']['label']} | {e55['A_exit3_2020']['cell_stage']['n_mixed_cells']:,} / {e55['A_exit3_2020']['cell_stage']['n_deals_mixed']:,} | {e55['A_exit3_2020']['cell_stage']['n_multi_round_cells']:,} / {e55['A_exit3_2020']['cell_stage']['n_deals_multi']:,} | {e55['A_exit3_2020']['cell_stage']['n_cells_var_pos']} | {e55['A_exit3_2020']['cell_stage']['dilution_share_sxx_single_round']:.2f} | {e55['A_exit3_2020']['cell_stage']['beta_full_pp']:+.2f} | {(f"{e55['A_exit3_2020']['cell_stage']['beta_multi_pp']:+.2f}" if e55['A_exit3_2020']['cell_stage'].get('beta_multi_pp') is not None else 'not identified')} | {(raw(e55['A_exit3_2020']['cell_stage']['ci_multi_pp'], 2) if e55['A_exit3_2020']['cell_stage'].get('beta_multi_pp') is not None else '—')} | {(f"{e55['A_exit3_2020']['cell_stage']['mde80_multi_pp']:.2f}; {e55['A_exit3_2020']['cell_stage']['mde80_multi_sd']:.2f}" if e55['A_exit3_2020']['cell_stage'].get('beta_multi_pp') is not None else '—')} | {(e55['A_exit3_2020']['cell_stage']['placebo_p95_multi_pp'] if e55['A_exit3_2020']['cell_stage'].get('beta_multi_pp') is not None else '—')} |
| {e55['A_exit3_2020']['c2']['label']} | {e55['A_exit3_2020']['c2']['n_mixed_cells']:,} / {e55['A_exit3_2020']['c2']['n_deals_mixed']:,} | {e55['A_exit3_2020']['c2']['n_multi_round_cells']:,} / {e55['A_exit3_2020']['c2']['n_deals_multi']:,} | {e55['A_exit3_2020']['c2']['n_cells_var_pos']} | {e55['A_exit3_2020']['c2']['dilution_share_sxx_single_round']:.2f} | {e55['A_exit3_2020']['c2']['beta_full_pp']:+.2f} | {(f"{e55['A_exit3_2020']['c2']['beta_multi_pp']:+.2f}" if e55['A_exit3_2020']['c2'].get('beta_multi_pp') is not None else 'not identified')} | {(raw(e55['A_exit3_2020']['c2']['ci_multi_pp'], 2) if e55['A_exit3_2020']['c2'].get('beta_multi_pp') is not None else '—')} | {(f"{e55['A_exit3_2020']['c2']['mde80_multi_pp']:.2f}; {e55['A_exit3_2020']['c2']['mde80_multi_sd']:.2f}" if e55['A_exit3_2020']['c2'].get('beta_multi_pp') is not None else '—')} | {(e55['A_exit3_2020']['c2']['placebo_p95_multi_pp'] if e55['A_exit3_2020']['c2'].get('beta_multi_pp') is not None else '—')} |
| {e55['A_exit3_2020']['c3']['label']} | {e55['A_exit3_2020']['c3']['n_mixed_cells']:,} / {e55['A_exit3_2020']['c3']['n_deals_mixed']:,} | {e55['A_exit3_2020']['c3']['n_multi_round_cells']:,} / {e55['A_exit3_2020']['c3']['n_deals_multi']:,} | {e55['A_exit3_2020']['c3']['n_cells_var_pos']} | {e55['A_exit3_2020']['c3']['dilution_share_sxx_single_round']:.2f} | {e55['A_exit3_2020']['c3']['beta_full_pp']:+.2f} | {(f"{e55['A_exit3_2020']['c3']['beta_multi_pp']:+.2f}" if e55['A_exit3_2020']['c3'].get('beta_multi_pp') is not None else 'not identified')} | {(raw(e55['A_exit3_2020']['c3']['ci_multi_pp'], 2) if e55['A_exit3_2020']['c3'].get('beta_multi_pp') is not None else '—')} | {(f"{e55['A_exit3_2020']['c3']['mde80_multi_pp']:.2f}; {e55['A_exit3_2020']['c3']['mde80_multi_sd']:.2f}" if e55['A_exit3_2020']['c3'].get('beta_multi_pp') is not None else '—')} | {(e55['A_exit3_2020']['c3']['placebo_p95_multi_pp'] if e55['A_exit3_2020']['c3'].get('beta_multi_pp') is not None else '—')} |
| {e55['A_exit3_2020']['cfs']['label']} | {e55['A_exit3_2020']['cfs']['n_mixed_cells']:,} / {e55['A_exit3_2020']['cfs']['n_deals_mixed']:,} | {e55['A_exit3_2020']['cfs']['n_multi_round_cells']:,} / {e55['A_exit3_2020']['cfs']['n_deals_multi']:,} | {e55['A_exit3_2020']['cfs']['n_cells_var_pos']} | {e55['A_exit3_2020']['cfs']['dilution_share_sxx_single_round']:.2f} | {e55['A_exit3_2020']['cfs']['beta_full_pp']:+.2f} | {(f"{e55['A_exit3_2020']['cfs']['beta_multi_pp']:+.2f}" if e55['A_exit3_2020']['cfs'].get('beta_multi_pp') is not None else 'not identified')} | {(raw(e55['A_exit3_2020']['cfs']['ci_multi_pp'], 2) if e55['A_exit3_2020']['cfs'].get('beta_multi_pp') is not None else '—')} | {(f"{e55['A_exit3_2020']['cfs']['mde80_multi_pp']:.2f}; {e55['A_exit3_2020']['cfs']['mde80_multi_sd']:.2f}" if e55['A_exit3_2020']['cfs'].get('beta_multi_pp') is not None else '—')} | {(e55['A_exit3_2020']['cfs']['placebo_p95_multi_pp'] if e55['A_exit3_2020']['cfs'].get('beta_multi_pp') is not None else '—')} |
| Deal-level coding, firm × year × sector: female-only vs male-only attributed deals (mixed-attribution deals excluded) | — | {e55['D_deal_level_coding']['cell_cat']['n_cells_fo_var']:,} cells / {e55['D_deal_level_coding']['cell_cat']['n_deals']:,} deals | {e55['D_deal_level_coding']['cell_cat']['n_cells_exit_var_pos']} | 0 by construction | — | {e55['D_deal_level_coding']['cell_cat']['beta_fo_vs_mo_pp']:+.2f} | {raw(e55['D_deal_level_coding']['cell_cat']['ci_pp'], 2)} | {e55['D_deal_level_coding']['cell_cat']['mde80_pp']:.2f} | {e55['D_deal_level_coding']['cell_cat']['placebo_p95_pp']} |
| Reference: sample-end horizon, deals through 2017-10, firm × year × sector (canonical run; Appendix Table IA.2, Panel E) | {e49['NAEU']['cell_cat']['n_mixed_cells']:,} / {e49['NAEU']['cell_cat']['n_deals_mixed']:,} | {e49['NAEU']['cell_cat']['n_multi_round_cells']:,} / {e49['NAEU']['cell_cat']['n_deals_multi']:,} | {e49['NAEU']['cell_cat']['n_cells_exit_var_pos']} | {e49['NAEU']['cell_cat']['dilution_share_sxx_single_round']:.2f} | {e49['NAEU']['cell_cat']['beta_full_pp']:+.2f} | {e49['NAEU']['cell_cat']['beta_multi_exit_ever_pp']:+.2f} | {raw(e49['NAEU']['cell_cat']['ci_multi_exit_ever_pp'], 2)} | {e49['NAEU']['cell_cat']['mde_multi_exit_ever_pp']:.2f}; — | {e49['NAEU']['cell_cat']['placebo_p95_multi_exit_ever_pp']} |

*Panel B: exit within 36 months of the deal; FF deals {e55['A_exit3_2020']['n_ff_deals']:,}, base rate {e55['A_exit3_2020']['base_y']:.3f}. Σx̃² is the within-cell estimator's identifying variance and d the share of it contributed by cells whose partner rows all belong to one round (co-attributed pairs), so that the all-cells coefficient equals the cross-deal coefficient times (1 − d). MDE80 = minimum detectable effect at 80 percent power. β on cross-deal cells is the within-cell estimator restricted to mixed cells whose partner rows span at least two rounds; investor-firm cluster bootstrap (500); placebo = 95th percentile of |β| under within-cell reassignment of partner gender (400). The firm × sector row adds additive year effects (two-way demeaning); with additive effects the identity β_all = (1 − d)·β_cross-deal holds only approximately, which is why that row's all-cells and cross-deal coefficients do not satisfy it exactly. The reference row repeats the canonical sample-end estimates of P001-49 so that the same specification carries one set of numbers throughout the paper. Sources: P001-55, P001-49.*

*Deals through 2017-10; exit = acquisition or IPO by sample end. n = {lad['GLOBAL']['pluscat'][2]:,} (global) / {lad['NAEU']['pluscat'][2]:,} (NA+EU). The deficit is detected only in the interacted firm–year–sector comparison; the coarser intervals contain both zero and the peer-comparison estimate, and only the + stage row's interval excludes it. All rows are estimated on one sample and one bootstrap draw. Identifying variation of the peer-comparison row (Appendix Table IA.2, Panel D): {q40n['n_mixed_cells']} NA+EU cells contain both a female- and a male-partner female-founded deal ({q40n['n_deals_mixed']} deals, {q40n['share_deals_mixed']*100:.1f} percent of the sample; global {q40g['n_mixed_cells']} cells, {q40g['n_deals_mixed']} deals). Base exit rate among female-founded deals, global: {i78['estimates']['exit_ever']['base_ff']*100:.1f} percent (I-78). Sources: P001-10 (ladder), P001-15 (additive row), P001-40 (identifying variation), I-78 (base rate).*
""")

hz = p12["estimates"]
bat = hz["battery_adj"]
rw_ = p13["estimates"]["rw_adjusted_p"]
perm2 = p14["estimates"]["e2_perm"]
rows4 = "\n".join(f"| {k} (adj.) | {v[0]:+.2f} | {pp(v[1])} | RW p = {rw_[k]} |"
                  for k, v in bat.items())
w("table5.md", f"""# Table 5. Within-partner outcome test and covariate-adjusted battery (NA+EU)
## Panel A. Covariate-adjusted exit hazard on the Table 4 cells (firm × year × sector × stage × duration effects; deal controls)
| | Estimate | 95% CI |
|---|---|---|
| Annual exit hazard gap (pp/yr) | {hz['hazard_gap_per_yr'][0]:+.3f} | {raw([c*100 for c in hz['hazard_gap_per_yr'][1]],2)} |
| Baseline hazard (%/yr) | {hz['hazard_base']*100:.2f} | interval within ±25% of baseline: {'yes' if hz['hazard_equiv_25pct'] else 'no'} |
| Same gap, multi-round cell–year groups only (pp/yr); MDE80 | {e50['B_hazard_gap']['multi_round_cells']['coef_pp']:+.3f}; {e50['B_hazard_gap']['multi_round_cells']['mde80_pp']:.2f} | {raw(e50['B_hazard_gap']['multi_round_cells']['ci95_pp'],2)}; within ±25% of baseline: {'yes' if e50['B_hazard_gap']['multi_round_cells']['within_quarter_of_base'] else 'no'} |
| Identifying base: cell–year groups with female-partner variation; share single-round co-attributions; groups with exit variation | {e50['A_cells']['n_mixed_cells']:,}; {e50['A_cells']['share_single_round_cells']:.2f}; {e50['A_cells']['n_cells_outcome_var_pos']} | — |

## Panel B. Within-partner outcome test: female-founded vs other deals of the same partner, by partner gender (36-month exit net of the year × sector × stage market mean; deals through 2020-10). β_int is the difference between female and male partners' own female-founded − other gaps
| Specification | β_int: female partners' extra FF gap (pp) | 95% CI | MDE80 (pp) | β_int in sd of the benchmarked outcome | inside ±5 pp | β_FF: male partners' own FF − other gap (pp) | 95% CI | n deals / partners (women) |
|---|---|---|---|---|---|---|---|---|
| Partner fixed effects, deal controls; partner-cluster bootstrap | {e54['A_exit3']['main_partnerFE_clPartner']['ffp']['coef']*100:+.2f} | {pp(e54['A_exit3']['main_partnerFE_clPartner']['ffp']['ci95'])} | {e54['A_exit3']['main_partnerFE_clPartner']['ffp']['mde80']*100:.2f} | {e54['A_exit3']['main_partnerFE_clPartner']['ffp']['beta_std']:+.3f} | {'yes' if e54['A_exit3']['main_partnerFE_clPartner']['ffp']['within_pm0.05'] else 'no'} | {e54['A_exit3']['main_partnerFE_clPartner']['ff']['coef']*100:+.2f} | {pp(e54['A_exit3']['main_partnerFE_clPartner']['ff']['ci95'])} | {e54['A_exit3']['main_partnerFE_clPartner']['n']:,} / {e54['A_exit3']['main_partnerFE_clPartner']['n_partners']:,} ({e54['A_exit3']['main_partnerFE_clPartner']['n_female_partners']}) |
| Same; investor-firm clusters | {e54['A_exit3']['main_partnerFE_clFirm']['ffp']['coef']*100:+.2f} | {pp(e54['A_exit3']['main_partnerFE_clFirm']['ffp']['ci95'])} | {e54['A_exit3']['main_partnerFE_clFirm']['ffp']['mde80']*100:.2f} | {e54['A_exit3']['main_partnerFE_clFirm']['ffp']['beta_std']:+.3f} | {'yes' if e54['A_exit3']['main_partnerFE_clFirm']['ffp']['within_pm0.05'] else 'no'} | {e54['A_exit3']['main_partnerFE_clFirm']['ff']['coef']*100:+.2f} | {pp(e54['A_exit3']['main_partnerFE_clFirm']['ff']['ci95'])} | {e54['A_exit3']['main_partnerFE_clFirm']['n']:,} / {e54['A_exit3']['main_partnerFE_clFirm']['n_partners']:,} ({e54['A_exit3']['main_partnerFE_clFirm']['n_female_partners']}) |
| Firm × year fixed effects instead of partner effects (partner gender included) | {e54['A_exit3']['V1_firmYearFE']['ffp']['coef']*100:+.2f} | {pp(e54['A_exit3']['V1_firmYearFE']['ffp']['ci95'])} | {e54['A_exit3']['V1_firmYearFE']['ffp']['mde80']*100:.2f} | {e54['A_exit3']['V1_firmYearFE']['ffp']['beta_std']:+.3f} | {'yes' if e54['A_exit3']['V1_firmYearFE']['ffp']['within_pm0.05'] else 'no'} | {e54['A_exit3']['V1_firmYearFE']['ff']['coef']*100:+.2f} | {pp(e54['A_exit3']['V1_firmYearFE']['ff']['ci95'])} | {e54['A_exit3']['V1_firmYearFE']['n']:,} / {e54['A_exit3']['V1_firmYearFE']['n_partners']:,} ({e54['A_exit3']['V1_firmYearFE']['n_female_partners']}) |
| Partner × two-year fixed effects | {e54['A_exit3']['V2_partner2yFE']['ffp']['coef']*100:+.2f} | {pp(e54['A_exit3']['V2_partner2yFE']['ffp']['ci95'])} | {e54['A_exit3']['V2_partner2yFE']['ffp']['mde80']*100:.2f} | {e54['A_exit3']['V2_partner2yFE']['ffp']['beta_std']:+.3f} | {'yes' if e54['A_exit3']['V2_partner2yFE']['ffp']['within_pm0.05'] else 'no'} | {e54['A_exit3']['V2_partner2yFE']['ff']['coef']*100:+.2f} | {pp(e54['A_exit3']['V2_partner2yFE']['ff']['ci95'])} | {e54['A_exit3']['V2_partner2yFE']['n']:,} / {e54['A_exit3']['V2_partner2yFE']['n_partners']:,} ({e54['A_exit3']['V2_partner2yFE']['n_female_partners']}) |
| Partners with ≥ 5 deals | {e54['A_exit3']['V3_partners_ge5']['ffp']['coef']*100:+.2f} | {pp(e54['A_exit3']['V3_partners_ge5']['ffp']['ci95'])} | {e54['A_exit3']['V3_partners_ge5']['ffp']['mde80']*100:.2f} | {e54['A_exit3']['V3_partners_ge5']['ffp']['beta_std']:+.3f} | {'yes' if e54['A_exit3']['V3_partners_ge5']['ffp']['within_pm0.05'] else 'no'} | {e54['A_exit3']['V3_partners_ge5']['ff']['coef']*100:+.2f} | {pp(e54['A_exit3']['V3_partners_ge5']['ff']['ci95'])} | {e54['A_exit3']['V3_partners_ge5']['n']:,} / {e54['A_exit3']['V3_partners_ge5']['n_partners']:,} ({e54['A_exit3']['V3_partners_ge5']['n_female_partners']}) |
| Vintages 2015 and later | {e54['A_exit3']['V4_2015plus']['ffp']['coef']*100:+.2f} | {pp(e54['A_exit3']['V4_2015plus']['ffp']['ci95'])} | {e54['A_exit3']['V4_2015plus']['ffp']['mde80']*100:.2f} | {e54['A_exit3']['V4_2015plus']['ffp']['beta_std']:+.3f} | {'yes' if e54['A_exit3']['V4_2015plus']['ffp']['within_pm0.05'] else 'no'} | {e54['A_exit3']['V4_2015plus']['ff']['coef']*100:+.2f} | {pp(e54['A_exit3']['V4_2015plus']['ff']['ci95'])} | {e54['A_exit3']['V4_2015plus']['n']:,} / {e54['A_exit3']['V4_2015plus']['n_partners']:,} ({e54['A_exit3']['V4_2015plus']['n_female_partners']}) |
| + company characteristics (Crunchbase profile values; see note) | {e54['A_exit3']['V5_company_controls']['ffp']['coef']*100:+.2f} | {pp(e54['A_exit3']['V5_company_controls']['ffp']['ci95'])} | {e54['A_exit3']['V5_company_controls']['ffp']['mde80']*100:.2f} | {e54['A_exit3']['V5_company_controls']['ffp']['beta_std']:+.3f} | {'yes' if e54['A_exit3']['V5_company_controls']['ffp']['within_pm0.05'] else 'no'} | {e54['A_exit3']['V5_company_controls']['ff']['coef']*100:+.2f} | {pp(e54['A_exit3']['V5_company_controls']['ff']['ci95'])} | {e54['A_exit3']['V5_company_controls']['n']:,} / {e54['A_exit3']['V5_company_controls']['n_partners']:,} ({e54['A_exit3']['V5_company_controls']['n_female_partners']}) |
| + prior patent applications (any before the deal; log count; assignee-match indicator, which is not pre-deal and absorbs unmatched zeros) | {e58['P3_patents']['within_partner_exit3']['patents']['ffp']['coef']*100:+.2f} | {pp(e58['P3_patents']['within_partner_exit3']['patents']['ffp']['ci95'])} | {e58['P3_patents']['within_partner_exit3']['patents']['ffp']['mde80']*100:.2f} | {e58['P3_patents']['within_partner_exit3']['patents']['ffp']['beta_std']:+.3f} | {'yes' if e58['P3_patents']['within_partner_exit3']['patents']['ffp']['within_pm0.05'] else 'no'} | {e58['P3_patents']['within_partner_exit3']['patents']['ff']['coef']*100:+.2f} | {pp(e58['P3_patents']['within_partner_exit3']['patents']['ff']['ci95'])} | {e58['P3_patents']['within_partner_exit3']['patents']['n']:,} / — (any prior patent: {e58['P3_patents']['within_partner_exit3']['patents']['any_patent_before']['coef']*100:+.2f} pp {pp(e58['P3_patents']['within_partner_exit3']['patents']['any_patent_before']['ci95'])}) |
| Follow-on financing within 36 months (deals through 2020-10) | {e54['B_fon']['main_partnerFE_clPartner']['ffp']['coef']*100:+.2f} | {pp(e54['B_fon']['main_partnerFE_clPartner']['ffp']['ci95'])} | {e54['B_fon']['main_partnerFE_clPartner']['ffp']['mde80']*100:.2f} | {e54['B_fon']['main_partnerFE_clPartner']['ffp']['beta_std']:+.3f} | {'yes' if e54['B_fon']['main_partnerFE_clPartner']['ffp']['within_pm0.05'] else 'no'} | {e54['B_fon']['main_partnerFE_clPartner']['ff']['coef']*100:+.2f} | {pp(e54['B_fon']['main_partnerFE_clPartner']['ff']['ci95'])} | {e54['B_fon']['main_partnerFE_clPartner']['n']:,} / {e54['B_fon']['main_partnerFE_clPartner']['n_partners']:,} ({e54['B_fon']['main_partnerFE_clPartner']['n_female_partners']}) |
| Exit by sample end (deals through 2017-10) | {e54['C_exit_ever']['main_partnerFE_clPartner']['ffp']['coef']*100:+.2f} | {pp(e54['C_exit_ever']['main_partnerFE_clPartner']['ffp']['ci95'])} | {e54['C_exit_ever']['main_partnerFE_clPartner']['ffp']['mde80']*100:.2f} | {e54['C_exit_ever']['main_partnerFE_clPartner']['ffp']['beta_std']:+.3f} | {'yes' if e54['C_exit_ever']['main_partnerFE_clPartner']['ffp']['within_pm0.05'] else 'no'} | {e54['C_exit_ever']['main_partnerFE_clPartner']['ff']['coef']*100:+.2f} | {pp(e54['C_exit_ever']['main_partnerFE_clPartner']['ff']['ci95'])} | {e54['C_exit_ever']['main_partnerFE_clPartner']['n']:,} / {e54['C_exit_ever']['main_partnerFE_clPartner']['n_partners']:,} ({e54['C_exit_ever']['main_partnerFE_clPartner']['n_female_partners']}) |
| &nbsp;&nbsp;vintages 2010–14 | {e59['A_vintage_horizon']['exit_ever_2017']['2010-14']['ffp']['coef']*100:+.2f} | {pp(e59['A_vintage_horizon']['exit_ever_2017']['2010-14']['ffp']['ci95'])} | {e59['A_vintage_horizon']['exit_ever_2017']['2010-14']['ffp']['mde80']*100:.2f} | {e59['A_vintage_horizon']['exit_ever_2017']['2010-14']['ffp']['beta_std']:+.3f} | {'yes' if e59['A_vintage_horizon']['exit_ever_2017']['2010-14']['ffp']['within_pm0.05'] else 'no'} | {e59['A_vintage_horizon']['exit_ever_2017']['2010-14']['ff']['coef']*100:+.2f} | {pp(e59['A_vintage_horizon']['exit_ever_2017']['2010-14']['ff']['ci95'])} | {e59['A_vintage_horizon']['exit_ever_2017']['2010-14']['n']:,} / {e59['A_vintage_horizon']['exit_ever_2017']['2010-14']['n_partners']:,} ({e59['A_vintage_horizon']['exit_ever_2017']['2010-14']['n_female_partners']}) |
| &nbsp;&nbsp;vintages 2015–17 | {e59['A_vintage_horizon']['exit_ever_2017']['2015-17']['ffp']['coef']*100:+.2f} | {pp(e59['A_vintage_horizon']['exit_ever_2017']['2015-17']['ffp']['ci95'])} | {e59['A_vintage_horizon']['exit_ever_2017']['2015-17']['ffp']['mde80']*100:.2f} | {e59['A_vintage_horizon']['exit_ever_2017']['2015-17']['ffp']['beta_std']:+.3f} | {'yes' if e59['A_vintage_horizon']['exit_ever_2017']['2015-17']['ffp']['within_pm0.05'] else 'no'} | {e59['A_vintage_horizon']['exit_ever_2017']['2015-17']['ff']['coef']*100:+.2f} | {pp(e59['A_vintage_horizon']['exit_ever_2017']['2015-17']['ff']['ci95'])} | {e59['A_vintage_horizon']['exit_ever_2017']['2015-17']['n']:,} / {e59['A_vintage_horizon']['exit_ever_2017']['2015-17']['n_partners']:,} ({e59['A_vintage_horizon']['exit_ever_2017']['2015-17']['n_female_partners']}) |
| &nbsp;&nbsp;partners with an attributed deal after October 2020 | {e59['A_vintage_horizon']['exit_ever_2017_active_partners']['ffp']['coef']*100:+.2f} | {pp(e59['A_vintage_horizon']['exit_ever_2017_active_partners']['ffp']['ci95'])} | {e59['A_vintage_horizon']['exit_ever_2017_active_partners']['ffp']['mde80']*100:.2f} | {e59['A_vintage_horizon']['exit_ever_2017_active_partners']['ffp']['beta_std']:+.3f} | {'yes' if e59['A_vintage_horizon']['exit_ever_2017_active_partners']['ffp']['within_pm0.05'] else 'no'} | {e59['A_vintage_horizon']['exit_ever_2017_active_partners']['ff']['coef']*100:+.2f} | {pp(e59['A_vintage_horizon']['exit_ever_2017_active_partners']['ff']['ci95'])} | {e59['A_vintage_horizon']['exit_ever_2017_active_partners']['n']:,} / {e59['A_vintage_horizon']['exit_ever_2017_active_partners']['n_partners']:,} ({e59['A_vintage_horizon']['exit_ever_2017_active_partners']['n_female_partners']}) |
| &nbsp;&nbsp;partners without one | {e59['A_vintage_horizon']['exit_ever_2017_inactive_partners']['ffp']['coef']*100:+.2f} | {pp(e59['A_vintage_horizon']['exit_ever_2017_inactive_partners']['ffp']['ci95'])} | {e59['A_vintage_horizon']['exit_ever_2017_inactive_partners']['ffp']['mde80']*100:.2f} | {e59['A_vintage_horizon']['exit_ever_2017_inactive_partners']['ffp']['beta_std']:+.3f} | {'yes' if e59['A_vintage_horizon']['exit_ever_2017_inactive_partners']['ffp']['within_pm0.05'] else 'no'} | {e59['A_vintage_horizon']['exit_ever_2017_inactive_partners']['ff']['coef']*100:+.2f} | {pp(e59['A_vintage_horizon']['exit_ever_2017_inactive_partners']['ff']['ci95'])} | {e59['A_vintage_horizon']['exit_ever_2017_inactive_partners']['n']:,} / {e59['A_vintage_horizon']['exit_ever_2017_inactive_partners']['n_partners']:,} ({e59['A_vintage_horizon']['exit_ever_2017_inactive_partners']['n_female_partners']}) |
| &nbsp;&nbsp;IPO by sample end | {e59['C_influence_decomposition_multiplicity']['ipo_ever']['ffp']['coef']*100:+.2f} | {pp(e59['C_influence_decomposition_multiplicity']['ipo_ever']['ffp']['ci95'])} | {e59['C_influence_decomposition_multiplicity']['ipo_ever']['ffp']['mde80']*100:.2f} | {e59['C_influence_decomposition_multiplicity']['ipo_ever']['ffp']['beta_std']:+.3f} | {'yes' if e59['C_influence_decomposition_multiplicity']['ipo_ever']['ffp']['within_pm0.05'] else 'no'} | {e59['C_influence_decomposition_multiplicity']['ipo_ever']['ff']['coef']*100:+.2f} | {pp(e59['C_influence_decomposition_multiplicity']['ipo_ever']['ff']['ci95'])} | {e59['C_influence_decomposition_multiplicity']['ipo_ever']['n']:,} / {e59['C_influence_decomposition_multiplicity']['ipo_ever']['n_partners']:,} ({e59['C_influence_decomposition_multiplicity']['ipo_ever']['n_female_partners']}) |
| &nbsp;&nbsp;acquisition by sample end (no IPO) | {e59['C_influence_decomposition_multiplicity']['acq_ever']['ffp']['coef']*100:+.2f} | {pp(e59['C_influence_decomposition_multiplicity']['acq_ever']['ffp']['ci95'])} | {e59['C_influence_decomposition_multiplicity']['acq_ever']['ffp']['mde80']*100:.2f} | {e59['C_influence_decomposition_multiplicity']['acq_ever']['ffp']['beta_std']:+.3f} | {'yes' if e59['C_influence_decomposition_multiplicity']['acq_ever']['ffp']['within_pm0.05'] else 'no'} | {e59['C_influence_decomposition_multiplicity']['acq_ever']['ff']['coef']*100:+.2f} | {pp(e59['C_influence_decomposition_multiplicity']['acq_ever']['ff']['ci95'])} | {e59['C_influence_decomposition_multiplicity']['acq_ever']['n']:,} / {e59['C_influence_decomposition_multiplicity']['acq_ever']['n_partners']:,} ({e59['C_influence_decomposition_multiplicity']['acq_ever']['n_female_partners']}) |
| &nbsp;&nbsp;company clusters | {e59['B_clusters_benchmark']['exit_ever_company_cluster']['ffp']['coef']*100:+.2f} | {pp(e59['B_clusters_benchmark']['exit_ever_company_cluster']['ffp']['ci95'])} | {e59['B_clusters_benchmark']['exit_ever_company_cluster']['ffp']['mde80']*100:.2f} | {e59['B_clusters_benchmark']['exit_ever_company_cluster']['ffp']['beta_std']:+.3f} | {'yes' if e59['B_clusters_benchmark']['exit_ever_company_cluster']['ffp']['within_pm0.05'] else 'no'} | {e59['B_clusters_benchmark']['exit_ever_company_cluster']['ff']['coef']*100:+.2f} | {pp(e59['B_clusters_benchmark']['exit_ever_company_cluster']['ff']['ci95'])} | {e59['B_clusters_benchmark']['exit_ever_company_cluster']['n']:,} / {e59['B_clusters_benchmark']['exit_ever_company_cluster']['n_partners']:,} ({e59['B_clusters_benchmark']['exit_ever_company_cluster']['n_female_partners']}) |
| 36-month exit, vintages 2010–14 | {e59['A_vintage_horizon']['exit3_2020']['2010-14']['ffp']['coef']*100:+.2f} | {pp(e59['A_vintage_horizon']['exit3_2020']['2010-14']['ffp']['ci95'])} | {e59['A_vintage_horizon']['exit3_2020']['2010-14']['ffp']['mde80']*100:.2f} | {e59['A_vintage_horizon']['exit3_2020']['2010-14']['ffp']['beta_std']:+.3f} | {'yes' if e59['A_vintage_horizon']['exit3_2020']['2010-14']['ffp']['within_pm0.05'] else 'no'} | {e59['A_vintage_horizon']['exit3_2020']['2010-14']['ff']['coef']*100:+.2f} | {pp(e59['A_vintage_horizon']['exit3_2020']['2010-14']['ff']['ci95'])} | {e59['A_vintage_horizon']['exit3_2020']['2010-14']['n']:,} / {e59['A_vintage_horizon']['exit3_2020']['2010-14']['n_partners']:,} ({e59['A_vintage_horizon']['exit3_2020']['2010-14']['n_female_partners']}) |
| &nbsp;&nbsp;vintages 2015–17 | {e59['A_vintage_horizon']['exit3_2020']['2015-17']['ffp']['coef']*100:+.2f} | {pp(e59['A_vintage_horizon']['exit3_2020']['2015-17']['ffp']['ci95'])} | {e59['A_vintage_horizon']['exit3_2020']['2015-17']['ffp']['mde80']*100:.2f} | {e59['A_vintage_horizon']['exit3_2020']['2015-17']['ffp']['beta_std']:+.3f} | {'yes' if e59['A_vintage_horizon']['exit3_2020']['2015-17']['ffp']['within_pm0.05'] else 'no'} | {e59['A_vintage_horizon']['exit3_2020']['2015-17']['ff']['coef']*100:+.2f} | {pp(e59['A_vintage_horizon']['exit3_2020']['2015-17']['ff']['ci95'])} | {e59['A_vintage_horizon']['exit3_2020']['2015-17']['n']:,} / {e59['A_vintage_horizon']['exit3_2020']['2015-17']['n_partners']:,} ({e59['A_vintage_horizon']['exit3_2020']['2015-17']['n_female_partners']}) |
| &nbsp;&nbsp;vintages 2018–20 | {e59['A_vintage_horizon']['exit3_2020']['2018-20']['ffp']['coef']*100:+.2f} | {pp(e59['A_vintage_horizon']['exit3_2020']['2018-20']['ffp']['ci95'])} | {e59['A_vintage_horizon']['exit3_2020']['2018-20']['ffp']['mde80']*100:.2f} | {e59['A_vintage_horizon']['exit3_2020']['2018-20']['ffp']['beta_std']:+.3f} | {'yes' if e59['A_vintage_horizon']['exit3_2020']['2018-20']['ffp']['within_pm0.05'] else 'no'} | {e59['A_vintage_horizon']['exit3_2020']['2018-20']['ff']['coef']*100:+.2f} | {pp(e59['A_vintage_horizon']['exit3_2020']['2018-20']['ff']['ci95'])} | {e59['A_vintage_horizon']['exit3_2020']['2018-20']['n']:,} / {e59['A_vintage_horizon']['exit3_2020']['2018-20']['n_partners']:,} ({e59['A_vintage_horizon']['exit3_2020']['2018-20']['n_female_partners']}) |
| 36-month exit, company clusters | {e59['B_clusters_benchmark']['exit3_company_cluster']['ffp']['coef']*100:+.2f} | {pp(e59['B_clusters_benchmark']['exit3_company_cluster']['ffp']['ci95'])} | {e59['B_clusters_benchmark']['exit3_company_cluster']['ffp']['mde80']*100:.2f} | {e59['B_clusters_benchmark']['exit3_company_cluster']['ffp']['beta_std']:+.3f} | {'yes' if e59['B_clusters_benchmark']['exit3_company_cluster']['ffp']['within_pm0.05'] else 'no'} | {e59['B_clusters_benchmark']['exit3_company_cluster']['ff']['coef']*100:+.2f} | {pp(e59['B_clusters_benchmark']['exit3_company_cluster']['ff']['ci95'])} | {e59['B_clusters_benchmark']['exit3_company_cluster']['n']:,} / {e59['B_clusters_benchmark']['exit3_company_cluster']['n_partners']:,} ({e59['B_clusters_benchmark']['exit3_company_cluster']['n_female_partners']}) |
| 36-month exit, year × sector × stage × country benchmark | {e59['B_clusters_benchmark']['exit3_country_benchmark']['ffp']['coef']*100:+.2f} | {pp(e59['B_clusters_benchmark']['exit3_country_benchmark']['ffp']['ci95'])} | {e59['B_clusters_benchmark']['exit3_country_benchmark']['ffp']['mde80']*100:.2f} | {e59['B_clusters_benchmark']['exit3_country_benchmark']['ffp']['beta_std']:+.3f} | {'yes' if e59['B_clusters_benchmark']['exit3_country_benchmark']['ffp']['within_pm0.05'] else 'no'} | {e59['B_clusters_benchmark']['exit3_country_benchmark']['ff']['coef']*100:+.2f} | {pp(e59['B_clusters_benchmark']['exit3_country_benchmark']['ff']['ci95'])} | {e59['B_clusters_benchmark']['exit3_country_benchmark']['n']:,} / {e59['B_clusters_benchmark']['exit3_country_benchmark']['n_partners']:,} ({e59['B_clusters_benchmark']['exit3_country_benchmark']['n_female_partners']}) |
| Same partners and window as eventual exit (deals through 2017-10): 36-month exit | {e57['A_2017']['exit3']['ffp']['coef']*100:+.2f} | {pp(e57['A_2017']['exit3']['ffp']['ci95'])} | {e57['A_2017']['exit3']['ffp']['mde80']*100:.2f} | {e57['A_2017']['exit3']['ffp']['coef']/e57['A_2017']['exit3']['sd_r']:+.3f} | {'yes' if e57['A_2017']['exit3']['ffp']['ci95'][0] >= -0.05 and e57['A_2017']['exit3']['ffp']['ci95'][1] <= 0.05 else 'no'} | {e57['A_2017']['exit3']['ff']['coef']*100:+.2f} | {pp(e57['A_2017']['exit3']['ff']['ci95'])} | {e57['A_2017']['exit3']['n']:,} / {e57['A_2017']['exit3']['n_partners']:,} |
| &nbsp;&nbsp;72-month exit | {e57['A_2017']['exit6']['ffp']['coef']*100:+.2f} | {pp(e57['A_2017']['exit6']['ffp']['ci95'])} | {e57['A_2017']['exit6']['ffp']['mde80']*100:.2f} | {e57['A_2017']['exit6']['ffp']['coef']/e57['A_2017']['exit6']['sd_r']:+.3f} | {'yes' if e57['A_2017']['exit6']['ffp']['ci95'][0] >= -0.05 and e57['A_2017']['exit6']['ffp']['ci95'][1] <= 0.05 else 'no'} | {e57['A_2017']['exit6']['ff']['coef']*100:+.2f} | {pp(e57['A_2017']['exit6']['ff']['ci95'])} | {e57['A_2017']['exit6']['n']:,} / {e57['A_2017']['exit6']['n_partners']:,} |
| &nbsp;&nbsp;exit after month 36 (indicator on the full sample: exit by sample end and not by month 36; equals eventual exit minus 36-month exit by construction) | {e57['A_2017']['late_exit']['ffp']['coef']*100:+.2f} | {pp(e57['A_2017']['late_exit']['ffp']['ci95'])} | {e57['A_2017']['late_exit']['ffp']['mde80']*100:.2f} | {e57['A_2017']['late_exit']['ffp']['coef']/e57['A_2017']['late_exit']['sd_r']:+.3f} | {'yes' if e57['A_2017']['late_exit']['ffp']['ci95'][0] >= -0.05 and e57['A_2017']['late_exit']['ffp']['ci95'][1] <= 0.05 else 'no'} | {e57['A_2017']['late_exit']['ff']['coef']*100:+.2f} | {pp(e57['A_2017']['late_exit']['ff']['ci95'])} | {e57['A_2017']['late_exit']['n']:,} / {e57['A_2017']['late_exit']['n_partners']:,} |
| &nbsp;&nbsp;follow-on financing within 36 months | {e57['A_2017']['fon']['ffp']['coef']*100:+.2f} | {pp(e57['A_2017']['fon']['ffp']['ci95'])} | {e57['A_2017']['fon']['ffp']['mde80']*100:.2f} | {e57['A_2017']['fon']['ffp']['coef']/e57['A_2017']['fon']['sd_r']:+.3f} | {'yes' if e57['A_2017']['fon']['ffp']['ci95'][0] >= -0.05 and e57['A_2017']['fon']['ffp']['ci95'][1] <= 0.05 else 'no'} | {e57['A_2017']['fon']['ff']['coef']*100:+.2f} | {pp(e57['A_2017']['fon']['ff']['ci95'])} | {e57['A_2017']['fon']['n']:,} / {e57['A_2017']['fon']['n_partners']:,} |
| Female partners' own female-founded − other gap (β_FF + β_int), 36-month exit, deals through 2020-10, 2,000 draws | {e60['A_female_own_gap']['exit3']['female_own_gap_ff_plus_ffp']['coef']*100:+.2f} | {pp(e60['A_female_own_gap']['exit3']['female_own_gap_ff_plus_ffp']['ci95'])} | {2.8*e60['A_female_own_gap']['exit3']['female_own_gap_ff_plus_ffp']['se_boot']*100:.2f} | {e60['A_female_own_gap']['exit3']['female_own_gap_ff_plus_ffp']['coef']/e60['A_female_own_gap']['exit3']['sd_r']:+.3f} | {'yes' if e60['A_female_own_gap']['exit3']['female_own_gap_ff_plus_ffp']['ci95'][0] >= -0.05 and e60['A_female_own_gap']['exit3']['female_own_gap_ff_plus_ffp']['ci95'][1] <= 0.05 else 'no'} | — | — | — |
| &nbsp;&nbsp;same, follow-on financing | {e60['A_female_own_gap']['fon']['female_own_gap_ff_plus_ffp']['coef']*100:+.2f} | {pp(e60['A_female_own_gap']['fon']['female_own_gap_ff_plus_ffp']['ci95'])} | {2.8*e60['A_female_own_gap']['fon']['female_own_gap_ff_plus_ffp']['se_boot']*100:.2f} | {e60['A_female_own_gap']['fon']['female_own_gap_ff_plus_ffp']['coef']/e60['A_female_own_gap']['fon']['sd_r']:+.3f} | {'yes' if e60['A_female_own_gap']['fon']['female_own_gap_ff_plus_ffp']['ci95'][0] >= -0.05 and e60['A_female_own_gap']['fon']['female_own_gap_ff_plus_ffp']['ci95'][1] <= 0.05 else 'no'} | — | — | — |
| &nbsp;&nbsp;same, eventual exit, deals through 2017-10 | {e60['A_female_own_gap']['exit_ever']['female_own_gap_ff_plus_ffp']['coef']*100:+.2f} | {pp(e60['A_female_own_gap']['exit_ever']['female_own_gap_ff_plus_ffp']['ci95'])} | {2.8*e60['A_female_own_gap']['exit_ever']['female_own_gap_ff_plus_ffp']['se_boot']*100:.2f} | {e60['A_female_own_gap']['exit_ever']['female_own_gap_ff_plus_ffp']['coef']/e60['A_female_own_gap']['exit_ever']['sd_r']:+.3f} | {'yes' if e60['A_female_own_gap']['exit_ever']['female_own_gap_ff_plus_ffp']['ci95'][0] >= -0.05 and e60['A_female_own_gap']['exit_ever']['female_own_gap_ff_plus_ffp']['ci95'][1] <= 0.05 else 'no'} | — | — | — |
| Vintage contrast, eventual exit (deals through 2017-10): β_int for 2015–17 minus β_int for 2010–14 (pooled interaction model) | {e60['B_vintage_contrast']['exit_ever_2017']['contrast_2015_17_minus_2010_14']['coef']*100:+.2f} | {pp(e60['B_vintage_contrast']['exit_ever_2017']['contrast_2015_17_minus_2010_14']['ci95'])} | {2.8*e60['B_vintage_contrast']['exit_ever_2017']['contrast_2015_17_minus_2010_14']['se_boot']*100:.2f} | {e60['B_vintage_contrast']['exit_ever_2017']['contrast_2015_17_minus_2010_14']['coef']/e60['A_female_own_gap']['exit_ever']['sd_r']:+.3f} | {'yes' if e60['B_vintage_contrast']['exit_ever_2017']['contrast_2015_17_minus_2010_14']['ci95'][0] >= -0.05 and e60['B_vintage_contrast']['exit_ever_2017']['contrast_2015_17_minus_2010_14']['ci95'][1] <= 0.05 else 'no'} | — | — | — |
| Vintage contrast, 36-month exit (deals through 2020-10): β_int for 2018–20 minus β_int for 2010–14 | {e60['B_vintage_contrast']['exit3_2020']['contrast_2018_20_minus_2010_14']['coef']*100:+.2f} | {pp(e60['B_vintage_contrast']['exit3_2020']['contrast_2018_20_minus_2010_14']['ci95'])} | {2.8*e60['B_vintage_contrast']['exit3_2020']['contrast_2018_20_minus_2010_14']['se_boot']*100:.2f} | {e60['B_vintage_contrast']['exit3_2020']['contrast_2018_20_minus_2010_14']['coef']/e60['A_female_own_gap']['exit3']['sd_r']:+.3f} | {'yes' if e60['B_vintage_contrast']['exit3_2020']['contrast_2018_20_minus_2010_14']['ci95'][0] >= -0.05 and e60['B_vintage_contrast']['exit3_2020']['contrast_2018_20_minus_2010_14']['ci95'][1] <= 0.05 else 'no'} | — | — | — |
| Exits dated on or before the deal excluded (post-deal rule): 36-month exit, deals through 2020-10 | {e60['C_post_deal_exit_rule']['within_partner_exit3']['post_deal_rule']['coef']*100:+.2f} | {pp(e60['C_post_deal_exit_rule']['within_partner_exit3']['post_deal_rule']['ci95'])} | {e60['C_post_deal_exit_rule']['within_partner_exit3']['post_deal_rule']['mde80']*100:.2f} | {e60['C_post_deal_exit_rule']['within_partner_exit3']['post_deal_rule']['beta_std']:+.3f} | {'yes' if e60['C_post_deal_exit_rule']['within_partner_exit3']['post_deal_rule']['ci95'][0] >= -0.05 and e60['C_post_deal_exit_rule']['within_partner_exit3']['post_deal_rule']['ci95'][1] <= 0.05 else 'no'} | — | — | {e60['C_post_deal_exit_rule']['within_partner_exit3']['n_post_rule']:,} / — |
| &nbsp;&nbsp;same, eventual exit, deals through 2017-10 | {e60['C_post_deal_exit_rule']['within_partner_exit_ever']['post_deal_rule']['coef']*100:+.2f} | {pp(e60['C_post_deal_exit_rule']['within_partner_exit_ever']['post_deal_rule']['ci95'])} | {e60['C_post_deal_exit_rule']['within_partner_exit_ever']['post_deal_rule']['mde80']*100:.2f} | {e60['C_post_deal_exit_rule']['within_partner_exit_ever']['post_deal_rule']['beta_std']:+.3f} | {'yes' if e60['C_post_deal_exit_rule']['within_partner_exit_ever']['post_deal_rule']['ci95'][0] >= -0.05 and e60['C_post_deal_exit_rule']['within_partner_exit_ever']['post_deal_rule']['ci95'][1] <= 0.05 else 'no'} | — | — | {e60['C_post_deal_exit_rule']['within_partner_exit_ever']['n_post_rule']:,} / — |

*Panel B: partners with at least one female-founded and one other deal in the window. Eligible deals {e60['A_female_own_gap']['exit3']['counts']['deals_eligible']:,} → {e54['A_exit3']['sample']['n_deals']:,} with a market benchmark ({e60['A_female_own_gap']['exit3']['counts']['deals_dropped_singleton_benchmark_cell']} deals alone in their year × sector × stage cell have none) → {e60['A_female_own_gap']['exit3']['counts']['deals_estimation']:,} in the estimation sample ({e60['A_female_own_gap']['exit3']['counts']['deals_dropped_single_row_partner']} are a partner's only remaining deal); {e54['A_exit3']['sample']['n_partners']:,} partners ({e54['A_exit3']['sample']['n_female_partners']} women) are eligible and {e60['A_female_own_gap']['exit3']['counts']['partners_identifying']:,} ({e60['A_female_own_gap']['exit3']['counts']['female_partners_identifying']}) retain both kinds of deal after these drops and identify β_int; the partner counts shown in each row follow the same convention (eligible for the P001-54 rows, identifying for the later rows). {e54['A_exit3']['sample']['n_deals_2015plus']:,} deals are dated 2015 or later; exit3 base rate {e54['A_exit3']['sample']['base_y']:.3f}. The "inside ±5 pp" column marks whether the 95% interval lies within a reference band equal to the peer-comparison gap of Table 4; it is a reference scale, not a materiality threshold. Outcome = deal outcome minus the leave-one-out mean of its year × sector × stage cell; deal controls as in Panel A. β_FF is the within-partner gap for male partners; β_int is the additional gap for female partners (favoritism predicts β_int < 0); female partners' own gap is β_FF + β_int, with its interval from the same bootstrap draws. The vintage-contrast rows come from one pooled regression with β_int interacted with vintage indicators; the post-deal-rule rows recode exits dated on or before the deal as non-exits (Appendix IA.1). Same-window rows re-estimate the specification on the eventual-exit sample (P001-57). Bootstrap two-sided p-values for β_int on the three featured outcomes (36-month exit, follow-on, exit by sample end): {e59['C_influence_decomposition_multiplicity']['holm_adjusted_p']['raw']['exit3']:.3f}, {e59['C_influence_decomposition_multiplicity']['holm_adjusted_p']['raw']['fon']:.3f}, {e59['C_influence_decomposition_multiplicity']['holm_adjusted_p']['raw']['exit_ever']:.3f}; Holm-adjusted {e59['C_influence_decomposition_multiplicity']['holm_adjusted_p']['holm']['exit3']:.3f}, {e59['C_influence_decomposition_multiplicity']['holm_adjusted_p']['holm']['fon']:.3f}, {e59['C_influence_decomposition_multiplicity']['holm_adjusted_p']['holm']['exit_ever']:.3f}. Dropping any one of the {e59['C_influence_decomposition_multiplicity']['exit_ever_loo_female']['n_female']} women from the exit-by-sample-end row moves β_int by at most {e59['C_influence_decomposition_multiplicity']['exit_ever_loo_female']['max_abs_shift']*100:.2f} points. Female partners' female-founded deals outside this sample (partners with no other deal): {e59['D_selection']['share_outside_within_partner_sample']*100:.1f} percent. Sources: P001-54, P001-57, P001-59, P001-60.*

## Panel C. Outcome battery (covariate-adjusted, pp) with Romano–Wolf stepdown
| Outcome | Gap | 95% CI | Multiple-testing |
|---|---|---|---|
{rows4}

Within-cell permutation (unadjusted spec): follow-on p = {perm2['fon'][1]}; exit p = {perm2['exit_ever'][1]}.
IPO and closure margins remain unresolved (MDE80 ≈ 2.8 / 3.6 pp) rather than established nulls.

*Deal controls: round size, company age, prior rounds, syndicate size, co-investor experience (all at deal date). Identifying base of the hazard (share of cell–year groups that are co-attributions on a single round; gap on multi-round groups): Appendix Table IA.2, Panel E. The deal-fixed continuation margin is Table 8. Sources: P001-12, P001-13, P001-14, P001-03 (MDEs), P001-50 (identifying base).*
""")

e80, e81 = i80["estimates"], i81["estimates"]
w("table3.md", f"""# Table 3. The stage tilt and its origins
| | Estimate | 95% CI |
|---|---|---|
| FP–early-stage association (firm×year) | {e80['fp_early_assoc'][0]*100:+.2f}pp | {pp(e80['fp_early_assoc'][1])} |
| — among deals with no observed female founder | {e81['ma_ff0'][0]*100:+.2f}pp | {pp(e81['ma_ff0'][1])} |
| Mean tenure: female / male partners (yrs) | {e81['tenure_mean_f']} / {e81['tenure_mean_m']} | |
| Within tenure-bin cells (attenuation {e81['mb_attenuation']*100:.0f}%) | {e81['mb_tenurecell'][0]*100:+.2f}pp | {pp(e81['mb_tenurecell'][1])} |
| Stage-graduation slope diff (F−M, pp/yr) | {e81['slope_diff'][0]*100:+.2f} | {pp(e81['slope_diff'][1])} |
| Outcome test, early deals (fon), exact stage cells | {p8['estimates']['becker_fon_finestage'][0]*100:+.2f}pp | {pp(p8['estimates']['becker_fon_finestage'][1])} |

*Sources: I-80, I-81, P001-08.*
""")

e11 = p11["estimates"]
e4b = p4b["estimates"]
e82 = i82["estimates"]
curve = p14b["estimates"]["sensitivity_curve_pp"]
w("table10.md", f"""# Table 10. Partner turnover and deal composition: deal-level stacked event studies (NA+EU)
## Featured: arrival margin (deal-level)
| | Estimate (pp) | 95% CI |
|---|---|---|
| **Female arrival × post (vs male arrivals, reweighted)** | **{e11['join'][0]:+.2f}** | **{pp(e11['join'][1])}** |
| Departure margin (same design) | {e11['exit'][0]:+.2f} | {pp(e11['exit'][1])} |
| Colleague deals only (event partner's own deals excluded) | {e11['colleague_joint'][0]:+.2f} | {pp(e11['colleague_joint'][1])} |
| Arrival + departure (mirror-reversal test: = 0 under exact reversal; same bootstrap draws) | {e11['join_plus_exit'][0]:+.2f} | {pp(e11['join_plus_exit'][1])} |
| Own-deal share of post-event flow after female arrivals; FF share of own deals vs colleagues' deals; direct composition share s·(p_own − p_colleagues) | {e11['mechanical_own_channel']['own_share_post_female_join']*100:.1f}%; {e11['mechanical_own_channel']['ff_share_own_deals']*100:.1f}% vs {e11['mechanical_own_channel']['ff_share_colleague_deals']*100:.1f}% | {e11['mechanical_own_channel']['direct_composition_pp']:+.2f} pp |
| Female arrivals that are the firm's first female partner; female departures that remove its last (shares of events) | {e11['female_events']['share_first_female_partner']*100:.0f}% of {e11['female_events']['n_join']:,}; {e11['female_events']['share_last_female_partner']*100:.0f}% of {e11['female_events']['n_exit']:,} | |
| Pre-event path k=−4..−2 (pp, ref k=−1) | {e11['path_join'].get('-4')}, {e11['path_join'].get('-3')}, {e11['path_join'].get('-2')} | |
| Trend sensitivity: CI lower bound reaches 0 at δ* (point stays >0 to ≈0.7) | 0.4 pp/half-yr | observed pre-slope ≈ 0 |
| Event-aggregated design, own breakdown slope (pp per half-year) | {p4b['estimates']['breakdown_slope_pp_per_half']} | |

## Robustness: symmetric and aggregated versions
| | Estimate (pp) | 95% CI |
|---|---|---|
| Deal-level arrival − departure contrast | {e11['joint_contrast'][0]:+.2f} | {pp(e11['joint_contrast'][1])} |
| Event-aggregated contrast (half-year shares, reweighted) | {e4b['L2_reweighted'][0]:+.2f} | {pp(e4b['L2_reweighted'][1])} |
| — permutation p (gender labels) | {e4b['perm_p']} | |
| — placebo: all-male-team deal counts (log points) | {e4b['placebo_allmale_counts'][0]:+.3f} | {raw(e4b['placebo_allmale_counts'][1])} |
| Pre-hire run-up in firm FF share, levels (I-76) | +2.2 | [+1.3, +3.2] |

*Deal-level design: {e11['n_deal_obs']:,} deal observations around {e11['n_events']:,} clean events (arrivals: no attributed deal before recorded start), event FE + relative-half FE, contaminated male controls excluded, firm-cluster bootstrap. Aggregated design: P001-04b (1,177 female events). Sources: P001-11, P001-14b, P001-04b, I-82, I-76.*
""")

e5 = p5["estimates"]
e18 = p18b["estimates"]
e23, e24, e25, e26, e27, e28, e29, e30 = (x["estimates"] for x in (p23, p24, p25, p26, p27, p28, p29, p30))
t2 = e29["T2_late_stage_control"]           # P001-29: 사전기 후기단계 비중 통제
r30 = e30                                    # P001-30: 분해·연공·회사FE·고정지평·LPO
jr = e25["B2_joint_RI"]
ri = jr["individual"]
lp = e23["A6_LP_side"]
b1, b1b = e25["B1_wedge_predicts_future"], e25["B1b_control_adj_predicts_future"]
lo1, lo2, lo3 = e27["B LOO"], e27["C LOO + 셀≥10"], e27["D LOO + 셀≥30"]
g1, g2, g3, g5 = (e26[k] for k in ("G1_fp_to_wedge", "G2_fp_to_future_adj",
                                   "G3_fp_controlling_wedge", "G5_control_fp_to_pre_adj"))
col = e23["A2_collinearity"]
# 위약 400회에서 초과 0 → 해석 가능한 최소 p 는 1/(N+1). "< 0.001" 은 과잉 주장이다.
import math
p_joint = (f"< {math.ceil(1000 / (jr['n_placebo'] + 1)) / 1000:.3f} (no exceedance in {jr['n_placebo']} permutations)"
           if jr["joint_RI_p"] < 1 / jr["n_placebo"] else f"{jr['joint_RI_p']:.3f}")
w("table7.md", f"""# Table 7. Track-record composition: size, pricing, and information content
## Panel A. Re-ranking: raw vs composition-adjusted exit rates
| | Raw → Adjusted |
|---|---|
| Female partners' mean percentile shift | {e5['pct_diff_female'][0]:+.2f} pts [{e5['pct_diff_female'][1][0]:+.2f}, {e5['pct_diff_female'][1][1]:+.2f}] |
| Male partners' mean percentile shift | {e5['pct_diff_male'][0]:+.2f} pts [{e5['pct_diff_male'][1][0]:+.2f}, {e5['pct_diff_male'][1][1]:+.2f}] |
| Female share of top quartile | {e5['topq_female_share_raw']*100:.2f}% → {e5['topq_female_share_adj']*100:.2f}% (Δ interval crosses zero) |
| Rank correlation (raw, adjusted) | {e5['spearman_raw_adj']} |

## Panel B. Subsequent attributed deal activity: log count of deals attributed to the partner in 2018–2020 on 2010–17 percentiles
| | β (log deals per unit of percentile rank, 0–1) | 95% CI |
|---|---|---|
| Adjusted percentile A, holding the raw percentile fixed (β_A) | {e18['beta_adj_given_raw'][0]:+.2f} | {raw(e18['beta_adj_given_raw'][1],2)} |
| Raw percentile R, holding A fixed (β_R) = coefficient on the rank difference R − A | {e18['beta_raw_given_adj'][0]:+.2f} | {raw(e18['beta_raw_given_adj'][1],2)} |
| Adjusted percentile A, holding the rank difference R − A fixed (β_R + β_A; same bootstrap draws) | {e18['beta_adj_given_rankdiff'][0]:+.2f} | {raw(e18['beta_adj_given_rankdiff'][1],2)} |

## Panel C. External outcomes among partners who move or spin out, 2017-11 to 2023-10
| Outcome | Sample | β on composition component (given adjusted percentile) | 95% CI | β with pre-period late-stage share as control | 95% CI | Late-stage share, own coefficient |
|---|---|---|---|---|---|---|
| New firm records a fund close (partners who spin out) | {lp['n_spinout']} partners; {lp['n_raised']} raise ({lp['rate']*100:.1f}%) | {ri['lp_any']['coef']:+.3f} | {raw(ri['lp_any']['ci95'])} | {t2['lp_any']['with_late_ctrl']['coef']:+.3f} | {raw(t2['lp_any']['with_late_ctrl']['ci95'])} | {t2['lp_any']['late_sh_own']['coef']:+.3f} {raw(t2['lp_any']['late_sh_own']['ci95'])} |
| log fund size recorded | {ri['lp_amt']['n']} | {ri['lp_amt']['coef']:+.3f} | {raw(ri['lp_amt']['ci95'])} | {t2['lp_amt']['with_late_ctrl']['coef']:+.3f} | {raw(t2['lp_amt']['with_late_ctrl']['ci95'])} | {t2['lp_amt']['late_sh_own']['coef']:+.3f} {raw(t2['lp_amt']['late_sh_own']['ci95'])} |
| Receiving firm's prior attributed deal count, log(1+n) (partners who move) | {ri['recv_q']['n']} | {ri['recv_q']['coef']:+.3f} | {raw(ri['recv_q']['ci95'])} | {t2['recv_q']['with_late_ctrl']['coef']:+.3f} | {raw(t2['recv_q']['with_late_ctrl']['ci95'])} | {t2['recv_q']['late_sh_own']['coef']:+.3f} {raw(t2['recv_q']['late_sh_own']['ci95'])} |
| Joint randomization test, three outcomes (uncontrolled) | {jr['n_placebo']} permutations of the composition component | Mahalanobis {jr['mahalanobis']:.1f} vs null 95th percentile {jr['placebo_p95']:.1f}; {jr['n_aligned']}/3 signs aligned | p {p_joint} | | | |

## Panel D1. Does composition carry information? Open horizon (exit by sample end); post window 2017-11 to 2023-10
Rows are on the percentile scale (β on raw percentile given adjusted percentile) unless marked *levels* (β on the composition component in exit-probability units).
| Specification | β | 95% CI | n |
|---|---|---|---|
| Baseline cell benchmark | {b1['coef']:+.3f} | {raw(b1['ci95'])} | {b1['n']:,} |
| Leave-one-out cell benchmark | {lo1['coef']:+.3f} | {raw(lo1['ci95'])} | {lo1['n']:,} |
| Leave-one-out, cells with ≥ 10 deals | {lo2['coef']:+.3f} | {raw(lo2['ci95'])} | {lo2['n']:,} |
| Leave-one-out, cells with ≥ 30 deals | {lo3['coef']:+.3f} | {raw(lo3['ci95'])} | {lo3['n']:,} |
| Leave-one-out, inverse-probability weighted for post-period observation | {e28['S2_ipw']['coef']:+.3f} | {raw(e28['S2_ipw']['ci95'])} | {e28['S2_ipw']['n']:,} |
| Levels instead of percentiles: raw exit rate given adjusted exit rate | {e28['S4_raw_given_adj_level']['coef']:+.3f} | {raw(e28['S4_raw_given_adj_level']['ci95'])} | {e28['S4_raw_given_adj_level']['n']:,} |
| Levels, composition component alone (unconditional) | {e28['S3_terrain_unconditional_level']['coef']:+.3f} | {raw(e28['S3_terrain_unconditional_level']['ci95'])} | {e28['S3_terrain_unconditional_level']['n']:,} |
| Percentile difference alone (unconditional) | {e29['T3_unconditional_percentile']['coef']:+.3f} | {raw(e29['T3_unconditional_percentile']['ci95'])} | {e29['T3_unconditional_percentile']['n']:,} |
| Excluding post-period deals in companies the partner backed pre-period | {e29['T1_excl_overlap']['coef']:+.3f} | {raw(e29['T1_excl_overlap']['ci95'])} | {e29['T1_excl_overlap']['n']:,} |
| Leave-partner-out cell benchmark | {r30['R6_leave_partner_out']['raw_lpo']['coef']:+.3f} | {raw(r30['R6_leave_partner_out']['raw_lpo']['ci95'])} | {r30['R6_leave_partner_out']['n']:,} |
| Composition component, levels, given tenure and first-deal-year effects | {r30['R2t_total_tenure']['terrain']['coef']:+.3f} | {raw(r30['R2t_total_tenure']['terrain']['ci95'])} | {r30['R2t_total_tenure']['n']:,} |
| Composition component, levels, home-firm fixed effects | {r30['R4t_total_firmFE']['terrain']['coef']:+.3f} | {raw(r30['R4t_total_firmFE']['terrain']['ci95'])} | {r30['R4t_total_firmFE']['n']:,} |
| Decomposition of the composition component, levels: vintage / stage within year / sector within year–stage | {r30['R1_decomp']['t_v']['coef']:+.3f} / {r30['R1_decomp']['t_s']['coef']:+.3f} / {r30['R1_decomp']['t_cs']['coef']:+.3f} | {raw(r30['R1_decomp']['t_v']['ci95'])} / {raw(r30['R1_decomp']['t_s']['ci95'])} / {raw(r30['R1_decomp']['t_cs']['ci95'])} | {r30['R1_decomp']['n']:,} |
| Same decomposition, given tenure and first-deal-year effects | {r30['R2_tenure']['t_v']['coef']:+.3f} / {r30['R2_tenure']['t_s']['coef']:+.3f} / {r30['R2_tenure']['t_cs']['coef']:+.3f} | {raw(r30['R2_tenure']['t_v']['ci95'])} / {raw(r30['R2_tenure']['t_s']['ci95'])} / {raw(r30['R2_tenure']['t_cs']['ci95'])} | {r30['R2_tenure']['n']:,} |
| Contrast, levels: adjusted exit rate, same regression as the composition-component levels row | {r30['R1t_total']['adj']['coef']:+.3f} | {raw(r30['R1t_total']['adj']['ci95'])} | {r30['R1t_total']['n']:,} |
| Contrast: adjusted percentile's own coefficient | {b1b['coef']:+.3f} | {raw(b1b['ci95'])} | {b1b['n']:,} |

## Panel D2. Same question at a fixed 36-month exit horizon in both periods (post window 2017-11 to 2020-10); levels
β on the composition component, or the named part, in 36-month exit-probability units. Partner-level rows include the adjusted rate, log deal count, gender, tenure, tenure², and first-deal-year effects unless noted. Deal-level rows include the partner's prior within-cell residual, log prior deals, gender, tenure at the deal date and its square, and year effects where no firm–year effect is present.
| Specification | β | 95% CI | n |
|---|---|---|---|
| **Composition component — preferred specification for this question** | **{fxA['F2t']['terrain']['coef']:+.3f}** | **{raw(fxA['F2t']['terrain']['ci95'])}** | {fxA['F2t']['n']:,} |
| Sector-within-year–stage part | {fxA['F2']['t_cs']['coef']:+.3f} | {raw(fxA['F2']['t_cs']['ci95'])} | {fxA['F2']['n']:,} |
| Adjusted exit rate's own coefficient, same regression as the preferred row | {fxA['F2t']['adj']['coef']:+.3f} | {raw(fxA['F2t']['adj']['ci95'])} | {fxA['F2t']['n']:,} |
| Without tenure and first-deal-year effects: composition component | {fxA['F1t']['terrain']['coef']:+.3f} | {raw(fxA['F1t']['terrain']['ci95'])} | {fxA['F1t']['n']:,} |
| Without tenure and first-deal-year effects: adjusted exit rate, same regression | {fxA['F1t']['adj']['coef']:+.3f} | {raw(fxA['F1t']['adj']['ci95'])} | {fxA['F1t']['n']:,} |
| Pre-period benchmark at a 72-month horizon | {fxB['F2t']['terrain']['coef']:+.3f} | {raw(fxB['F2t']['terrain']['ci95'])} | {fxB['F2t']['n']:,} |
| Home-firm fixed effects (minimum detectable effect {fxA['F3t']['terrain']['mde80']:.2f}; sector part {fxA['F3']['t_cs']['mde80']:.2f}) | {fxA['F3t']['terrain']['coef']:+.3f} | {raw(fxA['F3t']['terrain']['ci95'])} | {fxA['F3t']['n']:,} |
| Post-period deals in companies not backed pre-period | {fxA['F4t']['terrain']['coef']:+.3f} | {raw(fxA['F4t']['terrain']['ci95'])} | {fxA['F4t']['n']:,} |
| Leave-company-out benchmark | {fxA['F5t']['terrain']['coef']:+.3f} | {raw(fxA['F5t']['terrain']['ci95'])} | {fxA['F5t']['n']:,} |
| Both restrictions: companies not backed pre-period and leave-company-out benchmark | {fxA['F6t']['terrain']['coef']:+.3f} | {raw(fxA['F6t']['terrain']['ci95'])} | {fxA['F6t']['n']:,} |
| Post-period deals in companies the partner backed pre-period only | {e38['E_overlap_only']['F2t']['terrain']['coef']:+.3f} | {raw(e38['E_overlap_only']['F2t']['terrain']['ci95'])} | {e38['E_overlap_only']['F2t']['n']:,} |
| Pre-period restricted to deals whose 36-month window closes before the ranking date (deals through 2014-10; minimum detectable effect {fxD['exante_le_2014_10']['F2t']['terrain']['mde80']:.2f}) | {fxD['exante_le_2014_10']['F2t']['terrain']['coef']:+.3f} | {raw(fxD['exante_le_2014_10']['F2t']['terrain']['ci95'])} | {fxD['exante_le_2014_10']['F2t']['n']:,} |
| Pre-period restricted to deals from 2014-11 to 2017-10 | {fxD['mirror_2014_11_to_2017_10']['F2t']['terrain']['coef']:+.3f} | {raw(fxD['mirror_2014_11_to_2017_10']['F2t']['terrain']['ci95'])} | {fxD['mirror_2014_11_to_2017_10']['F2t']['n']:,} |
| Reweighted for selection out of post-period observation (inverse probability) | {e38['F_ipw_fixed']['F2t_ipw']['terrain']['coef']:+.3f} | {raw(e38['F_ipw_fixed']['F2t_ipw']['terrain']['ci95'])} | {e38['F_ipw_fixed']['F2t_ipw']['n']:,} |
| Exits recorded before the deal date excluded from the outcome | {e38['G_days_ge0']['F2t']['terrain']['coef']:+.3f} | {raw(e38['G_days_ge0']['F2t']['terrain']['ci95'])} | {e38['G_days_ge0']['F2t']['n']:,} |
| Tenure and rank from employment records (join date, title) instead of first-deal tenure; partners with a recorded join date | {fxJ['F2t_jobs']['terrain']['coef']:+.3f} | {raw(fxJ['F2t_jobs']['terrain']['ci95'])} | {fxJ['F2t_jobs']['n']:,} |
| Same partners, first-deal tenure controls (comparison) | {fxJ['F2t_TEN']['terrain']['coef']:+.3f} | {raw(fxJ['F2t_TEN']['terrain']['ci95'])} | {fxJ['F2t_TEN']['n']:,} |
| Home-firm fixed effects with employment-record tenure and rank | {fxJ['F3t_jobs']['terrain']['coef']:+.3f} | {raw(fxJ['F3t_jobs']['terrain']['ci95'])} | {fxJ['F3t_jobs']['n']:,} |
| Follow-on construct instead of exit (follow-on within 36 months, both periods) | {r30['R5_fixed_horizon']['terrain_fon']['coef']:+.3f} | {raw(r30['R5_fixed_horizon']['terrain_fon']['ci95'])} | {r30['R5_fixed_horizon']['n']:,} |
| Deal level, pooled: prior-year composition (sector part) → deal's within-cell outcome | {e34['D2_tenure_year']['t_cs_pr']['coef']:+.3f} | {raw(e34['D2_tenure_year']['t_cs_pr']['ci95'])} | {e34['D2_tenure_year']['n']:,} |
| Deal level, within firm–year: sector part (minimum detectable effect {e34['D3_firmyear_FE']['t_cs_pr']['mde80']:.2f}) | {e34['D3_firmyear_FE']['t_cs_pr']['coef']:+.3f} | {raw(e34['D3_firmyear_FE']['t_cs_pr']['ci95'])} | {e34['D3_firmyear_FE']['n']:,} |
| Deal level, within firm–year: composition component (minimum detectable effect {e34['D3t_total_firmyear_FE']['terrain_pr']['mde80']:.2f}) | {e34['D3t_total_firmyear_FE']['terrain_pr']['coef']:+.3f} | {raw(e34['D3t_total_firmyear_FE']['terrain_pr']['ci95'])} | {e34['D3t_total_firmyear_FE']['n']:,} |
| Deal level, within firm–year, deals in companies not previously backed by the partner: sector part | {e34['D3n_new_company_firmyear_FE']['t_cs_pr']['coef']:+.3f} | {raw(e34['D3n_new_company_firmyear_FE']['t_cs_pr']['ci95'])} | {e34['D3n_new_company_firmyear_FE']['n']:,} |
| Deal level, within partner: composition component (exploratory†) | {e34['D4t_total_partner_FE']['terrain_pr']['coef']:+.3f} | {raw(e34['D4t_total_partner_FE']['terrain_pr']['ci95'])} | {e34['D4t_total_partner_FE']['n']:,} |

## Panel E. By partner gender (female − male)
Percentile-scale rows are in fractions of the percentile scale (0.01 = one percentile point); *levels* rows are in exit-probability units (exit by sample end).
| Outcome | β | 95% CI | n |
|---|---|---|---|
| Composition component (raw − adjusted percentile) | {g1['coef']:+.3f} | {raw(g1['ci95'])} | {g1['n']:,} |
| Composition component, leave-one-out benchmark | {e27['gender_recheck']['LOO']['fp_to_wedge']['coef']:+.3f} | {raw(e27['gender_recheck']['LOO']['fp_to_wedge']['ci95'])} | {e27['gender_recheck']['LOO']['fp_to_wedge']['n']:,} |
| Post-period within-cell performance, levels | {g2['coef']:+.3f} | {raw(g2['ci95'])} | {g2['n']:,} |
| Post-period within-cell performance, levels, given composition | {g3['coef']:+.3f} | {raw(g3['ci95'])} | {g3['n']:,} |
| Pre-period within-cell performance, levels (adjusted exit rate) | {g5['coef']:+.3f} | {raw(g5['ci95'])} | {g5['n']:,} |
| Composition component, levels | {e36['G1_fp_to_component']['terrain']['fp']['coef']:+.3f} | {raw(e36['G1_fp_to_component']['terrain']['fp']['ci95'])} | {e36['G1_fp_to_component']['terrain']['n']:,} |
| Composition component, levels, given tenure and first-deal-year effects | {e36['G2_fp_to_component_tenure']['terrain']['fp']['coef']:+.3f} | {raw(e36['G2_fp_to_component_tenure']['terrain']['fp']['ci95'])} | {e36['G2_fp_to_component_tenure']['terrain']['n']:,} |
| Vintage / stage-within-year / sector-within-year–stage parts, levels | {e36['G1_fp_to_component']['t_v']['fp']['coef']:+.3f} / {e36['G1_fp_to_component']['t_s']['fp']['coef']:+.3f} / {e36['G1_fp_to_component']['t_cs']['fp']['coef']:+.3f} | {raw(e36['G1_fp_to_component']['t_v']['fp']['ci95'])} / {raw(e36['G1_fp_to_component']['t_s']['fp']['ci95'])} / {raw(e36['G1_fp_to_component']['t_cs']['fp']['ci95'])} | {e36['G1_fp_to_component']['t_v']['n']:,} |
| Composition component, levels, given employment-record tenure and rank | {e39['D_gender_given_jobs']['terrain']['jobs']['fp']['coef']:+.3f} | {raw(e39['D_gender_given_jobs']['terrain']['jobs']['fp']['ci95'])} | {e39['D_gender_given_jobs']['terrain']['jobs']['n']:,} |
| Composition component, levels, given rank only | {e39['D_gender_given_jobs']['terrain']['rank_only']['fp']['coef']:+.3f} | {raw(e39['D_gender_given_jobs']['terrain']['rank_only']['fp']['ci95'])} | {e39['D_gender_given_jobs']['terrain']['rank_only']['n']:,} |
| Implied contribution of composition to the post-period gap, levels, open horizon (Σ tenure-controlled part gap × tenure-controlled coefficient, same resamples; materiality band ±0.02; interval inside ±0.01) | {e36['G4_implied_netting']['total']['coef']:+.4f} | {raw(e36['G4_implied_netting']['total']['ci95'], 4)} | {e36['G4_implied_netting']['n']:,} |
| Same, fixed 36-month exit horizon (post window to 2020-10) | {e38['C_implied_netting_fixed']['total']['coef']:+.4f} | {raw(e38['C_implied_netting_fixed']['total']['ci95'], 4)} | {e38['C_implied_netting_fixed']['n']:,} |

*Partners with ≥5 attributed deals through 2017-10: {e5['n_partners']:,} ({e5['n_female']} women). Panels B–E: deal-count and gender controls (Panel B additionally pre-period early-stage share and sector breadth); investor-firm cluster bootstrap. Because the adjusted percentile is the raw percentile net of year–sector–stage cell benchmarks, the raw-percentile coefficient given the adjusted percentile equals the coefficient on their difference, the composition component (percentile correlation {col['rho_raw_adj']}, VIF {col['VIF_raw']:.1f}); Panel B's negative value is that composition coefficient. Panel D1 and Panel E percentile-scale rows: β per unit of the raw percentile (0.01 = one percentile point); *levels* rows: β per unit of the composition component in exit-probability units. Panel D2's control set is stated in its header; the follow-on-construct row reproduces P001-30 (a separate bootstrap in P001-33 returns the same point). Panel D2 rows below the preferred row are additional analyses. † Exploratory: identifies off within-partner changes in composition over time rather than off placement across partners; clustered by partner. Sources: P001-05, P001-18b, P001-23, P001-25, P001-26, P001-27, P001-28, P001-29, P001-30, P001-31, P001-33, P001-34, P001-36, P001-38, P001-39.*
""")

e6 = p6["estimates"]
e17 = p17["estimates"]
e19 = p19["estimates"]
s1 = e24["S1|처치 단독"]            # P001-24: 수렴한 유일 사양 (converged=True)
cnt = e24.get("counts", {})        # n_allf 등 — P001-24 재실행 후 채워진다
pf, pm = e6["p_fp_given_ff"][0], e6["p_fp_given_mf"][0]
w("table9.md", f"""# Table 9. The female-partner channel along the financing ladder (NA+EU)
| Stage | P(FP given FF deal) % | P(FP given no observed female founder) % |
|---|---|---|
| Early (pre-seed/seed/angel) | {pf[0]} | {pm[0]} |
| Series A | {pf[1]} | {pm[1]} |
| Series B and beyond | {pf[2]} | {pm[2]} |

| Differential early−late slope (FF − other) | Estimate (pp) | 95% CI |
|---|---|---|
| Baseline | {e6['diff_slope'][0]:+.2f} | {pp(e6['diff_slope'][1])} |
| Reweighted for stage-varying determinability | {e17['slope_reweighted'][0]*100:+.2f} | {pp(e17['slope_reweighted'][1])} |
| Majority-female founder teams | {e17['slope_majority_female'][0]*100:+.2f} | {pp(e17['slope_majority_female'][1])} |
| Reallocation counterfactual: late-stage FF–FP contacts | +{e6['counterfactual_late_ff_fp_gain_pct']}% (from {e6['n_ff_late_fp_deals']} deals) | |

## Between-firm check (Snellman–Solal-style): female-founded companies' first rounds
| Lead-team definition and sample | Design | Estimate | 95% CI | n / events (treated) |
|---|---|---|---|---|
| All attributed lead partners female vs all male, mixed teams excluded; US, seed and Series A, 2010–18 | Cox proportional hazards on exit, treatment only | HR {s1['hazard_ratio']:.3f} (log-hazard {s1['beta_allf']:+.3f}) | {raw(s1['ci95_beta'])} on log hazard | {s1['n']:,} / {s1['n_event']} ({cnt.get('n_allf', '—')}) |
| Alternative lead-team definition: any attributed lead partner female (pools mixed teams); NA+EU, 2010–20 | LPM follow-on within 36m, year FE | {e19['lead_fp_attr']['raw_yearFE'][0]*100:+.2f} pp | {pp(e19['lead_fp_attr']['raw_yearFE'][1])} | {e19['lead_fp_attr']['raw_yearFE'][2]:,} |
| Alternative: lead-firm female-partner share above median; NA+EU, 2010–20 | LPM follow-on within 36m, year FE | {e19['lead_fp_share_hi']['raw_yearFE'][0]*100:+.2f} pp | {pp(e19['lead_fp_share_hi']['raw_yearFE'][1])} | {e19['lead_fp_share_hi']['raw_yearFE'][2]:,} |

*n = {e6['n']:,} (ladder). The first between-firm row is the targeted comparison; Cox specifications adding year, sector, and stage terms did not meet the convergence criterion at {cnt.get('n_allf', '—')} treated observations (sparse year–sector cells) and are not reported. The alternative definitions pool all-female with mixed lead teams — the highest-performing cell in Snellman and Solal (2023) — and are reported as alternatives, not as estimates of the all-female contrast. Sources: P001-06, P001-17, P001-24, P001-19.*
""")

A7, B7 = p7["estimates"]["A_e1_sector"], p7["estimates"]["B_e2_fon"]
rows9a = "\n".join(f"| {k} | {v[0]*100:+.2f} | {pp(v[1])} | {v[2]:,} |" for k, v in A7.items())
rows9b = "\n".join(f"| {k} | {v[0]*100:+.2f} | {pp(v[1])} | {v[2]:,} |" for k, v in B7.items())
e8 = p8["estimates"]
e16 = p16["estimates"]
a4, a5, a7 = e23["A4_solo"], e23["A5_cv_auc"], e23["A7_receiving_firm"]   # P001-23 진단
w("tableIA2.md", f"""# Appendix Table IA.2. Robustness and measurement diagnostics
## Panel A. Sector-layer matching coefficient across specifications (rows re-estimated in a separate bootstrap run; the canonical baseline interval is Table 2)
| Row | Estimate (pp) | 95% CI | n |
|---|---|---|---|
{rows9a}
| stage layer, generic labels excluded | {e16['e1_stage_excl_generic'][0]*100:+.2f} | {pp(e16['e1_stage_excl_generic'][1])} | {e16['e1_stage_excl_generic'][2]:,} |

## Panel B. Covariate-adjusted follow-on estimates across specifications
| Row | Estimate (pp) | 95% CI | n |
|---|---|---|---|
{rows9b}

## Panel C. Measurement diagnostics
| | |
|---|---|
| Firm attribution rate ~ female-partner share (correlation) | {e8['r2_attr_fp_corr'][0]} {raw(e8['r2_attr_fp_corr'][1])} |
| Attribution × gender drift correlation (annual) | {e8['drift_corr']} |
| Deal-level salience fingerprint: FF × firm FP-share → P(attributed) | {e16['attr_ff_x_fpshare'][0]*100:+.2f}pp {pp(e16['attr_ff_x_fpshare'][1])} (varies within firms with the deal's founder gender, so it is not absorbed by firm fixed effects; Appendix IA.2) |
| Generic stage-label share: FP / MP deals | {e16['generic_share_fp']*100:.1f}% / {e16['generic_share_mp']*100:.1f}% |
| Founder-gender determinable vs not: US / early / vintage | {r4['us_diff_pp']:+.1f}pp / {r4['early_diff_pp']:+.1f}pp / {r4['year_diff']:+.2f}y |

## Panel D. Rank-measure diagnostics and external-pricing sensitivity
| | |
|---|---|
| Raw vs adjusted percentile: correlation / VIF / share of raw variation independent of controls | {col['rho_raw_adj']} / {col['VIF_raw']:.2f} / {col['identifying_share']*100:.1f}% |
| Raw percentile alone → mobility; → spinout | {a4['move|raw 단독']['coef']:+.3f} {raw(a4['move|raw 단독']['ci95'])}; {a4['spin|raw 단독']['coef']:+.3f} {raw(a4['spin|raw 단독']['ci95'])} |
| Adjusted percentile alone → mobility; → spinout | {a4['move|adj 단독']['coef']:+.3f} {raw(a4['move|adj 단독']['ci95'])}; {a4['spin|adj 단독']['coef']:+.3f} {raw(a4['spin|adj 단독']['ci95'])} |
| Out-of-sample AUC (5-fold), raw minus adjusted: mobility; spinout | {a5['move|raw 단독']-a5['move|adj 단독']:+.4f}; {a5['spin|raw 단독']-a5['spin|adj 단독']:+.4f} |
| Composition → fund formation: with pre-period early-stage share and sector breadth as controls / without | {lp['lp_any|wedge+adj']['coef']:+.3f} {raw(lp['lp_any|wedge+adj']['ci95'])} / {ri['lp_any']['coef']:+.3f} {raw(ri['lp_any']['ci95'])} |
| Composition → receiving-firm quality: with / without | {a7['recv_q|wedge+adj']['coef']:+.3f} {raw(a7['recv_q|wedge+adj']['ci95'])} / {ri['recv_q']['coef']:+.3f} {raw(ri['recv_q']['ci95'])} |
| Post-period observation ← composition component (LPM; percentile-point units) | {e28['S1_selection_on_wedge']['coef']:+.3f} {raw(e28['S1_selection_on_wedge']['ci95'])}; n = {e28['S1_selection_on_wedge']['n']:,} |
| Post-period observation ← vintage / stage-within-year / sector-within-year–stage components (levels) | {r30['R7_selection_decomp']['t_v']['coef']:+.3f} {raw(r30['R7_selection_decomp']['t_v']['ci95'])} / {r30['R7_selection_decomp']['t_s']['coef']:+.3f} {raw(r30['R7_selection_decomp']['t_s']['ci95'])} / {r30['R7_selection_decomp']['t_cs']['coef']:+.3f} {raw(r30['R7_selection_decomp']['t_cs']['ci95'])} |
| Post-period observation ← tenure (years since first attributed deal), given components | {r30['R7b_selection_tenure']['tenure']['coef']:+.4f} {raw(r30['R7b_selection_tenure']['tenure']['ci95'], 4)} |
| Composition → log fund size: with pre-period late-stage share as control / late-stage share own coefficient | {t2['lp_amt']['with_late_ctrl']['coef']:+.3f} {raw(t2['lp_amt']['with_late_ctrl']['ci95'])} / {t2['lp_amt']['late_sh_own']['coef']:+.3f} {raw(t2['lp_amt']['late_sh_own']['ci95'])} |
| Log fund size ← stage part / ← sector part given late-stage share / ← sector part given late-stage share and tenure | {e37['lp_amt']['L1']['t_s']['coef']:+.3f} {raw(e37['lp_amt']['L1']['t_s']['ci95'])} / {e37['lp_amt']['L2']['t_cs']['coef']:+.3f} {raw(e37['lp_amt']['L2']['t_cs']['ci95'])} / {e37['lp_amt']['L3']['t_cs']['coef']:+.3f} {raw(e37['lp_amt']['L3']['t_cs']['ci95'])}; n = {e37['lp_amt']['L1']['n']} |
| Fund formation ← sector part given late-stage share and tenure | {e37['lp_any']['L3']['t_cs']['coef']:+.3f} {raw(e37['lp_any']['L3']['t_cs']['ci95'])}; n = {e37['lp_any']['L3']['n']} |
| Minimum detectable effects (80% power), composition component / sector part: open-horizon home-firm FE; fixed-horizon home-firm FE; deal-level firm–year FE | {e31['A_mde']['R4t_total_firmFE']['terrain']['mde80']:.3f} / {e31['A_mde']['R4_firm_FE']['t_cs']['mde80']:.3f}; {fxA['F3t']['terrain']['mde80']:.3f} / {fxA['F3']['t_cs']['mde80']:.3f}; {e34['D3t_total_firmyear_FE']['terrain_pr']['mde80']:.3f} / {e34['D3_firmyear_FE']['t_cs_pr']['mde80']:.3f} |
| Three-part multiplicity adjustment (maximum absolute t) of the open-horizon sector part: two-sided p, adjusted / unadjusted | {e31['D_multiplicity_R1']['t_cs']['p_two_maxT_adj']:.3f} / {e31['D_multiplicity_R1']['t_cs']['p_two_unadj']:.3f} |
| Within-firm share of variance in the home-firm FE sample: composition component / sector part | {e31['C_within_share']['terrain']['within_share']:.2f} / {e31['C_within_share']['t_cs']['within_share']:.2f} |
| Mundlak decomposition, open horizon, within-firm / between-firm coefficient: sector part | {e32['W1_mundlak']['dev_t_cs']['coef']:+.3f} {raw(e32['W1_mundlak']['dev_t_cs']['ci95'])} / {e32['W1_mundlak']['fm_t_cs']['coef']:+.3f} {raw(e32['W1_mundlak']['fm_t_cs']['ci95'])} |
| Same, composition component | {e32['W3_total']['dev_terrain']['coef']:+.3f} {raw(e32['W3_total']['dev_terrain']['ci95'])} / {e32['W3_total']['fm_terrain']['coef']:+.3f} {raw(e32['W3_total']['fm_terrain']['ci95'])} | 
| Same, composition component, within-minus-between contrast | {e32['W3_contrast']['coef']:+.3f} {raw(e32['W3_contrast']['ci95'])} |
| Mundlak decomposition, fixed 36-month exit horizon, within-firm / between-firm / contrast: composition component | {e38['B3_mundlak_total_fixed']['dev_terrain']['coef']:+.3f} {raw(e38['B3_mundlak_total_fixed']['dev_terrain']['ci95'])} / {e38['B3_mundlak_total_fixed']['fm_terrain']['coef']:+.3f} {raw(e38['B3_mundlak_total_fixed']['fm_terrain']['ci95'])} / {e38['B3_contrast_terrain']['coef']:+.3f} {raw(e38['B3_contrast_terrain']['ci95'])}; n = {e38['B3_mundlak_total_fixed']['n']:,} |
| Same, adding the home firm's fund count, cumulative fund size and fund age at the sample split (Crunchbase funds; SEC Form D tier-1 filings): between-firm coefficient / contrast; R² of the firm-mean composition on those variables | {e58['P2_between_firm_decomposition']['firm_both']['fm_terrain']['coef']:+.3f} {raw(e58['P2_between_firm_decomposition']['firm_both']['fm_terrain']['ci95'])} / {e58['P2_between_firm_decomposition']['firm_both']['contrast_within_minus_between']['coef']:+.3f} {raw(e58['P2_between_firm_decomposition']['firm_both']['contrast_within_minus_between']['ci95'])}; R² {e58['P2_between_firm_decomposition']['fm_terrain_on_firm_vars']['r2']:.3f} |
| Same, sector part | {e38['B1_mundlak_parts_fixed']['dev_t_cs']['coef']:+.3f} {raw(e38['B1_mundlak_parts_fixed']['dev_t_cs']['ci95'])} / {e38['B1_mundlak_parts_fixed']['fm_t_cs']['coef']:+.3f} {raw(e38['B1_mundlak_parts_fixed']['fm_t_cs']['ci95'])} / {e38['B1_contrast_tcs']['coef']:+.3f} {raw(e38['B1_contrast_tcs']['ci95'])} |
| Follow-on vs exit benchmarks: weighted correlation of year–sector–stage cell means (follow-on, 36-month exit) / (follow-on, exit by sample end); range of stage-level rates excluding private equity, follow-on / 36-month exit | {e38['A_stage_rates']['cell_corr_fon_exit3_weighted']:+.2f} / {e38['A_stage_rates']['cell_corr_fon_exit_ever_weighted']:+.2f}; {e38['A_stage_rates']['fon_range_excl_pe']:.3f} / {e38['A_stage_rates']['exit3_range_excl_pe']:.3f} |
| Employment-record tenure: share of partners with a home-firm join date / correlation with first-deal tenure / share attributed before the recorded join date / female−male tenure difference (years) | {e39['A_coverage']['share_join_date']:.3f} / {e39['A_coverage']['corr_tenure_j_vs_first_deal']:+.2f} / {e39['A_coverage']['first_deal_minus_join_years']['share_negative']:.3f} / {e39['D_gender_given_jobs']['rank_gap_female_minus_male_tenure_j']:+.2f} |
| Standardized coefficients in one regression, composition component / adjusted rate: fixed horizon with tenure controls; open horizon | {fxA['F2t']['terrain']['beta_std']:+.3f} / {e38['H_standardized']['fixed_F2t']['adj']['beta_std']:+.3f}; {e38['H_standardized']['open_R1t']['terrain']['beta_std']:+.3f} / {e38['H_standardized']['open_R1t']['adj']['beta_std']:+.3f} |
| Split-half agreement at the fixed horizon (upper bound on reliability): sector part / composition component / adjusted rate | {e38['I_split_half_agreement_exit3']['t_cs']['rho_SB']:.2f} / {e38['I_split_half_agreement_exit3']['terrain']['rho_SB']:.2f} / {e38['I_split_half_agreement_exit3']['adj']['rho_SB']:.2f} |
| 36-month exit: share of positives recorded before the deal date, pre / post; post-period base rate with those excluded | {e38['G_days_ge0']['share_negative_lag_among_exit3_pre']:.3f} / {e38['G_days_ge0']['share_negative_lag_among_exit3_post']:.3f}; {e38['G_days_ge0']['base_post_pos']:.4f} |
| Post-period observation ← vintage part / employment-record tenure, given components and rank | {e39['E_selection']['R7_jobs']['t_v']['coef']:+.3f} {raw(e39['E_selection']['R7_jobs']['t_v']['ci95'])} / {e39['E_selection']['R7_jobs']['tenure_j']['coef']:+.4f} {raw(e39['E_selection']['R7_jobs']['tenure_j']['ci95'], 4)}; n = {e39['E_selection']['R7_jobs']['n']:,} |
| Share of the fixed-horizon partner sample observed in the post period | {e38['F_ipw_fixed']['share_observed']:.3f} |
| Pre-period deals entering the fixed-horizon panel whose 36-month window closes after the ranking date / whose outcome is undetermined at that date | {e47['A_exante_share']['share_window_closes_after_cut_panel']:.3f} / {e47['A_exante_share']['share_outcome_undetermined_at_cut_panel']:.3f} |
| Correlation of tenure (years since first attributed deal) with the composition component, open horizon | {r30['corr_tenure_terrain']:.2f} |
| Deal-level firm–year FE sample: deals / firms | {e34['D3_firmyear_FE']['n']:,} / {e34['D3_firmyear_FE']['n_firms']:,} |
| Fixed-horizon Mundlak: correlation of firm-mean composition with firm-mean adjusted rate / partners who are the only sampled partner at their firm | {e47['B_firm_means']['corr_fm_terrain_fm_adj_postsample']:+.3f} / {e47['C_singletons']['n_singleton_at_firm']} of {e47['C_singletons']['n_post_partners']:,} |
| Identifying variation of the Table 3 peer comparison (firm × year × sector), NA+EU / global: cells with both partner genders among FF deals / deals in them / share of FF deals | {q40n['n_mixed_cells']} / {q40n['n_deals_mixed']} / {q40n['share_deals_mixed']:.3f}; {q40g['n_mixed_cells']} / {q40g['n_deals_mixed']} / {q40g['share_deals_mixed']:.3f} |
| Peer availability, NA+EU: share of female-partner FF deals with a same-cell male-partner FF deal / female partners with at least one such deal (of {e40['NAEU']['n_female_partners']}) / same share across all deals | {q40n['share_fp_deals_with_peer']:.3f} / {q40n['n_female_partners_with_peer']} / {e40['NAEU_all_deals_fp_peer_share_cell_cat']:.3f} |
| Peer-comparison estimate re-estimated on the mixed cells only, NA+EU / global (pp) | {q40n['beta_mixed_pp']:+.2f} / {q40g['beta_mixed_pp']:+.2f} (identical to the full-sample estimates) |
| Leave-one-cell-out jackknife of the peer-comparison estimate: maximum shift (pp), NA+EU / global; any value outside the bootstrap interval | {q40n['jackknife']['max_abs_shift_pp']:.2f} / {q40g['jackknife']['max_abs_shift_pp']:.2f}; {'yes' if (q40n['jackknife']['any_outside_ci'] or q40g['jackknife']['any_outside_ci']) else 'no'} |
| Within-cell random reassignment of partner gender ({q40n['placebo']['n']} draws): 95th percentile of the absolute estimate (pp), NA+EU / global; share of draws at or beyond the estimate | {q40n['placebo']['p95_abs_pp']:.2f} / {q40g['placebo']['p95_abs_pp']:.2f}; {q40n['placebo']['share_ge_headline']:.3f} / {q40g['placebo']['share_ge_headline']:.3f} |
| Same for the + stage cells, NA+EU: cells / deals / placebo 95th percentile / share at or beyond | {q40s['n_mixed_cells']} / {q40s['n_deals_mixed']} / {q40s['placebo']['p95_abs_pp']:.2f} / {q40s['placebo']['share_ge_headline']:.3f} |
| Deal level, fixed horizon, without the partner's prior within-cell residual as a control — within firm–year: sector part / composition component; pooled: sector part | {e41['no_adjpr']['D3']['t_cs_pr']['coef']:+.3f} {raw(e41['no_adjpr']['D3']['t_cs_pr']['ci95'])} / {e41['no_adjpr']['D3t']['terrain_pr']['coef']:+.3f} {raw(e41['no_adjpr']['D3t']['terrain_pr']['ci95'])}; {e41['no_adjpr']['D2']['t_cs_pr']['coef']:+.3f} {raw(e41['no_adjpr']['D2']['t_cs_pr']['ci95'])} |
| Deal level, open-horizon construct (exit by sample end), within firm–year: sector part | {e34['D0fe_firmyear_exit_ever']['t_cs_pr']['coef']:+.3f} {raw(e34['D0fe_firmyear_exit_ever']['t_cs_pr']['ci95'])}; n = {e34['D0fe_firmyear_exit_ever']['n']:,} |
| Split-half agreement (Spearman–Brown; halves share cell benchmarks, so an upper bound on reliability): vintage / stage / sector parts / composition component / adjusted rate | {e35['A_reliability']['t_v']['rho_SB']:.2f} / {e35['A_reliability']['t_s']['rho_SB']:.2f} / {e35['A_reliability']['t_cs']['rho_SB']:.2f} / {e35['A_reliability']['terrain']['rho_SB']:.2f} / {e35['A_reliability']['adj']['rho_SB']:.2f} |
| Fixed exit horizon: standard deviation of the vintage part / standardized composition coefficient (sd units) | {fxA['sd_t_v']:.4f} / {fxA['F2t']['terrain']['beta_std']:+.3f} |
| Deal-level sample: firm–years with ≥ 2 partners / share of post-period deals in companies the partner backed pre-period (fixed-horizon window) | {e34['desc_exit3']['n_firm_years_multi']:,} / {fxA['share_repeat_company_post']:.3f} |
| Spinout population counts, leave-one-out partner sample: spinouts / fund close observed / fund size observed | {e37['counts']['spin']} / {e37['counts']['lp_any_pos']} / {e37['counts']['lp_amt_obs']} (Table 7 Panel C uses the baseline-benchmark sample: 380 / 221 / 197) |

## Panel E. Region split and the identifying base of the peer comparison
| | United States | North America (US + Canada) | Europe (24 countries) |
|---|---|---|---|
| Peer-comparison exit gap, firm × year × sector (pp); mixed cells / deals | {e48['USA']['A_ladder']['pluscat']['coef_pp']:+.2f} {raw(e48['USA']['A_ladder']['pluscat']['ci95_pp'],2)}; {e48['USA']['A_ladder']['pluscat']['n_mixed_cells']} / {e48['USA']['A_ladder']['pluscat']['n_deals_mixed']} | {e48['NA']['A_ladder']['pluscat']['coef_pp']:+.2f} {raw(e48['NA']['A_ladder']['pluscat']['ci95_pp'],2)}; {e48['NA']['A_ladder']['pluscat']['n_mixed_cells']} / {e48['NA']['A_ladder']['pluscat']['n_deals_mixed']} | not computable (within-cell exit variation zero); {e48['EU24']['A_ladder']['pluscat']['n_mixed_cells']} / {e48['EU24']['A_ladder']['pluscat']['n_deals_mixed']} |
| Within-cell reassignment placebo, 95th percentile of \|β\| (pp) | {e48['USA']['A_ladder']['pluscat']['placebo_p95_abs_pp']} | {e48['NA']['A_ladder']['pluscat']['placebo_p95_abs_pp']} | — |
| + stage cell gap (pp) | {e48['USA']['A_ladder']['plusstage']['coef_pp']:+.2f} {raw(e48['USA']['A_ladder']['plusstage']['ci95_pp'],2)} | {e48['NA']['A_ladder']['plusstage']['coef_pp']:+.2f} {raw(e48['NA']['A_ladder']['plusstage']['ci95_pp'],2)} | not computable |
| Follow-on within 36 months, + stage cell, FP coefficient (pp) | {e48['USA']['B_adjudication_stage_cell']['fon']['coef_pp']:+.2f} {raw(e48['USA']['B_adjudication_stage_cell']['fon']['ci95_pp'],2)} | {e48['NA']['B_adjudication_stage_cell']['fon']['coef_pp']:+.2f} {raw(e48['NA']['B_adjudication_stage_cell']['fon']['ci95_pp'],2)} | not computable |
| Fixed-horizon composition coefficient (Table 7 Panel D2 preferred specification); partners | {e48['USA']['C_fixed_horizon']['F2t']['terrain']['coef']:+.3f} {raw(e48['USA']['C_fixed_horizon']['F2t']['terrain']['ci95'])}; {e48['USA']['C_fixed_horizon']['n_partners']:,} | {e48['NA']['C_fixed_horizon']['F2t']['terrain']['coef']:+.3f} {raw(e48['NA']['C_fixed_horizon']['F2t']['terrain']['ci95'])}; {e48['NA']['C_fixed_horizon']['n_partners']:,} | {e48['EU24']['C_fixed_horizon']['F2t']['terrain']['coef']:+.3f} {raw(e48['EU24']['C_fixed_horizon']['F2t']['terrain']['ci95'])}; {e48['EU24']['C_fixed_horizon']['n_partners']:,} |

| Identifying base of the Table 3 peer comparison | NA+EU, firm × year × sector | NA+EU, + stage | Global, firm × year × sector |
|---|---|---|---|
| Mixed cells that are co-attributions on a single round (share) | {e49['NAEU']['cell_cat']['n_single_round_cells']} ({e49['NAEU']['cell_cat']['share_single_round_cells']:.2f}) | {e49['NAEU']['cell_stage']['n_single_round_cells']} ({e49['NAEU']['cell_stage']['share_single_round_cells']:.2f}) | {e49['GLOBAL']['cell_cat']['n_single_round_cells']} ({e49['GLOBAL']['cell_cat']['share_single_round_cells']:.2f}) |
| Cells with within-cell exit variation / deals in them | {e49['NAEU']['cell_cat']['n_cells_exit_var_pos']} / {e49['NAEU']['cell_cat']['n_deals_exit_var_pos']} | {e49['NAEU']['cell_stage']['n_cells_exit_var_pos']} / {e49['NAEU']['cell_stage']['n_deals_exit_var_pos']} | {e49['GLOBAL']['cell_cat']['n_cells_exit_var_pos']} / {e49['GLOBAL']['cell_cat']['n_deals_exit_var_pos']} |
| Share of identifying variance (Σx̃²) from single-round cells | {e49['NAEU']['cell_cat']['dilution_share_sxx_single_round']:.2f} | {e49['NAEU']['cell_stage']['dilution_share_sxx_single_round']:.2f} | {e49['GLOBAL']['cell_cat']['dilution_share_sxx_single_round']:.2f} |
| Exit gap on multi-round cells only (pp); MDE; placebo 95th percentile | {e49['NAEU']['cell_cat']['beta_multi_exit_ever_pp']:+.2f} {raw(e49['NAEU']['cell_cat']['ci_multi_exit_ever_pp'],2)}; {e49['NAEU']['cell_cat']['mde_multi_exit_ever_pp']}; {e49['NAEU']['cell_cat']['placebo_p95_multi_exit_ever_pp']} | {e49['NAEU']['cell_stage']['beta_multi_exit_ever_pp']:+.2f} {raw(e49['NAEU']['cell_stage']['ci_multi_exit_ever_pp'],2)}; {e49['NAEU']['cell_stage']['mde_multi_exit_ever_pp']}; {e49['NAEU']['cell_stage']['placebo_p95_multi_exit_ever_pp']} | {e49['GLOBAL']['cell_cat']['beta_multi_exit_ever_pp']:+.2f} {raw(e49['GLOBAL']['cell_cat']['ci_multi_exit_ever_pp'],2)}; {e49['GLOBAL']['cell_cat']['mde_multi_exit_ever_pp']}; {e49['GLOBAL']['cell_cat']['placebo_p95_multi_exit_ever_pp']} |
| Follow-on gap on multi-round cells only (pp) | {e49['NAEU']['cell_cat']['beta_multi_fon_pp']:+.2f} {raw(e49['NAEU']['cell_cat']['ci_multi_fon_pp'],2)} | {e49['NAEU']['cell_stage']['beta_multi_fon_pp']:+.2f} {raw(e49['NAEU']['cell_stage']['ci_multi_fon_pp'],2)} | {e49['GLOBAL']['cell_cat']['beta_multi_fon_pp']:+.2f} {raw(e49['GLOBAL']['cell_cat']['ci_multi_fon_pp'],2)} |

| Identifying base of the Table 4 hazard (cell × elapsed-year effects) | Value |
|---|---|
| Cells with female-partner variation / rows; share that are co-attributions on a single round | {e50['A_cells']['n_mixed_cells']:,} / {e50['A_cells']['n_rows_mixed']:,}; {e50['A_cells']['share_single_round_cells']:.2f} |
| Cells with within-cell exit variation (share); exit events in them | {e50['A_cells']['n_cells_outcome_var_pos']} ({e50['A_cells']['share_cells_outcome_var_pos']:.2f}); {e50['A_cells']['n_exit_events_varpos']} |
| Share of identifying variance from single-round cells | {e50['A_cells']['dilution_share_sxx_single_round']:.2f} |
| Annual hazard gap, all cells, re-estimated in this audit run with its own bootstrap (pp/yr; the reference estimate is Table 5, Panel A); within ±25% of the {e50['A_cells']['base_hazard']*100:.2f}% base | {e50['B_hazard_gap']['full']['coef_pp']:+.3f} {raw(e50['B_hazard_gap']['full']['ci95_pp'],2)}; {'yes' if e50['B_hazard_gap']['full']['within_quarter_of_base'] else 'no'} |
| Annual hazard gap, multi-round cells only (pp/yr); MDE; within ±25% of base | {e50['B_hazard_gap']['multi_round_cells']['coef_pp']:+.3f} {raw(e50['B_hazard_gap']['multi_round_cells']['ci95_pp'],2)}; {e50['B_hazard_gap']['multi_round_cells']['mde80_pp']:.2f}; {'yes' if e50['B_hazard_gap']['multi_round_cells']['within_quarter_of_base'] else 'no'} |

*Panel A 'baseline' re-estimates the Table 2 sector layer inside the robustness battery (separate bootstrap run; point identical, interval differs by resampling). Panel D: composition-component coefficients are in exit-probability units per unit of the component (0.01 of the percentile scale = one percentile point) unless a row states percentile-point units; fund-size coefficients are log points per unit of the component. Sources: P001-07, P001-08, P001-16, P001-22, P001-23, P001-25, P001-28, P001-29, P001-30, P001-31, P001-32, P001-33, P001-34, P001-35, P001-37, P001-38, P001-39, P001-40, P001-41, P001-48, P001-49, P001-50. Solo-attribution rows lose precision (negative_results/W4_notes.md); points consistent with baselines.*
""")


def rw(r, k, d=3):
    return f"{r[k]['coef']:+.{d}f} | {raw(r[k]['ci95'], d)}"


r42 = e42["B_reup_conditional"]["reg"]; a42 = e42["A_sample"]
b46 = e46["FF_cell_cat_pre"]; b46s = e46["FF_cell_stage_pre"]; b46a = e46["ALL_cell_stage_pre"]
COVLAB = {"age": "Company age at deal (years)", "ln_prior_rounds": "log(1 + prior equity rounds)", "ln_prior_capital": "log(1 + prior capital raised)",
          "emp_band": "Employee-count band (1–9)", "prev_investor_count": "Investor count on the previous round", "n_founders": "Number of founders",
          "n_female_founders": "Number of female founders", "founder_degree_share": "Share of founders with a recorded degree", "serial_share": "Share of serial founders", "hq_us": "Headquartered in the United States"}
b52 = e52["FF_cell_cat_pre"]["by_cov"]; b52s = e52["FF_cell_stage_pre"]["by_cov"]
def _mu(v):
    return "not identified" if not v or v.get("coef_multi") is None else f"{v['std_diff_multi']:+.2f} {raw(v['ci95_multi_sd_units'], 2)}; MDE {v['mde80_multi_sd']:.2f}"
rows46 = "\n".join(f"| {COVLAB[c]} | {v['coef']:+.3f} | {raw(v['ci95'])} | {v['std_diff']:+.3f} | {v['mde80_std']:.2f} | {b52[c]['dilution_share_sxx_single_round'] if b52.get(c) else float('nan'):.2f} | {_mu(b52.get(c))} | {_mu(b52s.get(c))} | {v['n']:,} |"
                   for c, v in b46["by_cov"].items() if v)
a43 = e43["A_sample"]; d1 = e43["D1_assignment"]; d2 = e43["D2_future_firm_placebo"]; d1b = e43["D1b_levels"]; d3b = e43["D3b_placebo_levels"]; d4 = e43["D4_direction"]
a44 = e44["A_sample"]; b44 = e44["B_colleague_ff_share"]; b44a = e44["B2_all_deals_ff_share"]; c44 = e44["C_placebos"]
m1 = e45["M1_attrition"]; m2 = e45["M2_firm_followon"]; m3 = e45["M3_partner_reattribution"]; m4 = e45["M4_entrants"]
_t10 = f"""# (split below)
## Panel A. Within-round comparison of co-investors: rounds with both a female- and a male-attributed investor (NA+EU companies, deals 2010-01 to 2020-10)
Outcome varies across investors in the same round; company, sector, stage, vintage, founder team, and syndicate are fixed by construction. Round fixed effects; investor experience control; company-cluster bootstrap. β is the female-partner slope in female-founded rounds; "other" is the slope in other rounds; "difference" is female-founded minus other.
| Outcome | β (female-founded rounds) | 95% CI | β (other rounds) | 95% CI | Difference | 95% CI | n rows / companies |
|---|---|---|---|---|---|---|---|
| Firm re-invests in the company's next round (next round within 36 months; conditional) | {rw(r42, 'b_FF')} | {rw(r42, 'b_other')} | {rw(r42, 'b_diff')} | {r42['n']:,} / {r42['n_firms']:,} |
| Same, unconditional (no next round coded as zero) | {rw(e42['C_reup_unconditional'], 'b_FF')} | {rw(e42['C_reup_unconditional'], 'b_other')} | {rw(e42['C_reup_unconditional'], 'b_diff')} | {e42['C_reup_unconditional']['n']:,} / {e42['C_reup_unconditional']['n_firms']:,} |
| Same partner attributed on the next round, given the firm re-invests | {rw(e42['D_repartner']['cond_on_reup'], 'b_FF')} | {rw(e42['D_repartner']['cond_on_reup'], 'b_other')} | {rw(e42['D_repartner']['cond_on_reup'], 'b_diff')} | {e42['D_repartner']['cond_on_reup']['n']:,} / {e42['D_repartner']['cond_on_reup']['n_firms']:,} |
| Lead-investor flag on the round (recorded on {e42['E_lead']['lead_recorded_share']*100:.0f} percent of rows) | {rw(e42['E_lead']['lead_within_round'], 'b_FF')} | {rw(e42['E_lead']['lead_within_round'], 'b_other')} | {rw(e42['E_lead']['lead_within_round'], 'b_diff')} | {e42['E_lead']['lead_within_round']['n']:,} / {e42['E_lead']['lead_within_round']['n_firms']:,} |
| Reverse placebo: firm invested in the company's previous round | {rw(e42['F_reverse_placebo'], 'b_FF')} | {rw(e42['F_reverse_placebo'], 'b_other')} | {rw(e42['F_reverse_placebo'], 'b_diff')} | {e42['F_reverse_placebo']['n']:,} / {e42['F_reverse_placebo']['n_firms']:,} |

*Variants of the re-investment margin, female-founded rounds only (P001-51; β = female-partner slope; company-cluster bootstrap unless stated):*
| Variant | β | 95% CI | MDE80 | within ±5 pp | n rows / clusters |
|---|---|---|---|---|---|
| Any-female attribution — initial run (400 draws) | {e51['A_baseline']['fp']['coef']*100:+.2f} | {pp(e51['A_baseline']['fp']['ci95'])} | {e51['A_baseline']['fp']['mde80']*100:.2f} | {'yes' if e51['A_baseline']['fp']['within_pm0.05'] else 'no'} | {e51['A_baseline']['n']:,} / {e51['A_baseline']['n_clusters']:,} |
| Female-only attribution — initial run (400 draws; {e51['B_treatment_definition']['n_mixed_attr_rows_dropped']} rows attributed to both a woman and a man dropped, {e51['A_baseline']['n'] - e51['B_treatment_definition']['female_only']['n']} rows in all once rounds left without a female–male contrast fall out) | {e51['B_treatment_definition']['female_only']['fp']['coef']*100:+.2f} | {pp(e51['B_treatment_definition']['female_only']['fp']['ci95'])} | {e51['B_treatment_definition']['female_only']['fp']['mde80']*100:.2f} | {'yes' if e51['B_treatment_definition']['female_only']['fp']['within_pm0.05'] else 'no'} | {e51['B_treatment_definition']['female_only']['n']:,} / {e51['B_treatment_definition']['female_only']['n_clusters']:,} |
| **Any-female attribution — reference run (2,000 draws)** | {e59['E_within_round_2000']['any_female']['fp']['coef']*100:+.2f} | {pp(e59['E_within_round_2000']['any_female']['fp']['ci95'])} | {e59['E_within_round_2000']['any_female']['fp']['mde80']*100:.2f} | {'yes' if e59['E_within_round_2000']['any_female']['fp']['within_pm0.05'] else 'no'} | {e59['E_within_round_2000']['any_female']['n']:,} / {e59['E_within_round_2000']['any_female']['n_clusters']:,} |
| **Female-only attribution — reference run (2,000 draws)** | {e59['E_within_round_2000']['female_only']['fp']['coef']*100:+.2f} | {pp(e59['E_within_round_2000']['female_only']['fp']['ci95'])} | {e59['E_within_round_2000']['female_only']['fp']['mde80']*100:.2f} | {'yes' if e59['E_within_round_2000']['female_only']['fp']['within_pm0.05'] else 'no'} | {e59['E_within_round_2000']['female_only']['n']:,} / {e59['E_within_round_2000']['female_only']['n_clusters']:,} |
| Three categories: female-only vs male-only | {e51['B_treatment_definition']['three_category']['female_only_vs_male_only']['coef']*100:+.2f} | {pp(e51['B_treatment_definition']['three_category']['female_only_vs_male_only']['ci95'])} | {e51['B_treatment_definition']['three_category']['female_only_vs_male_only']['mde80']*100:.2f} | — | {e51['B_treatment_definition']['three_category']['n']:,} / — |
| Three categories: mixed attribution vs male-only | {e51['B_treatment_definition']['three_category']['mixed_vs_male_only']['coef']*100:+.2f} | {pp(e51['B_treatment_definition']['three_category']['mixed_vs_male_only']['ci95'])} | {e51['B_treatment_definition']['three_category']['mixed_vs_male_only']['mde80']*100:.2f} | — | {e51['B_treatment_definition']['three_category']['n_mixed_rows']:,} mixed rows |
| Any-female, investor-cluster bootstrap | {e51['B_treatment_definition']['any_female_investor_cluster']['fp']['coef']*100:+.2f} | {pp(e51['B_treatment_definition']['any_female_investor_cluster']['fp']['ci95'])} | {e51['B_treatment_definition']['any_female_investor_cluster']['fp']['mde80']*100:.2f} | {'yes' if e51['B_treatment_definition']['any_female_investor_cluster']['fp']['within_pm0.05'] else 'no'} | {e51['B_treatment_definition']['any_female_investor_cluster']['n']:,} / {e51['B_treatment_definition']['any_female_investor_cluster']['n_clusters']:,} |
| Female-only, investor-cluster bootstrap | {e51['B_treatment_definition']['female_only_investor_cluster']['fp']['coef']*100:+.2f} | {pp(e51['B_treatment_definition']['female_only_investor_cluster']['fp']['ci95'])} | {e51['B_treatment_definition']['female_only_investor_cluster']['fp']['mde80']*100:.2f} | {'yes (margin ' + f"{e51['B_treatment_definition']['female_only_investor_cluster']['fp']['margin_lo_pp']:.2f}" + ' pp)' if e51['B_treatment_definition']['female_only_investor_cluster']['fp']['within_pm0.05'] else 'no'} | {e51['B_treatment_definition']['female_only_investor_cluster']['n']:,} / {e51['B_treatment_definition']['female_only_investor_cluster']['n_clusters']:,} |
| Any-female + all pre-round investor controls† | {e51['C_pre_round_controls']['all_pre_round']['any_female']['fp']['coef']*100:+.2f} | {pp(e51['C_pre_round_controls']['all_pre_round']['any_female']['fp']['ci95'])} | {e51['C_pre_round_controls']['all_pre_round']['any_female']['fp']['mde80']*100:.2f} | {'yes' if e51['C_pre_round_controls']['all_pre_round']['any_female']['fp']['within_pm0.05'] else 'no'} | {e51['C_pre_round_controls']['all_pre_round']['any_female']['n']:,} / {e51['C_pre_round_controls']['all_pre_round']['any_female']['n_clusters']:,} |
| Female-only + all pre-round investor controls† | {e51['C_pre_round_controls']['all_pre_round']['female_only']['fp']['coef']*100:+.2f} | {pp(e51['C_pre_round_controls']['all_pre_round']['female_only']['fp']['ci95'])} | {e51['C_pre_round_controls']['all_pre_round']['female_only']['fp']['mde80']*100:.2f} | {'yes' if e51['C_pre_round_controls']['all_pre_round']['female_only']['fp']['within_pm0.05'] else 'no'} | {e51['C_pre_round_controls']['all_pre_round']['female_only']['n']:,} / {e51['C_pre_round_controls']['all_pre_round']['female_only']['n_clusters']:,} |
| Any-female + fund-cycle controls (Crunchbase fund age, size, sequence; SEC Form D tier-1 vintages and amounts)‡ | {e58['P1_within_round_fund_controls']['both']['any_female']['fp']['coef']*100:+.2f} | {pp(e58['P1_within_round_fund_controls']['both']['any_female']['fp']['ci95'])} | {e58['P1_within_round_fund_controls']['both']['any_female']['fp']['mde80']*100:.2f} | {'yes' if e58['P1_within_round_fund_controls']['both']['any_female']['fp']['within_pm0.05'] else 'no'} | {e58['P1_within_round_fund_controls']['both']['any_female']['n']:,} / {e58['P1_within_round_fund_controls']['both']['any_female']['n_clusters']:,} |
| Female-only + fund-cycle controls‡ | {e58['P1_within_round_fund_controls']['both']['female_only']['fp']['coef']*100:+.2f} | {pp(e58['P1_within_round_fund_controls']['both']['female_only']['fp']['ci95'])} | {e58['P1_within_round_fund_controls']['both']['female_only']['fp']['mde80']*100:.2f} | {'yes' if e58['P1_within_round_fund_controls']['both']['female_only']['fp']['within_pm0.05'] else 'no'} | {e58['P1_within_round_fund_controls']['both']['female_only']['n']:,} / {e58['P1_within_round_fund_controls']['both']['female_only']['n_clusters']:,} |
| Round + investor fixed effects, all mixed rounds (fp × female-founded; β = female-founded slope) | {e51['F_twoway_FE_pooled']['b_FF']['coef']*100:+.2f} | {pp(e51['F_twoway_FE_pooled']['b_FF']['ci95'])} | {e51['F_twoway_FE_pooled']['b_FF']['mde80']*100:.2f} | {'yes' if e51['F_twoway_FE_pooled']['b_FF']['within_pm0.05'] else 'no'} | {e51['F_twoway_FE_pooled']['n']:,} / {e51['F_twoway_FE_pooled']['n_investors_fp_varying']} investors with varying attribution |

*Sample and window (P001-56): β, 95% CI, MDE80 and the ±5 pp verdict under the two treatment definitions:*
| Sample; deals through; next round within | Any-female attribution | Female-only attribution | FF rounds / rows |
|---|---|---|---|
| NA+EU companies; 2020-10; 36 months (baseline) | {e56['E_scope_window']['NAEU_2020_36m']['any_female']['fp']['coef']*100:+.2f} {pp(e56['E_scope_window']['NAEU_2020_36m']['any_female']['fp']['ci95'])}; MDE {e56['E_scope_window']['NAEU_2020_36m']['any_female']['fp']['mde80']*100:.2f}; {'yes' if e56['E_scope_window']['NAEU_2020_36m']['any_female']['fp']['within_pm0.05'] else 'no'} | {e56['E_scope_window']['NAEU_2020_36m']['female_only']['fp']['coef']*100:+.2f} {pp(e56['E_scope_window']['NAEU_2020_36m']['female_only']['fp']['ci95'])}; MDE {e56['E_scope_window']['NAEU_2020_36m']['female_only']['fp']['mde80']*100:.2f}; {'yes' if e56['E_scope_window']['NAEU_2020_36m']['female_only']['fp']['within_pm0.05'] else 'no'} | {e56['E_scope_window']['NAEU_2020_36m']['n_ff_cond_rounds']:,} / {e56['E_scope_window']['NAEU_2020_36m']['n_rows']:,} |
| All countries; 2020-10; 36 months | {e56['E_scope_window']['GLOBAL_2020_36m']['any_female']['fp']['coef']*100:+.2f} {pp(e56['E_scope_window']['GLOBAL_2020_36m']['any_female']['fp']['ci95'])}; MDE {e56['E_scope_window']['GLOBAL_2020_36m']['any_female']['fp']['mde80']*100:.2f}; {'yes' if e56['E_scope_window']['GLOBAL_2020_36m']['any_female']['fp']['within_pm0.05'] else 'no'} | {e56['E_scope_window']['GLOBAL_2020_36m']['female_only']['fp']['coef']*100:+.2f} {pp(e56['E_scope_window']['GLOBAL_2020_36m']['female_only']['fp']['ci95'])}; MDE {e56['E_scope_window']['GLOBAL_2020_36m']['female_only']['fp']['mde80']*100:.2f}; {'yes' if e56['E_scope_window']['GLOBAL_2020_36m']['female_only']['fp']['within_pm0.05'] else 'no'} | {e56['E_scope_window']['GLOBAL_2020_36m']['n_ff_cond_rounds']:,} / {e56['E_scope_window']['GLOBAL_2020_36m']['n_rows']:,} |
| NA+EU; 2021-10; 24 months | {e56['E_scope_window']['NAEU_2021_24m']['any_female']['fp']['coef']*100:+.2f} {pp(e56['E_scope_window']['NAEU_2021_24m']['any_female']['fp']['ci95'])}; MDE {e56['E_scope_window']['NAEU_2021_24m']['any_female']['fp']['mde80']*100:.2f}; {'yes' if e56['E_scope_window']['NAEU_2021_24m']['any_female']['fp']['within_pm0.05'] else 'no'} | {e56['E_scope_window']['NAEU_2021_24m']['female_only']['fp']['coef']*100:+.2f} {pp(e56['E_scope_window']['NAEU_2021_24m']['female_only']['fp']['ci95'])}; MDE {e56['E_scope_window']['NAEU_2021_24m']['female_only']['fp']['mde80']*100:.2f}; {'yes' if e56['E_scope_window']['NAEU_2021_24m']['female_only']['fp']['within_pm0.05'] else 'no'} | {e56['E_scope_window']['NAEU_2021_24m']['n_ff_cond_rounds']:,} / {e56['E_scope_window']['NAEU_2021_24m']['n_rows']:,} |
| All countries; 2021-10; 24 months | {e56['E_scope_window']['GLOBAL_2021_24m']['any_female']['fp']['coef']*100:+.2f} {pp(e56['E_scope_window']['GLOBAL_2021_24m']['any_female']['fp']['ci95'])}; MDE {e56['E_scope_window']['GLOBAL_2021_24m']['any_female']['fp']['mde80']*100:.2f}; {'yes' if e56['E_scope_window']['GLOBAL_2021_24m']['any_female']['fp']['within_pm0.05'] else 'no'} | {e56['E_scope_window']['GLOBAL_2021_24m']['female_only']['fp']['coef']*100:+.2f} {pp(e56['E_scope_window']['GLOBAL_2021_24m']['female_only']['fp']['ci95'])}; MDE {e56['E_scope_window']['GLOBAL_2021_24m']['female_only']['fp']['mde80']*100:.2f}; {'yes' if e56['E_scope_window']['GLOBAL_2021_24m']['female_only']['fp']['within_pm0.05'] else 'no'} | {e56['E_scope_window']['GLOBAL_2021_24m']['n_ff_cond_rounds']:,} / {e56['E_scope_window']['GLOBAL_2021_24m']['n_rows']:,} |

*Lead status, partner tenure, pseudo-treatment and the exit association (NA+EU baseline sample):*
| Check | Estimate | 95% CI | n rows / rounds |
|---|---|---|---|
| Lead flag recorded (investor-level flag combined with the round-level lead list): coverage | {e56['C_lead_union']['cov_union']*100:.0f} percent (agreement {e56['C_lead_union']['agreement_where_both']:.2f} where both exist) | — | — |
| Female-partner investor is lead, within round (pp) | {e56['C_lead_union']['lead_u_within_round_fp']['fp']['coef']*100:+.2f} | {pp(e56['C_lead_union']['lead_u_within_round_fp']['fp']['ci95'])} | {e56['C_lead_union']['lead_u_within_round_fp']['n']:,} / {e56['C_lead_union']['lead_u_within_round_fp']['n_rounds']:,} |
| Partner tenure, female-attributed − male-attributed investor (years) | {e56['D_tenure']['tenure_gap_within_round']['fp']['coef']:+.2f} | {raw(e56['D_tenure']['tenure_gap_within_round']['fp']['ci95'], 2)} | {e56['D_tenure']['tenure_gap_within_round']['n']:,} / {e56['D_tenure']['tenure_gap_within_round']['n_rounds']:,} |
| Re-investment, any-female, + tenure control (pp) | {e56['D_tenure']['reup_plus_tenure_any']['fp']['coef']*100:+.2f} | {pp(e56['D_tenure']['reup_plus_tenure_any']['fp']['ci95'])} | {e56['D_tenure']['reup_plus_tenure_any']['n']:,} / {e56['D_tenure']['reup_plus_tenure_any']['n_rounds']:,} |
| Re-investment, female-only, + tenure control (pp) | {e56['D_tenure']['reup_plus_tenure_fo']['fp']['coef']*100:+.2f} | {pp(e56['D_tenure']['reup_plus_tenure_fo']['fp']['ci95'])} | {e56['D_tenure']['reup_plus_tenure_fo']['n']:,} / {e56['D_tenure']['reup_plus_tenure_fo']['n_rounds']:,} |
| Pseudo-treatment: junior-partner investor in all-male female-founded rounds (pp) | {e56['D_tenure']['placebo_junior']['junior']['coef']*100:+.2f} | {pp(e56['D_tenure']['placebo_junior']['junior']['ci95'])} | {e56['D_tenure']['placebo_junior']['n']:,} / {e56['D_tenure']['placebo_pool']['n_all_male_ff_cond_rounds']:,} |
| Re-investment rate when the company later exits vs not (deals through October 2017; pp) | {(e56['F_calibration']['P_reup_exit']-e56['F_calibration']['P_reup_noexit'])*100:+.1f} | {pp(e56['F_calibration']['slope_reup_on_exit']['ci95'])} | {e56['F_calibration']['n_rows']:,} / — |

*Row 2 of the first sub-table (the unconditional outcome) includes {e52['Table10A_dilution']['n_ff_mixed_rounds_no_next36']} rounds with no next round, whose outcome is zero for every investor by construction ({e52['Table10A_dilution']['unconditional_y1_FF']['share_sxx_outcome_constant_rounds']*100:.0f} percent of their identifying variance comes from constant-outcome rounds); its interval is not read as a bound. The reference rows (2,000 draws) are the estimates quoted in the text; the initial 400-draw rows and the investor-cluster variants are shown for transparency and are not counted as separate robustness results. Sources: P001-42, P001-51, P001-52, P001-56, P001-58, P001-59.*

*Investor-level differences within the same rounds (female-attributed − male-attributed investor; pre-round traits) and positive controls (within-round slope of re-investment on the trait):*
| Investor trait | Difference | 95% CI | Standardized | Re-investment slope | 95% CI |
|---|---|---|---|---|---|
| Pre-round female-founded share of attributed deals | {e51['D_investor_balance']['pre_ff_share']['fp']['coef']:+.3f} | {raw(e51['D_investor_balance']['pre_ff_share']['fp']['ci95'])} | {e51['D_investor_balance']['pre_ff_share']['fp']['std_diff']:+.2f} | — | — |
| Pre-round early-stage share of attributed deals | {e51['D_investor_balance']['pre_early_share']['fp']['coef']:+.3f} | {raw(e51['D_investor_balance']['pre_early_share']['fp']['ci95'])} | {e51['D_investor_balance']['pre_early_share']['fp']['std_diff']:+.2f} | {e51['E_positive_controls']['pre_early_share']['coef']['coef']:+.3f} | {raw(e51['E_positive_controls']['pre_early_share']['coef']['ci95'])} |
| Investor firm age (years) | {e51['D_investor_balance']['firm_age']['fp']['coef']:+.2f} | {raw(e51['D_investor_balance']['firm_age']['fp']['ci95'],2)} | {e51['D_investor_balance']['firm_age']['fp']['std_diff']:+.2f} | — | — |
| Fund age (years since last fund announced; {e51['D_investor_balance']['fund_age']['coverage']*100:.0f} percent coverage) | {e51['D_investor_balance']['fund_age']['fp']['coef']:+.2f} | {raw(e51['D_investor_balance']['fund_age']['fp']['ci95'],2)} | {e51['D_investor_balance']['fund_age']['fp']['std_diff']:+.2f} | {e51['E_positive_controls']['fund_age']['coef']['coef']:+.4f} | {raw(e51['E_positive_controls']['fund_age']['coef']['ci95'],4)} |
| Log size of the latest fund (Crunchbase; P001-58) | {e58['P1_within_round_fund_controls']['balance']['ln_fund_size']['fp']['coef']:+.3f} | {raw(e58['P1_within_round_fund_controls']['balance']['ln_fund_size']['fp']['ci95'])} | {e58['P1_within_round_fund_controls']['balance']['ln_fund_size']['fp']['std_diff']:+.2f} | {e58['P1_within_round_fund_controls']['positive_controls']['ln_fund_size']['coef']['coef']:+.4f} | {raw(e58['P1_within_round_fund_controls']['positive_controls']['ln_fund_size']['coef']['ci95'],4)} |
| Fund sequence number (Crunchbase; P001-58) | {e58['P1_within_round_fund_controls']['balance']['fund_seq']['fp']['coef']:+.3f} | {raw(e58['P1_within_round_fund_controls']['balance']['fund_seq']['fp']['ci95'])} | {e58['P1_within_round_fund_controls']['balance']['fund_seq']['fp']['std_diff']:+.2f} | {e58['P1_within_round_fund_controls']['positive_controls']['fund_seq']['coef']['coef']:+.4f} | {raw(e58['P1_within_round_fund_controls']['positive_controls']['fund_seq']['coef']['ci95'],4)} |
| Any SEC Form D tier-1 fund filing before the round (coverage {e58['P1_within_round_fund_controls']['coverage']['fd_any']*100:.0f} percent) | {e58['P1_within_round_fund_controls']['balance']['fd_any']['fp']['coef']:+.3f} | {raw(e58['P1_within_round_fund_controls']['balance']['fd_any']['fp']['ci95'])} | {e58['P1_within_round_fund_controls']['balance']['fd_any']['fp']['std_diff']:+.2f} | {e58['P1_within_round_fund_controls']['positive_controls']['fd_any']['coef']['coef']:+.4f} | {raw(e58['P1_within_round_fund_controls']['positive_controls']['fd_any']['coef']['ci95'],4)} |
| Investor experience (log prior rounds) | {e51['D_investor_balance']['ln_exp']['fp']['coef']:+.3f} | {raw(e51['D_investor_balance']['ln_exp']['fp']['ci95'])} | {e51['D_investor_balance']['ln_exp']['fp']['std_diff']:+.2f} | {e51['E_positive_controls']['ln_exp']['coef']['coef']:+.4f} | {raw(e51['E_positive_controls']['ln_exp']['coef']['ci95'],4)} |
| Lead-investor flag ({e51['D_investor_balance']['lead']['coverage']*100:.0f} percent coverage) | {e51['D_investor_balance']['lead']['fp']['coef']:+.3f} | {raw(e51['D_investor_balance']['lead']['fp']['ci95'])} | {e51['D_investor_balance']['lead']['fp']['std_diff']:+.2f} | {e51['E_positive_controls']['lead']['coef']['coef']:+.3f} | {raw(e51['E_positive_controls']['lead']['coef']['ci95'])} |

Female-founded rounds with a next round within 36 months: {a42['n_cond_ff_rounds']:,} rounds, {a42['n_cond_ff_rows']:,} investor rows, {e51['G_estimand']['n_companies']:,} companies, {e51['G_estimand']['n_investor_firms']:,} investor firms (the pooled regression with other rounds spans {a42['n_cond_companies']:,} companies). These rounds are larger than all female-founded equity rounds in the window (median ${e51['G_estimand']['median_amt_usd_cond_rounds']/1e6:.1f} million vs ${e51['G_estimand']['median_amt_usd_all_ff_rounds']/1e6:.1f} million; early-stage {e51['G_estimand']['early_share_cond_rounds']*100:.0f} vs {e51['G_estimand']['early_share_all_ff_rounds']*100:.0f} percent); partner attribution covers {e51['G_estimand']['attribution_coverage_rows']*100:.0f} percent of their investor rows, and attributed co-investors re-invest {e51['G_estimand']['reup_attributed_minus_unattributed_within_round']['coef']*100:+.1f} pp {pp(e51['G_estimand']['reup_attributed_minus_unattributed_within_round']['ci95'])} more often than unattributed ones within the same rounds. † Pre-round controls: female-founded share, early-stage share and log count of the investor's prior attributed deals, investor firm age, fund age (each with a missing indicator). ‡ Fund-cycle controls: Crunchbase fund age, log size and sequence number of the investor's latest fund before the round, and the count, latest vintage and cumulative amount of the investor's SEC Form D tier-1 fund filings before the round (missing indicators included; P001-58). Sources: P001-42, P001-51. Re-investment base rate in those rounds {a42['base_reup_cond_ff']:.3f}; raw four-cell double difference {a42['raw_dd_reup_cond']:+.4f}. Within-round permutation of partner gender ({e42['B_reup_conditional']['perm_FF']['n_perm']} draws): two-sided p = {e42['B_reup_conditional']['perm_FF']['p_two']:.3f}. Minimum detectable effect (80% power) of β in female-founded rounds: {r42['b_FF']['mde80']:.3f}.

## Panel B. Balance of pre-assignment company characteristics within the Table 4 cells (female-founded deals, firm × year × sector; deals through 2017-10)
| Characteristic | Female − male partner, all mixed cells | 95% CI | Standardized (diluted) | MDE (sd) | Share of Σx̃² from single-round cells (d) | Identifying cells only: standardized difference [95% CI in sd]; MDE (sd) | Same, stage in the cell | n (all) |
|---|---|---|---|---|---|---|---|---|
{rows46}

*Prior patenting (USPTO PatentsView, matched to sample companies by normalized name and country/state/city; P001-58), female − male partner within cell:*
| Characteristic | Identifying (multi-round) cells: difference | 95% CI | Standardized | MDE (sd) | All mixed cells: difference | 95% CI |
|---|---|---|---|---|---|---|
| Any patent application filed before the deal | {e58['P3_patents']['balance_identifying_cells']['covs']['any_patent_before']['fp']['coef']:+.3f} | {raw(e58['P3_patents']['balance_identifying_cells']['covs']['any_patent_before']['fp']['ci95'])} | {e58['P3_patents']['balance_identifying_cells']['covs']['any_patent_before']['fp']['std_diff']:+.2f} | {e58['P3_patents']['balance_identifying_cells']['covs']['any_patent_before']['fp']['mde80_sd']:.2f} | {e58['P3_patents']['balance_all_mixed_cells']['covs']['any_patent_before']['fp']['coef']:+.3f} | {raw(e58['P3_patents']['balance_all_mixed_cells']['covs']['any_patent_before']['fp']['ci95'])} |
| Log (1 + applications filed before the deal) | {e58['P3_patents']['balance_identifying_cells']['covs']['ln_app_before']['fp']['coef']:+.3f} | {raw(e58['P3_patents']['balance_identifying_cells']['covs']['ln_app_before']['fp']['ci95'])} | {e58['P3_patents']['balance_identifying_cells']['covs']['ln_app_before']['fp']['std_diff']:+.2f} | {e58['P3_patents']['balance_identifying_cells']['covs']['ln_app_before']['fp']['mde80_sd']:.2f} | {e58['P3_patents']['balance_all_mixed_cells']['covs']['ln_app_before']['fp']['coef']:+.3f} | {raw(e58['P3_patents']['balance_all_mixed_cells']['covs']['ln_app_before']['fp']['ci95'])} |
| Company matched to a patent assignee (coverage indicator) | {e58['P3_patents']['balance_identifying_cells']['covs']['matched_assignee']['fp']['coef']:+.3f} | {raw(e58['P3_patents']['balance_identifying_cells']['covs']['matched_assignee']['fp']['ci95'])} | {e58['P3_patents']['balance_identifying_cells']['covs']['matched_assignee']['fp']['std_diff']:+.2f} | {e58['P3_patents']['balance_identifying_cells']['covs']['matched_assignee']['fp']['mde80_sd']:.2f} | {e58['P3_patents']['balance_all_mixed_cells']['covs']['matched_assignee']['fp']['coef']:+.3f} | {raw(e58['P3_patents']['balance_all_mixed_cells']['covs']['matched_assignee']['fp']['ci95'])} |

Dilution. A company characteristic is identical for the two partners of a co-attributed pair, so the all-cells coefficient equals the identifying-cells coefficient times (1 − d), where d is the share of identifying variance from single-round cells (identity verified to {e52['FF_cell_cat_pre']['identity_max_abs_err']:.0e}); the identifying cells are the {e52['FF_cell_cat_pre']['n_multi_round_cells']} multi-round cells with {e52['FF_cell_cat_pre']['n_deals_multi']} deals (sector cells) and {e52['FF_cell_stage_pre']['n_multi_round_cells']} cells with {e52['FF_cell_stage_pre']['n_deals_multi']} deals (stage cells; not identified). Joint tests. Largest absolute cluster-robust t across nine characteristics (prior-round investor count, 64 percent coverage, tested separately), against a shared within-cell permutation null ({e52['FF_cell_cat_pre']['joint_maxt_all']['n_perm']} draws): sector cells p = {e52['FF_cell_cat_pre']['joint_maxt_all']['p_perm']:.3f} (identifying cells only p = {e52['FF_cell_cat_pre']['joint_maxt_multi']['p_perm']:.3f}); the test rejects {e52['FF_cell_cat_pre']['joint_maxt_all']['size_calibration_reject_rate']*100:.0f} percent of {e52['FF_cell_cat_pre']['joint_maxt_all']['n_cal']} random within-cell reassignments at the 5 percent level. With stage in the cell p = {e52['FF_cell_stage_pre']['joint_maxt_all']['p_perm']:.3f}; on all deals with stage in the cell ({b46a['n_mixed_cells']:,} cells, {b46a['n_deals']:,} deals) p = {e52['ALL_cell_stage_pre']['joint_maxt_all']['p_perm']:.3f}. The Mahalanobis joint test (bootstrap covariance; complete cases n = {b46['joint']['n_complete']:,}) gives p = {b46['joint']['p_perm']:.3f} in the sector cells and is degenerate with stage in the cell (a zero-variance characteristic makes the covariance near-singular). Positive control, post-assignment log round size (female − male partner): same cells {e46['FF_cell_cat_post']['by_cov']['ln_round_size']['coef']:+.3f} {raw(e46['FF_cell_cat_post']['by_cov']['ln_round_size']['ci95'])}; all deals, firm × year × sector {e46['ALL_cell_cat_post']['by_cov']['ln_round_size']['coef']:+.3f} {raw(e46['ALL_cell_cat_post']['by_cov']['ln_round_size']['ci95'])}.

## Panel C. Movers: the same partner at two firms (≥ 5 attributed deals at each; NA+EU)
| Specification | β | 95% CI | n transitions |
|---|---|---|---|
| Change in the partner's early-stage share on the change in her firm's leave-partner-out early-stage share, all transitions | {rw(d1['early_pooled'], 'd_firm_early')} | {d1['early_pooled']['n']} |
| Same, non-overlapping spells only | {rw(d1['early_nonoverlap'], 'd_firm_early')} | {d1['early_nonoverlap']['n']} |
| Same for the stage part of the composition component | {rw(d1['ts_pooled'], 'd_firm_ts')} | {d1['ts_pooled']['n']} |
| Same for the sector part | {rw(d1['tcs_pooled'], 'd_firm_tcs')} | {d1['tcs_pooled']['n']} |
| Levels: destination firm's share / origin firm's share | {d1b['firm_early2']['coef']:+.3f} {raw(d1b['firm_early2']['ci95'])} / {d1b['firm_early1']['coef']:+.3f} {raw(d1b['firm_early1']['ci95'])} | | {d1b['n']} |
| Placebo destination (random firm in the same size decile) / origin | {d3b['firm_early2_placebo']['coef']:+.3f} {raw(d3b['firm_early2_placebo']['ci95'])} / {d3b['firm_early1']['coef']:+.3f} {raw(d3b['firm_early1']['ci95'])} | | {d3b['n']} |
| Sorting check: pre-move own share on the destination firm's share measured before the move (given the origin firm's) | {rw(d2['early'], 'dest_early_in_s1')} | {d2['early']['n']} |
| Moves toward later-stage firms / toward earlier-stage firms | {d4['to_later_stage_firm']['d_firm_early']['coef']:+.3f} {raw(d4['to_later_stage_firm']['d_firm_early']['ci95'])} / {d4['to_earlier_stage_firm']['d_firm_early']['coef']:+.3f} {raw(d4['to_earlier_stage_firm']['d_firm_early']['ci95'])} | | {d4['to_later_stage_firm']['n']} / {d4['to_earlier_stage_firm']['n']} |

Movers {a43['n_movers']} ({a43['n_female_movers']} women), {a43['n_transitions']} transitions, {a43['n_nonoverlap']} with non-overlapping spells. Partner-cluster bootstrap. The design is gender-neutral by construction (37 female movers).

## Panel D. Absences: interior gaps of 18 months or more in a partner's attributed record while she remains at the firm
Outcome: female-founded share of the firm's other deals in the half-year; partner × firm and half-year effects; firm-cluster bootstrap. "Difference" is the female-partner minus male-partner absence coefficient.
| Outcome / gap length | Female partners' absence | 95% CI | Male partners' absence | 95% CI | Difference | 95% CI | MDE |
|---|---|---|---|---|---|---|---|
| Colleagues' attributed deals, ≥ 18 months | {rw(b44['18'], 'b_female')} | {rw(b44['18'], 'b_male')} | {rw(b44['18'], 'diff_female_minus_male')} | {b44['18']['diff_female_minus_male']['mde80']:.3f} |
| Same, ≥ 24 months | {rw(b44['24'], 'b_female')} | {rw(b44['24'], 'b_male')} | {rw(b44['24'], 'diff_female_minus_male')} | {b44['24']['diff_female_minus_male']['mde80']:.3f} |
| All of the firm's equity deals in sample companies, ≥ 18 months | {rw(b44a['18'], 'b_female')} | {rw(b44a['18'], 'b_male')} | {rw(b44a['18'], 'diff_female_minus_male')} | {b44a['18']['diff_female_minus_male']['mde80']:.3f} |
| Same, spells with recorded continuous employment | {rw(b44a['cont_only_18'], 'b_female')} | {rw(b44a['cont_only_18'], 'b_male')} | {rw(b44a['cont_only_18'], 'diff_female_minus_male')} | {b44a['cont_only_18']['diff_female_minus_male']['mde80']:.3f} |
| Recording placebo: firm's attribution rate during the gap | {rw(c44['attribution_rate_18'], 'b_female')} | {rw(c44['attribution_rate_18'], 'b_male')} | {rw(c44['attribution_rate_18'], 'diff_female_minus_male')} | |
| Scale placebo: log colleague deal count | {rw(c44['ln_colleague_deals_18'], 'b_female')} | {rw(c44['ln_colleague_deals_18'], 'b_male')} | {rw(c44['ln_colleague_deals_18'], 'diff_female_minus_male')} | |

Partners with a ≥ 18-month gap {a44['n_partners_with_gap18']:,} ({a44['n_female_with_gap18']} women); spells in the panel {a44['n_spells_in_panel']:,}. Pre-gap event-time coefficients (four half-years) joint sup-t p = {e44['D_pretrend']['joint_p']:.2f}.

## Panel E. Financing-ladder pipeline (descriptive): where the female-partner share narrows along the ladder
| Margin | Estimate | 95% CI | n |
|---|---|---|---|
| Company reaches Series A: female-founded − other, first-round year × sector × country cells | {m1['reach_a_cell']['ff']['coef']*100:+.2f}pp | {pp(m1['reach_a_cell']['ff']['ci95'])} | {m1['reach_a_cell']['n']:,} |
| Company reaches Series B or later | {m1['reach_b_cell']['ff']['coef']*100:+.2f}pp | {pp(m1['reach_b_cell']['ff']['ci95'])} | {m1['reach_b_cell']['n']:,} |
| Same, companies acquired or listed before Series B excluded | {m1['reach_b_cell_excl_exit']['ff']['coef']*100:+.2f}pp | {pp(m1['reach_b_cell_excl_exit']['ff']['ci95'])} | {m1['reach_b_cell_excl_exit']['n']:,} |
| Incumbent firm re-invests in the next round (given a next round within 36 months): FP × FF, firm × year × sector × stage cells | {m2['firm_followon']['fpff']['coef']*100:+.2f}pp | {pp(m2['firm_followon']['fpff']['ci95'])} | {m2['firm_followon']['n']:,} |
| Same partner re-attributed (given the firm re-invests): FP × FF | {m3['partner_reattr']['fpff']['coef']*100:+.2f}pp | {pp(m3['partner_reattr']['fpff']['ci95'])} | {m3['partner_reattr']['n']:,} |
| Conditioning event (next round within 36 months): FP × FF | {m2['cond_balance']['fpff']['coef']*100:+.2f}pp | {pp(m2['cond_balance']['fpff']['ci95'])} | {m2['cond_balance']['n']:,} |
| Coverage: next round has recorded investors / re-investing firm has a recorded partner, FP × FF | {m2['coverage_next_investors']['fpff']['coef']*100:+.2f}pp {pp(m2['coverage_next_investors']['fpff']['ci95'])} / {m3['coverage_next_partner']['fpff']['coef']*100:+.2f}pp {pp(m3['coverage_next_partner']['fpff']['ci95'])} | | |
| Female-partner share among investors new to the company: early / later stage, female-founded companies | {m4['fp_share_entrants']['late0_ff1']['share']*100:.1f}% / {m4['fp_share_entrants']['late1_ff1']['share']*100:.1f}% | n = {m4['fp_share_entrants']['late0_ff1']['n']:,} / {m4['fp_share_entrants']['late1_ff1']['n']:,} | |
| Same, other companies | {m4['fp_share_entrants']['late0_ff0']['share']*100:.1f}% / {m4['fp_share_entrants']['late1_ff0']['share']*100:.1f}% | n = {m4['fp_share_entrants']['late0_ff0']['n']:,} / {m4['fp_share_entrants']['late1_ff0']['n']:,} | |
| Entrant female-partner share on later stage: all companies / female-founded × later stage | {m4['entrant_fp_on_late']['late']['coef']*100:+.2f}pp {pp(m4['entrant_fp_on_late']['late']['ci95'])} / {m4['entrant_fp_on_late']['lateff']['coef']*100:+.2f}pp {pp(m4['entrant_fp_on_late']['lateff']['ci95'])} | | {m4['entrant_fp_on_late']['n']:,} |

Raw four-cell re-investment rates (FP, FF): {m2['four_cell_firm_followon']}. Companies with an early first round 2010–2019: {m1['n_companies']:,} ({m1['n_ff']:,} female-founded). Sources: P001-42, P001-46, P001-43, P001-44, P001-45. All rows are bootstrap percentile intervals; no causal claim is made in this table.
"""
import re as _re
_parts = _re.split(r"(?m)^(?=## Panel [A-E]\.)", _t10)[1:]                     # Panels A–E of the former combined table
assert len(_parts) == 5, len(_parts)
w("table8.md", "# Table 8. The deal held fixed: within-round comparison of co-investors on female-founded rounds (NA+EU)\n" + _parts[0].split("\n", 1)[1])
w("table6.md", "# Table 6. Balance of company characteristics within the cells that identify the peer comparison (female-founded deals, firm × year × sector; deals through 2017-10)\n" + _parts[1].split("\n", 1)[1].rstrip("\n") + "\n\n*Characteristics are Crunchbase profile values. Founding date, prior equity rounds, prior funding, prior-round investors, and prior patent applications are dated relative to the deal; founder counts and degrees, serial founding, employee-count band, and headquarters are current profile fields whose historical timing is not recorded. The patent match indicator (whether the company appears in the assignee tables) is not a pre-deal quantity.*\n")
_ia3 = "# Appendix Table IA.3. Movers, absences, and the financing-ladder pipeline\n" + "".join(p.replace("## Panel C.", "## Panel A.", 1).replace("## Panel D.", "## Panel B.", 1).replace("## Panel E.", "## Panel C.", 1) for p in _parts[2:])
w("tableIA3.md", _ia3)



# ---- Table 7 slimming (R4 writing finding 19): full Panels D1/D2 -> Internet Appendix Table IA.1; 9 rows each kept in the paper ----
_t7 = open(os.path.join(OUT_T, "table7.md"), encoding="utf-8").read()
_parts = _t7.split("\n## ")
_keep_d1 = ("| Baseline cell benchmark", "| Leave-one-out cell benchmark |", "| Excluding post-period deals in companies", "| Composition component, levels, given tenure",
            "| Composition component, levels, home-firm fixed effects", "| Decomposition of the composition component, levels", "| Same decomposition, given tenure",
            "| Contrast, levels: adjusted exit rate", "| Contrast: adjusted percentile")
_keep_d2 = ("| **Composition component", "| Sector-within-year", "| Adjusted exit rate's own coefficient, same regression", "| Tenure and rank from employment records",
            "| Home-firm fixed effects (minimum", "| Deal level, within firm–year: composition component", "| Pre-period restricted to deals whose 36-month window closes before",
            "| Follow-on construct instead of exit", "| Reweighted for selection")
_ia = []
for _k, _p in enumerate(_parts):
    if _p.startswith("Panel D1.") or _p.startswith("Panel D2."):
        _ia.append("## " + _p)
        _lines = _p.split("\n")
        _hdr = [l for l in _lines if not l.startswith("| ") or l.startswith("| Specification") or l.startswith("|---")]
        _keep = _keep_d1 if _p.startswith("Panel D1.") else _keep_d2
        _rows = [l for l in _lines if l.startswith("| ") and not l.startswith("| Specification") and any(l.startswith(k) for k in _keep)]
        _head_end = next(i for i, l in enumerate(_lines) if l.startswith("|---")) + 1
        _parts[_k] = "\n".join(_lines[:_head_end] + _rows) + "\nRemaining rows (benchmark variation and additional analyses) are in Internet Appendix Table IA.1.\n"
open(os.path.join(OUT_T, "table7.md"), "w", encoding="utf-8").write("\n## ".join(_parts))
open(os.path.join(OUT_T, "tableIA1.md"), "w", encoding="utf-8").write("# Appendix Table IA.1. Does composition carry information? Full specification ladders (Table 7, Panels D1 and D2)\n" + "\n".join(_ia) +
                                                                     "\n*Same construction, samples, and sources as Table 7; see its note.*\n")
print("table: table7.md (slimmed) · tableIA1.md")


# ════════════════════════════ v9 blocks (2026-09-10; comments c1/c2/c3) ════════════════════════════
def ci_pp(v, d=2):
    return f"[{v['ci95'][0]*100:+.{d}f}, {v['ci95'][1]*100:+.{d}f}]"


def ci_pt(v, d=2):
    return f"[{v['ci95'][0]:+.{d}f}, {v['ci95'][1]:+.{d}f}]"


# ── Table 1 extra rows: population rule, unique units, investor types, titles ─────────────────────────────────────────────
_t63a, _t63b = e63["A_investor_types"], e63["B_partner_titles"]
w("t1_extra.md", f"""| Unique funding rounds / companies / investor firms / attributed partners | {p0['unique_rounds']:,} / {p0['unique_companies']:,} / {p0['unique_investor_firms']:,} / {p0['unique_partners']:,} |
| Attributed rows on companies with an acquisition or IPO recorded on or before the round date (excluded from the analysis file; global / NA+EU) | {p0['excluded_pre_exit_rows']:,} / {p0['excluded_pre_exit_rows_naeu']:,} |
| Deals at investors whose Crunchbase type includes venture capital, micro VC, or corporate VC (NA+EU); partners at such firms | {_t63a['share_deals_vc_type_naeu']*100:.1f}% ; {_t63a['share_partners_at_vc_type_firms']*100:.1f}% |
| Attributed partners with a job title at the firm containing "partner" (share of partner–firm pairs; deal-weighted) | {_t63b['share_any_partner_title_pairs']*100:.1f}% ; {(_t63b['share_by_bucket_deal_weighted']['general/managing/founding partner'] + _t63b['share_by_bucket_deal_weighted']['partner (other)'])*100:.1f}% |
| Attributed partners with no job record at the firm (share of pairs) | {_t63b['share_by_bucket_pairs']['no job record at the firm']*100:.1f}% |
""")

# ── Table 2 Panel B: co-attribution diagnostics and common-support ladder (P001-61) ───────────────────────────────────────
_A61, _B61, _C61 = e61["A_diagnostics_by_cell"], e61["B_original_ladder"], e61["C_common_support_ladder"]
_lab = {"L0_invyear": "Firm × year", "L1_pluscat": "+ sector", "L2_plusstage": "+ stage"}
_rows = "\n".join(f"| {_lab[k]} | {_A61[k]['n_mixed_cells']:,} / {_A61[k]['n_unique_rounds_mixed']:,} | {_A61[k]['share_single_round_cells']:.2f} | {_A61[k]['d_share_sxx_single_round']:.2f} | {_A61[k]['beta_all_pp']:+.2f} | {_A61[k]['beta_multi_pp']:+.2f} | {_C61[k]['coef_pp']:+.2f} [{_C61[k]['ci95_pp'][0]:+.2f}, {_C61[k]['ci95_pp'][1]:+.2f}] |" for k in ("L0_invyear", "L1_pluscat", "L2_plusstage"))
w("t2_panelB.md", f"""## Panel B. What each layer compares: co-attribution and the common-support ladder (NA+EU, all deals)
| Cell | Mixed cells / unique rounds in them | Share of mixed cells that are a single round | d: share of identifying variance from single-round cells | β, all rows (pp) | β, multi-round cells only (pp) | β on the common support (rows in cells mixed at the finest level; pp) 95% CI |
|---|---|---|---|---|---|---|
{_rows}
| Drop from firm × year to + stage (pp): original sample / common support | | | | {_B61['drop_L0_to_L2_pp']['coef_pp']:+.2f} [{_B61['drop_L0_to_L2_pp']['ci95_pp'][0]:+.2f}, {_B61['drop_L0_to_L2_pp']['ci95_pp'][1]:+.2f}] | | {_C61['drop_L0_to_L2_pp']['coef_pp']:+.2f} [{_C61['drop_L0_to_L2_pp']['ci95_pp'][0]:+.2f}, {_C61['drop_L0_to_L2_pp']['ci95_pp'][1]:+.2f}] |

*Panel B: the dependent variable (female-founded) is identical for the partners of a co-attributed pair, so the all-rows coefficient equals the multi-round coefficient times (1 − d), exactly as for the exit estimator. Common support = the {_C61['support']['rows']:,} rows ({_C61['support']['share_of_rows']*100:.1f} percent of the sample; {_C61['support']['unique_rounds']:,} unique rounds, {_C61['support']['unique_companies']:,} companies) that lie in firm × year × sector × stage cells containing both a female- and a male-partner deal; the three layers are re-estimated on those rows, so the observations are held fixed while the cells change — the implicit weights of the fixed-effects estimator still differ across layers, so this is a comparison-set diagnostic, not a decomposition of a pure composition effect. Investor-firm cluster bootstrap (500), shared across layers so that the drop is estimated from the same draws. Source: P001-61.*
""")

# ── Table 4: composition accounting, ranks, benchmark uncertainty (P001-62, P001-05) ──────────────────────────────────────
_A62 = e62["A_accounting_sample_end"]; _B62 = e62["B_benchmark_levels_sample_end"]; _C62 = e62["C_fixed_horizon"]; _D62 = e62["D_benchmark_uncertainty"]; _E62 = e62["E_benchmark_variants"]


def acc_row(lab, v):
    return f"| {lab} | {v['gap_raw']['coef']*100:+.2f} {ci_pp(v['gap_raw'])} | {v['gap_comp']['coef']*100:+.2f} {ci_pp(v['gap_comp'])} | {v['gap_adj']['coef']*100:+.2f} {ci_pp(v['gap_adj'])} | {v['female_raw_pct']['coef']:.1f} → {v['female_adj_pct']['coef']:.1f} | {v['male_raw_pct']['coef']:.1f} → {v['male_adj_pct']['coef']:.1f} | {v['female_shift']['coef']:+.2f} {ci_pt(v['female_shift'])} | {v['n_partners']:,} ({v['n_female']}) |"


w("t4_rank.md", f"""# Table 4. Track-record evaluation: composition accounting and rank changes (NA+EU partners with at least five attributed deals)
## Panel A. Levels and ranks on one sample: female − male differences and mean percentile ranks (exit by sample end, deals through 2017-10)
| Benchmark | Δ raw exit rate (pp) 95% CI | Δ benchmark component (pp) | Δ adjusted exit rate (pp) | Female mean percentile, raw → adjusted | Male mean percentile, raw → adjusted | Female shift (percentile points) 95% CI | Partners (women) |
|---|---|---|---|---|---|---|---|
{acc_row("Year", _B62["year"])}
{acc_row("Year × stage", _B62["year_stage"])}
{acc_row("Year × sector × stage (preferred)", _A62)}

## Panel B. The same accounting at fixed exit horizons
| Sample and horizon | Δ raw exit rate (pp) 95% CI | Δ benchmark component (pp) | Δ adjusted exit rate (pp) | Female mean percentile, raw → adjusted | Male mean percentile, raw → adjusted | Female shift (percentile points) 95% CI | Partners (women) |
|---|---|---|---|---|---|---|---|
{acc_row("36-month exit, deals through 2020-10; year × sector × stage", _C62["exit3_deals_to_2020_10"]["year_sector_stage"])}
{acc_row("&nbsp;&nbsp;year only", _C62["exit3_deals_to_2020_10"]["year"])}
{acc_row("72-month exit, deals through 2017-10; year × sector × stage", _C62["exit6_deals_to_2017_10"]["year_sector_stage"])}
{acc_row("&nbsp;&nbsp;year only", _C62["exit6_deals_to_2017_10"]["year"])}

## Panel C. What the interval covers, and the benchmark's weights
| | Female shift (percentile points) | 95% CI | Partners |
|---|---|---|---|
| Benchmark held fixed; partners resampled (as in Panels A–B) | {_D62['D1_fixed_benchmark_partner_resampling']['coef']:+.2f} | {ci_pt(_D62['D1_fixed_benchmark_partner_resampling'])} | {_A62['n_partners']:,} |
| Benchmark (market-cell means) and ranks recomputed in every replication | {_D62['D2_benchmark_recomputed_each_replication']['coef']:+.2f} | {ci_pt(_D62['D2_benchmark_recomputed_each_replication'])} (interval width ratio {_D62['width_ratio_D2_over_D1']:.2f}) | {_A62['n_partners']:,} |
| Benchmark from unique rounds (multiply attributed rounds counted once in cell means) | {_E62['unique_round']['female_shift']['coef']:+.2f} | {ci_pt(_E62['unique_round']['female_shift'])} | {_E62['unique_round']['n_partners']:,} |
| Leave-company-out benchmark | {_E62['leave_company_out']['female_shift']['coef']:+.2f} | {ci_pt(_E62['leave_company_out']['female_shift'])} | {_E62['leave_company_out']['n_partners']:,} |
| Top-quartile female share, raw → adjusted (P001-05) | {e5['topq_female_share_raw']*100:.1f}% → {e5['topq_female_share_adj']*100:.1f}% | {pp(e5['topq_change'][1]) if isinstance(e5['topq_change'], list) and isinstance(e5['topq_change'][1], list) else '—'} | {e5['n_partners']:,} |
| Rank correlation, raw vs adjusted (P001-05) | {e5['spearman_raw_adj']:.3f} | | |

*Raw exit rate = the partner's mean exit indicator; benchmark component = the deal-weighted mean of her market cells' exit rates (year, year × stage, or year × sector × stage; full cell means); adjusted rate = raw minus component, so the three level differences add up exactly on the same partners (maximum absolute deviation {e62['A_identity_check_max_abs']:.1e} in exit-rate units). Percentiles are computed across all partners in the row's sample; the identity does not hold for ranks. Intervals are 500 partner-resampling bootstrap replications (300 for the benchmark-level and fixed-horizon rows); the benchmark is held fixed except in the row that says otherwise. Multiply attributed rounds enter the cell means once per attributed row ({e62['E_rows_per_round_in_cells']['share_rounds_multiply_attributed']*100:.0f} percent of rounds in the cells are attributed more than once; {e62['E_rows_per_round_in_cells']['mean_rows_per_round']:.2f} rows per round on average). Sources: P001-62, P001-05.*
""")

# ── Table 7 extra: horizon differences from the same draws; two-way FE ────────────────────────────────────────────────────
_H = e57["A_horizon_differences_same_draws"]; _T = e57["C_twoway_FE"]
w("t7_horizon.md", f"""| Same partners and window (deals through 2017-10): 60-month exit | {e57['A_2017']['exit5']['ffp']['coef']*100:+.2f} | {pp(e57['A_2017']['exit5']['ffp']['ci95'])} | {e57['A_2017']['exit5']['ffp']['mde80']*100:.2f} | {e57['A_2017']['exit5']['ffp']['beta_std']:+.3f} | {'yes' if e57['A_2017']['exit5']['ffp']['within_pm0.05'] else 'no'} | {e57['A_2017']['exit5']['ff']['coef']*100:+.2f} | {pp(e57['A_2017']['exit5']['ff']['ci95'])} | {e57['A_2017']['exit5']['n']:,} / {e57['A_2017']['exit5']['n_partners']:,} |
| &nbsp;&nbsp;96-month exit | {e57['A_2017']['exit8']['ffp']['coef']*100:+.2f} | {pp(e57['A_2017']['exit8']['ffp']['ci95'])} | {e57['A_2017']['exit8']['ffp']['mde80']*100:.2f} | {e57['A_2017']['exit8']['ffp']['beta_std']:+.3f} | {'yes' if e57['A_2017']['exit8']['ffp']['within_pm0.05'] else 'no'} | {e57['A_2017']['exit8']['ff']['coef']*100:+.2f} | {pp(e57['A_2017']['exit8']['ff']['ci95'])} | {e57['A_2017']['exit8']['n']:,} / {e57['A_2017']['exit8']['n_partners']:,} |
| Horizon differences from the same bootstrap draws (deals through 2017-10): 60 − 36 months | {_H['exit5_minus_exit3']['coef']*100:+.2f} | {pp(_H['exit5_minus_exit3']['ci95'])} | — | — | — | — | — | paired draws {_H['exit5_minus_exit3']['paired_draws']} |
| &nbsp;&nbsp;72 − 36 months | {_H['exit6_minus_exit3']['coef']*100:+.2f} | {pp(_H['exit6_minus_exit3']['ci95'])} | — | — | — | — | — | |
| &nbsp;&nbsp;96 − 36 months | {_H['exit8_minus_exit3']['coef']*100:+.2f} | {pp(_H['exit8_minus_exit3']['ci95'])} | — | — | — | — | — | |
| &nbsp;&nbsp;eventual − 36 months | {_H['exit_ever_minus_exit3']['coef']*100:+.2f} | {pp(_H['exit_ever_minus_exit3']['ci95'])} | — | — | — | — | — | |
| &nbsp;&nbsp;eventual − 96 months | {_H['exit_ever_minus_exit8']['coef']*100:+.2f} | {pp(_H['exit_ever_minus_exit8']['ci95'])} | — | — | — | — | — | |
| Partner and year × sector × stage fixed effects entered jointly on the raw outcome: 36-month exit, deals through 2020-10 | {_T['exit3_2020']['ffp']['coef']*100:+.2f} | {pp(_T['exit3_2020']['ffp']['ci95'])} | {_T['exit3_2020']['ffp']['mde80']*100:.2f} | — | {'yes' if _T['exit3_2020']['ffp']['ci95'][0] >= -0.05 and _T['exit3_2020']['ffp']['ci95'][1] <= 0.05 else 'no'} | {_T['exit3_2020']['ff']['coef']*100:+.2f} | {pp(_T['exit3_2020']['ff']['ci95'])} | {_T['exit3_2020']['n']:,} / {_T['exit3_2020']['n_partners']:,} |
| &nbsp;&nbsp;eventual exit, deals through 2017-10 | {_T['exit_ever_2017']['ffp']['coef']*100:+.2f} | {pp(_T['exit_ever_2017']['ffp']['ci95'])} | {_T['exit_ever_2017']['ffp']['mde80']*100:.2f} | — | {'yes' if _T['exit_ever_2017']['ffp']['ci95'][0] >= -0.05 and _T['exit_ever_2017']['ffp']['ci95'][1] <= 0.05 else 'no'} | {_T['exit_ever_2017']['ff']['coef']*100:+.2f} | {pp(_T['exit_ever_2017']['ff']['ci95'])} | {_T['exit_ever_2017']['n']:,} / {_T['exit_ever_2017']['n_partners']:,} |
""")


# ── Table 7 extra: split-sample vintage difference (P001-60 B2) vs pooled interaction ──────────────────────────────────────
_S = e60["B_vintage_contrast"]["exit_ever_2017"]["split_sample"]
w("t7_vintage_split.md", f"""| Vintage difference from separate regressions per vintage, eventual exit (deals through 2017-10): β_int(2015–17) − β_int(2010–14), independent draws | {_S['difference_2015_17_minus_2010_14_independent_draws']['coef']*100:+.2f} | {pp(_S['difference_2015_17_minus_2010_14_independent_draws']['ci95'])} | — | — | — | — | — | {_S['n_2010_14']:,} + {_S['n_2015_17']:,} / — |""")

# ── Table 8 Mundlak rows (P001-60 D) ──────────────────────────────────────────────────────────────────────────────────────
_D60 = e60["D_mundlak_extended"]
def mrow(lab, v):
    return f"| {lab} | {v['dev_terrain']['coef']:+.3f} {ci_pt(v['dev_terrain'], 3)} | {v['fm_terrain']['coef']:+.3f} {ci_pt(v['fm_terrain'], 3)} | {v['contrast_dev_minus_fm']['coef']:+.3f} {ci_pt(v['contrast_dev_minus_fm'], 3)} | {v['n']:,} |"
w("t8_mundlak.md", f"""## Panel B. Where the association sits: within-firm and between-firm coefficients on the composition component (fixed 36-month horizon; Mundlak decomposition)
| Specification | Within firm (deviation from firm mean) 95% CI | Between firms (firm mean) 95% CI | Within − between 95% CI | Partners |
|---|---|---|---|---|
{mrow("Component split into within and between; adjusted rate, log deal count, gender and tenure as levels (partial decomposition)", _D60["baseline_partial_mundlak"])}
{mrow("+ adjusted rate and log deal count also split into within and between", _D60["full_mundlak_adj_lnn"])}
{mrow("Every regressor split into within and between", _D60["full_mundlak_all_within_between"])}

*Dependent variable: the partner's post-period (2017-11 to 2020-10) mean benchmarked 36-month exit. Home-firm cluster bootstrap (400). In the second row the firm mean of the adjusted rate carries {_D60['full_mundlak_adj_lnn']['fm_adj']['coef']:+.3f} {ci_pt(_D60['full_mundlak_adj_lnn']['fm_adj'], 3)} and its within-firm deviation {_D60['full_mundlak_adj_lnn']['dev_adj']['coef']:+.3f} {ci_pt(_D60['full_mundlak_adj_lnn']['dev_adj'], 3)}; the firm means of the component and of the adjusted rate correlate at {_D60['corr_fm_terrain_fm_adj']:+.2f}. Source: P001-60.*
""")

# ── Appendix Table IA.8: population check (P001-63) ───────────────────────────────────────────────────────────────────────
_C63 = e63["C_vc_only_key_results"]
_tb = e63["B_partner_titles"]["share_by_bucket_pairs"]
w("tableIA8.md", f"""# Appendix Table IA.8. Population check: investor types, attributed partners' titles, and key results on venture-capital-type firms only
## Panel A. Composition of the attributed records (NA+EU)
| | Share |
|---|---|
| Deals at investors whose Crunchbase type includes venture capital, micro VC, or corporate VC | {e63['A_investor_types']['share_deals_vc_type_naeu']*100:.1f}% |
| Deals at investors with no recorded type | {e63['A_investor_types']['share_deals_missing_type_naeu']*100:.1f}% |
| Most common first-listed investor types (share of deals) | {"; ".join(f"{k} {v*100:.1f}%" for k, v in list(e63['A_investor_types']['first_type_shares_naeu'].items())[:6])} |
| Attributed partner–firm pairs by job title at the firm: general/managing/founding partner; other partner; principal; director/MD/VP; founder/CEO/chief; associate/analyst; other; no job record | {"; ".join(f"{_tb[k]*100:.1f}%" for k in ("general/managing/founding partner", "partner (other)", "principal", "director/managing director/VP", "founder/CEO/chief", "associate/analyst", "other title", "no job record at the firm"))} |

## Panel B. Key results restricted to venture-capital-type investors
| | Estimate | 95% CI | n / cells or partners |
|---|---|---|---|
| Matching coefficient, firm × year cells (pp) | {_C63['matching_cell0']['coef_pp']:+.2f} | [{_C63['matching_cell0']['ci95_pp'][0]:+.2f}, {_C63['matching_cell0']['ci95_pp'][1]:+.2f}] | {_C63['matching_cell0']['n']:,} / {_C63['matching_cell0']['n_cells']:,} |
| Matching coefficient, firm × year × sector × stage cells (pp) | {_C63['matching_cell_stage']['coef_pp']:+.2f} | [{_C63['matching_cell_stage']['ci95_pp'][0]:+.2f}, {_C63['matching_cell_stage']['ci95_pp'][1]:+.2f}] | {_C63['matching_cell_stage']['n']:,} / {_C63['matching_cell_stage']['n_cells']:,} |
| Peer comparison, exit by sample end, female-founded deals through 2017-10, firm × year × sector: NA+EU (pp) | {_C63['peer_exit_ever_2017_cell_cat_NAEU']['coef_pp']:+.2f} | [{_C63['peer_exit_ever_2017_cell_cat_NAEU']['ci95_pp'][0]:+.2f}, {_C63['peer_exit_ever_2017_cell_cat_NAEU']['ci95_pp'][1]:+.2f}] | {_C63['peer_exit_ever_2017_cell_cat_NAEU']['n']:,} / {_C63['peer_exit_ever_2017_cell_cat_NAEU']['n_cells']:,} |
| &nbsp;&nbsp;global (pp) | {_C63['peer_exit_ever_2017_cell_cat_GLOBAL']['coef_pp']:+.2f} | [{_C63['peer_exit_ever_2017_cell_cat_GLOBAL']['ci95_pp'][0]:+.2f}, {_C63['peer_exit_ever_2017_cell_cat_GLOBAL']['ci95_pp'][1]:+.2f}] | {_C63['peer_exit_ever_2017_cell_cat_GLOBAL']['n']:,} / {_C63['peer_exit_ever_2017_cell_cat_GLOBAL']['n_cells']:,} |
| Within-partner β_int, 36-month exit, deals through 2020-10 (partner effects; no deal controls; pp) | {_C63['within_partner_exit3_2020_no_controls']['ffp']['coef']*100:+.2f} | {pp(_C63['within_partner_exit3_2020_no_controls']['ffp']['ci95'])} | {_C63['within_partner_exit3_2020_no_controls']['n']:,} / {_C63['within_partner_exit3_2020_no_controls']['n_partners']:,} ({_C63['within_partner_exit3_2020_no_controls']['n_female_partners']}) |
| Female mean percentile shift, raw → adjusted (exit by sample end; percentile points) | {_C63['rank_shift_female_sample_end']['coef']:+.2f} | [{_C63['rank_shift_female_sample_end']['ci95'][0]:+.2f}, {_C63['rank_shift_female_sample_end']['ci95'][1]:+.2f}] | {_C63['rank_shift_female_sample_end']['n_partners']:,} ({_C63['rank_shift_female_sample_end']['n_female']}) |

*Investor types are Crunchbase's investor_types field (a firm may list several); "partner" titles are read from the people–organization job records of the attributed partner at the investing firm. Investor-firm cluster bootstrap (500) for the cell estimators, partner cluster (400) for the within-partner row, partner resampling (500) for the rank shift. Source: P001-63.*
""")

# ---- Figures ----
# Figure 1: matching ladder — coefficients (original sample and common support) with the cross-deal information each layer keeps
fig, ax = plt.subplots(figsize=(6.4, 3.6))
names = ["Firm x year", "+ sector", "+ stage"]; keys61 = ["L0_invyear", "L1_pluscat", "L2_plusstage"]
vo = [e61["B_original_ladder"][k]["coef_pp"] for k in keys61]; lo_o = [e61["B_original_ladder"][k]["ci95_pp"][0] for k in keys61]; hi_o = [e61["B_original_ladder"][k]["ci95_pp"][1] for k in keys61]
vc = [e61["C_common_support_ladder"][k]["coef_pp"] for k in keys61]; lo_c = [e61["C_common_support_ladder"][k]["ci95_pp"][0] for k in keys61]; hi_c = [e61["C_common_support_ladder"][k]["ci95_pp"][1] for k in keys61]
x = np.arange(3)
ax.bar(x - 0.18, vo, 0.36, color="#4C72B0", label="Original sample at each layer")
ax.bar(x + 0.18, vc, 0.36, color="#DD8452", label="Common support (rows in cells mixed at the finest level)")
ax.errorbar(x - 0.18, vo, yerr=[np.array(vo) - lo_o, np.array(hi_o) - vo], fmt="none", ecolor="black", capsize=3, lw=1)
ax.errorbar(x + 0.18, vc, yerr=[np.array(vc) - lo_c, np.array(hi_c) - vc], fmt="none", ecolor="black", capsize=3, lw=1)
for k_, xi in zip(keys61, x):
    dg = e61["A_diagnostics_by_cell"][k_]
    ax.text(xi, max(hi_o[xi], hi_c[xi]) + 0.35, f"d = {dg['d_share_sxx_single_round']:.2f}\n{dg['n_unique_rounds_mixed']:,} rounds", ha="center", va="bottom", fontsize=7)
ax.axhline(0, color="grey", lw=0.8); ax.set_xticks(x, names); ax.set_ylabel("Female-partner coefficient on female-founded (pp)")
ax.set_ylim(top=max(hi_o + hi_c) + 2.2); ax.set_title("Figure 1. Matching ladder and cross-deal information (NA+EU)"); ax.legend(fontsize=7, loc="upper right")
fig.tight_layout(); fig.savefig(os.path.join(OUT_F, "figure1_ladder.png"))

# Figure 2: rank change — mean percentile by gender, raw vs adjusted, at three benchmark levels (sample end) and at the fixed horizons
fig, ax = plt.subplots(figsize=(6.4, 3.6))
levels = [("Year", e62["B_benchmark_levels_sample_end"]["year"]), ("Year x stage", e62["B_benchmark_levels_sample_end"]["year_stage"]), ("Year x sector x stage", e62["A_accounting_sample_end"]),
          ("36-month exit\n(deals to 2020-10)", e62["C_fixed_horizon"]["exit3_deals_to_2020_10"]["year_sector_stage"]), ("72-month exit\n(deals to 2017-10)", e62["C_fixed_horizon"]["exit6_deals_to_2017_10"]["year_sector_stage"])]
x = np.arange(len(levels))
fr = [v["female_raw_pct"]["coef"] for _, v in levels]; fa = [v["female_adj_pct"]["coef"] for _, v in levels]; mr = [v["male_raw_pct"]["coef"] for _, v in levels]; ma = [v["male_adj_pct"]["coef"] for _, v in levels]
ax.plot(x, fr, "o", color="#C44E52", label="Women, raw rank"); ax.plot(x, fa, "s", color="#C44E52", mfc="white", label="Women, adjusted rank")
ax.plot(x, mr, "o", color="#4C72B0", label="Men, raw rank"); ax.plot(x, ma, "s", color="#4C72B0", mfc="white", label="Men, adjusted rank")
for xi in x: ax.annotate("", xy=(xi, fa[xi]), xytext=(xi, fr[xi]), arrowprops=dict(arrowstyle="->", color="#C44E52", lw=1))
for xi, (_, v) in enumerate(levels): ax.text(xi + 0.08, (fr[xi] + fa[xi]) / 2, f"{v['female_shift']['coef']:+.1f}\n[{v['female_shift']['ci95'][0]:+.1f}, {v['female_shift']['ci95'][1]:+.1f}]", fontsize=7, va="center")
ax.set_xticks(x, [l for l, _ in levels], fontsize=7); ax.set_ylabel("Mean percentile rank"); ax.axhline(50, color="grey", lw=0.8, ls=":")
ax.set_title("Figure 2. Benchmark adjustment and mean percentile ranks, by gender"); ax.legend(fontsize=7, ncol=2, loc="lower left")
fig.tight_layout(); fig.savefig(os.path.join(OUT_F, "figure2_rank_change.png"))

# Figure 3: horizon dependence on one sample (deals through 2017-10), with differences from the same draws
fig, ax = plt.subplots(figsize=(6.4, 3.6))
hz = [("36", "exit3"), ("60", "exit5"), ("72", "exit6"), ("96", "exit8"), ("eventual", "exit_ever")]
x = np.arange(len(hz)); vals = [e57["A_2017"][k]["ffp"]["coef"] * 100 for _, k in hz]; lo = [e57["A_2017"][k]["ffp"]["ci95"][0] * 100 for _, k in hz]; hi = [e57["A_2017"][k]["ffp"]["ci95"][1] * 100 for _, k in hz]
ax.errorbar(x, vals, yerr=[np.array(vals) - lo, np.array(hi) - vals], fmt="o-", color="#4C72B0", capsize=4, lw=1, label="β_int (female partners' additional female-founded − other gap)")
v20 = e57["B_2020"]["exit3"]["ffp"]; ax.errorbar([0], [v20["coef"] * 100], yerr=[[v20["coef"] * 100 - v20["ci95"][0] * 100], [v20["ci95"][1] * 100 - v20["coef"] * 100]], fmt="D", color="#DD8452", capsize=4, lw=1, label="36 months, deals through 2020-10")
ax.axhline(0, color="grey", lw=0.8); ax.axhspan(-5, 5, color="grey", alpha=0.07, label="±5-point reference band")
_H = e57["A_horizon_differences_same_draws"]
for xi, (_, k) in enumerate(hz[1:], start=1):
    dk = _H[f"{k}_minus_exit3"]; ax.text(xi, hi[xi] + 0.6, f"Δ vs 36m {dk['coef']*100:+.1f}\n[{dk['ci95'][0]*100:+.1f}, {dk['ci95'][1]*100:+.1f}]", ha="center", fontsize=7)
ax.set_xticks(x, [f"{h} months" if h != "eventual" else "exit by\nsample end" for h, _ in hz], fontsize=8); ax.set_ylabel("Percentage points"); ax.set_ylim(top=max(hi) + 4)
ax.set_title("Figure 3. Within-partner differential across exit horizons (deals to 2017-10)"); ax.legend(fontsize=7, loc="lower left")
fig.tight_layout(); fig.savefig(os.path.join(OUT_F, "figure3_horizon.png"))

# Supplementary figures (Internet Appendix): event study (former Figure 2) and the financing-ladder channel (former Figure 3)
fig, ax = plt.subplots(figsize=(5.5, 3.2))
pj_ = e11["path_join"]
ks = sorted(int(k) for k in pj_)
ys = [pj_[str(k)] for k in ks]
ax.plot([k for k in ks], ys, "o-", color="#4C72B0", label="Arrival stack (deal-level, k=-1 ref)")
pci = e11.get("path_join_ci", {})
if pci:
    ax.errorbar([k for k in ks if str(k) in pci], [pj_[str(k)] for k in ks if str(k) in pci], yerr=[[pj_[str(k)] - pci[str(k)][0] for k in ks if str(k) in pci], [pci[str(k)][1] - pj_[str(k)] for k in ks if str(k) in pci]], fmt="none", ecolor="#4C72B0", capsize=3, lw=1, label="95% CI per half-year")
ax.scatter([-1], [0], color="#4C72B0", marker="s")
ax.axvline(-0.5, color="grey", ls=":", lw=1)
ax.axhline(0, color="grey", lw=0.8)
ax.fill_between([-0.5, 3.5], e11["join"][1][0] * 100, e11["join"][1][1] * 100, color="#4C72B0", alpha=0.10, label="Pooled post-period 95% CI (deal-weighted)")
ax.set_xlabel("Half-years relative to arrival")
ax.set_ylabel("FF share effect (pp)")
ax.set_title("Figure A1. Female-partner arrivals and new-deal composition")
ax.legend(fontsize=7)
fig.tight_layout()
fig.savefig(os.path.join(OUT_F, "figureA1_eventstudy.png"))

fig, ax = plt.subplots(figsize=(6.2, 3.4))
x = np.arange(3)
cf = [c for c in e6["p_fp_given_ff"][1]]
ax.bar(x - 0.18, pf, 0.36, label="Female-founded deals", color="#4C72B0")
ax.bar(x + 0.18, pm, 0.36, label="Deals with no observed female founder", color="#BBBBBB")
ax.errorbar(x - 0.18, pf, yerr=[[pf[i] - cf[i][0] * 100 for i in range(3)],
                                [cf[i][1] * 100 - pf[i] for i in range(3)]],
            fmt="none", ecolor="black", capsize=4, lw=1)
cm = [c for c in e6["p_fp_given_mf"][1]]
ax.errorbar(x + 0.18, pm, yerr=[[pm[i] - cm[i][0] * 100 for i in range(3)], [cm[i][1] * 100 - pm[i] for i in range(3)]], fmt="none", ecolor="black", capsize=4, lw=1)
ax.set_xticks(x, ["Early", "Series A", "Series B+"])
ax.set_ylabel("P(female partner | deal) %")
ax.set_title("Figure A2. Female-partner share by stage")
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(OUT_F, "figureA2_channel.png"))
print("figures: figure1-3 + IA.1-2 saved")
