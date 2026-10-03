# Plan: rerun of the Part 1 secondary checks, and the rock + pop genre sensitivity check

Written 2026-10-02, **before any estimation** (CLAUDE.md rule 6). It covers PROJECT_CONTEXT §11 items 1 and 2: rerun the Part 1 secondary checks first done in Claude chat, now under the ordered genre rule, and run one exploratory sensitivity check of that rule. Nothing here changes the frozen headline (`docs/analysis_plan.md`).

## A. Why a reconstruction is needed

The chat-era checks (PROJECT_CONTEXT §7) used the random 09-28 genre labels, and their scripts were never saved. Only the summary numbers survive. The checks below are rebuilt from those descriptions and the frozen plan's list of secondary checks. Before any estimate under the new labels is looked at, the rebuilt code is run on the **old 09-28 labels** (the committed `analysis_sample.csv` from commit `958405e`) and compared with the chat numbers. This tests whether the reconstruction matches what was run. The specifications are fixed by this plan and will **not** be adjusted to make the old numbers match. Any gap is reported.

## B. Data and flags

- **Sample:** `data/final/analysis_sample.csv`, 1,663 albums with a genre, ordered rule (the headline sample).
- **Charted:** the album has at least one Billboard 200 row (any week, `data/raw/billboard200.csv`) for the same MusicBrainz artist ID and album title. Chart artist credits are mapped to artist IDs through `musicbrainz_artist_matches.csv`. Artist and title are both normalised with the chat-era rule (ASCII-fold, lowercase, keep only `a-z 0-9` and spaces). It flags 1,172 albums against the chat's 1,168 (gap of 4, 0.24%). Genre is not involved, so the flag is the same under old and new labels.
- **Debut rank:** rank in the album's first chart week. **Weeks on chart:** number of distinct chart weeks for the album; outcome `ln(weeks)`.
- **UK origin:** the first credited artist's MusicBrainz `area` is United Kingdom, England, Scotland, Wales or Northern Ireland. It flags 176 albums, 47 of them post-rule, exactly the chat's 47.
- **Seconds per track:** `running_time_minutes × 60 / tracks_with_duration`, for albums where every track has a duration (`tracks_with_duration == standard_tracks`); outcome is its log.
- **Day-one multi-edition launch:** the release group's `same_day_different_length_editions` flag (several official editions of different length on the first release date).

## C. Specifications (all use the headline fixed effects `C(genre) + C(year)`, artist-clustered SEs)

| # | Check | Sample | Model | Term reported | Inference |
|---|---|---|---|---|---|
| 1 | Charted subsample | charted albums | `ln_tracks ~ post:heavy + FE` | post:heavy | artist-clustered + genre Webb bootstrap |
| 2 | Non-charted subsample | non-charted albums | same | post:heavy | artist-clustered + genre Webb bootstrap |
| 3 | Selection test (frozen plan) | all 1,663 | `charted ~ ln_tracks + ln_tracks:post + ln_tracks:heavy + ln_tracks:post:heavy + post:heavy + FE` (linear probability) | ln_tracks:post:heavy | artist-clustered + genre Webb bootstrap |
| 4a | Chart payoff: debut rank | charted | `debut_rank ~` same right-hand side as 3 | ln_tracks:post:heavy | artist-clustered + genre Webb bootstrap |
| 4b | Chart payoff: weeks | charted | `ln_weeks ~` same right-hand side as 3 | ln_tracks:post:heavy | artist-clustered + genre Webb bootstrap |
| 5 | Event study (frozen plan) | all 1,663 | `ln_tracks ~ Σ_y heavy×1[year=y] (y ≠ 2014) + FE` | each year; joint Wald test of 2009–2013 | artist-clustered |
| 6a | Exploratory: seconds per track | full-duration albums | `ln_sec_per_track ~ post:heavy + FE` | post:heavy | artist-clustered |
| 6b | Exploratory: day-one multi-edition | all 1,663 | `multi_edition ~ post:heavy + FE` | post:heavy | artist-clustered |
| 6c | Exploratory: UK origin | all 1,663 | `over12 ~ uk + post:uk + FE` | post:uk | artist-clustered |

The genre Webb bootstrap is the headline's: restricted wild cluster bootstrap at the genre level, Webb six-point weights, 9,999 draws, seed 20260928, restricted model = the same model without the reported term. Checks 6a–6c were already looked at in chat ("already peeked"), so they stay exploratory whatever they show.

## D. Exploratory sensitivity: rock + pop → pop

`docs/genre_classification.md` flags rock + pop → rock (326 two-genre artists) as the rule's largest judgement call. **Variant:** swap rock and pop in the priority order (latin, hip-hop/R&B, country, Christian, jazz, classical, electronic, **pop, rock**). Only artists whose tags match both rock and pop, and no higher-priority genre, change from rock to pop. Everything else is unchanged.

Estimated under the variant labels, with the same specification and inference as the current results:
- Part 1 headline (log tracks, `post:heavy`, artist-clustered + genre Webb bootstrap).
- Part 2b main estimate (weeks in first 52, `post:heavy`, artist-clustered + genre Webb bootstrap), by running the existing Part 2b scripts on the variant labels.

This check is **exploratory**. It cannot replace the ordered-rule results, whatever it shows, and both are reported.

## E. Outputs

- `code/18_part1_secondary_checks.py` writes `results/part1_album_length/secondary/secondary_checks.csv` and `event_study.csv`. Run with `--sample <old file> --tag old_labels` it writes the validation versions.
- `code/19_genre_rule_sensitivity.py` writes `results/part1_album_length/secondary/rockpop_sensitivity.csv`.
- Results are logged in `docs/devlog.md` §25, and PROJECT_CONTEXT §7 is updated.
