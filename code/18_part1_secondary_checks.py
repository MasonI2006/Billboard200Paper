"""Part 1 secondary checks, rebuilt from the Claude-chat versions (docs/part1_secondary_rerun_plan.md).

Default: current headline sample (ordered genre rule).
Validation: --sample <path> --tag old_labels runs the same code on the superseded 09-28 labels.
"""

import argparse
import math
import unicodedata

import numpy as np
import pandas as pd

from inference import fit_clustered, wild_bootstrap_pvalue
from musicbrainz_helpers import read_artist_cache
from paths import ANALYSIS_SAMPLE, ARTIST_MATCHES, RAW_BILLBOARD200, RESULTS_P1_SECONDARY

FE = ["C(genre)", "C(year)"]
UK_AREAS = {"United Kingdom", "England", "Scotland", "Wales", "Northern Ireland"}
SELECTION_RHS = ["ln_standard_tracks", "ln_standard_tracks:post", "ln_standard_tracks:heavy",
                 "ln_standard_tracks:post:heavy", "post:heavy", *FE]
TRIPLE = "ln_standard_tracks:post:heavy"


def nz(series):
    """Chat-era normaliser: ASCII-fold, lowercase, keep a-z 0-9 and spaces."""
    s = series.fillna("").astype(str).map(
        lambda x: unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode())
    return s.str.lower().str.replace(r"[^a-z0-9 ]", "", regex=True).str.replace(r"\s+", " ", regex=True).str.strip()


def add_chart_flags(data):
    """charted, debut_rank, ln_weeks from Billboard 200 rows matched on (artist ID, title)."""
    matches = pd.read_csv(ARTIST_MATCHES, dtype=str).fillna("")
    matches = matches[matches["musicbrainz_artist_id"] != ""]
    name_to_id = dict(zip(nz(matches["artist_name"]), matches["musicbrainz_artist_id"]))
    chart = pd.read_csv(RAW_BILLBOARD200, dtype=str, low_memory=False)
    chart["Date"] = pd.to_datetime(chart["Date"], errors="coerce")
    chart["Rank"] = pd.to_numeric(chart["Rank"], errors="coerce")
    chart["mbid"] = nz(chart["Artist"]).map(name_to_id)
    chart = chart.dropna(subset=["mbid", "Date"])
    chart["title_key"] = nz(chart["Song"])
    runs = (chart.sort_values("Date")
            .groupby(["mbid", "title_key"])
            .agg(first_date=("Date", "first"), debut_rank=("Rank", "first"), weeks=("Date", "nunique")))
    runs = runs.to_dict("index")
    title_keys = nz(data["album_title"])
    found = []
    for ids, title in zip(data["artist_ids"].astype(str).str.split(" | "), title_keys):
        hits = [runs[(i, title)] for i in ids if (i, title) in runs]
        found.append(min(hits, key=lambda h: h["first_date"]) if hits else None)
    data["charted"] = [int(h is not None) for h in found]
    data["debut_rank"] = [h["debut_rank"] if h else np.nan for h in found]
    data["ln_weeks"] = [math.log(h["weeks"]) if h else np.nan for h in found]
    return data


def add_uk_flag(data):
    matches = pd.read_csv(ARTIST_MATCHES, dtype=str).fillna("")
    cache = read_artist_cache()
    area = {}
    for row in matches.to_dict("records"):
        artist_id = row["musicbrainz_artist_id"]
        if not artist_id:
            continue
        for artist in cache.get(row["roster_artist_key"], {}).get("artists", []):
            if artist.get("id") == artist_id:
                area[artist_id] = (artist.get("area") or {}).get("name", "")
                break
    first_artist = data["artist_ids"].astype(str).str.split(" | ").str[0]
    data["uk"] = first_artist.map(lambda i: int(area.get(i, "") in UK_AREAS))
    return data


