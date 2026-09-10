*W5 v8 (2026-09-10, post external review); regenerated from P001-02 … P001-60 and I-73 … I-82 via `06_code/p001_09_exhibits.py`; assembled by the build step. Do not edit by hand.*

### Table 1. Sample and measurement coverage
| | |
|---|---|
| Partner-attributed deals with observable founder gender (global) | 154,123 |
| — excluded at construction (founder gender unobservable) | 34,457 |
| — North America + Europe (primary sample) | 127,061 |
| Partner gender observed (share of attributed deals) | 94.2% |
| Founder gender determinable (share of funded companies) | 83.2% |
| Female-founded (FF) share of deals | 17.2% |
| Female-partner (FP) share of deals | 10.6% |
| Determinability selection: US share diff (det − undet) | +28.2pp |
| — early-stage share diff | −17.8pp |
| — mean vintage diff (years) | −1.94 |

*Sources: sample_v1.parquet (sha256₁₆ 5b83f6785878d867); I-73; P001-08. Population: deals with observable founder gender.*

### Table 2. Partner–founder gender matching: decomposition ladder (NA+EU)
| Cell specification | FP coefficient (pp) | 95% CI |
|---|---|---|
| Firm × year | +6.96 | [+5.54, +8.25] |
| + sector | +3.21 | [+1.96, +4.75] |
| + stage (full cells) | +0.66 | [−0.48, +1.89] |
| Reverse order: + stage first | +5.77 | [+4.34, +7.04] |
| NA, full cells | +0.63 | [−0.67, +2.11] |
| EU, full cells | −0.37 | [−2.65, +2.03] |
| NA − EU difference | +1.00 | [−1.65, +3.65] |

Composition shares (order-bracketed): total 90.5%; sector 54–73%; stage 17–37%.

*Outcome: deal is female-founded. n = 127,061. Investor-cluster bootstrap. Within-cell permutation of the raw association: p < 0.005 (I-74). Sources: P001-02, P001-14.*

### Table 3. The stage tilt and its origins
| | Estimate | 95% CI |
|---|---|---|
| FP–early-stage association (firm×year) | +3.84pp | [+2.60, +5.00] |
| — among male-founded deals only | +3.12pp | [+1.74, +4.37] |
| Mean tenure: female / male partners (yrs) | 2.75 / 4.23 | |
| Within tenure-bin cells (attenuation 47%) | +2.02pp | [+0.91, +3.30] |
| Stage-graduation slope diff (F−M, pp/yr) | −0.42 | [−0.99, +0.15] |
| Outcome test, early deals (fon), exact stage cells | −1.12pp | [−3.03, +0.62] |

*Sources: I-80, I-81, P001-08.*

### Table 4. Where the exit gap lives: female-founded deals
## Panel A. Exit by sample end, deals through October 2017: the location ladder
| Comparison | Global | 95% CI | NA+EU | 95% CI |
|---|---|---|---|---|
| Year effects only | −2.73 | [−8.28, +3.01] | −3.35 | [−7.90, +2.16] |
| Firm × year | +0.21 | [−5.90, +5.34] | −0.50 | [−6.76, +5.42] |
| Additive firm+year+sector+stage | +0.78 | [−5.75, +7.05] | −0.82 | [−8.20, +5.24] |
| **Firm × year × sector (peer comparison)** | **-6.25 | [−11.50, −1.38]** | −4.55 | [−10.13, +0.22] |
| + stage | −1.75 | [−5.29, +1.43] | −1.02 | [−4.49, +2.67] |


## Panel B. Fixed 36-month exit horizon, deals through 2020-10 (NA+EU): the cross-deal comparisons as the estimator
| Cell definition | Mixed cells / deals | Multi-round (cross-deal) cells / deals | Cells with exit variation | Share of Σx̃² from single-round cells (d) | β, all cells (pp) | β, cross-deal cells (pp) | 95% CI | MDE80 (pp; sd) | Placebo 95th pct (pp) |
|---|---|---|---|---|---|---|---|---|---|
| firm×year×sector | 411 / 1,174 | 174 / 652 | 61 | 0.47 | −1.44 | −2.74 | [−9.41, +2.70] | 8.23; 0.25 | 5.64 |
| firm×year×sector×stage | 380 / 953 | 78 / 258 | 23 | 0.74 | −0.42 | −1.64 | [−13.20, +6.26] | 13.81; 0.42 | 7.28 |
| firm×2yr×sector | 399 / 1,338 | 228 / 956 | 82 | 0.31 | −0.28 | −0.40 | [−4.22, +3.04] | 5.47; 0.17 | 4.58 |
| firm×3yr×sector | 392 / 1,451 | 243 / 1,124 | 84 | 0.25 | −0.87 | −1.17 | [−5.21, +2.44] | 5.61; 0.17 | 3.8 |
| firm×sector + year FE | 360 / 1,960 | 274 / 1,765 | 111 | 0.12 | −2.93 | −2.26 | [−5.86, +1.52] | 5.20; 0.16 | 3.44 |
| Deal-level coding, firm × year × sector: female-only vs male-only attributed deals (mixed-attribution deals excluded) | — | 113 cells / 335 deals | 45 | 0 by construction | — | −8.57 | [−20.44, +0.14] | 14.61 | 8.57 |
| Reference: sample-end horizon, deals through 2017-10, firm × year × sector (canonical run; Appendix Table IA.2, Panel E) | 174 / 430 | 61 / 195 | 30 | 0.58 | −4.55 | −10.71 | [−0.22, +0.02] | 17.51; — | 12.67 |

*Panel B: exit within 36 months of the deal; FF deals 13,187, base rate 0.125. Σx̃² is the within-cell estimator's identifying variance and d the share of it contributed by cells whose partner rows all belong to one round (co-attributed pairs), so that the all-cells coefficient equals the cross-deal coefficient times (1 − d). MDE80 = minimum detectable effect at 80 percent power. β on cross-deal cells is the within-cell estimator restricted to mixed cells whose partner rows span at least two rounds; investor-firm cluster bootstrap (500); placebo = 95th percentile of |β| under within-cell reassignment of partner gender (400). The firm × sector row adds additive year effects (two-way demeaning); with additive effects the identity β_all = (1 − d)·β_cross-deal holds only approximately, which is why that row's all-cells and cross-deal coefficients do not satisfy it exactly. The reference row repeats the canonical sample-end estimates of P001-49 so that the same specification carries one set of numbers throughout the paper. Sources: P001-55, P001-49.*

*Deals through 2017-10; exit = acquisition or IPO by sample end. n = 8,058 (global) / 7,103 (NA+EU). The deficit is detected only in the interacted firm–year–sector comparison; the coarser intervals contain both zero and the peer-comparison estimate, and only the + stage row's interval excludes it. All rows are estimated on one sample and one bootstrap draw. Identifying variation of the peer-comparison row (Appendix Table IA.2, Panel D): 174 NA+EU cells contain both a female- and a male-partner female-founded deal (430 deals, 6.0 percent of the sample; global 191 cells, 478 deals). Base exit rate among female-founded deals, global: 46.4 percent (I-78). Sources: P001-10 (ladder), P001-15 (additive row), P001-40 (identifying variation), I-78 (base rate).*

### Table 5. Within-partner outcome test and covariate-adjusted battery (NA+EU)
## Panel A. Covariate-adjusted exit hazard on the Table 4 cells (firm × year × sector × stage × duration effects; deal controls)
| | Estimate | 95% CI |
|---|---|---|
| Annual exit hazard gap (pp/yr) | −0.240 | [−0.81, +0.26] |
| Baseline hazard (%/yr) | 6.19 | interval within ±25% of baseline: yes |
| Same gap, multi-round cell–year groups only (pp/yr); MDE80 | −1.699; 11.31 | [−11.83, +2.87]; within ±25% of baseline: no |
| Identifying base: cell–year groups with female-partner variation; share single-round co-attributions; groups with exit variation | 814; 0.89; 10 | — |

