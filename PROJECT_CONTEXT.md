# PROJECT_CONTEXT.md — Chart Rules and the Streaming Era

Full research context for the Billboard200Paper project, current as of 2026-10-02. `CLAUDE.md` has the working rules; `docs/devlog.md` has the detailed chronological history.

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
| **Headline, ordered rule, corrected dates (current)** | **6,775 albums / 1,492 artists** | **+0.0228** (SE 0.0152) | **p = 0.135; Webb p = 0.167** |

**Conclusion: no evidence albums got longer.** The headline is null on the corrected sample, the event study is flat (pre-2014 joint p = 0.88, no post-rule year significant), and the result does not depend on the genre rule (rock + pop → pop variant: +0.016, Webb p = 0.28). The early positive Spotify result reflected which albums reached the chart. Digital-edition checks: same-sample standard outcome +0.023 (p = 0.18); digital alternate outcome +0.020 (p = 0.24).

**Two bugs found 2026-10-02, both fixed; all earlier Part 1 numbers are superseded.**
1. *Genre labels* (devlog §24): artists matching several genres were assigned at random on each run (Python set order). Now the ordered rule (`docs/genre_classification.md`).
2. *Release dates* (devlog §25): the date parser blanked every full date, so the headline sample held only the 1,663 albums with year-only MusicBrainz dates and no 2014 albums. The corrected sample has 6,775 albums. Dated notes for both are at the end of `docs/analysis_plan.md`.

**Secondary checks** (rebuilt from the Claude-chat versions, `code/18_part1_secondary_checks.py`, plan `docs/part1_secondary_rerun_plan.md`; corrected sample, ordered rule; artist-clustered p, then genre Webb bootstrap p):
- Charted subsample (3,991 albums matched to the Billboard 200): +0.033 (p = 0.049; Webb p = 0.095). Non-charted (2,784): +0.016 (p = 0.56; Webb p = 0.47).
- Selection test (ln tracks × post × heavy on charting, linear probability): +0.177 (p = 0.052; **Webb p = 0.060**). Borderline: long streaming-heavy albums may have become somewhat more likely to chart after the rule.
- Chart payoff among charted albums: debut rank +21.8 (Webb p = 0.15); log weeks on chart +0.51 (Webb p = 0.48). Null.
- Event study (ref 2014): pre 2009–13 between −0.014 and +0.017 (joint p = 0.88); post 2015–19 +0.036, +0.027, +0.003, +0.016, +0.019 (all p > 0.2).
- Exploratory (already looked at in chat; artist-clustered only, no bootstrap): seconds per track −3.9% (p = 0.002); day-one multi-edition launches −5.1 pts (p = 0.007); UK-origin × post on >12 tracks +0.001 (p = 0.98; 405 UK albums, 164 post-rule). The first two are nominally significant but remain exploratory leads; any follow-up needs a written plan first.
- Validation of the rebuild on the old labels: event study and seconds per track reproduce the chat numbers exactly; payoff, non-charted and multi-edition are close; charted, selection and UK differ somewhat (charted flag 1,172 vs 1,168 albums; UK comparison group unrecorded). Details in devlog §25.

Validation already done (devlog §17–18): genre hand-check 0/100 clear errors (it already used the ordered rule; the new labels agree on 91/91 labelled albums); edition hand-check 30/30; Spotify vs MusicBrainz count mismatches 12% and not concentrated post-rule; Wikipedia checks favour MusicBrainz standard counts (caveat: physical vs digital standard editions can differ, e.g. *Pink Friday 2* 10 vs 22). Unresolved artist rates (ordered rule): hip-hop/R&B 19.2%, pop 20.5% (44 artists), Latin 10.4%, electronic 15.9%; streaming-heavy 17.9% vs other 16.5%.

**Not yet run from the plan:** album-order control; drop-pre-debut-albums check; artist fixed effects; mixtape robustness sample; 2009–2024 window; 2010–2019 window; continuous intensity; drop electronic; running time, >12 and ≥18 track outcomes under the frozen model. Check `results/part1_album_length/` before rerunning.

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

## 9. Part 2b — genre staying power (run in Claude chat)

Plan: `docs/q1b_analysis_plan.md`. Scripts: `code/21_part2b_build.py`, `22_part2b_analyze.py`, `23_part2b_album_age.py`; results in `results/part2b_genre_staying_power/`. Genre labels from `data/final/analysis_sample.csv` (1,941 artists: 707 streaming-heavy, 1,234 other; ordered rule, corrected dates); chart rows linked via `musicbrainz_artist_matches.csv`. Coverage: 51% of 2010–2019 chart slots (58% in 2010 → 29% in 2019; post-2014 newcomers not in roster).

