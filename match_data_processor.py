"""
Match Data Processor
Processes and combines WhoScored and FotMob data for visualization.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
import json


class MatchDataProcessor:
    """Process match data from WhoScored and FotMob."""

    def __init__(self, whoscored_data: Dict[str, Any], fotmob_data: Optional[Dict[str, Any]] = None):
        """
        Initialize processor with match data.

        Args:
            whoscored_data: WhoScored extracted data
            fotmob_data: FotMob extracted data (optional)
        """
        self.whoscored_data = whoscored_data
        self.fotmob_data = fotmob_data

        # Extract match centre data
        match_report = whoscored_data.get('sections', {}).get('match_report', {})
        self.match_centre_data = match_report.get('data', {}).get('matchCentreData', {})

        # Process basic info
        self.home_team = self.match_centre_data.get('home', {})
        self.away_team = self.match_centre_data.get('away', {})

        # Create DataFrames
        self.events_df = None
        self.players_df = None
        self.home_players_df = None
        self.away_players_df = None

        self._process_data()

    def _process_data(self):
        """Process raw data into DataFrames."""
        # Process events
        events = self.match_centre_data.get('events', [])
        if events:
            self.events_df = self._create_events_dataframe(events)

        # Process players
        self._create_players_dataframes()

    def _create_events_dataframe(self, events: List[Dict]) -> pd.DataFrame:
        """
        Convert events to DataFrame with proper scaling.

        Args:
            events: List of event dictionaries

        Returns:
            DataFrame with processed events
        """
        df = pd.DataFrame(events)

        if df.empty:
            return df

        # Scale coordinates to standard pitch (105m x 68m)
        if 'x' in df.columns:
            df['x'] = df['x'] * 1.05
        if 'y' in df.columns:
            df['y'] = df['y'] * 0.68
        if 'endX' in df.columns:
            df['endX'] = df['endX'] * 1.05
        if 'endY' in df.columns:
            df['endY'] = df['endY'] * 0.68

        # Extract event type information
        if 'type' in df.columns:
            df['type_display'] = df['type'].apply(lambda x: x.get('displayName', '') if isinstance(x, dict) else '')
            df['type_value'] = df['type'].apply(lambda x: x.get('value', 0) if isinstance(x, dict) else 0)

        # Extract outcome type
        if 'outcomeType' in df.columns:
            df['outcome_display'] = df['outcomeType'].apply(
                lambda x: x.get('displayName', '') if isinstance(x, dict) else ''
            )
            df['is_successful'] = df['outcome_display'] == 'Successful'

        # Extract period information
        if 'period' in df.columns:
            df['period_display'] = df['period'].apply(
                lambda x: x.get('displayName', '') if isinstance(x, dict) else ''
            )
            df['period_value'] = df['period'].apply(lambda x: x.get('value', 1) if isinstance(x, dict) else 1)

        # Calculate cumulative minutes
        df['cumulative_mins'] = self._calculate_cumulative_minutes(df)

        # Process qualifiers
        df['qualifiers_dict'] = df['qualifiers'].apply(self._process_qualifiers)

        # Check for specific qualifiers
        df['is_key_pass'] = df['qualifiers_dict'].apply(lambda x: 'KeyPass' in x if isinstance(x, dict) else False)
        df['is_assist'] = df['qualifiers_dict'].apply(lambda x: 'Assist' in x if isinstance(x, dict) else False)

        return df

    def _process_qualifiers(self, qualifiers) -> Dict[str, Any]:
        """
        Process qualifiers into a dictionary.

        Args:
            qualifiers: List of qualifier dictionaries

        Returns:
            Dictionary of qualifiers
        """
        if not isinstance(qualifiers, list):
            return {}

        result = {}
        for q in qualifiers:
            if isinstance(q, dict) and 'type' in q:
                q_type = q['type'].get('displayName', '') if isinstance(q['type'], dict) else ''
                q_value = q.get('value', True)
                if q_type:
                    result[q_type] = q_value

        return result

    def _calculate_cumulative_minutes(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate cumulative match minutes accounting for periods.

        Args:
            df: Events DataFrame

        Returns:
            Series with cumulative minutes
        """
        if 'minute' not in df.columns or 'second' not in df.columns:
            return pd.Series([0] * len(df))

        cumulative_mins = []
        for _, row in df.iterrows():
            period_value = row.get('period_value', 1)
            minute = row.get('minute', 0)
            second = row.get('second', 0)

            # Calculate base minutes for each period
            if period_value == 1:  # First half
                base = 0
            elif period_value == 2:  # Second half
                base = 45
            elif period_value == 3:  # First extra time
                base = 90
            elif period_value == 4:  # Second extra time
                base = 105
            else:
                base = 0

            total = base + minute + (second / 60.0)
            cumulative_mins.append(total)

        return pd.Series(cumulative_mins)

    def _create_players_dataframes(self):
        """Create DataFrames for players."""
        home_players = self.home_team.get('players', [])
        away_players = self.away_team.get('players', [])

        # Create DataFrames
        self.home_players_df = pd.DataFrame(home_players) if home_players else pd.DataFrame()
        self.away_players_df = pd.DataFrame(away_players) if away_players else pd.DataFrame()

        # Combine all players
        all_players = home_players + away_players
        self.players_df = pd.DataFrame(all_players) if all_players else pd.DataFrame()

    def get_passes_df(self, team_id: Optional[int] = None, successful_only: bool = False) -> pd.DataFrame:
        """
        Get all pass events.

        Args:
            team_id: Filter by team ID (optional)
            successful_only: Only return successful passes

        Returns:
            DataFrame of pass events
        """
        if self.events_df is None or self.events_df.empty:
            return pd.DataFrame()

        # Filter for passes
        passes = self.events_df[self.events_df['type_display'] == 'Pass'].copy()

        # Filter by team
        if team_id is not None:
            passes = passes[passes['teamId'] == team_id]

        # Filter by success
        if successful_only:
            passes = passes[passes['is_successful'] == True]

        # Identify receiver (next event by same team)
        passes['receiver'] = None
        for idx in passes.index:
            pass_row = passes.loc[idx]
            next_events = self.events_df[
                (self.events_df.index > idx) &
                (self.events_df['teamId'] == pass_row['teamId']) &
                (self.events_df['type_display'].isin(['Pass', 'TakeOn', 'Shot']))
            ]
            if len(next_events) > 0:
                passes.at[idx, 'receiver'] = next_events.iloc[0]['playerId']

        return passes

    def get_shots_df(self, team_id: Optional[int] = None) -> pd.DataFrame:
        """
        Get all shot events.

        Args:
            team_id: Filter by team ID (optional)

        Returns:
            DataFrame of shot events
        """
        if self.events_df is None or self.events_df.empty:
            return pd.DataFrame()

        shots = self.events_df[self.events_df['type_display'] == 'Shot'].copy()

        if team_id is not None:
            shots = shots[shots['teamId'] == team_id]

        # Extract xG from qualifiers
        shots['xg'] = shots['qualifiers_dict'].apply(
            lambda x: float(x.get('xG', 0)) if isinstance(x, dict) and 'xG' in x else 0.0
        )

        return shots

    def get_defensive_actions_df(self, team_id: Optional[int] = None) -> pd.DataFrame:
        """
        Get defensive action events (tackles, interceptions, clearances, blocks).

        Args:
            team_id: Filter by team ID (optional)

        Returns:
            DataFrame of defensive actions
        """
        if self.events_df is None or self.events_df.empty:
            return pd.DataFrame()

        defensive_types = ['Tackle', 'Interception', 'Clearance', 'BlockedPass']
        actions = self.events_df[self.events_df['type_display'].isin(defensive_types)].copy()

        if team_id is not None:
            actions = actions[actions['teamId'] == team_id]

        return actions

    def get_carries_df(self, team_id: Optional[int] = None) -> pd.DataFrame:
        """
        Get carry events.

        Args:
            team_id: Filter by team ID (optional)

        Returns:
            DataFrame of carry events
        """
        if self.events_df is None or self.events_df.empty:
            return pd.DataFrame()

        carries = self.events_df[self.events_df['type_display'] == 'Carry'].copy()

        if team_id is not None:
            carries = carries[carries['teamId'] == team_id]

        return carries

    def get_passes_between_players(self, team_id: int, starting_xi_only: bool = True) -> pd.DataFrame:
        """
        Get aggregated passes between players.

        Args:
            team_id: Team ID
            starting_xi_only: Only include starting XI players

        Returns:
            DataFrame with pass connections between players
        """
        passes = self.get_passes_df(team_id=team_id, successful_only=True)

        if passes.empty:
            return pd.DataFrame()

        # Filter for starting XI if requested
        if starting_xi_only:
            if team_id == self.home_team.get('teamId'):
                players_df = self.home_players_df
            else:
                players_df = self.away_players_df

            if not players_df.empty and 'isFirstEleven' in players_df.columns:
                starting_players = players_df[players_df['isFirstEleven'] == True]['playerId'].tolist()
                passes = passes[
                    (passes['playerId'].isin(starting_players)) &
                    (passes['receiver'].isin(starting_players))
                ]

        # Remove passes without receiver
        passes = passes[passes['receiver'].notna()]

        # Aggregate passes between players
        passes_between = passes.groupby(['playerId', 'receiver']).size().reset_index(name='pass_count')

        return passes_between

    def get_player_average_positions(self, team_id: int, starting_xi_only: bool = True) -> pd.DataFrame:
        """
        Calculate average positions for players based on events.

        Args:
            team_id: Team ID
            starting_xi_only: Only include starting XI players

        Returns:
            DataFrame with player average positions
        """
        if self.events_df is None or self.events_df.empty:
            return pd.DataFrame()

        # Get players
        if team_id == self.home_team.get('teamId'):
            players_df = self.home_players_df
        else:
            players_df = self.away_players_df

        if players_df.empty:
            return pd.DataFrame()

        # Filter events for this team
        team_events = self.events_df[self.events_df['teamId'] == team_id].copy()

        # Filter for starting XI
        if starting_xi_only and 'isFirstEleven' in players_df.columns:
            starting_players = players_df[players_df['isFirstEleven'] == True]['playerId'].tolist()
            team_events = team_events[team_events['playerId'].isin(starting_players)]
            players_df = players_df[players_df['isFirstEleven'] == True]

        # Calculate average positions
        avg_positions = team_events.groupby('playerId').agg({
            'x': 'median',
            'y': 'median'
        }).reset_index()

        # Merge with player info
        result = avg_positions.merge(
            players_df[['playerId', 'name', 'shirtNo', 'position']],
            on='playerId',
            how='left'
        )

        return result

    def get_team_info(self) -> Dict[str, Any]:
        """
        Get team information.

        Returns:
            Dictionary with team information
        """
        info = {
            'home': {
                'id': self.home_team.get('teamId'),
                'name': self.home_team.get('name'),
                'score': self.match_centre_data.get('score', '').split(':')[0].strip() if ':' in self.match_centre_data.get('score', '') else '0'
            },
            'away': {
                'id': self.away_team.get('teamId'),
                'name': self.away_team.get('name'),
                'score': self.match_centre_data.get('score', '').split(':')[1].strip() if ':' in self.match_centre_data.get('score', '') else '0'
            },
            'venue': self.match_centre_data.get('venueName', ''),
            'date': self.match_centre_data.get('startDate', ''),
            'league': self.match_centre_data.get('competition', {}).get('name', ''),
        }

        # Add FotMob data if available
        if self.fotmob_data and self.fotmob_data.get('success'):
            info['xg'] = self.fotmob_data.get('xg', {})
            info['possession'] = self.fotmob_data.get('possession', {})
            info['team_colors'] = self.fotmob_data.get('team_colors', {})
            info['shots'] = self.fotmob_data.get('shots', {})
        else:
            # Default values
            info['xg'] = {'home_xg': 0.0, 'away_xg': 0.0}
            info['possession'] = {'home_possession': 50.0, 'away_possession': 50.0}
            info['team_colors'] = {'home_color': '#FF0000', 'away_color': '#0000FF'}
            info['shots'] = {'home_shots': 0, 'away_shots': 0}

        return info

    def save_processed_data(self, filename: str):
        """
        Save processed data to CSV files.

        Args:
            filename: Base filename (will create multiple files)
        """
        base = filename.replace('.csv', '')

        if self.events_df is not None:
            self.events_df.to_csv(f"{base}_events.csv", index=False)
            print(f"Events saved to: {base}_events.csv")

        if self.players_df is not None:
            self.players_df.to_csv(f"{base}_players.csv", index=False)
            print(f"Players saved to: {base}_players.csv")


