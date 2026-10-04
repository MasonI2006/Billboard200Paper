# Plain-language guide to the paper

This explains the whole project without jargon: what we're asking, what we're measuring, every decision and test that goes in the paper, and why. Technical terms are explained when they first appear, and there's a glossary at the end. Exact numbers are in `parameters.md`; the formal list of tests is in `test_registry.md`.

---

## 1. The big picture in one paragraph

Billboard's album chart (the Billboard 200) used to rank albums purely by **sales**. Starting with the chart dated **13 December 2014**, Billboard also began counting **streams** (Spotify, Apple Music and so on): roughly 1,500 song streams count as one album sold. That's a change to the *scoreboard* of the music industry, and it happened on a known date. We use it to ask two things. Did artists change **what they make** to score better? And did the chart start rewarding **different albums**? The short answers: artists didn't noticeably change their albums, but the chart did start rewarding older, long-running albums over new releases, and that change seems to come from Billboard's rule specifically, not from the general rise of streaming.

---

## 2. The research questions

**Part 1: production.** *Did counting streams make artists release longer albums?*
Why it might: under the new rule, every song on an album that gets streamed adds to the album's chart score. More songs mean more chances to be streamed, so there's an incentive to "pad" albums with extra tracks. The incentive should be strongest in genres whose fans stream a lot (hip-hop, pop, Latin, electronic).

**Part 2: chart rewards.** *Did counting streams change which albums the chart rewards?*
Why it might: people buy an album once, usually soon after release, but they keep streaming old favourites for years. Counting streams should therefore help older albums stay on the chart and make it harder for new albums to break in.

**Part 2b: who benefits.** *Did albums in streaming-heavy genres gain more chart staying power than others?*
If streaming drove the Part 2 change, the effect should be biggest where fans stream the most.

**The economics angle.** Rankings run lots of markets (bestseller lists, app stores, playlists, university rankings). This paper is a clean case study of what happens when a ranking's formula changes: producers might change their products, or the ranking might simply reward different products. We find mostly the second.

---

## 3. The parameters we're estimating (what each number means)

A "parameter" is the single number that answers the question. Each part has one main parameter.

**Part 1: the "extra length" number.**
- *Plain meaning:* how much longer albums in streaming-heavy genres became after the rule, **compared with** albums in other genres over the same period.
- *How it's measured:* the change in the (log) number of tracks. A value of +0.02 means roughly 2% longer, which is about a quarter of a track on a typical 13-track album.
- *Our estimate:* **+0.023** (about +0.3 tracks), and **not statistically significant**. We can't tell it apart from zero.
- *Why "compared with other genres":* lots of things changed for all albums around 2014 (industry trends, tastes). Comparing the two groups cancels out whatever affected everyone. Only the extra change in streaming-heavy genres is attributed to the rule. This is called **difference-in-differences**.

**Part 2: the two "jump" numbers.**
- *Plain meaning:* how much the chart's make-up changed **immediately** when the rule started, beyond what the existing trend would predict.
- *Two measures, both weekly:*
  1. **New-entry share:** the fraction of the 200 chart spots held by albums in their first-ever week on the chart. Our estimate: it **dropped 2.6 percentage points** at the rule, from an average of 10.8%, about a quarter fewer.
  2. **Long-runner share:** the fraction held by albums with 52+ weeks on the chart. Our estimate: it **jumped 5.7 points**, from 22.1%.
- *Why "immediately":* streaming was growing every year, so a gradual change could be streaming's general growth. A sudden jump exactly on the rule date is much harder to explain any other way.

