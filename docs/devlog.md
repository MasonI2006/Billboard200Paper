# Devlog: Chart Rules and Album Padding

A running record of what has been done so far, what was found, and what is still open. Read `README_album_padding.md` first for the project idea; this file is the history and the technical detail behind it.

---

## 1. Project setup and fact-checking

**Goal:** an economics paper for the *Journal of Cultural Economics* asking whether Billboard's Dec 2014 switch to counting streams on the album chart led artists to make longer albums.

**Institutional facts verified (Sept 2026, from Billboard, Official Charts Company, trade press):**

| Event | Detail |
|---|---|
| Billboard 200 adds streams | Chart dated **Dec 13, 2014** (tracking week ending Nov 30, 2014). 1 album unit = 1 album sale = 10 track downloads = **1,500 on-demand audio streams** of songs from the album. |
| Paid vs. free streams weighted | Chart dated **July 14, 2018**: 1,250 paid streams or 3,750 ad-supported streams = 1 unit. Video still excluded. |
| Video/YouTube added | Chart dated **Jan 18, 2020**. Merch-bundle rules tightened the same month. |
| Merch/ticket bundles dropped | Announced July 2020; tours from Oct 2, 2020; exact merch start date unconfirmed. |
| Later change (outside window) | Chart dated Jan 17, 2026: 1,000 paid / 2,500 free streams = 1 unit. YouTube pulled its data from US Billboard charts after Jan 16, 2026. |
| UK album chart | Streams counted from **1 March 2015**, but only the **top 12 songs** of the standard edition (top two down-weighted) — **from the start**. The README's original idea that the UK added a cap later was wrong; there is no "reversal" to exploit. Germany (2016) and Australia (2017) use similar caps. |

**Other checks:**
- **Genre streaming intensity (Nielsen 2014 US year-end report):** each genre's share of streams divided by its share of album sales. Electronic 3.40, Latin 2.08, hip-hop/R&B 2.05, pop 1.95, rock 0.74, country 0.54, Christian 0.44, holiday 0.31, children 0.27, jazz 0.15, classical 0.14. Decision: use this ratio, not a genre's raw share of all streams, because raw share mostly measures genre size (rock has 25% of streams but 33% of album sales).
- **Spotify Web API:** popularity scores, follower counts, audio features and batch endpoints are no longer available to new developer apps (Nov 2024 and Feb 2026 changes). Existing datasets that already contain these fields are fine.
- **JCE rules:** max 30 pages including tables and figures; abstract 150–250 words; 4–6 keywords; JEL codes; LLM use must be described in the Methods section.
- **Literature:** Winkler et al. (2026, *Quantitative Marketing and Economics*, DOI 10.1007/s11129-026-09312-2) confirmed. Lech et al. year may be 2025, not 2024 (check). Added Gourévitch (2023, *Music & Science*) on Billboard 200 data.

**Files produced:** `01_scrape_billboard.py` (a Billboard scraper, tested offline only). It is now **superseded** by the Kaggle data below and is optional.

---

## 2. README rewrites

The README went through three versions:
1. A technical version with a build plan for a coding agent.
2. A plain-language version at the user's request (no data-source specifics).
3. The current version, which adds the data now in hand, preliminary results and revised steps.

---

## 3. Kaggle Billboard charts (`ludmin/billboard`)

**Files:** `billboard200.csv`, `hot100.csv`, `streaming.csv`, `digital.csv`, `radio.csv`.

| File | Contents | Coverage |
|---|---|---|
| billboard200.csv | Top 200 albums weekly | 1963 – Sept 2026 |
| hot100.csv | Top 100 songs weekly | 1958 – Sept 2026 |
| streaming.csv | Top 50 streaming songs weekly | Jan 2013 – Sept 2026 |
| digital.csv | Top 50 download-sales songs weekly | 2004 – Sept 2026 |
| radio.csv | Top 50 radio songs weekly | 1990 – Sept 2026 |

Columns (all files): `Date, Song, Artist, Rank, Last Week, Peak Position, Weeks in Charts, Image URL`.

**Quirks found:**
- Dates are stored as the **Wednesday** three days before Billboard's official Saturday date. The first chart under the new rule (Dec 13, 2014) appears as **2014-12-10**.
- On the album chart, the **album title is in the `Song` column**.
- 2010–2024: all 782 weeks present, exactly 200 rows each.
- Reading with pandas: use `dtype=str, low_memory=False` (a `usecols` read crashed on mixed types).
- A new album debut = `Weeks in Charts == 1` (first-ever week, so re-entries are excluded).

**Script:** `kaggle_analysis.py`. **Results:** `kaggle_results/A_*` to `E_*`, `D2_*`.

**What was done and found:**

- **A. Chart dynamics.** New albums entering the Billboard 200 per year fell from 1,253 (2014) to 393 (2024). Streaming keeps old albums on the chart.
- **B. Album bombs.** For each top-10 album debut, count the artist's songs debuting on each song chart the same week (matched on lead artist, i.e. the name before "featuring", "&", "and", "x", "with"). Hot 100: 0.1–0.3 (2010–14) → 3.4 (2021–24). Streaming chart: 0.04 (2014) → 2.4 (2024). Sales chart: 0.08 → 0.8. Radio chart: about 0 throughout (placebo). Top-10 albums with 5+ simultaneous Hot 100 debuts: about 1% → over 20%.
- **C. Filler signal.** Of same-week Hot 100 album-song debuts, the share lasting only one week: about 25–35% (2012–14) → 50–68% (2018–21) → about 46–49% (2022–24). The pre-rule baseline is noisy (2010 about 50% on few songs).
- **D. Artist streaming exposure.** Each artist's share of 2013-01 to 2014-11 song-chart weeks that were on the streaming chart rather than the sales chart (artists with 5+ weeks; about 205 artists). The exposure × post-rule effect on log(1 + Hot 100 bombs), with artist and year fixed effects, was +0.097 (p = 0.016). But the event study showed the rise before 2014, a sign of overlap bias. After dropping 2013–14 albums (the years used to build the score), the effect was +0.119 (p ≈ 0.06, 97 artists). Borderline.
- **E. Chart payoff.** More simultaneous song debuts → longer Billboard 200 runs, but the relationship did not change after the rule (interaction −0.07, p = 0.49).

---

## 4. Spotify sample (2009–2025)

**Files:** `track_data_final.csv` (8,778 tracks, 5,317 albums) and `spotify_data_clean.csv` (8,582 tracks — **all** also in the final file). Columns include `album_total_tracks`, `album_type`, `album_release_date`, `artist_genres`, `track_popularity`, `track_number`, `artist_popularity`, `artist_followers`, and duration. The two files store genres in different formats (Python list strings vs. comma-separated), so genres were combined from both.

**Script:** `spotify_analysis.py` (base), then `spotify_part2.py` to `spotify_part5.py`. **Results:** `kaggle_results/S*`.

