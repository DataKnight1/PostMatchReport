"""
Event Processor
Transforms raw event data into structured formats for analysis and visualization.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple


class EventProcessor:
    """Process and transform match events data."""

    def __init__(self, events_data: Dict[str, Any]):
        """
        Initialize processor with events data.

        Args:
            events_data: Events data from WhoScored
        """
        self.events_data = events_data
        self.events_df = None

        if events_data and 'all_events' in events_data:
            self.events_df = self._create_events_dataframe(events_data['all_events'])

    def _create_events_dataframe(self, events: List[Dict]) -> pd.DataFrame:
        """
        Create comprehensive events DataFrame.

        Args:
            events: List of event dictionaries

        Returns:
            DataFrame with all events
        """
        if not events:
            return pd.DataFrame()

        df = pd.DataFrame(events)

        # Scale coordinates to standard pitch (105m x 68m)
        if 'x' in df.columns:
            df['x'] = df['x'] * 1.05
        if 'y' in df.columns:
            df['y'] = df['y'] * 0.68
        if 'endX' in df.columns:
            df['endX'] = df['endX'] * 1.05
        if 'endY' in df.columns:
            df['endY'] = df['endY'] * 0.68

        # Extract nested fields
        if 'type' in df.columns:
            df['type_display'] = df['type'].apply(
                lambda x: x.get('displayName', '') if isinstance(x, dict) else ''
            )
            df['type_value'] = df['type'].apply(
                lambda x: x.get('value', 0) if isinstance(x, dict) else 0
            )

        if 'outcomeType' in df.columns:
            df['outcome_display'] = df['outcomeType'].apply(
                lambda x: x.get('displayName', '') if isinstance(x, dict) else ''
            )
            df['is_successful'] = df['outcome_display'] == 'Successful'

        if 'period' in df.columns:
            df['period_display'] = df['period'].apply(
                lambda x: x.get('displayName', '') if isinstance(x, dict) else ''
            )
            df['period_value'] = df['period'].apply(
                lambda x: x.get('value', 1) if isinstance(x, dict) else 1
            )

        # Calculate cumulative minutes
        df['cumulative_mins'] = self._calculate_cumulative_minutes(df)

        # Process qualifiers
        df['qualifiers_dict'] = df['qualifiers'].apply(self._process_qualifiers)

        # Extract common qualifiers
        df['is_key_pass'] = df['qualifiers_dict'].apply(
            lambda x: 'KeyPass' in x if isinstance(x, dict) else False
        )
        df['is_assist'] = df['qualifiers_dict'].apply(
            lambda x: 'Assist' in x if isinstance(x, dict) else False
        )
        df['is_goal'] = df['qualifiers_dict'].apply(
            lambda x: 'Goal' in x if isinstance(x, dict) else False
        )
        df['is_own_goal'] = df['qualifiers_dict'].apply(
            lambda x: 'OwnGoal' in x if isinstance(x, dict) else False
        )

        # Extract xG if available
        df['xg'] = df['qualifiers_dict'].apply(
            lambda x: float(x.get('xG', 0)) if isinstance(x, dict) and 'xG' in x else 0.0
        )

        # Calculate pass/carry distance and angle
        df = self._add_spatial_metrics(df)

        return df

    def _process_qualifiers(self, qualifiers) -> Dict[str, Any]:
        """Process qualifiers into dictionary."""
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
        """Calculate cumulative match minutes."""
        if 'minute' not in df.columns or 'second' not in df.columns:
            return pd.Series([0] * len(df))

        cumulative_mins = []
        for _, row in df.iterrows():
            period_value = row.get('period_value', 1)
            minute = row.get('minute', 0)
            second = row.get('second', 0)

            # Calculate base minutes for each period
            base_map = {1: 0, 2: 45, 3: 90, 4: 105, 5: 120}
            base = base_map.get(period_value, 0)

            total = base + minute + (second / 60.0)
            cumulative_mins.append(total)

        return pd.Series(cumulative_mins)

    def _add_spatial_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add spatial metrics like distance, angle, etc."""
        # Distance
        df['distance'] = np.sqrt(
            (df['endX'] - df['x'])**2 + (df['endY'] - df['y'])**2
        )

        # Angle (in radians)
        df['angle'] = np.arctan2(df['endY'] - df['y'], df['endX'] - df['x'])

        # Progressive (moving ball forward)
        df['is_progressive'] = (df['endX'] - df['x']) > 10  # More than 10m forward

        # Distance to goal (assuming attacking to the right)
        df['dist_to_goal'] = np.sqrt((105 - df['x'])**2 + (34 - df['y'])**2)
        df['end_dist_to_goal'] = np.sqrt((105 - df['endX'])**2 + (34 - df['endY'])**2)

        return df

    def get_passes(self, team_id: Optional[int] = None, successful_only: bool = False,
                  progressive_only: bool = False) -> pd.DataFrame:
        """
        Get pass events with filters.

        Args:
            team_id: Filter by team ID
            successful_only: Only successful passes
            progressive_only: Only progressive passes

        Returns:
            Filtered passes DataFrame
        """
        if self.events_df is None or self.events_df.empty:
            return pd.DataFrame()

        passes = self.events_df[self.events_df['type_display'] == 'Pass'].copy()

        if team_id is not None:
            passes = passes[passes['teamId'] == team_id]

        if successful_only:
            passes = passes[passes['is_successful'] == True]

        if progressive_only:
            passes = passes[passes['is_progressive'] == True]

        # Identify receiver
        passes = self._identify_receivers(passes)

        return passes

    def _identify_receivers(self, passes: pd.DataFrame) -> pd.DataFrame:
        """Identify pass receivers."""
        if passes.empty:
            return passes

        passes['receiver'] = None

        for idx in passes.index:
            pass_row = passes.loc[idx]
            next_events = self.events_df[
                (self.events_df.index > idx) &
                (self.events_df['teamId'] == pass_row['teamId']) &
                (self.events_df['type_display'].isin(['Pass', 'TakeOn', 'Shot', 'Carry']))
            ]
            if len(next_events) > 0:
                passes.at[idx, 'receiver'] = next_events.iloc[0]['playerId']

        return passes

    def get_shots(self, team_id: Optional[int] = None) -> pd.DataFrame:
        """Get shot events."""
        if self.events_df is None or self.events_df.empty:
            return pd.DataFrame()

        shots = self.events_df[self.events_df['type_display'] == 'Shot'].copy()

        if team_id is not None:
            shots = shots[shots['teamId'] == team_id]

        return shots

    def get_defensive_actions(self, team_id: Optional[int] = None) -> pd.DataFrame:
        """Get defensive actions."""
        if self.events_df is None or self.events_df.empty:
            return pd.DataFrame()

        defensive_types = ['Tackle', 'Interception', 'Clearance', 'BlockedPass', 'Challenge']
        actions = self.events_df[self.events_df['type_display'].isin(defensive_types)].copy()

        if team_id is not None:
            actions = actions[actions['teamId'] == team_id]

        return actions

    def get_carries(self, team_id: Optional[int] = None) -> pd.DataFrame:
        """Get carry/dribble events."""
        if self.events_df is None or self.events_df.empty:
            return pd.DataFrame()

        carries = self.events_df[self.events_df['type_display'].isin(['Carry', 'TakeOn'])].copy()

        if team_id is not None:
            carries = carries[carries['teamId'] == team_id]

        return carries

    def get_key_moments(self) -> pd.DataFrame:
        """Get key match moments (goals, cards, substitutions)."""
        if self.events_df is None or self.events_df.empty:
            return pd.DataFrame()

        key_types = ['Goal', 'SubstitutionOn', 'SubstitutionOff', 'Card']
        moments = self.events_df[self.events_df['type_display'].isin(key_types)].copy()

        return moments.sort_values('cumulative_mins')

    def get_events_by_zone(self, zone: str, team_id: Optional[int] = None) -> pd.DataFrame:
        """
        Get events in specific pitch zones.

        Args:
            zone: 'defensive_third', 'middle_third', 'attacking_third',
                  'zone14', 'left_half_space', 'right_half_space'
            team_id: Filter by team ID

        Returns:
            Filtered events
        """
        if self.events_df is None or self.events_df.empty:
            return pd.DataFrame()

        df = self.events_df.copy()

        if team_id is not None:
            df = df[df['teamId'] == team_id]

        # Define zones
        if zone == 'defensive_third':
            df = df[df['x'] <= 35]
        elif zone == 'middle_third':
            df = df[(df['x'] > 35) & (df['x'] <= 70)]
        elif zone == 'attacking_third':
            df = df[df['x'] > 70]
        elif zone == 'zone14':
            df = df[(df['x'] >= 70) & (df['x'] <= 87.5) & (df['y'] >= 20.4) & (df['y'] <= 47.6)]
        elif zone == 'left_half_space':
            df = df[(df['x'] >= 70) & (df['x'] <= 87.5) & (df['y'] >= 10.2) & (df['y'] <= 27.2)]
        elif zone == 'right_half_space':
            df = df[(df['x'] >= 70) & (df['x'] <= 87.5) & (df['y'] >= 40.8) & (df['y'] <= 57.8)]
        elif zone == 'penalty_box':
            df = df[(df['x'] >= 88.5) & (df['y'] >= 13.8) & (df['y'] <= 54.2)]

        return df

    def get_event_statistics(self) -> Dict[str, Any]:
        """Get comprehensive event statistics."""
        if self.events_df is None or self.events_df.empty:
            return {}

        stats = {
            'total_events': len(self.events_df),
            'by_type': self.events_df['type_display'].value_counts().to_dict(),
            'by_period': self.events_df['period_display'].value_counts().to_dict(),
            'by_team': self.events_df.groupby('teamId').size().to_dict(),
            'successful_events': len(self.events_df[self.events_df['is_successful'] == True]),
            'key_passes': len(self.events_df[self.events_df['is_key_pass'] == True]),
            'assists': len(self.events_df[self.events_df['is_assist'] == True]),
            'goals': len(self.events_df[self.events_df['is_goal'] == True]),
            'total_xg': self.events_df['xg'].sum(),
        }

        return stats

    def create_pass_network_data(self, team_id: int, starting_xi_only: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Create pass network data for visualization.

        Args:
            team_id: Team ID
            starting_xi_only: Only include starting XI

        Returns:
            Tuple of (player_positions, pass_connections)
        """
        # This will be implemented with player data
        # For now, return empty DataFrames
        return pd.DataFrame(), pd.DataFrame()
