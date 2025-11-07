#!/usr/bin/env python3
"""
WhoScored ETL Pipeline
Comprehensive ETL pipeline for extracting, transforming, and loading WhoScored match data.

This script orchestrates the entire ETL process:
1. Extract: Fetch data from WhoScored using Playwright
2. Transform: Process events, calculate statistics, aggregate data
3. Load: Export to database, CSV, JSON, Parquet, Excel

Usage:
    # Basic extraction and export to all formats
    python whoscored_etl.py 1946652

    # Export to specific database
    python whoscored_etl.py 1946652 --database postgresql://user:pass@localhost/dbname

    # Export specific formats
    python whoscored_etl.py 1946652 --export csv,json,excel

    # Skip cache
    python whoscored_etl.py 1946652 --no-cache

    # Verbose output
    python whoscored_etl.py 1946652 --verbose
"""

import argparse
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import json

# ETL Components
from ETL.extractors.whoscored_extractor import WhoScoredExtractor
from ETL.transformers.match_processor import MatchProcessor
from ETL.transformers.stats_aggregator import StatsAggregator
from ETL.loaders.data_loader import DataLoader
from ETL.loaders.file_exporter import FileExporter

# Optional: Database loader
try:
    from ETL.loaders.database_loader import DatabaseLoader
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False


