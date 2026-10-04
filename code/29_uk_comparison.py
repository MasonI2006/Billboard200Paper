"""Part 2 cross-country comparison: does each chart break at its own rule date?

Specifications are fixed in docs/uk_comparison_plan.md, written before estimation.
A: UK break at its own rule (chart week 2015-03-01). B: UK placebo at the U.S. date (2014-12-07).
C: pooled U.S. + UK, jump at own date vs jump at the other country's date.
D: placebo-date distribution (randomisation-style p-value used for interpretation).
Outcome definitions and the ITS model are those of 20_part2_incumbency.py.
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from paths import RAW_BILLBOARD200, RESULTS_P2, UK_ALBUMS_WEEKLY

US_RULE = pd.Timestamp("2014-12-10")       # first rule chart, Kaggle stored date
US_AT_UK_DATE = pd.Timestamp("2015-03-04")  # first U.S. stored chart date on/after 2015-03-01
UK_RULE = pd.Timestamp("2015-03-01")       # first UK chart including streams (week starting)
UK_AT_US_DATE = pd.Timestamp("2014-12-07")  # UK chart week containing the first U.S. rule chart
OUTCOMES = ["new_share", "long_share"]
EXCLUDE_WEEKS = 26


def weekly(frame, date, weeks):
    g = frame.groupby(date)[weeks]
    return pd.DataFrame({"n": g.size(), "new_share": g.apply(lambda x: (x == 1).mean()),
                         "long_share": g.apply(lambda x: (x >= 52).mean())}).reset_index().rename(columns={date: "Date"})


def load_series():
    us = pd.read_csv(RAW_BILLBOARD200, dtype=str, low_memory=False, usecols=["Date", "Rank", "Weeks in Charts"])
    us["Date"] = pd.to_datetime(us["Date"], errors="coerce")
    us["Rank"] = pd.to_numeric(us["Rank"], errors="coerce")
    us["Weeks in Charts"] = pd.to_numeric(us["Weeks in Charts"], errors="coerce")
    us = us[us["Date"].between("2010-01-06", "2019-12-25")]
    uk = pd.read_csv(UK_ALBUMS_WEEKLY, parse_dates=["chart_week"])
    uk = uk[uk["chart_week"].between("2010-01-03", "2019-12-29")]
    series = {"US": weekly(us, "Date", "Weeks in Charts"),
              "US top 100": weekly(us[us["Rank"] <= 100], "Date", "Weeks in Charts"),
              "UK": weekly(uk, "chart_week", "weeks_on_chart")}
    for name, s in series.items():
        s["country"] = name
        s["week_index"] = np.arange(len(s))
    return series


def design(s, rule):
    d = s.copy()
    d["t"] = (d["Date"] - d["Date"].min()).dt.days / 365.25
    d["post"] = (d["Date"] >= rule).astype(int)
    d["t_post"] = d["post"] * (d["Date"] - rule).dt.days.clip(lower=0) / 365.25
    d["woy"] = d["Date"].dt.isocalendar().week.astype(int)
    return d


def its(s, y, rule):
    d = design(s, rule)
    return smf.ols(f"{y} ~ t + post + t_post + C(woy)", d).fit(cov_type="HAC", cov_kwds={"maxlags": 12})


def its_row(test, name, s, y, rule, note=""):
    m = its(s, y, rule)
    d = design(s, rule)
    row = {"test": test, "series": name, "outcome": y, "break_date": rule.date(), "weeks": len(d),
           "pre_mean": d.loc[d["post"] == 0, y].mean(), "tau": m.params["post"], "tau_se": m.bse["post"],
           "tau_p_nw": m.pvalues["post"], "trend_change": m.params["t_post"], "trend_change_p": m.pvalues["t_post"],
           "note": note}
    print(f"  {test:28s} {name:10s} {y:10s} {rule.date()} tau={row['tau']:+.4f} (se {row['tau_se']:.4f}, NW p={row['tau_p_nw']:.3f})", flush=True)
    return row


def pooled(us, uk, y, cov):
    rows = []
    for s, own, other in ((us, US_RULE, US_AT_UK_DATE), (uk, UK_RULE, UK_AT_US_DATE)):
        d = design(s, own)
        d["post_other"] = (d["Date"] >= other).astype(int)
        rows.append(d)
    d = pd.concat(rows, ignore_index=True).sort_values(["country", "week_index"]).reset_index(drop=True)
    f = (f"{y} ~ C(country) + C(country):t + C(country):C(woy) + C(country):t_post + post + post_other")
    if cov == "nw_by_country":
        m = smf.ols(f, d).fit(cov_type="hac-panel", cov_kwds={"groups": d["country"].astype("category").cat.codes, "maxlags": 12})
    else:  # Driscoll-Kraay
        m = smf.ols(f, d).fit(cov_type="hac-groupsum", cov_kwds={"time": d["week_index"].to_numpy(), "maxlags": 12})
    diff = m.t_test("post - post_other = 0")
    return {"tau_own": m.params["post"], "tau_own_se": m.bse["post"], "tau_own_p": m.pvalues["post"],
            "tau_other": m.params["post_other"], "tau_other_se": m.bse["post_other"], "tau_other_p": m.pvalues["post_other"],
            "own_minus_other": float(diff.effect[0]), "own_minus_other_p": float(diff.pvalue)}


def placebo_distribution(s, y, true_dates, observed_dates):
    dates = s.loc[s["Date"].between("2011-01-01", "2018-12-31"), "Date"]
    keep = [d for d in dates if all(abs((d - t).days) > EXCLUDE_WEEKS * 7 for t in true_dates)]
    taus = np.array([its(s, y, d).params["post"] for d in keep])
    out = {}
    for label, date in observed_dates.items():
        tau = its(s, y, date).params["post"]
        out[label] = (tau, (1 + np.sum(np.abs(taus) >= abs(tau))) / (len(taus) + 1))
    return taus, keep, out


def main():
    series = load_series()
    us, us100, uk = series["US"], series["US top 100"], series["UK"]
    for name, s in series.items():
        print(f"{name}: {len(s)} weeks, slots per week {s['n'].min()}-{s['n'].max()}", flush=True)
    rows = []
    print("A/B. Interrupted time series", flush=True)
    for y in OUTCOMES:
        rows.append(its_row("A UK at own rule", "UK", uk, y, UK_RULE))
        rows.append(its_row("B UK placebo at U.S. date", "UK", uk, y, UK_AT_US_DATE))
        rows.append(its_row("ref U.S. at own rule", "US", us, y, US_RULE, "Part 2 main (2010-2019)"))
        rows.append(its_row("ref U.S. at UK date", "US", us, y, US_AT_UK_DATE, "single-break model at the UK date"))
        rows.append(its_row("ref U.S. top 100 at own rule", "US top 100", us100, y, US_RULE, "secondary: positions 1-100"))

    print("C. Pooled two-country test", flush=True)
    pooled_rows = []
    for y in OUTCOMES:
        for us_series, label in ((us, "US (200 slots)"), (us100, "US top 100 (secondary)")):
            for cov in ("nw_by_country", "driscoll_kraay"):
                r = {"outcome": y, "us_series": label, "se": cov, **pooled(us_series, uk, y, cov)}
                pooled_rows.append(r)
                print(f"  {y:10s} {label:24s} {cov:15s} own={r['tau_own']:+.4f} (p={r['tau_own_p']:.3f}) "
                      f"other={r['tau_other']:+.4f} (p={r['tau_other_p']:.3f}) diff p={r['own_minus_other_p']:.3f}", flush=True)

    print("D. Placebo-date distributions", flush=True)
    true_dates = [US_RULE, UK_AT_US_DATE, UK_RULE, US_AT_UK_DATE]
    placebo_rows, dist_rows = [], []
    for name, s, observed in (("UK", uk, {"own rule": UK_RULE, "U.S. date (placebo)": UK_AT_US_DATE}),
                              ("US", us, {"own rule": US_RULE, "UK date (placebo)": US_AT_UK_DATE})):
        for y in OUTCOMES:
            taus, dates, out = placebo_distribution(s, y, true_dates, observed)
            dist_rows += [{"series": name, "outcome": y, "fake_date": d.date(), "tau": t} for d, t in zip(dates, taus)]
            for label, (tau, p) in out.items():
                placebo_rows.append({"series": name, "outcome": y, "date": label, "tau": tau, "n_fake_dates": len(taus),
                                     "placebo_rank_p": p})
                print(f"  {name:3s} {y:10s} {label:22s} tau={tau:+.4f} placebo-rank p={p:.3f} ({len(taus)} fake dates)", flush=True)

    RESULTS_P2.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(RESULTS_P2 / "uk_comparison.csv", index=False)
    pd.DataFrame(pooled_rows).to_csv(RESULTS_P2 / "uk_comparison_pooled.csv", index=False)
    pd.DataFrame(placebo_rows).to_csv(RESULTS_P2 / "uk_comparison_placebo_rank.csv", index=False)
    pd.DataFrame(dist_rows).to_csv(RESULTS_P2 / "uk_comparison_placebo_distribution.csv", index=False)
    pd.concat([s.assign(country=n) for n, s in series.items()]).to_csv(RESULTS_P2 / "uk_us_weekly_series.csv", index=False)
    print("done", flush=True)


if __name__ == "__main__":
    main()
