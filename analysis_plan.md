# Phase 2: Prespecified Main Test (Approved and Frozen 2026-09-27)

## Research question

Did the December 2014 Billboard 200 rule change lead artists in streaming-heavy genres to release longer standard-edition albums? The headline analysis concerns album length, not chart performance. The artist cohort is determined from pre-rule chart history and frozen before examining post-rule outcomes.

## Primary album universe and pre-release information

The primary artist roster is every artist with at least one Billboard 200 album debut dated from 2009-01-01 through 2014-11-23. Use Kaggle's chart dates as stored; the first issue under the rule, dated 2014-12-13, is stored as 2014-12-10. Include all studio albums by roster artists released from 2009 through 2024, whether or not each album charted. Chart debut is used only to define this pre-rule artist roster and as an outcome in a secondary selection analysis.

Do not use Wikipedia presence, streaming counts, popularity scores, or any other post-release success measure to decide which artists or albums enter this primary universe. Document the artist roster rule, chart matching, and resulting coverage before collection. Use one consistent artist identity rule; record ambiguous or unresolved identities rather than silently dropping them.

Include every studio album released by a roster artist during the analysis window, including albums released before the artist's first qualifying Billboard 200 debut. The artist roster is frozen using chart history that ends before the December 2014 rule change; no post-rule chart result or other post-release success measure determines inclusion. This is the approved universe definition.

A broader list, such as all qualifying major-label studio albums, may be built only as a secondary check. Its label criterion must be observable at the album's release and specified before collection. It must not replace the primary artist-cohort result.

## Main comparison and outcome

Compare albums from streaming-heavy genres with albums from other genres, before versus after the rule. The coefficient of interest is the streaming-heavy-by-post interaction: whether the genre-group difference in album length changed after the rule.

The main outcome is the natural logarithm of the number of tracks on the original standard edition. Count every track, including intros, skits, and interludes. Each album receives equal weight. Include fixed effects for the assigned genre categories and release year. Report artist-clustered standard errors and use the genre-level wild cluster bootstrap p-value as the headline inference.

For the headline p-value, use a restricted wild cluster bootstrap at the nine genre-category level, Webb six-point weights, 9,999 draws, a fixed documented random seed, and a two-sided test of the interaction. Report the number of genre clusters and the bootstrap p-value alongside the artist-clustered coefficient, standard error, and conventional p-value. Do not substitute the artist-clustered p-value for the prespecified headline p-value.

## Genre groups and manual validation

Streaming intensity is each genre's 2014 share of on-demand streams divided by its share of album sales. Streaming-heavy genres have an intensity ratio of at least 1.9:

- Streaming-heavy: hip-hop/R&B (2.05), pop (1.95), Latin (2.08), and electronic (3.40).
- Other genres: rock (0.74), country (0.54), Christian (0.44), jazz (0.15), and classical (0.14).

Use the existing ordered Spotify-genre keyword classification. Before running any regression, draw a reproducible random sample of 100 albums from the assembled primary list and hand-check the album genre assignments against documented reliable genre sources. Define an error as an assigned genre category that is clearly inconsistent with the available album/artist genre evidence; ambiguous cases are recorded separately, not counted as clear errors. Fix only clear errors. Record the random seed, number checked, number of clear errors, error rate, each changed album's artist/title and old/new assignment, and unresolved cases in `devlog.md`. Freeze the assignments after this audit; do not alter them in response to regression results. Albums without a usable genre assignment are excluded from the headline regression, and their number and share are reported.

## Timing and analysis windows

The first Billboard 200 issue using the rule was dated December 13, 2014; Kaggle stores it as December 10, 2014. Define post-rule albums as released on or after 2014-11-24, the start of that tracking week. Releases before that date are pre-rule. Keep this threshold fixed.

The headline release window is 2009-2019 inclusive. The 2009-2024 window is a secondary analysis only. Interpret the extended window in light of the July 2018 change to paid/free stream weighting and the January 2020 addition of video and changes to merchandise/ticket bundle rules; do not treat the later years as an unchanged policy regime.

## Standard edition and eligibility

Use the earliest official release of an album. If standard and deluxe versions were officially released on the same day, use the version with fewer tracks. Count all tracks on that version, including intros, skits, and interludes. Record the source and evidence used to identify the release date, edition, and count. Running time is a secondary outcome.

