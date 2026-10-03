"""Every project directory and file path, defined relative to the project root.

All pipeline scripts import their paths from here; nothing else should build a
path from ``__file__``. Layout is described in CLAUDE.md and docs/cleanup_move_map.md.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# Directories
CODE_DIR = ROOT / "code"
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"              # read-only Kaggle + Spotify inputs
EXTERNAL_DIR = DATA_DIR / "external"    # MusicBrainz caches, API logs, collected tables
INTERIM_DIR = DATA_DIR / "interim"
FINAL_DIR = DATA_DIR / "final"
RESULTS_DIR = ROOT / "results"
RESULTS_P1 = RESULTS_DIR / "part1_album_length"
RESULTS_P1_VALIDATION = RESULTS_P1 / "validation"
RESULTS_P1_SPOTIFY = RESULTS_P1 / "spotify_exploratory"
RESULTS_P1_SECONDARY = RESULTS_P1 / "secondary"
RESULTS_P2 = RESULTS_DIR / "part2_incumbency"
RESULTS_P2B = RESULTS_DIR / "part2b_genre_staying_power"

# Raw inputs (never edit)
RAW_BILLBOARD200 = RAW_DIR / "billboard200.csv"
RAW_HOT100 = RAW_DIR / "hot100.csv"
RAW_STREAMING = RAW_DIR / "streaming.csv"
RAW_DIGITAL = RAW_DIR / "digital.csv"
RAW_RADIO = RAW_DIR / "radio.csv"
RAW_SPOTIFY_TRACKS = RAW_DIR / "track_data_final.csv"
RAW_SPOTIFY_CLEAN = RAW_DIR / "spotify_data clean.csv"   # the space is in the real filename

# External: MusicBrainz caches (never delete) and collector outputs
ARTIST_SEARCH_CACHE = EXTERNAL_DIR / "musicbrainz_artist_search_cache.jsonl"
RELEASE_GROUP_CACHE = EXTERNAL_DIR / "musicbrainz_release_group_cache.jsonl"
OFFICIAL_RELEASE_CACHE = EXTERNAL_DIR / "musicbrainz_official_release_cache.jsonl"
ZERO_COMPONENT_CACHE = EXTERNAL_DIR / "musicbrainz_zero_component_searches.jsonl"
ARTIST_SEARCH_ERRORS = EXTERNAL_DIR / "musicbrainz_artist_search_errors.jsonl"
DISCOGRAPHY_API_ERRORS = EXTERNAL_DIR / "musicbrainz_discography_api_errors.jsonl"
RELEASE_GROUPS = EXTERNAL_DIR / "musicbrainz_release_groups.csv"
OFFICIAL_RELEASES = EXTERNAL_DIR / "musicbrainz_official_releases.csv"
ALBUM_CANDIDATES = EXTERNAL_DIR / "musicbrainz_standard_album_candidates.csv"

# Interim
ROSTER = INTERIM_DIR / "pre_rule_artist_roster.csv"
ROSTER_CREDIT_AUDIT = INTERIM_DIR / "pre_rule_artist_credit_audit.csv"
SPOTIFY_ALBUM_SAMPLE = INTERIM_DIR / "spotify_album_sample.csv"
ARTIST_MATCHES = INTERIM_DIR / "musicbrainz_artist_matches.csv"
ARTIST_MATCHES_REVIEW = INTERIM_DIR / "musicbrainz_artist_matches_review.csv"
AMBIGUITY_AUTO_RESOLUTION = INTERIM_DIR / "musicbrainz_ambiguity_auto_resolution.csv"
TARGETED_ARTIST_SEARCHES = INTERIM_DIR / "musicbrainz_targeted_artist_searches.csv"
TARGETED_IDENTITY_DECISIONS = INTERIM_DIR / "musicbrainz_targeted_identity_decisions.csv"
CONFIRMED_NOT_FOUND = INTERIM_DIR / "musicbrainz_confirmed_not_found.csv"
ZERO_COMPONENT_RESULTS = INTERIM_DIR / "musicbrainz_zero_component_results.csv"
ZERO_COMPONENT_SUMMARY = INTERIM_DIR / "musicbrainz_zero_component_summary.csv"
UNRESOLVED_BALANCE = INTERIM_DIR / "musicbrainz_unresolved_balance.csv"
TRUE_NOMATCH_ZERO = INTERIM_DIR / "true_nomatch_zero.csv"
FLAGGED_COMPOSITE_PARTIAL = INTERIM_DIR / "flagged_composite_partial.csv"
PART2B_CHART_LABELLED = INTERIM_DIR / "part2b_chart_labelled.pkl"

# Final (analysis-ready)
ANALYSIS_SAMPLE = FINAL_DIR / "analysis_sample.csv"
ARTIST_GENRES = FINAL_DIR / "artist_genres.csv"   # one genre per resolved roster artist (step 12a)
PART2_WEEKLY = FINAL_DIR / "part2_weekly_billboard200.csv"
PART2B_ALBUM_RUNS = FINAL_DIR / "part2b_album_runs.csv"
ANALYSIS_SAMPLE_0928 = ROOT / "archive" / "superseded_0928_genre_labels" / "analysis_sample_0928.csv"  # random labels, validation only

# Part 1 results and validation outputs
DIGITAL_ROBUSTNESS = RESULTS_P1 / "digital_robustness.csv"
BILLBOARD_COVERAGE = RESULTS_P1_VALIDATION / "musicbrainz_billboard_coverage.csv"
SPOTIFY_COUNT_COMPARISON = RESULTS_P1_VALIDATION / "musicbrainz_spotify_count_comparison.csv"
GENRE_BALANCE = RESULTS_P1_VALIDATION / "musicbrainz_genre_balance.csv"
SUBGENRE_BALANCE = RESULTS_P1_VALIDATION / "musicbrainz_subgenre_balance.csv"
UNRESOLVED_GENRE_BREAKDOWN = RESULTS_P1_VALIDATION / "musicbrainz_unresolved_genre_breakdown.csv"
EDITION_HANDCHECK_SAMPLE = RESULTS_P1_VALIDATION / "musicbrainz_edition_handcheck_sample.csv"
GENRE_HANDCHECK_SAMPLE = RESULTS_P1_VALIDATION / "genre_handcheck_sample_100.csv"
