"""Match frozen roster entries to MusicBrainz artists; do not fetch discographies."""

import argparse
import csv
import json
import re
import time
import unicodedata
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
ROSTER_PATH = DATA_DIR / "pre_rule_artist_roster.csv"
CACHE_PATH = DATA_DIR / "musicbrainz_artist_search_cache.jsonl"
MATCHES_PATH = DATA_DIR / "musicbrainz_artist_matches.csv"
REVIEW_PATH = DATA_DIR / "musicbrainz_artist_matches_review.csv"
ERROR_LOG_PATH = DATA_DIR / "musicbrainz_artist_search_errors.jsonl"
API_URL = "https://musicbrainz.org/ws/2/artist"
USER_AGENT = "Billboard200Paper/0.1 (academic metadata research; contact: project workspace)"
REQUEST_INTERVAL_SECONDS = 1.0
SEARCH_LIMIT = 100


def normalize_name(value):
    normalized = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return re.sub(r"\s+", " ", normalized).strip()


def punctuation_insensitive_name(value):
    normalized = unicodedata.normalize("NFKC", str(value or "")).casefold()
    normalized = "".join(
        character
        for character in normalized
        if unicodedata.category(character)[0] not in {"P", "S"}
    )
    return re.sub(r"\s+", " ", normalized).strip()


