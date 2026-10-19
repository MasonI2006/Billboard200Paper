# Paper TODOs that can be answered from the code, data and results

Context: `main.tex` is the draft of "Changing the Scoreboard: How Counting Streams Reshaped the Billboard 200 but Not the Albums on It" (Journal of Cultural Economics). Red `\todo{...}` markers in the LaTeX are things the author must confirm. The items below can be settled from the replication code, data files, results CSVs and plan documents in this project.

## Rules for the agent

1. **Do not edit `main.tex`, `online_resource1.tex` or `references.bib`.** Only read, and re-run scripts where an item says so.
2. **Do not guess.** If the code or data does not answer a question, say "not found" and list where you looked.
3. For every item, report the **answer, the exact file and line or CSV row it came from, and a confidence note** (for example "read directly from results_main.csv" versus "inferred").
4. If you rerun a script, record the command, the date, and whether any output differs from what `parameters.md` or `devlog.md` records. Flag every difference rather than overwriting numbers silently.
5. Write all answers into one file, `todo_answers.md`, using the item numbers below.
6. Numbers already in `parameters.md` are the target of "match to the results". If a results CSV and `parameters.md` disagree, report both.

---

## A. Dates and definitions to confirm in the code

### A1. July 2018 break date (main.tex, Sect. 2.1 footnote)
The paper says the first chart under the paid/ad-supported weighting is dated 14 July 2018 (tracking week 29 June to 5 July 2018). Which date does the code use for the "July 2018 extra break" test?
- Look in: the Part 2 / Q1 script that produces `results/part2_incumbency/D_with_2018_break.csv`; grep for `2018` in all scripts.
- Report: the exact date string or `pd.Timestamp` the code uses, the date convention (stored date, which is 3 days before the issue date, or issue date), and the file and line.
- Note: the source stores charts 3 days before Billboard's issue date, so 14 July 2018 (issue) would be stored as 11 July 2018.

### A2. Which date defines "post" in each analysis
The paper uses three definitions and must state them correctly.
- **Part 1** (`Post_a`): release date on or after 2014-11-24.
- **Part 2b** (`PostDebut_a`): debut chart date on or after the first chart under the rule. In `part2b_album_runs.csv`, `post=1` for 1,368 albums and `post=0` for 3,149, and 23 albums with debut on or after 2014-11-24 are coded `post=0`.
- **Part 2** (`Post_w`): the first chart under the rule (stored 2014-12-10).
Confirm in the code the exact cutoff constants for each (and whether the 2014-12-10 stored date or the 2014-12-13 issue date is used for the weekly series), and confirm that the 23 albums above are the albums with debut dates from 2014-11-24 to 2014-12-09. Report the cutoff for each.

### A3. Part 1 plan frozen date (main.tex, Sect. 4.4)
The paper says "Part 1 plan frozen 27 September 2026". Find the plan file (for example `q1_analysis_plan.md`, `part1_plan.md`) and report its recorded freeze date, from the text, git history (`git log --follow`), or file metadata. Also report the freeze or completion dates of the Part 2 plan (`q1_analysis_plan.md`), the Part 2b plan (`q1b_analysis_plan.md`), `uk_comparison_plan.md`, `matched_albums_plan.md`, `final_checks_plan.md`, `items4_5_plan.md` and `part1_secondary_rerun_plan.md` if they exist.

## B. Estimation details to confirm in the code

### B1. Newey-West lag choice (main.tex, Sect. 4.2)
The paper says standard errors use 12 lags, "roughly one quarter of weekly data".
- Find where `12` lags is set (look for `maxlags`, `HAC`, `cov_kwds`, `nw_lags`) and whether the analysis plan gives a reason for it.
- Report the plan's wording, if any, and whether the lag was fixed before estimation.
- Also report whether any run uses a different lag (for example 4, 8 or 26) and what those results are.

