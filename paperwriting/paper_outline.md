# Paper outline

Target: *Journal of Cultural Economics*, about 30 pages plus an online appendix. Numbers below come from `parameters.md` (generated from the results files). Test status codes (FP, PS, PF, EX, DE) are explained in `test_registry.md`. Figures are in `figures/` and listed in `README.md`.

## Working title options

1. *Changing the Scoreboard: How Counting Streams Reshaped the Billboard 200 but Not the Albums on It*
2. *Measurement Rules and Market Rewards: Evidence from Billboard's 2014 Streaming Rule*
3. *Did Streaming Change the Album? Production and Chart Responses to Billboard's 2014 Rule Change*

## Core claims (keep the paper anchored on these)

1. **No production response on average.** Streaming-heavy albums did not get longer after the rule. We can rule out increases above about two-thirds of a track (4.9%), and there are no pre-trends.
2. **A sharp change in what the chart rewards.** At the rule, the new-entry share fell by 2.6 points (from 10.8%) and the 52+-week share rose by 5.7 points (from 22.1%). The new-entry jump is larger than at all but one of about 350 fake dates.
3. **It is the rule, not the streaming boom.** Four pieces of evidence:
   - the jumps survive controls for actual U.S. streaming growth (RIAA);
   - the UK chart, which shared the streaming boom but changed its rule three months later, shows no break at either date, and its new-entry share stayed flat while the U.S. share halved;
   - the same albums gained U.S. chart presence relative to their own UK presence at the U.S. date (suggestive; fragile to trend terms);
   - the event study shows a step, not a drift.
4. **Who benefits (supporting).** Albums in streaming-heavy genres gained about 3.2 weeks of first-year chart life. The result is:
   - largest for hip-hop/R&B;
   - absent on the UK chart;
   - sensitive to how rock + pop artists are classified.

   Present it as a U.S.-specific supporting result.

Optional discussion claim (interpretation, not a tested result): the evidence leans toward *how* streams were counted mattering, not just *whether*. Billboard's 2014 formula had no track cap or down-weighting; the UK's did.

## Abstract skeleton (~150 words)

- **Setting:** In December 2014 the Billboard 200 began counting streams.
- **Production:** Using 6,775 albums by artists with pre-rule chart careers, we find no change in album length for streaming-heavy genres (effects above 5% ruled out).
- **Chart rewards:** The new-entry share fell 2.6 points and the share held by year-old albums rose 5.7 points at the rule. The jumps are exceptional relative to placebo dates, survive controls for streaming growth, and are absent from the UK chart, which adopted streams later under a different formula.
- **Genre:** Streaming-heavy albums gained about three weeks of chart life in the U.S. but not in the UK.
- **Takeaway:** Ranking rules can reshape competition among products without changing the products.

## 1. Introduction (3–4 pages)

- **Hook:** rankings run cultural markets (charts, bestseller lists, app stores, playlists). When a ranking's formula changes, do producers change what they make, or does the ranking just reward different products?
- **The natural experiment:** a single, dated rule change. Billboard 200 chart dated 13 December 2014 (stored 2014-12-10 in the data).
- **Preview of the three findings and the four pieces of identification evidence** (core claims above).
- **Contribution** (verified citations only; list in PROJECT_CONTEXT §12):
  - **Chart dynamics and incumbency:** Strobl & Tucker (2000, *JCE*); Elberse (2010).
  - **Bestseller lists and rankings:** Sorensen (2007).
  - **Streaming and music markets:** Hiller & Walter (2017); McKenzie et al. (2020, *JCE*); Ivaldi et al. (2023, *JCE*); Jensen (2024, *JCE*).
  - **Closest paper:** Zanella et al. (2021, *SMJ*), on the Hot 100 rule and label portfolios. Differentiate: albums, not songs; production *and* rewards; a cross-country comparison with a different adoption date.
- **Transparency:** pre-written analysis plans, every test reported (online appendix registry).

## 2. Institutional background (2–3 pages)

- **How the Billboard 200 is compiled:** before December 2014, sales only; after, album-equivalent units (1,500 song streams = 1 album unit; track-equivalent albums). Catalogue albums were allowed on the chart from December 2009, which is why the window starts in 2010.
- **Later U.S. changes, outside or controlled for:** July 2018 paid/free stream weighting (tested, no further break); January 2020 video streams (after the window).
- **The UK Official Albums Chart:** streams included from the chart of 1 March 2015. The 12 most-streamed tracks count, the top two are down-weighted, and 1,000 streams = 1 sale. Later singles-chart changes are not modelled; the July 2018 album weighting is unverified.
- **Fig. 1 (RIAA revenue):** streaming grew smoothly through the rule (23% of U.S. revenue in 2013, 31% in 2014, 38% in 2015). That smooth trend is the backdrop against which the chart breaks are sharp.
- **Mechanisms and predictions:**
  - Production: per-track streaming makes extra tracks raise album units, so the incentive is to lengthen albums, especially in streaming-heavy genres.
  - Rewards: streams accrue to catalogue albums over time, so incumbents are favoured, especially in streaming-heavy genres.