**Building the album sample:**
- One row per album; keep `album_type == "album"`, 6+ songs, release years 2009–2024.
- Drop album names containing: deluxe, expanded, edition, version, anniversary, remaster, live, greatest, best of, collection, hits, complete, reissue, bonus, extended. This leaves 1,505 studio albums.
- **Genre groups** come from artist genre tags via keyword rules, applied in this priority order: Latin, hip-hop/R&B, country, Christian, jazz, soundtrack (dropped), classical, electronic, rock, pop. This gives 699 albums with a genre. Nielsen 2014 intensity is attached to each group.
- "High" streaming genres = intensity ≥ 1.9 (hip-hop/R&B, pop, Latin, electronic).
- Post-rule = release date on or after 2014-11-24.
- Matched to Billboard 200 debuts on normalized lead artist + album title: **499 of 699** matched.

**Results:**

| Sample / spec | Effect on log(songs) | p |
|---|---|---|
| All 699, continuous intensity × post (genre + year fixed effects) | −0.006 | 0.82 |
| All 699, high × post | +0.045 | 0.40 |
| All 699, high × post, only hip-hop vs rock + country | +0.098 | 0.13 |
| **499 Billboard 200 albums, high × post** | **+0.123** | **0.015** |
| 499 Billboard, continuous intensity | +0.057 | 0.037 |
| 499 Billboard, continuous, no electronic | +0.081 | 0.029 |
| 499 Billboard, 2010–2019 only | +0.141 | 0.009 |
| 499 Billboard, >12 songs (share) | +0.202 | 0.036 |
| 499 Billboard, 18+ songs (share) | +0.142 | 0.022 |
| 499 Billboard, bootstrap with genre groups | — | 0.064 |
| 499 Billboard, artist fixed effects (same artist before/after) | +0.072 | 0.42 |
| 200 non-charting albums, high × post | −0.032 | (ns) |
| 249 albums with Kaggle artist-exposure score | +0.017 | 0.58 |

Standard errors are clustered by artist unless noted. The genre-group wild bootstrap uses Webb weights with 499 draws.

**Raw means, Billboard 200 sample:**

| | Other genres | Streaming-heavy genres |
|---|---|---|
| Avg. songs, before → after | 13.8 → 13.2 | 13.2 → 15.2 |
| Share with more than 12 songs | 49% → 50% | 48% → 72% |
| Share with 18+ songs | 10% → 5% | 8% → 27% |

By three-year periods, streaming-heavy albums with more than 12 songs: 50% (2009–11), 49% (2012–14), 67% (2015–17), 76% (2018–20), 70% (2021–24). Other genres: 50, 48, 45, 50, 61.

**Event study (Billboard sample, high group, reference year 2014).** Pre-period coefficients are near zero (joint test p = 0.89). Post-period coefficients: 2016 +0.16, 2017 +0.12, 2018 +0.26, 2020 +0.12, 2021 +0.19, 2022 +0.19, with 2019 and 2023–24 negative. The pattern is noisy but builds after 2015.

**Dilution (Spotify popularity):** inconclusive. Later track position predicts lower popularity (−4.4, p = 0.006), but the before/after × genre interactions do not follow the predicted pattern. The sampled tracks are likely not random within albums, and popularity is measured today.

**Main open problem — selection:** the effect appears only among albums that charted. Either the rule changed production for albums aiming at the chart, or long streaming-heavy albums simply became more likely to chart after the rule. Resolving this needs standard-edition song counts for all notable releases, charting or not.

**Honesty note:** the first pre-planned test (all albums, continuous intensity) was null. The Billboard-subsample result was found afterwards. Before the write-up, fix one main specification in advance.

---

## 5. Known issues in the code

- **Folder layout (paths fixed):** scripts live in `InitialAnalysisCode/`, raw data in `OriginalDataFiles/`, and all outputs go to `kaggle_results/`, all inside the project folder `Billboard200Paper/`. Paths are worked out from each script's own location, so the scripts run from any folder.
- **Scripts chain via `exec()`:** `spotify_part2.py` runs part of `spotify_analysis.py`; `part3` runs `part2`; `part4` and `part5` run `part3`. All must stay together in `InitialAnalysisCode/`. **Recommended first task for the agent:** merge them into one clean script with functions, keeping the same outputs.
- **Run order:** `kaggle_analysis.py` first (it creates `kaggle_results/D_artist_exposure.csv`, which `spotify_part2.py` reads), then `spotify_analysis.py`, then parts 2–5.
- **Name matching** (lead artist + album title) is simple normalization. Nothing was hand-checked, so the match accuracy is unknown.
- **Genre rules** are keyword-based and unchecked. Christian (3) and jazz (2) have almost no albums, so the "other" group is effectively rock + country (+ a little classical).
- **Deluxe detection** relies on album-name keywords only. Spotify may list a deluxe tracklist under the original name.
- **Required packages:** pandas, numpy, statsmodels (plus billboard.py, requests and beautifulsoup4 only for the optional scraper).

---

## 6. Next steps (from README)

1. Build the full album list: all notable studio albums 2009–2024, charting or not, with standard-edition song count, running time, genre and label.
2. Check song counts against original standard editions.
3. Rerun the main comparison on the full list, and separately test whether long albums became more likely to chart.
4. Year-by-year pre-trend check on the full list.
5. Watered-down songs via song charts (radio as placebo); chart payoff.
6. Stress tests; UK 12-song comparison; fix the main specification before writing.

---

## 7. Phase 1 reproduction and clean pipeline (2026-09-27)

**Original-script reproduction:** Ran `kaggle_analysis.py`, `spotify_analysis.py`, then `spotify_part2.py` through `spotify_part5.py` in the documented order. Original code and `OriginalDataFiles/` were left unchanged. To preserve the archived `kaggle_results/`, outputs from this run were redirected to `results/phase1_original/`.

- The chart-side files reproduce the logged results, including 1,253 new Billboard 200 debuts in 2014 and 393 in 2024; the artist-exposure interaction is +0.097 (p = 0.016), and the chart-payoff interaction is -0.069 (p = 0.494).
- The Spotify build reproduces 1,505 core albums, 699 with usable genres, and 499 genre-coded Billboard 200 matches. The headline Billboard-only estimate is +0.123 on log songs (SE = 0.050, p = 0.015). The all-genre-coded estimate is +0.045 (p = 0.402), and the non-charting estimate is -0.032 (not significant).
- The Billboard-sample event study's joint pre-trend test is p = 0.893; the genre-cluster bootstrap p-value is 0.064. The artist-exposure variant is +0.017 (p = 0.582).
- The original Spotify scripts do not run unmodified against the current raw folder: they request `spotify_data_clean.csv`, but the existing file is `spotify_data clean.csv`; additionally, `str.contains()` can return missing values that make unary `~` fail. The reproduction used temporary in-memory compatibility handling for the filename and null filter; no raw or first-round source files were changed. The clean pipeline reads the actual filename and uses `na=False` in the reissue filter.
- The initial chart lead-artist matcher uses additional separators (`feat.`, `ft.`, and `/`) beyond the Spotify album-match rule. The clean code keeps these normalizers distinct; this restores the logged 205-artist exposure sample and the +0.017 estimate.

**Clean pipeline:** Added `code/load_clean_data.py`, `code/build_album_sample.py`, and `code/analyze_albums.py`. They use functions and project-relative paths, do not chain via `exec()`, and write the one-row-per-album dataset to `data/spotify_album_sample.csv` and analysis tables to `results/phase1_clean/`.

