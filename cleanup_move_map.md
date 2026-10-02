# Cleanup stage 2: proposed layout and move map

Proposed 2026-10-02. **Nothing has been moved yet. Waiting for approval.** Builds on `cleanup_inventory.md` and your answers to its questions:
1. Your discretion on `kaggle_results` vs `phase1_original`. Checked: the two match to floating-point precision. The only real difference is a tie-break in `S_albums_core.csv`, where two rows swap `artist_pop` 89↔90. Both go to the archive, with `kaggle_results/` as the canonical first-round record.
2. The root-level `true_nomatch_zero.csv` and `flagged_composite_partial.csv` move to `data/interim/` and the scripts are repointed.
3. `.venv/` goes to the archive and out of the project root. It is moved, not deleted, and gitignored.
4. `git init` inside OneDrive is fine.
5. Add a cache-only guard so the full chain can run.

## 1. Target layout

```
Billboard200Paper/
  CLAUDE.md  PROJECT_CONTEXT.md  README.md (new, short)  .gitignore (new)
  docs/        analysis_plan.md (frozen, content unchanged), q1_analysis_plan.md, q1b_analysis_plan.md,
               devlog.md, llm_use_log.md (new), cleanup_inventory.md, cleanup_move_map.md
  data/raw/        Kaggle and Spotify inputs (read-only; names unchanged, including the space)
  data/external/   MusicBrainz caches, API error logs, and the tables the collector writes
  data/interim/    roster, matches, identity audits and decisions, Spotify album sample, zero-match lists
  data/final/      analysis-ready samples (Part 1 analysis sample, Part 2 weekly series, Part 2b album runs)
  code/            paths.py, load_clean_data.py, musicbrainz_helpers.py, numbered scripts 01–23, run_pipeline.py
  results/part1_album_length/            headline, digital robustness, validation/, spotify_exploratory/
  results/part2_incumbency/
  results/part2b_genre_staying_power/
  archive/         first-round code and results, the phase1 reproduction, root strays, devlog section files, old venv
```

## 2. Move map

All moves use `git mv` after the initial commit, so history follows each file. Nothing is deleted.

### 2a. Raw data: `OriginalDataFiles/` → `data/raw/`
| Old | New |
|---|---|
| `OriginalDataFiles/billboard200.csv` | `data/raw/billboard200.csv` |
| `OriginalDataFiles/hot100.csv` | `data/raw/hot100.csv` |
| `OriginalDataFiles/streaming.csv` | `data/raw/streaming.csv` |
| `OriginalDataFiles/digital.csv` | `data/raw/digital.csv` |
| `OriginalDataFiles/radio.csv` | `data/raw/radio.csv` |
| `OriginalDataFiles/track_data_final.csv` | `data/raw/track_data_final.csv` |
| `OriginalDataFiles/spotify_data clean.csv` | `data/raw/spotify_data clean.csv` (name kept) |
| `OriginalDataFiles/dataset-metadata.json` | `data/raw/dataset-metadata.json` |

### 2b. `data/` → `data/external/` (caches and collector output: never delete)
| Old | New |
|---|---|
| `data/musicbrainz_artist_search_cache.jsonl` | `data/external/musicbrainz_artist_search_cache.jsonl` |
| `data/musicbrainz_release_group_cache.jsonl` | `data/external/musicbrainz_release_group_cache.jsonl` |
| `data/musicbrainz_official_release_cache.jsonl` | `data/external/musicbrainz_official_release_cache.jsonl` |
| `data/musicbrainz_zero_component_searches.jsonl` | `data/external/musicbrainz_zero_component_searches.jsonl` |
| `data/musicbrainz_artist_search_errors.jsonl` | `data/external/musicbrainz_artist_search_errors.jsonl` |
| `data/musicbrainz_discography_api_errors.jsonl` | `data/external/musicbrainz_discography_api_errors.jsonl` |
| `data/musicbrainz_release_groups.csv` | `data/external/musicbrainz_release_groups.csv` |
| `data/musicbrainz_official_releases.csv` | `data/external/musicbrainz_official_releases.csv` |
| `data/musicbrainz_standard_album_candidates.csv` | `data/external/musicbrainz_standard_album_candidates.csv` |