class WhoScoredETL:
    """Main ETL orchestrator for WhoScored data."""

    def __init__(self, cache_dir: str = "./cache", output_dir: str = "./exports",
                 database_url: Optional[str] = None, verbose: bool = False):
        """
        Initialize ETL pipeline.

        Args:
            cache_dir: Directory for caching raw data
            output_dir: Directory for exported files
            database_url: Database connection URL (optional)
            verbose: Enable verbose logging
        """
        # Setup logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.data_loader = DataLoader(cache_dir=cache_dir)
        self.file_exporter = FileExporter(output_dir=output_dir)

        # Initialize database loader if URL provided
        self.database_loader = None
        if database_url:
            if not DATABASE_AVAILABLE:
                self.logger.error("Database export requested but SQLAlchemy not available.")
                self.logger.error("Install with: pip install sqlalchemy psycopg2-binary")
            else:
                try:
                    self.database_loader = DatabaseLoader(database_url)
                    self.logger.info(f"Database loader initialized: {database_url}")
                except Exception as e:
                    self.logger.error(f"Failed to initialize database loader: {e}")

    def run(self, match_id: int, use_cache: bool = True,
            export_formats: Optional[list] = None) -> Dict[str, Any]:
        """
        Run complete ETL pipeline.

        Args:
            match_id: WhoScored match ID
            use_cache: Use cached data if available
            export_formats: List of export formats ('csv', 'json', 'excel', 'parquet', 'database')
                          If None, exports all available formats

        Returns:
            Dictionary with ETL results and export paths
        """
        self.logger.info("="*70)
        self.logger.info(f"Starting WhoScored ETL Pipeline for Match ID: {match_id}")
        self.logger.info("="*70)

        results = {
            'match_id': match_id,
            'success': False,
            'error': None,
            'exports': {},
            'stats': {},
            'start_time': datetime.now().isoformat()
        }

        try:
            # ===== EXTRACT =====
            self.logger.info("\n[1/3] EXTRACT - Fetching data from WhoScored...")
            whoscored_data = self.data_loader.load_whoscored_data(match_id, use_cache=use_cache)

            if not whoscored_data.get('match_centre', {}).get('success'):
                raise Exception("Failed to extract match data from WhoScored")

            self.logger.info("✓ Data extraction successful")

            # ===== TRANSFORM =====
            self.logger.info("\n[2/3] TRANSFORM - Processing and transforming data...")

            # Initialize match processor
            match_processor = MatchProcessor(whoscored_data, fotmob_data=None)

            if not match_processor.event_processor:
                raise Exception("Failed to initialize event processor")

            # Get match info
            match_centre = whoscored_data.get('match_centre', {})
            match_info = match_centre.get('match_info', {})
            home_team = match_centre.get('home_team', {})
            away_team = match_centre.get('away_team', {})

            self.logger.info(f"  Match: {home_team.get('name')} vs {away_team.get('name')}")
            self.logger.info(f"  Score: {match_info.get('score')}")
            self.logger.info(f"  Date: {match_info.get('date')}")
            self.logger.info(f"  Venue: {match_info.get('venue')}")

            # Aggregate statistics
            events_df = match_processor.get_events_dataframe()
            self.logger.info(f"  Processed {len(events_df)} events")

            stats_aggregator = StatsAggregator(
                events_df,
                home_team.get('team_id'),
                away_team.get('team_id')
            )

            aggregated_stats = stats_aggregator.aggregate_all_stats()
            whoscored_format_stats = stats_aggregator.export_whoscored_format()

            self.logger.info("✓ Data transformation complete")

            # Store stats in results
            results['stats'] = aggregated_stats
            results['whoscored_format'] = whoscored_format_stats

            # ===== LOAD =====
            self.logger.info("\n[3/3] LOAD - Exporting data...")

            # Determine export formats
            if export_formats is None:
                export_formats = ['csv', 'json', 'excel', 'parquet']
                if self.database_loader:
                    export_formats.append('database')

            # Export to database
            if 'database' in export_formats and self.database_loader:
                self.logger.info("  Exporting to database...")
                success = self.database_loader.load_complete_match(whoscored_data, match_processor)
                if success:
                    results['exports']['database'] = 'Success'
                    self.logger.info("  ✓ Database export complete")
                else:
                    self.logger.error("  ✗ Database export failed")

            # Export to CSV
            if 'csv' in export_formats:
                self.logger.info("  Exporting to CSV...")
                csv_path = self.file_exporter.export_events_csv(events_df, match_id)
                results['exports']['events_csv'] = csv_path

                stats_path = self.file_exporter.export_statistics_csv(aggregated_stats, match_id)
                results['exports']['stats_csv'] = stats_path
                self.logger.info(f"  ✓ CSV exports: {csv_path}, {stats_path}")

            # Export to JSON
            if 'json' in export_formats:
                self.logger.info("  Exporting to JSON...")
                json_path = self.file_exporter.export_complete_match_json(
                    whoscored_data, match_processor, aggregated_stats, match_id
                )
                results['exports']['json'] = json_path
                self.logger.info(f"  ✓ JSON export: {json_path}")

            # Export to Excel
            if 'excel' in export_formats:
                try:
                    self.logger.info("  Exporting to Excel...")
                    excel_path = self.file_exporter.export_to_excel(
                        whoscored_data, match_processor, aggregated_stats, match_id
                    )
                    results['exports']['excel'] = excel_path
                    self.logger.info(f"  ✓ Excel export: {excel_path}")
                except ImportError as e:
                    self.logger.warning(f"  ⚠ Excel export skipped: {e}")

            # Export to Parquet
            if 'parquet' in export_formats:
                try:
                    self.logger.info("  Exporting to Parquet...")
                    parquet_path = self.file_exporter.export_events_parquet(events_df, match_id)
                    results['exports']['parquet'] = parquet_path
                    self.logger.info(f"  ✓ Parquet export: {parquet_path}")
                except ImportError as e:
                    self.logger.warning(f"  ⚠ Parquet export skipped: {e}")

            results['success'] = True
            results['end_time'] = datetime.now().isoformat()

            self.logger.info("\n" + "="*70)
            self.logger.info("ETL Pipeline completed successfully!")
            self.logger.info("="*70)

            # Print summary
            self._print_summary(results)

        except Exception as e:
            self.logger.error(f"\nETL Pipeline failed: {e}")
            import traceback
            traceback.print_exc()
            results['error'] = str(e)
            results['end_time'] = datetime.now().isoformat()

        return results

    def _print_summary(self, results: Dict[str, Any]):
        """Print ETL summary."""
        print("\n" + "="*70)
        print("ETL SUMMARY")
        print("="*70)

        # Match info
        if 'stats' in results and 'home' in results['stats']:
            print("\nMatch Statistics:")
            home_stats = results['stats']['home']
            away_stats = results['stats']['away']

            print(f"  Shots: {home_stats.get('shots', 0)} - {away_stats.get('shots', 0)}")
            print(f"  Passes: {home_stats.get('passes', 0)} - {away_stats.get('passes', 0)}")
            print(f"  Pass Accuracy: {home_stats.get('pass_accuracy', 0):.1f}% - {away_stats.get('pass_accuracy', 0):.1f}%")
            print(f"  Tackles: {home_stats.get('tackles', 0)} - {away_stats.get('tackles', 0)}")
            print(f"  xG: {home_stats.get('xg', 0):.2f} - {away_stats.get('xg', 0):.2f}")

        # Exports
        print("\nExported Files:")
        for format_name, path in results.get('exports', {}).items():
            print(f"  {format_name}: {path}")

        print("\n" + "="*70)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='WhoScored ETL Pipeline - Extract, Transform, Load match data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage - export to all formats
  %(prog)s 1946652

  # Export to PostgreSQL database
  %(prog)s 1946652 --database postgresql://user:pass@localhost/dbname

  # Export to SQLite database
  %(prog)s 1946652 --database sqlite:///matches.db

  # Export specific formats only
  %(prog)s 1946652 --export csv,json

  # Skip cache and re-download
  %(prog)s 1946652 --no-cache

  # Verbose logging
  %(prog)s 1946652 --verbose

  # Custom output directory
  %(prog)s 1946652 --output-dir ./my_exports
        """
    )

    parser.add_argument('match_id', type=int,
                       help='WhoScored match ID (e.g., 1946652)')

    parser.add_argument('--database', '--db', dest='database_url',
                       help='Database URL (e.g., sqlite:///matches.db or postgresql://...)')

    parser.add_argument('--export', '-e', dest='export_formats',
                       help='Comma-separated export formats: csv,json,excel,parquet,database')

    parser.add_argument('--cache-dir', default='./cache',
                       help='Cache directory (default: ./cache)')

    parser.add_argument('--output-dir', default='./exports',
                       help='Output directory for exports (default: ./exports)')

    parser.add_argument('--no-cache', action='store_true',
                       help='Skip cache and fetch fresh data')

    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose logging')

    parser.add_argument('--summary-only', action='store_true',
                       help='Only print summary statistics without exporting')

    args = parser.parse_args()

    # Parse export formats
    export_formats = None
    if args.export_formats:
        export_formats = [f.strip() for f in args.export_formats.split(',')]

    # Initialize ETL
    etl = WhoScoredETL(
        cache_dir=args.cache_dir,
        output_dir=args.output_dir,
        database_url=args.database_url,
        verbose=args.verbose
    )

    # Run pipeline
    if args.summary_only:
        export_formats = []  # Don't export anything

    results = etl.run(
        match_id=args.match_id,
        use_cache=not args.no_cache,
        export_formats=export_formats
    )

    # Exit with appropriate code
    sys.exit(0 if results['success'] else 1)


if __name__ == "__main__":
    main()
