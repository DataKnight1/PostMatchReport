"""
Pitch Visualizations
Shot maps, pass networks, and other pitch-based visualizations.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mplsoccer import Pitch, VerticalPitch
from typing import Optional


class PitchVisualizations:
    """Create pitch-based visualizations."""

    def __init__(self, pitch_color='#d6c39f', line_color='#0e1117'):
        self.pitch_color = pitch_color
        self.line_color = line_color

    def create_shot_map(self, ax, shots_home, shots_away, home_color, away_color):
        """Create shot map with xG visualization."""
        pitch = VerticalPitch(pitch_type='custom', pitch_length=105, pitch_width=68,
                             pitch_color=self.pitch_color, line_color=self.line_color, linewidth=1.5)
        pitch.draw(ax=ax)

        # Plot home shots (bottom)
        for _, shot in shots_home.iterrows():
            marker = '*' if shot.get('is_goal') else ('o' if shot.get('is_successful') else 'x')
            size = 400 if shot.get('is_goal') else 200 if shot.get('is_successful') else 150
            edge = 'gold' if shot.get('is_goal') else home_color
            alpha = 0.4 + (0.6 * shot.get('xg', 0))
            
            ax.scatter(shot['x'], shot['y'], s=size, c=home_color, marker=marker,
                      alpha=alpha, edgecolors=edge, linewidths=2, zorder=3)

        # Plot away shots (top, mirrored)
        for _, shot in shots_away.iterrows():
            marker = '*' if shot.get('is_goal') else ('o' if shot.get('is_successful') else 'x')
            size = 400 if shot.get('is_goal') else 200 if shot.get('is_successful') else 150
            edge = 'gold' if shot.get('is_goal') else away_color
            alpha = 0.4 + (0.6 * shot.get('xg', 0))
            
            ax.scatter(105-shot['x'], 68-shot['y'], s=size, c=away_color, marker=marker,
                      alpha=alpha, edgecolors=edge, linewidths=2, zorder=3)

        ax.set_title('Shot Map', fontsize=12, fontweight='bold', pad=10)

    def create_pass_network(self, ax, player_positions, pass_connections, team_color, team_name):
        """Create pass network visualization."""
        pitch = Pitch(pitch_type='custom', pitch_length=105, pitch_width=68,
                     pitch_color=self.pitch_color, line_color=self.line_color, linewidth=1.5)
        pitch.draw(ax=ax)

        if player_positions.empty:
            ax.text(52.5, 34, 'No Data Available', ha='center', va='center')
            ax.set_title(f'{team_name} Pass Network', fontsize=12, fontweight='bold')
            return

        # Plot pass lines
        if not pass_connections.empty:
            max_passes = pass_connections['pass_count'].max()
            for _, conn in pass_connections.iterrows():
                passer = player_positions[player_positions['player_id'] == conn['playerId']]
                receiver = player_positions[player_positions['player_id'] == conn['receiver']]
                
                if not passer.empty and not receiver.empty:
                    lw = 0.5 + (conn['pass_count'] / max_passes) * 4
                    ax.plot([passer.iloc[0]['avg_x'], receiver.iloc[0]['avg_x']],
                           [passer.iloc[0]['avg_y'], receiver.iloc[0]['avg_y']],
                           color=team_color, linewidth=lw, alpha=0.6, zorder=1)

        # Plot players
        for _, player in player_positions.iterrows():
            ax.scatter(player['avg_x'], player['avg_y'], s=600, c=team_color,
                      edgecolors='white', linewidths=2, zorder=3, alpha=0.9)
            ax.text(player['avg_x'], player['avg_y'], str(player.get('shirt_no', '?')),
                   ha='center', va='center', fontsize=9, fontweight='bold',
                   color='white', zorder=4)

        ax.set_title(f'{team_name} Pass Network', fontsize=12, fontweight='bold')
