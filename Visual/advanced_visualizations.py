"""
Advanced Visualizations
Momentum graphs, xG timelines, and advanced analytics.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.patches as patches

from Visual.base_visualization import BaseVisualization


class AdvancedVisualizations(BaseVisualization):
    """Create advanced analytical visualizations."""

    def __init__(self, theme_manager=None, pitch_color: str = '#d6c39f',
                 line_color: str = '#0e1117', show_colorbars: bool = True):
        super().__init__(theme_manager, pitch_color, line_color, show_colorbars)

    def create_momentum_graph(self, ax, events_df, home_id, away_id, home_color, away_color, home_name, away_name):
        """Net momentum around zero using weighted attacking actions.

        Positive values favor home; negative favor away. Stable and less noisy.
        """
        if events_df is None or events_df.empty:
            ax.axis('off')
            ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center',
                   color=self.get_text_color())
            return

        df = events_df[events_df['cumulative_mins'] <= 90].copy()
        df['weight'] = 0.0
        shot_mask = df['type_display'].isin(['Shot', 'SavedShot', 'MissedShots', 'ShotOnPost', 'Goal'])
        keypass_mask = df['is_key_pass'] if 'is_key_pass' in df.columns else None
        in_final_third = df['x'].fillna(0) >= 70
        in_box = (df['x'].fillna(0) >= 88.5) & (df['y'].fillna(0) >= 13.8) & (df['y'].fillna(0) <= 54.2)

        df.loc[in_final_third, 'weight'] += 1.0
        df.loc[in_box, 'weight'] += 1.0
        if keypass_mask is not None:
            try:
                df.loc[keypass_mask == True, 'weight'] += 2.0
            except Exception:
                pass
        df.loc[shot_mask, 'weight'] += 5.0 + (df.loc[shot_mask, 'xg'].fillna(0.0).clip(0, 1) * 5.0)

        bins = np.arange(0, 91, 1.0)
        centers = (bins[:-1] + bins[1:]) / 2.0
        home_series, away_series = [], []
        for i in range(len(bins) - 1):
            w = df[(df['cumulative_mins'] >= bins[i]) & (df['cumulative_mins'] < bins[i+1])]
            home_series.append(w[w['teamId'] == home_id]['weight'].sum())
            away_series.append(w[w['teamId'] == away_id]['weight'].sum())

        import numpy as _np
        home_series = _np.array(home_series)
        away_series = _np.array(away_series)
        denom = home_series + away_series
        net = _np.where(denom > 0, (home_series - away_series) / denom * 100.0, 0.0)

        try:
            from scipy.ndimage import gaussian_filter1d
            if len(net) > 5:
                net = gaussian_filter1d(net, sigma=1.0)
        except Exception:
            pass

        ax.axhline(0, color='#9aa6b2', linestyle='--', linewidth=1.2, alpha=0.6)
        ax.fill_between(centers, 0, net, where=net>=0, color=home_color, alpha=0.45, label=home_name)
        ax.fill_between(centers, 0, net, where=net<0, color=away_color, alpha=0.45, label=away_name)
        ax.plot(centers, net, color=home_color if (_np.nanmean(net) if hasattr(_np, 'nanmean') else 0) >= 0 else away_color, linewidth=1.4, alpha=0.9)

        ax.axvline(45, color='#9aa6b2', linestyle='-', linewidth=1.0, alpha=0.6)
        ax.text(45, 95, 'HT', ha='center', va='center', fontsize=8,
                color=self.get_text_color())

        goals = df[df['type_display'] == 'Goal']
        for _, g in goals.iterrows():
            is_home = g['teamId'] == home_id
            y = 80 if is_home else -80
            ax.scatter(g['cumulative_mins'], y, s=160, c=(home_color if is_home else away_color),
                       marker='*', edgecolors='gold', linewidths=1.8, zorder=4)
            lbl = f"{int(g.get('minute', g['cumulative_mins']))}'"
            ax.text(g['cumulative_mins'], y, lbl, fontsize=7,
                    ha='center', va='center', color=self.get_text_color())

        ax.set_xlim(0, 90)
        ax.set_ylim(-100, 100)
        ax.set_yticks([-100, -50, 0, 50, 100])
        ax.set_yticklabels(['Away', '', 'Even', '', 'Home'])
        ax.set_xlabel('Match Time (minutes)')
        ax.set_ylabel('Net Momentum')
        self.prepare_axis(ax, 'Match Momentum (net)')
        ax.legend(loc='upper left', fontsize=8, framealpha=0.9)
        ax.grid(True, alpha=0.15, axis='x')

    def create_xg_timeline(self, ax, shots_df, home_id, away_id, home_color, away_color):
        """Create shot timeline showing when shots were taken."""
        if shots_df is None or shots_df.empty:
            ax.axis('off')
            ax.text(0.5, 0.5, 'No Shot Data', ha='center', va='center', fontsize=11,
                   color=self.get_text_color())
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
        self.prepare_axis(ax, 'Shot Timeline')
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
        pitch = self.create_pitch()
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

        self.prepare_axis(ax, f'{team_name} Zone 14 & Half-Spaces')

    def create_cumulative_xg(self, ax, shots_df, home_id, away_id,
                              home_color, away_color, home_name, away_name):
        """Cumulative xG step chart per team with goal markers.

        Uses shot events with columns: teamId, cumulative_mins, xg, type_display.
        """
        if shots_df is None or shots_df.empty:
            ax.axis('off')
            ax.text(0.5, 0.5, 'No Shot Data', ha='center', va='center', fontsize=11,
                   color=self.get_text_color())
            return

        cols = ['teamId', 'cumulative_mins', 'xg', 'type_display', 'x', 'y', 'qualifiers_dict', 'dist_to_goal', 'angle', 'outcome_display']
        keep = [c for c in cols if c in shots_df.columns]
        df = shots_df[keep].copy()
        df = df[df['cumulative_mins'].notna()].sort_values('cumulative_mins')
        df = df[df['cumulative_mins'] <= 90]

        # Heuristic xG estimator when per-shot xG is missing or zero
        import numpy as _np
        def _heuristic_xg(r):
            q = r.get('qualifiers_dict', {}) if isinstance(r.get('qualifiers_dict', {}), dict) else {}
            t = r.get('type_display', '')
            outcome = r.get('outcome_display', '')
            x = float(r.get('x', _np.nan))
            y = float(r.get('y', _np.nan))
            d = r.get('dist_to_goal', _np.nan)
            if not _np.isfinite(d) and _np.isfinite(x) and _np.isfinite(y):
                d = ((105.0 - x)**2 + (34.0 - y)**2) ** 0.5
            ang = r.get('angle', _np.nan)

            if isinstance(q, dict) and 'Penalty' in q:
                return 0.76

            base = 0.02
            in_box = _np.isfinite(x) and _np.isfinite(y) and (x >= 88.5) and (13.8 <= y <= 54.2)
            if in_box:
                base += 0.10
            elif _np.isfinite(x) and x >= 70:
                base += 0.05

            if _np.isfinite(d):
                if d < 8: base += 0.20
                elif d < 12: base += 0.12
                elif d < 18: base += 0.07
                elif d < 25: base += 0.03

            if _np.isfinite(ang):
                if ang > 0.35: base += 0.05
                elif ang > 0.25: base += 0.03

            if (isinstance(q, dict) and 'Head' in q) or t == 'Head':
                base *= 0.7

            if outcome in ['SavedShot', 'ShotOnPost']:
                base += 0.03
            if outcome in ['MissedShots']:
                base -= 0.01
            if t == 'Goal':
                base = max(base, 0.25)

            return float(max(0.01, min(0.95, base)))

        def _xg_used(row):
            xv = row.get('xg', 0.0)
            try:
                xv = float(xv)
            except Exception:
                xv = 0.0
            if xv and xv > 0:
                return xv
            return _heuristic_xg(row)

        def build_series(team_id):
            d = df[df['teamId'] == team_id].copy()
            if d.empty:
                return [0], [0]
            times = [0.0]
            vals = [0.0]
            for _, r in d.iterrows():
                t = float(r['cumulative_mins'])
                xg = _xg_used(r)
                times += [t, t]
                vals += [vals[-1], vals[-1] + xg]
            return times, vals

        ht, hv = build_series(home_id)
        at, av = build_series(away_id)

        # Determine visible y-range with minimum headroom
        import numpy as _np
        ymax = max((_np.max(hv) if len(hv) else 0), (_np.max(av) if len(av) else 0), 0.05) * 1.25

        # Filled steps for visibility
        ax.fill_between(ht, hv, step='post', color=home_color, alpha=0.18)
        ax.fill_between(at, av, step='post', color=away_color, alpha=0.18)
        ax.plot(ht, hv, color=home_color, linewidth=2.2, drawstyle='steps-post', label=f'{home_name} xG')
        ax.plot(at, av, color=away_color, linewidth=2.2, drawstyle='steps-post', label=f'{away_name} xG')

        # Mark goals with stars at their time on the respective step line
        goals = df[df['type_display'] == 'Goal']
        for _, g in goals.iterrows():
            is_home = g['teamId'] == home_id
            t = float(g['cumulative_mins'])
            series_t, series_v = (ht, hv) if is_home else (at, av)
            y = 0.0
            for i in range(1, len(series_t)):
                if series_t[i] >= t:
                    y = series_v[i-1]
                    break
            ax.scatter(t, y, s=160, c=(home_color if is_home else away_color), marker='*',
                       edgecolors='gold', linewidths=1.8, zorder=4)

        ax.set_xlim(0, 90)
        ax.set_ylim(0, ymax)
        ax.set_xlabel('Match Time (minutes)')
        ax.set_ylabel('Cumulative xG')
        self.prepare_axis(ax, 'Cumulative xG (steps)')
        ax.grid(True, axis='x', alpha=0.15)
        ax.legend(loc='lower right', fontsize=8, framealpha=0.9)



