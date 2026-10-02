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
