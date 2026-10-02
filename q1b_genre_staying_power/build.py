import pandas as pd, numpy as np, re, unicodedata
U = "/mnt/user-data/uploads/"
def nz(s):
    s = s.fillna("").astype(str).map(lambda x: unicodedata.normalize("NFKD", x).encode("ascii","ignore").decode())
    return s.str.lower().str.replace(r"[^a-z0-9 ]", "", regex=True).str.replace(r"\s+", " ", regex=True).str.strip()

b = pd.read_csv(U+"billboard200.csv", dtype=str, low_memory=False)
b["Date"] = pd.to_datetime(b.Date, errors="coerce")
for c in ["Rank","Weeks in Charts"]: b[c] = pd.to_numeric(b[c], errors="coerce")
b = b[(b.Date >= "2010-01-01") & (b.Date <= "2019-12-31")].copy()

m = pd.read_csv(U+"musicbrainz_artist_matches.csv", low_memory=False)
m = m[m.musicbrainz_artist_id.notna()]
name2id = dict(zip(nz(m.artist_name), m.musicbrainz_artist_id))

a = pd.read_csv(U+"analysis_sample.csv")
first_id = a.artist_ids.astype(str).str.extract(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})")[0]
gmap = pd.DataFrame({"mbid": first_id, "genre": a.genre, "heavy": a.heavy}).dropna().drop_duplicates("mbid").set_index("mbid")
print("artists with a genre label:", len(gmap), gmap.heavy.value_counts().to_dict())

b["an"] = nz(b.Artist)
b["mbid"] = b.an.map(name2id)
b = b.join(gmap, on="mbid")
print("chart rows 2010-2019:", len(b))
print("  rows with MusicBrainz artist ID: %.1f%%" % (100*b.mbid.notna().mean()))
print("  rows with genre label:           %.1f%%" % (100*b.genre.notna().mean()))
cov = b.groupby(b.Date.dt.year).agg(slots_labelled=("genre", lambda x: x.notna().mean()))
deb = b[b["Weeks in Charts"] == 1]
cov["debuts_labelled"] = deb.groupby(deb.Date.dt.year).genre.apply(lambda x: x.notna().mean())
print(cov.round(3).to_string())
b.to_pickle("chart_labelled.pkl")
