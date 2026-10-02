"""Build the Spotify studio-album sample and match Billboard 200 debuts."""

import numpy as np
import pandas as pd

from load_clean_data import (
    DATA_DIR,
    GENRE_INTENSITY,
    classify_genre,
    collect_artist_genres,
    load_chart,
    load_spotify_tables,
    normalize_match_text,
    spotify_lead_artist,
)


REISSUE_PATTERN = (
    r"deluxe|expanded|edition|version|anniversary|remaster|live|greatest|best of|"
    r"collection|hits|complete|reissue|bonus|extended|\(.*vol"
)


def build_album_sample():
    """Return one row per qualifying 2009-2024 Spotify studio album."""
    tracks, clean_tracks = load_spotify_tables()
    genres_by_artist = collect_artist_genres(tracks, clean_tracks)

    tracks = tracks.copy()
    tracks["genre"] = tracks["artist_name"].map(
        lambda artist: classify_genre(artist, genres_by_artist)
    )
    tracks["intensity"] = tracks["genre"].map(GENRE_INTENSITY)

    albums = (
        tracks.sort_values("track_popularity", ascending=False)
        .groupby("album_id")
        .agg(
            album_name=("album_name", "first"),
            artist=("artist_name", "first"),
            album_type=("album_type", "first"),
            release_date=("release_date", "first"),
            year=("year", "first"),
            tracks=("album_total_tracks", "first"),
            genre=("genre", "first"),
            intensity=("intensity", "first"),
            artist_pop=("artist_popularity", "first"),
            n_sampled=("track_id", "size"),
        )
        .reset_index()
    )

    albums["reissue_flag"] = albums["album_name"].str.lower().str.contains(
        REISSUE_PATTERN, regex=True, na=False
    )
    sample = albums.loc[
        (albums["album_type"] == "album")
        & (albums["genre"] != "soundtrack")
        & ~albums["reissue_flag"]
        & albums["year"].between(2009, 2024)
        & (albums["tracks"] >= 6)
    ].copy()
    sample["post"] = (sample["release_date"] >= "2014-11-24").astype(int)
    sample["ln_tracks"] = np.log(sample["tracks"])
    sample["high"] = np.where(
        sample["intensity"].notna(), (sample["intensity"] >= 1.9).astype(int), np.nan
    )

    chart = load_chart("b200")
    debuts = chart.loc[
        (chart["Weeks in Charts"] == 1) & (chart["Date"] >= "2009-01-01")
    ].copy()
    debuts["match_key"] = normalize_match_text(
        spotify_lead_artist(debuts["Artist"])
    ) + "|" + normalize_match_text(debuts["Song"])
    debuts = debuts[["match_key", "Date", "Rank"]].drop_duplicates("match_key")

    sample["match_key"] = normalize_match_text(
        spotify_lead_artist(sample["artist"])
    ) + "|" + normalize_match_text(sample["album_name"])
    sample = sample.merge(debuts, on="match_key", how="left")
    sample = sample.rename(columns={"Date": "billboard_date", "Rank": "billboard_rank"})
    sample["billboard_debut"] = sample["billboard_date"].notna()
    return sample


def main():
    sample = build_album_sample()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    sample.to_csv(DATA_DIR / "spotify_album_sample.csv", index=False)
    genre_sample = sample.dropna(subset=["genre"])
    print(
        f"Saved {len(sample)} core albums; "
        f"{len(genre_sample)} have a genre; "
        f"{sample['billboard_debut'].sum()} total and "
        f"{genre_sample['billboard_debut'].sum()} genre-coded albums match a Billboard 200 debut."
    )
    print("Genre counts:")
    print(sample["genre"].value_counts(dropna=False).to_string())


if __name__ == "__main__":
    main()