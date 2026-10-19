# Answers to `todo_for_code_agent.md`

Prepared 2026-10-08 by Claude Code (Claude Opus 5.5). `main.tex`, `online_resource1.tex` and `references.bib` were read but not edited. The only rerun was `py -3.10 code/run_pipeline.py --only 12 13 14` (2026-10-08 22:14 CDT, cache-only, about 25 s). Its outputs were **byte-identical** to the committed files (`git diff` empty), so no number changed. Everything else was read from files, or recomputed read-only by scratch scripts that were not saved in the project.

Confidence labels used below:
- **direct**: read straight from a file;
- **recomputed**: recomputed from the data in this session and matches;
- **inferred**: reasoned from indirect evidence;
- **not found**.

---

## Conflicts and surprises (read these first)

1. **C2: three cells under "Genre boot. p" in Table 4 are genuine genre-level wild-bootstrap p-values, but they use two different t-statistics.**
   - All Part 2b bootstrap p-values in the project are restricted wild cluster bootstraps with Webb weights over genre clusters. The labels "artist-clustered t" and "genre-clustered t" in `parameters.md` describe which standard error goes into the bootstrap t-statistic. They are not different tests.
   - Main (0.015), without hip-hop/R&B (0.10) and rock + pop (0.174) use the genre-clustered t (script 22's `wild_boot`).
   - Career position (0.012) and the UK row (0.983) use the artist-clustered t (`code/inference.py`). On that variant the main row is **0.011**, not 0.015.
   - No bootstrap exists for **debut-rank controls** or **artist fixed effects**. Filling those cells needs a rerun, which I have not done (details in C2).
2. **C3 / Table 3: the RIAA range for the new-entry share omits one specification.** The paper's "−2.9 to −3.3" covers "+ streaming share" (−2.90) and "+ both" (−3.26). "+ log streaming revenue" gives **−2.64**, so the full range is **−2.6 to −3.3**. The 52+-week range "+5.0 to +5.6" does cover all three. `test_registry.md` row 37 has the same omission.
3. **B2: the U.S. new-entry jump is larger than *every* placebo jump, not "all but one".**
   - p = 0.0028 = (1 + 0)/(352 + 1): none of the 352 fake-date |tau| values reaches the actual |tau|.
   - devlog §31, PROJECT_CONTEXT and `paper_outline.md` ("larger than at all but one") misread the +1 in the formula.
   - The test is **two-sided on |tau|**, not one-sided "in the predicted direction" as the main.tex footnote says.
4. **D5: one UK week in 2010–2019 has 99 rows, not 100.** Week 2013-03-17 lacks position 97 in the raw workbook itself (98 data rows plus the rebuilt #1). devlog §30 and `uk_comparison_plan.md` say "all 522 weeks complete (100 rows)". The 522-week count is right.
5. **D1: the todo's premise is slightly off.** Step 14 does not write `musicbrainz_genre_balance.csv`; step 12 does. The committed tables were already regenerated under the ordered rule on 2026-10-02 (commit 2f1371b), and today's rerun reproduces them exactly. "Similar across genre groups" holds at the group level (17.9% vs 16.5%), with caveats in D1.
6. **A3: "a written analysis plan completed before its estimates were seen" needs two qualifications.**
   - The Part 2 plan records that yearly averages of both outcomes had been seen beforehand.
   - The Part 1 plan was written after the exploratory Spotify result (+0.123) had been seen (devlog §4, "honesty note").
   - Git history cannot confirm the September plan dates, because the repository was created on 2026-10-02.
7. **B1: the plan fixes 12 lags but gives no reason.** "Roughly one quarter of weekly data" is a description added later (12 weeks is about 0.23 of a year). No run uses a different lag.
8. **D8: holiday albums are not excluded by any rule in the code.** The frozen plan lists holiday albums among the exclusions. MusicBrainz has no holiday type, and the code excludes only by secondary type (compilation, soundtrack, live, remix, mixtape, and so on). The main.tex wording is accurate because it does not mention holiday albums.
9. **E1–E3: the Kaggle version number and the RIAA export date are not recorded anywhere in the project.** The UK file's identity can only be inferred.

---

## A. Dates and definitions

### A1. July 2018 break date
- **Answer:** `R2018 = pd.Timestamp("2018-07-11")`, a **stored** (Kaggle) date. The code comment reads "chart dated July 14, 2018". So the test uses the chart with issue date 14 July 2018, stored three days earlier, as main.tex says.
- **Evidence:**
  - `code/20_part2_incumbency.py:7` defines the date.
  - Lines 33–35 build `post2 = Date >= R2018` and `t_post2`; line 77 runs it for both outcomes.
  - Output: `results/part2_incumbency/D_with_2018_break.csv`.
- **Notes:**
  - **Results:** July 2018 jump −0.96 pts (NW p = 0.12) in new-entry share and −1.70 pts (p = 0.39) in 52+-week share.
  - With the 2018 break in the model, the December 2014 jumps become −2.87 / +5.97 pts (vs −2.59 / +5.67 without).
  - Confidence: **direct**. The tracking week (29 June–5 July 2018) is not in the code and was not checked.

### A2. Which date defines "post" in each analysis
| Analysis | Cutoff in code | Convention | Evidence |
|---|---|---|---|
| Part 1 (`Post_a`) | `release_date >= 2014-11-24` | release date (start of the first tracking week) | `code/musicbrainz_helpers.py:425` (`RULE_DATE`) and line 488 |
| Part 2b (`PostDebut_a`) | `debut >= 2014-12-10` | **stored** chart date of the first rule chart | `code/22_part2b_analyze.py:5` and line 20 |
| Part 2 (`Post_w`) | `Date >= 2014-12-10` | **stored** date (not the 13 Dec issue date) | `code/20_part2_incumbency.py:6` and line 31; also `29_uk_comparison.py:16`, `31_matched_album_tests.py:32`, `32_final_checks.py:21` |

- **The 23 albums: confirmed.** In `data/final/part2b_album_runs.csv`:
  - post = 1 for 1,368 albums and post = 0 for 3,149; N = 4,517; 1,800 artists.
  - Exactly **23** albums debut on or after 2014-11-24 with post = 0. They are the debuts stored **2014-11-26 and 2014-12-03**, the only two chart dates between 2014-11-24 and 2014-12-09.
  - The earliest post = 1 debut is 2014-12-10.
- **Notes:**
  - Only the figures use the issue date, 2014-12-13 (`33_paper_materials.py:20`; `31_matched_album_tests.py:282`).
  - Part 1 cross-check: the earliest post-rule release date in `analysis_sample.csv` is 2014-11-24 and the latest pre-rule date is 2014-11-21.
  - Confidence: **direct + recomputed**.

### A3. Plan freeze and completion dates
| Plan | Date in the text | Git (first commit touching the file) | Notes |
|---|---|---|---|
| `docs/analysis_plan.md` (Part 1) | Title: "Approved and Frozen 2026-09-27"; approval record: "Approved and frozen by the user on 2026-09-27" | c0aebb4, 2026-10-02 (repo snapshot) | devlog §8–9 (2026-09-27). Dated notes added 2026-10-02 (×2) and 2026-10-03. |
| `docs/q1_analysis_plan.md` (Part 2) | "Written 2026-09-28 before running any estimates. Already seen beforehand: yearly averages of the new-entry share and the 52+-week share" | c0aebb4, 2026-10-02 | Written in Claude chat (devlog §21) |
| `docs/q1b_analysis_plan.md` (Part 2b) | "Written 2026-09-28 before running estimates" | c0aebb4, 2026-10-02 | Dated note 2026-10-03 (artist-FE SE choice, made after seeing both numbers) |
| `docs/part1_secondary_rerun_plan.md` | "Written 2026-10-02, before any estimation" | 3835fa7, 2026-10-02 22:02 | |
| `docs/items4_5_plan.md` | "Written 2026-10-02, before any estimation" | 2f83fc6, 2026-10-03 00:10 | |
| `docs/long_albums_followup_plan.md` | "Written 2026-10-03, before any estimation" | 511f0a8, 2026-10-03 20:27 | Approved and run 2026-10-03; post-estimation notes |
| `docs/uk_comparison_plan.md` | "Written 2026-10-03, before any estimation" | 4cb0249, 2026-10-03 21:45 | Results commit c7a6f55 later the same day |
| `docs/matched_albums_plan.md` | "Written 2026-10-03, before any estimation" | 02843d6, 2026-10-03 21:57 (plan-only commit) | Results commit f4bdd9a |
| `docs/final_checks_plan.md` | "Written 2026-10-03, before any estimation" | 77ca140, 2026-10-03 22:15 | **Plan and results in the same commit**; the plan says the author approved running immediately |

- **Answer:** "Part 1 plan frozen 27 September 2026" is supported by the plan text and the devlog.
- **Notes:**
  - The repository was initialised on 2026-10-02 (devlog §23), so git cannot independently confirm the 09-27/09-28 dates. File modification dates were reset by the folder move.
  - For the three plans committed separately before their results (uk_comparison, matched_albums, and long_albums in commit 511f0a8 vs results 9445461), git confirms that the plan came first.
  - Qualification for main.tex Sect. 4.4: see surprise 6.
  - Confidence: **direct** (text); git: **direct**, but uninformative for the September plans.

## B. Estimation details

### B1. Newey–West lags
- **Answer:** 12 lags, fixed in the Part 2 plan before estimation. The plan's wording: "Newey-West standard errors with 12 lags" (`docs/q1_analysis_plan.md`, test A). **No reason is given.** Later plans inherit it:
  - `uk_comparison_plan.md:34, :42` (including Driscoll–Kraay with 12 lags);
  - `matched_albums_plan.md:41`;
  - `final_checks_plan.md:25`.
- **Evidence:** `maxlags: 12` appears at `code/20_part2_incumbency.py:38`; `29_uk_comparison.py:58, 81, 83`; `31_matched_album_tests.py:108, 262`; `32_final_checks.py:114`.
- **Other lags:** none. No script uses any other `maxlags`.
- **Notes:**
  - "Roughly one quarter" is a fair description (12 of 52 weeks) but was not the stated rationale. Suggested wording: "12 lags, fixed in the analysis plan (about one quarter of weekly data)".
  - Confidence: **direct**.

### B2. Placebo p-value
- **Answer:** **two-sided**.
  - Formula: p = (1 + #{fake dates with |tau_fake| ≥ |tau_actual|}) / (N_fake + 1). Ties count (≥), and the actual date is added to numerator and denominator.
  - This matches the plan: "Report the rank of the true-date |tau|" (`uk_comparison_plan.md:44`).
- **Evidence:** `code/29_uk_comparison.py:90–98` (formula at line 97); `EXCLUDE_WEEKS = 26` at line 21.
- **Placebo dates:**
  - **352 for the U.S. series** (stored dates 2011-01-05 to 2018-12-26) and **353 for the UK** (2011-01-02 to 2018-12-30). Source: `uk_comparison_placebo_rank.csv`, `uk_comparison_placebo_distribution.csv`.
  - Candidate window: chart dates from 2011-01-01 to 2018-12-31 (line 91).
  - Exclusion (line 92): a date is dropped unless it is **more than 182 days from all four true dates**: U.S. rule 2014-12-10, UK week 2014-12-07, UK rule 2015-03-01, U.S. week 2015-03-04. In effect, about mid-2014 to about August 2015 is excluded.
- **Implication:** the U.S. new-entry p = 0.0028 = 1/353 means **no** fake date matched it (surprise 3). The U.S. 52+-week p = 0.076 means 26 fake dates did.
- **Wording for main.tex:** "the share of placebo jumps at least as large in absolute value as the actual jump (two-sided), counting the actual date".
- Confidence: **direct**.

### B3. Mapping the annual RIAA series to weeks
- **Answer:** linear interpolation.
  - Each annual value is placed on **1 July** of its year, and every weekly chart date is linearly interpolated between the mid-year points (`np.interp`).
  - Two series: streaming share of total revenue, and log nominal streaming revenue.
  - Variants: either one alone, or both together.
- **Evidence:** `code/31_matched_album_tests.py:244–266` (mid-year placement at 248–249; interpolation at 252–253). Plan: `docs/matched_albums_plan.md:76` ("placed at mid-year and linearly interpolated to weeks").
- Confidence: **direct**.

## C. Numbers

### C1. Streaming share of U.S. recorded-music revenue
- **Answer:** **2013: 23.3%; 2014: 31.2%; 2015: 38.0%.** These support the paper's 23%, 31% and 38%.
- **Evidence:**
  - `data/final/riaa_revenue_by_category.csv`, `streaming_share` column, rows 2013–2015 (0.232805, 0.311917, 0.380484).
  - Built by `code/27_riaa_revenue.py:44` as `streaming_nominal / total_nominal`.
  - `figA1_riaa_streaming_growth` reads the same file (`code/33_paper_materials.py:159–160`).
- **Definitions:**
  - **Numerator:** RIAA's "Streaming" category total, i.e. the sum of the formats Paid Subscriptions (Premium), Paid Subscriptions (Non-Premium; $0 in these years), Free Streaming and "Other Streaming". For 2014: $423.6M + $0 + $283.8M + $773.4M = $1,480.8M.
  - **Denominator:** total recorded-music revenue (physical + downloads + streaming + synchronisation) in **nominal** dollars ($4,747.6M in 2014).
- **Notes:**
  - "Other Streaming" is the largest component. In RIAA's taxonomy it usually covers SoundExchange distributions and other ad-supported streaming, including non-interactive digital radio. That label meaning is **inferred**: the export does not define it. If the paper says "on-demand streaming", that is not quite the series.
  - File: `data/raw/RIAARevenue.csv` (Tableau crosstab export, UTF-16, tab-separated). Export date: **not found** (see E3).
  - Confidence: **recomputed**.

### C2. Part 2b table (Table 4)
| Row | Estimate | p (artist-clustered) | Genre wild-bootstrap p | Bootstrap t-statistic | Source |
|---|---|---|---|---|---|
| Main, N = 4,517 | 3.23 | <0.001 (0.0003) | **0.015** (9 clusters) | genre-clustered | `results_main.csv` row 2 |
| (main, other variant) | 3.23 | <0.001 | **0.011** | artist-clustered | `extensions.csv` row 2 |
| + Debut-rank controls | 2.59 | <0.001 (0.0003) | **does not exist** | — | `results_main.csv` row 5 (bootstrap column blank) |
| + Career position | 3.10 | **<0.001 (0.0005)** | **0.012** (9 clusters) | artist-clustered | `extensions.csv` row 3 |
| Artist fixed effects (within) | 1.73 | 0.034 | **does not exist** | — | `results_main.csv` row 6 |
| Rock + pop coded as pop | 2.45 | 0.001 | **0.174** | genre-clustered (step 19 reruns script 22) | `results/part1_album_length/secondary/rockpop_sensitivity.csv` row 3 |
| Without hip-hop/R&B | 1.85 | **0.079** | **0.102** (8 clusters) | genre-clustered (`32_final_checks.py:56–57`, "verbatim" copy of script 22's `wild_boot`) | `results/final_checks/part2b_leave_one_genre_out.csv` row 7 |
| UK chart (post = March 2015) | 0.03 | 0.98 (0.984) | **0.983** | artist-clustered (`inference.py`; `31_matched_album_tests.py:232`) | `results/part2_incumbency/matched/D_uk_part2b.csv` row 2 |

- **Answer to the "important check":** 0.012 (career position) and 0.10 (without hip-hop/R&B) **are both genuine genre-level restricted Webb wild cluster bootstrap p-values**, so they belong under "Genre boot. p". The `parameters.md` labels describe the t-statistic inside the bootstrap, not the type of p-value.
- **The column mixes two variants.**
  - Main, rock + pop and leave-one-out use the genre-clustered t.
  - Career position and UK use the artist-clustered t. On that variant the main row is 0.011.
  - Options:
    - (a) footnote the difference; or
    - (b) report the career-position row next to the artist-t main (0.011 vs 0.012).
- **Rows that need a rerun to fill the bootstrap cell** (not run, per the todo's instruction):
  1. debut-rank controls: script 22's `wild_boot` would need a `C(rank_bin)` term added (not timed; the main 9,999-draw bootstrap is part of step 22's 32 s run, devlog §27);
  2. artist fixed effects: would need the bootstrap applied to the within-demeaned design (`inference.py` supports `intercept=False`). This was never specified in a plan, so it would be a new, post hoc specification.

  Alternatively, mark both cells "—" with a note that the plan prescribed the bootstrap only for the main test.
- **Notes:** the leave-one-out row has 8 genre clusters, not 9. The UK row's cluster count is not stored in the CSV. Confidence: **direct** (all values) and **direct** (code paths).

### C3. Table 3 additions (Part 2)
**U.S. jumps (2010–2019, 521 weeks), from `A_break_tests.csv` rows 2–3:**

| | New-entry share | 52+-week share |
|---|---|---|
| tau (Newey–West SE) | −0.0259 (0.0041), p = 1.9e-10 | +0.0567 (0.0087), p = 8.7e-11 |
| 2010–2024 window (782 weeks), rows 6–7 | −0.0322 (0.0048), p = 1.8e-11 | +0.0554 (0.0092), p = 1.7e-9 |

**UK (522 weeks), from `uk_comparison.csv`:**

| | New-entry share | 52+-week share |
|---|---|---|
| UK at own date, 2015-03-01 | −0.0064 (0.0048), NW p = 0.18; placebo p = 0.545 | +0.0191 (0.0141), NW p = 0.18; placebo p = 0.944 |
| UK at U.S. date, 2014-12-07 | −0.0028 (0.0048), NW p = 0.56; placebo p = 0.785 | +0.0022 (0.0152), NW p = 0.88; placebo p = 0.997 |

**RIAA controls (`matched/E_riaa_control.csv`):**

| Specification | New-entry tau (SE) | 52+-week tau (SE) |
|---|---|---|
| No control | −0.0259 (0.0041) | +0.0567 (0.0087) |
| + streaming share | −0.0290 (0.0041) | +0.0541 (0.0091) |
| + log streaming revenue | **−0.0264** (0.0046) | **+0.0557** (0.0111) |
| + both | **−0.0326** (0.0046) | **+0.0500** (0.0098) |

- Correct ranges across the three control specifications: new-entry **−2.6 to −3.3** (endpoints: log revenue, both); 52+-week **+5.0 to +5.6** (endpoints: both, log revenue). All p < 1e-6. See surprise 2.

**Pooled U.S.–UK own-minus-other test (`uk_comparison_pooled.csv`, U.S. 200-slot rows):**

| Outcome | Own-date jump | Other-date jump | Own − other | p, NW by country | p, Driscoll–Kraay |
|---|---|---|---|---|---|
| New-entry share | −0.0191 (NW SE 0.0074; DK 0.0057) | +0.0035 | **−0.0226** | **0.112** | **0.034** |
| 52+-week share | +0.0343 (NW SE 0.0127; DK 0.0088) | +0.0043 | **+0.0300** | **0.248** | **0.079** |

- Secondary rows with the U.S. top 100: new-entry −0.0130 (p 0.34 / 0.33); 52+-week +0.0546 (p 0.005 / 0.002).
- **Notes:**
  - The "UK at U.S. rule date ≈ 0" row is −0.28 and +0.22 pts.
  - All values agree with `parameters.md` lines 116–145.
  - Confidence: **direct**.

### C4. Table 1 checks
- **Panel A: confirmed.** From `data/final/analysis_sample.csv`:
  - N = 6,775 albums by 1,942 artists (`artist_cluster`), 9 genres.
  - Streaming-heavy: 1,507 pre / 1,079 post, mean tracks 13.99 / 14.05.
  - Other: 2,548 pre / 1,641 post, means 12.50 / 12.18.
  - Also in `results/part1_album_length/headline_means.csv`. Confidence: **recomputed**.
- **Panel B: confirmed.** From `results/part2_incumbency/annual_means.csv` and `data/final/part2_weekly_billboard200.csv`:
  - "Pre-rule mean" = all **257 weekly charts stored 2010-01-06 to 2014-12-03**: new-entry 10.80%, 52+-week 22.14%. This is the `pre_mean` in `A_break_tests.csv`.
  - 2014: 11.82% / 26.19%. Calendar-year mean over **53 weekly charts**, including 4 post-rule charts (2014-12-10 to 2014-12-31).
  - 2019: 5.67% / 48.87% (52 charts).
  - Table 3 labels the pre-rule mean "U.S., 2010–2014". Strictly, it runs to the last pre-rule chart, 2014-12-03.
- **Panel C: confirmed.** Estimation reads `PART2B_ALBUM_RUNS` = `data/final/part2b_album_runs.csv`:
  - script 22 writes it at line 24 and estimates on the same frame;
  - scripts 25 and 32 read it back;
  - N = 4,517, 1,800 artists (`mbid`), and the counts and means match.
- **Week counts: confirmed.**
  - U.S.: **521** weekly charts in 2010–2019 (2010-01-06 to 2019-12-25), each with 200 rows.
  - UK: **522** chart weeks (2010-01-03 to 2019-12-29). One UK week has 99 rows (surprise 4).
  - Confidence: **recomputed**.

## D. Data-section claims

### D1. Unmatched rate by genre group: **supported, with caveats**
- **Rerun:** `py -3.10 code/run_pipeline.py --only 12 13 14`, 2026-10-08. Step 12 writes the genre tables; 13 re-adjudicates the edition sheet that 12 regenerates (30/30 pass); 14 writes the coverage and Spotify tables. **All outputs byte-identical** to the versions committed 2026-10-02 under the ordered genre rule. The path is `results/part1_album_length/validation/musicbrainz_genre_balance.csv`, not `data/`.
- **Groups** (`musicbrainz_genre_balance.csv`; denominator = resolved + unresolved roster artists with that genre):

| Group | Roster artists | Unmatched | Rate |
|---|---|---|---|
| Streaming-heavy | 903 | 162 | **17.9%** |
| Other | 1,548 | 255 | **16.5%** |
| Unknown genre | 910 | 577 | 63.4% |
| All | 3,361 | 994 | 29.6% |

- **Nine genres** (heavy rows are in `musicbrainz_subgenre_balance.csv`; the other five were recomputed with step 12's own logic, lines 56–117, read-only):

| Genre | Artists | Unmatched | Rate |
|---|---|---|---|
| hip-hop/R&B* | 637 | 122 | 19.2% |
| pop* | 44 | 9 | 20.5% |
| electronic* | 145 | 23 | 15.9% |
| latin* | 77 | 8 | 10.4% |
| rock | 936 | 169 | 18.1% |
| country | 314 | 44 | 14.0% |
| Christian | 156 | 22 | 14.1% |
| jazz | 75 | 12 | 16.0% |
| classical | 67 | 8 | 11.9% |

\* streaming-heavy.

- **Caveats for the footnote / Table S:**
  1. For unmatched artists a genre is known only when every same-name MusicBrainz candidate's tags agree (`infer_row_genre`, `musicbrainz_helpers.py:400–418`). **577 of the 994 unmatched (58%) have no genre at all**, so the comparison covers 417 of them.
  2. The devlog §17–18 rates (17.6% / 16.8%; subgenre 22.2% etc.) predate the tie-break fix and are superseded. PROJECT_CONTEXT §7 already gives the current numbers.
- Step 14's Billboard-coverage table groups artists by **Spotify** genre (412 / 183 streaming-heavy debut rows), not MusicBrainz. It is unchanged since devlog §17.
- Confidence: **direct** (group and heavy rows) and **recomputed** (other five genres).

### D2. 100-album genre hand check: **supported**
- **File:** `results/part1_album_length/validation/genre_handcheck_sample_100.csv`: 100 rows; `handcheck_status` = 90 `hand_checked_pass` and 10 `manual_override`; `clear_error` = False for all 100.
- **Seed:** 20260928 (`code/15_prepare_genre_handcheck.py:22`; sampling at line 84).
- **Log:** devlog §17 (2026-09-28: 0/100 clear errors; the 10 edge cases named). Re-checked against the ordered rule in devlog §24 / `docs/genre_classification.md` §5: 91 of 100 are labelled, and 91/91 agree.
- **Notes:**
  - The 10 "manual overrides" are assignments to edge cases with no clean tag match. They are not counted as errors, per the plan's definition.
  - The check used MusicBrainz metadata and artist disambiguation, not an external genre source (devlog §17 says so).
  - Confidence: **direct**.

### D3. Independent streaming-service sample: **supported**
- **File:** `results/part1_album_length/validation/musicbrainz_spotify_count_comparison.csv` (step 14):
  - 305 exact artist/album matches between MusicBrainz standard editions and the Spotify sample;
  - **222 (72.8%) agree exactly**, 268 (87.9%) within 2 tracks, and 37 (12.1%) differ by 3 or more.
- **Hand checks:** devlog §17 checked 8 large mismatches against Wikipedia track listings:
  - MusicBrainz matched the standard edition in 4 (*The Pale Emperor*, *Moon Landing*, *Neighbourhood*, *My Everything*) and was closer in 1 (*Indie Cindy*);
  - Spotify matched in 1 (*Justice*);
  - 2 were edition-definition cases (*Pink Friday 2*: physical 10 vs digital 22; *Nothing but the Beat*: double album).
- **Also:** the mismatch rate is not higher after the rule (15.0% pre, 8.3% post).
- **Notes:** "for most albums" is accurate at 73% exact / 88% within two tracks. "Hand checks favour MusicBrainz" rests on 8 albums, and one (*Justice*) went the other way. Confidence: **direct**.

### D4. Earliest digital edition: **supported**
- **File:** `results/part1_album_length/digital_robustness.csv` (step 16).
- **Estimates:**
  - digital alternate outcome **+0.0197** (artist-clustered SE 0.0163, p = 0.227);
  - frozen standard outcome on the same 5,612 albums +0.0230 (p = 0.157);
  - full-sample headline +0.0228.
- **Coverage:** 5,612 of 6,775 albums have an identifiable digital edition (1,163 missing); the count differs from the frozen standard for 979.
- **Notes:** no bootstrap was run for this check (blank column). Small caveat: `digital_track_counts()` picks the earliest digital date by comparing text, so within a year a year-only date beats a full date (`musicbrainz_helpers.py:457`). Confidence: **direct**.

### D5. UK number-one reconstruction: **partly supported; the published list was not compared**
- **What was actually checked:**
  1. **Peak = 1.**
     - The code itself sets `peak = 1` on rebuilt rows (`code/28_uk_albums_build.py:80, 88`), so it does not test this.
     - The devlog §30 check, re-run independently today on the raw-derived rows: all 938 source rows marked "LW:1" (2000–2025) carry peak 1, and all 1,326 identified rebuilt #1 albums show peak 1 in at least one non-rebuilt row. **Holds.**
  2. **Sequence around the rule.** Devlog §30 compared about six weeks against named albums (One Direction *Four*, Olly Murs, Take That *III*, Ed Sheeran *X* at Christmas 2014, Sam Smith *In the Lonely Hour* on 1 March 2015). The rebuilt sequence for 2014-11-16 to 2015-03-15 was re-listed today and shows these.
     - Only the Sam Smith week is tied to a cited source: the Official Charts Company names it the first streams-inclusive #1.
     - The rest were checked against general knowledge, not a downloaded list.
- **Not done:** no systematic comparison with the Official Charts Company's published list of number-one albums. "The sequence around the rule matches the published record" overstates it. Suggested: "spot checks of the weeks around the rule match the published record".
- **Other facts:**
  - 9 weeks (all 2021 or later) have an unidentifiable #1.
  - 2010–2019 has none, but week 2013-03-17 has only 99 rows: position 97 is missing in the source sheet (surprise 4).
- Confidence: **recomputed** (peak, sequence) and **direct** (devlog).

### D6. Roster and sample counts: **all supported**
| Claim | Value | Evidence |
|---|---|---|
| Roster artists | 3,361 | `data/interim/pre_rule_artist_roster.csv` (3,361 rows) |
| Matched uniquely | 2,367 | `data/interim/musicbrainz_artist_matches.csv`: 2,367 rows with an ID, 2,367 unique IDs |
| With a genre | 2,034: 741 heavy, 1,293 other | `data/final/artist_genres.csv` (`heavy` 1 = 741, 0 = 1,293) |
| Part 1 sample | 6,775 albums, 1,942 artists | `data/final/analysis_sample.csv`; `results/part1_album_length/headline.csv` |

Confidence: **recomputed**.

### D7. Weeks per source: **supported**
- `data/raw/billboard200.csv` stored chart dates run from **1963-08-07 to 2026-09-16** (3,293 weekly charts; no unparseable dates).
- 2010-01-06 to 2019-12-25: **521** charts, 200 rows each (`data/final/part2_weekly_billboard200.csv`; `A_break_tests.csv`, `weeks` = 521).
- Issue dates are three days later (first 1963-08-10, last 2026-09-19).
- Confidence: **recomputed**.

### D8. Eligibility rules: **supported**, with one caveat
- **2014 year-only dropped:**
  - flag `2014_year_only_exclude_headline = (earliest_date == "2014")` at `code/11_collect_discographies.py:380`;
  - excluded in `headline_selection()`, `musicbrainz_helpers.py:466–470`;
  - also a month-only "2014-11" is excluded (line 485; 1 album, dated plan note).
  - The sample has 0 albums from 2014 with a year-only date.
- **Other year-only dates kept:** 1,663 year-precision albums in the sample, in every year except 2014 (275 in 2009 … 56 in 2019); 5,033 day- and 79 month-precision.
- **Minimum 6 tracks:** `musicbrainz_helpers.py:510`; the sample minimum is 6.
- **At least one official release:**
  - official releases are requested with `status=official` (`11_collect_discographies.py:250`);
  - candidates are built only from those releases, and groups with no dated official release are skipped (lines 343–346).
  - Studio album = primary type Album with no secondary types (line 210); Mixtape/Street is a secondary type, so it is excluded from the headline (Mixtape/Street robustness at line 211).
- **Caveat:** no rule excludes holiday albums, although the frozen plan lists them (surprise 8).
- **Minor note:** the earliest date within a release group is also chosen by text comparison (line 347), so a year-only release beats full dates in the same year. This is part of why 1,663 albums carry year precision.
- Confidence: **direct + recomputed**.

## E. Provenance

### E1. Kaggle Billboard dataset
- **File names:** `data/raw/billboard200.csv` (plus `hot100.csv`, `streaming.csv`, `digital.csv`, `radio.csv`) and `dataset-metadata.json`, which contains only `{"title": "Billboard Hot 100", "id": "ludmin/billboard", ...}`.
- **Version number:** **not found.** Searched `dataset-metadata.json`, all of `docs/`, `PROJECT_CONTEXT.md`, `README.md`, `archive/` (including `InitialAnalysisCode/kaggle_analysis.py`), and the code. No version or download log exists.
- **Download date:** not recorded.
  - The files' modification time is **2026-09-27 17:38 CDT**, probably when they were copied into the project.
  - The last chart in the file is stored 2026-09-16 (issue 2026-09-19), so the download was on or after about 2026-09-16.
  - Whether that matches version 131 must be checked on Kaggle's version history.
- Confidence: **not found** (version); **inferred** (date).

### E2. UK charts file
- **Answer (inferred):** `top_100_albums_1956_to_20250809.xlsx`, renamed `uktop100albums.xlsx`.
- **Evidence:**
  - The workbook's internal properties (`docProps/core.xml`) give created and modified **2025-08-09T20:43:30Z**, matching the "20250809" in that file name.
  - It has 3,602 sheets, the last being "Week 20250803". A file ending in 2024 could not contain 2025 weeks.
  - The project name differs from both repository names, so it was renamed.
- **Not found:** the GitHub repository is not mentioned anywhere in the project. Devlog §30 says only "the author added".
- **Download / copy date:** file modification time **2026-10-03 21:26 CDT** (copy into the project; the download date is not recorded).
- Confidence: **inferred**.

### E3. RIAA export
- **Answer:** export date **not found**.
- **Evidence:**
  - `data/raw/RIAARevenue.csv` modification time **2026-10-03 21:34 CDT** (copy into the project).
  - Columns: Disclaimer, Year, Format2 (category), Format, Units (empty), Revenue, CPI Adjustment.
  - It covers 1973–2025, 5 categories and 23 formats, with the CPI adjustment in 2025 dollars (factor 1.000 in 2025). So the export was made after RIAA had posted full-year 2025 data.
  - Devlog §29 records the author's description: copied from **RIAA's U.S. Sales Database (Tableau)**, i.e. the "U.S. Sales by Format" revenue view with all formats selected.
  - The companion `data/raw/4_Baseline.csv` is a Tableau parameter table (baseline/inflation toggle), not data.
- Confidence: **direct** (contents) and **not found** (date).

### E4. MusicBrainz collection
- **Dates** (UTC stamps inside the cached responses, plus file times; CDT = UTC−5):
  - Artist searches: `created` stamps from **2026-09-28 00:23 UTC to 02:08 UTC** (19:23–21:08 CDT on 27 Sept), 3,453 responses (3,361 plus 92 retries).
  - Zero-result component searches: 2026-09-28 02:17–02:19 UTC (67 responses).
  - Release-group browse cache: file written up to 2026-09-28 00:42 CDT.
  - Official-release cache: up to 2026-09-28 04:24 CDT. Discography API error log stamps run 06:01–07:43 UTC on 09-28.
  - **Collection window: 27 Sept 2026 (evening, CDT) to 28 Sept 2026 (early morning).** Consistent with devlog §12–16.
- **Endpoints:**
  - `https://musicbrainz.org/ws/2/artist` search: unfielded quoted query, `dismax=true`, `limit=100`, `fmt=json` (`musicbrainz_helpers.py:72, 111–125`).
  - `/ws/2/release-group?artist=<MBID>&type=album&inc=artist-credits&limit=100` (`11_collect_discographies.py:160–169`).
  - `/ws/2/release?release-group=<id>&status=official&inc=media+recordings+labels+artist-credits` (lines 248–255).
- **Rate limit:** at most 1 request per second (`REQUEST_INTERVAL_SECONDS = 1.0` for searches, `musicbrainz_helpers.py:74`; `REQUEST_INTERVAL = 1.05` s for the collector, `11_collect_discographies.py:33`).
- **User-Agent:** `Billboard200Paper/0.1 (academic metadata research; contact: project workspace)` (`musicbrainz_helpers.py:73`; `11_collect_discographies.py:32`).
- Confidence: **direct**.
