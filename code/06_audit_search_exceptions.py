"""Create audit files for zero-result retries and partial composite credits."""

import csv
import json
import re
import unicodedata
from musicbrainz_helpers import CACHE_PATH, load_cache, load_roster
from paths import ARTIST_MATCHES_REVIEW, FLAGGED_COMPOSITE_PARTIAL, TRUE_NOMATCH_ZERO


ZERO_LIST_PATH = TRUE_NOMATCH_ZERO
ZERO_AUDIT_PATH = TRUE_NOMATCH_ZERO
COMPOSITE_AUDIT_PATH = FLAGGED_COMPOSITE_PARTIAL
REVIEW_PATH = ARTIST_MATCHES_REVIEW
SPECIAL_CHARS = set("$+():.")

PARTIAL_CREDITS = {
    "Frank Sinatra, Dean Martin & Sammy Davis Jr": (
        "The Rat Pack",
        "35e227e5-f724-4699-91b2-d5184cdc7411",
        "Joint billing names three performers; the MusicBrainz candidate has an exact full-credit alias.",
    ),
    "Dharoha Project, Laura Marling And Mumford & Sons": (
        "Mumford & Sons",
        "c44e9c22-ef82-4a77-9bcd-af6c958446d6",
        "Candidate corresponds only to one named act in a three-act billing.",
    ),
    "JP, Chrissie & The Fairground Boys": (
        "The Fairground Boys",
        "8d4e845b-f688-41b8-a930-98fa4a71920d",
        "Candidate corresponds only to the group component of the joint billing.",
    ),
    "Lil Boosie, Webbie, Lil Trill & Trill Fam": (
        "Lil Trill",
        "077c166a-d8dc-44d4-bf01-4bb7fea2b943",
        "Candidate corresponds only to one named performer in a four-act billing.",
    ),
}


def normalize_credit(value):
    text = unicodedata.normalize("NFKC", str(value or "")).casefold().strip().strip('"')
    return re.sub(r"[\W_]+", " ", text, flags=re.UNICODE).strip()


def candidate_matches_credit(candidate, credit):
    target = normalize_credit(credit)
    if normalize_credit(candidate.get("name", "")) == target:
        return "canonical_name"
    for alias in candidate.get("aliases", []):
        alias_name = alias.get("name", "") if isinstance(alias, dict) else alias
        if normalize_credit(alias_name) == target:
            return "exact_alias"
    return ""


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    roster = load_roster()
    roster_by_name = {row["artist_name"]: row for row in roster}
    cache = load_cache()
    query_by_key = {}
    with CACHE_PATH.open(encoding="utf-8") as stream:
        for line in stream:
            record = json.loads(line)
            query_by_key[record["roster_artist_key"]] = record.get("query", "")
    zero_names = read_csv(ZERO_LIST_PATH)
    zero_audit = []

    for item in zero_names:
        name = item["artist_name"]
        roster_row = roster_by_name[name]
        response = cache[roster_row["roster_artist_key"]]
        candidates = response.get("artists", [])
        previous_count = item.get("previous_api_count", "0") or "0"
        query = query_by_key.get(roster_row["roster_artist_key"], "")
        zero_audit.append(
            {
                "artist_name": name,
                "first_qualifying_debut": item.get(
                    "first_qualifying_debut", roster_row["first_qualifying_debut"]
                ),
                "original_api_count": previous_count,
                "retry_api_count": response.get("count", 0),
                "retry_returned_candidates": len(candidates),
                "retry_query": query,
                "top_candidate_names": " | ".join(
                    candidate.get("name", "") for candidate in candidates[:5]
                ),
                "contains_lucene_special_character": any(
                    character in name for character in SPECIAL_CHARS
                ),
                "api_error_recorded": False,
                "retry_result": (
                    "candidates_returned"
                    if candidates
                    else "zero_candidates_after_literal_alias_aware_retry"
                ),
            }
        )

    zero_fields = [
        "artist_name",
        "first_qualifying_debut",
        "original_api_count",
        "retry_api_count",
        "retry_returned_candidates",
        "retry_query",
        "top_candidate_names",
        "contains_lucene_special_character",
        "api_error_recorded",
        "retry_result",
    ]
    write_csv(ZERO_AUDIT_PATH, zero_audit, zero_fields)

    review = read_csv(REVIEW_PATH)
    review_by_name = {row["artist_name"].strip('"'): row for row in review}
    composite_rows = []
    for credit, (candidate_name, candidate_id, rationale) in PARTIAL_CREDITS.items():
        row = review_by_name[credit]
        candidates = json.loads(row["candidate_summary"] or "[]")
        selected = next(
            (
                candidate
                for candidate in candidates
                if candidate.get("id") == candidate_id
                and candidate.get("name") == candidate_name
            ),
            None,
        )
        match_basis = candidate_matches_credit(selected, credit) if selected else ""
        assigned_id = candidate_id if match_basis == "exact_alias" else ""
        if not assigned_id:
            rationale = (
                "Top candidate does not have an exact canonical-name or alias match to the full joint credit; "
                + rationale
            )
        composite_rows.append(
            {
                "artist_name": credit,
                "first_qualifying_debut": row["first_qualifying_debut"],
                "musicbrainz_artist_id": assigned_id,
                "top_candidate_name": candidate_name,
                "top_candidate_id_for_review_only": candidate_id,
                "match_status": (
                    "matched_full_credit_alias"
                    if assigned_id
                    else "composite_partial_candidate_do_not_assign"
                ),
                "match_basis": match_basis,
                "rationale": rationale,
                "candidate_context": row["candidate_summary"],
            }
        )
    composite_fields = [
        "artist_name",
        "first_qualifying_debut",
        "musicbrainz_artist_id",
        "top_candidate_name",
        "top_candidate_id_for_review_only",
        "match_status",
        "match_basis",
        "rationale",
        "candidate_context",
    ]
    write_csv(COMPOSITE_AUDIT_PATH, composite_rows, composite_fields)

    print(
        f"Updated {ZERO_AUDIT_PATH}: {len(zero_audit)} retry rows, "
        f"{sum(row['retry_returned_candidates'] > 0 for row in zero_audit)} now return candidates, "
        f"{sum(row['retry_returned_candidates'] == 0 for row in zero_audit)} still return none."
    )
    print(f"Wrote {len(composite_rows)} partial-credit rows to {COMPOSITE_AUDIT_PATH}.")


if __name__ == "__main__":
    main()