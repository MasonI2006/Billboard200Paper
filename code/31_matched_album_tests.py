"""Matched U.S.-UK album tests A-F (docs/matched_albums_plan.md, written before estimation).

A: weekly U.S.-minus-UK top-100 presence of matched catalogue albums, jumps at Dec 2014 and Mar 2015.
B: album-level U.S.-minus-UK first-year top-100 weeks for simultaneous releases.
C: genre triple difference on B's outcome (Part 2b labels).
D: Part 2b on the UK chart (post = debut on/after 2015-03-01).
E: Part 2 time series with the RIAA streaming share as a control.
F: figure.
Weeks are UK chart weeks (Sunday start); a U.S. stored date S maps to the UK week S - 3 days
(the UK week containing the Billboard issue date S + 3). Debuts use each chart's own
weeks-on-chart count (true first chart week), backdated for albums first seen after 2000.
"""

import importlib
import unicodedata

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from inference import fit_clustered, wild_bootstrap_pvalue
from paths import (ANALYSIS_SAMPLE, ARTIST_GENRES, ARTIST_MATCHES, PART2_WEEKLY, RAW_BILLBOARD200,
                   RESULTS_P2, RIAA_REVENUE_BY_CATEGORY, UK_ALBUMS_WEEKLY)

matching = importlib.import_module("30_match_us_uk_albums")
OUT = RESULTS_P2 / "matched"
J1 = pd.Timestamp("2014-12-07")   # UK week containing the first U.S. rule issue (2014-12-13)
J2 = pd.Timestamp("2015-03-01")   # first UK chart including streams
US_RULE_STORED = pd.Timestamp("2014-12-10")
WEEK = pd.Timedelta(days=7)


def nz21(series):
    """Normaliser of 21_part2b_build.py (used for the Part 2b artist -> MusicBrainz ID map)."""
    s = series.fillna("").astype(str).map(lambda x: unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode())
    return s.str.lower().str.replace(r"[^a-z0-9 ]", "", regex=True).str.replace(r"\s+", " ", regex=True).str.strip()


def labels():
    """Part 2b labels (Part 1 sample, via the artist's MusicBrainz match) and the per-artist file."""
    m = pd.read_csv(ARTIST_MATCHES, low_memory=False)
    m = m[m["musicbrainz_artist_id"].notna()]
    name2id = dict(zip(nz21(m["artist_name"]), m["musicbrainz_artist_id"]))
    a = pd.read_csv(ANALYSIS_SAMPLE)
    first_id = a["artist_ids"].astype(str).str.extract(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})")[0]
    part2b = (pd.DataFrame({"mbid": first_id, "genre": a["genre"], "heavy": a["heavy"]})
              .dropna().drop_duplicates("mbid").set_index("mbid"))
    artist_file = pd.read_csv(ARTIST_GENRES).set_index("musicbrainz_artist_id")[["artist_name", "genre", "heavy"]]
    return name2id, part2b, artist_file


def load_panels(matches):
    us = matching.load_us()
    extra = pd.read_csv(RAW_BILLBOARD200, dtype=str, low_memory=False, usecols=["Date", "Weeks in Charts"])
    us["woc"] = pd.to_numeric(extra.loc[us.index, "Weeks in Charts"], errors="coerce")
    uk = matching.load_uk()
    us = us.merge(matches[["album_id", "us_tkey", "us_akey"]], left_on=["tkey", "akey"], right_on=["us_tkey", "us_akey"])
    uk = uk.merge(matches[["album_id", "uk_tkey", "uk_akey"]], left_on=["tkey", "akey"], right_on=["uk_tkey", "uk_akey"])
    us["week"] = us["Date"] - pd.Timedelta(days=3)
    return us, uk


def debuts(us, uk):
    """True debut per chart: the week with weeks-on-chart 1; otherwise backdated from the first observed week."""
    def first(frame, date, woc):
        f = frame.sort_values(date).groupby("album_id").first()
        return f[date] - (f[woc].fillna(1) - 1) * WEEK, f
    us_debut, us_first = first(us, "week", "woc")
    uk_debut, uk_first = first(uk, "chart_week", "weeks_on_chart")
    us_true = us[us["woc"] == 1].groupby("album_id").agg(us_debut_week=("week", "min"), us_debut_stored=("Date", "min"),
                                                         us_debut_rank=("Rank", "first"))
    uk_true = uk[uk["weeks_on_chart"] == 1].groupby("album_id").agg(uk_debut_week=("chart_week", "min"))
    out = pd.DataFrame({"debut_any": pd.concat([us_debut, uk_debut], axis=1).min(axis=1)})
    return out.join(us_true).join(uk_true)