### B2. Placebo p-value: one-sided or two-sided (main.tex, Sect. 4.2 footnote)
The paper says the placebo p-value is "the share of placebo jumps at least as large as the actual jump in the predicted direction". Check the placebo-rank code (`code/29_uk_comparison.py`, `uk_comparison_placebo_rank.csv`, `uk_comparison_placebo_distribution.csv`):
- one-sided in the predicted direction, or two-sided on the absolute value?
- are ties counted? is the actual jump included in the denominator (`(count+1)/(N+1)` or `count/N`)?
- the exact number of placebo dates used (the paper says "about 350"), and the exact window and exclusion rule.

### B3. How the annual RIAA series is mapped to weeks (main.tex, Sect. 4.2)
Find in `matched_albums_plan.md` (test E) and the code behind `results/part2_incumbency/matched/E_riaa_control.csv` how annual RIAA streaming share and streaming revenue enter the weekly regression: constant within calendar year, linearly interpolated, or something else. Report the method and the file and line.

## C. Numbers to match to the results

### C1. Streaming's share of U.S. recorded-music revenue, 2013, 2014 and 2015 (main.tex, Sect. 2.3)
The paper claims 23%, 31% and 38%. Recompute from the RIAA data file used for `figA1_riaa_streaming_growth` (U.S. sales database export). Report: the three shares to one decimal, which RIAA series defines "streaming" (paid subscription plus ad-supported plus other?), whether the denominator is total revenue in nominal dollars, and the name and export date of the RIAA file.

### C2. Part 2b table (main.tex, Table 4) blanks and possible mislabelled column
Table 4 has columns Weeks, p and Genre boot. p. Several cells are blank (`\todo{}`). Using `results/part2b_genre_staying_power/*.csv`, `extensions.csv` and `results/final_checks/part2b_leave_one_genre_out.csv`, fill in this grid. For every cell give the estimate, the artist-clustered p, and the **genre-level wild cluster bootstrap p** (Webb weights, 9 genre clusters), and say which kind of p each reported number is:

| Row | Estimate | p (artist-clustered or conventional) | Genre wild-bootstrap p |
|---|---|---|---|
| Main, N=4,517 | 3.23 | <0.001 | 0.015 |
| + Debut-rank controls | 2.59 | <0.001 | ? |
| + Career position (chart-career debut ordinal) | 3.10 | ? | ? |
| Artist fixed effects | 1.73 | 0.034 | ? |
| Rock+pop coded as pop | 2.45 | 0.001 | 0.174 |
| Without hip-hop/R&B | 1.85 | ? | ? |
| UK chart (post = March 2015) | 0.03 | 0.98 | ? |

**Important check:** `parameters.md` lists 0.012 for the career-position row as an "artist-clustered t" p-value, and 0.10 for "without hip-hop/R&B" as a "genre-clustered t" p-value. The table currently puts them under "Genre boot. p". Report which test each number really is and whether a true genre-level wild-bootstrap p exists for each row. If it does not exist, say so and list which rows would need a rerun (do not run new estimation without asking).

### C3. Table 2 (Part 2) additions (main.tex, footnote under Table 3)
The note asks for standard errors and the pooled U.S.-UK test. From `results/part2_incumbency/*.csv` and `parameters.md` extract: the SE of the U.S. jump for new-entry share and for long-runner share, the SEs for the UK own-date and U.S.-date jumps, the RIAA-control range endpoints and which specifications produce them, the 2010-2024 window SEs, and the pooled U.S.-UK own-minus-other test (estimate and both p-values: Newey-West by country and Driscoll-Kraay) from `uk_comparison_pooled.csv`.

