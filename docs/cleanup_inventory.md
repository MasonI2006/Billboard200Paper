# Cleanup inventory (stage 1, read-only)

Built 2026-10-02. Nothing has been moved, renamed or deleted. Sizes and modified times are taken from the filesystem; read/write links come from grepping every `.py` file in `code/`, `InitialAnalysisCode/`, `q1_incumbency/` and `q1b_genre_staying_power/`.

Totals: about 185 project files (excluding `.venv/`, which has 861 files) and about 1.6 GB on disk. Two MusicBrainz files make up about 1.3 GB of that.

---

## A. Flags (summary)

### A1. Duplicates
| Files | Status |
|---|---|
| `D_artist_exposure.csv` (root) = `kaggle_results/D_artist_exposure.csv` | Byte-identical (same MD5). The root copy is stray: no current script writes to the root. It probably came from an early run of `kaggle_analysis.py`, before that script started changing into `kaggle_results/`. |
| `kaggle_results/*` vs `results/phase1_original/*` | Same 18 file names. Seven are identical apart from CRLF/LF line endings (A, B, B2, C, D_artist_exposure, S4, S7). The other 11 have different values: D2, D_did, D_event_study, E_payoff, S1, S2, S3, S5, S6 and S_albums_core. phase1_original is the devlog §7 reproduction run, so the gaps may come from the in-memory compatibility fixes made in that run. **Not yet explained. Should be checked before anything is archived as "the same".** |
| `results/phase1_original/*` vs `results/phase1_clean/*` | Of the 17 shared names, 10 are byte-identical and 7 differ (B2, S2–S7). phase1_clean also has 2 extra files (`D2_did_excluding_2013_2014.csv`, `S7_non_billboard_result.csv`) and has no `S_albums_core.csv`. These differences are expected: phase1_clean comes from the cleaned `analyze_albums.py`. |
| `q1_incumbency/devlog_section_21.md`, `q1b_genre_staying_power/devlog_section_22.md` | **Not yet appended** to `devlog.md`, which ends at §20. These files are content waiting to be merged, not duplicates. |

### A2. Stray files at the root
| File | Notes |
|---|---|
| `D_artist_exposure.csv` | Duplicate (see A1). Not read from the root by anything. `spotify_part2.py` reads `D_artist_exposure.csv` relative to the working directory, which is `kaggle_results/` after the `os.chdir` it inherits. |
| `true_nomatch_zero.csv` | **A live pipeline input stored at the root.** It is read by `retry_musicbrainz_zero_matches.py`, `search_zero_results_by_components.py` and `audit_musicbrainz_search_exceptions.py`, which also **overwrites it in place** (its input and output paths are the same). The user's original 92-row list therefore no longer exists in its original form. |
| `flagged_composite_partial.csv` | Written by `audit_musicbrainz_search_exceptions.py`. Devlog §14 says the file was later updated (Rat Pack MBID); no script seems to write that update, so it was probably a hand or ad-hoc edit. No script reads it. |
| `README_album_padding.md` | First-round project README. Its code and table references point to `kaggle_results/` and the first-round scripts. Superseded by `PROJECT_CONTEXT.md` but still cited in the first line of `devlog.md`. |

### A3. Outputs with no producing script on disk
| File | Notes |
|---|---|
| `results/phase1_original/` (18 files) | Made by running the `InitialAnalysisCode/` scripts with outputs redirected and with temporary in-memory fixes (devlog §7). That redirected or patched version was never saved, so these files can't be regenerated exactly. |
| `data/musicbrainz_confirmed_not_found.csv` | Created by hand or ad hoc (devlog §14). No script mentions it. |
| `flagged_composite_partial.csv` (current contents) | See A2: the script makes the first version, and a later edit has no script. |
| `q1b_genre_staying_power/results/*` | `album_age.py` and `analyze.py` do produce these, but they write to the **current working directory**, not `results/`. The files were moved into `results/` by hand. |
| `chart_labelled.pkl` (**missing**) | An intermediate file that `build.py` writes and that `analyze.py` and `album_age.py` read. It is not on disk, so the two Q1b analysis scripts can't run until `build.py` is rerun. |