# ---------- A ----------
def gap_series(us, uk, deb, us_max_rank):
    weeks = sorted(set(uk["chart_week"]).intersection(set(us["week"])))
    weeks = [w for w in weeks if pd.Timestamp("2010-01-01") <= w <= pd.Timestamp("2019-12-31")]
    us_in = us[us["Rank"] <= us_max_rank].groupby("week")["album_id"].apply(set)
    uk_in = uk.groupby("chart_week")["album_id"].apply(set)
    debut_any = deb["debut_any"]
    rows = []
    for w in weeks:
        catalogue = set(debut_any.index[debut_any <= w - 52 * WEEK])
        n_us = len(us_in.get(w, set()) & catalogue)
        n_uk = len(uk_in.get(w, set()) & catalogue)
        rows.append({"week": w, "n_catalogue": len(catalogue), "us_present": n_us, "uk_present": n_uk,
                     "D": (n_us - n_uk) / len(catalogue)})
    return pd.DataFrame(rows)


def gap_model(series, j1, j2, trends=False):
    d = series.copy()
    d["t"] = (d["week"] - d["week"].min()).dt.days / 365.25
    d["j1"] = (d["week"] >= j1).astype(int)
    d["j2"] = (d["week"] >= j2).astype(int)
    d["woy"] = d["week"].dt.isocalendar().week.astype(int)
    f = "D ~ t + j1 + j2 + C(woy)"
    if trends:
        d["tp1"] = d["j1"] * (d["week"] - j1).dt.days.clip(lower=0) / 365.25
        d["tp2"] = d["j2"] * (d["week"] - j2).dt.days.clip(lower=0) / 365.25
        f += " + tp1 + tp2"
    return smf.ols(f, d).fit(cov_type="HAC", cov_kwds={"maxlags": 12})


def test_a(us, uk, deb):
    main = gap_series(us, uk, deb, 100)
    full = gap_series(us, uk, deb, 200)
    rows = []
    for label, series, trends in (("A main: U.S. top 100", main, False), ("A secondary: + trend changes", main, True),
                                  ("A secondary: full Billboard 200", full, False)):
        m = gap_model(series, J1, J2, trends)
        rows.append({"test": label, "weeks": int(m.nobs), "pre_mean_D": series.loc[series["week"] < J1, "D"].mean(),
                     "tau1": m.params["j1"], "tau1_se": m.bse["j1"], "tau1_p_nw": m.pvalues["j1"],
                     "tau2": m.params["j2"], "tau2_se": m.bse["j2"], "tau2_p_nw": m.pvalues["j2"]})
        print(f"  {label:32s} tau1={m.params['j1']:+.4f} (NW p={m.pvalues['j1']:.3f}) "
              f"tau2={m.params['j2']:+.4f} (NW p={m.pvalues['j2']:.3f})", flush=True)
    # placebo-rank p for tau1: same two-jump model shifted (f, f + 12 weeks)
    spacing = J2 - J1
    fakes = [w for w in main["week"] if pd.Timestamp("2011-01-01") <= w <= pd.Timestamp("2018-12-31")
             and all(abs((w - t).days) > 26 * 7 for t in (J1, J2))]
    taus = np.array([gap_model(main, f, f + spacing).params["j1"] for f in fakes])
    p_rank = (1 + np.sum(np.abs(taus) >= abs(rows[0]["tau1"]))) / (len(taus) + 1)
    rows[0]["tau1_placebo_rank_p"] = p_rank
    rows[0]["n_fake_dates"] = len(taus)
    print(f"  A tau1 placebo-rank p = {p_rank:.3f} ({len(taus)} fake dates)", flush=True)
    pd.DataFrame({"fake_date": fakes, "tau1": taus}).to_csv(OUT / "A_placebo_distribution.csv", index=False)
    main.to_csv(OUT / "A_weekly_gap_series.csv", index=False)
    return pd.DataFrame(rows), main


# ---------- B, C ----------
def first_year_weeks(frame, date, debut, album_debut):
    f = frame.merge(album_debut.rename(debut), left_on="album_id", right_index=True)
    within = f[(f[date] >= f[debut]) & (f[date] < f[debut] + 52 * WEEK)]
    return within.groupby("album_id")[date].nunique()


