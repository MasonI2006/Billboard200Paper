# Remaining TODOs: round 2

Context: `main.tex` is the draft of a paper for the *Journal of Cultural Economics* on Billboard's December 2014 rule that began counting streams on the Billboard 200. Red `\todo{...}` markers are items still to resolve. This file lists every remaining marker in `main.tex`, plus the Online Resource 1 tables and bibliography details they depend on. Line numbers refer to the author's current `main.tex` (18 October 2026).

Round 1 (`todo_for_code_agent.md` and `todo_answers.md`) is already applied. Do not redo those items unless this file says so.

## Rules for the agent

1. **Do not edit `main.tex` or `references.bib`.** The live copy is in Overleaf, so local edits would be lost. Write every answer as a finished replacement that the author can paste.
2. You **may** create new LaTeX table files for Online Resource 1 (Section C). Do not edit `online_resource1.tex` itself. Give the `\input{}` lines and where they go instead.
3. **Do not guess.** If the code, data or a source does not answer an item, write "not found" and list where you looked. A wrong number is far worse than an open todo.
4. For every item, give the **answer**, the **evidence** (file and line, CSV row and column, or for literature the page and a short quote) and a **confidence note** ("read directly from X" or "inferred because Y").
5. Do not run new estimation unless an item says so. If you rerun a script, record the command and flag any number that differs from `parameters.md` or from the paper.
6. Write all output to **`todo_answers_round2.md`**, one section per item ID, with a "Conflicts and surprises" list at the top.

## Style rules for any text you write

The author is strict about these, so follow them in every replacement sentence, caption and table note.

- No colons in running prose. Table notes may keep the existing "SE: ..." pattern.
- British spelling (favour, organise, analyse, behaviour, artefact).
- No Oxford comma ("A, B and C").
- Every number has its unit and says what it measures ("2.6 percentage points in the new-entry share", never "2.6 points" or "the jump").
- Percentage-point changes in shares are "percentage points". Log-point estimates are reported as percent (0.023 is "2.3 percent").
- Math-mode signs for signed numbers (`$+2.6$`, `$-0.6$`).
- Do not mention "the analysis plan" or "prespecified" in the Results section (Sect. 5).
- Figure and table captions have no final full stop.
- Use "UK" without full stops and "U.S." with full stops.

---

## A. Numbers to pull from results files (main.tex)

### A1. Point estimate in tracks (line 235)
Text: "Relative to other genres, streaming-heavy genres lengthened their albums by 2.3 percent, which equates to about 0.3 tracks."
- From `results/final_checks/equivalence.csv` (or wherever the 90% CI in tracks, $-0.03$ to $+0.63$, is computed), report the point estimate converted to tracks and the conversion used (for example, $\beta$ times the pre-rule mean track count of streaming-heavy albums, or the CI midpoint).
- Confirm or correct "about 0.3 tracks". The Introduction (line 78) uses the same figure.
- **Deliver** the replacement sentence with the todo removed.

### A2. Selection-and-payoff test effect size (line 239)
Text: "Testing whether or not longer albums in streaming-heavy genres became more likely to reach the chart after the rule, we found an increase of \todo{...}, which is significant at the 10% level but not at the 5% level (bootstrap $p=0.063$)."
- Find the Part 1 selection-and-payoff test whose bootstrap p is 0.063.
- Report: the outcome (for example, probability of charting), how "longer album" is defined (threshold or continuous track count), the estimate with units, the standard error and the exact bootstrap p.
- **Deliver** a replacement sentence that states the estimate in plain units (for example, "the probability of reaching the chart rose by X percentage points more for albums with N or more tracks in streaming-heavy genres than in other genres") and that keeps "significant at the 10% level but not at the 5% level (bootstrap $p=0.063$)".
- Also remove the space before `\footnote` in that sentence (`$p=0.063$). \footnote` should be `$p=0.063$).\footnote`).

