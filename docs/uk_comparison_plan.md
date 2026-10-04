# Plan: UK Official Albums Chart as a cross-country comparison for Part 2

Written 2026-10-03, **before any estimation** (CLAUDE.md rule 6). Awaiting the author's approval. Nothing here changes the frozen Part 1 plan or the Part 2 plan (`docs/q1_analysis_plan.md`). Every result is reported, including nulls.

## Why

Part 2's main limitation is that it has one treated series: the Billboard 200 jumps toward incumbents at December 2014, but streaming was growing at the same time (RIAA: streaming share of U.S. revenue 23% in 2013, 31% in 2014, 38% in 2015, a smooth trend). The UK Official Albums Chart added streams on a **different date**: the first chart including streams was published Sunday **1 March 2015** (Official Charts Company announcement; sheet "Week 20150301" in the data).

If the chart rule causes the incumbency shift, each chart should break at **its own** rule date:
- the UK at March 2015, and not at December 2014;
- the U.S. at December 2014, with no further break at March 2015.

A common streaming shock would instead move both markets together. Between December 2014 and March 2015 the U.S. chart counts streams and the UK chart does not, which is the comparison window.

## Data

- **UK:** `data/final/uk_albums_weekly.csv` (step 28): Official Albums Chart top 100, weekly, 2000–2025, with the #1 rows rebuilt (they are missing from the author's workbook; method in the script docstring; all 522 weeks of 2010–2019 complete).
- **U.S.:** the Part 2 weekly Billboard 200 series (`data/final/part2_weekly_billboard200.csv`, step 20).
- **Window:** chart weeks 2010–2019, as in Part 2. U.S. dates use the Kaggle stored dates (rule = 2014-12-10). UK dates are the Sunday the chart week starts (rule = 2015-03-01).

## Outcomes (as in Part 2)

1. **New-entry share:** share of chart slots held by albums in their first week on the chart (UK "LW:New").
2. **52+-week share:** share held by albums with 52 or more weeks on chart (cumulative, re-entries included, as in Billboard's count).

Both are shares of the chart's slots: 200 for the U.S. and 100 for the UK. For comparability, the U.S. series is **also** computed on positions 1–100 as a secondary version.

## Main tests

**A. UK break at its own rule.** The Part 2 interrupted-time-series model on the UK series:

`Y_t = a + b*t + tau*Post_t + d*(t - t0)*Post_t + week-of-year FE + e_t`

with t0 = 2015-03-01 and Newey-West SEs (12 lags). The parameter is tau (the immediate jump), as in Part 2.

**B. UK placebo at the U.S. date.** Same model on the UK series with t0 = 2014-12-07 (the UK chart week containing the first U.S. rule chart). The UK did not change its rule then, so a jump here would point to a common shock. Prediction: tau near 0.

**C. Pooled two-country test.** Stack the two weekly series (2 x 522 weeks). Each country gets its own intercept, trend and week-of-year effects, plus a jump at **each** of the two dates. The coefficients of interest:
- tau_own: the average jump of a country at its own rule date (main parameter);
- tau_other: the average jump at the other country's date (placebo, prediction 0).

The test of the design is tau_own > 0 and tau_own − tau_other > 0. SEs: Newey-West (12 lags) by country, combined (Driscoll–Kraay with 12 lags as a check).

**D. Placebo-date distribution.** Part 2 found that significant trend changes also appear at fake dates, so nominal p-values overstate certainty. For each country and outcome, re-estimate tau at every fake date from 2011-01 to 2018-12, excluding 26 weeks either side of either true date. Report the rank of the true-date |tau| in that distribution as a randomisation-style p-value. **This is the p-value used for interpretation.**

## Interpretation rules, fixed now

- **Rule effect supported:** in A the UK shows a jump in the same direction as the U.S. (new-entry share down, 52+ share up), with placebo-rank p < 0.10; B is small and not significant; and in C tau_own exceeds tau_other.
- **Common shock indicated:** jumps of similar size appear at the U.S. date in both countries (B significant), or the UK does not break at its own date.
- **Inconclusive:** anything else, reported as such.

## Known differences and caveats (stated now)

- **Different rule details.** The UK counts the 12 most-streamed tracks, with the top two down-weighted, at 1,000 streams per album. Billboard counted 1,500 streams per album with no cap at the time. The direction of the predicted effect is the same; the magnitudes need not be.
- **Smaller chart.** The UK top 100 is half the size of the Billboard 200 and catalogue-heavy in both countries.
- **Other UK rule changes.** Any other UK albums-chart rule changes within 2010–2019 (for example, later changes to streaming weights) must be **verified from Official Charts Company sources before estimation** and listed in a dated note; they are not modelled unless the author decides otherwise.
- **The UK Christmas peak** is handled by week-of-year effects, as in the U.S.
- **Compilations** have had their own UK chart since 1989, so they are not on the albums chart. Billboard 200 rules on compilations differ; noted, not adjusted.

## Outputs

- New script `code/29_uk_comparison.py` (runner step after 28).
- Output `results/part2_incumbency/uk_comparison.csv`, plus the placebo distribution and a weekly series figure.
- Logged in `docs/devlog.md`; PROJECT_CONTEXT updated.
