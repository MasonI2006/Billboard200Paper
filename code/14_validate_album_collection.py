"""Validate Billboard coverage and compare MusicBrainz counts with Spotify."""

import json
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

from load_clean_data import lead_artist, load_chart, normalize_match_text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
MATCHES_PATH = DATA_DIR / "musicbrainz_artist_matches.csv"
ROSTER_PATH = DATA_DIR / "pre_rule_artist_roster.csv"
GROUPS_PATH = DATA_DIR / "musicbrainz_release_groups.csv"
ALBUMS_PATH = DATA_DIR / "musicbrainz_standard_album_candidates.csv"
SPOTIFY_PATH = DATA_DIR / "spotify_album_sample.csv"
ARTIST_CACHE_PATH = DATA_DIR / "musicbrainz_artist_search_cache.jsonl"
COVERAGE_PATH = DATA_DIR / "musicbrainz_billboard_coverage.csv"
DIFF_PATH = DATA_DIR / "musicbrainz_spotify_count_comparison.csv"

GENRE_TERMS = {
    "hiphop_rnb": ("hip hop", "hip-hop", "rap", "r&b", "soul", "grime", "trap"),
    "pop": ("pop", "dance-pop", "dance pop", "synth-pop", "electropop"),
    "latin": ("latin", "reggaeton", "salsa", "corrido", "banda", "cumbia"),
    "electronic": ("electronic", "edm", "house", "techno", "dubstep", "trance"),
    "rock": ("rock", "metal", "punk", "emo", "grunge", "indie", "alternative"),
    "country": ("country", "americana", "bluegrass", "red dirt"),
    "christian": ("christian", "gospel", "worship", "ccm"),
    "jazz": ("jazz", "bossa", "swing"),
    "classical": ("classical", "orchestral", "opera", "chamber"),
}
HEAVY = {"hiphop_rnb", "pop", "latin", "electronic"}


def normalize(value):
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return re.sub(r"[\W_]+", " ", text, flags=re.UNICODE).strip()


def genre_from_artist(response, artist_id):
    for artist in response.get("artists", []):
        if artist.get("id") != artist_id:
            continue
        text = " ".join(
            [artist.get("disambiguation", "")]
            + [tag.get("name", "") for tag in artist.get("tags", [])]
        ).casefold()
        groups = {
            genre
            for genre, terms in GENRE_TERMS.items()
            if any(term in text for term in terms)
        }
        return next(iter(groups)) if len(groups) == 1 else ""
    return ""


def load_artist_genres():
    cache = {}
    with ARTIST_CACHE_PATH.open(encoding="utf-8") as stream:
        for line in stream:
            record = json.loads(line)
            cache[record["roster_artist_key"]] = record["response"]
    matches = pd.read_csv(MATCHES_PATH, dtype=str).fillna("")
    genres = {}
    for row in matches.to_dict("records"):
        if not row["musicbrainz_artist_id"]:
            continue
        genres[row["musicbrainz_artist_id"]] = genre_from_artist(
            cache.get(row["roster_artist_key"], {}), row["musicbrainz_artist_id"]
        )
    return genres


def build_billboard_debut_keys():
    chart = load_chart("b200")
    chart = chart.loc[
        (chart["Weeks in Charts"] == 1)
        & chart["Date"].between("2009-01-01", "2024-12-31")
    ].copy()
    chart["artist_key"] = lead_artist(chart["Artist"])
    chart["title_key"] = normalize_match_text(chart["Song"])
    chart["period"] = np.where(chart["Date"] < "2014-12-10", "pre_rule", "post_rule")
    return chart


