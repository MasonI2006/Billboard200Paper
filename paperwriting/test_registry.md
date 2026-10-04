# Test registry: every test, its plan, its status and its result

Purpose: one place mapping every estimate to the plan that specified it, so the paper can present a clear hierarchy and referees can verify that nothing was chosen after the fact. Exact numbers for every row are in `parameters.md` (generated from the results files). Plans are in `docs/`; the devlog (`docs/devlog.md`) has the full record.

## Status codes

| Code | Meaning | How to present |
|---|---|---|
| **FP** | Frozen primary: the main test in a plan approved before any estimate (`analysis_plan.md` for Part 1, frozen 2026-09-27; `q1_analysis_plan.md` for Part 2; `q1b_analysis_plan.md` for Part 2b). | Headline results. |
| **PS** | Prespecified secondary: listed in one of those plans before estimation. | Robustness tables; all reported. |
| **PF** | Prespecified follow-up: specified in a later written plan, before *that* test was estimated, but after related results were seen (the plan says what had been seen). | Secondary or supporting; state the timing. |
| **EX** | Exploratory: not prespecified, or labelled exploratory in its plan. | Footnotes or appendix, labelled as exploratory. |
| **DE** | Descriptive figure or table; no inference used for any claim. | Figures. |
| **PH** | Post hoc decision: made after seeing results (disclosed in a dated plan note). | Disclose in a footnote. |

Placement: **M** = main text, **A** = appendix, **F** = footnote, **O** = omit (mention only in the data history).

## Part 1: did counting streams change album length?