def load_roster():
    with ROSTER_PATH.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def load_cache():
    cache = {}
    if not CACHE_PATH.exists():
        return cache
    with CACHE_PATH.open(encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            record = json.loads(line)
            cache[record["roster_artist_key"]] = record["response"]
    return cache


def request_artist_search(name):
    query_text = f'"{name}"'
    query = urlencode(
        {
            "query": query_text,
            "fmt": "json",
            "limit": SEARCH_LIMIT,
            "dismax": "true",
        }
    )
    request = Request(
        f"{API_URL}?{query}",
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    for attempt in range(4):
        try:
            with urlopen(request, timeout=45) as response:
                return json.loads(response.read().decode("utf-8")), query_text
        except HTTPError as error:
            log_search_error(name, query_text, attempt + 1, error)
            if error.code == 429 and attempt < 3:
                retry_after = error.headers.get("Retry-After")
                time.sleep(max(1.0, float(retry_after or 2 ** (attempt + 1))))
                continue
            if error.code in (500, 502, 503, 504) and attempt < 3:
                time.sleep(2 ** (attempt + 1))
                continue
            raise
        except (TimeoutError, URLError) as error:
            log_search_error(name, query_text, attempt + 1, error)
            if attempt == 3:
                raise
            time.sleep(2 ** (attempt + 1))
    raise RuntimeError(f"MusicBrainz search failed for {name!r}")


def log_search_error(name, query_text, attempt, error):
    with ERROR_LOG_PATH.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(
            json.dumps(
                {
                    "artist_name": name,
                    "query": query_text,
                    "attempt": attempt,
                    "error_type": type(error).__name__,
                    "error": str(error),
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                },
                ensure_ascii=False,
            )
            + "\n"
        )
        stream.flush()


def append_cache(roster_artist_key, response, query=None):
    with CACHE_PATH.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(
            json.dumps(
                {
                    "roster_artist_key": roster_artist_key,
                    "query": query,
                    "response": response,
                },
                ensure_ascii=False,
            )
            + "\n"
        )
        stream.flush()


def resolve_candidate(roster_row, response):
    artist_name = roster_row["artist_name"]
    roster_key = normalize_name(artist_name)
    candidates = response.get("artists", [])
    exact_name = [
        artist
        for artist in candidates
        if normalize_name(artist.get("name")) == roster_key
    ]
    exact_alias = [
        artist
        for artist in candidates
        if any(
            normalize_name(alias.get("name")) == roster_key
            for alias in artist.get("aliases", [])
        )
    ]
    exact_by_id = {
        artist.get("id"): artist for artist in exact_name + exact_alias
    }
    exact = list(exact_by_id.values())
    punctuation_matches = [
        artist
        for artist in candidates
        if punctuation_insensitive_name(artist.get("name"))
        == punctuation_insensitive_name(artist_name)
        or any(
            punctuation_insensitive_name(alias.get("name"))
            == punctuation_insensitive_name(artist_name)
            for alias in artist.get("aliases", [])
        )
    ]
    top_score_matches = [
        artist for artist in punctuation_matches if artist.get("score") == 100
    ]
    composite = str(roster_row.get("identity_review_needed", "")).casefold() in {
        "true",
        "1",
        "yes",
    }
    truncated = len(candidates) >= SEARCH_LIMIT

    result = {
        "roster_artist_key": roster_row["roster_artist_key"],
        "artist_name": artist_name,
        "first_qualifying_debut": roster_row["first_qualifying_debut"],
        "identity_review_needed": composite,
        "search_candidate_count": len(candidates),
        "exact_name_candidate_count": len(exact_name),
        "exact_alias_candidate_count": len(exact_alias),
        "exact_match_candidate_count": len(exact),
        "punctuation_match_candidate_count": len(punctuation_matches),
        "score_100_match_candidate_count": len(top_score_matches),
        "candidate_summary": json.dumps(
            [
                {
                    "id": artist.get("id", ""),
                    "name": artist.get("name", ""),
                    "score": artist.get("score", ""),
                    "disambiguation": artist.get("disambiguation", ""),
                    "type": artist.get("type", ""),
                    "area": (artist.get("area") or {}).get("name", ""),
                    "aliases": [
                        alias.get("name", "")
                        for alias in artist.get("aliases", [])[:5]
                    ],
                }
                for artist in candidates[:10]
            ],
            ensure_ascii=False,
        ),
        "musicbrainz_artist_id": "",
        "match_candidate_summary": "",
        "match_status": "",
        "match_basis": "",
    }

    if composite:
        result["match_status"] = "review_composite_credit"
    elif truncated and len(exact) == 1:
        result["match_status"] = "review_truncated_search"
    elif len(exact) > 1:
        result["match_status"] = "ambiguous_same_name"
    elif len(exact) == 1:
        result["musicbrainz_artist_id"] = exact[0].get("id", "")
        result["match_candidate_summary"] = json.dumps(
            {"id": exact[0].get("id", ""), "name": exact[0].get("name", "")},
            ensure_ascii=False,
        )
        if exact_name:
            result["match_status"] = "matched_exact_name"
            result["match_basis"] = "canonical_name"
        else:
            result["match_status"] = "matched_exact_alias"
            result["match_basis"] = "artist_alias"
    elif len(top_score_matches) == 1:
        result["musicbrainz_artist_id"] = top_score_matches[0].get("id", "")
        result["match_candidate_summary"] = json.dumps(
            {
                "id": top_score_matches[0].get("id", ""),
                "name": top_score_matches[0].get("name", ""),
                "score": top_score_matches[0].get("score", ""),
            },
            ensure_ascii=False,
        )
        result["match_status"] = "matched_unique_score_100"
        result["match_basis"] = "unique_punctuation_normalized_score_100"
    elif top_score_matches:
        result["match_status"] = "ambiguous_top_score"
    else:
        result["match_status"] = "unmatched_no_exact_name"
    return result


def write_csv(path, rows):
    fields = [
        "roster_artist_key",
        "artist_name",
        "first_qualifying_debut",
        "identity_review_needed",
        "search_candidate_count",
        "exact_name_candidate_count",
        "exact_alias_candidate_count",
        "exact_match_candidate_count",
        "punctuation_match_candidate_count",
        "score_100_match_candidate_count",
        "musicbrainz_artist_id",
        "match_candidate_summary",
        "match_status",
        "match_basis",
        "candidate_summary",
    ]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-artists",
        type=int,
        help="Limit this run for a smoke test; cached results can be resumed later.",
    )
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
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