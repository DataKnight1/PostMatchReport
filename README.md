# WhoScored Data Extractor

A comprehensive Python tool to extract data from all WhoScored match sections including Preview, Head to Head, Betting, Match Centre, and Match Report.

## Features

- **Complete Data Extraction**: Extract data from all WhoScored match sections
- **Browser Automation**: Uses Playwright for reliable data extraction
- **Multiple Sections Support**:
  - **Preview**: Pre-match information and predictions
  - **Head to Head**: Historical matchup data between teams
  - **Betting**: Odds and betting information
  - **Match Centre**: Live match statistics and events
  - **Match Report**: Detailed match events, player positions, and comprehensive statistics

- **Data Analysis Tools**: Built-in utilities to parse and analyze extracted data
- **Export Options**: Save data to JSON and CSV formats
- **Pandas Integration**: Convert match events to DataFrame for easy analysis

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd PostMatchReport
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install firefox
```

## Quick Start

### Extract All Data from a Match

```python
from whoscored_extractor import WhoScoredExtractor

# Initialize extractor
extractor = WhoScoredExtractor(headless=True, browser_type="firefox")

# Extract data from all sections
match_id = 1716104  # Replace with your match ID
all_data = extractor.extract_all_sections(match_id)

# Save to JSON
extractor.save_to_json(all_data, f"match_{match_id}_data.json")
```

### Extract Data from a Single Section

```python
from whoscored_extractor import WhoScoredExtractor

extractor = WhoScoredExtractor()
match_id = 1716104

# Extract only Match Report
match_report = extractor.extract_match_report(match_id)

# Extract only Preview
preview = extractor.extract_preview(match_id)

# Extract only Head to Head
h2h = extractor.extract_head_to_head(match_id)
```

### Analyze Extracted Data

```python
from data_analyzer import WhoScoredDataAnalyzer

# Load extracted data
analyzer = WhoScoredDataAnalyzer("match_1716104_data.json")

# Get match information
match_info = analyzer.get_match_info()
print(f"{match_info['home_team']} vs {match_info['away_team']}")

# Get all events
events = analyzer.get_match_events()

# Convert events to DataFrame
df = analyzer.events_to_dataframe()
df.to_csv("match_events.csv", index=False)

# Get specific event types
shots = analyzer.get_events_by_type("Shot")
passes = analyzer.get_events_by_type("Pass")

# Print summary
analyzer.print_summary()
```

## Finding Match IDs

To find a WhoScored match ID:

1. Visit [WhoScored.com](https://www.whoscored.com)
2. Navigate to any match page
3. Look at the URL: `https://www.whoscored.com/Matches/{MATCH_ID}/Live/...`
4. The match ID is the number in the URL (e.g., `1716104`)

## Usage Examples

### Example 1: Extract and Analyze

```bash
# Run the example script
python example_usage.py
```

This will:
- Extract data from all sections
- Save to JSON file
- Print extraction summary

### Example 2: Analyze Saved Data

```bash
# Analyze previously extracted data
python data_analyzer.py match_1716104_data.json
```

This will:
- Load the JSON file
- Print data summary
- Export events to CSV

## Data Structure

### Extracted Data Format

```json
{
  "match_id": 1716104,
  "sections": {
    "preview": {
      "section": "preview",
      "match_id": 1716104,
      "url": "https://www.whoscored.com/Matches/1716104/Preview",
      "data": { ... },
      "success": true
    },
    "head_to_head": { ... },
    "betting": { ... },
    "match_centre": { ... },
    "match_report": { ... }
  }
}
```

### Available Data Points

**Match Report Section** includes:
- Match events (passes, shots, tackles, etc.)
- Player positions and formations
- Event coordinates (x, y)
- Event outcomes and qualifiers
- Period information
- Player and team IDs

**Preview Section** includes:
- Pre-match predictions
- Team form
- Expected lineups

**Head to Head Section** includes:
- Previous meetings
- Historical results
- Performance trends

**Betting Section** includes:
- Odds from various bookmakers
- Betting markets
- Probability predictions

**Match Centre Section** includes:
- Live statistics
- Possession data
- Shot maps
- Key events

## API Reference

### WhoScoredExtractor

#### Methods

- `extract_preview(match_id)` - Extract preview data
- `extract_head_to_head(match_id)` - Extract head-to-head data
- `extract_betting(match_id)` - Extract betting data
- `extract_match_centre(match_id)` - Extract match centre data
- `extract_match_report(match_id)` - Extract match report data
- `extract_all_sections(match_id)` - Extract all sections
- `save_to_json(data, filename)` - Save data to JSON file

#### Parameters

- `headless` (bool): Run browser in headless mode (default: True)
- `browser_type` (str): Browser to use - 'firefox', 'chromium', or 'webkit' (default: 'firefox')

### WhoScoredDataAnalyzer

#### Methods

- `load_data(file_path)` - Load data from JSON file
- `get_match_info()` - Get basic match information
- `get_match_events()` - Get all match events
- `get_events_by_type(event_type)` - Filter events by type
- `get_player_statistics()` - Get player stats
- `get_team_statistics()` - Get team stats
- `get_head_to_head_history()` - Get H2H history
- `get_betting_odds()` - Get betting odds
- `events_to_dataframe()` - Convert events to pandas DataFrame
- `print_summary()` - Print data summary

## Dependencies

- `playwright` - Browser automation
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `pandas` - Data analysis
- `numpy` - Numerical computing
- `lxml` - XML/HTML processing

## Troubleshooting

### Browser Issues

If you encounter browser-related errors:

```bash
# Reinstall Playwright browsers
playwright install firefox

# Or try a different browser
extractor = WhoScoredExtractor(browser_type="chromium")
```

### Timeout Errors

If extraction times out:

```python
# The timeout is set to 60 seconds by default
# The page wait is configured in the _fetch_page_content method
```

### No Data Found

If extraction returns no data:
- Verify the match ID is correct
- Check if the match page exists on WhoScored
- Ensure the match has been played (for Match Report data)
- Some sections may not be available for all matches

## Notes

- **Rate Limiting**: Be respectful of WhoScored's servers. Add delays between requests when extracting multiple matches
- **Data Availability**: Not all sections may be available for all matches
- **Dynamic Content**: WhoScored pages load content dynamically, which is why we use Playwright
- **Match Status**: Some data (like Match Report) is only available after the match has been played

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is for educational purposes. Please respect WhoScored's Terms of Service when using this tool.

## Acknowledgments

- Inspired by [ibidi/streamlit_whoscored_match_report](https://github.com/ibidi/streamlit_whoscored_match_report)
- Built upon the work of developer 'adnaaan433'
