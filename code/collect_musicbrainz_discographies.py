"""Collect resolved-roster MusicBrainz release groups and official releases."""

import argparse
import csv
import json
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
MATCHES_PATH = DATA_DIR / "musicbrainz_artist_matches.csv"
GROUP_CACHE = DATA_DIR / "musicbrainz_release_group_cache.jsonl"
RELEASE_CACHE = DATA_DIR / "musicbrainz_official_release_cache.jsonl"
ERROR_LOG = DATA_DIR / "musicbrainz_discography_api_errors.jsonl"
GROUPS_PATH = DATA_DIR / "musicbrainz_release_groups.csv"
RELEASES_PATH = DATA_DIR / "musicbrainz_official_releases.csv"
ALBUMS_PATH = DATA_DIR / "musicbrainz_standard_album_candidates.csv"
API_ROOT = "https://musicbrainz.org/ws/2"
USER_AGENT = "Billboard200Paper/0.1 (academic metadata research; contact: project workspace)"
REQUEST_INTERVAL = 1.05
PAGE_SIZE = 100
START_YEAR = 2009
END_YEAR = 2024
RESOLVED_STATUSES = {
    "matched_exact_name",
    "matched_exact_alias",
    "matched_unique_score_100",
    "matched_auto_metadata",
    "matched_group_credit",
    "matched_full_credit_alias",
}

_last_request_time = None


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_jsonl_cache(path):
    cache = {}
    if not path.exists():
        return cache
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                record = json.loads(line)
                cache[record["cache_key"]] = record
    return cache


def append_jsonl(path, record):
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")
        stream.flush()


