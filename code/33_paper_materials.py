"""Paper materials: figures and the parameter list in paperwriting/, read straight from results files.

Every number in paperwriting/parameters.md is pulled from a results CSV named in its row, so the
list regenerates with the pipeline. Figures go to paperwriting/figures/. No estimation here.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from paths import (ANALYSIS_SAMPLE, PAPERWRITING, RESULTS_FINAL_CHECKS, RESULTS_P1, RESULTS_P1_SECONDARY,
                   RESULTS_P2, RESULTS_P2B, RIAA_REVENUE_BY_CATEGORY)

FIG = PAPERWRITING / "figures"
MATCHED = RESULTS_P2 / "matched"
US_ISSUE = pd.Timestamp("2014-12-13")
UK_RULE = pd.Timestamp("2015-03-01")
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / name, dpi=200)
    plt.close(fig)


# ---------------- figures ----------------
def fig_riaa():
    r = pd.read_csv(RIAA_REVENUE_BY_CATEGORY)
    r = r[r["year"].between(2005, 2019)]
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    for col, label in (("physical_nominal", "Physical"), ("digital_downloads_nominal", "Downloads"),
                       ("streaming_nominal", "Streaming")):
        ax.plot(r["year"], r[col] / 1e9, marker="o", ms=3, label=label)
    ax.set_ylabel("U.S. revenue, $ billion (nominal)")
    ax2 = ax.twinx()
    ax2.plot(r["year"], 100 * r["streaming_share"], color="black", ls=":", label="Streaming share (right axis)")
    ax2.set_ylabel("Streaming share of revenue, %")
    ax2.spines["top"].set_visible(False)
    ax.axvline(2014.95, color="tab:red", ls="--", lw=1)
    ax.text(2014.95, ax.get_ylim()[1], " Billboard rule", color="tab:red", va="top", fontsize=8)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=7, loc="center left")
    save(fig, "fig01_riaa_revenue.png")


def fig_part1_means():
    a = pd.read_csv(ANALYSIS_SAMPLE)
    m = a.groupby(["year", "heavy"])["standard_tracks"].mean().unstack()
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    ax.plot(m.index, m[1], marker="o", ms=3, label="Streaming-heavy genres")
    ax.plot(m.index, m[0], marker="s", ms=3, label="Other genres")
    ax.axvline(2014.9, color="tab:red", ls="--", lw=1)
    ax.set_xlabel("Release year"); ax.set_ylabel("Mean tracks, standard edition")
    ax.legend(fontsize=8)
    save(fig, "fig02_part1_mean_tracks_by_year.png")


def coef_plot(ax, x, b, se, ref=None):
    ax.errorbar(x, b, yerr=1.96 * np.asarray(se), fmt="o", ms=4, capsize=2, lw=1)
    ax.axhline(0, color="grey", lw=0.8)
    if ref is not None:
        ax.plot([ref], [0], "o", ms=4, color="tab:blue", mfc="white")


def fig_part1_event():
    e = pd.read_csv(RESULTS_P1_SECONDARY / "event_study.csv")
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    coef_plot(ax, e["year"], e["coef"], e["se_artist"], ref=2014)
    ax.axvline(2014.5, color="tab:red", ls="--", lw=1)
    ax.set_xlabel("Release year (2014 = reference)")
    ax.set_ylabel("Streaming-heavy minus other,\nlog tracks")
    ax.set_title(f"Joint pre-2014 test p = {e['joint_pre2014_p'].iloc[0]:.2f}", fontsize=9)
    save(fig, "fig03_part1_event_study.png")


def fig_part1_thresholds():
    t = pd.read_csv(RESULTS_P1_SECONDARY / "long_albums_thresholds.csv")
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    ax.errorbar(t["threshold"], t["coef"], yerr=[t["coef"] - t["ci_low"], t["ci_high"] - t["coef"]],
                fmt="o", ms=4, capsize=2, lw=1)
    ax.axhline(0, color="grey", lw=0.8)
    ax.set_xlabel("Track-count threshold k")
    ax.set_ylabel("Post x streaming-heavy,\nshare of albums with >= k tracks")
    save(fig, "figA1_part1_threshold_profile.png")


def fig_part2_series():
    s = pd.read_csv(RESULTS_P2 / "uk_us_weekly_series.csv", parse_dates=["Date"])
    fig, axes = plt.subplots(2, 1, figsize=(6.5, 5.2), sharex=True)
    for ax, y, title in ((axes[0], "new_share", "Share of chart slots held by new entries"),
                         (axes[1], "long_share", "Share of chart slots held by albums with 52+ weeks on chart")):
        for name, label in (("US", "U.S. Billboard 200"), ("UK", "UK Official Albums Chart")):
            d = s[s["country"] == name]
            ax.plot(d["Date"], d[y].rolling(8, center=True).mean(), lw=1.2, label=label)
        ax.axvline(US_ISSUE, color="tab:red", ls="--", lw=1)
        ax.axvline(UK_RULE, color="tab:blue", ls="--", lw=1)
        ax.set_title(title, fontsize=9)
    axes[0].legend(fontsize=8)
    axes[1].set_xlabel("8-week centred averages; dashed lines: U.S. rule (red), UK rule (blue)")
    save(fig, "fig04_part2_us_uk_series.png")


def fig_part2_event():
    e = pd.read_csv(RESULTS_FINAL_CHECKS / "event_study_monthly.csv")
    fig, axes = plt.subplots(2, 2, figsize=(7, 5), sharex=True)
    order = [("U.S. (rule Dec 2014)", "new_share"), ("UK (rule Mar 2015)", "new_share"),
             ("U.S. (rule Dec 2014)", "long_share"), ("UK (rule Mar 2015)", "long_share")]
    names = {"new_share": "new-entry share", "long_share": "52+-week share"}
    for ax, (series, y) in zip(axes.ravel(), order):
        d = e[(e["series"] == series) & (e["outcome"] == y)]
        ax.errorbar(d["rel_month"], d["coef"], yerr=1.96 * d["se"], fmt="o", ms=2.5, lw=0.7)
        ax.axhline(0, color="grey", lw=0.8)
        ax.axvline(-0.5, color="tab:red", ls="--", lw=1)
        ax.set_title(f"{series}: {names[y]}", fontsize=9)
    for ax in axes[-1]:
        ax.set_xlabel("Months relative to own rule")
    save(fig, "fig05_part2_event_study_monthly.png")


def fig_part2_placebo():
    dist = pd.read_csv(RESULTS_P2 / "uk_comparison_placebo_distribution.csv")
    rank = pd.read_csv(RESULTS_P2 / "uk_comparison_placebo_rank.csv")
    fig, axes = plt.subplots(1, 2, figsize=(7, 2.8))
    for ax, y, title in ((axes[0], "new_share", "New-entry share"), (axes[1], "long_share", "52+-week share")):
        d = dist[(dist["series"] == "US") & (dist["outcome"] == y)]
        r = rank[(rank["series"] == "US") & (rank["outcome"] == y) & (rank["date"] == "own rule")].iloc[0]
        ax.hist(d["tau"], bins=40, color="lightgrey", edgecolor="grey")
        ax.axvline(r["tau"], color="tab:red", lw=1.5)
        ax.set_title(f"{title}: rule-date jump vs {int(r['n_fake_dates'])} fake dates\n(placebo-rank p = {r['placebo_rank_p']:.3f})", fontsize=8)
        ax.set_xlabel("Estimated jump")
    save(fig, "figA2_part2_placebo_distribution.png")


def fig_matched_gap():
    g = pd.read_csv(MATCHED / "A_weekly_gap_series.csv", parse_dates=["week"])
    fig, ax = plt.subplots(figsize=(6.5, 3))
    ax.plot(g["week"], (g["us_present"] - g["uk_present"]).rolling(8, center=True).mean(), color="black", lw=1.2)
    ax.axvline(US_ISSUE, color="tab:red", ls="--", lw=1)
    ax.axvline(UK_RULE, color="tab:blue", ls="--", lw=1)
    ax.axhline(0, color="grey", lw=0.8)
    ax.set_ylabel("Matched catalogue albums:\nU.S. top 100 minus UK top 100")
    ax.set_xlabel("8-week centred average")
    save(fig, "figA3_part2_matched_catalogue_gap.png")


def fig_part2b_event():
    e = pd.read_csv(RESULTS_P2B / "results_event_study.csv").rename(columns={"Unnamed: 0": "year"})
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    coef_plot(ax, e["year"], e["coef"], e["se"], ref=2014)
    ax.axvline(2014.5, color="tab:red", ls="--", lw=1)
    ax.set_xlabel("Debut year (2014 = reference)")
    ax.set_ylabel("Streaming-heavy minus other,\nweeks on chart in first 52")
    ax.set_title(f"Joint pre-2014 test p = {e['joint_pre2014_p'].iloc[0]:.2f}", fontsize=9)
    save(fig, "fig06_part2b_event_study.png")


def fig_part2b_loo():
    l = pd.read_csv(RESULTS_FINAL_CHECKS / "part2b_leave_one_genre_out.csv")
    l = l.iloc[::-1]
    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    y = np.arange(len(l))
    ax.errorbar(l["coef"], y, xerr=1.96 * l["se_artist"], fmt="o", ms=4, capsize=2, lw=1)
    ax.set_yticks(y, ["Full sample" if g.startswith("(") else f"Drop {g}" for g in l["genre_dropped"]])
    ax.axvline(0, color="grey", lw=0.8)
    ax.axvline(l["coef"].iloc[-1], color="tab:blue", ls=":", lw=1)
    ax.set_xlabel("Post x streaming-heavy, weeks on chart in first 52 (95% CI, artist-clustered)")
    save(fig, "figA4_part2b_leave_one_genre_out.png")


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
    for make in (fig_riaa, fig_part1_means, fig_part1_event, fig_part1_thresholds, fig_part2_series, fig_part2_event,
                 fig_part2_placebo, fig_matched_gap, fig_part2b_event, fig_part2b_loo):
        make()
    parameters()
    print("figures:", sorted(x.name for x in FIG.glob("*.png")))
    print("parameters.md written")


if __name__ == "__main__":
    main()
