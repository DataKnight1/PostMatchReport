#!/usr/bin/env python3
"""
Batch ETL Example
Demonstrates processing multiple matches in batch.
"""

import sys
sys.path.insert(0, '..')

from whoscored_etl import WhoScoredETL
import time


def main():
    """Process multiple matches in batch."""

    # List of match IDs to process
    match_ids = [
        1946652,  # FC Utrecht vs FC Porto
        # Add more match IDs here
    ]

    print("="*70)
    print(f"Batch ETL Processing - {len(match_ids)} matches")
    print("="*70)

    # Initialize ETL with database
    etl = WhoScoredETL(
        cache_dir="./cache",
        output_dir="./exports",
        database_url="sqlite:///whoscored_matches.db",  # Change to your database
        verbose=False
    )

    results_summary = []

    for i, match_id in enumerate(match_ids, 1):
        print(f"\n{'='*70}")
        print(f"Processing match {i}/{len(match_ids)}: {match_id}")
        print(f"{'='*70}")

        try:
            # Run ETL for this match
            result = etl.run(
                match_id=match_id,
                use_cache=True,
                export_formats=['database', 'csv', 'json']
            )

            results_summary.append({
                'match_id': match_id,
                'success': result['success'],
                'error': result.get('error')
            })

            # Rate limiting: wait between requests to avoid being blocked
            if i < len(match_ids):
                print("\nWaiting 10 seconds before next match...")
                time.sleep(10)

        except Exception as e:
            print(f"ERROR processing match {match_id}: {e}")
            results_summary.append({
                'match_id': match_id,
                'success': False,
                'error': str(e)
            })

    # Print summary
    print("\n" + "="*70)
    print("BATCH PROCESSING SUMMARY")
    print("="*70)

    successful = sum(1 for r in results_summary if r['success'])
    failed = len(results_summary) - successful

    print(f"\nTotal matches: {len(match_ids)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

    if failed > 0:
        print("\nFailed matches:")
        for result in results_summary:
            if not result['success']:
                print(f"  {result['match_id']}: {result['error']}")

    print("\n" + "="*70)


if __name__ == "__main__":
    main()
