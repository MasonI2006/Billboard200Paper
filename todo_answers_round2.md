# Answers to `todo_round2_for_code_agent.md`

Prepared 2026-10-18 by Claude Code (Claude Opus 5.5). `main.tex`, `online_resource1.tex` and `references.bib` were not edited. The repository holds only the 8 October copies of the two `.tex` files and no `references.bib`, so replacements are written against the text quoted in the round-2 file, with the 8 October copy used for context. Please check each "old text" against Overleaf before pasting.

**What was run**
- No new estimation.
- One code change. `code/12_validate_musicbrainz_collection.py` now writes all nine genres to `musicbrainz_subgenre_balance.csv`; it previously wrote only the four streaming-heavy genres. This lets Table C1 be built from a results file.
- Rerun: `py -3.10 code/run_pipeline.py --only 12 13` (2026-10-18, cache-only). The four existing rows and every other output are byte-identical. Five rows were added: rock, country, Christian, jazz and classical.
- One read-only refit of an existing model (A4), to get a standard error. It is not saved to `results/`.
- Web sources were used for D1, D3, D4, D6 and E1–E5. They are listed at the end. billboard.com was not fetched (its robots.txt blocks AI agents), so Billboard announcement dates come from search results and secondary sources.

---

## 1. Conflicts and surprises

1. **A4: the $+7.8$-week triple difference applies to only 18 albums.**
   - The model has two treatment terms, streaming-heavy × post-U.S.-rule and streaming-heavy × post-UK-rule.
   - The post-U.S. indicator is also 1 for every album after March 2015. So $+7.8$ (bootstrap $p=0.43$) is the effect for albums that debuted in the 12 weeks between the two rules: 18 albums, 10 of them streaming-heavy.
   - For the 364 albums released after March 2015, the implied U.S.-minus-UK gain is the sum $+7.83-4.30=+3.5$ weeks (artist-clustered SE 2.01, $p=0.079$, no bootstrap). That is close to the main estimate.
   - The outcome is also different from the main estimate. It is weeks in the **U.S. top 100** minus weeks in the **UK top 100** in the first 52 weeks, for albums that debuted in the U.S. top 100 within eight weeks of their UK debut. The main estimate counts weeks on the full Billboard 200.
   - The current sentence misdescribes the estimate. Replacement in Sect. 2.
2. **D3: the Kaggle data are not version 131.**
   - The dataset (`ludmin/billboard`, "Billboard Hot 100 & more", Godefroy Lambert) updates every Wednesday and is now at version 179 (14 October 2026).
   - Our raw files contain charts through stored date 2026-09-16 and were on disk by 2026-09-27 17:38 CDT. Version 177 was created on 2026-09-30, so our copy is **version 175 or 176**.
   - Weekly versioning puts version 131 around November 2025, before charts our files contain.
   - The licence is **CC BY-NC-SA 4.0**.
3. **D1: more than half of RIAA "streaming" revenue is not on-demand.**
   - The streaming share (23/31/38 percent) includes RIAA's "Other Streaming": SoundExchange distributions and other payments from digital and customised radio services under statutory licences. That was $773$ million of $1,481$ million in 2014.
   - "On-demand streaming also grew" (line 278) is therefore inaccurate for this series and should change.
   - On-demand categories alone give 11.1, 14.9 and 21.2 percent of revenue in 2013–2015.
4. **E3: Sim et al. (2022) do not show that a high rank raises demand.**
   - They find that **entering** a streaming service's top-100 list raises song discovery by 11–13 percent.
   - Rank position **within** the top 100 shows no significant discontinuity.
   - Line 369 is supported. The claims at lines 72 and 80 that "appearing near the top" or "a high rank" raises demand need rewording.
5. **C3: the five long-album outcomes are not all thresholds, and the smallest Holm $p$ is 0.245.**
   - Three are threshold shares (15, 20 and 25 or more tracks). Two are the 75th and 90th percentiles of log track count.
   - The smallest Holm-adjusted $p$ is 0.2455, which rounds to **0.25**, not 0.24.
   - The unadjusted $p$ for the two quantile outcomes comes from an artist pairs cluster bootstrap (999 draws), not the genre wild bootstrap.
6. **E1: Schneider and Gros do support the diversity claim, but the bibliographic details need care.**
   - The paper finds that diversity on the U.S. Billboard album chart had been rising and "reversed" after the 2014/15 switch to the streaming-inclusive metric. So line 286 is broadly right.
   - Correct DOI: **10.1098/rsos.190944** (*R. Soc. Open Sci.* 6(8), 190944).
   - Their diversity measure is distinct albums per chart slot per year, roughly the inverse of mean weeks on the chart.
   - They also used Billboard's sales-only Top Album Sales chart after 2014. That chart is the missing control for Part 2 (PROJECT_CONTEXT §11).
7. **A5: the counts are 352 U.S. and 353 UK placebo dates**, not "about 350". The Online Resource 1 Fig. S3 caption also says "about 350".
8. **B2: `appendix_test_registry.tex` is not in the repository**, so I cannot see whether it contains a table. Both numberings are given. A longtable is likely, since `paperwriting/test_registry.md` is a 59-row table, and that would shift every table by one.
9. **D5: two items are not reproducible from the repository alone.**
   - `data/raw/` (142 MB) and `data/external/` (1.4 GB of MusicBrainz caches) are gitignored.
   - The Kaggle source and MusicBrainz both change over time. The replication package must include the cached responses and record the Kaggle version, or the script cannot reproduce the numbers.
