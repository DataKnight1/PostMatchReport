# Project Structure Documentation

## Clean ETL Architecture

PostMatchReport follows a professional **ETL (Extract, Transform, Load)** architecture with clear separation of concerns.

## Directory Structure

```
PostMatchReport/
│
├── ETL/                           # Extract, Transform, Load Layer
│   │
│   ├── extractors/                # Data Extraction
│   │   ├── __init__.py
│   │   ├── whoscored_extractor.py    # WhoScored data extraction
│   │   └── fotmob_extractor.py       # FotMob data extraction
│   │
│   ├── transformers/              # Data Processing
│   │   ├── __init__.py
│   │   ├── event_processor.py        # Event-level processing
│   │   ├── player_processor.py       # Player-level analytics
│   │   ├── team_processor.py         # Team-level analytics
│   │   └── match_processor.py        # Match coordinator
│   │
│   └── loaders/                   # Data Loading & Caching
│       ├── __init__.py
│       └── data_loader.py            # Cache management
│
├── Visual/                        # Visualization Layer
│   ├── __init__.py
│   ├── pitch_visualizations.py       # Pitch-based charts
│   ├── statistical_visualizations.py # Stats and comparisons
│   ├── heatmap_visualizations.py     # Heatmaps and density
│   └── advanced_visualizations.py    # Advanced analytics
│
├── Reporting/                     # Report Generation Layer
│   ├── __init__.py
│   └── report_generator.py           # Main report coordinator
│
├── config/                        # Configuration
│   └── settings.py                   # Project settings
│
├── cache/                         # Data Cache (auto-created)
│
├── main.py                        # CLI Interface
├── app.py                         # Streamlit Web Interface
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
└── README.md                      # Main documentation
```

## Layer Descriptions

### ETL Layer

#### Extractors (`ETL/extractors/`)
- **Purpose**: Fetch raw data from external sources
- **Modules**:
  - `whoscored_extractor.py`: Playwright-based scraping of WhoScored
  - `fotmob_extractor.py`: API-based extraction from FotMob
- **Outputs**: Raw JSON data

#### Transformers (`ETL/transformers/`)
- **Purpose**: Process and transform raw data into usable formats
- **Modules**:
  - `event_processor.py`: Process match events (passes, shots, etc.)
  - `player_processor.py`: Calculate player statistics and positions
  - `team_processor.py`: Aggregate team-level statistics
  - `match_processor.py`: Coordinate all transformations
- **Outputs**: Pandas DataFrames, structured dictionaries

#### Loaders (`ETL/loaders/`)
- **Purpose**: Manage data persistence and caching
- **Modules**:
  - `data_loader.py`: Load data with smart caching
- **Features**: Automatic caching, cache management

### Visual Layer (`Visual/`)

- **Purpose**: Create modular, reusable visualizations
- **Modules**:
  - `pitch_visualizations.py`: Shot maps, pass networks
  - `statistical_visualizations.py`: Match summaries, stat bars
  - `heatmap_visualizations.py`: Defensive actions, pitch control
  - `advanced_visualizations.py`: Momentum, xG timeline, Zone 14
- **Benefits**: Each visualization is independent and reusable

### Reporting Layer (`Reporting/`)

- **Purpose**: Coordinate ETL and Visual layers to produce reports
- **Modules**:
  - `report_generator.py`: Main report generation
- **Responsibilities**:
  - Load data via ETL
  - Generate visualizations via Visual
  - Combine into complete report
  - Handle output and caching

### Configuration (`config/`)

- **Purpose**: Centralized configuration
- **Settings**:
  - Visualization colors and styles
  - Default parameters
  - Zone definitions
  - Thresholds

## Data Flow

```
1. USER REQUEST
   ↓
2. EXTRACT (ETL/extractors)
   - Fetch from WhoScored
   - Fetch from FotMob
   ↓
3. TRANSFORM (ETL/transformers)
   - Process events
   - Calculate player stats
   - Aggregate team stats
   ↓
4. VISUALIZE (Visual)
   - Create pitch charts
   - Create statistical charts
   - Create heatmaps
   ↓
5. REPORT (Reporting)
   - Combine all visualizations
   - Add metadata
   - Generate final report
   ↓
6. OUTPUT
   - PNG file
   - Display in app
```