- Clean results match the headline, pre-trend, bootstrap, exposure, and reported robustness estimates to the logged precision.
- Statsmodels emitted rank-deficiency warnings for the genre-trend and track-popularity specifications, consistent with the original specifications; those results were not changed or suppressed.
- The available working Python runtime was Python 3.10 with pandas, numpy, and statsmodels; statsmodels was installed there after the selected Python 3.12/MSYS interpreter proved to lack pandas and pip.

**Phase status at the time:** Phase 1 was complete for review. Phase 2 had not started, and no large collection or scraping had begun.

---

## 8. Phase 2 analysis plan (2026-09-27)

Created `analysis_plan.md` before any new album collection or analysis. The headline is fixed as the streaming-heavy-genre-by-post-rule interaction in an unweighted model of log standard-edition song counts, with individual genre-category and release-year fixed effects and standard errors clustered by artist.

- Streaming-heavy genres are hip-hop/R&B, pop, Latin, and electronic, using the prespecified 2014 stream-share-to-album-sales-share threshold of 1.9; the comparison genres are rock, country, Christian, jazz, and classical.
- Post-rule means release on or after 2014-11-24, the start of the tracking week for the Billboard issue dated Dec 13, 2014 (stored as Dec 10 in Kaggle).
- The main target is the full eligible 2009-2024 notable studio-album list, charted or not, with standard-edition song counts; chart-only results, the chart-selection model, event study, alternate outcomes, and robustness checks are secondary.
- The album-discovery source and operational definition of "notable" remain to be fixed and documented before Phase 3 collection. Billboard debut status will not be used to define the album universe.

**Phase status:** Phase 2 plan is drafted and awaiting user review. Phase 3 has not started; no large download or scraping has occurred.

---

## 9. Phase 2 revisions requested (2026-09-27)

Revised `analysis_plan.md` in response to the user's requested design changes. No album collection or regression was started.

- Primary artist roster: at least one Billboard 200 album debut from 2009-01-01 through 2014-11-23; include the roster artists' studio albums whether charting or not. Post-release popularity, streaming counts, Wikipedia presence, and similar success measures are prohibited for universe inclusion. A broader major-label list is secondary.
- Headline window: releases 2009-2019; 2009-2024 is secondary and explicitly notes the 2018 paid/free weighting and 2020 video/bundle rule changes.
- Outcome edition: earliest official release; for same-day standard/deluxe releases, use fewer tracks. Count intros, skits, interludes, and all other tracks. Running time is secondary.
- Genre auditing: before regression, hand-check a reproducible random sample of 100 primary-list albums, fix only clear classification errors, and record seed, error rate, each change, and ambiguous cases here.
- Headline inference: restricted wild cluster bootstrap at nine genre categories, Webb six-point weights, 9,999 draws and a documented fixed seed; report artist-clustered SE and conventional p-value as well.
- Artist fixed effects are included as a robustness check due to the artist-based universe.

**User decision (2026-09-27):** retain all studio albums by roster artists released in the analysis window, including albums released before an artist's first qualifying debut. Roster inclusion uses only pre-rule Billboard 200 chart history; no post-rule information determines inclusion. The analysis plan now treats this as the approved primary universe rather than an unresolved issue.

- Added a sensitivity check dropping each artist's albums released on or before their first qualifying Billboard 200 debut.
- Added a control for ordinal studio-album order (since 2009, or from career start when available) to address artist aging/career stage; incomplete history will need to be reported.
- Marked `analysis_plan.md` approved and frozen on 2026-09-27. Primary analysis definition must not be changed after viewing Phase 3 results; deviations must be logged separately.

**Phase status:** Phase 2 approved and frozen. Phase 3 step 1 (constructing the pre-rule artist roster from Kaggle Billboard 200 data) is authorized. Do not collect full discographies until the user selects a proposed sourcing approach.

---

## 10. Phase 3 step 1: pre-rule artist roster and source options (2026-09-27)

Built the primary roster from the Kaggle Billboard 200 rows where `Weeks in Charts == 1` and stored chart date is 2009-01-01 through 2014-11-23, inclusive. The roster was determined only from this pre-rule chart history.

- The filter returns 6,603 qualifying debut rows and 3,366 distinct artist-credit strings after case/whitespace normalization.
- Excluding the non-artist credit `Various Artists` leaves 3,365 billed-credit strings. Those rows account for 368 chart debuts and are excluded from the artist roster because they do not identify a single artist; underlying compilation albums are not artist entries.
- Eleven distinct credits include an explicit `featuring`/`feat.`/`ft.` marker. The roster uses the billing before that marker as the artist candidate and does not add the featured guest solely from that credit. These produce 10 distinct lead candidates after deduplication against other credits.
- The resulting file has 3,361 provisional roster entities. There are 292 composite credits flagged for identity review. The flags include `&`, `and`, `x`, `with`, commas, or slashes; these are not automatically split because the syntax also occurs in established bands, duos, group names, and suffixes such as Jr. Two featured credits have composite lead billing and are flagged too.
- The 3,361 is a provisional count of normalized billed identities, not a fully reconciled count of unique human artists/bands. Alias spellings and the 292 composite credits remain unresolved; `data/pre_rule_artist_credit_audit.csv` preserves chart credits and examples for curation. The roster is in `data/pre_rule_artist_roster.csv`; it excludes `Various Artists` and retains unresolved composite credits as single provisional entries.
- Added `code/build_pre_rule_artist_roster.py` for reproducible construction. It reads only the Kaggle Billboard 200 data and wrote no files under `OriginalDataFiles/`. No discography queries, downloads, or scraping were performed.

**Discography-source choices proposed (awaiting user selection; no collection started):**

1. **MusicBrainz API.** It has structured artist/release/release-group data, official status, release dates, media, formats, and tracklists; the service is free for non-commercial use and requires no API key. Its policy permits no more than one request per second, and coverage/edition tagging is community-maintained, so standard-vs-deluxe adjudication and the flagged identities still need review. Rough effort: 3-5 working days for matching, throttled retrieval, normalization, and an initial quality pass; elapsed API time depends on pages/details per artist and could be several hours or more.
2. **Discogs API, or a local Discogs dump if approved.** Artist release pages and release records provide format, label, date, and tracklist data, and the monthly database dump is documented as CC0. The API documents 25 unauthenticated or 60 authenticated requests per minute; API terms apply, and the full dump is a large download and requires local database processing. Coverage includes many reissues and duplicate pressings, so choosing the earliest official standard edition will require substantial deduplication. Rough effort: 4-7 working days with the API; a dump-based workflow adds setup/storage time and should be approved before downloading.
3. **Hybrid catalog plus primary-source adjudication.** Use a structured catalog (MusicBrainz or Discogs) to discover candidate albums, then resolve edition/date/count against official artist or label pages, digital storefront product pages, and, where needed, release booklets. This best supports the exact earliest-standard-edition rule and leaves an auditable source URL per album, but historical pages may disappear and manual checks are labor-intensive across 3,361 provisional entities. Rough effort: about 1-3 weeks for an initial automated catalog plus focused manual resolution; complete manual coverage may take longer.

Source documentation checked: MusicBrainz API and database download documentation; Discogs API developer documentation. No method has been selected and no large or paid step has been undertaken.

**Phase status:** Phase 3 step 1 is complete for review. Waiting for the user's source choice before collecting any studio discographies.

