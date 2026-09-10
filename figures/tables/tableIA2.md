# Appendix Table IA.2. Robustness and measurement diagnostics
## Panel A. Sector-layer matching coefficient across specifications (rows re-estimated in a separate bootstrap run; the canonical baseline interval is Table 2)
| Row | Estimate (pp) | 95% CI | n |
|---|---|---|---|
| baseline | +3.21 | [+1.79, +4.54] | 127,061 |
| T1_ff_majority | +2.98 | [+1.78, +4.43] | 127,061 |
| T1_ff_solo | +1.13 | [+0.48, +1.91] | 127,061 |
| T2_solo_attr | +3.40 | [-1.36, +11.17] | 35,587 |
| T4_profile_rich | +3.62 | [+2.10, +5.17] | 104,854 |
| T5_cluster_partner | +3.21 | [+2.07, +4.42] | 127,061 |
| T5_cluster_org | +3.21 | [+2.09, +4.29] | 127,061 |
| stage layer, generic labels excluded | +0.59 | [-0.53, +1.91] | 114,658 |

## Panel B. Covariate-adjusted follow-on estimates across specifications
| Row | Estimate (pp) | 95% CI | n |
|---|---|---|---|
| baseline | +1.08 | [-1.42, +3.48] | 13,187 |
| T1_ff_majority | +0.58 | [-1.72, +3.49] | 8,255 |
| T2_solo_attr | +7.18 | [-42.86, +12.25] | 4,133 |
| T3_fon24 | +1.33 | [-1.60, +4.35] | 16,737 |
| T4_profile_rich | +2.50 | [-0.43, +6.50] | 10,780 |
| T5_cluster_partner | +1.08 | [-0.81, +3.13] | 13,187 |

## Panel C. Measurement diagnostics
| | |
|---|---|
| Firm attribution rate ~ female-partner share (correlation) | -0.023 [-0.044, -0.002] |
| Attribution × gender drift correlation (annual) | -0.048 |
| Deal-level salience fingerprint: FF × firm FP-share → P(attributed) | +2.46pp [+0.70, +4.44] (≈0.4pp per sd; absorbed by firm FE) |
| Generic stage-label share: FP / MP deals | 8.7% / 9.9% |
| Founder-gender determinable vs not: US / early / vintage | +28.2pp / -17.8pp / -1.94y |