def album_sample(us, uk, deb, matches):
    d = deb.dropna(subset=["us_debut_week", "uk_debut_week"]).copy()
    d = d[(d["us_debut_rank"] <= 100) & ((d["us_debut_week"] - d["uk_debut_week"]).abs() <= 8 * WEEK)]
    d["debut"] = d[["us_debut_week", "uk_debut_week"]].min(axis=1)
    d = d[d["debut"].between("2010-01-01", "2018-12-31")]
    us100 = us[us["Rank"] <= 100]
    d["us_weeks52"] = first_year_weeks(us100, "Date", "us_debut", d["us_debut_stored"])
    d["uk_weeks52"] = first_year_weeks(uk, "chart_week", "uk_debut", d["uk_debut_week"])
    d[["us_weeks52", "uk_weeks52"]] = d[["us_weeks52", "uk_weeks52"]].fillna(0)
    d["diff"] = d["us_weeks52"] - d["uk_weeks52"]
    d["t_debut"] = (d["debut"] - pd.Timestamp("2010-01-01")).dt.days / 365.25
    d["post_us"] = (d["debut"] >= J1).astype(int)
    d["post_uk"] = (d["debut"] >= J2).astype(int)
    d["month"] = d["debut"].dt.month
    d["year"] = d["debut"].dt.year
    return d.join(matches.set_index("album_id")[["us_title", "us_artist", "uk_album", "uk_artist", "us_akey"]])


def test_b(d):
    m = smf.ols("diff ~ t_debut + post_us + post_uk + C(month)", d).fit(cov_type="cluster", cov_kwds={"groups": d["us_akey"]})
    row = {"test": "B first-year top-100 weeks, U.S. minus UK", "n_albums": len(d), "n_artists": d["us_akey"].nunique(),
           "mean_diff_pre": d.loc[d["post_us"] == 0, "diff"].mean(),
           "tau1": m.params["post_us"], "tau1_se": m.bse["post_us"], "tau1_p": m.pvalues["post_us"],
           "tau2": m.params["post_uk"], "tau2_se": m.bse["post_uk"], "tau2_p": m.pvalues["post_uk"]}
    print(f"  B n={len(d)} tau1={row['tau1']:+.2f} (p={row['tau1_p']:.3f}) tau2={row['tau2']:+.2f} (p={row['tau2_p']:.3f})", flush=True)
    return pd.DataFrame([row])


def test_c(d, name2id, part2b, artist_file):
    d = d.copy()
    d["mbid"] = nz21(d["us_artist"]).map(name2id)
    rows = []
    for label, table, bootstrap in (("C main: Part 2b labels (Part 1 sample)", part2b, True),
                                    ("C secondary: per-artist file labels", artist_file, False)):
        s = d.join(table[["genre", "heavy"]], on="mbid").dropna(subset=["genre"]).reset_index(drop=True)
        s["heavy"] = s["heavy"].astype(int)
        rhs = ["post_us:heavy", "post_uk:heavy", "C(genre)", "C(year)"]
        m = fit_clustered("diff ~ " + " + ".join(rhs), s, cluster="mbid")
        p_boot = wild_bootstrap_pvalue(s, "diff", rhs, "post_us:heavy", robust_cluster="mbid")[0] if bootstrap else np.nan
        rows.append({"test": label, "n_albums": len(s), "n_artists": s["mbid"].nunique(), "n_heavy": int(s["heavy"].sum()),
                     "heavy_x_post_us": m.params["post_us:heavy"], "se_us": m.bse["post_us:heavy"],
                     "p_us_artist": m.pvalues["post_us:heavy"], "p_us_wildboot_genre": p_boot,
                     "heavy_x_post_uk": m.params["post_uk:heavy"], "se_uk": m.bse["post_uk:heavy"],
                     "p_uk_artist": m.pvalues["post_uk:heavy"]})
        print(f"  {label:40s} n={len(s)} heavy x post_US={rows[-1]['heavy_x_post_us']:+.2f} (p={rows[-1]['p_us_artist']:.3f}, "
              f"boot p={p_boot:.3f}) heavy x post_UK={rows[-1]['heavy_x_post_uk']:+.2f} (p={rows[-1]['p_uk_artist']:.3f})", flush=True)
    return pd.DataFrame(rows)