---

## 11. MusicBrainz source decision and pre-collection clarifications (2026-09-27)

The user selected MusicBrainz Web Service API as the single primary source for roster discographies. Discogs and manual primary-source checks are authorized only for flagged cases and quality checks; they may not fill albums absent from MusicBrainz. The source choice does not change the frozen headline specification.

Added dated implementation clarifications to `analysis_plan.md`:

- Studio album eligibility is MusicBrainz release group primary type `Album`, no secondary types, and an `Official` release. `Mixtape/Street` is excluded from the headline and retained for a separate robustness check.
- Standard edition means earliest-dated worldwide official release; ties go to fewer tracks. Count tracks summed across all discs/media. Store artist, release-group, and release IDs and source URL for every album.
- Flag year-only dates; exclude 2014 year-only releases from the headline and report the number. Keep other year-only dates flagged without inventing precision.
- Artist-ID matching is the only current collection step. Stop with a match-rate report and ambiguity file (including same-name and composite-credit entries) for user review. Do not retrieve release groups, releases, or track counts until that review is complete.
- Later API retrieval must stay at or below one request per second, send a descriptive User-Agent, and cache raw responses. Coverage audit and pre-resolution flags are required after retrieval is authorized.

**Phase status:** Authorized to perform artist-ID matching only. One cached smoke-test search was run to validate the artist endpoint; full roster matching is now underway. Discography collection remains gated on the user's review of the match output.

---

## 12. MusicBrainz artist-ID matching (2026-09-27, in progress)

Added `code/match_musicbrainz_artists.py`. It queries only MusicBrainz's artist search endpoint, sends a descriptive User-Agent, serializes requests to no more than one per second, and appends each raw JSON response to `data/musicbrainz_artist_search_cache.jsonl` for resumability. It does not call release-group or release endpoints.

- The one-entry smoke test validated a live search for `!MAYDAY!`; MusicBrainz returns canonical `¡MAYDAY!` with `MAYDAY!` as an alias. The matcher now permits a punctuation-normalized fallback only when there is exactly one score-100 candidate; less certain or composite records remain for review.
- Offline matcher checks passed for a unique exact name, multiple exact same-name candidates, a composite credit with an exact candidate, and a fuzzy-only candidate. Match IDs are written only under the documented unique-match conditions.
- The first attempt under the MSYS Python interpreter failed TLS certificate verification before a request was sent. Retried successfully under Python 3.10 with certificate validation enabled; no TLS checks were disabled.
- Full roster search has been started and will take about 56 minutes at the required rate. Its final matched/review counts and outcomes will be logged after completion. No discography information has been requested.

### Completion update

Completed the full artist-only pass and regenerated output tables from the cached responses. All 3,361 roster entries have one cached MusicBrainz artist search response; no release-group or release endpoints were called.

- **Conservative resolved match rate:** 2,260 / 3,361 roster rows = 67.2%. These are unique exact canonical-name, exact-alias, or unique punctuation-normalized score-100 candidates, after duplicate-ID roster rows are removed to review.
- Before duplicate-ID reconciliation, 2,266 rows (67.4%) had a unique candidate under those criteria. Six rows form three duplicate-ID pairs: `Keb Mo` / `Keb' Mo'`, `Doobie Brothers` / `The Doobie Brothers`, and `Robert Cray Band` / `The Robert Cray Band`. These six rows are retained with IDs but marked for review; together they refer to three MusicBrainz entities.
- The review file has 1,101 rows: 666 same-name ambiguities; 291 composite roster entities; 130 with no exact name/alias or unique score-100 punctuation match; 8 truncated candidate searches; and 6 duplicate roster spellings sharing an ID.
- The earlier figure of 292 is the number of distinct flagged source-credit strings. These collapse to 291 roster entities because `Mormon Tabernacle Choir/Orchestra At Temple Square` has two flagged billing variants that normalize to one roster key.
- The search cache contains raw responses for the entire roster. The review CSV includes candidate IDs, candidate display names, scores, disambiguation text, type, area, and sample aliases so unresolved identities can be assessed before discography lookup.
- The initial smoke test and later cached table regeneration did not duplicate API calls. API traffic remained serial at one request per second, with TLS verification enabled.

**Phase status:** artist-ID matching is complete and awaiting user review of `data/musicbrainz_artist_matches_review.csv` and `data/musicbrainz_artist_matches.csv`. Do not collect release groups, releases, media, or track counts until the user approves the identity matches.

---

## 13. MusicBrainz zero-result and composite-credit audit (2026-09-27)

Investigated the user's 92-row `true_nomatch_zero.csv` and four suspected partial composite credits before any hand-checking or discography retrieval.

- All 92 original cache entries contain valid MusicBrainz JSON responses with `count: 0` and empty `artists` arrays. None were missing from cache. The original matcher only cached a response after successful HTTP and JSON parsing; HTTP 429/5xx/transport errors raised and retried or stopped the run, rather than being converted to a zero-count response. The original cache did not record HTTP status/error history, so there is no historical error ledger; the cached valid response envelopes are evidence these 92 attempts were successful zero-result responses.
- Root cause: the original query was fielded as `artist:"<name>"`, which required the canonical artist field and omitted alias search. It also used the default Lucene query parser rather than MusicBrainz's documented `dismax=true` literal mode, so search syntax characters were not protected as intended. MusicBrainz's API search documentation states the unfielded artist query searches aliases, artist names and sort names; `dismax=true` escapes special query syntax characters.
- Tested the corrected unfielded quoted query with `dismax=true` on `The Ramones`, `A$AP Ferg`, `(hed) p.e.`, and `Ke$ha` using the API. The first three yielded candidates; output from the `(hed) p.e.` probe could not print its non-ASCII candidate under the Windows console encoding, but the API response itself returned count 1. No TLS verification was disabled.
- Re-queried all 92 names serially at one request per second and cached each successful raw response. 47 now return one or more candidates; 45 still return none. Of the 20 names containing one of `$`, `+`, parentheses, colon, or period, 8 returned candidates; among the other 72, 39 returned candidates. The query fix improves coverage but demonstrates zero-result recovery is not limited to those punctuation characters.
- Updated `true_nomatch_zero.csv` with the original/retry counts, actual retry query, candidate names, special-character indicator, retry result, and `api_error_recorded=False` for every row. The Ramones now matches MusicBrainz ID `d6ed7887-a401-47a8-893c-34b967444d26` by the exact `The Ramones` alias.
- Created `flagged_composite_partial.csv` for the four user-identified joint billing cases: Frank Sinatra/Dean Martin/Sammy Davis Jr. (top candidate The Rat Pack), Dharoha Project/Laura Marling/Mumford & Sons (Mumford & Sons), JP/Chrissie/The Fairground Boys (The Fairground Boys), and Lil Boosie/Webbie/Lil Trill/Trill Fam (Lil Trill). All four rows have a blank `musicbrainz_artist_id`; candidate IDs are included only as review context. They remain multi-artist credits and are not assigned to a single act.
- Added `code/retry_musicbrainz_zero_matches.py` and `code/audit_musicbrainz_search_exceptions.py`. The main artist matcher now uses literal alias-aware dismax artist search and logs request errors/retries in `data/musicbrainz_artist_search_errors.jsonl`; none occurred during this 92-name retry.
- Rebuilt the match and review tables from the updated cache. Current statuses: 2,285 unique exact/alias/score-100 rows before reconciliation, 27 rows with IDs shared by multiple roster spellings held for review, 666 same-name ambiguities, 291 composite entities, 84 still with no qualifying match, 8 truncated searches. Overall review file: 1,076 rows. These counts supersede the earlier match totals.

