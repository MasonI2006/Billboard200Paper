# paperwriting/

Materials for writing the paper. Created 2026-10-03.

| File | What it is | How it is made |
|---|---|---|
| `plain_language_guide.md` | Plain-English walk-through: research questions, the parameters, every decision and test in the paper, bugs, what can and can't be claimed, likely referee questions, glossary | Hand-written |
| `paper_outline.md` | Section-by-section outline: core claims, abstract skeleton, which figure/table/number goes where, appendix plan, checklist | Hand-written |
| `test_registry.md` | Every test mapped to its plan, status (frozen primary, prespecified, follow-up, exploratory, descriptive, post hoc), result, devlog section and suggested placement | Hand-written from `docs/` plans and the devlog |
| `parameters.md` | Every estimated parameter for the paper, with SE, p-values, N and the results file it comes from | **Generated** by `code/33_paper_materials.py`; do not edit by hand |
| `figures/` | All figures for the paper (main and appendix) | **Generated** by `code/33_paper_materials.py` |

Regenerate the generated files after any rerun: `py -3.10 code/run_pipeline.py --only 33` (2 seconds; reads results files only, no estimation).

## Figures

Four for the main text and four for the appendix. Each is saved as PNG (300 dpi) and PDF (vector, for the journal). Colours are colour-blind safe (Okabe-Ito). The captions below are drafts.

| File | Placement | Draft caption |
|---|---|---|
| `fig1_part1_album_length` | Main, §4 | **Album length, streaming-heavy vs other genres.** (a) Average standard-edition track count by release year (6,775 albums by artists with pre-rule Billboard 200 careers). (b) Year-by-year difference in album length (%), streaming-heavy minus other genres, relative to 2014, with genre and year fixed effects; 95% intervals from artist-clustered SEs. Joint test that the pre-2014 differences are zero: p = 0.85. Albums released on or after 24 November 2014 count as post-rule. |
| `fig2_us_uk_chart_shares` | Main, §5 (key figure) | **Chart composition, U.S. vs UK.** Share of chart spots held by (a) albums in their first chart week and (b) albums that have charted 52 weeks or more, 8-week moving averages. Dashed lines: the U.S. rule (chart dated 13 December 2014) and the UK rule (chart of 1 March 2015). |
| `fig3_monthly_event_study` | Main, §5 | **Monthly event study around each country's rule.** Coefficients on months relative to each country's own rule (reference: the month before), with week-of-year effects, estimated on weekly data 2010–2019 with end bins; shaded 95% intervals, Newey–West (12 lags). Grey: before the rule; blue: after. |
| `fig4_part2b_staying_power` | Main, §6 | **Staying power of streaming-heavy albums.** Year-by-year difference in weeks on the chart during the first 52 weeks after debut, streaming-heavy minus other genres, relative to 2014 (4,517 Billboard 200 debuts, 2010–2018); 95% intervals from artist-clustered SEs. Joint pre-2014 test: p = 0.79. |
| `figA1_riaa_streaming_growth` | Appendix (background) | **U.S. recorded-music revenue, 2005–2019 (RIAA).** (a) Revenue by format, nominal dollars. (b) Streaming's share of revenue. Streaming grew smoothly through the December 2014 rule. |
| `figA2_placebo_dates` | Appendix D | **The U.S. jump compared with fake rule dates.** Histogram of jumps estimated at about 350 fake dates (2011–2018, excluding 26 weeks around either country's rule); the red line is the jump at the actual rule date. Placebo-rank p in each panel title. |
| `figA3_leave_one_genre_out` | Appendix E | **Part 2b with one genre left out at a time.** Extra weeks on chart in the first year for streaming-heavy albums after the rule, re-estimated dropping each genre (95% artist-clustered intervals; dotted line: main estimate). * = streaming-heavy genre. |
| `figA4_track_count_thresholds` | Appendix C | **Where in the length distribution any change sits.** Post-rule change in the share of albums with at least k tracks, streaming-heavy vs other genres, for k = 8–30 (shaded 95% artist-clustered intervals). Descriptive context for the prespecified long-albums follow-up, in which none of five upper-tail tests survives a Holm correction. |

**Dropped:**
- The matched-catalogue-gap figure: it was noisy, dominated by December holiday spikes, and the result is fragile. It is reported in a table only.
- The earlier draft figures (`fig01_*` to `fig06_*`, `figA1_part1_*`, `figA2_part2_*`, `figA3_part2_*`, `figA4_part2b_*`): superseded by the set above; moved to `archive/superseded_paper_figures_2026-10-03/`.

## Tables to build from `parameters.md`

1. Summary statistics (Part 1 means by group and period; Part 2 weekly means 2014 vs 2019; Part 2b means).
2. Part 1: headline, what the null rules out, key robustness checks.
3. Part 2: U.S. jumps, placebo-rank p, RIAA controls, windows, July 2018.
4. Part 2 cross-country: UK own date, UK at U.S. date, pooled test, matched albums.
5. Part 2b: main and robustness, with leave-one-genre-out and UK results in the notes.

Appendix tables: all 12 frozen-plan Part 1 checks, the long-albums follow-up family, Part 2 placebo dates and song charts, and the Part 2b cross-country tests.