## Panel B. Within-partner outcome test: female-founded vs other deals of the same partner, by partner gender (36-month exit net of the year × sector × stage market mean; deals through 2020-10). β_int is the difference between female and male partners' own female-founded − other gaps
| Specification | β_int: female partners' extra FF gap (pp) | 95% CI | MDE80 (pp) | β_int in sd of the benchmarked outcome | inside ±5 pp | β_FF: male partners' own FF − other gap (pp) | 95% CI | n deals / partners (women) |
|---|---|---|---|---|---|---|---|---|
| Partner fixed effects, deal controls; partner-cluster bootstrap | +0.48 | [−1.82, +2.79] | 3.50 | +0.014 | yes | −2.55 | [−3.47, −1.68] | 49,835 / 3,448 (418) |
| Same; investor-firm clusters | +0.48 | [−2.31, +3.11] | 3.85 | +0.014 | yes | −2.55 | [−3.46, −1.70] | 49,835 / 3,448 (418) |
| Firm × year fixed effects instead of partner effects (partner gender included) | +0.91 | [−2.29, +3.82] | 4.06 | +0.027 | yes | −2.70 | [−3.73, −1.67] | 46,152 / 3,448 (418) |
| Partner × two-year fixed effects | +1.22 | [−1.24, +4.19] | 3.82 | +0.036 | yes | −2.67 | [−3.67, −1.77] | 46,458 / 3,448 (418) |
| Partners with ≥ 5 deals | +0.48 | [−2.38, +3.33] | 3.85 | +0.014 | yes | −2.69 | [−3.61, −1.95] | 47,001 / 2,474 (286) |
| Vintages 2015 and later | +1.18 | [−1.60, +3.58] | 3.78 | +0.037 | yes | −2.43 | [−3.36, −1.42] | 32,946 / 3,318 (408) |
| + company characteristics (Crunchbase profile values; see note) | +0.37 | [−2.03, +2.68] | 3.45 | +0.011 | yes | −1.41 | [−3.27, +0.59] | 49,835 / 3,448 (418) |
| + prior patent applications (any before the deal; log count; assignee-match indicator, which is not pre-deal and absorbs unmatched zeros) | +0.53 | [−1.78, +2.83] | 3.46 | +0.016 | yes | −2.51 | [−3.31, −1.63] | 49,835 / — (any prior patent: +3.99 pp [+2.36, +5.66]) |
| Follow-on financing within 36 months (deals through 2020-10) | −1.28 | [−4.57, +2.04] | 4.59 | −0.029 | yes | −0.37 | [−1.38, +0.70] | 49,835 / 3,448 (418) |
| Exit by sample end (deals through 2017-10) | −6.51 | [−11.77, −0.54] | 8.52 | −0.144 | no | −1.88 | [−3.72, −0.03] | 28,556 / 1,998 (206) |
| &nbsp;&nbsp;vintages 2010–14 | −10.54 | [−17.93, −2.71] | 10.89 | −0.234 | no | −0.75 | [−3.42, +1.65] | 15,203 / 1,146 (89) |
| &nbsp;&nbsp;vintages 2015–17 | −3.22 | [−9.96, +3.54] | 10.01 | −0.071 | no | −2.78 | [−5.16, −0.40] | 12,930 / 1,291 (147) |
| &nbsp;&nbsp;partners with an attributed deal after October 2020 | −6.63 | [−12.48, −0.33] | 8.76 | −0.147 | no | −1.61 | [−3.96, +0.58] | 23,710 / 1,428 (146) |
| &nbsp;&nbsp;partners without one | −6.22 | [−18.06, +5.57] | 17.86 | −0.137 | no | −3.04 | [−7.00, +0.94] | 4,846 / 559 (59) |
| &nbsp;&nbsp;IPO by sample end | −3.02 | [−6.58, +0.44] | 5.03 | −0.110 | no | +1.27 | [+0.16, +2.55] | 28,556 / 1,987 (205) |
| &nbsp;&nbsp;acquisition by sample end (no IPO) | −3.49 | [−9.79, +2.66] | 8.69 | −0.075 | no | −3.15 | [−5.20, −1.29] | 28,556 / 1,987 (205) |
| &nbsp;&nbsp;company clusters | −6.51 | [−12.28, −0.91] | 8.10 | −0.144 | no | −1.88 | [−4.44, +0.87] | 28,556 / 1,987 (205) |
| 36-month exit, vintages 2010–14 | −3.23 | [−9.51, +4.12] | 10.03 | −0.088 | no | −3.23 | [−5.04, −1.40] | 16,389 / 1,146 (89) |
| &nbsp;&nbsp;vintages 2015–17 | +0.08 | [−4.50, +4.86] | 6.53 | +0.003 | yes | −2.98 | [−4.41, −1.42] | 15,289 / 1,374 (161) |
| &nbsp;&nbsp;vintages 2018–20 | +2.91 | [−0.15, +5.95] | 4.30 | +0.090 | no | −2.38 | [−3.74, −1.05] | 16,831 / 1,926 (264) |
| 36-month exit, company clusters | +0.48 | [−2.09, +2.75] | 3.67 | +0.014 | yes | −2.55 | [−3.70, −1.38] | 49,835 / 3,425 (415) |
| 36-month exit, year × sector × stage × country benchmark | +0.90 | [−1.76, +3.48] | 3.59 | +0.027 | yes | −2.67 | [−3.53, −1.78] | 48,367 / 3,319 (402) |
| Same partners and window as eventual exit (deals through 2017-10): 36-month exit | −1.29 | [−5.22, +2.37] | 5.26 | −0.037 | no | −2.92 | [−4.18, −1.92] | 28,556 / 1,998 |
| &nbsp;&nbsp;72-month exit | −4.12 | [−9.10, +0.87] | 7.24 | −0.092 | no | −1.70 | [−3.50, −0.06] | 28,556 / 1,998 |
| &nbsp;&nbsp;exit after month 36 (among deals not exited by month 36) | −5.22 | [−10.82, +0.14] | 8.13 | −0.116 | no | +1.05 | [−0.49, +2.74] | 28,556 / 1,998 |
| &nbsp;&nbsp;follow-on financing within 36 months | −0.74 | [−5.52, +3.35] | 6.62 | −0.017 | no | +0.10 | [−1.11, +1.18] | 28,556 / 1,998 |
| Female partners' own female-founded − other gap (β_FF + β_int), 36-month exit, deals through 2020-10, 2,000 draws | −2.07 | [−4.42, +0.23] | 3.32 | −0.061 | yes | — | — | — |
| &nbsp;&nbsp;same, follow-on financing | −1.65 | [−4.60, +1.39] | 4.24 | −0.038 | yes | — | — | — |
| &nbsp;&nbsp;same, eventual exit, deals through 2017-10 | −8.38 | [−13.83, −3.27] | 7.57 | −0.185 | no | — | — | — |
| Vintage contrast, eventual exit (deals through 2017-10): β_int for 2015–17 minus β_int for 2010–14 (pooled interaction model) | +1.83 | [−6.87, +9.49] | 11.71 | +0.040 | no | — | — | — |
| Vintage contrast, 36-month exit (deals through 2020-10): β_int for 2018–20 minus β_int for 2010–14 | +0.97 | [−4.76, +6.74] | 8.16 | +0.029 | no | — | — | — |
| Exits dated on or before the deal excluded (post-deal rule): 36-month exit, deals through 2020-10 | +0.64 | [−1.57, +3.27] | 3.47 | +0.019 | yes | — | — | 49,835 / — |
| &nbsp;&nbsp;same, eventual exit, deals through 2017-10 | −6.50 | [−11.85, −1.42] | 7.68 | −0.144 | no | — | — | 28,556 / — |