**Interpretation limitation: physical versus digital standard editions.** MusicBrainz can contain different same-title "standard" editions for physical and digital/streaming formats. For example, *Pink Friday 2* has a 10-track physical standard edition and a 22-track digital/streaming standard release. The frozen fewest-tracks tiebreak therefore defaults toward the physical count when these editions share an applicable date. This is part of the headline measurement definition, not evidence that the digital edition is an error. As a robustness check only, use the earliest official MusicBrainz digital/streaming edition when its media format is identifiable; do not replace the frozen headline outcome.

Include studio albums with at least six standard-edition tracks. Exclude compilations, greatest-hits albums, soundtracks, live albums, holiday albums, and reissues. Report exclusions and missing-data counts. The main regression requires a usable release date, standard-edition track count, and genre.

## Secondary checks

These analyses are secondary and cannot replace or redefine the headline test:

- Use the 2009-2024 release window, with the 2018 and 2020 rule changes noted above.
- Add artist fixed effects to the primary model as a robustness check; report the supporting sample and any loss of identification caused by artists with no within-artist variation.
- Drop each artist's albums released on or before that artist's first qualifying Billboard 200 debut, to assess sensitivity to the pre-period tilt toward charting albums.
- Control for album order in the artist's career (ordinal studio-album number since 2009, or since career start when that history is available) to address aging and career-stage trends. State how incomplete career histories are handled.
- Run the comparison among Billboard 200 debut albums only and among non-debut albums separately.
- Test selection: whether longer albums from streaming-heavy genres became more likely to debut on the Billboard 200 after the rule.
- Estimate the year-by-year streaming-heavy versus other-genre difference in log tracks, with 2014 as reference, and report the joint pre-rule test.
- Use running time, more-than-12-track, and 18-or-more-track outcomes.
- Report continuous genre intensity, exclusion of electronic, a 2010-2019 window as a sensitivity check to the 2009-2019 headline window, genre-level bootstrap inference for alternatives, and the broader major-label list if assembled.
- Treat song-chart debuts, one-week chart duration, chart payoff, Spotify popularity/dilution, and the capped-streaming UK comparison as supporting or exploratory analyses.

Report every prespecified result, including weak and null estimates. Do not promote a secondary specification to the headline based on sign or statistical significance.

## Approval record

Approved and frozen by the user on 2026-09-27. The user explicitly decided to include all 2009-2019 studio albums by roster artists in the headline sample, including albums released before the artist's first qualifying debut; 2009-2024 remains secondary. Roster inclusion uses only pre-rule chart history, so no post-rule information determines inclusion. The sensitivity checks dropping albums on or before each artist's first qualifying debut and controlling for career album order are required secondary checks.

Do not change the primary universe, headline window, outcome, genre groups, treatment date, or headline inference after examining Phase 3 album counts or regression results. Any later deviation must be logged and presented as a deviation, not substituted as the headline test.

## Pre-collection clarifications (2026-09-27)

These dated instructions specify MusicBrainz collection and edition coding. They do not change the approved headline universe, window, outcome, comparison, or inference.

1. **Album type and status.** Define a studio album as a MusicBrainz release group with primary type `Album`, no secondary types, and at least one release whose status is `Official`. Exclude MusicBrainz `Mixtape/Street` release groups from the headline sample; include them only in a separately reported robustness sample.
2. **Standard edition and track count.** Within a release group, choose the earliest-dated worldwide official release. If multiple official releases share that earliest date, choose the one with fewer tracks. Track count is the sum of tracks across all discs/media in the selected release. Record the MusicBrainz artist, release-group, and release IDs and source URL for every album row.
3. **Imprecise dates.** Flag MusicBrainz release dates reported only as a year. For a 2014 year-only date, exclude the album from the headline regression because its position relative to the rule cannot be established. Report the count of these exclusions. Preserve other year-only dates with an imprecision flag and report them; do not invent a month or day.
4. **Source hierarchy.** MusicBrainz Web Service API is the sole primary source for discovering roster-artist discographies and filling album data. Discogs and manual primary-source checks may be used only to investigate flagged records and conduct quality checks; they must not add albums missing from MusicBrainz.

## Phase 3 collection gate

First match every provisional roster entry to a MusicBrainz artist ID using artist search only. Report the match rate and provide an ambiguity file for same-name candidates and the 292 composite-credit entries. Stop for user review at that point. Do not request release groups, releases, media, or track counts until the user has reviewed the artist-ID matches. For subsequent authorized retrieval, comply with MusicBrainz's one-request-per-second limit, use a descriptive User-Agent, and cache raw responses so they need not be downloaded again. After discography retrieval is approved, audit MusicBrainz coverage of Kaggle Billboard 200 debut albums by genre group and before/after period; flag material coverage differences. Count and report same-day different-length editions and differences from Spotify sample counts before resolving any cases.
