"""Part 1: album-order control and the remaining frozen-plan secondary checks.

Specifications are fixed in docs/items4_5_plan.md (sections 2-3), written before estimation.
"""

import math

import numpy as np
import pandas as pd

from inference import fit_clustered, within_fe_design, wild_bootstrap_pvalue
from load_clean_data import GENRE_INTENSITY
from musicbrainz_helpers import build_data, headline_selection
from paths import RELEASE_GROUPS, RESULTS_P1, RESULTS_P1_SECONDARY, ROSTER

FE = ["C(genre)", "C(year)"]
ORDER_BINS = [0, 1, 2, 3, 5, 9, np.inf]
ORDER_LABELS = ["1", "2", "3", "4-5", "6-9", "10+"]


def prepare(data):
    data = data[data["genre"].ne("")].copy()
    data["ln_standard_tracks"] = data["standard_tracks"].map(math.log)
    data["over12"] = (data["standard_tracks"] > 12).astype(int)
    data["long18"] = (data["standard_tracks"] >= 18).astype(int)
    data["year"] = data["year"].astype(int)
    for column in ("running_time_minutes", "tracks_with_duration"):   # build_data reads these as text
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data["lead_id"] = data["artist_ids"].astype(str).str.split(" | ", regex=False).str[0]
    return data.reset_index(drop=True)


def order_bin(ordinal):
    return pd.cut(ordinal, ORDER_BINS, labels=ORDER_LABELS).astype(str)


def career_order(data):
    """Ordinal among the lead artist's MusicBrainz studio albums since career start."""
    groups = pd.read_csv(RELEASE_GROUPS, dtype=str,
                         usecols=["release_group_id", "first_release_date", "eligible_headline_type", "roster_artist_ids"]).fillna("")
    groups = groups[(groups["eligible_headline_type"] == "True") & (groups["first_release_date"] != "")].copy()
    groups["date"] = pd.to_datetime(groups["first_release_date"], format="mixed", errors="coerce")
    groups = groups.dropna(subset=["date"])
    first_date = dict(zip(groups["release_group_id"], groups["date"]))
    by_artist = {}
    for ids, group_id, date in zip(groups["roster_artist_ids"], groups["release_group_id"], groups["date"]):
        for artist_id in ids.split(" | "):
            if artist_id:
                by_artist.setdefault(artist_id, []).append((date, group_id))
    ordinals = []
    for artist_id, group_id, release_date in zip(data["lead_id"], data["release_group_id"], data["release_date"]):
        own = (first_date.get(group_id, release_date), group_id)
        ordinals.append(1 + sum(1 for item in by_artist.get(artist_id, []) if item < own))
    return pd.Series(ordinals, index=data.index)


def since_2009_order(data):
    """Ordinal among the lead artist's eligible standard-album candidates since 2009."""
    pool = build_data(select=lambda c: c["mixtape_street_robustness"] != "True")
    pool = pool[pool["standard_tracks"] >= 6]
    pool["lead_id"] = pool["artist_ids"].astype(str).str.split(" | ", regex=False).str[0]
    by_artist = pool.groupby("lead_id").apply(lambda g: sorted(zip(g["release_date"], g["release_group_id"]))).to_dict()
    return pd.Series([1 + sum(1 for item in by_artist.get(a, []) if item < (d, g))
                      for a, d, g in zip(data["lead_id"], data["release_date"], data["release_group_id"])], index=data.index)


def estimate(label, sample, outcome, rhs, term, note="", intercept=True, bootstrap=True):
    formula = f"{outcome} ~ " + " + ".join(rhs) + ("" if intercept else " - 1")
    model = fit_clustered(formula, sample)
    boot_p = wild_bootstrap_pvalue(sample, outcome, rhs, term, intercept=intercept)[0] if bootstrap else np.nan
    row = {"check": label, "outcome": outcome, "term": term, "n_albums": len(sample),
           "n_artists": sample["artist_cluster"].nunique(), "n_genre_clusters": sample["genre"].nunique(),
           "coef": model.params[term], "se_artist": model.bse[term], "p_artist": model.pvalues[term],
           "p_wildboot_genre": boot_p, "note": note}
    print(f"  {label:42s} coef={row['coef']:+.4f} se={row['se_artist']:.4f} p={row['p_artist']:.3f} "
          f"boot_p={boot_p:.3f} n={row['n_albums']}", flush=True)
    return row


