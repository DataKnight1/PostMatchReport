"""
Match Database Manager
Handles loading and querying the match database for dropdown selection.
"""

import json
import os
from typing import Dict, List, Optional, Tuple


class MatchDatabaseManager:
    """Manages the match database for league and match selection."""

    def __init__(self, database_path: str = None):
        """
        Initialize the match database manager.

        Args:
            database_path: Path to the match database JSON file
        """
        if database_path is None:
            # Default path relative to project root
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            database_path = os.path.join(project_root, 'data', 'match_database.json')

        self.database_path = database_path
        self.data = self._load_database()

    def _load_database(self) -> Dict:
        """Load the match database from JSON file."""
        try:
            with open(self.database_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Match database not found at {self.database_path}")
            return {"leagues": []}
        except json.JSONDecodeError as e:
            print(f"Error parsing match database: {e}")
            return {"leagues": []}

    def get_all_leagues(self) -> List[Dict]:
        """
        Get all available leagues.

        Returns:
            List of league dictionaries
        """
        return self.data.get('leagues', [])

    def get_league_names(self) -> List[str]:
        """
        Get list of all league names.

        Returns:
            List of league names
        """
        return [league['name'] for league in self.get_all_leagues()]

    def get_league_by_name(self, league_name: str) -> Optional[Dict]:
        """
        Get league data by name.

        Args:
            league_name: Name of the league

        Returns:
            League dictionary or None if not found
        """
        for league in self.get_all_leagues():
            if league['name'] == league_name:
                return league
        return None

    def get_matches_by_league(self, league_name: str) -> List[Dict]:
        """
        Get all matches for a specific league.

        Args:
            league_name: Name of the league

        Returns:
            List of match dictionaries
        """
        league = self.get_league_by_name(league_name)
        if league:
            return league.get('matches', [])
        return []

    def get_match_display_names(self, league_name: str) -> List[str]:
        """
        Get formatted display names for all matches in a league.

        Args:
            league_name: Name of the league

        Returns:
            List of match display names
        """
        matches = self.get_matches_by_league(league_name)
        return [match['display'] for match in matches]

    def get_match_by_display_name(self, league_name: str, display_name: str) -> Optional[Dict]:
        """
        Get match data by its display name.

        Args:
            league_name: Name of the league
            display_name: Display name of the match

        Returns:
            Match dictionary or None if not found
        """
        matches = self.get_matches_by_league(league_name)
        for match in matches:
            if match['display'] == display_name:
                return match
        return None

    def get_match_ids(self, league_name: str, display_name: str) -> Tuple[Optional[int], Optional[int]]:
        """
        Get WhoScored and FotMob IDs for a specific match.

        Args:
            league_name: Name of the league
            display_name: Display name of the match

        Returns:
            Tuple of (whoscored_id, fotmob_id) or (None, None) if not found
        """
        match = self.get_match_by_display_name(league_name, display_name)
        if match:
            return match.get('whoscored_id'), match.get('fotmob_id')
        return None, None

    def add_match(self, league_name: str, match_data: Dict) -> bool:
        """
        Add a new match to the database.

        Args:
            league_name: Name of the league
            match_data: Dictionary containing match information

        Returns:
            True if successful, False otherwise
        """
        league = self.get_league_by_name(league_name)
        if league is None:
            print(f"League '{league_name}' not found")
            return False

        # Validate required fields
        required_fields = ['id', 'home_team', 'away_team', 'date', 'whoscored_id', 'fotmob_id']
        if not all(field in match_data for field in required_fields):
            print(f"Missing required fields in match data")
            return False

        # Create display name if not provided
        if 'display' not in match_data:
            match_data['display'] = f"{match_data['home_team']} {match_data.get('score', 'vs')} {match_data['away_team']} ({match_data['date']})"

        # Add match to league
        league['matches'].append(match_data)

        # Save to file
        return self._save_database()

    def _save_database(self) -> bool:
        """
        Save the current database state to file.

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.database_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving database: {e}")
            return False

    def search_matches(self, query: str) -> List[Dict]:
        """
        Search for matches across all leagues.

        Args:
            query: Search query (team name, date, etc.)

        Returns:
            List of matching matches with league information
        """
        results = []
        query_lower = query.lower()

        for league in self.get_all_leagues():
            for match in league.get('matches', []):
                # Search in team names, date, and display name
                searchable_text = (
                    f"{match.get('home_team', '')} "
                    f"{match.get('away_team', '')} "
                    f"{match.get('date', '')} "
                    f"{match.get('display', '')}"
                ).lower()

                if query_lower in searchable_text:
                    match_with_league = match.copy()
                    match_with_league['league_name'] = league['name']
                    results.append(match_with_league)

        return results

    def get_total_matches(self) -> int:
        """
        Get total number of matches in the database.

        Returns:
            Total match count
        """
        total = 0
        for league in self.get_all_leagues():
            total += len(league.get('matches', []))
        return total

    def get_database_stats(self) -> Dict:
        """
        Get statistics about the match database.

        Returns:
            Dictionary with database statistics
        """
        leagues = self.get_all_leagues()
        return {
            'total_leagues': len(leagues),
            'total_matches': self.get_total_matches(),
            'leagues': [
                {
                    'name': league['name'],
                    'country': league.get('country', 'Unknown'),
                    'match_count': len(league.get('matches', []))
                }
                for league in leagues
            ]
        }
