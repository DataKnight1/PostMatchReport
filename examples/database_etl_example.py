#!/usr/bin/env python3
"""
Database ETL Example
Demonstrates loading WhoScored data into a database.
"""

import sys
sys.path.insert(0, '..')

from ETL.extractors.whoscored_extractor import WhoScoredExtractor
from ETL.transformers.match_processor import MatchProcessor
from ETL.transformers.stats_aggregator import StatsAggregator
from ETL.loaders.database_loader import DatabaseLoader
from ETL.loaders.data_loader import DataLoader


def main():
    """Example of loading data into a database."""

    # Match ID
    match_id = 1946652

    print("="*70)
    print(f"Database ETL Example - Match ID: {match_id}")
    print("="*70)

    # ===== EXTRACT =====
    print("\n[1/3] Extracting data...")

    loader = DataLoader(cache_dir="./cache")
    data = loader.load_whoscored_data(match_id, use_cache=True)

    if not data.get('match_centre', {}).get('success'):
        print("ERROR: Failed to extract data")
        return

    print("✓ Data extracted successfully")

    # ===== TRANSFORM =====
    print("\n[2/3] Transforming data...")

    processor = MatchProcessor(data, fotmob_data=None)

    # Aggregate statistics
    events_df = processor.get_events_dataframe()
    home_id = data['match_centre']['home_team']['team_id']
    away_id = data['match_centre']['away_team']['team_id']

    aggregator = StatsAggregator(events_df, home_id, away_id)
    stats = aggregator.aggregate_all_stats()

    print("✓ Data transformed successfully")

    # ===== LOAD TO DATABASE =====
    print("\n[3/3] Loading to database...")

    # Initialize database (SQLite for this example)
    db = DatabaseLoader(database_url="sqlite:///whoscored_matches.db")

    # Load complete match
    success = db.load_complete_match(data, processor)

    if success:
        print("✓ Data loaded to database successfully")

        # Query back the data
        print("\n" + "-"*70)
        print("Querying data back from database...")
        print("-"*70)

        # Query match info
        match_df = db.query_match_stats(match_id)
        print("\nMatch Info:")
        print(match_df[['whoscored_id', 'home_team_name', 'away_team_name',
                       'home_score', 'away_score', 'venue']].to_string(index=False))

        # Query events
        events_df = db.query_events(match_id)
        print(f"\nTotal events in database: {len(events_df)}")
        print("\nSample events:")
        print(events_df[['minute', 'type', 'team_name', 'player_name', 'is_successful']].head(10).to_string(index=False))

    else:
        print("ERROR: Failed to load data to database")

    # Close database connection
    db.close()

    print("\n" + "="*70)
    print("Database example completed!")
    print("="*70)


if __name__ == "__main__":
    main()