10. **E2: Zanella, Cillo and Verona is 2022** (*SMJ* 43(7)), not 2021 as in the 8 October draft. The rule change they study is the Hot 100's March 2012 inclusion of streams.

---

## 2. Paste-ready replacements

**Line 235 (A1).** The figure is confirmed: 2.30 percent of the 13.0-track sample mean is 0.30 tracks. Remove the todo.
```latex
Relative to other genres, streaming-heavy genres lengthened their albums by 2.3 percent, which equates to about 0.3 tracks on an average album of 13.0 tracks.
```

**Line 239 (A2).** The estimate is the coefficient on log track count × post × streaming-heavy in a linear probability model of ever charting: $+0.177$ per log point, so $0.177\times\ln 1.1 = 1.7$ percentage points for a 10 percent longer album. The space before `\footnote` is removed.
```latex
Testing whether longer albums in streaming-heavy genres became more likely to reach the chart after the rule, we found that a 10 percent increase in an album's track count raised its probability of appearing on the Billboard 200 by 1.7 percentage points more in streaming-heavy genres than in other genres, which is significant at the 10\% level but not at the 5\% level (bootstrap $p=0.063$).\footnote{
```
(Keep the existing footnote text after `\footnote{`.)

**Line 286 (A3).** Both $p$-values are Newey–West. No placebo-date $p$ exists for the top-100 run.
```latex
Restricting the chart to its top 100 positions gives a larger fall in the new-entry share ($-3.6$ percentage points, $p<0.001$) and a smaller rise in the long-runner share ($+2.3$ percentage points, $p=0.059$).
```

**Line 333 (A4).** Two versions.
- (a) Uses only numbers in the results files.
- (b) Adds the $+3.5$ weeks for post-March-2015 albums. That figure comes from a refit of the same model and is not yet in a results file. If you choose (b), I can add it to step 31's output.

```latex
% (a)
A triple difference that compares the same albums' weeks in the top 100 of both charts gives $+7.8$ weeks in the U.S. relative to the UK for albums released between the two rule dates, but this estimate rests on 18 albums and its bootstrap $p$-value is 0.43.
% (b)
A triple difference that compares the same albums' weeks in the top 100 of both charts gives $+7.8$ weeks in the U.S. relative to the UK for the 18 albums released between the two rule dates (bootstrap $p=0.43$) and $+3.5$ weeks for albums released after the UK rule ($p=0.079$), so holding the album fixed leaves an imprecise estimate of similar size to the main one.
```

**Line 207 (A5)**
```latex
First, because weekly shares are persistent and seasonal, we compare the actual jump with jumps estimated at 352 placebo rule dates between 2011 and 2018.
```
**Table 2 rows (A5)**
```latex
\quad Placebo-date $p$ (352 placebo dates)          & 0.003 & 0.076 \\
```
```latex
\quad Placebo-date $p$ (353 placebo dates)          & 0.55 & 0.94 \\
```

**Line 115 (D1, with B1).** The new sentence names the series accurately and keeps the 23/31/38 percent figures.
```latex
Streaming's share of U.S. recorded-music revenue, which in the RIAA data covers paid subscriptions, free ad-supported services and payments from digital and customised radio services under statutory licences, rose smoothly from 23 percent in 2013 to 31 percent in 2014 and 38 percent in 2015 (Online Resource 1, Fig.~S2) \citep{riaa_sales_database}.
```
**Line 278 (D1).** "On-demand" must change. Replace "On-demand streaming also grew" with:
```latex
Streaming revenue also grew
```

**Line 333 (B1).** Use `Fig.~S4` for the leave-one-genre-out figure.

**Lines 149, 197 and 241 (B2).** If `appendix_test_registry.tex` contains a table (likely):
```latex
% line 149
Table~S2
% lines 197 and 241
Table~S3
```
If it does not, use `Table~S1` (line 149) and `Table~S2` (lines 197 and 241).

**Line 84 (E1).** Completing "The closest evidence to ours is \citet{schneider2019five}, who ...":
```latex
The closest evidence to ours is \citet{schneider2019five}, who show that the number of distinct albums reaching the Billboard album chart each year had been rising since the early 1990s and that this trend reversed after the chart began counting streams in 2014.
```
**Line 286 (E1).** Clause replacing "that diversity on the Billboard 200 fell after streams were added":
```latex
that the number of distinct albums reaching the Billboard album chart each year, which had been rising, fell after the chart began counting streams \citep{schneider2019five}
```

**Line 80 (E2).** Clause for "incumbent firms respond when the information a market reports changes":
```latex
incumbent record labels changed what they released after the Billboard Hot 100 began counting streams in 2012, which revealed rising demand for novelty and variety \citep{zanella2022whatever}
```

**Line 369 (E3).** Supported as written ("chart rankings on streaming services shape which songs listeners discover"). Optional, more precise version:
```latex
entering a streaming service's top-100 chart raises how many listeners discover a song \citep{sim2022bestseller}
```
**Lines 72 and 80 (E3).** Replace "appearing near the top of them raises demand" with:
```latex
appearing on them raises demand
```
Replace "a high rank raises demand ... for music on streaming services" with:
```latex
being listed on a streaming service's top-100 chart raises song discovery, although rank within the list does not \citep{sim2022bestseller}
```

