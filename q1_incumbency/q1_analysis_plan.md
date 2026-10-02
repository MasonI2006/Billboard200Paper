# Question 1 plan: did counting streams lock older albums onto the Billboard 200?

Written 2026-09-28 before running any estimates. Already seen beforehand: yearly averages of the
new-entry share and the 52+-week share (shown to the user in the previous step).

## Question
Did the Billboard 200 switch to counting streams (chart dated Dec 13, 2014; stored in the Kaggle
file as 2014-12-10) make the chart "stickier": fewer new albums entering and more slots held by
albums that have been on the chart a long time?

## Data and window
- Kaggle `billboard200.csv`, weekly, 200 rows per week.
- Main window: charts stored 2010-01-06 to 2019-12-25. Starts after Billboard let catalog albums onto
  the Billboard 200 (chart dated Dec 5, 2009), and ends before video streams were added (Jan 2020).
- Secondary window: 2010-2024.

## Outcomes (weekly)
Primary:
1. New-entry share: share of the 200 slots held by albums in their first-ever chart week.
2. Long-runner share: share of slots held by albums with 52+ weeks on the chart.

Secondary: re-entry share; artist concentration (Herfindahl index of slots by artist); first-run
length of newly debuting albums (album-level).

## Tests
A. **Break at the rule (main test).** Weekly regression of each primary outcome on a linear time
   trend, a post-rule level shift, a post-rule change in trend, and week-of-year dummies (holiday
   seasonality). Newey-West standard errors with 12 lags. Headline quantity: the level shift, plus
   the trend change.
B. **Placebo dates.** Rerun A with fake rule dates in early December 2011, 2012, 2016 and 2017. If
   breaks of similar size show up at fake dates, the real break is not distinctive.
C. **Song charts as a comparison.** The streaming, sales and radio song charts did not change how
   they count in December 2014. Run test A for the new-entry share on each (Jan 2013 - Dec 2019).
   A break on the Billboard 200 but not on these would point to the counting rule rather than
   general growth in streaming. (The long-runner share is not compared, because Billboard song
   charts remove old songs under "recurrent" rules.)
D. **July 2018 paid/free weighting** as a second, secondary break (added to A).

Report all results, including nulls. Do not add or swap outcomes or tests after seeing results.
