"""
Data Utilities
General data manipulation utilities for visualizations.
"""

import numpy as np
import pandas as pd
from typing import Union, Optional


def safe_divide(numerator: Union[int, float, np.ndarray],
                denominator: Union[int, float, np.ndarray],
                default: float = 0.0) -> Union[float, np.ndarray]:
    """
    Safely divide two numbers, returning default if denominator is zero.

    Args:
        numerator: Numerator value(s)
        denominator: Denominator value(s)
        default: Default value to return if division by zero

    Returns:
        Result of division or default value
    """
    if isinstance(denominator, (int, float)):
        return numerator / denominator if denominator != 0 else default
    else:
        # Handle numpy arrays
        result = np.divide(numerator, denominator,
                          out=np.full_like(numerator, default, dtype=float),
                          where=denominator != 0)
        return result


def calculate_percentile(value: float, data: Union[list, np.ndarray, pd.Series]) -> float:
    """
    Calculate what percentile a value represents in a dataset.

    Args:
        value: Value to calculate percentile for
        data: Dataset to compare against

    Returns:
        Percentile (0-100)
    """
    if isinstance(data, pd.Series):
        data = data.values
    elif isinstance(data, list):
        data = np.array(data)

    if len(data) == 0:
        return 50.0

    percentile = (np.sum(data <= value) / len(data)) * 100
    return float(percentile)


def normalize_values(values: Union[list, np.ndarray, pd.Series],
                     min_val: float = 0.0,
                     max_val: float = 1.0) -> np.ndarray:
    """
    Normalize values to a specific range.

    Args:
        values: Values to normalize
        min_val: Minimum value of output range
        max_val: Maximum value of output range

    Returns:
        Normalized array
    """
    if isinstance(values, pd.Series):
        values = values.values
    elif isinstance(values, list):
        values = np.array(values)

    if len(values) == 0:
        return np.array([])

    values_min = np.min(values)
    values_max = np.max(values)

    if values_max == values_min:
        return np.full_like(values, (min_val + max_val) / 2, dtype=float)

    normalized = (values - values_min) / (values_max - values_min)
    scaled = normalized * (max_val - min_val) + min_val

    return scaled


def bin_data(data: Union[list, np.ndarray, pd.Series],
             bins: int = 10,
             labels: Optional[list] = None) -> pd.Series:
    """
    Bin continuous data into discrete categories.

    Args:
        data: Data to bin
        bins: Number of bins or list of bin edges
        labels: Optional labels for bins

    Returns:
        Series with binned categories
    """
    if isinstance(data, (list, np.ndarray)):
        data = pd.Series(data)

    return pd.cut(data, bins=bins, labels=labels)


def rolling_average(data: Union[list, np.ndarray, pd.Series],
                    window: int = 5,
                    min_periods: int = 1) -> pd.Series:
    """
    Calculate rolling average of data.

    Args:
        data: Data to smooth
        window: Window size for rolling average
        min_periods: Minimum number of observations required

    Returns:
        Series with rolling average
    """
    if isinstance(data, (list, np.ndarray)):
        data = pd.Series(data)

    return data.rolling(window=window, min_periods=min_periods).mean()


def filter_outliers(data: pd.DataFrame,
                    column: str,
                    method: str = 'iqr',
                    threshold: float = 1.5) -> pd.DataFrame:
    """
    Filter outliers from a dataframe based on a column.

    Args:
        data: DataFrame to filter
        column: Column to check for outliers
        method: 'iqr' (interquartile range) or 'zscore'
        threshold: Threshold for outlier detection (1.5 for IQR, 3 for z-score)

    Returns:
        Filtered DataFrame
    """
    if data.empty or column not in data.columns:
        return data

    if method == 'iqr':
        Q1 = data[column].quantile(0.25)
        Q3 = data[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        return data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]

    elif method == 'zscore':
        z_scores = np.abs((data[column] - data[column].mean()) / data[column].std())
        return data[z_scores < threshold]

    else:
        raise ValueError(f"Unknown method: {method}. Use 'iqr' or 'zscore'")


def aggregate_by_player(events_df: pd.DataFrame,
                        team_id: int,
                        agg_functions: dict = None) -> pd.DataFrame:
    """
    Aggregate events by player.

    Args:
        events_df: DataFrame with event data
        team_id: Team ID to filter by
        agg_functions: Dictionary of aggregation functions per column

    Returns:
        DataFrame aggregated by player
    """
    if events_df.empty:
        return pd.DataFrame()

    # Filter by team
    team_events = events_df[events_df['teamId'] == team_id].copy()

    if team_events.empty:
        return pd.DataFrame()

    # Default aggregation functions
    if agg_functions is None:
        agg_functions = {
            'x': 'mean',
            'y': 'mean',
            'eventType': 'count'
        }

    # Group by player
    if 'playerId' in team_events.columns:
        grouped = team_events.groupby('playerId').agg(agg_functions)
        return grouped.reset_index()
    else:
        return pd.DataFrame()