**Part 2b: the "extra staying power" number.**
- *Plain meaning:* how many more weeks (out of an album's first year) streaming-heavy albums stayed on the chart after the rule, compared with other albums.
- *Our estimate:* **+3.2 weeks**, statistically significant.

---

## 4. The data and the decisions behind it

### 4.1 Chart data
- **Billboard 200, weekly** (a public Kaggle dataset). Main window **2010–2019**.
  - *Why start in 2010:* in December 2009 Billboard changed another rule (letting older "catalogue" albums onto the chart). Starting after that avoids mixing up the two changes.
  - *Why end in 2019:* in January 2020 Billboard started counting YouTube/video streams, a different change.
- **Quirk we found:** the dataset stores each chart date 3 days early (Wednesday instead of Billboard's Saturday). So the first rule chart (13 December 2014) appears as 10 December 2014. We account for that everywhere.

### 4.2 Which albums count for Part 1 (the most important design decisions)
- **Only artists who were already established before the rule.** We built a list ("roster") of artists who had albums on the Billboard 200 *before* the rule: 3,361 artist entities, of which 2,367 could be identified reliably.
  - *Why:* if we included artists who first appeared after 2014, the streaming era itself would decide who's in the sample, which biases the comparison. Using a fixed, pre-rule set of artists means we compare like with like.
- **Album data from MusicBrainz** (a large, free, community-run music database), collected through its official interface, about 1 request per second, with every response saved.
  - We took each artist's **studio albums** (no live albums, compilations or mixtapes).
  - *Why not mixtapes:* they're a different kind of release. We checked them separately as a robustness test.
- **Standard edition only.** Many albums come out in several versions (standard, deluxe, expanded). We use the **earliest official release** and, if there's a tie, the one with fewer tracks.
  - *Why:* deluxe editions add tracks for reasons unrelated to the rule, and we want the artist's core album.
- **At least 6 tracks**, so EPs and singles don't count as albums.
- **Release window 2009–2019.** Albums released on or after **24 November 2014** count as "post-rule", because their first sales week would land on the first rule chart.
- **Unclear dates:** some albums list only a year. A "2014" with no month can't be placed before or after the rule, so those are excluded. Other year-only dates are kept.
- **Result:** **6,775 albums by 1,942 artists**.

### 4.3 Genres and "streaming-heavy"
- Each artist gets one genre from MusicBrainz's genre tags, mapped to 9 groups: hip-hop/R&B, pop, Latin, electronic, rock, country, Christian, jazz, classical.
- **Streaming-heavy** = hip-hop/R&B, pop, Latin and electronic. These are the genres where, according to industry (Nielsen) data, people stream more than they buy. The others are "other".
- **Artists with several genre tags:** a fixed priority order decides (Latin first, then hip-hop/R&B, country, Christian, jazz, classical, electronic, rock, pop last).
  - *Why that order:* specific genres that define a distinct audience beat broad ones, and "pop" is the vaguest tag, so it's last. The same order was used earlier in the project before any results existed.
- **Checked by hand:** 100 random albums were inspected and the labels had no clear errors.

### 4.4 Data for the comparisons (added later)
- **UK Official Albums Chart** (top 100, weekly). The UK started counting streams on **1 March 2015**, about three months after the US, and with a different formula.
  - The file you supplied was missing the #1 album in almost every week. We rebuilt it from the next week's "last week: 1" marker, and checked it against known #1s.
- **RIAA revenue data:** yearly US music revenue by format (CDs, downloads, streaming). It shows how fast streaming was growing.
- **Albums on both charts:** we matched 4,678 albums that charted in both the US and the UK. A random 50 were checked by hand, and all were correct.

---

## 5. The tools, explained simply

- **Difference-in-differences:** compare the before/after change in one group with the before/after change in a comparison group. Whatever affected both groups cancels out.
- **Fixed effects:** extra controls that soak up differences we're not interested in. "Genre fixed effects" mean rock albums are only compared with how rock albums usually look. "Year fixed effects" absorb anything that hit all albums in a given year.
- **Standard error and p-value:** the standard error says how uncertain an estimate is. The p-value asks: if the true effect were zero, how often would we see an estimate this large by chance? Below 0.05 is conventionally called "significant". We treat p-values as evidence, not a pass/fail switch.
- **Clustering by artist:** albums by the same artist resemble each other. Treating them as independent would make us overconfident, so the uncertainty calculation groups them.
- **Wild bootstrap at the genre level (Part 1 and 2b's strictest test):** the "treatment" (being streaming-heavy) is assigned to whole genres, and there are only 9 genres. Ordinary formulas are unreliable with so few groups. The bootstrap reruns the analysis 9,999 times on shuffled versions of the data to get an honest p-value. It's the most demanding test we use, so we report it alongside the usual one.
- **Interrupted time series (Part 2):** fit the trend before the rule and see whether the series suddenly **jumps** at the rule date. We also allow for regular seasonal patterns (the chart always fills with new releases in the autumn and Christmas albums in December).
- **Newey–West standard errors:** a version of the uncertainty calculation for weekly data, where this week's chart is naturally similar to last week's.
- **Placebo dates:** pretend the rule happened on a date when nothing changed and rerun the test. If fake dates give jumps as large as the real one, the real one isn't special. We tested about 350 fake dates.
- **Event study:** instead of one before/after comparison, estimate the gap separately for each year (or month). It shows whether a gap was already opening before the rule (a warning sign) or appears right at it.
- **Equivalence test:** a normal test asks "is the effect different from zero?" An equivalence test asks the reverse: "can we rule out effects bigger than X?" It turns a "no effect" result into "no effect bigger than X".
- **Holm correction:** when you run many tests, some come out "significant" by luck. Holm raises the bar to account for the number of tests.

---

## 6. Every test that goes in the paper, part by part

### 6.0 Ground rules we followed
- **Analysis plans written before running tests.** The Part 1 plan was approved and **frozen** on 27 September 2026. Every new set of tests got a short written plan first, saying what we'd run and how we'd read the results.
- **Every result is reported, including the ones that didn't work out.** We never tried different versions until something came out significant.
- **Deviations are recorded.** When we changed anything (a bug fix, a different standard error), it got a dated note.

### 6.1 Part 1: did albums get longer?

**Main test.** Compare album length before and after the rule, streaming-heavy vs other genres, controlling for genre and year.
- **Result:** +0.023 (about +0.3 tracks), p = 0.13; strict bootstrap p = 0.16. **No detectable effect.**
- In raw numbers: streaming-heavy albums averaged 13.99 tracks before and 14.05 after; other albums went from 12.50 to 12.18.

**What the "no effect" rules out (equivalence test).**
- We can rule out increases bigger than **about 0.63 tracks (4.9%)**.
- We had planned to check whether we could rule out half a track; we can't (p = 0.16). We report that honestly.
- In the paper: "no increase larger than about two-thirds of a track".

**Year-by-year check (event study).** The gap between the groups was flat before 2014 (test of "no pre-existing trend": p = 0.85) and didn't clearly rise after. This rules out the worry that a difference was already opening before the rule.

**Robustness checks** (the 12 extra checks listed in the frozen plan; all reported):
- **Career stage:** artists' later albums might naturally differ from their first ones, so we controlled for each album's position in the artist's career. Still null.
- **Same artist before vs after** (artist fixed effects). Still null.
- **Dropping early albums:** dropping albums released before the artist first charted. Still null.
- **Including mixtapes:** null.
- **Different windows** (2009–2024; 2010–2019): null.
- **Using each genre's actual streaming intensity instead of a yes/no group:** null.
- **Dropping electronic music:** null.
- **Running time instead of track count:** null.
- **Share of albums over 12 tracks:** null.
- **Share of albums with 18+ tracks: +4.3 percentage points, significant (bootstrap p = 0.012).**

**The 18+ track result, and why we don't promote it.**
- *Why we're cautious:* with 12 checks, about one would come out "significant" by luck alone.
- *The follow-up:* we wrote a new plan and tested five related measures (albums with 15+, 20+, 25+ tracks, and the upper end of the length distribution). Each pointed slightly positive, but **none survived the correction for multiple tests**.
- *Verdict:* "suggestive, not robust". At most, a few acts made very long (18–23 track) albums; it didn't hold up across the board.

**Smaller extras:**
- *Digital edition:* using the digital edition's track count gives the same null.
- *Selection:* did long streaming-heavy albums become more likely to chart? Borderline (p ≈ 0.06).
- *Payoff:* did longer albums do better on the chart? No clear effect.
- *Exploratory, not tests:* songs got shorter (about 4% fewer seconds per track), and fewer albums launched in several versions on the same day. Interesting, but these weren't planned, so they're footnotes.

**Genre-rule check.** If artists tagged both rock and pop are counted as pop instead of rock, the result is still null.

**Bottom line for Part 1:** artists didn't measurably lengthen their albums in response to the rule.

### 6.2 Part 2: did the chart reward different albums?

**Main test (interrupted time series).** Weekly shares of new entries and long-runners, 2010–2019, with a jump allowed at the rule date and seasonal patterns removed.
- New-entry share: **−2.6 points** at the rule (p < 0.001).
- Long-runner share: **+5.7 points** (p < 0.001).
- Over time: new entries went from 11.8% of the chart (2014) to 5.7% (2019); long-runners from 26% to 49%.

**Is the jump special? (placebo dates)**
- Out of about 350 fake dates, the real jump in new entries is bigger than all but one (**p = 0.003**).
- For long-runners it's in the top 8% (**p = 0.076**).
- An earlier check with four fake dates had found some significant "jumps" at fake dates too. That's why we built this fuller distribution and rely on it.
- *Why we focus on the jump and not the trend change:* fake dates often show significant trend changes, so trend changes aren't trustworthy here. Jumps are.

**Is it just the streaming boom? (RIAA control)** We added actual US streaming growth to the model. The jumps barely move (new entries −2.9 to −3.3; long-runners +5.0 to +5.6). Streaming grew smoothly; the chart jumped.

**The UK comparison: the strongest evidence it was the rule.**
- **Why the UK helps:** it had the same streaming boom but changed its chart three months later, with a different formula. If a general streaming shock caused the US change, the UK should show it too, at the same time.
- **UK at its own rule date (March 2015):** no significant jump.
- **UK at the US date (December 2014):** nothing.
- **Over 2014–2019:** UK new-entry share basically flat (11.5% → 10.1%) while the US share halved. Long-runners rose in both countries, gradually, but only the US shows a sudden jump at its rule.
- **A wrinkle we report honestly:** our plan's pre-written rule said "if the UK doesn't break at its own date, call it a common shock". Taken literally, that's the verdict. But the data show no shock in the UK at all, so that label doesn't fit. We report both the literal verdict and the explanation.

**Same album, two charts (matched albums).**
- **The idea:** about 2,500 older albums appear on both charts. For each one, compare its US presence with its UK presence. The album's own popularity cancels out.
- **Result:** after the US rule, these albums gained US presence relative to UK, about 6.5 more of them in the US top 100 per week (placebo p = 0.071). About half that gap closed once the UK also counted streams.
- **Why we call it fragile:** it disappears if we also allow trend changes, and after correcting for testing two main things, p = 0.14. It's supporting evidence, not a pillar.

**Event-study figure.** Monthly estimates around each rule. US: new entries step down right at the rule (after drifting *up* beforehand) and long-runners step up. UK: no step.

**Other checks:**
- *Smaller outcomes:* re-entries dipped slightly; artist concentration didn't change; new albums' first chart runs didn't get shorter.
- *2018:* Billboard's July 2018 change to stream weighting caused no further jump.
- *Song charts:* mixed results, now superseded by the UK comparison.

**Bottom line for Part 2:** the chart's make-up changed sharply at the rule, and the evidence points to Billboard's rule rather than streaming's general rise.

### 6.3 Part 2b: did streaming-heavy albums gain more?

**Main test.** For 4,517 albums that debuted 2010–2018: weeks on the chart in the first year, streaming-heavy vs other, before vs after.
- **Result: +3.2 weeks** (strict bootstrap p = 0.015).
- Raw numbers: other albums went from 6.6 to 5.2 weeks, streaming-heavy albums from 7.8 to 9.5.

**Checks that it holds:**
- *Pre-existing trend:* none (p = 0.79).
- *Controlling for how high the album debuted:* +2.6.
- *Career stage:* +3.1.
- *Broader genre list:* +3.3.
- *Same artist before vs after:* +1.7 (p = 0.034).

**Limits that must be stated in the main text:**
- **Genre classification:** counting rock+pop artists as pop drops the strict p-value to 0.17.
- **Hip-hop/R&B:** without it, the effect falls to +1.85 weeks (p = 0.10). Hip-hop/R&B carries much of it, which makes sense, since it's the most streamed genre.
- **The UK:** no such effect on the UK chart (+0.03 weeks).
- **Same album across both charts:** large but imprecise (+7.8 weeks, strict p = 0.43).

**Bottom line for Part 2b:** a real US effect, largest in hip-hop/R&B, but not a universal one. Present it as supporting evidence.

---

## 7. Decisions made after seeing results (disclosed)

- **Part 2b, same-artist standard error.** The first version used a calculation that counts each of ~1,800 artists as an extra parameter, which inflates uncertainty (p = 0.10). The standard calculation, also used in Part 1, gives p = 0.034. You chose the standard one after seeing both, so the paper reports it with the other in a footnote, and the plan has a dated note.
- **Event-study figure.** The originally planned version was mathematically broken (it produced a repeating saw-tooth pattern), so it was redrawn using the standard method. It's a figure only; no conclusion depends on it.

## 8. Bugs we found and fixed (disclose in the paper)

1. **Random genres:** artists with several genre tags got a random genre each time the code ran, a quirk of Python. Fixed with the priority order.
2. **Dates misread:** a date-parsing quirk silently threw out every album with a full release date, so the first headline used only 1,663 albums (those with year-only dates). Fixed; now 6,775.
3. **Wrong artist groups:** the code grouped albums by the first word of the artist name ("The", "Young"…) instead of the artist. This affected uncertainty calculations only, not the estimates. Fixed.

All earlier results were replaced, and the paper's appendix says so. Being upfront here helps credibility.

---

## 9. What we can and can't claim

**Can claim:**
- No measurable change in album length (nothing above ~2/3 of a track).
- A sharp, rule-timed shift toward long-running albums and away from new entries on the Billboard 200.
- Strong evidence this came from Billboard's rule, not the streaming boom: placebo dates, the RIAA control, the UK comparison, the event study.
- A US-specific staying-power gain for streaming-heavy albums, largest in hip-hop/R&B.

**Should not claim:**
- That albums got longer at the top end (the 18+ result didn't survive its follow-up).
- That the long-run rise in long-runners is all due to the rule (part of it happened in the UK too).
- That *how* streams are counted (caps, down-weighting) definitely matters. The UK evidence hints at it, but it's interpretation, not a tested result.
- Anything about artists who started after 2014 (not in the sample by design).

**Main limitations to state:**
- **One country's rule, with the UK as a partial comparison.** There's no US sales-only chart to compare with: Billboard's website blocks automated collection by AI tools, so it wasn't scraped.
- **Genre labels** come from community tags.
- **Matched albums** may change in composition after the rule.
- **The RIAA data** are yearly.

---

## 10. Questions a referee might ask, with short answers

- *"Isn't this just streaming growing?"* Streaming grew smoothly; the chart jumped on the rule date. The jump survives controlling for streaming growth, beats ~350 fake dates, and doesn't appear in the UK, which had the same streaming boom.
- *"Is your null just low power?"* No. We show what it rules out: anything above ~0.63 tracks.
- *"You ran a lot of tests. Fishing?"* Plans were written first, every test is reported, and the appendix registry lists each test's status. The one significant Part 1 check was followed up and didn't hold.
- *"Is Part 2b driven by one genre?"* Partly hip-hop/R&B, and we say so. It's positive without any single genre.
- *"Are the genre labels reliable?"* A 100-album hand check found no clear errors. Results are shown under an alternative rule too.
- *"Why only pre-2014 artists?"* Including post-rule newcomers would let the streaming era pick the sample.

---

## 11. Glossary

| Term | Meaning |
|---|---|
| Album-equivalent unit | Billboard's chart currency after 2014: one album sale, 10 track downloads, or 1,500 song streams |
| Catalogue album | An older album still selling or streaming, well after release |
| Cluster | A group of observations that are treated as related when measuring uncertainty (e.g. all albums by one artist) |
| Difference-in-differences | Comparing the before/after change of one group with that of a comparison group |
| Equivalence bound | The size of effect a "no effect" result can rule out |
| Event study | Estimating the effect separately for each period around the event |
| Fixed effects | Controls that absorb fixed differences between groups or periods |
| Holm correction | A way of raising the bar for significance when running several tests |
| Interrupted time series | Testing for a sudden break in a series at a known date |
| MusicBrainz | Free, community-run music database used for album details |
| Placebo date | A fake event date used to check that the real result is special |
| p-value | How surprising the estimate would be if the true effect were zero |
| Robustness check | Re-running the analysis a different reasonable way to see whether the answer holds |
| Streaming-heavy genres | Hip-hop/R&B, pop, Latin, electronic: genres where fans stream more than they buy |
| Wild bootstrap | Re-running the analysis thousands of times on reshuffled data to get honest p-values with few groups |
