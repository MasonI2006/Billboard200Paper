"""Part 2b extensions: per-artist genre file and album-order control (docs/items4_5_plan.md).

Rows: baseline (current Part 2b sample), labels from data/final/artist_genres.csv, and the
album-order (chart-career debut ordinal) control. All with artist-clustered SEs and the
genre Webb bootstrap from inference.py; the artist-file run also reports the Part 2b
script's own estimates. Run after steps 12a and 21-23.
"""

import runpy
import tempfile
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

import paths
from inference import fit_clustered, wild_bootstrap_pvalue

FE = ["C(genre)", "C(year)"]
ORDER_BINS = [0, 1, 2, 3, 5, 9, np.inf]
ORDER_LABELS = ["1", "2", "3", "4-5", "6-9", "10+"]


def nz(series):  # same normaliser as 21_part2b_build.py
    s = series.fillna("").astype(str).map(lambda x: unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode())
    return s.str.lower().str.replace(r"[^a-z0-9 ]", "", regex=True).str.replace(r"\s+", " ", regex=True).str.strip()


def load_runs(path):
    runs = pd.read_csv(path)
    runs["artist_cluster"] = runs["mbid"]
    return runs


def estimate(label, runs, rhs, note=""):
    model = fit_clustered("weeks52 ~ " + " + ".join(rhs), runs)
    boot_p = wild_bootstrap_pvalue(runs, "weeks52", rhs, "post:heavy")[0]
    row = {"spec": label, "n_albums": len(runs), "n_artists": runs["mbid"].nunique(),
           "n_heavy_albums": int(runs["heavy"].sum()), "coef": model.params["post:heavy"],
           "se_artist": model.bse["post:heavy"], "p_artist": model.pvalues["post:heavy"],
           "p_wildboot_genre": boot_p, "note": note}
    print(f"  {label:40s} coef={row['coef']:+.3f} se={row['se_artist']:.3f} p={row['p_artist']:.4f} "
          f"boot_p={boot_p:.4f} n={row['n_albums']}", flush=True)
    return row


def chart_career_order(runs):
    """Ordinal of each album's Billboard 200 debut among the artist's debuts since 1963."""
    matches = pd.read_csv(paths.ARTIST_MATCHES, low_memory=False)
    matches = matches[matches["musicbrainz_artist_id"].notna()]
    name_to_id = dict(zip(nz(matches["artist_name"]), matches["musicbrainz_artist_id"]))
    chart = pd.read_csv(paths.RAW_BILLBOARD200, dtype=str, low_memory=False)
    chart["Date"] = pd.to_datetime(chart["Date"], errors="coerce")
    chart = chart[pd.to_numeric(chart["Weeks in Charts"], errors="coerce") == 1].copy()
    chart["an"] = nz(chart["Artist"])
    chart["mbid"] = chart["an"].map(name_to_id)
    chart["key"] = chart["an"] + "|" + chart["Song"].str.lower().str.strip()   # same key as 22_part2b_analyze.py
    debuts = chart.dropna(subset=["mbid", "Date"]).sort_values("Date").drop_duplicates("key")
    debuts["ordinal"] = debuts.groupby("mbid")["Date"].rank(method="first")
    ordinal = runs["key"].map(dict(zip(debuts["key"], debuts["ordinal"])))
    return pd.cut(ordinal, ORDER_BINS, labels=ORDER_LABELS).astype(str), int(ordinal.isna().sum())


def run_part2b_with_labels(label_frame, workdir):
    """Run the unchanged scripts 21 and 22 with another artist->genre source."""
    sample_path = workdir / "labels.csv"
    label_frame.to_csv(sample_path, index=False)
    saved = {k: getattr(paths, k) for k in ("ANALYSIS_SAMPLE", "PART2B_CHART_LABELLED", "PART2B_ALBUM_RUNS", "RESULTS_P2B")}
    try:
        paths.ANALYSIS_SAMPLE = sample_path
        paths.PART2B_CHART_LABELLED = workdir / "chart_labelled.pkl"
        paths.PART2B_ALBUM_RUNS = workdir / "album_runs.csv"
        paths.RESULTS_P2B = workdir
        runpy.run_path(str(paths.CODE_DIR / "21_part2b_build.py"), run_name="__main__")
        runpy.run_path(str(paths.CODE_DIR / "22_part2b_analyze.py"), run_name="__main__")
    finally:
        for k, v in saved.items():
            setattr(paths, k, v)
    own = pd.read_csv(workdir / "results_main.csv")
    return load_runs(workdir / "album_runs.csv"), own[(own["outcome"] == "weeks52") & (own["spec"] == "main")].iloc[0]


def main():
    base_rhs = ["post:heavy", *FE]
    runs = load_runs(paths.PART2B_ALBUM_RUNS)
    rows = [estimate("baseline (Part 1 sample labels)", runs, base_rhs,
                     "same sample as results_main.csv; inference.py bootstrap (artist-clustered t)")]

    runs["order_bin"], missing = chart_career_order(runs)
    print("Chart-career order bins:", runs["order_bin"].value_counts().to_dict(), "| unmatched:", missing, flush=True)
    rows.append(estimate("album order control (chart-career debut ordinal)", runs, base_rhs + ["C(order_bin)"],
                         "bins 1,2,3,4-5,6-9,10+ of Billboard 200 debuts since 1963"))

    artists = pd.read_csv(paths.ARTIST_GENRES)
    labels = pd.DataFrame({"artist_ids": artists["musicbrainz_artist_id"], "genre": artists["genre"], "heavy": artists["heavy"]})
    with tempfile.TemporaryDirectory() as tmp:
        file_runs, own = run_part2b_with_labels(labels, Path(tmp))
    rows.append(estimate("labels from artist_genres.csv", file_runs, base_rhs,
                         f"{len(artists)} labelled artists; Part 2b script's own estimate {own['coef']:+.3f}, "
                         f"p={own['p_artist']:.4f}, its bootstrap p={own['p_wildboot_genre']:.4f}"))

    paths.RESULTS_P2B.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(paths.RESULTS_P2B / "extensions.csv", index=False)


if __name__ == "__main__":
    main()