### A3. Top-100 restriction, new-entry p-value (line 286)
Text: "Restricting the chart to its top 100 positions gives a larger fall in the new-entry share ($-3.6$ percentage points, \todo{p-value}) and a smaller rise in the long-runner share ($+2.3$ percentage points, $p=0.059$)."
- From the top-100 robustness output in `results/part2_incumbency/`, report the Newey–West p for the new-entry estimate, and confirm $-3.6$, $+2.3$ and 0.059.
- Say whether 0.059 is Newey–West or placebo-rank. If placebo-rank p-values exist for the top-100 run, report them too.
- **Deliver** the replacement sentence.

### A4. Triple-difference scale check (line 333, no todo but must verify)
Text: "A triple difference that compares the same albums on both charts gives $+7.8$ weeks in the U.S. relative to the UK, but the bootstrap $p$-value is 0.43."
- $+7.8$ weeks is more than twice the main estimate (3.2 weeks). Confirm from the Part 2b UK comparison output that 7.8 is in **weeks on chart in the first 52 weeks after debut**, the same outcome as the main estimate, and not a different horizon, a different chart length or a sum over countries.
- Report the sample (number of matched albums), the estimate, SE and bootstrap p. If 7.8 is on a different scale, give corrected wording.

### A5. Placebo-date count consistency (no todo)
The paper uses "352 placebo dates" in Sect. 5.2, the Introduction and the Conclusion, but "about 350 placebo rule dates" in Sect. 4.2 (line 207) and "≈350 fake dates" in Table 2 (line 312).
- Confirm 352 is the exact count for the U.S. new-entry series, and report the count for the UK series (the UK placebo p-values 0.55 and 0.94 use it).
- **Deliver** replacements for line 207 ("about 350") and the Table 2 row label (replace "fake dates" with "placebo dates", give the exact count).

## B. Online Resource 1 cross-references (main.tex)

Online Resource 1 numbers its figures and tables S1, S2, ... in order of appearance. The figure order is already settled.

| Figure | Content | File |
|---|---|---|
| S1 | track-count thresholds | figA4 |
| S2 | RIAA streaming growth | figA1 |
| S3 | placebo dates | figA2 |
| S4 | leave-one-genre-out | figA3 |

### B1. Figure references (resolved, just confirm)
- Line 115 (Sect. 2.3, RIAA figure): should become `Fig.~S2`.
- Line 333 (Sect. 5.3, leave-one-genre-out): should become `Fig.~S4`.
- Confirm against `online_resource1.tex` that the figure environments still appear in the order S1 to S4 above. Report any mismatch.

### B2. Table references
These depend on the tables you build in Section C. Once their order is fixed, report the final number for each.
- Line 149 (MusicBrainz footnote, unmatched rates by genre): `Table~S\todo{n}`.
- Line 197 (Sect. 4.1, the twelve secondary checks): `Table~S\todo{n}`.
- Line 241 (Sect. 5.1, alternative samples, windows and controls): `Table~S\todo{n}`, the same table as line 197.

**Important.** `online_resource1.tex` begins with `\input{appendix_test_registry}`. If that file contains a `table` or `longtable` environment, it takes Table S1 and every table below shifts by one. Check this first and number accordingly.

## C. Online Resource 1 tables to build

Each table goes in its own file under `online_resource1_tables/` as a `table` (or `longtable`) environment with `\caption{...}` (no final full stop), `\label{tab:S_...}`, booktabs rules (`\toprule`, `\midrule`, `\botrule`) and a `\footnotetext{}` note naming the source files. Build only from existing results CSVs. If a number is missing, put `\todo{...}` in that cell and list it in your answers.

Suggested order (adjust if the test registry contains a table):

