"""Compare frozen MusicBrainz counts with cached digital-edition counts."""

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
CANDIDATES_PATH = DATA_DIR / "musicbrainz_standard_album_candidates.csv"
RELEASES_PATH = DATA_DIR / "musicbrainz_official_releases.csv"
MATCHES_PATH = DATA_DIR / "musicbrainz_artist_matches.csv"
CACHE_PATH = DATA_DIR / "musicbrainz_artist_search_cache.jsonl"
OUTPUT_PATH = DATA_DIR / "musicbrainz_digital_robustness.csv"
RULE_DATE = pd.Timestamp("2014-11-24")
HEAVY_GENRES = {"hiphop_rnb", "pop", "latin", "electronic"}

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_musicbrainz_collection import infer_row_genre, read_artist_cache  # noqa: E402


def digital_track_counts():
    counts = defaultdict(list)
    releases = pd.read_csv(
        RELEASES_PATH,
        usecols=["release_group_id", "release_id", "date", "track_count_sum_media", "media_json"],
        dtype=str,
    ).fillna("")
    for row in releases.itertuples(index=False):
        try:
            media = json.loads(row.media_json)
        except (TypeError, json.JSONDecodeError):
            continue
        formats = {str(item.get("format", "")).casefold() for item in media}
        identifiable = any(
            "digital" in fmt or "download" in fmt or "stream" in fmt or fmt == "file"
            for fmt in formats
        )
        if identifiable and row.date:
            counts[row.release_group_id].append(
                {
                    "digital_date": row.date,
                    "digital_release_id": row.release_id,
                    "digital_tracks": pd.to_numeric(row.track_count_sum_media, errors="coerce"),
                    "digital_formats": " | ".join(sorted(formats)),
                }
            )
    selected = {}
    for group_id, rows in counts.items():
        earliest_date = min(row["digital_date"] for row in rows)
        same_day = [row for row in rows if row["digital_date"] == earliest_date]
        selected[group_id] = min(
            same_day,
            key=lambda row: (row["digital_tracks"] if pd.notna(row["digital_tracks"]) else float("inf"), row["digital_release_id"]),
        )
    return pd.DataFrame.from_dict(selected, orient="index").rename_axis("release_group_id").reset_index()


def build_data():
    candidates = pd.read_csv(CANDIDATES_PATH, dtype=str).fillna("")
    candidates = candidates[
        (candidates["headline_window_2009_2019"] == "True")
        & (candidates["2014_year_only_exclude_headline"] != "True")
    ].copy()
    candidates["release_date"] = pd.to_datetime(candidates["release_date"], errors="coerce")
    candidates["standard_tracks"] = pd.to_numeric(candidates["standard_track_count"], errors="coerce")
    candidates["year"] = candidates["release_date"].dt.year
    candidates["post"] = (candidates["release_date"] >= RULE_DATE).astype(int)

    matches = pd.read_csv(MATCHES_PATH, dtype=str).fillna("")
    cache = read_artist_cache()
    genre_by_id = {}
    for row in matches.to_dict("records"):
        genre = infer_row_genre(row, cache.get(row["roster_artist_key"], {}))
        if genre and row["musicbrainz_artist_id"]:
            genre_by_id[row["musicbrainz_artist_id"]] = genre

    def candidate_genre(value):
        for artist_id in str(value).split(" | "):
            if artist_id in genre_by_id:
                return genre_by_id[artist_id]
        return ""

    candidates["genre"] = candidates["artist_ids"].map(candidate_genre)
    candidates["heavy"] = candidates["genre"].isin(HEAVY_GENRES).astype(int)
    candidates["artist_cluster"] = candidates["roster_artist_names"].str.split(" | ").str[0]
    candidates = candidates.dropna(subset=["release_date", "year"])
    candidates = candidates[candidates["standard_tracks"] >= 6].copy()
    digital = digital_track_counts()
    return candidates.merge(digital, on="release_group_id", how="left")