### 2c. → `data/interim/`
| Old | New |
|---|---|
| `data/pre_rule_artist_roster.csv` | `data/interim/pre_rule_artist_roster.csv` |
| `data/pre_rule_artist_credit_audit.csv` | `data/interim/pre_rule_artist_credit_audit.csv` |
| `data/spotify_album_sample.csv` | `data/interim/spotify_album_sample.csv` |
| `data/musicbrainz_artist_matches.csv` | `data/interim/musicbrainz_artist_matches.csv` |
| `data/musicbrainz_artist_matches_review.csv` | `data/interim/musicbrainz_artist_matches_review.csv` |
| `data/musicbrainz_ambiguity_auto_resolution.csv` | `data/interim/musicbrainz_ambiguity_auto_resolution.csv` |
| `data/musicbrainz_targeted_artist_searches.csv` | `data/interim/musicbrainz_targeted_artist_searches.csv` |
| `data/musicbrainz_targeted_identity_decisions.csv` | `data/interim/musicbrainz_targeted_identity_decisions.csv` |
| `data/musicbrainz_confirmed_not_found.csv` | `data/interim/musicbrainz_confirmed_not_found.csv` |
| `data/musicbrainz_zero_component_results.csv` | `data/interim/musicbrainz_zero_component_results.csv` |
| `data/musicbrainz_zero_component_summary.csv` | `data/interim/musicbrainz_zero_component_summary.csv` |
| `data/musicbrainz_unresolved_balance.csv` | `data/interim/musicbrainz_unresolved_balance.csv` |
| `true_nomatch_zero.csv` (root) | `data/interim/true_nomatch_zero.csv` |
| `flagged_composite_partial.csv` (root) | `data/interim/flagged_composite_partial.csv` |
| *(regenerated, currently missing)* `chart_labelled.pkl` | `data/interim/part2b_chart_labelled.pkl` (gitignored) |

### 2d. → `data/final/`
| Old | New |
|---|---|
| `results/phase3_first_pass/analysis_sample.csv` | `data/final/analysis_sample.csv` (Part 1 sample; also the Part 2b genre source) |
| `q1_incumbency/results/weekly_billboard200.csv` | `data/final/part2_weekly_billboard200.csv` |
| `q1b_genre_staying_power/results/album_runs.csv` | `data/final/part2b_album_runs.csv` |

### 2e. → `results/`
| Old | New |
|---|---|
| `results/phase3_first_pass/headline.csv` | `results/part1_album_length/headline.csv` |
| `results/phase3_first_pass/headline_means.csv` | `results/part1_album_length/headline_means.csv` |
| `data/musicbrainz_digital_robustness.csv` | `results/part1_album_length/digital_robustness.csv` |
| `data/musicbrainz_billboard_coverage.csv` | `results/part1_album_length/validation/musicbrainz_billboard_coverage.csv` |
| `data/musicbrainz_spotify_count_comparison.csv` | `results/part1_album_length/validation/musicbrainz_spotify_count_comparison.csv` |
| `data/musicbrainz_genre_balance.csv` | `results/part1_album_length/validation/musicbrainz_genre_balance.csv` |
| `data/musicbrainz_subgenre_balance.csv` | `results/part1_album_length/validation/musicbrainz_subgenre_balance.csv` |
| `data/musicbrainz_unresolved_genre_breakdown.csv` | `results/part1_album_length/validation/musicbrainz_unresolved_genre_breakdown.csv` |
| `data/musicbrainz_edition_handcheck_sample.csv` | `results/part1_album_length/validation/musicbrainz_edition_handcheck_sample.csv` |
| `data/genre_handcheck_sample_100.csv` | `results/part1_album_length/validation/genre_handcheck_sample_100.csv` (holds manual judgements) |
| `results/phase1_clean/*` (19 files) | `results/part1_album_length/spotify_exploratory/*` (still produced by script 02, so kept live rather than archived) |
| `q1_incumbency/results/A_break_tests.csv`, `B_placebo_dates.csv`, `C_song_chart_comparison.csv`, `D_with_2018_break.csv`, `E_debut_first_run_break.csv`, `E_debut_first_runs_by_year.csv`, `annual_means.csv` | `results/part2_incumbency/` (same names) |
| `q1b_genre_staying_power/results/results_main.csv`, `results_event_study.csv`, `results_album_age_share.csv` | `results/part2b_genre_staying_power/` (same names) |

