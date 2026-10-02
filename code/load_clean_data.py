"""Shared data loading and normalization for the Billboard 200 project."""

import ast
import re
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "OriginalDataFiles"
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"

GENRE_RULES = [
    ("latin", r"latin|reggaeton|urbano|corrido|banda|mariachi|norte|cumbia|bachata|salsa|trap latino|mexican"),
    ("hiphop_rnb", r"hip hop|rap|trap|drill|r&b|soul|crunk|grime|phonk|plugg|rage"),
    ("country", r"country|bluegrass|americana|red dirt"),
    ("christian", r"christian|worship|gospel|ccm"),
    ("jazz", r"jazz|bossa|swing"),
    ("soundtrack", r"soundtrack|anime|video game|musical|broadway"),
    ("classical", r"classical|orchestral|opera|chamber|medieval|neoclassical"),
    (
        "electronic",
        r"edm|house|techno|electro|dubstep|trance|drum and bass|dnb|bass music|moombahton|big room|brostep|hardstyle|garage",
    ),
    ("rock", r"rock|metal|punk|emo|grunge|indie|alternative|folk|shoegaze|hardcore"),
    ("pop", r"pop"),
]

GENRE_INTENSITY = {
    "electronic": 3.40,
    "latin": 2.08,
    "hiphop_rnb": 2.05,
    "pop": 1.95,
    "rock": 0.74,
    "country": 0.54,
    "christian": 0.44,
    "jazz": 0.15,
    "classical": 0.14,
}

CHART_FILES = {
    "b200": "billboard200.csv",
    "hot100": "hot100.csv",
    "streaming": "streaming.csv",
    "digital": "digital.csv",
    "radio": "radio.csv",
}


def load_spotify_tables():
    """Load Spotify track tables and parse album release dates."""
    tracks = pd.read_csv(RAW_DATA_DIR / "track_data_final.csv", low_memory=False)
    clean_tracks = pd.read_csv(RAW_DATA_DIR / "spotify_data clean.csv", low_memory=False)
    tracks["release_date"] = pd.to_datetime(
        tracks["album_release_date"], errors="coerce", format="mixed"
    )
    tracks["year"] = tracks["release_date"].dt.year
    return tracks, clean_tracks


def load_chart(chart_name):
    """Load one Kaggle chart and normalize dates and numeric chart fields."""
    if chart_name not in CHART_FILES:
        raise ValueError(f"Unknown chart name: {chart_name}")

    chart = pd.read_csv(
        RAW_DATA_DIR / CHART_FILES[chart_name], dtype=str, low_memory=False
    )
    chart["Date"] = pd.to_datetime(chart["Date"], errors="coerce")
    for column in ("Rank", "Peak Position", "Weeks in Charts"):
        chart[column] = pd.to_numeric(chart[column], errors="coerce")
    return chart.dropna(subset=["Date"])


def parse_genres(value):
    """Parse either Python-list or comma-separated Spotify genre fields."""
    if pd.isna(value):
        return []

    text = str(value)
    if text.startswith("["):
        try:
            parsed = ast.literal_eval(text)
        except (SyntaxError, ValueError):
            return []
        return [str(genre).strip() for genre in parsed if str(genre).strip()]
    return [genre.strip() for genre in text.split(",") if genre.strip()]


def collect_artist_genres(*tables):
    """Combine genre tags across Spotify source tables by artist name."""
    genres_by_artist = {}
    for table in tables:
        for artist, value in zip(table["artist_name"], table["artist_genres"]):
            genres = parse_genres(value)
            if genres:
                genres_by_artist.setdefault(artist, set()).update(genres)
    return {artist: sorted(genres) for artist, genres in genres_by_artist.items()}


def classify_genre(artist, genres_by_artist):
    """Apply the project's ordered keyword rules to an artist's tags."""
    tags = " | ".join(genres_by_artist.get(artist, [])).lower()
    for genre, pattern in GENRE_RULES:
        if re.search(pattern, tags):
            return genre
    return np.nan


def normalize_match_text(values):
    """Normalize artist and album names using the archived matching rule."""
    return (
        values.fillna("")
        .astype(str)
        .str.lower()
        .str.replace(r"\(.*?\)|\[.*?\]", "", regex=True)
        .str.replace(r"[^a-z0-9 ]", "", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )


def lead_artist(values):
    """Keep the chart-side lead artist, including the archived credit separators."""
    return (
        values.fillna("")
        .astype(str)
        .str.lower()
        .str.replace(r"\s+", " ", regex=True)
        .str.split(
            r" featuring | feat\.? | ft\.? | with | x | & | and |, | / ",
            regex=True,
        )
        .str[0]
        .str.strip()
    )


def spotify_lead_artist(values):
    """Keep the lead artist using the Spotify-to-chart matching rule."""
    return (
        values.fillna("")
        .astype(str)
        .str.lower()
        .str.split(r" featuring | & | and | x | with |, ", regex=True)
        .str[0]
        .str.strip()
    )


def main():
    tracks, clean_tracks = load_spotify_tables()
    billboard = load_chart("b200")
    print(
        f"Loaded {len(tracks)} Spotify tracks, {len(clean_tracks)} clean-table tracks, "
        f"and {len(billboard)} dated Billboard 200 rows."
    )


if __name__ == "__main__":
    main()