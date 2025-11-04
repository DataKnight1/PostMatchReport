"""
Advanced Visualizations
Momentum graphs, xG timelines, and advanced analytics.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.patches as patches


class AdvancedVisualizations:
    """Create advanced analytical visualizations."""

    def create_momentum_graph(self, ax, events_df, home_id, away_id, home_color, away_color, home_name, away_name):
        """Create match momentum/flow visualization."""
        if events_df is None or events_df.empty:
            ax.axis('off')
            ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center')
            return

        max_time = events_df['cumulative_mins'].max()
        time_bins = np.arange(0, max_time + 2, 2)

        home_momentum, away_momentum, time_points = [], [], []

        for i in range(len(time_bins) - 1):
            window = events_df[
                (events_df['cumulative_mins'] >= time_bins[i]) &
                (events_df['cumulative_mins'] < time_bins[i + 1])
            ]

            if len(window) > 0:
                home_cnt = len(window[window['teamId'] == home_id])
                away_cnt = len(window[window['teamId'] == away_id])
                total = home_cnt + away_cnt

                if total > 0:
                    home_momentum.append((home_cnt / total) * 100)
                    away_momentum.append((away_cnt / total) * 100)
                    time_points.append((time_bins[i] + time_bins[i + 1]) / 2)

        if time_points:
            ax.fill_between(time_points, 50, home_momentum, color=home_color, alpha=0.4, label=home_name)
            ax.fill_between(time_points, 50, away_momentum, color=away_color, alpha=0.4, label=away_name)
            ax.axhline(y=50, color='black', linestyle='--', linewidth=1, alpha=0.5)

            # Mark goals
            goals = events_df[events_df['is_goal'] == True]
            for _, goal in goals.iterrows():
                color = home_color if goal['teamId'] == home_id else away_color
                y_pos = 95 if goal['teamId'] == home_id else 5
                ax.scatter(goal['cumulative_mins'], y_pos, s=200, c=color,
                          marker='o', edgecolors='gold', linewidths=2, zorder=5)

        ax.set_xlim(0, max(time_points) if time_points else 90)
        ax.set_ylim(0, 100)
        ax.set_xlabel('Match Time (minutes)', fontsize=9)
        ax.set_ylabel('Possession %', fontsize=9)
        ax.set_title('Match Momentum', fontsize=12, fontweight='bold')
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.3)

    def create_xg_timeline(self, ax, shots_df, home_id, away_id, home_color, away_color):
        """Create cumulative xG timeline."""
        if shots_df is None or shots_df.empty:
            ax.axis('off')
            ax.text(0.5, 0.5, 'No xG Data', ha='center', va='center')
            return

        home_shots = shots_df[shots_df['teamId'] == home_id].sort_values('cumulative_mins')
        away_shots = shots_df[shots_df['teamId'] == away_id].sort_values('cumulative_mins')

        home_xg_cumsum = home_shots['xg'].cumsum() if 'xg' in home_shots.columns else []
        away_xg_cumsum = away_shots['xg'].cumsum() if 'xg' in away_shots.columns else []

        if len(home_xg_cumsum) > 0:
            ax.plot(home_shots['cumulative_mins'], home_xg_cumsum, color=home_color,
                   linewidth=2, label='Home xG', marker='o', markersize=4)

        if len(away_xg_cumsum) > 0:
            ax.plot(away_shots['cumulative_mins'], away_xg_cumsum, color=away_color,
                   linewidth=2, label='Away xG', marker='o', markersize=4)

        ax.set_xlabel('Match Time (minutes)', fontsize=9)
        ax.set_ylabel('Cumulative xG', fontsize=9)
        ax.set_title('Expected Goals Timeline', fontsize=12, fontweight='bold')
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3)

    def create_zone14_map(self, ax, passes_df, team_color, team_name):
        """Create Zone 14 and half-spaces visualization."""
        from mplsoccer import Pitch
        
        pitch = Pitch(pitch_type='custom', pitch_length=105, pitch_width=68,
                     pitch_color='#d6c39f', line_color='#0e1117', linewidth=1.5)
        pitch.draw(ax=ax)

        # Define zones
        zone14_rect = patches.Rectangle((70, 20.4), 17.5, 27.2, linewidth=2,
                                       edgecolor='#bd841c', facecolor='#bd841c', alpha=0.2, zorder=2)
        left_hs_rect = patches.Rectangle((70, 10.2), 17.5, 17, linewidth=2,
                                        edgecolor=team_color, facecolor=team_color, alpha=0.15, zorder=2)
        right_hs_rect = patches.Rectangle((70, 40.8), 17.5, 17, linewidth=2,
                                         edgecolor=team_color, facecolor=team_color, alpha=0.15, zorder=2)
        
        ax.add_patch(zone14_rect)
        ax.add_patch(left_hs_rect)
        ax.add_patch(right_hs_rect)

        # Plot passes in zones
        if not passes_df.empty:
            zone_passes = passes_df[
                (passes_df['x'] >= 70) & (passes_df['x'] <= 87.5) &
                (((passes_df['y'] >= 20.4) & (passes_df['y'] <= 47.6)) |
                 ((passes_df['y'] >= 10.2) & (passes_df['y'] <= 27.2)) |
                 ((passes_df['y'] >= 40.8) & (passes_df['y'] <= 57.8)))
            ]

            for _, p in zone_passes.iterrows():
                if pd.notna(p.get('endX')) and pd.notna(p.get('endY')):
                    ax.plot([p['x'], p['endX']], [p['y'], p['endY']],
                           color=team_color, linewidth=1.5, alpha=0.5, zorder=3)
                    ax.scatter(p['x'], p['y'], s=30, c=team_color, alpha=0.7, zorder=4)

        ax.set_title(f'{team_name} Zone 14 & Half-Spaces', fontsize=12, fontweight='bold')
