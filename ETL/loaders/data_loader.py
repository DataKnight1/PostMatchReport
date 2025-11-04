"""
Data Loader
Handles loading, caching, and saving of match data.
"""

import json
import os
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from ETL.extractors.whoscored_extractor import WhoScoredExtractor
from ETL.extractors.fotmob_extractor import FotMobExtractor


class DataLoader:
    """Load and cache match data from various sources."""

    def __init__(self, cache_dir: str = "./cache"):
        """
        Initialize data loader.

        Args:
            cache_dir: Directory for caching data
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

        self.whoscored_extractor = WhoScoredExtractor(headless=True)
        self.fotmob_extractor = FotMobExtractor()

    def load_whoscored_data(self, match_id: int, use_cache: bool = True) -> Dict[str, Any]:
        """
        Load WhoScored data with caching.

        Args:
            match_id: WhoScored match ID
            use_cache: Use cached data if available

        Returns:
            WhoScored match data
        """
        cache_file = os.path.join(self.cache_dir, f"whoscored_{match_id}.json")

        # Try cache first
        if use_cache and os.path.exists(cache_file):
            print(f"Loading WhoScored data from cache: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        # Extract fresh data
        print(f"Extracting fresh WhoScored data for match {match_id}...")
        data = self.whoscored_extractor.extract_all_sections(match_id)

        # Cache the data
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Data cached to: {cache_file}")

        return data

    def load_fotmob_data(self, match_id: int, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Load FotMob data with caching.

        Args:
            match_id: FotMob match ID
            use_cache: Use cached data if available

        Returns:
            FotMob match data or None
        """
        if not match_id:
            return None

        cache_file = os.path.join(self.cache_dir, f"fotmob_{match_id}.json")

        # Try cache first
        if use_cache and os.path.exists(cache_file):
            print(f"Loading FotMob data from cache: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        # Extract fresh data
        print(f"Extracting fresh FotMob data for match {match_id}...")
        data = self.fotmob_extractor.extract_all_stats(match_id)

        # Cache the data
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Data cached to: {cache_file}")

        return data

    def load_all_data(self, whoscored_id: int, fotmob_id: Optional[int] = None,
                     use_cache: bool = True) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Load both WhoScored and FotMob data.

        Args:
            whoscored_id: WhoScored match ID
            fotmob_id: FotMob match ID (optional)
            use_cache: Use cached data

        Returns:
            Tuple of (whoscored_data, fotmob_data)
        """
        whoscored_data = self.load_whoscored_data(whoscored_id, use_cache)
        fotmob_data = self.load_fotmob_data(fotmob_id, use_cache) if fotmob_id else None

        return whoscored_data, fotmob_data

    def save_processed_data(self, data: Dict[str, Any], filename: str):
        """
        Save processed data to file.

        Args:
            data: Processed data dictionary
            filename: Output filename
        """
        filepath = os.path.join(self.cache_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Processed data saved to: {filepath}")

    def clear_cache(self, match_id: Optional[int] = None):
        """
        Clear cached data.

        Args:
            match_id: Clear specific match ID, or all if None
        """
        if match_id:
            # Clear specific match
            ws_file = os.path.join(self.cache_dir, f"whoscored_{match_id}.json")
            fm_file = os.path.join(self.cache_dir, f"fotmob_{match_id}.json")

            if os.path.exists(ws_file):
                os.remove(ws_file)
                print(f"Removed: {ws_file}")

            if os.path.exists(fm_file):
                os.remove(fm_file)
                print(f"Removed: {fm_file}")
        else:
            # Clear all cache
            import shutil
            if os.path.exists(self.cache_dir):
                shutil.rmtree(self.cache_dir)
                os.makedirs(self.cache_dir)
                print(f"Cleared all cache in: {self.cache_dir}")
