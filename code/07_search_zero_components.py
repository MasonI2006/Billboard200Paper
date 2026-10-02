"""Search components of unresolved billed credits, then four targeted names."""

import csv
import json
import re
import time
import unicodedata
from musicbrainz_helpers import (
    REQUEST_INTERVAL_SECONDS,
    configure_api_access,
    request_artist_search,
)
from paths import (
    INTERIM_DIR,
    TARGETED_ARTIST_SEARCHES,
    TRUE_NOMATCH_ZERO,
    ZERO_COMPONENT_CACHE,
    ZERO_COMPONENT_RESULTS,
    ZERO_COMPONENT_SUMMARY,
)


ZERO_LIST = TRUE_NOMATCH_ZERO
COMPONENT_CACHE = ZERO_COMPONENT_CACHE
COMPONENT_RESULTS = ZERO_COMPONENT_RESULTS
COMPONENT_SUMMARY = ZERO_COMPONENT_SUMMARY
TARGETED_RESULTS = TARGETED_ARTIST_SEARCHES
COMPONENT_SEPARATOR = re.compile(
    r"\s*(?:a\s*\.\s*k\s*\.\s*a\s*\.?|a\.k\.a\.|aka|presents|"
    r"\+|&|,|\band\b|\bwith\b|\bx\b|/|\bof\b)\s*",
    re.IGNORECASE,
)
TARGETED_NAMES = [
    ("The Kenny Wayne Shepherd Band", "Kenny Wayne Shepherd"),
    ("The Dead Rabbitts", "Dead Rabbitts"),
    ("The Nick Hexum Quintet", "Nick Hexum"),
    ("The CAJO Family", "CAJO"),
]
_last_request_at = None


def normalize(value):
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return re.sub(r"[\W_]+", " ", text, flags=re.UNICODE).strip()


def split_credit(credit):
    components = [part.strip(" \t\r\n:;'\"") for part in COMPONENT_SEPARATOR.split(credit)]
    components = [part for part in components if len(part) > 1]
    return list(dict.fromkeys(components)) or [credit.strip()]


def load_zero_names():
    with ZERO_LIST.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if rows and "retry_api_count" in rows[0]:
        return [row for row in rows if int(row.get("retry_api_count") or 0) == 0]
    return rows


