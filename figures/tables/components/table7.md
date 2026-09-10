# Table 7. Track-record composition: size, pricing, and information content
## Panel A. Re-ranking: raw vs composition-adjusted exit rates
| | Raw → Adjusted |
|---|---|
| Female partners' mean percentile shift | +4.59 pts [+2.59, +6.86] |
| Male partners' mean percentile shift | -0.35 pts [-0.54, -0.19] |
| Female share of top quartile | 7.16% → 8.21% (Δ interval crosses zero) |
| Rank correlation (raw, adjusted) | 0.861 |

## Panel B. Subsequent attributed deal activity: log count of deals attributed to the partner in 2018–2020 on 2010–17 percentiles
| | β (log deals per unit of percentile rank, 0–1) | 95% CI |
|---|---|---|
| Adjusted percentile A, holding the raw percentile fixed (β_A) | +1.55 | [+1.27, +1.84] |
| Raw percentile R, holding A fixed (β_R) = coefficient on the rank difference R − A | -1.74 | [-2.06, -1.41] |
| Adjusted percentile A, holding the rank difference R − A fixed (β_R + β_A; same bootstrap draws) | -0.18 | [-0.31, -0.05] |

## Panel C. External outcomes among partners who move or spin out, 2017-11 to 2023-10
| Outcome | Sample | β on composition component (given adjusted percentile) | 95% CI | β with pre-period late-stage share as control | 95% CI | Late-stage share, own coefficient |
|---|---|---|---|---|---|---|
| New firm records a fund close (partners who spin out) | 379 partners; 221 raise (58.3%) | +0.506 | [+0.150, +0.847] | +0.460 | [-0.056, +1.000] | +0.206 [+0.042, +0.362] |
| log fund size recorded | 197 | +2.490 | [+0.960, +3.955] | +0.679 | [-1.383, +2.738] | +1.417 [+0.721, +2.140] |
| Receiving firm's prior attributed deal count, log(1+n) (partners who move) | 710 | +1.227 | [+0.313, +2.156] | +0.716 | [-0.802, +2.317] | +0.590 [+0.150, +1.064] |
| Joint randomization test, three outcomes (uncontrolled) | 400 permutations of the composition component | Mahalanobis 28.8 vs null 95th percentile 7.7; 3/3 signs aligned | p < 0.003 (no exceedance in 400 permutations) | | | |

## Panel D1. Does composition carry information? Open horizon (exit by sample end); post window 2017-11 to 2023-10
Rows are on the percentile scale (β on raw percentile given adjusted percentile) unless marked *levels* (β on the composition component in exit-probability units).
| Specification | β | 95% CI | n |
|---|---|---|---|
| Baseline cell benchmark | +0.091 | [+0.026, +0.151] | 2,169 |
| Leave-one-out cell benchmark | +0.096 | [+0.021, +0.164] | 2,155 |
| Excluding post-period deals in companies the partner backed pre-period | +0.081 | [+0.014, +0.147] | 1,852 |
| Composition component, levels, given tenure and first-deal-year effects | +0.075 | [-0.010, +0.160] | 2,155 |
| Composition component, levels, home-firm fixed effects | +0.088 | [-0.063, +0.270] | 1,616 |
| Decomposition of the composition component, levels: vintage / stage within year / sector within year–stage | +0.058 / +0.079 / +0.161 | [-0.112, +0.258] / [-0.028, +0.190] / [+0.016, +0.325] | 2,155 |
| Same decomposition, given tenure and first-deal-year effects | -0.054 / +0.057 / +0.155 | [-0.322, +0.183] / [-0.072, +0.166] / [+0.004, +0.312] | 2,155 |
| Contrast, levels: adjusted exit rate, same regression as the composition-component levels row | +0.331 | [+0.288, +0.382] | 2,155 |
| Contrast: adjusted percentile's own coefficient | +0.243 | [+0.207, +0.280] | 2,169 |
Remaining rows (benchmark variation and additional analyses) are in Internet Appendix Table IA.1.