### 2f. Code: `code/` (+ q1/q1b scripts)
Numbers give the run order. Modules imported by other scripts stay unnumbered, because Python can't import a name that starts with a digit. The identity-step order (05 → 10) comes from devlog §13–15 and the final file timestamps, which show resolve ran, then apply, then report. Stage 5 confirms this order by reproducing 2,367 resolved artists.

| Old | New | Notes |
|---|---|---|
| *(new)* | `code/paths.py` | Every directory and file path, relative to the project root |
| `code/load_clean_data.py` | `code/load_clean_data.py` | Unchanged name (helper module for the Kaggle and Spotify loaders) |
| *(new)* | `code/musicbrainz_helpers.py` | Shared MusicBrainz functions moved here **verbatim** (see §4) and the cache-only guard |
| `code/build_album_sample.py` | `code/01_build_spotify_album_sample.py` | |
| `code/analyze_albums.py` | `code/02_spotify_exploratory_analysis.py` | |
| `code/build_pre_rule_artist_roster.py` | `code/03_build_pre_rule_roster.py` | |
| `code/match_musicbrainz_artists.py` | `code/04_match_musicbrainz_artists.py` | API (guarded) |
| `code/retry_musicbrainz_zero_matches.py` | `code/05_retry_zero_matches.py` | API (guarded; replays cache) |
| `code/audit_musicbrainz_search_exceptions.py` | `code/06_audit_search_exceptions.py` | |
| `code/search_zero_results_by_components.py` | `code/07_search_zero_components.py` | API (guarded) |
| `code/resolve_musicbrainz_ambiguities.py` | `code/08_resolve_ambiguities.py` | |
| `code/apply_musicbrainz_identity_decisions.py` | `code/09_apply_identity_decisions.py` | |
| `code/report_musicbrainz_resolution_balance.py` | `code/10_report_resolution_balance.py` | |
| `code/collect_musicbrainz_discographies.py` | `code/11_collect_discographies.py` | API (guarded) |
| `code/validate_musicbrainz_collection.py` | `code/12_validate_musicbrainz_collection.py` | |
| `code/adjudicate_edition_handcheck.py` | `code/13_adjudicate_edition_handcheck.py` | Automated from cache |
| `code/validate_album_collection.py` | `code/14_validate_album_collection.py` | |
| `code/prepare_genre_handcheck.py` | `code/15_prepare_genre_handcheck.py` | **One-time; left out of the rerun chain**, because it would wipe the manual judgement columns |
| `code/analyze_musicbrainz_digital_robustness.py` | `code/16_part1_digital_robustness.py` | |
| `code/analyze_musicbrainz_first_pass.py` | `code/17_part1_headline.py` | |
| `q1_incumbency/q1_incumbency.py` | `code/20_part2_incumbency.py` | Repoint `/mnt/` |
| `q1b_genre_staying_power/build.py` | `code/21_part2b_build.py` | Repoint `/mnt/` |
| `q1b_genre_staying_power/analyze.py` | `code/22_part2b_analyze.py` | Repoint (outputs relative to the working directory) |
| `q1b_genre_staying_power/album_age.py` | `code/23_part2b_album_age.py` | Repoint `/mnt/` |
| *(new)* | `code/run_pipeline.py` | Runs 01–23 in order (skips 15). Cache-only unless `--allow-api` is passed |
| `code/__pycache__/` | stays, gitignored | Stale `.pyc` files are harmless |

### 2g. Docs
| Old | New |
|---|---|
| `analysis_plan.md` | `docs/analysis_plan.md` (**content unchanged**) |
| `q1_incumbency/q1_analysis_plan.md` | `docs/q1_analysis_plan.md` |
| `q1b_genre_staying_power/q1b_analysis_plan.md` | `docs/q1b_analysis_plan.md` |
| `devlog.md` | `docs/devlog.md`. Append §21 and §22 from the chat files, then the cleanup as §23. Leave the §16 numbering gap and add a note about it |
| `cleanup_inventory.md`, `cleanup_move_map.md` | `docs/` |
| *(new)* | `docs/llm_use_log.md` |
| *(new)* | `README.md` (short: project, layout, how to run) |