def load_search_cache():
    cached = {}
    if not COMPONENT_CACHE.exists():
        return cached
    with COMPONENT_CACHE.open(encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            row = json.loads(line)
            cached[(row["source_artist_name"], row["component"], row["search_kind"])] = row
    return cached


def save_search(cache, source_name, component, search_kind, response, query):
    row = {
        "source_artist_name": source_name,
        "component": component,
        "search_kind": search_kind,
        "query": query,
        "response": response,
    }
    with COMPONENT_CACHE.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        stream.flush()
    cache[(source_name, component, search_kind)] = row
    return row


def search_with_cache(cache, source_name, component, search_kind):
    global _last_request_at
    key = (source_name, component, search_kind)
    if key in cache:
        return cache[key]
    if _last_request_at is not None:
        delay = REQUEST_INTERVAL_SECONDS - (time.monotonic() - _last_request_at)
        if delay > 0:
            time.sleep(delay)
    _last_request_at = time.monotonic()
    response, query = request_artist_search(component)
    row = save_search(cache, source_name, component, search_kind, response, query)
    row["just_fetched"] = True
    return row


def exact_hits(response, component):
    target = normalize(component)
    hits = []
    for artist in response.get("artists", []):
        names = [(artist.get("name", ""), "canonical_name")]
        for alias in artist.get("aliases", []):
            alias_name = alias.get("name", "") if isinstance(alias, dict) else alias
            names.append((alias_name, "alias"))
        matched_basis = next((basis for name, basis in names if normalize(name) == target), "")
        if matched_basis:
            hits.append(
                {
                    "id": artist.get("id", ""),
                    "name": artist.get("name", ""),
                    "score": artist.get("score", ""),
                    "basis": matched_basis,
                    "disambiguation": artist.get("disambiguation", ""),
                    "type": artist.get("type", ""),
                    "area": (artist.get("area") or {}).get("name", ""),
                }
            )
            break
    return hits


def write_csv(path, rows, fieldnames):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    configure_api_access()
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    cache = load_search_cache()
    zero_rows = load_zero_names()
    component_rows = []
    summary_rows = []
    request_count = 0

    for index, row in enumerate(zero_rows, start=1):
        credit = row["artist_name"]
        components = split_credit(credit)
        hit_components = []
        any_candidate = False
        for component in components:
            search = search_with_cache(cache, credit, component, "component")
            response = search["response"]
            if search.get("just_fetched"):
                request_count += 1
            candidates = response.get("artists", [])
            any_candidate |= bool(candidates)
            exact = exact_hits(response, component)
            if exact:
                hit_components.append({"component": component, **exact[0]})
            component_rows.append(
                {
                    "source_artist_name": credit,
                    "component": component,
                    "query": search.get("query", ""),
                    "candidate_count": response.get("count", 0),
                    "returned_candidate_count": len(candidates),
                    "exact_component_hit_count": len(exact),
                    "exact_component_hits": json.dumps(exact, ensure_ascii=False),
                    "top_candidates": json.dumps(
                        [
                            {
                                "id": artist.get("id", ""),
                                "name": artist.get("name", ""),
                                "score": artist.get("score", ""),
                                "disambiguation": artist.get("disambiguation", ""),
                            }
                            for artist in candidates[:5]
                        ],
                        ensure_ascii=False,
                    ),
                }
            )

        summary_rows.append(
            {
                "artist_name": credit,
                "components_searched": " | ".join(components),
                "component_count": len(components),
                "any_candidate_returned": any_candidate,
                "exact_components_found": " | ".join(
                    hit["component"] for hit in hit_components
                ),
                "exact_component_hit_count": len(hit_components),
                "exact_component_matches": json.dumps(hit_components, ensure_ascii=False),
                "composite_credit_not_single_artist": len(components) > 1,
            }
        )
        if index % 10 == 0 or index == len(zero_rows):
            print(f"Processed component splits for {index}/{len(zero_rows)} original zero names")

    targeted_rows = []
    for index, (name, query_name) in enumerate(TARGETED_NAMES):
        search = search_with_cache(cache, name, query_name, "targeted_core_name")
        response = search["response"]
        if search.get("just_fetched"):
            request_count += 1
        targeted_rows.append(
            {
                "artist_name": name,
                "targeted_search_term": query_name,
                "query": search.get("query", ""),
                "candidate_count": response.get("count", 0),
                "returned_candidate_count": len(response.get("artists", [])),
                "target_term_exact_name_or_alias_hits": json.dumps(
                    exact_hits(response, query_name), ensure_ascii=False
                ),
                "full_billing_exact_name_or_alias_hits": json.dumps(
                    exact_hits(response, name), ensure_ascii=False
                ),
                "top_candidates": json.dumps(
                    [
                        {
                            "id": artist.get("id", ""),
                            "name": artist.get("name", ""),
                            "score": artist.get("score", ""),
                            "disambiguation": artist.get("disambiguation", ""),
                            "type": artist.get("type", ""),
                            "area": (artist.get("area") or {}).get("name", ""),
                        }
                        for artist in response.get("artists", [])[:10]
                    ],
                    ensure_ascii=False,
                ),
            }
        )
        time.sleep(1.05 if index < len(TARGETED_NAMES) - 1 else 0)

    write_csv(
        COMPONENT_RESULTS,
        component_rows,
        [
            "source_artist_name",
            "component",
            "query",
            "candidate_count",
            "returned_candidate_count",
            "exact_component_hit_count",
            "exact_component_hits",
            "top_candidates",
        ],
    )
    write_csv(
        COMPONENT_SUMMARY,
        summary_rows,
        [
            "artist_name",
            "components_searched",
            "component_count",
            "any_candidate_returned",
            "exact_components_found",
            "exact_component_hit_count",
            "exact_component_matches",
            "composite_credit_not_single_artist",
        ],
    )
    write_csv(
        TARGETED_RESULTS,
        targeted_rows,
        [
            "artist_name",
            "targeted_search_term",
            "query",
            "candidate_count",
            "returned_candidate_count",
            "target_term_exact_name_or_alias_hits",
            "full_billing_exact_name_or_alias_hits",
            "top_candidates",
        ],
    )

    recovered_any = sum(row["any_candidate_returned"] for row in summary_rows)
    recovered_exact_component = sum(row["exact_component_hit_count"] > 0 for row in summary_rows)
    print(f"Component searches yielding any candidates: {recovered_any}/{len(summary_rows)}")
    print(f"Credits with exact name/alias hit for at least one component: {recovered_exact_component}/{len(summary_rows)}")
    print(f"New network requests issued: {request_count}; all raw responses cached at {COMPONENT_CACHE}")
    print(f"Targeted results saved to {TARGETED_RESULTS}")


if __name__ == "__main__":
    main()