**Data availability (backmatter, line 405; D6)**
```latex
The weekly Billboard 200 charts are from a public compilation on Kaggle \citep{kaggle_billboard} (version \todo{175 or 176}, licensed under CC BY-NC-SA 4.0), and the weekly UK Official Albums Chart is from a public scrape of the Official Charts Company website \citep{uktop100scrape}. Neither is redistributed, because the underlying charts belong to Billboard and the Official Charts Company, but both are available from the sources cited. Album, release and artist data are from the MusicBrainz web service \citep{musicbrainz}, whose core data are in the public domain (CC0) and whose tags, from which our genre labels are derived, are licensed under CC BY-NC-SA 3.0. U.S. revenue by format is from the RIAA U.S. Sales Database \citep{riaa_sales_database}, and genre streaming intensities are from the published Nielsen 2014 U.S. year-end music report \todo{cite}. The cached MusicBrainz responses, the album-level analysis samples with genre labels and all derived tables are available at \todo{repository DOI} under CC BY-NC-SA 4.0.
```

**Code availability (backmatter, line 406; D5)**
```latex
All code is available at \todo{repository DOI}. One script, \texttt{code/run\_pipeline.py}, reproduces every estimate, table and figure in the article and in Online Resource 1 from the cached source data, without new requests to the MusicBrainz web service, in about three and a half hours on a desktop computer.
```

---

## 3. Item-by-item answers

### A1. Point estimate in tracks
- **Answer:** 0.30 tracks.
  - Conversion: the sample mean track count (13.00, all 6,775 albums) × $(e^{\beta}-1)$, with $\beta=0.02275$, giving 2.30 percent.
  - The 90% CI in tracks ($-0.03$ to $+0.63$) uses the same conversion.
  - "About 0.3 tracks" is correct at line 235 and at line 78.
  - Using the streaming-heavy pre-rule mean (13.99) instead would give 0.32.
- **Evidence:** `results/final_checks/equivalence.csv` row 2 (`tracks` = 0.2992, `percent` = 2.301, `mean_tracks` = 13.0018). Formula at `code/32_final_checks.py`, function `equivalence()` (`to_tracks = m * (exp(x) - 1)`, `m` = mean of `standard_tracks` in `analysis_sample.csv`).
- **Confidence:** read directly.

### A2. Selection test effect size
- **Answer:**
  - **Outcome:** `charted` = 1 if the album ever appears on the Billboard 200. It is matched on MusicBrainz artist ID and normalised title against every week in the Kaggle file; 3,991 of 6,775 albums chart.
  - **Model:** linear probability model `charted ~ ln_tracks + ln_tracks:post + ln_tracks:heavy + ln_tracks:post:heavy + post:heavy + C(genre) + C(year)`.
  - **"Longer"** is continuous log track count, not a threshold.
  - **Estimate:** $+0.1771$ per log point of tracks (artist-clustered SE 0.0934, $p=0.058$), bootstrap $p=0.0627$ (genre Webb, 9,999 draws).
  - **In plain units:** a 10 percent longer album gives $0.177\times\ln(1.1)=0.0169$, i.e. 1.7 percentage points. One extra track on a 13-track album gives 1.3 percentage points.
- **Evidence:** `results/part1_album_length/secondary/secondary_checks.csv` row 4 ("3 selection test"). Specification at `code/18_part1_secondary_checks.py:20–22` (`SELECTION_RHS`, `TRIPLE`); charted flag at lines 32–55.
- **Confidence:** read directly; the conversion is arithmetic.

### A3. Top-100 restriction
- **Answer:**
  - New-entry share $-3.55$ percentage points (Newey–West SE 0.68, $p=1.6\times10^{-7}$, so $p<0.001$).
  - 52+-week share $+2.31$ (SE 1.22, Newey–West $p=0.0587$).
  - $-3.6$, $+2.3$ and 0.059 are confirmed, and 0.059 is Newey–West.
  - No placebo-rank $p$ was computed for the top-100 series. `uk_comparison_placebo_rank.csv` covers only the U.S. 200-position and UK series.
- **Evidence:** `results/part2_incumbency/uk_comparison.csv`, rows "ref U.S. top 100 at own rule" (columns `tau`, `tau_se`, `tau_p_nw`). Code: `code/29_uk_comparison.py:113`.
- **Confidence:** read directly.

