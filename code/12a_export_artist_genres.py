"""Export one genre label per resolved roster artist (docs/items4_5_plan.md, section 1).

Same classification as every analysis (infer_row_genre, ordered GENRE_PRIORITY tie-break).
"""

import pandas as pd

from musicbrainz_helpers import (
    GENRE_PRIORITY,
    HEAVY_GENRES,
    candidate_genres,
    infer_row_genre,
    read_artist_cache,
)
from paths import ARTIST_GENRES, ARTIST_MATCHES, FINAL_DIR


def main():
    matches = pd.read_csv(ARTIST_MATCHES, dtype=str).fillna("")
    cache = read_artist_cache()
    rows = []
    for row in matches.to_dict("records"):
        artist_id = row["musicbrainz_artist_id"]
        if not artist_id:
            continue
        response = cache.get(row["roster_artist_key"], {})
        genre = infer_row_genre(row, response)
        if not genre:
            continue
        candidates = [c for c in response.get("artists", []) if c.get("id") == artist_id]
        matched = set().union(*(candidate_genres(c) for c in candidates)) if candidates else set()
        rows.append({
            "roster_artist_key": row["roster_artist_key"],
            "artist_name": row["artist_name"],
            "musicbrainz_artist_id": artist_id,
            "genre": genre,
            "heavy": int(genre in HEAVY_GENRES),
            "matched_genres": " | ".join(sorted(matched, key=GENRE_PRIORITY.index)),
            "decided_by_ordered_rule": len(matched) > 1,
        })
    out = pd.DataFrame(rows)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(ARTIST_GENRES, index=False)
    print(f"Artist genres: {len(out)} artists ({int(out['heavy'].sum())} streaming-heavy); "
          f"{int(out['decided_by_ordered_rule'].sum())} decided by the ordered tie-break -> {ARTIST_GENRES}")


if __name__ == "__main__":
    main()
