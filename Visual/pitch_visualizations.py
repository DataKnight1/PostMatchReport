"""
Pitch Visualizations
Shot maps, pass networks, and other pitch-based visualizations.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mplsoccer import Pitch, VerticalPitch
from typing import Optional
from matplotlib.colors import to_rgba


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

    def create_pass_network(self, ax, avg_positions_df, pass_connections_df, team_color, team_name):
        """
        Create enhanced pass network visualization with:
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
        """
        # Use custom pitch (105x68m)
        pitch = Pitch(pitch_type='custom', pitch_length=105, pitch_width=68,
                     pitch_color=self.pitch_color, line_color=self.line_color, linewidth=1.5)
        pitch.draw(ax=ax)

        if avg_positions_df.empty:
            ax.text(52.5, 34, 'No Data Available', ha='center', va='center', fontsize=10)
            ax.set_title(f'{team_name} Pass Network', fontsize=12, fontweight='bold')
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
                for idx, row in pass_connections_df.iterrows():
                    if pd.notna(row.get('x')) and pd.notna(row.get('y')) and \
                       pd.notna(row.get('x_end')) and pd.notna(row.get('y_end')):
                        ax.plot([row['x'], row['x_end']], 
                               [row['y'], row['y_end']],
                               color=color[idx],
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

        ax.set_title(f'{team_name} Pass Network', fontsize=12, fontweight='bold', pad=10)

    def create_pass_network_simple(self, ax, player_positions, pass_connections, team_color, team_name):
        """
        Create simple pass network (old version, kept for compatibility).
        """
        pitch = Pitch(pitch_type='custom', pitch_length=105, pitch_width=68,
                     pitch_color=self.pitch_color, line_color=self.line_color, linewidth=1.5)
        pitch.draw(ax=ax)

        if player_positions.empty:
            ax.text(52.5, 34, 'No Data Available', ha='center', va='center')
            ax.set_title(f'{team_name} Pass Network', fontsize=12, fontweight='bold')
            return

        # Plot pass lines
        if not pass_connections.empty:
            max_passes = pass_connections['pass_count'].max() if 'pass_count' in pass_connections.columns else 1
            for _, conn in pass_connections.iterrows():
                passer = player_positions[player_positions['player_id'] == conn['playerId']] \
                    if 'playerId' in conn else player_positions[player_positions['player_id'] == conn['pos_min']]
                receiver = player_positions[player_positions['player_id'] == conn['receiver']] \
                    if 'receiver' in conn else player_positions[player_positions['player_id'] == conn['pos_max']]
                
                if not passer.empty and not receiver.empty:
                    lw = 0.5 + (conn.get('pass_count', 1) / max_passes) * 4
                    x_col = 'avg_x' if 'avg_x' in passer.columns else 'x'
                    y_col = 'avg_y' if 'avg_y' in passer.columns else 'y'
                    
                    ax.plot([passer.iloc[0][x_col], receiver.iloc[0][x_col]],
                           [passer.iloc[0][y_col], receiver.iloc[0][y_col]],
                           color=team_color, linewidth=lw, alpha=0.6, zorder=1)

        # Plot players
        for _, player in player_positions.iterrows():
            x_col = 'avg_x' if 'avg_x' in player.index else 'x'
            y_col = 'avg_y' if 'avg_y' in player.index else 'y'
            
            ax.scatter(player[x_col], player[y_col], s=600, c=team_color,
                      edgecolors='white', linewidths=2, zorder=3, alpha=0.9)
            
            shirt_no = player.get('shirt_no', '?')
            ax.text(player[x_col], player[y_col], str(shirt_no),
                   ha='center', va='center', fontsize=9, fontweight='bold',
                   color='white', zorder=4)

        ax.set_title(f'{team_name} Pass Network', fontsize=12, fontweight='bold')
