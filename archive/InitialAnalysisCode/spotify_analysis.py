import pandas as pd, numpy as np, re, ast
from pathlib import Path
import os
CODE = Path(__file__).resolve().parent          # .../Billboard200Paper/InitialAnalysisCode
ROOT = CODE.parent                               # .../Billboard200Paper
U = str(ROOT / "OriginalDataFiles") + os.sep     # input data
RESULTS = ROOT / "kaggle_results"                # all outputs are written here
RESULTS.mkdir(exist_ok=True)
os.chdir(RESULTS)
t=pd.read_csv(U+"track_data_final.csv"); c=pd.read_csv(U+"spotify_data_clean.csv")
t["rel"]=pd.to_datetime(t.album_release_date,errors="coerce",format="mixed"); t["year"]=t.rel.dt.year
# artist genres: combine both files (final uses list strings, clean uses comma strings)
def parse(g):
    if pd.isna(g): return []
    g=str(g)
    if g.startswith("["):
        try: return list(ast.literal_eval(g))
        except Exception: return []
    return [x.strip() for x in g.split(",") if x.strip()]
gen={}
for d in (t,c):
    for a,g in zip(d.artist_name,d.artist_genres):
        l=parse(g)
        if l: gen[a]=sorted(set(gen.get(a,[]))|set(l))
RULES=[("latin",r"latin|reggaeton|urbano|corrido|banda|mariachi|norte|cumbia|bachata|salsa|trap latino|mexican"),
       ("hiphop_rnb",r"hip hop|rap|trap|drill|r&b|soul|crunk|grime|phonk|plugg|rage"),
       ("country",r"country|bluegrass|americana|red dirt"),
       ("christian",r"christian|worship|gospel|ccm"),
       ("jazz",r"jazz|bossa|swing"),("soundtrack",r"soundtrack|anime|video game|musical|broadway"),("classical",r"classical|orchestral|opera|chamber|medieval|neoclassical"),
       ("electronic",r"edm|house|techno|electro|dubstep|trance|drum and bass|dnb|bass music|moombahton|big room|brostep|hardstyle|garage"),
       ("rock",r"rock|metal|punk|emo|grunge|indie|alternative|folk|shoegaze|hardcore"),
       ("pop",r"pop")]
def bucket(a):
    s=" | ".join(gen.get(a,[]))
    for b,rx in RULES:
        if re.search(rx,s): return b
    return np.nan
t["genre"]=t.artist_name.map(bucket)
INT={"electronic":3.40,"latin":2.08,"hiphop_rnb":2.05,"pop":1.95,"rock":0.74,"country":0.54,"christian":0.44,"jazz":0.15,"classical":0.14}
t["intensity"]=t.genre.map(INT)
# ---- album-level file ----
alb=t.sort_values("track_popularity",ascending=False).groupby("album_id").agg(
    album_name=("album_name","first"),artist=("artist_name","first"),album_type=("album_type","first"),
    rel=("rel","first"),year=("year","first"),tracks=("album_total_tracks","first"),
    genre=("genre","first"),intensity=("intensity","first"),artist_pop=("artist_popularity","first"),
    n_sampled=("track_id","size")).reset_index()