## 3. Data (3–4 pages)

- **Chart data:**
  - Billboard 200 weekly (Kaggle), 2010–2019 main window (2010–2024 secondary).
  - Song charts (streaming, digital sales, radio).
  - UK Official Albums Chart top 100 (2000–2025), with the #1 rows rebuilt.
- **Part 1 album universe:**
  - Pre-rule roster: 3,361 artist entities with Billboard 200 debuts before the rule; 2,367 resolved to MusicBrainz IDs.
  - MusicBrainz studio-album release groups (Mixtape/Street excluded), standard edition = earliest official release.
  - 10,913 candidates (7,729 in 2009–2019); **6,775 albums by 1,942 artists** with a genre and ≥ 6 tracks.
  - Explain why the roster is pre-rule: post-rule newcomers would reintroduce selection.
- **Genre classification:**
  - MusicBrainz tags mapped to 9 genres by an ordered rule.
  - Streaming-heavy = hip-hop/R&B, pop, Latin, electronic (Nielsen streaming-to-sales ratios > 1).
  - 2,451 labelled artists (903 streaming-heavy).
  - 100-album hand check: 0 clear errors.
- **Part 2 outcomes:** weekly new-entry share (first-ever chart week) and 52+-week share (cumulative weeks on chart).
- **Part 2b sample:** 4,517 Billboard 200 debuts (2010–2018) by genre-labelled artists; outcome = weeks on chart in the first 52 weeks.
- **RIAA revenue by format (1973–2025).**
- **U.S.-UK matched albums:** 4,678 albums on both charts; 50 of 50 hand-checked correct.
- **Table 1 (summary statistics):**
  - Part 1 means by group and period (other 12.50 → 12.18 tracks; streaming-heavy 13.99 → 14.05);
  - Part 2 weekly means (2014 vs 2019);
  - Part 2b means by group and period (other 6.58 → 5.23 weeks; streaming-heavy 7.81 → 9.50).

## 4. Part 1: did album length change? (4–5 pages)

- **Design:** difference-in-differences, `ln(tracks) ~ post x streaming-heavy + genre FE + release-year FE`. Post = released on/after 2014-11-24. Artist-clustered SEs; genre-level restricted Webb wild cluster bootstrap (9 clusters, 9,999 draws). Explain why the genre bootstrap: treatment varies at the genre level.
- **Fig. 2:** mean tracks by year and group (raw data).
- **Table 2:**
  - headline (+0.0228, SE 0.0151, p = 0.133, Webb p = 0.161);
  - what the null rules out (90% CI −0.03 to +0.63 tracks; TOST bound 0.63 tracks / 4.9%; MDE 0.56; half-track bound not ruled out);
  - key robustness checks: album order, artist FE, windows, intensity, Mixtape/Street, digital edition.
- **Fig. 3:** event study (joint pre-2014 p = 0.85).
- **Other outcomes:** > 12 tracks (null), running time (null), ≥ 18 tracks (+4.3 pts, Webb p = 0.012). The 18+ result is 1 of 12 checks, and its prespecified follow-up fails (0 of 5 upper-tail tests survive Holm). Present it as "suggestive, not robust". Fig. A1 shows where the positive estimates sit (18–23 tracks).
- **Selection and payoff** (marginal/null), charted vs non-charted subsamples.
- **Exploratory footnote:** seconds per track −3.9% (p = 0.002) and fewer same-day multi-edition launches (−5.1 pts), labelled exploratory.
- **Interpretation:** the chart incentive to pad was small next to artistic, contractual and reputational costs, and it was concentrated among a few acts.

## 5. Part 2: did the chart reward different albums? (5–6 pages)

- **Design:** interrupted time series on weekly shares: `Y_t = a + b·t + tau·Post_t + d·(t − t0)·Post_t + week-of-year FE`, Newey–West SEs (12 lags). The level jump tau is the parameter of interest.
  - Explain why tau and not the trend change d: fake dates also give significant trend changes.
- **Fig. 4:** U.S. vs UK weekly series with both rule dates (the key figure).
- **Table 3:**
  - jumps: new-entry −2.6 pts, 52+-week +5.7 pts, re-entry −1.3, HHI ≈ 0;
  - placebo-rank p (0.003, 0.076);
  - RIAA controls (−2.9 to −3.3; +5.0 to +5.6);
  - 2010–2024 window;
  - July 2018 (no extra break).
