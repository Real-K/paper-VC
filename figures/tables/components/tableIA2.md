# Appendix Table IA.2. Robustness and measurement diagnostics
## Panel A. Sector-layer matching coefficient across specifications (rows re-estimated in a separate bootstrap run; the canonical baseline interval is Table 2)
| Row | Estimate (pp) | 95% CI | n |
|---|---|---|---|
| baseline | +3.22 | [+1.83, +4.51] | 126,128 |
| T1_ff_majority | +2.98 | [+1.85, +4.21] | 126,128 |
| T1_ff_solo | +1.13 | [+0.51, +1.77] | 126,128 |
| T2_solo_attr | +3.61 | [-0.82, +12.16] | 35,193 |
| T4_profile_rich | +3.63 | [+2.17, +5.19] | 104,232 |
| T5_cluster_partner | +3.22 | [+2.09, +4.21] | 126,128 |
| T5_cluster_org | +3.22 | [+2.07, +4.40] | 126,128 |
| stage layer, generic labels excluded | +0.56 | [-0.71, +2.12] | 113,940 |

## Panel B. Covariate-adjusted follow-on estimates across specifications
| Row | Estimate (pp) | 95% CI | n |
|---|---|---|---|
| baseline | +1.01 | [-1.46, +3.82] | 13,116 |
| T1_ff_majority | +0.58 | [-2.09, +2.94] | 8,216 |
| T2_solo_attr | +7.18 | [-50.00, +12.17] | 4,101 |
| T3_fon24 | +1.39 | [-1.88, +4.19] | 16,646 |
| T4_profile_rich | +2.50 | [-0.43, +6.27] | 10,722 |
| T5_cluster_partner | +1.01 | [-0.82, +2.87] | 13,116 |

