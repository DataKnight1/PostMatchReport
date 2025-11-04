"""
Team Processor
Transforms team-level data and calculates team statistics.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


class TeamProcessor:
    """Process and transform team data."""

    def __init__(self, home_team: Dict[str, Any], away_team: Dict[str, Any],
                 events_df: Optional[pd.DataFrame] = None):
        """
        Initialize processor with team data.

        Args:
            home_team: Home team data
            away_team: Away team data
            events_df: Events DataFrame for calculating stats
        """
        self.home_team = home_team
        self.away_team = away_team
        self.events_df = events_df

    def get_team_basic_info(self, team_type: str = 'both') -> Dict[str, Any]:
        """
        Get basic team information.

        Args:
            team_type: 'home', 'away', or 'both'

        Returns:
            Team information
        """
        if team_type == 'home':
            return {
                'id': self.home_team.get('team_id'),
                'name': self.home_team.get('name'),
                'manager': self.home_team.get('manager'),
                'formation': self.home_team.get('formation'),
                'country': self.home_team.get('country_name')
            }
        elif team_type == 'away':
            return {
                'id': self.away_team.get('team_id'),
                'name': self.away_team.get('name'),
                'manager': self.away_team.get('manager'),
                'formation': self.away_team.get('formation'),
                'country': self.away_team.get('country_name')
            }
        else:
            return {
                'home': self.get_team_basic_info('home'),
                'away': self.get_team_basic_info('away')
            }

    def calculate_possession(self) -> Dict[str, float]:
        """Calculate possession percentages from events."""
        if self.events_df is None or self.events_df.empty:
            return {'home': 50.0, 'away': 50.0}

        home_id = self.home_team.get('team_id')
        away_id = self.away_team.get('team_id')

        home_events = len(self.events_df[self.events_df['teamId'] == home_id])
        away_events = len(self.events_df[self.events_df['teamId'] == away_id])

        total = home_events + away_events

        if total == 0:
            return {'home': 50.0, 'away': 50.0}

        return {
            'home': (home_events / total) * 100,
            'away': (away_events / total) * 100
        }

    def calculate_passing_stats(self, team_id: int) -> Dict[str, Any]:
        """Calculate passing statistics for a team."""
        if self.events_df is None or self.events_df.empty:
            return {}

        passes = self.events_df[
            (self.events_df['teamId'] == team_id) &
            (self.events_df['type_display'] == 'Pass')
        ]

        if passes.empty:
            return {
                'total_passes': 0,
                'completed_passes': 0,
                'pass_accuracy': 0,
                'forward_passes': 0,
                'backward_passes': 0,
                'short_passes': 0,
                'long_passes': 0,
                'key_passes': 0,
                'assists': 0
            }

        completed = passes[passes['is_successful'] == True]

        return {
            'total_passes': len(passes),
            'completed_passes': len(completed),
            'pass_accuracy': (len(completed) / len(passes) * 100) if len(passes) > 0 else 0,
            'forward_passes': len(passes[passes['distance'] > 0]),
            'progressive_passes': len(passes[passes['is_progressive'] == True]),
            'short_passes': len(passes[passes['distance'] < 15]),
            'long_passes': len(passes[passes['distance'] >= 25]),
            'key_passes': len(passes[passes['is_key_pass'] == True]),
            'assists': len(passes[passes['is_assist'] == True]),
            'avg_pass_length': passes['distance'].mean() if 'distance' in passes.columns else 0
        }

    def calculate_shooting_stats(self, team_id: int) -> Dict[str, Any]:
        """Calculate shooting statistics for a team."""
        if self.events_df is None or self.events_df.empty:
            return {}

        shots = self.events_df[
            (self.events_df['teamId'] == team_id) &
            (self.events_df['type_display'] == 'Shot')
        ]

        if shots.empty:
            return {
                'total_shots': 0,
                'shots_on_target': 0,
                'goals': 0,
                'xg': 0,
                'shot_accuracy': 0
            }

        on_target = shots[shots['is_successful'] == True]
        goals = shots[shots['is_goal'] == True]

        return {
            'total_shots': len(shots),
            'shots_on_target': len(on_target),
            'goals': len(goals),
            'xg': shots['xg'].sum() if 'xg' in shots.columns else 0,
            'shot_accuracy': (len(on_target) / len(shots) * 100) if len(shots) > 0 else 0,
            'shots_inside_box': len(shots[shots['x'] >= 88.5]),
            'shots_outside_box': len(shots[shots['x'] < 88.5])
        }

    def calculate_defensive_stats(self, team_id: int) -> Dict[str, Any]:
        """Calculate defensive statistics for a team."""
        if self.events_df is None or self.events_df.empty:
            return {}

        defensive_types = ['Tackle', 'Interception', 'Clearance', 'BlockedPass']
        actions = self.events_df[
            (self.events_df['teamId'] == team_id) &
            (self.events_df['type_display'].isin(defensive_types))
        ]

        return {
            'total_defensive_actions': len(actions),
            'tackles': len(actions[actions['type_display'] == 'Tackle']),
            'interceptions': len(actions[actions['type_display'] == 'Interception']),
            'clearances': len(actions[actions['type_display'] == 'Clearance']),
            'blocked_passes': len(actions[actions['type_display'] == 'BlockedPass']),
            'successful_defensive_actions': len(actions[actions['is_successful'] == True])
        }

    def calculate_territorial_stats(self, team_id: int) -> Dict[str, Any]:
        """Calculate territorial statistics."""
        if self.events_df is None or self.events_df.empty:
            return {}

        team_events = self.events_df[self.events_df['teamId'] == team_id]

        if team_events.empty:
            return {}

        # Events by third
        defensive_third = team_events[team_events['x'] <= 35]
        middle_third = team_events[(team_events['x'] > 35) & (team_events['x'] <= 70)]
        attacking_third = team_events[team_events['x'] > 70]

        total = len(team_events)

        return {
            'defensive_third_events': len(defensive_third),
            'middle_third_events': len(middle_third),
            'attacking_third_events': len(attacking_third),
            'defensive_third_pct': (len(defensive_third) / total * 100) if total > 0 else 0,
            'middle_third_pct': (len(middle_third) / total * 100) if total > 0 else 0,
            'attacking_third_pct': (len(attacking_third) / total * 100) if total > 0 else 0,
            'avg_event_x': team_events['x'].mean(),
            'avg_event_y': team_events['y'].mean()
        }

    def get_comprehensive_team_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get all statistics for both teams."""
        home_id = self.home_team.get('team_id')
        away_id = self.away_team.get('team_id')

        return {
            'home': {
                'info': self.get_team_basic_info('home'),
                'passing': self.calculate_passing_stats(home_id),
                'shooting': self.calculate_shooting_stats(home_id),
                'defensive': self.calculate_defensive_stats(home_id),
                'territorial': self.calculate_territorial_stats(home_id)
            },
            'away': {
                'info': self.get_team_basic_info('away'),
                'passing': self.calculate_passing_stats(away_id),
                'shooting': self.calculate_shooting_stats(away_id),
                'defensive': self.calculate_defensive_stats(away_id),
                'territorial': self.calculate_territorial_stats(away_id)
            },
            'possession': self.calculate_possession()
        }

    def compare_teams(self) -> pd.DataFrame:
        """Create comparison DataFrame between teams."""
        stats = self.get_comprehensive_team_stats()

        comparison_data = []

        # Passing stats
        for key in stats['home']['passing'].keys():
            comparison_data.append({
                'category': 'Passing',
                'stat': key,
                'home': stats['home']['passing'][key],
                'away': stats['away']['passing'][key]
            })

        # Shooting stats
        for key in stats['home']['shooting'].keys():
            comparison_data.append({
                'category': 'Shooting',
                'stat': key,
                'home': stats['home']['shooting'][key],
                'away': stats['away']['shooting'][key]
            })

        # Defensive stats
        for key in stats['home']['defensive'].keys():
            comparison_data.append({
                'category': 'Defensive',
                'stat': key,
                'home': stats['home']['defensive'][key],
                'away': stats['away']['defensive'][key]
            })

        return pd.DataFrame(comparison_data)
