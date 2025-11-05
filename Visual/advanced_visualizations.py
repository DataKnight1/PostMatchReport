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
        """Create enhanced match momentum/flow visualization with key events."""
        if events_df is None or events_df.empty:
            ax.axis('off')
            ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center')
            return

        # Filter to regular 90 minutes only (exclude injury/extra time)
        events_df = events_df[events_df['cumulative_mins'] <= 90].copy()

        max_time = min(events_df['cumulative_mins'].max(), 90)
        time_bins = np.arange(0, 91, 1.5)  # Fixed to 90 minutes

        home_momentum, away_momentum, time_points = [], [], []

        # Calculate momentum with weighted events
        for i in range(len(time_bins) - 1):
            window = events_df[
                (events_df['cumulative_mins'] >= time_bins[i]) &
                (events_df['cumulative_mins'] < time_bins[i + 1])
            ]

            if len(window) > 0:
                # Weight dangerous events more heavily
                home_events = window[window['teamId'] == home_id]
                away_events = window[window['teamId'] == away_id]

                # Count with weights
                home_score = len(home_events)
                away_score = len(away_events)

                # Bonus for attacking actions
                home_score += len(home_events[home_events['type_display'].isin(['Shot', 'SavedShot', 'MissedShots'])]) * 2
                away_score += len(away_events[away_events['type_display'].isin(['Shot', 'SavedShot', 'MissedShots'])]) * 2

                total = home_score + away_score
                if total > 0:
                    home_momentum.append((home_score / total) * 100)
                    away_momentum.append((away_score / total) * 100)
                    time_points.append((time_bins[i] + time_bins[i + 1]) / 2)

        if time_points:
            # Smooth the data
            from scipy.ndimage import gaussian_filter1d
            if len(home_momentum) > 5:
                home_momentum = gaussian_filter1d(home_momentum, sigma=1.5)
                away_momentum = gaussian_filter1d(away_momentum, sigma=1.5)

            # Plot with gradient effect
            ax.fill_between(time_points, 50, home_momentum, color=home_color, alpha=0.5, label=home_name)
            ax.fill_between(time_points, 50, away_momentum, color=away_color, alpha=0.5, label=away_name)
            ax.plot(time_points, home_momentum, color=home_color, linewidth=2, alpha=0.8)
            ax.plot(time_points, away_momentum, color=away_color, linewidth=2, alpha=0.8)
            ax.axhline(y=50, color='black', linestyle='--', linewidth=1.5, alpha=0.6)

            # Mark half-time break prominently
            ax.axvline(x=45, color='black', linestyle='-', linewidth=2, alpha=0.4)
            ax.text(45, 102, 'HT', ha='center', fontsize=9, fontweight='bold',
                   color='black', bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

            # Mark goals with annotations
            goals = events_df[events_df['type_display'] == 'Goal']
            for idx, goal in goals.iterrows():
                is_home = goal['teamId'] == home_id
                color = home_color if is_home else away_color
                y_pos = 97 if is_home else 3

                ax.scatter(goal['cumulative_mins'], y_pos, s=250, c=color,
                          marker='*', edgecolors='gold', linewidths=2.5, zorder=5)

                # Add minute label
                ax.text(goal['cumulative_mins'], y_pos, f"{int(goal['minute'])}'",
                       ha='center', va='center', fontsize=7, fontweight='bold',
                       color='white', zorder=6)

            # Mark dangerous moments (shots)
            shots = events_df[events_df['type_display'].isin(['SavedShot', 'MissedShots'])]
            for _, shot in shots.iterrows():
                is_home = shot['teamId'] == home_id
                y_pos = 90 if is_home else 10
                color = home_color if is_home else away_color
                ax.scatter(shot['cumulative_mins'], y_pos, s=30, c=color,
                          marker='o', alpha=0.4, zorder=4)

        # Set x-axis to 0-90 minutes
        ax.set_xlim(0, 90)
        ax.set_ylim(0, 105)
        ax.set_xlabel('Match Time (minutes)', fontsize=9)
        ax.set_ylabel('Momentum %', fontsize=9)
        ax.set_title('Match Momentum & Key Events', fontsize=12, fontweight='bold')
        ax.legend(loc='upper left', fontsize=8, framealpha=0.9)
        ax.grid(True, alpha=0.2, axis='x')

        # Add minute markers
        ax.set_xticks([0, 15, 30, 45, 60, 75, 90])
        ax.set_xticklabels(['0', '15', '30', '45', '60', '75', '90'], fontsize=8)

    def create_xg_timeline(self, ax, shots_df, home_id, away_id, home_color, away_color):
        """Create shot timeline showing when shots were taken."""
        if shots_df is None or shots_df.empty:
            ax.axis('off')
            ax.text(0.5, 0.5, 'No Shot Data', ha='center', va='center', fontsize=11)
            return

        # Filter to 90 minutes for consistency
        shots_df = shots_df[shots_df['cumulative_mins'] <= 90].copy()

        home_shots = shots_df[shots_df['teamId'] == home_id].sort_values('cumulative_mins')
        away_shots = shots_df[shots_df['teamId'] == away_id].sort_values('cumulative_mins')

        # Plot shot events as scatter points
        for _, shot in home_shots.iterrows():
            shot_type = shot.get('type_display', '')
            is_goal = shot_type == 'Goal'
            is_on_target = shot_type in ['SavedShot', 'Goal']

            marker = '*' if is_goal else ('o' if is_on_target else 'x')
            size = 200 if is_goal else 100 if is_on_target else 60
            alpha = 1.0 if is_goal else 0.8 if is_on_target else 0.5
            edge = 'gold' if is_goal else home_color

            ax.scatter(shot['cumulative_mins'], 1, s=size, c=home_color, marker=marker,
                      alpha=alpha, edgecolors=edge, linewidths=2 if is_goal else 1, zorder=3)

        for _, shot in away_shots.iterrows():
            shot_type = shot.get('type_display', '')
            is_goal = shot_type == 'Goal'
            is_on_target = shot_type in ['SavedShot', 'Goal']

            marker = '*' if is_goal else ('o' if is_on_target else 'x')
            size = 200 if is_goal else 100 if is_on_target else 60
            alpha = 1.0 if is_goal else 0.8 if is_on_target else 0.5
            edge = 'gold' if is_goal else away_color

            ax.scatter(shot['cumulative_mins'], 0, s=size, c=away_color, marker=marker,
                      alpha=alpha, edgecolors=edge, linewidths=2 if is_goal else 1, zorder=3)

        # Formatting
        ax.set_xlim(0, 90)
        ax.set_ylim(-0.5, 1.5)
        ax.set_yticks([0, 1])
        ax.set_yticklabels(['Away', 'Home'], fontsize=9)
        ax.set_xlabel('Match Time (minutes)', fontsize=9)
        ax.set_title('Shot Timeline', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.2, axis='x')

        # Mark half-time
        ax.axvline(x=45, color='gray', linestyle='--', linewidth=1.5, alpha=0.5)

        # Add minute markers
        ax.set_xticks([0, 15, 30, 45, 60, 75, 90])
        ax.set_xticklabels(['0', '15', '30', '45', '60', '75', '90'], fontsize=8)

        # Add legend
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker='*', color='w', markerfacecolor='gray', markersize=12,
                  markeredgecolor='gold', markeredgewidth=2, label='Goal'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=10,
                  label='On Target'),
            Line2D([0], [0], marker='x', color='w', markerfacecolor='gray', markersize=8,
                  label='Off Target')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=7, framealpha=0.9)

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