| # | Test | Status | Plan | Result | Reading | Devlog | Place |
|---|---|---|---|---|---|---|---|
| 1 | **Headline DiD:** log tracks on post x streaming-heavy, genre + year FE (6,775 albums) | FP | `analysis_plan.md` | +0.0228, SE 0.0151, p = 0.133, Webb p = 0.161 | Null | §25–26 | M |
| 2 | What the null rules out: 90% CI, TOST bound, MDE | PF | `final_checks_plan.md` | 90% CI −0.03 to +0.63 tracks; rules out > 0.63 tracks (4.9%); MDE 0.56 tracks; prespecified half-track TOST **fails** (p = 0.16) | Bounded null at ~2/3 of a track | §34 | M |
| 3 | Year-by-year event study, joint pre-2014 test | PS | `analysis_plan.md` | Pre-2014 coefficients −0.014 to +0.017; joint p = 0.85 | No pre-trends | §25–26 | M (Fig. 3) |
| 4 | Charted (Billboard 200 debut) subsample | PS | `analysis_plan.md`; rebuilt per `part1_secondary_rerun_plan.md` | +0.033, p = 0.035, Webb p = 0.084 | Small, not significant at genre level | §25–26 | A |
| 5 | Non-charted subsample | PS | same | +0.016, Webb p = 0.47 | Null | §25–26 | A |
| 6 | Selection: did long streaming-heavy albums become likelier to chart? | PS | same | +0.177, p = 0.058, Webb p = 0.063 | Marginal | §25–26 | A |
| 7 | Chart payoff: debut rank; log weeks on chart | PS (supporting in frozen plan) | same | +21.8 (Webb p = 0.14); +0.51 (Webb p = 0.45) | Null | §25–26 | A |
| 8 | Album-order (career-stage) control, career start (plan's main definition) | PS | `analysis_plan.md`; implemented per `items4_5_plan.md` | +0.021, Webb p = 0.21 | Null, robust | §26 | A |
| 9 | Album order since 2009 (alternate) | PS | same | +0.011, Webb p = 0.37 | Null | §26 | A |
| 10 | Artist fixed effects (within) | PS | same | +0.019, Webb p = 0.30 | Null | §26 | A |
| 11 | Drop albums on/before artist's first qualifying debut | PS | same | +0.029, Webb p = 0.20 | Null | §26 | A |
| 12 | Including Mixtape/Street release groups | PS | same | −0.016, Webb p = 0.74 | Null | §26 | A |
| 13 | 2009–2024 window | PS | same | +0.013, Webb p = 0.45 | Null | §26 | A |
| 14 | 2010–2019 window | PS | same | +0.026, Webb p = 0.12 | Null | §26 | A |
| 15 | Continuous genre intensity (Nielsen ratio) | PS | same | +0.012 per ratio point, Webb p = 0.11 | Null | §26 | A |
| 16 | Exclude electronic | PS | same | +0.020, Webb p = 0.23 | Null | §26 | A |
| 17 | Log running time | PS | same | −0.015, Webb p = 0.81 | Null | §26 | A |
| 18 | Share with > 12 tracks | PS | same | +0.009, Webb p = 0.75 | Null | §26 | A |
| 19 | **Share with ≥ 18 tracks** | PS | same | **+0.043, p = 0.004, Webb p = 0.012** | The 1 significant check of 12 (~0.6 expected by chance) | §26 | A + text |
| 20 | Digital-edition alternate outcome (same sample) | PS | `analysis_plan.md` | +0.020, p = 0.23 | Null | §18, §25 | A |
| 21 | Long-albums follow-up family A1–A5: shares ≥ 15/20/25 tracks, 75th/90th quantiles, Holm | PF | `long_albums_followup_plan.md` | −0.004 / +0.030 / +0.013 / +0.061 / +0.069; **0 of 5 survive Holm** | Test 19 does not generalise; "suggestive, not robust" | §28 | A + F |
| 22 | Long-albums supporting checks: threshold profile k = 8–30; ≥ 18 event study; charted split; ≥ 60 minutes | PF (supporting) | same | Positive at 18–23 tracks only; pre-trend p = 0.998; charted +0.053 / non-charted +0.034; ≥ 60 min −0.008 | Descriptive context for test 19 | §28 | A (Fig. A1) |
| 23 | Seconds per track | EX | `part1_secondary_rerun_plan.md` (labelled exploratory) | −3.9%, p = 0.002 | Shorter songs; exploratory | §25 | F / discussion |
| 24 | Same-day multi-edition launches | EX | same | −5.1 pts, p = 0.008 | Exploratory | §25 | F |
| 25 | UK-origin artists x post (> 12 tracks) | EX | same | +0.001, p = 0.98 | Null | §25 | O / F |
| 26 | Genre rule: rock + pop artists → pop | EX | `genre_classification.md` | +0.016, Webb p = 0.29 | Null robust to genre rule | §25–26 | A |
| 27 | First-round Spotify-sample analyses (Kaggle/Spotify, pre-plan) | EX, superseded | none (devlog §1–20) | Various | Motivated the design; superseded by the MusicBrainz sample | §1–20 | O |

## Part 2: did the rule change which albums the chart rewards?

| # | Test | Status | Plan | Result | Reading | Devlog | Place |
|---|---|---|---|---|---|---|---|
| 28 | **ITS jump at rule: new-entry share** (2010–2019, NW SEs) | FP | `q1_analysis_plan.md` A | −2.6 pts (pre-mean 10.8%), NW p < 0.001; **placebo-rank p = 0.003** | Sharp drop in new entries | §21, §31 | M |
| 29 | **ITS jump at rule: 52+-week share** | FP | same | +5.7 pts (pre-mean 22.1%), NW p < 0.001; placebo-rank p = 0.076 | Jump toward long-runners | §21, §31 | M |
| 30 | Trend changes at the rule (both outcomes) | FP (plan reports with the jump) | same | −1.3 / +1.7 pts per year, p < 0.001 | **Unreliable**: fake dates also give significant trend changes (test 34); report, don't lean on | §21 | A |
| 31 | Re-entry share; artist concentration (HHI) | PS | same | −1.3 pts (p = 0.02); HHI ≈ 0 (p = 0.90) | No change in concentration | §21 | A |
| 32 | First-run length of new debuts | PS | same | Jump +0.009 log weeks (p = 0.83) | Null | §21 | A |
| 33 | 2010–2024 window | PS | same | −3.2 / +5.5 pts | Same | §21 | A |
| 34 | Placebo dates (Dec 2011, 2012, 2016, 2017) | PS | same B | Some fake-date jumps significant (e.g. new-entry +1.6 pts in 2011, p = 0.004) | Nominal p overstates certainty; motivates test 38 | §21 | A |
| 35 | Song charts (streaming, digital sales, radio), new-entry share | PS | same C | Streaming +2.5 (p = 0.39); digital sales −1.2 (p = 0.32); radio −2.3 (p < 0.001) | Mixed; superseded by the UK comparison as the main external check | §21 | A / F |
| 36 | July 2018 paid/free weighting as a second break | PS | same D | −1.0 / −1.7 pts, n.s. | No further break | §21 | A / F |
| 37 | RIAA streaming share / revenue as controls | PF | `matched_albums_plan.md` E | Jumps unchanged: −2.6 → −2.9 to −3.3; +5.7 → +5.0 to +5.6; all p < 0.001 | Smooth streaming growth does not explain the jumps | §33 | M |
| 38 | Placebo-date distribution for the U.S. jumps (~350 fake dates) | PF | `uk_comparison_plan.md` D | Ranks: p = 0.003 (new entries), 0.076 (52+ weeks) | Jump in new entries is exceptional | §31 | M (Fig. A2 or main) |
| 39 | UK chart: break at its own rule (Mar 2015) | PF | `uk_comparison_plan.md` A | −0.6 pts (placebo p = 0.55); +1.9 pts (placebo p = 0.94) | No UK break | §31 | M |
| 40 | UK chart: placebo at the U.S. date | PF | same B | ≈ 0 on both outcomes | No common shock at Dec 2014 | §31 | M |
| 41 | Pooled U.S. + UK: own-date vs other-date jump | PF | same C | Own −0.019 (p = 0.01) / +0.034 (p = 0.007); other ≈ 0; own − other p 0.03–0.25 | Own-date jumps, driven by the U.S. | §31 | A |
| — | *Plan verdict for 39–41* | — | same | "Common shock indicated" via the clause "UK does not break at own date" | **Caveat recorded:** the data show no common shock (UK flat at both dates; UK new-entry share flat 2014–2019 while the U.S. share halved) | §31 | M (state both) |
| 42 | **Matched albums A:** U.S.-minus-UK top-100 presence of the same catalogue albums, jumps at Dec 2014 (tau1) and Mar 2015 (tau2) | PF (main) | `matched_albums_plan.md` A | tau1 +0.0026 (~6.5 albums), placebo-rank p = 0.071 (Holm 0.14); tau2 −0.0012 | Supported under the plan's rule; **fragile** (tau1 vanishes with trend changes, test 43) | §33 | M or A |
| 43 | Matched A secondaries: + trend changes; full Billboard 200 | PF | same | tau1 +0.0001 (p = 0.92); tau1 +0.0051 (p < 0.001) | Fragility disclosed | §33 | A |
| 44 | Inclusion vs formula (|tau2| / tau1) | PF | same | 0.46 < 0.5: "formula details matter", borderline | Discussion point, not a finding | §33 | Discussion |
| 45 | Matched B: first-year runs of simultaneous releases | PF (secondary) | same B | tau1 −0.27 weeks (p = 0.88) | Null | §33 | A |
| 46 | Monthly event-study figure, U.S. and UK | DE (spec deviated, see plan note) | `final_checks_plan.md` | U.S. step down in new entries after upward drift; U.S. step up in 52+; UK no step | Visual evidence of sharpness | §34 | M (Fig. 5) |
| 47 | Weekly U.S. vs UK series | DE | — | U.S. new-entry share 11.8% → 5.7% (2014–19); UK 11.5% → 10.1% | Key figure | §31 | M (Fig. 4) |

## Part 2b: did streaming-heavy albums gain more staying power?

| # | Test | Status | Plan | Result | Reading | Devlog | Place |
|---|---|---|---|---|---|---|---|
| 48 | **Main: weeks on chart in first 52, post x streaming-heavy** (4,517 albums) | FP | `q1b_analysis_plan.md` | +3.23 weeks, SE 0.90, p < 0.001, genre bootstrap p = 0.015 | Positive | §25 | M |
| 49 | Weeks in first 26; still on chart at week 26 | PS | same | +1.78 (boot p = 0.007); +4.6 pts (p = 0.04; boot p = 0.44) | Consistent | §25 | A |
| 50 | Debut-rank controls | PS | same | +2.59, p < 0.001 | Survives | §25 | A |
| 51 | Artist fixed effects | PS; SE choice **PH** | same; dated note 2026-10-03 | +1.73, SE 0.81, p = 0.034 (within); dummy-count SE 1.05, p = 0.10 | Positive within artists; SE switch made after seeing both, disclosed | §26–27 | A + F |
| 52 | Event study, joint pre-2014 test | PS | same | Pre +1.5, −0.1, +0.6, +0.8; joint p = 0.79; post +3.1 to +3.9 | No pre-trends | §25 | M (Fig. 6) |
| 53 | Album-age share of chart slots (descriptive) | PS (descriptive) | same | Rising before the rule in both groups | Context | §22 | A / F |
| 54 | Album-order (career-stage) control | PS (extension) | `items4_5_plan.md` | +3.10, boot p = 0.012 | Survives | §26 | A |
| 55 | Labels from the per-artist genre file | PS (extension) | same | +3.29, boot p = 0.010 | Survives | §26 | A |
| 56 | Genre rule: rock + pop → pop | EX | `genre_classification.md` | +2.45, p = 0.001, **boot p = 0.174** | Genre-level significance depends on this call; report in main text | §25–26 | M (sentence) + A |
| 57 | Leave-one-genre-out | PF | `final_checks_plan.md` | All 9 positive (+1.85 to +3.73); without hip-hop/R&B +1.85 (boot p = 0.10) | Not driven by one genre by the plan's rule, but hip-hop/R&B carries much of it | §34 | A (Fig. A4) + text |
| 58 | Cross-country triple difference (same album, U.S. vs UK) | PF (main) | `matched_albums_plan.md` C | heavy x post-U.S. +7.8 weeks (p = 0.06; **boot p = 0.43**); heavy x post-UK −4.3 | Not supported at the genre level | §33 | A |
| 59 | Part 2b replicated on the UK chart (post = Mar 2015) | PF | same D | +0.03 weeks (p = 0.98) | Null: Part 2b is U.S.-specific | §33 | M (sentence) + A |

## Data-quality checks (not tests; report in the data section)

| Check | Result | Devlog |
|---|---|---|
| Genre hand check, 100 random albums | 0 clear errors; 91 of 91 labelled albums agree with the ordered rule | §24 |
| Edition hand check, 30 albums | Standard-edition rule adjudicated (step 13) | §17, §23 |
| U.S.-UK album matches, 50 random | 50 of 50 correct | §33 |
| UK #1 rows rebuilt | All 522 weeks of 2010–2019 complete; sequence matches the record | §30 |
| Determinism | Genre labels identical across five runs with different hash seeds | §24 |

## Superseded estimates (disclose in a footnote or appendix)

Three implementation bugs were found and fixed on 2026-10-02/03, each documented in a dated note in `docs/analysis_plan.md`. All estimates above are post-fix.
1. **Random genre tie-break** (Python set order): the 2026-09-28 headline +0.0356 (Webb p = 0.247) is superseded.
2. **Release-date parsing** (the headline sample held only year-only-dated albums, 1,663 albums): −0.0247 (Webb p = 0.434) is superseded.
3. **Artist clusters were the first word of the artist name**: SEs and p-values only; the corrected headline is above.

## Multiplicity: how to present it

- **Main claims rest on four FP tests:** Part 1 headline (#1), the Part 2 jumps (#28, #29), and the Part 2b main estimate (#48).
- **Part 1 has 12 frozen-plan secondary checks** (#8–19). One is significant (#19), about what chance predicts (0.6), and its follow-up fails Holm (#21).
- **Every other test is supporting.** Its status code should appear in the table notes.
