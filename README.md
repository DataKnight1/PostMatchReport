# ⚽ PostMatchReport - Football Match Analysis System

A comprehensive Python system to extract football match data from WhoScored and FotMob, and generate detailed match reports with 12 advanced visualizations.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🌟 Features

### Data Extraction
- **WhoScored Integration**: Extract data from all match sections
  - Preview (pre-match info)
  - Head to Head (historical data)
  - Betting (odds and markets)
  - Match Centre (live statistics)
  - Match Report (detailed events)

- **FotMob Integration**: Enhanced statistics
  - Expected Goals (xG)
  - Team colors
  - Possession data
  - Additional match statistics

### Match Report Visualizations (12 Total)
1. **Match Summary Panel** - Key statistics comparison
2. **Shot Map** - All shots with xG values and outcomes
3. **Match Momentum Graph** - Possession flow over time
4. **Pass Networks** (Home & Away) - Player connections and positioning
5. **Key Passes & Assists Map** - Attacking creativity
6. **Zone 14 & Half-Spaces** (Home & Away) - Advanced attacking zones
7. **Penalty Box Entries** - Box penetrations from both teams
8. **Defensive Actions Heatmaps** (Home & Away) - Pressure zones
9. **Pitch Control Map** - Territorial dominance by zones

### Web Application
- **Streamlit Interface**: User-friendly web app
- **Interactive Reports**: Generate and download reports
- **Caching System**: Fast re-generation of reports
- **Export Options**: Download high-quality PNG reports

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/PostMatchReport.git
cd PostMatchReport
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install Playwright browsers:**
```bash
playwright install firefox
```

## 🚀 Quick Start

### Method 1: Web Application (Recommended)

Launch the Streamlit web app:

```bash
streamlit run app.py
```

Then:
1. Enter WhoScored Match ID
2. (Optional) Enter FotMob Match ID for enhanced stats
3. Click "Generate Report"
4. Download the generated report

### Method 2: Command Line

Generate a report from command line:

```bash
python generate_report.py 1716104 --fotmob-id 4193558 --output my_report.png
```

Options:
- `--fotmob-id`: FotMob match ID (optional)
- `--output`: Output file path
- `--dpi`: Image quality (default: 150)
- `--no-cache`: Disable data caching
- `--display`: Display the report after generation

### Method 3: Python Script

```python
from generate_report import MatchReportGenerator

# Initialize generator
generator = MatchReportGenerator()

# Generate and save report
fig = generator.generate_report(
    whoscored_id=1716104,
    fotmob_id=4193558,  # Optional
    output_file="match_report.png",
    dpi=150
)
```

## 📚 Usage Examples

### Extract WhoScored Data Only

```python
from whoscored_extractor import WhoScoredExtractor

extractor = WhoScoredExtractor(headless=True)

# Extract all sections
all_data = extractor.extract_all_sections(match_id=1716104)

# Or extract specific sections
preview = extractor.extract_preview(match_id=1716104)
match_report = extractor.extract_match_report(match_id=1716104)

# Save to JSON
extractor.save_to_json(all_data, "match_data.json")
```

### Extract FotMob Data

```python
from fotmob_extractor import FotMobExtractor

extractor = FotMobExtractor()

# Extract all stats
stats = extractor.extract_all_stats(match_id=4193558)

print(f"Home xG: {stats['xg']['home_xg']}")
print(f"Away xG: {stats['xg']['away_xg']}")
print(f"Home Color: {stats['team_colors']['home_color']}")
```

### Process and Analyze Data

```python
from match_data_processor import MatchDataProcessor
import json

# Load extracted data
with open('whoscored_data.json', 'r') as f:
    whoscored_data = json.load(f)

with open('fotmob_data.json', 'r') as f:
    fotmob_data = json.load(f)

# Process data
processor = MatchDataProcessor(whoscored_data, fotmob_data)

# Get match info
team_info = processor.get_team_info()
print(f"{team_info['home']['name']} vs {team_info['away']['name']}")

# Get all passes
passes_df = processor.get_passes_df(successful_only=True)

# Get shots
shots_df = processor.get_shots_df()

# Get defensive actions
defensive_df = processor.get_defensive_actions_df()

# Export to CSV
processor.save_processed_data("processed_match.csv")
```

### Create Custom Visualizations

```python
from match_data_processor import MatchDataProcessor
from match_visualizations import MatchVisualizer
import matplotlib.pyplot as plt
from mplsoccer import Pitch

# Process data
processor = MatchDataProcessor(whoscored_data, fotmob_data)
team_info = processor.get_team_info()

# Create visualizer
viz = MatchVisualizer(processor, team_info)

# Create custom visualization
fig, ax = plt.subplots(figsize=(12, 8))
viz.create_shot_map(ax)
plt.savefig("custom_shot_map.png", dpi=150, bbox_inches='tight')
```

## 🔍 Finding Match IDs

