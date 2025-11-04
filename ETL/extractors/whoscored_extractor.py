"""
Enhanced WhoScored Data Extractor
Extracts comprehensive match data from all WhoScored sections with detailed parsing.
"""

import re
import json
from typing import Dict, Any, Optional, List
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


class WhoScoredExtractor:
    """Extract comprehensive data from WhoScored match pages."""

    BASE_URL = "https://www.whoscored.com/Matches/{match_id}/{section}"
    JSON_REGEX = r'(?<=require\.config\.params\["args"\]\s=\s)[\s\S]*?;'

    def __init__(self, headless: bool = True, browser_type: str = "firefox"):
        """
        Initialize the extractor.

        Args:
            headless: Run browser in headless mode
            browser_type: Browser to use ('firefox', 'chromium', 'webkit')
        """
        self.headless = headless
        self.browser_type = browser_type

    def _fetch_page_content(self, url: str, wait_for_idle: bool = True) -> str:
        """
        Fetch page content using Playwright.

        Args:
            url: URL to fetch
            wait_for_idle: Wait for network idle before returning

        Returns:
            HTML content of the page
        """
        with sync_playwright() as p:
            if self.browser_type == "firefox":
                browser = p.firefox.launch(headless=self.headless)
            elif self.browser_type == "chromium":
                browser = p.chromium.launch(headless=self.headless)
            else:
                browser = p.webkit.launch(headless=self.headless)

            try:
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()

                if wait_for_idle:
                    page.goto(url, wait_until="networkidle", timeout=60000)
                else:
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)

                html = page.content()
                return html
            finally:
                browser.close()

    def _extract_json_from_html(self, html: str) -> Optional[Dict[str, Any]]:
        """
        Extract embedded JSON data from HTML.

        Args:
            html: HTML content

        Returns:
            Parsed JSON data or None if not found
        """
        match = re.search(self.JSON_REGEX, html)
        if not match:
            return None

        json_str = match.group(0).rstrip(';').strip()

        try:
            data = json.loads(json_str)
            return data
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None

    def extract_match_centre_detailed(self, match_id: int) -> Dict[str, Any]:
        """
        Extract comprehensive Match Centre data with all available information.

        Args:
            match_id: WhoScored match ID

        Returns:
            Dictionary containing all match centre data
        """
        url = self.BASE_URL.format(match_id=match_id, section="Live")
        print(f"Extracting comprehensive Match Centre data from: {url}")

        try:
            html = self._fetch_page_content(url)
            raw_data = self._extract_json_from_html(html)

            if not raw_data:
                return {'success': False, 'error': 'No JSON data found'}

            # Extract matchCentreData
            match_centre_data = raw_data.get('matchCentreData', {})

            # Parse all components
            result = {
                'match_id': match_id,
                'success': True,
                'url': url,

                # Basic match info
                'match_info': self._parse_match_info(match_centre_data),

                # Teams
                'home_team': self._parse_team_data(match_centre_data.get('home', {})),
                'away_team': self._parse_team_data(match_centre_data.get('away', {})),

                # Events
                'events': self._parse_events(match_centre_data.get('events', [])),

                # Players
                'players': self._parse_all_players(match_centre_data),

                # Team stats
                'team_stats': self._parse_team_stats(match_centre_data),

                # Period data
                'periods': self._parse_periods(match_centre_data),

                # Formation
                'formations': self._parse_formations(match_centre_data),

                # Event types mapping
                'event_types': raw_data.get('matchCentreEventTypeJson', []),

                # Player ID to name mapping
                'player_id_map': raw_data.get('playerIdNameDictionary', {}),

                # Formation mappings
                'formation_map': raw_data.get('formationIdNameMappings', {}),

                # Raw data for advanced use
                'raw_match_centre': match_centre_data
            }

            return result

        except Exception as e:
            return {
                'match_id': match_id,
                'url': url,
                'success': False,
                'error': str(e)
            }

    def _parse_match_info(self, data: Dict) -> Dict[str, Any]:
        """Parse basic match information."""
        return {
            'score': data.get('score'),
            'ft_score': data.get('ftScore'),
            'ht_score': data.get('htScore'),
            'et_score': data.get('etScore'),
            'pk_score': data.get('pkScore'),
            'venue': data.get('venueName'),
            'date': data.get('startDate'),
            'start_time': data.get('startTime'),
            'referee': data.get('referee', {}).get('name'),
            'attendance': data.get('attendance'),
            'weather': data.get('weatherCode'),
            'elapsed_time': data.get('elapsed'),
            'period': data.get('period'),
            'competition': data.get('competition', {}),
            'season': data.get('season'),
            'week': data.get('week')
        }

    def _parse_team_data(self, team_data: Dict) -> Dict[str, Any]:
        """Parse comprehensive team data."""
        return {
            'team_id': team_data.get('teamId'),
            'name': team_data.get('name'),
            'country_name': team_data.get('countryName'),
            'manager': team_data.get('managerName'),
            'formation': team_data.get('formations'),
            'players': team_data.get('players', []),
            'player_id_map': team_data.get('playerIdNameDictionary', {}),
            'stats': team_data.get('stats', {}),
            'scores': {
                'fulltime': team_data.get('scores', {}).get('fulltime'),
                'halftime': team_data.get('scores', {}).get('halftime'),
                'extra_time': team_data.get('scores', {}).get('extratime')
            },
            'incidents': team_data.get('incidents', [])
        }

    def _parse_events(self, events: List[Dict]) -> Dict[str, Any]:
        """Parse and categorize all match events."""
        if not events:
            return {}

        categorized = {
            'all_events': events,
            'by_type': {},
            'by_period': {},
            'by_team': {},
            'timeline': [],
            'key_events': []
        }

        # Categorize events
        for event in events:
            # By type
            event_type = event.get('type', {}).get('displayName', 'Unknown')
            if event_type not in categorized['by_type']:
                categorized['by_type'][event_type] = []
            categorized['by_type'][event_type].append(event)

            # By period
            period = event.get('period', {}).get('displayName', 'Unknown')
            if period not in categorized['by_period']:
                categorized['by_period'][period] = []
            categorized['by_period'][period].append(event)

            # By team
            team_id = event.get('teamId')
            if team_id not in categorized['by_team']:
                categorized['by_team'][team_id] = []
            categorized['by_team'][team_id].append(event)

            # Key events (goals, cards, substitutions)
            if event_type in ['Goal', 'SubstitutionOn', 'SubstitutionOff', 'Card']:
                categorized['key_events'].append(event)

        # Create timeline
        categorized['timeline'] = sorted(events, key=lambda x: (
            x.get('period', {}).get('value', 0),
            x.get('minute', 0),
            x.get('second', 0)
        ))

        # Statistics
        categorized['stats'] = {
            'total_events': len(events),
            'event_types_count': {k: len(v) for k, v in categorized['by_type'].items()},
            'period_count': {k: len(v) for k, v in categorized['by_period'].items()}
        }

        return categorized

    def _parse_all_players(self, data: Dict) -> Dict[str, Any]:
        """Parse all player data including statistics."""
        home_players = data.get('home', {}).get('players', [])
        away_players = data.get('away', {}).get('players', [])

        all_players = []
        for player in home_players + away_players:
            parsed_player = {
                'player_id': player.get('playerId'),
                'name': player.get('name'),
                'shirt_no': player.get('shirtNo'),
                'position': player.get('position'),
                'age': player.get('age'),
                'height': player.get('height'),
                'weight': player.get('weight'),
                'is_first_eleven': player.get('isFirstEleven'),
                'is_captain': player.get('isCaptain'),
                'team_id': player.get('teamId'),
                'stats': player.get('stats', {}),
                'ratings': {
                    'overall': player.get('rating'),
                    'detailed': player.get('ratings', {})
                },
                'substitute_info': {
                    'is_man_of_match': player.get('isManOfTheMatch'),
                    'subon_minute': player.get('subOnMin'),
                    'suboff_minute': player.get('subOffMin')
                }
            }
            all_players.append(parsed_player)

        return {
            'all_players': all_players,
            'home_players': [p for p in all_players if p['team_id'] == data.get('home', {}).get('teamId')],
            'away_players': [p for p in all_players if p['team_id'] == data.get('away', {}).get('teamId')],
            'starting_xi': {
                'home': [p for p in all_players if p['is_first_eleven'] and p['team_id'] == data.get('home', {}).get('teamId')],
                'away': [p for p in all_players if p['is_first_eleven'] and p['team_id'] == data.get('away', {}).get('teamId')]
            },
            'substitutes': {
                'home': [p for p in all_players if not p['is_first_eleven'] and p['team_id'] == data.get('home', {}).get('teamId')],
                'away': [p for p in all_players if not p['is_first_eleven'] and p['team_id'] == data.get('away', {}).get('teamId')]
            }
        }

    def _parse_team_stats(self, data: Dict) -> Dict[str, Any]:
        """Parse team-level statistics."""
        home_stats = data.get('home', {}).get('stats', {})
        away_stats = data.get('away', {}).get('stats', {})

        return {
            'home': home_stats,
            'away': away_stats,
            'comparison': self._compare_stats(home_stats, away_stats)
        }

    def _compare_stats(self, home_stats: Dict, away_stats: Dict) -> Dict[str, Any]:
        """Compare statistics between teams."""
        comparison = {}

        all_stat_keys = set(home_stats.keys()) | set(away_stats.keys())

        for key in all_stat_keys:
            home_val = home_stats.get(key, 0)
            away_val = away_stats.get(key, 0)

            comparison[key] = {
                'home': home_val,
                'away': away_val,
                'total': home_val + away_val if isinstance(home_val, (int, float)) and isinstance(away_val, (int, float)) else None,
                'home_percentage': (home_val / (home_val + away_val) * 100) if isinstance(home_val, (int, float)) and isinstance(away_val, (int, float)) and (home_val + away_val) > 0 else None
            }

        return comparison

    def _parse_periods(self, data: Dict) -> List[Dict]:
        """Parse period information."""
        periods = []

        # Extract period data from events or other sources
        seen_periods = set()
        events = data.get('events', [])

        for event in events:
            period_data = event.get('period', {})
            period_value = period_data.get('value')

            if period_value and period_value not in seen_periods:
                periods.append({
                    'value': period_value,
                    'display_name': period_data.get('displayName'),
                    'short_name': period_data.get('shortName')
                })
                seen_periods.add(period_value)

        return sorted(periods, key=lambda x: x['value'])

    def _parse_formations(self, data: Dict) -> Dict[str, Any]:
        """Parse formation information."""
        return {
            'home': data.get('home', {}).get('formations', []),
            'away': data.get('away', {}).get('formations', [])
        }

    def extract_all_sections(self, match_id: int) -> Dict[str, Any]:
        """
        Extract data from all sections (kept for backwards compatibility).

        Args:
            match_id: WhoScored match ID

        Returns:
            Dictionary containing data from all sections
        """
        print(f"\n{'='*60}")
        print(f"Extracting comprehensive data for Match ID: {match_id}")
        print(f"{'='*60}\n")

        # Get comprehensive match centre data
        match_centre = self.extract_match_centre_detailed(match_id)

        results = {
            'match_id': match_id,
            'match_centre': match_centre
        }

        print(f"{'='*60}")
        print(f"Extraction Complete")
        print(f"{'='*60}\n")

        return results

    def save_to_json(self, data: Dict[str, Any], filename: str):
        """Save extracted data to JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to: {filename}")
