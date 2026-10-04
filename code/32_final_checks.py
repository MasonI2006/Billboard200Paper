"""Final checks (docs/final_checks_plan.md, written before estimation).

1. Part 1: what the null rules out (90% CI, smallest TOST bound, MDE, TOST at half a track).
2. Part 2b: leave-one-genre-out, with the Part 2b script's own genre wild bootstrap.
3. Part 2: monthly event-study plot around each country's rule (descriptive).
"""

import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import patsy
import statsmodels.formula.api as smf
from scipy import stats

from paths import ANALYSIS_SAMPLE, PART2_WEEKLY, PART2B_ALBUM_RUNS, RESULTS_FINAL_CHECKS, RESULTS_P1, RESULTS_P2

US_RULE = pd.Timestamp("2014-12-10")
UK_RULE = pd.Timestamp("2015-03-01")


# ---------- 1 ----------
def equivalence():
    h = pd.read_csv(RESULTS_P1 / "headline.csv").iloc[0]
    b, se = h["coef_post_by_streaming_heavy"], h["se_artist_cluster"]
    m = pd.read_csv(ANALYSIS_SAMPLE)["standard_tracks"].mean()
    z90, z80 = stats.norm.ppf(0.95), stats.norm.ppf(0.80)
    to_tracks = lambda x: m * (math.exp(x) - 1)
    lo, hi = b - z90 * se, b + z90 * se
    smallest = abs(b) + z90 * se
    mde = (stats.norm.ppf(0.975) + z80) * se
    delta = math.log((m + 0.5) / m)
    p_lower = 1 - stats.norm.cdf((b + delta) / se)    # H0: b <= -delta
    p_upper = stats.norm.cdf((b - delta) / se)        # H0: b >= +delta
    rows = [
        {"quantity": "headline estimate", "log_points": b, "percent": 100 * (math.exp(b) - 1), "tracks": to_tracks(b)},
        {"quantity": "90% CI lower", "log_points": lo, "percent": 100 * (math.exp(lo) - 1), "tracks": to_tracks(lo)},
        {"quantity": "90% CI upper", "log_points": hi, "percent": 100 * (math.exp(hi) - 1), "tracks": to_tracks(hi)},
        {"quantity": "smallest equivalence bound rejected at 5% (TOST)", "log_points": smallest,
         "percent": 100 * (math.exp(smallest) - 1), "tracks": to_tracks(smallest)},
        {"quantity": "minimum detectable effect (80% power, 5% two-sided)", "log_points": mde,
         "percent": 100 * (math.exp(mde) - 1), "tracks": to_tracks(mde)},
        {"quantity": "prespecified bound: half a track", "log_points": delta, "percent": 100 * (math.exp(delta) - 1),
         "tracks": 0.5, "tost_p": max(p_lower, p_upper), "tost_pass_5pct": max(p_lower, p_upper) < 0.05},
    ]
    out = pd.DataFrame(rows)
    out["mean_tracks"] = m
    print(out.round(4).to_string(index=False), flush=True)
    return out


# ---------- 2 ----------
def wild_boot(y, d, B=9999, seed=20260928):
    """Verbatim algorithm of wild_boot() in 22_part2b_analyze.py: restricted wild cluster bootstrap,
    genre clusters, Webb weights; t-stats use genre-cluster SEs."""
    f_full = f"{y} ~ post:heavy + C(genre) + C(year)"
    yv, X = patsy.dmatrices(f_full, d, return_type="dataframe")
    j = list(X.columns).index("post:heavy")
    yv = yv.values.ravel(); Xv = X.values
    Xr = np.delete(Xv, j, axis=1)
    br = np.linalg.lstsq(Xr, yv, rcond=None)[0]; fr = Xr @ br; ur = yv - fr
    XtXi = np.linalg.pinv(Xv.T @ Xv); A = XtXi @ Xv.T
    g = d["genre"].values; G = np.unique(g); idx = [np.where(g == k)[0] for k in G]

    def tstat(yy):
        beta = A @ yy; e = yy - Xv @ beta
        meat = sum(np.outer(Xv[i].T @ e[i], Xv[i].T @ e[i]) for i in idx)
        V = XtXi @ meat @ XtXi
        return beta[j] / np.sqrt(V[j, j]), beta[j]
    t0, b0 = tstat(yv)
    W = np.array([-np.sqrt(1.5), -1, -np.sqrt(.5), np.sqrt(.5), 1, np.sqrt(1.5)])
    rng = np.random.default_rng(seed); ts = np.empty(B)
    for r in range(B):
        wg = rng.choice(W, len(G)); wv = np.empty(len(yv))
        for k, i in enumerate(idx): wv[i] = wg[k]
        ts[r] = tstat(fr + ur * wv)[0]
    return (np.abs(ts) >= abs(t0)).mean(), len(G)


