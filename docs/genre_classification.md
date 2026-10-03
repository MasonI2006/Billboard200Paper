# Genre classification: the ordered rule

Adopted 2026-10-02. Applies to every analysis that uses MusicBrainz artist genres: the Part 1 headline and its secondary checks, the validation tables, and Part 2b (which takes its labels from `data/final/analysis_sample.csv`). Code: `GENRE_PRIORITY` and `infer_row_genre()` in `code/musicbrainz_helpers.py`.

## 1. How an artist gets a genre

1. Take the artist's MusicBrainz record (the resolved artist ID) from the cached artist search, and join its disambiguation text and all of its tags.
2. Find every genre whose keywords appear in that text (substring match, case-insensitive):

   | Genre | Keywords | Group |
   |---|---|---|
   | latin | latin, reggaeton, salsa, corrido, banda, cumbia | streaming-heavy |
   | hiphop_rnb | hip hop, hip-hop, rap, r&b, soul, grime, trap | streaming-heavy |
   | country | country, americana, bluegrass, red dirt | other |
   | christian | christian, gospel, worship, ccm | other |
   | jazz | jazz, bossa, swing | other |
   | classical | classical, orchestral, opera, chamber | other |
   | electronic | electronic, edm, house, techno, dubstep, trance | streaming-heavy |
   | rock | rock, metal, punk, emo, grunge, indie, alternative | other |
   | pop | pop, dance-pop, dance pop, synth-pop, electropop | streaming-heavy |

3. **If exactly one genre matches**, that is the artist's genre.
4. **If several match, the ordered rule decides:** go down the list in the order shown above (latin → hip-hop/R&B → country → Christian → jazz → classical → electronic → rock → pop) and take the first genre that matched.
5. If nothing matches, the artist has no genre, and their albums are excluded from the headline regression (as the frozen plan requires).

An album takes the genre of the first credited roster artist who has one. Streaming-heavy means a 2014 Nielsen streaming-to-sales ratio of at least 1.9 (`docs/analysis_plan.md`).

## 2. Why this order

**The rule was not chosen now.** The same order already existed before any MusicBrainz result was seen: in the project's Spotify classification (`GENRE_RULES` in `code/load_clean_data.py`, 2026-09-27) and in the hand-check script's `proposed_group()` (`code/15_prepare_genre_handcheck.py`). The frozen plan says to "use the existing ordered Spotify-genre keyword classification". Adopting it brings the analysis in line with the plan and with the labels that were actually audited. It is not a specification picked after seeing results.

**The principle is that specific beats broad.** A genre word that says a lot about an artist's audience, market and sales channel goes ahead of one that gets attached to almost anything.

- **Pop is last.** It is the vaguest tag. It appears inside pop rock, pop punk, country pop, latin pop, pop rap and K-pop. If pop won ties, it would absorb artists whose market is elsewhere. Artists tagged *only* with pop still get pop.
- **Rock is second-to-last**, for the same reason in milder form. Its keywords include broad descriptors such as "indie" and "alternative".
- **Latin is first.** For Latin artists, language and audience define the market whatever the style: an artist tagged reggaeton, trap and pop is a Latin-market act. Latin is also its own category in the Nielsen ratios that define streaming intensity.
- **Hip-hop/R&B is second.** "Pop rap" and "R&B/pop" acts are hip-hop/R&B acts in industry terms.
- **Country, Christian, jazz and classical come before electronic, rock and pop.** They mark distinct fan communities and sales channels (country radio, Christian retail, classical charts). A "country pop" act is marketed as country, and a "Christian rock" act sells through Christian channels.
- **Electronic comes after the niche genres but before rock and pop.** Clearly electronic tags (EDM, house, techno, dubstep, trance) identify an electronic act. Hybrid pop tags like "dance-pop" and "electropop" are pop keywords, so they don't trigger electronic.

**It does not favour either group.** Streaming-heavy genres sit at the top (latin, hip-hop/R&B) and at positions 7 and 9 (electronic, pop). Pop-rap goes to the streaming-heavy side; pop-rock and country-pop go to "other". The direction of any effect on the headline could not be predicted from the order.

