"""
Heatmap Visualizations
Defensive actions, touches, and pressure visualizations.
"""

import matplotlib.pyplot as plt
import numpy as np
from mplsoccer import Pitch
from scipy.ndimage import gaussian_filter
from matplotlib.colors import LinearSegmentedColormap, to_rgba

from Visual.base_visualization import BaseVisualization


class HeatmapVisualizations(BaseVisualization):
    """Create heatmap-based visualizations."""

    def __init__(self, theme_manager=None, pitch_color='#d6c39f', line_color='#0e1117',
                 show_colorbars: bool = True):
        super().__init__(theme_manager, pitch_color, line_color, show_colorbars)

    def _tinted_cmap(self, base_hex: str, dark_bg: bool = False) -> LinearSegmentedColormap:
        """Create a transparent-to-teamcolor ramp colormap."""
        r, g, b, _ = to_rgba(base_hex)
        mid = (min(1.0, r * 0.8 + 0.2), min(1.0, g * 0.8 + 0.2), min(1.0, b * 0.8 + 0.2), 0.6)
        end_alpha = 0.75 if dark_bg else 0.6
        colors = [(r, g, b, 0.0), mid, (r, g, b, end_alpha)]
        return LinearSegmentedColormap.from_list('team_tint', colors)

    def create_defensive_actions_heatmap(self, ax, actions_df, team_color, team_name):
        """Create defensive actions heatmap (team-tinted, optional colorbar)."""
        pitch = self.create_pitch()
        pitch.draw(ax=ax)

        im = None
        if not actions_df.empty and len(actions_df) >= 5:
            x_bins = np.linspace(0, 105, 21)
            y_bins = np.linspace(0, 68, 14)
            
            heatmap, _, _ = np.histogram2d(actions_df['x'].values, actions_df['y'].values, 
                                          bins=[x_bins, y_bins])
            heatmap = gaussian_filter(heatmap, sigma=1.0)
            
            cmap = self._tinted_cmap(team_color, dark_bg=self.is_dark_theme())
            im = ax.imshow(heatmap.T, extent=[0, 105, 0, 68], origin='lower',
                           cmap=cmap, alpha=1.0, aspect='auto', zorder=2)

        self.prepare_axis(ax, f'{team_name} Defensive Actions')

        # Compact colorbar
        if im is not None:
            self.add_colorbar(ax, im, label='Density')

    def create_touch_heatmap(self, ax, events_df, team_color, team_name):
        """Create player touches heatmap (optional colorbar)."""
        pitch = self.create_pitch()
        pitch.draw(ax=ax)

        im = None
        if not events_df.empty and len(events_df) >= 10:
            x_bins = np.linspace(0, 105, 21)
            y_bins = np.linspace(0, 68, 14)
            
            heatmap, _, _ = np.histogram2d(events_df['x'].values, events_df['y'].values,
                                          bins=[x_bins, y_bins])
            heatmap = gaussian_filter(heatmap, sigma=1.5)

            im = ax.imshow(heatmap.T, extent=[0, 105, 0, 68], origin='lower',
                           cmap='YlOrRd', alpha=0.8, aspect='auto', zorder=2)

        self.prepare_axis(ax, f'{team_name} Touch Map')

        if im is not None:
            self.add_colorbar(ax, im, label='Density')

    def create_pitch_control_map(self, ax, home_events, away_events, home_color, away_color):
        """Create pitch control/dominance visualization."""
        pitch = self.create_pitch()
        pitch.draw(ax=ax)

        import matplotlib.patches as patches
        
        x_bins = np.linspace(0, 105, 7)
        y_bins = np.linspace(0, 68, 6)

        for i in range(len(x_bins) - 1):
            for j in range(len(y_bins) - 1):
                x_start, x_end = x_bins[i], x_bins[i + 1]
                y_start, y_end = y_bins[j], y_bins[j + 1]

                home_cnt = len(home_events[
                    (home_events['x'] >= x_start) & (home_events['x'] < x_end) &
                    (home_events['y'] >= y_start) & (home_events['y'] < y_end)
                ])
                away_cnt = len(away_events[
                    (away_events['x'] >= x_start) & (away_events['x'] < x_end) &
                    (away_events['y'] >= y_start) & (away_events['y'] < y_end)
                ])

                total = home_cnt + away_cnt
                if total > 0:
                    home_pct = home_cnt / total
                    if home_pct > 0.6:
                        color, alpha = home_color, 0.2 + (home_pct - 0.6) * 1.5
                    elif home_pct < 0.4:
                        color, alpha = away_color, 0.2 + (0.4 - home_pct) * 1.5
                    else:
                        color, alpha = 'gray', 0.1

                    rect = patches.Rectangle((x_start, y_start), x_end - x_start, y_end - y_start,
                                            facecolor=color, alpha=min(alpha, 0.6), edgecolor='none', zorder=2)
                    ax.add_patch(rect)

        self.prepare_axis(ax, 'Pitch Control')

        # Simple legend blocks (dark friendly)
        try:
            import matplotlib.patches as mpatches
            from matplotlib.lines import Line2D
            home_patch = mpatches.Patch(color=home_color, alpha=0.35, label='Home control')
            away_patch = mpatches.Patch(color=away_color, alpha=0.35, label='Away control')
            neutral_patch = mpatches.Patch(color='gray', alpha=0.15, label='Contested')
            leg = ax.legend(handles=[home_patch, away_patch, neutral_patch],
                            loc='lower center', bbox_to_anchor=(0.5, -0.08), ncol=3,
                            fontsize=8, framealpha=0.9)
        except Exception:
            pass
