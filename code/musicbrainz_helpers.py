"""Shared MusicBrainz helpers used by several numbered pipeline scripts.

Functions were moved here verbatim during the 2026-10-02 cleanup so that
numbered scripts (which Python cannot import) no longer import each other:
- artist search, cache and match resolution: from 04_match_musicbrainz_artists.py
- genre inference from cached artist tags: from 12_validate_musicbrainz_collection.py
- Part 1 analysis data builder: from 16_part1_digital_robustness.py

Cache-only guard: network requests are refused unless the script was started
with --allow-api (or BB200_ALLOW_API=1 is set). A cache miss in cache-only mode
raises CacheMissError instead of calling the API.
"""

import csv
import json
import os
import re
import sys
import time
import unicodedata
from collections import defaultdict
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

from paths import (
    ALBUM_CANDIDATES,
    ARTIST_MATCHES,
    ARTIST_SEARCH_CACHE,
    ARTIST_SEARCH_ERRORS,
    OFFICIAL_RELEASES,
    ROSTER,
)


# --- Cache-only guard ---------------------------------------------------------

API_ENV_VAR = "BB200_ALLOW_API"


class CacheMissError(RuntimeError):
    """Raised when a MusicBrainz response is not cached and API access is off."""


def configure_api_access():
    """Consume an --allow-api flag from the command line before argparse runs."""
    if "--allow-api" in sys.argv:
        sys.argv.remove("--allow-api")
        os.environ[API_ENV_VAR] = "1"


def api_allowed():
    return os.environ.get(API_ENV_VAR) == "1"


def require_api(description):
    if not api_allowed():
        raise CacheMissError(
            f"{description} is not in the cache and API access is off. "
            "Rerun with --allow-api (or set BB200_ALLOW_API=1) only after approval."
        )


# --- Artist search (from 04_match_musicbrainz_artists.py) ---------------------

ROSTER_PATH = ROSTER
CACHE_PATH = ARTIST_SEARCH_CACHE
MATCHES_PATH = ARTIST_MATCHES
ERROR_LOG_PATH = ARTIST_SEARCH_ERRORS
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
    require_api(f"MusicBrainz artist search for {name!r}")
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


# --- Genre inference from artist tags (from 12_validate_musicbrainz_collection.py)

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

# Ordered tie-break rule (docs/genre_classification.md). When an artist's tags
# match several genres, the first genre in this list wins: specific genres that
# define a distinct market/audience beat broad ones; pop, the vaguest tag, is last.
# Same order as the project's Spotify GENRE_RULES (load_clean_data.py) and the
# genre hand-check's proposed_group() (15_prepare_genre_handcheck.py).
# Replaces next(iter(set)), whose result depended on Python's per-process
# string hash randomisation (bug found 2026-10-02).
GENRE_PRIORITY = (
    "latin",
    "hiphop_rnb",
    "country",
    "christian",
    "jazz",
    "classical",
    "electronic",
    "rock",
    "pop",
)


def first_by_priority(genres):
    return min(genres, key=GENRE_PRIORITY.index)


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
        return first_by_priority(genre_sets[0])
    if len(genre_sets) > 1:
        intersection = set.intersection(*genre_sets)
        if len(intersection) == 1:
            return next(iter(intersection))
    return ""


# --- Part 1 analysis data (from 16_part1_digital_robustness.py) ---------------

CANDIDATES_PATH = ALBUM_CANDIDATES
RELEASES_PATH = OFFICIAL_RELEASES
RULE_DATE = pd.Timestamp("2014-11-24")
HEAVY_GENRES = {"hiphop_rnb", "pop", "latin", "electronic"}


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
