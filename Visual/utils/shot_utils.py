"""
Shot Utilities
Utilities for shot visualization and analysis.
"""

import pandas as pd
from typing import Dict, Any


def get_shot_marker(row: pd.Series) -> str:
    """
    Get marker style for shot based on outcome.

    Args:
        row: Pandas series with shot data

    Returns:
        Marker character for matplotlib
    """
    if row.get('is_goal', False):
        return 'football'  # Special football marker (if available)
    elif row.get('is_on_target', False):
        return 'o'  # Circle
    else:
        return 'x'  # Cross


def get_shot_color(row: pd.Series, team_color: str, goal_color: str = '#00ff00') -> str:
    """
    Get color for shot based on outcome.

    Args:
        row: Pandas series with shot data
        team_color: Default team color
        goal_color: Color for goals (default green)

    Returns:
        Hex color string
    """
    if row.get('is_goal', False):
        return goal_color
    else:
        return team_color


def get_shot_size(row: pd.Series, base_size: float = 100, xg_multiplier: float = 500) -> float:
    """
    Get marker size based on xG value.

    Args:
        row: Pandas series with shot data
        base_size: Minimum marker size
        xg_multiplier: Multiplier for xG value

    Returns:
        Marker size
    """
    xg = row.get('xG', row.get('expected_goals', 0.1))
    return base_size + (xg * xg_multiplier)


def classify_shot(row: pd.Series) -> str:
    """
    Classify shot outcome.

    Args:
        row: Pandas series with shot data

    Returns:
        Shot classification: 'goal', 'on_target', 'off_target', 'blocked'
    """
    if row.get('is_goal', False):
        return 'goal'
    elif row.get('is_blocked', False):
        return 'blocked'
    elif row.get('is_on_target', False):
        return 'on_target'
    else:
        return 'off_target'


def filter_90min(df: pd.DataFrame, time_column: str = 'cumulative_mins') -> pd.DataFrame:
    """
    Filter dataframe to include only events within 90 minutes.

    Args:
        df: DataFrame to filter
        time_column: Name of time column

    Returns:
        Filtered DataFrame
    """
    if df.empty:
        return df

    if time_column in df.columns:
        return df[df[time_column] <= 90].copy()
    else:
        return df


def get_shot_stats(shots_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate shot statistics from shots dataframe.

    Args:
        shots_df: DataFrame with shot data

    Returns:
        Dictionary with shot statistics
    """
    if shots_df.empty:
        return {
            'total_shots': 0,
            'on_target': 0,
            'off_target': 0,
            'blocked': 0,
            'goals': 0,
            'xG': 0.0,
            'accuracy': 0.0
        }

    total_shots = len(shots_df)
    on_target = shots_df.get('is_on_target', pd.Series([False])).sum()
    goals = shots_df.get('is_goal', pd.Series([False])).sum()
    blocked = shots_df.get('is_blocked', pd.Series([False])).sum()
    off_target = total_shots - on_target - blocked

    # Calculate total xG
    xg_col = 'xG' if 'xG' in shots_df.columns else 'expected_goals'
    total_xg = shots_df[xg_col].sum() if xg_col in shots_df.columns else 0.0

    # Calculate accuracy
    accuracy = (on_target / total_shots * 100) if total_shots > 0 else 0.0

    return {
        'total_shots': total_shots,
        'on_target': int(on_target),
        'off_target': int(off_target),
        'blocked': int(blocked),
        'goals': int(goals),
        'xG': float(total_xg),
        'accuracy': float(accuracy)
    }
