"""
Match Visualizations
Creates all visualizations for the match report.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager
import numpy as np
import pandas as pd
from mplsoccer import Pitch, VerticalPitch
from scipy.ndimage import gaussian_filter
from typing import Dict, Any, Tuple, Optional, List
import warnings

warnings.filterwarnings('ignore')


class MatchVisualizer:
    """Create visualizations for match reports."""

    def __init__(self, processor, team_info: Dict[str, Any]):
        """
        Initialize visualizer.

        Args:
            processor: MatchDataProcessor instance
            team_info: Team information dictionary
        """
        self.processor = processor
        self.team_info = team_info

        # Colors
        self.home_color = team_info.get('team_colors', {}).get('home_color', '#FF0000')
        self.away_color = team_info.get('team_colors', {}).get('away_color', '#0000FF')
        self.pitch_color = '#d6c39f'
        self.line_color = '#0e1117'

        # Team IDs
        self.home_team_id = team_info['home']['id']
        self.away_team_id = team_info['away']['id']

    def create_match_summary_panel(self, ax) -> None:
        """
        Create match summary statistics panel.

        Args:
            ax: Matplotlib axis
        """
        ax.axis('off')

        # Title
        home_name = self.team_info['home']['name']
        away_name = self.team_info['away']['name']
        home_score = self.team_info['home']['score']
        away_score = self.team_info['away']['score']

        title = f"{home_name} {home_score} - {away_score} {away_name}"
        ax.text(0.5, 0.95, title, ha='center', va='top', fontsize=16, fontweight='bold')

        # League and date info
        subtitle = f"{self.team_info.get('league', 'League')} | {self.team_info.get('date', '')[:10]}"
        ax.text(0.5, 0.88, subtitle, ha='center', va='top', fontsize=10)

        # Statistics
        stats_y = 0.75
        line_height = 0.08

        stats = [
            ('Possession', f"{self.team_info['possession']['home_possession']:.0f}%",
             f"{self.team_info['possession']['away_possession']:.0f}%"),
            ('xG', f"{self.team_info['xg']['home_xg']:.2f}", f"{self.team_info['xg']['away_xg']:.2f}"),
            ('Shots', f"{self.team_info['shots']['home_shots']}", f"{self.team_info['shots']['away_shots']}"),
        ]

        for stat_name, home_val, away_val in stats:
            # Stat name
            ax.text(0.5, stats_y, stat_name, ha='center', va='center', fontsize=11, fontweight='bold')

            # Home value
            ax.text(0.25, stats_y, home_val, ha='center', va='center', fontsize=11,
                   color=self.home_color, fontweight='bold')

            # Away value
            ax.text(0.75, stats_y, away_val, ha='center', va='center', fontsize=11,
                   color=self.away_color, fontweight='bold')

            stats_y -= line_height

    def create_shot_map(self, ax) -> None:
        """
        Create shot map visualization.

        Args:
            ax: Matplotlib axis
        """
        pitch = VerticalPitch(pitch_type='custom', pitch_length=105, pitch_width=68,
                             pitch_color=self.pitch_color, line_color=self.line_color,
                             linewidth=1.5)
        pitch.draw(ax=ax)

        # Get shots data
        home_shots = self.processor.get_shots_df(team_id=self.home_team_id)
        away_shots = self.processor.get_shots_df(team_id=self.away_team_id)

        # Plot home shots (bottom half)
        if not home_shots.empty:
            for _, shot in home_shots.iterrows():
                # Determine marker based on outcome
                if 'Goal' in shot.get('qualifiers_dict', {}):
                    marker = '*'
                    size = 400
                    edgecolor = 'gold'
                    linewidth = 2
                elif shot['is_successful']:
                    marker = 'o'
                    size = 200
                    edgecolor = self.home_color
                    linewidth = 1.5
                else:
                    marker = 'x'
                    size = 150
                    edgecolor = self.home_color
                    linewidth = 1.5

                xg_value = shot.get('xg', 0)
                alpha = 0.4 + (0.6 * xg_value)  # Higher xG = more opaque

                ax.scatter(shot['x'], shot['y'], s=size, c=self.home_color,
                          marker=marker, alpha=alpha, edgecolors=edgecolor, linewidths=linewidth, zorder=3)

        # Plot away shots (top half) - mirror coordinates
        if not away_shots.empty:
            for _, shot in away_shots.iterrows():
                # Mirror coordinates
                x_mirrored = 105 - shot['x']
                y_mirrored = 68 - shot['y']

                # Determine marker based on outcome
                if 'Goal' in shot.get('qualifiers_dict', {}):
                    marker = '*'
                    size = 400
                    edgecolor = 'gold'
                    linewidth = 2
                elif shot['is_successful']:
                    marker = 'o'
                    size = 200
                    edgecolor = self.away_color
                    linewidth = 1.5
                else:
                    marker = 'x'
                    size = 150
                    edgecolor = self.away_color
                    linewidth = 1.5

                xg_value = shot.get('xg', 0)
                alpha = 0.4 + (0.6 * xg_value)

                ax.scatter(x_mirrored, y_mirrored, s=size, c=self.away_color,
                          marker=marker, alpha=alpha, edgecolors=edgecolor, linewidths=linewidth, zorder=3)

        # Title
        ax.set_title('Shot Map', fontsize=12, fontweight='bold', pad=10)

        # Legend
        legend_elements = [
            plt.scatter([], [], c='gray', marker='*', s=200, label='Goal'),
            plt.scatter([], [], c='gray', marker='o', s=100, label='On Target'),
            plt.scatter([], [], c='gray', marker='x', s=100, label='Off Target')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=8, framealpha=0.8)

    def create_pass_network(self, ax, team_id: int, team_color: str, team_name: str) -> None:
        """
        Create pass network visualization.

        Args:
            ax: Matplotlib axis
            team_id: Team ID
            team_color: Team color
            team_name: Team name
        """
        pitch = Pitch(pitch_type='custom', pitch_length=105, pitch_width=68,
                     pitch_color=self.pitch_color, line_color=self.line_color,
                     linewidth=1.5)
        pitch.draw(ax=ax)

        # Get player positions and pass connections
        player_positions = self.processor.get_player_average_positions(team_id, starting_xi_only=True)
        passes_between = self.processor.get_passes_between_players(team_id, starting_xi_only=True)

        if player_positions.empty:
            ax.set_title(f'{team_name} Pass Network', fontsize=12, fontweight='bold', pad=10)
            ax.text(52.5, 34, 'No Data Available', ha='center', va='center', fontsize=10)
            return

        # Plot pass connections
        if not passes_between.empty:
            # Filter significant connections (top 75%)
            threshold = passes_between['pass_count'].quantile(0.25)
            significant_passes = passes_between[passes_between['pass_count'] >= threshold]

            for _, row in significant_passes.iterrows():
                passer = player_positions[player_positions['playerId'] == row['playerId']]
                receiver = player_positions[player_positions['playerId'] == row['receiver']]

                if not passer.empty and not receiver.empty:
                    x1, y1 = passer.iloc[0]['x'], passer.iloc[0]['y']
                    x2, y2 = receiver.iloc[0]['x'], receiver.iloc[0]['y']

                    # Line width based on pass count
                    max_passes = passes_between['pass_count'].max()
                    line_width = 0.5 + (row['pass_count'] / max_passes) * 4

                    ax.plot([x1, x2], [y1, y2], color=team_color, linewidth=line_width,
                           alpha=0.6, zorder=1)

        # Plot player positions
        for _, player in player_positions.iterrows():
            # Plot point
            ax.scatter(player['x'], player['y'], s=600, c=team_color,
                      edgecolors='white', linewidths=2, zorder=3, alpha=0.9)

            # Add shirt number
            shirt_no = player.get('shirtNo', '?')
            ax.text(player['x'], player['y'], str(shirt_no),
                   ha='center', va='center', fontsize=9, fontweight='bold',
                   color='white', zorder=4)

        ax.set_title(f'{team_name} Pass Network', fontsize=12, fontweight='bold', pad=10)

    def create_momentum_graph(self, ax) -> None:
        """
        Create momentum/match flow graph.

        Args:
            ax: Matplotlib axis
        """
        # Get all events
        if self.processor.events_df is None or self.processor.events_df.empty:
            ax.axis('off')
            ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center')
            return

        # Calculate momentum using possession events in time windows
        df = self.processor.events_df.copy()

        # Create time bins (every 2 minutes)
        max_time = df['cumulative_mins'].max()
        time_bins = np.arange(0, max_time + 2, 2)

        home_momentum = []
        away_momentum = []
        time_points = []

        for i in range(len(time_bins) - 1):
            start_time = time_bins[i]
            end_time = time_bins[i + 1]

            # Get events in this window
            window_events = df[(df['cumulative_mins'] >= start_time) &
                              (df['cumulative_mins'] < end_time)]

            if len(window_events) > 0:
                home_events = len(window_events[window_events['teamId'] == self.home_team_id])
                away_events = len(window_events[window_events['teamId'] == self.away_team_id])

                total = home_events + away_events
                if total > 0:
                    home_pct = (home_events / total) * 100
                    away_pct = (away_events / total) * 100
                else:
                    home_pct = away_pct = 50

                home_momentum.append(home_pct)
                away_momentum.append(away_pct)
                time_points.append((start_time + end_time) / 2)

        # Plot momentum
        if time_points:
            ax.fill_between(time_points, 50, home_momentum, color=self.home_color, alpha=0.4, label=self.team_info['home']['name'])
            ax.fill_between(time_points, 50, away_momentum, color=self.away_color, alpha=0.4, label=self.team_info['away']['name'])
            ax.axhline(y=50, color='black', linestyle='--', linewidth=1, alpha=0.5)

            # Mark goals
            goals = df[(df['type_display'] == 'Shot') &
                      (df['qualifiers_dict'].apply(lambda x: 'Goal' in x if isinstance(x, dict) else False))]

            for _, goal in goals.iterrows():
                color = self.home_color if goal['teamId'] == self.home_team_id else self.away_color
                y_pos = 95 if goal['teamId'] == self.home_team_id else 5
                ax.scatter(goal['cumulative_mins'], y_pos, s=200, c=color,
                          marker='o', edgecolors='gold', linewidths=2, zorder=5)

        ax.set_xlim(0, max(time_points) if time_points else 90)
        ax.set_ylim(0, 100)
        ax.set_xlabel('Match Time (minutes)', fontsize=9)
        ax.set_ylabel('Possession %', fontsize=9)
        ax.set_title('Match Momentum', fontsize=12, fontweight='bold', pad=10)
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.3)

    def create_key_passes_map(self, ax) -> None:
        """
        Create key passes and assists visualization.

        Args:
            ax: Matplotlib axis
        """
        pitch = Pitch(pitch_type='custom', pitch_length=105, pitch_width=68,
                     pitch_color=self.pitch_color, line_color=self.line_color,
                     linewidth=1.5)
        pitch.draw(ax=ax)

        # Get key passes and assists
        all_passes = self.processor.get_passes_df(successful_only=True)

        if not all_passes.empty:
            key_passes = all_passes[all_passes['is_key_pass'] == True]
            assists = all_passes[all_passes['is_assist'] == True]

            # Plot key passes
            for _, kp in key_passes.iterrows():
                color = self.home_color if kp['teamId'] == self.home_team_id else self.away_color

                if pd.notna(kp['endX']) and pd.notna(kp['endY']):
                    ax.annotate('', xy=(kp['endX'], kp['endY']), xytext=(kp['x'], kp['y']),
                               arrowprops=dict(arrowstyle='->', color=color, lw=2, alpha=0.6))

            # Plot assists (highlighted)
            for _, assist in assists.iterrows():
                color = self.home_color if assist['teamId'] == self.home_team_id else self.away_color

                if pd.notna(assist['endX']) and pd.notna(assist['endY']):
                    ax.annotate('', xy=(assist['endX'], assist['endY']),
                               xytext=(assist['x'], assist['y']),
                               arrowprops=dict(arrowstyle='->', color=color, lw=3,
                                             alpha=0.8, linestyle='--'))

                    # Mark assist start with a star
                    ax.scatter(assist['x'], assist['y'], s=300, c=color,
                             marker='*', edgecolors='gold', linewidths=2, zorder=5)

        ax.set_title('Key Passes & Assists', fontsize=12, fontweight='bold', pad=10)

    def create_defensive_actions_heatmap(self, ax, team_id: int, team_color: str, team_name: str) -> None:
        """
        Create defensive actions heatmap.

        Args:
            ax: Matplotlib axis
            team_id: Team ID
            team_color: Team color
            team_name: Team name
        """
        pitch = Pitch(pitch_type='custom', pitch_length=105, pitch_width=68,
                     pitch_color=self.pitch_color, line_color=self.line_color,
                     linewidth=1.5)
        pitch.draw(ax=ax)

        # Get defensive actions
        defensive_actions = self.processor.get_defensive_actions_df(team_id=team_id)

        if not defensive_actions.empty and len(defensive_actions) >= 5:
            # Create 2D histogram for heatmap
            x = defensive_actions['x'].values
            y = defensive_actions['y'].values

            # Create bins
            x_bins = np.linspace(0, 105, 21)
            y_bins = np.linspace(0, 68, 14)

            # Calculate histogram
            heatmap, xedges, yedges = np.histogram2d(x, y, bins=[x_bins, y_bins])

            # Apply Gaussian filter for smoothing
            heatmap = gaussian_filter(heatmap, sigma=1.0)

            # Plot heatmap
            extent = [0, 105, 0, 68]
            im = ax.imshow(heatmap.T, extent=extent, origin='lower',
                          cmap='Reds', alpha=0.6, aspect='auto', zorder=2)

        ax.set_title(f'{team_name} Defensive Actions', fontsize=12, fontweight='bold', pad=10)

    def create_zone14_halfspace_map(self, ax, team_id: int, team_color: str, team_name: str) -> None:
        """
        Create Zone 14 and half-space visualization.

        Args:
            ax: Matplotlib axis
            team_id: Team ID
            team_color: Team color
            team_name: Team name
        """
        pitch = Pitch(pitch_type='custom', pitch_length=105, pitch_width=68,
                     pitch_color=self.pitch_color, line_color=self.line_color,
                     linewidth=1.5)
        pitch.draw(ax=ax)

        # Define Zone 14 (central area in attacking third)
        zone14_x = [70, 87.5]  # Between penalty box and attacking third
        zone14_y = [20.4, 47.6]  # Central channel

        # Define half-spaces
        left_halfspace_y = [10.2, 27.2]  # Left half-space
        right_halfspace_y = [40.8, 57.8]  # Right half-space

        # Draw zones
        # Zone 14
        rect_z14 = patches.Rectangle((zone14_x[0], zone14_y[0]),
                                     zone14_x[1] - zone14_x[0],
                                     zone14_y[1] - zone14_y[0],
                                     linewidth=2, edgecolor='#bd841c',
                                     facecolor='#bd841c', alpha=0.2, zorder=2)
        ax.add_patch(rect_z14)

        # Left half-space
        rect_lhs = patches.Rectangle((zone14_x[0], left_halfspace_y[0]),
                                     zone14_x[1] - zone14_x[0],
                                     left_halfspace_y[1] - left_halfspace_y[0],
                                     linewidth=2, edgecolor=team_color,
                                     facecolor=team_color, alpha=0.15, zorder=2)
        ax.add_patch(rect_lhs)

        # Right half-space
        rect_rhs = patches.Rectangle((zone14_x[0], right_halfspace_y[0]),
                                     zone14_x[1] - zone14_x[0],
                                     right_halfspace_y[1] - right_halfspace_y[0],
                                     linewidth=2, edgecolor=team_color,
                                     facecolor=team_color, alpha=0.15, zorder=2)
        ax.add_patch(rect_rhs)

        # Get passes in these zones
        passes = self.processor.get_passes_df(team_id=team_id, successful_only=True)

        if not passes.empty:
            # Filter passes in zone 14 and half-spaces
            zone_passes = passes[
                (passes['x'] >= zone14_x[0]) & (passes['x'] <= zone14_x[1]) &
                (((passes['y'] >= zone14_y[0]) & (passes['y'] <= zone14_y[1])) |
                 ((passes['y'] >= left_halfspace_y[0]) & (passes['y'] <= left_halfspace_y[1])) |
                 ((passes['y'] >= right_halfspace_y[0]) & (passes['y'] <= right_halfspace_y[1])))
            ]

            # Plot passes
            for _, pass_event in zone_passes.iterrows():
                if pd.notna(pass_event['endX']) and pd.notna(pass_event['endY']):
                    ax.plot([pass_event['x'], pass_event['endX']],
                           [pass_event['y'], pass_event['endY']],
                           color=team_color, linewidth=1.5, alpha=0.5, zorder=3)

                    ax.scatter(pass_event['x'], pass_event['y'], s=30,
                             c=team_color, alpha=0.7, zorder=4)

        ax.set_title(f'{team_name} Zone 14 & Half-Spaces', fontsize=12, fontweight='bold', pad=10)

    def create_box_entry_map(self, ax) -> None:
        """
        Create penalty box entry visualization.

        Args:
            ax: Matplotlib axis
        """
        pitch = Pitch(pitch_type='custom', pitch_length=105, pitch_width=68,
                     pitch_color=self.pitch_color, line_color=self.line_color,
                     linewidth=1.5)
        pitch.draw(ax=ax)

        # Box coordinates
        box_x = 88.5  # Start of penalty box
        box_y_bottom = 13.8
        box_y_top = 54.2

        # Get all passes and carries
        all_passes = self.processor.get_passes_df(successful_only=True)
        all_carries = self.processor.get_carries_df()

        # Combine passes and carries
        events = pd.concat([all_passes, all_carries], ignore_index=True)

        if not events.empty:
            # Filter for box entries (start outside, end inside box)
            box_entries = events[
                (events['x'] < box_x) &
                (events['endX'] >= box_x) &
                (events['endY'] >= box_y_bottom) &
                (events['endY'] <= box_y_top)
            ]

            # Plot entries
            for _, entry in box_entries.iterrows():
                color = self.home_color if entry['teamId'] == self.home_team_id else self.away_color

                if pd.notna(entry['endX']) and pd.notna(entry['endY']):
                    ax.plot([entry['x'], entry['endX']],
                           [entry['y'], entry['endY']],
                           color=color, linewidth=2, alpha=0.6, zorder=3)

                    ax.scatter(entry['endX'], entry['endY'], s=80,
                             c=color, alpha=0.7, edgecolors='white', linewidths=1, zorder=4)

        ax.set_title('Penalty Box Entries', fontsize=12, fontweight='bold', pad=10)

    def create_pitch_control_map(self, ax) -> None:
        """
        Create pitch control/congestion visualization.

        Args:
            ax: Matplotlib axis
        """
        pitch = Pitch(pitch_type='custom', pitch_length=105, pitch_width=68,
                     pitch_color=self.pitch_color, line_color=self.line_color,
                     linewidth=1.5)
        pitch.draw(ax=ax)

        # Get all events
        if self.processor.events_df is None or self.processor.events_df.empty:
            ax.set_title('Pitch Control', fontsize=12, fontweight='bold', pad=10)
            return

        # Create grid
        x_bins = np.linspace(0, 105, 7)  # 6 columns
        y_bins = np.linspace(0, 68, 6)   # 5 rows

        # Calculate control for each cell
        for i in range(len(x_bins) - 1):
            for j in range(len(y_bins) - 1):
                x_start, x_end = x_bins[i], x_bins[i + 1]
                y_start, y_end = y_bins[j], y_bins[j + 1]

                # Count events in this cell
                cell_events = self.processor.events_df[
                    (self.processor.events_df['x'] >= x_start) &
                    (self.processor.events_df['x'] < x_end) &
                    (self.processor.events_df['y'] >= y_start) &
                    (self.processor.events_df['y'] < y_end)
                ]

                if len(cell_events) > 0:
                    home_events = len(cell_events[cell_events['teamId'] == self.home_team_id])
                    away_events = len(cell_events[cell_events['teamId'] == self.away_team_id])

                    total = home_events + away_events
                    if total > 0:
                        home_pct = home_events / total

                        # Determine color (blend between team colors)
                        if home_pct > 0.6:
                            color = self.home_color
                            alpha = 0.2 + (home_pct - 0.6) * 1.5
                        elif home_pct < 0.4:
                            color = self.away_color
                            alpha = 0.2 + (0.4 - home_pct) * 1.5
                        else:
                            color = 'gray'
                            alpha = 0.1

                        rect = patches.Rectangle((x_start, y_start),
                                                x_end - x_start,
                                                y_end - y_start,
                                                facecolor=color, alpha=min(alpha, 0.6),
                                                edgecolor='none', zorder=2)
                        ax.add_patch(rect)

        ax.set_title('Pitch Control', fontsize=12, fontweight='bold', pad=10)


def create_full_match_report(processor, team_info: Dict[str, Any],
                             figsize: Tuple[int, int] = (20, 22)) -> plt.Figure:
    """
    Create complete match report with all visualizations.

    Args:
        processor: MatchDataProcessor instance
        team_info: Team information dictionary
        figsize: Figure size

    Returns:
        Matplotlib Figure
    """
    # Create figure with grid
    fig = plt.figure(figsize=figsize, facecolor='#f0f0f0')
    gs = fig.add_gridspec(4, 3, hspace=0.3, wspace=0.3,
                         left=0.05, right=0.95, top=0.95, bottom=0.05)

    # Initialize visualizer
    viz = MatchVisualizer(processor, team_info)

    # Create all visualizations
    # Row 1
    ax1 = fig.add_subplot(gs[0, 0])
    viz.create_match_summary_panel(ax1)

    ax2 = fig.add_subplot(gs[0, 1])
    viz.create_shot_map(ax2)

    ax3 = fig.add_subplot(gs[0, 2])
    viz.create_momentum_graph(ax3)

    # Row 2
    ax4 = fig.add_subplot(gs[1, 0])
    viz.create_pass_network(ax4, viz.home_team_id, viz.home_color,
                           team_info['home']['name'])

    ax5 = fig.add_subplot(gs[1, 1])
    viz.create_key_passes_map(ax5)

    ax6 = fig.add_subplot(gs[1, 2])
    viz.create_pass_network(ax6, viz.away_team_id, viz.away_color,
                           team_info['away']['name'])

    # Row 3
    ax7 = fig.add_subplot(gs[2, 0])
    viz.create_zone14_halfspace_map(ax7, viz.home_team_id, viz.home_color,
                                   team_info['home']['name'])

    ax8 = fig.add_subplot(gs[2, 1])
    viz.create_box_entry_map(ax8)

    ax9 = fig.add_subplot(gs[2, 2])
    viz.create_zone14_halfspace_map(ax9, viz.away_team_id, viz.away_color,
                                   team_info['away']['name'])

    # Row 4
    ax10 = fig.add_subplot(gs[3, 0])
    viz.create_defensive_actions_heatmap(ax10, viz.home_team_id, viz.home_color,
                                        team_info['home']['name'])

    ax11 = fig.add_subplot(gs[3, 1])
    viz.create_pitch_control_map(ax11)

    ax12 = fig.add_subplot(gs[3, 2])
    viz.create_defensive_actions_heatmap(ax12, viz.away_team_id, viz.away_color,
                                        team_info['away']['name'])

    # Add watermark
    fig.text(0.5, 0.01, 'PostMatchReport', ha='center', fontsize=10,
            alpha=0.5, style='italic')

    return fig