- **Fig. 5:** monthly event study, U.S. and UK. U.S.: step down in new entries after an upward drift; step up in 52+. UK: no step.
- **5.x Cross-country evidence (Table 4):**
  - UK at its own date: no break (placebo p 0.55 / 0.94);
  - UK at the U.S. date: about zero;
  - pooled own- vs other-date test;
  - matched catalogue albums: +6.5 albums at the U.S. date, placebo p = 0.071, Holm 0.14, fragile to trend terms;
  - new releases: null.
  - **Report the plan's literal verdict ("common shock indicated", via its "no UK break" clause) and explain the caveat.** The UK shows no shock at either date.
- **Selection caveat for matched albums:** their share of U.S. top-100 slots rose from 48.8% to 59.1% at the rule.
- **Interpretation:**
  - the rule raised the bar for entry: fewer new albums, more slots for incumbents;
  - long-run catalogue ageing is partly a shared U.S./UK trend; the U.S. adds a jump at its rule.

## 6. Part 2b: who gained staying power? (3 pages)

- **Design:** album-level DiD, `weeks52 ~ post x streaming-heavy + genre FE + debut-year FE`, artist-clustered SEs, genre bootstrap.
- **Table 5:**
  - main +3.23 weeks (boot p = 0.015);
  - first 26 weeks +1.78;
  - debut-rank controls +2.59;
  - artist FE +1.73 (p = 0.034, with the SE-choice footnote);
  - album order +3.10;
  - artist-file labels +3.29.
- **Fig. 6:** event study (pre p = 0.79; post +3.1 to +3.9).
- **Limits, stated in the main text:**
  - rock + pop → pop classification gives boot p = 0.17;
  - without hip-hop/R&B: +1.85 (boot p = 0.10) (Fig. A4);
  - on the UK chart: null (+0.03);
  - holding the album fixed across charts: +7.8 weeks but boot p = 0.43.
- **Conclusion for this section:** a U.S.-specific effect, largest in the most streaming-intensive genre.

## 7. Discussion (2 pages)

- Rankings as market institutions: the same products, different winners.
- Why no production response: small marginal incentive, costs of adding tracks, album as an artistic unit. Note the suggestive upper-tail and shorter-songs patterns.
- Formula design: whether streams count vs how they are counted. U.S.-only effects in the UK comparison and in Part 2b point to formula details (track caps, down-weighting) as a policy lever. This is interpretation, not a tested result.
- Welfare and attention: entry barriers for new releases; implications for discovery and for labels' release strategies.
- **Limitations:**
  - one country's rule, with the UK as a partial comparison;
  - no sales-only control chart;
  - genre labels from MusicBrainz tags;
  - pre-rule roster (no newcomers in Part 1);
  - selection into the matched sample;
  - annual RIAA data.

## 8. Conclusion (1 page)

## Methods-section text required by JCE

- **LLM use:** draft in `docs/llm_use_log.md` ("Draft wording for the Methods section"). Update it to cover the full set of sessions.
- **Pre-registration-style plans:** list the plan files and dates; dated deviation notes; the superseded-results disclosure (three implementation bugs found and fixed before submission; `test_registry.md`, "Superseded estimates").

## Online appendix

- **A. Test registry** (from `test_registry.md`): every test, status, plan and result.
- **B. Data construction:** roster, MusicBrainz matching, edition rule, genre rule (`docs/genre_classification.md`), hand checks.
- **C. Part 1 robustness:**
  - full table of the 12 frozen-plan checks;
  - long-albums follow-up (Fig. A1);
  - selection and payoff;
  - exploratory checks;
  - rock + pop.
- **D. Part 2 robustness:**
  - placebo dates and distribution (Fig. A2);
  - song charts;
  - July 2018;
  - first-run lengths;
  - pooled U.S.-UK;
  - matched catalogue gap (Fig. A3);
  - RIAA controls.
- **E. Part 2b robustness:**
  - leave-one-genre-out (Fig. A4);
  - SE choice for artist FE;
  - cross-country tests;
  - UK replication.
- **F. Superseded estimates and implementation fixes.**
- **G. Replication:** `py -3.10 code/run_pipeline.py` reproduces every number from cached raw data (about 3.5 hours, mostly bootstraps).

## Writing checklist

- [ ] Use the four core claims as section openers.
- [ ] Every number from `parameters.md`; regenerate it before final submission (`run_pipeline.py --only 33`).
- [ ] Each table note gives the test status code and plan.
- [ ] State the Part 2b caveats in the main text, not only in the appendix.
- [ ] Verify every citation (PROJECT_CONTEXT §12; check the Lech et al. year).
- [ ] Update `docs/llm_use_log.md` and the Methods LLM paragraph.
