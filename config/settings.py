"""
Configuration Settings
Default settings for the PostMatchReport system.
"""

# Visualization settings
PITCH_COLOR = '#d6c39f'
LINE_COLOR = '#0e1117'
BACKGROUND_COLOR = '#f0f0f0'

# Default team colors (fallback)
DEFAULT_HOME_COLOR = '#FF0000'
DEFAULT_AWAY_COLOR = '#0000FF'

# Figure settings
DEFAULT_FIGSIZE = (20, 22)
DEFAULT_DPI = 150

# Cache settings
CACHE_DIR = './cache'
USE_CACHE_BY_DEFAULT = True

# Browser settings
BROWSER_TYPE = 'chromium'  # 'firefox', 'chromium', or 'webkit'
HEADLESS = True

# Data extraction
FETCH_TIMEOUT = 60000  # milliseconds

# Visualization thresholds
MIN_PASSES_FOR_NETWORK = 3
MIN_EVENTS_FOR_HEATMAP = 5
MIN_SHOTS_FOR_XG_TIMELINE = 1

# Zone definitions (meters)
ZONE_14 = {
    'x_min': 70,
    'x_max': 87.5,
    'y_min': 20.4,
    'y_max': 47.6
}

HALF_SPACES = {
    'left': {'x_min': 70, 'x_max': 87.5, 'y_min': 10.2, 'y_max': 27.2},
    'right': {'x_min': 70, 'x_max': 87.5, 'y_min': 40.8, 'y_max': 57.8}
}

# Pitch dimensions
PITCH_LENGTH = 105
PITCH_WIDTH = 68