### A4. Triple-difference scale
- **Answer:** $+7.8$ is in weeks, but it is **not the main estimate's outcome or scope**.
  - **Outcome:** weeks in the U.S. **top 100** in the 52 weeks after U.S. debut, minus weeks in the UK top 100 in the 52 weeks after UK debut.
  - **Sample:** albums on both charts that debuted in the U.S. top 100 within 8 weeks of their UK debut (2010–2018). 986 albums with Part 2b genre labels (353 streaming-heavy, 517 artists).
  - **Model:** `diff ~ heavy×post_US + heavy×post_UK + C(genre) + C(year)`, with post_US = debut on or after 2014-12-07 and post_UK = on or after 2015-03-01.
  - **Estimates:**
    - heavy × post_US $+7.83$ weeks (SE 4.16, artist $p=0.060$, genre bootstrap $p=0.431$);
    - heavy × post_UK $-4.30$ (SE 4.20, $p=0.306$).
  - **Scope.** Because post_US = 1 for all post-UK-rule albums, $+7.83$ is the effect for albums that debuted between the two rules. There are 18 of them: 10 streaming-heavy, with a mean U.S.-minus-UK difference of 9.7 weeks, and 8 other. For the 364 albums after March 2015, the effect is the sum, **$+3.53$ weeks (SE 2.01, $p=0.079$)**. That figure comes from a refit of the identical model; it reproduces both coefficients exactly.
- **Evidence:**
  - `results/part2_incumbency/matched/C_genre_triple_difference.csv` row 2.
  - Sample and outcome: `code/31_matched_album_tests.py:144–162` (`album_sample`; `us100 = us[us["Rank"] <= 100]`; `diff = us_weeks52 - uk_weeks52`) and 172–190 (`test_c`).
  - Group counts from `matched/B_album_sample.csv` joined to the Part 2b labels.
- **Confidence:** read directly (coefficients and definitions); refit (the sum, SE and period counts).

### A5. Placebo-date counts
- **Answer:** **352** placebo dates for the U.S. series, for both shares; **353** for the UK series, for both shares and both test dates. The matched-catalogue placebo also uses 353.
- **Evidence:** `results/part2_incumbency/uk_comparison_placebo_rank.csv`, column `n_fake_dates`. Window and exclusion: `code/29_uk_comparison.py:90–98` (dates 2011-01-01 to 2018-12-31, excluding dates within 26 weeks of any of the four rule dates).
- **Note:** the Online Resource 1 Fig. S3 caption also says "about 350 placebo dates". Suggested: "352 placebo dates".
- **Confidence:** read directly.

### B1. Figure references
- **Answer:** confirmed. In `online_resource1.tex` (8 October copy) the figure environments appear in the order:
  - `figA4_track_count_thresholds` (S1, Part 1 section);
  - `figA1_riaa_streaming_growth` (S2);
  - `figA2_placebo_dates` (S3, both in the Part 2 section);
  - `figA3_leave_one_genre_out` (S4, Part 2b section).

  So line 115 should use `Fig.~S2` and line 333 `Fig.~S4`. The 8 October `main.tex` still says `Fig.~S1` for the RIAA figure.
- **Confidence:** read directly from the local copy. If the Overleaf copy has moved figures, recheck.

### B2. Table references
- **Answer:** depends on `appendix_test_registry.tex`, which is not in the repository.
  - **With a table in it:** C1 = S2, C2 = S3, C3 = S4, C4 = S5, C5 = S6, C6 = S7. Line 149 → `Table~S2`; lines 197 and 241 → `Table~S3`.
  - **Without:** S1–S6. Line 149 → `Table~S1`; lines 197 and 241 → `Table~S2`.
- **Recommendation:** each table file has a `\label{tab:S_...}`, so inside Online Resource 1 use `\ref{tab:S_part1}` and so on. For `main.tex`, the `xr` package (`\externaldocument{online_resource1}`) would let the numbers update automatically.
- **Confidence:** not found (registry file); the numbering logic is certain.

### C1–C6. Tables
See Sect. 4 for files and `\input` lines.

| Table | Content | Checks against the paper |
|---|---|---|
| C1 | Unmatched roster artists by genre | 17.9% (streaming-heavy), 16.5% (other) and 577 of 994 unmatched with no genre: all reproduce. |
| C2 | Part 1 robustness | The range $-1.6$ to $+2.9$ percent is defined by "including mixtapes" ($-1.59$) and "drop albums before first chart debut" ($+2.87$). It spans the eight checks with the log-track outcome and the streaming-heavy indicator: both career-position definitions, artist FE, drop pre-debut, mixtapes, the two windows and excluding electronic. Excluded from the range: continuous intensity (different treatment) and running time, more than 12 tracks and 18 or more tracks (different outcomes). The **twelve** checks are the eleven in the `online_resource1.tex` list plus the second career-position definition (since 2009); `test_registry.md` rows 8–19 count it the same way. |
| C3 | Long-albums family | Exact definitions are in the table. Smallest Holm $p$ is 0.245 (A4), not 0.24. "Five outcomes defined by long-album thresholds" is inaccurate. Suggested: "five upper-tail outcomes (the shares of albums with 15, 20 and 25 or more tracks and the 75th and 90th percentiles of track count)". |
| C4 | Part 2 robustness | RIAA cells give $-2.6$ to $-3.3$ and $+5.0$ to $+5.6$. The July 2018 break SE is not stored in `D_with_2018_break.csv` (shown as "--"). The matched catalogue panel gives level-only and with-trend-change versions. |
| C5 | Part 2b robustness | Bootstrap $p$ for weeks in the first 26 and still-on-chart-at-26 uses 1,999 draws, not 9,999 (`code/22_part2b_analyze.py`: `B=9999 if y == "weeks52" else 1999`). The note says so. The +3.5 sentence carries a `\todo` for your decision (A4). |
| C6 | Superseded estimates | From devlog §24–26 and the dated notes in `docs/analysis_plan.md`. Fix commits: 2f1371b, 3835fa7, 2f83fc6. The earlier Mixtape/Street correction (devlog §20, $-0.0487\to+0.0356$) predates the three listed errors and is not in the table; add it if you want a complete history. |

