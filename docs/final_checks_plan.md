# Plan: Part 1 equivalence bound, Part 2b leave-one-genre-out, Part 2 event-study plot

Written 2026-10-03, **before any estimation** (CLAUDE.md rule 6). The author approved running these three immediately after the plan. Nothing here changes any frozen specification. Every result is reported.

## 1. What the Part 1 null rules out (equivalence)

- **Estimate:** the frozen Part 1 headline (+0.0228 log points, artist-clustered SE 0.0151; 6,775 albums). Already known, so this section only re-expresses it; no new estimate.
- **Reported:**
  - the 90% confidence interval;
  - the **smallest equivalence bound rejected at 5%** by two one-sided tests (TOST), i.e. |b| + 1.645·SE. This needs no choice of bound;
  - the minimum detectable effect at 80% power and 5% two-sided (2.80·SE).
  - All three are converted to tracks at the sample's mean album length.
- **Prespecified bound:** half a track. In conversation the agent said the design could detect "about half a track"; that was stated before this calculation. TOST is run at δ = ln((m + 0.5)/m), with m the mean track count, and the result is reported whether it passes or fails.
- **Inference:** artist-clustered SE, normal critical values. The genre-level wild bootstrap does not give a standard error, so it is not used for the bound. This is noted.

## 2. Part 2b with each genre left out

- **Sample and model:** the reported Part 2b sample (`data/final/part2b_album_runs.csv`, 4,517 albums), `weeks52 ~ post:heavy + C(genre) + C(year)`, artist-clustered SEs. Re-estimated 9 times, dropping one genre each time.
- **Inference:** the Part 2b script's own genre wild bootstrap: restricted, Webb weights, genre-clustered t-statistics, 9,999 draws, seed 20260928. The function is copied verbatim from `code/22_part2b_analyze.py` so the method matches the reported p = 0.015. With 8 genre clusters left, bootstrap p-values are coarse; reported as they come.
- **Interpretation rule (fixed now):** Part 2b is "not driven by a single genre" if all nine estimates are positive and the smallest is at least half the full-sample estimate (≥ 1.61 weeks). Otherwise the paper names the genre whose removal moves the estimate below that bar.

## 3. Event-study plot for the Part 2 jump (descriptive)

- **Series:** U.S. weekly new-entry and 52+-week shares (Part 2 series), 24 months either side of the rule. The same for the UK around its own rule date, as a comparison panel.
- **Model:** each weekly share on dummies for months relative to the rule (−24 … +24; the month before the rule is the reference) plus week-of-year effects, Newey–West SEs (12 lags). Coefficients plotted with 95% intervals.
- **Use:** a figure only. No test or p-value from it is used for any verdict.

## Outputs

- Script `code/32_final_checks.py` (runner step 32).
- Results `results/final_checks/`: `equivalence.csv`, `part2b_leave_one_genre_out.csv`, `event_study_monthly.csv`, `fig_event_study.png`.
- Devlog section and PROJECT_CONTEXT update.

## Post-estimation notes (2026-10-03)

Added after running; the plan above is unchanged.
- **Deviation in section 3 (figure only).** As specified (only the +-24-month window, month dummies plus week-of-year effects), the month dummies and week-of-year effects are not separately identified with four years of data. The first plot showed a repeating 12-month sawtooth. Replaced by the standard fix: the full 2010-2019 series, with months outside +-24 grouped in two end bins (<= -25, >= +24), so the seasonal effects are identified from the years outside the window. No test or verdict uses the figure.
- **Check on the copied bootstrap (section 2):** the full-sample run reproduces the reported Part 2b bootstrap p = 0.015 exactly.
- **Equivalence:** the prespecified half-track bound fails (TOST p = 0.16), as reported below and in devlog section 34.
