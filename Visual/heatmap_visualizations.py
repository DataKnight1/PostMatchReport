"""
Heatmap Visualizations
Defensive actions, touches, and pressure visualizations.
"""

import matplotlib.pyplot as plt
import numpy as np
from mplsoccer import Pitch
from scipy.ndimage import gaussian_filter


class HeatmapVisualizations:
    """Create heatmap-based visualizations."""

    def __init__(self, pitch_color='#d6c39f', line_color='#0e1117'):
        self.pitch_color = pitch_color
        self.line_color = line_color

    def create_defensive_actions_heatmap(self, ax, actions_df, team_color, team_name):
        """Create defensive actions heatmap."""
        pitch = Pitch(pitch_type='custom', pitch_length=105, pitch_width=68,
                     pitch_color=self.pitch_color, line_color=self.line_color, linewidth=1.5)
        pitch.draw(ax=ax)

        if not actions_df.empty and len(actions_df) >= 5:
            x_bins = np.linspace(0, 105, 21)
            y_bins = np.linspace(0, 68, 14)
            
            heatmap, _, _ = np.histogram2d(actions_df['x'].values, actions_df['y'].values, 
                                          bins=[x_bins, y_bins])
            heatmap = gaussian_filter(heatmap, sigma=1.0)
            
            ax.imshow(heatmap.T, extent=[0, 105, 0, 68], origin='lower',
                     cmap='Reds', alpha=0.6, aspect='auto', zorder=2)

        ax.set_title(f'{team_name} Defensive Actions', fontsize=12, fontweight='bold')

    def create_touch_heatmap(self, ax, events_df, team_color, team_name):
        """Create player touches heatmap."""
        pitch = Pitch(pitch_type='custom', pitch_length=105, pitch_width=68,
                     pitch_color=self.pitch_color, line_color=self.line_color, linewidth=1.5)
        pitch.draw(ax=ax)

        if not events_df.empty and len(events_df) >= 10:
            x_bins = np.linspace(0, 105, 21)
            y_bins = np.linspace(0, 68, 14)
            
            heatmap, _, _ = np.histogram2d(events_df['x'].values, events_df['y'].values,
                                          bins=[x_bins, y_bins])
            heatmap = gaussian_filter(heatmap, sigma=1.5)
            
            ax.imshow(heatmap.T, extent=[0, 105, 0, 68], origin='lower',
                     cmap='YlOrRd', alpha=0.6, aspect='auto', zorder=2)

        ax.set_title(f'{team_name} Touch Map', fontsize=12, fontweight='bold')

    def create_pitch_control_map(self, ax, home_events, away_events, home_color, away_color):
        """Create pitch control/dominance visualization."""
        pitch = Pitch(pitch_type='custom', pitch_length=105, pitch_width=68,
                     pitch_color=self.pitch_color, line_color=self.line_color, linewidth=1.5)
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

        ax.set_title('Pitch Control', fontsize=12, fontweight='bold')