**Lead-in sentences** (style rules applied):
- C1: "Table~\ref{tab:S_unmatched} reports how many roster artists were matched to MusicBrainz in each genre group and genre, and shows that the share left unmatched is similar for streaming-heavy and other genres."
- C2: "Table~\ref{tab:S_part1} reports the twelve secondary checks in the Part 1 plan, the remaining secondary checks and three exploratory checks, each as the streaming-heavy $\times$ post-rule coefficient."
- C3: "Table~\ref{tab:S_longalbums} reports the five upper-tail outcomes fixed after the 18-or-more-tracks result, with $p$-values adjusted for testing all five."
- C4: "Table~\ref{tab:S_part2} reports the jumps in the new-entry and 52+-week shares under placebo dates, alternative samples and controls, the pooled U.S. and UK test, the song charts and the matched catalogue albums."
- C5: "Table~\ref{tab:S_part2b} reports the Part 2b estimate for other outcomes, with further controls and fixed effects, and on the UK chart."
- C6: "Table~\ref{tab:S_superseded} lists the estimates changed by the three implementation corrections described in Sect.~4.4 of the article, before and after each correction."

### D1. RIAA streaming categories
- **Answer:**
  - In the export, the "Streaming" category is the sum of four formats: Paid Subscriptions (Premium), Paid Subscriptions (Non-Premium; \$0 in 2013–2015), Free Streaming, and Other Streaming.
  - 2014: \$423.6M + \$0 + \$283.8M + \$773.4M = \$1,480.8M of \$4,747.6M total (31.2 percent).
  - **RIAA definitions** (riaa.com/u-s-sales-database):
    - **Free Streaming** (formerly "On-Demand Streaming – Ad-Supported"): "Ad-supported audio and music video services that do not operate under statutory licenses".
    - **Other Streaming** (new in 2025, combining "SoundExchange Distributions" and "Other Ad-Supported Streaming"): "Estimated payments to performers and copyright holders for digital and customized radio services … operating under statutory licenses, including SoundExchange distributions and similar direct deals".
  - The series therefore **includes non-interactive radio-style streaming**, and that part is the largest component: 52 percent of streaming revenue in 2014.
  - "On-demand" at line 278 must change.
  - On-demand-only shares (premium + non-premium + free) of total revenue: 11.1% (2013), 14.9% (2014), 21.2% (2015).
- **Evidence:** `data/final/riaa_revenue_long.csv` (category Streaming, 2013–2015); `code/27_riaa_revenue.py:44`. RIAA definitions from the U.S. Sales Database page (URL below).
- **Confidence:** read directly (amounts and RIAA wording). The 2025 definitions are applied to the 2013–2015 values: the export uses the 2025 category names throughout.

### D2. RIAA export details
- **Answer:**
  - **Export date: not found.**
  - File: `data/raw/RIAARevenue.csv`. It is a Tableau crosstab export (UTF-16, tab-separated) of the RIAA U.S. Sales Database revenue-by-format view: 1973–2025, five categories, 23 formats, nominal revenue and a "CPI Adjustment" column in 2025 dollars.
  - It was copied into the project on 2026-10-03 21:34 CDT (file modification time).
  - Its contents (2025 data; the 2025 category name "Other Streaming") show it was exported after RIAA published full-year 2025 figures and revised its categories.
  - For the bib entry, an "accessed" date of 3 October 2026 is the latest defensible date; confirm with your browser history.
- **Evidence:** file metadata; devlog §29; `code/27_riaa_revenue.py` docstring.
- **Confidence:** not found (date); read directly (contents).

### D3. Kaggle dataset
- **Answer:**
  - Title "Billboard Hot 100 & more"; owner and creator **Godefroy Lambert** (`ludmin`); licence **CC BY-NC-SA 4.0**.
  - "Data is refreshed every Wednesday at 02:00 (server time)".
  - Current version **179** (2026-10-14).
  - Versions 176 and 177 were created on 2026-09-23 and 2026-09-30.
  - Our files end at stored chart date 2026-09-16 and were on disk at 2026-09-27 17:38 CDT, so they are **version 175 or 176, not 131**. Kaggle's version page shows each version's file preview, which would settle which one.
  - **Download date:** not recorded; on or before 2026-09-27.
- **Evidence:** Kaggle API metadata (`kaggle.com/api/v1/datasets/view/ludmin/billboard`); `data/raw/dataset-metadata.json` (id only); file modification times; last stored date in `billboard200.csv`.
- **Confidence:** read directly (licence, versions); inferred (which version).

### D4. UK chart file
- **Answer:**
  - `top_100_albums_1956_to_20250809.xlsx`, renamed `uktop100albums.xlsx`.
  - The repository holds both candidate files under an **Apache-2.0** licence (code). Its README says "This project is for educational and research purposes" and asks users to "respect the Official Charts Company's terms of service".
  - Download date: not recorded. The file was copied into the project on 2026-10-03 21:26 CDT.
