#!/usr/bin/env python3
"""
Simple ETL Example
Demonstrates basic usage of the WhoScored ETL pipeline.
"""

import sys
sys.path.insert(0, '..')

from ETL.extractors.whoscored_extractor import WhoScoredExtractor
from ETL.transformers.match_processor import MatchProcessor
from ETL.transformers.stats_aggregator import StatsAggregator
from ETL.loaders.file_exporter import FileExporter


def main():
    """Simple example of extracting and processing match data."""

    # Match ID for FC Utrecht vs FC Porto
    match_id = 1946652

    print("="*70)
    print(f"Simple WhoScored ETL Example - Match ID: {match_id}")
    print("="*70)

    # ===== STEP 1: EXTRACT =====
    print("\n[1/3] Extracting data from WhoScored...")

    extractor = WhoScoredExtractor(headless=True)
    data = extractor.extract_all_sections(match_id)

    if not data.get('match_centre', {}).get('success'):
        print("ERROR: Failed to extract data")
        return

    print("✓ Data extracted successfully")

    # ===== STEP 2: TRANSFORM =====
    print("\n[2/3] Transforming and processing data...")

    # Initialize processor
    processor = MatchProcessor(data, fotmob_data=None)

    # Get match summary
    summary = processor.get_complete_match_summary()

    # Get team information
    home_team = summary['teams']['home']
    away_team = summary['teams']['away']

    print(f"\nMatch: {home_team['name']} vs {away_team['name']}")
    print(f"Formation: {home_team['formation']} vs {away_team['formation']}")

    # Get events
    events_df = processor.get_events_dataframe()
    print(f"Total events processed: {len(events_df)}")

    # Aggregate statistics
    home_id = data['match_centre']['home_team']['team_id']
    away_id = data['match_centre']['away_team']['team_id']

    aggregator = StatsAggregator(events_df, home_id, away_id)
    stats = aggregator.aggregate_all_stats()

    print("\n✓ Data transformed successfully")

    # ===== STEP 3: DISPLAY STATS =====
    print("\n[3/3] Match Statistics:")
    print("-" * 70)

    home_stats = stats['home']
    away_stats = stats['away']

    print(f"\n{'Statistic':<25} {'Home':>10} {'Away':>10}")
    print("-" * 50)
    print(f"{'Shots':<25} {home_stats['shots']:>10} {away_stats['shots']:>10}")
    print(f"{'Shots on Target':<25} {home_stats['shots_on_target']:>10} {away_stats['shots_on_target']:>10}")
    print(f"{'Goals':<25} {home_stats['goals']:>10} {away_stats['goals']:>10}")
    print(f"{'xG':<25} {home_stats['xg']:>10.2f} {away_stats['xg']:>10.2f}")
    print(f"{'Passes':<25} {home_stats['passes']:>10} {away_stats['passes']:>10}")
    print(f"{'Pass Accuracy (%)':<25} {home_stats['pass_accuracy']:>10.1f} {away_stats['pass_accuracy']:>10.1f}")
    print(f"{'Touches':<25} {home_stats['touches']:>10} {away_stats['touches']:>10}")
    print(f"{'Tackles':<25} {home_stats['tackles']:>10} {away_stats['tackles']:>10}")
    print(f"{'Interceptions':<25} {home_stats['interceptions']:>10} {away_stats['interceptions']:>10}")
    print(f"{'Clearances':<25} {home_stats['clearances']:>10} {away_stats['clearances']:>10}")
    print(f"{'Dribbles':<25} {home_stats['dribbles']:>10} {away_stats['dribbles']:>10}")
    print(f"{'Fouls':<25} {home_stats['fouls']:>10} {away_stats['fouls']:>10}")

    print("\n" + "="*70)
    print("Example completed successfully!")
    print("="*70)

    # Optional: Export data
    print("\nExporting data to JSON...")
    exporter = FileExporter(output_dir="./exports")
    json_path = exporter.export_complete_match_json(data, processor, stats, match_id)
    print(f"✓ Data exported to: {json_path}")


if __name__ == "__main__":
    main()
