## 21. Question 1: streaming and chart incumbency on the Billboard 200 (2026-09-28)

Run outside the agent (in Claude chat) using only the Kaggle `billboard200.csv`, `streaming.csv`, `digital.csv` and `radio.csv`. Plan written before estimation: `q1_incumbency/q1_analysis_plan.md`. Script: `q1_incumbency/q1_incumbency.py`. Results: `q1_incumbency/results/`.

Verified before running: Billboard lifted catalog restrictions on the Billboard 200 with the chart dated Dec 5, 2009, so the main window starts in January 2010. It ends in December 2019 (before video counted, Jan 2020).

**Main break test (weekly, 2010-2019, linear trend + post-rule level and trend change + week-of-year dummies, Newey-West SEs, 12 lags):**

| Outcome | Pre-rule mean | Pre-rule trend | Jump at Dec 2014 | Trend change |
|---|---:|---:|---:|---:|
| New-entry share | 10.8% | +0.5 pts/yr | -2.6 pts (p < 0.001) | -1.3 pts/yr (p < 0.001) |
| Share held by albums 52+ weeks on chart | 22.1% | +1.9 pts/yr | +5.7 pts (p < 0.001) | +1.7 pts/yr (p < 0.001) |
| Re-entry share | 8.4% | +0.9 pts/yr | -1.3 pts (p = 0.024) | -1.9 pts/yr (p < 0.001) |
| Artist concentration (HHI) | 0.0099 | ~0 | ~0 (p = 0.90) | ~0 (p = 0.26) |

The 2010-2024 window gives the same picture (new-entry jump -3.2 pts; long-runner jump +5.5 pts).

**Placebo dates:** fake breaks in Dec 2011 and Dec 2012 show no drop in new entries (+1.6 and +0.7 pts) and almost no jump in long runners (+0.3, +0.7 pts). Post-rule fake dates (2016, 2017) produce some significant shifts, and trend-change terms are significant at every fake date, so nominal p-values from this model overstate certainty; the level jumps are the more reliable evidence.

**Song-chart comparison (new-entry share, 2013-2019):** no break on the streaming song chart (+2.5 pts, p = 0.39) or the sales song chart (-1.2 pts, p = 0.32); a significant drop on the radio chart (-2.3 pts, p < 0.001). Billboard 200 in the same window: -3.5 pts. Mixed.

**July 2018 second break:** no significant additional shift; Dec 2014 results unchanged when it is included.

**Debut first runs:** the share of new albums lasting only one week rose from 37.5% (2010) to 50.6% (2014) and then levelled off (53-55%). First-run length was shrinking before the rule (-6.5% per year) and stopped shrinking after (trend change +5.7%/yr, p < 0.001); no immediate jump.

**Interpretation:** a large, immediate break at the rule: fewer new entries and more slots held by long-running albums, reversing a rising pre-trend in new entries. Not driven by a few superstars (artist concentration unchanged). Limitations: one treated series (time-series evidence only); no sales-only album chart in the data as a control; the radio-chart drop means the song-chart comparison does not cleanly isolate the counting rule.

**Suggested next step:** scrape Billboard's sales-only Top Album Sales chart for 2010-2019 (the earlier `01_scrape_billboard.py` can do this with a different chart name, after checking the URL slug) to run a proper album-market difference-in-differences.