- **Evidence:**
  - The workbook's internal properties give created and modified 2025-08-09T20:43:30Z, matching "20250809".
  - It has 3,602 sheets ending "Week 20250803". A 2024 file could not contain 2025 weeks.
  - Repository page (URL below).
- **Confidence:** inferred (strong).

### D5. Code availability
- **Answer:** yes, with conditions.
  - **Command:** `py -3.10 code/run_pipeline.py` (cache-only by default). It runs steps 01–33 in list order, skipping step 15 (the one-time genre hand-check sheet).
  - **Outputs:** `data/interim/`, `data/final/`, every CSV in `results/`, and `paperwriting/parameters.md` and `paperwriting/figures/` (step 33).
  - **Runtime:** a few minutes for the data steps, plus about 3.3 hours of bootstraps.
  - **Requirements:** Python 3.10 with pandas, numpy, statsmodels, scipy, patsy, matplotlib and openpyxl. It also needs `data/raw/` (142 MB) and `data/external/` (1.4 GB of MusicBrainz caches and tables). Both are gitignored, so they must be in the replication package.
  - **Not produced by the script:**
    1. the 1.7 percentage points in A2 (arithmetic on a produced coefficient);
    2. the $+3.5$ weeks in A4 (refit), if used;
    3. hand-check verdicts. The 100-album genre sheet holds manual columns and is not regenerated (step 15 skipped). The 50/50 U.S.–UK match check is recorded only in devlog §33; `match_handcheck_sample.csv` has no verdict column.
    4. the Nielsen 2014 intensity ratios, which are inputs hard-coded at `code/load_clean_data.py:31–34`;
    5. institutional dates and facts.
  - Without the cached responses, `--allow-api` would refetch from MusicBrainz for hours, and the results would differ because MusicBrainz data change. The same holds for re-downloading the weekly-updated Kaggle data.
- **Confidence:** read directly (`code/run_pipeline.py`, `.gitignore`, folder sizes).

### D6. Data availability
- **Answer:**

| Source | Terms found | Shareable from the repository |
|---|---|---|
| Kaggle Billboard compilation | CC BY-NC-SA 4.0 (Kaggle metadata); the underlying charts are Billboard's | Derived aggregates (weekly shares) and album-level samples; the raw chart files are better cited than redistributed |
| UK scrape | Code Apache-2.0; README asks users to respect the Official Charts Company's terms | Derived weekly shares; not the workbook |
| MusicBrainz | Core data CC0; "tags (including genre associations)" are supplementary data under CC BY-NC-SA 3.0 | Cached responses and genre labels, with attribution, non-commercially, share-alike |
| RIAA | No licence on the database page; questions go to research@riaa.com | Annual shares as reported facts; not the export |
| Nielsen 2014 report | Not in the repository; published report | The nine ratios as cited |

  Draft statement in Sect. 2. CC BY-NC-SA 4.0 is suggested for the shared derived data, to satisfy both share-alike licences.
- **Confidence:** read directly from the source pages; the redistribution advice is a judgement, not a legal opinion.

### E1. Schneider and Gros (2019)
- **Answer:** close evidence; line 286 is broadly supported.
  - Full text read on PubMed Central (PMC6731713). Citation: *Royal Society Open Science* 6(8), 190944, DOI 10.1098/rsos.190944.
  - Sect. 2: "A major update occurred for the Billboard charts in 2014/15", to "a ranking based on a multi-metric consumption rate".
  - Sect. 2.1: US and German sales-chart "chart diversity increases rapidly since the early 1990s", and for the multi-metric version "the trend to become more diverse reversed".
  - The abstract and introduction say the inclusion of streaming "affects chart diversity adversely".
  - **Diversity** = distinct albums listed per year ÷ chart slots.
  - Post-2014 data run to about 2018. For continuity they use Billboard's sales-only Top Album Sales chart, which is relevant to the missing Part 2 control.
  - They do not test the rule causally. "Billboard 200" is implied rather than named for the multi-metric chart.
- **Confidence:** read the full text.

