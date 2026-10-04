# Plan: same album, two charts — U.S. vs UK matched-album tests, UK replication of Part 2b, RIAA control

Written 2026-10-03, **before any estimation** (CLAUDE.md rule 6). Awaiting the author's approval. Nothing here changes the frozen Part 1 plan, the Part 2 plan or the Part 2b plan. Every result is reported, including nulls.

**What has already been seen.** The aggregate UK weekly series and the tests in `docs/uk_comparison_plan.md` (devlog §31): no significant UK break at its own date, a flat UK new-entry share, and a rising UK 52+-week share. Everything below is new: album-matched comparisons, the genre triple difference, the UK version of Part 2b, and the RIAA control. None has been estimated. The only thing computed so far is a feasibility count: about 2,500 albums appear on both charts in 2009–2019 (title and artist match, allowing for truncated UK names).

## Why

Part 2 cannot separate "the chart changed" from "the albums changed". An album that charts in both countries carries the same quality, promotion, release date and artist fame into both charts, so the **difference between its U.S. and UK chart runs** removes all of that. Three periods give different rule contrasts:

| Period | U.S. counts streams | UK counts streams | Contrast |
|---|---|---|---|
| Before 2014-12-13 (U.S. issue date) | no | no | baseline |
| 2014-12-13 to 2015-02-28 (12 weeks) | yes | no | **inclusion of streams** |
| From 2015-03-01 | yes (no track cap, 1,500:1) | yes (12-track cap, top two down-weighted, 1,000:1) | **formula details** |

Two hypotheses make different predictions for the U.S.-minus-UK gap in catalogue albums' chart presence:
- **H-inclusion:** what matters is whether streams count at all. The gap jumps at December 2014 and closes again from March 2015, when the UK catches up.
- **H-formula:** the details of the formula matter. The gap jumps at December 2014 and persists after March 2015. The flat UK new-entry share seen in §31 hints at this, which is why both are tested.

## Data and matching

- **U.S.:** Billboard 200 (`data/raw/billboard200.csv`; album title is in `Song`). Stored dates are mapped to the issue date (stored + 3 days). The U.S. week is aligned to the UK chart week (Sunday start) that contains the Billboard issue date.
  - Alignment is approximate (±1 week of tracking period), stated as a limitation.
