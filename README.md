# ⚽ PostMatchReport - Advanced Football Match Analysis System

A professional-grade Python system for extracting, transforming, and visualizing football match data with clean **ETL architecture**.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Architecture](https://img.shields.io/badge/architecture-ETL-orange.svg)

## 🏗️ Clean Architecture

```
PostMatchReport/
├── ETL/                        # Extract, Transform, Load
│   ├── extractors/             # Data sources
│   │   ├── whoscored_extractor.py
│   │   └── fotmob_extractor.py
│   ├── transformers/           # Data processing
│   │   ├── event_processor.py
│   │   ├── player_processor.py
│   │   ├── team_processor.py
│   │   └── match_processor.py
│   └── loaders/                # Caching & loading
│       └── data_loader.py
├── Visual/                     # Visualizations
│   ├── pitch_visualizations.py
│   ├── statistical_visualizations.py
│   ├── heatmap_visualizations.py
│   └── advanced_visualizations.py
├── Reporting/                  # Report generation
│   └── report_generator.py
├── config/                     # Settings
│   └── settings.py
├── main.py                     # CLI
└── app.py                      # Web UI
```

## 🚀 Quick Start

```bash
# Install
pip install -r requirements.txt
playwright install firefox

# Generate report (CLI)
python main.py 1716104 --fotmob-id 4193558

# Or use web app
streamlit run app.py
```

## 📊 Comprehensive Data Extraction

### WhoScored (Complete Match Data)
- ✅ All events with coordinates
- ✅ Player statistics & positions
- ✅ Team formations & tactics
- ✅ Event qualifiers (xG, KeyPass, etc.)
- ✅ Match timeline & periods

### FotMob (Enhanced Statistics)
- ✅ Expected Goals (xG)
- ✅ Official team colors
- ✅ Possession metrics

## 🎨 12 Professional Visualizations

1. Match Summary Panel
2. Shot Map (with xG)
3. Match Momentum Graph
4. Pass Networks (×2)
5. xG Timeline
6. Zone 14 & Half-Spaces (×2)
7. Pitch Control Map
8. Defensive Heatmaps (×2)
9. Touch Heatmap

## 💻 Usage Examples

### CLI
```bash
python main.py 1716104 --fotmob-id 4193558 -o report.png --dpi 200
```

### Python API
```python
from Reporting.report_generator import ReportGenerator

generator = ReportGenerator()
fig = generator.generate_report(
    whoscored_id=1716104,
    fotmob_id=4193558,
    output_file="report.png"
)
```

### Custom Analysis
```python
from ETL.loaders.data_loader import DataLoader
from ETL.transformers.match_processor import MatchProcessor

# Load data
loader = DataLoader()
ws_data, fm_data = loader.load_all_data(1716104, 4193558)

# Process
processor = MatchProcessor(ws_data, fm_data)

# Get specific data
events_df = processor.get_events_dataframe()
passes = processor.get_passes(team_id=123, successful_only=True)
positions = processor.get_player_positions(team_id=123)

# Export
events_df.to_csv('events.csv')
```

## 📚 Documentation

See full documentation for:
- [Data Extraction](docs/extraction.md)
- [Data Transformation](docs/transformation.md)
- [Visualizations](docs/visualizations.md)
- [API Reference](docs/api.md)

## 🏗️ Architecture Benefits

**Separation of Concerns:**
- ETL handles data operations
- Visual handles rendering
- Reporting coordinates everything

**Modularity:**
- Easy to add new data sources
- Simple to create custom visualizations
- Flexible report layouts

**Reusability:**
- Use components independently
- Mix and match visualizations
- Export data at any stage

## 🔍 Finding Match IDs

**WhoScored:** `whoscored.com/Matches/{ID}/Live/...`  
**FotMob:** `fotmob.com/matches/{ID}/...`

## 🤝 Contributing

The clean architecture makes it easy to extend!

---

**Made with ⚽ and clean code principles**
