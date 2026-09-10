*W5 v9 (2026-09-10, sample_v2 rebuild; reviews c1–c3); regenerated from P001-00 … P001-63 and I-73 … I-82 via `06_code/p001_09_exhibits.py` and `p001_09d_compose_v9.py`; assembled by the build step. Do not edit by hand.*

### Table 1. Sample and measurement coverage
| | |
|---|---|
| Partner-attributed deals with observable founder gender (global) | 153,012 |
| — excluded at construction (founder gender unobservable) | 34,457 |
| — North America + Europe (primary sample) | 126,128 |
| Partner gender observed (share of attributed deals) | 94.2% |
| Founder gender determinable (share of funded companies) | 83.2% |
| Female-founded (FF) share of deals | 17.2% |
| Female-partner (FP) share of deals | 10.6% |
| Determinability selection: US share diff (det − undet) | +27.6pp |
| — early-stage share diff | −16.6pp |
| — mean vintage diff (years) | −1.92 |
| Unique funding rounds / companies / investor firms / attributed partners | 84,079 / 47,173 / 14,963 / 29,551 |
| Attributed rows on companies with an acquisition or IPO recorded on or before the round date (excluded from the analysis file; global / NA+EU) | 1,111 / 933 |
| Deals at investors whose Crunchbase type includes venture capital, micro VC, or corporate VC (NA+EU); partners at such firms | 86.8% ; 71.9% |
| Attributed partners with a job title at the firm containing "partner" (share of partner–firm pairs; deal-weighted) | 39.5% ; 61.6% |
| Attributed partners with no job record at the firm (share of pairs) | 25.0% |

*Sources: sample_v2.parquet (sha256₁₆ 3acfb38d12559791; P001-00); I-73; P001-08; P001-63. Population: partner-attributed equity deals, 2010-01 to 2023-10, with observable founder gender, of companies with no acquisition or IPO recorded on or before the round date (Appendix IA.1).*

### Table 2. Partner–founder gender matching: decomposition ladder (NA+EU)
## Panel A. Decomposition ladder: firm × year cells, adding sector, adding stage
| Cell specification | FP coefficient (pp) | 95% CI |
|---|---|---|
| Firm × year | +7.02 | [+5.74, +8.29] |
| + sector | +3.22 | [+1.92, +4.69] |
| + stage (full cells) | +0.63 | [−0.58, +1.86] |
| Reverse order: + stage first | +5.82 | [+4.54, +7.20] |
| NA, full cells | +0.60 | [−0.55, +2.07] |
| EU, full cells | −0.47 | [−2.78, +1.84] |
| NA − EU difference | +1.07 | [−1.52, +3.77] |

Composition shares (order-bracketed): total 91.0%; sector 54–74%; stage 17–37%.

*Outcome: deal is female-founded. n = 126,128. Investor-cluster bootstrap. Within-cell permutation of the raw association: p < 0.005 (I-74). Sources: P001-02, P001-14.*

## Panel B. What each layer compares: co-attribution and the common-support ladder (NA+EU, all deals)
| Cell | Mixed cells / unique rounds in them | Share of mixed cells that are a single round | d: share of identifying variance from single-round cells | β, all rows (pp) | β, multi-round cells only (pp) | β on the common support (rows in cells mixed at the finest level; pp) 95% CI |
|---|---|---|---|---|---|---|
| Firm × year | 3,686 / 25,666 | 0.06 | 0.02 | +7.02 | +7.17 | +1.62 [+0.49, +2.82] |
| + sector | 3,871 / 10,515 | 0.28 | 0.19 | +3.22 | +3.98 | +0.87 [−0.34, +2.09] |
| + stage | 3,206 / 5,801 | 0.53 | 0.44 | +0.63 | +1.13 | +0.63 [−0.62, +1.83] |
| Drop from firm × year to + stage (pp): original sample / common support | | | | +6.39 [+4.97, +7.93] | | +0.99 [+0.41, +1.51] |

*Panel B: the dependent variable (female-founded) is identical for the partners of a co-attributed pair, so the all-rows coefficient equals the multi-round coefficient times (1 − d), exactly as for the exit estimator. Common support = the 9,256 rows (7.3 percent of the sample; 5,801 unique rounds, 4,495 companies) that lie in firm × year × sector × stage cells containing both a female- and a male-partner deal; the three layers are re-estimated on those rows, so the observations are held fixed while the cells change — the implicit weights of the fixed-effects estimator still differ across layers, so this is a comparison-set diagnostic, not a decomposition of a pure composition effect. Investor-firm cluster bootstrap (500), shared across layers so that the drop is estimated from the same draws. Source: P001-61.*

### Table 3. The stage tilt and its origins
| | Estimate | 95% CI |
|---|---|---|
| FP–early-stage association (firm×year) | +3.86pp | [+2.65, +5.06] |
| — among deals with no observed female founder | +3.14pp | [+1.96, +4.49] |
| Mean tenure: female / male partners (yrs) | 2.75 / 4.24 | |
| Within tenure-bin cells (attenuation 47%) | +2.05pp | [+0.76, +3.18] |
| Stage-graduation slope diff (F−M, pp/yr) | −0.42 | [−0.97, +0.13] |
| Outcome test, early deals (fon), exact stage cells | −1.01pp | [−2.90, +0.71] |

*Sources: I-80, I-81, P001-08.*

### Table 4. Track-record evaluation: composition accounting and rank changes (NA+EU partners with at least five attributed deals)
## Panel A. Levels and ranks on one sample: female − male differences and mean percentile ranks (exit by sample end, deals through 2017-10)
| Benchmark | Δ raw exit rate (pp) 95% CI | Δ benchmark component (pp) | Δ adjusted exit rate (pp) | Female mean percentile, raw → adjusted | Male mean percentile, raw → adjusted | Female shift (percentile points) 95% CI | Partners (women) |
|---|---|---|---|---|---|---|---|
| Year | −2.88 [−7.15, +1.31] | −1.91 [−2.78, −0.91] | −0.97 [−4.81, +3.00] | 47.2 → 48.9 | 50.2 → 50.1 | +1.65 [+0.62, +2.46] | 2,680 (191) |
| Year × stage | −2.88 [−6.97, +1.42] | −3.54 [−5.79, −1.50] | +0.66 [−3.25, +4.45] | 47.2 → 50.9 | 50.2 → 49.9 | +3.68 [+1.62, +5.85] | 2,680 (191) |
| Year × sector × stage (preferred) | −2.88 [−7.16, +1.23] | −4.09 [−6.39, −1.48] | +1.21 [−1.97, +4.40] | 47.2 → 51.8 | 50.2 → 49.9 | +4.59 [+2.15, +6.84] | 2,680 (191) |

## Panel B. The same accounting at fixed exit horizons
| Sample and horizon | Δ raw exit rate (pp) 95% CI | Δ benchmark component (pp) | Δ adjusted exit rate (pp) | Female mean percentile, raw → adjusted | Male mean percentile, raw → adjusted | Female shift (percentile points) 95% CI | Partners (women) |
|---|---|---|---|---|---|---|---|
| 36-month exit, deals through 2020-10; year × sector × stage | −1.54 [−3.54, +0.27] | −1.60 [−2.45, −0.70] | +0.06 [−1.47, +1.79] | 46.2 → 49.7 | 50.4 → 50.0 | +3.42 [+1.56, +4.89] | 4,120 (392) |
| &nbsp;&nbsp;year only | −1.54 [−3.19, +0.28] | −0.63 [−0.77, −0.50] | −0.91 [−2.55, +0.90] | 46.2 → 48.0 | 50.4 → 50.2 | +1.80 [+1.33, +2.32] | 4,120 (392) |
| 72-month exit, deals through 2017-10; year × sector × stage | −0.69 [−4.50, +3.08] | −1.74 [−3.66, +0.11] | +1.05 [−1.93, +4.22] | 48.8 → 51.7 | 50.1 → 49.9 | +2.92 [+0.73, +5.24] | 2,680 (191) |
| &nbsp;&nbsp;year only | −0.69 [−4.71, +3.04] | −0.62 [−0.97, −0.26] | −0.06 [−3.85, +3.66] | 48.8 → 49.5 | 50.1 → 50.1 | +0.70 [+0.29, +1.14] | 2,680 (191) |

## Panel C. What the interval covers, and the benchmark's weights
| | Female shift (percentile points) | 95% CI | Partners |
|---|---|---|---|
| Benchmark held fixed; partners resampled (as in Panels A–B) | +4.59 | [+2.15, +6.84] | 2,680 |
| Benchmark (market-cell means) and ranks recomputed in every replication | +4.59 | [+2.07, +7.18] (interval width ratio 1.09) | 2,680 |
| Benchmark from unique rounds (multiply attributed rounds counted once in cell means) | +4.66 | [+2.55, +6.61] | 2,680 |
| Leave-company-out benchmark | +5.11 | [+3.01, +6.96] | 2,624 |
| Top-quartile female share, raw → adjusted (P001-05) | 7.2% → 8.2% | [−0.27, +2.52] | 2,680 |
| Rank correlation, raw vs adjusted (P001-05) | 0.861 | | |

*Raw exit rate = the partner's mean exit indicator; benchmark component = the deal-weighted mean of her market cells' exit rates (year, year × stage, or year × sector × stage; full cell means); adjusted rate = raw minus component, so the three level differences add up exactly on the same partners (maximum absolute deviation 0.0e+00 in exit-rate units). Percentiles are computed across all partners in the row's sample; the identity does not hold for ranks. Intervals are 500 partner-resampling bootstrap replications (300 for the benchmark-level and fixed-horizon rows); the benchmark is held fixed except in the row that says otherwise. Multiply attributed rounds enter the cell means once per attributed row (47 percent of rounds in the cells are attributed more than once; 1.92 rows per round on average). Sources: P001-62, P001-05.*

### Table 5. Where the exit gap lives: female-founded deals across comparison sets, and the cross-deal information each retains
## Panel A. Exit by sample end, deals through October 2017: the location ladder
| Comparison | Global | 95% CI | NA+EU | 95% CI |
|---|---|---|---|---|
| Year effects only | −2.68 | [−7.36, +2.66] | −3.34 | [−8.36, +2.21] |
| Firm × year | +0.21 | [−5.36, +5.34] | −0.51 | [−6.10, +5.18] |
| Additive firm+year+sector+stage | +0.82 | [−5.11, +6.76] | −0.81 | [−6.91, +5.69] |
| **Firm × year × sector (peer comparison)** | **-6.19 | [−12.12, −1.62]** | −4.47 | [−10.61, +0.21] |
| + stage | −1.58 | [−5.10, +1.56] | −0.82 | [−3.90, +2.79] |


