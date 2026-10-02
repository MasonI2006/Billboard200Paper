# Chart Rules and Album Padding in the Streaming Era

**Goal:** an economics paper for the *Journal of Cultural Economics*.
**Status:** Weekly chart data (Kaggle) and a Spotify sample with songs-per-album and genres are in hand. Preliminary results are promising but not yet conclusive (see "Preliminary results"). Main open issue: separating a real change in album length from a change in which albums make the chart.

---

## The idea in one paragraph

Until late 2014, Billboard's main album chart (the Billboard 200) ranked albums only by how many copies they sold. Starting with the chart dated **December 13, 2014**, it began counting streams too: **1,500 song streams from an album count as one album sale**, and so do 10 song downloads. The catch is that streams of *every* song on the album count. So each extra song is another source of chart points. This project asks whether artists and labels responded by making albums longer, whether the extra songs were filler, and whether the longer albums actually charted better.

## The research questions

1. **Did albums get longer because of the rule?** More songs, longer running time.
2. **Did padding water down the songs?** Did each song on a longer album get less attention?
3. **Did it work?** Did longer albums chart higher or stay on the chart longer after the rule?

## Why this isn't obvious

Albums might have been getting longer anyway. Streaming was taking over, hip-hop was booming, and tastes change. Economic theory actually predicted the opposite: that streaming would push artists toward fewer, better songs. So we can't just show that albums got longer after 2014. We need to show the rule caused it.

## How we tell cause from coincidence

**Main comparison.** The rule didn't matter equally for every genre. Fans of some genres (hip-hop/R&B, pop, Latin, electronic) already streamed a lot compared with how many albums they bought. Fans of others (rock, country, Christian, jazz, classical) still mostly bought albums. An extra song was worth a lot of chart points in the first group and very little in the second. So we compare album lengths in heavy-streaming genres versus light-streaming genres, before versus after 2014. If the rule mattered, the gap should open up after 2014 and not before.

Important: the right measure of "heavy-streaming" is how much a genre's fans stream *relative to how many albums they buy*, not the genre's total share of all streams. Rock had a big share of streams in 2014 simply because rock is big, but its fans still mostly bought albums.

**Timing.** Albums are planned months ahead, so any effect should build up gradually over 2015–2016 rather than appear overnight.

**Supporting comparison: the UK.** The UK album chart has always counted only an album's **12 most-streamed songs** (since it added streaming in March 2015). A 13th song earns nothing there but earns full credit in the US. If the story is right, artists who mainly care about the UK chart should tend to stop at 12 songs, while US-focused artists shouldn't. Germany and Australia have similar caps.

## Other rule changes to keep in mind

These happened later and could muddy the results, so the main analysis focuses on **2010–2019**, with later years as a check.

- **July 2018:** paid-subscription streams started counting more than free, ad-supported streams.
- **January 2020:** music video plays (including YouTube) started counting, and rules on albums sold bundled with merchandise or concert tickets were tightened, then largely eliminated later in 2020.
- **January 2026:** the stream thresholds changed again (outside our window).

---

## Data we need

**Already have (Kaggle Billboard charts, weekly, through Sept 2026)**

- Billboard 200 albums, top 200 each week (from 1963).
- Hot 100 songs, top 100 each week (from 1958).
- Streaming songs chart, top 50 each week (from Jan 2013).
- Digital song sales chart, top 50 each week (from 2004).
- Radio songs chart, top 50 each week (from 1990).

Each file has: date, title, artist, rank, last week's rank, peak position, weeks on chart. Two quirks: chart dates are stored as the **Wednesday** before Billboard's official Saturday date (so the first chart under the new rule, Dec 13, 2014, appears as **Dec 10, 2014**), and on the album chart the album title is in the column called `Song`.

**Spotify sample (2009–2025).** About 8,800 tracks from about 5,300 albums, with songs per album, release date, album type (album/single/compilation), artist genres, and current Spotify popularity scores (0–100). After removing singles, compilations, soundtracks and deluxe/anniversary/"version" re-releases, about 1,500 studio albums from 2009–2024 remain; about 700 have a usable genre, and about 500 of those match an album that debuted on the Billboard 200. Caveats: it is a sample, not every album; song counts are for the version on Spotify today, which may be a deluxe edition; popularity is measured now, not at release.

**Still needed (the core question depends on these)**

1. **Album length for the full set of albums, not just a sample:** number of songs and running time of the **original standard edition** for (a) every album that debuted on the Billboard 200 and (b) ideally, all major studio albums released each year whether or not they charted. Part (b) is what lets us rule out the chart-selection problem described below.
2. **Genre** for every album in that set (the Spotify sample covers only part of it).
3. **How streaming-heavy each genre was before the rule** (around 2014): each genre's share of streams compared with its share of album sales. Already found for 2014: electronic 3.4, Latin 2.1, hip-hop/R&B 2.1, pop 2.0, rock 0.7, country 0.5, Christian 0.4, jazz 0.15, classical 0.14 (streams share ÷ album-sales share).

**Nice to have**

4. **Deluxe editions:** whether and when a longer version came out after the original.
5. Whether the label is a major (Universal, Sony, Warner) or independent.
6. The artist's home country (for the UK comparison), and UK album chart data if available.

**What to leave out of the main sample:** compilations, greatest-hits albums, soundtracks, live albums, holiday albums and reissues.

---

## Preliminary results

Code: `kaggle_analysis.py` and `spotify_analysis.py` / `spotify_part2-5.py`. Tables: `kaggle_results/`. "Streaming-heavy genres" = hip-hop/R&B, pop, Latin, electronic (2014 intensity ≈ 2 or more); "other" = rock, country, Christian, jazz, classical.

