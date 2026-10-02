"""Report unresolved MusicBrainz identities by Spotify genre and debut period."""

import csv
import re
import unicodedata
import pandas as pd

from load_clean_data import load_chart
from paths import ARTIST_MATCHES, ROSTER, SPOTIFY_ALBUM_SAMPLE, UNRESOLVED_BALANCE


MATCHES_PATH = ARTIST_MATCHES
ROSTER_PATH = ROSTER
SPOTIFY_SAMPLE_PATH = SPOTIFY_ALBUM_SAMPLE
OUTPUT_PATH = UNRESOLVED_BALANCE
RULE_CHART_DATE = pd.Timestamp("2014-12-10")
HEAVY_GENRES = {"hiphop_rnb", "pop", "latin", "electronic"}
RESOLVED_STATUSES = {
    "matched_exact_name",
    "matched_exact_alias",
    "matched_unique_score_100",
    "matched_auto_metadata",
    "matched_group_credit",
    "matched_full_credit_alias",
}


def normalize(value):
    text = unicodedata.normalize("NFKC", str(value or "")).casefold().strip().strip('"')
    return re.sub(r"[\W_]+", " ", text).strip()


def write_csv(rows):
    fields = [
        "split_dimension",
        "split_group",
        "n_units",
        "n_unresolved",
        "unresolved_rate",
        "note",
    ]
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def append_rate(rows, dimension, group, records, unit_key, note):
    unresolved = sum(not record["is_resolved"] for record in records)
    denominator = len(records)
    rows.append(
        {
            "split_dimension": dimension,
            "split_group": group,
            "n_units": denominator,
            "n_unresolved": unresolved,
            "unresolved_rate": unresolved / denominator if denominator else "",
            "note": note,
        }
    )


def main():
    matches = pd.read_csv(MATCHES_PATH, dtype=str).fillna("")
    roster = pd.read_csv(ROSTER_PATH, dtype=str).fillna("")
    spotify = pd.read_csv(SPOTIFY_SAMPLE_PATH, low_memory=False)
    status_by_key = dict(zip(matches["roster_artist_key"], matches["match_status"]))
    id_by_key = dict(zip(matches["roster_artist_key"], matches["musicbrainz_artist_id"]))

    spotify_genre = (
        spotify.dropna(subset=["genre"])
        .groupby(spotify["artist"].map(normalize))["genre"]
        .agg(lambda values: values.mode().iloc[0])
        .to_dict()
    )

    records = []
    for row in roster.to_dict("records"):
        artist_name = row["artist_name"]
        key = row["roster_artist_key"]
        genre = spotify_genre.get(normalize(artist_name), "")
        records.append(
            {
                "roster_artist_key": key,
                "artist_name": artist_name,
                "first_qualifying_debut": row["first_qualifying_debut"],
                "genre": genre,
                "status": status_by_key.get(key, "missing_match_row"),
                "musicbrainz_artist_id": id_by_key.get(key, ""),
                "is_resolved": bool(id_by_key.get(key, ""))
                and status_by_key.get(key, "") in RESOLVED_STATUSES,
            }
        )

    rows = []
    genre_known = [record for record in records if record["genre"]]
    heavy = [record for record in genre_known if record["genre"] in HEAVY_GENRES]
    other = [record for record in genre_known if record["genre"] not in HEAVY_GENRES]
    append_rate(
        rows,
        "artist_genre",
        "streaming_heavy",
        heavy,
        "artist",
        "Artist-level; genre from exact normalized artist match in Spotify sample.",
    )
    append_rate(
        rows,
        "artist_genre",
        "other",
        other,
        "artist",
        "Artist-level; genre from exact normalized artist match in Spotify sample.",
    )

    pre = [record for record in records if record["first_qualifying_debut"] < "2014-11-24"]
    post = [record for record in records if record["first_qualifying_debut"] >= "2014-11-24"]
    period_note = (
        "First qualifying debut defines the roster and is restricted to pre-rule dates; "
        "the post group is structurally empty and is not an estimable comparison."
    )
    append_rate(rows, "first_qualifying_artist_debut", "pre_rule", pre, "artist", period_note)
    append_rate(rows, "first_qualifying_artist_debut", "post_rule", post, "artist", period_note)

    roster_credit_to_key = {}
    for row in roster.to_dict("records"):
        for credit in row["source_credits"].split(" | "):
            roster_credit_to_key[normalize(credit)] = row["roster_artist_key"]
    debut_rows = load_chart("b200")
    debut_rows = debut_rows.loc[
        (debut_rows["Weeks in Charts"] == 1)
        & debut_rows["Date"].between("2009-01-01", "2024-12-31")
    ].copy()
    debut_rows["roster_key"] = debut_rows["Artist"].map(
        lambda credit: roster_credit_to_key.get(normalize(credit), "")
    )
    charting = debut_rows.loc[debut_rows["roster_key"] != ""].copy()
    charting["period"] = charting["Date"].map(
        lambda date: "pre_rule" if date < RULE_CHART_DATE else "post_rule"
    )
    chart_records = []
    for row in charting.to_dict("records"):
        key = row["roster_key"]
        chart_records.append(
            {
                "artist_name": row["Artist"],
                "period": row["period"],
                "is_resolved": bool(id_by_key.get(key, ""))
                and status_by_key.get(key, "") in RESOLVED_STATUSES,
            }
        )
    chart_period_note = (
        "Supporting album-debut-weighted split among charting album debuts by roster artists; "
        "not the first-qualifying-artist-debut split."
    )
    for group in ("pre_rule", "post_rule"):
        selected = [record for record in chart_records if record["period"] == group]
        append_rate(rows, "charting_album_debut", group, selected, "debut row", chart_period_note)

    write_csv(rows)
    print(f"Genre-known roster artists: {len(genre_known)} of {len(records)}")
    print(f"Roster artists with post-rule first qualifying debut: {len(post)}")
    print(f"Charting album-debut rows matched to roster: {len(chart_records)}")
    print(f"Saved balance report to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()