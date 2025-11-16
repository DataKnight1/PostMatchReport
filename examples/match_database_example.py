"""
Example script demonstrating the Match Database Manager functionality.

This script shows how to:
1. Load and browse the match database
2. Select matches by league
3. Retrieve match IDs for WhoScored and FotMob
4. Add new matches to the database
"""

import sys
import os

# Add parent directory to path to import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.match_database_manager import MatchDatabaseManager


def main():
    """Demonstrate match database functionality."""

    # Initialize the database manager
    print("=" * 60)
    print("Match Database Manager - Example Usage")
    print("=" * 60)

    db = MatchDatabaseManager()

    # Display database statistics
    print("\n1. Database Statistics")
    print("-" * 60)
    stats = db.get_database_stats()
    print(f"Total Leagues: {stats['total_leagues']}")
    print(f"Total Matches: {stats['total_matches']}")

    print("\nLeagues breakdown:")
    for league in stats['leagues']:
        print(f"  • {league['name']} ({league['country']}): {league['match_count']} matches")

    # Browse matches by league
    print("\n2. Browse Matches by League")
    print("-" * 60)

    league_name = "Premier League"
    print(f"Matches in {league_name}:")
    matches = db.get_match_display_names(league_name)

    for i, match in enumerate(matches, 1):
        print(f"  {i}. {match}")

    # Get match IDs
    print("\n3. Retrieve Match IDs")
    print("-" * 60)

    if matches:
        selected_match = matches[0]
        whoscored_id, fotmob_id = db.get_match_ids(league_name, selected_match)

        print(f"Selected: {selected_match}")
        print(f"  WhoScored ID: {whoscored_id}")
        print(f"  FotMob ID: {fotmob_id}")
        print(f"\nURLs:")
        print(f"  WhoScored: https://www.whoscored.com/Matches/{whoscored_id}/Live")
        print(f"  FotMob: https://www.fotmob.com/matches/{fotmob_id}")

    # Example: Adding a new match (commented out to prevent accidental modification)
    print("\n4. Adding New Matches (Example - Not Executed)")
    print("-" * 60)
    print("""
To add a new match programmatically:

    new_match = {
        'id': 'pl-005',
        'home_team': 'Newcastle',
        'away_team': 'Brighton',
        'date': '2024-05-25',
        'score': '3-2',
        'whoscored_id': 1821320,
        'fotmob_id': 3900975
    }

    success = db.add_match('Premier League', new_match)
    if success:
        print("Match added successfully!")
    """)

    # Search functionality
    print("\n5. Search Matches")
    print("-" * 60)

    search_query = "Arsenal"
    print(f"Searching for: '{search_query}'")
    results = db.search_matches(search_query)

    print(f"Found {len(results)} matches:")
    for result in results:
        print(f"  • {result['display']} ({result['league_name']})")

    # Display all leagues with their matches
    print("\n6. Complete Match Database")
    print("-" * 60)

    for league in db.get_all_leagues():
        print(f"\n{league['name']} ({league['country']}):")
        for match in league['matches']:
            print(f"  • {match['display']}")

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