def estimate(data, outcome, label):
    sample = data.dropna(subset=[outcome]).copy()
    model = smf.ols(
        f"{outcome} ~ post:heavy + C(genre) + C(year)",
        data=sample,
    ).fit(cov_type="cluster", cov_kwds={"groups": sample["artist_cluster"]})
    term = "post:heavy"
    return {
        "spec": label,
        "outcome": outcome,
        "n_albums": len(sample),
        "coef": model.params.get(term, float("nan")),
        "se_artist_cluster": model.bse.get(term, float("nan")),
        "p_artist_cluster": model.pvalues.get(term, float("nan")),
        "direction": "positive" if model.params.get(term, 0) > 0 else "negative",
    }


def wild_bootstrap_pvalue(data, outcome, draws=9999, seed=20260928):
    sample = data.dropna(subset=[outcome]).copy()
    formula = f"{outcome} ~ post:heavy + C(genre) + C(year)"
    restricted_formula = f"{outcome} ~ C(genre) + C(year)"
    model = smf.ols(formula, data=sample).fit(
        cov_type="cluster", cov_kwds={"groups": sample["artist_cluster"]}
    )
    restricted = smf.ols(restricted_formula, data=sample).fit()
    fitted = restricted.fittedvalues.to_numpy()
    residuals = restricted.resid.to_numpy()
    clusters = sample["genre"].to_numpy()
    unique_clusters = np.unique(clusters)
    weights = np.array([-math.sqrt(1.5), -1, -math.sqrt(0.5), math.sqrt(0.5), 1, math.sqrt(1.5)])
    rng = np.random.default_rng(seed)
    observed = model.params["post:heavy"] / model.bse["post:heavy"]
    simulated = []
    response_column = outcome
    for _ in range(draws):
        weight_map = dict(zip(unique_clusters, rng.choice(weights, len(unique_clusters))))
        bootstrap = sample.copy()
        bootstrap[response_column] = fitted + residuals * np.array([weight_map[x] for x in clusters])
        fitted_bootstrap = smf.ols(formula, data=bootstrap).fit(
            cov_type="cluster", cov_kwds={"groups": bootstrap["artist_cluster"]}
        )
        simulated.append(
            fitted_bootstrap.params["post:heavy"] / fitted_bootstrap.bse["post:heavy"]
        )
    return float(np.mean(np.abs(simulated) >= abs(observed)))


def main():
    data = build_data()
    data["ln_standard_tracks"] = data["standard_tracks"].map(math.log)
    data["ln_digital_tracks"] = pd.to_numeric(data["digital_tracks"], errors="coerce").map(
        lambda value: math.log(value) if pd.notna(value) and value > 0 else float("nan")
    )
    known = data[data["genre"].ne("")].copy()
    digital_known = known.dropna(subset=["digital_tracks"]).copy()
    rows = []
    for sample, outcome, label in [
        (known, "ln_standard_tracks", "standard_frozen_all_known_genre"),
        (digital_known, "ln_standard_tracks", "standard_same_digital_sample"),
        (digital_known, "ln_digital_tracks", "digital_alternate_same_sample"),
    ]:
        row = estimate(sample, outcome, label)
        row["p_wildboot_genre"] = ""
        rows.append(row)
    report = pd.DataFrame(rows)
    report["digital_identifiable"] = len(digital_known)
    report["digital_missing"] = len(known) - len(digital_known)
    report["count_affected"] = int(
        (digital_known["standard_tracks"] != pd.to_numeric(digital_known["digital_tracks"])).sum()
    )
    report.to_csv(OUTPUT_PATH, index=False)
    print(report.round(4).to_string(index=False))
    print(
        f"Known-genre albums: {len(known):,}; digital editions: {len(digital_known):,}; "
        f"missing digital format: {len(known) - len(digital_known):,}; "
        f"different counts: {int((digital_known['standard_tracks'] != pd.to_numeric(digital_known['digital_tracks'])).sum()):,}"
    )


if __name__ == "__main__":
    main()