## Panel B. Fixed 36-month exit horizon, deals through 2020-10 (NA+EU): the cross-deal comparisons as the estimator
| Cell definition | Mixed cells / deals | Multi-round (cross-deal) cells / deals | Cells with exit variation | Share of Σx̃² from single-round cells (d) | β, all cells (pp) | β, cross-deal cells (pp) | 95% CI | MDE80 (pp; sd) | Placebo 95th pct (pp) |
|---|---|---|---|---|---|---|---|---|---|
| firm×year×sector | 410 / 1,169 | 174 / 649 | 60 | 0.47 | −1.34 | −2.55 | [−9.37, +2.96] | 8.43; 0.26 | 5.47 |
| firm×year×sector×stage | 379 / 950 | 78 / 257 | 23 | 0.74 | −0.34 | −1.34 | [−12.50, +7.16] | 14.24; 0.44 | 8.5 |
| firm×2yr×sector | 396 / 1,328 | 226 / 948 | 79 | 0.31 | −0.21 | −0.31 | [−4.43, +3.47] | 5.77; 0.18 | 4.34 |
| firm×3yr×sector | 390 / 1,443 | 242 / 1,118 | 82 | 0.25 | −0.72 | −0.97 | [−5.38, +2.63] | 5.75; 0.18 | 3.86 |
| firm×sector + year FE | 358 / 1,951 | 273 / 1,758 | 109 | 0.12 | −2.86 | −2.18 | [−5.90, +1.53] | 5.30; 0.16 | 3.23 |
| Deal-level coding, firm × year × sector: female-only vs male-only attributed deals (mixed-attribution deals excluded) | — | 113 cells / 332 deals | 44 | 0 by construction | — | −8.27 | [−21.25, −0.20] | 15.54 | 8.27 |
| Reference: sample-end horizon, deals through 2017-10, firm × year × sector (canonical run; Appendix Table IA.2, Panel E) | 173 / 427 | 61 / 194 | 30 | 0.57 | −4.47 | −10.49 | [−22.19, +1.50] | 17.73; — | 12.83 |

*Panel B: exit within 36 months of the deal; FF deals 13,116, base rate 0.120. Σx̃² is the within-cell estimator's identifying variance and d the share of it contributed by cells whose partner rows all belong to one round (co-attributed pairs), so that the all-cells coefficient equals the cross-deal coefficient times (1 − d). MDE80 = minimum detectable effect at 80 percent power. β on cross-deal cells is the within-cell estimator restricted to mixed cells whose partner rows span at least two rounds; investor-firm cluster bootstrap (500); placebo = 95th percentile of |β| under within-cell reassignment of partner gender (400). The firm × sector row adds additive year effects (two-way demeaning); with additive effects the identity β_all = (1 − d)·β_cross-deal holds only approximately, which is why that row's all-cells and cross-deal coefficients do not satisfy it exactly. The reference row repeats the canonical sample-end estimates of P001-49 so that the same specification carries one set of numbers throughout the paper. Sources: P001-55, P001-49.*

*Deals through 2017-10; exit = acquisition or IPO by sample end. n = 8,021 (global) / 7,071 (NA+EU). The deficit is detected only in the interacted firm–year–sector comparison; the coarser intervals contain both zero and the peer-comparison estimate, and only the + stage row's interval excludes it. All rows are estimated on one sample and one bootstrap draw. Identifying variation of the peer-comparison row (Appendix Table IA.2, Panel D): 173 NA+EU cells contain both a female- and a male-partner female-founded deal (427 deals, 6.0 percent of the sample; global 190 cells, 475 deals). Base exit rate among female-founded deals, global: 46.4 percent (I-78). Sources: P001-10 (ladder), P001-15 (additive row), P001-40 (identifying variation), I-78 (base rate).*

### Table 6. Balance of company characteristics within the cells that identify the peer comparison (female-founded deals, firm × year × sector; deals through 2017-10)
| Characteristic | Female − male partner, all mixed cells | 95% CI | Standardized (diluted) | MDE (sd) | Share of Σx̃² from single-round cells (d) | Identifying cells only: standardized difference [95% CI in sd]; MDE (sd) | Same, stage in the cell | n (all) |
|---|---|---|---|---|---|---|---|---|
| Company age at deal (years) | −0.110 | [−0.406, +0.171] | −0.033 | 0.13 | 0.57 | −0.09 [−0.37, +0.14]; MDE 0.37 | +0.17 [−0.09, +0.48]; MDE 0.41 | 427 |
| log(1 + prior equity rounds) | −0.060 | [−0.123, +0.012] | −0.096 | 0.16 | 0.57 | −0.23 [−0.47, −0.00]; MDE 0.35 | +0.10 [−0.15, +0.52]; MDE 0.47 | 427 |
| log(1 + prior capital raised) | −0.648 | [−1.737, +0.272] | −0.082 | 0.19 | 0.57 | −0.20 [−0.51, +0.07]; MDE 0.42 | −0.08 [−0.36, +0.31]; MDE 0.51 | 427 |
| Employee-count band (1–9) | −0.151 | [−0.307, −0.009] | −0.085 | 0.12 | 0.57 | −0.22 [−0.41, +0.01]; MDE 0.31 | +0.17 [−0.14, +0.60]; MDE 0.54 | 427 |
| Investor count on the previous round | −0.505 | [−0.923, −0.203] | −0.174 | 0.18 | 0.62 | −0.48 [−0.88, −0.24]; MDE 0.45 | −0.34 [−0.89, +0.04]; MDE 0.74 | 266 |
| Number of founders | −0.208 | [−0.423, −0.007] | −0.142 | 0.19 | 0.57 | −0.28 [−0.48, −0.05]; MDE 0.33 | −0.01 [−0.48, +0.50]; MDE 0.74 | 427 |
| Number of female founders | +0.047 | [+0.012, +0.091] | +0.100 | 0.13 | 0.57 | +0.24 [+0.04, +0.46]; MDE 0.31 | +0.00 [−0.53, +0.56]; MDE 0.77 | 427 |
| Share of founders with a recorded degree | −0.003 | [−0.038, +0.028] | −0.011 | 0.16 | 0.57 | −0.03 [−0.33, +0.21]; MDE 0.40 | −0.14 [−0.59, +0.37]; MDE 0.72 | 427 |
| Share of serial founders | −0.031 | [−0.074, +0.007] | −0.078 | 0.15 | 0.57 | −0.18 [−0.40, +0.00]; MDE 0.30 | +0.02 [−0.37, +0.45]; MDE 0.61 | 427 |
| Headquartered in the United States | −0.009 | [−0.038, +0.015] | −0.025 | 0.11 | 0.57 | −0.06 [−0.23, +0.11]; MDE 0.26 | −0.25 [−0.61, +0.00]; MDE 0.46 | 427 |

*Prior patenting (USPTO PatentsView, matched to sample companies by normalized name and country/state/city; P001-58), female − male partner within cell:*
| Characteristic | Identifying (multi-round) cells: difference | 95% CI | Standardized | MDE (sd) | All mixed cells: difference | 95% CI |
|---|---|---|---|---|---|---|
| Any patent application filed before the deal | −0.118 | [−0.199, −0.048] | −0.27 | 0.26 | −0.050 | [−0.092, −0.020] |
| Log (1 + applications filed before the deal) | −0.263 | [−0.448, −0.136] | −0.32 | 0.28 | −0.112 | [−0.190, −0.045] |
| Company matched to a patent assignee (coverage indicator) | −0.097 | [−0.234, +0.056] | −0.19 | 0.39 | −0.041 | [−0.110, +0.018] |

Dilution. A company characteristic is identical for the two partners of a co-attributed pair, so the all-cells coefficient equals the identifying-cells coefficient times (1 − d), where d is the share of identifying variance from single-round cells (identity verified to 0e+00); the identifying cells are the 61 multi-round cells with 194 deals (sector cells) and 20 cells with 50 deals (stage cells; not identified). Joint tests. Largest absolute cluster-robust t across nine characteristics (prior-round investor count, 64 percent coverage, tested separately), against a shared within-cell permutation null (1000 draws): sector cells p = 0.177 (identifying cells only p = 0.194); the test rejects 6 percent of 100 random within-cell reassignments at the 5 percent level. With stage in the cell p = 0.802; on all deals with stage in the cell (973 cells, 2,527 deals) p = 0.777. The Mahalanobis joint test (bootstrap covariance; complete cases n = 266) gives p = 0.552 in the sector cells and is degenerate with stage in the cell (a zero-variance characteristic makes the covariance near-singular). Positive control, post-assignment log round size (female − male partner): same cells −0.139 [−0.282, −0.026]; all deals, firm × year × sector −0.060 [−0.138, +0.011].

*Characteristics are Crunchbase profile values. Founding date, prior equity rounds, prior funding, prior-round investors, and prior patent applications are dated relative to the deal; founder counts and degrees, serial founding, employee-count band, and headquarters are current profile fields whose historical timing is not recorded. The patent match indicator (whether the company appears in the assignee tables) is not a pre-deal quantity.*

### Table 7. Within-partner outcome test: female-founded versus other deals of the same partner, by partner gender, across horizons (NA+EU)
Outcome: the deal's exit (or follow-on) indicator net of the leave-one-out mean of its year × sector × stage market cell; partner fixed effects and deal controls. β_int is the difference between female and male partners' own female-founded − other gaps.

