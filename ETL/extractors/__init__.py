"""
Extractors Package
Data extraction from various sources (WhoScored, FotMob, etc.)
"""

from .whoscored_extractor import WhoScoredExtractor
from .fotmob_extractor import FotMobExtractor

__all__ = ['WhoScoredExtractor', 'FotMobExtractor']
