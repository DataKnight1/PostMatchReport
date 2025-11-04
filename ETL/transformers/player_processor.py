"""
Player Processor
Transforms player data and calculates player-level statistics.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


class PlayerProcessor:
    """Process and transform player data."""

    def __init__(self, players_data: Dict[str, Any], events_df: Optional[pd.DataFrame] = None):
        """
        Initialize processor with player data.

        Args:
            players_data: Player data from WhoScored
            events_df: Events DataFrame for calculating stats
        """
        self.players_data = players_data
        self.events_df = events_df

        self.all_players_df = None
        self.home_players_df = None
        self.away_players_df = None

        if players_data and 'all_players' in players_data:
            self._create_player_dataframes()

    def _create_player_dataframes(self):
        """Create player DataFrames."""
        all_players = self.players_data.get('all_players', [])

        if all_players:
            self.all_players_df = pd.DataFrame(all_players)

            # Separate home and away
            self.home_players_df = pd.DataFrame(self.players_data.get('home_players', []))
            self.away_players_df = pd.DataFrame(self.players_data.get('away_players', []))

    def get_starting_xi(self, team_id: Optional[int] = None) -> pd.DataFrame:
        """Get starting XI players."""
        if self.all_players_df is None or self.all_players_df.empty:
            return pd.DataFrame()

        starting = self.all_players_df[self.all_players_df['is_first_eleven'] == True].copy()

        if team_id is not None:
            starting = starting[starting['team_id'] == team_id]

        return starting

    def get_substitutes(self, team_id: Optional[int] = None) -> pd.DataFrame:
        """Get substitute players."""
        if self.all_players_df is None or self.all_players_df.empty:
            return pd.DataFrame()

        subs = self.all_players_df[self.all_players_df['is_first_eleven'] == False].copy()

        if team_id is not None:
            subs = subs[subs['team_id'] == team_id]

        return subs

    def calculate_player_positions(self, team_id: int, starting_xi_only: bool = True) -> pd.DataFrame:
        """
        Calculate average player positions from events.

        Args:
            team_id: Team ID
            starting_xi_only: Only starting XI

        Returns:
            DataFrame with player positions
        """
        if self.events_df is None or self.events_df.empty:
            return pd.DataFrame()

        # Get players
        if starting_xi_only:
            players = self.get_starting_xi(team_id)
        else:
            players = self.all_players_df[self.all_players_df['team_id'] == team_id]

        if players.empty:
            return pd.DataFrame()

        # Filter events for this team
        team_events = self.events_df[self.events_df['teamId'] == team_id].copy()

        if starting_xi_only:
            player_ids = players['player_id'].tolist()
            team_events = team_events[team_events['playerId'].isin(player_ids)]

        # Calculate average positions
        positions = team_events.groupby('playerId').agg({
            'x': 'median',
            'y': 'median',
            'eventId': 'count'  # Count of events
        }).reset_index()

        positions.columns = ['player_id', 'avg_x', 'avg_y', 'event_count']

        # Merge with player info
        result = positions.merge(
            players[['player_id', 'name', 'shirt_no', 'position']],
            on='player_id',
            how='left'
        )

        return result

    def calculate_player_stats_from_events(self, player_id: int) -> Dict[str, Any]:
        """
        Calculate player statistics from events.

        Args:
            player_id: Player ID

        Returns:
            Dictionary of player statistics
        """
        if self.events_df is None or self.events_df.empty:
            return {}

        player_events = self.events_df[self.events_df['playerId'] == player_id]

        stats = {
            'total_events': len(player_events),
            'passes_attempted': len(player_events[player_events['type_display'] == 'Pass']),
            'passes_completed': len(player_events[
                (player_events['type_display'] == 'Pass') &
                (player_events['is_successful'] == True)
            ]),
            'shots': len(player_events[player_events['type_display'] == 'Shot']),
            'key_passes': len(player_events[player_events['is_key_pass'] == True]),
            'assists': len(player_events[player_events['is_assist'] == True]),
            'tackles': len(player_events[player_events['type_display'] == 'Tackle']),
            'interceptions': len(player_events[player_events['type_display'] == 'Interception']),
            'clearances': len(player_events[player_events['type_display'] == 'Clearance']),
            'total_xg': player_events['xg'].sum() if 'xg' in player_events.columns else 0
        }

        # Calculate pass completion percentage
        if stats['passes_attempted'] > 0:
            stats['pass_completion_pct'] = (stats['passes_completed'] / stats['passes_attempted']) * 100
        else:
            stats['pass_completion_pct'] = 0

        return stats

    def get_top_performers(self, metric: str = 'event_count', team_id: Optional[int] = None,
                          top_n: int = 5) -> pd.DataFrame:
        """
        Get top performing players by metric.

        Args:
            metric: Metric to rank by
            team_id: Filter by team
            top_n: Number of players to return

        Returns:
            DataFrame of top players
        """
        if self.all_players_df is None or self.all_players_df.empty:
            return pd.DataFrame()

        players = self.all_players_df.copy()

        if team_id is not None:
            players = players[players['team_id'] == team_id]

        # Calculate stats for each player if we have events
        if self.events_df is not None:
            player_stats = []
            for player_id in players['player_id']:
                stats = self.calculate_player_stats_from_events(player_id)
                stats['player_id'] = player_id
                player_stats.append(stats)

            stats_df = pd.DataFrame(player_stats)
            players = players.merge(stats_df, on='player_id', how='left')

        # Sort by metric
        if metric in players.columns:
            players = players.sort_values(metric, ascending=False).head(top_n)

        return players

    def get_pass_connections(self, team_id: int, min_passes: int = 3) -> pd.DataFrame:
        """
        Get pass connections between players.

        Args:
            team_id: Team ID
            min_passes: Minimum number of passes to include

        Returns:
            DataFrame with pass connections
        """
        if self.events_df is None or self.events_df.empty:
            return pd.DataFrame()

        # Get successful passes for team
        passes = self.events_df[
            (self.events_df['teamId'] == team_id) &
            (self.events_df['type_display'] == 'Pass') &
            (self.events_df['is_successful'] == True)
        ].copy()

        # Get starting XI
        starting = self.get_starting_xi(team_id)
        if starting.empty:
            return pd.DataFrame()

        starting_ids = starting['player_id'].tolist()

        # Identify receivers - the next player from same team who touches the ball
        passes['receiver'] = None
        for idx in passes.index:
            pass_row = passes.loc[idx]
            next_events = self.events_df[
                (self.events_df.index > idx) &
                (self.events_df['teamId'] == team_id) &
                (self.events_df['playerId'] != pass_row['playerId'])
            ]
            if len(next_events) > 0:
                passes.at[idx, 'receiver'] = next_events.iloc[0]['playerId']

        # Filter for starting XI only
        passes = passes[
            (passes['playerId'].isin(starting_ids)) &
            (passes['receiver'].isin(starting_ids))
        ]

        # Remove passes without receiver
        passes = passes[passes['receiver'].notna()]

        # Calculate pass counts both ways (pos_min, pos_max approach)
        passes_copy = passes[['playerId', 'receiver']].copy()
        passes_copy['pos_min'] = passes_copy[['playerId', 'receiver']].min(axis=1)
        passes_copy['pos_max'] = passes_copy[['playerId', 'receiver']].max(axis=1)

        # Aggregate passes between each pair
        connections = passes_copy.groupby(['pos_min', 'pos_max']).size().reset_index(name='pass_count')

        # Filter by minimum passes
        connections = connections[connections['pass_count'] >= min_passes]

        return connections

    def get_pass_network_data(self, team_id: int, min_passes: int = 3) -> tuple:
        """
        Get complete pass network data including positions and connections.

        Args:
            team_id: Team ID
            min_passes: Minimum passes to show connection

        Returns:
            Tuple of (average_positions_df, pass_connections_df)
        """
        if self.events_df is None or self.events_df.empty:
            return pd.DataFrame(), pd.DataFrame()

        # Get successful passes for team
        passes = self.events_df[
            (self.events_df['teamId'] == team_id) &
            (self.events_df['type_display'] == 'Pass') &
            (self.events_df['is_successful'] == True)
        ].copy()

        # Get starting XI
        starting = self.get_starting_xi(team_id)
        if starting.empty:
            return pd.DataFrame(), pd.DataFrame()

        starting_ids = starting['player_id'].tolist()

        # Filter for starting XI
        passes = passes[passes['playerId'].isin(starting_ids)]

        # Calculate average positions from pass locations
        avg_positions = passes.groupby('playerId').agg({
            'x': 'mean',
            'y': 'mean',
            'eventId': 'count'
        }).reset_index()
        avg_positions.columns = ['playerId', 'x', 'y', 'count']

        # Merge with player info
        avg_positions = avg_positions.merge(
            starting[['player_id', 'name', 'shirt_no', 'position']],
            left_on='playerId',
            right_on='player_id',
            how='left'
        )

        # Identify receivers
        passes['receiver'] = None
        for idx in passes.index:
            pass_row = passes.loc[idx]
            next_events = self.events_df[
                (self.events_df.index > idx) &
                (self.events_df['teamId'] == team_id) &
                (self.events_df['playerId'] != pass_row['playerId'])
            ]
            if len(next_events) > 0:
                passes.at[idx, 'receiver'] = next_events.iloc[0]['playerId']

        # Filter for starting XI receivers
        passes = passes[passes['receiver'].isin(starting_ids)]
        passes = passes[passes['receiver'].notna()]

        # Calculate pass counts using pos_min/pos_max
        passes_copy = passes[['playerId', 'receiver']].copy()
        passes_copy['pos_min'] = passes_copy[['playerId', 'receiver']].min(axis=1)
        passes_copy['pos_max'] = passes_copy[['playerId', 'receiver']].max(axis=1)

        # Aggregate
        connections = passes_copy.groupby(['pos_min', 'pos_max']).size().reset_index(name='pass_count')

        # Add position data for both players
        connections = connections.merge(
            avg_positions[['playerId', 'x', 'y']],
            left_on='pos_min',
            right_on='playerId',
            how='left'
        ).drop('playerId', axis=1)

        connections = connections.merge(
            avg_positions[['playerId', 'x', 'y']],
            left_on='pos_max',
            right_on='playerId',
            how='left',
            suffixes=['', '_end']
        ).drop('playerId', axis=1)

        # Filter by minimum passes
        connections = connections[connections['pass_count'] >= min_passes]

        return avg_positions, connections
