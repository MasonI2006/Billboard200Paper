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

Captions are drafts.

| File | Placement | Draft caption |
|---|---|---|
| `fig01_riaa_revenue.png` | Main, §2 (background) | U.S. recorded-music revenue by format, 2005–2019 (RIAA, nominal dollars), and streaming's share of revenue (right axis). The dashed line marks Billboard's December 2014 rule. Streaming grew smoothly through the rule change. |
| `fig02_part1_mean_tracks_by_year.png` | Main, §4 | Mean standard-edition track count by release year, albums by streaming-heavy vs other-genre artists (6,775 albums by artists with pre-rule Billboard 200 careers). Dashed line: albums released on or after 24 November 2014 count as post-rule. |
| `fig03_part1_event_study.png` | Main, §4 | Year-by-year difference in log track count, streaming-heavy minus other genres, relative to 2014, with genre and year fixed effects. 95% intervals from artist-clustered SEs. Joint test of the pre-2014 coefficients: p = 0.85. |
| `fig04_part2_us_uk_series.png` | Main, §5 (key figure) | Share of chart slots held by new entries (top) and by albums with 52+ weeks on chart (bottom), U.S. Billboard 200 vs UK Official Albums Chart, 8-week centred averages. Dashed lines: U.S. rule (December 2014, red) and UK rule (March 2015, blue). |
| `fig05_part2_event_study_monthly.png` | Main, §5 | Monthly event study around each country's own rule: weekly shares on month-relative dummies (reference: month before the rule) with week-of-year effects, estimated on 2010–2019 with end bins. 95% intervals, Newey–West (12 lags). |
| `fig06_part2b_event_study.png` | Main, §6 | Year-by-year difference in weeks on chart in the first 52 weeks after debut, streaming-heavy minus other genres, relative to 2014 (4,517 Billboard 200 debuts, 2010–2018). Joint pre-2014 test: p = 0.79. |
| `figA1_part1_threshold_profile.png` | Appendix C | Post x streaming-heavy coefficient on the share of albums with at least k tracks, k = 8–30 (95% artist-clustered intervals). Descriptive context for the prespecified long-albums follow-up, in which none of five upper-tail tests survives a Holm correction. |
| `figA2_part2_placebo_distribution.png` | Appendix D (or main §5) | Jump at the U.S. rule date (red) against jumps estimated at about 350 fake dates (2011–2018, excluding 26 weeks around either country's rule). Placebo-rank p = 0.003 (new entries) and 0.076 (52+ weeks). |
| `figA3_part2_matched_catalogue_gap.png` | Appendix D | Albums on both charts (4,678 matched), catalogue only (52+ weeks since debut): number in the U.S. top 100 minus number in the UK top 100, 8-week centred average. December spikes are holiday catalogue albums returning to the U.S. chart; the model absorbs them with week-of-year effects. |
| `figA4_part2b_leave_one_genre_out.png` | Appendix E | Part 2b estimate re-estimated dropping one genre at a time (95% artist-clustered intervals; dotted line: full sample). Dropping hip-hop/R&B lowers the estimate to +1.85 weeks. |

**Not included:** the earlier three-panel draft (`results/part2_incumbency/matched/fig_us_uk_series.png`). It is superseded by Fig. 4 and Fig. A3.

## Tables to build from `parameters.md`

1. Summary statistics (Part 1 means by group and period; Part 2 weekly means 2014 vs 2019; Part 2b means).
2. Part 1: headline, what the null rules out, key robustness checks.
3. Part 2: U.S. jumps, placebo-rank p, RIAA controls, windows, July 2018.
4. Part 2 cross-country: UK own date, UK at U.S. date, pooled test, matched albums.
5. Part 2b: main and robustness, with leave-one-genre-out and UK results in the notes.

Appendix tables: all 12 frozen-plan Part 1 checks, the long-albums follow-up family, Part 2 placebo dates and song charts, and the Part 2b cross-country tests.