## Panel D. Rank-measure diagnostics and external-pricing sensitivity
| | |
|---|---|
| Raw vs adjusted percentile: correlation / VIF / share of raw variation independent of controls | 0.8614 / 7.37 / 13.6% |
| Raw percentile alone → mobility; → spinout | +0.049 [-0.015, +0.123]; +0.035 [-0.022, +0.088] |
| Adjusted percentile alone → mobility; → spinout | +0.057 [+0.001, +0.113]; +0.062 [+0.022, +0.102] |
| Out-of-sample AUC (5-fold), raw minus adjusted: mobility; spinout | -0.0040; -0.0083 |
| Composition → fund formation: with pre-period early-stage share and sector breadth as controls / without | +0.374 [-0.093, +0.810] / +0.494 [+0.143, +0.862] |
| Composition → receiving-firm quality: with / without | +1.047 [-0.233, +2.474] / +1.201 [+0.362, +2.244] |
| Post-period observation ← composition component (LPM; percentile-point units) | -0.425 [-0.535, -0.307]; n = 2,661 |
| Post-period observation ← vintage / stage-within-year / sector-within-year–stage components (levels) | -2.188 [-2.417, -1.972] / +0.379 [+0.198, +0.585] / +0.082 [-0.164, +0.299] |
| Post-period observation ← tenure (years since first attributed deal), given components | +0.0283 [+0.0022, +0.0754] |
| Composition → log fund size: with pre-period late-stage share as control / late-stage share own coefficient | +0.662 [-1.577, +2.964] / +1.423 [+0.756, +2.201] |
| Log fund size ← stage part / ← sector part given late-stage share / ← sector part given late-stage share and tenure | +5.639 [+2.994, +8.312] / +2.777 [+0.045, +5.655] / +2.580 [-0.643, +5.611]; n = 196 |
| Fund formation ← sector part given late-stage share and tenure | +0.250 [-0.564, +1.020]; n = 378 |
| Minimum detectable effects (80% power), composition component / sector part: open-horizon home-firm FE; fixed-horizon home-firm FE; deal-level firm–year FE | 0.226 / 0.344; 0.379 / 0.401; 0.164 / 0.187 |
| Three-part multiplicity adjustment (maximum absolute t) of the open-horizon sector part: two-sided p, adjusted / unadjusted | 0.133 / 0.045 |
| Within-firm share of variance in the home-firm FE sample: composition component / sector part | 0.33 / 0.62 |
| Mundlak decomposition, open horizon, within-firm / between-firm coefficient: sector part | +0.131 [-0.096, +0.349] / +0.170 [-0.042, +0.395] |
| Same, composition component | +0.119 [-0.026, +0.279] / +0.061 [-0.038, +0.148] | 
| Same, composition component, within-minus-between contrast | +0.058 [-0.098, +0.216] |
| Mundlak decomposition, fixed 36-month exit horizon, within-firm / between-firm / contrast: composition component | -0.018 [-0.293, +0.221] / +0.435 [+0.177, +0.694] / -0.453 [-0.786, -0.130]; n = 2,017 |
| Same, adding the home firm's fund count, cumulative fund size and fund age at the sample split (Crunchbase funds; SEC Form D tier-1 filings): between-firm coefficient / contrast; R² of the firm-mean composition on those variables | +0.428 [+0.154, +0.664] / -0.447 [-0.760, -0.049]; R² 0.060 |
| Same, sector part | +0.044 [-0.234, +0.316] / +0.508 [+0.167, +0.848] / -0.464 [-0.874, -0.037] |
| Follow-on vs exit benchmarks: weighted correlation of year–sector–stage cell means (follow-on, 36-month exit) / (follow-on, exit by sample end); range of stage-level rates excluding private equity, follow-on / 36-month exit | -0.26 / -0.04; 0.193 / 0.279 |
| Employment-record tenure: share of partners with a home-firm join date / correlation with first-deal tenure / share attributed before the recorded join date / female−male tenure difference (years) | 0.877 / +0.65 / 0.293 / -1.55 |
| Standardized coefficients in one regression, composition component / adjusted rate: fixed horizon with tenure controls; open horizon | +0.083 / +0.098; +0.057 / +0.300 |
| Split-half agreement at the fixed horizon (upper bound on reliability): sector part / composition component / adjusted rate | 0.50 / 0.62 / 0.47 |
| 36-month exit: share of positives recorded before the deal date, pre / post; post-period base rate with those excluded | 0.028 / 0.048; 0.1384 |
| Post-period observation ← vintage part / employment-record tenure, given components and rank | -2.380 [-2.702, -2.079] / +0.0126 [+0.0052, +0.0195]; n = 2,333 |
| Share of the fixed-horizon partner sample observed in the post period | 0.758 |
| Pre-period deals entering the fixed-horizon panel whose 36-month window closes after the ranking date / whose outcome is undetermined at that date | 0.467 / 0.398 |
| Correlation of tenure (years since first attributed deal) with the composition component, open horizon | 0.52 |
| Deal-level firm–year FE sample: deals / firms | 25,600 / 661 |
| Fixed-horizon Mundlak: correlation of firm-mean composition with firm-mean adjusted rate / partners who are the only sampled partner at their firm | +0.121 / 434 of 2,017 |
| Identifying variation of the Table 3 peer comparison (firm × year × sector), NA+EU / global: cells with both partner genders among FF deals / deals in them / share of FF deals | 174 / 430 / 0.060; 191 / 478 / 0.059 |
| Peer availability, NA+EU: share of female-partner FF deals with a same-cell male-partner FF deal / female partners with at least one such deal (of 326) / same share across all deals | 0.237 / 90 / 0.419 |
| Peer-comparison estimate re-estimated on the mixed cells only, NA+EU / global (pp) | -4.55 / -6.25 (identical to the full-sample estimates) |
| Leave-one-cell-out jackknife of the peer-comparison estimate: maximum shift (pp), NA+EU / global; any value outside the bootstrap interval | 0.72 / 0.64; no |
| Within-cell random reassignment of partner gender (400 draws): 95th percentile of the absolute estimate (pp), NA+EU / global; share of draws at or beyond the estimate | 5.54 / 5.36; 0.100 / 0.025 |
| Same for the + stage cells, NA+EU: cells / deals / placebo 95th percentile / share at or beyond | 155 / 336 / 2.64 / 0.540 |
| Deal level, fixed horizon, without the partner's prior within-cell residual as a control — within firm–year: sector part / composition component; pooled: sector part | +0.043 [-0.096, +0.173] / +0.039 [-0.096, +0.149]; +0.177 [+0.065, +0.274] |
| Deal level, open-horizon construct (exit by sample end), within firm–year: sector part | +0.002 [-0.155, +0.162]; n = 33,611 |
| Split-half agreement (Spearman–Brown; halves share cell benchmarks, so an upper bound on reliability): vintage / stage / sector parts / composition component / adjusted rate | 0.97 / 0.87 / 0.47 / 0.84 / 0.59 |
| Fixed exit horizon: standard deviation of the vintage part / standardized composition coefficient (sd units) | 0.0147 / +0.083 |
| Deal-level sample: firm–years with ≥ 2 partners / share of post-period deals in companies the partner backed pre-period (fixed-horizon window) | 2,402 / 0.218 |
| Spinout population counts, leave-one-out partner sample: spinouts / fund close observed / fund size observed | 378 / 220 / 196 (Table 7 Panel C uses the baseline-benchmark sample: 380 / 221 / 197) |

