from pathlib import Path
exec(open(Path(__file__).resolve().parent / 'spotify_part3.py').read().split('# event study')[0])
gb["period"]=pd.cut(gb.year,[2008,2011,2014,2017,2020,2024],labels=["2009-11","2012-14","2015-17","2018-20","2021-24"])
x=gb.groupby(["period","high"],observed=True).agg(tracks=("tracks","mean"),over12=("over12","mean"),n=("tracks","size")).unstack(); print(x.round(2).to_string())
x.to_csv("S8_bb200_periods.csv")