def main():
    """Example usage."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python match_data_processor.py <whoscored_data.json> [fotmob_data.json]")
        return

    # Load WhoScored data
    with open(sys.argv[1], 'r') as f:
        whoscored_data = json.load(f)

    # Load FotMob data if provided
    fotmob_data = None
    if len(sys.argv) > 2:
        with open(sys.argv[2], 'r') as f:
            fotmob_data = json.load(f)

    # Process data
    processor = MatchDataProcessor(whoscored_data, fotmob_data)

    # Print summary
    team_info = processor.get_team_info()
    print("\n" + "=" * 60)
    print("MATCH DATA PROCESSING SUMMARY")
    print("=" * 60)
    print(f"\nMatch: {team_info['home']['name']} vs {team_info['away']['name']}")
    print(f"Score: {team_info['home']['score']} - {team_info['away']['score']}")

    if processor.events_df is not None:
        print(f"\nTotal Events: {len(processor.events_df)}")

        # Event breakdown
        event_counts = processor.events_df['type_display'].value_counts()
        print("\nTop Event Types:")
        for event_type, count in event_counts.head(10).items():
            print(f"  {event_type:20} - {count}")

    # Save processed data
    processor.save_processed_data("processed_match_data.csv")


if __name__ == "__main__":
    main()
