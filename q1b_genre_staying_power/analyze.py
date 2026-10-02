import pandas as pd, numpy as np, re, statsmodels.formula.api as smf
from scipy import stats
RULE = pd.Timestamp("2014-12-10")
b = pd.read_pickle("chart_labelled.pkl")
b["key"] = b.an + "|" + b.Song.str.lower().str.strip()

# album runs: debut week, then weeks on chart within 52 / 26 weeks after debut
deb = b[b["Weeks in Charts"] == 1].drop_duplicates("key")[["key","Date","Rank","mbid","genre","heavy"]].rename(columns={"Date":"debut","Rank":"debut_rank"})
deb = deb[(deb.debut >= "2010-01-06") & (deb.debut <= "2018-12-26") & deb.genre.notna()]
pos = b[b.key.isin(deb.key)][["key","Date"]].merge(deb[["key","debut"]], on="key")
pos["dw"] = (pos.Date - pos.debut).dt.days // 7
w52 = pos[(pos.dw >= 0) & (pos.dw < 52)].groupby("key").size()
w26 = pos[(pos.dw >= 0) & (pos.dw < 26)].groupby("key").size()
on26 = pos[pos.dw == 26].groupby("key").size()
deb["weeks52"] = deb.key.map(w52).fillna(1)
deb["weeks26"] = deb.key.map(w26).fillna(1)
deb["still_on_26"] = deb.key.isin(on26.index).astype(int)
deb["post"] = (deb.debut >= RULE).astype(int)
deb["year"] = deb.debut.dt.year
deb["heavy"] = deb.heavy.astype(int)
deb["rank_bin"] = pd.cut(deb.debut_rank, [0,10,50,100,200], labels=["1-10","11-50","51-100","101-200"])
deb.to_csv("album_runs.csv", index=False)
print("albums:", len(deb), "| artists:", deb.mbid.nunique())
print(deb.groupby(["heavy","post"]).agg(n=("key","size"), weeks52=("weeks52","mean"), median52=("weeks52","median"), still26=("still_on_26","mean"), weeks26=("weeks26","mean")).round(2))

def fit(y, d, extra="", cl="mbid"):
    f = f"{y} ~ post:heavy + C(genre) + C(year){extra}"
    return smf.ols(f, d).fit(cov_type="cluster", cov_kwds={"groups": d[cl]})

def wild_boot(y, d, B=9999, seed=20260928):
    """Restricted wild cluster bootstrap, genre clusters, Webb weights; t-stats use genre-cluster SEs."""
    import patsy
    f_full = f"{y} ~ post:heavy + C(genre) + C(year)"
    yv, X = patsy.dmatrices(f_full, d, return_type="dataframe")
    j = list(X.columns).index("post:heavy")
    yv = yv.values.ravel(); Xv = X.values
    Xr = np.delete(Xv, j, axis=1)
    br = np.linalg.lstsq(Xr, yv, rcond=None)[0]; fr = Xr @ br; ur = yv - fr
    XtXi = np.linalg.pinv(Xv.T @ Xv); A = XtXi @ Xv.T
    g = d["genre"].values; G = np.unique(g); idx = [np.where(g == k)[0] for k in G]
    def tstat(yy):
        beta = A @ yy; e = yy - Xv @ beta
        meat = sum(np.outer(Xv[i].T @ e[i], Xv[i].T @ e[i]) for i in idx)
        V = XtXi @ meat @ XtXi
        return beta[j] / np.sqrt(V[j, j]), beta[j]
    t0, b0 = tstat(yv)
    W = np.array([-np.sqrt(1.5), -1, -np.sqrt(.5), np.sqrt(.5), 1, np.sqrt(1.5)])
    rng = np.random.default_rng(seed); ts = np.empty(B)
    for r in range(B):
        wg = rng.choice(W, len(G)); wv = np.empty(len(yv))
        for k, i in enumerate(idx): wv[i] = wg[k]
        ts[r] = tstat(fr + ur * wv)[0]
    return (np.abs(ts) >= abs(t0)).mean(), len(G)

rows = []
for y in ["weeks52", "still_on_26", "weeks26"]:
    m = fit(y, deb)
    p_wb, G = wild_boot(y, deb, B=9999 if y == "weeks52" else 1999)
    rows.append([y, "main", m.params["post:heavy"], m.bse["post:heavy"], m.pvalues["post:heavy"], p_wb, G, len(deb)])
m = fit("weeks52", deb, " + C(rank_bin)")
rows.append(["weeks52", "+ debut-rank controls", m.params["post:heavy"], m.bse["post:heavy"], m.pvalues["post:heavy"], np.nan, np.nan, len(deb)])
m = smf.ols("weeks52 ~ post:heavy + C(mbid) + C(year)", deb).fit(cov_type="cluster", cov_kwds={"groups": deb.mbid})
dfe = deb[deb.groupby("mbid").post.transform("nunique") == 2]
rows.append(["weeks52", "artist fixed effects", m.params["post:heavy"], m.bse["post:heavy"], m.pvalues["post:heavy"], np.nan, np.nan, f"{len(deb)} ({dfe.mbid.nunique()} artists with pre+post albums)"])
R = pd.DataFrame(rows, columns=["outcome","spec","coef","se_artist","p_artist","p_wildboot_genre","genre_clusters","n"])
R.to_csv("results_main.csv", index=False); print(R.round(4).to_string(index=False))

# event study
yrs = [y for y in range(2010, 2019) if y != 2014]
es = smf.ols("weeks52 ~ " + " + ".join(f"I((year=={y})*heavy)" for y in yrs) + " + C(genre) + C(year)", deb).fit(cov_type="cluster", cov_kwds={"groups": deb.mbid})
E = pd.DataFrame({"coef": es.params.filter(regex=r"^I\(\(year"), "se": es.bse.filter(regex=r"^I\(\(year")})
E.index = [int(re.search(r"(20\d\d)", i).group(1)) for i in E.index]; E = E.sort_index()
E["p"] = 2 * (1 - stats.norm.cdf(abs(E.coef / E.se)))
pre = [n for n in es.params.index if re.search(r"year ?== ?201[0-3]\)", n)]
R_ = np.vstack([(es.params.index == n).astype(float) for n in pre])
print("\nEvent study (weeks in first 52, heavy minus other, ref 2014):"); print(E.round(2).to_string())
print("joint pre-2014 test p =", round(float(es.wald_test(R_, scalar=True).pvalue), 3))
E.to_csv("results_event_study.csv")