### 2h. → `archive/`
| Old | New |
|---|---|
| `InitialAnalysisCode/` | `archive/InitialAnalysisCode/` (untouched, broken filename left as is) |
| `kaggle_results/` | `archive/kaggle_results/` (canonical first-round results) |
| `results/phase1_original/` | `archive/phase1_original_reproduction/` |
| `D_artist_exposure.csv` (root) | `archive/root_strays/D_artist_exposure.csv` (byte-identical to `kaggle_results/`) |
| `README_album_padding.md` | `archive/README_album_padding.md` |
| `q1_incumbency/devlog_section_21.md` | `archive/devlog_sections_from_chat/` (after appending) |
| `q1b_genre_staying_power/devlog_section_22.md` | `archive/devlog_sections_from_chat/` (after appending) |
| `.venv/` | `archive/venv_msys_py312/` (gitignored) |

`.vscode/settings.json` stays where it is. Once everything is moved, these folders will be empty: `OriginalDataFiles/`, `q1_incumbency/`, `q1b_genre_staying_power/`, `results/phase1_clean/`, `results/phase1_original/` and `results/phase3_first_pass/`. **I'll remove them only if you approve.**

## 3. Git (stage 3, before any move)
`git init`, add the `.gitignore` below, then commit the current state with everything in its current location.

```
data/raw/
data/external/
OriginalDataFiles/
data/*cache*.jsonl
data/musicbrainz_release_groups.csv
data/musicbrainz_official_releases.csv
data/musicbrainz_standard_album_candidates.csv
*.pkl
__pycache__/
*.pyc
.venv/
archive/venv_msys_py312/
```
The old-location lines cover the first commit, before the moves. Everything else is tracked: code, docs, `data/interim/` (about 6 MB), `data/final/` (about 2.3 MB), results and the archive. Tracking interim and results is what makes stage 5 safe: any file a rerun overwrites can be diffed against the commit and restored. Raw data and caches are never committed and never touched.

## 4. Code changes (stage 4)
- **`paths.py`:** `ROOT = Path(__file__).resolve().parents[1]`, plus `RAW`, `EXTERNAL`, `INTERIM`, `FINAL`, `RESULTS_P1`, `RESULTS_P2`, `RESULTS_P2B` and a constant for every file. Every script imports it, replacing the 14 local `PROJECT_ROOT` / `DATA_DIR` definitions.
- **`musicbrainz_helpers.py`:**
  - Functions moved verbatim: `normalize_name`, `punctuation_insensitive_name`, `load_roster`, `load_cache`, `request_artist_search`, `log_search_error`, `append_cache` and the request constants (from script 04); `normalize`, `read_artist_cache`, `genre_from_text`, `candidate_genres`, `exact_candidates`, `infer_row_genre` (from 12); `digital_track_counts`, `build_data` (from 16).
  - The scripts that use them import from here. That is the only way to keep cross-script imports working after numbering.
- **Cache-only guard:**
  - **The default is no network.** Requests run only with `--allow-api` (or `BB200_ALLOW_API=1`).
  - In cache-only mode, a cache miss raises `CacheMissError`, naming the key and the script. It never quietly calls the API.
  - Scripts 05 and 07 replay the cached response for each key instead of requesting it again.
  - The guard covers both request functions: `request_artist_search` (04, 05, 07) and `request_json` (11).
- **Scripts 20–23:** inputs come from `paths.py`; outputs go to `results/part2*` and `data/final`; the pickle goes to `data/interim`.
- **No analysis logic changes.** If any number moves in stage 5, I'll report it and won't patch around it.

## 5. Stage 5 preview
Run `run_pipeline.py` in cache-only mode, then check the "must reproduce" numbers in CLAUDE.md. Then `git diff --stat` on `data/interim/`, `data/final/` and `results/` against the commit, to catch any overwritten file that changed. The edition hand-check is regenerated and re-adjudicated by scripts 12 and 13, and should come out identical. The genre hand-check is not regenerated.