- **C1. Unmatched roster artists by genre** (Data construction section). From `results/part1_album_length/validation/musicbrainz_genre_balance.csv` and `musicbrainz_subgenre_balance.csv`. Rows are streaming-heavy, other and no identifiable genre, then the nine genres. Columns are roster artists, matched uniquely, unmatched and percent unmatched. It must reproduce 17.9% (streaming-heavy), 16.5% (other) and "577 of the 994 unmatched artists have no identifiable genre". Replaces the todo in the Data construction bullet of `online_resource1.tex`.
- **C2. The twelve Part 1 secondary checks** (Part 1 robustness). From `plan_checks.csv` and `parameters.md`. One row per check with estimate, artist-clustered SE, genre bootstrap p and N. Mark the 18-or-more-tracks row. The range across checks that keep the outcome and treatment definition must match "$-1.6$ to $+2.9$ percent" in Sect. 5.1. Report which rows define that range. Also list charted versus non-charted subsamples ($+0.033$, p 0.084; $+0.017$, p 0.47), the selection-and-payoff test (A2), the earliest digital edition ($+0.020$, p 0.23) and the rock+pop to pop recoding, then the exploratory checks in a separate panel labelled exploratory.
- **C3. Long-albums follow-up family** (Part 1, Long albums subsection). Five upper-tail outcomes, the unadjusted bootstrap p and the Holm-adjusted p (the smallest adjusted p should be 0.24). Report the exact definition of each of the five outcomes, because the main text describes them as "five outcomes defined by long-album thresholds" and that wording must be checked.
- **C4. Part 2 robustness.** Placebo-date summary for both shares and both countries, song charts (radio $-2.3$, streaming $+2.5$, digital sales $-1.2$, with p-values), the July 2018 break, first-run length of new debuts, the pooled U.S.–UK test (Newey–West by country and Driscoll–Kraay p), RIAA controls by specification (four cells giving the ranges $-2.6$ to $-3.3$ and $+5.0$ to $+5.6$), the top-100 restriction (A3), the 2010–2024 window and the matched catalogue albums comparison (level-only versus with trend change, which the main text no longer reports).
- **C5. Part 2b robustness.** Weeks in the first 26 weeks ($+1.8$, bootstrap p 0.007), still on the chart at week 26 ($+4.6$ percentage points, p 0.44), the artist fixed-effects SE choice (within 0.8, p 0.034; dummy-variable 1.05, p 0.10), the cross-country triple difference (A4) and the UK replication ($+0.03$).
- **C6. Superseded estimates.** The three implementation errors in the Sect. 4.4 footnote (non-deterministic genre tie-break, date-parsing error restricting Part 1 to year-only-dated albums, artist clusters by first word of name). For each, list the estimates it affected, the superseded value and the corrected value, from `devlog.md` and git history. Replaces the todo in the last section of `online_resource1.tex`.

For each table, also give a one-sentence lead-in for the Online Resource 1 section, following the style rules.

## D. Facts to confirm from data files and sources

### D1. RIAA "Other Streaming" (line 115)
The text says streaming's share of U.S. recorded-music revenue was 23%, 31% and 38% in 2013, 2014 and 2015.
- From the RIAA export used for `figA1`, list exactly which RIAA categories are summed as "streaming" (paid subscription, on-demand ad-supported, SoundExchange distributions, other ad-supported streaming, limited-tier subscription and so on).
- If you have web access, report RIAA's own definition of "Other Ad-Supported Streaming" or "Other Streaming" from the RIAA U.S. Sales Database notes, with the URL.
- Report whether the series includes non-interactive (radio-style) streaming such as SoundExchange distributions. That decides whether the paper can call it "on-demand" streaming. Sect. 5.2 (line 278) currently says "On-demand streaming also grew".
- **Deliver** a replacement for the line 115 sentence that describes the series accurately, and say whether "On-demand" in line 278 must change.

### D2. RIAA export details (references.bib, `riaa_sales_database`)
The export or download date of the RIAA file, the exact table or chart exported, and the file name.

### D3. Kaggle Billboard dataset (references.bib, `kaggle_billboard`)
The download date, version (expected 131) and licence shown on the Kaggle page (Lambert, Godefroy, `ludmin/billboard`).

### D4. UK chart file (references.bib, `uktop100scrape`)
Which file from GitHub `JackDanHollister/UkTop100Scrape` was used (`top_100_albums_1956_to_2024.xlsx` or `top_100_albums_1956_to_20250809.xlsx`), whether it was renamed (`uktop100albums.xlsx`) and the download date (file metadata, download log or git history).

