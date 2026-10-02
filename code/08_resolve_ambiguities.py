"""Apply conservative cached-metadata rules to ambiguous artist search rows."""

import csv
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
ROSTER_PATH = DATA_DIR / "pre_rule_artist_roster.csv"
MATCHES_PATH = DATA_DIR / "musicbrainz_artist_matches.csv"
REVIEW_PATH = DATA_DIR / "musicbrainz_artist_matches_review.csv"
CACHE_PATH = DATA_DIR / "musicbrainz_artist_search_cache.jsonl"
SPOTIFY_SAMPLE_PATH = DATA_DIR / "spotify_album_sample.csv"
RESOLUTION_AUDIT_PATH = DATA_DIR / "musicbrainz_ambiguity_auto_resolution.csv"
BALANCE_PATH = DATA_DIR / "musicbrainz_unresolved_balance.csv"

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
HEAVY_GENRES = {"hiphop_rnb", "pop", "latin", "electronic"}


def normalize(value):
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return re.sub(r"[\W_]+", " ", text, flags=re.UNICODE).strip()


def read_cache():
    cache = {}
    with CACHE_PATH.open(encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            row = json.loads(line)
            cache[row["roster_artist_key"]] = row["response"]
    return cache


def read_matches():
    with MATCHES_PATH.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def spotify_genres_by_artist():
    sample = pd.read_csv(SPOTIFY_SAMPLE_PATH)
    genres = {}
    for artist, genre in zip(sample["artist"], sample["genre"]):
        if pd.isna(genre):
            continue
        genres.setdefault(normalize(artist), set()).add(str(genre))
    return genres


def candidate_credit_names(candidate):
    names = [candidate.get("name", "")]
    for alias in candidate.get("aliases", []):
        names.append(alias.get("name", "") if isinstance(alias, dict) else alias)
    return names


def extract_exact_candidates(response, roster_name):
    target = normalize(roster_name)
    by_id = {}
    for candidate in response.get("artists", []):
        if any(normalize(name) == target for name in candidate_credit_names(candidate)):
            by_id[candidate.get("id", "")] = candidate
    return [candidate for candidate in by_id.values() if candidate.get("id")]


def country_value(candidate):
    return (candidate.get("country") or "").upper()


def area_value(candidate):
    return str((candidate.get("area") or {}).get("name") or "").casefold()


def explicit_us(candidate):
    return country_value(candidate) == "US" or area_value(candidate) == "united states"


def explicit_foreign(candidate):
    country = country_value(candidate)
    return bool(country and country != "US")


def genre_evidence(candidate, genres):
    text_parts = [candidate.get("disambiguation", "")]
    text_parts.extend(tag.get("name", "") for tag in candidate.get("tags", []))
    text = " ".join(text_parts).casefold()
    evidence = set()
    for genre in genres:
        if any(term in text for term in GENRE_TERMS.get(genre, ())):
            evidence.add(genre)
    return evidence


def choose_ambiguity(roster_row, response, genre_lookup):
    artist_name = roster_row["artist_name"]
    candidates = extract_exact_candidates(response, artist_name)
    count = response.get("count", len(response.get("artists", [])))
    returned = len(response.get("artists", []))
    result = {
        "artist_name": artist_name,
        "roster_artist_key": roster_row["roster_artist_key"],
        "candidate_count": count,
        "returned_artist_count": returned,
        "exact_candidate_count": len(candidates),
        "spotify_genres": " | ".join(sorted(genre_lookup.get(normalize(artist_name), set()))),
        "resolution_rule": "",
        "selected_musicbrainz_artist_id": "",
        "selected_candidate": "",
        "candidate_evidence": json.dumps(
            [
                {
                    "id": candidate.get("id"),
                    "name": candidate.get("name"),
                    "type": candidate.get("type"),
                    "country": candidate.get("country"),
                    "area": area_value(candidate),
                    "disambiguation": candidate.get("disambiguation", ""),
                    "genre_evidence": sorted(
                        genre_evidence(
                            candidate, genre_lookup.get(normalize(artist_name), set())
                        )
                    ),
                }
                for candidate in candidates
            ],
            ensure_ascii=False,
        ),
        "status": "manual_review",
    }

    if count > returned:
        result["resolution_rule"] = "candidate_search_truncated"
        return result
    if len(candidates) < 2:
        result["resolution_rule"] = "not_multiple_exact_candidates"
        return result

    us_candidates = [candidate for candidate in candidates if explicit_us(candidate)]
    if len(us_candidates) == 1 and all(
        explicit_foreign(candidate)
        for candidate in candidates
        if candidate["id"] != us_candidates[0]["id"]
    ):
        return resolved(result, us_candidates[0], "unique_us_candidate_vs_explicit_foreign_candidates")

    group_candidates = [candidate for candidate in candidates if candidate.get("type") == "Group"]
    if (
        len(group_candidates) == 1
        and explicit_us(group_candidates[0])
        and all(candidate.get("type") == "Person" for candidate in candidates if candidate["id"] != group_candidates[0]["id"])
    ):
        return resolved(result, group_candidates[0], "unique_us_group_vs_person_candidates")

    genres = genre_lookup.get(normalize(artist_name), set())
    if genres:
        evidence = {candidate["id"]: genre_evidence(candidate, genres) for candidate in candidates}
        compatible = [candidate for candidate in candidates if evidence[candidate["id"]] & genres]
        if len(compatible) == 1 and all(
            evidence[candidate["id"]]
            and not (evidence[candidate["id"]] & genres)
            for candidate in candidates
            if candidate["id"] != compatible[0]["id"]
        ):
            return resolved(result, compatible[0], "unique_candidate_genre_disambiguation_matches_spotify")

    result["resolution_rule"] = "no_single_candidate_supported_by_metadata"
    return result


def resolved(result, candidate, rule):
    result["resolution_rule"] = rule
    result["selected_musicbrainz_artist_id"] = candidate["id"]
    result["selected_candidate"] = json.dumps(
        {
            "id": candidate.get("id"),
            "name": candidate.get("name"),
            "type": candidate.get("type"),
            "country": candidate.get("country"),
            "area": area_value(candidate),
            "disambiguation": candidate.get("disambiguation", ""),
        },
        ensure_ascii=False,
    )
    result["status"] = "auto_resolved_metadata"
    return result


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cache = read_cache()
    rows = read_matches()
    roster = {row["roster_artist_key"]: row for row in rows}
    ambiguous = [row for row in rows if row["match_status"] == "ambiguous_same_name"]
    genre_lookup = spotify_genres_by_artist()
    decisions = []

    for match in ambiguous:
        roster_row = roster[match["roster_artist_key"]]
        response = cache.get(match["roster_artist_key"], {})
        decisions.append(choose_ambiguity(roster_row, response, genre_lookup))

    auto_by_key = {
        row["roster_artist_key"]: row
        for row in decisions
        if row["status"] == "auto_resolved_metadata"
    }
    for match in rows:
        decision = auto_by_key.get(match["roster_artist_key"])
        if decision:
            match["musicbrainz_artist_id"] = decision["selected_musicbrainz_artist_id"]
            match["match_candidate_summary"] = decision["selected_candidate"]
            match["match_status"] = "matched_auto_metadata"
            match["match_basis"] = decision["resolution_rule"]

    id_to_rows = {}
    for match in rows:
        artist_id = match.get("musicbrainz_artist_id", "")
        if artist_id:
            id_to_rows.setdefault(artist_id, []).append(match)
    duplicate_keys = set()
    for matches in id_to_rows.values():
        if len(matches) > 1:
            duplicate_keys.update(row["roster_artist_key"] for row in matches)
    for match in rows:
        if match["roster_artist_key"] in duplicate_keys and match["match_status"] == "matched_auto_metadata":
            match["musicbrainz_artist_id"] = ""
            match["match_candidate_summary"] = ""
            match["match_status"] = "ambiguous_same_name_duplicate_id_review"
            match["match_basis"] = ""

    fields = list(rows[0].keys())
    write_csv(MATCHES_PATH, rows, fields)
    review_rows = [
        row
        for row in rows
        if row["match_status"] not in {
            "matched_exact_name",
            "matched_exact_alias",
            "matched_unique_score_100",
            "matched_auto_metadata",
        }
    ]
    write_csv(REVIEW_PATH, review_rows, fields)

    resolution_fields = list(decisions[0].keys()) if decisions else []
    write_csv(RESOLUTION_AUDIT_PATH, decisions, resolution_fields)
    auto_count = sum(row["status"] == "auto_resolved_metadata" for row in decisions)
    manual_count = len(decisions) - auto_count
    print(f"Ambiguous-name rows analyzed: {len(decisions)}")
    print(f"Auto-resolved by cached metadata: {auto_count}")
    print(f"Still requiring a human: {manual_count}")
    print(f"Spotify genre matches among ambiguous names: {sum(bool(row['spotify_genres']) for row in decisions)}")

    report_balance(rows, genre_lookup)


def report_balance(rows, genre_lookup):
    output = []
    for split_label, selector in (
        ("streaming_heavy", lambda genres: bool(genres & HEAVY_GENRES)),
        ("other", lambda genres: bool(genres) and not bool(genres & HEAVY_GENRES)),
    ):
        selected = [
            row
            for row in rows
            if (genres := genre_lookup.get(normalize(row["artist_name"]), set()))
            and selector(genres)
        ]
        output.append(balance_row("genre_group", split_label, selected))

    for split_label, selector in (
        ("pre_2014_11_24", lambda date: str(date) < "2014-11-24"),
        ("post_2014_11_24", lambda date: str(date) >= "2014-11-24"),
    ):
        selected = [row for row in rows if selector(row["first_qualifying_debut"])]
        output.append(balance_row("debut_period", split_label, selected))

    write_csv(
        BALANCE_PATH,
        output,
        ["split_dimension", "split_group", "n_roster_artists", "n_unresolved", "unresolved_rate"],
    )
    for row in output:
        print(
            f"{row['split_dimension']}={row['split_group']}: "
            f"unresolved {row['n_unresolved']}/{row['n_roster_artists']} "
            f"({row['unresolved_rate']:.1%})"
        )


def balance_row(dimension, group, selected):
    unresolved_statuses = {
        "ambiguous_same_name",
        "ambiguous_same_name_duplicate_id_review",
        "review_composite_credit",
        "unmatched_no_exact_name",
        "review_truncated_search",
        "ambiguous_top_score",
    }
    unresolved = sum(row["match_status"] in unresolved_statuses for row in selected)
    return {
        "split_dimension": dimension,
        "split_group": group,
        "n_roster_artists": len(selected),
        "n_unresolved": unresolved,
        "unresolved_rate": unresolved / len(selected) if selected else 0.0,
    }


if __name__ == "__main__":
    main()