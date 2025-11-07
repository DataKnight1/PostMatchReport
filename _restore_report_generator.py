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
from Visual.pitch_visualizations import PitchVisualizations
from Visual.statistical_visualizations import StatisticalVisualizations
from Visual.heatmap_visualizations import HeatmapVisualizations
from Visual.advanced_visualizations import AdvancedVisualizations
from Visual.tactical_visualizations import TacticalVisualizer


class ReportGenerator:
    """Generate comprehensive match reports."""

    def __init__(self, cache_dir: str = "./cache", theme: str = 'dark'):
        """
        Initialize report generator.

        Args:
            cache_dir: Directory for caching data
            theme: 'dark' or 'light'
        """
        self.cache_dir = cache_dir
        self.data_loader = DataLoader(cache_dir)

        # Initialize visualization modules
        self.theme = theme.lower()
        if self.theme == 'dark':
            self.bg_color = '#0e1117'
            self.text_color = 'white'
            pitch_color = '#0e1117'
            line_color = '#e6e6e6'
        else:
            self.bg_color = '#f0f0f0'
            self.text_color = 'black'
            pitch_color = '#d6c39f'
            line_color = '#0e1117'

        self.pitch_viz = PitchVisualizations(pitch_color=pitch_color, line_color=line_color)
        self.stats_viz = StatisticalVisualizations()
        self.heatmap_viz = HeatmapVisualizations()
        self.advanced_viz = AdvancedVisualizations(pitch_color=pitch_color, line_color=line_color)
        self.tactical_viz = TacticalVisualizer()

    def generate_report(self, whoscored_id: int, fotmob_id: Optional[int] = None,
                       output_file: Optional[str] = None, use_cache: bool = True,
                       dpi: int = 150, figsize: Tuple[int, int] = (20, 22)) -> plt.Figure:
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

        def _apply_dark(ax):
            if self.theme != 'dark':
                return
            try:
                for spine in ax.spines.values():
                    spine.set_color('white')
            except Exception:
                pass
            ax.tick_params(colors='white')
            for lbl in ax.get_xticklabels() + ax.get_yticklabels():
                try:
                    lbl.set_color('white')
                except Exception:
                    pass
            try:
                ax.set_title(ax.get_title(), color='white')
                ax.xaxis.label.set_color('white')
                ax.yaxis.label.set_color('white')
                leg = ax.get_legend()
                if leg is not None:
                    for text in leg.get_texts():
                        text.set_color('white')
                    leg.get_frame().set_edgecolor('white')
            except Exception:
                pass

        # Row 1
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.set_facecolor(self.bg_color)
        self.stats_viz.create_match_summary_panel(ax1, match_summary, text_color=self.text_color)
        _apply_dark(ax1)

        ax2 = fig.add_subplot(gs[0, 1])
        ax2.set_facecolor(self.bg_color)
        # Dark xG shot map
        self.pitch_viz.create_xg_shot_map(ax2, shots_home, shots_away, home_color, away_color)
        _apply_dark(ax2)


