"""
Match Report Generator
Main script to generate complete match reports.
"""

import json
import matplotlib.pyplot as plt
from typing import Optional, Tuple
import os
from datetime import datetime

from whoscored_extractor import WhoScoredExtractor
from fotmob_extractor import FotMobExtractor
from match_data_processor import MatchDataProcessor
from match_visualizations import create_full_match_report


class MatchReportGenerator:
    """Generate complete match reports from WhoScored and FotMob data."""

    def __init__(self, cache_dir: str = "./cache"):
        """
        Initialize the report generator.

        Args:
            cache_dir: Directory to store cached data
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

        self.whoscored_extractor = WhoScoredExtractor(headless=True)
        self.fotmob_extractor = FotMobExtractor()

    def extract_all_data(self, whoscored_id: int, fotmob_id: Optional[int] = None,
                        use_cache: bool = True) -> Tuple[dict, Optional[dict]]:
        """
        Extract data from both WhoScored and FotMob.

        Args:
            whoscored_id: WhoScored match ID
            fotmob_id: FotMob match ID (optional)
            use_cache: Use cached data if available

        Returns:
            Tuple of (whoscored_data, fotmob_data)
        """
        # Check cache
        ws_cache_file = os.path.join(self.cache_dir, f"whoscored_{whoscored_id}.json")
        fm_cache_file = os.path.join(self.cache_dir, f"fotmob_{fotmob_id}.json") if fotmob_id else None

        # Extract WhoScored data
        if use_cache and os.path.exists(ws_cache_file):
            print(f"Loading WhoScored data from cache: {ws_cache_file}")
            with open(ws_cache_file, 'r', encoding='utf-8') as f:
                whoscored_data = json.load(f)
        else:
            print(f"Extracting WhoScored data for match {whoscored_id}...")
            whoscored_data = self.whoscored_extractor.extract_all_sections(whoscored_id)

            # Save to cache
            with open(ws_cache_file, 'w', encoding='utf-8') as f:
                json.dump(whoscored_data, f, indent=2, ensure_ascii=False)
            print(f"WhoScored data cached to: {ws_cache_file}")

        # Extract FotMob data
        fotmob_data = None
        if fotmob_id:
            if use_cache and fm_cache_file and os.path.exists(fm_cache_file):
                print(f"Loading FotMob data from cache: {fm_cache_file}")
                with open(fm_cache_file, 'r', encoding='utf-8') as f:
                    fotmob_data = json.load(f)
            else:
                print(f"Extracting FotMob data for match {fotmob_id}...")
                fotmob_data = self.fotmob_extractor.extract_all_stats(fotmob_id)

                # Save to cache
                if fm_cache_file:
                    with open(fm_cache_file, 'w', encoding='utf-8') as f:
                        json.dump(fotmob_data, f, indent=2, ensure_ascii=False)
                    print(f"FotMob data cached to: {fm_cache_file}")

        return whoscored_data, fotmob_data

    def generate_report(self, whoscored_id: int, fotmob_id: Optional[int] = None,
                       output_file: Optional[str] = None, use_cache: bool = True,
                       dpi: int = 150) -> plt.Figure:
        """
        Generate complete match report.

        Args:
            whoscored_id: WhoScored match ID
            fotmob_id: FotMob match ID (optional)
            output_file: Path to save the figure (optional)
            use_cache: Use cached data if available
            dpi: DPI for saved figure

        Returns:
            Matplotlib Figure
        """
        print("\n" + "=" * 70)
        print("MATCH REPORT GENERATION")
        print("=" * 70)

        # Extract data
        whoscored_data, fotmob_data = self.extract_all_data(
            whoscored_id, fotmob_id, use_cache=use_cache
        )

        # Process data
        print("\nProcessing match data...")
        processor = MatchDataProcessor(whoscored_data, fotmob_data)
        team_info = processor.get_team_info()

        print(f"\nMatch: {team_info['home']['name']} vs {team_info['away']['name']}")
        print(f"Score: {team_info['home']['score']} - {team_info['away']['score']}")

        # Create visualizations
        print("\nCreating visualizations...")
        fig = create_full_match_report(processor, team_info)

        # Save figure
        if output_file:
            print(f"\nSaving report to: {output_file}")
            fig.savefig(output_file, dpi=dpi, bbox_inches='tight', facecolor='#f0f0f0')
            print(f"Report saved successfully!")

        print("\n" + "=" * 70)
        print("REPORT GENERATION COMPLETE")
        print("=" * 70 + "\n")

        return fig

    def generate_and_display(self, whoscored_id: int, fotmob_id: Optional[int] = None,
                            use_cache: bool = True):
        """
        Generate report and display it.

        Args:
            whoscored_id: WhoScored match ID
            fotmob_id: FotMob match ID (optional)
            use_cache: Use cached data if available
        """
        # Generate default filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"match_report_{whoscored_id}_{timestamp}.png"

        # Generate report
        fig = self.generate_report(whoscored_id, fotmob_id, output_file, use_cache)

        # Display
        plt.show()

        return fig


def main():
    """Command-line interface for report generation."""
    import argparse

    parser = argparse.ArgumentParser(description='Generate football match reports')
    parser.add_argument('whoscored_id', type=int, help='WhoScored match ID')
    parser.add_argument('--fotmob-id', type=int, help='FotMob match ID (optional)')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--no-cache', action='store_true', help='Disable caching')
    parser.add_argument('--dpi', type=int, default=150, help='DPI for output (default: 150)')
    parser.add_argument('--cache-dir', default='./cache', help='Cache directory')
    parser.add_argument('--display', action='store_true', help='Display the report')

    args = parser.parse_args()

    # Create generator
    generator = MatchReportGenerator(cache_dir=args.cache_dir)

    # Generate output filename if not provided
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"match_report_{args.whoscored_id}_{timestamp}.png"

    # Generate report
    fig = generator.generate_report(
        whoscored_id=args.whoscored_id,
        fotmob_id=args.fotmob_id,
        output_file=args.output,
        use_cache=not args.no_cache,
        dpi=args.dpi
    )

    # Display if requested
    if args.display:
        plt.show()
    else:
        plt.close(fig)


if __name__ == "__main__":
    main()