## Import Patterns

### Using Extractors
```python
from ETL.extractors.whoscored_extractor import WhoScoredExtractor
from ETL.extractors.fotmob_extractor import FotMobExtractor
```

### Using Transformers
```python
from ETL.transformers.event_processor import EventProcessor
from ETL.transformers.player_processor import PlayerProcessor
from ETL.transformers.team_processor import TeamProcessor
from ETL.transformers.match_processor import MatchProcessor
```

### Using Loaders
```python
from ETL.loaders.data_loader import DataLoader
```

### Using Visualizations
```python
from Visual.pitch_visualizations import PitchVisualizations
from Visual.statistical_visualizations import StatisticalVisualizations
from Visual.heatmap_visualizations import HeatmapVisualizations
from Visual.advanced_visualizations import AdvancedVisualizations
```

### Using Reports
```python
from Reporting.report_generator import ReportGenerator
```

## Interface Files

### CLI (`main.py`)
- Command-line interface
- Argument parsing
- Progress display
- Error handling

### Web App (`app.py`)
- Streamlit interface
- Interactive widgets
- Real-time generation
- Download functionality

## Benefits of This Architecture

1. **Separation of Concerns**: Each layer has a single responsibility
2. **Modularity**: Components can be used independently
3. **Reusability**: Visualization and processing modules are reusable
4. **Maintainability**: Easy to locate and update code
5. **Extensibility**: Simple to add new extractors or visualizations
6. **Testability**: Each module can be tested in isolation
7. **Professional**: Follows industry best practices

## Adding New Features

### Adding a New Data Source
1. Create new extractor in `ETL/extractors/`
2. Implement extraction logic
3. Add to `DataLoader` if needed

### Adding a New Visualization
1. Create new method in appropriate `Visual/` module
2. Or create new module for new category
3. Add to report layout in `ReportGenerator`

### Adding a New Metric
1. Add calculation to appropriate transformer
2. Update visualization to display it
3. Update report summary if needed

## File Responsibilities

| File | Responsibility | Dependencies |
|------|----------------|--------------|
| `ETL/extractors/whoscored_extractor.py` | Scrape WhoScored | Playwright |
| `ETL/extractors/fotmob_extractor.py` | Fetch from FotMob | Requests |
| `ETL/transformers/event_processor.py` | Process events | Pandas |
| `ETL/transformers/player_processor.py` | Player analytics | Pandas |
| `ETL/transformers/team_processor.py` | Team analytics | Pandas |
| `ETL/transformers/match_processor.py` | Coordinate all | All transformers |
| `ETL/loaders/data_loader.py` | Cache management | Extractors |
| `Visual/pitch_visualizations.py` | Pitch charts | mplsoccer |
| `Visual/statistical_visualizations.py` | Stats charts | matplotlib |
| `Visual/heatmap_visualizations.py` | Heatmaps | scipy |
| `Visual/advanced_visualizations.py` | Advanced charts | matplotlib |
| `Reporting/report_generator.py` | Generate reports | ETL + Visual |
| `main.py` | CLI interface | Reporting |
| `app.py` | Web interface | Reporting |

## Development Workflow

1. **Data Extraction**: Work in `ETL/extractors/`
2. **Data Processing**: Work in `ETL/transformers/`
3. **Visualization**: Work in `Visual/`
4. **Integration**: Work in `Reporting/`
5. **Interface**: Work in `main.py` or `app.py`

## Testing Strategy

Each layer can be tested independently:

```python
# Test extractor
extractor = WhoScoredExtractor()
data = extractor.extract_match_centre_detailed(1716104)
assert data['success'] == True

# Test transformer
processor = EventProcessor(events_data)
passes = processor.get_passes()
assert len(passes) > 0

# Test visualization
viz = PitchVisualizations()
fig, ax = plt.subplots()
viz.create_shot_map(ax, shots_home, shots_away, '#FF0000', '#0000FF')
assert ax.get_title() == 'Shot Map'
```

---

This structure ensures maintainability, scalability, and professional code organization.
