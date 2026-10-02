import pandas as pd, numpy as np, unicodedata
def nz(s):
    s = s.fillna("").astype(str).map(lambda x: unicodedata.normalize("NFKD", x).encode("ascii","ignore").decode())
    s = s.str.lower().str.replace(r"\(.*?\)|\[.*?\]", "", regex=True)
    return s.str.replace(r"[^a-z0-9 ]", "", regex=True).str.replace(r"\s+", " ", regex=True).str.strip()
b = pd.read_pickle("chart_labelled.pkl"); b = b[b.genre.notna()].copy()
rg = pd.read_csv("/mnt/user-data/uploads/musicbrainz_release_groups.csv", low_memory=False, usecols=["title","first_release_date","roster_artist_ids"])
rg["mbid"] = rg.roster_artist_ids.astype(str).str.extract(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})")[0]
rg["t"] = nz(rg.title)
rg["rel"] = pd.to_datetime(rg.first_release_date.astype(str).str[:4] + "-07-01", errors="coerce")   # year precision is enough for a 3-year cutoff
full = pd.to_datetime(rg.first_release_date, errors="coerce", format="mixed")
rg["rel"] = full.fillna(rg.rel)
rg = rg.dropna(subset=["rel"]).sort_values("rel").drop_duplicates(["mbid","t"])
b["t"] = nz(b.Song)
b = b.merge(rg[["mbid","t","rel"]], on=["mbid","t"], how="left")
print("labelled chart rows with a release date: %.1f%%" % (100*b.rel.notna().mean()))
print(b.groupby("heavy").rel.apply(lambda x: x.notna().mean()).round(3))
b = b.dropna(subset=["rel"])
b["old3"] = ((b.Date - b.rel).dt.days / 365.25 >= 3).astype(int)
t = b.groupby([b.Date.dt.year, "heavy"]).old3.mean().unstack().rename(columns={0:"other",1:"streaming_heavy"})
t.index.name = "year"; print((100*t).round(1).to_string()); t.to_csv("results_album_age_share.csv")
