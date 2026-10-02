from pathlib import Path
exec(open(Path(__file__).resolve().parent / 'spotify_analysis.py').read().split("res=[]")[0].replace("print(fig","#").replace("print(g.groupby","#"))
out=[]
def run(name,f,d):
    m=smf.ols(f,d).fit(cov_type="cluster",cov_kwds={"groups":d.artist}); k=[x for x in m.params.index if x.startswith("post:")][0]
    out.append([name,k,round(m.params[k],3),round(m.bse[k],3),round(m.pvalues[k],3),len(d)])
for y in ["ln_tracks","long18","over12"]:
    run(f"binary high, {y}",f"{y} ~ post:high + C(genre) + C(year)",g)
run("binary, excl electronic",f"ln_tracks ~ post:high + C(genre) + C(year)",g[g.genre!="electronic"])
run("binary, window 2010-19",f"ln_tracks ~ post:high + C(genre) + C(year)",g[g.year.between(2010,2019)])
run("hiphop vs rock+country only",f"ln_tracks ~ post:high + C(genre) + C(year)",g[g.genre.isin(["hiphop_rnb","rock","country"])])
run("over12, hiphop vs rock+country",f"over12 ~ post:high + C(genre) + C(year)",g[g.genre.isin(["hiphop_rnb","rock","country"])])
# Billboard 200 match
import sys; sys.path.insert(0,".")
b=pd.read_csv(U+"billboard200.csv",dtype=str,low_memory=False); b["Date"]=pd.to_datetime(b.Date,errors="coerce")
b["wk"]=pd.to_numeric(b["Weeks in Charts"],errors="coerce"); b["Rank"]=pd.to_numeric(b.Rank,errors="coerce")
deb=b[(b.wk==1)&(b.Date>="2009-01-01")]
nz=lambda s:s.fillna("").str.lower().str.replace(r"\(.*?\)|\[.*?\]","",regex=True).str.replace(r"[^a-z0-9 ]","",regex=True).str.replace(r"\s+"," ",regex=True).str.strip()
la=lambda s:nz(s.str.lower().str.split(r" featuring | & | and | x | with |, ",regex=True).str[0])
deb=deb.assign(k=la(deb.Artist)+"|"+nz(deb.Song))
g["k"]=la(g.artist)+"|"+nz(g.album_name)
gb=g.merge(deb[["k","Date","Rank"]].drop_duplicates("k"),on="k",how="inner")
print("albums matched to a Billboard 200 debut:",len(gb),"of",len(g))
if len(gb)>60: run("Billboard-200 albums only",f"ln_tracks ~ post:high + C(genre) + C(year)",gb)
# Kaggle artist exposure
ex=pd.read_csv("D_artist_exposure.csv"); ex["a"]=ex.a.astype(str)
g["a"]=g.artist.str.lower().str.split(r" featuring | & | and | x | with |, ",regex=True).str[0].str.strip()
ge=g.merge(ex[["a","exposure"]],on="a"); ge["exp_std"]=(ge.exposure-ge.exposure.mean())/ge.exposure.std()
print("albums with artist exposure:",len(ge))
if len(ge)>60: run("artist exposure (Kaggle), ln_tracks","ln_tracks ~ post:exp_std + C(genre) + C(year)",ge)
O=pd.DataFrame(out,columns=["spec","term","coef","se","p","n"]); O.to_csv("S4_did_variants.csv",index=False); print(O.to_string(index=False))
