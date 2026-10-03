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
                          boot_cluster="genre", robust_cluster="artist_cluster", intercept=True):
    """Return (p-value, observed t) for `term` in `outcome ~ rhs_terms`.

    intercept=False fits without a constant (for within-demeaned data).
    """
    data = data.reset_index(drop=True)
    tail = "" if intercept else " - 1"
    formula = f"{outcome} ~ " + " + ".join(rhs_terms) + tail
    restricted_formula = f"{outcome} ~ " + " + ".join(t for t in rhs_terms if t != term) + tail
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


def within_demean(data, columns, group):
    """Subtract group means (absorbs group fixed effects; Frisch-Waugh-Lovell)."""
    out = data.copy()
    means = data.groupby(group)[columns].transform("mean")
    for column in columns:
        out[column] = data[column] - means[column]
    return out


def within_fe_design(data, outcome, term_values, year_col="year", group="artist_cluster"):
    """Within-group design for `outcome ~ term + C(year) + C(group)`.

    Returns (demeaned frame, rhs term names) with columns y_w, x_w and year
    dummies yd_<year> (first year dropped), all demeaned by `group`.
    Groups with a single row carry no information and are dropped.
    """
    frame = data.copy()
    frame = frame[frame.groupby(group)[outcome].transform("size") > 1].copy()
    frame["y_w"] = frame[outcome].astype(float)
    frame["x_w"] = term_values.loc[frame.index].astype(float)
    years = sorted(frame[year_col].astype(int).unique())[1:]
    dummies = []
    for year in years:
        name = f"yd_{year}"
        frame[name] = (frame[year_col].astype(int) == year).astype(float)
        dummies.append(name)
    frame = within_demean(frame, ["y_w", "x_w", *dummies], group)
    return frame, ["x_w", *dummies]