### C4. Verify the Table 1 numbers against the source files
- **Panel A** (album counts and mean tracks by group and pre/post): 1,507 / 1,079 heavy, 2,548 / 1,641 other; means 13.99 / 14.05 and 12.50 / 12.18. Recompute from the Part 1 analysis sample (`analysis_sample.csv`) and confirm N = 6,775 albums by 1,942 artists.
- **Panel B**: pre-rule mean new-entry share 10.8%, 2014 11.8%, 2019 5.7%; long-runner 22.1%, 26.2%, 48.9%. Recompute from the weekly series (`annual_means.csv`) and report exactly which weeks define the "pre-rule mean".
- **Panel C** counts (1,087 / 498 heavy, 2,062 / 870 other) and means (7.81 / 9.50, 6.58 / 5.23) have been checked against `part2b_album_runs.csv` and match. Just confirm `part2b_album_runs.csv` is the file the estimation uses (N = 4,517, 1,800 artists).
- Confirm the number of weekly U.S. charts used (the paper says 521 for 2010-2019) and that the UK series has 522.

## D. Data-section claims to check against code and data

For each, report supported, not supported or not found, with the file as evidence.

- **D1. Unmatched rate by genre group** (main.tex footnote in Sect. 3.2, and Online Resource 1). Rerun `code/14_validate_album_collection.py` under the ordered genre rule, produce `data/musicbrainz_genre_balance.csv`, and report the unmatched share of roster artists by genre group (streaming-heavy versus other, and by the nine genres if available). Roster is 3,361 artists with 2,367 matched uniquely. Say whether "similar across genre groups" holds and give the numbers. The devlog rates predate the genre tie-break fix, so do not reuse them.
- **D2. 100-album genre hand check.** The paper says a hand check of 100 randomly drawn albums found no clear misclassification. Find the file or log that records this (sample, seed, result).
- **D3. Independent streaming-service sample.** The paper says MusicBrainz track counts agree with an independent streaming-service sample for most albums and that hand checks favour MusicBrainz except where physical and digital editions differ. Find the comparison, its sample size and the agreement rate.
- **D4. Earliest digital edition gives the same result.** Find the result file and the estimate.
- **D5. UK number-one reconstruction.** The paper says "every reconstructed album peaked at number one and the sequence around the rule matches the published record". Find the checks the code or devlog actually ran and report exactly what was verified. If the published number-one list was not compared, say so.
- **D6. Roster and sample counts.** 3,361 roster artists; 2,367 matched; 2,034 with a genre (741 streaming-heavy, 1,293 other); 6,775 albums by 1,942 artists. Confirm each from the data files. (2,034 and 741 already match `artist_genres.csv`.)
- **D7. Weeks per source.** Confirm the date range of the Billboard file (first and last chart date) and the 521-chart count.
- **D8. Mixtapes, year-only dates.** Confirm that albums dated only to 2014 are dropped, other year-only dates are kept, the minimum is 6 tracks, and the "at least one official release" rule.

## E. Data provenance for the bib entries

- **E1. Kaggle Billboard dataset.** Find the file name, version number (the author used version 131 of the dataset at kaggle.com/datasets/ludmin/billboard) and the download date (file modification date, download log, scraper log).
- **E2. UK charts file.** Find which file from the GitHub repo `JackDanHollister/UkTop100Scrape` was used (`top_100_albums_1956_to_2024.xlsx` or `top_100_albums_1956_to_20250809.xlsx`), whether it was renamed (it appears in the paper as `uktop100albums.xlsx`), and its download date.
- **E3. RIAA export date** and the exact dataset or table exported.
- **E4. MusicBrainz collection dates.** The date range of the cached API responses (first and last collection date) and the API endpoints, rate limit and user-agent used.

---

## Not answerable from code (author must do these)

- Intro and Discussion bib entries (Zanella et al., Lech et al., Hiller and Walter, Datta et al., etc.).
- Exact publication days for Billboard 2009, 2018, 2019 and Official Charts Company 2015 announcements.
- AI-tool versions (Sect. 4.5), funding, competing interests, author contributions, acknowledgements, repository link and data and code statements.
- Conclusion, Results prose and the remaining narrative sections.

## Output format

Reply in `todo_answers.md` with one section per item ID (A1, A2, ..., E4), each containing: **Answer**, **Evidence** (file and line or CSV row) and **Notes or conflicts**. Put a short "Conflicts and surprises" list at the top.