### A4. Hard-coded or fragile paths
| Script | Problem |
|---|---|
| `q1_incumbency/q1_incumbency.py:5` | `DATA = Path("/mnt/user-data/uploads")`. `OUT = Path("results")` is relative to the working directory, so the script only works when run from `q1_incumbency/`. |
| `q1b_genre_staying_power/build.py:2` | `U = "/mnt/user-data/uploads/"`. Used for `billboard200.csv`, `musicbrainz_artist_matches.csv` and `analysis_sample.csv`. Writes `chart_labelled.pkl` to the working directory. |
| `q1b_genre_staying_power/album_age.py:7` | `"/mnt/user-data/uploads/musicbrainz_release_groups.csv"`. Reads and writes in the working directory. |
| `q1b_genre_staying_power/analyze.py` | All input and output paths are relative to the working directory (`chart_labelled.pkl`, `album_runs.csv`, `results_*.csv`). |
| `InitialAnalysisCode/spotify_analysis.py:10` | Asks for `spotify_data_clean.csv`, but the file on disk is `spotify_data clean.csv`, so the script **fails as written** (known; devlog §7). |
| `InitialAnalysisCode/kaggle_analysis.py`, `spotify_analysis.py` | Call `os.chdir(kaggle_results)` and then write bare filenames. `spotify_part2–5.py` work by running each other's source text with `exec(open(...).read().split(...))`, which is fragile but archive-only. |
| `code/analyze_albums.py:650` | `RESULTS_DIR.parent / "data"` rebuilds the data folder path instead of importing `DATA_DIR`. It works, but it will break if `results/` moves away from the root. |
| `code/audit_musicbrainz_search_exceptions.py:13-15`, `retry_musicbrainz_zero_matches.py:24`, `search_zero_results_by_components.py:18` | Point at root-level `true_nomatch_zero.csv` and `flagged_composite_partial.csv`. |
| All of `code/*.py` | Each script works out `PROJECT_ROOT = Path(__file__).parents[1]` and defines `DATA_DIR` locally, in 14 separate places, and `load_clean_data.py` defines `RAW_DATA_DIR`, `DATA_DIR` and `RESULTS_DIR`. They are not hard-coded, but they are duplicated. A shared `paths.py` (stage 4) replaces them. |

### A5. Other issues relevant to later stages
1. **Scripts that overwrite their own inputs** affect stage 5, the cached rerun:
   - `musicbrainz_artist_matches.csv` and `_review.csv` are rewritten in turn by `match_musicbrainz_artists.py`, then `retry_musicbrainz_zero_matches.py`, then `resolve_musicbrainz_ambiguities.py`, then `apply_musicbrainz_identity_decisions.py`. Rerunning an earlier step after a later one would **undo later identity decisions**, so the order must be exact.
   - `adjudicate_edition_handcheck.py` overwrites `musicbrainz_edition_handcheck_sample.csv`, which is also its input. `validate_musicbrainz_collection.py` regenerates that sample and would **wipe the hand adjudications**.
   - `audit_musicbrainz_search_exceptions.py` overwrites `true_nomatch_zero.csv` (see A2).
2. **There is no cache-only mode.** `match_musicbrainz_artists.py`, `retry_…`, `search_zero_results_by_components.py` and `collect_musicbrainz_discographies.py` call the MusicBrainz API whenever the cache doesn't have an entry. Stage 5 needs either an offline guard or a decision to start from the matched tables instead of rerunning these scripts.
3. **Large files and git:** `musicbrainz_official_releases.csv` (639 MB) and `musicbrainz_official_release_cache.jsonl` (631 MB) are far over GitHub's 100 MB limit. Other large files: `billboard200.csv` (69 MB), `release_group_cache.jsonl` (46 MB), `release_groups.csv` (36 MB), `hot100.csv` (37 MB). All of these need `.gitignore` entries.
4. **The project is inside OneDrive.** OneDrive syncing a `.git` folder and about 1.6 GB of churning data can cause lock and conflict problems. Worth deciding before `git init` (stage 3).
5. **`.venv/`** is a Python **3.12 venv built from MSYS** (`C:\msys64\ucrt64`). CLAUDE.md says this interpreter has no pandas and failed TLS checks, so the venv is unused. It's a candidate for `.gitignore` and possibly for removal, but only with your approval.
6. `devlog.md` has **no §16**: the numbering goes from 15 to 17. This is cosmetic, but worth noting before §21 and §22 are appended.
7. **There is no per-artist genre file.** The genre classifier is `infer_row_genre()` in `validate_musicbrainz_collection.py`, and per-artist labels exist only inside `results/phase3_first_pass/analysis_sample.csv`. That file is a result, but `q1b/build.py` uses it as an input. This matters for open issue #2.
8. `code/__pycache__/` (5 `.pyc` files) needs a `.gitignore` entry.
9. `llm_use_log.md` doesn't exist yet. CLAUDE.md rule 7 requires it.

