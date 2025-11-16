"""
Pitch Visualizations
Shot maps, pass networks, and other pitch-based visualizations.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mplsoccer import VerticalPitch
from matplotlib.colors import Normalize, to_rgba
import matplotlib.cm as cm
from typing import Optional

from Visual.base_visualization import BaseVisualization
from Visual.utils import filter_90min


class PitchVisualizations(BaseVisualization):
    """Create pitch-based visualizations."""

    def __init__(self, theme_manager=None, pitch_color='#d6c39f', line_color='#0e1117',
                 show_colorbars=True):
        """
        Initialize pitch visualizations.

        Args:
            theme_manager: ThemeManager instance
            pitch_color: Override pitch color (for backward compatibility)
            line_color: Override line color (for backward compatibility)
            show_colorbars: Whether to show colorbars
        """
        super().__init__(theme_manager, pitch_color, line_color, show_colorbars)

    def create_shot_map(self, ax, shots_home, shots_away, home_color, away_color):
        """Create shot map with shot outcome visualization."""
        # Create vertical pitch
        pitch = self.pitch_factory.create_pitch(vertical=True)
        pitch.draw(ax=ax)

        # Plot home shots (bottom) - swap x,y for VerticalPitch
        for _, shot in shots_home.iterrows():
            shot_type = shot.get('type_display', '')
            is_goal = shot_type == 'Goal'
            is_on_target = shot_type in ['SavedShot', 'Goal']

            marker = '*' if is_goal else ('o' if is_on_target else 'x')
            size = 500 if is_goal else 250 if is_on_target else 150
            edge = 'gold' if is_goal else home_color
            alpha = 1.0 if is_goal else 0.7 if is_on_target else 0.5

            # VerticalPitch: x=width, y=length; Data: x=length, y=width -> swap
            ax.scatter(shot['y'], shot['x'], s=size, c=home_color, marker=marker,
                      alpha=alpha, edgecolors=edge, linewidths=2.5 if is_goal else 2, zorder=3)

        # Plot away shots (top, mirrored along length axis)
        for _, shot in shots_away.iterrows():
            shot_type = shot.get('type_display', '')
            is_goal = shot_type == 'Goal'
            is_on_target = shot_type in ['SavedShot', 'Goal']

            marker = '*' if is_goal else ('o' if is_on_target else 'x')
            size = 500 if is_goal else 250 if is_on_target else 150
            edge = 'gold' if is_goal else away_color
            alpha = 1.0 if is_goal else 0.7 if is_on_target else 0.5

            # VerticalPitch: x=width, y=length; Mirror length (105-x)
            ax.scatter(shot['y'], 105-shot['x'], s=size, c=away_color, marker=marker,
                      alpha=alpha, edgecolors=edge, linewidths=2.5 if is_goal else 2, zorder=3)

        self.prepare_axis(ax, 'Shot Map')

    def create_xg_shot_map(self, ax, shots_home: pd.DataFrame, shots_away: pd.DataFrame,
                            home_color: str, away_color: str,
                            cmap: str = 'inferno'):
        """
        xG shot map with color-mapped xG and rich markers.

        - Uses VerticalPitch (105x68) with theme colors.
        - Colors markers by xG and scales size by xG.
        - Uses marker shape to distinguish header, set-piece, other.
        - Mirrors away shots to top half.
        - Adds an inset horizontal colorbar.
        """
        # Create vertical pitch
        pitch = self.pitch_factory.create_pitch(vertical=True)
        pitch.draw(ax=ax)

        norm = Normalize(vmin=0.0, vmax=1.0)
        cmap_obj = cm.get_cmap(cmap)

        # If no shots at all, show an informative message
        if (shots_home is None or shots_home.empty) and (shots_away is None or shots_away.empty):
            ax.text(0.5, 0.5, 'No shots yet', transform=ax.transAxes,
                    ha='center', va='center', fontsize=12, color=self.get_text_color())
            self.prepare_axis(ax, 'xG Shot Map')
            return

        def marker_for(shot_row: pd.Series):
            q = shot_row.get('qualifiers_dict', {})
            if isinstance(q, dict):
                if 'Head' in q:
                    return 'o', 250, 150
                if 'Penalty' in q or 'DirectFreeKick' in q:
                    return 's', 175, 125
            # fallback by type
            t = shot_row.get('type_display', '')
            if t == 'MissedShots' or t == 'ShotOnPost' or t == 'SavedShot':
                return 'h', 220, 130
            return 'h', 300, 150

        last_pathcoll = None

        def plot_shot(row: pd.Series, is_home: bool):
            nonlocal last_pathcoll
            xg = float(row.get('xg', 0.0))
            color = cmap_obj(norm(xg))
            marker, s, s_delta = marker_for(row)
            # Determine plot coords for VerticalPitch: use (y, x)
            x = float(row.get('x', 0.0))
            y = float(row.get('y', 0.0))
            yy = y
            xx = x if is_home else 105 - x

            shot_type = row.get('type_display', '')
            is_goal = shot_type == 'Goal'
            is_saved_or_post = shot_type in ['SavedShot', 'ShotOnPost']
            is_miss_or_block = shot_type in ['MissedShots']

            edge = 'white' if is_goal else 'lightgray'
            lw = 1.5 if is_goal else 0.8
            alpha = 1.0 if is_goal else 0.9 if is_saved_or_post else 0.7 if is_miss_or_block else 0.8

            size = max(120, int(120 + xg * 380))

            last_pathcoll = ax.scatter(yy, xx, marker=marker, s=size,
                                       c=[color], alpha=alpha, edgecolors=edge, lw=lw, zorder=3)

            if is_goal:
                ax.scatter(yy, xx, marker=marker, s=size + s_delta, c=self.pitch_color,
                           edgecolors='gold', lw=1.5, zorder=2)

        if shots_home is not None and not shots_home.empty:
            for _, r in shots_home.iterrows():
                plot_shot(r, is_home=True)
        if shots_away is not None and not shots_away.empty:
            for _, r in shots_away.iterrows():
                plot_shot(r, is_home=False)

        # Add colorbar using utility
        if last_pathcoll is not None:
            mappable = cm.ScalarMappable(norm=norm, cmap=cmap_obj)
            self.add_colorbar(ax, mappable, label='xG',
                            bbox_to_anchor=(0.5, -0.08, 0.0, 0.0))

        self.prepare_axis(ax, 'xG Shot Map')

    def create_pass_network(self, ax, avg_positions_df, pass_connections_df,
                           team_color, team_name, simple_mode=False):
        """
        Create enhanced pass network visualization.

        - Line widths based on pass volume
        - Player marker sizes based on number of passes
        - Transparency based on pass volume
        - Player initials on markers

        Args:
            ax: Matplotlib axis
            avg_positions_df: DataFrame with player average positions
            pass_connections_df: DataFrame with pass connections
            team_color: Team color
            team_name: Team name
            simple_mode: If True, use simpler visualization
        """
        # Create pitch
        pitch = self.create_pitch()
        pitch.draw(ax=ax)

        if avg_positions_df.empty:
            ax.text(52.5, 34, 'No Data Available', ha='center', va='center',
                   fontsize=10, color=self.get_text_color())
            self.prepare_axis(ax, f'{team_name} Pass Network')
            return

        # Constants for scaling
        MAX_LINE_WIDTH = 10
        MAX_MARKER_SIZE = 3000
        MIN_TRANSPARENCY = 0.3

        # Scale line widths based on pass count
        if not pass_connections_df.empty and 'pass_count' in pass_connections_df.columns:
            max_passes = pass_connections_df['pass_count'].max()
            if max_passes > 0:
                pass_connections_df = pass_connections_df.copy()
                pass_connections_df['line_width'] = (
                    pass_connections_df['pass_count'] / max_passes * MAX_LINE_WIDTH
                )

                # Create transparency array for lines
                color = np.array(to_rgba(team_color))
                color = np.tile(color, (len(pass_connections_df), 1))
                transparency = pass_connections_df['pass_count'] / max_passes
                transparency = (transparency * (1 - MIN_TRANSPARENCY)) + MIN_TRANSPARENCY
                color[:, 3] = transparency

                # Draw pass lines
                for i, (idx, row) in enumerate(pass_connections_df.iterrows()):
                    if pd.notna(row.get('x')) and pd.notna(row.get('y')) and \
                       pd.notna(row.get('x_end')) and pd.notna(row.get('y_end')):
                        ax.plot([row['x'], row['x_end']],
                               [row['y'], row['y_end']],
                               color=color[i],
                               linewidth=row['line_width'],
                               zorder=1,
                               solid_capstyle='round')

        # Scale marker sizes based on pass count
        if 'count' in avg_positions_df.columns:
            max_count = avg_positions_df['count'].max()
            if max_count > 0:
                avg_positions_df = avg_positions_df.copy()
                avg_positions_df['marker_size'] = (
                    avg_positions_df['count'] / max_count * MAX_MARKER_SIZE
                )
            else:
                avg_positions_df['marker_size'] = 1000
        else:
            avg_positions_df['marker_size'] = 1000

        # Draw player markers
        for _, player in avg_positions_df.iterrows():
            # Draw marker (hexagon shape)
            ax.scatter(player['x'], player['y'],
                      s=player['marker_size'],
                      marker='h',  # hexagon
                      c='white',
                      edgecolors=team_color,
                      linewidths=2,
                      alpha=0.95,
                      zorder=3)

            # Add player initials
            name = player.get('name', '')
            if name:
                # Create initials from player name
                name_parts = name.split()
                initials = "".join(word[0] for word in name_parts if word).upper()

                # Draw initials
                ax.text(player['x'], player['y'], initials,
                       ha='center', va='center',
                       fontsize=9, fontweight='bold',
                       color=team_color,
                       zorder=4)
            elif pd.notna(player.get('shirt_no')):
                # Fallback to shirt number if no name
                ax.text(player['x'], player['y'], str(int(player['shirt_no'])),
                       ha='center', va='center',
                       fontsize=9, fontweight='bold',
                       color=team_color,
                       zorder=4)

        self.prepare_axis(ax, f'{team_name} Pass Network')