def main():
    data = prepare(build_data())
    base = ["post:heavy", *FE]
    headline = pd.read_csv(RESULTS_P1 / "headline.csv").iloc[0]
    rows = [{"check": "0 headline (baseline, from step 17)", "outcome": "ln_standard_tracks", "term": "post:heavy",
             "n_albums": int(headline["n_albums"]), "n_artists": int(headline["n_artists"]), "n_genre_clusters": 9,
             "coef": headline["coef_post_by_streaming_heavy"], "se_artist": headline["se_artist_cluster"],
             "p_artist": headline["p_artist_cluster"], "p_wildboot_genre": headline["p_wildboot_genre_webb_9999"], "note": ""}]

    # album order (career start = main; since 2009 = alternate)
    data["order_career"] = order_bin(career_order(data))
    data["order_2009"] = order_bin(since_2009_order(data))
    print("Career-order bins:", data["order_career"].value_counts().to_dict(), flush=True)
    print("Since-2009-order bins:", data["order_2009"].value_counts().to_dict(), flush=True)
    rows.append(estimate("album order: career start (main)", data, "ln_standard_tracks", base + ["C(order_career)"], "post:heavy",
                         "bins 1,2,3,4-5,6-9,10+ over MusicBrainz studio albums since career start"))
    rows.append(estimate("album order: since 2009 (alternate)", data, "ln_standard_tracks", base + ["C(order_2009)"], "post:heavy",
                         "bins over eligible standard-album candidates since 2009"))

    # a. artist fixed effects (within-artist demeaning)
    within, terms = within_fe_design(data, "ln_standard_tracks", data["post"] * data["heavy"])
    both = within.groupby("artist_cluster")["post"].nunique().eq(2).sum()
    rows.append(estimate("a artist fixed effects", within, "y_w", terms, "x_w",
                         f"within-artist; single-album artists dropped; {both} artists with pre and post albums", intercept=False))

    # b. drop albums released on or before the lead artist's first qualifying debut
    roster = pd.read_csv(ROSTER, dtype=str)
    debut = dict(zip(roster["artist_name"], pd.to_datetime(roster["first_qualifying_debut"])))
    debut_date = data["artist_cluster"].map(debut)
    kept = data[debut_date.notna() & (data["release_date"] > debut_date)]
    rows.append(estimate("b drop albums on/before first debut", kept, "ln_standard_tracks", base, "post:heavy",
                         f"{int(debut_date.isna().sum())} albums without a roster debut date also dropped"))

    # c. mixtape/street robustness sample
    def with_mixtapes(c):
        year = c["release_date"].str[:4]
        mixtape = (c["mixtape_street_robustness"] == "True") & year.between("2009", "2019") & ~(
            (c["release_date_precision"] == "year") & (year == "2014"))
        return headline_selection(c) | mixtape
    mix = prepare(build_data(select=with_mixtapes))
    rows.append(estimate("c including Mixtape/Street", mix, "ln_standard_tracks", base, "post:heavy",
                         f"{len(mix) - len(data)} Mixtape/Street albums added"))

    # d. 2009-2024 window
    wide = prepare(build_data(select=lambda c: (c["secondary_window_2009_2024"] == "True")
                              & (c["2014_year_only_exclude_headline"] != "True")))
    rows.append(estimate("d 2009-2024 window", wide, "ln_standard_tracks", base, "post:heavy",
                         "2018 and 2020 rule changes inside the window, not modelled"))

    # e. 2010-2019 window
    rows.append(estimate("e 2010-2019 window", data[data["year"] >= 2010], "ln_standard_tracks", base, "post:heavy"))

    # f. continuous genre intensity
    data["intensity"] = data["genre"].map(GENRE_INTENSITY)
    rows.append(estimate("f continuous intensity", data, "ln_standard_tracks", ["post:intensity", *FE], "post:intensity",
                         "Nielsen 2014 streaming/sales ratio"))

    # g. exclude electronic
    rows.append(estimate("g exclude electronic", data[data["genre"] != "electronic"], "ln_standard_tracks", base, "post:heavy"))

    # h-j. alternative outcomes
    full = data[(data["tracks_with_duration"] == data["standard_tracks"]) & (data["running_time_minutes"] > 0)].copy()
    full["ln_running_time"] = np.log(full["running_time_minutes"])
    rows.append(estimate("h log running time", full, "ln_running_time", base, "post:heavy", "albums with all track durations"))
    rows.append(estimate("i more than 12 tracks", data, "over12", base, "post:heavy", "linear probability"))
    rows.append(estimate("j 18 or more tracks", data, "long18", base, "post:heavy", "linear probability"))

    RESULTS_P1_SECONDARY.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(RESULTS_P1_SECONDARY / "plan_checks.csv", index=False)


if __name__ == "__main__":
    main()
