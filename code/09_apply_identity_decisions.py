"""Apply explicit alias/group identity decisions already reviewed by the user."""

import csv
import json
import re
import unicodedata
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
MATCHES_PATH = DATA_DIR / "musicbrainz_artist_matches.csv"
REVIEW_PATH = DATA_DIR / "musicbrainz_artist_matches_review.csv"
TARGETED_PATH = DATA_DIR / "musicbrainz_targeted_artist_searches.csv"
DECISIONS_PATH = DATA_DIR / "musicbrainz_targeted_identity_decisions.csv"

DECISIONS = {
    "Frank Sinatra, Dean Martin & Sammy Davis Jr": {
        "musicbrainz_artist_id": "35e227e5-f724-4699-91b2-d5184cdc7411",
        "entity_name": "The Rat Pack",
        "entity_type": "Group",
        "decision": "matched_full_credit_alias",
        "basis": "Exact MusicBrainz alias equals full joint Billboard credit.",
    },
    "The Kenny Wayne Shepherd Band": {
        "musicbrainz_artist_id": "",
        "entity_name": "Kenny Wayne Shepherd",
        "entity_type": "Person",
        "decision": "unresolved_band_entity_not_found",
        "basis": "The exact billed-band search returned only the solo Person entity; its alias does not convert it into a separate band entity, so do not assign the Person to the band credit.",
    },
    "The Dead Rabbitts": {
        "musicbrainz_artist_id": "ebafff3d-0105-4e5d-a7a4-98972c48a57f",
        "entity_name": "Dead Rabbitts",
        "entity_type": "Group",
        "decision": "matched_group_credit",
        "basis": "The billed act is a group; exact core name resolves to the Group entity, with only the leading article differing.",
    },
    "The Nick Hexum Quintet": {
        "musicbrainz_artist_id": "23af1753-e926-4338-aef6-7cfe2861d1d8",
        "entity_name": "Nick Hexum Quintet",
        "entity_type": "Group",
        "decision": "matched_group_credit",
        "basis": "The billed act names the Quintet; MusicBrainz has a separate Group entity, preferred over solo Person Nick Hexum.",
    },
    "The CAJO Family": {
        "musicbrainz_artist_id": "",
        "entity_name": "",
        "entity_type": "",
        "decision": "unmatched_no_artist_entity",
        "basis": "Exact full-credit and CAJO searches did not identify a matching artist or group; candidates were unrelated.",
    },
}


def read_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader), list(reader.fieldnames or [])


def write_rows(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def normalize_artist(value):
    text = unicodedata.normalize("NFKC", str(value or "")).casefold().strip().strip('"')
    return re.sub(r"[\W_]+", " ", text).strip()


def main():
    matches, fields = read_rows(MATCHES_PATH)
    targeted, _ = read_rows(TARGETED_PATH)
    targeted_by_name = {row["artist_name"]: row for row in targeted}
    for name in (
        "The Kenny Wayne Shepherd Band",
        "The Dead Rabbitts",
        "The Nick Hexum Quintet",
        "The CAJO Family",
    ):
        if name not in targeted_by_name:
            raise ValueError(f"Missing targeted search evidence for {name}")

    applied = []
    for name, decision in DECISIONS.items():
        target_key = normalize_artist(name)
        row = next(
            (candidate for candidate in matches if normalize_artist(candidate["artist_name"]) == target_key),
            None,
        )
        if row is None:
            continue
        row["musicbrainz_artist_id"] = decision["musicbrainz_artist_id"]
        row["match_status"] = decision["decision"]
        row["match_basis"] = decision["basis"]
        row["match_candidate_summary"] = json.dumps(
            {
                "id": decision["musicbrainz_artist_id"],
                "name": decision["entity_name"],
                "type": decision["entity_type"],
            },
            ensure_ascii=False,
        ) if decision["musicbrainz_artist_id"] else ""
        applied.append({"artist_name": row["artist_name"], **decision})

    id_to_rows = {}
    for row in matches:
        artist_id = row.get("musicbrainz_artist_id", "")
        if artist_id:
            id_to_rows.setdefault(artist_id, []).append(row)
    for same_id_rows in id_to_rows.values():
        if len(same_id_rows) > 1:
            for row in same_id_rows:
                row["match_status"] = "duplicate_roster_entries_same_artist_id_review"
                row["match_basis"] = "Multiple roster spellings map to this MusicBrainz ID; reconcile before collection."
                row["musicbrainz_artist_id"] = ""

    write_rows(MATCHES_PATH, matches, fields)
    resolved_statuses = {
        "matched_exact_name",
        "matched_exact_alias",
        "matched_unique_score_100",
        "matched_auto_metadata",
        "matched_group_credit",
        "matched_full_credit_alias",
    }
    review_rows = [row for row in matches if row.get("match_status") not in resolved_statuses]
    write_rows(REVIEW_PATH, review_rows, fields)
    write_rows(
        DECISIONS_PATH,
        applied,
        [
            "artist_name",
            "musicbrainz_artist_id",
            "entity_name",
            "entity_type",
            "decision",
            "basis",
        ],
    )
    print(f"Applied explicit identity decisions for {len(applied)} roster entries.")
    print(f"Resolved identity rows: {len(matches) - len(review_rows)}; review rows: {len(review_rows)}")


if __name__ == "__main__":
    main()