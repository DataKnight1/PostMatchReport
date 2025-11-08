"""
Tactical Visualizations
Creates tactical analysis visualizations like zonal control maps.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Rectangle, Arc, Polygon
from mplsoccer import Pitch
from typing import Dict, Any, Optional


class TacticalVisualizer:
    """Create tactical analysis visualizations."""

    def __init__(self):
        """Initialize tactical visualizer."""
        pass

    def create_zonal_control_map(self, ax, zone_matrix: np.ndarray,
                                 home_team: Dict[str, Any], away_team: Dict[str, Any],
                                 home_color: str = '#0000FF', away_color: str = '#FF0000',
                                 home_attack_dir: str = 'right', away_attack_dir: str = 'left'):
        """
        Create flat, minimalist zonal control visualization.

        Args:
            ax: Matplotlib axis
            zone_matrix: 2D array with 'H', 'A', or 'C' for each zone
            home_team: Home team info dict with 'name' key
            away_team: Away team info dict with 'name' key
            home_color: Home team color (hex)
            away_color: Away team color (hex)
            home_attack_dir: Home team attack direction ('left' or 'right')
            away_attack_dir: Away team attack direction ('left' or 'right')
        """
        # Clear axis
        ax.clear()
        ax.set_xlim(-5, 110)
        ax.set_ylim(-5, 73)
        ax.set_aspect('equal')
        ax.axis('off')

        # Set background
        ax.set_facecolor('#f5f5f5')

        # Pitch dimensions
        pitch_length = 105.0
        pitch_width = 68.0

        # Get grid dimensions from zone_matrix
        grid_rows, grid_cols = zone_matrix.shape

        # Zone dimensions
        zone_length = pitch_length / grid_cols
        zone_width = pitch_width / grid_rows

        # Define colors
        contested_color = '#d0d0d0'

        # Draw zone fills first (background layer)
        for row in range(grid_rows):
            for col in range(grid_cols):
                x_min = col * zone_length
                y_min = row * zone_width

                control = zone_matrix[row, col]

                # Determine fill color
                if control == 'H':
                    fill_color = home_color
                    alpha = 0.3
                elif control == 'A':
                    fill_color = away_color
                    alpha = 0.3
                else:  # 'C' for contested
                    fill_color = contested_color
                    alpha = 0.2

                # Draw zone rectangle
                rect = Rectangle((x_min, y_min), zone_length, zone_width,
                               facecolor=fill_color, edgecolor='none',
                               alpha=alpha, zorder=1)
                ax.add_patch(rect)

        # Draw pitch markings (on top of zones)
        self._draw_pitch_markings(ax, pitch_length, pitch_width)

        # Draw grid lines
        for i in range(grid_cols + 1):
            x = i * zone_length
            ax.plot([x, x], [0, pitch_width], color='#333333',
                   linewidth=0.8, alpha=0.4, zorder=3)

        for i in range(grid_rows + 1):
            y = i * zone_width
            ax.plot([0, pitch_length], [y, y], color='#333333',
                   linewidth=0.8, alpha=0.4, zorder=3)

        # Add title
        title_text = 'Zonal Control by Touches'
        ax.text(pitch_length / 2, pitch_width + 4, title_text,
               ha='center', va='bottom', fontsize=16, fontweight='bold',
               color='#333333')

        # Add team names with attack direction arrows
        home_name = home_team.get('name', 'Home')
        away_name = away_team.get('name', 'Away')

        # Home team (left side)
        arrow_symbol_home = '→' if home_attack_dir == 'right' else '←'
        ax.text(-3, pitch_width / 2, f"{home_name} {arrow_symbol_home}",
               ha='right', va='center', fontsize=11, fontweight='bold',
               color=home_color, rotation=90)

        # Away team (right side)
        arrow_symbol_away = '←' if away_attack_dir == 'left' else '→'
        ax.text(pitch_length + 3, pitch_width / 2, f"{arrow_symbol_away} {away_name}",
               ha='left', va='center', fontsize=11, fontweight='bold',
               color=away_color, rotation=90)

        # Add legend at bottom
        legend_y = -3
        legend_x_start = pitch_length / 2 - 20

        # Home legend
        legend_rect_home = Rectangle((legend_x_start, legend_y), 3, 2,
                                     facecolor=home_color, edgecolor='black',
                                     alpha=0.3, linewidth=0.5)
        ax.add_patch(legend_rect_home)
        ax.text(legend_x_start + 4, legend_y + 1, home_name,
               ha='left', va='center', fontsize=9, color='black', fontweight='bold')

        # Away legend
        legend_rect_away = Rectangle((legend_x_start + 15, legend_y), 3, 2,
                                     facecolor=away_color, edgecolor='black',
                                     alpha=0.3, linewidth=0.5)
        ax.add_patch(legend_rect_away)
        ax.text(legend_x_start + 19, legend_y + 1, away_name,
               ha='left', va='center', fontsize=9, color='black', fontweight='bold')

        # Contested legend
        legend_rect_contested = Rectangle((legend_x_start + 30, legend_y), 3, 2,
                                         facecolor=contested_color, edgecolor='black',
                                         alpha=0.2, linewidth=0.5)
        ax.add_patch(legend_rect_contested)
        ax.text(legend_x_start + 34, legend_y + 1, 'Contested',
               ha='left', va='center', fontsize=9, color='black', fontweight='bold')

        # Add footer note
        footer_text = f'Grid: {grid_cols}×{grid_rows} zones | Control based on touch count'
        ax.text(pitch_length / 2, -4.5, footer_text,
               ha='center', va='top', fontsize=8, color='#666666',
               style='italic')

    def _draw_pitch_markings(self, ax, length: float = 105.0, width: float = 68.0):
        """
        Draw standard football pitch markings.

        Args:
            ax: Matplotlib axis
            length: Pitch length (default 105m)
            width: Pitch width (default 68m)
        """
        # Pitch outline
        ax.plot([0, length], [0, 0], color='white', linewidth=2, zorder=2)
        ax.plot([0, length], [width, width], color='white', linewidth=2, zorder=2)
        ax.plot([0, 0], [0, width], color='white', linewidth=2, zorder=2)
        ax.plot([length, length], [0, width], color='white', linewidth=2, zorder=2)

        # Halfway line
        ax.plot([length/2, length/2], [0, width], color='white', linewidth=2, zorder=2)

        # Center circle
        center_circle = Circle((length/2, width/2), 9.15, fill=False,
                              edgecolor='white', linewidth=2, zorder=2)
        ax.add_patch(center_circle)

        # Center spot
        center_spot = Circle((length/2, width/2), 0.5, fill=True,
                            facecolor='white', edgecolor='none', zorder=2)
        ax.add_patch(center_spot)

        # Left penalty area
        ax.plot([0, 16.5], [13.84, 13.84], color='white', linewidth=2, zorder=2)
        ax.plot([0, 16.5], [width-13.84, width-13.84], color='white', linewidth=2, zorder=2)
        ax.plot([16.5, 16.5], [13.84, width-13.84], color='white', linewidth=2, zorder=2)

        # Right penalty area
        ax.plot([length-16.5, length], [13.84, 13.84], color='white', linewidth=2, zorder=2)
        ax.plot([length-16.5, length], [width-13.84, width-13.84], color='white', linewidth=2, zorder=2)
        ax.plot([length-16.5, length-16.5], [13.84, width-13.84], color='white', linewidth=2, zorder=2)

        # Left six-yard box
        ax.plot([0, 5.5], [24.84, 24.84], color='white', linewidth=2, zorder=2)
        ax.plot([0, 5.5], [width-24.84, width-24.84], color='white', linewidth=2, zorder=2)
        ax.plot([5.5, 5.5], [24.84, width-24.84], color='white', linewidth=2, zorder=2)

        # Right six-yard box
        ax.plot([length-5.5, length], [24.84, 24.84], color='white', linewidth=2, zorder=2)
        ax.plot([length-5.5, length], [width-24.84, width-24.84], color='white', linewidth=2, zorder=2)
        ax.plot([length-5.5, length-5.5], [24.84, width-24.84], color='white', linewidth=2, zorder=2)

        # Penalty spots
        left_penalty_spot = Circle((11, width/2), 0.5, fill=True,
                                  facecolor='white', edgecolor='none', zorder=2)
        ax.add_patch(left_penalty_spot)

        right_penalty_spot = Circle((length-11, width/2), 0.5, fill=True,
                                   facecolor='white', edgecolor='none', zorder=2)
        ax.add_patch(right_penalty_spot)

        # Penalty arcs (18-yard box arcs)
        left_arc = Arc((11, width/2), 18.3, 18.3, angle=0, theta1=308, theta2=52,
                      edgecolor='white', linewidth=2, fill=False, zorder=2)
        ax.add_patch(left_arc)

        right_arc = Arc((length-11, width/2), 18.3, 18.3, angle=0, theta1=128, theta2=232,
                       edgecolor='white', linewidth=2, fill=False, zorder=2)
        ax.add_patch(right_arc)

        # Goals
        ax.plot([-2, 0], [width/2-3.66, width/2-3.66], color='white', linewidth=2, zorder=2)
        ax.plot([-2, 0], [width/2+3.66, width/2+3.66], color='white', linewidth=2, zorder=2)
        ax.plot([-2, -2], [width/2-3.66, width/2+3.66], color='white', linewidth=2, zorder=2)

        ax.plot([length, length+2], [width/2-3.66, width/2-3.66], color='white', linewidth=2, zorder=2)
        ax.plot([length, length+2], [width/2+3.66, width/2+3.66], color='white', linewidth=2, zorder=2)
        ax.plot([length+2, length+2], [width/2-3.66, width/2+3.66], color='white', linewidth=2, zorder=2)
