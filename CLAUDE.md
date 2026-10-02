# CLAUDE.md — Billboard200Paper

Economics research project for the *Journal of Cultural Economics*: how Billboard's December 2014 switch to counting streams on the Billboard 200 album chart affected (1) what artists produce and (2) which albums the chart rewards.

**Read `PROJECT_CONTEXT.md` before doing any analysis.** It has the research question, mechanisms, parameters, every result so far, and the full history. `devlog.md` is the detailed chronological log (sections 1–20 written by the previous agent; sections 21–22 were done in Claude chat and live in `q1_incumbency/devlog_section_21.md` and `q1b_genre_staying_power/devlog_section_22.md` — append them if missing).

## Hard rules
1. **Never edit, rename or delete raw data** (`OriginalDataFiles/` or its future `data/raw/` location).
2. **Never delete MusicBrainz caches** (`data/*cache*.jsonl`). Rebuilding them takes hours of rate-limited API calls.
3. **`analysis_plan.md` is frozen** (approved 2026-09-27). Never change the headline specification. Deviations go in a dated note at the end, and in devlog.md.
4. **Ask before**: deleting anything, any web scraping or API calls, anything slow or costly, or changing a prespecified test.
5. After any substantive work, **append a dated section to devlog.md** (what was done, what was found, files touched).
6. Report every test run, including nulls. Never search specifications for p < 0.05. New research questions get a short written plan *before* estimation (see `q1_incumbency/q1_analysis_plan.md` for the format).
7. JCE requires describing LLM use in the Methods section: keep `llm_use_log.md` updated (create it if missing).

## Environment
- Windows + VS Code. Use the **Python 3.10** interpreter (has pandas, numpy, statsmodels, scipy). The MSYS Python 3.12 lacks pandas/pip and failed TLS verification.
- The Windows console can't print some non-ASCII artist names; write to files instead of printing, or set UTF-8 output.

## Current folder layout (messy — see first task)
- `OriginalDataFiles/` — raw inputs: Kaggle `billboard200.csv`, `hot100.csv`, `streaming.csv`, `digital.csv`, `radio.csv`; Spotify `track_data_final.csv` and **`spotify_data clean.csv` (note the space in the filename)**.
- `InitialAnalysisCode/` + `kaggle_results/` — first-round exploratory scripts and outputs (superseded; keep as archive).
- `code/` — the previous agent's pipeline (roster building, MusicBrainz matching/collection, validation, headline analysis). Script names are listed in devlog sections 7–20.
- `data/` — roster, artist matches, MusicBrainz caches and tables, audit files.
- `results/phase1_original/`, `results/phase1_clean/`, `results/phase3_first_pass/` (current headline outputs).
- `q1_incumbency/`, `q1b_genre_staying_power/` — analyses run in Claude chat. **Their scripts have hard-coded paths (`/mnt/user-data/uploads/`) that must be repointed.**
- Root-level docs: `README_album_padding.md`, `devlog.md`, `analysis_plan.md`, `PROJECT_CONTEXT.md`, this file. Possibly stray CSVs (e.g. `D_artist_exposure.csv`, `true_nomatch_zero.csv`, `flagged_composite_partial.csv`).

## Known gotchas (each has caused a real bug)
- **Kaggle chart dates are stored 3 days early** (Wednesday, not Billboard's Saturday). The first rule chart (dated 2014-12-13) is stored as **2014-12-10**. Album post-rule threshold = release on/after **2014-11-24**.
- In `billboard200.csv` the **album title is in the `Song` column**. Read chart files with `dtype=str, low_memory=False`.
- **Mixed-precision dates** (`"1999"` and `"1999-02-23"` in one column): default `pd.to_datetime(..., errors="coerce")` silently blanks most values. Use `format="mixed"` and handle year-only values explicitly.
- **Never name a variable `C`** in scripts that use statsmodels formulas: it shadows patsy's `C()` and breaks every regression.
- `heavy` (streaming-heavy genre flag) is a function of `genre`: don't include a bare `heavy` main effect alongside `C(genre)` (rank-deficient). Use `post:heavy` interactions only.
- Mixtape/Street release groups must be excluded **before** assigning window flags (bug fixed in devlog §20; keep it fixed).
- `data/musicbrainz_genre_balance.csv` is a **3-row summary**, not per-artist labels. Per-artist genre labels currently exist only inside `results/phase3_first_pass/analysis_sample.csv` (≈1,040 artists).
- MusicBrainz API: ≤1 request/second, descriptive User-Agent, unfielded quoted query with `dismax=true`, cache every raw response.

## Numbers that must reproduce after any refactor
- Kaggle: 1,253 new Billboard 200 album debuts in 2014; 393 in 2024.
- Roster: 3,361 roster entities; 2,367 with resolved MusicBrainz IDs.
- Album candidates: 10,913 total; 7,729 in the 2009–2019 headline window.
- **Part 1 headline (corrected):** 1,663 albums, 853 artists, interaction +0.0356, artist-clustered SE 0.0289, p = 0.218, Webb wild bootstrap p = 0.247.
- **Q1 incumbency:** jump at the rule in new-entry share −0.026; in 52+-week share +0.057 (`q1_incumbency/results/A_break_tests.csv`).
- **Q1b:** +2.48 weeks, artist-clustered p = 0.008, genre bootstrap p = 0.055.

## First task: clean up the work environment
Do this in stages and stop for approval between them.
1. **Inventory (read-only).** List every file and folder with size, last-modified date, and which scripts read/write it (grep the code). Flag duplicates, stray files, outputs with no producing script, and hard-coded paths. Save as `cleanup_inventory.md`.
2. **Propose a layout and a move map** (old path → new path), then wait for approval. Suggested target:
   ```
   Billboard200Paper/
     CLAUDE.md  README.md  PROJECT_CONTEXT.md
     docs/      analysis plans (frozen plan included, unchanged), devlog.md, llm_use_log.md
     data/raw/      Kaggle + Spotify inputs (read-only)
     data/external/ MusicBrainz caches + collected tables
     data/interim/  roster, matches, audits, flags
     data/final/    analysis-ready samples
     code/          numbered pipeline scripts + one shared paths/helpers module
     results/part1_album_length/  results/part2_incumbency/  results/part2b_genre_staying_power/
     archive/       InitialAnalysisCode/, kaggle_results/, phase1_* results, superseded files
   ```
3. **Before moving anything:** initialise git if there is no repo and commit the current state. Add a `.gitignore` for large data and caches. Move, never delete (superseded material goes to `archive/`).
4. **Fix paths:** one shared module (e.g. `code/paths.py`) defines every directory relative to the project root; all scripts import it. Repoint the q1/q1b scripts.
5. **Verify:** rerun the pipeline from cached data only (no API calls) and confirm every number in the list above reproduces. Report any mismatch rather than patching around it.
6. **Log** the cleanup in devlog.md and update the folder map in this file.
