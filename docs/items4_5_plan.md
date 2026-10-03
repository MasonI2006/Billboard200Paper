# Plan: per-artist genre file, album-order control, and the remaining frozen-plan Part 1 checks

Written 2026-10-02, **before any estimation** (CLAUDE.md rule 6). Covers PROJECT_CONTEXT §11 items 3–4 (labelled "4 and 5" in the 2026-10-02 discussion). The author authorised running them without a further approval step. Nothing here changes the frozen headline. Every result is reported, including nulls.

Common conventions (as in `docs/part1_secondary_rerun_plan.md`): headline fixed effects `C(genre) + C(year)`, artist-clustered SEs, and the genre-level restricted Webb wild bootstrap (9,999 draws, seed 20260928, `code/inference.py`). Part 1 sample: the corrected headline sample (6,775 albums, ordered genre rule).

## 1. Per-artist genre file (item 3)

- **Output:** `data/final/artist_genres.csv`, one row per resolved roster artist with a genre (2,451 artists). Columns: roster key, name, MusicBrainz ID, genre, streaming-heavy flag, all matched genres, and whether the ordered tie-break decided. Written by a new pipeline step (`code/12a_export_artist_genres.py`) from the same `infer_row_genre()` used everywhere else.
- **Part 2b with the file:** rerun the unchanged Part 2b scripts with genre labels from the artist file instead of the Part 1 sample (which only labels artists who have an album in that sample: 1,941). Report the main estimate (weeks in first 52, post × heavy) with both inference methods below.
- **Status:** the Part 2b plan (`docs/q1b_analysis_plan.md`) names the Part 1 sample as the label source. The artist-file version is therefore a **secondary** specification. The reported Part 2b result is not replaced. The author can decide later whether to adopt the broader file as primary, which would need a dated note.

## 2. Album-order (career-stage) control (item 4; required by the frozen plan)

**Part 1.**
- **Main definition (career start, as the plan prefers when history is available):** ordinal number of the album among the lead roster artist's MusicBrainz studio albums (release groups with `eligible_headline_type`, i.e. primary type Album, no secondary types, not Mixtape/Street) since the start of their career. The lead artist is the first credited roster artist.
- Ordering is by first release date. Year-only dates count as 1 January of their year, as in the headline; ties are broken by release-group ID. The 449 release groups without a date are left out of the ordering.
- **Incomplete histories:** pre-2009 albums have no track counts, so the career ordinal counts every studio album regardless of length. An artist whose earlier albums are missing from MusicBrainz gets a lower ordinal than the truth. This is a stated limitation.
- **Control:** album-order fixed effects in bins 1, 2, 3, 4–5, 6–9, 10+.
- **Alternate definition (also in the plan):** ordinal since 2009 among the artist's eligible standard-album candidates (≥6 tracks, same date and tie rules), same bins.
- Model: `ln_tracks ~ post:heavy + C(genre) + C(year) + C(order_bin)`.

**Part 2b.**
- Ordinal of the album's Billboard 200 debut among all the artist's Billboard 200 album debuts since the chart's start (1963). Chart rows are mapped to artists as in the Part 2b build script. Same bins.
- Model: the main Part 2b model plus `C(order_bin)`.

## 3. Remaining frozen-plan Part 1 secondary checks

| # | Check (frozen plan wording) | Implementation |
|---|---|---|
| a | Artist fixed effects | `ln_tracks ~ post:heavy + C(year)` with artist fixed effects absorbed by within-artist demeaning; artists with a single album dropped (they carry no information). Report the number of artists with both pre- and post-rule albums. |
| b | Drop each artist's albums released on or before their first qualifying Billboard 200 debut | Lead roster artist's `first_qualifying_debut` (Kaggle stored date). Year-only albums dated in the debut year count as 1 January, so they are dropped (conservative). |
| c | Mixtape/Street robustness sample | Headline sample plus Mixtape/Street release groups meeting the same rules (2009–2019, ≥6 tracks, a genre, 2014 year-only and month-only Nov 2014 excluded). |
| d | 2009–2024 window | Candidates in the secondary window, same rules. The 2018 and 2020 rule changes fall inside it; noted, not modelled. |
| e | 2010–2019 window | Headline sample without 2009. |
| f | Continuous genre intensity | `post:intensity` in place of `post:heavy`, using the Nielsen ratios in the plan. |
| g | Exclude electronic | Headline model without electronic albums. |
| h | Running time | Log running time; albums whose tracks all have durations. |
| i | More than 12 tracks | Linear probability, headline model. |
| j | 18 or more tracks | Linear probability, headline model. |

All of a–j and both Part 1 album-order specifications get artist-clustered and genre-bootstrap inference.
- **Part 2b:** the artist-file and album-order versions are reported with artist-clustered inference and the same genre bootstrap as the Part 1 checks (`code/inference.py`, artist-clustered t-statistics). The Part 2b baseline is re-estimated under that method, so the comparison is like for like.
- The Part 2b script's own bootstrap uses genre-clustered t-statistics, which is why its p-value (0.015) can differ from the `inference.py` version. Both are shown.
- **Not run:** the plan's "broader major-label list, if assembled". No such list exists.

## 4. Also in this batch (not a new estimate)

`code/22_part2b_analyze.py` falls back to a within-artist (demeaned) estimator when the artist-dummy regression fails numerically, as it did on the rock + pop variant labels. The coefficient is mathematically identical to the dummy version. The clustered SE can differ slightly because absorbed fixed effects are not counted in the small-sample correction. It is used only when the dummy version fails, so reported outputs are unchanged.

## 5. Outputs

- `results/part1_album_length/secondary/plan_checks.csv` (2 album-order specifications and a–j, with the headline as a baseline row).
- `results/part2b_genre_staying_power/extensions.csv` (baseline, artist-file labels, album order).
- Logged in `docs/devlog.md` §26; PROJECT_CONTEXT updated.

## Post-estimation notes (2026-10-03)

Added after running; the plan above is unchanged.
- **Artist count:** the per-artist file holds 2,034 resolved artists, not 2,451. The 2,451 in the validation table includes 417 unresolved roster names without a MusicBrainz ID.
- **Within-estimator SE (section 4):** "can differ slightly" was wrong. On the reported Part 2b labels the within SE is 0.813, against 1.049 for the dummy version (same coefficient). The dummy version counts ~1,800 absorbed artist dummies in the clustered small-sample correction. The reported Part 2b artist-FE result keeps the dummy-version SE; see devlog §26.
- **Artist clusters:** while building check (a), the artist-cluster variable was found to be the first word of the artist's name (pandas regex split). It was fixed before any of this plan's estimates were run; see devlog §26.
