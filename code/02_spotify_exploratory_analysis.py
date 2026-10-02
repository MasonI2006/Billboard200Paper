"""Run the first-round chart and album analyses without script chaining."""

import re

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from paths import RESULTS_P1_SPOTIFY, SPOTIFY_ALBUM_SAMPLE
from load_clean_data import (
    collect_artist_genres,
    classify_genre,
    lead_artist,
    load_chart,
    load_spotify_tables,
)


RULE_DATE = pd.Timestamp("2014-12-10")
OUTPUT_DIR = RESULTS_P1_SPOTIFY


def save_table(table, filename, index=False):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUTPUT_DIR / filename, index=index)


def clustered_ols(formula, data, cluster="artist"):
    return smf.ols(formula, data=data).fit(
        cov_type="cluster", cov_kwds={"groups": data[cluster]}
    )


def wild_cluster_pvalue(formula, data, coefficient, cluster, draws=499, seed=1):
    """Webb six-point restricted wild-cluster bootstrap used in the first round."""
    rng = np.random.default_rng(seed)
    restricted_formula = formula.replace(f"{coefficient} + ", "")
    restricted = smf.ols(restricted_formula, data=data).fit()
    fitted = restricted.fittedvalues
    residuals = restricted.resid
    clusters = data[cluster].to_numpy()
    unique_clusters = np.unique(clusters)
    weights = np.array(
        [-np.sqrt(1.5), -1, -np.sqrt(0.5), np.sqrt(0.5), 1, np.sqrt(1.5)]
    )

    observed = clustered_ols(formula, data, cluster=cluster)
    observed_t = observed.params[coefficient] / observed.bse[coefficient]
    outcome = formula.split("~", maxsplit=1)[0].strip()
    bootstrap_t = []

    for _ in range(draws):
        cluster_weights = dict(
            zip(unique_clusters, rng.choice(weights, size=len(unique_clusters)))
        )
        boot_data = data.copy()
        boot_data[outcome] = fitted + residuals * np.array(
            [cluster_weights[value] for value in clusters]
        )
        result = clustered_ols(formula, boot_data, cluster=cluster)
        bootstrap_t.append(result.params[coefficient] / result.bse[coefficient])

    return float((np.abs(bootstrap_t) >= abs(observed_t)).mean())