---

## B. Full inventory

Columns: size, last modified, and **R** = read by / **W** = written by (scripts named without the `.py`).

### B1. Root
| File | Size | Modified | R / W | Notes |
|---|---|---|---|---|
| `CLAUDE.md` | 6.7 KB | 2026-10-02 | — | Working rules |
| `PROJECT_CONTEXT.md` | 13.0 KB | 2026-10-02 | — | Research context |
| `analysis_plan.md` | 11.3 KB | 2026-09-28 | — | **Frozen** Part 1 plan |
| `devlog.md` | 53.9 KB | 2026-09-28 | — | §1–20 (no §16; §21–22 not appended) |
| `README_album_padding.md` | 12.7 KB | 2026-09-27 | — | First-round README (superseded) |
| `D_artist_exposure.csv` | 6.8 KB | 2026-09-27 | none from the root | Duplicate, stray |
| `true_nomatch_zero.csv` | 11.0 KB | 2026-09-27 | R: retry_musicbrainz_zero_matches, search_zero_results_by_components, audit_musicbrainz_search_exceptions · W: audit_musicbrainz_search_exceptions (in place) | Pipeline input at the root |
| `flagged_composite_partial.csv` | 11.8 KB | 2026-09-27 | W: audit_musicbrainz_search_exceptions | Later edited by hand or ad hoc |
| `.vscode/settings.json` | 68 B | 2026-09-27 | — | Sets the Python env manager to system |
| `.venv/` | 14 MB, 861 files | 2026-09-27 | — | MSYS Python 3.12 venv, unused |

### B2. `OriginalDataFiles/` (raw data: never edit)
| File | Size | Modified | Read by |
|---|---|---|---|
| `billboard200.csv` | 68.4 MB | 2026-09-27 | load_clean_data (used by build_pre_rule_artist_roster, report_musicbrainz_resolution_balance, validate_album_collection, analyze_albums), kaggle_analysis, spotify_part2, q1_incumbency†, q1b/build† |
| `hot100.csv` | 36.6 MB | 2026-09-27 | load_clean_data, kaggle_analysis |
| `streaming.csv` | 4.6 MB | 2026-09-27 | load_clean_data, kaggle_analysis, q1_incumbency† |
| `digital.csv` | 6.6 MB | 2026-09-27 | load_clean_data, kaggle_analysis, q1_incumbency† |
| `radio.csv` | 10.9 MB | 2026-09-27 | load_clean_data, kaggle_analysis, q1_incumbency† |
| `track_data_final.csv` | 1.4 MB | 2026-09-27 | load_clean_data, spotify_analysis |
| `spotify_data clean.csv` (space) | 1.4 MB | 2026-09-27 | load_clean_data (correct name); spotify_analysis (wrong name, so it fails) |
| `dataset-metadata.json` | 109 B | 2026-09-27 | — (Kaggle metadata, id `ludmin/billboard`) |

† via a hard-coded `/mnt/user-data/uploads/` path.

