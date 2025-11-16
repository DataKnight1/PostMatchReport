# WhoScored ETL Pipeline

A comprehensive ETL (Extract, Transform, Load) system for WhoScored match data.

## Overview

This ETL pipeline automatically extracts match data from WhoScored, processes event-level information, calculates comprehensive statistics, and exports to various formats (database, CSV, JSON, Excel, Parquet).

## Features

### Extract
- **WhoScored Extractor**: Playwright-based scraper that extracts `matchCentreData` from WhoScored pages
- **Intelligent Caching**: Avoids redundant requests
- **FotMob Support**: Optional additional data source

### Transform
- **Event Processor**: Converts raw events into structured DataFrame with spatial metrics
- **Player Processor**: Calculates player positions, ratings, and pass networks
- **Team Processor**: Aggregates team-level statistics (passing, shooting, defensive)
- **Stats Aggregator**: Comprehensive statistics matching WhoScored interface

### Load
- **Database Loader**: SQLAlchemy-based loader supporting SQLite, PostgreSQL, MySQL
- **File Exporter**: Export to CSV, JSON, Excel, Parquet
- **Data Loader**: Caching and retrieval manager

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install chromium
```

### Basic Usage

```bash
# Extract and export to all formats
python whoscored_etl.py 1946652

# Export to database
python whoscored_etl.py 1946652 --database sqlite:///matches.db

# Export specific formats
python whoscored_etl.py 1946652 --export csv,json
```

### Python API

```python
from whoscored_etl import WhoScoredETL

etl = WhoScoredETL(
    cache_dir="./cache",
    output_dir="./exports",
    database_url="sqlite:///matches.db"
)

results = etl.run(match_id=1946652, use_cache=True)
print(results['stats'])
```

## Architecture

```
ETL/
├── extractors/
│   ├── whoscored_extractor.py  # Playwright-based scraper
│   └── fotmob_extractor.py     # FotMob API client
│
├── transformers/
│   ├── event_processor.py      # Event-level processing
│   ├── player_processor.py     # Player analytics
│   ├── team_processor.py       # Team aggregation
│   ├── match_processor.py      # Main coordinator
│   └── stats_aggregator.py     # Statistics aggregation
│
└── loaders/
    ├── data_loader.py          # Cache manager
    ├── database_loader.py      # SQL database loader
    └── file_exporter.py        # File format exports
```

## Data Schema

### Events Table
- Event-level data with spatial coordinates
- Type, outcome, timestamps, qualifiers
- Flags: is_successful, is_progressive, is_key_pass, is_goal
- Spatial metrics: distance, angle, distance_to_goal

### Match Statistics
Over 40 aggregated statistics including:
- **Offensive**: shots, passes, dribbles, xG
- **Defensive**: tackles, interceptions, clearances, blocks
- **Possession**: touches, dispossessed
- **Discipline**: fouls, cards, offsides
- **Shot Breakdown**: by zone, body part, situation

### Database Tables
- `matches` - Match metadata
- `teams` - Team information
- `players` - Player details
- `match_players` - Player participation
- `events` - All match events
- `match_stats` - Aggregated statistics

## Examples

See the `examples/` directory:
- `simple_etl_example.py` - Basic extraction and statistics
- `database_etl_example.py` - Loading to database
- `batch_etl_example.py` - Processing multiple matches

## Documentation

Full documentation: [WHOSCORED_ETL_GUIDE.md](../docs/WHOSCORED_ETL_GUIDE.md)

## Statistics Coverage

The pipeline extracts and calculates statistics matching the WhoScored match summary interface:

| Category | Statistics |
|----------|-----------|
| **Shots** | Shots, on target, off target, blocked, goals, xG |
| **Passing** | Total passes, accuracy, progressive, key passes, assists |
| **Possession** | Touches, dispossessed, bad touches |
| **Defensive** | Tackles, interceptions, clearances, blocks |
| **Dribbles** | Attempts, successful |
| **Discipline** | Fouls, yellow/red cards, offsides |
| **Aerials** | Duels, won |
| **Goalkeeping** | Saves |
| **Shot Zones** | Penalty area, six yard box, outside box |
| **Shot Type** | Right foot, left foot, headed |
| **Shot Situation** | Open play, set piece, counter attack |

## Development

### Adding New Statistics

Extend `StatsAggregator`:

```python
class CustomAggregator(StatsAggregator):
    def _count_progressive_passes(self, events):
        passes = events[events['type_display'] == 'Pass']
        return len(passes[passes['is_progressive'] == True])
```

### Adding New Export Formats

Extend `FileExporter`:

```python
class CustomExporter(FileExporter):
    def export_to_custom_format(self, data, match_id):
        # Your export logic
        pass
```

## License

Part of the PostMatchReport project.

## Support

For detailed documentation, see [WHOSCORED_ETL_GUIDE.md](../docs/WHOSCORED_ETL_GUIDE.md)