def main():
    albums = pd.read_csv(ALBUMS_PATH, dtype=str).fillna("")
    matches = pd.read_csv(MATCHES_PATH, dtype=str).fillna("")
    roster = pd.read_csv(ROSTER_PATH, dtype=str).fillna("")
    artist_genres = load_artist_genres()

    chart = build_billboard_debut_keys()
    source_names = {}
    for row in roster.to_dict("records"):
        source_names.setdefault(row["roster_artist_key"], set()).update(
            normalize(value) for value in [row["artist_name"], *row["source_credits"].split(" | ")]
        )
    resolved_name_to_id = {}
    for row in matches.to_dict("records"):
        if row["musicbrainz_artist_id"]:
            resolved_name_to_id[normalize(row["artist_name"])] = row["musicbrainz_artist_id"]
    chart["resolved_artist_id"] = chart["artist_key"].map(resolved_name_to_id)
    chart = chart.loc[chart["resolved_artist_id"].notna()].copy()
    chart["title_key"] = normalize_match_text(chart["Song"])

    albums["album_title_key"] = normalize_match_text(albums["album_title"])
    albums["artist_id_list"] = albums["artist_ids"].str.split(" | ")
    album_keys = set()
    album_genre = {}
    for row in albums.to_dict("records"):
        title = row["album_title_key"]
        ids = [artist_id for artist_id in row["artist_id_list"] if artist_id]
        for artist_id in ids:
            album_keys.add((artist_id, title))
        genres = {artist_genres.get(artist_id, "") for artist_id in ids}
        genres.discard("")
        album_genre[row["release_group_id"]] = next(iter(genres)) if len(genres) == 1 else ""

    chart["in_musicbrainz"] = [
        (artist_id, title) in album_keys
        for artist_id, title in zip(chart["resolved_artist_id"], chart["title_key"])
    ]
    chart["genre_group"] = chart["resolved_artist_id"].map(
        lambda artist_id: artist_genres.get(artist_id, "")
    )
    chart["genre_group"] = chart["genre_group"].map(
        lambda genre: "streaming_heavy" if genre in HEAVY else ("other" if genre else "unknown")
    )
    coverage = (
        chart.groupby(["genre_group", "period"], dropna=False)
        .agg(
            billboard_debut_rows=("Song", "size"),
            found_in_musicbrainz=("in_musicbrainz", "sum"),
        )
        .reset_index()
    )
    coverage["coverage_rate"] = coverage["found_in_musicbrainz"] / coverage["billboard_debut_rows"]
    coverage.to_csv(COVERAGE_PATH, index=False)

    spotify = pd.read_csv(SPOTIFY_PATH, dtype=str).fillna("")
    spotify["key"] = normalize_match_text(spotify["artist"]) + "|" + normalize_match_text(spotify["album_name"])
    spotify_counts = spotify.groupby("key", as_index=False).agg(
        spotify_tracks=("tracks", "first"),
        spotify_artist=("artist", "first"),
        spotify_album=("album_name", "first"),
    )
    album_match_rows = []
    for row in albums.to_dict("records"):
        names = set(part.strip() for part in row["roster_artist_names"].split(" | ") if part.strip())
        try:
            credits = json.loads(row["artist_credits"] or "[]")
        except json.JSONDecodeError:
            credits = []
        names.update(
            credit.get("name", "")
            for credit in credits
            if credit.get("name")
        )
        for name in names:
            album_match_rows.append(
                {
                    "release_group_id": row["release_group_id"],
                    "album_title": row["album_title"],
                    "musicbrainz_tracks": row["standard_track_count"],
                    "musicbrainz_artist": name,
                    "spotify_key": normalize(name) + "|" + normalize(row["album_title"]),
                }
            )
    album_match_frame = pd.DataFrame(album_match_rows)
    differences = album_match_frame.merge(spotify_counts, left_on="spotify_key", right_on="key", how="inner")
    differences = differences.drop_duplicates("release_group_id")
    differences["musicbrainz_tracks"] = pd.to_numeric(differences["musicbrainz_tracks"], errors="coerce")
    differences["spotify_tracks_numeric"] = pd.to_numeric(differences["spotify_tracks"], errors="coerce")
    differences["track_count_difference"] = differences["musicbrainz_tracks"] - differences["spotify_tracks_numeric"]
    differences["large_difference_flag"] = differences["track_count_difference"].abs() >= 3
    differences.to_csv(DIFF_PATH, index=False)

    print("Billboard coverage:")
    print(coverage.to_string(index=False))
    print(f"Spotify matches: {len(differences):,}; large differences (>=3 tracks): {int(differences.large_difference_flag.sum()):,}")
    print(f"Saved {COVERAGE_PATH} and {DIFF_PATH}")


if __name__ == "__main__":
    main()