**Phase status:** the 92 zero-result retry and the four partial-composite flags are complete. Artist-ID resolution still awaits user review. No release groups, releases, media, or track counts have been requested.

---

## 14. Composite alias assignment and expanded zero-credit search (2026-09-27)

- Rechecked full billed credits against both MusicBrainz canonical names and aliases. `Frank Sinatra, Dean Martin & Sammy Davis Jr` has an exact full-credit alias on `The Rat Pack`; updated `flagged_composite_partial.csv` with MBID `35e227e5-f724-4699-91b2-d5184cdc7411`, `match_status=matched_full_credit_alias`, and `match_basis=exact_alias`. The other three flagged credits have no exact canonical-name or alias match to the full billing and remain unassigned.
- `code/audit_musicbrainz_search_exceptions.py` now uses a reusable normalized full-credit canonical-name/alias check, so future composite cases are not limited to canonical names.
- Expanded the zero-credit splitter to include `presents`, `+`, `aka`/`a.k.a.`, and `of` in addition to the prior separators. Ran the component pipeline on all 45 entries whose literal alias-aware retry still returned zero. Searches stayed serial and throttled at one request per second; component responses are cached in `data/musicbrainz_zero_component_searches.jsonl`.
- **Component results:** 13/45 component passes returned at least one search candidate; 12/45 had an exact canonical-name/alias hit on one or more components. These are component identities only, not automatic full-credit roster matches. One additional credit returned candidates without an exact component hit. The summary is in `data/musicbrainz_zero_component_summary.csv`, with per-component evidence in `data/musicbrainz_zero_component_results.csv`.
- Performed one targeted core-name search for each requested identity. Kenny Wayne Shepherd returned person MBID `c5f42b91-82b9-466c-891c-a9cc391b50bc`; Dead Rabbitts returned group MBID `ebafff3d-0105-4e5d-a7a4-98972c48a57f`; Nick Hexum returned person MBID `dd28acec-0a35-4a7d-a1a2-b506dbfb19f2` and also a `Nick Hexum Quintet` group candidate (MBID `23af1753-e926-4338-aef6-7cfe2861d1d8`, score 84); CAJO returned no clear artist/group matching `The CAJO Family` (top results included CAJO Productions and unrelated CAJO-like names). Full billed names did not exactly match canonical artist names or aliases in these targeted results. Details are in `data/musicbrainz_targeted_artist_searches.csv`.
- Created `data/musicbrainz_confirmed_not_found.csv`: four generic Broadway cast-recording billing labels returned no full-entity or component candidates; `Smokie Norful Presents: Victory Cathedral Choir` returned no single full-credit entity, although searches identified Smokie Norful and Victory Cathedral Choir separately. These are not treated as one MusicBrainz artist.
- The four explicitly partial composites remain: one is now matched to an exact full-credit alias (The Rat Pack); three remain unassigned. No release groups, releases, media, or track counts have been requested.

**Phase status:** the zero-result and composite-identity follow-ups are logged. User review of the artist-ID mapping is still required before discography collection begins.

---

## 15. Efficient identity resolution and conditional collection gate (2026-09-27)

### Four targeted identities

- **The Kenny Wayne Shepherd Band:** Billboard chart rows use the full band credit (including `Live! In Chicago`, `How I Go`, and `Goin' Home`). MusicBrainz exact searches returned only the solo Person entity `Kenny Wayne Shepherd` (MBID `c5f42b91-82b9-466c-891c-a9cc391b50bc`), whose aliases include the text `Kenny Wayne Shepherd Band`; no separate Group entity was returned. Per the user's instruction not to substitute a person for a billed band, leave this roster row unresolved.
- **The Dead Rabbitts:** Billboard bills `The Dead Rabbitts`; MusicBrainz returns the Group `Dead Rabbitts` (MBID `ebafff3d-0105-4e5d-a7a4-98972c48a57f`). Use this Group; the only difference is the leading article.
- **The Nick Hexum Quintet:** Billboard bills `The Nick Hexum Quintet`; MusicBrainz has a separate Group `Nick Hexum Quintet` (MBID `23af1753-e926-4338-aef6-7cfe2861d1d8`, search score 100 on the exact group query) and solo Person `Nick Hexum` (MBID `dd28acec-0a35-4a7d-a1a2-b506dbfb19f2`). Use the Group for the Quintet billing.
- **The CAJO Family:** full-credit and `CAJO` searches did not identify a matching artist/group; results were unrelated. Leave unresolved.

The decisions are in `data/musicbrainz_targeted_identity_decisions.csv` and applied to the main match table. The Rat Pack's exact full-credit alias is also applied in both identity outputs.

### Ambiguity pass and coverage balance

Applied a conservative rule pass to the 666 `ambiguous_same_name` rows using full cached candidates, not just the top-ten review summary. It refuses truncated result sets. Rules were: a unique exact candidate in the US versus alternatives explicitly identified as foreign; or one US Group candidate versus exact-name Person candidates; no broad fuzzy candidate is auto-selected. Genre evidence is recorded but was not needed for an auto decision in this pass.

- Auto-resolved: **79/666** (59 unique-US vs explicit-foreign; 20 unique-US Group vs Person candidates).
- Still human review: **587/666**.
- Only 41 of the 666 ambiguous names matched an artist with a usable genre in the Spotify sample. Across the full 3,361 roster, 146 (4.3%) had an exact normalized-name genre assignment, so the genre split has limited coverage.
- Among genre-known roster artists, unresolved: streaming-heavy **26/78 = 33.3%**; other genres **16/68 = 23.5%**. The 9.8 percentage-point difference is uncertain (approximate 95% interval for the difference: -4.7 to +24.3 points); it is not evidence of a precise imbalance, but the higher heavy-genre rate and low coverage are flagged.
- The first qualifying Billboard debut date cannot be split pre/post rule: the frozen roster definition restricts all 3,361 artists to pre-rule qualifying debuts. A requested post-rule group at this artist-level definition is structurally empty.
- As a separate descriptive proxy, among 9,531 Billboard album-debut rows matched back to roster credits, unresolved rows are **1,650/6,273 = 26.3%** before the rule and **793/3,258 = 24.3%** after. This is album-debut-weighted, not an artist-level first-debut split, and repeated artists mean the observations are not independent.

### Current identity state and next-step decision

After the 79-rule pass and explicit decisions, **2,367/3,361** roster rows have resolved, unique IDs; **994** remain for review, including 587 same-name ambiguities. All duplicate-ID rows are blanked and held for review. The remaining review is lower priority under the user's direction to begin with resolved artists. The descriptive pre/post charting-album rates are close; the genre split's uncertainty is broad but its coverage is small. Therefore proceed only with release metadata for the 2,367 uniquely resolved artist IDs, preserving the 994 unresolved entries out of the fetch list. Continue to log coverage and do not use partial/composite candidates as artist IDs.

