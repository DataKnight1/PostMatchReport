"""
Statistical Visualizations
Bar charts, line graphs, and statistical comparisons.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.patches as patches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
import os

from Visual.base_visualization import BaseVisualization


class StatisticalVisualizations(BaseVisualization):
    """Create statistical visualizations."""

    def __init__(self, theme_manager=None, pitch_color='#d6c39f', line_color='#0e1117',
                 show_colorbars: bool = True):
        super().__init__(theme_manager, pitch_color, line_color, show_colorbars)

    def create_match_summary_panel(self, ax, match_info, text_color: str = None, rows: list | None = None):
        """Create match summary statistics panel.

        Args:
            ax: Matplotlib axis
            match_info: Summary dict from MatchProcessor
            text_color: Base text color (deprecated - uses theme if None)
            rows: Optional list of (label, home_value, away_value). If None, a sensible default is computed.
        """
        # Use theme color if not explicitly provided
        if text_color is None:
            text_color = self.get_text_color()

        ax.axis('off')

        home_name = match_info.get('teams', {}).get('home', {}).get('name', 'Home')
        away_name = match_info.get('teams', {}).get('away', {}).get('name', 'Away')

        score_text = match_info.get('match_info', {}).get('score', '0 : 0')
        try:
            parts = [p.strip() for p in score_text.split(':')]
            home_score = parts[0]
            away_score = parts[1]
        except Exception:
            home_score, away_score = '0', '0'

        title = f"{home_name} {home_score} - {away_score} {away_name}"
        ax.text(0.5, 0.94, title, ha='center', va='top', fontsize=18, fontweight='bold', color=text_color)

        subtitle = f"{match_info.get('match_info', {}).get('venue', 'Venue')} | {match_info.get('match_info', {}).get('date', '')[:10]}"
        ax.text(0.5, 0.89, subtitle, ha='center', va='top', fontsize=10, color=text_color, alpha=0.9)

        # Team crests or initials badges (optional)
        logos = match_info.get('team_logos', {}) if isinstance(match_info, dict) else {}
        home_logo = logos.get('home') if isinstance(logos, dict) else None
        away_logo = logos.get('away') if isinstance(logos, dict) else None

        team_colors = match_info.get('team_colors', {}) if isinstance(match_info, dict) else {}
        home_col = team_colors.get('home_color', '#FF0000')
        away_col = team_colors.get('away_color', '#0000FF')

        def draw_badge(x, y, logo_path, initials, facecolor):
            if logo_path and os.path.isfile(logo_path):
                try:
                    img = mpimg.imread(logo_path)
                    oi = OffsetImage(img, zoom=0.2)
                    ab = AnnotationBbox(oi, (x, y), frameon=False, xycoords=ax.transAxes)
                    ax.add_artist(ab)
                    return
                except Exception:
                    pass
            circ = patches.Circle((x, y), 0.035, transform=ax.transAxes, facecolor=facecolor, edgecolor='white', linewidth=1.2)
            ax.add_patch(circ)
            ax.text(x, y, initials, ha='center', va='center', color='white', fontsize=10, fontweight='bold', transform=ax.transAxes)

        def initials_from(name: str) -> str:
            parts = [p for p in str(name).split() if p]
            if not parts:
                return '??'
            if len(parts) == 1:
                return parts[0][:2].upper()
            return (parts[0][0] + parts[-1][0]).upper()

        draw_badge(0.08, 0.935, home_logo, initials_from(home_name), home_col)
        draw_badge(0.92, 0.935, away_logo, initials_from(away_name), away_col)

        # Stats block layout (moved lower to avoid overlap with bars)
        stats_y, line_height = 0.60, 0.08

        # Get team stats
        team_stats = match_info.get('team_stats', {})
        home_stats = team_stats.get('home', {})
        away_stats = team_stats.get('away', {})

        # Get shots data (use FotMob if available, otherwise from event data)
        shots_data = match_info.get('shots_data', {})
        home_shots = shots_data.get('home_shots', 0) if shots_data else 0
        away_shots = shots_data.get('away_shots', 0) if shots_data else 0

        # Build default rows if not provided
        if rows is None:
            hp = home_stats.get('passing', {})
            ap = away_stats.get('passing', {})
            hd = home_stats.get('defensive', {})
            ad = away_stats.get('defensive', {})
            hs = home_stats.get('shooting', {})
            as_ = away_stats.get('shooting', {})
            # Compose values with good formatting
            def fmt_passes(p):
                return f"{int(p.get('completed_passes', 0))}/{int(p.get('total_passes', 0))}"
            def pct(x):
                try:
                    return f"{float(x):.1f}%"
                except Exception:
                    return f"{x}"
            # Prefer transformer shooting totals over FotMob shot summary if present
            if isinstance(hs, dict) and 'total_shots' in hs and isinstance(as_, dict) and 'total_shots' in as_:
                home_shots = hs.get('total_shots', home_shots)
                away_shots = as_.get('total_shots', away_shots)
            rows = [
                ('Possession', f"{match_info.get('possession', {}).get('home', 50):.0f}%",
                 f"{match_info.get('possession', {}).get('away', 50):.0f}%"),
                ('xG', f"{match_info.get('xg', {}).get('home_xg', 0):.2f}",
                 f"{match_info.get('xg', {}).get('away_xg', 0):.2f}"),
                ('Shots', f"{home_shots}", f"{away_shots}"),
                ('Shots on Target', f"{hs.get('shots_on_target', 0)}", f"{as_.get('shots_on_target', 0)}"),
                ('Passes Completed', fmt_passes(hp), fmt_passes(ap)),
                ('Pass Accuracy', pct(hp.get('pass_accuracy', 0)), pct(ap.get('pass_accuracy', 0))),
                ('Key Passes', f"{hp.get('key_passes', 0)}", f"{ap.get('key_passes', 0)}"),
                ('Assists', f"{hp.get('assists', 0)}", f"{ap.get('assists', 0)}"),
                ('Tackles', f"{hd.get('tackles', 0)}", f"{ad.get('tackles', 0)}"),
                ('Interceptions', f"{hd.get('interceptions', 0)}", f"{ad.get('interceptions', 0)}"),
                ('Clearances', f"{hd.get('clearances', 0)}", f"{ad.get('clearances', 0)}"),
                ('Blocks', f"{hd.get('blocked_passes', 0)}", f"{ad.get('blocked_passes', 0)}"),
            ]

        home_color = match_info.get('team_colors', {}).get('home_color', '#FF0000')
        away_color = match_info.get('team_colors', {}).get('away_color', '#0000FF')

        # Compact bars for Possession and xG (dark-friendly)
        try:
            home_pos = float(match_info.get('possession', {}).get('home', 50.0))
            away_pos = 100.0 - home_pos
        except Exception:
            home_pos, away_pos = 50.0, 50.0
        home_xg = float(match_info.get('xg', {}).get('home_xg', 0.0))
        away_xg = float(match_info.get('xg', {}).get('away_xg', 0.0))
        tot_xg = max(home_xg + away_xg, 0.0001)

        # Get bar background color from theme
        bar_bg_color = self.theme.get_color('surface') if self.is_dark_theme() else '#e0e0e0'

        # Possession bar
        ax.text(0.1, 0.80, 'Possession', color=text_color, fontsize=10, transform=ax.transAxes)
        ax.add_patch(patches.Rectangle((0.1, 0.76), 0.8, 0.04, transform=ax.transAxes,
                                       facecolor=bar_bg_color, edgecolor='none', zorder=0))
        ax.add_patch(patches.Rectangle((0.1, 0.76), 0.8 * (home_pos/100.0), 0.04, transform=ax.transAxes,
                                       facecolor=home_color, alpha=0.6, edgecolor='none', zorder=1))
        ax.text(0.1, 0.755, f"{home_pos:.0f}%", color=text_color, fontsize=9, fontweight='bold', transform=ax.transAxes)
        ax.text(0.9, 0.755, f"{away_pos:.0f}%", color=text_color, fontsize=9, fontweight='bold', ha='right', transform=ax.transAxes)

        # xG bar
        ax.text(0.1, 0.71, 'xG', color=text_color, fontsize=10, transform=ax.transAxes)
        ax.add_patch(patches.Rectangle((0.1, 0.67), 0.8, 0.04, transform=ax.transAxes,
                                       facecolor=bar_bg_color, edgecolor='none', zorder=0))
        ax.add_patch(patches.Rectangle((0.1, 0.67), 0.8 * (home_xg/tot_xg), 0.04, transform=ax.transAxes,
                                       facecolor=home_color, alpha=0.6, edgecolor='none', zorder=1))
        ax.text(0.1, 0.665, f"{home_xg:.2f}", color=text_color, fontsize=9, fontweight='bold', transform=ax.transAxes)
        ax.text(0.9, 0.665, f"{away_xg:.2f}", color=text_color, fontsize=9, fontweight='bold', ha='right', transform=ax.transAxes)

        # Column headers with team logos above the table
        logos = match_info.get('team_logos', {}) if isinstance(match_info, dict) else {}
        x_home, x_stat, x_away = 0.25, 0.5, 0.75
        header_y = stats_y + 0.04

        # small logo helpers
        def draw_small_badge(x, y, logo_path, initials, facecolor):
            if logo_path and os.path.isfile(logo_path):
                try:
                    img = mpimg.imread(logo_path)
                    oi = OffsetImage(img, zoom=0.12)
                    ab = AnnotationBbox(oi, (x, y), frameon=False, xycoords=ax.transAxes)
                    ax.add_artist(ab)
                    return
                except Exception:
                    pass
            circ = patches.Circle((x, y), 0.02, transform=ax.transAxes, facecolor=facecolor, edgecolor='white', linewidth=0.8)
            ax.add_patch(circ)
            ax.text(x, y, initials, ha='center', va='center', color='white', fontsize=7, fontweight='bold', transform=ax.transAxes)

        draw_small_badge(x_home, header_y, logos.get('home'), initials_from(home_name), home_col)
        draw_small_badge(x_away, header_y, logos.get('away'), initials_from(away_name), away_col)
        ax.text(x_stat, header_y, 'Team Stats', ha='center', va='center', fontsize=10, color=text_color, transform=ax.transAxes)

        # Draw zebra row backgrounds and aligned text using theme colors
        is_dark = self.is_dark_theme()
        # Use theme surface color for main row background
        row_bg = self.theme.get_color('surface')
        # Slightly lighter/darker for alternate rows
        alt_row_bg = self.theme.get_color('background') if is_dark else '#f5f5f5'

        def _fmt(v):
            s = str(v)
            # remove stray spaces inside numeric strings like "85 .4%"
            if any(ch.isdigit() for ch in s):
                s = s.replace(' ', '')
            return s

        for i, (stat_name, home_val, away_val) in enumerate(rows):
            # Background stripe
            y0 = stats_y - (line_height / 2) + 0.01
            rect_color = row_bg if i % 2 == 0 else alt_row_bg
            ax.add_patch(patches.Rectangle((0.1, y0), 0.8, line_height - 0.02,
                                           transform=ax.transAxes, facecolor=rect_color,
                                           edgecolor='none', zorder=0))

            # Text values - use text_color for better visibility on all backgrounds
            ax.text(x_stat, stats_y, stat_name, ha='center', va='center', fontsize=10,
                    fontweight='bold', color=text_color, zorder=1, transform=ax.transAxes)
            # Right align home, left align away - use text color for visibility
            ax.text(x_home-0.02, stats_y, _fmt(home_val), ha='right', va='center', fontsize=10,
                    color=text_color, fontweight='bold', zorder=1, transform=ax.transAxes)
            ax.text(x_away+0.02, stats_y, _fmt(away_val), ha='left', va='center', fontsize=10,
                    color=text_color, fontweight='bold', zorder=1, transform=ax.transAxes)
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
        self.prepare_axis(ax, f'{stat_name} Comparison')

        for i, v in enumerate(values):
            ax.text(v, i, f' {v}', va='center', fontweight='bold')




