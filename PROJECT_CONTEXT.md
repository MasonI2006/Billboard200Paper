# PROJECT_CONTEXT.md — Chart Rules and the Streaming Era

Full research context for the Billboard200Paper project, current as of 2026-10-03. `CLAUDE.md` has the working rules; `docs/devlog.md` has the detailed chronological history.

---

## 1. What the study is about

The Billboard 200 is the main US album chart. Until late 2014 it ranked albums only by sales. From the chart dated **December 13, 2014**, it ranks by "album-equivalent units": 1 album sale = 10 track downloads = **1,500 on-demand audio streams** of songs from the album. The study asks what that counting-rule change did to (1) what artists produce and (2) which albums the chart rewards.

Target journal: *Journal of Cultural Economics* (JCE). Limits: ≤30 pages incl. tables/figures; abstract 150–250 words; 4–6 keywords; JEL codes; LLM use must be described in Methods.

## 2. Economic mechanisms

**Mechanism 1 — a scoring rule shapes production (Goodhart's law).** Streams of every song on an album count toward its chart score, so each extra song is another source of chart points. A label that values chart position has an incentive to add songs ("album padding"). Theory foil: Hiller & Walter (2017) predict streaming leads to fewer, better songs.

**Mechanism 2 — counting use instead of purchase changes who wins.** A sale happens once, mostly in release week; a stream recurs every time someone plays the album. A purchase-based chart rewards front-loaded new releases; a listening-based chart rewards albums with lasting replay value (catalog, greatest hits). Chart position drives visibility (press, radio, playlists), so the rule may raise entry barriers for new releases.

## 3. Research questions

- **Part 1 (original):** After the rule, did albums get longer in genres whose fans stream a lot, relative to genres whose fans mostly bought albums?
- **Part 2 (emerged):** After the rule, did the chart become "stickier" — fewer new albums entering and more slots held by long-running albums?
- **Part 2b:** Did albums in streaming-heavy genres gain more staying power than albums in other genres?

## 4. Key institutional facts (verified)

| Event | Detail |
|---|---|
| Catalog albums allowed on Billboard 200 | Chart dated Dec 5, 2009 (why Part 2 starts in Jan 2010) |
| Streams added to Billboard 200 | Chart dated Dec 13, 2014 (tracking week ending Nov 30, 2014) |
| Paid vs free stream weighting | Chart dated July 14, 2018: 1,250 paid or 3,750 ad-supported streams = 1 unit |
| Video (YouTube) added; bundle rules tightened | Chart dated Jan 18, 2020 |
| Merch/ticket bundles dropped | Announced July 2020 (tours from Oct 2, 2020; merch date unconfirmed) |
| Later change (outside window) | Chart dated Jan 17, 2026: 1,000 paid / 2,500 free; YouTube data withdrawn after Jan 16, 2026 |
| UK album chart | Streams from 1 March 2015, but only the top 12 tracks of the standard edition count — from the start (no later "reversal") |

**Genre streaming intensity** (Nielsen 2014 US year-end report; genre share of streams ÷ share of album sales): electronic 3.40, Latin 2.08, hip-hop/R&B 2.05, pop 1.95, rock 0.74, country 0.54, Christian 0.44, jazz 0.15, classical 0.14. **Streaming-heavy = ratio ≥ 1.9** (hip-hop/R&B, pop, Latin, electronic). Use the ratio, not raw stream share (raw share mostly measures genre size).

## 5. Data sources

| Source | What it gives | Location |
|---|---|---|
| Kaggle `ludmin/billboard` | Weekly Billboard 200 (1963–2026), Hot 100, streaming/digital-sales/radio song charts (top 50). Columns: Date, Song, Artist, Rank, Last Week, Peak Position, Weeks in Charts, Image URL | `data/raw/` |
| Spotify sample | ~8,800 tracks / 5,300 albums, 2009–2025: track counts, genres, popularity (exploratory only) | `data/raw/` |
| MusicBrainz API | Artist IDs, 72,091 release groups, 40,469 official releases, 10,913 standard-edition album candidates, artist tags | `data/external/` (tables + raw caches) |

Kaggle quirks: dates stored 3 days early (Dec 13, 2014 chart → 2014-12-10); album title is in `Song`; new debut = `Weeks in Charts == 1`.

## 6. Part 1 — design (frozen in `docs/analysis_plan.md`, approved 2026-09-27)

- **Sample universe (no selection on success):** artists with ≥1 Billboard 200 debut between 2009-01-01 and 2014-11-23 (3,361 roster entities; 2,367 resolved to MusicBrainz IDs). Include **all** their studio albums released 2009–2019, charted or not. 2009–2024 is secondary.
- **Album eligibility:** MusicBrainz release group primary type Album, no secondary types, Official status. Mixtape/Street excluded from headline (separate robustness check). ≥6 tracks.
- **Outcome:** log track count of the original standard edition = earliest official worldwide release; same-day ties → fewer tracks; tracks summed across discs; intros/skits count. 2014 year-only dates excluded.
- **Post-rule:** release on/after 2014-11-24.
- **Model:** `ln(tracks) ~ post:heavy + C(genre) + C(year)`, unweighted.
- **Parameter (β):** coefficient on post × streaming-heavy = the differential change in log album length for streaming-heavy vs other genres after the rule (≈ percent).
- **Genre assignment:** MusicBrainz artist tags mapped to 9 genres by keyword; artists matching several genres are assigned by the ordered rule latin → hip-hop/R&B → country → Christian → jazz → classical → electronic → rock → pop (first match wins). Rule and reasoning: `docs/genre_classification.md` (adopted 2026-10-02 after a random tie-break bug; dated note in the plan).
- **Headline inference:** restricted wild cluster bootstrap at the 9 genre clusters, Webb six-point weights, 9,999 draws, seed 20260928. Artist-clustered SEs reported alongside.
- **Secondary checks in the plan:** charted-only and non-charted subsamples; selection test (did long streaming-heavy albums become more likely to chart?); event study (ref 2014, joint pre-test); running time, >12 tracks, ≥18 tracks; continuous intensity; drop electronic; 2010–2019; artist fixed effects; drop albums released on/before artist's first qualifying debut; **album-order (career stage) control**; mixtape robustness; digital-edition alternate outcome.

## 7. Part 1 — results

| Estimate | Sample | Coefficient | Inference |
|---|---|---|---|
| Spotify sample, charting albums only (exploratory) | 499 albums | +0.123 | p = 0.015 (selection-biased) |
| Resolved-only, before mixtape fix | 1,716 | −0.0487 | p = 0.135; Webb p = 0.112 |
| Corrected headline, random genre labels, year-only sample (superseded) | 1,663 / 853 | +0.0356 (SE 0.0289) | p = 0.218; Webb p = 0.247 |
| Ordered genre rule, year-only sample (superseded) | 1,663 / 853 | −0.0247 (SE 0.0291) | p = 0.397; Webb p = 0.434 |
| **Headline, ordered rule, corrected dates, artist clusters (current)** | **6,775 albums / 1,942 artists** | **+0.0228** (SE 0.0151) | **p = 0.133; Webb p = 0.161** |

**Conclusion: no evidence albums got longer.** The headline is null on the corrected sample, the event study is flat (pre-2014 joint p = 0.88, no post-rule year significant), and the result does not depend on the genre rule (rock + pop → pop variant: +0.016, Webb p = 0.29) or on the album-order (career-stage) control (+0.021, Webb p = 0.21). The early positive Spotify result reflected which albums reached the chart. Digital-edition checks: same-sample standard outcome +0.023 (p = 0.16); digital alternate outcome +0.020 (p = 0.23).

**Three bugs found 2026-10-02/03, all fixed; all earlier Part 1 numbers are superseded.**
1. *Genre labels* (devlog §24): artists matching several genres were assigned at random on each run (Python set order). Now the ordered rule (`docs/genre_classification.md`).
2. *Release dates* (devlog §25): the date parser blanked every full date, so the headline sample held only the 1,663 albums with year-only MusicBrainz dates and no 2014 albums. The corrected sample has 6,775 albums.
3. *Artist clusters* (devlog §26): the artist-cluster variable was the first word of the artist's name (a pandas regex split), so SEs, p-values and artist counts were off; coefficients were not affected. Dated notes for all three are at the end of `docs/analysis_plan.md`.

**Secondary checks** (rebuilt from the Claude-chat versions, `code/18_part1_secondary_checks.py`, plan `docs/part1_secondary_rerun_plan.md`; corrected sample, ordered rule; artist-clustered p, then genre Webb bootstrap p):
- Charted subsample (3,991 albums matched to the Billboard 200): +0.033 (p = 0.035; Webb p = 0.084). Non-charted (2,784): +0.016 (p = 0.57; Webb p = 0.47).
- Selection test (ln tracks × post × heavy on charting, linear probability): +0.177 (p = 0.058; **Webb p = 0.063**). Borderline: long streaming-heavy albums may have become somewhat more likely to chart after the rule.
- Chart payoff among charted albums: debut rank +21.8 (Webb p = 0.14); log weeks on chart +0.51 (Webb p = 0.45). Null.
- Event study (ref 2014): pre 2009–13 between −0.014 and +0.017 (joint p = 0.85); post 2015–19 +0.036, +0.027, +0.003, +0.016, +0.019 (all p > 0.2).
- Exploratory (already looked at in chat; artist-clustered only, no bootstrap): seconds per track −3.9% (p = 0.002); day-one multi-edition launches −5.1 pts (p = 0.008); UK-origin × post on >12 tracks +0.001 (p = 0.98; 405 UK albums, 164 post-rule). The first two are nominally significant but remain exploratory leads; any follow-up needs a written plan first.
- Validation of the rebuild on the old labels: event study and seconds per track reproduce the chat numbers exactly; payoff, non-charted and multi-edition are close; charted, selection and UK differ somewhat (charted flag 1,172 vs 1,168 albums; UK comparison group unrecorded). Details in devlog §25.

Validation already done (devlog §17–18): genre hand-check 0/100 clear errors (it already used the ordered rule; the new labels agree on 91/91 labelled albums); edition hand-check 30/30; Spotify vs MusicBrainz count mismatches 12% and not concentrated post-rule; Wikipedia checks favour MusicBrainz standard counts (caveat: physical vs digital standard editions can differ, e.g. *Pink Friday 2* 10 vs 22). Unresolved artist rates (ordered rule): hip-hop/R&B 19.2%, pop 20.5% (44 artists), Latin 10.4%, electronic 15.9%; streaming-heavy 17.9% vs other 16.5%.

**Frozen-plan secondary checks** (`code/24_part1_plan_checks.py`, plan `docs/items4_5_plan.md`; artist-clustered p, then Webb p):
- **Album-order (career-stage) control**, ordinal among the artist's MusicBrainz studio albums since career start: +0.021 (p = 0.18; Webb p = 0.21). Since-2009 ordinal: +0.011 (Webb p = 0.37).
- Artist fixed effects (within; 1,394 artists with pre and post albums): +0.019 (Webb p = 0.30). Drop albums on/before the artist's first qualifying debut (4,491 albums): +0.029 (Webb p = 0.20). With Mixtape/Street (+670): −0.016 (Webb p = 0.74). 2009–2024 window: +0.013 (Webb p = 0.45). 2010–2019: +0.026 (Webb p = 0.12). Continuous intensity: +0.012 per ratio point (Webb p = 0.11). Without electronic: +0.020 (Webb p = 0.23). Log running time: −0.015 (Webb p = 0.81). More than 12 tracks: +0.009 (Webb p = 0.75).
- **18 or more tracks: +4.3 pts (p = 0.004; Webb p = 0.012).** The one significant check of 12 (about 0.6 expected by chance at 5%). Mean length and the >12 share do not move, so if anything the rule is associated with more very long albums in streaming-heavy genres, not longer albums overall. Prespecified secondary outcome; reported, not promoted.
- **What the null rules out (devlog §34):** 90% CI −0.03 to +0.63 tracks. We can rule out increases above about 0.63 tracks (4.9%; TOST), but not a prespecified half-track bound (TOST p = 0.16). MDE 0.56 tracks.
- **Follow-up (plan `docs/long_albums_followup_plan.md`, devlog §28): the 18+ result does not generalise robustly.** Of five prespecified upper-tail tests (shares >= 15, >= 20, >= 25 tracks; 75th and 90th percentiles), **0 survive Holm**. A1 -0.004 (Webb p = 0.91); A2 +0.030 (0.062); A3 +0.013 (0.088); A4 +0.061 (bootstrap p = 0.049); A5 +0.069 (0.065). No pre-trend in the >= 18 share (joint p = 0.998). Descriptively, the positive coefficients sit at 18-23 tracks. There is no rise in albums >= 60 minutes (Webb p = 0.80), consistent with shorter songs. Paper wording: suggestive, not robust.
- Not run: the plan's "broader major-label list" (never assembled).

## 8. Part 2 — chart incumbency (run in Claude chat)

Plan: `docs/q1_analysis_plan.md` (written before estimation). Script: `code/20_part2_incumbency.py`; results in `results/part2_incumbency/`. Data: Kaggle charts only (no MusicBrainz).

- **Outcomes (weekly):** share of 200 slots held by new entries; share held by albums with 52+ weeks on chart.
- **Model (interrupted time series, 2010-01 to 2019-12):** `Y_t = α + β·t + τ·Post_t + δ·(t − t0)·Post_t + week-of-year FE + ε_t`, Newey-West SEs (12 lags).
- **Parameters:** **τ** = immediate jump at the rule vs the extrapolated pre-trend (main); δ = change in trend.

| Outcome | Pre mean | Pre trend | τ (jump) | δ (trend change) |
|---|---|---|---|---|
| New-entry share | 10.8% | +0.5 pts/yr | −2.6 pts (p<0.001) | −1.3 pts/yr |
| 52+-week share | 22.1% | +1.9 pts/yr | +5.7 pts (p<0.001) | +1.7 pts/yr |
| Re-entry share | 8.4% | | −1.3 pts (p=0.02) | −1.9 pts/yr |
| Artist concentration (HHI) | | | ≈0 (p=0.90) | ≈0 |

Example: chart dated Dec 6, 2014 had 30 new albums and 29 year-plus albums; Dec 7, 2019 had 11 and 102.

Checks: fake dates Dec 2011/2012 show no comparable jump; fake dates in 2016/2017 and trend-change terms are significant at fake dates too, so nominal p-values overstate certainty (trust τ more than δ). Song charts (2013–2019): no break on streaming (+2.5 pts, p=0.39) or sales (−1.2, p=0.32) charts, but a significant drop on radio (−2.3, p<0.001) — mixed. July 2018 adds no further break.

**Main limitation:** one treated series; no sales-only album chart as a control.

**UK comparison** (plan `docs/uk_comparison_plan.md`, devlog §31). The UK albums chart added streams from 1 March 2015.
- **UK at its own date:** jumps in the predicted direction but small and not significant (new-entry −0.6 pts, placebo-rank p = 0.55; 52+-week +1.9 pts, p = 0.94).
- **UK placebo at the U.S. date:** about zero.
- **Plan verdict, as written:** "common shock indicated" (the clause "UK does not break at its own date"). But the data show no common shock: the UK new-entry share is flat 2014–2019 (11.5% → 10.1%) while the U.S. share halves (11.8% → 5.7%). The UK 52+-week share rises gradually in both countries (UK 26% → 40%, U.S. 26% → 49%).
- **Reading:** the U.S. new-entry decline is U.S.-specific, consistent with Billboard's rule; catalogue ageing is partly a shared trend, with a U.S.-only jump at the rule.
- **Placebo-date ranks for the U.S. jumps** (new for Part 2): new-entry p = 0.003, 52+-week p = 0.076.

**Matched albums and RIAA control** (plan `docs/matched_albums_plan.md`, devlog §33; 4,678 albums on both charts, 50/50 hand check).
- **Same-album test:** after the U.S. rule, matched catalogue albums gained U.S. top-100 presence relative to their own UK presence (+0.0026, about 6.5 albums; placebo-rank p = 0.071; Holm 0.14). About half the gap closed when the UK started counting streams (|tau2| / tau1 = 0.46, "formula details matter" under the plan's cut-off, borderline). It vanishes if trend changes are added (fragile).
- **RIAA control:** the U.S. jumps survive (new-entry −0.026 → −0.029 to −0.033; 52+-week +0.057 → +0.050 to +0.056; all p < 0.001).
- **New releases (B):** null.

## 9. Part 2b — genre staying power (run in Claude chat)

Plan: `docs/q1b_analysis_plan.md`. Scripts: `code/21_part2b_build.py`, `22_part2b_analyze.py`, `23_part2b_album_age.py`; results in `results/part2b_genre_staying_power/`. Genre labels from `data/final/analysis_sample.csv` (1,941 artists: 707 streaming-heavy, 1,234 other; ordered rule, corrected dates); chart rows linked via `musicbrainz_artist_matches.csv`. Coverage: 51% of 2010–2019 chart slots (58% in 2010 → 29% in 2019; post-2014 newcomers not in roster).

- Sample: 4,517 albums / 1,800 artists debuting 2010–2018. Outcome: weeks on chart in the first 52 weeks after debut.
- Results below use the ordered genre rule and the corrected Part 1 sample (devlog §25). Superseded: +2.48 weeks (bootstrap p = 0.055, random labels) and +3.03 (bootstrap p = 0.001, year-only sample).
- Raw means: other genres 6.58 → 5.23 weeks; streaming-heavy 7.81 → 9.50.
- **Parameter:** post × heavy on first-year weeks = **+3.23 weeks** (SE 0.90, artist-clustered p < 0.001; **genre Webb bootstrap p = 0.015**, 9,999 draws).
- Weeks in first 26: +1.78 (bootstrap p = 0.007); still on chart at week 26: +4.6 pts (p = 0.04; bootstrap p = 0.44).
- With debut-rank controls: +2.59 (p < 0.001). With artist fixed effects: +1.73 (SE 0.81, p = 0.034; 869 artists with pre and post albums; within estimator). With explicit artist dummies the SE counts the absorbed effects: SE 1.05, p = 0.10 (footnote).
- Event study: pre-2014 +1.54, −0.06, +0.64, +0.83 (joint p = 0.79); post 2015–18 +3.4, +3.1, +3.3, +3.9 (p = 0.04, 0.04, 0.06, 0.05).
- **Album-order (career-stage) control** (ordinal of the album's Billboard 200 debut in the artist's chart career since 1963): +3.10 (p < 0.001; bootstrap p = 0.012). The effect is not explained by roster ageing along this dimension.
- **Labels from the per-artist genre file** (`data/final/artist_genres.csv`, 2,034 artists; secondary, since the Part 2b plan names the Part 1 sample as the label source): 4,696 albums, +3.29 (p < 0.001; bootstrap p = 0.010).
- Note on the artist-FE SE: until 2026-10-03 the reported +1.73 used a correction that counts the ~1,800 absorbed artist dummies (p = 0.10). The author switched it to the within estimator (p = 0.034), the standard treatment when fixed effects are nested in clusters and the one the Part 1 FE check uses. The switch was made after both numbers were seen, which is stated in the dated note on `docs/q1b_analysis_plan.md` (devlog §27).
- **Cross-country (devlog §33):** on the UK chart, the Part 2b effect is null (+0.03 weeks, p = 0.98; 1,641 labelled UK debuts). Holding the album fixed across the two charts, streaming-heavy albums gained +7.8 more first-year U.S. weeks than UK weeks after the U.S. rule (artist p = 0.06, but genre-bootstrap p = 0.43). Part 2b looks U.S.-specific.
- **Leave-one-genre-out (devlog §34):** all nine estimates positive (+1.85 to +3.73). Without hip-hop/R&B: +1.85 (bootstrap p = 0.10); without any other genre: +3.0 to +3.7 (bootstrap p < 0.03). Not driven by a single genre under the fixed rule, but hip-hop/R&B carries much of it.
- **Genre-rule sensitivity (exploratory):** with rock + pop artists counted as pop, +2.45 weeks (artist-clustered p = 0.001) but **genre bootstrap p = 0.174**. The genre-level significance depends on that classification call; report it alongside the main result.
- Album age (descriptive): share of labelled slots held by albums 3+ years old, streaming-heavy 4.1% (2010) → 14.4% (2014) → 32.2% (2019); other 7.1% → 14.3% → 35.1%. Rising before the rule in both groups.

## 10. Overall story so far

Counting streams did **not** measurably change what artists produced on average (Part 1 null on the corrected 6,775-album sample, flat event study, robust to the genre rule and the album-order control; the one exception among 12 frozen-plan checks, a 4-point rise in the share of albums with 18+ tracks in streaming-heavy genres, does not survive a prespecified upper-tail follow-up), but it **did** change what the chart rewards: long-running albums gained slots and new releases lost them (Part 2, strong). Streaming-heavy albums gained more staying power than others (Part 2b: +3.2 weeks, genre bootstrap p = 0.015); this survives debut-rank and album-order (career-stage) controls and the broader per-artist label file, and is positive within artists (+1.73, p = 0.034), but its genre-level significance is sensitive to how rock + pop artists are classified (bootstrap p = 0.17 under the alternative).

## 11. Open issues and next steps (priority order)

1. ~~Clean up the work environment~~ (devlog §23). ~~Genre tie-break bug~~ (§24). ~~Release-date parsing bug~~ and ~~rerun of the Part 1 secondary checks~~, plus the exploratory rock + pop check (§25). ~~Artist-cluster bug~~, ~~per-artist genre file~~, ~~album-order control~~ and ~~remaining frozen-plan checks~~ (§26).
2. ~~Author decisions~~ (devlog §27): Part 2b keeps the Part 1-sample labels (artist file = robustness row); Part 2b artist-FE uses the within-estimator SE. ~~18+-track follow-up~~ (§28: 0 of 5 upper-tail tests survive Holm; reported as suggestive, not robust). The shorter-songs and multi-edition leads stay exploratory, with no new estimates.
3. **A control for Part 2.** Billboard's sales-only Top Album Sales chart would allow a proper difference-in-differences, but billboard.com's robots.txt blocks AI agents, so the agent cannot scrape it (devlog §29). The `01_scrape_billboard.py` mentioned earlier does not exist. Options: an existing dataset, library back issues, a data request, or the author's own collection. **In progress instead:** UK Official Albums Chart data from the author (UK added streams from the chart of 1 March 2015, a different date; tidied in step 28 with the missing #1 rows rebuilt, devlog §30; comparison run, devlog §31: UK has no significant break at its own date, but also no common shock; U.S. new-entry decline is U.S.-specific), then matched-album tests, devlog §33: same-album U.S. catalogue gain at the U.S. date (placebo p = 0.07, fragile), Part 2 jumps survive the RIAA control, Part 2b does not replicate in the UK, plus RIAA U.S. revenue by format (tidied, step 27: streaming share 23% in 2013, 31% in 2014, 38% in 2015, a smooth trend with no break). Also considered: the song charts already in hand as a fuller placebo section, and a test that locates the break date from the data. Each needs a written plan before estimation.
4. Resolve the 994 unmatched roster artists (587 same-name ambiguities); add post-2014 newcomers for Part 2 only (not Part 1, which would reintroduce selection).
5. Further questions answerable with collected data: deluxe re-release timing (official releases table); release cadence and format mix (release groups); song length (official releases).
6. Write-up. **Materials ready in `paperwriting/`** (outline, test registry, parameter list, figures; devlog §35).

## 12. Literature (verified)

Zanella et al. (2021, *SMJ*, 10.1002/smj.3372) — closest paper (Hot 100 rule, label portfolios). Hiller & Walter (2017, *Rev. Network Econ.*, 10.1515/rne-2017-0064). Elberse (2010, *J. Marketing*, 10.1509/jmkg.74.3.107). Danaher et al. (2014, *Mgmt Sci*, 10.1287/mnsc.2014.1958). Strobl & Tucker (2000, *JCE*, 10.1023/a:1007601402245) — UK chart dynamics, key for Part 2. McKenzie et al. (2020, *JCE*, 10.1007/s10824-020-09396-y). Jensen (2024, *JCE*, 10.1007/s10824-024-09507-z). Ivaldi et al. (2023, *JCE*, 10.1007/s10824-023-09471-0). Klimmt et al. (2023, *Convergence*, 10.1177/13548565231208918). Sorensen (2007, bestseller lists, 10.2139/ssrn.647608). Lech et al. (*EPJ Data Science*, 10.1140/epjds/s13688-025-00571-9; check year 2024 vs 2025). Gourévitch (2023, *Music & Science*, 10.1177/20592043231186692). Winkler et al. (2026, *QME*, 10.1007/s11129-026-09312-2). Callaway & Sant'Anna (2021, *J. Econometrics*). Only cite papers that have been verified.
