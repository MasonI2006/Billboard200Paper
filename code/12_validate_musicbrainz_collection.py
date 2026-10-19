"""Validate MusicBrainz genre coverage, unresolved balance, and edition flags."""

import pandas as pd

from musicbrainz_helpers import infer_row_genre, read_artist_cache
from paths import (
    ALBUM_CANDIDATES,
    ARTIST_MATCHES,
    EDITION_HANDCHECK_SAMPLE,
    GENRE_BALANCE,
    RELEASE_GROUPS,
    SUBGENRE_BALANCE,
    UNRESOLVED_GENRE_BREAKDOWN,
)


MATCHES_PATH = ARTIST_MATCHES
GROUPS_PATH = RELEASE_GROUPS
ALBUMS_PATH = ALBUM_CANDIDATES
GENRE_REPORT_PATH = GENRE_BALANCE
UNRESOLVED_GENRE_PATH = UNRESOLVED_GENRE_BREAKDOWN
SUBGENRE_BALANCE_PATH = SUBGENRE_BALANCE
EDITION_SAMPLE_PATH = EDITION_HANDCHECK_SAMPLE

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
    # all nine genres (the four streaming-heavy genres first, as before; the other five added
    # 2026-10-18 for Online Resource 1, Table C1)
    for genre in ("hiphop_rnb", "pop", "latin", "electronic", "rock", "country", "christian", "jazz", "classical"):
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
    print("Genre balance, all nine genres:")
    print(pd.DataFrame(subgenre_rows).to_string(index=False))
    print(f"Wrote reproducible 30-case edition hand-check sample to {EDITION_SAMPLE_PATH}")


if __name__ == "__main__":
    main()