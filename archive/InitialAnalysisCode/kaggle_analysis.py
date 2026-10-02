"""Exploratory analyses on the Kaggle Billboard charts (ludmin/billboard).
Charts stored on Wednesdays (3 days before Billboard's Saturday issue date):
the first album-unit chart (issue Dec 13, 2014) is stored as 2014-12-10."""
import pandas as pd, numpy as np, re
from pathlib import Path
import os
CODE = Path(__file__).resolve().parent          # .../Billboard200Paper/InitialAnalysisCode
ROOT = CODE.parent                               # .../Billboard200Paper
U = str(ROOT / "OriginalDataFiles") + os.sep     # input data
RESULTS = ROOT / "kaggle_results"                # all outputs are written here
RESULTS.mkdir(exist_ok=True)
os.chdir(RESULTS)
RULE = pd.Timestamp("2014-12-10")

def load(f):
    x = pd.read_csv(U + f, dtype=str, low_memory=False)
    x["Date"] = pd.to_datetime(x.Date, errors="coerce")
    for c in ["Rank", "Peak Position", "Weeks in Charts"]:
        x[c] = pd.to_numeric(x[c], errors="coerce")
    return x.dropna(subset=["Date"])

def lead(s):  # lead artist: text before featuring / & / and / x / with / ,
    return (s.str.lower().str.replace(r"\s+", " ", regex=True)
             .str.split(r" featuring | feat\.? | ft\.? | with | x | & | and |, | / ", regex=True)
             .str[0].str.strip())

charts = {k: load(f) for k, f in [("b200", "billboard200.csv"), ("hot100", "hot100.csv"),
          ("streaming", "streaming.csv"), ("digital", "digital.csv"), ("radio", "radio.csv")]}
for k in charts: charts[k]["a"] = lead(charts[k].Artist)

b = charts["b200"]; b = b[(b.Date >= "2010-01-01") & (b.Date <= "2024-12-31")]
# album runs: total weeks on chart = max 'Weeks in Charts' observed for artist+title
runs = b.groupby(["a", "Song"]).agg(total_weeks=("Weeks in Charts", "max"),
                                    peak=("Peak Position", "min")).reset_index()
deb = b[b["Weeks in Charts"] == 1].merge(runs, on=["a", "Song"], how="left")
deb["year"] = deb.Date.dt.year; deb["post"] = (deb.Date >= RULE).astype(int)

# ---- A. Billboard 200 dynamics --------------------------------------------------
A = deb.groupby("year").agg(new_albums=("Song", "size"),
                            median_weeks_all=("total_weeks", "median"),
                            median_weeks_top10=("total_weeks", lambda s: s[deb.loc[s.index, "Rank"] <= 10].median()))
A.to_csv("A_b200_dynamics.csv")

# ---- B. Same-week song debuts per album debut, 4 song charts -----------------------
def same_week(chart):
    s = charts[chart]; d1 = s[s["Weeks in Charts"] == 1]
    return d1.groupby(["Date", "a"]).size().rename(chart)
for c in ["hot100", "streaming", "digital", "radio"]:
    deb = deb.merge(same_week(c), left_on=["Date", "a"], right_index=True, how="left")
    deb[c] = deb[c].fillna(0)
top10 = deb[deb.Rank <= 10]
B = top10.groupby("year")[["hot100", "streaming", "digital", "radio"]].mean()
B["share_hot100_5plus"] = top10.groupby("year").hot100.apply(lambda s: (s >= 5).mean())
B.to_csv("B_bombs_by_chart.csv")
# quarterly streaming-chart series around the rule (streaming chart starts 2013)
q = top10[top10.Date >= "2013-01-16"].copy(); q["q"] = q.Date.dt.to_period("Q").astype(str)
q.groupby("q")[["streaming", "hot100"]].mean().to_csv("B2_quarterly.csv")

# ---- C. Dilution: how long do same-week album-track debuts last on the Hot 100? ---------
h = charts["hot100"]
song_runs = h.groupby(["a", "Song"]).agg(first=("Date", "min"), weeks=("Weeks in Charts", "max"),
                                         peak=("Peak Position", "min")).reset_index()
keys = top10[["Date", "a", "year"]].drop_duplicates()
tracks = song_runs.merge(keys, left_on=["first", "a"], right_on=["Date", "a"])
Cdil = tracks.groupby("year").agg(n_tracks=("Song", "size"),
                               share_1week=("weeks", lambda w: (w <= 1).mean()),
                               share_2orless=("weeks", lambda w: (w <= 2).mean()),
                               median_peak=("peak", "median"),
                               share_top40=("peak", lambda p: (p <= 40).mean()))
Cdil.to_csv("C_dilution.csv")

