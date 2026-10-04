# Plan: did the rule lengthen the longest albums? (follow-up to the 18+-track result)

Written 2026-10-03, **before any estimation** (CLAUDE.md rule 6). The author approved writing this plan; estimation waits for the author's approval of the plan itself. Nothing here changes the frozen headline in `docs/analysis_plan.md`. Every result is reported, including nulls.

## Why this follow-up, and what it can and cannot show

Among the 12 frozen-plan Part 1 checks (devlog §26), one was significant: the share of albums with 18 or more tracks rose by 4.3 points for streaming-heavy genres after the rule (Webb p = 0.012). The mean (log tracks, headline) and the share above 12 tracks did not move. One reading consistent with all three is that the incentive to add tracks (each stream of each track counts towards album units) was taken up only by a minority of releases, in the upper tail.

**Limits, stated up front.**
- The 18+ result has already been seen. Outcomes near 18 tracks are strongly correlated with it, so this follow-up **cannot independently confirm** it. It can only show whether the pattern is a single-threshold blip or a consistent shift in the upper tail.
- The same 6,775 albums are used. A fresh sample would need new data (e.g. 2020–2024 releases under a different rule regime), which is out of scope.
- Results are described as "secondary/exploratory follow-up" in the paper, whatever they show.

## Data and common conventions

As in `docs/part1_secondary_rerun_plan.md` and `docs/items4_5_plan.md`:
- **Sample:** the corrected headline sample (6,775 albums, 2009–2019, ordered genre rule, `data/final/analysis_sample.csv`).
- **Model:** `outcome ~ post:heavy + C(genre) + C(year)`.
- **Inference:** artist-clustered SEs and the genre-level restricted Webb wild bootstrap (9,999 draws, seed 20260928, `code/inference.py`).
- **Track count:** `standard_tracks`.

## A. The prespecified family (5 tests, multiplicity-adjusted)

Linear probability models for the share of albums with at least k tracks:

| # | Outcome | Note |
|---|---|---|
| A1 | ≥ 15 tracks | Just above the mass of the distribution (75th percentile overall is 14). |
| A2 | ≥ 20 tracks | Upper tail. |
| A3 | ≥ 25 tracks | Extreme tail (streaming-era "playlist albums"). |

Quantile regressions of `ln_standard_tracks`:

| # | Outcome | Note |
|---|---|---|
| A4 | 75th percentile | `statsmodels` QuantReg, same fixed effects. |
| A5 | 90th percentile | Same. |

- **Quantile inference:** QuantReg has no clustered SEs. P-values come from a pairs cluster bootstrap over artists (999 draws, seed 20260928): resample artists with replacement and re-estimate. The genre wild bootstrap is not defined for quantile regression, so it is not used there.
- **Threshold inference:** headline inference for A1–A3 (artist-clustered and Webb).
- **Multiplicity:** Holm adjustment across A1–A5, applied to the Webb p for A1–A3 and the cluster-bootstrap p for A4–A5. **Headline reading of this plan:** how many of the five survive Holm at 5%.
- The 18+ result itself is **not** in the family (already seen). It is shown alongside for reference.

## B. Supporting checks (reported, not multiplicity-adjusted, not used as evidence on their own)

1. **Distribution-regression figure.** The A1–A3 LPM coefficient for every threshold k = 8, 9, …, 30, with 95% artist-clustered intervals. This is descriptive and shows where in the distribution any shift sits.
2. **Event study for the ≥ 18 share.** Year × heavy interactions, reference year 2014, as in the headline event study, plus a joint pre-2014 test. This checks whether the 18+ gap was already opening before the rule.
3. **Who makes the long albums.** The ≥ 18 LPM separately for the charted and non-charted subsamples (the charted flag from `code/18_part1_secondary_checks.py`). This tests whether the tail shift is concentrated among acts with chart prospects, where the incentive bites.
4. **Running time of the long albums.** Among albums with all track durations, an LPM for running time ≥ 60 minutes. Many short tracks and a few long tracks are different behaviours.

## C. The two earlier exploratory leads

Shorter songs (seconds per track −3.9%, p = 0.002) and fewer same-day multi-edition launches (−5.1 points, p = 0.008) have already been estimated twice (Claude chat and devlog §25). No new estimates are planned for them. They are reported in the paper as exploratory, next to the tail result where relevant: more tracks with shorter songs is what a per-stream incentive predicts. Any further work on them needs its own plan.

## Interpretation rules, fixed now

- **≥ 2 of A1–A5 survive Holm, and the pre-2014 event-study test does not reject:** report a robust upper-tail shift, as a secondary finding next to the null headline. The paper's claim becomes "no average change, but more very long albums in streaming-heavy genres".
- **0–1 survive:** report that the 18+ result does not generalise across the upper tail and is most likely a single-threshold result. Part 1 stays a plain null.
- **Pre-2014 event-study test rejects (p < 0.05):** the tail result is treated as unreliable whatever the A results show.

## Outputs

- New script `code/26_long_albums_followup.py` (runner step after 24).
- Output `results/part1_album_length/secondary/long_albums_followup.csv`, plus the figure data.
- Logged in `docs/devlog.md`; PROJECT_CONTEXT updated.
- Expected runtime: about 30–45 minutes (three 9,999-draw Webb bootstraps and two 999-draw quantile bootstraps).

## Post-estimation notes (2026-10-03)

Added after running; the plan above is unchanged. The author approved the plan on 2026-10-03 and it was run as written (`code/26_long_albums_followup.py`, runner step 26, 43 minutes). Results and interpretation: `docs/devlog.md` section 28.
- **Verdict under the fixed rules: 0 of 5 survive Holm**, so the 18+ result does not generalise robustly across the upper tail, and Part 1 stays a plain null. The pre-2014 test does not reject (p = 0.998).
- **Smoke test:** before the full run, the script was smoke-tested with 19 bootstrap draws to check that it ran. Its point estimates were the same as the final ones; no specification was changed after it.
- **Quantile regressions on a discrete outcome:** track counts are integers, so the 75th and 90th percentiles of log tracks move in steps (one track at the 75th percentile is about 0.07 log points). The percentile intervals touch zero. This is a property of the data, noted for the write-up.
