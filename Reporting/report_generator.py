"""
Report Generator
Main module for generating complete match reports using ETL and Visual components.
"""

import matplotlib.pyplot as plt
from typing import Dict, Any, Optional, Tuple
import os

from ETL.loaders.data_loader import DataLoader
from ETL.transformers.match_processor import MatchProcessor
from Visual.pitch_visualizations import PitchVisualizations
from Visual.statistical_visualizations import StatisticalVisualizations
from Visual.heatmap_visualizations import HeatmapVisualizations
from Visual.advanced_visualizations import AdvancedVisualizations


class ReportGenerator:
    """Generate comprehensive match reports."""

    def __init__(self, cache_dir: str = "./cache"):
        """
        Initialize report generator.

        Args:
            cache_dir: Directory for caching data
        """
        self.cache_dir = cache_dir
        self.data_loader = DataLoader(cache_dir)

        # Initialize visualization modules
        self.pitch_viz = PitchVisualizations()
        self.stats_viz = StatisticalVisualizations()
        self.heatmap_viz = HeatmapVisualizations()
        self.advanced_viz = AdvancedVisualizations()

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
        
        # Player positions and connections
        home_positions = processor.get_player_positions(home_id, starting_xi_only=True)
        away_positions = processor.get_player_positions(away_id, starting_xi_only=True)
        home_connections = processor.get_pass_connections(home_id, min_passes=3)
        away_connections = processor.get_pass_connections(away_id, min_passes=3)

        # Create figure
        print("3. Creating visualizations...")
        fig = plt.figure(figsize=figsize, facecolor='#f0f0f0')
        gs = fig.add_gridspec(4, 3, hspace=0.3, wspace=0.3,
                             left=0.05, right=0.95, top=0.95, bottom=0.05)

        # Row 1
        ax1 = fig.add_subplot(gs[0, 0])
        self.stats_viz.create_match_summary_panel(ax1, match_summary)

        ax2 = fig.add_subplot(gs[0, 1])
        self.pitch_viz.create_shot_map(ax2, shots_home, shots_away, home_color, away_color)

        ax3 = fig.add_subplot(gs[0, 2])
        self.advanced_viz.create_momentum_graph(ax3, events_df, home_id, away_id,
                                               home_color, away_color, home_name, away_name)

        # Row 2
        ax4 = fig.add_subplot(gs[1, 0])
        self.pitch_viz.create_pass_network(ax4, home_positions, home_connections,
                                           home_color, home_name)

        ax5 = fig.add_subplot(gs[1, 1])
        self.advanced_viz.create_xg_timeline(ax5, events_df[events_df['type_display']=='Shot'],
                                            home_id, away_id, home_color, away_color)

        ax6 = fig.add_subplot(gs[1, 2])
        self.pitch_viz.create_pass_network(ax6, away_positions, away_connections,
                                           away_color, away_name)

        # Row 3
        ax7 = fig.add_subplot(gs[2, 0])
        self.advanced_viz.create_zone14_map(ax7, passes_home, home_color, home_name)

        ax8 = fig.add_subplot(gs[2, 1])
        self.heatmap_viz.create_pitch_control_map(ax8, 
                                                  events_df[events_df['teamId']==home_id],
                                                  events_df[events_df['teamId']==away_id],
                                                  home_color, away_color)

        ax9 = fig.add_subplot(gs[2, 2])
        self.advanced_viz.create_zone14_map(ax9, passes_away, away_color, away_name)

        # Row 4
        ax10 = fig.add_subplot(gs[3, 0])
        self.heatmap_viz.create_defensive_actions_heatmap(ax10, def_actions_home,
                                                          home_color, home_name)

        ax11 = fig.add_subplot(gs[3, 1])
        self.heatmap_viz.create_touch_heatmap(ax11, events_df[events_df['teamId']==home_id],
                                              home_color, home_name)

        ax12 = fig.add_subplot(gs[3, 2])
        self.heatmap_viz.create_defensive_actions_heatmap(ax12, def_actions_away,
                                                          away_color, away_name)

        # Add watermark
        fig.text(0.5, 0.01, 'PostMatchReport - Advanced Football Analytics',
                ha='center', fontsize=10, alpha=0.5, style='italic')

        # Save if requested
        if output_file:
            print(f"\n4. Saving report to: {output_file}")
            fig.savefig(output_file, dpi=dpi, bbox_inches='tight', facecolor='#f0f0f0')
            print("Report saved successfully!")

        print("\n" + "=" * 70)
        print("REPORT GENERATION COMPLETE")
        print("=" * 70 + "\n")

        return fig

    def clear_cache(self, match_id: Optional[int] = None):
        """Clear cached data."""
        self.data_loader.clear_cache(match_id)
