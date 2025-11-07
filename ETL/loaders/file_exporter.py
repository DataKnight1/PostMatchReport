"""
File Exporter
Exports processed data to various file formats (CSV, Parquet, JSON, Excel).
"""

import pandas as pd
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging


class FileExporter:
    """Export match data to various file formats."""

    def __init__(self, output_dir: str = "./exports"):
        """
        Initialize file exporter.

        Args:
            output_dir: Directory for exported files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export_events_csv(self, events_df: pd.DataFrame, match_id: int,
                         filename: Optional[str] = None) -> str:
        """
        Export events to CSV.

        Args:
            events_df: Events DataFrame
            match_id: Match ID
            filename: Custom filename (optional)

        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"events_{match_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        filepath = os.path.join(self.output_dir, filename)

        # Select key columns for export
        export_columns = [
            'teamId', 'playerId', 'period_value', 'minute', 'second',
            'cumulative_mins', 'type_display', 'outcome_display', 'is_successful',
            'x', 'y', 'endX', 'endY', 'distance', 'angle',
            'is_progressive', 'is_key_pass', 'is_assist', 'is_goal', 'xg'
        ]

        # Filter to available columns
        available_columns = [col for col in export_columns if col in events_df.columns]

        events_df[available_columns].to_csv(filepath, index=False)
        logging.info(f"Events exported to CSV: {filepath}")

        return filepath

    def export_events_parquet(self, events_df: pd.DataFrame, match_id: int,
                             filename: Optional[str] = None) -> str:
        """
        Export events to Parquet format.

        Args:
            events_df: Events DataFrame
            match_id: Match ID
            filename: Custom filename (optional)

        Returns:
            Path to exported file
        """
        try:
            import pyarrow
        except ImportError:
            raise ImportError("pyarrow is required for Parquet export. Install with: pip install pyarrow")

        if filename is None:
            filename = f"events_{match_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"

        filepath = os.path.join(self.output_dir, filename)

        events_df.to_parquet(filepath, index=False, engine='pyarrow')
        logging.info(f"Events exported to Parquet: {filepath}")

        return filepath

    def export_players_csv(self, players_df: pd.DataFrame, match_id: int,
                          filename: Optional[str] = None) -> str:
        """
        Export players to CSV.

        Args:
            players_df: Players DataFrame
            match_id: Match ID
            filename: Custom filename (optional)

        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"players_{match_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        filepath = os.path.join(self.output_dir, filename)

        players_df.to_csv(filepath, index=False)
        logging.info(f"Players exported to CSV: {filepath}")

        return filepath

    def export_statistics_csv(self, stats: Dict[str, Any], match_id: int,
                             filename: Optional[str] = None) -> str:
        """
        Export aggregated statistics to CSV.

        Args:
            stats: Statistics dictionary from StatsAggregator
            match_id: Match ID
            filename: Custom filename (optional)

        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"statistics_{match_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        filepath = os.path.join(self.output_dir, filename)

        # Convert to DataFrame
        data = []
        for stat_name, stat_value in stats.get('home', {}).items():
            data.append({
                'stat': stat_name,
                'home': stat_value,
                'away': stats.get('away', {}).get(stat_name, 0)
            })

        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        logging.info(f"Statistics exported to CSV: {filepath}")

        return filepath

    def export_complete_match_json(self, whoscored_data: Dict[str, Any],
                                   match_processor, stats: Dict[str, Any],
                                   match_id: int, filename: Optional[str] = None) -> str:
        """
        Export complete match data to JSON.

        Args:
            whoscored_data: Raw WhoScored data
            match_processor: MatchProcessor instance
            stats: Aggregated statistics
            match_id: Match ID
            filename: Custom filename (optional)

        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"match_complete_{match_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = os.path.join(self.output_dir, filename)

        # Build complete export
        export_data = {
            'match_id': match_id,
            'extracted_at': datetime.now().isoformat(),
            'match_info': whoscored_data.get('match_centre', {}).get('match_info', {}),
            'home_team': whoscored_data.get('match_centre', {}).get('home_team', {}),
            'away_team': whoscored_data.get('match_centre', {}).get('away_team', {}),
            'aggregated_stats': stats,
            'summary': match_processor.get_complete_match_summary() if match_processor else {}
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logging.info(f"Complete match data exported to JSON: {filepath}")

        return filepath

    def export_to_excel(self, whoscored_data: Dict[str, Any], match_processor,
                       stats: Dict[str, Any], match_id: int,
                       filename: Optional[str] = None) -> str:
        """
        Export to Excel with multiple sheets.

        Args:
            whoscored_data: Raw WhoScored data
            match_processor: MatchProcessor instance
            stats: Aggregated statistics
            match_id: Match ID
            filename: Custom filename (optional)

        Returns:
            Path to exported file
        """
        try:
            import openpyxl
        except ImportError:
            raise ImportError("openpyxl is required for Excel export. Install with: pip install openpyxl")

        if filename is None:
            filename = f"match_{match_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        filepath = os.path.join(self.output_dir, filename)

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Match info sheet
            match_info = whoscored_data.get('match_centre', {}).get('match_info', {})
            match_info_df = pd.DataFrame([match_info])
            match_info_df.to_excel(writer, sheet_name='Match Info', index=False)

            # Statistics sheet
            stats_data = []
            for stat_name, stat_value in stats.get('home', {}).items():
                stats_data.append({
                    'stat': stat_name,
                    'home': stat_value,
                    'away': stats.get('away', {}).get(stat_name, 0)
                })
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name='Statistics', index=False)

            # Events sheet
            if match_processor:
                events_df = match_processor.get_events_dataframe()
                if not events_df.empty:
                    # Select key columns
                    export_columns = [
                        'teamId', 'playerId', 'period_value', 'minute', 'second',
                        'type_display', 'outcome_display', 'is_successful',
                        'x', 'y', 'distance', 'is_key_pass', 'is_goal'
                    ]
                    available_columns = [col for col in export_columns if col in events_df.columns]
                    events_df[available_columns].to_excel(writer, sheet_name='Events', index=False)

            # Players sheet
            if match_processor:
                players_df = match_processor.get_players_dataframe()
                if not players_df.empty:
                    players_df.to_excel(writer, sheet_name='Players', index=False)

        logging.info(f"Match data exported to Excel: {filepath}")

        return filepath

    def export_pass_network_data(self, positions_df: pd.DataFrame,
                                connections_df: pd.DataFrame,
                                team_name: str, match_id: int,
                                filename: Optional[str] = None) -> str:
        """
        Export pass network data to CSV.

        Args:
            positions_df: Player positions DataFrame
            connections_df: Pass connections DataFrame
            team_name: Team name
            match_id: Match ID
            filename: Custom filename (optional)

        Returns:
            Path to exported file
        """
        if filename is None:
            team_slug = team_name.lower().replace(' ', '_')
            filename = f"pass_network_{team_slug}_{match_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        filepath = os.path.join(self.output_dir, filename)

        # Combine positions and connections
        with open(filepath, 'w') as f:
            f.write("# Player Positions\n")

        positions_df.to_csv(filepath, mode='a', index=False)

        with open(filepath, 'a') as f:
            f.write("\n# Pass Connections\n")

        connections_df.to_csv(filepath, mode='a', index=False)

        logging.info(f"Pass network data exported to CSV: {filepath}")

        return filepath

    def export_all_formats(self, whoscored_data: Dict[str, Any], match_processor,
                          stats: Dict[str, Any], match_id: int) -> Dict[str, str]:
        """
        Export to all available formats.

        Args:
            whoscored_data: Raw WhoScored data
            match_processor: MatchProcessor instance
            stats: Aggregated statistics
            match_id: Match ID

        Returns:
            Dictionary mapping format to filepath
        """
        exports = {}

        # CSV
        if match_processor:
            events_df = match_processor.get_events_dataframe()
            if not events_df.empty:
                exports['events_csv'] = self.export_events_csv(events_df, match_id)

            players_df = match_processor.get_players_dataframe()
            if not players_df.empty:
                exports['players_csv'] = self.export_players_csv(players_df, match_id)

        # Statistics CSV
        exports['stats_csv'] = self.export_statistics_csv(stats, match_id)

        # JSON
        exports['json'] = self.export_complete_match_json(
            whoscored_data, match_processor, stats, match_id
        )

        # Excel (if available)
        try:
            exports['excel'] = self.export_to_excel(
                whoscored_data, match_processor, stats, match_id
            )
        except ImportError:
            logging.warning("Excel export skipped (openpyxl not installed)")

        # Parquet (if available)
        try:
            if match_processor:
                events_df = match_processor.get_events_dataframe()
                if not events_df.empty:
                    exports['parquet'] = self.export_events_parquet(events_df, match_id)
        except ImportError:
            logging.warning("Parquet export skipped (pyarrow not installed)")

        return exports
