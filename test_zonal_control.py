"""
Test script for zonal control visualization
"""

import numpy as np
import matplotlib.pyplot as plt
from Visual.tactical_visualizations import TacticalVisualizer


def test_zonal_control():
    """Test the zonal control visualization."""
    print("Testing Zonal Control Visualization...")

    # Create sample zone matrix (6 columns x 4 rows)
    # Simulate a match where home team (H) dominates left side,
    # away team (A) dominates right side, and middle is contested (C)
    zone_matrix = np.array([
        ['H', 'H', 'C', 'A', 'A', 'A'],  # Top row
        ['H', 'H', 'C', 'C', 'A', 'A'],  # Second row
        ['H', 'C', 'C', 'C', 'A', 'A'],  # Third row
        ['H', 'H', 'C', 'A', 'A', 'A'],  # Bottom row
    ])

    # Team info
    home_team = {
        'name': 'Manchester United',
        'id': 1
    }
    away_team = {
        'name': 'Liverpool',
        'id': 2
    }

    # Colors
    home_color = '#DA291C'  # Man Utd red
    away_color = '#C8102E'  # Liverpool red

    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(12, 10), facecolor='#f5f5f5')

    # Create visualization
    viz = TacticalVisualizer()
    viz.create_zonal_control_map(
        ax, zone_matrix,
        home_team, away_team,
        home_color, away_color,
        'right', 'left'
    )

    # Save figure
    output_file = '/home/user/PostMatchReport/test_zonal_control_output.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='#f5f5f5')
    print(f"✓ Test visualization saved to: {output_file}")

    plt.close()

    print("✓ Zonal control visualization test completed successfully!")
    return True


if __name__ == '__main__':
    try:
        test_zonal_control()
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
