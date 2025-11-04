"""
PostMatchReport - Main CLI
Command-line interface for generating match reports using the new modular structure.
"""

import argparse
from datetime import datetime
import matplotlib.pyplot as plt

from Reporting.report_generator import ReportGenerator


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='Generate comprehensive football match reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 1716104
  %(prog)s 1716104 --fotmob-id 4193558
  %(prog)s 1716104 -o my_report.png --dpi 200
  %(prog)s 1716104 --no-cache --display
        """
    )

    parser.add_argument('whoscored_id', type=int,
                       help='WhoScored match ID')
    parser.add_argument('--fotmob-id', type=int,
                       help='FotMob match ID (optional, for xG and colors)')
    parser.add_argument('-o', '--output',
                       help='Output file path (default: auto-generated)')
    parser.add_argument('--dpi', type=int, default=150,
                       help='DPI for output image (default: 150)')
    parser.add_argument('--no-cache', action='store_true',
                       help='Disable caching, fetch fresh data')
    parser.add_argument('--display', action='store_true',
                       help='Display the report after generation')
    parser.add_argument('--cache-dir', default='./cache',
                       help='Cache directory (default: ./cache)')
    parser.add_argument('--clear-cache', action='store_true',
                       help='Clear cache before generation')

    args = parser.parse_args()

    # Create generator
    generator = ReportGenerator(cache_dir=args.cache_dir)

    # Clear cache if requested
    if args.clear_cache:
        generator.clear_cache()
        print("Cache cleared.")

    # Generate output filename if not provided
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"match_report_{args.whoscored_id}_{timestamp}.png"

    try:
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

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