# ---- D. Artist-level streaming exposure (pre-rule, 2013-01 to 2014-11) ------------------
pre = lambda c: charts[c][(charts[c].Date >= "2013-01-16") & (charts[c].Date < RULE)]
sw = pre("streaming").groupby("a").size().rename("stream_wks")
dw = pre("digital").groupby("a").size().rename("digital_wks")
ex = pd.concat([sw, dw], axis=1).fillna(0)
ex = ex[(ex.sum(axis=1) >= 5)]
ex["exposure"] = ex.stream_wks / (ex.stream_wks + ex.digital_wks)   # 0 = sales-only, 1 = streaming-only
ex.to_csv("D_artist_exposure.csv")

import statsmodels.formula.api as smf
panel = deb.merge(ex[["exposure"]], left_on="a", right_index=True)
panel = panel[panel.year <= 2019]                       # main window
# keep artists with album debuts both before and after the rule
k = panel.groupby("a").post.agg(["min", "max"]); keep = k[(k["min"] == 0) & (k["max"] == 1)].index
panel = panel[panel.a.isin(keep)].copy()
panel["ln_hot100"] = np.log1p(panel.hot100)
panel["exp_std"] = (panel.exposure - panel.exposure.mean()) / panel.exposure.std()
res = {}
for y in ["ln_hot100", "hot100"]:
    m = smf.ols(f"{y} ~ post:exp_std + C(a) + C(year)", data=panel).fit(
        cov_type="cluster", cov_kwds={"groups": panel.a})
    res[y] = (m.params["post:exp_std"], m.bse["post:exp_std"], m.pvalues["post:exp_std"])
# event study: year x exposure, omit 2014
es = smf.ols("ln_hot100 ~ " + " + ".join(f"I((year=={t})*exp_std)" for t in range(2010, 2020) if t != 2014)
             + " + C(a) + C(year)", data=panel).fit(cov_type="cluster", cov_kwds={"groups": panel.a})
ES = pd.DataFrame({"coef": es.params.filter(regex=r"^I\(\(year"), "se": es.bse.filter(regex=r"^I\(\(year")})
ES.index = [int(re.search(r"(20\d\d)", i).group(1)) for i in ES.index]
ES.sort_index().to_csv("D_event_study.csv")
pd.DataFrame(res, index=["coef", "se", "p"]).to_csv("D_did.csv")

# ---- E. Chart payoff: do albums with more same-week song debuts last longer, pre vs post? ---
t = top10[top10.year <= 2019].copy(); t["ln_weeks"] = np.log(t.total_weeks)
t["bomb"] = np.log1p(t.hot100)
m = smf.ols("ln_weeks ~ bomb*post + C(Rank) + C(year)", data=t).fit(cov_type="HC1")
pd.DataFrame({"coef": m.params, "se": m.bse, "p": m.pvalues}).loc[["bomb", "bomb:post"]].to_csv("E_payoff.csv")

print("sample: debuts", len(deb), "| exposure artists", len(ex), "| DiD panel", len(panel), "albums,", panel.a.nunique(), "artists")
for f in ["A_b200_dynamics", "B_bombs_by_chart", "C_dilution", "D_did", "D_event_study", "E_payoff"]:
    print("\n==", f); print(pd.read_csv(f + ".csv").round(3).to_string(index=False))
print("\nexposure top/bottom:"); print(ex.sort_values("exposure").iloc[[0,1,2,3,-4,-3,-2,-1]].round(2).to_string())

# ---- D2. Robustness: drop albums from the exposure-measurement window (2013-14), omit 2012 in event study
p2 = panel[~panel.year.isin([2013, 2014])].copy()
k2 = p2.groupby("a").post.agg(["min", "max"]); p2 = p2[p2.a.isin(k2[(k2["min"] == 0) & (k2["max"] == 1)].index)]
m2 = smf.ols("ln_hot100 ~ post:exp_std + C(a) + C(year)", data=p2).fit(cov_type="cluster", cov_kwds={"groups": p2.a})
es2 = smf.ols("ln_hot100 ~ " + " + ".join(f"I((year=={t})*exp_std)" for t in [2010, 2011, 2015, 2016, 2017, 2018, 2019])
              + " + C(a) + C(year)", data=p2).fit(cov_type="cluster", cov_kwds={"groups": p2.a})
out = pd.DataFrame({"coef": es2.params.filter(regex=r"^I\(\(year"), "se": es2.bse.filter(regex=r"^I\(\(year")})
out.index = [int(re.search(r"(20\d\d)", i).group(1)) for i in out.index]
print("\n== D2 DiD excl 2013-14:", round(m2.params["post:exp_std"], 3), "se", round(m2.bse["post:exp_std"], 3),
      "p", round(m2.pvalues["post:exp_std"], 3), "| n", len(p2), "artists", p2.a.nunique())
print("event study (ref 2012):"); print(out.round(3).to_string())
out.to_csv("D2_event_study_ref2012.csv")
