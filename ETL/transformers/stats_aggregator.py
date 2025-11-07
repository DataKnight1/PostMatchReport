"""
Statistics Aggregator
Aggregates event data into summary statistics matching WhoScored interface.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


class StatsAggregator:
    """
    Aggregate match events into comprehensive statistics.
    Matches the statistics shown on WhoScored match summary interface.
    """

    def __init__(self, events_df: pd.DataFrame, home_id: int, away_id: int):
        """
        Initialize aggregator.

        Args:
            events_df: Events DataFrame from EventProcessor
            home_id: Home team ID
            away_id: Away team ID
        """
        self.events_df = events_df
        self.home_id = home_id
        self.away_id = away_id

    def aggregate_all_stats(self) -> Dict[str, Any]:
        """
        Aggregate all statistics for both teams.

        Returns:
            Dictionary with home and away stats matching WhoScored interface
        """
        stats = {
            'home': self.aggregate_team_stats(self.home_id),
            'away': self.aggregate_team_stats(self.away_id),
            'comparison': {}
        }

        # Add comparison
        for key in stats['home'].keys():
            if key in stats['away']:
                stats['comparison'][key] = {
                    'home': stats['home'][key],
                    'away': stats['away'][key]
                }

        return stats

    def aggregate_team_stats(self, team_id: int) -> Dict[str, Any]:
        """
        Aggregate statistics for a single team.

        Args:
            team_id: Team ID

        Returns:
            Statistics dictionary
        """
        team_events = self.events_df[self.events_df['teamId'] == team_id]

        return {
            # Shots
            'shots': self._count_shots(team_events),
            'shots_on_target': self._count_shots_on_target(team_events),
            'shots_off_target': self._count_shots_off_target(team_events),
            'blocked_shots': self._count_blocked_shots(team_events),
            'goals': self._count_goals(team_events),

            # Passing
            'passes': self._count_passes(team_events),
            'passes_completed': self._count_passes_completed(team_events),
            'pass_accuracy': self._calculate_pass_accuracy(team_events),

            # Possession
            'touches': self._count_touches(team_events),

            # Defensive
            'tackles': self._count_tackles(team_events),
            'interceptions': self._count_interceptions(team_events),
            'clearances': self._count_clearances(team_events),
            'blocks': self._count_blocks(team_events),

            # Dribbles
            'dribbles': self._count_dribbles(team_events),
            'dribbles_successful': self._count_successful_dribbles(team_events),

            # Discipline
            'fouls': self._count_fouls(team_events),
            'yellow_cards': self._count_yellow_cards(team_events),
            'red_cards': self._count_red_cards(team_events),
            'offsides': self._count_offsides(team_events),

            # Aerials
            'aerial_duels': self._count_aerial_duels(team_events),
            'aerial_duels_won': self._count_aerial_duels_won(team_events),

            # Saves (goalkeeper)
            'saves': self._count_saves(team_events),

            # Errors
            'errors_leading_to_shot': self._count_errors_leading_to_shot(team_events),
            'errors_leading_to_goal': self._count_errors_leading_to_goal(team_events),

            # Lost possession
            'dispossessed': self._count_dispossessed(team_events),
            'bad_touches': self._count_bad_touches(team_events),

            # xG
            'xg': self._calculate_xg(team_events),

            # Shot breakdown by zone
            'penalty_area_shots': self._count_penalty_area_shots(team_events),
            'six_yard_box_shots': self._count_six_yard_box_shots(team_events),
            'outside_box_shots': self._count_outside_box_shots(team_events),

            # Shot breakdown by body part
            'right_foot_shots': self._count_right_foot_shots(team_events),
            'left_foot_shots': self._count_left_foot_shots(team_events),
            'headed_shots': self._count_headed_shots(team_events),

            # Shot breakdown by situation
            'open_play_shots': self._count_open_play_shots(team_events),
            'set_piece_shots': self._count_set_piece_shots(team_events),
            'counter_attack_shots': self._count_counter_attack_shots(team_events),
        }

    # Shot statistics
    def _count_shots(self, events: pd.DataFrame) -> int:
        """Count total shots."""
        shot_types = ['Shot', 'MissedShots', 'SavedShot', 'ShotOnPost', 'Goal']
        return len(events[events['type_display'].isin(shot_types)])

    def _count_shots_on_target(self, events: pd.DataFrame) -> int:
        """Count shots on target."""
        shot_types = ['SavedShot', 'Goal']
        return len(events[events['type_display'].isin(shot_types)])

    def _count_shots_off_target(self, events: pd.DataFrame) -> int:
        """Count shots off target."""
        return len(events[events['type_display'] == 'MissedShots'])

    def _count_blocked_shots(self, events: pd.DataFrame) -> int:
        """Count blocked shots."""
        return len(events[events['type_display'] == 'BlockedPass'])

    def _count_goals(self, events: pd.DataFrame) -> int:
        """Count goals."""
        goals = len(events[events['type_display'] == 'Goal'])
        # Subtract own goals
        own_goals = len(events[(events['type_display'] == 'Goal') & (events['is_own_goal'] == True)])
        return goals - own_goals

    # Passing statistics
    def _count_passes(self, events: pd.DataFrame) -> int:
        """Count total passes."""
        return len(events[events['type_display'] == 'Pass'])

    def _count_passes_completed(self, events: pd.DataFrame) -> int:
        """Count completed passes."""
        return len(events[(events['type_display'] == 'Pass') & (events['is_successful'] == True)])

    def _calculate_pass_accuracy(self, events: pd.DataFrame) -> float:
        """Calculate pass accuracy percentage."""
        total = self._count_passes(events)
        if total == 0:
            return 0.0
        completed = self._count_passes_completed(events)
        return round((completed / total) * 100, 1)

    # Possession statistics
    def _count_touches(self, events: pd.DataFrame) -> int:
        """Count total touches (all events)."""
        return len(events)

    # Defensive statistics
    def _count_tackles(self, events: pd.DataFrame) -> int:
        """Count tackle attempts."""
        return len(events[events['type_display'] == 'Tackle'])

    def _count_interceptions(self, events: pd.DataFrame) -> int:
        """Count interceptions."""
        return len(events[events['type_display'] == 'Interception'])

    def _count_clearances(self, events: pd.DataFrame) -> int:
        """Count clearances."""
        return len(events[events['type_display'] == 'Clearance'])

    def _count_blocks(self, events: pd.DataFrame) -> int:
        """Count blocked shots/passes."""
        return len(events[events['type_display'].isin(['BlockedPass', 'Block'])])

    # Dribbles
    def _count_dribbles(self, events: pd.DataFrame) -> int:
        """Count dribble attempts."""
        return len(events[events['type_display'] == 'TakeOn'])

    def _count_successful_dribbles(self, events: pd.DataFrame) -> int:
        """Count successful dribbles."""
        return len(events[(events['type_display'] == 'TakeOn') & (events['is_successful'] == True)])

    # Discipline
    def _count_fouls(self, events: pd.DataFrame) -> int:
        """Count fouls committed."""
        return len(events[events['type_display'] == 'Foul'])

    def _count_yellow_cards(self, events: pd.DataFrame) -> int:
        """Count yellow cards."""
        if 'qualifiers_dict' not in events.columns:
            return 0
        yellow = 0
        for qualifiers in events['qualifiers_dict']:
            if isinstance(qualifiers, dict) and 'YellowCard' in qualifiers:
                yellow += 1
        return yellow

    def _count_red_cards(self, events: pd.DataFrame) -> int:
        """Count red cards."""
        if 'qualifiers_dict' not in events.columns:
            return 0
        red = 0
        for qualifiers in events['qualifiers_dict']:
            if isinstance(qualifiers, dict) and 'RedCard' in qualifiers:
                red += 1
        return red

    def _count_offsides(self, events: pd.DataFrame) -> int:
        """Count offsides."""
        return len(events[events['type_display'] == 'OffsidePass'])

    # Aerials
    def _count_aerial_duels(self, events: pd.DataFrame) -> int:
        """Count aerial duel attempts."""
        return len(events[events['type_display'] == 'Aerial'])

    def _count_aerial_duels_won(self, events: pd.DataFrame) -> int:
        """Count aerial duels won."""
        return len(events[(events['type_display'] == 'Aerial') & (events['is_successful'] == True)])

    # Goalkeeping
    def _count_saves(self, events: pd.DataFrame) -> int:
        """Count goalkeeper saves."""
        return len(events[events['type_display'] == 'Save'])

    # Errors
    def _count_errors_leading_to_shot(self, events: pd.DataFrame) -> int:
        """Count errors leading to opposition shot."""
        return len(events[events['type_display'] == 'Error'])

    def _count_errors_leading_to_goal(self, events: pd.DataFrame) -> int:
        """Count errors leading to opposition goal."""
        if 'qualifiers_dict' not in events.columns:
            return 0
        errors = 0
        for qualifiers in events['qualifiers_dict']:
            if isinstance(qualifiers, dict) and 'LeadToGoal' in qualifiers:
                errors += 1
        return errors

    # Lost possession
    def _count_dispossessed(self, events: pd.DataFrame) -> int:
        """Count times dispossessed."""
        return len(events[events['type_display'] == 'Dispossessed'])

    def _count_bad_touches(self, events: pd.DataFrame) -> int:
        """Count bad touches."""
        if 'qualifiers_dict' not in events.columns:
            return 0
        bad = 0
        for qualifiers in events['qualifiers_dict']:
            if isinstance(qualifiers, dict) and 'BadTouch' in qualifiers:
                bad += 1
        return bad

    # xG
    def _calculate_xg(self, events: pd.DataFrame) -> float:
        """Calculate total expected goals."""
        if 'xg' not in events.columns:
            return 0.0
        return round(events['xg'].sum(), 2)

    # Shot breakdown by zone
    def _count_penalty_area_shots(self, events: pd.DataFrame) -> int:
        """Count shots from penalty area."""
        shot_types = ['Shot', 'MissedShots', 'SavedShot', 'ShotOnPost', 'Goal']
        shots = events[events['type_display'].isin(shot_types)]
        # Penalty area: x >= 88.5, y between 13.8 and 54.2
        return len(shots[(shots['x'] >= 88.5) & (shots['y'] >= 13.8) & (shots['y'] <= 54.2)])

    def _count_six_yard_box_shots(self, events: pd.DataFrame) -> int:
        """Count shots from six yard box."""
        shot_types = ['Shot', 'MissedShots', 'SavedShot', 'ShotOnPost', 'Goal']
        shots = events[events['type_display'].isin(shot_types)]
        # Six yard box: x >= 99.5, y between 24.8 and 43.2
        return len(shots[(shots['x'] >= 99.5) & (shots['y'] >= 24.8) & (shots['y'] <= 43.2)])

    def _count_outside_box_shots(self, events: pd.DataFrame) -> int:
        """Count shots from outside the box."""
        shot_types = ['Shot', 'MissedShots', 'SavedShot', 'ShotOnPost', 'Goal']
        shots = events[events['type_display'].isin(shot_types)]
        return len(shots[shots['x'] < 88.5])

    # Shot breakdown by body part
    def _count_right_foot_shots(self, events: pd.DataFrame) -> int:
        """Count right foot shots."""
        if 'qualifiers_dict' not in events.columns:
            return 0
        shot_types = ['Shot', 'MissedShots', 'SavedShot', 'ShotOnPost', 'Goal']
        shots = events[events['type_display'].isin(shot_types)]
        count = 0
        for qualifiers in shots['qualifiers_dict']:
            if isinstance(qualifiers, dict) and 'RightFoot' in qualifiers:
                count += 1
        return count

    def _count_left_foot_shots(self, events: pd.DataFrame) -> int:
        """Count left foot shots."""
        if 'qualifiers_dict' not in events.columns:
            return 0
        shot_types = ['Shot', 'MissedShots', 'SavedShot', 'ShotOnPost', 'Goal']
        shots = events[events['type_display'].isin(shot_types)]
        count = 0
        for qualifiers in shots['qualifiers_dict']:
            if isinstance(qualifiers, dict) and 'LeftFoot' in qualifiers:
                count += 1
        return count

    def _count_headed_shots(self, events: pd.DataFrame) -> int:
        """Count headed shots."""
        if 'qualifiers_dict' not in events.columns:
            return 0
        shot_types = ['Shot', 'MissedShots', 'SavedShot', 'ShotOnPost', 'Goal']
        shots = events[events['type_display'].isin(shot_types)]
        count = 0
        for qualifiers in shots['qualifiers_dict']:
            if isinstance(qualifiers, dict) and 'Head' in qualifiers:
                count += 1
        return count

    # Shot breakdown by situation
    def _count_open_play_shots(self, events: pd.DataFrame) -> int:
        """Count shots from open play."""
        if 'qualifiers_dict' not in events.columns:
            return self._count_shots(events)  # Default to all shots

        shot_types = ['Shot', 'MissedShots', 'SavedShot', 'ShotOnPost', 'Goal']
        shots = events[events['type_display'].isin(shot_types)]
        count = 0
        for qualifiers in shots['qualifiers_dict']:
            if isinstance(qualifiers, dict):
                # Open play if not from set piece
                if not any(k in qualifiers for k in ['FreeKick', 'Corner', 'ThrowIn', 'Penalty']):
                    count += 1
        return count

    def _count_set_piece_shots(self, events: pd.DataFrame) -> int:
        """Count shots from set pieces."""
        if 'qualifiers_dict' not in events.columns:
            return 0

        shot_types = ['Shot', 'MissedShots', 'SavedShot', 'ShotOnPost', 'Goal']
        shots = events[events['type_display'].isin(shot_types)]
        count = 0
        for qualifiers in shots['qualifiers_dict']:
            if isinstance(qualifiers, dict):
                if any(k in qualifiers for k in ['FreeKick', 'Corner', 'ThrowIn', 'Penalty']):
                    count += 1
        return count

    def _count_counter_attack_shots(self, events: pd.DataFrame) -> int:
        """Count shots from counter attacks."""
        if 'qualifiers_dict' not in events.columns:
            return 0

        shot_types = ['Shot', 'MissedShots', 'SavedShot', 'ShotOnPost', 'Goal']
        shots = events[events['type_display'].isin(shot_types)]
        count = 0
        for qualifiers in shots['qualifiers_dict']:
            if isinstance(qualifiers, dict) and 'CounterAttack' in qualifiers:
                count += 1
        return count

    def export_to_dataframe(self) -> pd.DataFrame:
        """
        Export aggregated statistics as comparison DataFrame.

        Returns:
            DataFrame with home vs away statistics
        """
        stats = self.aggregate_all_stats()

        data = []
        for stat_name in stats['home'].keys():
            data.append({
                'stat': stat_name,
                'home': stats['home'][stat_name],
                'away': stats['away'][stat_name]
            })

        return pd.DataFrame(data)

    def export_whoscored_format(self) -> Dict[str, Any]:
        """
        Export in format matching WhoScored match summary.

        Returns:
            Dictionary matching WhoScored interface structure
        """
        stats = self.aggregate_all_stats()

        return {
            'offensive': {
                'shots': {'home': stats['home']['shots'], 'away': stats['away']['shots']},
                'shots_on_target': {'home': stats['home']['shots_on_target'], 'away': stats['away']['shots_on_target']},
                'passes': {'home': stats['home']['passes'], 'away': stats['away']['passes']},
                'dribbles': {'home': stats['home']['dribbles'], 'away': stats['away']['dribbles']},
            },
            'defensive': {
                'tackles': {'home': stats['home']['tackles'], 'away': stats['away']['tackles']},
                'clearances': {'home': stats['home']['clearances'], 'away': stats['away']['clearances']},
                'interceptions': {'home': stats['home']['interceptions'], 'away': stats['away']['interceptions']},
                'blocks': {'home': stats['home']['blocks'], 'away': stats['away']['blocks']},
            },
            'possession': {
                'touches': {'home': stats['home']['touches'], 'away': stats['away']['touches']},
                'dispossessed': {'home': stats['home']['dispossessed'], 'away': stats['away']['dispossessed']},
            },
            'discipline': {
                'fouls': {'home': stats['home']['fouls'], 'away': stats['away']['fouls']},
                'yellow_cards': {'home': stats['home']['yellow_cards'], 'away': stats['away']['yellow_cards']},
                'red_cards': {'home': stats['home']['red_cards'], 'away': stats['away']['red_cards']},
                'offsides': {'home': stats['home']['offsides'], 'away': stats['away']['offsides']},
            },
            'aerials': {
                'aerial_duels': {'home': stats['home']['aerial_duels'], 'away': stats['away']['aerial_duels']},
                'aerial_duels_won': {'home': stats['home']['aerial_duels_won'], 'away': stats['away']['aerial_duels_won']},
            },
            'goalkeeping': {
                'saves': {'home': stats['home']['saves'], 'away': stats['away']['saves']},
            },
            'errors': {
                'errors_leading_to_shot': {'home': stats['home']['errors_leading_to_shot'], 'away': stats['away']['errors_leading_to_shot']},
                'errors_leading_to_goal': {'home': stats['home']['errors_leading_to_goal'], 'away': stats['away']['errors_leading_to_goal']},
            },
            'shot_breakdown': {
                'penalty_area': {'home': stats['home']['penalty_area_shots'], 'away': stats['away']['penalty_area_shots']},
                'six_yard_box': {'home': stats['home']['six_yard_box_shots'], 'away': stats['away']['six_yard_box_shots']},
                'outside_box': {'home': stats['home']['outside_box_shots'], 'away': stats['away']['outside_box_shots']},
                'right_foot': {'home': stats['home']['right_foot_shots'], 'away': stats['away']['right_foot_shots']},
                'left_foot': {'home': stats['home']['left_foot_shots'], 'away': stats['away']['left_foot_shots']},
                'headed': {'home': stats['home']['headed_shots'], 'away': stats['away']['headed_shots']},
                'open_play': {'home': stats['home']['open_play_shots'], 'away': stats['away']['open_play_shots']},
                'set_piece': {'home': stats['home']['set_piece_shots'], 'away': stats['away']['set_piece_shots']},
                'counter_attack': {'home': stats['home']['counter_attack_shots'], 'away': stats['away']['counter_attack_shots']},
            }
        }
