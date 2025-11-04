"""
Statistical Visualizations
Bar charts, line graphs, and statistical comparisons.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class StatisticalVisualizations:
    """Create statistical visualizations."""

    def create_match_summary_panel(self, ax, match_info):
        """Create match summary statistics panel."""
        ax.axis('off')

        home_name = match_info.get('teams', {}).get('home', {}).get('name', 'Home')
        away_name = match_info.get('teams', {}).get('away', {}).get('name', 'Away')
        home_score = match_info.get('match_info', {}).get('score', '0:0').split(':')[0]
        away_score = match_info.get('match_info', {}).get('score', '0:0').split(':')[1]

        title = f"{home_name} {home_score} - {away_score} {away_name}"
        ax.text(0.5, 0.95, title, ha='center', va='top', fontsize=16, fontweight='bold')

        subtitle = f"{match_info.get('match_info', {}).get('venue', 'Venue')} | {match_info.get('match_info', {}).get('date', '')[:10]}"
        ax.text(0.5, 0.88, subtitle, ha='center', va='top', fontsize=10)

        # Stats
        stats_y, line_height = 0.75, 0.08
        
        stats = [
            ('Possession', f"{match_info.get('possession', {}).get('home', 50):.0f}%",
             f"{match_info.get('possession', {}).get('away', 50):.0f}%"),
            ('xG', f"{match_info.get('xg', {}).get('home_xg', 0):.2f}",
             f"{match_info.get('xg', {}).get('away_xg', 0):.2f}"),
        ]

        home_color = match_info.get('team_colors', {}).get('home_color', '#FF0000')
        away_color = match_info.get('team_colors', {}).get('away_color', '#0000FF')

        for stat_name, home_val, away_val in stats:
            ax.text(0.5, stats_y, stat_name, ha='center', fontsize=11, fontweight='bold')
            ax.text(0.25, stats_y, home_val, ha='center', fontsize=11, color=home_color, fontweight='bold')
            ax.text(0.75, stats_y, away_val, ha='center', fontsize=11, color=away_color, fontweight='bold')
            stats_y -= line_height

    def create_stats_comparison_bars(self, ax, team_stats, stat_name, home_color, away_color):
        """Create horizontal bar chart comparing team stats."""
        home_val = team_stats.get('home', {}).get(stat_name, 0)
        away_val = team_stats.get('away', {}).get(stat_name, 0)

        y_pos = [0, 1]
        values = [home_val, away_val]
        colors = [home_color, away_color]

        ax.barh(y_pos, values, color=colors, alpha=0.7)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(['Home', 'Away'])
        ax.set_xlabel(stat_name)
        ax.set_title(f'{stat_name} Comparison', fontweight='bold')
        
        for i, v in enumerate(values):
            ax.text(v, i, f' {v}', va='center', fontweight='bold')
