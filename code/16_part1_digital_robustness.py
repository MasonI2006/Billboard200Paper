"""Compare frozen MusicBrainz counts with cached digital-edition counts."""

import math

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

from musicbrainz_helpers import build_data
from paths import DIGITAL_ROBUSTNESS, RESULTS_P1

OUTPUT_PATH = DIGITAL_ROBUSTNESS


def estimate(data, outcome, label):
    sample = data.dropna(subset=[outcome]).copy()
    model = smf.ols(
        f"{outcome} ~ post:heavy + C(genre) + C(year)",
        data=sample,
    ).fit(cov_type="cluster", cov_kwds={"groups": sample["artist_cluster"]})
    term = "post:heavy"
    return {
        "spec": label,
        "outcome": outcome,
        "n_albums": len(sample),
        "coef": model.params.get(term, float("nan")),
        "se_artist_cluster": model.bse.get(term, float("nan")),
        "p_artist_cluster": model.pvalues.get(term, float("nan")),
        "direction": "positive" if model.params.get(term, 0) > 0 else "negative",
    }


def wild_bootstrap_pvalue(data, outcome, draws=9999, seed=20260928):
    sample = data.dropna(subset=[outcome]).copy()
    formula = f"{outcome} ~ post:heavy + C(genre) + C(year)"
    restricted_formula = f"{outcome} ~ C(genre) + C(year)"
    model = smf.ols(formula, data=sample).fit(
        cov_type="cluster", cov_kwds={"groups": sample["artist_cluster"]}
    )
    restricted = smf.ols(restricted_formula, data=sample).fit()
    fitted = restricted.fittedvalues.to_numpy()
    residuals = restricted.resid.to_numpy()
    clusters = sample["genre"].to_numpy()
    unique_clusters = np.unique(clusters)
    weights = np.array([-math.sqrt(1.5), -1, -math.sqrt(0.5), math.sqrt(0.5), 1, math.sqrt(1.5)])
    rng = np.random.default_rng(seed)
    observed = model.params["post:heavy"] / model.bse["post:heavy"]
    simulated = []
    response_column = outcome
    for _ in range(draws):
        weight_map = dict(zip(unique_clusters, rng.choice(weights, len(unique_clusters))))
        bootstrap = sample.copy()
        bootstrap[response_column] = fitted + residuals * np.array([weight_map[x] for x in clusters])
        fitted_bootstrap = smf.ols(formula, data=bootstrap).fit(
            cov_type="cluster", cov_kwds={"groups": bootstrap["artist_cluster"]}
        )
        simulated.append(
            fitted_bootstrap.params["post:heavy"] / fitted_bootstrap.bse["post:heavy"]
        )
    return float(np.mean(np.abs(simulated) >= abs(observed)))


def main():
    data = build_data()
    data["ln_standard_tracks"] = data["standard_tracks"].map(math.log)
    data["ln_digital_tracks"] = pd.to_numeric(data["digital_tracks"], errors="coerce").map(
        lambda value: math.log(value) if pd.notna(value) and value > 0 else float("nan")
    )
    known = data[data["genre"].ne("")].copy()
    digital_known = known.dropna(subset=["digital_tracks"]).copy()
    rows = []
    for sample, outcome, label in [
        (known, "ln_standard_tracks", "standard_frozen_all_known_genre"),
        (digital_known, "ln_standard_tracks", "standard_same_digital_sample"),
        (digital_known, "ln_digital_tracks", "digital_alternate_same_sample"),
    ]:
        row = estimate(sample, outcome, label)
        row["p_wildboot_genre"] = ""
        rows.append(row)
    report = pd.DataFrame(rows)
    report["digital_identifiable"] = len(digital_known)
    report["digital_missing"] = len(known) - len(digital_known)
    report["count_affected"] = int(
        (digital_known["standard_tracks"] != pd.to_numeric(digital_known["digital_tracks"])).sum()
    )
    RESULTS_P1.mkdir(parents=True, exist_ok=True)
    report.to_csv(OUTPUT_PATH, index=False)
    print(report.round(4).to_string(index=False))
    print(
        f"Known-genre albums: {len(known):,}; digital editions: {len(digital_known):,}; "
        f"missing digital format: {len(known) - len(digital_known):,}; "
        f"different counts: {int((digital_known['standard_tracks'] != pd.to_numeric(digital_known['digital_tracks'])).sum()):,}"
    )


if __name__ == "__main__":
    main()