## Panel A. Estimates: female-founded vs other deals of the same partner, by partner gender (36-month exit net of the year × sector × stage market mean; deals through 2020-10). β_int is the difference between female and male partners' own female-founded − other gaps
| Specification | β_int: female partners' extra FF gap (pp) | 95% CI | MDE80 (pp) | β_int in sd of the benchmarked outcome | inside ±5 pp | β_FF: male partners' own FF − other gap (pp) | 95% CI | n deals / partners (women) |
|---|---|---|---|---|---|---|---|---|
| Partner fixed effects, deal controls; partner-cluster bootstrap | +0.47 | [−2.37, +2.93] | 3.65 | +0.014 | yes | −2.69 | [−3.54, −1.76] | 49,583 / 3,430 (416) |
| Same; investor-firm clusters | +0.47 | [−2.05, +3.10] | 3.64 | +0.014 | yes | −2.69 | [−3.80, −1.76] | 49,583 / 3,430 (416) |
| Firm × year fixed effects instead of partner effects (partner gender included) | +0.84 | [−1.79, +3.41] | 3.90 | +0.025 | yes | −2.79 | [−3.78, −1.79] | 45,934 / 3,430 (416) |
| Partner × two-year fixed effects | +1.10 | [−1.43, +3.79] | 3.87 | +0.033 | yes | −2.82 | [−3.72, −1.96] | 46,236 / 3,430 (416) |
| Partners with ≥ 5 deals | +0.56 | [−1.74, +3.10] | 3.49 | +0.017 | yes | −2.85 | [−3.65, −2.02] | 46,758 / 2,459 (284) |
| Vintages 2015 and later | +1.23 | [−1.49, +3.90] | 3.90 | +0.038 | yes | −2.67 | [−3.62, −1.80] | 32,786 / 3,300 (406) |
| + company characteristics (Crunchbase profile values; see note) | +0.34 | [−2.04, +2.74] | 3.40 | +0.010 | yes | −1.63 | [−3.46, +0.25] | 49,583 / 3,430 (416) |
| + prior patent applications (any before the deal; log count; assignee-match indicator, which is not pre-deal and absorbs unmatched zeros) | +0.53 | [−1.45, +2.75] | 3.18 | +0.016 | yes | −2.64 | [−3.64, −1.73] | 49,583 / — (any prior patent: +3.67 pp [+1.63, +5.46]) |
| Follow-on financing within 36 months (deals through 2020-10) | −1.06 | [−4.09, +2.07] | 4.45 | −0.025 | yes | −0.41 | [−1.48, +0.59] | 49,583 / 3,430 (416) |
| Exit by sample end (deals through 2017-10) | −6.77 | [−12.13, −1.65] | 7.37 | −0.150 | no | −1.86 | [−3.73, +0.07] | 28,412 / 1,987 (204) |
| &nbsp;&nbsp;vintages 2010–14 | −10.12 | [−17.56, −3.20] | 10.43 | −0.225 | no | −0.61 | [−3.24, +1.96] | 15,124 / 1,139 (89) |
| &nbsp;&nbsp;vintages 2015–17 | −3.37 | [−10.82, +2.59] | 10.03 | −0.074 | no | −2.90 | [−5.41, −0.63] | 12,871 / 1,285 (146) |
| &nbsp;&nbsp;partners with an attributed deal after October 2020 | −7.13 | [−13.67, −0.38] | 9.52 | −0.158 | no | −1.64 | [−3.71, +0.32] | 23,608 / 1,421 (144) |
| &nbsp;&nbsp;partners without one | −5.62 | [−18.09, +7.24] | 19.34 | −0.123 | no | −2.85 | [−7.09, +1.15] | 4,804 / 555 (59) |
| &nbsp;&nbsp;IPO by sample end | −3.14 | [−7.20, +0.22] | 5.33 | −0.115 | no | +1.24 | [+0.16, +2.48] | 28,412 / 1,976 (203) |
| &nbsp;&nbsp;acquisition by sample end (no IPO) | −3.63 | [−9.63, +2.55] | 8.51 | −0.078 | no | −3.10 | [−4.82, −1.04] | 28,412 / 1,976 (203) |
| &nbsp;&nbsp;company clusters | −6.77 | [−11.97, −1.20] | 8.06 | −0.150 | no | −1.86 | [−4.58, +0.93] | 28,412 / 1,976 (203) |
| 36-month exit, vintages 2010–14 | −2.80 | [−9.56, +3.89] | 9.56 | −0.076 | no | −3.14 | [−4.84, −1.25] | 16,299 / 1,139 (89) |
| &nbsp;&nbsp;vintages 2015–17 | −0.04 | [−4.89, +4.59] | 6.73 | −0.001 | yes | −3.22 | [−4.68, −1.63] | 15,227 / 1,367 (160) |
| &nbsp;&nbsp;vintages 2018–20 | +3.05 | [+0.02, +6.39] | 4.97 | +0.096 | no | −2.74 | [−4.11, −1.39] | 16,738 / 1,913 (263) |
| 36-month exit, company clusters | +0.47 | [−2.16, +3.18] | 3.61 | +0.014 | yes | −2.69 | [−3.88, −1.48] | 49,583 / 3,406 (413) |
| 36-month exit, year × sector × stage × country benchmark | +0.96 | [−1.37, +3.39] | 3.47 | +0.029 | yes | −2.79 | [−3.56, −1.90] | 48,122 / 3,299 (400) |
| Same partners and window as eventual exit (deals through 2017-10): 36-month exit | −1.47 | [−5.19, +2.73] | 5.56 | −0.042 | no | −2.97 | [−4.27, −1.78] | 28,412 / 1,987 |
| &nbsp;&nbsp;72-month exit | −4.40 | [−9.64, +0.25] | 7.33 | −0.099 | no | −1.69 | [−3.45, −0.17] | 28,412 / 1,987 |
| &nbsp;&nbsp;exit after month 36 (indicator on the full sample: exit by sample end and not by month 36; equals eventual exit minus 36-month exit by construction) | −5.29 | [−11.01, +0.26] | 8.02 | −0.118 | no | +1.11 | [−0.67, +2.89] | 28,412 / 1,987 |
| &nbsp;&nbsp;follow-on financing within 36 months | −0.75 | [−5.20, +3.73] | 6.88 | −0.017 | no | +0.02 | [−1.22, +1.34] | 28,412 / 1,987 |
| Same partners and window (deals through 2017-10): 60-month exit | −3.76 | [−9.10, +1.03] | 7.24 | −0.088 | no | −1.55 | [−3.13, −0.10] | 28,412 / 1,987 |
| &nbsp;&nbsp;96-month exit | −4.13 | [−8.80, +0.93] | 7.15 | −0.090 | no | −2.32 | [−4.09, −0.58] | 28,412 / 1,987 |
| Horizon differences from the same bootstrap draws (deals through 2017-10): 60 − 36 months | −2.28 | [−5.73, +0.56] | — | — | — | — | — | paired draws 400 |
| &nbsp;&nbsp;72 − 36 months | −2.93 | [−6.94, +0.53] | — | — | — | — | — | |
| &nbsp;&nbsp;96 − 36 months | −2.66 | [−7.20, +1.79] | — | — | — | — | — | |
| &nbsp;&nbsp;eventual − 36 months | −5.29 | [−11.01, +0.26] | — | — | — | — | — | |
| &nbsp;&nbsp;eventual − 96 months | −2.63 | [−5.69, +0.29] | — | — | — | — | — | |
| Partner and year × sector × stage fixed effects entered jointly on the raw outcome: 36-month exit, deals through 2020-10 | +0.67 | [−1.77, +3.07] | 3.53 | — | yes | −2.82 | [−3.77, −1.90] | 49,583 / 3,418 |
| &nbsp;&nbsp;eventual exit, deals through 2017-10 | −5.71 | [−12.18, −0.01] | 8.66 | — | no | −2.43 | [−4.65, −0.40] | 28,412 / 1,983 |
| Female partners' own female-founded − other gap (β_FF + β_int), 36-month exit, deals through 2020-10, 2,000 draws | −2.21 | [−4.42, −0.05] | 3.17 | −0.066 | yes | — | — | — |
| &nbsp;&nbsp;same, follow-on financing | −1.48 | [−4.39, +1.74] | 4.37 | −0.034 | yes | — | — | — |
| &nbsp;&nbsp;same, eventual exit, deals through 2017-10 | −8.62 | [−13.83, −3.23] | 7.49 | −0.191 | no | — | — | — |
| Vintage contrast, eventual exit (deals through 2017-10): β_int for 2015–17 minus β_int for 2010–14 (pooled interaction model) | +1.92 | [−6.09, +10.06] | 11.21 | +0.042 | no | — | — | — |
| Vintage contrast, 36-month exit (deals through 2020-10): β_int for 2018–20 minus β_int for 2010–14 | +1.22 | [−5.37, +7.36] | 8.95 | +0.036 | no | — | — | — |
| Vintage difference from separate regressions per vintage, eventual exit (deals through 2017-10): β_int(2015–17) − β_int(2010–14), independent draws | +6.75 | [−3.29, +16.33] | — | — | — | — | — | 15,124 + 12,871 / — |
| Exits dated on or before the deal excluded (post-deal rule): 36-month exit, deals through 2020-10 | +0.47 | [−1.92, +2.62] | 3.31 | +0.014 | yes | — | — | 49,583 / — |
| &nbsp;&nbsp;same, eventual exit, deals through 2017-10 | −6.77 | [−11.69, −1.04] | 7.44 | −0.150 | no | — | — | 28,412 / — |