### B3. `InitialAnalysisCode/` (first round, superseded)
| File | Size | Modified | Reads | Writes |
|---|---|---|---|---|
| `kaggle_analysis.py` | 7.6 KB | 2026-09-27 | the 5 chart CSVs | `kaggle_results/` A, B, B2, C, D, D_did, D_event_study, E, D2 |
| `spotify_analysis.py` | 6.5 KB | 2026-09-27 | track_data_final, `spotify_data_clean.csv` (wrong name) | `kaggle_results/` S_albums_core, S1, S2, S3 |
| `spotify_part2.py` | 2.5 KB | 2026-09-27 | runs spotify_analysis' source text; billboard200, D_artist_exposure | S4 |
| `spotify_part3.py` | 1.9 KB | 2026-09-27 | runs part2's source text | S5, S6 |
| `spotify_part4.py` | 1.5 KB | 2026-09-27 | runs part3's source text | S7 |
| `spotify_part5.py` | 0.4 KB | 2026-09-27 | runs part3's source text | S8 |

### B4. `kaggle_results/` (first-round outputs, 18 files, about 196 KB, all 2026-09-27 18:51)
`A_b200_dynamics`, `B2_quarterly`, `B_bombs_by_chart`, `C_dilution`, `D2_event_study_ref2012`, `D_artist_exposure`, `D_did`, `D_event_study`, `E_payoff` (W: kaggle_analysis) · `S1_tracks_by_year`, `S2_did`, `S3_event_study`, `S_albums_core` (W: spotify_analysis) · `S4_did_variants` (W: spotify_part2) · `S5_event_study_bb200_binary`, `S6_dilution_popularity` (W: spotify_part3) · `S7_bb200_variants` (W: spotify_part4) · `S8_bb200_periods` (W: spotify_part5). Producing scripts exist; see A1 for how these compare with phase1_original.

### B5. `code/` (current pipeline)
Listed in rough pipeline order from devlog §7–20. ⚠ = calls the MusicBrainz API when the cache has no entry; ✎ = overwrites a file it also reads.

| Script | Size | Modified | Reads | Writes |
|---|---|---|---|---|
| `load_clean_data.py` (module) | 5.2 KB | 09-27 | raw charts, Spotify files | — (defines `RAW_DATA_DIR`, `DATA_DIR`, `RESULTS_DIR`) |
| `build_album_sample.py` | 3.5 KB | 09-27 | via load_clean_data | `data/spotify_album_sample.csv` |
| `analyze_albums.py` | 22.1 KB | 09-27 | spotify_album_sample, charts | `results/phase1_clean/*` (19 files) |
| `build_pre_rule_artist_roster.py` | 4.7 KB | 09-27 | billboard200 | `data/pre_rule_artist_roster.csv`, `pre_rule_artist_credit_audit.csv` |
| `match_musicbrainz_artists.py` ⚠✎ | 12.5 KB | 09-27 | roster, artist_search_cache | artist_search_cache (append), artist_matches, artist_matches_review, artist_search_errors (append) |
| `audit_musicbrainz_search_exceptions.py` ✎ | 7.1 KB | 09-27 | `true_nomatch_zero.csv`, artist_search_cache, review | `true_nomatch_zero.csv` (in place), `flagged_composite_partial.csv` |
| `retry_musicbrainz_zero_matches.py` ⚠✎ | 4.1 KB | 09-27 | `true_nomatch_zero.csv`, cache, matches | matches, review, cache (append) |
| `search_zero_results_by_components.py` ⚠ | 10.6 KB | 09-27 | `true_nomatch_zero.csv`, zero_component_searches | zero_component_searches (append), zero_component_results, zero_component_summary, targeted_artist_searches |
| `resolve_musicbrainz_ambiguities.py` ✎ | 12.5 KB | 09-27 | roster, matches, review, cache, spotify_album_sample | matches, review, ambiguity_auto_resolution, unresolved_balance |
| `apply_musicbrainz_identity_decisions.py` ✎ | 5.7 KB | 09-27 | matches, review, targeted_artist_searches | matches, review, targeted_identity_decisions |
| `report_musicbrainz_resolution_balance.py` | 6.3 KB | 09-27 | matches, roster, spotify_album_sample, billboard200 | unresolved_balance |
| `collect_musicbrainz_discographies.py` ⚠ | 18.1 KB | 09-28 | matches, release_group_cache, official_release_cache | both caches (append), discography_api_errors, release_groups, official_releases, standard_album_candidates |
| `validate_album_collection.py` | 7.9 KB | 09-28 | matches, roster, release_groups, album_candidates, spotify_album_sample, artist cache, billboard200 | billboard_coverage, spotify_count_comparison |
| `validate_musicbrainz_collection.py` (also a module) | 8.2 KB | 09-28 | matches, release_groups, album_candidates, artist cache | genre_balance, unresolved_genre_breakdown, subgenre_balance, edition_handcheck_sample |
| `adjudicate_edition_handcheck.py` ✎ | 3.6 KB | 09-28 | edition_handcheck_sample, official_release_cache | edition_handcheck_sample (in place) |
| `prepare_genre_handcheck.py` | 5.1 KB | 09-28 | album_candidates, matches, artist cache, spotify_album_sample | genre_handcheck_sample_100 |
| `analyze_musicbrainz_digital_robustness.py` (also a module: `build_data`) | 7.8 KB | 09-28 | album_candidates, official_releases, matches, artist cache | digital_robustness |
| `analyze_musicbrainz_first_pass.py` | 4.4 KB | 09-28 | via `build_data` | `results/phase3_first_pass/` headline, headline_means, analysis_sample |
| `__pycache__/` (5 .pyc) | about 46 KB | 09-27/28 | — | Compiled files, ignore |