## Panel E. Region split and the identifying base of the peer comparison
| | United States | North America (US + Canada) | Europe (24 countries) |
|---|---|---|---|
| Peer-comparison exit gap, firm × year × sector (pp); mixed cells / deals | -4.12 [-10.71, +1.99]; 145 / 352 | -4.69 [-11.84, +1.32]; 146 / 354 | not computable (within-cell exit variation zero); 27 / 63 |
| Within-cell reassignment placebo, 95th percentile of \|β\| (pp) | 5.53 | 5.9 | — |
| + stage cell gap (pp) | -1.26 [-5.67, +2.60] | -1.26 [-5.26, +2.99] | not computable |
| Follow-on within 36 months, + stage cell, FP coefficient (pp) | +1.01 [-2.14, +5.13] | +1.01 [-2.05, +5.15] | not computable |
| Fixed-horizon composition coefficient (Table 7 Panel D2 preferred specification); partners | +0.190 [-0.018, +0.377]; 2,079 | +0.242 [+0.036, +0.480]; 2,158 | +0.363 [+0.121, +0.583]; 464 |

| Identifying base of the Table 3 peer comparison | NA+EU, firm × year × sector | NA+EU, + stage | Global, firm × year × sector |
|---|---|---|---|
| Mixed cells that are co-attributions on a single round (share) | 113 (0.65) | 135 (0.87) | 120 (0.63) |
| Cells with within-cell exit variation / deals in them | 30 / 101 | 8 / 19 | 35 / 120 |
| Share of identifying variance (Σx̃²) from single-round cells | 0.58 | 0.85 | 0.55 |
| Exit gap on multi-round cells only (pp); MDE; placebo 95th percentile | -10.71 [-21.72, +2.07]; 17.51; 12.67 | -6.80 [-25.40, +17.23]; 30.7; 23.13 | -13.87 [-24.77, -2.50]; 15.73; 11.89 |
| Follow-on gap on multi-round cells only (pp) | -1.17 [-11.25, +7.00] | +5.44 [-11.37, +27.80] | -2.15 [-11.54, +7.18] |

| Identifying base of the Table 4 hazard (cell × elapsed-year effects) | Value |
|---|---|
| Cells with female-partner variation / rows; share that are co-attributions on a single round | 814 / 1,764; 0.89 |
| Cells with within-cell exit variation (share); exit events in them | 10 (0.01); 12 |
| Share of identifying variance from single-round cells | 0.87 |
| Annual hazard gap, all cells, re-estimated in this audit run with its own bootstrap (pp/yr; the reference estimate is Table 5, Panel A); within ±25% of the 6.19% base | -0.244 [-1.00, +0.31]; yes |
| Annual hazard gap, multi-round cells only (pp/yr); MDE; within ±25% of base | -1.699 [-11.83, +2.87]; 11.31; no |

*Panel A 'baseline' re-estimates the Table 2 sector layer inside the robustness battery (separate bootstrap run; point identical, interval differs by resampling). Panel D: composition-component coefficients are in exit-probability units per unit of the component (0.01 of the percentile scale = one percentile point) unless a row states percentile-point units; fund-size coefficients are log points per unit of the component. Sources: P001-07, P001-08, P001-16, P001-22, P001-23, P001-25, P001-28, P001-29, P001-30, P001-31, P001-32, P001-33, P001-34, P001-35, P001-37, P001-38, P001-39, P001-40, P001-41, P001-48, P001-49, P001-50. Solo-attribution rows lose precision (negative_results/W4_notes.md); points consistent with baselines.*