*Panel B: partners with at least one female-founded and one other deal in the window. Eligible deals 49,898 → 49,595 with a market benchmark (303 deals alone in their year × sector × stage cell have none) → 49,583 in the estimation sample (12 are a partner's only remaining deal); 3,430 partners (416 women) are eligible and 3,406 (413) retain both kinds of deal after these drops and identify β_int; the partner counts shown in each row follow the same convention (eligible for the P001-54 rows, identifying for the later rows). 32,979 deals are dated 2015 or later; exit3 base rate 0.153. The "inside ±5 pp" column marks whether the 95% interval lies within a reference band equal to the peer-comparison gap of Table 5; it is a reference scale, not a materiality threshold. Outcome = deal outcome minus the leave-one-out mean of its year × sector × stage cell; deal controls as in Panel A. β_FF is the within-partner gap for male partners; β_int is the additional gap for female partners (favoritism predicts β_int < 0); female partners' own gap is β_FF + β_int, with its interval from the same bootstrap draws. The vintage-contrast rows come from one pooled regression with β_int interacted with vintage indicators; the post-deal-rule rows recode exits dated on or before the deal as non-exits (Appendix IA.1). Same-window rows re-estimate the specification on the eventual-exit sample (P001-57). Bootstrap two-sided p-values for β_int on the three featured outcomes (36-month exit, follow-on, exit by sample end): 0.722, 0.494, 0.014; Holm-adjusted 0.988, 0.988, 0.042. Dropping any one of the 204 women from the exit-by-sample-end row moves β_int by at most 0.87 points. Female partners' female-founded deals outside this sample (partners with no other deal): 23.5 percent. Sources: P001-54, P001-57, P001-59, P001-60.*

### Table 8. Does the composition component carry information about later performance? (NA+EU partners with at least five attributed deals through 2017-10)

## Panel A. Open horizon (exit by sample end); post window 2017-11 to 2023-10
Rows are on the percentile scale (β on raw percentile given adjusted percentile) unless marked *levels* (β on the composition component in exit-probability units).
| Specification | β | 95% CI | n |
|---|---|---|---|
| Baseline cell benchmark | +0.091 | [+0.026, +0.151] | 2,169 |
| Leave-one-out cell benchmark | +0.096 | [+0.021, +0.164] | 2,155 |
| Excluding post-period deals in companies the partner backed pre-period | +0.081 | [+0.014, +0.147] | 1,852 |
| Composition component, levels, given tenure and first-deal-year effects | +0.075 | [−0.010, +0.160] | 2,155 |
| Composition component, levels, home-firm fixed effects | +0.088 | [−0.063, +0.270] | 1,616 |
| Decomposition of the composition component, levels: vintage / stage within year / sector within year–stage | +0.058 / +0.079 / +0.161 | [−0.112, +0.258] / [−0.028, +0.190] / [+0.016, +0.325] | 2,155 |
| Same decomposition, given tenure and first-deal-year effects | −0.054 / +0.057 / +0.155 | [−0.322, +0.183] / [−0.072, +0.166] / [+0.004, +0.312] | 2,155 |
| Contrast, levels: adjusted exit rate, same regression as the composition-component levels row | +0.331 | [+0.288, +0.382] | 2,155 |
| Contrast: adjusted percentile's own coefficient | +0.243 | [+0.207, +0.280] | 2,169 |
Remaining rows (benchmark variation and additional analyses) are in Internet Appendix Table IA.1.

## Panel B. Fixed 36-month exit horizon in both periods (post window 2017-11 to 2020-10); levels
β on the composition component, or the named part, in 36-month exit-probability units. Partner-level rows include the adjusted rate, log deal count, gender, tenure, tenure², and first-deal-year effects unless noted. Deal-level rows include the partner's prior within-cell residual, log prior deals, gender, tenure at the deal date and its square, and year effects where no firm–year effect is present.
| Specification | β | 95% CI | n |
|---|---|---|---|
| **Composition component — preferred specification for this question** | **+0.283** | **[+0.070, +0.485]** | 2,009 |
| Sector-within-year–stage part | +0.289 | [+0.026, +0.538] | 2,009 |
| Adjusted exit rate's own coefficient, same regression as the preferred row | +0.155 | [+0.073, +0.253] | 2,009 |
| Home-firm fixed effects (minimum detectable effect 0.41; sector part 0.44) | −0.057 | [−0.318, +0.234] | 1,484 |
| Pre-period restricted to deals whose 36-month window closes before the ranking date (deals through 2014-10; minimum detectable effect 0.35) | +0.067 | [−0.162, +0.302] | 1,118 |
| Reweighted for selection out of post-period observation (inverse probability) | +0.265 | [+0.004, +0.508] | 2,009 |
| Tenure and rank from employment records (join date, title) instead of first-deal tenure; partners with a recorded join date | +0.320 | [+0.122, +0.529] | 1,781 |
| Follow-on construct instead of exit (follow-on within 36 months, both periods) | +0.044 | [−0.164, +0.233] | 2,009 |
| Deal level, within firm–year: composition component (minimum detectable effect 0.17) | +0.056 | [−0.065, +0.168] | 25,471 |
Remaining rows (benchmark variation and additional analyses) are in Internet Appendix Table IA.1.

## Panel C. Where the association sits: within-firm and between-firm coefficients on the composition component (fixed 36-month horizon; Mundlak decomposition)
| Specification | Within firm (deviation from firm mean) 95% CI | Between firms (firm mean) 95% CI | Within − between 95% CI | Partners |
|---|---|---|---|---|
| Component split into within and between; adjusted rate, log deal count, gender and tenure as levels (partial decomposition) | −0.024 [−0.269, +0.228] | +0.447 [+0.193, +0.678] | −0.471 [−0.806, −0.129] | 2,009 |
| + adjusted rate and log deal count also split into within and between | −0.021 [−0.260, +0.248] | +0.440 [+0.166, +0.687] | −0.461 [−0.766, −0.100] | 2,009 |
| Every regressor split into within and between | −0.036 [−0.343, +0.218] | +0.460 [+0.166, +0.703] | −0.496 [−0.852, −0.113] | 2,009 |

*Dependent variable: the partner's post-period (2017-11 to 2020-10) mean benchmarked 36-month exit. Home-firm cluster bootstrap (400). In the second row the firm mean of the adjusted rate carries +0.203 [+0.063, +0.354] and its within-firm deviation +0.081 [−0.055, +0.237]; the firm means of the component and of the adjusted rate correlate at +0.09. Source: P001-60.*

## Panel D. By partner gender (female − male)
Percentile-scale rows are in fractions of the percentile scale (0.01 = one percentile point); *levels* rows are in exit-probability units (exit by sample end).
| Outcome | β | 95% CI | n |
|---|---|---|---|
| Composition component (raw − adjusted percentile) | −0.050 | [−0.075, −0.027] | 2,680 |
| Composition component, leave-one-out benchmark | −0.051 | [−0.080, −0.024] | 2,654 |
| Post-period within-cell performance, levels | −0.004 | [−0.040, +0.034] | 2,169 |
| Post-period within-cell performance, levels, given composition | −0.006 | [−0.043, +0.036] | 2,169 |
| Pre-period within-cell performance, levels (adjusted exit rate) | +0.013 | [−0.019, +0.049] | 2,680 |
| Composition component, levels | −0.041 | [−0.063, −0.018] | 2,654 |
| Composition component, levels, given tenure and first-deal-year effects | −0.016 | [−0.033, +0.002] | 2,654 |
| Vintage / stage-within-year / sector-within-year–stage parts, levels | −0.018 / −0.015 / −0.007 | [−0.029, −0.009] / [−0.029, −0.001] / [−0.016, +0.001] | 2,654 |
| Composition component, levels, given employment-record tenure and rank | −0.020 | [−0.040, +0.000] | 2,327 |
| Composition component, levels, given rank only | −0.039 | [−0.064, −0.013] | 2,327 |

*Partners with ≥5 attributed deals through 2017-10: 2,680 (191 women). Panels A, B and D: deal-count and gender controls; investor-firm cluster bootstrap. Because the adjusted percentile is the raw percentile net of year–sector–stage cell benchmarks, the raw-percentile coefficient given the adjusted percentile equals the coefficient on their difference, the composition component (percentile correlation 0.8613, VIF 7.3); Appendix Table IA.7, Panel A's negative value is that composition coefficient. Panel A and Panel D percentile-scale rows: β per unit of the raw percentile (0.01 = one percentile point); *levels* rows: β per unit of the composition component in exit-probability units. Panel B's control set is stated in its header; the follow-on-construct row reproduces P001-30 (a separate bootstrap in P001-33 returns the same point). Panel B rows below the preferred row are additional analyses. † Exploratory: identifies off within-partner changes in composition over time rather than off placement across partners; clustered by partner. Sources: P001-05, P001-18b, P001-23, P001-25, P001-26, P001-27, P001-28, P001-29, P001-30, P001-31, P001-33, P001-34, P001-36, P001-38, P001-39.*

### Appendix Table IA.1. Does composition carry information? Full specification ladders (Table 8, Panels A and B)
## Panel A. Open horizon (exit by sample end); post window 2017-11 to 2023-10
Rows are on the percentile scale (β on raw percentile given adjusted percentile) unless marked *levels* (β on the composition component in exit-probability units).
| Specification | β | 95% CI | n |
|---|---|---|---|
| Baseline cell benchmark | +0.091 | [+0.026, +0.151] | 2,169 |
| Leave-one-out cell benchmark | +0.096 | [+0.021, +0.164] | 2,155 |
| Leave-one-out, cells with ≥ 10 deals | +0.106 | [+0.026, +0.179] | 2,002 |
| Leave-one-out, cells with ≥ 30 deals | +0.086 | [−0.012, +0.183] | 1,659 |
| Leave-one-out, inverse-probability weighted for post-period observation | +0.086 | [+0.010, +0.159] | 2,155 |
| Levels instead of percentiles: raw exit rate given adjusted exit rate | +0.092 | [+0.016, +0.155] | 2,155 |
| Levels, composition component alone (unconditional) | +0.138 | [+0.072, +0.208] | 2,155 |
| Percentile difference alone (unconditional) | −0.043 | [−0.115, +0.024] | 2,155 |
| Excluding post-period deals in companies the partner backed pre-period | +0.081 | [+0.014, +0.147] | 1,852 |
| Leave-partner-out cell benchmark | +0.094 | [+0.021, +0.155] | 2,155 |
| Composition component, levels, given tenure and first-deal-year effects | +0.075 | [−0.010, +0.160] | 2,155 |
| Composition component, levels, home-firm fixed effects | +0.088 | [−0.063, +0.270] | 1,616 |
| Decomposition of the composition component, levels: vintage / stage within year / sector within year–stage | +0.058 / +0.079 / +0.161 | [−0.112, +0.258] / [−0.028, +0.190] / [+0.016, +0.325] | 2,155 |
| Same decomposition, given tenure and first-deal-year effects | −0.054 / +0.057 / +0.155 | [−0.322, +0.183] / [−0.072, +0.166] / [+0.004, +0.312] | 2,155 |
| Contrast, levels: adjusted exit rate, same regression as the composition-component levels row | +0.331 | [+0.288, +0.382] | 2,155 |
| Contrast: adjusted percentile's own coefficient | +0.243 | [+0.207, +0.280] | 2,169 |

## Panel B. Fixed 36-month exit horizon in both periods (post window 2017-11 to 2020-10); levels
β on the composition component, or the named part, in 36-month exit-probability units. Partner-level rows include the adjusted rate, log deal count, gender, tenure, tenure², and first-deal-year effects unless noted. Deal-level rows include the partner's prior within-cell residual, log prior deals, gender, tenure at the deal date and its square, and year effects where no firm–year effect is present.
| Specification | β | 95% CI | n |
|---|---|---|---|
| **Composition component — preferred specification for this question** | **+0.283** | **[+0.070, +0.485]** | 2,009 |
| Sector-within-year–stage part | +0.289 | [+0.026, +0.538] | 2,009 |
| Adjusted exit rate's own coefficient, same regression as the preferred row | +0.155 | [+0.073, +0.253] | 2,009 |
| Without tenure and first-deal-year effects: composition component | +0.290 | [+0.100, +0.470] | 2,009 |
| Without tenure and first-deal-year effects: adjusted exit rate, same regression | +0.158 | [+0.060, +0.261] | 2,009 |
| Pre-period benchmark at a 72-month horizon | +0.157 | [+0.040, +0.280] | 2,009 |
| Home-firm fixed effects (minimum detectable effect 0.41; sector part 0.44) | −0.057 | [−0.318, +0.234] | 1,484 |
| Post-period deals in companies not backed pre-period | +0.232 | [+0.008, +0.449] | 1,568 |
| Leave-company-out benchmark | +0.319 | [+0.130, +0.517] | 1,995 |
| Both restrictions: companies not backed pre-period and leave-company-out benchmark | +0.313 | [+0.050, +0.561] | 1,557 |
| Post-period deals in companies the partner backed pre-period only | +0.329 | [+0.044, +0.607] | 1,587 |
| Pre-period restricted to deals whose 36-month window closes before the ranking date (deals through 2014-10; minimum detectable effect 0.35) | +0.067 | [−0.162, +0.302] | 1,118 |
| Pre-period restricted to deals from 2014-11 to 2017-10 | +0.321 | [+0.133, +0.503] | 1,293 |
| Reweighted for selection out of post-period observation (inverse probability) | +0.265 | [+0.004, +0.508] | 2,009 |
| Exits recorded before the deal date excluded from the outcome | +0.283 | [+0.073, +0.481] | 2,009 |
| Tenure and rank from employment records (join date, title) instead of first-deal tenure; partners with a recorded join date | +0.320 | [+0.122, +0.529] | 1,781 |
| Same partners, first-deal tenure controls (comparison) | +0.299 | [+0.092, +0.511] | 1,781 |
| Home-firm fixed effects with employment-record tenure and rank | −0.109 | [−0.406, +0.228] | 1,307 |
| Follow-on construct instead of exit (follow-on within 36 months, both periods) | +0.044 | [−0.164, +0.233] | 2,009 |
| Deal level, pooled: prior-year composition (sector part) → deal's within-cell outcome | +0.137 | [+0.056, +0.236] | 35,163 |
| Deal level, within firm–year: sector part (minimum detectable effect 0.18) | +0.047 | [−0.089, +0.166] | 25,471 |
| Deal level, within firm–year: composition component (minimum detectable effect 0.17) | +0.056 | [−0.065, +0.168] | 25,471 |
| Deal level, within firm–year, deals in companies not previously backed by the partner: sector part | +0.117 | [−0.087, +0.316] | 11,630 |
| Deal level, within partner: composition component (exploratory†) | +0.235 | [+0.016, +0.451] | 34,727 |

*Same construction, samples, and sources as Appendix Table IA.4; see its note.*

### Appendix Table IA.2. Robustness and measurement diagnostics
## Panel A. Sector-layer matching coefficient across specifications (rows re-estimated in a separate bootstrap run; the canonical baseline interval is Table 2)
| Row | Estimate (pp) | 95% CI | n |
|---|---|---|---|
| baseline | +3.22 | [+1.83, +4.51] | 126,128 |
| T1_ff_majority | +2.98 | [+1.85, +4.21] | 126,128 |
| T1_ff_solo | +1.13 | [+0.51, +1.77] | 126,128 |
| T2_solo_attr | +3.61 | [−0.82, +12.16] | 35,193 |
| T4_profile_rich | +3.63 | [+2.17, +5.19] | 104,232 |
| T5_cluster_partner | +3.22 | [+2.09, +4.21] | 126,128 |
| T5_cluster_org | +3.22 | [+2.07, +4.40] | 126,128 |
| stage layer, generic labels excluded | +0.56 | [−0.71, +2.12] | 113,940 |

## Panel B. Follow-on estimates across specifications (cell-demeaned within-cell estimator; the 'baseline' row carries no deal controls, which is why it differs from the covariate-adjusted battery of Appendix Table IA.9, Panel B)
| Row | Estimate (pp) | 95% CI | n |
|---|---|---|---|
| baseline | +1.01 | [−1.46, +3.82] | 13,116 |
| T1_ff_majority | +0.58 | [−2.09, +2.94] | 8,216 |
| T2_solo_attr | +7.18 | [−50.00, +12.17] | 4,101 |
| T3_fon24 | +1.39 | [−1.88, +4.19] | 16,646 |
| T4_profile_rich | +2.50 | [−0.43, +6.27] | 10,722 |
| T5_cluster_partner | +1.01 | [−0.82, +2.87] | 13,116 |

## Panel C. Measurement diagnostics
| | |
|---|---|
| Firm attribution rate ~ female-partner share (correlation) | −0.022 [−0.042, +0.000] |
| Attribution × gender drift correlation (annual) | −0.061 |
| Deal-level salience fingerprint: FF × firm FP-share → P(attributed) | +2.45pp [+0.43, +4.34] (varies within firms with the deal's founder gender, so it is not absorbed by firm fixed effects; Appendix IA.2) |
| Generic stage-label share: FP / MP deals | 8.6% / 9.8% |
| Founder-gender determinable vs not: US / early / vintage | +27.6pp / −16.6pp / −1.92y |

## Panel D. Rank-measure diagnostics and external-pricing sensitivity
| | |
|---|---|
| Raw vs adjusted percentile: correlation / VIF / share of raw variation independent of controls | 0.8613 / 7.31 / 13.7% |
| Raw percentile alone → mobility; → spinout | +0.045 [−0.023, +0.119]; +0.034 [−0.017, +0.089] |
| Adjusted percentile alone → mobility; → spinout | +0.054 [−0.002, +0.119]; +0.061 [+0.017, +0.106] |
| Out-of-sample AUC (5-fold), raw minus adjusted: mobility; spinout | −0.0036; −0.0145 |
| Composition → fund formation: with pre-period early-stage share and sector breadth as controls / without | +0.393 [−0.141, +0.849] / +0.506 [+0.150, +0.847] |
| Composition → receiving-firm quality: with / without | +1.100 [−0.371, +2.375] / +1.227 [+0.313, +2.156] |
| Post-period observation ← composition component (LPM; percentile-point units) | −0.432 [−0.528, −0.324]; n = 2,654 |
| Post-period observation ← vintage / stage-within-year / sector-within-year–stage components (levels) | −2.183 [−2.403, −1.935] / +0.361 [+0.150, +0.564] / +0.108 [−0.141, +0.333] |
| Post-period observation ← tenure (years since first attributed deal), given components | +0.0299 [+0.0040, +0.0771] |
| Composition → log fund size: with pre-period late-stage share as control / late-stage share own coefficient | +0.679 [−1.383, +2.738] / +1.417 [+0.721, +2.140] |
| Log fund size ← stage part / ← sector part given late-stage share / ← sector part given late-stage share and tenure | +5.535 [+2.659, +8.311] / +2.787 [+0.173, +5.601] / +2.596 [−0.892, +5.378]; n = 196 |
| Fund formation ← sector part given late-stage share and tenure | +0.292 [−0.543, +1.066]; n = 377 |
| Minimum detectable effects (80% power), composition component / sector part: open-horizon home-firm FE; fixed-horizon home-firm FE; deal-level firm–year FE | 0.238 / 0.328; 0.407 / 0.437; 0.170 / 0.179 |
| Three-part multiplicity adjustment (maximum absolute t) of the open-horizon sector part: two-sided p, adjusted / unadjusted | 0.135 / 0.048 |
| Within-firm share of variance in the home-firm FE sample: composition component / sector part | 0.33 / 0.62 |
| Mundlak decomposition, open horizon, within-firm / between-firm coefficient: sector part | +0.136 [−0.085, +0.355] / +0.173 [−0.036, +0.397] |
| Same, composition component | +0.115 [−0.017, +0.276] / +0.061 [−0.031, +0.163] | 
| Same, composition component, within-minus-between contrast | +0.054 [−0.087, +0.216] |
| Mundlak decomposition, fixed 36-month exit horizon, within-firm / between-firm / contrast: composition component | −0.024 [−0.280, +0.250] / +0.447 [+0.196, +0.727] / −0.471 [−0.854, −0.106]; n = 2,009 |
| Same, adding the home firm's fund count, cumulative fund size and fund age at the sample split (Crunchbase funds; SEC Form D tier-1 filings): between-firm coefficient / contrast; R² of the firm-mean composition on those variables | +0.438 [+0.143, +0.688] / −0.464 [−0.807, −0.082]; R² 0.058 |
| Same, sector part | +0.011 [−0.291, +0.284] / +0.505 [+0.151, +0.890] / −0.494 [−0.954, −0.074] |
| Follow-on vs exit benchmarks: weighted correlation of year–sector–stage cell means (follow-on, 36-month exit) / (follow-on, exit by sample end); range of stage-level rates excluding private equity, follow-on / 36-month exit | −0.24 / −0.03; 0.187 / 0.279 |
| Employment-record tenure: share of partners with a home-firm join date / correlation with first-deal tenure / share attributed before the recorded join date / female−male tenure difference (years) | 0.877 / +0.65 / 0.293 / −1.61 |
| Standardized coefficients in one regression, composition component / adjusted rate: fixed horizon with tenure controls; open horizon | +0.084 / +0.084; +0.053 / +0.298 |
| Split-half agreement at the fixed horizon (upper bound on reliability): sector part / composition component / adjusted rate | 0.49 / 0.61 / 0.47 |
| 36-month exit: share of positives recorded before the deal date, pre / post; post-period base rate with those excluded | 0.000 / 0.000; 0.1388 |
| Post-period observation ← vintage part / employment-record tenure, given components and rank | −2.370 [−2.695, −2.052] / +0.0125 [+0.0055, +0.0203]; n = 2,327 |
| Share of the fixed-horizon partner sample observed in the post period | 0.757 |
| Pre-period deals entering the fixed-horizon panel whose 36-month window closes after the ranking date / whose outcome is undetermined at that date | 0.467 / 0.399 |
| Correlation of tenure (years since first attributed deal) with the composition component, open horizon | 0.52 |
| Deal-level firm–year FE sample: deals / firms | 25,471 / 658 |
| Fixed-horizon Mundlak: correlation of firm-mean composition with firm-mean adjusted rate / partners who are the only sampled partner at their firm | +0.117 / 434 of 2,009 |
| Identifying variation of the Table 5 peer comparison (firm × year × sector), NA+EU / global: cells with both partner genders among FF deals / deals in them / share of FF deals | 173 / 427 / 0.060; 190 / 475 / 0.059 |
| Peer availability, NA+EU: share of female-partner FF deals with a same-cell male-partner FF deal / female partners with at least one such deal (of 323) / same share across all deals | 0.236 / 89 / 0.419 |
| Peer-comparison estimate re-estimated on the mixed cells only, NA+EU / global (pp) | −4.47 / −6.19 (identical to the full-sample estimates) |
| Leave-one-cell-out jackknife of the peer-comparison estimate: maximum shift (pp), NA+EU / global; any value outside the bootstrap interval | 0.72 / 0.64; no |
| Within-cell random reassignment of partner gender (400 draws): 95th percentile of the absolute estimate (pp), NA+EU / global; share of draws at or beyond the estimate | 5.51 / 4.61; 0.115 / 0.025 |
| Same for the + stage cells, NA+EU: cells / deals / placebo 95th percentile / share at or beyond | 154 / 333 / 3.28 / 0.635 |
| Deal level, fixed horizon, without the partner's prior within-cell residual as a control — within firm–year: sector part / composition component; pooled: sector part | +0.037 [−0.123, +0.163] / +0.037 [−0.102, +0.161]; +0.162 [+0.056, +0.254] |
| Deal level, open-horizon construct (exit by sample end), within firm–year: sector part | +0.002 [−0.155, +0.167]; n = 33,441 |
| Split-half agreement (Spearman–Brown; halves share cell benchmarks, so an upper bound on reliability): vintage / stage / sector parts / composition component / adjusted rate | 0.97 / 0.87 / 0.46 / 0.84 / 0.59 |
| Fixed exit horizon: standard deviation of the vintage part / standardized composition coefficient (sd units) | 0.0152 / +0.084 |
| Deal-level sample: firm–years with ≥ 2 partners / share of post-period deals in companies the partner backed pre-period (fixed-horizon window) | 2,391 / 0.218 |
| Spinout population counts, leave-one-out partner sample: spinouts / fund close observed / fund size observed | 377 / 220 / 196 (Appendix Table IA.7, Panel B, uses the baseline-benchmark sample: 380 / 221 / 197) |

## Panel E. Region split and the identifying base of the peer comparison
| | United States | North America (US + Canada) | Europe (24 countries) |
|---|---|---|---|
| Peer-comparison exit gap, firm × year × sector (pp); mixed cells / deals | −4.02 [−10.35, +1.41]; 144 / 349 | −4.60 [−11.95, +1.13]; 145 / 351 | not computable (within-cell exit variation zero); 27 / 63 |
| Within-cell reassignment placebo, 95th percentile of \|β\| (pp) | 5.69 | 5.81 | — |
| + stage cell gap (pp) | −1.02 [−5.36, +3.17] | −1.02 [−4.93, +3.04] | not computable |
| Follow-on within 36 months, + stage cell, FP coefficient (pp) | +0.76 [−2.56, +4.11] | +0.76 [−2.89, +4.62] | not computable |
| Fixed-horizon composition coefficient (Table 8, Panel B, preferred specification); partners | +0.189 [−0.017, +0.401]; 2,075 | +0.229 [+0.004, +0.435]; 2,155 | +0.295 [+0.083, +0.579]; 461 |

| Identifying base of the Table 5 peer comparison | NA+EU, firm × year × sector | NA+EU, + stage | Global, firm × year × sector |
|---|---|---|---|
| Mixed cells that are co-attributions on a single round (share) | 112 (0.65) | 134 (0.87) | 119 (0.63) |
| Cells with within-cell exit variation / deals in them | 30 / 100 | 8 / 18 | 35 / 119 |
| Share of identifying variance (Σx̃²) from single-round cells | 0.57 | 0.85 | 0.55 |
| Exit gap on multi-round cells only (pp); MDE; placebo 95th percentile | −10.49 [−22.19, +1.50]; 17.73; 12.83 | −5.52 [−26.76, +20.50]; 32.4; 22.07 | −13.69 [−24.59, −2.32]; 15.73; 12.11 |
| Follow-on gap on multi-round cells only (pp) | −1.29 [−9.95, +7.27] | +4.14 [−11.34, +24.63] | −2.25 [−11.72, +7.18] |

| Identifying base of the Appendix Table IA.9 hazard (cell × elapsed-year effects) | Value |
|---|---|
| Cells with female-partner variation / rows; share that are co-attributions on a single round | 814 / 1,764; 0.89 |
| Cells with within-cell exit variation (share); exit events in them | 10 (0.01); 12 |
| Share of identifying variance from single-round cells | 0.87 |
| Annual hazard gap, all cells, re-estimated in this audit run with its own bootstrap (pp/yr; the reference estimate is Appendix Table IA.9, Panel A); within ±25% of the 6.19% base | −0.244 [−1.00, +0.31]; yes |
| Annual hazard gap, multi-round cells only (pp/yr); MDE; within ±25% of base | −1.699 [−11.83, +2.87]; 11.31; no |

*Panel A 'baseline' re-estimates the Table 2 sector layer inside the robustness battery (separate bootstrap run; point identical, interval differs by resampling). Panel D: composition-component coefficients are in exit-probability units per unit of the component (0.01 of the percentile scale = one percentile point) unless a row states percentile-point units; fund-size coefficients are log points per unit of the component. Sources: P001-07, P001-08, P001-16, P001-22, P001-23, P001-25, P001-28, P001-29, P001-30, P001-31, P001-32, P001-33, P001-34, P001-35, P001-37, P001-38, P001-39, P001-40, P001-41, P001-48, P001-49, P001-50. Solo-attribution rows lose precision (negative_results/W4_notes.md); points consistent with baselines.*

### Appendix Table IA.3. Movers, absences, and the financing-ladder pipeline
## Panel A. Movers: the same partner at two firms (≥ 5 attributed deals at each; NA+EU)
| Specification | β | 95% CI | n transitions |
|---|---|---|---|
| Change in the partner's early-stage share on the change in her firm's leave-partner-out early-stage share, all transitions | +0.563 | [+0.461, +0.665] | 241 |
| Same, non-overlapping spells only | +0.621 | [+0.421, +0.808] | 79 |
| Same for the stage part of the composition component | +0.706 | [+0.555, +0.821] | 241 |
| Same for the sector part | +0.179 | [−0.037, +0.386] | 241 |
| Levels: destination firm's share / origin firm's share | +0.535 [+0.410, +0.678] / −0.605 [−0.751, −0.493] | | 241 |
| Placebo destination (random firm in the same size decile) / origin | +0.050 [−0.071, +0.170] / −0.458 [−0.572, −0.350] | | 233 |
| Sorting check: pre-move own share on the destination firm's share measured before the move (given the origin firm's) | +0.149 | [+0.022, +0.268] | 162 |
| Moves toward later-stage firms / toward earlier-stage firms | +0.406 [+0.102, +0.716] / +0.579 [+0.393, +0.787] | | 81 / 157 |

Movers 380 (37 women), 408 transitions, 138 with non-overlapping spells. Partner-cluster bootstrap. The design is gender-neutral by construction (37 female movers).

## Panel B. Absences: interior gaps of 18 months or more in a partner's attributed record while she remains at the firm
Outcome: female-founded share of the firm's other deals in the half-year; partner × firm and half-year effects; firm-cluster bootstrap. "Difference" is the female-partner minus male-partner absence coefficient.
| Outcome / gap length | Female partners' absence | 95% CI | Male partners' absence | 95% CI | Difference | 95% CI | MDE |
|---|---|---|---|---|---|---|---|
| Colleagues' attributed deals, ≥ 18 months | −0.017 | [−0.050, +0.013] | −0.004 | [−0.012, +0.004] | −0.013 | [−0.046, +0.019] | 0.047 |
| Same, ≥ 24 months | −0.014 | [−0.052, +0.034] | −0.009 | [−0.020, +0.001] | −0.005 | [−0.044, +0.045] | 0.064 |
| All of the firm's equity deals in sample companies, ≥ 18 months | +0.003 | [−0.020, +0.028] | −0.000 | [−0.006, +0.005] | +0.003 | [−0.019, +0.029] | 0.034 |
| Same, spells with recorded continuous employment | −0.002 | [−0.030, +0.025] | +0.001 | [−0.005, +0.008] | −0.003 | [−0.030, +0.026] | 0.040 |
| Recording placebo: firm's attribution rate during the gap | −0.167 | [−0.216, −0.117] | −0.208 | [−0.231, −0.188] | +0.041 | [−0.015, +0.093] | |
| Scale placebo: log colleague deal count | −0.129 | [−0.194, −0.057] | −0.167 | [−0.189, −0.141] | +0.038 | [−0.034, +0.108] | |

Partners with a ≥ 18-month gap 1,564 (128 women); spells in the panel 1,556. Pre-gap event-time coefficients (four half-years) joint sup-t p = 0.43.

## Panel C. Financing-ladder pipeline (descriptive): where the female-partner share narrows along the ladder
| Margin | Estimate | 95% CI | n |
|---|---|---|---|
| Company reaches Series A: female-founded − other, first-round year × sector × country cells | −7.27pp | [−9.12, −5.58] | 18,124 |
| Company reaches Series B or later | −6.61pp | [−8.26, −4.86] | 18,124 |
| Same, companies acquired or listed before Series B excluded | −8.19pp | [−10.09, −6.39] | 14,981 |
| Incumbent firm re-invests in the next round (given a next round within 36 months): FP × FF, firm × year × sector × stage cells | −1.27pp | [−6.54, +3.46] | 20,687 |
| Same partner re-attributed (given the firm re-invests): FP × FF | −0.85pp | [−7.00, +6.48] | 10,299 |
| Conditioning event (next round within 36 months): FP × FF | −0.98pp | [−6.45, +3.70] | 31,218 |
| Coverage: next round has recorded investors / re-investing firm has a recorded partner, FP × FF | −0.12pp [−2.43, +2.05] / −4.52pp [−10.69, +1.05] | | |
| Female-partner share among investors new to the company: early / later stage, female-founded companies | 15.6% / 12.0% | n = 1,465 / 722 | |
| Same, other companies | 8.3% / 8.0% | n = 7,736 / 4,862 | |
| Entrant female-partner share on later stage: all companies / female-founded × later stage | −0.37pp [−1.33, +0.61] / −3.21pp [−6.74, −0.29] | | 14,785 |

Raw four-cell re-investment rates (FP, FF): {'fp0_ff0': 0.5252, 'fp0_ff1': 0.4901, 'fp1_ff0': 0.5045, 'fp1_ff1': 0.4301}. Companies with an early first round 2010–2019: 19,380 (3,738 female-founded). Sources: P001-42, P001-46, P001-43, P001-44, P001-45. All rows are bootstrap percentile intervals; no causal claim is made in this table.

### Appendix Table IA.4. The deal held fixed: within-round comparison of co-investors on female-founded rounds (NA+EU)
Outcome varies across investors in the same round; company, sector, stage, vintage, founder team, and syndicate are fixed by construction. Round fixed effects; investor experience control; company-cluster bootstrap. β is the female-partner slope in female-founded rounds; "other" is the slope in other rounds; "difference" is female-founded minus other.
| Outcome | β (female-founded rounds) | 95% CI | β (other rounds) | 95% CI | Difference | 95% CI | n rows / companies |
|---|---|---|---|---|---|---|---|
| Firm re-invests in the company's next round (next round within 36 months; conditional) | −0.004 | [−0.048, +0.031] | +0.006 | [−0.013, +0.026] | −0.010 | [−0.056, +0.026] | 7,675 / 1,730 |
| Same, unconditional (no next round coded as zero) | +0.002 | [−0.027, +0.030] | +0.003 | [−0.013, +0.018] | −0.001 | [−0.034, +0.029] | 10,361 / 2,314 |
| Same partner attributed on the next round, given the firm re-invests | −0.002 | [−0.044, +0.039] | +0.005 | [−0.015, +0.026] | −0.007 | [−0.050, +0.037] | 3,294 / 884 |
| Lead-investor flag on the round (recorded on 58 percent of rows) | −0.031 | [−0.092, +0.026] | −0.002 | [−0.034, +0.030] | −0.029 | [−0.098, +0.038] | 4,756 / 1,283 |
| Reverse placebo: firm invested in the company's previous round | −0.003 | [−0.049, +0.040] | −0.016 | [−0.040, +0.009] | +0.013 | [−0.040, +0.064] | 8,862 / 1,935 |

*Variants of the re-investment margin, female-founded rounds only (P001-51; β = female-partner slope; company-cluster bootstrap unless stated):*
| Variant | β | 95% CI | MDE80 | within ±5 pp | n rows / clusters |
|---|---|---|---|---|---|
| Any-female attribution — initial run (400 draws) | −0.38 | [−4.08, +3.18] | 5.36 | yes | 1,609 / 388 |
| Female-only attribution — initial run (400 draws; 126 rows attributed to both a woman and a man dropped, 322 rows in all once rounds left without a female–male contrast fall out) | −1.53 | [−5.93, +2.46] | 6.27 | no | 1,287 / 323 |
| **Any-female attribution — reference run (2,000 draws)** | −0.38 | [−4.13, +3.34] | 5.46 | yes | 1,609 / 388 |
| **Female-only attribution — reference run (2,000 draws)** | −1.53 | [−6.06, +3.13] | 6.52 | no | 1,287 / 323 |
| Three categories: female-only vs male-only | −1.37 | [−5.71, +2.53] | 5.98 | — | 1,609 / — |
| Three categories: mixed attribution vs male-only | +3.55 | [−4.79, +11.21] | 11.01 | — | 126 mixed rows |
| Any-female, investor-cluster bootstrap | −0.38 | [−3.55, +2.40] | 4.34 | yes | 1,609 / 756 |
| Female-only, investor-cluster bootstrap | −1.53 | [−4.60, +1.85] | 4.65 | yes (margin 0.40 pp) | 1,287 / 670 |
| Any-female + all pre-round investor controls† | −0.65 | [−4.14, +3.93] | 5.60 | yes | 1,609 / 388 |
| Female-only + all pre-round investor controls† | −1.56 | [−5.99, +2.92] | 6.50 | no | 1,287 / 323 |
| Any-female + fund-cycle controls (Crunchbase fund age, size, sequence; SEC Form D tier-1 vintages and amounts)‡ | −0.40 | [−4.38, +3.30] | 5.69 | yes | 1,609 / 388 |
| Female-only + fund-cycle controls‡ | −1.69 | [−5.72, +2.53] | 6.22 | no | 1,287 / 323 |
| Round + investor fixed effects, all mixed rounds (fp × female-founded; β = female-founded slope) | −1.09 | [−6.52, +4.86] | 8.87 | no | 7,675 / 291 investors with varying attribution |

*Sample and window (P001-56): β, 95% CI, MDE80 and the ±5 pp verdict under the two treatment definitions:*
| Sample; deals through; next round within | Any-female attribution | Female-only attribution | FF rounds / rows |
|---|---|---|---|
| NA+EU companies; 2020-10; 36 months (baseline) | −0.38 [−4.23, +3.65]; MDE 5.45; yes | −1.53 [−5.77, +3.27]; MDE 6.43; no | 532 / 1,609 |
| All countries; 2020-10; 36 months | −0.10 [−3.79, +3.80]; MDE 5.40; yes | −0.85 [−4.78, +3.44]; MDE 6.02; yes | 590 / 1,764 |
| NA+EU; 2021-10; 24 months | −1.20 [−4.53, +2.34]; MDE 5.06; yes | −2.12 [−6.39, +2.33]; MDE 6.26; no | 586 / 1,785 |
| All countries; 2021-10; 24 months | −0.45 [−3.80, +2.86]; MDE 4.96; yes | −1.03 [−5.12, +2.77]; MDE 5.62; no | 665 / 2,010 |

*Lead status, partner tenure, pseudo-treatment and the exit association (NA+EU baseline sample):*
| Check | Estimate | 95% CI | n rows / rounds |
|---|---|---|---|
| Lead flag recorded (investor-level flag combined with the round-level lead list): coverage | 88 percent (agreement 1.00 where both exist) | — | — |
| Female-partner investor is lead, within round (pp) | −0.42 | [−5.98, +5.10] | 1,391 / 471 |
| Partner tenure, female-attributed − male-attributed investor (years) | −1.24 | [−1.87, −0.71] | 1,609 / 532 |
| Re-investment, any-female, + tenure control (pp) | −0.18 | [−4.17, +3.80] | 1,609 / 532 |
| Re-investment, female-only, + tenure control (pp) | −1.29 | [−6.01, +3.51] | 1,287 / 434 |
| Pseudo-treatment: junior-partner investor in all-male female-founded rounds (pp) | −0.10 | [−2.85, +2.09] | 3,020 / 1,164 |
| Re-investment rate when the company later exits vs not (deals through October 2017; pp) | +3.7 | [−6.42, +13.90] | 786 / — |

*Row 2 of the first sub-table (the unconditional outcome) includes 199 rounds with no next round, whose outcome is zero for every investor by construction (69 percent of their identifying variance comes from constant-outcome rounds); its interval is not read as a bound. The reference rows (2,000 draws) are the estimates quoted in the text; the initial 400-draw rows and the investor-cluster variants are shown for transparency and are not counted as separate robustness results. Sources: P001-42, P001-51, P001-52, P001-56, P001-58, P001-59.*

*Investor-level differences within the same rounds (female-attributed − male-attributed investor; pre-round traits) and positive controls (within-round slope of re-investment on the trait):*
| Investor trait | Difference | 95% CI | Standardized | Re-investment slope | 95% CI |
|---|---|---|---|---|---|
| Pre-round female-founded share of attributed deals | +0.070 | [+0.044, +0.098] | +0.30 | — | — |
| Pre-round early-stage share of attributed deals | +0.041 | [+0.011, +0.079] | +0.13 | −0.209 | [−0.310, −0.111] |
| Investor firm age (years) | −3.70 | [−5.95, −1.73] | −0.18 | — | — |
| Fund age (years since last fund announced; 75 percent coverage) | −0.33 | [−0.59, −0.07] | −0.18 | −0.0211 | [−0.0353, −0.0075] |
| Log size of the latest fund (Crunchbase; P001-58) | −0.372 | [−0.579, −0.167] | −0.23 | +0.0348 | [+0.0158, +0.0544] |
| Fund sequence number (Crunchbase; P001-58) | +0.329 | [−0.320, +0.944] | +0.06 | +0.0067 | [+0.0023, +0.0128] |
| Any SEC Form D tier-1 fund filing before the round (coverage 23 percent) | +0.043 | [−0.010, +0.098] | +0.10 | +0.0267 | [−0.0275, +0.0766] |
| Investor experience (log prior rounds) | −0.172 | [−0.384, +0.037] | −0.10 | +0.0327 | [+0.0173, +0.0471] |
| Lead-investor flag (57 percent coverage) | −0.049 | [−0.120, +0.019] | −0.10 | +0.107 | [+0.035, +0.172] |

Female-founded rounds with a next round within 36 months: 532 rounds, 1,609 investor rows, 388 companies, 756 investor firms (the pooled regression with other rounds spans 1,730 companies). These rounds are larger than all female-founded equity rounds in the window (median $8.0 million vs $2.5 million; early-stage 62 vs 70 percent); partner attribution covers 45 percent of their investor rows, and attributed co-investors re-invest +18.9 pp [+15.76, +22.21] more often than unattributed ones within the same rounds. † Pre-round controls: female-founded share, early-stage share and log count of the investor's prior attributed deals, investor firm age, fund age (each with a missing indicator). ‡ Fund-cycle controls: Crunchbase fund age, log size and sequence number of the investor's latest fund before the round, and the count, latest vintage and cumulative amount of the investor's SEC Form D tier-1 fund filings before the round (missing indicators included; P001-58). Sources: P001-42, P001-51. Re-investment base rate in those rounds 0.465; raw four-cell double difference −0.0380. Within-round permutation of partner gender (500 draws): two-sided p = 0.860. Minimum detectable effect (80% power) of β in female-founded rounds: 0.055.

### Appendix Table IA.5. The female-partner channel along the financing ladder (NA+EU)
| Stage | P(FP given FF deal) % | P(FP given no observed female founder) % |
|---|---|---|
| Early (pre-seed/seed/angel) | 20.2 | 11.07 |
| Series A | 17.94 | 9.81 |
| Series B and beyond | 13.38 | 8.13 |

| Differential early−late slope (FF − other) | Estimate (pp) | 95% CI |
|---|---|---|
| Baseline | +3.89 | [+1.36, +6.63] |
| Reweighted for stage-varying determinability | +4.38 | [+1.81, +7.10] |
| Majority-female founder teams | +3.71 | [+0.72, +6.79] |
| Reallocation counterfactual: late-stage FF–FP contacts | +26.8% (from 813 deals) | |

## Between-firm check (Snellman–Solal-style): female-founded companies' first rounds
| Lead-team definition and sample | Design | Estimate | 95% CI | n / events (treated) |
|---|---|---|---|---|
| All attributed lead partners female vs all male, mixed teams excluded; US, seed and Series A, 2010–18 | Cox proportional hazards on exit, treatment only | HR 0.990 (log-hazard −0.010) | [−0.831, +0.466] on log hazard | 421 / 142 (36) |
| Alternative lead-team definition: any attributed lead partner female (pools mixed teams); NA+EU, 2010–20 | LPM follow-on within 36m, year FE | +2.26 pp | [−5.26, +9.13] | 1,377 |
| Alternative: lead-firm female-partner share above median; NA+EU, 2010–20 | LPM follow-on within 36m, year FE | +6.15 pp | [+1.50, +10.37] | 4,197 |

*n = 113,066 (ladder). The first between-firm row is the targeted comparison; Cox specifications adding year, sector, and stage terms did not meet the convergence criterion at 36 treated observations (sparse year–sector cells) and are not reported. The alternative definitions pool all-female with mixed lead teams — the highest-performing cell in Snellman and Solal (2023) — and are reported as alternatives, not as estimates of the all-female contrast. Sources: P001-06, P001-17, P001-24, P001-19.*

### Appendix Table IA.6. Partner turnover and deal composition: deal-level stacked event studies (NA+EU)
## Featured: arrival margin (deal-level)
| | Estimate (pp) | 95% CI |
|---|---|---|
| **Female arrival × post (vs male arrivals, reweighted)** | **+2.83** | **[+1.49, +3.99]** |
| Departure margin (same design) | +0.88 | [−1.71, +3.15] |
| Colleague deals only (event partner's own deals excluded) | +1.95 | [−0.14, +4.21] |
| Arrival + departure (mirror-reversal test: = 0 under exact reversal; same bootstrap draws) | +3.72 | [+0.22, +6.74] |
| Own-deal share of post-event flow after female arrivals; FF share of own deals vs colleagues' deals; direct composition share s·(p_own − p_colleagues) | 2.1%; 28.8% vs 24.3% | +0.10 pp |
| Female arrivals that are the firm's first female partner; female departures that remove its last (shares of events) | 36% of 1,057; 33% of 400 | |
| Pre-event path k=−4..−2 (pp, ref k=−1) | −1.35, −0.37, −1.69 | |
| Trend sensitivity: CI lower bound reaches 0 at δ* (point stays >0 to ≈0.7) | 0.4 pp/half-yr | observed pre-slope ≈ 0 |
| Event-aggregated design, own breakdown slope (pp per half-year) | 0.597 | |

## Robustness: symmetric and aggregated versions
| | Estimate (pp) | 95% CI |
|---|---|---|
| Deal-level arrival − departure contrast | +1.95 | [−0.14, +4.13] |
| Event-aggregated contrast (half-year shares, reweighted) | +2.39 | [+0.18, +4.63] |
| — permutation p (gender labels) | 0.02 | |
| — placebo: all-male-team deal counts (log points) | −0.024 | [−0.125, +0.082] |
| Pre-hire run-up in firm FF share, levels (I-76) | +2.2 | [+1.3, +3.2] |

*Deal-level design: 242,388 deal observations around 4,788 clean events (arrivals: no attributed deal before recorded start), event FE + relative-half FE, contaminated male controls excluded, firm-cluster bootstrap. Aggregated design: P001-04b (1,177 female events). Sources: P001-11, P001-14b, P001-04b, I-82, I-76.*

### Appendix Table IA.7. Subsequent attributed deal activity, career margins, and the implied composition contribution to the gender gap (NA+EU partners with at least five attributed deals through 2017-10)

## Panel A. Subsequent attributed deal activity: log count of deals attributed to the partner in 2018–2020 on 2010–17 percentiles
| | β (log deals per unit of percentile rank, 0–1) | 95% CI |
|---|---|---|
| Adjusted percentile A, holding the raw percentile fixed (β_A) | +1.55 | [+1.27, +1.84] |
| Raw percentile R, holding A fixed (β_R) = coefficient on the rank difference R − A | −1.74 | [−2.06, −1.41] |
| Adjusted percentile A, holding the rank difference R − A fixed (β_R + β_A; same bootstrap draws) | −0.18 | [−0.31, −0.05] |

## Panel B. External outcomes among partners who move or spin out, 2017-11 to 2023-10
| Outcome | Sample | β on composition component (given adjusted percentile) | 95% CI | β with pre-period late-stage share as control | 95% CI | Late-stage share, own coefficient |
|---|---|---|---|---|---|---|
| New firm records a fund close (partners who spin out) | 379 partners; 221 raise (58.3%) | +0.506 | [+0.150, +0.847] | +0.460 | [−0.056, +1.000] | +0.206 [+0.042, +0.362] |
| log fund size recorded | 197 | +2.490 | [+0.960, +3.955] | +0.679 | [−1.383, +2.738] | +1.417 [+0.721, +2.140] |
| Receiving firm's prior attributed deal count, log(1+n) (partners who move) | 710 | +1.227 | [+0.313, +2.156] | +0.716 | [−0.802, +2.317] | +0.590 [+0.150, +1.064] |
| Joint randomization test, three outcomes (uncontrolled) | 400 permutations of the composition component | Mahalanobis 28.8 vs null 95th percentile 7.7; 3/3 signs aligned | p < 0.003 (no exceedance in 400 permutations) | | | |

## Panel C. Implied contribution of female partners' composition to the female − male difference in post-period within-cell performance (levels; Σ tenure-controlled part gap × tenure-controlled coefficient, same resamples)
| Horizon | β | 95% CI | n |
|---|---|---|---|
| Implied contribution of composition to the post-period gap, levels, open horizon (Σ tenure-controlled part gap × tenure-controlled coefficient, same resamples; materiality band ±0.02; interval inside ±0.01) | −0.0014 | [−0.0047, +0.0008] | 2,155 |
| Same, fixed 36-month exit horizon (post window to 2020-10) | −0.0006 | [−0.0047, +0.0041] | 2,009 |

*Panel A: deal-count and gender controls plus pre-period early-stage share and sector breadth; investor-firm cluster bootstrap. Panel C is a model-conditional implied contribution (common linear slopes across genders; tenure controls), reported against a ±2-point materiality band for this channel. Sources: P001-18b, P001-23, P001-25, P001-29, P001-36, P001-38.*

### Appendix Table IA.8. Population check: investor types, attributed partners' titles, and key results on venture-capital-type firms only
## Panel A. Composition of the attributed records (NA+EU)
| | Share |
|---|---|
| Deals at investors whose Crunchbase type includes venture capital, micro VC, or corporate VC | 86.8% |
| Deals at investors with no recorded type | 2.1% |
| Most common first-listed investor types (share of deals) | venture_capital 61.0%; private_equity_firm 12.2%; accelerator 7.1%; micro_vc 5.0%; corporate_venture_capital 4.9%; angel_group 2.2% |
| Attributed partner–firm pairs by job title at the firm: general/managing/founding partner; other partner; principal; director/MD/VP; founder/CEO/chief; associate/analyst; other; no job record | 21.0%; 18.5%; 3.2%; 14.4%; 9.1%; 0.8%; 8.0%; 25.0% |

## Panel B. Key results restricted to venture-capital-type investors
| | Estimate | 95% CI | n / cells or partners |
|---|---|---|---|
| Matching coefficient, firm × year cells (pp) | +7.04 | [+5.55, +8.58] | 35,232 / 3,250 |
| Matching coefficient, firm × year × sector × stage cells (pp) | +0.67 | [−0.60, +1.93] | 8,461 / 2,921 |
| Peer comparison, exit by sample end, female-founded deals through 2017-10, firm × year × sector: NA+EU (pp) | −4.80 | [−11.33, +0.18] | 398 / 161 |
| &nbsp;&nbsp;global (pp) | −6.72 | [−12.38, −0.82] | 437 / 174 |
| Within-partner β_int, 36-month exit, deals through 2020-10 (partner effects; no deal controls; pp) | +1.03 | [−1.57, +3.18] | 45,734 / 2,993 (367) |
| Female mean percentile shift, raw → adjusted (exit by sample end; percentile points) | +3.95 | [+1.49, +6.53] | 2,459 (174) |

*Investor types are Crunchbase's investor_types field (a firm may list several); "partner" titles are read from the people–organization job records of the attributed partner at the investing firm. Investor-firm cluster bootstrap (500) for the cell estimators, partner cluster (400) for the within-partner row, partner resampling (500) for the rank shift. Source: P001-63.*

### Appendix Table IA.9. Covariate-adjusted exit hazard and outcome battery on the peer-comparison cells (NA+EU)

## Panel A. Covariate-adjusted exit hazard on the Table 5 cells (firm × year × sector × stage × duration effects; deal controls)
| | Estimate | 95% CI |
|---|---|---|
| Annual exit hazard gap (pp/yr) | −0.240 | [−0.78, +0.34] |
| Baseline hazard (%/yr) | 6.19 | interval within ±25% of baseline: yes |
| Same gap, multi-round cell–year groups only (pp/yr); MDE80 | −1.699; 11.31 | [−11.83, +2.87]; within ±25% of baseline: no |
| Identifying base: cell–year groups with female-partner variation; share single-round co-attributions; groups with exit variation | 814; 0.89; 10 | — |

## Panel B. Outcome battery (covariate-adjusted, pp) with Romano–Wolf stepdown
| Outcome | Gap | 95% CI | Multiple-testing |
|---|---|---|---|
| fon (adj.) | +0.83 | [−1.02, +3.00] | RW p = 1.0 |
| exit_ever (adj.) | −0.77 | [−3.90, +2.52] | RW p = 0.84 |
| ipo6 (adj.) | −0.23 | [−1.97, +1.77] | RW p = 0.983 |
| acqp6 (adj.) | +0.64 | [−0.26, +2.41] | RW p = 1.0 |
| closed6 (adj.) | +1.38 | [−0.71, +3.87] | RW p = 0.693 |

Within-cell permutation (unadjusted spec): follow-on p = 0.52; exit p = 0.65.
IPO and closure margins remain unresolved (MDE80 ≈ 2.8 / 3.6 pp) rather than established nulls.

*Deal controls: round size, company age, prior rounds, syndicate size, co-investor experience (all at deal date). Identifying base of the hazard (share of cell–year groups that are co-attributions on a single round; gap on multi-round groups): Appendix Table IA.2, Panel E. The deal-fixed continuation margin is Appendix Table IA.4. Sources: P001-12, P001-13, P001-14, P001-03 (MDEs), P001-50 (identifying base).*