**Phase status:** identity balance and caveats recorded before retrieval. Release-group collection may proceed for uniquely resolved IDs only; unresolved artist rows remain excluded until reviewed. Use the approved MusicBrainz rate limit, User-Agent, and raw-response cache. No Discogs or manual source may fill absent MusicBrainz albums.

### Resolved-only collection started

Added `code/collect_musicbrainz_discographies.py` and successfully smoke-tested one resolved artist. The test retrieved 14 release groups, 10 eligible headline/mixtape groups within or without a date, and 19 official release editions; the output correctly flagged two same-day different-length groups. It included release artist credits, labels, media track totals, recording durations, and source IDs/URLs.

The full resolved-artist release-group index is now being collected serially for 2,367 unique resolved IDs, with raw page responses cached in `data/musicbrainz_release_group_cache.jsonl`. Estimate is approximately 41 minutes at the API limit. The release-edition stage will be sized from the resulting eligible group count before proceeding; no unresolved roster IDs are included.

### Collection completion update (2026-09-28)

The resolved-only MusicBrainz collection completed successfully. It produced:

- 72,091 release groups from the 2,367 uniquely resolved artist IDs.
- 40,469 official release editions with media metadata, labels, artist credits, track counts, and available recording durations.
- 10,913 standard-edition album candidates after selecting the earliest official worldwide release within each release group, breaking same-date ties by fewer tracks.
- 8,431 candidates in the 2009-2019 headline window and 10,912 in the 2009-2024 secondary window.
- 198 2014 year-only dates flagged for headline exclusion.
- 1,611 same-day different-length edition cases flagged before resolution.
- Running time available for 10,785 of 10,913 candidates; track counts and release dates are present for all candidates.
- 740 Mixtape/Street candidates retained for the separate robustness sample.

Raw API responses are cached in `data/musicbrainz_release_group_cache.jsonl` and `data/musicbrainz_official_release_cache.jsonl`. Processed tables are `data/musicbrainz_release_groups.csv`, `data/musicbrainz_official_releases.csv`, and `data/musicbrainz_standard_album_candidates.csv`. No unresolved artist IDs were included, and no raw files were modified.

**Next phase:** validate charting-album coverage by genre and pre/post period, compare MusicBrainz counts with the Spotify sample, inspect the 1,611 edition flags and 198 year-only exclusions, then hand-check the prespecified random 100-album genre audit before running any regression.

---

## 17. Pre-regression validation completed (2026-09-28)

### MusicBrainz tag balance

Used cached MusicBrainz artist tags and disambiguation text for the full roster, not only the Spotify overlap. A conservative genre group was assigned only where the tags supported one group; conflicting or absent evidence was left unknown.

- MusicBrainz tags were available for 2,047 of 2,367 resolved artist IDs (86.5%).
- Across all 3,361 roster rows, conservative groups were: streaming-heavy 735, other 1,716, unknown 910.
- Unresolved identity rates: streaming-heavy 129/735 = 17.6%; other 288/1,716 = 16.8%; unknown 577/910 = 63.4%.

### Spotify/MusicBrainz track-count mismatch validation

The 305 exact artist/album joins in `data/musicbrainz_spotify_count_comparison.csv` were merged back to the standard-edition candidate table and split at the frozen 2014-11-24 threshold. A mismatch is defined as an absolute count difference of at least three tracks.

| Period | Matched albums | Mismatches | Rate | Spotify higher | MusicBrainz higher |
|---|---:|---:|---:|---:|---:|
| Pre-rule | 173 | 26 | 15.0% | 16 | 10 |
| Post-rule | 132 | 11 | 8.3% | 4 | 7 |
| Overall | 305 | 37 | 12.1% | 20 | 17 |

The mismatch rate is lower after the rule, so the large differences are not concentrated among post-2014 albums. The earlier genre-period count table is also not a denominator-free result: among hip-hop/R&B comparisons, mismatches were 11 pre and 8 post; among pop comparisons, 13 pre and 3 post. These raw counts do not indicate a post-rule streaming-heavy data problem.

Eight mismatches were independently checked against accessible album track listings or release descriptions:

| Album | MusicBrainz | Spotify | Independent source | Adjudication |
|---|---:|---:|---|---|
| Pink Friday 2 | 10 | 22 | https://en.wikipedia.org/wiki/Pink_Friday_2: standard physical edition has 10; standard digital/streaming release has 22 | Edition-definition ambiguity; Spotify matches the standard digital release, while MusicBrainz matches the physical standard |
| The Pale Emperor | 10 | 13 | https://en.wikipedia.org/wiki/The_Pale_Emperor: standard edition has 10; deluxe adds 3 acoustic tracks | MusicBrainz matches standard |
| Justice | 27 | 16 | https://en.wikipedia.org/wiki/Justice_(Justin_Bieber_album): standard edition has 16; deluxe/complete editions add tracks | Spotify matches standard; MusicBrainz appears to combine a later expanded edition |
| Nothing but the Beat | 22 | 13 | https://en.wikipedia.org/wiki/Nothing_but_the_Beat: original release is a double album with two 12-track discs; later editions differ | Edition-definition ambiguity; neither count alone is a clean standard double-disc count |
| Indie Cindy | 13 | 25 | https://en.wikipedia.org/wiki/Indie_Cindy: standard album has 12; deluxe/live material expands the release | MusicBrainz is closer but still includes one non-standard/bonus track |
| Moon Landing | 11 | 18 | https://en.wikipedia.org/wiki/Moon_Landing_(album): standard 11, deluxe 14, Apollo Edition 19 | MusicBrainz matches standard |
| Hard to Imagine the Neighbourhood Ever Changing | 12 | 21 | https://en.wikipedia.org/wiki/The_Neighbourhood_(album): original album has 12; expanded release combines EP material | MusicBrainz matches the original album; Spotify reflects the expanded compilation |
| My Everything | 12 | 15 | https://en.wikipedia.org/wiki/My_Everything_(Ariana_Grande_album): standard edition has 12; deluxe adds tracks 13–15 | MusicBrainz matches standard |

The independent checks therefore support using the MusicBrainz standard-edition count for the frozen outcome, with explicit caveats for multi-disc albums and albums whose digital and physical standard releases differ. Spotify is useful as a comparison source but commonly represents the currently available deluxe/expanded streaming version. No track counts were changed based on these checks, and no regression was run in this step.

**Validation decision:** the mismatch pattern does not justify excluding post-rule albums or replacing the MusicBrainz outcome. Retain the frozen MusicBrainz standard-edition counts, preserve the mismatch table and edition flags as audit evidence, and carry the edition-definition limitation into the regression interpretation.
- Among unresolved rows directly: hip-hop/R&B 73, electronic 40, pop 9, Latin 7, rock 241, country 21, Christian 15, jazz 8, classical 3, unknown 577. The unresolved set is not disproportionately hip-hop/rap.
- Outputs: `data/musicbrainz_genre_balance.csv` and `data/musicbrainz_unresolved_genre_breakdown.csv`.

### Edition hand-check

Created a seeded 30-row sample from the 1,611 same-day different-length flags using seed 20260928. Each was compared with every cached official MusicBrainz release edition in its group: selected date had to equal the earliest official date and selected track count the minimum among same-day editions.