- Sample: 4,517 albums / 1,800 artists debuting 2010–2018. Outcome: weeks on chart in the first 52 weeks after debut.
- Results below use the ordered genre rule and the corrected Part 1 sample (devlog §25). Superseded: +2.48 weeks (bootstrap p = 0.055, random labels) and +3.03 (bootstrap p = 0.001, year-only sample).
- Raw means: other genres 6.58 → 5.23 weeks; streaming-heavy 7.81 → 9.50.
- **Parameter:** post × heavy on first-year weeks = **+3.23 weeks** (SE 0.90, artist-clustered p < 0.001; **genre Webb bootstrap p = 0.015**, 9,999 draws).
- Weeks in first 26: +1.78 (bootstrap p = 0.007); still on chart at week 26: +4.6 pts (p = 0.04; bootstrap p = 0.44).
- With debut-rank controls: +2.59 (p < 0.001). With artist fixed effects: +1.73 (p = 0.10; 869 artists with pre and post albums), positive but imprecise.
- Event study: pre-2014 +1.54, −0.06, +0.64, +0.83 (joint p = 0.79); post 2015–18 +3.4, +3.1, +3.3, +3.9 (p = 0.04, 0.04, 0.06, 0.05).
- **Genre-rule sensitivity (exploratory):** with rock + pop artists counted as pop, +2.45 weeks (artist-clustered p = 0.001) but **genre bootstrap p = 0.174**. The genre-level significance depends on that classification call; report it alongside the main result.
- Album age (descriptive): share of labelled slots held by albums 3+ years old, streaming-heavy 4.1% (2010) → 14.4% (2014) → 32.2% (2019); other 7.1% → 14.3% → 35.1%. Rising before the rule in both groups.

## 10. Overall story so far

Counting streams did **not** measurably change what artists produced (Part 1 null on the corrected 6,775-album sample, flat event study, robust to the genre rule), but it **did** change what the chart rewards: long-running albums gained slots and new releases lost them (Part 2, strong). Streaming-heavy albums gained more staying power than others (Part 2b: +3.2 weeks, genre bootstrap p = 0.015); this survives debut-rank controls and is positive within artists, but its genre-level significance is sensitive to how rock + pop artists are classified (bootstrap p = 0.17 under the alternative).

## 11. Open issues and next steps (priority order)

1. ~~Clean up the work environment~~ (devlog §23). ~~Genre tie-break bug~~ (§24). ~~Release-date parsing bug~~ and ~~rerun of the Part 1 secondary checks~~, plus the exploratory rock + pop check (§25).
2. Exploratory leads from §7 (shorter songs; fewer same-day multi-edition launches for streaming-heavy albums after the rule) would need a written plan before any further estimation.
3. **Export a per-artist genre file** from the MusicBrainz tag classification (~2,450 classified artists) and rerun Q1b with it (Q1b currently takes labels for 1,941 artists from the Part 1 sample).
4. **Album-order (career stage) control** for Part 1 and Q1b; finish the remaining frozen-plan secondary checks for Part 1 (§7 "not yet run").
5. **Get Billboard's sales-only Top Album Sales chart, 2010–2019** (needs scraping — ask first; `01_scrape_billboard.py` from the first round can be adapted after checking the URL slug). Enables a proper difference-in-differences for Part 2. Billboard's Top Current Albums chart would also help.
6. Resolve the 994 unmatched roster artists (587 same-name ambiguities); add post-2014 newcomers for Part 2 only (not Part 1, which would reintroduce selection).
7. Further questions answerable with collected data: deluxe re-release timing (official releases table); release cadence and format mix (release groups); song length (official releases).
8. Write-up.

## 12. Literature (verified)

Zanella et al. (2021, *SMJ*, 10.1002/smj.3372) — closest paper (Hot 100 rule, label portfolios). Hiller & Walter (2017, *Rev. Network Econ.*, 10.1515/rne-2017-0064). Elberse (2010, *J. Marketing*, 10.1509/jmkg.74.3.107). Danaher et al. (2014, *Mgmt Sci*, 10.1287/mnsc.2014.1958). Strobl & Tucker (2000, *JCE*, 10.1023/a:1007601402245) — UK chart dynamics, key for Part 2. McKenzie et al. (2020, *JCE*, 10.1007/s10824-020-09396-y). Jensen (2024, *JCE*, 10.1007/s10824-024-09507-z). Ivaldi et al. (2023, *JCE*, 10.1007/s10824-023-09471-0). Klimmt et al. (2023, *Convergence*, 10.1177/13548565231208918). Sorensen (2007, bestseller lists, 10.2139/ssrn.647608). Lech et al. (*EPJ Data Science*, 10.1140/epjds/s13688-025-00571-9; check year 2024 vs 2025). Gourévitch (2023, *Music & Science*, 10.1177/20592043231186692). Winkler et al. (2026, *QME*, 10.1007/s11129-026-09312-2). Callaway & Sant'Anna (2021, *J. Econometrics*). Only cite papers that have been verified.
