"""Adjudicate the seeded edition sample against cached official MusicBrainz records."""

import json
from urllib.parse import parse_qs, urlparse
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
SAMPLE_PATH = DATA_DIR / "musicbrainz_edition_handcheck_sample.csv"
CACHE_PATH = DATA_DIR / "musicbrainz_official_release_cache.jsonl"
OUTPUT_PATH = DATA_DIR / "musicbrainz_edition_handcheck_sample.csv"


def load_release_cache():
    by_group = {}
    with CACHE_PATH.open(encoding="utf-8") as stream:
        for line in stream:
            record = json.loads(line)
            response = record["response"]
            group_id = parse_qs(urlparse(record.get("url", "")).query).get(
                "release-group", [""]
            )[0]
            for release in response.get("releases", []):
                if group_id:
                    by_group.setdefault(group_id, {})[release.get("id")] = release
    return by_group


def track_count(release):
    return sum(int(media.get("track-count") or 0) for media in release.get("media", []))


def main():
    sample = pd.read_csv(SAMPLE_PATH, dtype=str).fillna("")
    releases_by_group = load_release_cache()
    statuses = []
    notes = []
    competing = []

    for _, row in sample.iterrows():
        releases = list(releases_by_group.get(row["release_group_id"], {}).values())
        dated = [release for release in releases if release.get("date")]
        if not dated:
            statuses.append("fail_no_dated_official_release")
            notes.append("No dated official release was available in cached API records.")
            competing.append("[]")
            continue

        earliest_date = min(release["date"] for release in dated)
        earliest = [release for release in dated if release["date"] == earliest_date]
        counts = {release.get("id"): track_count(release) for release in earliest}
        minimum_count = min(counts.values())
        selected_count = int(row["standard_track_count"])
        selected_date = row["release_date"]
        selected_is_rule = selected_date == earliest_date and selected_count == minimum_count
        statuses.append("pass" if selected_is_rule else "fail")
        notes.append(
            f"Earliest cached official date={earliest_date}; same-day counts={counts}; "
            f"selected date/count={selected_date}/{selected_count}."
        )
        competing.append(
            json.dumps(
                [
                    {
                        "release_id": release.get("id"),
                        "title": release.get("title"),
                        "date": release.get("date"),
                        "country": release.get("country"),
                        "track_count": counts.get(release.get("id")),
                    }
                    for release in sorted(earliest, key=lambda item: item.get("id", ""))
                ],
                ensure_ascii=False,
            )
        )

    sample["handcheck_status"] = statuses
    sample["handcheck_notes"] = notes
    sample["handcheck_competing_earliest_editions"] = competing
    sample["handcheck_source"] = "Cached MusicBrainz API official-release responses; browser pages were JS-challenge blocked."
    sample.to_csv(OUTPUT_PATH, index=False)
    print(f"Hand-check sample rows: {len(sample)}")
    print(sample["handcheck_status"].value_counts().to_string())
    print(f"Error rate: {(sample['handcheck_status'] != 'pass').mean():.1%}")


if __name__ == "__main__":
    main()