- 30/30 passed; observed error rate **0%** against cached official MusicBrainz API records.
- Browser-facing release pages were blocked by a JavaScript verification screen in this environment, so the audit used cached official API records as the documented fallback; this limitation is recorded in every sample row.
- Output: `data/musicbrainz_edition_handcheck_sample.csv`; adjudicator: `code/adjudicate_edition_handcheck.py`.

### Billboard and Spotify validation

- Billboard coverage among genre-classified charting debut rows: streaming-heavy 308/412 = 74.8% pre-rule and 149/183 = 81.4% post-rule; other genres 883/1,094 = 80.7% pre-rule and 453/526 = 86.1% post-rule. Unknown-genre coverage was 62.6% in both periods.
- MusicBrainz-to-Spotify standard-count comparison matched 305 albums. 37 differed by at least three tracks (12.1%), flagged for likely edition/version or matching review.
- Outputs: `data/musicbrainz_billboard_coverage.csv` and `data/musicbrainz_spotify_count_comparison.csv`; validator: `code/validate_album_collection.py`.

### Genre hand-check

Prepared a reproducible 100-album sample with seed 20260928. Ninety rows followed the frozen tag rules. Ten edge cases received explicit manual classifications from artist credit/disambiguation: six other-group assignments (`On Fire`, `Right Now God`, `Best Intentions`, `French Impressions`, `Wild and Free`, `Blood, Wood & Steel`) and four streaming-heavy assignments (`Fire`, `How to Be a Lady, Volume 1`, `Level Up`, `Rollin’ Stone`). No clear errors were found; observed clear-error rate **0/100 = 0%**. Every override and rationale is in `data/genre_handcheck_sample_100.csv`; preparation script: `code/prepare_genre_handcheck.py`.

This audit uses MusicBrainz metadata and artist-credit/disambiguation review; it is not a claim that all genre labels are independently authoritative.

**Phase status:** validation outputs and the resolved-only first-pass headline analysis are complete. Remaining risks are unresolved artist coverage (994 review rows), the 305-album Spotify comparison sample, and the digital-edition limitation documented below.

## 18. Subgenre resolution rates and digital-edition robustness (2026-09-28)

### Streaming-heavy subgenre unresolved rates

The previous combined streaming-heavy rate concealed meaningful subgenre differences. Using the repository validator's definition of unresolved (`UNRESOLVED` status or no MusicBrainz artist ID), with resolved plus unresolved artists assigned to each individual subgenre as the denominator:

| Subgenre | Artists | Unresolved | Unresolved rate |
|---|---:|---:|---:|
| Hip-hop/R&B | 243 | 54 | 22.2% |
| Pop | 639 | 86 | 13.5% |
| Latin | 69 | 8 | 11.6% |
| Electronic | 73 | 15 | 20.5% |

The reproducible table is `data/musicbrainz_subgenre_balance.csv`; the validator is `code/validate_musicbrainz_collection.py`. These rates supersede the earlier count-only description.

### Digital/streaming-edition robustness

No new collection was required. The cached `data/musicbrainz_official_releases.csv` retains `media_json` and identifiable `Digital Media` format values for the 40,469 official releases. The alternate outcome selects the earliest dated official digital/streaming release within each release group; same-day digital ties use the fewer-track edition. This is a robustness outcome only and does not replace the frozen fewest-track headline outcome.

- In the 2009–2019 headline candidate window, after excluding 2014 year-only dates, 8,233 candidate albums remain. A digital/streaming edition is identifiable for 6,801; 1,432 have no identifiable digital format. The digital count differs from the frozen count for 1,053 albums.
- In the resolved-only, genre-known first-pass regression sample, 1,716 albums have a usable genre. Digital editions are identifiable for 1,417, missing for 299, and differ from the frozen count for 466.
- Cached-data-only comparison, with artist-clustered standard errors and year/genre fixed effects, gives the following conventional estimates. The frozen headline bootstrap was not rerun for this robustness screen; the required 9,999-draw genre bootstrap remains part of the first-pass headline analysis.

| Specification | N | Interaction | Artist-clustered SE | Conventional p | Direction |
|---|---:|---:|---:|---:|---|
| Frozen standard outcome, all known-genre albums | 1,716 | -0.0409 | 0.0317 | 0.1971 | Negative |
| Frozen standard outcome, same albums with digital counts | 1,417 | -0.0655 | 0.0322 | 0.0420 | Negative |
| Digital alternate outcome, same albums | 1,417 | -0.0783 | 0.0330 | 0.0176 | Negative |

The alternate outcome therefore does not change the sign; it produces a somewhat larger negative interaction in the common sample. This is a measurement robustness result, not a change to the frozen headline specification. Output: `data/musicbrainz_digital_robustness.csv`; script: `code/analyze_musicbrainz_digital_robustness.py`.

## 19. Resolved-only first-pass headline analysis (2026-09-28)

Ran the frozen headline specification on the resolved-only MusicBrainz sample: 2009–2019 albums, log standard-edition track count, streaming-heavy-by-post interaction, genre and year fixed effects, artist-clustered standard errors, and a nine-cluster Webb six-point wild bootstrap with 9,999 draws and seed 20260928.

| Sample | N albums | N artists | Interaction | Artist-clustered SE | Conventional p | Webb p |
|---|---:|---:|---:|---:|---:|---:|
| Resolved-only headline | 1,716 | 870 | -0.0487 | 0.0326 | 0.135 | 0.112 |

The estimate is negative and not statistically distinguishable from zero under either inference method. Descriptive means show the source of the sign: other-genre albums average 13.12 tracks pre-rule and 13.15 post-rule, while streaming-heavy albums average 14.88 pre-rule and 13.76 post-rule. The post-rule streaming-heavy share above 12 tracks is 57.0%, versus 37.3% for other genres; the share with at least 18 tracks is 12.0% versus 5.8%.

The headline output is in `results/phase3_first_pass/headline.csv`, descriptive means are in `results/phase3_first_pass/headline_means.csv`, and the analysis sample is in `results/phase3_first_pass/analysis_sample.csv`. The bootstrap uses matrix-equivalent OLS and clustered covariance calculations for speed; the model, Webb weights, draw count, and seed are unchanged.

## 20. Mixtape/Street headline eligibility correction (2026-09-28)

Audited the reported 53 rows in `results/phase3_first_pass/analysis_sample.csv` with `mixtape_street_robustness=True`. The collection code correctly computed `eligible_headline_type` for release groups, but `build_standard_album_candidates()` assigned `headline_window_2009_2019` from the release year alone and did not require that eligibility flag. This allowed Mixtape/Street groups into the headline sample; 52 of the 53 contaminated rows were streaming-heavy.

Fixed `code/collect_musicbrainz_discographies.py` so both headline and secondary-window flags require `eligible_headline_type=True`. Rebuilt `data/musicbrainz_standard_album_candidates.csv` entirely from the cached release-group and official-release tables; no API collection was needed. The headline candidate count falls from 8,233 to 7,729, and zero Mixtape/Street rows remain in the headline flag.

### Headline comparison