reissue=r"deluxe|expanded|edition|version|anniversary|remaster|live|greatest|best of|collection|hits|complete|reissue|bonus|extended|\(.*vol"
alb["reissue_flag"]=alb.album_name.str.lower().str.contains(reissue,regex=True)
core=alb[(alb.album_type=="album")&(alb.genre!="soundtrack")&(~alb.reissue_flag)&alb.year.between(2009,2024)&(alb.tracks>=6)].copy()
core["post"]=(core.rel>="2014-11-24").astype(int)   # first tracking week under the rule
core["ln_tracks"]=np.log(core.tracks)
core.to_csv("S_albums_core.csv",index=False)
print("albums total",len(alb),"| core studio albums 2009-24 (>=6 tracks)",len(core),"| with genre",core.genre.notna().sum())
print(core.genre.value_counts().to_dict())
print(core.genre.value_counts().to_dict())
import statsmodels.formula.api as smf
g=core.dropna(subset=["genre"]).copy()
g["high"]=(g.intensity>=1.9).astype(int); g["long18"]=(g.tracks>=18).astype(int); g["over12"]=(g.tracks>12).astype(int)
# 1. descriptive series
fig=g.groupby(["year","high"]).tracks.mean().unstack().rename(columns={0:"low",1:"high"})
fig["n_high"]=g[g.high==1].groupby("year").size(); fig["n_low"]=g[g.high==0].groupby("year").size()
fig.to_csv("S1_tracks_by_year.csv"); print(fig.round(1).to_string())
# 2-way pre/post means
print(g.groupby(["high","post"]).agg(mean_tracks=("tracks","mean"),share18=("long18","mean"),share_over12=("over12","mean"),n=("tracks","size")).round(3))
# 2. DiD
def wild_boot(formula,data,coef,cl,B=999,seed=1):
    rng=np.random.default_rng(seed)
    m=smf.ols(formula,data).fit(); t0=m.params[coef]/m.bse[coef]
    r=smf.ols(formula.replace(coef,"0").replace("+ 0",""),data).fit() if False else None
    # restricted model: drop the tested term
    rf=formula.replace(f"{coef} + ","")
    mr=smf.ols(rf,data).fit(); yhat=mr.fittedvalues; u=mr.resid
    cls=data[cl].values; uc=np.unique(cls); W=np.array([-np.sqrt(1.5),-1,-np.sqrt(.5),np.sqrt(.5),1,np.sqrt(1.5)])
    ts=[]
    for _ in range(B):
        w=dict(zip(uc,rng.choice(W,len(uc)))); d=data.copy()
        d[formula.split("~")[0].strip()]=yhat+u*np.array([w[x] for x in cls])
        mb=smf.ols(formula,d).fit(cov_type="cluster",cov_kwds={"groups":d[cl]})
        ts.append(mb.params[coef]/mb.bse[coef])
    mc=smf.ols(formula,data).fit(cov_type="cluster",cov_kwds={"groups":data[cl]})
    t0=mc.params[coef]/mc.bse[coef]
    return (np.abs(ts)>=abs(t0)).mean()
res=[]
for y in ["ln_tracks","long18","over12"]:
    f=f"{y} ~ post:intensity + C(genre) + C(year)"
    m=smf.ols(f,g).fit(cov_type="cluster",cov_kwds={"groups":g.artist})
    p_wb=wild_boot(f,g,"post:intensity","genre",B=499)
    res.append([y,"genre+year FE",m.params["post:intensity"],m.bse["post:intensity"],m.pvalues["post:intensity"],p_wb,len(g)])
# within-artist
ga=g[g.groupby("artist").post.transform("nunique")==2]
m=smf.ols("ln_tracks ~ post:intensity + C(artist) + C(year)",ga).fit(cov_type="cluster",cov_kwds={"groups":ga.artist})
res.append(["ln_tracks","artist+year FE",m.params["post:intensity"],m.bse["post:intensity"],m.pvalues["post:intensity"],np.nan,len(ga)])
# control for linear genre trends
g["trend"]=g.year-2014
m=smf.ols("ln_tracks ~ post:intensity + C(genre) + C(year) + C(genre):trend",g).fit(cov_type="cluster",cov_kwds={"groups":g.artist})
res.append(["ln_tracks","+ genre trends",m.params["post:intensity"],m.bse["post:intensity"],m.pvalues["post:intensity"],np.nan,len(g)])
R=pd.DataFrame(res,columns=["outcome","spec","coef","se_artist","p_artist","p_wildboot_genre","n"]); R.to_csv("S2_did.csv",index=False); print(R.round(3).to_string())
# 3. event study (ref 2014)
yrs=[y for y in range(2009,2025) if y!=2014]
es=smf.ols("ln_tracks ~ "+" + ".join(f"I((year=={y})*intensity)" for y in yrs)+" + C(genre) + C(year)",g).fit(cov_type="cluster",cov_kwds={"groups":g.artist})
ES=pd.DataFrame({"coef":es.params.filter(regex=r"^I\(\(year"),"se":es.bse.filter(regex=r"^I\(\(year")})
ES.index=[int(re.search(r"(20\d\d)",i).group(1)) for i in ES.index]; ES.sort_index().to_csv("S3_event_study.csv"); print(ES.sort_index().round(3).T.to_string())