### WhoScored Match ID
1. Go to [WhoScored.com](https://www.whoscored.com)
2. Navigate to any match page
3. Look at the URL: `https://www.whoscored.com/Matches/{MATCH_ID}/Live/...`
4. The number is your match ID (e.g., `1716104`)

### FotMob Match ID
1. Go to [FotMob.com](https://www.fotmob.com)
2. Navigate to any match page
3. Look at the URL: `https://www.fotmob.com/matches/{MATCH_ID}/...`
4. The number is your match ID (e.g., `4193558`)

## 📊 What's in the Report?

### 1. Match Summary Panel
- Final score
- League and date
- Possession percentages
- xG (Expected Goals)
- Total shots

### 2. Shot Map
- All shots from both teams
- Shot outcomes (goal, on target, off target)
- xG visualization (opacity based on xG value)
- Mirrored view for away team

### 3. Match Momentum
- Possession flow over time
- Goal markers
- Period transitions
- Team dominance visualization

### 4. Pass Networks
- Starting XI player positions
- Pass connections between players
- Line thickness shows pass frequency
- Average positions on pitch

### 5. Key Passes & Assists
- All key passes (passes leading to shots)
- Assists highlighted with stars
- Direction and location of creative passes

### 6. Zone 14 & Half-Spaces
- Highlighted attacking zones
- Passes in dangerous areas
- Both teams analyzed separately

### 7. Box Entries
- Successful entries into penalty area
- Entry points and directions
- Both passes and carries

### 8. Defensive Actions Heatmaps
- Tackles, interceptions, clearances
- Pressure zones
- Defensive positioning
- Smoothed heatmap visualization

### 9. Pitch Control
- Territorial dominance by zones
- 6x5 grid analysis
- Color-coded team control

## 🗂️ Project Structure

```
PostMatchReport/
├── app.py                      # Streamlit web application
├── generate_report.py          # Main report generator
├── whoscored_extractor.py      # WhoScored data extraction
├── fotmob_extractor.py         # FotMob data extraction
├── match_data_processor.py     # Data processing and aggregation
├── match_visualizations.py     # All 12 visualizations
├── data_analyzer.py            # Data analysis utilities
├── example_usage.py            # Usage examples
├── requirements.txt            # Python dependencies
├── cache/                      # Cached data (auto-created)
└── README.md                   # This file
```

## 🛠️ API Reference

### WhoScoredExtractor

```python
extractor = WhoScoredExtractor(headless=True, browser_type="firefox")

# Extract specific sections
extractor.extract_preview(match_id)
extractor.extract_head_to_head(match_id)
extractor.extract_betting(match_id)
extractor.extract_match_centre(match_id)
extractor.extract_match_report(match_id)

# Extract all sections
extractor.extract_all_sections(match_id)
```

### FotMobExtractor

```python
extractor = FotMobExtractor()

# Get all statistics
extractor.extract_all_stats(match_id)

# Get specific data
extractor.get_match_details(match_id)
extractor.extract_team_colors(match_data)
extractor.extract_xg_data(match_data)
```

### MatchDataProcessor

```python
processor = MatchDataProcessor(whoscored_data, fotmob_data)

# Get processed data
processor.get_team_info()
processor.get_passes_df(team_id, successful_only)
processor.get_shots_df(team_id)
processor.get_defensive_actions_df(team_id)
processor.get_passes_between_players(team_id)
processor.get_player_average_positions(team_id)
```

### MatchReportGenerator

```python
generator = MatchReportGenerator(cache_dir="./cache")

# Extract data
whoscored_data, fotmob_data = generator.extract_all_data(
    whoscored_id, fotmob_id, use_cache=True
)

# Generate report
fig = generator.generate_report(
    whoscored_id, fotmob_id, output_file, use_cache, dpi
)
```

## 🎨 Customization

### Change Team Colors

```python
team_info['team_colors'] = {
    'home_color': '#FF0000',  # Red
    'away_color': '#0000FF'   # Blue
}
```

### Adjust Figure Size and DPI

```python
fig = create_full_match_report(processor, team_info, figsize=(24, 26))
fig.savefig("report.png", dpi=300)  # High quality
```

### Filter Events

```python
# Only successful passes
passes = processor.get_passes_df(successful_only=True)

# Only home team shots
shots = processor.get_shots_df(team_id=home_team_id)

# Defensive actions from first half
defensive = processor.get_defensive_actions_df()
first_half = defensive[defensive['period_value'] == 1]
```

## 🐛 Troubleshooting

### Playwright Browser Issues

```bash
# Reinstall browsers
playwright install firefox

# Try different browser
extractor = WhoScoredExtractor(browser_type="chromium")
```

### Memory Issues

```python
# Use lower DPI
generator.generate_report(whoscored_id, dpi=80)

# Clear cache
import shutil
shutil.rmtree("./cache")
```

### No Data Found

- Verify match ID is correct
- Check if match has been played
- Ensure internet connection is stable
- Try disabling cache: `use_cache=False`

## 📝 Dependencies

- **playwright**: Browser automation for web scraping
- **requests**: HTTP library for API calls
- **beautifulsoup4**: HTML parsing
- **pandas**: Data manipulation
- **numpy**: Numerical computing
- **matplotlib**: Plotting and visualization
- **mplsoccer**: Football pitch visualization
- **streamlit**: Web application framework
- **scipy**: Scientific computing
- **Pillow**: Image processing

## 📄 License

This project is for educational purposes. Please respect the Terms of Service of WhoScored and FotMob when using this tool.

## 🙏 Acknowledgments

- Inspired by [ibidi/streamlit_whoscored_match_report](https://github.com/ibidi/streamlit_whoscored_match_report)
- Built upon work by developer 'adnaaan433'
- Uses [mplsoccer](https://mplsoccer.readthedocs.io/) for pitch visualizations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or issues, please open an issue on GitHub.

---

**Made with ⚽ for football analytics enthusiasts**