def analyze_charts():
    """Reproduce the first-round Billboard and song-chart analyses."""
    charts = {
        name: load_chart(name)
        for name in ("b200", "hot100", "streaming", "digital", "radio")
    }
    for chart in charts.values():
        chart["a"] = lead_artist(chart["Artist"])

    albums = charts["b200"]
    albums = albums.loc[
        albums["Date"].between("2010-01-01", "2024-12-31")
    ].copy()
    runs = albums.groupby(["a", "Song"]).agg(
        total_weeks=("Weeks in Charts", "max"),
        peak=("Peak Position", "min"),
    )
    debuts = albums.loc[albums["Weeks in Charts"] == 1].merge(
        runs, on=["a", "Song"], how="left"
    )
    debuts["year"] = debuts["Date"].dt.year
    debuts["post"] = (debuts["Date"] >= RULE_DATE).astype(int)

    dynamics = debuts.groupby("year").agg(
        new_albums=("Song", "size"),
        median_weeks_all=("total_weeks", "median"),
        median_weeks_top10=(
            "total_weeks",
            lambda values: values[debuts.loc[values.index, "Rank"] <= 10].median(),
        ),
    )
    save_table(dynamics, "A_b200_dynamics.csv", index=True)

    def same_week_debuts(chart_name):
        chart = charts[chart_name]
        return (
            chart.loc[chart["Weeks in Charts"] == 1]
            .groupby(["Date", "a"])
            .size()
            .rename(chart_name)
        )

    for chart_name in ("hot100", "streaming", "digital", "radio"):
        debuts = debuts.merge(
            same_week_debuts(chart_name),
            left_on=["Date", "a"],
            right_index=True,
            how="left",
        )
        debuts[chart_name] = debuts[chart_name].fillna(0)

    top10 = debuts.loc[debuts["Rank"] <= 10].copy()
    bombs = top10.groupby("year")[["hot100", "streaming", "digital", "radio"]].mean()
    bombs["share_hot100_5plus"] = top10.groupby("year")["hot100"].apply(
        lambda values: (values >= 5).mean()
    )
    save_table(bombs, "B_bombs_by_chart.csv", index=True)

    quarterly = top10.loc[top10["Date"] >= "2013-01-16"].copy()
    quarterly["quarter"] = quarterly["Date"].dt.to_period("Q").astype(str)
    save_table(
        quarterly.groupby("quarter")[["streaming", "hot100"]].mean(),
        "B2_quarterly.csv",
        index=True,
    )

    hot100 = charts["hot100"]
    song_runs = hot100.groupby(["a", "Song"]).agg(
        first=("Date", "min"),
        weeks=("Weeks in Charts", "max"),
        peak=("Peak Position", "min"),
    ).reset_index()
    album_keys = top10[["Date", "a", "year"]].drop_duplicates()
    tracks = song_runs.merge(
        album_keys, left_on=["first", "a"], right_on=["Date", "a"]
    )
    dilution = tracks.groupby("year").agg(
        n_tracks=("Song", "size"),
        share_1week=("weeks", lambda values: (values <= 1).mean()),
        share_2orless=("weeks", lambda values: (values <= 2).mean()),
        median_peak=("peak", "median"),
        share_top40=("peak", lambda values: (values <= 40).mean()),
    )
    save_table(dilution, "C_dilution.csv", index=True)

    pre_streaming = charts["streaming"].loc[
        (charts["streaming"]["Date"] >= "2013-01-16")
        & (charts["streaming"]["Date"] < RULE_DATE)
    ]
    pre_digital = charts["digital"].loc[
        (charts["digital"]["Date"] >= "2013-01-16")
        & (charts["digital"]["Date"] < RULE_DATE)
    ]
    stream_weeks = pre_streaming.groupby("a").size().rename("stream_wks")
    digital_weeks = pre_digital.groupby("a").size().rename("digital_wks")
    exposure = pd.concat([stream_weeks, digital_weeks], axis=1).fillna(0)
    exposure = exposure.loc[exposure.sum(axis=1) >= 5].copy()
    exposure["exposure"] = exposure["stream_wks"] / exposure.sum(axis=1)
    save_table(exposure.reset_index(), "D_artist_exposure.csv")

    panel = debuts.merge(exposure[["exposure"]], left_on="a", right_index=True)
    panel = panel.loc[panel["year"] <= 2019].copy()
    artists_by_period = panel.groupby("a")["post"].agg(["min", "max"])
    both_periods = artists_by_period.index[
        (artists_by_period["min"] == 0) & (artists_by_period["max"] == 1)
    ]
    panel = panel.loc[panel["a"].isin(both_periods)].copy()
    panel["ln_hot100"] = np.log1p(panel["hot100"])
    panel["exp_std"] = (panel["exposure"] - panel["exposure"].mean()) / panel[
        "exposure"
    ].std()

    did_rows = {}
    for outcome in ("ln_hot100", "hot100"):
        model = clustered_ols(
            f"{outcome} ~ post:exp_std + C(a) + C(year)", panel, cluster="a"
        )
        did_rows[outcome] = [
            model.params["post:exp_std"],
            model.bse["post:exp_std"],
            model.pvalues["post:exp_std"],
        ]
    save_table(
        pd.DataFrame(did_rows, index=["coef", "se", "p"]),
        "D_did.csv",
        index=True,
    )

    event_terms = [
        f"I((year=={year})*exp_std)" for year in range(2010, 2020) if year != 2014
    ]
    event_model = clustered_ols(
        "ln_hot100 ~ " + " + ".join(event_terms) + " + C(a) + C(year)",
        panel,
        cluster="a",
    )
    event_table = pd.DataFrame(
        {
            "coef": event_model.params.filter(regex=r"^I\(\(year"),
            "se": event_model.bse.filter(regex=r"^I\(\(year"),
        }
    )
    event_table.index = [
        int(re.search(r"(20\d\d)", term).group(1)) for term in event_table.index
    ]
    save_table(event_table.sort_index(), "D_event_study.csv", index=True)

    clean_panel = panel.loc[~panel["year"].isin([2013, 2014])].copy()
    periods = clean_panel.groupby("a")["post"].agg(["min", "max"])
    both_periods = periods.index[(periods["min"] == 0) & (periods["max"] == 1)]
    clean_panel = clean_panel.loc[clean_panel["a"].isin(both_periods)].copy()
    clean_model = clustered_ols(
        "ln_hot100 ~ post:exp_std + C(a) + C(year)",
        clean_panel,
        cluster="a",
    )
    clean_event_terms = [
        f"I((year=={year})*exp_std)"
        for year in (2010, 2011, 2015, 2016, 2017, 2018, 2019)
    ]
    clean_event = clustered_ols(
        "ln_hot100 ~ " + " + ".join(clean_event_terms) + " + C(a) + C(year)",
        clean_panel,
        cluster="a",
    )
    clean_event_table = pd.DataFrame(
        {
            "coef": clean_event.params.filter(regex=r"^I\(\(year"),
            "se": clean_event.bse.filter(regex=r"^I\(\(year"),
        }
    )
    clean_event_table.index = [
        int(re.search(r"(20\d\d)", term).group(1))
        for term in clean_event_table.index
    ]
    save_table(
        clean_event_table.sort_index(), "D2_event_study_ref2012.csv", index=True
    )
    save_table(
        pd.DataFrame(
            {
                "coef": [clean_model.params["post:exp_std"]],
                "se": [clean_model.bse["post:exp_std"]],
                "p": [clean_model.pvalues["post:exp_std"]],
                "n": [len(clean_panel)],
                "artists": [clean_panel["a"].nunique()],
            }
        ),
        "D2_did_excluding_2013_2014.csv",
    )

    top10 = top10.loc[top10["year"] <= 2019].copy()
    top10["ln_weeks"] = np.log(top10["total_weeks"])
    top10["bomb"] = np.log1p(top10["hot100"])
    payoff = smf.ols(
        "ln_weeks ~ bomb*post + C(Rank) + C(year)", data=top10
    ).fit(cov_type="HC1")
    payoff_table = pd.DataFrame(
        {"coef": payoff.params, "se": payoff.bse, "p": payoff.pvalues}
    ).loc[["bomb", "bomb:post"]]
    save_table(payoff_table, "E_payoff.csv", index=True)

    return charts, exposure


