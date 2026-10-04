"""Part 1 follow-up: did the rule lengthen the longest albums?

Specifications are fixed in docs/long_albums_followup_plan.md, written before estimation.
A: prespecified family (>=15, >=20, >=25 tracks; 75th and 90th quantiles), Holm-adjusted.
B: supporting checks (threshold profile, >=18 event study, charted split, running time >=60 min).
"""

import importlib
import math

import numpy as np
import pandas as pd
import patsy
import statsmodels.api as sm
from scipy import stats

from inference import fit_clustered, wild_bootstrap_pvalue
from paths import ANALYSIS_SAMPLE, RESULTS_P1_SECONDARY

FE = ["C(genre)", "C(year)"]
BASE = ["post:heavy", *FE]
SEED = 20260928
QUANTILE_DRAWS = 999


def prepare():
    data = pd.read_csv(ANALYSIS_SAMPLE)
    data = data[data["genre"].notna()].reset_index(drop=True)
    data["year"] = data["year"].astype(int)
    data["ln_standard_tracks"] = data["standard_tracks"].map(math.log)
    for k in range(8, 31):
        data[f"ge{k}"] = (data["standard_tracks"] >= k).astype(int)
    return data


def lpm(label, family, sample, outcome, bootstrap=True, note=""):
    model = fit_clustered(f"{outcome} ~ " + " + ".join(BASE), sample)
    boot_p = wild_bootstrap_pvalue(sample, outcome, BASE, "post:heavy", seed=SEED)[0] if bootstrap else np.nan
    row = {"test": label, "family": family, "outcome": outcome, "method": "LPM",
           "n_albums": len(sample), "n_artists": sample["artist_cluster"].nunique(),
           "coef": model.params["post:heavy"], "se": model.bse["post:heavy"],
           "p_artist": model.pvalues["post:heavy"], "p_family": boot_p,
           "p_family_kind": "genre Webb wild bootstrap" if bootstrap else "", "note": note}
    print(f"  {label:38s} coef={row['coef']:+.4f} se={row['se']:.4f} p={row['p_artist']:.3f} boot_p={boot_p:.3f}", flush=True)
    return row


def quantile(label, data, q):
    """QuantReg with genre and year FE; p-value from a pairs cluster bootstrap over artists."""
    y, X = patsy.dmatrices("ln_standard_tracks ~ " + " + ".join(BASE), data, return_type="dataframe")
    j = list(X.columns).index("post:heavy")
    yv, Xv = y.to_numpy().ravel(), X.to_numpy()
    coef = sm.QuantReg(yv, Xv).fit(q=q, max_iter=5000).params[j]
    groups = [np.flatnonzero(data["artist_cluster"].to_numpy() == a) for a in data["artist_cluster"].unique()]
    rng = np.random.default_rng(SEED)
    draws, failed = [], 0
    for _ in range(QUANTILE_DRAWS):
        idx = np.concatenate([groups[i] for i in rng.integers(0, len(groups), len(groups))])
        try:
            draws.append(sm.QuantReg(yv[idx], Xv[idx]).fit(q=q, max_iter=5000).params[j])
        except Exception:
            failed += 1
    draws = np.array(draws)
    se = draws.std(ddof=1)
    p = 2 * (1 - stats.norm.cdf(abs(coef / se))) if se > 0 else np.nan
    lo, hi = np.percentile(draws, [2.5, 97.5])
    note = (f"bootstrap SE (normal p); percentile 95% CI [{lo:+.4f}, {hi:+.4f}]; "
            f"share of draws with coef exactly 0: {np.mean(draws == 0):.2f}; failed draws: {failed}")
    print(f"  {label:38s} coef={coef:+.4f} se={se:.4f} p={p:.3f} ({note})", flush=True)
    return {"test": label, "family": "A", "outcome": f"ln_standard_tracks q{int(q * 100)}", "method": "quantile regression",
            "n_albums": len(data), "n_artists": data["artist_cluster"].nunique(), "coef": coef, "se": se,
            "p_artist": np.nan, "p_family": p, "p_family_kind": f"artist pairs cluster bootstrap ({QUANTILE_DRAWS})", "note": note}


def holm(pvalues):
    order = np.argsort(pvalues)
    adjusted, running = np.empty(len(pvalues)), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(pvalues) - rank) * pvalues[i]))
        adjusted[i] = running
    return adjusted


