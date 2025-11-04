"""
Match Processor
Main processor that coordinates all data transformation.
"""

import pandas as pd
from typing import Dict, Any, Optional

from .event_processor import EventProcessor
from .player_processor import PlayerProcessor
from .team_processor import TeamProcessor


class MatchProcessor:
    """Main processor for complete match data."""

    def __init__(self, whoscored_data: Dict[str, Any], fotmob_data: Optional[Dict[str, Any]] = None):
        """
        Initialize with match data.

        Args:
            whoscored_data: Data from WhoScoredExtractor
            fotmob_data: Data from FotMobExtractor (optional)
        """
        self.whoscored_data = whoscored_data
        self.fotmob_data = fotmob_data

        # Extract match centre data
        match_centre = whoscored_data.get('match_centre', {})

        # Initialize sub-processors
        self.event_processor = None
        self.player_processor = None
        self.team_processor = None

        if match_centre.get('success'):
            # Events
            events_data = match_centre.get('events', {})
            self.event_processor = EventProcessor(events_data)

            # Players
            players_data = match_centre.get('players', {})
            self.player_processor = PlayerProcessor(
                players_data,
                self.event_processor.events_df if self.event_processor else None
            )

            # Teams
            home_team = match_centre.get('home_team', {})
            away_team = match_centre.get('away_team', {})
            self.team_processor = TeamProcessor(
                home_team,
                away_team,
                self.event_processor.events_df if self.event_processor else None
            )

            # Store basic info
            self.match_info = match_centre.get('match_info', {})
            self.home_team_data = home_team
            self.away_team_data = away_team

    def get_complete_match_summary(self) -> Dict[str, Any]:
        """Get complete match summary with all statistics."""
        summary = {
            'match_info': self.match_info,
            'success': self.whoscored_data.get('match_centre', {}).get('success', False)
        }

        if not summary['success']:
            return summary

        # Team information
        summary['teams'] = {
            'home': {
                'id': self.home_team_data.get('team_id'),
                'name': self.home_team_data.get('name'),
                'manager': self.home_team_data.get('manager'),
                'formation': self.home_team_data.get('formation')
            },
            'away': {
                'id': self.away_team_data.get('team_id'),
                'name': self.away_team_data.get('name'),
                'manager': self.away_team_data.get('manager'),
                'formation': self.away_team_data.get('formation')
            }
        }

        # Add FotMob data if available
        if self.fotmob_data and self.fotmob_data.get('success'):
            summary['xg'] = self.fotmob_data.get('xg', {})
            summary['team_colors'] = self.fotmob_data.get('team_colors', {})
            summary['fotmob_possession'] = self.fotmob_data.get('possession', {})
            summary['shots_data'] = self.fotmob_data.get('shots', {})
        else:
            summary['xg'] = {'home_xg': 0.0, 'away_xg': 0.0}
            summary['team_colors'] = {'home_color': '#FF0000', 'away_color': '#0000FF'}
            summary['fotmob_possession'] = None
            summary['shots_data'] = None

        # Calculate possession from events
        if self.team_processor:
            summary['possession'] = self.team_processor.calculate_possession()
        else:
            summary['possession'] = {'home': 50.0, 'away': 50.0}

        # Event statistics
        if self.event_processor:
            summary['event_stats'] = self.event_processor.get_event_statistics()
        else:
            summary['event_stats'] = {}

        # Team statistics
        if self.team_processor:
            summary['team_stats'] = self.team_processor.get_comprehensive_team_stats()
        else:
            summary['team_stats'] = {}

        return summary

    def get_events_dataframe(self) -> pd.DataFrame:
        """Get processed events DataFrame."""
        if self.event_processor and self.event_processor.events_df is not None:
            return self.event_processor.events_df
        return pd.DataFrame()

    def get_players_dataframe(self, team: str = 'all') -> pd.DataFrame:
        """
        Get players DataFrame.

        Args:
            team: 'all', 'home', or 'away'

        Returns:
            Players DataFrame
        """
        if not self.player_processor:
            return pd.DataFrame()

        if team == 'home':
            return self.player_processor.home_players_df if self.player_processor.home_players_df is not None else pd.DataFrame()
        elif team == 'away':
            return self.player_processor.away_players_df if self.player_processor.away_players_df is not None else pd.DataFrame()
        else:
            return self.player_processor.all_players_df if self.player_processor.all_players_df is not None else pd.DataFrame()

    def get_passes(self, team_id: Optional[int] = None, **kwargs) -> pd.DataFrame:
        """Get passes with filters."""
        if self.event_processor:
            return self.event_processor.get_passes(team_id, **kwargs)
        return pd.DataFrame()

    def get_shots(self, team_id: Optional[int] = None) -> pd.DataFrame:
        """Get shots."""
        if self.event_processor:
            return self.event_processor.get_shots(team_id)
        return pd.DataFrame()

    def get_defensive_actions(self, team_id: Optional[int] = None) -> pd.DataFrame:
        """Get defensive actions."""
        if self.event_processor:
            return self.event_processor.get_defensive_actions(team_id)
        return pd.DataFrame()

    def get_player_positions(self, team_id: int, starting_xi_only: bool = True) -> pd.DataFrame:
        """Get player average positions."""
        if self.player_processor:
            return self.player_processor.calculate_player_positions(team_id, starting_xi_only)
        return pd.DataFrame()

    def get_pass_connections(self, team_id: int, min_passes: int = 3) -> pd.DataFrame:
        """Get pass connections between players."""
        if self.player_processor:
            return self.player_processor.get_pass_connections(team_id, min_passes)
        return pd.DataFrame()

    def export_summary_to_dict(self) -> Dict[str, Any]:
        """Export complete summary as dictionary for reporting."""
        summary = self.get_complete_match_summary()

        # Add processor data
        summary['events_available'] = self.event_processor is not None
        summary['players_available'] = self.player_processor is not None
        summary['teams_available'] = self.team_processor is not None

        return summary