### E2. Zanella, Cillo and Verona (2022)
- **Answer:**
  - *Strategic Management Journal* 43(7), 1258–1286 (online 2 January 2022), "Whatever you want, whatever you like: How incumbents respond to changes in market information regimes".
  - **Setting:** the U.S. Billboard **Hot 100** adding streaming, March 2012 (per Bocconi's summary).
  - **Outcomes:** record labels' release strategies.
  - **Finding:** "the inclusion of streaming reveals increasing demand for novelty and variety". Incumbents with broad experience proliferate across niches, those with focused experience increase novelty, and breadth is associated with better performance.
  - Replacement clause in Sect. 2.
- **Evidence:** Crossref record and Research Summary; Bocconi news item.
- **Confidence:** abstract and research summary read; full text not accessed.

### E3. Sim et al. (2022)
- **Answer:**
  - *Journal of Economic Behavior & Organization* 194, 550–567.
  - **Design:** a regression discontinuity at the top-100 cutoff of a streaming platform's hourly bestseller list.
  - **Findings:** "being added to the top 100 charts increases song discovery by 11–13%". Rank within the top 100 shows no significant discontinuity. Prior popularity does not moderate the effect.
  - The platform and country are not stated in the abstract.
  - Line 369 is supported. Lines 72 and 80 overstate it when they say "a high rank" or "near the top"; replacements in Sect. 2.
- **Evidence:** RePEc/IDEAS abstract page.
- **Confidence:** abstract read; full text not accessed.

### E4. Other Introduction citations
| Key | Paper | Supports the sentence? | Evidence |
|---|---|---|---|
| `elberse2010bye` | Elberse, "Bye-bye bundles: The unbundling of music in digital channels", *J. Marketing* 74(3), 107–123 | Yes (unbundling). Weekly sales 2005–2007; "Fueled by digital distribution, unbundling is prevalent…" | Abstract (OpenAlex) |
| `danaher2014empirical` | Danaher, Huang, Smith and Telang, "An empirical analysis of digital music bundling strategies", *Mgmt Sci* 60(6), 1413–1433 | Yes. "unbundling albums outperforms 'album-only' pricing policies" | Abstract (OpenAlex) |
| `hiller2017rise` | Hiller and Walter, "The rise of streaming music and implications for music production", *Rev. Network Econ.* 16(4), 351–385 | Yes. Model in which streaming leads musicians "to release fewer songs, but at a higher quality" and completes "the unbundling process" | Abstract (OpenAlex) |
| `datta2018changing` | Datta, Knox and Bronnenberg, "Changing their tune: How consumers' adoption of online streaming affects music consumption and discovery", *Marketing Science* 37(1), 5–21 | Yes, by title (consumption and discovery) | **Abstract not accessed**; title and metadata only |
| `ivaldi2024displacement` | Ivaldi, Nicolle, Verboven and Zhang, "Displacement and complementarity in the recorded music industry: evidence from France", *JCE* 48(1), 43–94 (online 2023) | Yes. "streaming displaces digital sales" and has "a promotional effect on physical sales" | Abstract (Crossref) |
| `mckenzie2021takes` | McKenzie, Crosby and Lenten, "It takes two, baby! Feature artist collaborations and streaming demand for music", *JCE* 45(3), 385–408 | Partly. It studies one driver (collaborations); "drivers of streaming demand" is broad. Suggested: "how collaborations between artists affect streaming demand" | Title and metadata; **abstract not accessed** |
| `jensen2024rethinking` | Jensen, "Rethinking royalties: alternative payment systems on music streaming platforms", *JCE* 48(3), 439–462 | Yes, by title (how streaming revenue is paid) | Title and metadata; **abstract not accessed** |
| `strobl2000dynamics` | Strobl and Tucker, "The dynamics of chart success in the U.K. pre-recorded popular music industry", *JCE* 24(2), 113–134 | Yes. "British album chart listings … 1980 to 1993"; album type, season and "initial popularity" predict chart survival | Abstract (RePEc) |
| `bhattacharjee2007effect` | Bhattacharjee, Gopal, Lertwachara, Marsden and Telang, "The effect of digital sharing technologies on music markets: A survival analysis of albums on ranking charts", *Mgmt Sci* 53(9), 1359–1374 | Yes. "significantly reduced chart survival except for those albums that debut high on the charts" | Abstract (OpenAlex) |
| `lech2025harder` | Lech, Lehmann and Juul, "Is it getting harder to make a hit? Evidence from 65 years of US music chart history", *EPJ Data Science* 14, 67 (published 2 September 2025) | Yes, for the **Hot 100** (songs, from 1958), not albums. Year is 2025 (2024 was the preprint) | Crossref and abstract |
| `gourevitch2023billboard` | Gourévitch, "Billboard 200: The lessons of musical success in the U.S.", *Music & Science* (2023) | Yes. Billboard 200 "for the period 1963–2019"; "success is more diverse than it was a few decades ago" | Abstract (Semantic Scholar) |

### E5. Announcement dates
| Key | Date | Confidence |
|---|---|---|
| `billboard2009makeover` ("Billboard 200 Undergoes Makeover") | **17 November 2009** | Secondary: Wikipedia "Billboard 200" dates the Billboard article to this day. Effective with the issue dated 5 December 2009. Billboard page not fetched. |
| `billboard2018weighting` | **Not confirmed**: May 2018. The earliest dated coverage found is 3 May 2018; effective with the release week of 29 June–5 July 2018 | Leave as a todo |
| `billboard2019video` | **13 December 2019** | Secondary: dated coverage the same day (Tubefilter, 13 December 2019). Effective with the chart dated 18 January 2020 |
| `occ2015streams` | **11 February 2015** | Read directly. officialcharts.com, "By Rob Copsey, 11 February 2015"; URL below |

---

## 4. New files created (Section C)

All in `online_resource1_tables/`, using booktabs with `\botrule`, captions without a final full stop, and labels `tab:S_*`. They were checked for balanced braces and equal cell counts per row. They were **not compiled**, because no LaTeX installation is available here.

| File | Table | `\input` line | Where it goes in `online_resource1.tex` |
|---|---|---|---|
| `tab_unmatched_by_genre.tex` | C1 | `\input{online_resource1_tables/tab_unmatched_by_genre}` | Data construction section, after the itemize. Replace the todo in the "Pre-rule roster" bullet with "(Table~\ref{tab:S_unmatched})". |
| `tab_part1_checks.tex` | C2 | `\input{online_resource1_tables/tab_part1_checks}` | Part 1 robustness, in place of the `\todo{Table: all 12 frozen-plan checks …}` paragraph |
| `tab_long_albums.tex` | C3 | `\input{online_resource1_tables/tab_long_albums}` | Long albums follow-up subsection, in place of `\todo{Family A1--A5 …}`, before Fig. S1 |
| `tab_part2_robustness.tex` | C4 | `\input{online_resource1_tables/tab_part2_robustness}` | Part 2 robustness, in place of `\todo{Placebo-date table; …}` |
| `tab_part2b_robustness.tex` | C5 | `\input{online_resource1_tables/tab_part2b_robustness}` | Part 2b robustness, in place of `\todo{Weeks in first 26; …}` |
| `tab_superseded.tex` | C6 | `\input{online_resource1_tables/tab_superseded}` | Last section, in place of `\todo{The three bugs …}` |

Upload the folder to the Overleaf project, or drop the `online_resource1_tables/` prefix if the files sit next to `online_resource1.tex`. C4 is long and set in `\footnotesize`. If it overflows a page, split it after panel D, or change it to a `longtable`.

**Also in `online_resource1.tex`** (for you to apply):
- The first data-construction bullet's todo can go. The pre/post split for the weekly series uses the stored date 2014-12-10, and Part 1 uses release dates from 24 November 2014 (round 1, A2).
- The UK-chart bullet's todo: the documented checks are "every reconstructed number one has a peak position of 1 in the source rows, and the weeks around the rule were spot-checked against the published record" (round 1, D5).
- Fig. S3 caption: "about 350 placebo dates" → "352 placebo dates".

---

## 5. Still open

- **For your decision:**
  - A4 version (a) or (b); the `\todo` in the C5 note;
  - whether to add the Mixtape/Street correction to C6;
  - the table numbering (B2) once you check `appendix_test_registry.tex`.
- **Not found:**
  - RIAA export date (D2);
  - Kaggle download date and exact version, 175 or 176 (D3);
  - UK file download date (D4);
  - the exact day of the 2018 Billboard announcement (E5).
- **Not accessed (abstract or full text):** Datta et al. (2018), McKenzie et al. (2021) and Jensen (2024), checked by title and metadata only. Zanella et al. (2022) and Sim et al. (2022): abstracts only.
- **Section F (author only):** AI tools and versions (Sect. 4.5, line 224); acknowledgements, funding, competing interests, author contributions; the title.
- **Still open from round 1:** the two empty bootstrap cells in Table 4 (debut-rank controls and artist fixed effects). Suggested: mark them "--" with a note that the bootstrap was computed only for the main specification and the rows shown.

## Sources
- [Schneider and Gros (2019), PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC6731713/)
- [Zanella, Cillo and Verona (2022), Crossref record](https://api.crossref.org/works/10.1002/smj.3372); [Bocconi news item](https://www.unibocconi.it/it/news/serve-uno-shock-informativo-far-capire-alle-imprese-che-la-musica-sta-cambiando)
- [Sim et al. (2022), RePEc abstract](https://ideas.repec.org/a/eee/jeborg/v194y2022icp550-567.html)
- [Lech et al. (2025), Crossref record](https://api.crossref.org/works/10.1140/epjds/s13688-025-00571-9)
- [Strobl and Tucker (2000), RePEc abstract](https://ideas.repec.org/a/kap/jculte/v24y2000i2p113-134.html)
- OpenAlex records for [Elberse](https://api.openalex.org/works/doi:10.1509/jmkg.74.3.107), [Danaher et al.](https://api.openalex.org/works/doi:10.1287/mnsc.2014.1958), [Hiller and Walter](https://api.openalex.org/works/doi:10.1515/rne-2017-0064), [Bhattacharjee et al.](https://api.openalex.org/works/doi:10.1287/mnsc.1070.0699), [McKenzie et al.](https://api.openalex.org/works/doi:10.1007/s10824-020-09396-y)
- Crossref records for [Ivaldi et al.](https://api.crossref.org/works/10.1007/s10824-023-09471-0) and [Jensen](https://api.crossref.org/works/10.1007/s10824-024-09507-z); Semantic Scholar for [Gourévitch](https://api.semanticscholar.org/graph/v1/paper/DOI:10.1177/20592043231186692)
- [RIAA U.S. Sales Database (category definitions)](https://www.riaa.com/u-s-sales-database/)
- [Kaggle dataset metadata](https://www.kaggle.com/api/v1/datasets/view/ludmin/billboard)
- [UkTop100Scrape repository](https://github.com/JackDanHollister/UkTop100Scrape)
- [MusicBrainz data licence](https://musicbrainz.org/doc/About/Data_License); [core and supplementary data](https://musicbrainz.org/doc/MusicBrainz_Database)
- [Official Charts Company, 11 February 2015](https://www.officialcharts.com/chart-news/uk-official-albums-chart-to-include-streaming-data-for-first-time-3479/)
- [Wikipedia, Billboard 200 (2009 announcement date)](https://en.wikipedia.org/wiki/Billboard_200); [Tubefilter, 13 December 2019](https://tubefilter.com/2019/12/13/youtube-consumption-billboard-200-albums-chart/); [RAIN News on the 2018 weighting](https://rainnews.com/billboard-shifts-streaming-equivalents-giving-more-weight-to-paid-subscriptions/)