*Panel B: partners with at least one female-founded and one other deal in the window. Eligible deals 50,153 → 49,847 with a market benchmark (306 deals alone in their year × sector × stage cell have none) → 49,835 in the estimation sample (12 are a partner's only remaining deal); 3,448 partners (418 women) are eligible and 3,425 (415) retain both kinds of deal after these drops and identify β_int; the partner counts shown in each row follow the same convention (eligible for the P001-54 rows, identifying for the later rows). 33,142 deals are dated 2015 or later; exit3 base rate 0.157. The "inside ±5 pp" column marks whether the 95% interval lies within a reference band equal to the peer-comparison gap of Table 4; it is a reference scale, not a materiality threshold. Outcome = deal outcome minus the leave-one-out mean of its year × sector × stage cell; deal controls as in Panel A. β_FF is the within-partner gap for male partners; β_int is the additional gap for female partners (favoritism predicts β_int < 0); female partners' own gap is β_FF + β_int, with its interval from the same bootstrap draws. The vintage-contrast rows come from one pooled regression with β_int interacted with vintage indicators; the post-deal-rule rows recode exits dated on or before the deal as non-exits (Appendix IA.1). Same-window rows re-estimate the specification on the eventual-exit sample (P001-57). Bootstrap two-sided p-values for β_int on the three featured outcomes (36-month exit, follow-on, exit by sample end): 0.708, 0.424, 0.022; Holm-adjusted 0.848, 0.848, 0.066. Dropping any one of the 206 women from the exit-by-sample-end row moves β_int by at most 0.88 points. Female partners' female-founded deals outside this sample (partners with no other deal): 23.4 percent. Sources: P001-54, P001-57, P001-59, P001-60.*

## Panel C. Outcome battery (covariate-adjusted, pp) with Romano–Wolf stepdown
| Outcome | Gap | 95% CI | Multiple-testing |
|---|---|---|---|
| fon (adj.) | +0.91 | [−1.35, +3.21] | RW p = 1.0 |
| exit_ever (adj.) | −0.94 | [−4.20, +2.41] | RW p = 0.703 |
| ipo6 (adj.) | −0.40 | [−2.27, +1.37] | RW p = 0.91 |
| acqp6 (adj.) | +0.65 | [−0.24, +2.24] | RW p = 0.997 |
| closed6 (adj.) | +1.38 | [−0.78, +3.84] | RW p = 0.64 |

Within-cell permutation (unadjusted spec): follow-on p = 0.514; exit p = 0.52.
IPO and closure margins remain unresolved (MDE80 ≈ 2.8 / 3.6 pp) rather than established nulls.

*Deal controls: round size, company age, prior rounds, syndicate size, co-investor experience (all at deal date). Identifying base of the hazard (share of cell–year groups that are co-attributions on a single round; gap on multi-round groups): Appendix Table IA.2, Panel E. The deal-fixed continuation margin is Table 8. Sources: P001-12, P001-13, P001-14, P001-03 (MDEs), P001-50 (identifying base).*

### Table 6. Balance of company characteristics within the cells that identify the peer comparison (female-founded deals, firm × year × sector; deals through 2017-10)
| Characteristic | Female − male partner, all mixed cells | 95% CI | Standardized (diluted) | MDE (sd) | Share of Σx̃² from single-round cells (d) | Identifying cells only: standardized difference [95% CI in sd]; MDE (sd) | Same, stage in the cell | n (all) |
|---|---|---|---|---|---|---|---|---|
| Company age at deal (years) | −0.102 | [−0.427, +0.166] | −0.030 | 0.12 | 0.58 | −0.09 [−0.37, +0.14]; MDE 0.37 | +0.22 [−0.08, +0.48]; MDE 0.42 | 430 |
| log(1 + prior equity rounds) | −0.060 | [−0.132, +0.007] | −0.096 | 0.15 | 0.58 | −0.24 [−0.47, −0.01]; MDE 0.35 | +0.09 [−0.17, +0.43]; MDE 0.46 | 430 |
| log(1 + prior capital raised) | −0.646 | [−1.743, +0.329] | −0.082 | 0.18 | 0.58 | −0.20 [−0.51, +0.07]; MDE 0.42 | −0.09 [−0.38, +0.29]; MDE 0.51 | 430 |
| Employee-count band (1–9) | −0.152 | [−0.304, −0.001] | −0.086 | 0.12 | 0.58 | −0.22 [−0.41, +0.01]; MDE 0.31 | +0.14 [−0.18, +0.57]; MDE 0.52 | 430 |
| Investor count on the previous round | −0.504 | [−0.914, −0.207] | −0.175 | 0.19 | 0.63 | −0.49 [−0.88, −0.24]; MDE 0.45 | −0.38 [−0.94, +0.06]; MDE 0.72 | 269 |
| Number of founders | −0.212 | [−0.430, −0.033] | −0.144 | 0.20 | 0.58 | −0.28 [−0.48, −0.05]; MDE 0.33 | −0.07 [−0.61, +0.49]; MDE 0.84 | 430 |
| Number of female founders | +0.047 | [+0.010, +0.092] | +0.100 | 0.13 | 0.58 | +0.24 [+0.04, +0.46]; MDE 0.31 | +0.00 [−0.65, +0.53]; MDE 0.84 | 430 |
| Share of founders with a recorded degree | −0.003 | [−0.038, +0.029] | −0.011 | 0.16 | 0.58 | −0.03 [−0.33, +0.21]; MDE 0.40 | −0.15 [−0.67, +0.35]; MDE 0.80 | 430 |
| Share of serial founders | −0.031 | [−0.072, +0.005] | −0.078 | 0.14 | 0.58 | −0.18 [−0.40, +0.00]; MDE 0.30 | −0.00 [−0.50, +0.47]; MDE 0.69 | 430 |
| Headquartered in the United States | −0.009 | [−0.037, +0.017] | −0.025 | 0.10 | 0.58 | −0.06 [−0.23, +0.11]; MDE 0.26 | −0.25 [−0.59, +0.00]; MDE 0.43 | 430 |

*Prior patenting (USPTO PatentsView, matched to sample companies by normalized name and country/state/city; P001-58), female − male partner within cell:*
| Characteristic | Identifying (multi-round) cells: difference | 95% CI | Standardized | MDE (sd) | All mixed cells: difference | 95% CI |
|---|---|---|---|---|---|---|
| Any patent application filed before the deal | −0.119 | [−0.208, −0.052] | −0.27 | 0.26 | −0.050 | [−0.090, −0.020] |
| Log (1 + applications filed before the deal) | −0.266 | [−0.430, −0.101] | −0.32 | 0.28 | −0.113 | [−0.191, −0.050] |
| Company matched to a patent assignee (coverage indicator) | −0.098 | [−0.229, +0.042] | −0.20 | 0.40 | −0.042 | [−0.102, +0.014] |

Dilution. A company characteristic is identical for the two partners of a co-attributed pair, so the all-cells coefficient equals the identifying-cells coefficient times (1 − d), where d is the share of identifying variance from single-round cells (identity verified to 0e+00); the identifying cells are the 61 multi-round cells with 195 deals (sector cells) and 20 cells with 51 deals (stage cells; not identified). Joint tests. Largest absolute cluster-robust t across nine characteristics (prior-round investor count, 64 percent coverage, tested separately), against a shared within-cell permutation null (1000 draws): sector cells p = 0.192 (identifying cells only p = 0.172); the test rejects 5 percent of 100 random within-cell reassignments at the 5 percent level. With stage in the cell p = 0.811; on all deals with stage in the cell (974 cells, 2,532 deals) p = 0.761. The Mahalanobis joint test (bootstrap covariance; complete cases n = 269) gives p = 0.658 in the sector cells and is degenerate with stage in the cell (a zero-variance characteristic makes the covariance near-singular). Positive control, post-assignment log round size (female − male partner): same cells −0.139 [−0.255, −0.030]; all deals, firm × year × sector −0.058 [−0.143, +0.021].

*Characteristics are Crunchbase profile values. Founding date, prior equity rounds, prior funding, prior-round investors, and prior patent applications are dated relative to the deal; founder counts and degrees, serial founding, employee-count band, and headquarters are current profile fields whose historical timing is not recorded. The patent match indicator (whether the company appears in the assignee tables) is not a pre-deal quantity.*

### Table 7. Track-record composition: size, pricing, and information content
## Panel A. Re-ranking: raw vs composition-adjusted exit rates
| | Raw → Adjusted |
|---|---|
| Female partners' mean percentile shift | +4.43 pts [+2.13, +6.77] |
| Male partners' mean percentile shift | −0.34 pts [−0.52, −0.15] |
| Female share of top quartile | 7.11% → 8.18% (Δ interval crosses zero) |
| Rank correlation (raw, adjusted) | 0.861 |

## Panel B. Subsequent attributed deal activity: log count of deals attributed to the partner in 2018–2020 on 2010–17 percentiles
| | β (log deals per unit of percentile rank, 0–1) | 95% CI |
|---|---|---|
| Adjusted percentile A, holding the raw percentile fixed (β_A) | +1.54 | [+1.24, +1.86] |
| Raw percentile R, holding A fixed (β_R) = coefficient on the rank difference R − A | −1.73 | [−2.11, −1.39] |
| Adjusted percentile A, holding the rank difference R − A fixed (β_R + β_A; same bootstrap draws) | −0.19 | [−0.32, −0.08] |

## Panel C. External outcomes among partners who move or spin out, 2017-11 to 2023-10
| Outcome | Sample | β on composition component (given adjusted percentile) | 95% CI | β with pre-period late-stage share as control | 95% CI | Late-stage share, own coefficient |
|---|---|---|---|---|---|---|
| New firm records a fund close (partners who spin out) | 380 partners; 221 raise (58.2%) | +0.494 | [+0.143, +0.862] | +0.456 | [−0.086, +0.966] | +0.200 [+0.028, +0.358] |
| log fund size recorded | 197 | +2.501 | [+0.996, +4.194] | +0.662 | [−1.577, +2.964] | +1.423 [+0.756, +2.201] |
| Receiving firm's prior attributed deal count, log(1+n) (partners who move) | 712 | +1.201 | [+0.362, +2.244] | +0.663 | [−0.693, +2.258] | +0.584 [+0.150, +1.062] |
| Joint randomization test, three outcomes (uncontrolled) | 400 permutations of the composition component | Mahalanobis 30.0 vs null 95th percentile 7.5; 3/3 signs aligned | p < 0.003 (no exceedance in 400 permutations) | | | |

## Panel D1. Does composition carry information? Open horizon (exit by sample end); post window 2017-11 to 2023-10
Rows are on the percentile scale (β on raw percentile given adjusted percentile) unless marked *levels* (β on the composition component in exit-probability units).
| Specification | β | 95% CI | n |
|---|---|---|---|
| Baseline cell benchmark | +0.097 | [+0.039, +0.160] | 2,178 |
| Leave-one-out cell benchmark | +0.103 | [+0.034, +0.176] | 2,164 |
| Excluding post-period deals in companies the partner backed pre-period | +0.079 | [+0.017, +0.158] | 1,858 |
| Composition component, levels, given tenure and first-deal-year effects | +0.076 | [−0.018, +0.162] | 2,164 |
| Composition component, levels, home-firm fixed effects | +0.099 | [−0.060, +0.257] | 1,624 |
| Decomposition of the composition component, levels: vintage / stage within year / sector within year–stage | +0.075 / +0.081 / +0.160 | [−0.089, +0.258] / [−0.040, +0.198] / [+0.004, +0.307] | 2,164 |
| Same decomposition, given tenure and first-deal-year effects | −0.037 / +0.057 / +0.151 | [−0.269, +0.212] / [−0.068, +0.189] / [−0.008, +0.300] | 2,164 |
| Contrast, levels: adjusted exit rate, same regression as the composition-component levels row | +0.335 | [+0.284, +0.383] | 2,164 |
| Contrast: adjusted percentile's own coefficient | +0.246 | [+0.208, +0.279] | 2,178 |
Remaining rows (benchmark variation and additional analyses) are in Internet Appendix Table IA.1.

## Panel D2. Same question at a fixed 36-month exit horizon in both periods (post window 2017-11 to 2020-10); levels
β on the composition component, or the named part, in 36-month exit-probability units. Partner-level rows include the adjusted rate, log deal count, gender, tenure, tenure², and first-deal-year effects unless noted. Deal-level rows include the partner's prior within-cell residual, log prior deals, gender, tenure at the deal date and its square, and year effects where no firm–year effect is present.
| Specification | β | 95% CI | n |
|---|---|---|---|
| **Composition component — preferred specification for this question** | **+0.278** | **[+0.075, +0.480]** | 2,017 |
| Sector-within-year–stage part | +0.307 | [+0.057, +0.570] | 2,017 |
| Adjusted exit rate's own coefficient, same regression as the preferred row | +0.180 | [+0.083, +0.281] | 2,017 |
| Home-firm fixed effects (minimum detectable effect 0.38; sector part 0.40) | −0.039 | [−0.328, +0.235] | 1,490 |
| Pre-period restricted to deals whose 36-month window closes before the ranking date (deals through 2014-10; minimum detectable effect 0.35) | +0.090 | [−0.123, +0.350] | 1,127 |
| Reweighted for selection out of post-period observation (inverse probability) | +0.252 | [−0.005, +0.519] | 2,017 |
| Tenure and rank from employment records (join date, title) instead of first-deal tenure; partners with a recorded join date | +0.305 | [+0.117, +0.501] | 1,789 |
| Follow-on construct instead of exit (follow-on within 36 months, both periods) | +0.035 | [−0.159, +0.237] | 2,017 |
| Deal level, within firm–year: composition component (minimum detectable effect 0.16) | +0.058 | [−0.044, +0.176] | 25,600 |
Remaining rows (benchmark variation and additional analyses) are in Internet Appendix Table IA.1.

## Panel E. By partner gender (female − male)
Percentile-scale rows are in fractions of the percentile scale (0.01 = one percentile point); *levels* rows are in exit-probability units (exit by sample end).
| Outcome | β | 95% CI | n |
|---|---|---|---|
| Composition component (raw − adjusted percentile) | −0.048 | [−0.075, −0.025] | 2,686 |
| Composition component, leave-one-out benchmark | −0.050 | [−0.079, −0.022] | 2,661 |
| Post-period within-cell performance, levels | −0.007 | [−0.048, +0.034] | 2,178 |
| Post-period within-cell performance, levels, given composition | −0.008 | [−0.045, +0.031] | 2,178 |
| Pre-period within-cell performance, levels (adjusted exit rate) | +0.014 | [−0.020, +0.049] | 2,686 |
| Composition component, levels | −0.041 | [−0.061, −0.016] | 2,661 |
| Composition component, levels, given tenure and first-deal-year effects | −0.016 | [−0.034, +0.003] | 2,661 |
| Vintage / stage-within-year / sector-within-year–stage parts, levels | −0.017 / −0.016 / −0.007 | [−0.028, −0.009] / [−0.029, −0.002] / [−0.017, +0.004] | 2,661 |
| Composition component, levels, given employment-record tenure and rank | −0.021 | [−0.041, +0.001] | 2,333 |
| Composition component, levels, given rank only | −0.039 | [−0.063, −0.016] | 2,333 |
| Implied contribution of composition to the post-period gap, levels, open horizon (Σ tenure-controlled part gap × tenure-controlled coefficient, same resamples; materiality band ±0.02; interval inside ±0.01) | −0.0014 | [−0.0042, +0.0008] | 2,164 |
| Same, fixed 36-month exit horizon (post window to 2020-10) | −0.0002 | [−0.0041, +0.0053] | 2,017 |

*Partners with ≥5 attributed deals through 2017-10: 2,686 (192 women). Panels B–E: deal-count and gender controls (Panel B additionally pre-period early-stage share and sector breadth); investor-firm cluster bootstrap. Because the adjusted percentile is the raw percentile net of year–sector–stage cell benchmarks, the raw-percentile coefficient given the adjusted percentile equals the coefficient on their difference, the composition component (percentile correlation 0.8614, VIF 7.4); Panel B's negative value is that composition coefficient. Panel D1 and Panel E percentile-scale rows: β per unit of the raw percentile (0.01 = one percentile point); *levels* rows: β per unit of the composition component in exit-probability units. Panel D2's control set is stated in its header; the follow-on-construct row reproduces P001-30 (a separate bootstrap in P001-33 returns the same point). Panel D2 rows below the preferred row are additional analyses. † Exploratory: identifies off within-partner changes in composition over time rather than off placement across partners; clustered by partner. Sources: P001-05, P001-18b, P001-23, P001-25, P001-26, P001-27, P001-28, P001-29, P001-30, P001-31, P001-33, P001-34, P001-36, P001-38, P001-39.*

### Table 8. The deal held fixed: within-round comparison of co-investors on female-founded rounds (NA+EU)
Outcome varies across investors in the same round; company, sector, stage, vintage, founder team, and syndicate are fixed by construction. Round fixed effects; investor experience control; company-cluster bootstrap. β is the female-partner slope in female-founded rounds; "other" is the slope in other rounds; "difference" is female-founded minus other.
| Outcome | β (female-founded rounds) | 95% CI | β (other rounds) | 95% CI | Difference | 95% CI | n rows / companies |
|---|---|---|---|---|---|---|---|
| Firm re-invests in the company's next round (next round within 36 months; conditional) | −0.004 | [−0.042, +0.029] | +0.007 | [−0.010, +0.028] | −0.011 | [−0.055, +0.029] | 7,734 / 1,741 |
| Same, unconditional (no next round coded as zero) | +0.002 | [−0.025, +0.030] | +0.003 | [−0.013, +0.018] | −0.001 | [−0.030, +0.033] | 10,399 / 2,321 |
| Same partner attributed on the next round, given the firm re-invests | −0.002 | [−0.045, +0.037] | +0.004 | [−0.018, +0.026] | −0.007 | [−0.055, +0.038] | 3,301 / 886 |
| Lead-investor flag on the round (recorded on 58 percent of rows) | −0.027 | [−0.088, +0.030] | −0.001 | [−0.032, +0.033] | −0.026 | [−0.097, +0.038] | 4,770 / 1,287 |
| Reverse placebo: firm invested in the company's previous round | −0.004 | [−0.047, +0.037] | −0.016 | [−0.039, +0.010] | +0.012 | [−0.034, +0.060] | 8,898 / 1,942 |

*Variants of the re-investment margin, female-founded rounds only (P001-51; β = female-partner slope; company-cluster bootstrap unless stated):*
| Variant | β | 95% CI | MDE80 | within ±5 pp | n rows / clusters |
|---|---|---|---|---|---|
| Any-female attribution — initial run (400 draws) | −0.38 | [−3.96, +3.15] | 5.21 | yes | 1,623 / 390 |
| Female-only attribution — initial run (400 draws; 127 rows attributed to both a woman and a man dropped, 327 rows in all once rounds left without a female–male contrast fall out) | −1.54 | [−6.94, +2.75] | 6.48 | no | 1,296 / 324 |
| **Any-female attribution — reference run (2,000 draws)** | −0.38 | [−4.30, +3.12] | 5.32 | yes | 1,623 / 390 |
| **Female-only attribution — reference run (2,000 draws)** | −1.54 | [−5.88, +3.21] | 6.41 | no | 1,296 / 324 |
| Three categories: female-only vs male-only | −1.38 | [−5.73, +2.65] | 6.08 | — | 1,623 / — |
| Three categories: mixed attribution vs male-only | +3.57 | [−4.18, +10.26] | 10.16 | — | 127 mixed rows |
| Any-female, investor-cluster bootstrap | −0.38 | [−3.46, +2.78] | 4.49 | yes | 1,623 / 760 |
| Female-only, investor-cluster bootstrap | −1.54 | [−4.91, +2.13] | 4.84 | yes (margin 0.09 pp) | 1,296 / 672 |
| Any-female + all pre-round investor controls† | −0.67 | [−4.14, +2.83] | 5.16 | yes | 1,623 / 390 |
| Female-only + all pre-round investor controls† | −1.59 | [−6.09, +2.77] | 6.34 | no | 1,296 / 324 |
| Any-female + fund-cycle controls (Crunchbase fund age, size, sequence; SEC Form D tier-1 vintages and amounts)‡ | −0.42 | [−4.41, +3.25] | 5.55 | yes | 1,623 / 390 |
| Female-only + fund-cycle controls‡ | −1.72 | [−6.06, +2.38] | 6.08 | no | 1,296 / 324 |
| Round + investor fixed effects, all mixed rounds (fp × female-founded; β = female-founded slope) | −0.94 | [−8.31, +5.91] | 10.46 | no | 7,734 / 291 investors with varying attribution |

*Sample and window (P001-56): β, 95% CI, MDE80 and the ±5 pp verdict under the two treatment definitions:*
| Sample; deals through; next round within | Any-female attribution | Female-only attribution | FF rounds / rows |
|---|---|---|---|
| NA+EU companies; 2020-10; 36 months (baseline) | −0.38 [−3.84, +3.18]; MDE 5.33; yes | −1.54 [−5.36, +3.08]; MDE 6.22; no | 535 / 1,623 |
| All countries; 2020-10; 36 months | −0.10 [−3.44, +3.54]; MDE 5.11; yes | −0.86 [−5.01, +3.37]; MDE 5.93; no | 593 / 1,778 |
| NA+EU; 2021-10; 24 months | −1.20 [−4.59, +2.21]; MDE 4.93; yes | −2.12 [−6.72, +2.50]; MDE 6.52; no | 586 / 1,785 |
| All countries; 2021-10; 24 months | −0.45 [−4.06, +2.71]; MDE 4.87; yes | −1.03 [−4.73, +2.90]; MDE 5.63; yes | 665 / 2,010 |

*Lead status, partner tenure, pseudo-treatment and the exit association (NA+EU baseline sample):*
| Check | Estimate | 95% CI | n rows / rounds |
|---|---|---|---|
| Lead flag recorded (investor-level flag combined with the round-level lead list): coverage | 88 percent (agreement 1.00 where both exist) | — | — |
| Female-partner investor is lead, within round (pp) | +0.07 | [−5.27, +6.20] | 1,405 / 474 |
| Partner tenure, female-attributed − male-attributed investor (years) | −1.28 | [−1.83, −0.75] | 1,623 / 535 |
| Re-investment, any-female, + tenure control (pp) | −0.18 | [−4.34, +3.69] | 1,623 / 535 |
| Re-investment, female-only, + tenure control (pp) | −1.29 | [−5.64, +2.91] | 1,296 / 436 |
| Pseudo-treatment: junior-partner investor in all-male female-founded rounds (pp) | +0.00 | [−2.57, +2.69] | 3,046 / 1,175 |
| Re-investment rate when the company later exits vs not (deals through October 2017; pp) | +2.8 | [−7.51, +12.76] | 800 / — |

*Row 2 of the first sub-table (the unconditional outcome) includes 199 rounds with no next round, whose outcome is zero for every investor by construction (69 percent of their identifying variance comes from constant-outcome rounds); its interval is not read as a bound. The reference rows (2,000 draws) are the estimates quoted in the text; the initial 400-draw rows and the investor-cluster variants are shown for transparency and are not counted as separate robustness results. Sources: P001-42, P001-51, P001-52, P001-56, P001-58, P001-59.*

*Investor-level differences within the same rounds (female-attributed − male-attributed investor; pre-round traits) and positive controls (within-round slope of re-investment on the trait):*
| Investor trait | Difference | 95% CI | Standardized | Re-investment slope | 95% CI |
|---|---|---|---|---|---|
| Pre-round female-founded share of attributed deals | +0.071 | [+0.044, +0.101] | +0.30 | — | — |
| Pre-round early-stage share of attributed deals | +0.041 | [+0.008, +0.079] | +0.13 | −0.210 | [−0.308, −0.117] |
| Investor firm age (years) | −3.68 | [−5.84, −1.59] | −0.18 | — | — |
| Fund age (years since last fund announced; 75 percent coverage) | −0.34 | [−0.58, −0.11] | −0.18 | −0.0211 | [−0.0343, −0.0073] |
| Log size of the latest fund (Crunchbase; P001-58) | −0.373 | [−0.609, −0.162] | −0.24 | +0.0347 | [+0.0165, +0.0532] |
| Fund sequence number (Crunchbase; P001-58) | +0.325 | [−0.299, +0.982] | +0.06 | +0.0066 | [+0.0023, +0.0139] |
| Any SEC Form D tier-1 fund filing before the round (coverage 23 percent) | +0.046 | [−0.013, +0.098] | +0.11 | +0.0262 | [−0.0245, +0.0737] |
| Investor experience (log prior rounds) | −0.172 | [−0.414, +0.038] | −0.10 | +0.0324 | [+0.0202, +0.0454] |
| Lead-investor flag (57 percent coverage) | −0.044 | [−0.117, +0.026] | −0.09 | +0.106 | [+0.041, +0.171] |

Female-founded rounds with a next round within 36 months: 535 rounds, 1,623 investor rows, 390 companies, 760 investor firms (the pooled regression with other rounds spans 1,741 companies). These rounds are larger than all female-founded equity rounds in the window (median $8.2 million vs $2.5 million; early-stage 62 vs 69 percent); partner attribution covers 45 percent of their investor rows, and attributed co-investors re-invest +18.9 pp [+15.57, +22.09] more often than unattributed ones within the same rounds. † Pre-round controls: female-founded share, early-stage share and log count of the investor's prior attributed deals, investor firm age, fund age (each with a missing indicator). ‡ Fund-cycle controls: Crunchbase fund age, log size and sequence number of the investor's latest fund before the round, and the count, latest vintage and cumulative amount of the investor's SEC Form D tier-1 fund filings before the round (missing indicators included; P001-58). Sources: P001-42, P001-51. Re-investment base rate in those rounds 0.463; raw four-cell double difference −0.0356. Within-round permutation of partner gender (500 draws): two-sided p = 0.846. Minimum detectable effect (80% power) of β in female-founded rounds: 0.053.

### Table 9. The female-partner channel along the financing ladder (NA+EU)
| Stage | P(FP given FF deal) % | P(FP given no observed female founder) % |
|---|---|---|
| Early (pre-seed/seed/angel) | 20.18 | 11.08 |
| Series A | 17.92 | 9.81 |
| Series B and beyond | 13.32 | 8.13 |

| Differential early−late slope (FF − other) | Estimate (pp) | 95% CI |
|---|---|---|
| Baseline | +3.91 | [+1.50, +6.69] |
| Reweighted for stage-varying determinability | +4.40 | [+1.70, +7.22] |
| Majority-female founder teams | +3.71 | [+0.57, +6.86] |
| Reallocation counterfactual: late-stage FF–FP contacts | +26.8% (from 818 deals) | |

## Between-firm check (Snellman–Solal-style): female-founded companies' first rounds
| Lead-team definition and sample | Design | Estimate | 95% CI | n / events (treated) |
|---|---|---|---|---|
| All attributed lead partners female vs all male, mixed teams excluded; US, seed and Series A, 2010–18 | Cox proportional hazards on exit, treatment only | HR 0.990 (log-hazard −0.010) | [−0.831, +0.466] on log hazard | 421 / 142 (36) |
| Alternative lead-team definition: any attributed lead partner female (pools mixed teams); NA+EU, 2010–20 | LPM follow-on within 36m, year FE | +2.26 pp | [−5.26, +9.13] | 1,377 |
| Alternative: lead-firm female-partner share above median; NA+EU, 2010–20 | LPM follow-on within 36m, year FE | +5.91 pp | [+1.31, +10.19] | 4,197 |

*n = 113,708 (ladder). The first between-firm row is the targeted comparison; Cox specifications adding year, sector, and stage terms did not meet the convergence criterion at 36 treated observations (sparse year–sector cells) and are not reported. The alternative definitions pool all-female with mixed lead teams — the highest-performing cell in Snellman and Solal (2023) — and are reported as alternatives, not as estimates of the all-female contrast. Sources: P001-06, P001-17, P001-24, P001-19.*

### Table 10. Partner turnover and deal composition: deal-level stacked event studies (NA+EU)
## Featured: arrival margin (deal-level)
| | Estimate (pp) | 95% CI |
|---|---|---|
| **Female arrival × post (vs male arrivals, reweighted)** | **+2.81** | **[+1.39, +3.95]** |
| Departure margin (same design) | +0.75 | [−2.29, +3.08] |
| Colleague deals only (event partner's own deals excluded) | +2.04 | [−0.09, +4.48] |
| Arrival + departure (mirror-reversal test: = 0 under exact reversal; same bootstrap draws) | +3.56 | [−0.36, +6.55] |
| Own-deal share of post-event flow after female arrivals; FF share of own deals vs colleagues' deals; direct composition share s·(p_own − p_colleagues) | 2.1%; 28.8% vs 24.2% | +0.10 pp |
| Female arrivals that are the firm's first female partner; female departures that remove its last (shares of events) | 36% of 1,059; 33% of 401 | |
| Pre-event path k=−4..−2 (pp, ref k=−1) | −1.17, −0.24, −1.71 | |
| Trend sensitivity: CI lower bound reaches 0 at δ* (point stays >0 to ≈0.7) | 0.4 pp/half-yr | observed pre-slope ≈ 0 |
| Event-aggregated design, own breakdown slope (pp per half-year) | 0.58 | |

## Robustness: symmetric and aggregated versions
| | Estimate (pp) | 95% CI |
|---|---|---|
| Deal-level arrival − departure contrast | +2.06 | [−0.07, +4.57] |
| Event-aggregated contrast (half-year shares, reweighted) | +2.32 | [+0.18, +4.49] |
| — permutation p (gender labels) | 0.025 | |
| — placebo: all-male-team deal counts (log points) | −0.023 | [−0.122, +0.077] |
| Pre-hire run-up in firm FF share, levels (I-76) | +2.2 | [+1.3, +3.2] |

*Deal-level design: 244,349 deal observations around 4,824 clean events (arrivals: no attributed deal before recorded start), event FE + relative-half FE, contaminated male controls excluded, firm-cluster bootstrap. Aggregated design: P001-04b (1,177 female events). Sources: P001-11, P001-14b, P001-04b, I-82, I-76.*

### Appendix Table IA.1. Does composition carry information? Full specification ladders (Table 7, Panels D1 and D2)
## Panel D1. Does composition carry information? Open horizon (exit by sample end); post window 2017-11 to 2023-10
Rows are on the percentile scale (β on raw percentile given adjusted percentile) unless marked *levels* (β on the composition component in exit-probability units).
| Specification | β | 95% CI | n |
|---|---|---|---|
| Baseline cell benchmark | +0.097 | [+0.039, +0.160] | 2,178 |
| Leave-one-out cell benchmark | +0.103 | [+0.034, +0.176] | 2,164 |
| Leave-one-out, cells with ≥ 10 deals | +0.108 | [+0.039, +0.186] | 2,011 |
| Leave-one-out, cells with ≥ 30 deals | +0.093 | [+0.000, +0.191] | 1,673 |
| Leave-one-out, inverse-probability weighted for post-period observation | +0.093 | [+0.028, +0.162] | 2,164 |
| Levels instead of percentiles: raw exit rate given adjusted exit rate | +0.098 | [+0.028, +0.157] | 2,164 |
| Levels, composition component alone (unconditional) | +0.146 | [+0.079, +0.215] | 2,164 |
| Percentile difference alone (unconditional) | −0.037 | [−0.110, +0.028] | 2,164 |
| Excluding post-period deals in companies the partner backed pre-period | +0.079 | [+0.017, +0.158] | 1,858 |
| Leave-partner-out cell benchmark | +0.100 | [+0.025, +0.164] | 2,164 |
| Composition component, levels, given tenure and first-deal-year effects | +0.076 | [−0.018, +0.162] | 2,164 |
| Composition component, levels, home-firm fixed effects | +0.099 | [−0.060, +0.257] | 1,624 |
| Decomposition of the composition component, levels: vintage / stage within year / sector within year–stage | +0.075 / +0.081 / +0.160 | [−0.089, +0.258] / [−0.040, +0.198] / [+0.004, +0.307] | 2,164 |
| Same decomposition, given tenure and first-deal-year effects | −0.037 / +0.057 / +0.151 | [−0.269, +0.212] / [−0.068, +0.189] / [−0.008, +0.300] | 2,164 |
| Contrast, levels: adjusted exit rate, same regression as the composition-component levels row | +0.335 | [+0.284, +0.383] | 2,164 |
| Contrast: adjusted percentile's own coefficient | +0.246 | [+0.208, +0.279] | 2,178 |

## Panel D2. Same question at a fixed 36-month exit horizon in both periods (post window 2017-11 to 2020-10); levels
β on the composition component, or the named part, in 36-month exit-probability units. Partner-level rows include the adjusted rate, log deal count, gender, tenure, tenure², and first-deal-year effects unless noted. Deal-level rows include the partner's prior within-cell residual, log prior deals, gender, tenure at the deal date and its square, and year effects where no firm–year effect is present.
| Specification | β | 95% CI | n |
|---|---|---|---|
| **Composition component — preferred specification for this question** | **+0.278** | **[+0.075, +0.480]** | 2,017 |
| Sector-within-year–stage part | +0.307 | [+0.057, +0.570] | 2,017 |
| Adjusted exit rate's own coefficient, same regression as the preferred row | +0.180 | [+0.083, +0.281] | 2,017 |
| Without tenure and first-deal-year effects: composition component | +0.289 | [+0.102, +0.464] | 2,017 |
| Without tenure and first-deal-year effects: adjusted exit rate, same regression | +0.184 | [+0.088, +0.304] | 2,017 |
| Pre-period benchmark at a 72-month horizon | +0.155 | [+0.038, +0.267] | 2,017 |
| Home-firm fixed effects (minimum detectable effect 0.38; sector part 0.40) | −0.039 | [−0.328, +0.235] | 1,490 |
| Post-period deals in companies not backed pre-period | +0.193 | [−0.036, +0.399] | 1,574 |
| Leave-company-out benchmark | +0.332 | [+0.118, +0.537] | 2,002 |
| Both restrictions: companies not backed pre-period and leave-company-out benchmark | +0.282 | [+0.024, +0.528] | 1,562 |
| Post-period deals in companies the partner backed pre-period only | +0.358 | [+0.082, +0.643] | 1,594 |
| Pre-period restricted to deals whose 36-month window closes before the ranking date (deals through 2014-10; minimum detectable effect 0.35) | +0.090 | [−0.123, +0.350] | 1,127 |
| Pre-period restricted to deals from 2014-11 to 2017-10 | +0.326 | [+0.141, +0.499] | 1,298 |
| Reweighted for selection out of post-period observation (inverse probability) | +0.252 | [−0.005, +0.519] | 2,017 |
| Exits recorded before the deal date excluded from the outcome | +0.271 | [+0.078, +0.470] | 2,017 |
| Tenure and rank from employment records (join date, title) instead of first-deal tenure; partners with a recorded join date | +0.305 | [+0.117, +0.501] | 1,789 |
| Same partners, first-deal tenure controls (comparison) | +0.283 | [+0.036, +0.489] | 1,789 |
| Home-firm fixed effects with employment-record tenure and rank | −0.112 | [−0.389, +0.185] | 1,313 |
| Follow-on construct instead of exit (follow-on within 36 months, both periods) | +0.035 | [−0.159, +0.237] | 2,017 |
| Deal level, pooled: prior-year composition (sector part) → deal's within-cell outcome | +0.150 | [+0.053, +0.251] | 35,348 |
| Deal level, within firm–year: sector part (minimum detectable effect 0.19) | +0.050 | [−0.081, +0.173] | 25,600 |
| Deal level, within firm–year: composition component (minimum detectable effect 0.16) | +0.058 | [−0.044, +0.176] | 25,600 |
| Deal level, within firm–year, deals in companies not previously backed by the partner: sector part | +0.128 | [−0.094, +0.338] | 11,697 |
| Deal level, within partner: composition component (exploratory†) | +0.226 | [−0.015, +0.463] | 34,905 |

*Same construction, samples, and sources as Table 7; see its note.*

### Appendix Table IA.2. Robustness and measurement diagnostics
## Panel A. Sector-layer matching coefficient across specifications (rows re-estimated in a separate bootstrap run; the canonical baseline interval is Table 2)
| Row | Estimate (pp) | 95% CI | n |
|---|---|---|---|
| baseline | +3.21 | [+1.79, +4.54] | 127,061 |
| T1_ff_majority | +2.98 | [+1.78, +4.43] | 127,061 |
| T1_ff_solo | +1.13 | [+0.48, +1.91] | 127,061 |
| T2_solo_attr | +3.40 | [−1.36, +11.17] | 35,587 |
| T4_profile_rich | +3.62 | [+2.10, +5.17] | 104,854 |
| T5_cluster_partner | +3.21 | [+2.07, +4.42] | 127,061 |
| T5_cluster_org | +3.21 | [+2.09, +4.29] | 127,061 |
| stage layer, generic labels excluded | +0.59 | [−0.53, +1.91] | 114,658 |

## Panel B. Covariate-adjusted follow-on estimates across specifications
| Row | Estimate (pp) | 95% CI | n |
|---|---|---|---|
| baseline | +1.08 | [−1.42, +3.48] | 13,187 |
| T1_ff_majority | +0.58 | [−1.72, +3.49] | 8,255 |
| T2_solo_attr | +7.18 | [−42.86, +12.25] | 4,133 |
| T3_fon24 | +1.33 | [−1.60, +4.35] | 16,737 |
| T4_profile_rich | +2.50 | [−0.43, +6.50] | 10,780 |
| T5_cluster_partner | +1.08 | [−0.81, +3.13] | 13,187 |

## Panel C. Measurement diagnostics
| | |
|---|---|
| Firm attribution rate ~ female-partner share (correlation) | −0.023 [−0.044, −0.002] |
| Attribution × gender drift correlation (annual) | −0.048 |
| Deal-level salience fingerprint: FF × firm FP-share → P(attributed) | +2.46pp [+0.70, +4.44] (≈0.4pp per sd; absorbed by firm FE) |
| Generic stage-label share: FP / MP deals | 8.7% / 9.9% |
| Founder-gender determinable vs not: US / early / vintage | +28.2pp / −17.8pp / −1.94y |

## Panel D. Rank-measure diagnostics and external-pricing sensitivity
| | |
|---|---|
| Raw vs adjusted percentile: correlation / VIF / share of raw variation independent of controls | 0.8614 / 7.37 / 13.6% |
| Raw percentile alone → mobility; → spinout | +0.049 [−0.015, +0.123]; +0.035 [−0.022, +0.088] |
| Adjusted percentile alone → mobility; → spinout | +0.057 [+0.001, +0.113]; +0.062 [+0.022, +0.102] |
| Out-of-sample AUC (5-fold), raw minus adjusted: mobility; spinout | −0.0040; −0.0083 |
| Composition → fund formation: with pre-period early-stage share and sector breadth as controls / without | +0.374 [−0.093, +0.810] / +0.494 [+0.143, +0.862] |
| Composition → receiving-firm quality: with / without | +1.047 [−0.233, +2.474] / +1.201 [+0.362, +2.244] |
| Post-period observation ← composition component (LPM; percentile-point units) | −0.425 [−0.535, −0.307]; n = 2,661 |
| Post-period observation ← vintage / stage-within-year / sector-within-year–stage components (levels) | −2.188 [−2.417, −1.972] / +0.379 [+0.198, +0.585] / +0.082 [−0.164, +0.299] |
| Post-period observation ← tenure (years since first attributed deal), given components | +0.0283 [+0.0022, +0.0754] |
| Composition → log fund size: with pre-period late-stage share as control / late-stage share own coefficient | +0.662 [−1.577, +2.964] / +1.423 [+0.756, +2.201] |
| Log fund size ← stage part / ← sector part given late-stage share / ← sector part given late-stage share and tenure | +5.639 [+2.994, +8.312] / +2.777 [+0.045, +5.655] / +2.580 [−0.643, +5.611]; n = 196 |
| Fund formation ← sector part given late-stage share and tenure | +0.250 [−0.564, +1.020]; n = 378 |
| Minimum detectable effects (80% power), composition component / sector part: open-horizon home-firm FE; fixed-horizon home-firm FE; deal-level firm–year FE | 0.226 / 0.344; 0.379 / 0.401; 0.164 / 0.187 |
| Three-part multiplicity adjustment (maximum absolute t) of the open-horizon sector part: two-sided p, adjusted / unadjusted | 0.133 / 0.045 |
| Within-firm share of variance in the home-firm FE sample: composition component / sector part | 0.33 / 0.62 |
| Mundlak decomposition, open horizon, within-firm / between-firm coefficient: sector part | +0.131 [−0.096, +0.349] / +0.170 [−0.042, +0.395] |
| Same, composition component | +0.119 [−0.026, +0.279] / +0.061 [−0.038, +0.148] | 
| Same, composition component, within-minus-between contrast | +0.058 [−0.098, +0.216] |
| Mundlak decomposition, fixed 36-month exit horizon, within-firm / between-firm / contrast: composition component | −0.018 [−0.293, +0.221] / +0.435 [+0.177, +0.694] / −0.453 [−0.786, −0.130]; n = 2,017 |
| Same, adding the home firm's fund count, cumulative fund size and fund age at the sample split (Crunchbase funds; SEC Form D tier-1 filings): between-firm coefficient / contrast; R² of the firm-mean composition on those variables | +0.428 [+0.154, +0.664] / −0.447 [−0.760, −0.049]; R² 0.060 |
| Same, sector part | +0.044 [−0.234, +0.316] / +0.508 [+0.167, +0.848] / −0.464 [−0.874, −0.037] |
| Follow-on vs exit benchmarks: weighted correlation of year–sector–stage cell means (follow-on, 36-month exit) / (follow-on, exit by sample end); range of stage-level rates excluding private equity, follow-on / 36-month exit | −0.26 / −0.04; 0.193 / 0.279 |
| Employment-record tenure: share of partners with a home-firm join date / correlation with first-deal tenure / share attributed before the recorded join date / female−male tenure difference (years) | 0.877 / +0.65 / 0.293 / −1.55 |
| Standardized coefficients in one regression, composition component / adjusted rate: fixed horizon with tenure controls; open horizon | +0.083 / +0.098; +0.057 / +0.300 |
| Split-half agreement at the fixed horizon (upper bound on reliability): sector part / composition component / adjusted rate | 0.50 / 0.62 / 0.47 |
| 36-month exit: share of positives recorded before the deal date, pre / post; post-period base rate with those excluded | 0.028 / 0.048; 0.1384 |
| Post-period observation ← vintage part / employment-record tenure, given components and rank | −2.380 [−2.702, −2.079] / +0.0126 [+0.0052, +0.0195]; n = 2,333 |
| Share of the fixed-horizon partner sample observed in the post period | 0.758 |
| Pre-period deals entering the fixed-horizon panel whose 36-month window closes after the ranking date / whose outcome is undetermined at that date | 0.467 / 0.398 |
| Correlation of tenure (years since first attributed deal) with the composition component, open horizon | 0.52 |
| Deal-level firm–year FE sample: deals / firms | 25,600 / 661 |
| Fixed-horizon Mundlak: correlation of firm-mean composition with firm-mean adjusted rate / partners who are the only sampled partner at their firm | +0.121 / 434 of 2,017 |
| Identifying variation of the Table 3 peer comparison (firm × year × sector), NA+EU / global: cells with both partner genders among FF deals / deals in them / share of FF deals | 174 / 430 / 0.060; 191 / 478 / 0.059 |
| Peer availability, NA+EU: share of female-partner FF deals with a same-cell male-partner FF deal / female partners with at least one such deal (of 326) / same share across all deals | 0.237 / 90 / 0.419 |
| Peer-comparison estimate re-estimated on the mixed cells only, NA+EU / global (pp) | −4.55 / −6.25 (identical to the full-sample estimates) |
| Leave-one-cell-out jackknife of the peer-comparison estimate: maximum shift (pp), NA+EU / global; any value outside the bootstrap interval | 0.72 / 0.64; no |
| Within-cell random reassignment of partner gender (400 draws): 95th percentile of the absolute estimate (pp), NA+EU / global; share of draws at or beyond the estimate | 5.54 / 5.36; 0.100 / 0.025 |
| Same for the + stage cells, NA+EU: cells / deals / placebo 95th percentile / share at or beyond | 155 / 336 / 2.64 / 0.540 |
| Deal level, fixed horizon, without the partner's prior within-cell residual as a control — within firm–year: sector part / composition component; pooled: sector part | +0.043 [−0.096, +0.173] / +0.039 [−0.096, +0.149]; +0.177 [+0.065, +0.274] |
| Deal level, open-horizon construct (exit by sample end), within firm–year: sector part | +0.002 [−0.155, +0.162]; n = 33,611 |
| Split-half agreement (Spearman–Brown; halves share cell benchmarks, so an upper bound on reliability): vintage / stage / sector parts / composition component / adjusted rate | 0.97 / 0.87 / 0.47 / 0.84 / 0.59 |
| Fixed exit horizon: standard deviation of the vintage part / standardized composition coefficient (sd units) | 0.0147 / +0.083 |
| Deal-level sample: firm–years with ≥ 2 partners / share of post-period deals in companies the partner backed pre-period (fixed-horizon window) | 2,402 / 0.218 |
| Spinout population counts, leave-one-out partner sample: spinouts / fund close observed / fund size observed | 378 / 220 / 196 (Table 7 Panel C uses the baseline-benchmark sample: 380 / 221 / 197) |

## Panel E. Region split and the identifying base of the peer comparison
| | United States | North America (US + Canada) | Europe (24 countries) |
|---|---|---|---|
| Peer-comparison exit gap, firm × year × sector (pp); mixed cells / deals | −4.12 [−10.71, +1.99]; 145 / 352 | −4.69 [−11.84, +1.32]; 146 / 354 | not computable (within-cell exit variation zero); 27 / 63 |
| Within-cell reassignment placebo, 95th percentile of \|β\| (pp) | 5.53 | 5.9 | — |
| + stage cell gap (pp) | −1.26 [−5.67, +2.60] | −1.26 [−5.26, +2.99] | not computable |
| Follow-on within 36 months, + stage cell, FP coefficient (pp) | +1.01 [−2.14, +5.13] | +1.01 [−2.05, +5.15] | not computable |
| Fixed-horizon composition coefficient (Table 7 Panel D2 preferred specification); partners | +0.190 [−0.018, +0.377]; 2,079 | +0.242 [+0.036, +0.480]; 2,158 | +0.363 [+0.121, +0.583]; 464 |

| Identifying base of the Table 3 peer comparison | NA+EU, firm × year × sector | NA+EU, + stage | Global, firm × year × sector |
|---|---|---|---|
| Mixed cells that are co-attributions on a single round (share) | 113 (0.65) | 135 (0.87) | 120 (0.63) |
| Cells with within-cell exit variation / deals in them | 30 / 101 | 8 / 19 | 35 / 120 |
| Share of identifying variance (Σx̃²) from single-round cells | 0.58 | 0.85 | 0.55 |
| Exit gap on multi-round cells only (pp); MDE; placebo 95th percentile | −10.71 [−21.72, +2.07]; 17.51; 12.67 | −6.80 [−25.40, +17.23]; 30.7; 23.13 | −13.87 [−24.77, −2.50]; 15.73; 11.89 |
| Follow-on gap on multi-round cells only (pp) | −1.17 [−11.25, +7.00] | +5.44 [−11.37, +27.80] | −2.15 [−11.54, +7.18] |

| Identifying base of the Table 4 hazard (cell × elapsed-year effects) | Value |
|---|---|
| Cells with female-partner variation / rows; share that are co-attributions on a single round | 814 / 1,764; 0.89 |
| Cells with within-cell exit variation (share); exit events in them | 10 (0.01); 12 |
| Share of identifying variance from single-round cells | 0.87 |
| Annual hazard gap, all cells, re-estimated in this audit run with its own bootstrap (pp/yr; the reference estimate is Table 5, Panel A); within ±25% of the 6.19% base | −0.244 [−1.00, +0.31]; yes |
| Annual hazard gap, multi-round cells only (pp/yr); MDE; within ±25% of base | −1.699 [−11.83, +2.87]; 11.31; no |

*Panel A 'baseline' re-estimates the Table 2 sector layer inside the robustness battery (separate bootstrap run; point identical, interval differs by resampling). Panel D: composition-component coefficients are in exit-probability units per unit of the component (0.01 of the percentile scale = one percentile point) unless a row states percentile-point units; fund-size coefficients are log points per unit of the component. Sources: P001-07, P001-08, P001-16, P001-22, P001-23, P001-25, P001-28, P001-29, P001-30, P001-31, P001-32, P001-33, P001-34, P001-35, P001-37, P001-38, P001-39, P001-40, P001-41, P001-48, P001-49, P001-50. Solo-attribution rows lose precision (negative_results/W4_notes.md); points consistent with baselines.*

### Appendix Table IA.3. Movers, absences, and the financing-ladder pipeline
## Panel A. Movers: the same partner at two firms (≥ 5 attributed deals at each; NA+EU)
| Specification | β | 95% CI | n transitions |
|---|---|---|---|
| Change in the partner's early-stage share on the change in her firm's leave-partner-out early-stage share, all transitions | +0.562 | [+0.450, +0.665] | 243 |
| Same, non-overlapping spells only | +0.616 | [+0.420, +0.806] | 80 |
| Same for the stage part of the composition component | +0.713 | [+0.554, +0.824] | 243 |
| Same for the sector part | +0.157 | [−0.049, +0.381] | 243 |
| Levels: destination firm's share / origin firm's share | +0.534 [+0.408, +0.650] / −0.606 [−0.732, −0.497] | | 243 |
| Placebo destination (random firm in the same size decile) / origin | −0.005 [−0.135, +0.133] / −0.444 [−0.570, −0.329] | | 247 |
| Sorting check: pre-move own share on the destination firm's share measured before the move (given the origin firm's) | +0.149 | [+0.023, +0.270] | 162 |
| Moves toward later-stage firms / toward earlier-stage firms | +0.410 [+0.112, +0.763] / +0.575 [+0.400, +0.765] | | 83 / 157 |

Movers 382 (37 women), 410 transitions, 139 with non-overlapping spells. Partner-cluster bootstrap. The design is gender-neutral by construction (37 female movers).

## Panel B. Absences: interior gaps of 18 months or more in a partner's attributed record while she remains at the firm
Outcome: female-founded share of the firm's other deals in the half-year; partner × firm and half-year effects; firm-cluster bootstrap. "Difference" is the female-partner minus male-partner absence coefficient.
| Outcome / gap length | Female partners' absence | 95% CI | Male partners' absence | 95% CI | Difference | 95% CI | MDE |
|---|---|---|---|---|---|---|---|
| Colleagues' attributed deals, ≥ 18 months | −0.018 | [−0.048, +0.011] | −0.004 | [−0.013, +0.005] | −0.014 | [−0.045, +0.018] | 0.045 |
| Same, ≥ 24 months | −0.015 | [−0.054, +0.023] | −0.008 | [−0.019, +0.002] | −0.007 | [−0.047, +0.035] | 0.061 |
| All of the firm's equity deals in sample companies, ≥ 18 months | +0.004 | [−0.018, +0.031] | −0.001 | [−0.008, +0.006] | +0.005 | [−0.016, +0.033] | 0.034 |
| Same, spells with recorded continuous employment | −0.001 | [−0.027, +0.027] | +0.001 | [−0.006, +0.008] | −0.002 | [−0.028, +0.027] | 0.041 |
| Recording placebo: firm's attribution rate during the gap | −0.167 | [−0.220, −0.116] | −0.208 | [−0.232, −0.187] | +0.041 | [−0.012, +0.092] | |
| Scale placebo: log colleague deal count | −0.129 | [−0.197, −0.059] | −0.168 | [−0.190, −0.144] | +0.039 | [−0.031, +0.116] | |

Partners with a ≥ 18-month gap 1,575 (128 women); spells in the panel 1,567. Pre-gap event-time coefficients (four half-years) joint sup-t p = 0.37.

## Panel C. Financing-ladder pipeline (descriptive): where the female-partner share narrows along the ladder
| Margin | Estimate | 95% CI | n |
|---|---|---|---|
| Company reaches Series A: female-founded − other, first-round year × sector × country cells | −7.24pp | [−8.95, −5.40] | 18,178 |
| Company reaches Series B or later | −6.34pp | [−8.11, −4.64] | 18,178 |
| Same, companies acquired or listed before Series B excluded | −8.12pp | [−9.93, −6.22] | 14,991 |
| Incumbent firm re-invests in the next round (given a next round within 36 months): FP × FF, firm × year × sector × stage cells | −1.22pp | [−6.67, +3.24] | 20,854 |
| Same partner re-attributed (given the firm re-invests): FP × FF | −0.85pp | [−7.47, +5.72] | 10,337 |
| Conditioning event (next round within 36 months): FP × FF | −0.98pp | [−6.34, +4.47] | 31,390 |
| Coverage: next round has recorded investors / re-investing firm has a recorded partner, FP × FF | −0.08pp [−2.37, +2.07] / −4.48pp [−10.53, +1.40] | | |
| Female-partner share among investors new to the company: early / later stage, female-founded companies | 15.7% / 12.3% | n = 1,469 / 730 | |
| Same, other companies | 8.3% / 8.0% | n = 7,782 / 4,898 | |
| Entrant female-partner share on later stage: all companies / female-founded × later stage | −0.29pp [−1.23, +0.71] / −3.04pp [−6.81, +0.55] | | 14,879 |

Raw four-cell re-investment rates (FP, FF): {'fp0_ff0': 0.5233, 'fp0_ff1': 0.4887, 'fp1_ff0': 0.5029, 'fp1_ff1': 0.4284}. Companies with an early first round 2010–2019: 19,434 (3,749 female-founded). Sources: P001-42, P001-46, P001-43, P001-44, P001-45. All rows are bootstrap percentile intervals; no causal claim is made in this table.