## Panel D2. Same question at a fixed 36-month exit horizon in both periods (post window 2017-11 to 2020-10); levels
β on the composition component, or the named part, in 36-month exit-probability units. Partner-level rows include the adjusted rate, log deal count, gender, tenure, tenure², and first-deal-year effects unless noted. Deal-level rows include the partner's prior within-cell residual, log prior deals, gender, tenure at the deal date and its square, and year effects where no firm–year effect is present.
| Specification | β | 95% CI | n |
|---|---|---|---|
| **Composition component — preferred specification for this question** | **+0.283** | **[+0.070, +0.485]** | 2,009 |
| Sector-within-year–stage part | +0.289 | [+0.026, +0.538] | 2,009 |
| Adjusted exit rate's own coefficient, same regression as the preferred row | +0.155 | [+0.073, +0.253] | 2,009 |
| Home-firm fixed effects (minimum detectable effect 0.41; sector part 0.44) | -0.057 | [-0.318, +0.234] | 1,484 |
| Pre-period restricted to deals whose 36-month window closes before the ranking date (deals through 2014-10; minimum detectable effect 0.35) | +0.067 | [-0.162, +0.302] | 1,118 |
| Reweighted for selection out of post-period observation (inverse probability) | +0.265 | [+0.004, +0.508] | 2,009 |
| Tenure and rank from employment records (join date, title) instead of first-deal tenure; partners with a recorded join date | +0.320 | [+0.122, +0.529] | 1,781 |
| Follow-on construct instead of exit (follow-on within 36 months, both periods) | +0.044 | [-0.164, +0.233] | 2,009 |
| Deal level, within firm–year: composition component (minimum detectable effect 0.17) | +0.056 | [-0.065, +0.168] | 25,471 |
Remaining rows (benchmark variation and additional analyses) are in Internet Appendix Table IA.1.

## Panel E. By partner gender (female − male)
Percentile-scale rows are in fractions of the percentile scale (0.01 = one percentile point); *levels* rows are in exit-probability units (exit by sample end).
| Outcome | β | 95% CI | n |
|---|---|---|---|
| Composition component (raw − adjusted percentile) | -0.050 | [-0.075, -0.027] | 2,680 |
| Composition component, leave-one-out benchmark | -0.051 | [-0.080, -0.024] | 2,654 |
| Post-period within-cell performance, levels | -0.004 | [-0.040, +0.034] | 2,169 |
| Post-period within-cell performance, levels, given composition | -0.006 | [-0.043, +0.036] | 2,169 |
| Pre-period within-cell performance, levels (adjusted exit rate) | +0.013 | [-0.019, +0.049] | 2,680 |
| Composition component, levels | -0.041 | [-0.063, -0.018] | 2,654 |
| Composition component, levels, given tenure and first-deal-year effects | -0.016 | [-0.033, +0.002] | 2,654 |
| Vintage / stage-within-year / sector-within-year–stage parts, levels | -0.018 / -0.015 / -0.007 | [-0.029, -0.009] / [-0.029, -0.001] / [-0.016, +0.001] | 2,654 |
| Composition component, levels, given employment-record tenure and rank | -0.020 | [-0.040, +0.000] | 2,327 |
| Composition component, levels, given rank only | -0.039 | [-0.064, -0.013] | 2,327 |
| Implied contribution of composition to the post-period gap, levels, open horizon (Σ tenure-controlled part gap × tenure-controlled coefficient, same resamples; materiality band ±0.02; interval inside ±0.01) | -0.0014 | [-0.0047, +0.0008] | 2,155 |
| Same, fixed 36-month exit horizon (post window to 2020-10) | -0.0006 | [-0.0047, +0.0041] | 2,009 |

*Partners with ≥5 attributed deals through 2017-10: 2,680 (191 women). Panels B–E: deal-count and gender controls (Panel B additionally pre-period early-stage share and sector breadth); investor-firm cluster bootstrap. Because the adjusted percentile is the raw percentile net of year–sector–stage cell benchmarks, the raw-percentile coefficient given the adjusted percentile equals the coefficient on their difference, the composition component (percentile correlation 0.8613, VIF 7.3); Panel B's negative value is that composition coefficient. Panel D1 and Panel E percentile-scale rows: β per unit of the raw percentile (0.01 = one percentile point); *levels* rows: β per unit of the composition component in exit-probability units. Panel D2's control set is stated in its header; the follow-on-construct row reproduces P001-30 (a separate bootstrap in P001-33 returns the same point). Panel D2 rows below the preferred row are additional analyses. † Exploratory: identifies off within-partner changes in composition over time rather than off placement across partners; clustered by partner. Sources: P001-05, P001-18b, P001-23, P001-25, P001-26, P001-27, P001-28, P001-29, P001-30, P001-31, P001-33, P001-34, P001-36, P001-38, P001-39.*