def leave_one_genre_out():
    deb = pd.read_csv(PART2B_ALBUM_RUNS)
    deb = deb[deb["genre"].notna()].copy()
    deb["heavy"] = deb["heavy"].astype(int)
    rows = []
    for drop in ["(none: full sample)"] + sorted(deb["genre"].unique()):
        d = deb if drop.startswith("(") else deb[deb["genre"] != drop]
        d = d.reset_index(drop=True)
        m = smf.ols("weeks52 ~ post:heavy + C(genre) + C(year)", d).fit(cov_type="cluster", cov_kwds={"groups": d["mbid"]})
        p, G = wild_boot("weeks52", d)
        rows.append({"genre_dropped": drop, "dropped_is_heavy": int(deb.loc[deb["genre"] == drop, "heavy"].max()) if not drop.startswith("(") else np.nan,
                     "n_albums": len(d), "n_heavy": int(d["heavy"].sum()), "genre_clusters": G,
                     "coef": m.params["post:heavy"], "se_artist": m.bse["post:heavy"], "p_artist": m.pvalues["post:heavy"],
                     "p_wildboot_genre": p})
        print(f"  drop {drop:22s} n={len(d)} coef={rows[-1]['coef']:+.2f} (p={rows[-1]['p_artist']:.3f}, boot p={p:.3f}, G={G})", flush=True)
    out = pd.DataFrame(rows)
    full = out.iloc[0]["coef"]
    loo = out.iloc[1:]
    verdict = bool((loo["coef"] > 0).all() and loo["coef"].min() >= full / 2)
    print(f"  not driven by a single genre (all positive and min >= {full / 2:.2f}): {verdict}", flush=True)
    out["rule_not_driven_by_single_genre"] = verdict
    return out


# ---------- 3 ----------
def event_study(series, date_col, rule, y):
    # Full 2010-2019 series with end bins (<= -25, >= +24): within +-24 months alone, month dummies
    # and week-of-year effects are not separately identified (plan deviation, devlog section 34).
    d = series[series[date_col].between("2010-01-01", "2019-12-31")].copy()
    d["rel"] = np.floor((d[date_col] - rule).dt.days / 30.4375).astype(int).clip(-25, 24)
    d["woy"] = d[date_col].dt.isocalendar().week.astype(int)
    m = smf.ols(f"{y} ~ C(rel, Treatment(reference=-1)) + C(woy)", d).fit(cov_type="HAC", cov_kwds={"maxlags": 12})
    rows = []
    for k in range(-24, 24):
        name = f"C(rel, Treatment(reference=-1))[T.{k}]"
        b, s = (0.0, 0.0) if k == -1 else (m.params[name], m.bse[name])
        rows.append({"rel_month": k, "coef": b, "se": s})
    return pd.DataFrame(rows)


def event_plots():
    us = pd.read_csv(PART2_WEEKLY, parse_dates=["Date"])
    uk = pd.read_csv(RESULTS_P2 / "uk_us_weekly_series.csv", parse_dates=["Date"])
    uk = uk[uk["country"] == "UK"]
    panels, rows = [], []
    for country, s, rule in (("U.S. (rule Dec 2014)", us, US_RULE), ("UK (rule Mar 2015)", uk, UK_RULE)):
        for y, label in (("new_share", "New-entry share"), ("long_share", "52+-week share")):
            es = event_study(s, "Date", rule, y)
            es["series"], es["outcome"] = country, y
            rows.append(es)
            panels.append((country, label, es))
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True)
    for ax, (country, label, es) in zip(axes.T.ravel(), panels):
        ax.errorbar(es["rel_month"], es["coef"], yerr=1.96 * es["se"], fmt="o", ms=3, lw=0.8, capsize=0)
        ax.axhline(0, color="grey", lw=0.8)
        ax.axvline(-0.5, color="tab:red", ls="--", lw=1)
        ax.set_title(f"{country}: {label}", fontsize=10)
    for ax in axes[-1]:
        ax.set_xlabel("Months relative to the country's rule (reference: month before)")
    fig.tight_layout()
    fig.savefig(RESULTS_FINAL_CHECKS / "fig_event_study.png", dpi=150)
    return pd.concat(rows, ignore_index=True)


def main():
    RESULTS_FINAL_CHECKS.mkdir(parents=True, exist_ok=True)
    print("1. Equivalence", flush=True)
    equivalence().to_csv(RESULTS_FINAL_CHECKS / "equivalence.csv", index=False)
    print("3. Event-study plot", flush=True)
    event_plots().to_csv(RESULTS_FINAL_CHECKS / "event_study_monthly.csv", index=False)
    print("2. Part 2b leave-one-genre-out", flush=True)
    leave_one_genre_out().to_csv(RESULTS_FINAL_CHECKS / "part2b_leave_one_genre_out.csv", index=False)
    print("done", flush=True)


if __name__ == "__main__":
    main()
