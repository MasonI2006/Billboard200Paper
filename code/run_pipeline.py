"""Run the full pipeline in order, cache-only by default.

Usage (from the project root, with the Python 3.10 interpreter):
    py -3.10 code/run_pipeline.py                 # cache-only: a cache miss stops the run
    py -3.10 code/run_pipeline.py --from 11       # start at step 11
    py -3.10 code/run_pipeline.py --only 20 21    # run selected steps
    py -3.10 code/run_pipeline.py --allow-api     # permit MusicBrainz requests (ask first)

Step 15 (genre hand-check sheet) is never run here: it regenerates a sheet that
holds the manual hand-check columns. Run it directly only if the sheet must be rebuilt.
"""

import argparse
import os
import subprocess
import sys
import time

from paths import CODE_DIR, ROOT


STEPS = [
    ("01", "01_build_spotify_album_sample.py", []),
    ("02", "02_spotify_exploratory_analysis.py", []),
    ("03", "03_build_pre_rule_roster.py", []),
    ("04", "04_match_musicbrainz_artists.py", []),
    ("05", "05_retry_zero_matches.py", []),
    ("06", "06_audit_search_exceptions.py", []),
    ("07", "07_search_zero_components.py", []),
    ("08", "08_resolve_ambiguities.py", []),
    ("09", "09_apply_identity_decisions.py", []),
    ("10", "10_report_resolution_balance.py", []),
    ("11", "11_collect_discographies.py", ["--phase", "all"]),
    ("12", "12_validate_musicbrainz_collection.py", []),
    ("13", "13_adjudicate_edition_handcheck.py", []),
    ("14", "14_validate_album_collection.py", []),
    ("16", "16_part1_digital_robustness.py", []),
    ("17", "17_part1_headline.py", []),
    ("18", "18_part1_secondary_checks.py", []),
    ("20", "20_part2_incumbency.py", []),
    ("21", "21_part2b_build.py", []),
    ("22", "22_part2b_analyze.py", []),
    ("23", "23_part2b_album_age.py", []),
    ("19", "19_genre_rule_sensitivity.py", []),  # exploratory; needs 17 and 21-23 first
]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--from", dest="start", help="First step number to run, e.g. 11")
    parser.add_argument("--only", nargs="+", help="Run only these step numbers")
    parser.add_argument("--allow-api", action="store_true", help="Permit MusicBrainz API requests")
    args = parser.parse_args()

    steps = STEPS
    if args.start:
        steps = [step for step in steps if step[0] >= args.start.zfill(2)]
    if args.only:
        wanted = {number.zfill(2) for number in args.only}
        steps = [step for step in steps if step[0] in wanted]

    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    extra = ["--allow-api"] if args.allow_api else []
    print(f"Mode: {'API allowed' if args.allow_api else 'cache-only'}; steps: {' '.join(s[0] for s in steps)}", flush=True)
    for number, script, script_args in steps:
        command = [sys.executable, str(CODE_DIR / script), *script_args]
        # Only the scripts that can call the API accept --allow-api.
        if number in {"04", "05", "07", "11"}:
            command += extra
        print(f"\n=== Step {number}: {script}", flush=True)
        started = time.monotonic()
        result = subprocess.run(command, cwd=ROOT, env=env)
        if result.returncode != 0:
            print(f"Step {number} failed with exit code {result.returncode}; stopping.", flush=True)
            sys.exit(result.returncode)
        print(f"--- Step {number} finished in {time.monotonic() - started:.0f}s", flush=True)
    print("\nPipeline finished.")


if __name__ == "__main__":
    main()
