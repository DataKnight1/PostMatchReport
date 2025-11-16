"""
Report Generator
Main module for generating complete match reports using ETL and Visual components.
"""

import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, Any, Optional, Tuple
import os

from ETL.loaders.data_loader import DataLoader
from ETL.transformers.match_processor import MatchProcessor
from Visual.theme_manager import ThemeManager
from Visual.pitch_visualizations import PitchVisualizations
from Visual.statistical_visualizations import StatisticalVisualizations
from Visual.heatmap_visualizations import HeatmapVisualizations
from Visual.advanced_visualizations import AdvancedVisualizations
from Visual.tactical_visualizations import TacticalVisualizer


class ReportGenerator:
    """Generate comprehensive match reports."""

    def __init__(self, cache_dir: str = "./cache", theme: str = 'dark', show_colorbars: bool = True):
        """
        Initialize report generator.

        Args:
            cache_dir: Directory for caching data
            theme: 'dark', 'light', or 'monochrome'
        """
        self.cache_dir = cache_dir
        self.data_loader = DataLoader(cache_dir)
        self.show_colorbars = show_colorbars

        # Initialize theme manager
        self.theme_manager = ThemeManager(theme)
        self.bg_color = self.theme_manager.get_color('background')
        self.text_color = self.theme_manager.get_color('text_primary')

        # Initialize visualization modules with theme manager
        self.pitch_viz = PitchVisualizations(theme_manager=self.theme_manager, show_colorbars=self.show_colorbars)
        self.stats_viz = StatisticalVisualizations(theme_manager=self.theme_manager, show_colorbars=self.show_colorbars)
        self.heatmap_viz = HeatmapVisualizations(theme_manager=self.theme_manager, show_colorbars=self.show_colorbars)
        self.advanced_viz = AdvancedVisualizations(theme_manager=self.theme_manager, show_colorbars=self.show_colorbars)
        self.tactical_viz = TacticalVisualizer(theme_manager=self.theme_manager, show_colorbars=self.show_colorbars)

    def _find_team_logo(self, team_id: Optional[int], team_name: Optional[str]) -> Optional[str]:
        """Try to resolve a team logo path locally under config/logos.

        Checks by ID then by sanitized name. Returns path or None.
        """
        base = os.path.join(os.path.dirname(__file__), '..', 'config', 'logos')
        base = os.path.abspath(base)
        candidates = []
        if team_id is not None:
            candidates.append(os.path.join(base, f"{team_id}.png"))
            candidates.append(os.path.join(base, f"{team_id}.jpg"))
            candidates.append(os.path.join(base, f"{team_id}.svg"))
        if team_name:
            key = ''.join(ch for ch in team_name.lower() if ch.isalnum())
            candidates.append(os.path.join(base, f"{key}.png"))
            candidates.append(os.path.join(base, f"{key}.jpg"))
            candidates.append(os.path.join(base, f"{key}.svg"))
        for p in candidates:
            if os.path.isfile(p):
                return p
        return None

    def _resolve_logo_input(self, logo_val: Optional[str], team_key: str, team_id: Optional[int]) -> Optional[str]:
        """Accept a local path or URL; if URL, download to cache and return local path."""
        if not logo_val:
            return None
        try:
            if isinstance(logo_val, str) and logo_val.startswith('http'):
                import requests
                os.makedirs(self.cache_dir, exist_ok=True)
                fn = os.path.join(self.cache_dir, f"logo_{team_key}_{team_id or 'unknown'}.png")
                if not os.path.isfile(fn):
                    r = requests.get(logo_val, timeout=10)
                    if r.status_code == 200:
                        with open(fn, 'wb') as f:
                            f.write(r.content)
                        return fn
                    else:
                        return None
                return fn
            # Local path case
            return logo_val if os.path.isfile(logo_val) else None
        except Exception:
            return None

    def generate_report(self, whoscored_id: int, fotmob_id: Optional[int] = None,
                       output_file: Optional[str] = None, use_cache: bool = True,
                       dpi: int = 150, figsize: Tuple[int, int] = (20, 22),
                       home_logo_path: Optional[str] = None,
                       away_logo_path: Optional[str] = None) -> plt.Figure:
        """
        Generate complete match report.

        Args:
            whoscored_id: WhoScored match ID
            fotmob_id: FotMob match ID (optional)
            output_file: Path to save figure
            use_cache: Use cached data
            dpi: DPI for output
            figsize: Figure size

        Returns:
            Matplotlib Figure
        """
        print("\n" + "=" * 70)
        print("MATCH REPORT GENERATION")
        print("=" * 70)

        # Load data
        print("\n1. Loading data...")
        whoscored_data, fotmob_data = self.data_loader.load_all_data(
            whoscored_id, fotmob_id, use_cache
        )

        # Process data
        print("2. Processing data...")
        processor = MatchProcessor(whoscored_data, fotmob_data)
        match_summary = processor.get_complete_match_summary()

        if not match_summary.get('success'):
            raise ValueError("Failed to process match data")

        # Extract team info
        home_id = match_summary['teams']['home']['id']
        away_id = match_summary['teams']['away']['id']
        home_name = match_summary['teams']['home']['name']
        away_name = match_summary['teams']['away']['name']
        home_color = match_summary['team_colors'].get('home_color', '#FF0000')
        away_color = match_summary['team_colors'].get('away_color', '#0000FF')

        print(f"\nMatch: {home_name} vs {away_name}")

        # Attach team logos if available
        # Prefer source-provided URLs, then overrides, then local lookup
        provided_logos = match_summary.get('team_logos', {}) if isinstance(match_summary.get('team_logos'), dict) else {}
        home_from_data = provided_logos.get('home') if provided_logos else None
        away_from_data = provided_logos.get('away') if provided_logos else None

        home_path_final = self._resolve_logo_input(home_logo_path, 'home', home_id) or \
                          self._resolve_logo_input(home_from_data, 'home', home_id) or \
                          self._find_team_logo(home_id, home_name)
        away_path_final = self._resolve_logo_input(away_logo_path, 'away', away_id) or \
                          self._resolve_logo_input(away_from_data, 'away', away_id) or \
                          self._find_team_logo(away_id, away_name)

        match_summary['team_logos'] = {
            'home': home_path_final,
            'away': away_path_final
        }

        # Get data for visualizations
        events_df = processor.get_events_dataframe()
        shots_home = processor.get_shots(home_id)
        shots_away = processor.get_shots(away_id)
        passes_home = processor.get_passes(home_id, successful_only=True)
        passes_away = processor.get_passes(away_id, successful_only=True)
        def_actions_home = processor.get_defensive_actions(home_id)
        def_actions_away = processor.get_defensive_actions(away_id)
        
        # Pass network data (using enhanced method)
        home_positions, home_connections = processor.get_pass_network_data(home_id, min_passes=3)
        away_positions, away_connections = processor.get_pass_network_data(away_id, min_passes=3)

        # Zonal control data
        zone_matrix = None
        if processor.event_processor:
            zone_matrix = processor.event_processor.calculate_zonal_control(home_id, away_id,
                                                                           grid_cols=6, grid_rows=4)

        # Create figure
        print("3. Creating visualizations...")
        fig = plt.figure(figsize=figsize, facecolor=self.bg_color)
        gs = fig.add_gridspec(4, 3, hspace=0.3, wspace=0.3,
                             left=0.05, right=0.95, top=0.95, bottom=0.05)

        # Row 1
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.set_facecolor(self.bg_color)
        self.stats_viz.create_match_summary_panel(ax1, match_summary)

        ax2 = fig.add_subplot(gs[0, 1])
        ax2.set_facecolor(self.bg_color)
        self.pitch_viz.create_xg_shot_map(ax2, shots_home, shots_away, home_color, away_color)

        ax3 = fig.add_subplot(gs[0, 2])
        ax3.set_facecolor(self.bg_color)
        self.advanced_viz.create_momentum_graph(ax3, events_df, home_id, away_id,
                                               home_color, away_color, home_name, away_name)

        # Row 2
        ax4 = fig.add_subplot(gs[1, 0])
        ax4.set_facecolor(self.bg_color)
        self.pitch_viz.create_pass_network(ax4, home_positions, home_connections,
                                           home_color, home_name)

        ax5 = fig.add_subplot(gs[1, 1])
        ax5.set_facecolor(self.bg_color)
        # Combine shots from both teams for xG timeline
        all_shots = pd.concat([shots_home, shots_away]) if not shots_home.empty and not shots_away.empty else (shots_home if not shots_home.empty else shots_away)
        # Replace timeline with cumulative xG steps
        self.advanced_viz.create_cumulative_xg(ax5, all_shots,
                                              home_id, away_id, home_color, away_color,
                                              home_name, away_name)

        ax6 = fig.add_subplot(gs[1, 2])
        ax6.set_facecolor(self.bg_color)
        self.pitch_viz.create_pass_network(ax6, away_positions, away_connections,
                                           away_color, away_name)

        # Row 3
        ax7 = fig.add_subplot(gs[2, 0])
        ax7.set_facecolor(self.bg_color)
        self.advanced_viz.create_zone14_map(ax7, passes_home, home_color, home_name)

        ax8 = fig.add_subplot(gs[2, 1])
        ax8.set_facecolor(self.bg_color)
        self.heatmap_viz.create_pitch_control_map(ax8,
                                                  events_df[events_df['teamId']==home_id],
                                                  events_df[events_df['teamId']==away_id],
                                                  home_color, away_color)

        ax9 = fig.add_subplot(gs[2, 2])
        ax9.set_facecolor(self.bg_color)
        self.advanced_viz.create_zone14_map(ax9, passes_away, away_color, away_name)

        # Row 4
        ax10 = fig.add_subplot(gs[3, 0])
        ax10.set_facecolor(self.bg_color)
        self.heatmap_viz.create_defensive_actions_heatmap(ax10, def_actions_home,
                                                          home_color, home_name)

        ax11 = fig.add_subplot(gs[3, 1])
        ax11.set_facecolor(self.bg_color)
        if zone_matrix is not None:
            # Create zonal control map
            home_team_info = {
                'name': home_name,
                'id': home_id
            }
            away_team_info = {
                'name': away_name,
                'id': away_id
            }
            self.tactical_viz.create_zonal_control_map(ax11, zone_matrix,
                                                      home_team_info, away_team_info,
                                                      home_color, away_color,
                                                      'right', 'left')
        else:
            # Fallback to touch heatmap if no data
            self.heatmap_viz.create_touch_heatmap(ax11, events_df[events_df['teamId']==home_id],
                                                  home_color, home_name)

        ax12 = fig.add_subplot(gs[3, 2])
        ax12.set_facecolor(self.bg_color)
        self.heatmap_viz.create_defensive_actions_heatmap(ax12, def_actions_away,
                                                          away_color, away_name)

        # Add watermark
        fig.text(0.5, 0.01, 'PostMatchReport - Advanced Football Analytics',
                ha='center', fontsize=10, alpha=0.6, style='italic', color=self.text_color)

        # Save if requested
        if output_file:
            print(f"\n4. Saving report to: {output_file}")
            fig.savefig(output_file, dpi=dpi, bbox_inches='tight', facecolor=self.bg_color)
            print("Report saved successfully!")

        print("\n" + "=" * 70)
        print("REPORT GENERATION COMPLETE")
        print("=" * 70 + "\n")

        return fig

    def clear_cache(self, match_id: Optional[int] = None):
        """Clear cached data."""
        self.data_loader.clear_cache(match_id)


