"""Build the frozen pre-rule Billboard 200 artist roster and credit audit."""

import re

import pandas as pd

from load_clean_data import load_chart
from paths import INTERIM_DIR, ROSTER, ROSTER_CREDIT_AUDIT


ROSTER_START = pd.Timestamp("2009-01-01")
ROSTER_END = pd.Timestamp("2014-11-23")
FEATURE_MARKER = re.compile(r"\s+(?:featuring|feat\.?|ft\.?)\s+", re.IGNORECASE)
COMPOSITE_MARKER = re.compile(r"&|\band\b|\bx\b|\bwith\b|,|/", re.IGNORECASE)


def normalize_credit(credit):
    return re.sub(r"\s+", " ", str(credit).strip()).casefold()


def classify_credit(credit):
    """Return roster candidate, disposition, and whether identity review is needed."""
    normalized = normalize_credit(credit)
    if re.fullmatch(r"various artists?", normalized):
        return "", "excluded_various_artists", False

    lead = FEATURE_MARKER.split(str(credit).strip(), maxsplit=1)[0].strip()
    if lead != str(credit).strip():
        if COMPOSITE_MARKER.search(lead):
            return lead, "featured_lead_composite_credit_review", True
        return lead, "lead_before_explicit_feature_credit", False

    if COMPOSITE_MARKER.search(str(credit)):
        return str(credit).strip(), "retained_composite_credit_review_identity", True

    return str(credit).strip(), "provisional_single_billed_credit", False


def build_roster():
    chart = load_chart("b200")
    debuts = chart.loc[
        (chart["Weeks in Charts"] == 1)
        & chart["Date"].between(ROSTER_START, ROSTER_END)
    ].copy()
    debuts["source_artist_credit"] = debuts["Artist"].fillna("").astype(str).str.strip()
    debuts["credit_key"] = debuts["source_artist_credit"].map(normalize_credit)

    credit_audit = (
        debuts.groupby("credit_key", as_index=False)
        .agg(
            source_artist_credit=("source_artist_credit", "first"),
            first_qualifying_debut=("Date", "min"),
            qualifying_debut_rows=("Song", "size"),
            example_albums=("Song", lambda values: " | ".join(pd.unique(values)[:5])),
        )
    )
    classified = credit_audit["source_artist_credit"].map(classify_credit)
    credit_audit[["roster_artist_candidate", "credit_handling", "identity_review_needed"]] = (
        pd.DataFrame(classified.tolist(), index=credit_audit.index)
    )
    credit_audit["roster_artist_key"] = credit_audit["roster_artist_candidate"].map(
        normalize_credit
    )

    roster_credits = credit_audit.loc[
        credit_audit["roster_artist_key"] != ""
    ].copy()
    roster = (
        roster_credits.groupby("roster_artist_key", as_index=False)
        .agg(
            artist_name=("roster_artist_candidate", "first"),
            first_qualifying_debut=("first_qualifying_debut", "min"),
            source_credit_count=("source_artist_credit", "nunique"),
            qualifying_debut_rows=("qualifying_debut_rows", "sum"),
            source_credits=(
                "source_artist_credit",
                lambda values: " | ".join(pd.unique(values)),
            ),
            identity_review_needed=("identity_review_needed", "max"),
        )
        .sort_values(["artist_name", "first_qualifying_debut"], kind="stable")
        .reset_index(drop=True)
    )

    return debuts, roster, credit_audit


def main():
    debuts, roster, credit_audit = build_roster()
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    roster.to_csv(ROSTER, index=False)
    credit_audit.to_csv(ROSTER_CREDIT_AUDIT, index=False)

    various = credit_audit["credit_handling"].eq("excluded_various_artists")
    feature = credit_audit["source_artist_credit"].str.contains(
        FEATURE_MARKER, regex=True, na=False
    )
    unresolved = credit_audit["identity_review_needed"]
    print(f"Qualifying Billboard 200 debut rows: {len(debuts):,}")
    print(f"Provisional roster entities after feature handling: {len(roster):,}")
    print(
        "Distinct raw chart-billed credits: "
        f"{len(credit_audit):,}; excluded Various Artists credits: {int(various.sum())}; "
        f"explicit featured-credit strings: {int(feature.sum())}; "
        f"composite credits flagged for identity review: {int(unresolved.sum())}."
    )
    print(
        "Qualifying debut rows billed to Various Artists: "
        f"{int(credit_audit.loc[various, 'qualifying_debut_rows'].sum()):,}."
    )
    if unresolved.any():
        print("Flagged composite-credit examples:")
        print(
            credit_audit.loc[unresolved, "source_artist_credit"]
            .sort_values()
            .head(30)
            .to_string(index=False)
        )
    print(f"Roster and credit audit saved under {INTERIM_DIR}.")


if __name__ == "__main__":
    main()