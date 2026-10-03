"""Genre-level restricted wild cluster bootstrap (Webb weights) for any OLS term.

Same algorithm as wild_bootstrap_pvalue() in 17_part1_headline.py, generalised to
any formula and term: impose the null by dropping the term, resample residuals
with one Webb weight per genre cluster, and compare artist-clustered t-statistics.
"""

import math

import numpy as np
import statsmodels.formula.api as smf

WEBB = np.array([-math.sqrt(1.5), -1, -math.sqrt(0.5), math.sqrt(0.5), 1, math.sqrt(1.5)])


def fit_clustered(formula, data, cluster="artist_cluster"):
    return smf.ols(formula, data=data).fit(cov_type="cluster", cov_kwds={"groups": data[cluster]})


def wild_bootstrap_pvalue(data, outcome, rhs_terms, term, draws=9999, seed=20260928,
                          boot_cluster="genre", robust_cluster="artist_cluster"):
    """Return (p-value, observed t) for `term` in `outcome ~ rhs_terms`."""
    data = data.reset_index(drop=True)
    formula = f"{outcome} ~ " + " + ".join(rhs_terms)
    restricted_formula = f"{outcome} ~ " + " + ".join(t for t in rhs_terms if t != term)
    model = fit_clustered(formula, data, robust_cluster)
    restricted = smf.ols(restricted_formula, data=data).fit()
    fitted = restricted.fittedvalues.to_numpy()
    residuals = restricted.resid.to_numpy()
    design = model.model.exog
    inverse = np.linalg.inv(design.T @ design)
    index = list(model.params.index).index(term)
    clusters = data[boot_cluster].to_numpy()
    robust = data[robust_cluster].to_numpy()
    unique_clusters = np.unique(clusters)
    robust_groups = [robust == c for c in np.unique(robust)]
    n_robust = len(robust_groups)
    correction = (n_robust / (n_robust - 1)) * ((len(data) - design.shape[1]) / (len(data) - 1))
    rng = np.random.default_rng(seed)
    observed = model.params[term] / model.bse[term]
    simulated = np.empty(draws)
    for draw in range(draws):
        weight_map = dict(zip(unique_clusters, rng.choice(WEBB, len(unique_clusters))))
        response = fitted + residuals * np.array([weight_map[x] for x in clusters])
        beta = inverse @ design.T @ response
        resid = response - design @ beta
        meat = np.zeros_like(inverse)
        for selected in robust_groups:
            score = design[selected].T @ resid[selected]
            meat += np.outer(score, score)
        covariance = inverse @ meat @ inverse * correction
        simulated[draw] = beta[index] / math.sqrt(max(covariance[index, index], 0))
    return float(np.mean(np.abs(simulated) >= abs(observed))), float(observed)
