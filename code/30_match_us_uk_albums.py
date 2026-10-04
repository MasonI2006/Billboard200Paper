"""Match Billboard 200 albums to UK Official Albums Chart albums (docs/matched_albums_plan.md).

Rule (fixed in the plan): titles equal after normalisation, or the U.S. title starts with the UK
title when the UK title is at its 40-character cap; and artists equal, or one a word-boundary
prefix of the other, or the U.S. artist starts with the UK artist when the UK name is at its
~30-character cap. Albums matching more than one album on the other chart are dropped.
Titles are compared with spaces removed, because some Kaggle titles have lost a space
("STRONGER withEach Tear"). Matching uses all weeks 2000 onward.
"""

import bisect
import unicodedata

import numpy as np
import pandas as pd

from paths import INTERIM_DIR, RAW_BILLBOARD200, RESULTS_P2, UK_ALBUMS_WEEKLY

MATCHES = INTERIM_DIR / "us_uk_album_matches.csv"
OUT = RESULTS_P2 / "matched"
UK_TITLE_CAP = 40
UK_ARTIST_CAP = 28


def norm(series):
    s = series.fillna("").astype(str).map(lambda x: unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode())
    s = s.str.lower().str.replace("&", " and ", regex=False)
    return s.str.replace(r"[^a-z0-9 ]", "", regex=True).str.replace(r"\s+", " ", regex=True).str.strip()


def title_key(series):
    return norm(series).str.replace(" ", "", regex=False)


def load_us():
    us = pd.read_csv(RAW_BILLBOARD200, dtype=str, low_memory=False, usecols=["Date", "Song", "Artist", "Rank"])
    us["Date"] = pd.to_datetime(us["Date"], errors="coerce")
    us["Rank"] = pd.to_numeric(us["Rank"], errors="coerce")
    us = us[us["Date"] >= "2000-01-01"].dropna(subset=["Date"]).copy()
    us["tkey"], us["akey"] = title_key(us["Song"]), norm(us["Artist"])
    return us


def load_uk():
    uk = pd.read_csv(UK_ALBUMS_WEEKLY, parse_dates=["chart_week"])
    uk = uk[~uk["no1_unidentified"]].copy()
    uk["tkey"], uk["akey"] = title_key(uk["album"]), norm(uk["artist"])
    return uk


def artist_ok(us_artist, uk_artist, uk_raw_len):
    if us_artist.replace(" ", "") == uk_artist.replace(" ", ""):
        return True
    short, long_ = sorted((us_artist, uk_artist), key=len)
    if short and long_.startswith(short + " "):
        return True
    return uk_raw_len >= UK_ARTIST_CAP and us_artist.startswith(uk_artist)


def match(us_albums, uk_albums):
    by_title = uk_albums.groupby("tkey").indices
    us_sorted = us_albums.sort_values("tkey").reset_index(drop=True)
    us_keys = us_sorted["tkey"].tolist()
    pairs = []
    for i, row in us_albums.iterrows():
        for j in by_title.get(row["tkey"], []):
            uk = uk_albums.iloc[j]
            if artist_ok(row["akey"], uk["akey"], uk["artist_len"]):
                pairs.append((i, j, "title equal"))
    capped = uk_albums[(uk_albums["title_len"] >= UK_TITLE_CAP) & (uk_albums["tkey"] != "")]
    for j, uk in capped.iterrows():
        start = bisect.bisect_left(us_keys, uk["tkey"])
        for k in range(start, len(us_keys)):
            if not us_keys[k].startswith(uk["tkey"]):
                break
            us = us_sorted.iloc[k]
            if us["tkey"] != uk["tkey"] and artist_ok(us["akey"], uk["akey"], uk["artist_len"]):
                pairs.append((us["us_index"], j, "title prefix (UK title capped)"))
    pairs = pd.DataFrame(pairs, columns=["us_index", "uk_index", "match_type"]).drop_duplicates(["us_index", "uk_index"])
    n_us = pairs.groupby("us_index").size()
    n_uk = pairs.groupby("uk_index").size()
    ambiguous = pairs["us_index"].map(n_us).gt(1) | pairs["uk_index"].map(n_uk).gt(1)
    return pairs[~ambiguous], int(ambiguous.sum()), pairs


def main():
    us, uk = load_us(), load_uk()
    us_albums = (us.groupby(["tkey", "akey"])
                 .agg(us_title=("Song", "first"), us_artist=("Artist", "first"), us_first_week=("Date", "min"),
                      us_weeks=("Date", "nunique")).reset_index())
    us_albums["us_index"] = us_albums.index
    uk_albums = (uk.groupby(["tkey", "akey"])
                 .agg(uk_album=("album", "first"), uk_artist=("artist", "first"), uk_first_week=("chart_week", "min"),
                      uk_weeks=("chart_week", "nunique")).reset_index())
    uk_albums["title_len"] = uk_albums["uk_album"].str.len()
    uk_albums["artist_len"] = uk_albums["uk_artist"].str.len()
    print(f"distinct albums 2000+: U.S. {len(us_albums)}, UK {len(uk_albums)}", flush=True)

    kept, n_ambiguous, all_pairs = match(us_albums, uk_albums)
    m = (kept.merge(us_albums.add_prefix("us_").rename(columns={"us_us_index": "us_index"}), on="us_index")
             .merge(uk_albums.add_prefix("uk_"), left_on="uk_index", right_index=True))
    m = m.rename(columns={"us_us_title": "us_title", "us_us_artist": "us_artist", "us_us_first_week": "us_first_week",
                          "us_us_weeks": "us_weeks", "uk_uk_album": "uk_album", "uk_uk_artist": "uk_artist",
                          "uk_uk_first_week": "uk_first_week", "uk_uk_weeks": "uk_weeks"})
    m["album_id"] = np.arange(len(m))
    cols = ["album_id", "us_title", "us_artist", "us_tkey", "us_akey", "uk_album", "uk_artist", "uk_tkey", "uk_akey",
            "match_type", "us_first_week", "uk_first_week", "us_weeks", "uk_weeks"]
    m = m[cols]
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    m.to_csv(MATCHES, index=False)

    OUT.mkdir(parents=True, exist_ok=True)
    m.sample(50, random_state=20260928).to_csv(OUT / "match_handcheck_sample.csv", index=False)
    print(f"candidate pairs {len(all_pairs)}; dropped as ambiguous {n_ambiguous}; matched albums {len(m)} "
          f"({m['match_type'].value_counts().to_dict()})", flush=True)

    # share of each chart's slots held by matched albums, by year (selection caveat)
    us_keys = set(zip(m["us_tkey"], m["us_akey"]))
    uk_keys = set(zip(m["uk_tkey"], m["uk_akey"]))
    us["matched"] = [k in us_keys for k in zip(us["tkey"], us["akey"])]
    uk["matched"] = [k in uk_keys for k in zip(uk["tkey"], uk["akey"])]
    top = us[us["Rank"] <= 100]
    shares = pd.DataFrame({
        "us_top100_slots_matched": top.groupby(top["Date"].dt.year)["matched"].mean(),
        "us_bb200_slots_matched": us.groupby(us["Date"].dt.year)["matched"].mean(),
        "uk_top100_slots_matched": uk.groupby(uk["chart_week"].dt.year)["matched"].mean(),
    }).loc[2000:2024]
    shares.to_csv(OUT / "matched_slot_shares_by_year.csv")
    print(shares.loc[2009:2019].round(3).to_string(), flush=True)


if __name__ == "__main__":
    main()
