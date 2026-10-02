"""Validate MusicBrainz genre coverage, unresolved balance, and edition flags."""

import json
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
MATCHES_PATH = DATA_DIR / "musicbrainz_artist_matches.csv"
GROUPS_PATH = DATA_DIR / "musicbrainz_release_groups.csv"
ALBUMS_PATH = DATA_DIR / "musicbrainz_standard_album_candidates.csv"
CACHE_PATH = DATA_DIR / "musicbrainz_artist_search_cache.jsonl"
GENRE_REPORT_PATH = DATA_DIR / "musicbrainz_genre_balance.csv"
UNRESOLVED_GENRE_PATH = DATA_DIR / "musicbrainz_unresolved_genre_breakdown.csv"
SUBGENRE_BALANCE_PATH = DATA_DIR / "musicbrainz_subgenre_balance.csv"
EDITION_SAMPLE_PATH = DATA_DIR / "musicbrainz_edition_handcheck_sample.csv"

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
RESOLVED = {
    "matched_exact_name",
    "matched_exact_alias",
    "matched_unique_score_100",
    "matched_auto_metadata",
    "matched_group_credit",
    "matched_full_credit_alias",
}
UNRESOLVED = {
    "ambiguous_same_name",
    "ambiguous_same_name_duplicate_id_review",
    "review_composite_credit",
    "unmatched_no_exact_name",
    "review_truncated_search",
    "ambiguous_top_score",
    "unmatched_no_artist_entity",
    "unresolved_band_entity_not_found",
}


def normalize(value):
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return re.sub(r"[\W_]+", " ", text, flags=re.UNICODE).strip()


def read_artist_cache():
    cache = {}
    with CACHE_PATH.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                record = json.loads(line)
                cache[record["roster_artist_key"]] = record["response"]
    return cache


def genre_from_text(text):
    lowered = text.casefold()
    return {
        genre for genre, terms in GENRE_TERMS.items() if any(term in lowered for term in terms)
    }


def candidate_genres(candidate):
    tag_text = " ".join(tag.get("name", "") for tag in candidate.get("tags", []))
    return genre_from_text(" ".join([candidate.get("disambiguation", ""), tag_text]))


def exact_candidates(response, artist_name):
    target = normalize(artist_name)
    candidates = []
    for candidate in response.get("artists", []):
        names = [candidate.get("name", "")]
        names.extend(
            alias.get("name", "") if isinstance(alias, dict) else alias
            for alias in candidate.get("aliases", [])
        )
        if any(normalize(name) == target for name in names):
            candidates.append(candidate)
    return {candidate.get("id"): candidate for candidate in candidates if candidate.get("id")}


def infer_row_genre(row, response):
    artist_id = row["musicbrainz_artist_id"]
    if artist_id:
        candidates = [
            candidate
            for candidate in response.get("artists", [])
            if candidate.get("id") == artist_id
        ]
    else:
        candidates = list(exact_candidates(response, row["artist_name"]).values())
    genre_sets = [candidate_genres(candidate) for candidate in candidates]
    genre_sets = [genres for genres in genre_sets if genres]
    if len(genre_sets) == 1:
        return next(iter(genre_sets[0]))
    if len(genre_sets) > 1:
        intersection = set.intersection(*genre_sets)
        if len(intersection) == 1:
            return next(iter(intersection))
    return ""


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as stream:
        rows[0].keys()
        pd.DataFrame(rows).to_csv(stream, index=False)


def main():
    matches = pd.read_csv(MATCHES_PATH, dtype=str).fillna("")
    cache = read_artist_cache()
    match_records = []
    for row in matches.to_dict("records"):
        genre = infer_row_genre(row, cache.get(row["roster_artist_key"], {}))
        status = row["match_status"]
        match_records.append(
            {
                **row,
                "musicbrainz_genre": genre,
                "genre_group": "streaming_heavy"
                if genre in HEAVY
                else ("other" if genre else "unknown"),
                "is_resolved": status in RESOLVED and bool(row["musicbrainz_artist_id"]),
                "is_unresolved": status in UNRESOLVED or not row["musicbrainz_artist_id"],
            }
        )

    genre_rows = []
    for group in ("streaming_heavy", "other", "unknown"):
        selected = [row for row in match_records if row["genre_group"] == group]
        unresolved = sum(row["is_unresolved"] for row in selected)
        genre_rows.append(
            {
                "genre_group": group,
                "n_artists": len(selected),
                "n_unresolved": unresolved,
                "unresolved_rate": unresolved / len(selected) if selected else "",
                "note": "MusicBrainz artist tags/disambiguation; unknown means no conservative single-group inference.",
            }
        )
    write_csv(GENRE_REPORT_PATH, genre_rows)

    unresolved_rows = [row for row in match_records if row["is_unresolved"]]
    breakdown = []
    for genre in ("hiphop_rnb", "pop", "latin", "electronic", "rock", "country", "christian", "jazz", "classical", "unknown"):
        selected = [row for row in unresolved_rows if row["musicbrainz_genre"] == genre or (genre == "unknown" and not row["musicbrainz_genre"])]
        breakdown.append(
            {
                "genre": genre,
                "n_unresolved": len(selected),
                "share_of_unresolved": len(selected) / len(unresolved_rows) if unresolved_rows else "",
                "unresolved_statuses": " | ".join(sorted({row["match_status"] for row in selected})),
            }
        )
    write_csv(UNRESOLVED_GENRE_PATH, breakdown)

    subgenre_rows = []
    for genre in ("hiphop_rnb", "pop", "latin", "electronic"):
        selected = [row for row in match_records if row["musicbrainz_genre"] == genre]
        unresolved = sum(row["is_unresolved"] for row in selected)
        subgenre_rows.append(
            {
                "genre": genre,
                "n_artists": len(selected),
                "n_unresolved": unresolved,
                "unresolved_rate": unresolved / len(selected) if selected else "",
                "note": "MusicBrainz artist tags/disambiguation; denominator is resolved plus unresolved artists assigned to this subgenre.",
            }
        )
    write_csv(SUBGENRE_BALANCE_PATH, subgenre_rows)

    albums = pd.read_csv(ALBUMS_PATH, dtype=str).fillna("")
    flags = albums[albums["same_day_different_length_editions"].str.casefold() == "true"].copy()
    sample = flags.sample(n=min(30, len(flags)), random_state=20260928).copy()
    sample["handcheck_status"] = "pending"
    sample["handcheck_notes"] = ""
    sample["musicbrainz_release_page_url"] = sample["release_id"].map(
        lambda release_id: f"https://musicbrainz.org/release/{release_id}"
    )
    sample.to_csv(EDITION_SAMPLE_PATH, index=False)

    print("MusicBrainz tag coverage rows:", len(match_records))
    print("Genre balance:")
    print(pd.DataFrame(genre_rows).to_string(index=False))
    print("Unresolved genre breakdown:")
    print(pd.DataFrame(breakdown).to_string(index=False))
    print("Streaming-heavy subgenre balance:")
    print(pd.DataFrame(subgenre_rows).to_string(index=False))
    print(f"Wrote reproducible 30-case edition hand-check sample to {EDITION_SAMPLE_PATH}")


if __name__ == "__main__":
    main()