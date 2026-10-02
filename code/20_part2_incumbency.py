"""Question 1: did counting streams lock older albums onto the Billboard 200?
Follows q1_analysis_plan.md exactly. Uses only the Kaggle chart files."""
import pandas as pd, numpy as np, statsmodels.formula.api as smf
from pathlib import Path
DATA = Path("/mnt/user-data/uploads"); OUT = Path("results"); OUT.mkdir(exist_ok=True)
RULE = pd.Timestamp("2014-12-10")        # chart dated Dec 13, 2014 (stored 3 days early)
R2018 = pd.Timestamp("2018-07-11")       # chart dated July 14, 2018

def load(name):
    d = pd.read_csv(DATA / name, dtype=str, low_memory=False)
    d["Date"] = pd.to_datetime(d.Date, errors="coerce")
    for c in ["Rank", "Last Week", "Weeks in Charts"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    return d.dropna(subset=["Date"])

def weekly(d, long_weeks=52):
    g = d.groupby("Date")
    w = pd.DataFrame({
        "n": g.size(),
        "new_share": g["Weeks in Charts"].apply(lambda x: (x == 1).mean()),
        "long_share": g["Weeks in Charts"].apply(lambda x: (x >= long_weeks).mean()),
        "reentry_share": g.apply(lambda x: ((x["Weeks in Charts"] > 1) & x["Last Week"].isna()).mean(), include_groups=False),
        "hhi": g["Artist"].apply(lambda a: ((a.value_counts() / len(a)) ** 2).sum()),
    })
    return w.reset_index()

def its(w, y, start, end, rule=RULE, extra_break=None):
    d = w[(w.Date >= start) & (w.Date <= end)].copy()
    d["t"] = (d.Date - d.Date.min()).dt.days / 365.25          # trend in years
    d["post"] = (d.Date >= rule).astype(int)
    d["t_post"] = d.post * (d.Date - rule).dt.days.clip(lower=0) / 365.25
    d["woy"] = d.Date.dt.isocalendar().week.astype(int)
    f = f"{y} ~ t + post + t_post + C(woy)"
    if extra_break is not None:
        d["post2"] = (d.Date >= extra_break).astype(int)
        d["t_post2"] = d.post2 * (d.Date - extra_break).dt.days.clip(lower=0) / 365.25
        f += " + post2 + t_post2"
    m = smf.ols(f, d).fit(cov_type="HAC", cov_kwds={"maxlags": 12})
    row = {"outcome": y, "start": start, "end": end, "rule_date": rule.date(), "weeks": len(d),
           "pre_mean": d.loc[d.post == 0, y].mean(),
           "level_shift": m.params["post"], "level_se": m.bse["post"], "level_p": m.pvalues["post"],
           "trend_change_per_yr": m.params["t_post"], "trend_se": m.bse["t_post"], "trend_p": m.pvalues["t_post"],
           "pre_trend_per_yr": m.params["t"]}
    if extra_break is not None:
        row.update({"jul2018_level": m.params["post2"], "jul2018_level_p": m.pvalues["post2"],
                    "jul2018_trend": m.params["t_post2"], "jul2018_trend_p": m.pvalues["t_post2"]})
    return row

b = load("billboard200.csv")
wb = weekly(b)
wb.to_csv(OUT / "weekly_billboard200.csv", index=False)
MAIN = ("2010-01-06", "2019-12-25"); SEC = ("2010-01-06", "2024-12-31")

# A. main break test (+ secondary window)
A = [its(wb, y, *MAIN) for y in ["new_share", "long_share"]]
A += [its(wb, y, *MAIN) for y in ["reentry_share", "hhi"]]
A += [its(wb, y, *SEC) for y in ["new_share", "long_share"]]
pd.DataFrame(A).to_csv(OUT / "A_break_tests.csv", index=False)

# B. placebo dates (first chart stored in December of each year)
B = []
for yr in [2011, 2012, 2016, 2017]:
    fake = wb[(wb.Date.dt.year == yr) & (wb.Date.dt.month == 12)].Date.min()
    for y in ["new_share", "long_share"]:
        B.append(its(wb, y, *MAIN, rule=fake))
pd.DataFrame(B).to_csv(OUT / "B_placebo_dates.csv", index=False)

# C. song charts as comparison (new-entry share only; recurrent rules affect long runners)
Crows = []
for f in ["streaming.csv", "digital.csv", "radio.csv"]:
    w = weekly(load(f))
    r = its(w, "new_share", "2013-01-16", "2019-12-25"); r["chart"] = f.replace(".csv", ""); Crows.append(r)
r = its(wb, "new_share", "2013-01-16", "2019-12-25"); r["chart"] = "billboard200 (same window)"; Crows.append(r)
pd.DataFrame(Crows).to_csv(OUT / "C_song_chart_comparison.csv", index=False)

# D. July 2018 as a second break
D = [its(wb, y, *MAIN, extra_break=R2018) for y in ["new_share", "long_share"]]
pd.DataFrame(D).to_csv(OUT / "D_with_2018_break.csv", index=False)

# Secondary: first-run length of newly debuting albums (album-level)
b = b.sort_values("Date"); b["key"] = b.Artist.str.lower() + "|" + b.Song.str.lower()
deb = b[b["Weeks in Charts"] == 1].drop_duplicates("key")[["key", "Date", "Rank"]]
run = {}
for k, g in b[b.key.isin(deb.key)].groupby("key"):
    wks = g["Weeks in Charts"].values; n = 1
    for i in range(1, len(wks)):
        if wks[i] == wks[i-1] + 1: n += 1
        else: break
    run[k] = n
deb["first_run_weeks"] = deb.key.map(run)
deb = deb[(deb.Date >= MAIN[0]) & (deb.Date <= "2019-06-30")]   # allow runs to finish inside data
deb["post"] = (deb.Date >= RULE).astype(int); deb["year"] = deb.Date.dt.year
deb["ln_run"] = np.log(deb.first_run_weeks)
E = deb.groupby("year").agg(debuts=("key", "size"), median_first_run=("first_run_weeks", "median"),
                           share_one_week=("first_run_weeks", lambda x: (x == 1).mean()))
E.to_csv(OUT / "E_debut_first_runs_by_year.csv")
t = (deb.Date - deb.Date.min()).dt.days / 365.25
deb["t"] = t; deb["t_post"] = deb.post * ((deb.Date - RULE).dt.days.clip(lower=0) / 365.25)
deb["top10"] = (deb.Rank <= 10).astype(int)
m = smf.ols("ln_run ~ t + post + t_post + top10 + C(Date.dt.month)", deb).fit(cov_type="HC1")
pd.DataFrame({"coef": m.params, "se": m.bse, "p": m.pvalues}).loc[["post", "t_post", "t", "top10"]].to_csv(OUT / "E_debut_first_run_break.csv")

annual = wb[(wb.Date >= "2010-01-01") & (wb.Date <= "2024-12-31")].groupby(wb.Date.dt.year)[["new_share", "long_share", "reentry_share", "hhi"]].mean()
annual.to_csv(OUT / "annual_means.csv")
print("done")
