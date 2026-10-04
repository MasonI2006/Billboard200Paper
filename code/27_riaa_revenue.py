"""Tidy the RIAA U.S. recorded-music revenue export (context for the streaming confound).

The raw file is a Tableau crosstab export: UTF-16, tab-separated, dollar strings with
thousands separators, negatives in accounting parentheses, and a "Total" row per category,
per year and overall. The units column is empty in the export. Revenue is nominal; the
"CPI Adjustment" column is in 2025 dollars (its factor is 1.000 for 2025).
"""

import pandas as pd

from paths import FINAL_DIR, RAW_RIAA_REVENUE, RIAA_REVENUE_LONG, RIAA_REVENUE_BY_CATEGORY


def money(series):
    s = series.str.replace(r"[$,]", "", regex=True).str.strip()
    negative = s.str.match(r"^\(.*\)$")
    return pd.to_numeric(s.str.strip("()")) * negative.map({True: -1, False: 1})


def main():
    raw = pd.read_csv(RAW_RIAA_REVENUE, encoding="utf-16", sep="\t", dtype=str)
    data = raw[(raw["Disclaimer"] != "Grand Total") & (raw["Year"] != "Total")].copy()
    data = data.rename(columns={"Year": "year", "Format2": "category", "Format": "format"})
    data["year"] = data["year"].astype(int)
    data["revenue_nominal"] = money(data["Revenue"])
    data["revenue_2025usd"] = money(data["CPI Adjustment"])

    # consistency: formats sum to category totals, categories sum to the grand total (to rounding)
    formats = data[data["format"] != "Total"].groupby(["year", "category"])["revenue_nominal"].sum()
    category_totals = data[(data["format"] == "Total") & (data["category"] != "Total")].set_index(["year", "category"])["revenue_nominal"]
    assert (formats - category_totals).abs().max() <= 5
    grand = data[data["category"] == "Total"].set_index("year")["revenue_nominal"]
    assert (category_totals.groupby("year").sum() - grand).abs().max() <= 5

    long = data[data["format"] != "Total"][["year", "category", "format", "revenue_nominal", "revenue_2025usd"]]
    long = long.sort_values(["year", "category", "format"])
    wide = data[data["format"] == "Total"].pivot(index="year", columns="category", values="revenue_nominal")
    wide.columns = [f"{c.lower().replace(' ', '_')}_nominal" for c in wide.columns]
    wide["streaming_share"] = wide["streaming_nominal"] / wide["total_nominal"]

    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(RIAA_REVENUE_LONG, index=False)
    wide.reset_index().to_csv(RIAA_REVENUE_BY_CATEGORY, index=False)
    print(f"{len(long)} format-year rows, {long['year'].min()}-{long['year'].max()}")
    print(wide.loc[2010:2019, ["streaming_nominal", "total_nominal", "streaming_share"]].round(3).to_string())


if __name__ == "__main__":
    main()