## Panel C. Measurement diagnostics
| | |
|---|---|
| Firm attribution rate ~ female-partner share (correlation) | -0.022 [-0.042, +0.000] |
| Attribution × gender drift correlation (annual) | -0.061 |
| Deal-level salience fingerprint: FF × firm FP-share → P(attributed) | +2.45pp [+0.43, +4.34] (varies within firms with the deal's founder gender, so it is not absorbed by firm fixed effects; Appendix IA.2) |
| Generic stage-label share: FP / MP deals | 8.6% / 9.8% |
| Founder-gender determinable vs not: US / early / vintage | +27.6pp / -16.6pp / -1.92y |

## Panel D. Rank-measure diagnostics and external-pricing sensitivity
| | |
|---|---|
| Raw vs adjusted percentile: correlation / VIF / share of raw variation independent of controls | 0.8613 / 7.31 / 13.7% |
| Raw percentile alone → mobility; → spinout | +0.045 [-0.023, +0.119]; +0.034 [-0.017, +0.089] |
| Adjusted percentile alone → mobility; → spinout | +0.054 [-0.002, +0.119]; +0.061 [+0.017, +0.106] |
| Out-of-sample AUC (5-fold), raw minus adjusted: mobility; spinout | -0.0036; -0.0145 |
| Composition → fund formation: with pre-period early-stage share and sector breadth as controls / without | +0.393 [-0.141, +0.849] / +0.506 [+0.150, +0.847] |
| Composition → receiving-firm quality: with / without | +1.100 [-0.371, +2.375] / +1.227 [+0.313, +2.156] |
| Post-period observation ← composition component (LPM; percentile-point units) | -0.432 [-0.528, -0.324]; n = 2,654 |
| Post-period observation ← vintage / stage-within-year / sector-within-year–stage components (levels) | -2.183 [-2.403, -1.935] / +0.361 [+0.150, +0.564] / +0.108 [-0.141, +0.333] |
| Post-period observation ← tenure (years since first attributed deal), given components | +0.0299 [+0.0040, +0.0771] |
| Composition → log fund size: with pre-period late-stage share as control / late-stage share own coefficient | +0.679 [-1.383, +2.738] / +1.417 [+0.721, +2.140] |
| Log fund size ← stage part / ← sector part given late-stage share / ← sector part given late-stage share and tenure | +5.535 [+2.659, +8.311] / +2.787 [+0.173, +5.601] / +2.596 [-0.892, +5.378]; n = 196 |
| Fund formation ← sector part given late-stage share and tenure | +0.292 [-0.543, +1.066]; n = 377 |
| Minimum detectable effects (80% power), composition component / sector part: open-horizon home-firm FE; fixed-horizon home-firm FE; deal-level firm–year FE | 0.238 / 0.328; 0.407 / 0.437; 0.170 / 0.179 |
| Three-part multiplicity adjustment (maximum absolute t) of the open-horizon sector part: two-sided p, adjusted / unadjusted | 0.135 / 0.048 |
| Within-firm share of variance in the home-firm FE sample: composition component / sector part | 0.33 / 0.62 |
| Mundlak decomposition, open horizon, within-firm / between-firm coefficient: sector part | +0.136 [-0.085, +0.355] / +0.173 [-0.036, +0.397] |
| Same, composition component | +0.115 [-0.017, +0.276] / +0.061 [-0.031, +0.163] | 
| Same, composition component, within-minus-between contrast | +0.054 [-0.087, +0.216] |
| Mundlak decomposition, fixed 36-month exit horizon, within-firm / between-firm / contrast: composition component | -0.024 [-0.280, +0.250] / +0.447 [+0.196, +0.727] / -0.471 [-0.854, -0.106]; n = 2,009 |
| Same, adding the home firm's fund count, cumulative fund size and fund age at the sample split (Crunchbase funds; SEC Form D tier-1 filings): between-firm coefficient / contrast; R² of the firm-mean composition on those variables | +0.438 [+0.143, +0.688] / -0.464 [-0.807, -0.082]; R² 0.058 |
| Same, sector part | +0.011 [-0.291, +0.284] / +0.505 [+0.151, +0.890] / -0.494 [-0.954, -0.074] |
| Follow-on vs exit benchmarks: weighted correlation of year–sector–stage cell means (follow-on, 36-month exit) / (follow-on, exit by sample end); range of stage-level rates excluding private equity, follow-on / 36-month exit | -0.24 / -0.03; 0.187 / 0.279 |
| Employment-record tenure: share of partners with a home-firm join date / correlation with first-deal tenure / share attributed before the recorded join date / female−male tenure difference (years) | 0.877 / +0.65 / 0.293 / -1.61 |
| Standardized coefficients in one regression, composition component / adjusted rate: fixed horizon with tenure controls; open horizon | +0.084 / +0.084; +0.053 / +0.298 |
| Split-half agreement at the fixed horizon (upper bound on reliability): sector part / composition component / adjusted rate | 0.49 / 0.61 / 0.47 |
| 36-month exit: share of positives recorded before the deal date, pre / post; post-period base rate with those excluded | 0.000 / 0.000; 0.1388 |
| Post-period observation ← vintage part / employment-record tenure, given components and rank | -2.370 [-2.695, -2.052] / +0.0125 [+0.0055, +0.0203]; n = 2,327 |
| Share of the fixed-horizon partner sample observed in the post period | 0.757 |
| Pre-period deals entering the fixed-horizon panel whose 36-month window closes after the ranking date / whose outcome is undetermined at that date | 0.467 / 0.399 |
| Correlation of tenure (years since first attributed deal) with the composition component, open horizon | 0.52 |
| Deal-level firm–year FE sample: deals / firms | 25,471 / 658 |
| Fixed-horizon Mundlak: correlation of firm-mean composition with firm-mean adjusted rate / partners who are the only sampled partner at their firm | +0.117 / 434 of 2,009 |
| Identifying variation of the Table 3 peer comparison (firm × year × sector), NA+EU / global: cells with both partner genders among FF deals / deals in them / share of FF deals | 173 / 427 / 0.060; 190 / 475 / 0.059 |
| Peer availability, NA+EU: share of female-partner FF deals with a same-cell male-partner FF deal / female partners with at least one such deal (of 323) / same share across all deals | 0.236 / 89 / 0.419 |
| Peer-comparison estimate re-estimated on the mixed cells only, NA+EU / global (pp) | -4.47 / -6.19 (identical to the full-sample estimates) |
| Leave-one-cell-out jackknife of the peer-comparison estimate: maximum shift (pp), NA+EU / global; any value outside the bootstrap interval | 0.72 / 0.64; no |
| Within-cell random reassignment of partner gender (400 draws): 95th percentile of the absolute estimate (pp), NA+EU / global; share of draws at or beyond the estimate | 5.51 / 4.61; 0.115 / 0.025 |
| Same for the + stage cells, NA+EU: cells / deals / placebo 95th percentile / share at or beyond | 154 / 333 / 3.28 / 0.635 |
| Deal level, fixed horizon, without the partner's prior within-cell residual as a control — within firm–year: sector part / composition component; pooled: sector part | +0.037 [-0.123, +0.163] / +0.037 [-0.102, +0.161]; +0.162 [+0.056, +0.254] |
| Deal level, open-horizon construct (exit by sample end), within firm–year: sector part | +0.002 [-0.155, +0.167]; n = 33,441 |
| Split-half agreement (Spearman–Brown; halves share cell benchmarks, so an upper bound on reliability): vintage / stage / sector parts / composition component / adjusted rate | 0.97 / 0.87 / 0.46 / 0.84 / 0.59 |
| Fixed exit horizon: standard deviation of the vintage part / standardized composition coefficient (sd units) | 0.0152 / +0.084 |
| Deal-level sample: firm–years with ≥ 2 partners / share of post-period deals in companies the partner backed pre-period (fixed-horizon window) | 2,391 / 0.218 |
| Spinout population counts, leave-one-out partner sample: spinouts / fund close observed / fund size observed | 377 / 220 / 196 (Table 7 Panel C uses the baseline-benchmark sample: 380 / 221 / 197) |

## Panel E. Region split and the identifying base of the peer comparison
| | United States | North America (US + Canada) | Europe (24 countries) |
|---|---|---|---|
| Peer-comparison exit gap, firm × year × sector (pp); mixed cells / deals | -4.02 [-10.35, +1.41]; 144 / 349 | -4.60 [-11.95, +1.13]; 145 / 351 | not computable (within-cell exit variation zero); 27 / 63 |
| Within-cell reassignment placebo, 95th percentile of \|β\| (pp) | 5.69 | 5.81 | — |
| + stage cell gap (pp) | -1.02 [-5.36, +3.17] | -1.02 [-4.93, +3.04] | not computable |
| Follow-on within 36 months, + stage cell, FP coefficient (pp) | +0.76 [-2.56, +4.11] | +0.76 [-2.89, +4.62] | not computable |
| Fixed-horizon composition coefficient (Table 7 Panel D2 preferred specification); partners | +0.189 [-0.017, +0.401]; 2,075 | +0.229 [+0.004, +0.435]; 2,155 | +0.295 [+0.083, +0.579]; 461 |

| Identifying base of the Table 3 peer comparison | NA+EU, firm × year × sector | NA+EU, + stage | Global, firm × year × sector |
|---|---|---|---|
| Mixed cells that are co-attributions on a single round (share) | 112 (0.65) | 134 (0.87) | 119 (0.63) |
| Cells with within-cell exit variation / deals in them | 30 / 100 | 8 / 18 | 35 / 119 |
| Share of identifying variance (Σx̃²) from single-round cells | 0.57 | 0.85 | 0.55 |
| Exit gap on multi-round cells only (pp); MDE; placebo 95th percentile | -10.49 [-22.19, +1.50]; 17.73; 12.83 | -5.52 [-26.76, +20.50]; 32.4; 22.07 | -13.69 [-24.59, -2.32]; 15.73; 12.11 |
| Follow-on gap on multi-round cells only (pp) | -1.29 [-9.95, +7.27] | +4.14 [-11.34, +24.63] | -2.25 [-11.72, +7.18] |

| Identifying base of the Table 4 hazard (cell × elapsed-year effects) | Value |
|---|---|
| Cells with female-partner variation / rows; share that are co-attributions on a single round | 814 / 1,764; 0.89 |
| Cells with within-cell exit variation (share); exit events in them | 10 (0.01); 12 |
| Share of identifying variance from single-round cells | 0.87 |
| Annual hazard gap, all cells, re-estimated in this audit run with its own bootstrap (pp/yr; the reference estimate is Table 5, Panel A); within ±25% of the 6.19% base | -0.244 [-1.00, +0.31]; yes |
| Annual hazard gap, multi-round cells only (pp/yr); MDE; within ±25% of base | -1.699 [-11.83, +2.87]; 11.31; no |

*Panel A 'baseline' re-estimates the Table 2 sector layer inside the robustness battery (separate bootstrap run; point identical, interval differs by resampling). Panel D: composition-component coefficients are in exit-probability units per unit of the component (0.01 of the percentile scale = one percentile point) unless a row states percentile-point units; fund-size coefficients are log points per unit of the component. Sources: P001-07, P001-08, P001-16, P001-22, P001-23, P001-25, P001-28, P001-29, P001-30, P001-31, P001-32, P001-33, P001-34, P001-35, P001-37, P001-38, P001-39, P001-40, P001-41, P001-48, P001-49, P001-50. Solo-attribution rows lose precision (negative_results/W4_notes.md); points consistent with baselines.*
