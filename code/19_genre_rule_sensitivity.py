"""Exploratory: rock + pop -> pop sensitivity of the ordered genre rule.

Swaps rock and pop in GENRE_PRIORITY (docs/part1_secondary_rerun_plan.md, section D),
then re-estimates the Part 1 headline and the Part 2b main estimate on the variant
labels. Exploratory only; the ordered-rule results remain the reported ones.
Run after steps 17 and 21-23 (needs data/final/analysis_sample.csv).
"""

import math
import runpy
import tempfile
from pathlib import Path

import pandas as pd

import paths
from inference import fit_clustered, wild_bootstrap_pvalue
from musicbrainz_helpers import GENRE_PRIORITY, build_data

VARIANT = tuple(g for g in GENRE_PRIORITY if g not in ("rock", "pop")) + ("pop", "rock")
FE = ["C(genre)", "C(year)"]


def part1_sample(priority):
    data = build_data(priority)
    data["ln_standard_tracks"] = data["standard_tracks"].map(math.log)
    data = data[data["genre"].ne("")].copy()
    data["over12"] = (data["standard_tracks"] > 12).astype(int)
    data["long18"] = (data["standard_tracks"] >= 18).astype(int)
    return data


def part2b_main(sample_path, workdir):
    """Run the unchanged Part 2b scripts (21, 22) on another analysis sample."""
    saved = {k: getattr(paths, k) for k in ("ANALYSIS_SAMPLE", "PART2B_CHART_LABELLED", "PART2B_ALBUM_RUNS", "RESULTS_P2B")}
    try:
        paths.ANALYSIS_SAMPLE = Path(sample_path)
        paths.PART2B_CHART_LABELLED = workdir / "chart_labelled.pkl"
        paths.PART2B_ALBUM_RUNS = workdir / "album_runs.csv"
        paths.RESULTS_P2B = workdir
        runpy.run_path(str(paths.CODE_DIR / "21_part2b_build.py"), run_name="__main__")
        runpy.run_path(str(paths.CODE_DIR / "22_part2b_analyze.py"), run_name="__main__")
    finally:
        for k, v in saved.items():
            setattr(paths, k, v)
    main = pd.read_csv(workdir / "results_main.csv")
    return main[(main["outcome"] == "weeks52") & (main["spec"] == "main")].iloc[0]


def main():
    print("Variant priority:", " > ".join(VARIANT), flush=True)
    current = pd.read_csv(paths.ANALYSIS_SAMPLE)
    current = current[current["genre"].notna()]
    variant = part1_sample(VARIANT)
    merged = current[["release_group_id", "genre", "heavy"]].merge(
        variant[["release_group_id", "genre", "heavy"]], on="release_group_id", suffixes=("_ordered", "_variant"))
    changed = merged[merged["genre_ordered"] != merged["genre_variant"]]
    print(f"Albums changing genre: {len(changed)} of {len(merged)} "
          f"({changed.groupby(['genre_ordered', 'genre_variant']).size().to_dict()})", flush=True)

    rhs = ["post:heavy", *FE]
    model = fit_clustered("ln_standard_tracks ~ " + " + ".join(rhs), variant)
    boot_p, _ = wild_bootstrap_pvalue(variant, "ln_standard_tracks", rhs, "post:heavy")
    rows = [{
        "estimate": "Part 1 headline (log tracks)", "labels": "variant: pop before rock",
        "n": len(variant), "n_heavy": int(variant["heavy"].sum()), "albums_changing_genre": len(changed),
        "coef": model.params["post:heavy"], "se_artist": model.bse["post:heavy"],
        "p_artist": model.pvalues["post:heavy"], "p_wildboot_genre": boot_p,
    }]
    print(f"  Part 1 variant: coef={rows[0]['coef']:+.4f} p={rows[0]['p_artist']:.3f} boot_p={boot_p:.3f}", flush=True)

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        sample_path = workdir / "analysis_sample_variant.csv"
        variant.to_csv(sample_path, index=False)
        q1b = part2b_main(sample_path, workdir)
    rows.append({
        "estimate": "Part 2b weeks in first 52", "labels": "variant: pop before rock",
        "n": int(q1b["n"]), "n_heavy": None, "albums_changing_genre": None,
        "coef": q1b["coef"], "se_artist": q1b["se_artist"], "p_artist": q1b["p_artist"],
        "p_wildboot_genre": q1b["p_wildboot_genre"],
    })
    print(f"  Part 2b variant: coef={q1b['coef']:+.3f} p={q1b['p_artist']:.3f} boot_p={q1b['p_wildboot_genre']:.3f}", flush=True)

    paths.RESULTS_P1_SECONDARY.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(paths.RESULTS_P1_SECONDARY / "rockpop_sensitivity.csv", index=False)
    changed.to_csv(paths.RESULTS_P1_SECONDARY / "rockpop_changed_albums.csv", index=False)


if __name__ == "__main__":
    main()
