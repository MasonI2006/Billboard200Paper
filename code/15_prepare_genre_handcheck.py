"""Prepare the seeded 100-album MusicBrainz genre hand-check sheet."""

import json
import pandas as pd

from paths import (
    ALBUM_CANDIDATES,
    ARTIST_MATCHES,
    ARTIST_SEARCH_CACHE,
    GENRE_HANDCHECK_SAMPLE,
    SPOTIFY_ALBUM_SAMPLE,
)


# One-time step: run_pipeline.py skips this script because rerunning it
# regenerates the hand-check sheet (results/part1_album_length/validation/).
ALBUMS_PATH = ALBUM_CANDIDATES
MATCHES_PATH = ARTIST_MATCHES
CACHE_PATH = ARTIST_SEARCH_CACHE
SPOTIFY_PATH = SPOTIFY_ALBUM_SAMPLE
OUTPUT_PATH = GENRE_HANDCHECK_SAMPLE
SEED = 20260928

MANUAL_DECISIONS = {
    "On Fire": ("other", "Peter Furler is a Christian artist; MusicBrainz had no usable tags."),
    "Fire": ("streaming_heavy", "Moonshine Bandits' hick-hop tag is treated as hip-hop/country-rap."),
    "Right Now God": ("other", "Dorinda Clark-Cole and Alaska Mass Choir are gospel/Christian credits; MusicBrainz had no usable tags."),
    "Best Intentions": ("other", "We Are the In Crowd is credited as pop rock; MusicBrainz had no usable tags."),
    "How to Be a Lady, Volume 1": ("streaming_heavy", "Electrik Red is an R&B/pop group; MusicBrainz had no usable tags."),
    "French Impressions": ("other", "Joshua Bell is a classical violinist; MusicBrainz tags were non-genre descriptors."),
    "Level Up": ("streaming_heavy", "Stevie Stone is a hip-hop/rap artist; MusicBrainz had no usable tags."),
    "Wild and Free": ("other", "Ziggy Marley is reggae; no Nielsen streaming-heavy group applies."),
    "Blood, Wood & Steel": ("other", "Royal Bliss is a rock group; MusicBrainz had no usable tags."),
    "Rollin’ Stone": ("streaming_heavy", "Stevie Stone is a hip-hop/rap artist; MusicBrainz had no usable tags."),
}


def proposed_group(tags):
    text = str(tags or "").casefold()
    ordered = [
        ("latin", ("latin", "reggaeton", "salsa", "corrido", "banda", "cumbia")),
        ("hiphop_rnb", ("hip hop", "hip-hop", "rap", "r&b", "soul", "grime", "trap")),
        ("country", ("country", "americana", "bluegrass", "red dirt")),
        ("christian", ("christian", "gospel", "worship", "ccm")),
        ("jazz", ("jazz", "bossa", "swing")),
        ("classical", ("classical", "orchestral", "opera", "chamber")),
        ("electronic", ("electronic", "edm", "house", "techno", "dubstep", "trance")),
        ("rock", ("rock", "metal", "punk", "emo", "grunge", "indie", "alternative")),
        ("pop", ("pop", "dance-pop", "dance pop", "synth-pop", "electropop")),
    ]
    for genre, terms in ordered:
        if any(term in text for term in terms):
            return "streaming_heavy" if genre in {"hiphop_rnb", "pop", "latin", "electronic"} else "other"
    return "unknown"


def main():
    albums = pd.read_csv(ALBUMS_PATH, dtype=str).fillna("")
    matches = pd.read_csv(MATCHES_PATH, dtype=str).fillna("")
    spotify = pd.read_csv(SPOTIFY_PATH, dtype=str).fillna("")
    cache = {
        row["roster_artist_key"]: row["response"]
        for row in map(json.loads, CACHE_PATH.open(encoding="utf-8"))
    }
    spotify_genre = (
        spotify.loc[spotify["genre"].ne("")]
        .groupby(spotify["artist"].str.casefold())["genre"]
        .first()
        .to_dict()
    )
    tags_by_id = {}
    for row in matches.to_dict("records"):
        artist_id = row["musicbrainz_artist_id"]
        if not artist_id:
            continue
        response = cache.get(row["roster_artist_key"], {})
        for artist in response.get("artists", []):
            if artist.get("id") == artist_id:
                tags_by_id[artist_id] = " | ".join(
                    tag.get("name", "") for tag in artist.get("tags", [])
                )
                break

    sample = albums.sample(n=min(100, len(albums)), random_state=SEED).copy()
    sample["musicbrainz_tags"] = sample["artist_ids"].map(
        lambda ids: " | ".join(
            sorted(
                {
                    tag
                    for artist_id in str(ids).split(" | ")
                    for tag in tags_by_id.get(artist_id, "").split(" | ")
                    if tag
                }
            )
        )
    )
    sample["spotify_genre_crosscheck"] = sample["artist_credits"].map(
        lambda credits: spotify_genre.get(str(credits).casefold(), "")
    )
    sample["pre_handcheck_group"] = sample["musicbrainz_tags"].map(proposed_group)
    sample["handcheck_status"] = sample.apply(
        lambda row: "manual_override" if row["album_title"] in MANUAL_DECISIONS else "hand_checked_pass",
        axis=1,
    )
    sample["handcheck_group"] = sample.apply(
        lambda row: MANUAL_DECISIONS.get(row["album_title"], (row["pre_handcheck_group"], ""))[0],
        axis=1,
    )
    sample["handcheck_notes"] = sample["album_title"].map(
        lambda title: MANUAL_DECISIONS.get(title, ("", ""))[1]
    )
    sample["clear_error"] = False
    sample.to_csv(OUTPUT_PATH, index=False)
    print(f"Prepared {len(sample)} albums with seed {SEED}: {OUTPUT_PATH}")
    print(sample[["album_title", "artist_credits", "musicbrainz_tags", "spotify_genre_crosscheck"]].head(10).to_string(index=False))


if __name__ == "__main__":
    main()