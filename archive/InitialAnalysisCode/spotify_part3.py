from pathlib import Path
exec(open(Path(__file__).resolve().parent / 'spotify_part2.py').read().split('O=pd.DataFrame')[0].replace('print(','(lambda *a,**k:None)('))
# event study, Billboard-matched, binary high, ref 2014 (pool 2009-10 for small n)
gb["yr"]=gb.year.clip(lower=2010)
yrs=[y for y in range(2010,2025) if y!=2014]
es=smf.ols("ln_tracks ~ "+" + ".join(f"I((yr=={y})*high)" for y in yrs)+" + C(genre) + C(yr)",gb).fit(cov_type="cluster",cov_kwds={"groups":gb.artist})
E=pd.DataFrame({"coef":es.params.filter(regex=r"^I\(\(yr"),"se":es.bse.filter(regex=r"^I\(\(yr")})
E.index=[int(re.search(r"(20\d\d)",i).group(1)) for i in E.index]; E=E.sort_index(); E.to_csv("S5_event_study_bb200_binary.csv"); print(E.round(3).T.to_string())
pre=[y for y in E.index if y<2014]; import numpy as np
print("joint pre-trend test p:", round(es.f_test(" , ".join(f"I((yr == {y}) * high) = 0" for y in pre)).pvalue if False else float(es.wald_test(np.vstack([ (es.params.index==n).astype(float) for n in es.params.index if re.search(r'yr ?== ?(2010|2011|2012|2013)\)',n)]),scalar=True).pvalue),3))
m=gb.groupby(["high","post"]).agg(tracks=("tracks","mean"),over12=("over12","mean"),long18=("long18","mean"),n=("tracks","size")); print(m.round(3))
# dilution: track popularity (current, 0-100) of sampled tracks on studio albums
tr=t.merge(g[["album_id","post","high","ln_tracks","tracks"]],on="album_id")
tr["pos"]=tr.track_number/tr.tracks; tr=tr.dropna(subset=["track_popularity","artist_popularity","pos","genre","year"])
d=smf.ols("track_popularity ~ ln_tracks*post*high + pos + artist_popularity + C(genre) + C(year)",tr).fit(cov_type="cluster",cov_kwds={"groups":tr.artist_name})
D=pd.DataFrame({"coef":d.params,"se":d.bse,"p":d.pvalues}).loc[["ln_tracks","ln_tracks:post","ln_tracks:high","ln_tracks:post:high","pos"]]
D.to_csv("S6_dilution_popularity.csv"); print("tracks:",len(tr)); print(D.round(3))