def prepare_analysis_sample(sample):
    """Restrict to albums with a genre and add binary outcome indicators."""
    analysis = sample.dropna(subset=["genre"]).copy()
    analysis["high"] = analysis["high"].astype(int)
    analysis["long18"] = (analysis["tracks"] >= 18).astype(int)
    analysis["over12"] = (analysis["tracks"] > 12).astype(int)
    return analysis


def add_event_study_terms(data, year_column, group_column, years, reference_year):
    terms = [
        f"I(({year_column}=={year})*{group_column})"
        for year in years
        if year != reference_year
    ]
    return terms


def analyze_spotify(sample, exposure):
    """Reproduce the Spotify sample, matched-sample, and robustness analyses."""
    analysis = prepare_analysis_sample(sample)

    yearly = analysis.groupby(["year", "high"])["tracks"].mean().unstack()
    yearly = yearly.rename(columns={0: "low", 1: "high"})
    yearly["n_high"] = analysis.loc[analysis["high"] == 1].groupby("year").size()
    yearly["n_low"] = analysis.loc[analysis["high"] == 0].groupby("year").size()
    save_table(yearly, "S1_tracks_by_year.csv", index=True)

    baseline_rows = []
    for outcome in ("ln_tracks", "long18", "over12"):
        formula = f"{outcome} ~ post:intensity + C(genre) + C(year)"
        model = clustered_ols(formula, analysis)
        bootstrap_p = wild_cluster_pvalue(
            formula, analysis, "post:intensity", "genre", draws=499
        )
        baseline_rows.append(
            [
                outcome,
                "genre+year FE",
                model.params["post:intensity"],
                model.bse["post:intensity"],
                model.pvalues["post:intensity"],
                bootstrap_p,
                len(analysis),
            ]
        )

    within_artist = analysis.loc[
        analysis.groupby("artist")["post"].transform("nunique") == 2
    ].copy()
    model = clustered_ols(
        "ln_tracks ~ post:intensity + C(artist) + C(year)", within_artist
    )
    baseline_rows.append(
        [
            "ln_tracks",
            "artist+year FE",
            model.params["post:intensity"],
            model.bse["post:intensity"],
            model.pvalues["post:intensity"],
            np.nan,
            len(within_artist),
        ]
    )

    analysis["trend"] = analysis["year"] - 2014
    trend_model = clustered_ols(
        "ln_tracks ~ post:intensity + C(genre) + C(year) + C(genre):trend",
        analysis,
    )
    baseline_rows.append(
        [
            "ln_tracks",
            "+ genre trends",
            trend_model.params["post:intensity"],
            trend_model.bse["post:intensity"],
            trend_model.pvalues["post:intensity"],
            np.nan,
            len(analysis),
        ]
    )
    baseline = pd.DataFrame(
        baseline_rows,
        columns=[
            "outcome",
            "spec",
            "coef",
            "se_artist",
            "p_artist",
            "p_wildboot_genre",
            "n",
        ],
    )
    save_table(baseline, "S2_did.csv")

    event_years = [year for year in range(2009, 2025) if year != 2014]
    event_terms = add_event_study_terms(
        analysis, "year", "intensity", event_years, 2014
    )
    event_model = clustered_ols(
        "ln_tracks ~ "
        + " + ".join(event_terms)
        + " + C(genre) + C(year)",
        analysis,
    )
    event_table = pd.DataFrame(
        {
            "coef": event_model.params.filter(regex=r"^I\(\(year"),
            "se": event_model.bse.filter(regex=r"^I\(\(year"),
        }
    )
    event_table.index = [
        int(re.search(r"(20\d\d)", term).group(1)) for term in event_table.index
    ]
    save_table(event_table.sort_index(), "S3_event_study.csv", index=True)

    variants = []

    def add_variant(label, formula, data):
        model = clustered_ols(formula, data)
        coefficient = next(
            name for name in model.params.index if name.startswith("post:")
        )
        variants.append(
            [
                label,
                coefficient,
                model.params[coefficient],
                model.bse[coefficient],
                model.pvalues[coefficient],
                len(data),
            ]
        )

    for outcome in ("ln_tracks", "long18", "over12"):
        add_variant(
            f"binary high, {outcome}",
            f"{outcome} ~ post:high + C(genre) + C(year)",
            analysis,
        )
    add_variant(
        "binary, excl electronic",
        "ln_tracks ~ post:high + C(genre) + C(year)",
        analysis.loc[analysis["genre"] != "electronic"],
    )
    add_variant(
        "binary, window 2010-19",
        "ln_tracks ~ post:high + C(genre) + C(year)",
        analysis.loc[analysis["year"].between(2010, 2019)],
    )
    hiphop_rock_country = analysis.loc[
        analysis["genre"].isin(["hiphop_rnb", "rock", "country"])
    ]
    add_variant(
        "hiphop vs rock+country only",
        "ln_tracks ~ post:high + C(genre) + C(year)",
        hiphop_rock_country,
    )
    add_variant(
        "over12, hiphop vs rock+country",
        "over12 ~ post:high + C(genre) + C(year)",
        hiphop_rock_country,
    )

    matched = analysis.loc[analysis["billboard_debut"]].copy()
    add_variant(
        "Billboard-200 albums only",
        "ln_tracks ~ post:high + C(genre) + C(year)",
        matched,
    )
    artist_exposure = exposure.reset_index().rename(columns={"a": "artist_key"})
    analysis["artist_key"] = (
        analysis["artist"].str.lower().str.split(
            r" featuring | & | and | x | with |, ", regex=True
        ).str[0].str.strip()
    )
    exposed = analysis.merge(
        artist_exposure[["artist_key", "exposure"]], on="artist_key", how="inner"
    )
    exposed["exp_std"] = (exposed["exposure"] - exposed["exposure"].mean()) / exposed[
        "exposure"
    ].std()
    add_variant(
        "artist exposure (Kaggle), ln_tracks",
        "ln_tracks ~ post:exp_std + C(genre) + C(year)",
        exposed,
    )
    variant_table = pd.DataFrame(
        variants, columns=["spec", "term", "coef", "se", "p", "n"]
    )
    save_table(variant_table, "S4_did_variants.csv")

    event_sample = matched.copy()
    event_sample["yr"] = event_sample["year"].clip(lower=2010)
    matched_event_terms = add_event_study_terms(
        event_sample,
        "yr",
        "high",
        range(2010, 2025),
        2014,
    )
    matched_event = clustered_ols(
        "ln_tracks ~ "
        + " + ".join(matched_event_terms)
        + " + C(genre) + C(yr)",
        event_sample,
    )
    matched_event_table = pd.DataFrame(
        {
            "coef": matched_event.params.filter(regex=r"^I\(\(yr"),
            "se": matched_event.bse.filter(regex=r"^I\(\(yr"),
        }
    )
    matched_event_table.index = [
        int(re.search(r"(20\d\d)", term).group(1))
        for term in matched_event_table.index
    ]
    save_table(
        matched_event_table.sort_index(), "S5_event_study_bb200_binary.csv", index=True
    )
    pre_parameters = [
        name
        for name in matched_event.params.index
        if re.search(r"yr ?== ?(2010|2011|2012|2013)\)", name)
    ]
    restriction = np.vstack(
        [(matched_event.params.index == name).astype(float) for name in pre_parameters]
    )
    pretrend_p = float(matched_event.wald_test(restriction, scalar=True).pvalue)

    track_data, clean_track_data = load_spotify_tables()
    genres_by_artist = collect_artist_genres(track_data, clean_track_data)
    track_data = track_data.copy()
    track_data["genre"] = track_data["artist_name"].map(
        lambda artist: classify_genre(artist, genres_by_artist)
    )
    track_analysis = track_data.merge(
        analysis[["album_id", "post", "high", "ln_tracks", "tracks", "genre", "year"]],
        on="album_id",
        suffixes=("_track", ""),
    )
    track_analysis["pos"] = track_analysis["track_number"] / track_analysis["tracks"]
    track_analysis = track_analysis.dropna(
        subset=[
            "track_popularity",
            "artist_popularity",
            "pos",
            "genre",
            "year",
        ]
    )
    dilution_model = clustered_ols(
        "track_popularity ~ ln_tracks*post*high + pos + artist_popularity + C(genre) + C(year)",
        track_analysis,
        cluster="artist_name",
    )
    dilution_terms = [
        "ln_tracks",
        "ln_tracks:post",
        "ln_tracks:high",
        "ln_tracks:post:high",
        "pos",
    ]
    dilution_table = pd.DataFrame(
        {
            "coef": dilution_model.params,
            "se": dilution_model.bse,
            "p": dilution_model.pvalues,
        }
    ).loc[dilution_terms]
    save_table(dilution_table, "S6_dilution_popularity.csv", index=True)

    stress_specs = [
        (
            "BB200, continuous intensity",
            "ln_tracks ~ post:intensity + C(genre) + C(year)",
            matched,
        ),
        (
            "BB200, continuous, excl electronic",
            "ln_tracks ~ post:intensity + C(genre) + C(year)",
            matched.loc[matched["genre"] != "electronic"],
        ),
        (
            "BB200, binary, over12",
            "over12 ~ post:high + C(genre) + C(year)",
            matched,
        ),
        (
            "BB200, binary, long18",
            "long18 ~ post:high + C(genre) + C(year)",
            matched,
        ),
        (
            "BB200, binary, 2010-2019",
            "ln_tracks ~ post:high + C(genre) + C(year)",
            matched.loc[matched["year"].between(2010, 2019)],
        ),
        (
            "BB200, binary, artist FE",
            "ln_tracks ~ post:high + C(artist) + C(year)",
            matched,
        ),
    ]
    stress_rows = []
    for label, formula, data in stress_specs:
        model = clustered_ols(formula, data)
        coefficient = next(
            name for name in model.params.index if name.startswith("post:")
        )
        stress_rows.append(
            [
                label,
                model.params[coefficient],
                model.bse[coefficient],
                model.pvalues[coefficient],
                len(data),
            ]
        )
    stress_table = pd.DataFrame(
        stress_rows, columns=["spec", "coef", "se", "p", "n"]
    )
    save_table(stress_table, "S7_bb200_variants.csv")
    bootstrap_p = wild_cluster_pvalue(
        "ln_tracks ~ post:high + C(genre) + C(year)",
        matched,
        "post:high",
        "genre",
        draws=499,
    )

    non_charting = analysis.loc[~analysis["album_id"].isin(matched["album_id"])].copy()
    non_chart_model = clustered_ols(
        "ln_tracks ~ post:high + C(genre) + C(year)", non_charting
    )
    save_table(
        pd.DataFrame(
            {
                "coef": [non_chart_model.params["post:high"]],
                "se": [non_chart_model.bse["post:high"]],
                "p": [non_chart_model.pvalues["post:high"]],
                "n": [len(non_charting)],
            }
        ),
        "S7_non_billboard_result.csv",
    )

    periods = pd.cut(
        matched["year"],
        [2008, 2011, 2014, 2017, 2020, 2024],
        labels=["2009-11", "2012-14", "2015-17", "2018-20", "2021-24"],
    )
    period_sample = matched.assign(period=periods)
    period_table = period_sample.groupby(["period", "high"], observed=True).agg(
        tracks=("tracks", "mean"), over12=("over12", "mean"), n=("tracks", "size")
    )
    save_table(period_table.unstack(), "S8_bb200_periods.csv", index=True)

    main_model = clustered_ols(
        "ln_tracks ~ post:high + C(genre) + C(year)", matched
    )
    print(
        f"Sample: {len(sample)} core albums, {len(analysis)} with genre, "
        f"{len(matched)} genre-coded Billboard debuts."
    )
    print(
        "Billboard-only high x post on log songs: "
        f"{main_model.params['post:high']:.3f} "
        f"(SE {main_model.bse['post:high']:.3f}, "
        f"p={main_model.pvalues['post:high']:.3f})."
    )
    print(f"Matched-sample pre-trend joint test p={pretrend_p:.3f}.")
    print(f"Genre-cluster wild-bootstrap p={bootstrap_p:.3f}.")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    charts, exposure = analyze_charts()
    sample = pd.read_csv(
        SPOTIFY_ALBUM_SAMPLE,
        parse_dates=["release_date", "billboard_date"],
    )
    analyze_spotify(sample, exposure)
    print(f"Saved clean analysis tables to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()