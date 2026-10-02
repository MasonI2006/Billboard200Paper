"""Match frozen roster entries to MusicBrainz artists; do not fetch discographies."""

import argparse
import time

from musicbrainz_helpers import (
    MATCHES_PATH,
    REQUEST_INTERVAL_SECONDS,
    append_cache,
    configure_api_access,
    load_cache,
    load_roster,
    request_artist_search,
    resolve_candidate,
    write_csv,
)
from paths import ARTIST_MATCHES_REVIEW, INTERIM_DIR


REVIEW_PATH = ARTIST_MATCHES_REVIEW


def main():
    configure_api_access()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-artists",
        type=int,
        help="Limit this run for a smoke test; cached results can be resumed later.",
    )
    args = parser.parse_args()

    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    roster = load_roster()
    cache = load_cache()
    selected = roster[: args.max_artists] if args.max_artists else roster
    rows = []
    last_request_at = None

    for index, roster_row in enumerate(selected, start=1):
        key = roster_row["roster_artist_key"]
        if key not in cache:
            if last_request_at is not None:
                delay = REQUEST_INTERVAL_SECONDS - (time.monotonic() - last_request_at)
                if delay > 0:
                    time.sleep(delay)
            last_request_at = time.monotonic()
            response, query = request_artist_search(roster_row["artist_name"])
            append_cache(key, response, query)
            cache[key] = response

        rows.append(resolve_candidate(roster_row, cache[key]))
        if index % 100 == 0 or index == len(selected):
            print(f"Processed {index:,}/{len(selected):,} roster entries", flush=True)

    id_counts = {}
    for row in rows:
        musicbrainz_id = row["musicbrainz_artist_id"]
        if musicbrainz_id:
            id_counts[musicbrainz_id] = id_counts.get(musicbrainz_id, 0) + 1
    for row in rows:
        musicbrainz_id = row["musicbrainz_artist_id"]
        if musicbrainz_id and id_counts[musicbrainz_id] > 1:
            row["match_status"] = "duplicate_roster_entries_same_artist_id_review"

    write_csv(MATCHES_PATH, rows)
    review_rows = [
        row
        for row in rows
        if row["match_status"]
        not in {
            "matched_exact_name",
            "matched_exact_alias",
            "matched_unique_score_100",
        }
    ]
    write_csv(REVIEW_PATH, review_rows)

    matched = sum(
        row["match_status"]
        in {
            "matched_exact_name",
            "matched_exact_alias",
            "matched_unique_score_100",
        }
        for row in rows
    )
    ambiguous = sum(row["match_status"] == "ambiguous_same_name" for row in rows)
    composite = sum(row["match_status"] == "review_composite_credit" for row in rows)
    duplicate_ids = sum(
        row["match_status"] == "duplicate_roster_entries_same_artist_id_review"
        for row in rows
    )
    print(f"Roster entries processed: {len(rows):,}")
    print(
        "Automatically matched by a unique exact name, alias, or punctuation-normalized "
        f"score-100 result: {matched:,} ({matched / max(1, len(rows)):.1%})"
    )
    print(f"Same-name ambiguities: {ambiguous:,}")
    print(f"Composite credits held for review: {composite:,}")
    print(f"Duplicate roster rows sharing an artist ID, held for review: {duplicate_ids:,}")
    print(f"All unresolved/review entries saved to {REVIEW_PATH}")
    print("Only artist-search responses were requested; no release or release-group data was fetched.")


if __name__ == "__main__":
    main()