def result(label, sample, outcome, rhs, term, bootstrap, kind):
    model = fit_clustered(f"{outcome} ~ " + " + ".join(rhs), sample)
    row = {
        "check": label, "kind": kind, "outcome": outcome, "term": term,
        "n_albums": len(sample), "n_artists": sample["artist_cluster"].nunique(),
        "n_genre_clusters": sample["genre"].nunique(),
        "coef": model.params[term], "se_artist": model.bse[term], "p_artist": model.pvalues[term],
        "p_wildboot_genre": np.nan,
    }
    if bootstrap:
        row["p_wildboot_genre"], _ = wild_bootstrap_pvalue(sample, outcome, rhs, term)
    print(f"  {label:38s} coef={row['coef']:+.4f} se={row['se_artist']:.4f} p={row['p_artist']:.3f}"
          f" boot_p={row['p_wildboot_genre']:.3f} n={row['n_albums']}", flush=True)
    return row


def event_study(data):
    years = sorted(int(y) for y in data["year"].unique() if int(y) != 2014)
    for y in years:
        data[f"hy_{y}"] = data["heavy"] * (data["year"] == y)
    terms = [f"hy_{y}" for y in years]
    model = fit_clustered("ln_standard_tracks ~ " + " + ".join(terms + FE), data)
    table = pd.DataFrame({"year": years, "coef": model.params[terms].to_numpy(),
                          "se_artist": model.bse[terms].to_numpy(), "p_artist": model.pvalues[terms].to_numpy()})
    pre = [f"hy_{y}" for y in years if y < 2014]
    joint = model.wald_test(", ".join(f"{t} = 0" for t in pre), scalar=True)
    return table, float(joint.pvalue)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", default=str(ANALYSIS_SAMPLE))
    parser.add_argument("--tag", default="")
    args = parser.parse_args()
    suffix = f"_{args.tag}" if args.tag else ""

    data = pd.read_csv(args.sample)
    data = data[data["genre"].notna()].reset_index(drop=True)
    data["year"] = data["year"].astype(int)
    data = add_chart_flags(add_uk_flag(data))
    data["multi_edition"] = data["same_day_different_length_editions"].astype(str).str.casefold().eq("true").astype(int)
    full = data["tracks_with_duration"] == data["standard_tracks"]
    data["ln_sec_per_track"] = np.where(
        full & (data["running_time_minutes"] > 0),
        np.log(data["running_time_minutes"] * 60 / data["tracks_with_duration"].where(full)), np.nan)
    print(f"Sample: {len(data)} albums; charted {int(data['charted'].sum())}; "
          f"UK {int(data['uk'].sum())} (post-rule {int((data['uk'] & data['post']).sum())})", flush=True)

    charted = data[data["charted"] == 1]
    rows = [
        result("1 charted subsample", charted, "ln_standard_tracks", ["post:heavy", *FE], "post:heavy", True, "secondary"),
        result("2 non-charted subsample", data[data["charted"] == 0], "ln_standard_tracks", ["post:heavy", *FE], "post:heavy", True, "secondary"),
        result("3 selection test", data, "charted", SELECTION_RHS, TRIPLE, True, "secondary"),
        result("4a payoff: debut rank", charted, "debut_rank", SELECTION_RHS, TRIPLE, True, "secondary"),
        result("4b payoff: log weeks on chart", charted, "ln_weeks", SELECTION_RHS, TRIPLE, True, "secondary"),
        result("6a seconds per track", data.dropna(subset=["ln_sec_per_track"]), "ln_sec_per_track", ["post:heavy", *FE], "post:heavy", False, "exploratory"),
        result("6b day-one multi-edition launch", data, "multi_edition", ["post:heavy", *FE], "post:heavy", False, "exploratory"),
        result("6c UK origin x post, >12 tracks", data, "over12", ["uk", "post:uk", *FE], "post:uk", False, "exploratory"),
    ]
    table, joint_p = event_study(data)
    print(table.round(4).to_string(index=False))
    print(f"  joint pre-2014 test p = {joint_p:.3f}")

    RESULTS_P1_SECONDARY.mkdir(parents=True, exist_ok=True)
    out = pd.DataFrame(rows)
    out["labels"] = args.tag or "ordered_rule"
    out.to_csv(RESULTS_P1_SECONDARY / f"secondary_checks{suffix}.csv", index=False)
    table["joint_pre2014_p"] = joint_p
    table.to_csv(RESULTS_P1_SECONDARY / f"event_study{suffix}.csv", index=False)


if __name__ == "__main__":
    main()
