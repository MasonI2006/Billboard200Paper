from pathlib import Path
exec(open(Path(__file__).resolve().parent / 'spotify_part3.py').read().split('# event study')[0])
rows=[]
for name,f,d in [("BB200, continuous intensity","ln_tracks ~ post:intensity + C(genre) + C(year)",gb),
                 ("BB200, continuous, excl electronic","ln_tracks ~ post:intensity + C(genre) + C(year)",gb[gb.genre!="electronic"]),
                 ("BB200, binary, over12","over12 ~ post:high + C(genre) + C(year)",gb),
                 ("BB200, binary, long18","long18 ~ post:high + C(genre) + C(year)",gb),
                 ("BB200, binary, 2010-2019","ln_tracks ~ post:high + C(genre) + C(year)",gb[gb.year.between(2010,2019)]),
                 ("BB200, binary, artist FE","ln_tracks ~ post:high + C(artist) + C(year)",gb)]:
    m=smf.ols(f,d).fit(cov_type="cluster",cov_kwds={"groups":d.artist}); k=[x for x in m.params.index if x.startswith("post:")][0]
    rows.append([name,round(m.params[k],3),round(m.bse[k],3),round(m.pvalues[k],3),len(d)])
pwb=wild_boot("ln_tracks ~ post:high + C(genre) + C(year)",gb,"post:high","genre",B=499)
R=pd.DataFrame(rows,columns=["spec","coef","se","p","n"]); print(R.to_string(index=False)); print("wild bootstrap p (genre clusters), BB200 binary ln_tracks:",pwb)
R.to_csv("S7_bb200_variants.csv",index=False)
print("non-BB200 albums, binary:"); nb=g[~g.album_id.isin(gb.album_id)]
m=smf.ols("ln_tracks ~ post:high + C(genre) + C(year)",nb).fit(cov_type="cluster",cov_kwds={"groups":nb.artist}); print(round(m.params["post:high"],3),round(m.bse["post:high"],3),len(nb))