# ---------- D ----------
def test_d(matches, us, name2id, part2b, artist_file):
    uk = pd.read_csv(UK_ALBUMS_WEEKLY, parse_dates=["chart_week"])
    uk = uk[~uk["no1_unidentified"]].copy()
    uk["tkey"], uk["akey"] = matching.title_key(uk["album"]), matching.norm(uk["artist"])
    deb = uk[(uk["weeks_on_chart"] == 1) & uk["chart_week"].between("2010-01-01", "2018-12-31")].drop_duplicates(["tkey", "akey"])
    deb = deb[["tkey", "akey", "album", "artist", "chart_week"]].rename(columns={"chart_week": "debut"})
    runs = uk.merge(deb[["tkey", "akey", "debut"]], on=["tkey", "akey"])
    runs = runs[(runs["chart_week"] >= runs["debut"]) & (runs["chart_week"] < runs["debut"] + 52 * WEEK)]
    deb = deb.merge(runs.groupby(["tkey", "akey"])["chart_week"].nunique().rename("weeks52"), on=["tkey", "akey"])
    # label source 1: matched U.S. album's artist (Part 2b labels)
    mm = matches[["uk_tkey", "uk_akey", "us_artist"]].rename(columns={"uk_tkey": "tkey", "uk_akey": "akey"})
    deb = deb.merge(mm, on=["tkey", "akey"], how="left")
    deb["mbid"] = nz21(deb["us_artist"]).map(name2id)
    deb = deb.join(part2b[["genre", "heavy"]], on="mbid")
    deb["label_source"] = np.where(deb["genre"].notna(), "matched U.S. album (Part 2b labels)", "")
    # label source 2: per-artist file by normalised name (exact, else prefix for capped names); ambiguous dropped
    names = artist_file.assign(key=nz21(artist_file["artist_name"])).reset_index()
    by_name = names.groupby("key")
    need = deb["genre"].isna()
    for i in deb.index[need]:
        key = nz21(pd.Series([deb.at[i, "artist"]]))[0]
        if key in by_name.groups:
            hit = by_name.get_group(key)
        elif len(deb.at[i, "artist"]) >= matching.UK_ARTIST_CAP:
            hit = names[names["key"].str.startswith(key)]
        else:
            continue
        if hit["musicbrainz_artist_id"].nunique() == 1:
            deb.at[i, "mbid"] = hit["musicbrainz_artist_id"].iloc[0]
            deb.at[i, "genre"] = hit["genre"].iloc[0]
            deb.at[i, "heavy"] = hit["heavy"].iloc[0]
            deb.at[i, "label_source"] = "per-artist file by name"
    s = deb.dropna(subset=["genre"]).reset_index(drop=True)
    s["heavy"] = s["heavy"].astype(int)
    s["post"] = (s["debut"] >= J2).astype(int)
    s["year"] = s["debut"].dt.year
    rhs = ["post:heavy", "C(genre)", "C(year)"]
    m = fit_clustered("weeks52 ~ " + " + ".join(rhs), s, cluster="mbid")
    p_boot = wild_bootstrap_pvalue(s, "weeks52", rhs, "post:heavy", robust_cluster="mbid")[0]
    row = {"test": "D UK Part 2b: weeks in first 52, post x heavy (post = debut >= 2015-03-01)",
           "n_uk_debuts": len(deb), "n_albums": len(s), "share_labelled": len(s) / len(deb), "n_artists": s["mbid"].nunique(),
           "label_sources": s["label_source"].value_counts().to_dict(), "coef": m.params["post:heavy"],
           "se_artist": m.bse["post:heavy"], "p_artist": m.pvalues["post:heavy"], "p_wildboot_genre": p_boot,
           "means_by_group": s.groupby(["heavy", "post"])["weeks52"].mean().round(2).to_dict()}
    print(f"  D n={len(s)} of {len(deb)} UK debuts labelled; post x heavy={row['coef']:+.2f} "
          f"(p={row['p_artist']:.3f}, boot p={p_boot:.3f})", flush=True)
    return pd.DataFrame([row])


# ---------- E ----------
def test_e():
    w = pd.read_csv(PART2_WEEKLY, parse_dates=["Date"])
    w = w[w["Date"].between("2010-01-06", "2019-12-25")].copy()
    r = pd.read_csv(RIAA_REVENUE_BY_CATEGORY)
    points = pd.DataFrame({"date": pd.to_datetime(r["year"].astype(str) + "-07-01"),
                           "share": r["streaming_share"], "log_rev": np.log(r["streaming_nominal"].where(r["streaming_nominal"] > 0))})
    days = (points["date"] - pd.Timestamp("2000-01-01")).dt.days.to_numpy()
    x = (w["Date"] - pd.Timestamp("2000-01-01")).dt.days.to_numpy()
    w["stream_share"] = np.interp(x, days, points["share"].to_numpy())
    w["log_stream_rev"] = np.interp(x, days, points["log_rev"].to_numpy())
    w["t"] = (w["Date"] - w["Date"].min()).dt.days / 365.25
    w["post"] = (w["Date"] >= US_RULE_STORED).astype(int)
    w["t_post"] = w["post"] * (w["Date"] - US_RULE_STORED).dt.days.clip(lower=0) / 365.25
    w["woy"] = w["Date"].dt.isocalendar().week.astype(int)
    rows = []
    for y in ("new_share", "long_share"):
        for label, extra in (("Part 2 model (no control)", ""), ("+ streaming share", " + stream_share"),
                             ("+ log streaming revenue", " + log_stream_rev"), ("+ both", " + stream_share + log_stream_rev")):
            m = smf.ols(f"{y} ~ t + post + t_post + C(woy){extra}", w).fit(cov_type="HAC", cov_kwds={"maxlags": 12})
            rows.append({"outcome": y, "model": label, "tau": m.params["post"], "tau_se": m.bse["post"],
                         "tau_p": m.pvalues["post"], "trend_change": m.params["t_post"], "trend_change_p": m.pvalues["t_post"]})
            print(f"  E {y:10s} {label:28s} tau={m.params['post']:+.4f} (p={m.pvalues['post']:.3f})", flush=True)
    return pd.DataFrame(rows)