## 3. What the rule decides in practice

Of the 2,451 artists with a genre, **1,135 have tags matching more than one genre** (705 match two, 311 three, 120 four or more). For 866 of them the candidate genres span both groups, so the rule decides whether they count as streaming-heavy. The most common two-genre cases:

| Matched genres | Count | Rule assigns |
|---|---|---|
| rock + pop | 326 | rock (other) |
| hip-hop/R&B + pop | 69 | hip-hop/R&B |
| country + rock | 56 | country |
| Christian + rock | 45 | Christian |
| hip-hop/R&B + rock | 37 | hip-hop/R&B |
| country + pop | 27 | country |
| electronic + rock | 23 | electronic |
| electronic + pop | 18 | electronic |
| latin + pop | 17 | latin |

**Effect on the genre clusters in the Part 1 headline sample.** The corrected sample (6,775 albums, after the release-date fix in devlog §25) is the current one. The 1,663-album columns are the superseded year-only sample, kept for the record.

| Genre | Albums, corrected sample | Artists, corrected sample | Albums, year-only sample, ordered rule | Albums, year-only sample, 09-28 random draw |
|---|---|---|---|---|
| rock | 2,286 | 605 | 593 | 353 |
| hip-hop/R&B | 1,797 | 450 | 340 | 82 |
| country | 931 | 210 | 249 | 118 |
| Christian | 488 | 116 | 81 | 87 |
| electronic | 362 | 109 | 94 | 30 |
| latin | 274 | 59 | 96 | 42 |
| classical | 253 | 54 | 86 | 33 |
| jazz | 231 | 55 | 82 | 53 |
| pop | 153 | 32 | 42 | 865 |

Because pop is last, it keeps only artists tagged with pop and nothing else, so it is the smallest of the 9 bootstrap clusters. The streaming-heavy group is led by hip-hop/R&B rather than pop. In the 09-28 draw, pop happened to win many ties and held more than half the sample.

**Judgement calls to be aware of:**
- **Rock + pop → rock is the decision that matters most** (326 artists). Many "pop rock" acts are mainstream radio acts, and you could argue they belong with pop. The rule follows the specific-beats-broad principle (pop is the catch-all), but because this is the largest group the rule decides, a robustness check that sends rock + pop to pop would be informative. That check is not in the frozen plan; it was run as an exploratory check (plan: `docs/part1_secondary_rerun_plan.md` §D; results in §6 below). **It matters for Part 2b**: sending rock + pop to pop leaves Part 1 null but raises Part 2b's genre bootstrap p from 0.015 to 0.174.
- "Indie pop" becomes rock, because "indie" is a rock keyword.
- Keyword matching is by substring, so "rap" also matches inside words such as "trap" (already a hip-hop keyword) and "soul" counts as R&B.

**Alternative considered:** let the tag with the most MusicBrainz user votes win. It is arguably more data-driven, but it is not what the plan specifies, and votes are sparse for smaller artists. It is a candidate robustness check, not the headline rule.

## 4. Why the rule was needed (bug found 2026-10-02)

The previous code returned `next(iter(genre_set))` when several genres matched. Python sets have no fixed order for strings: the order depends on a hash seed that Python randomises every time a script starts. Each run therefore assigned the 1,135 multi-genre artists at random. Rerunning the same code on the same data under four fixed hash seeds gave 766, 1,267, 1,244 and 1,032 streaming-heavy artists (out of 2,451), with 930–1,190 artists changing genre between runs.

Consequences:
- The headline reported on 2026-09-28 (+0.0356, Webb p = 0.247) came from one random draw of labels. The cleanup rerun on 2026-10-02 drew another (−0.0148, Webb p = 0.624). Neither is a valid estimate, and both are superseded.
- Part 2b (+2.48 weeks, bootstrap p = 0.055) inherited the 09-28 draw through `analysis_sample.csv` and is superseded too.
- The genre hand-check (0/100 clear errors) was **not** affected. It labelled albums with the ordered rule all along (`proposed_group()`), so it audited the rule now adopted.

