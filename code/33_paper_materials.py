"""Paper materials: figures and the parameter list in paperwriting/, read straight from results files.

Every number in paperwriting/parameters.md is pulled from a results CSV named in its row, so the
list regenerates with the pipeline. Figures go to paperwriting/figures/ as PNG (300 dpi) and PDF.
Main text: Fig. 1-4. Appendix: Fig. A1-A4. No estimation here.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from paths import (ANALYSIS_SAMPLE, PAPERWRITING, RESULTS_FINAL_CHECKS, RESULTS_P1, RESULTS_P1_SECONDARY,
                   RESULTS_P2, RESULTS_P2B, RIAA_REVENUE_BY_CATEGORY)

FIG = PAPERWRITING / "figures"
MATCHED = RESULTS_P2 / "matched"
US_ISSUE = pd.Timestamp("2014-12-13")
UK_RULE = pd.Timestamp("2015-03-01")

# Okabe-Ito colour-blind-safe palette
BLUE, ORANGE, GREEN, RED, GREY = "#0072B2", "#E69F00", "#009E73", "#D55E00", "#7F7F7F"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9.5, "axes.titlesize": 10, "axes.titleweight": "bold",
    "axes.labelsize": 9.5, "legend.fontsize": 8.5, "legend.frameon": False,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#E6E6E6",
    "grid.linewidth": 0.6, "axes.axisbelow": True, "xtick.labelsize": 8.5, "ytick.labelsize": 8.5,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.05,
})


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"{name}.{ext}", dpi=300)
    plt.close(fig)


def panel_label(ax, letter, title):
    ax.set_title(f"({letter}) {title}", loc="left")


def rule_line(ax, x, label, color=RED, ypos=0.97, ha="left"):
    ax.axvline(x, color=color, ls="--", lw=1)
    ax.text(x, ypos, f" {label} ", transform=ax.get_xaxis_transform(), color=color, fontsize=8, va="top", ha=ha)


def event_points(ax, x, b, se, ref, pre_last, scale=1.0):
    """Coefficients with 95% intervals; pre-period grey, post-period blue, reference period hollow."""
    x, b, se = np.asarray(x), np.asarray(b) * scale, np.asarray(se) * scale
    pre = x <= pre_last
    for mask, color in ((pre, GREY), (~pre, BLUE)):
        ax.errorbar(x[mask], b[mask], yerr=1.96 * se[mask], fmt="o", ms=5, color=color, ecolor=color,
                    elinewidth=1.2, capsize=3)
    ax.plot([ref], [0], "o", ms=5, mfc="white", mec=GREY, zorder=5)
    ax.axhline(0, color="black", lw=0.8)


# ---------------- main-text figures ----------------
def fig1_part1():
    a = pd.read_csv(ANALYSIS_SAMPLE)
    m = a.groupby(["year", "heavy"])["standard_tracks"].mean().unstack()
    e = pd.read_csv(RESULTS_P1_SECONDARY / "event_study.csv")
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.1))
    ax = axes[0]
    ax.plot(m.index, m[1], "-o", ms=4, color=BLUE, label="Streaming-heavy genres")
    ax.plot(m.index, m[0], "-s", ms=4, color=ORANGE, label="Other genres")
    rule_line(ax, 2014.9, "Rule", ypos=0.08)
    ax.set_xlabel("Release year"); ax.set_ylabel("Average number of tracks")
    ax.set_xticks(range(2009, 2020, 2))
    ax.legend(loc="center left", bbox_to_anchor=(0.0, 0.52))
    panel_label(ax, "a", "Average album length")
    ax = axes[1]
    years = list(e["year"]) + [2014]
    order = np.argsort(years)
    x = np.array(years)[order]
    b = np.append(e["coef"].to_numpy(), 0.0)[order]
    se = np.append(e["se_artist"].to_numpy(), 0.0)[order]
    event_points(ax, x, b, se, ref=2014, pre_last=2014, scale=100)
    rule_line(ax, 2014.5, "Rule", ypos=0.08)
    ax.set_xlabel("Release year (2014 = reference)"); ax.set_ylabel("Difference in album length,\nstreaming-heavy vs other (%)")
    ax.set_xticks(range(2009, 2020, 2))
    panel_label(ax, "b", "Difference by year")
    # pre-2014 joint test p is reported in the caption (paperwriting/README.md)
    fig.tight_layout()
    save(fig, "fig1_part1_album_length")


def fig2_us_uk_series():
    s = pd.read_csv(RESULTS_P2 / "uk_us_weekly_series.csv", parse_dates=["Date"])
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 5.6), sharex=True)
    for ax, y, letter, title, ylab in (
            (axes[0], "new_share", "a", "New albums entering the chart", "% of chart spots held by\nalbums in their first week"),
            (axes[1], "long_share", "b", "Long-running albums", "% of chart spots held by\nalbums charting 52+ weeks")):
        for name, color, label in (("US", BLUE, "U.S. Billboard 200"), ("UK", ORANGE, "UK Official Albums Chart")):
            d = s[s["country"] == name].set_index("Date")[y] * 100
            ax.plot(d.index, d.rolling(8, center=True).mean(), color=color, lw=1.6, label=label)
        lo, hi = ax.get_ylim()
        ax.set_ylim(lo, hi + 0.22 * (hi - lo))
        rule_line(ax, US_ISSUE, "U.S. rule (Dec 2014)", color=RED, ha="right", ypos=0.99)
        rule_line(ax, UK_RULE, "UK rule (Mar 2015)", color=GREEN, ypos=0.99)
        ax.set_ylabel(ylab)
        panel_label(ax, letter, title)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.02))
    axes[1].xaxis.set_major_locator(mdates.YearLocator())
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axes[1].set_xlabel("Chart week (8-week moving average)")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    save(fig, "fig2_us_uk_chart_shares")


def fig3_monthly_event():
    e = pd.read_csv(RESULTS_FINAL_CHECKS / "event_study_monthly.csv")
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.2), sharex=True, sharey="row")
    spec = [("U.S. (rule Dec 2014)", "new_share", "a", "U.S.: new albums"),
            ("UK (rule Mar 2015)", "new_share", "b", "UK: new albums"),
            ("U.S. (rule Dec 2014)", "long_share", "c", "U.S.: long-running albums"),
            ("UK (rule Mar 2015)", "long_share", "d", "UK: long-running albums")]
    for ax, (series, y, letter, title) in zip(axes.ravel(), spec):
        d = e[(e["series"] == series) & (e["outcome"] == y)]
        b, se = d["coef"] * 100, d["se"] * 100
        pre = d["rel_month"] < 0
        ax.fill_between(d["rel_month"], b - 1.96 * se, b + 1.96 * se, color=BLUE, alpha=0.15, lw=0)
        ax.plot(d["rel_month"][pre], b[pre], "o", ms=3, color=GREY)
        ax.plot(d["rel_month"][~pre], b[~pre], "o", ms=3, color=BLUE)
        ax.axhline(0, color="black", lw=0.8)
        ax.axvline(-0.5, color=RED, ls="--", lw=1)
        panel_label(ax, letter, title)
        ax.set_xticks(range(-24, 25, 6))
    axes[0, 0].set_ylabel("New-entry share vs month before\nrule (percentage points)")
    axes[1, 0].set_ylabel("52+-week share vs month before\nrule (percentage points)")
    for ax in axes[1]:
        ax.set_xlabel("Months since own country's rule")
    fig.tight_layout()
    save(fig, "fig3_monthly_event_study")


def fig4_part2b_event():
    e = pd.read_csv(RESULTS_P2B / "results_event_study.csv").rename(columns={"Unnamed: 0": "year"})
    years = list(e["year"]) + [2014]
    order = np.argsort(years)
    x = np.array(years)[order]
    b = np.append(e["coef"].to_numpy(), 0.0)[order]
    se = np.append(e["se"].to_numpy(), 0.0)[order]
    fig, ax = plt.subplots(figsize=(6.0, 3.2))
    event_points(ax, x, b, se, ref=2014, pre_last=2014)
    rule_line(ax, 2014.5, "Rule")
    ax.set_xlabel("Year the album debuted (2014 = reference)")
    ax.set_ylabel("Extra weeks on chart in first year,\nstreaming-heavy minus other genres")
    ax.set_xticks(range(2010, 2019))
    ax.text(0.02, 0.95, f"Pre-2014 joint test: p = {e['joint_pre2014_p'].iloc[0]:.2f}", transform=ax.transAxes, fontsize=8, color=GREY, va="top")
    fig.tight_layout()
    save(fig, "fig4_part2b_staying_power")


# ---------------- appendix figures ----------------
def figA1_riaa():
    r = pd.read_csv(RIAA_REVENUE_BY_CATEGORY)
    r = r[r["year"].between(2005, 2019)]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0))
    ax = axes[0]
    for col, color, label in (("physical_nominal", GREY, "CDs and vinyl"), ("digital_downloads_nominal", ORANGE, "Downloads"),
                              ("streaming_nominal", BLUE, "Streaming")):
        ax.plot(r["year"], r[col] / 1e9, "-o", ms=3.5, color=color, label=label)
    rule_line(ax, 2014.95, "Rule")
    ax.set_xlabel("Year"); ax.set_ylabel("U.S. revenue ($ billion, nominal)")
    ax.legend(loc="upper left", bbox_to_anchor=(0.22, 1.0))
    panel_label(ax, "a", "Revenue by format")
    ax = axes[1]
    ax.plot(r["year"], 100 * r["streaming_share"], "-o", ms=3.5, color=BLUE)
    rule_line(ax, 2014.95, "Rule")
    ax.set_xlabel("Year"); ax.set_ylabel("Streaming share of revenue (%)")
    panel_label(ax, "b", "Streaming's share")
    fig.tight_layout()
    save(fig, "figA1_riaa_streaming_growth")


def figA2_placebo():
    dist = pd.read_csv(RESULTS_P2 / "uk_comparison_placebo_distribution.csv")
    rank = pd.read_csv(RESULTS_P2 / "uk_comparison_placebo_rank.csv")
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9))
    for ax, y, letter, title in ((axes[0], "new_share", "a", "New-entry share"), (axes[1], "long_share", "b", "52+-week share")):
        d = dist[(dist["series"] == "US") & (dist["outcome"] == y)]["tau"] * 100
        r = rank[(rank["series"] == "US") & (rank["outcome"] == y) & (rank["date"] == "own rule")].iloc[0]
        ax.hist(d, bins=35, color="#C9D9E8", edgecolor="white")
        ax.axvline(r["tau"] * 100, color=RED, lw=2)
        ax.text(r["tau"] * 100, 0.95, " actual\n rule date" if r["tau"] < 0 else "actual \nrule date ", transform=ax.get_xaxis_transform(),
                color=RED, fontsize=8, va="top", ha="left" if r["tau"] < 0 else "right")
        ax.set_xlabel("Estimated jump (percentage points)")
        ax.set_ylabel("Number of fake dates")
        panel_label(ax, letter, f"{title} (p = {r['placebo_rank_p']:.3f})")
    fig.tight_layout()
    save(fig, "figA2_placebo_dates")


def figA3_leave_one_out():
    names = {"christian": "Christian", "classical": "Classical", "country": "Country", "electronic": "Electronic*",
             "hiphop_rnb": "Hip-hop/R&B*", "jazz": "Jazz", "latin": "Latin*", "pop": "Pop*", "rock": "Rock"}
    l = pd.read_csv(RESULTS_FINAL_CHECKS / "part2b_leave_one_genre_out.csv")
    full, rest = l.iloc[0], l.iloc[1:].sort_values("coef")
    rows = [("All genres (main estimate)", full["coef"], full["se_artist"], True)] + \
           [(f"Without {names[g]}", c, s, False) for g, c, s in zip(rest["genre_dropped"], rest["coef"], rest["se_artist"])]
    rows = rows[::-1]
    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    for i, (label, c, s, main) in enumerate(rows):
        ax.errorbar(c, i, xerr=1.96 * s, fmt="D" if main else "o", ms=5, color=RED if main else BLUE, capsize=3, elinewidth=1.2)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows])
    ax.axvline(0, color="black", lw=0.8)
    ax.axvline(full["coef"], color=RED, ls=":", lw=1)
    ax.set_xlabel("Extra weeks on chart in first year (95% CI)")
    ax.text(1.0, 1.01, "* streaming-heavy genre", transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color=GREY)
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    save(fig, "figA3_leave_one_genre_out")


def figA4_thresholds():
    t = pd.read_csv(RESULTS_P1_SECONDARY / "long_albums_thresholds.csv")
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    ax.fill_between(t["threshold"], t["ci_low"] * 100, t["ci_high"] * 100, color=BLUE, alpha=0.15, lw=0)
    ax.plot(t["threshold"], t["coef"] * 100, "-o", ms=3.5, color=BLUE)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xlabel("Album has at least this many tracks")
    ax.set_ylabel("Change in share of albums,\nstreaming-heavy vs other\n(percentage points)")
    ax.set_xticks(range(8, 31, 2))
    fig.tight_layout()
    save(fig, "figA4_track_count_thresholds")


FIGURES = (fig1_part1, fig2_us_uk_series, fig3_monthly_event, fig4_part2b_event,
           figA1_riaa, figA2_placebo, figA3_leave_one_out, figA4_thresholds)


# ---------------- parameter list ----------------
def f(x, d=3):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return ""
    if isinstance(x, (int, np.integer)):
        return f"{x:,}"
    return f"{x:+.{d}f}" if d and abs(x) >= 0 else f"{x}"


def p(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return ""
    return "<0.001" if x < 0.001 else f"{x:.3f}"


def table(rows):
    head = "| Parameter | Estimate | SE | p (conventional) | p (bootstrap / placebo) | N | Source |\n|---|---|---|---|---|---|---|\n"
    return head + "\n".join(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | `{r[6]}` |" for r in rows) + "\n"


def parameters():
    out = ["# Parameters for the paper\n",
           "Generated by `code/33_paper_materials.py` from the results files named in each row; do not edit by hand. "
           "Regenerate with `py -3.10 code/run_pipeline.py --only 33`. \"Conventional\" p: artist-clustered for album-level models, "
           "Newey-West for weekly series. \"Bootstrap\": genre-level restricted Webb wild cluster bootstrap (9,999 draws) unless noted; "
           "\"placebo\": rank of the true-date estimate among fake-date estimates. Status of each test: `test_registry.md`.\n"]

    # ---- Part 1
    h = pd.read_csv(RESULTS_P1 / "headline.csv").iloc[0]
    means = pd.read_csv(RESULTS_P1 / "headline_means.csv")
    eq = pd.read_csv(RESULTS_FINAL_CHECKS / "equivalence.csv").set_index("quantity")
    ev = pd.read_csv(RESULTS_P1_SECONDARY / "event_study.csv")
    rows = [["**Headline: post x streaming-heavy, log tracks**", f(h["coef_post_by_streaming_heavy"], 4), f"{h['se_artist_cluster']:.4f}",
             p(h["p_artist_cluster"]), p(h["p_wildboot_genre_webb_9999"]), f"{int(h['n_albums']):,} albums / {int(h['n_artists']):,} artists",
             "results/part1_album_length/headline.csv"]]
    for _, r in means.iterrows():
        rows.append([f"Mean tracks, {'streaming-heavy' if r['heavy'] else 'other'}, {'post' if r['post'] else 'pre'}",
                     f"{r['mean_tracks']:.2f}", "", "", "", f"{int(r['n']):,}", "results/part1_album_length/headline_means.csv"])
    rows += [["90% CI of headline, in tracks", f"{eq.loc['90% CI lower', 'tracks']:+.2f} to {eq.loc['90% CI upper', 'tracks']:+.2f}", "", "", "", "", "results/final_checks/equivalence.csv"],
             ["Smallest effect ruled out (TOST, 5%), tracks / %", f"{eq.loc['smallest equivalence bound rejected at 5% (TOST)', 'tracks']:.2f} / {eq.loc['smallest equivalence bound rejected at 5% (TOST)', 'percent']:.1f}%", "", "", "", "", "results/final_checks/equivalence.csv"],
             ["Minimum detectable effect (80% power), tracks", f"{eq.loc['minimum detectable effect (80% power, 5% two-sided)', 'tracks']:.2f}", "", "", "", "", "results/final_checks/equivalence.csv"],
             ["TOST at prespecified half-track bound", "fails", "", p(eq.loc["prespecified bound: half a track", "tost_p"]), "", "", "results/final_checks/equivalence.csv"],
             ["Event study: joint pre-2014 test", "", "", p(ev["joint_pre2014_p"].iloc[0]), "", "", "results/part1_album_length/secondary/event_study.csv"]]
    for _, r in ev.iterrows():
        rows.append([f"Event study {int(r['year'])} (ref 2014)", f(r["coef"], 4), f"{r['se_artist']:.4f}", p(r["p_artist"]), "", "", "results/part1_album_length/secondary/event_study.csv"])
    out.append("## Part 1: album length\n\n### Headline, means, what the null rules out, event study\n\n" + table(rows))

    sec = pd.read_csv(RESULTS_P1_SECONDARY / "secondary_checks.csv")
    rows = [[r["check"] + f" ({r['kind']})", f(r["coef"], 4), f"{r['se_artist']:.4f}", p(r["p_artist"]), p(r["p_wildboot_genre"]),
             f"{int(r['n_albums']):,}", "results/part1_album_length/secondary/secondary_checks.csv"] for _, r in sec.iterrows()]
    pc = pd.read_csv(RESULTS_P1_SECONDARY / "plan_checks.csv").iloc[1:]
    rows += [[r["check"], f(r["coef"], 4), f"{r['se_artist']:.4f}", p(r["p_artist"]), p(r["p_wildboot_genre"]),
              f"{int(r['n_albums']):,}", "results/part1_album_length/secondary/plan_checks.csv"] for _, r in pc.iterrows()]
    dg = pd.read_csv(RESULTS_P1 / "digital_robustness.csv").iloc[1:]
    rows += [[f"digital edition: {r['spec']}", f(r["coef"], 4), f"{r['se_artist_cluster']:.4f}", p(r["p_artist_cluster"]), p(r["p_wildboot_genre"]),
              f"{int(r['n_albums']):,}", "results/part1_album_length/digital_robustness.csv"] for _, r in dg.iterrows()]
    rp = pd.read_csv(RESULTS_P1_SECONDARY / "rockpop_sensitivity.csv").iloc[0]
    rows.append(["genre rule: rock + pop -> pop (exploratory)", f(rp["coef"], 4), f"{rp['se_artist']:.4f}", p(rp["p_artist"]), p(rp["p_wildboot_genre"]),
                 f"{int(rp['n']):,}", "results/part1_album_length/secondary/rockpop_sensitivity.csv"])
    out.append("### Secondary, frozen-plan and exploratory checks\n\n" + table(rows))

    la = pd.read_csv(RESULTS_P1_SECONDARY / "long_albums_followup.csv")
    rows = []
    for _, r in la.iterrows():
        extra = f" (Holm {r['p_holm']:.3f})" if not np.isnan(r["p_holm"]) else ""
        rows.append([f"{r['test']} [{r['method']}]", f(r["coef"], 4), "" if np.isnan(r["se"]) else f"{r['se']:.4f}", p(r["p_artist"]),
                     (p(r["p_family"]) + extra) if not np.isnan(r["p_family"]) else "", "" if np.isnan(r["n_albums"]) else f"{int(r['n_albums']):,}",
                     "results/part1_album_length/secondary/long_albums_followup.csv"])
    out.append("### Long-albums follow-up (prespecified family A1-A5, Holm)\n\n" + table(rows))

    # ---- Part 2
    a = pd.read_csv(RESULTS_P2 / "A_break_tests.csv")
    rank = pd.read_csv(RESULTS_P2 / "uk_comparison_placebo_rank.csv")
    rows = []
    for _, r in a.iterrows():
        window = "2010-19" if r["end"].startswith("2019") else "2010-24"
        rr = rank[(rank["series"] == "US") & (rank["outcome"] == r["outcome"]) & (rank["date"] == "own rule")]
        placebo = p(rr["placebo_rank_p"].iloc[0]) if window == "2010-19" and len(rr) else ""
        main_row = window == "2010-19" and r["outcome"] in ("new_share", "long_share")
        rows.append([("**" if main_row else "") + f"Jump at rule: {r['outcome']} ({window})" + ("**" if main_row else ""), f(r["level_shift"], 4), f"{r['level_se']:.4f}", p(r["level_p"]), placebo,
                     f"{int(r['weeks'])} weeks", "results/part2_incumbency/A_break_tests.csv"])
        rows.append([f"Trend change per year: {r['outcome']} ({window})", f(r["trend_change_per_yr"], 4), f"{r['trend_se']:.4f}", p(r["trend_p"]), "",
                     "", "results/part2_incumbency/A_break_tests.csv"])
        rows.append([f"Pre-rule mean: {r['outcome']}", f"{r['pre_mean']:.4f}", "", "", "", "", "results/part2_incumbency/A_break_tests.csv"])
    am = pd.read_csv(RESULTS_P2 / "annual_means.csv").set_index("Date")
    for y in ("new_share", "long_share"):
        rows.append([f"Annual mean {y}: 2014 -> 2019", f"{am.loc[2014, y]:.3f} -> {am.loc[2019, y]:.3f}", "", "", "", "", "results/part2_incumbency/annual_means.csv"])
    b = pd.read_csv(RESULTS_P2 / "B_placebo_dates.csv")
    rows += [[f"Placebo date {r['rule_date']}: jump in {r['outcome']}", f(r["level_shift"], 4), f"{r['level_se']:.4f}", p(r["level_p"]), "", "",
              "results/part2_incumbency/B_placebo_dates.csv"] for _, r in b.iterrows()]
    c = pd.read_csv(RESULTS_P2 / "C_song_chart_comparison.csv")
    rows += [[f"Song chart, jump in new-entry share: {r['chart']} (2013-19)", f(r["level_shift"], 4), f"{r['level_se']:.4f}", p(r["level_p"]), "", "",
              "results/part2_incumbency/C_song_chart_comparison.csv"] for _, r in c.iterrows()]
    d = pd.read_csv(RESULTS_P2 / "D_with_2018_break.csv")
    rows += [[f"July 2018 extra jump: {r['outcome']}", f(r["jul2018_level"], 4), "", p(r["jul2018_level_p"]), "", "",
              "results/part2_incumbency/D_with_2018_break.csv"] for _, r in d.iterrows()]
    e = pd.read_csv(RESULTS_P2 / "E_debut_first_run_break.csv").set_index("Unnamed: 0")
    rows.append(["First-run length of debuts (log weeks): jump at rule", f(e.loc["post", "coef"], 4), f"{e.loc['post', 'se']:.4f}", p(e.loc["post", "p"]), "", "",
                 "results/part2_incumbency/E_debut_first_run_break.csv"])
    rc = pd.read_csv(MATCHED / "E_riaa_control.csv")
    rows += [[f"RIAA control: {r['outcome']}, {r['model']}", f(r["tau"], 4), f"{r['tau_se']:.4f}", p(r["tau_p"]), "", "",
              "results/part2_incumbency/matched/E_riaa_control.csv"] for _, r in rc.iterrows()]
    out.append("## Part 2: chart incumbency\n\n### U.S. break, placebos, song charts, RIAA control\n\n" + table(rows))

    uk = pd.read_csv(RESULTS_P2 / "uk_comparison.csv")
    rows = []
    for _, r in uk.iterrows():
        rr = rank[(rank["series"] == r["series"]) & (rank["outcome"] == r["outcome"])]
        label = {"A UK at own rule": "own rule", "B UK placebo at U.S. date": "U.S. date (placebo)"}.get(r["test"])
        placebo = p(rr[rr["date"] == label]["placebo_rank_p"].iloc[0]) if label else ""
        rows.append([f"{r['test']}: {r['outcome']} ({r['break_date']})", f(r["tau"], 4), f"{r['tau_se']:.4f}", p(r["tau_p_nw"]), placebo,
                     f"{int(r['weeks'])} weeks", "results/part2_incumbency/uk_comparison.csv"])
    po = pd.read_csv(RESULTS_P2 / "uk_comparison_pooled.csv")
    for _, r in po[po["us_series"].str.startswith("US (200")].iterrows():
        rows.append([f"Pooled own-date jump: {r['outcome']} [{r['se']}]", f(r["tau_own"], 4), f"{r['tau_own_se']:.4f}", p(r["tau_own_p"]), "", "",
                     "results/part2_incumbency/uk_comparison_pooled.csv"])
        rows.append([f"Pooled other-date jump: {r['outcome']} [{r['se']}]", f(r["tau_other"], 4), f"{r['tau_other_se']:.4f}", p(r["tau_other_p"]),
                     f"own - other p = {p(r['own_minus_other_p'])}", "", "results/part2_incumbency/uk_comparison_pooled.csv"])
    ma = pd.read_csv(MATCHED / "A_catalogue_gap.csv")
    for _, r in ma.iterrows():
        rows.append([f"Matched catalogue gap, tau1 (Dec 2014): {r['test']}", f(r["tau1"], 4), f"{r['tau1_se']:.4f}", p(r["tau1_p_nw"]),
                     p(r["tau1_placebo_rank_p"]) + (f" (Holm {r['p_holm_main_tests']:.3f})" if not np.isnan(r["p_holm_main_tests"]) else ""),
                     f"{int(r['weeks'])} weeks", "results/part2_incumbency/matched/A_catalogue_gap.csv"])
        rows.append([f"Matched catalogue gap, tau2 (Mar 2015): {r['test']}", f(r["tau2"], 4), f"{r['tau2_se']:.4f}", p(r["tau2_p_nw"]), "", "",
                     "results/part2_incumbency/matched/A_catalogue_gap.csv"])
    mb = pd.read_csv(MATCHED / "B_first_year_runs.csv").iloc[0]
    rows.append(["Matched new releases, U.S. minus UK first-year weeks: tau1", f(mb["tau1"], 2), f"{mb['tau1_se']:.2f}", p(mb["tau1_p"]), "",
                 f"{int(mb['n_albums']):,}", "results/part2_incumbency/matched/B_first_year_runs.csv"])
    rows.append(["Matched new releases: tau2", f(mb["tau2"], 2), f"{mb['tau2_se']:.2f}", p(mb["tau2_p"]), "", "",
                 "results/part2_incumbency/matched/B_first_year_runs.csv"])
    ms = pd.read_csv(MATCHED / "matched_slot_shares_by_year.csv", index_col=0)
    rows.append(["Matched albums' share of U.S. top-100 slots, 2014 -> 2015", f"{ms.loc[2014, 'us_top100_slots_matched']:.3f} -> {ms.loc[2015, 'us_top100_slots_matched']:.3f}",
                 "", "", "", "", "results/part2_incumbency/matched/matched_slot_shares_by_year.csv"])
    out.append("### UK comparison and matched albums\n\n" + table(rows))

    # ---- Part 2b
    m = pd.read_csv(RESULTS_P2B / "results_main.csv")
    rows = [[f"{'**' if r['spec'] == 'main' and r['outcome'] == 'weeks52' else ''}{r['outcome']}: {r['spec']}{'**' if r['spec'] == 'main' and r['outcome'] == 'weeks52' else ''}",
             f(r["coef"], 3), f"{r['se_artist']:.3f}", p(r["p_artist"]), p(r["p_wildboot_genre"]) + (" (genre-clustered t)" if not np.isnan(r["p_wildboot_genre"]) else ""),
             (f"{int(r['n']):,}" if str(r["n"]).isdigit() else str(r["n"])), "results/part2b_genre_staying_power/results_main.csv"] for _, r in m.iterrows()]
    es = pd.read_csv(RESULTS_P2B / "results_event_study.csv").rename(columns={"Unnamed: 0": "year"})
    rows.append(["Event study: joint pre-2014 test", "", "", p(es["joint_pre2014_p"].iloc[0]), "", "", "results/part2b_genre_staying_power/results_event_study.csv"])
    rows += [[f"Event study {int(r['year'])} (ref 2014)", f(r["coef"], 2), f"{r['se']:.2f}", p(r["p"]), "", "",
              "results/part2b_genre_staying_power/results_event_study.csv"] for _, r in es.iterrows()]
    ex = pd.read_csv(RESULTS_P2B / "extensions.csv")
    rows += [[f"{r['spec']}", f(r["coef"], 3), f"{r['se_artist']:.3f}", p(r["p_artist"]), p(r["p_wildboot_genre"]) + " (artist-clustered t)",
              f"{int(r['n_albums']):,}", "results/part2b_genre_staying_power/extensions.csv"] for _, r in ex.iterrows()]
    rp = pd.read_csv(RESULTS_P1_SECONDARY / "rockpop_sensitivity.csv").iloc[1]
    rows.append(["genre rule: rock + pop -> pop (exploratory)", f(rp["coef"], 3), f"{rp['se_artist']:.3f}", p(rp["p_artist"]), p(rp["p_wildboot_genre"]),
                 f"{int(rp['n']):,}", "results/part1_album_length/secondary/rockpop_sensitivity.csv"])
    lo = pd.read_csv(RESULTS_FINAL_CHECKS / "part2b_leave_one_genre_out.csv").iloc[1:]
    rows += [[f"leave out {r['genre_dropped']}", f(r["coef"], 3), f"{r['se_artist']:.3f}", p(r["p_artist"]), p(r["p_wildboot_genre"]) + " (genre-clustered t)",
              f"{int(r['n_albums']):,}", "results/final_checks/part2b_leave_one_genre_out.csv"] for _, r in lo.iterrows()]
    cc = pd.read_csv(MATCHED / "C_genre_triple_difference.csv")
    for _, r in cc.iterrows():
        rows.append([f"Cross-country: heavy x post-U.S. [{r['test']}]", f(r["heavy_x_post_us"], 2), f"{r['se_us']:.2f}", p(r["p_us_artist"]),
                     p(r["p_us_wildboot_genre"]) + (f" (Holm {r['p_holm_main_tests']:.3f})" if not np.isnan(r["p_holm_main_tests"]) else ""),
                     f"{int(r['n_albums']):,}", "results/part2_incumbency/matched/C_genre_triple_difference.csv"])
        rows.append([f"Cross-country: heavy x post-UK [{r['test']}]", f(r["heavy_x_post_uk"], 2), f"{r['se_uk']:.2f}", p(r["p_uk_artist"]), "", "",
                     "results/part2_incumbency/matched/C_genre_triple_difference.csv"])
    du = pd.read_csv(MATCHED / "D_uk_part2b.csv").iloc[0]
    rows.append(["UK chart: post (Mar 2015) x heavy, weeks in first 52", f(du["coef"], 3), f"{du['se_artist']:.3f}", p(du["p_artist"]), p(du["p_wildboot_genre"]) + " (artist-clustered t)",
                 f"{int(du['n_albums']):,} of {int(du['n_uk_debuts']):,} UK debuts", "results/part2_incumbency/matched/D_uk_part2b.csv"])
    out.append("## Part 2b: genre staying power\n\n" + table(rows))
    (PAPERWRITING / "parameters.md").write_text("\n".join(out), encoding="utf-8")


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    for make in FIGURES:
        make()
    parameters()
    print("figures:", [f.__name__ for f in FIGURES])
    print("parameters.md written")


if __name__ == "__main__":
    main()
