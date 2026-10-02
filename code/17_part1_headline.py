"""Run the resolved-only MusicBrainz first-pass headline analysis."""

import math

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from musicbrainz_helpers import build_data
from paths import ANALYSIS_SAMPLE, FINAL_DIR, RESULTS_P1

RESULTS_DIR = RESULTS_P1
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
FINAL_DIR.mkdir(parents=True, exist_ok=True)


def wild_bootstrap_pvalue(data, draws=9999, seed=20260928):
    outcome = "ln_standard_tracks"
    formula = f"{outcome} ~ post:heavy + C(genre) + C(year)"
    restricted_formula = f"{outcome} ~ C(genre) + C(year)"
    model = smf.ols(formula, data=data).fit(
        cov_type="cluster", cov_kwds={"groups": data["artist_cluster"]}
    )
    restricted = smf.ols(restricted_formula, data=data).fit()
    fitted = restricted.fittedvalues.to_numpy()
    residuals = restricted.resid.to_numpy()
    design = model.model.exog
    inverse = np.linalg.inv(design.T @ design)
    coefficient_index = list(model.params.index).index("post:heavy")
    clusters = data["genre"].to_numpy()
    robust_clusters = data["artist_cluster"].to_numpy()
    unique_clusters = np.unique(clusters)
    unique_robust_clusters = np.unique(robust_clusters)
    weights = np.array([-math.sqrt(1.5), -1, -math.sqrt(0.5), math.sqrt(0.5), 1, math.sqrt(1.5)])
    rng = np.random.default_rng(seed)
    observed = model.params["post:heavy"] / model.bse["post:heavy"]
    simulated = []
    for _ in range(draws):
        weight_map = dict(zip(unique_clusters, rng.choice(weights, len(unique_clusters))))
        response = fitted + residuals * np.array([weight_map[x] for x in clusters])
        beta = inverse @ design.T @ response
        score_meat = np.zeros_like(inverse)
        fitted_response = design @ beta
        for cluster in unique_robust_clusters:
            selected = robust_clusters == cluster
            score = design[selected].T @ (response[selected] - fitted_response[selected])
            score_meat += np.outer(score, score)
        correction = (len(unique_robust_clusters) / (len(unique_robust_clusters) - 1)) * (
            (len(response) - design.shape[1]) / (len(response) - 1)
        )
        covariance = inverse @ score_meat @ inverse * correction
        standard_error = math.sqrt(max(covariance[coefficient_index, coefficient_index], 0))
        simulated.append(beta[coefficient_index] / standard_error)
    return float(np.mean(np.abs(simulated) >= abs(observed))), observed


def main():
    data = build_data()
    data["ln_standard_tracks"] = data["standard_tracks"].map(math.log)
    data = data[data["genre"].ne("")].copy()
    data["over12"] = (data["standard_tracks"] > 12).astype(int)
    data["long18"] = (data["standard_tracks"] >= 18).astype(int)

    formula = "ln_standard_tracks ~ post:heavy + C(genre) + C(year)"
    model = smf.ols(formula, data=data).fit(
        cov_type="cluster", cov_kwds={"groups": data["artist_cluster"]}
    )
    wild_p, observed_t = wild_bootstrap_pvalue(data)
    headline = pd.DataFrame(
        [{
            "spec": "resolved-only headline",
            "window": "2009-2019",
            "outcome": "log standard-edition track count",
            "n_albums": len(data),
            "n_artists": data["artist_cluster"].nunique(),
            "n_genre_clusters": data["genre"].nunique(),
            "coef_post_by_streaming_heavy": model.params["post:heavy"],
            "se_artist_cluster": model.bse["post:heavy"],
            "p_artist_cluster": model.pvalues["post:heavy"],
            "t_artist_cluster": model.tvalues["post:heavy"],
            "p_wildboot_genre_webb_9999": wild_p,
            "t_wildboot_observed": observed_t,
            "seed": 20260928,
        }]
    )
    headline.to_csv(RESULTS_DIR / "headline.csv", index=False)
    means = data.groupby(["heavy", "post"]).agg(
        mean_tracks=("standard_tracks", "mean"),
        mean_log_tracks=("ln_standard_tracks", "mean"),
        share_over12=("over12", "mean"),
        share_long18=("long18", "mean"),
        n=("standard_tracks", "size"),
    ).reset_index()
    means.to_csv(RESULTS_DIR / "headline_means.csv", index=False)
    data.to_csv(ANALYSIS_SAMPLE, index=False)
    print(headline.to_string(index=False))
    print(means.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