### D5. Code availability statement (backmatter, line 406)
Confirm whether one replication script reproduces every number in the paper from cached raw data. Give the script name and the command, and say which outputs it writes. List any numbers in the paper that the script does not produce.

### D6. Data availability statement (backmatter, line 405)
For each data source (Kaggle Billboard compilation, UK scrape, MusicBrainz, RIAA, Nielsen 2014 report), report its licence or redistribution terms if stated in the repo or source, and which derived files the repo could share. **Deliver** a draft statement for JCE's type 2 research data policy, following the style rules, with `\todo{}` for the repository DOI.

## E. Literature checks (needs web or paper access)

For each, read at least the abstract and the relevant results section. Quote the passage that supports the sentence with a page or section number. If the paper does not support the sentence, say so plainly and propose an accurate replacement. If you cannot access the paper, write "not accessed" and do not paraphrase from memory.

### E1. Schneider and Gros (2019), `schneider2019five` (lines 84 and 286)
Bib title: "Five decades of US, UK, German and Dutch music charts show that cultural processes are accelerating", *Royal Society Open Science*.
- Line 286 claims they found "that diversity on the Billboard 200 fell after streams were added". **This may be wrong.** The title suggests a finding about accelerating chart dynamics, not about diversity after 2014. Check whether the paper says anything about the Billboard 200 after December 2014 or about streaming at all.
- **Deliver** accurate replacements for line 286 and for the line 84 todo ("The closest evidence to ours is \citet{schneider2019five}, who ..."). If the paper is not close evidence, say so and suggest which bib entry is (for example, `lech2025harder` or `gourevitch2023billboard`), with its supporting quote.

### E2. Zanella, Cillo and Verona (2022), `zanella2022whatever` (line 80)
Text: "incumbent firms respond when the information a market reports changes". Report the setting (which chart or rule change, which years), the outcome studied and the main finding. **Deliver** a replacement clause.

### E3. Sim et al. (2022), `sim2022bestseller` (line 369, and cited in lines 72 and 80)
Text: "chart rankings on streaming services shape which songs listeners discover". Report the setting and main finding, and **deliver** a replacement clause if needed. Also check that lines 72 and 80 ("appearing near the top of them raises demand", "a high rank raises demand ... for music on streaming services") are supported.

### E4. Other Introduction citations (lines 82 and 84, no todos but must be accurate)
For each, confirm that the paper is about what the sentence says, with a short quote.
- `elberse2010bye`, `danaher2014empirical` (unbundling of albums into tracks)
- `hiller2017rise` (implications of streaming for music production)
- `datta2018changing` (effects on consumption and discovery)
- `ivaldi2024displacement` (relationship with other formats)
- `mckenzie2021takes` (drivers of streaming demand)
- `jensen2024rethinking` (how streaming revenue is paid)
- `strobl2000dynamics` (dynamics of chart success in the UK)
- `bhattacharjee2007effect` (how long albums survive on the charts)
- `lech2025harder`, `gourevitch2023billboard` (long-run changes in U.S. chart history)

### E5. Bibliography dates (references.bib)
The exact publication days of the Billboard announcements (`billboard2009makeover`, `billboard2018weighting`, `billboard2019video`) and the Official Charts Company announcement (`occ2015streams`), with URLs. Leave any you cannot confirm as todos.

## F. Author-only items (do not attempt)

Report these back as still open, so the author has the full list.
- Sect. 4.5 (line 224): which AI tools and versions were used.
- Backmatter: acknowledgements, funding, competing interests, author contributions.
- The title (currently "Working Title / Working Subtitle").

## Output format

`todo_answers_round2.md`, with these sections in order:

1. **Conflicts and surprises.** Any number in the paper that the results do not support, and any citation that does not say what the paper claims.
2. **Paste-ready replacements.** For each `main.tex` item, the line number, the old text and the new text, in a fenced `latex` block.
3. **Item-by-item answers** (A1 to E5), each with Answer, Evidence and Confidence.
4. **New files created** (Section C), with the `\input{}` line for each and where it goes in `online_resource1.tex`.
5. **Still open**, everything not found plus Section F.