The labels are now deterministic: five runs under different hash seeds give identical labels (903 streaming-heavy, 1,548 other).

## 5. Validation before the regression was rerun

The frozen plan requires the genre hand-check before any regression on the labels. The existing 100-album hand-check sheet (`results/part1_album_length/validation/genre_handcheck_sample_100.csv`, seed 20260928) was compared with the new labels before rerunning:
- 91 of the 100 albums get a genre from the new rule; the other 9 have no usable tags and stay excluded.
- **91/91 agree** with the audited streaming-heavy/other group (`handcheck_group`, which includes the 10 manual corrections).
- For comparison, the old 09-28 labels agreed on 3 of the 5 hand-checked albums that were also in the headline sample.

Because the audit already used the ordered rule and agrees fully with the new labels, it was not redone.

## 6. Results under the ordered rule

Full cache-only pipeline reruns on 2026-10-02. The **current** column uses the corrected release-date parsing (devlog §25). The two superseded columns are kept for the record: the 09-28 random labels, and the ordered rule on the year-only sample (devlog §24). Genre labels are byte-identical when rerun under a different hash seed.

| Estimate | 09-28: random labels, year-only sample (superseded) | Ordered rule, year-only sample (superseded) | **Ordered rule, corrected sample (current)** |
|---|---|---|---|
| Labelled artists: streaming-heavy / other | random (766–1,267 heavy) | 903 / 1,548 | 903 / 1,548 |
| **Part 1 headline**: post × heavy on log tracks | +0.0356, SE 0.0289, p = 0.218, Webb p = 0.247 (1,663 albums) | −0.0247, SE 0.0291, p = 0.397, Webb p = 0.434 (1,663 albums) | **+0.0228, SE 0.0151, p = 0.133, Webb p = 0.161** (6,775 albums, 1,942 artists; artist clusters fixed 2026-10-03, devlog §26) |
| Part 1 albums: heavy / other | — | 572 / 1,091 | 2,586 / 4,189 |
| Part 1 digital-edition alternate outcome | — | −0.066, p = 0.026 | +0.020, p = 0.240 |
| **Part 2b**: post × heavy on weeks in first 52 | +2.48, p = 0.008, bootstrap p = 0.055 (2,807 albums) | +3.03, p = 0.012, bootstrap p = 0.001 (2,807 albums) | **+3.23, SE 0.90, p < 0.001, genre bootstrap p = 0.015** (4,517 albums, 1,800 artists) |
| Part 2b weeks in first 26 | +1.51, bootstrap p = 0.056 | +1.68, bootstrap p = 0.013 | +1.78, bootstrap p = 0.007 |
| Part 2b with debut-rank controls | +1.28, p = 0.09 | +2.39, p = 0.011 | +2.59, p < 0.001 |
| Part 2b with artist fixed effects | −0.23, p = 0.83 | +1.93, p = 0.16 | +1.73, p = 0.10 |
| Part 2b joint pre-2014 event-study test | p = 0.88 | p = 0.47 | p = 0.79 |

**Exploratory sensitivity, rock + pop → pop** (rock and pop swapped in the priority order; 918 albums move from rock to pop; corrected sample):

| Estimate | Ordered rule (reported) | Variant: pop before rock (exploratory) |
|---|---|---|
| Part 1 headline | +0.0228, Webb p = 0.161 | +0.0159, p = 0.233, Webb p = 0.288 |
| Part 2b weeks in first 52 | +3.23, p < 0.001, bootstrap p = 0.015 | +2.45, p = 0.001, bootstrap p = 0.174 |

Part 1 is a null result under every labelling. Part 2b is positive and conventionally significant under both rules, but its genre-level bootstrap significance depends on the rock + pop decision, so the sensitivity check must be reported alongside it. The ordered rule stays the reported one because it was fixed before these results were seen.