### B6. `data/` (all names below start with `musicbrainz_` unless shown otherwise)
| File | Size | Modified | Written by | Read by | Suggested class |
|---|---|---|---|---|---|
| `artist_search_cache.jsonl` | 18.8 MB | 09-27 | match, retry (append) | 7 scripts | **cache: never delete** |
| `release_group_cache.jsonl` | 45.7 MB | 09-28 | collect | collect | **cache** |
| `official_release_cache.jsonl` | 630.6 MB | 09-28 | collect | collect, adjudicate | **cache** |
| `zero_component_searches.jsonl` | 297 KB | 09-30 | search_zero | search_zero | **cache** (modified 09-30, two days after the last devlog entry) |
| `artist_search_errors.jsonl` | 205 B | 09-27 | match | (retry mentions it) | log |
| `discography_api_errors.jsonl` | 1.6 KB | 09-28 | collect | — | log |
| `release_groups.csv` | 36.2 MB | 09-28 | collect | validate×2, collect, q1b/album_age† | external table |
| `official_releases.csv` | 638.7 MB | 09-28 | collect | digital_robustness | external table |
| `standard_album_candidates.csv` | 11.5 MB | 09-28 | collect | 4 scripts | external table / interim |
| `artist_matches.csv` | 2.4 MB | 09-27 | match, retry, resolve, apply | 9 scripts + q1b/build† | interim (key) |
| `artist_matches_review.csv` | 1.1 MB | 09-27 | match, retry, resolve, apply | audit | interim |
| `ambiguity_auto_resolution.csv` | 877 KB | 09-27 | resolve | — | audit |
| `targeted_artist_searches.csv` | 3.3 KB | 09-27 | search_zero | apply | interim |
| `targeted_identity_decisions.csv` | 1.1 KB | 09-27 | apply | — | audit |
| `confirmed_not_found.csv` | 1.1 KB | 09-27 | **none (hand-made)** | — | audit |
| `zero_component_results.csv` | 22.1 KB | 09-27 | search_zero | — | audit |
| `zero_component_summary.csv` | 8.6 KB | 09-27 | search_zero | — | audit |
| `unresolved_balance.csv` | 1.1 KB | 09-27 | resolve, report_balance | — | audit |
| `billboard_coverage.csv` | 366 B | 09-28 | validate_album | — | validation output |
| `spotify_count_comparison.csv` | 47.8 KB | 09-28 | validate_album | — | validation output |
| `genre_balance.csv` | 448 B | 09-28 | validate_mb | — | validation output (3-row summary) |
| `subgenre_balance.csv` | 650 B | 09-28 | validate_mb | — | validation output |
| `unresolved_genre_breakdown.csv` | 1.2 KB | 09-28 | validate_mb | — | validation output |
| `edition_handcheck_sample.csv` | 33.8 KB | 09-28 | validate_mb, adjudicate | adjudicate | **hand-check, protect** |
| `genre_handcheck_sample_100.csv` (no prefix) | 123 KB | 09-28 | prepare_genre_handcheck | — | **hand-check** |
| `digital_robustness.csv` | 559 B | 09-28 | digital_robustness | — | result |
| `pre_rule_artist_roster.csv` (no prefix) | 212 KB | 09-27 | build_roster | 4 scripts | interim (key) |
| `pre_rule_artist_credit_audit.csv` (no prefix) | 474 KB | 09-27 | build_roster | — | audit |
| `spotify_album_sample.csv` (no prefix) | 242 KB | 09-27 | build_album_sample | 6 scripts | interim |