- **UK:** `data/final/uk_albums_weekly.csv` (step 28, #1 rows rebuilt).
- **Chart size:** to compare like with like, U.S. outcomes use **positions 1–100** only. The full Billboard 200 is a secondary version.
- **Matching rule (fixed now):**
  1. Normalise titles and artists: ASCII-fold, lowercase, "&" to "and", keep letters, digits and spaces.
  2. A U.S. and a UK album match if their titles are equal, or one is a prefix of the other where the UK title is at its 40-character cap; **and** the artists are equal, or one is a prefix of the other (UK artist names are cut at about 30 characters, and U.S. credits add "featuring …" or "and the …").
  3. Ambiguous matches (one album matching several on the other chart) are dropped.
  4. Matching uses all weeks 2000–2025, so the matched universe does not depend on the analysis window.
  5. The match rate and 50 random matches are written out for a hand check, reported before the results.
- **Debut:** first week on each chart (top 100). Album-level tests (B, C) keep albums whose U.S. and UK debuts are within 8 weeks of each other, i.e. simultaneous releases.
- **Genre labels:** the Part 2b labels (`data/final/part2b_album_runs.csv`, Part 1-sample labels via the U.S. artist's MusicBrainz match), so they are identical to Part 2b. The per-artist file (`data/final/artist_genres.csv`) is a secondary version.

## A. Catalogue albums: weekly U.S.-minus-UK gap (main test for Part 2)

- **Panel:** matched albums × aligned weeks, 2010–2019.
- **Catalogue rows:** album-weeks where the album is at least 52 weeks past its first debut on either chart.
- **Outcome:** `D_t` = mean over catalogue matched albums of [in U.S. top 100 in week t] − [in UK top 100 in week t]. The album's own demand cancels within the week.
- **Model:** `D_t = a + b*t + tau1*1[t >= Dec 2014] + tau2*1[t >= Mar 2015] + week-of-year FE + e_t`, Newey–West (12 lags).
- **Predictions:**
  - **tau1 > 0:** U.S. catalogue advantage appears when only the U.S. counts streams.
  - **tau2:** negative and of similar size under H-inclusion; about zero under H-formula.
- **Inference:** Newey–West p, plus a placebo-rank p for tau1. Re-estimate the jump at every fake date from 2011 to 2018, excluding 26 weeks around both true dates, as in §31. **The placebo-rank p is used for interpretation.**
- **Secondary:** the same with trend changes at both dates; and with the full Billboard 200 for the U.S. side.

## B. New releases: album-level U.S.-minus-UK first-year runs

- **Sample:** matched simultaneous releases debuting 2010-01 to 2018-12, so each has a full 52-week follow-up.
- **Outcome:** `diff_a` = weeks in the U.S. top 100 within 52 weeks of U.S. debut, minus weeks in the UK top 100 within 52 weeks of UK debut.
- **Model:** `diff_a = a + b*t_debut + tau1*1[debut >= Dec 2014] + tau2*1[debut >= Mar 2015] + month-of-year FE + e`, artist-clustered SEs.
- **Note:** albums debuting December 2014 to February 2015 had only part of their first year under the U.S.-only contrast, so tau1 is weak for this outcome. B is secondary to A.

## C. Part 2b cross-country: do streaming-heavy albums gain more in the U.S. than on the UK chart? (main test for Part 2b)

- **Sample:** B's sample with a genre label.
- **Model:** `diff_a = heavy x post_US + heavy x post_UK + C(genre) + C(debut year) + e`, where post_US = debut ≥ Dec 2014 and post_UK = debut ≥ Mar 2015.
- **Inference:** artist-clustered SEs; genre-level Webb wild bootstrap (9,999 draws, seed 20260928, `code/inference.py`) for the heavy × post_US term.
- **Reading:**
  - heavy × post_US > 0: the Part 2b effect survives holding the album fixed across charts.
  - The sign of heavy × post_UK distinguishes H-inclusion (negative: UK catches up) from H-formula (about zero).

## D. UK replication of Part 2b

- **Sample:** UK albums debuting 2010-01 to 2018-12, by artists with a genre label.
  - The label comes from the matched U.S. album's artist where the album matches.
  - Otherwise it comes from the per-artist file by normalised name (prefix rule for truncated names; ambiguous names dropped).
- **Specification:** Part 2b, exactly. Outcome: weeks on the UK chart in the 52 weeks after debut. `weeks52 ~ post:heavy + C(genre) + C(year)`, with post = debut ≥ 2015-03-01. Artist-clustered SEs and a genre Webb bootstrap (9,999 draws).
- **Reading:**
  - A positive effect replicates Part 2b in a second market with a different date.
  - A null says the Part 2b effect is U.S.-specific, which fits H-formula and is not by itself evidence against Part 2b.

## E. RIAA streaming growth as a control in the Part 2 time series

- **Data:** annual streaming share of U.S. recorded-music revenue (`data/final/riaa_revenue_by_category.csv`), placed at mid-year and linearly interpolated to weeks.
- **Model:** the Part 2 model for the U.S. new-entry and 52+-week shares, plus that series as a regressor. Variants: with the log of streaming revenue instead; and with both.
- **Report:** tau with and without the control.
- **Reading:** if tau keeps at least half its size and stays significant, a smooth streaming trend does not explain the jump. Annual data cannot rival a weekly jump, so this is a robustness check, not a test of the mechanism.

## F. Figure (descriptive)

U.S. and UK weekly new-entry and 52+-week shares, 2010–2019, with both rule dates marked; plus `D_t` from A.

## Interpretation rules, fixed now

- **Album-level rule effect (Part 2) supported:** A's tau1 > 0 with placebo-rank p < 0.10.
- **H-inclusion vs H-formula:** decided by A's tau2.
  - tau2 < 0 with |tau2| ≥ half of tau1: H-inclusion.
  - |tau2| < half of tau1: H-formula.
  - If tau1 is not supported, the comparison is reported but not interpreted.
- **Part 2b robust to holding the album fixed:** C's heavy × post_US > 0 with genre-bootstrap p < 0.10.
- **D and E** are reported as replication and robustness; they do not change the verdicts above.
- **Multiplicity:** two main tests (A tau1, C heavy × post_US). Holm across them is reported alongside the unadjusted p-values.

## Caveats (stated now)

- **Selection into matching.** Only albums that chart in both countries enter. If the rule changes which albums chart in the U.S., the matched sample itself changes after 2014. Mitigations: matching over 2000–2025, and A's per-week design. The share of each chart's slots held by matched albums is reported by year.
- **Different album versions.** Deluxe or regional editions with different titles do not match. Same-title albums by different artists are guarded by the artist rule and the ambiguity drop.
- **Imperfect week alignment** (tracking weeks differ by a few days).
- **Unverified July 2018 UK albums-chart weighting** (devlog §31). It is not modelled, and is noted for A's post-2018 period.

## Outputs and runtime

- New scripts: `code/30_match_us_uk_albums.py` (matching and hand-check sheet) and `code/31_matched_album_tests.py` (A–F).
- Results in `results/part2_incumbency/matched/`; logged in `docs/devlog.md`; PROJECT_CONTEXT updated.
- Expected runtime: matching a few minutes; A, B, E and F a few minutes; C and D about 15–25 minutes (two 9,999-draw bootstraps).
