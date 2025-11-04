"""
WhoScored Data Extractor
Extracts data from all WhoScored match sections:
- Preview
- Head to Head
- Betting
- Match Centre
- Match Report
"""

import re
import json
from typing import Dict, Any, Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


class WhoScoredExtractor:
    """Extract data from WhoScored match pages."""

    BASE_URL = "https://www.whoscored.com/Matches/{match_id}/{section}"

    # Regex pattern to extract embedded JSON data
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
            # Launch browser
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

                # Navigate to page
                if wait_for_idle:
                    page.goto(url, wait_until="networkidle", timeout=60000)
                else:
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)

                # Get HTML content
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

        # Extract and clean JSON string
        json_str = match.group(0)
        json_str = json_str.rstrip(';').strip()

        try:
            data = json.loads(json_str)
            return data
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None

    def extract_preview(self, match_id: int) -> Dict[str, Any]:
        """
        Extract data from Preview section.

        Args:
            match_id: WhoScored match ID

        Returns:
            Dictionary containing preview data
        """
        url = self.BASE_URL.format(match_id=match_id, section="Preview")
        print(f"Fetching Preview data from: {url}")

        try:
            html = self._fetch_page_content(url)
            data = self._extract_json_from_html(html)

            if data:
                # Extract relevant preview information
                return {
                    'section': 'preview',
                    'match_id': match_id,
                    'url': url,
                    'data': data,
                    'success': True
                }
            else:
                return {
                    'section': 'preview',
                    'match_id': match_id,
                    'url': url,
                    'error': 'No JSON data found',
                    'success': False
                }
        except Exception as e:
            return {
                'section': 'preview',
                'match_id': match_id,
                'url': url,
                'error': str(e),
                'success': False
            }

    def extract_head_to_head(self, match_id: int) -> Dict[str, Any]:
        """
        Extract data from Head to Head section.

        Args:
            match_id: WhoScored match ID

        Returns:
            Dictionary containing head to head data
        """
        url = self.BASE_URL.format(match_id=match_id, section="Head-To-Head")
        print(f"Fetching Head to Head data from: {url}")

        try:
            html = self._fetch_page_content(url)
            data = self._extract_json_from_html(html)

            if data:
                return {
                    'section': 'head_to_head',
                    'match_id': match_id,
                    'url': url,
                    'data': data,
                    'success': True
                }
            else:
                return {
                    'section': 'head_to_head',
                    'match_id': match_id,
                    'url': url,
                    'error': 'No JSON data found',
                    'success': False
                }
        except Exception as e:
            return {
                'section': 'head_to_head',
                'match_id': match_id,
                'url': url,
                'error': str(e),
                'success': False
            }

    def extract_betting(self, match_id: int) -> Dict[str, Any]:
        """
        Extract data from Betting section.

        Args:
            match_id: WhoScored match ID

        Returns:
            Dictionary containing betting data
        """
        url = self.BASE_URL.format(match_id=match_id, section="Betting")
        print(f"Fetching Betting data from: {url}")

        try:
            html = self._fetch_page_content(url)
            data = self._extract_json_from_html(html)

            if data:
                return {
                    'section': 'betting',
                    'match_id': match_id,
                    'url': url,
                    'data': data,
                    'success': True
                }
            else:
                return {
                    'section': 'betting',
                    'match_id': match_id,
                    'url': url,
                    'error': 'No JSON data found',
                    'success': False
                }
        except Exception as e:
            return {
                'section': 'betting',
                'match_id': match_id,
                'url': url,
                'error': str(e),
                'success': False
            }

    def extract_match_centre(self, match_id: int) -> Dict[str, Any]:
        """
        Extract data from Match Centre section.

        Args:
            match_id: WhoScored match ID

        Returns:
            Dictionary containing match centre data with detailed event information
        """
        url = self.BASE_URL.format(match_id=match_id, section="MatchCentre")
        print(f"Fetching Match Centre data from: {url}")

        try:
            html = self._fetch_page_content(url)
            data = self._extract_json_from_html(html)

            if data:
                return {
                    'section': 'match_centre',
                    'match_id': match_id,
                    'url': url,
                    'data': data,
                    'success': True
                }
            else:
                return {
                    'section': 'match_centre',
                    'match_id': match_id,
                    'url': url,
                    'error': 'No JSON data found',
                    'success': False
                }
        except Exception as e:
            return {
                'section': 'match_centre',
                'match_id': match_id,
                'url': url,
                'error': str(e),
                'success': False
            }

    def extract_match_report(self, match_id: int) -> Dict[str, Any]:
        """
        Extract data from Match Report/Live section.
        This contains detailed match events, player positions, and statistics.

        Args:
            match_id: WhoScored match ID

        Returns:
            Dictionary containing match report data with events and statistics
        """
        url = self.BASE_URL.format(match_id=match_id, section="Live")
        print(f"Fetching Match Report data from: {url}")

        try:
            html = self._fetch_page_content(url)
            data = self._extract_json_from_html(html)

            if data:
                return {
                    'section': 'match_report',
                    'match_id': match_id,
                    'url': url,
                    'data': data,
                    'success': True
                }
            else:
                return {
                    'section': 'match_report',
                    'match_id': match_id,
                    'url': url,
                    'error': 'No JSON data found',
                    'success': False
                }
        except Exception as e:
            return {
                'section': 'match_report',
                'match_id': match_id,
                'url': url,
                'error': str(e),
                'success': False
            }

    def extract_all_sections(self, match_id: int) -> Dict[str, Any]:
        """
        Extract data from all sections of a match.

        Args:
            match_id: WhoScored match ID

        Returns:
            Dictionary containing data from all sections
        """
        print(f"\n{'='*60}")
        print(f"Extracting all data for Match ID: {match_id}")
        print(f"{'='*60}\n")

        results = {
            'match_id': match_id,
            'sections': {}
        }

        # Extract from each section
        results['sections']['preview'] = self.extract_preview(match_id)
        print()

        results['sections']['head_to_head'] = self.extract_head_to_head(match_id)
        print()

        results['sections']['betting'] = self.extract_betting(match_id)
        print()

        results['sections']['match_centre'] = self.extract_match_centre(match_id)
        print()

        results['sections']['match_report'] = self.extract_match_report(match_id)
        print()

        # Summary
        successful = sum(1 for section in results['sections'].values() if section['success'])
        total = len(results['sections'])

        print(f"{'='*60}")
        print(f"Extraction Complete: {successful}/{total} sections successful")
        print(f"{'='*60}\n")

        return results

    def save_to_json(self, data: Dict[str, Any], filename: str):
        """
        Save extracted data to JSON file.

        Args:
            data: Data to save
            filename: Output filename
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to: {filename}")
