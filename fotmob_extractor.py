"""
FotMob Data Extractor
Extracts match data from FotMob API including xG, team colors, and statistics.
"""

import requests
import hashlib
import base64
import json
from typing import Dict, Any, Optional
from datetime import datetime


class FotMobExtractor:
    """Extract match data from FotMob API."""

    BASE_URL = "https://www.fotmob.com/api"
    MATCH_DETAILS_URL = f"{BASE_URL}/matchDetails"

    def __init__(self):
        """Initialize the FotMob extractor."""
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://www.fotmob.com',
            'Referer': 'https://www.fotmob.com/',
        }

    def get_match_details(self, match_id: int) -> Dict[str, Any]:
        """
        Get match details from FotMob.

        Args:
            match_id: FotMob match ID

        Returns:
            Dictionary containing match details
        """
        url = f"{self.MATCH_DETAILS_URL}?matchId={match_id}"
        print(f"Fetching FotMob data from: {url}")

        try:
            response = self.session.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            data = response.json()

            return {
                'match_id': match_id,
                'data': data,
                'success': True
            }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching FotMob data: {e}")
            return {
                'match_id': match_id,
                'error': str(e),
                'success': False
            }

    def extract_team_colors(self, match_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract team colors from match data.

        Args:
            match_data: FotMob match data

        Returns:
            Dictionary with home and away team colors
        """
        try:
            general = match_data.get('data', {}).get('general', {})
            home_team = general.get('homeTeam', {})
            away_team = general.get('awayTeam', {})

            return {
                'home_color': f"#{home_team.get('teamColors', {}).get('primary', 'FF0000')}",
                'away_color': f"#{away_team.get('teamColors', {}).get('primary', '0000FF')}"
            }
        except Exception as e:
            print(f"Error extracting team colors: {e}")
            return {
                'home_color': '#FF0000',
                'away_color': '#0000FF'
            }

    def extract_match_info(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract basic match information.

        Args:
            match_data: FotMob match data

        Returns:
            Dictionary with match information
        """
        try:
            data = match_data.get('data', {})
            general = data.get('general', {})

            home_team = general.get('homeTeam', {})
            away_team = general.get('awayTeam', {})

            return {
                'home_team': home_team.get('name'),
                'away_team': away_team.get('name'),
                'home_score': general.get('homeTeamScore'),
                'away_score': general.get('awayTeamScore'),
                'league': general.get('leagueName'),
                'league_id': general.get('parentLeagueId'),
                'round': general.get('leagueRoundName'),
                'venue': general.get('venue'),
                'date': general.get('matchTimeUTCDate'),
                'status': general.get('status', {}).get('finished', False)
            }
        except Exception as e:
            print(f"Error extracting match info: {e}")
            return {}

    def extract_xg_data(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract expected goals (xG) data.

        Args:
            match_data: FotMob match data

        Returns:
            Dictionary with xG data
        """
        try:
            data = match_data.get('data', {})
            header = data.get('header', {})

            teams = header.get('teams', [])
            if len(teams) >= 2:
                home_xg = teams[0].get('xg', 0.0)
                away_xg = teams[1].get('xg', 0.0)
            else:
                home_xg = away_xg = 0.0

            return {
                'home_xg': float(home_xg) if home_xg else 0.0,
                'away_xg': float(away_xg) if away_xg else 0.0
            }
        except Exception as e:
            print(f"Error extracting xG data: {e}")
            return {
                'home_xg': 0.0,
                'away_xg': 0.0
            }

    def extract_possession(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract possession statistics.

        Args:
            match_data: FotMob match data

        Returns:
            Dictionary with possession data
        """
        try:
            data = match_data.get('data', {})
            content = data.get('content', {})
            stats = content.get('stats', {})

            possession_stats = None
            for stat in stats.get('Periods', {}).get('All', {}).get('stats', []):
                if stat.get('title') == 'Possession':
                    possession_stats = stat
                    break

            if possession_stats:
                stats_list = possession_stats.get('stats', [])
                if len(stats_list) >= 2:
                    home_poss = float(stats_list[0].get('value', '50').replace('%', ''))
                    away_poss = float(stats_list[1].get('value', '50').replace('%', ''))
                else:
                    home_poss = away_poss = 50.0
            else:
                home_poss = away_poss = 50.0

            return {
                'home_possession': home_poss,
                'away_possession': away_poss
            }
        except Exception as e:
            print(f"Error extracting possession data: {e}")
            return {
                'home_possession': 50.0,
                'away_possession': 50.0
            }

    def extract_shots_data(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract shots statistics.

        Args:
            match_data: FotMob match data

        Returns:
            Dictionary with shots data
        """
        try:
            data = match_data.get('data', {})
            content = data.get('content', {})
            stats = content.get('stats', {})

            shots_stats = None
            for stat in stats.get('Periods', {}).get('All', {}).get('stats', []):
                if stat.get('title') == 'Shots':
                    shots_stats = stat
                    break

            if shots_stats:
                stats_list = shots_stats.get('stats', [])
                if len(stats_list) >= 2:
                    home_shots = int(stats_list[0].get('value', 0))
                    away_shots = int(stats_list[1].get('value', 0))
                else:
                    home_shots = away_shots = 0
            else:
                home_shots = away_shots = 0

            return {
                'home_shots': home_shots,
                'away_shots': away_shots
            }
        except Exception as e:
            print(f"Error extracting shots data: {e}")
            return {
                'home_shots': 0,
                'away_shots': 0
            }

    def extract_all_stats(self, match_id: int) -> Dict[str, Any]:
        """
        Extract all available statistics for a match.

        Args:
            match_id: FotMob match ID

        Returns:
            Dictionary with all statistics
        """
        match_data = self.get_match_details(match_id)

        if not match_data['success']:
            return match_data

        result = {
            'match_id': match_id,
            'success': True,
            'match_info': self.extract_match_info(match_data),
            'team_colors': self.extract_team_colors(match_data),
            'xg': self.extract_xg_data(match_data),
            'possession': self.extract_possession(match_data),
            'shots': self.extract_shots_data(match_data),
            'raw_data': match_data.get('data', {})
        }

        return result

    def save_to_json(self, data: Dict[str, Any], filename: str):
        """
        Save extracted data to JSON file.

        Args:
            data: Data to save
            filename: Output filename
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"FotMob data saved to: {filename}")


def main():
    """Example usage."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python fotmob_extractor.py <match_id>")
        print("\nExample: python fotmob_extractor.py 4193558")
        return

    match_id = int(sys.argv[1])

    extractor = FotMobExtractor()
    stats = extractor.extract_all_stats(match_id)

    if stats['success']:
        print("\n" + "=" * 60)
        print("FOTMOB DATA EXTRACTION SUMMARY")
        print("=" * 60)

        info = stats['match_info']
        print(f"\nMatch: {info['home_team']} vs {info['away_team']}")
        print(f"Score: {info['home_score']} - {info['away_score']}")
        print(f"League: {info['league']}")
        print(f"Date: {info['date']}")

        xg = stats['xg']
        print(f"\nxG: {xg['home_xg']:.2f} - {xg['away_xg']:.2f}")

        poss = stats['possession']
        print(f"Possession: {poss['home_possession']:.1f}% - {poss['away_possession']:.1f}%")

        colors = stats['team_colors']
        print(f"\nTeam Colors:")
        print(f"  Home: {colors['home_color']}")
        print(f"  Away: {colors['away_color']}")

        # Save to file
        filename = f"fotmob_match_{match_id}.json"
        extractor.save_to_json(stats, filename)
    else:
        print(f"Failed to extract FotMob data: {stats.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
