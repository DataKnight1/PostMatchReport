"""
FotMob Data Extractor
Extracts match data from FotMob API using signature-based authentication.
"""

import json
import hashlib
import base64
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup


class FotMobExtractor:
    """Extract match data from FotMob using signature-based authentication."""

    BASE_URL = "https://www.fotmob.com/api"
    MATCH_DETAILS_URL = f"{BASE_URL}/matchDetails"

    def __init__(self):
        """Initialize the FotMob extractor."""
        self.version_number = self._get_version_number()
        self.xmas_pass = self._get_xmas_pass()

    def _get_version_number(self) -> Optional[str]:
        """Get the current FotMob version number from their homepage."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            }
            response = requests.get("https://www.fotmob.com/", headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            version_element = soup.find('span', class_=lambda cls: cls and 'VersionNumber' in cls)
            if version_element:
                version = version_element.text.strip()
                print(f"FotMob version: {version}")
                return version
            return None
        except Exception as e:
            print(f"Error getting version number: {e}")
            return None

    def _get_xmas_pass(self) -> Optional[str]:
        """Fetch the xmas pass from GitHub."""
        try:
            url = 'https://raw.githubusercontent.com/bariscanyeksin/streamlit_radar/refs/heads/main/xmas_pass.txt'
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            print(f"Error getting xmas pass: {e}")
            return None

    def _create_xmas_header(self, url: str, password: str) -> str:
        """Create the x-mas authentication header."""
        try:
            timestamp = int(datetime.now().timestamp() * 1000)
            request_data = {
                "url": url,
                "code": timestamp,
                "foo": self.version_number
            }

            json_string = f"{json.dumps(request_data, separators=(',', ':'))}{password.strip()}"
            signature = hashlib.md5(json_string.encode('utf-8')).hexdigest().upper()
            body = {
                "body": request_data,
                "signature": signature
            }
            encoded = base64.b64encode(json.dumps(body, separators=(',', ':')).encode('utf-8')).decode('utf-8')
            return encoded
        except Exception as e:
            print(f"Error creating xmas header: {e}")
            return ""

    def get_match_details(self, match_id: int) -> Dict[str, Any]:
        """
        Get match details from FotMob API.

        Args:
            match_id: FotMob match ID

        Returns:
            Dictionary containing match details
        """
        api_url = f"/api/matchDetails?matchId={match_id}"
        full_url = f"https://www.fotmob.com{api_url}"
        print(f"Fetching FotMob data from: {full_url}")

        try:
            if not self.version_number or not self.xmas_pass:
                raise Exception("Missing version number or xmas pass")

            xmas_value = self._create_xmas_header(api_url, self.xmas_pass)

            headers = {
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'referer': 'https://www.fotmob.com/',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'x-mas': xmas_value,
            }

            response = requests.get(full_url, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            print("FotMob data fetched successfully!")

            return {
                'match_id': match_id,
                'data': data,
                'success': True
            }

        except Exception as e:
            print(f"Error fetching FotMob data: {e}")
            print("FotMob data is optional - continuing without it...")
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
            team_colors = general.get('teamColors', {}).get('lightMode', {})

            home_color = team_colors.get('home', 'FF0000')
            away_color = team_colors.get('away', '0000FF')

            # Add # if not present
            if not home_color.startswith('#'):
                home_color = f'#{home_color}'
            if not away_color.startswith('#'):
                away_color = f'#{away_color}'

            return {
                'home_color': home_color,
                'away_color': away_color
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
            content = data.get('content', {})
            stats = content.get('stats', {})
            periods = stats.get('Periods', {})
            all_period = periods.get('All', {})
            stats_array = all_period.get('stats', [])

            # Find the Top stats group
            for stat_group in stats_array:
                if stat_group.get('title') == 'Top stats':
                    # Find expected_goals within Top stats
                    for stat in stat_group.get('stats', []):
                        if stat.get('key') == 'expected_goals':
                            xg_values = stat.get('stats', ['0.0', '0.0'])
                            return {
                                'home_xg': float(xg_values[0]) if xg_values[0] else 0.0,
                                'away_xg': float(xg_values[1]) if len(xg_values) > 1 and xg_values[1] else 0.0
                            }

            return {'home_xg': 0.0, 'away_xg': 0.0}

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
            periods = stats.get('Periods', {})
            all_period = periods.get('All', {})
            stats_array = all_period.get('stats', [])

            # Find the Top stats group and get Ball possession
            for stat_group in stats_array:
                if stat_group.get('title') == 'Top stats':
                    for stat in stat_group.get('stats', []):
                        if stat.get('key') == 'BallPossesion':
                            poss_values = stat.get('stats', [50, 50])
                            return {
                                'home_possession': float(poss_values[0]) if poss_values[0] else 50.0,
                                'away_possession': float(poss_values[1]) if len(poss_values) > 1 and poss_values[1] else 50.0
                            }

            return {'home_possession': 50.0, 'away_possession': 50.0}

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
            periods = stats.get('Periods', {})
            all_period = periods.get('All', {})
            stats_array = all_period.get('stats', [])

            # Find the Top stats group and get total shots
            for stat_group in stats_array:
                if stat_group.get('title') == 'Top stats':
                    for stat in stat_group.get('stats', []):
                        if stat.get('key') == 'total_shots':
                            shot_values = stat.get('stats', [0, 0])
                            return {
                                'home_shots': int(shot_values[0]) if shot_values[0] else 0,
                                'away_shots': int(shot_values[1]) if len(shot_values) > 1 and shot_values[1] else 0
                            }

            return {'home_shots': 0, 'away_shots': 0}

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