| Sample | N albums | N artists | Interaction | Artist-clustered SE | Conventional p | Webb p |
|---|---:|---:|---:|---:|---:|---:|
| Original, Mixtape/Street contamination | 1,716 | 870 | -0.0487 | 0.0326 | 0.135 | 0.112 |
| Corrected headline | 1,663 | 853 | +0.0356 | 0.0289 | 0.218 | 0.247 |

The correction removes 53 albums and 17 artist clusters from the resolved-only regression and reverses the point estimate from negative to positive, but the corrected estimate is not statistically distinguishable from zero. The full 9,999-draw Webb bootstrap was rerun with seed 20260928 and nine genre clusters. The corrected first-pass outputs overwrite `results/phase3_first_pass/` and are the results to use going forward; Section 19 is retained as the pre-audit result for transparent comparison.

The refreshed digital robustness sample contains 1,663 known-genre albums, 1,382 identifiable digital editions, 281 missing digital formats, and 462 differing counts. Its common-sample standard interaction is -0.0116 and the digital alternate interaction is -0.0585; these secondary figures supersede the earlier Section 18 table after the eligibility correction.

---

## 21. Question 1: streaming and chart incumbency on the Billboard 200 (2026-09-28)

Run outside the agent (in Claude chat) using only the Kaggle `billboard200.csv`, `streaming.csv`, `digital.csv` and `radio.csv`. Plan written before estimation: `q1_incumbency/q1_analysis_plan.md`. Script: `q1_incumbency/q1_incumbency.py`. Results: `q1_incumbency/results/`.

Verified before running: Billboard lifted catalog restrictions on the Billboard 200 with the chart dated Dec 5, 2009, so the main window starts in January 2010. It ends in December 2019 (before video counted, Jan 2020).

**Main break test (weekly, 2010-2019, linear trend + post-rule level and trend change + week-of-year dummies, Newey-West SEs, 12 lags):**

| Outcome | Pre-rule mean | Pre-rule trend | Jump at Dec 2014 | Trend change |
|---|---:|---:|---:|---:|
| New-entry share | 10.8% | +0.5 pts/yr | -2.6 pts (p < 0.001) | -1.3 pts/yr (p < 0.001) |
| Share held by albums 52+ weeks on chart | 22.1% | +1.9 pts/yr | +5.7 pts (p < 0.001) | +1.7 pts/yr (p < 0.001) |
| Re-entry share | 8.4% | +0.9 pts/yr | -1.3 pts (p = 0.024) | -1.9 pts/yr (p < 0.001) |
| Artist concentration (HHI) | 0.0099 | ~0 | ~0 (p = 0.90) | ~0 (p = 0.26) |

The 2010-2024 window gives the same picture (new-entry jump -3.2 pts; long-runner jump +5.5 pts).

**Placebo dates:** fake breaks in Dec 2011 and Dec 2012 show no drop in new entries (+1.6 and +0.7 pts) and almost no jump in long runners (+0.3, +0.7 pts). Post-rule fake dates (2016, 2017) produce some significant shifts, and trend-change terms are significant at every fake date, so nominal p-values from this model overstate certainty; the level jumps are the more reliable evidence.

**Song-chart comparison (new-entry share, 2013-2019):** no break on the streaming song chart (+2.5 pts, p = 0.39) or the sales song chart (-1.2 pts, p = 0.32); a significant drop on the radio chart (-2.3 pts, p < 0.001). Billboard 200 in the same window: -3.5 pts. Mixed.

**July 2018 second break:** no significant additional shift; Dec 2014 results unchanged when it is included.

**Debut first runs:** the share of new albums lasting only one week rose from 37.5% (2010) to 50.6% (2014) and then levelled off (53-55%). First-run length was shrinking before the rule (-6.5% per year) and stopped shrinking after (trend change +5.7%/yr, p < 0.001); no immediate jump.

**Interpretation:** a large, immediate break at the rule: fewer new entries and more slots held by long-running albums, reversing a rising pre-trend in new entries. Not driven by a few superstars (artist concentration unchanged). Limitations: one treated series (time-series evidence only); no sales-only album chart in the data as a control; the radio-chart drop means the song-chart comparison does not cleanly isolate the counting rule.

**Suggested next step:** scrape Billboard's sales-only Top Album Sales chart for 2010-2019 (the earlier `01_scrape_billboard.py` can do this with a different chart name, after checking the URL slug) to run a proper album-market difference-in-differences.

---

## 22. Question 1b: did streaming-heavy albums gain staying power? (2026-09-28)

Run in Claude chat. Plan written before estimation: `q1b_genre_staying_power/q1b_analysis_plan.md`. Scripts: `build.py` (link chart rows to MusicBrainz artist IDs and genres), `analyze.py` (main test, bootstrap, event study), `album_age.py` (album-age descriptive). Data: Kaggle `billboard200.csv`; `musicbrainz_artist_matches.csv`; per-artist genre labels taken from the corrected `analysis_sample.csv` (the `musicbrainz_genre_balance.csv` file is a 3-row summary, not per-artist); `musicbrainz_release_groups.csv` for release dates.

**Coverage:** 1,040 roster artists have a genre label. 41.3% of Billboard 200 slots in 2010-2019 are labelled (49% in 2010, falling to 23% in 2019 because artists who first charted after Nov 2014 are not on the roster). 21-38% of new debuts are labelled.

**Sample:** 2,807 albums by 971 labelled artists that debuted Jan 2010 - Dec 2018 (full 52-week follow-up before the 2020 video change).

**Raw means, weeks on chart in the first 52 weeks after debut:** other genres 5.47 before -> 3.17 after; streaming-heavy 10.73 -> 10.80.

| Outcome | Streaming-heavy x post | Artist-clustered p | Genre wild bootstrap p (9 clusters) |
|---|---:|---:|---:|
| Weeks on chart, first 52 weeks (primary) | +2.48 weeks | 0.008 | 0.055 |
| Weeks on chart, first 26 weeks | +1.51 weeks | 0.005 | 0.056 |
| Still on chart 26 weeks after debut | +2.6 pts | 0.256 | 0.203 |
| Primary + debut-rank controls | +1.28 weeks | 0.093 | - |
| Primary + artist fixed effects | -0.23 weeks | 0.834 | - |

Event study (reference 2014): pre-period coefficients -0.8 to +0.7, joint test p = 0.878; 2015 +3.6 (p = 0.04), 2016-2018 +0.9 to +1.7 (not significant).

**Album age (descriptive, labelled slots with a release date, 93.7% matched):** share of slots held by albums released 3+ years earlier rose from 6.6% (2010) to 18.1% (2014) to 35.0% (2019) for streaming-heavy artists; other-genre shares are noisy (2.6%, 9.5%, 25.5%). Both were rising before the rule.

**Interpretation:** consistent with the counting rule favouring genres whose fans stream more: streaming-heavy albums held their first-year chart life while other-genre albums lost about 2.3 weeks. Borderline under the prespecified inference (bootstrap p = 0.055). About half the gap reflects streaming-heavy albums debuting higher. With artist fixed effects the gap disappears, so it comes from differences between artists rather than the same artist's albums changing; ageing of the fixed roster (e.g. rock and country roster artists past their peak) is a plausible alternative explanation.

**Bug note:** parsing `first_release_date` (mix of full dates and bare years) with default pandas date inference silently blanked most values; fixed with explicit handling. Worth confirming the agent's pipeline does not have the same issue.