† hard-coded `/mnt/` path.

### B7. `results/`
| Folder | Files | Size | Producer | Notes |
|---|---|---|---|---|
| `phase1_original/` | 18 | about 196 KB | **none saved** (redirected reproduction, devlog §7) | Archive candidate |
| `phase1_clean/` | 19 | about 20 KB | `code/analyze_albums.py` | Spotify-sample exploratory results, superseded by the MusicBrainz design |
| `phase3_first_pass/` | 3 | 1.9 MB | `code/analyze_musicbrainz_first_pass.py` | **Current Part 1 headline.** `analysis_sample.csv` is also the per-artist genre source for Q1b |

### B8. `q1_incumbency/` (Part 2)
| File | Size | Modified | Notes |
|---|---|---|---|
| `q1_analysis_plan.md` | 2.2 KB | 10-02 | Plan written before estimation |
| `q1_incumbency.py` | 5.5 KB | 10-02 | Hard-coded `/mnt/` input; outputs go to `results/` relative to the working directory |
| `devlog_section_21.md` | 3.0 KB | 10-02 | To append to devlog |
| `results/A_break_tests.csv` … `annual_means.csv` (7 small CSVs) | about 7 KB | 10-02 | All written by `q1_incumbency.py`. `A_break_tests.csv` holds the numbers that must reproduce |
| `results/weekly_billboard200.csv` | 157 KB | 10-02 | Written by `q1_incumbency.py` |

### B9. `q1b_genre_staying_power/` (Part 2b)
| File | Size | Modified | Notes |
|---|---|---|---|
| `q1b_analysis_plan.md` | 2.2 KB | 10-02 | Plan written before estimation |
| `build.py` | 1.7 KB | 10-02 | Hard-coded `/mnt/`. Reads billboard200, artist_matches, analysis_sample. Writes `chart_labelled.pkl` to the working directory (missing) |
| `analyze.py` | 4.7 KB | 10-02 | Reads the pkl. Writes album_runs, results_main and results_event_study to the working directory |
| `album_age.py` | 1.6 KB | 10-02 | Reads the pkl and release_groups (hard-coded `/mnt/`). Writes results_album_age_share to the working directory |
| `devlog_section_22.md` | 2.9 KB | 10-02 | To append to devlog |
| `results/` (4 CSVs) | 302 KB | 10-02 | Moved into `results/` by hand. Not regenerable until `build.py` is rerun |

---

## C. Questions for your review
1. **`kaggle_results/` vs `results/phase1_original/`:** 11 files differ in value. Should I diff them during stage 2, or archive both as they are?
2. **`true_nomatch_zero.csv` and `flagged_composite_partial.csv`:** should they go to `data/interim/`, with the scripts repointed? The original 92-row version can't be recovered.
3. **`.venv/`:** gitignore it and leave it in place, or archive or remove it (with your approval)?
4. **OneDrive:** are you happy to `git init` inside the OneDrive folder, or would you rather pause syncing or move the project first?
5. **Stage 5 strategy:** rerun only the offline steps (from `artist_matches.csv` onward: collect in cache-only mode → validate → first_pass, plus q1 and q1b), or add a cache-only guard to the API scripts so the full chain can run? The second option means editing code that calls the API.