def event_study(data, outcome):
    years = sorted(int(y) for y in data["year"].unique() if int(y) != 2014)
    for y in years:
        data[f"hy_{y}"] = data["heavy"] * (data["year"] == y)
    terms = [f"hy_{y}" for y in years]
    model = fit_clustered(f"{outcome} ~ " + " + ".join(terms + FE), data)
    table = pd.DataFrame({"year": years, "coef": model.params[terms].to_numpy(),
                          "se_artist": model.bse[terms].to_numpy(), "p_artist": model.pvalues[terms].to_numpy()})
    pre = [f"hy_{y}" for y in years if y < 2014]
    return table, float(model.wald_test(", ".join(f"{t} = 0" for t in pre), scalar=True).pvalue)


def main():
    data = prepare()
    print(f"Sample: {len(data)} albums, {data['artist_cluster'].nunique()} artists", flush=True)
    RESULTS_P1_SECONDARY.mkdir(parents=True, exist_ok=True)

    # descriptive shares by group and period
    shares = data.groupby(["heavy", "post"])[[f"ge{k}" for k in (15, 18, 20, 25)]].mean().reset_index()
    shares["n"] = data.groupby(["heavy", "post"]).size().to_numpy()
    shares.to_csv(RESULTS_P1_SECONDARY / "long_albums_shares.csv", index=False)
    print(shares.round(3).to_string(index=False), flush=True)

    # A. prespecified family
    print("A. Prespecified family", flush=True)
    family = [lpm("A1 >=15 tracks", "A", data, "ge15"),
              lpm("A2 >=20 tracks", "A", data, "ge20"),
              lpm("A3 >=25 tracks", "A", data, "ge25"),
              quantile("A4 75th percentile, log tracks", data, 0.75),
              quantile("A5 90th percentile, log tracks", data, 0.90)]
    adjusted = holm(np.array([r["p_family"] for r in family]))
    for row, p in zip(family, adjusted):
        row["p_holm"] = p
    survivors = int(sum(p < 0.05 for p in adjusted))
    print(f"  Holm survivors at 5%: {survivors} of 5", flush=True)
    rows = family + [lpm("ref >=18 tracks (already seen; not in family)", "reference", data, "ge18")]

    # B. supporting checks
    print("B. Supporting checks", flush=True)
    profile = []
    for k in range(8, 31):
        m = fit_clustered(f"ge{k} ~ " + " + ".join(BASE), data)
        b, se = m.params["post:heavy"], m.bse["post:heavy"]
        profile.append({"threshold": k, "share_overall": data[f"ge{k}"].mean(), "coef": b, "se_artist": se,
                        "ci_low": b - 1.96 * se, "ci_high": b + 1.96 * se, "p_artist": m.pvalues["post:heavy"]})
    profile = pd.DataFrame(profile)
    profile.to_csv(RESULTS_P1_SECONDARY / "long_albums_thresholds.csv", index=False)
    print(profile.round(4).to_string(index=False), flush=True)

    table, joint_p = event_study(data.copy(), "ge18")
    table.to_csv(RESULTS_P1_SECONDARY / "long_albums_event_study.csv", index=False)
    print(table.round(4).to_string(index=False), flush=True)
    print(f"  B2 joint pre-2014 test, >=18 share: p = {joint_p:.3f}", flush=True)
    rows.append({"test": "B2 event study >=18: joint pre-2014 test", "family": "B", "outcome": "ge18",
                 "method": "Wald", "n_albums": len(data), "n_artists": data["artist_cluster"].nunique(),
                 "p_artist": joint_p, "note": "year x heavy, ref 2014; coefficients in long_albums_event_study.csv"})

    secondary = importlib.import_module("18_part1_secondary_checks")
    charted = secondary.add_chart_flags(data.copy())
    rows.append(lpm("B3 >=18 tracks, charted", "B", charted[charted["charted"] == 1], "ge18"))
    rows.append(lpm("B3 >=18 tracks, non-charted", "B", charted[charted["charted"] == 0], "ge18"))

    full = data[(data["tracks_with_duration"] == data["standard_tracks"]) & (data["running_time_minutes"] > 0)].copy()
    full["ge60min"] = (full["running_time_minutes"] >= 60).astype(int)
    rows.append(lpm("B4 running time >=60 minutes", "B", full, "ge60min", note="albums with all track durations"))

    out = pd.DataFrame(rows)
    out.to_csv(RESULTS_P1_SECONDARY / "long_albums_followup.csv", index=False)
    print(f"Wrote long_albums_followup.csv; Holm survivors {survivors}/5; pre-trend p = {joint_p:.3f}", flush=True)


if __name__ == "__main__":
    main()