def log_error(endpoint, params, attempt, error):
    append_jsonl(
        ERROR_LOG,
        {
            "endpoint": endpoint,
            "params": params,
            "attempt": attempt,
            "error_type": type(error).__name__,
            "error": str(error),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
    )


def request_json(endpoint, params):
    global _last_request_time
    delay = REQUEST_INTERVAL - (time.monotonic() - _last_request_time) if _last_request_time else 0
    if delay > 0:
        time.sleep(delay)

    query = urlencode({**params, "fmt": "json"})
    url = f"{API_ROOT}/{endpoint}?{query}"
    request = Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    for attempt in range(1, 5):
        _last_request_time = time.monotonic()
        try:
            with urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8")), url
        except HTTPError as error:
            log_error(endpoint, params, attempt, error)
            if error.code == 429 and attempt < 4:
                retry_after = error.headers.get("Retry-After")
                time.sleep(max(REQUEST_INTERVAL, float(retry_after or 2 ** attempt)))
                continue
            if error.code in (500, 502, 503, 504) and attempt < 4:
                time.sleep(2 ** attempt)
                continue
            raise
        except (TimeoutError, URLError) as error:
            log_error(endpoint, params, attempt, error)
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError(f"MusicBrainz request failed: {url}")


def cached_request(cache, cache_path, endpoint, params):
    cache_key = endpoint + "?" + urlencode(params)
    if cache_key in cache:
        return cache[cache_key]["response"]
    response, url = request_json(endpoint, params)
    record = {"cache_key": cache_key, "url": url, "response": response}
    append_jsonl(cache_path, record)
    cache[cache_key] = record
    return response


def resolved_artists(max_artists=None):
    matches = read_csv(MATCHES_PATH)
    seen_ids = set()
    artists = []
    for row in matches:
        artist_id = row.get("musicbrainz_artist_id", "")
        if row.get("match_status") not in RESOLVED_STATUSES or not artist_id:
            continue
        if artist_id in seen_ids:
            raise ValueError(f"Duplicate resolved MusicBrainz ID: {artist_id}")
        seen_ids.add(artist_id)
        artists.append(row)
    if max_artists is not None:
        artists = artists[:max_artists]
    return artists


def fetch_release_groups(artists, cache):
    group_rows = {}
    for index, artist in enumerate(artists, start=1):
        offset = 0
        while True:
            params = {
                "artist": artist["musicbrainz_artist_id"],
                "type": "album",
                "inc": "artist-credits",
                "limit": PAGE_SIZE,
                "offset": offset,
            }
            data = cached_request(cache, GROUP_CACHE, "release-group", params)
            groups = data.get("release-groups", [])
            for group in groups:
                group_id = group.get("id", "")
                if not group_id:
                    continue
                record = group_rows.setdefault(
                    group_id,
                    {
                        "release_group_id": group_id,
                        "title": group.get("title", ""),
                        "first_release_date": group.get("first-release-date", ""),
                        "primary_type": group.get("primary-type", ""),
                        "secondary_types": " | ".join(group.get("secondary-types", [])),
                        "artist_credit": json.dumps(
                            group.get("artist-credit", []), ensure_ascii=False
                        ),
                        "roster_artist_ids": set(),
                        "roster_artist_names": set(),
                    },
                )
                record["roster_artist_ids"].add(artist["musicbrainz_artist_id"])
                record["roster_artist_names"].add(artist["artist_name"])
            if not groups or offset + len(groups) >= data.get("release-group-count", offset + len(groups)):
                break
            offset += len(groups)
        if index % 100 == 0 or index == len(artists):
            print(f"Release-group pages collected for {index:,}/{len(artists):,} artists", flush=True)

    rows = []
    for record in group_rows.values():
        date = record["first_release_date"]
        year = int(date[:4]) if len(date) >= 4 and date[:4].isdigit() else None
        secondary = [part for part in record["secondary_types"].split(" | ") if part]
        mixtape = "Mixtape/Street" in secondary
        include_window = year is None or START_YEAR <= year <= END_YEAR
        record["roster_artist_ids"] = " | ".join(sorted(record["roster_artist_ids"]))
        record["roster_artist_names"] = " | ".join(sorted(record["roster_artist_names"]))
        record["first_release_year"] = year if year is not None else ""
        record["date_precision"] = "year" if len(date) == 4 else ("month" if len(date) == 7 else ("day" if date else "unknown"))
        record["mixtape_street"] = mixtape
        record["eligible_headline_type"] = record["primary_type"] == "Album" and not secondary
        record["eligible_mixtape_robustness"] = record["primary_type"] == "Album" and mixtape
        record["fetch_official_releases"] = include_window and (
            record["eligible_headline_type"] or record["eligible_mixtape_robustness"]
        )
        rows.append(record)
    rows.sort(key=lambda row: (row["first_release_date"] or "9999", row["title"].casefold()))
    fields = [
        "release_group_id",
        "title",
        "first_release_date",
        "first_release_year",
        "date_precision",
        "primary_type",
        "secondary_types",
        "artist_credit",
        "mixtape_street",
        "eligible_headline_type",
        "eligible_mixtape_robustness",
        "fetch_official_releases",
        "roster_artist_ids",
        "roster_artist_names",
    ]
    write_csv(GROUPS_PATH, rows, fields)
    print(
        f"Unique release groups: {len(rows):,}; "
        f"headline-type groups in window/undated: {sum(bool(r['fetch_official_releases']) and r['eligible_headline_type'] for r in rows):,}; "
        f"Mixtape/Street robustness groups: {sum(bool(r['fetch_official_releases']) and r['eligible_mixtape_robustness'] for r in rows):,}"
    )
    return rows


def fetch_official_releases(groups, cache):
    eligible = [group for group in groups if group["fetch_official_releases"] in (True, "True")]
    release_rows = {}
    for index, group in enumerate(eligible, start=1):
        offset = 0
        while True:
            params = {
                "release-group": group["release_group_id"],
                "status": "official",
                "inc": "media+recordings+labels+artist-credits",
                "limit": PAGE_SIZE,
                "offset": offset,
            }
            data = cached_request(cache, RELEASE_CACHE, "release", params)
            releases = data.get("releases", [])
            for release in releases:
                release_id = release.get("id", "")
                media = release.get("media", [])
                track_counts = [int(m.get("track-count") or 0) for m in media]
                track_lengths = [
                    int(
                        track.get("length")
                        or (track.get("recording") or {}).get("length")
                        or 0
                    )
                    for medium in media
                    for track in (medium.get("tracks") or [])
                ]
                known_lengths = [length for length in track_lengths if length > 0]
                label_names = [
                    (item.get("label") or {}).get("name", "")
                    for item in release.get("label-info", [])
                    if (item.get("label") or {}).get("name")
                ]
                release_rows[release_id] = {
                    "release_group_id": group["release_group_id"],
                    "release_group_title": group["title"],
                    "release_id": release_id,
                    "release_title": release.get("title", ""),
                    "status": release.get("status", ""),
                    "date": release.get("date", ""),
                    "country": release.get("country", ""),
                    "track_count_sum_media": sum(track_counts),
                    "media_count": len(media),
                    "media_track_counts": " | ".join(map(str, track_counts)),
                    "running_time_minutes": round(sum(known_lengths) / 60000, 3)
                    if known_lengths
                    else "",
                    "tracks_with_duration": len(known_lengths),
                    "label_names": " | ".join(dict.fromkeys(label_names)),
                    "artist_credit": json.dumps(
                        release.get("artist-credit", []), ensure_ascii=False
                    ),
                    "media_json": json.dumps(media, ensure_ascii=False),
                    "source_url": f"https://musicbrainz.org/release/{release_id}",
                    "eligible_headline_type": group["eligible_headline_type"],
                    "eligible_mixtape_robustness": group["eligible_mixtape_robustness"],
                }
            if not releases or offset + len(releases) >= data.get("release-count", offset + len(releases)):
                break
            offset += len(releases)
        if index % 100 == 0 or index == len(eligible):
            print(f"Official-release lists collected for {index:,}/{len(eligible):,} groups", flush=True)

    rows = list(release_rows.values())
    rows.sort(key=lambda row: (row["release_group_id"], row["date"] or "9999", row["release_id"]))
    write_csv(
        RELEASES_PATH,
        rows,
        [
            "release_group_id",
            "release_group_title",
            "release_id",
            "release_title",
            "status",
            "date",
            "country",
            "track_count_sum_media",
            "media_count",
            "media_track_counts",
            "running_time_minutes",
            "tracks_with_duration",
            "label_names",
            "artist_credit",
            "media_json",
            "source_url",
            "eligible_headline_type",
            "eligible_mixtape_robustness",
        ],
    )
    print(f"Official release editions collected: {len(rows):,}")
    return rows


def build_standard_album_candidates(groups, releases):
    group_by_id = {group["release_group_id"]: group for group in groups}
    by_group = {}
    for release in releases:
        by_group.setdefault(release["release_group_id"], []).append(release)

    albums = []
    for group_id, editions in by_group.items():
        dated = [edition for edition in editions if edition["date"]]
        if not dated:
            continue
        earliest_date = min(edition["date"] for edition in dated)
        earliest = [edition for edition in dated if edition["date"] == earliest_date]
        chosen = min(earliest, key=lambda edition: int(edition["track_count_sum_media"]))
        group = group_by_id[group_id]
        year = int(earliest_date[:4]) if earliest_date[:4].isdigit() else None
        albums.append(
            {
                "release_group_id": group_id,
                "release_id": chosen["release_id"],
                "album_title": group["title"],
                "release_title": chosen["release_title"],
                "release_date": earliest_date,
                "release_date_precision": "year" if len(earliest_date) == 4 else ("month" if len(earliest_date) == 7 else "day"),
                "standard_track_count": chosen["track_count_sum_media"],
                "running_time_minutes": chosen["running_time_minutes"],
                "tracks_with_duration": chosen["tracks_with_duration"],
                "label": chosen["label_names"],
                "country": chosen["country"],
                "media_count": chosen["media_count"],
                "media_track_counts": chosen["media_track_counts"],
                "artist_credit": chosen["artist_credit"],
                "mixtape_street_robustness": group["eligible_mixtape_robustness"] in (True, "True"),
                "artist_ids": group["roster_artist_ids"],
                "roster_artist_names": group["roster_artist_names"],
                "artist_credits": chosen["artist_credit"],
                "source": "MusicBrainz Web Service API",
                "musicbrainz_release_group_id": group_id,
                "musicbrainz_release_id": chosen["release_id"],
                "source_url": chosen["source_url"],
                "release_group_first_date": group["first_release_date"],
                "same_day_different_length_editions": len(
                    {edition["track_count_sum_media"] for edition in earliest}
                ) > 1,
                "2014_year_only_exclude_headline": earliest_date == "2014",
                "headline_window_2009_2019": group["eligible_headline_type"] in (True, "True")
                and bool(year and 2009 <= year <= 2019),
                "secondary_window_2009_2024": group["eligible_headline_type"] in (True, "True")
                and bool(year and 2009 <= year <= 2024),
            }
        )
    write_csv(
        ALBUMS_PATH,
        albums,
        [
            "release_group_id",
            "release_id",
            "album_title",
            "release_title",
            "release_date",
            "release_date_precision",
            "standard_track_count",
            "running_time_minutes",
            "tracks_with_duration",
            "label",
            "country",
            "media_count",
            "media_track_counts",
            "artist_credit",
            "mixtape_street_robustness",
            "artist_ids",
            "roster_artist_names",
            "artist_credits",
            "source",
            "musicbrainz_release_group_id",
            "musicbrainz_release_id",
            "source_url",
            "release_group_first_date",
            "same_day_different_length_editions",
            "2014_year_only_exclude_headline",
            "headline_window_2009_2019",
            "secondary_window_2009_2024",
        ],
    )
    tied = sum(bool(album["same_day_different_length_editions"]) for album in albums)
    year_only_2014 = sum(bool(album["2014_year_only_exclude_headline"]) for album in albums)
    print(f"Standard album candidates: {len(albums):,}; same-day different-length edition flags: {tied:,}; 2014 year-only exclusions: {year_only_2014:,}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("groups", "releases", "all"), default="groups")
    parser.add_argument("--max-artists", type=int, help="Smoke-test with the first N resolved artists.")
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    artists = resolved_artists(args.max_artists)
    group_cache = read_jsonl_cache(GROUP_CACHE)
    release_cache = read_jsonl_cache(RELEASE_CACHE)
    print(f"Resolved artist IDs queued: {len(artists):,}")

    if args.phase in ("groups", "all"):
        groups = fetch_release_groups(artists, group_cache)
    else:
        groups = read_csv(GROUPS_PATH)

    if args.phase in ("releases", "all"):
        releases = fetch_official_releases(groups, release_cache)
        build_standard_album_candidates(groups, releases)


if __name__ == "__main__":
    main()