**Did albums get longer? (Spotify sample matched to Billboard 200 debuts, about 500 albums)**

| | Other genres | Streaming-heavy genres |
|---|---|---|
| Avg. songs, before rule | 13.8 | 13.2 |
| Avg. songs, after rule | 13.2 | 15.2 |
| Share with more than 12 songs, before → after | 49% → 50% | 48% → 72% |
| Share with 18+ songs, before → after | 10% → 5% | 8% → 27% |

- Streaming-heavy albums gained about **2 songs (≈13%) relative to other genres** after the rule. Albums over 12 songs rose about 20 percentage points more, and albums with 18+ songs about 14 points more.
- **Before the rule, the two groups moved together** (no difference in 2009–2014; statistical test of equal pre-trends p ≈ 0.9). The gap opens from 2016 and is largest around 2018–2022, which fits a delayed response (albums are planned months ahead).
- The result holds with the continuous genre-intensity score, without electronic, and for 2010–2019 only (p between 0.01 and 0.04). It is weaker with only about 9 genre groups to compare (bootstrap p ≈ 0.06) and not significant when comparing the same artist's albums before and after (fewer such pairs).

**The big caveat: which albums make the chart.** In the full Spotify sample (charting and non-charting albums together), there is **no** clear effect, and among albums that never charted it is roughly zero. There are two readings:
1. The rule only mattered for albums with a real shot at the chart, so the effect shows up only there (supports the story).
2. After the rule, long albums from streaming-heavy genres were simply *more likely to reach* the Billboard 200, because extra songs add chart points. Then the chart sample fills up with long albums even if artists didn't change anything (a selection effect, not a production change).

Telling these apart is now the most important task. It needs album lengths for all notable releases, not just charting ones (see steps).

**Consumption side (Kaggle charts)**

- **Album bombs:** for top-10 album debuts, songs debuting on the Hot 100 the same week rose from about 0.1–0.3 (2010–2014) to about 3.4 (2021–2024). On the streaming chart: 0.04 → 2.4. On the sales chart: much smaller rise. On the radio chart: near zero throughout (a useful placebo).
- **Suggestive filler signal:** of those same-week Hot 100 debuts, the share that lasted only one week rose from about 25–35% (2012–2014) to 50–68% (2018–2021). The pre-rule baseline is noisy.
- **Artist-level streaming exposure** (pre-rule share of an artist's song-chart weeks on the streaming vs. sales chart) predicts bigger album bombs after the rule, but only borderline (p ≈ 0.06), and it does not predict longer albums in the Spotify sample (about 250 albums).
- **No sign the chart payoff to bombing changed** after the rule.

**Watered-down songs (Spotify popularity):** inconclusive. Songs later in an album are less popular, as expected, but the before/after pattern by genre is mixed and hard to interpret, because the sampled songs are probably not a random draw from each album and popularity is measured today.

**Sample note:** new albums entering the Billboard 200 each year fell from about 1,250 (2014) to about 390 (2024), as streaming keeps older albums on the chart.

---

## The steps, in order

1. ~~Collect weekly charts.~~ **Done** (Kaggle). Remember dates are stored three days early (Dec 13, 2014 appears as Dec 10) and the album title is in the `Song` column.
2. ~~First look at album length by genre.~~ **Done on a sample** (Spotify, about 500 charting albums). Result is promising; see above.
3. **Build the full album list (top priority).** All notable studio albums released 2009–2024, *whether or not they charted*, with standard-edition song count, running time, release date, genre and label. Mark which ones debuted on the Billboard 200.
4. **Check song counts are for the original standard edition,** not a later deluxe version. Compare against the Spotify counts on a subsample.
5. **Rerun the main comparison on the full list** (streaming-heavy vs. other genres, before vs. after). Then answer the selection question two ways:
   - Does the effect appear among *all* releases, not just charting ones? If yes, it's a real production change.
   - Did long albums become more likely to reach the chart after the rule? That is itself a result (it is the payoff), but it has to be kept separate from the production effect.
6. **Year-by-year check:** confirm the groups moved together before 2014 on the full list.
7. **Watered-down songs:** use the song charts. What share of an album's songs chart in its debut week, how high, and how many drop off after one week, relative to album length. Radio chart as placebo. Treat Spotify popularity only as a secondary measure.
8. **Chart payoff:** did longer albums debut higher or stay on the Billboard 200 longer after the rule than before?
9. **Stress tests:** continuous vs. two-group genre measure; with and without electronic; ending in mid-2018 (before paid/free stream weighting) and 2019 (before video counted); same-artist comparisons; the UK 12-song comparison.
10. Write up, keeping the main specification fixed in advance to avoid picking the version that works best.

## What the paper will show

- **Figure 1:** average songs per album by year, heavy- vs. light-streaming genres.
- **Figure 2:** year-by-year difference between the two groups (should be flat before 2014 and rise after).
- **Figure 3:** how many songs albums have, before vs. after, with a marker at 12 songs.
- **Figure 4 (motivation, already possible):** songs debuting the same week as their album on the streaming, sales and radio charts, by year.
- **Tables:** summary statistics; main results; watered-down songs; chart payoff; robustness checks.

---

## Notes for the write-up

- Journal of Cultural Economics: maximum 30 pages including tables and figures; abstract of 150–250 words; 4–6 keywords.
- The journal asks authors to say where AI tools were used, so keep a short log as you go.
- Only cite papers that have been checked and confirmed to exist. Key related work: Zanella et al. (2021, *Strategic Management Journal*) on how labels responded when streaming entered the Hot 100 singles chart (closest paper; ours differs by studying album length under the album chart rule); Hiller & Walter (2017, *Review of Network Economics*), the theory predicting fewer, better songs; Elberse (2010, *Journal of Marketing*) on unbundling of albums.
