"""
WhoScored Data Analyzer

Utility functions to parse and analyze extracted WhoScored data.
"""

import json
from typing import Dict, Any, List, Optional
import pandas as pd


class WhoScoredDataAnalyzer:
    """Analyze and parse WhoScored extracted data."""

    def __init__(self, data_file: Optional[str] = None):
        """
        Initialize analyzer.

        Args:
            data_file: Path to JSON file with extracted data
        """
        self.data = None
        if data_file:
            self.load_data(data_file)

    def load_data(self, data_file: str):
        """Load data from JSON file."""
        with open(data_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        print(f"Loaded data from: {data_file}")

    def get_match_info(self) -> Optional[Dict[str, Any]]:
        """Extract basic match information."""
        if not self.data:
            return None

        match_report = self.data.get('sections', {}).get('match_report', {})
        if not match_report.get('success'):
            return None

        match_data = match_report.get('data', {}).get('matchCentreData', {})

        return {
            'match_id': self.data.get('match_id'),
            'home_team': match_data.get('home', {}).get('name'),
            'away_team': match_data.get('away', {}).get('name'),
            'score': match_data.get('score'),
            'venue': match_data.get('venueName'),
            'date': match_data.get('startDate'),
            'competition': match_data.get('competition', {}).get('name'),
        }

    def get_match_events(self) -> Optional[List[Dict[str, Any]]]:
        """Extract all match events."""
        if not self.data:
            return None

        match_report = self.data.get('sections', {}).get('match_report', {})
        if not match_report.get('success'):
            return None

        match_data = match_report.get('data', {}).get('matchCentreData', {})
        return match_data.get('events', [])

    def get_events_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """
        Filter events by type.

        Args:
            event_type: Type of event (e.g., 'Pass', 'Shot', 'Tackle')

        Returns:
            List of events matching the type
        """
        events = self.get_match_events()
        if not events:
            return []

        return [e for e in events if e.get('type', {}).get('displayName') == event_type]

    def get_player_statistics(self) -> Optional[Dict[str, Any]]:
        """Extract player statistics."""
        if not self.data:
            return None

        match_report = self.data.get('sections', {}).get('match_report', {})
        if not match_report.get('success'):
            return None

        match_data = match_report.get('data', {}).get('matchCentreData', {})

        home_players = match_data.get('home', {}).get('players', [])
        away_players = match_data.get('away', {}).get('players', [])

        return {
            'home': home_players,
            'away': away_players
        }

    def get_team_statistics(self) -> Optional[Dict[str, Any]]:
        """Extract team-level statistics."""
        if not self.data:
            return None

        match_centre = self.data.get('sections', {}).get('match_centre', {})
        if not match_centre.get('success'):
            return None

        stats_data = match_centre.get('data', {}).get('matchCentreData', {})

        return {
            'home': stats_data.get('home', {}).get('stats'),
            'away': stats_data.get('away', {}).get('stats')
        }

    def get_head_to_head_history(self) -> Optional[List[Dict[str, Any]]]:
        """Extract head-to-head match history."""
        if not self.data:
            return None

        h2h = self.data.get('sections', {}).get('head_to_head', {})
        if not h2h.get('success'):
            return None

        return h2h.get('data', {}).get('previousMeetings', [])

    def get_betting_odds(self) -> Optional[Dict[str, Any]]:
        """Extract betting odds information."""
        if not self.data:
            return None

        betting = self.data.get('sections', {}).get('betting', {})
        if not betting.get('success'):
            return None

        return betting.get('data', {}).get('bettingData')

    def events_to_dataframe(self) -> Optional[pd.DataFrame]:
        """Convert match events to pandas DataFrame."""
        events = self.get_match_events()
        if not events:
            return None

        # Flatten event data for DataFrame
        flattened_events = []
        for event in events:
            flat_event = {
                'event_id': event.get('eventId'),
                'minute': event.get('minute'),
                'second': event.get('second'),
                'team_id': event.get('teamId'),
                'player_id': event.get('playerId'),
                'x': event.get('x'),
                'y': event.get('y'),
                'end_x': event.get('endX'),
                'end_y': event.get('endY'),
                'type': event.get('type', {}).get('displayName'),
                'outcome': event.get('outcomeType', {}).get('displayName'),
                'period': event.get('period', {}).get('displayName'),
                'is_touch': event.get('isTouch'),
            }

            # Add qualifiers
            qualifiers = event.get('qualifiers', [])
            for qualifier in qualifiers:
                qual_type = qualifier.get('type', {}).get('displayName')
                qual_value = qualifier.get('value')
                flat_event[f'qualifier_{qual_type}'] = qual_value

            flattened_events.append(flat_event)

        return pd.DataFrame(flattened_events)

    def print_summary(self):
        """Print a summary of extracted data."""
        if not self.data:
            print("No data loaded.")
            return

        print("\n" + "=" * 70)
        print("WHOSCORED DATA SUMMARY")
        print("=" * 70)

        # Match info
        match_info = self.get_match_info()
        if match_info:
            print(f"\nMatch ID: {match_info['match_id']}")
            print(f"Teams: {match_info['home_team']} vs {match_info['away_team']}")
            print(f"Score: {match_info['score']}")
            print(f"Venue: {match_info['venue']}")
            print(f"Date: {match_info['date']}")
            print(f"Competition: {match_info['competition']}")

        # Events summary
        events = self.get_match_events()
        if events:
            print(f"\nTotal Events: {len(events)}")

            # Count by type
            event_types = {}
            for event in events:
                event_type = event.get('type', {}).get('displayName', 'Unknown')
                event_types[event_type] = event_types.get(event_type, 0) + 1

            print("\nEvents by Type:")
            for event_type, count in sorted(event_types.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {event_type:20} - {count}")

        # Section status
        print("\n" + "=" * 70)
        print("SECTIONS STATUS")
        print("=" * 70)

        sections = self.data.get('sections', {})
        for section_name, section_data in sections.items():
            status = "✓" if section_data.get('success') else "✗"
            print(f"  {status} {section_name.upper()}")

        print("=" * 70 + "\n")


def main():
    """Example usage of the analyzer."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python data_analyzer.py <data_file.json>")
        print("\nExample: python data_analyzer.py whoscored_match_1716104_all_data.json")
        return

    data_file = sys.argv[1]

    # Initialize analyzer
    analyzer = WhoScoredDataAnalyzer(data_file)

    # Print summary
    analyzer.print_summary()

    # Get match info
    match_info = analyzer.get_match_info()
    if match_info:
        print(f"\nMatch: {match_info['home_team']} vs {match_info['away_team']}")

    # Get events as DataFrame
    df = analyzer.events_to_dataframe()
    if df is not None:
        print(f"\nEvents DataFrame shape: {df.shape}")
        print("\nFirst few events:")
        print(df.head())

        # Save to CSV
        csv_file = data_file.replace('.json', '_events.csv')
        df.to_csv(csv_file, index=False)
        print(f"\nEvents saved to: {csv_file}")


if __name__ == "__main__":
    main()
