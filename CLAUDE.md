# CLAUDE.md — Billboard200Paper

Economics research project for the *Journal of Cultural Economics*: how Billboard's December 2014 switch to counting streams on the Billboard 200 album chart affected (1) what artists produce and (2) which albums the chart rewards.

**Read `PROJECT_CONTEXT.md` before doing any analysis.** It has the research question, mechanisms, parameters, every result so far, and the full history. `docs/devlog.md` is the detailed chronological log (§1–20 by the previous agent; §21–22 from Claude chat; §23–29 the 2026-10-02/03 cleanup, genre-rule fix, release-date fix, artist-cluster fix, the secondary and frozen-plan checks, the author's Part 2b decisions, the long-albums follow-up, §28, and the RIAA data, §29).

## Hard rules
1. **Never edit, rename or delete raw data** (`data/raw/`, formerly `OriginalDataFiles/`).
2. **Never delete MusicBrainz caches** (`data/external/*.jsonl`). Rebuilding them takes hours of rate-limited API calls.
3. **`docs/analysis_plan.md` is frozen** (approved 2026-09-27). Never change the headline specification. Deviations go in a dated note at the end, and in devlog.md.
4. **Ask before**: deleting anything, any web scraping or API calls, anything slow or costly, or changing a prespecified test.
5. After any substantive work, **append a dated section to `docs/devlog.md`** (what was done, what was found, files touched).
6. Report every test run, including nulls. Never search specifications for p < 0.05. New research questions get a short written plan *before* estimation (see `docs/q1_analysis_plan.md` for the format).
7. JCE requires describing LLM use in the Methods section: keep `docs/llm_use_log.md` updated.

## Environment
- Windows + VS Code. Use the **Python 3.10** interpreter (`py -3.10`; has pandas, numpy, statsmodels, scipy). The MSYS Python 3.12 lacks pandas/pip and failed TLS verification (its old venv is in `archive/venv_msys_py312/`).
- The Windows console can't print some non-ASCII artist names; write to files instead of printing, or set UTF-8 output (`PYTHONIOENCODING=utf-8`).
- Git repo on `main` with `core.autocrlf false`. `data/raw/`, `data/external/` and `*.pkl` are gitignored; everything else is tracked, so `git diff` shows exactly which outputs a rerun changed.
- **Run the pipeline:** `py -3.10 code/run_pipeline.py` (cache-only). The data steps take minutes; the 9,999-draw bootstraps in steps 17, 18, 24, 26, 25 and 19 take about 3.3 hours in total, so long runs are best split with `--only`. `--from 16` or `--only 20 21` runs part of it. MusicBrainz requests need `--allow-api` (ask first); without it a cache miss raises `CacheMissError`.

## Folder layout
- `data/raw/` — Kaggle `billboard200.csv`, `hot100.csv`, `streaming.csv`, `digital.csv`, `radio.csv`; Spotify `track_data_final.csv` and **`spotify_data clean.csv` (note the space)**; RIAA `RIAARevenue.csv` (Tableau export: **UTF-16, tab-separated**, negatives in parentheses; read via step 27). Read-only.
- `data/external/` — MusicBrainz caches (`*.jsonl`), API error logs, and the collector's tables (release groups, official releases, standard-album candidates).
- `data/interim/` — roster, credit audit, artist matches and review, identity decisions and audits, zero-match lists, Spotify album sample, Part 2b intermediate pickle.
- `data/final/` — `analysis_sample.csv` (Part 1 sample; also the Part 2b genre source), `artist_genres.csv` (one genre per resolved artist, step 12a), `part2_weekly_billboard200.csv`, `part2b_album_runs.csv`, `riaa_revenue_long.csv` and `riaa_revenue_by_category.csv` (step 27).
- `code/` — `paths.py` (every path), `load_clean_data.py`, `musicbrainz_helpers.py` (shared functions, genre rule) and `inference.py` (genre Webb bootstrap), numbered scripts 01–25 (run order is the list in `run_pipeline.py`; 12a, 24, 25 and 19 run out of numeric order), `run_pipeline.py`. Step 15 (genre hand-check sheet) is one-time and skipped by the runner.
- `results/part1_album_length/` — headline, means, digital robustness; `secondary/` (secondary checks, event study, frozen-plan checks incl. album order, long-albums follow-up (step 26), rock + pop sensitivity, old-label validation); `validation/` (coverage, genre balance, hand-check sheets); `spotify_exploratory/` (first Spotify-sample analysis).
- `results/part2_incumbency/`, `results/part2b_genre_staying_power/` (incl. `extensions.csv`: album-order control, artist-file labels).
- `docs/` — frozen `analysis_plan.md`, `q1_analysis_plan.md`, `q1b_analysis_plan.md`, `part1_secondary_rerun_plan.md`, `items4_5_plan.md`, `long_albums_followup_plan.md`, `devlog.md`, `llm_use_log.md`, `genre_classification.md`, cleanup inventory and move map.
- `archive/` — first-round code (`InitialAnalysisCode/`) and results (`kaggle_results/`), the phase-1 reproduction, root strays, devlog section files from chat, old venv. Don't edit.

## Known gotchas (each has caused a real bug)
- **billboard.com blocks AI agents in robots.txt** (`anthropic-ai`, `ClaudeBot`): don't scrape it, even with the author's approval (devlog §29).
- **Kaggle chart dates are stored 3 days early** (Wednesday, not Billboard's Saturday). The first rule chart (dated 2014-12-13) is stored as **2014-12-10**. Album post-rule threshold = release on/after **2014-11-24**.
- In `billboard200.csv` the **album title is in the `Song` column**. Read chart files with `dtype=str, low_memory=False`.
- **Mixed-precision dates** (`"1999"` and `"1999-02-23"` in one column): default `pd.to_datetime(..., errors="coerce")` silently blanks most values. Use `format="mixed"` and handle year-only values explicitly. This bug made the Part 1 headline sample year-only albums only until 2026-10-02 (devlog §25); fixed in `build_data()`.
- **Never name a variable `C`** in scripts that use statsmodels formulas: it shadows patsy's `C()` and breaks every regression.
- `heavy` (streaming-heavy genre flag) is a function of `genre`: don't include a bare `heavy` main effect alongside `C(genre)` (rank-deficient). Use `post:heavy` interactions only.
- Mixtape/Street release groups must be excluded **before** assigning window flags (bug fixed in devlog §20; keep it fixed).
- **`Series.str.split(" | ")` is a regex split in pandas** (any pattern longer than one character is a regex unless `regex=False`), so it splits on every space. This made the artist clusters the first word of the artist name until 2026-10-03 (devlog §26). Use `regex=False` for literal separators.
- **Never take "the first element" of a set** (`next(iter(some_set))`) when the set can hold more than one item: Python randomises string-set order in every process, so results change from run to run. This made every genre label random until 2026-10-02 (devlog §24). Multi-genre artists are assigned by `GENRE_PRIORITY` (`docs/genre_classification.md`).
- `results/part1_album_length/validation/musicbrainz_genre_balance.csv` is a **3-row summary**, not per-artist labels. Per-artist genre labels currently exist only inside `data/final/analysis_sample.csv` (≈1,040 artists).
- Script 12 regenerates the edition hand-check sheet and script 13 re-adjudicates it; always run them together, in that order (the runner does).
- MusicBrainz API: ≤1 request/second, descriptive User-Agent, unfielded quoted query with `dismax=true`, cache every raw response.

## Numbers that must reproduce after any refactor
Last verified 2026-10-03 by a full cache-only rerun (devlog §23–26).
- Kaggle: 1,253 new Billboard 200 album debuts in 2014; 393 in 2024.
- Roster: 3,361 roster entities; 2,367 with resolved MusicBrainz IDs.
- Album candidates: 10,913 total; 7,729 in the 2009–2019 headline window.
- Genre labels (ordered rule): 2,451 labelled artists, 903 streaming-heavy and 1,548 other.
- **Part 1 headline:** 6,775 albums, 1,942 artists, interaction +0.0228, artist-clustered SE 0.0151, p = 0.133, Webb wild bootstrap p = 0.161. (Superseded: +0.0356 / Webb p = 0.247 used random genre labels; −0.0247 / Webb p = 0.434 used the year-only sample. Both had 1,663 albums.)
- **Q1 incumbency:** jump at the rule in new-entry share −0.026; in 52+-week share +0.057 (`results/part2_incumbency/A_break_tests.csv`).
- **Q1b:** +3.23 weeks, artist-clustered p < 0.001, genre bootstrap p = 0.015 (4,517 albums). (Superseded: +2.48 / bootstrap p = 0.055, random labels; +3.03 / bootstrap p = 0.001, year-only sample.)

## Cleanup (done 2026-10-02)
The staged cleanup (inventory, move map, git, shared paths, cache-only rerun, logging) is complete; see `docs/cleanup_inventory.md`, `docs/cleanup_move_map.md` and devlog §23. Next steps are in `PROJECT_CONTEXT.md` §11.
