# Question 1b plan: did albums in streaming-heavy genres gain more staying power?

Written 2026-09-28 before running estimates. Builds on question 1 (chart-wide break at Dec 2014).

## Question
After the Billboard 200 started counting streams, did albums by artists in streaming-heavy genres
(hip-hop/R&B, pop, Latin, electronic) start staying on the chart longer, relative to albums by
artists in other genres? If the counting rule drove the chart-wide shift toward long-running
albums, the effect should be largest where fans stream the most.

## Data
- `billboard200.csv` (Kaggle): album chart runs.
- `musicbrainz_artist_matches.csv`: Billboard artist credit -> MusicBrainz artist ID.
- Artist genre: the frozen genre label carried in the corrected `analysis_sample.csv`
  (the agent's genre-group file was a summary table, so per-artist labels are taken from there).
- `musicbrainz_release_groups.csv`: release dates, for album age (secondary).

## Sample
Albums by genre-labelled roster artists that debut on the Billboard 200 (first-ever chart week)
between 2010-01-06 and 2018-12-26 (stored dates), so every album has a full 52-week follow-up
before the January 2020 video change.

## Outcomes
Primary: number of weeks on the chart in the 52 weeks after debut (1-52).
Secondary: (a) still on the chart 26 weeks after debut (yes/no); (b) weeks on chart in the 26 weeks
after debut.

## Main test
Album-level regression: outcome on streaming-heavy x post-rule debut, with genre and debut-year
fixed effects. Post = debut on or after 2014-12-10 (stored date of the first rule chart).
Standard errors clustered by artist; genre-level wild cluster bootstrap p-value (Webb weights,
9,999 draws, seed 20260928), as in the main paper.

## Secondary checks
1. Add debut-rank controls (debut rank may itself be affected by the rule, so this is secondary).
2. Artist fixed effects (same artist's albums before vs after).
3. Year-by-year version (event study), reference year 2014.
4. Descriptive: share of chart slots held by albums released 3+ years earlier, by genre group, per year.

## Reporting
Report first the share of Billboard 200 debuts and chart slots that could be genre-labelled.
Report all results, including nulls. No outcome or test changes after seeing results.

## Dated note (2026-10-03): standard error for secondary check 2 (artist fixed effects)

The main test, outcomes, sample and other checks are unchanged. Label source: the reported result keeps the Part 1 sample labels named above; the per-artist genre file (`data/final/artist_genres.csv`) is reported as a robustness row only (author's decision, 2026-10-03).

Secondary check 2 was first estimated with explicit artist dummies, where statsmodels counts the ~1,800 absorbed artist effects in the clustered small-sample correction: +1.73, SE 1.05, p = 0.10. The standard treatment when fixed effects are nested in the clusters (as in `reghdfe`; Cameron and Miller) does not count them; the within-artist estimator gives the identical coefficient with SE 0.81, p = 0.034. **This change was made after both results were seen**, on the author's decision, for consistency with the Part 1 artist-FE check (which uses the within estimator) and because the dummy-count correction is a software artefact rather than a design choice. The reported row is now the within estimator; the dummy version is kept as a second row in `results_main.csv` and is to be shown in a footnote. Details in `docs/devlog.md` section 27.
