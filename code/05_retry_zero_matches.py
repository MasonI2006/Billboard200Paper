"""Re-query user-flagged zero-result artists with literal alias-aware search."""

import argparse
import csv
import time
from pathlib import Path

from musicbrainz_helpers import (
    CACHE_PATH,
    ERROR_LOG_PATH,
    MATCHES_PATH,
    REQUEST_INTERVAL_SECONDS,
    CacheMissError,
    api_allowed,
    append_cache,
    configure_api_access,
    load_cache,
    load_roster,
    request_artist_search,
    resolve_candidate,
    write_csv,
)
from paths import ARTIST_MATCHES_REVIEW, TRUE_NOMATCH_ZERO


REVIEW_PATH = ARTIST_MATCHES_REVIEW
DEFAULT_ZERO_LIST = TRUE_NOMATCH_ZERO


def load_zero_list(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def rebuild_match_outputs(roster, cache):
    rows = []
    for roster_row in roster:
        key = roster_row["roster_artist_key"]
        response = cache.get(key)
        if response is None:
            raise RuntimeError(f"No cached MusicBrainz response for {roster_row['artist_name']}")
        rows.append(resolve_candidate(roster_row, response))

    id_counts = {}
    for row in rows:
        artist_id = row["musicbrainz_artist_id"]
        if artist_id:
            id_counts[artist_id] = id_counts.get(artist_id, 0) + 1
    for row in rows:
        artist_id = row["musicbrainz_artist_id"]
        if artist_id and id_counts[artist_id] > 1:
            row["match_status"] = "duplicate_roster_entries_same_artist_id_review"

    write_csv(MATCHES_PATH, rows)
    needs_review = [
        row
        for row in rows
        if row["match_status"]
        not in {
            "matched_exact_name",
            "matched_exact_alias",
            "matched_unique_score_100",
        }
    ]
    write_csv(REVIEW_PATH, needs_review)
    return rows


def main():
    configure_api_access()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_ZERO_LIST)
    args = parser.parse_args()

    roster = load_roster()
    by_name = {row["artist_name"]: row for row in roster}
    zero_rows = load_zero_list(args.input)
    cache = load_cache()
    completed = []
    failed = []
    last_request_at = None

    for index, zero_row in enumerate(zero_rows, start=1):
        name = zero_row["artist_name"]
        roster_row = by_name.get(name)
        if roster_row is None:
            failed.append((name, "artist name did not map to frozen roster"))
            continue

        roster_key = roster_row["roster_artist_key"]
        if not api_allowed():
            # Cache-only mode: replay the retry response already cached for this key.
            if roster_key not in cache:
                raise CacheMissError(f"No cached retry response for {name!r}")
            response = cache[roster_key]
            completed.append((name, response.get("count", 0), len(response.get("artists", []))))
            continue

        if last_request_at is not None:
            delay = REQUEST_INTERVAL_SECONDS - (time.monotonic() - last_request_at)
            if delay > 0:
                time.sleep(delay)
        last_request_at = time.monotonic()

        try:
            response, query = request_artist_search(name)
        except Exception as error:
            failed.append((name, f"{type(error).__name__}: {error}"))
            continue

        append_cache(roster_key, response, query)
        cache[roster_key] = response
        completed.append((name, response.get("count", 0), len(response.get("artists", []))))
        if index % 10 == 0 or index == len(zero_rows):
            print(f"Re-queried {index}/{len(zero_rows)} zero-result names", flush=True)

    if not failed:
        final_rows = rebuild_match_outputs(roster, cache)
        auto_matched = sum(
            row["match_status"]
            in {
                "matched_exact_name",
                "matched_exact_alias",
                "matched_unique_score_100",
            }
            for row in final_rows
        )
        print(f"Updated unique matches after retries: {auto_matched}/{len(final_rows)}")
    else:
        print(f"Failed zero-result retries: {len(failed)}")
        for name, error in failed:
            print(f"ERROR {name}: {error}")

    print(f"Names re-queried: {len(completed)}")
    print(f"Still returned zero candidates: {sum(count == 0 for _, count, _ in completed)}")
    print(f"Search responses cached in {CACHE_PATH}")
    print(f"API errors logged in {ERROR_LOG_PATH}")


if __name__ == "__main__":
    main()