# ---------- F ----------
def figure(gap):
    s = pd.read_csv(RESULTS_P2 / "uk_us_weekly_series.csv", parse_dates=["Date"])
    fig, axes = plt.subplots(3, 1, figsize=(9, 10), sharex=True)
    for ax, y, title in ((axes[0], "new_share", "Share of chart slots held by new entries"),
                         (axes[1], "long_share", "Share of chart slots held by albums with 52+ weeks on chart")):
        for name, style in (("US", "-"), ("UK", "-")):
            d = s[s["country"] == name]
            ax.plot(d["Date"], d[y].rolling(4, center=True).mean(), style, label=f"{name} (4-week average)", lw=1.2)
        ax.set_title(title, fontsize=10)
    axes[2].plot(gap["week"], gap["D"].rolling(4, center=True).mean(), color="black", lw=1.2)
    axes[2].set_title("Matched catalogue albums: U.S. top-100 presence minus UK top-100 presence", fontsize=10)
    for ax in axes:
        ax.axvline(pd.Timestamp("2014-12-13"), color="tab:red", ls="--", lw=1)
        ax.axvline(J2, color="tab:blue", ls="--", lw=1)
    axes[0].legend(fontsize=8)
    axes[2].text(pd.Timestamp("2014-12-13"), axes[2].get_ylim()[1], " U.S. rule", color="tab:red", fontsize=8, va="top", ha="right")
    axes[2].text(J2, axes[2].get_ylim()[1], " UK rule", color="tab:blue", fontsize=8, va="top")
    fig.tight_layout()
    fig.savefig(OUT / "fig_us_uk_series.png", dpi=150)


def holm(p):
    p = np.asarray(p, dtype=float)
    order = np.argsort(p)
    adj, running = np.empty(len(p)), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(p) - rank) * p[i]))
        adj[i] = running
    return adj


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    matches = pd.read_csv(matching.MATCHES)
    us, uk = load_panels(matches)
    deb = debuts(us, uk)
    name2id, part2b, artist_file = labels()
    print(f"matched albums {len(matches)}; with U.S. true debut {deb['us_debut_week'].notna().sum()}, "
          f"UK true debut {deb['uk_debut_week'].notna().sum()}", flush=True)
    print("A. Catalogue gap", flush=True)
    a, gap = test_a(us, uk, deb)
    print("B/C. Album-level", flush=True)
    sample = album_sample(us, uk, deb, matches)
    b = test_b(sample)
    c = test_c(sample, name2id, part2b, artist_file)
    print("D. UK Part 2b", flush=True)
    d = test_d(matches, us, name2id, part2b, artist_file)
    print("E. RIAA control", flush=True)
    e = test_e()
    figure(gap)
    adjusted = holm([a.loc[0, "tau1_placebo_rank_p"], c.loc[0, "p_us_wildboot_genre"]])
    a.loc[0, "p_holm_main_tests"] = adjusted[0]
    c.loc[0, "p_holm_main_tests"] = adjusted[1]
    print(f"Holm across the two main tests: A {adjusted[0]:.3f}, C {adjusted[1]:.3f}", flush=True)
    a.to_csv(OUT / "A_catalogue_gap.csv", index=False)
    b.to_csv(OUT / "B_first_year_runs.csv", index=False)
    c.to_csv(OUT / "C_genre_triple_difference.csv", index=False)
    d.to_csv(OUT / "D_uk_part2b.csv", index=False)
    e.to_csv(OUT / "E_riaa_control.csv", index=False)
    sample.to_csv(OUT / "B_album_sample.csv", index=False)
    print("done", flush=True)


if __name__ == "__main__":
    main()
