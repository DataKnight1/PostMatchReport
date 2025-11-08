# WhoScored ETL Pipeline - Complete Guide

## Overview

This comprehensive ETL (Extract, Transform, Load) pipeline automatically extracts match data from WhoScored, transforms it into structured tables and aggregated statistics, and loads it into databases or exports to various file formats.

### Features

- **Extraction**: Automated data retrieval from WhoScored using Playwright
- **Transformation**:
  - Event-level processing with spatial metrics
  - Comprehensive statistics aggregation matching WhoScored interface
  - Player and team analytics
- **Loading**:
  - Database support (SQLite, PostgreSQL, MySQL)
  - File exports (CSV, JSON, Excel, Parquet)
  - Intelligent caching

## Quick Start

### Basic Usage

```bash
# Extract and export match data to all formats
python whoscored_etl.py 1946652

# Export to specific database
python whoscored_etl.py 1946652 --database sqlite:///matches.db

# Export only CSV and JSON
python whoscored_etl.py 1946652 --export csv,json
```

### Python API

```python
from whoscored_etl import WhoScoredETL

# Initialize ETL
etl = WhoScoredETL(
    cache_dir="./cache",
    output_dir="./exports",
    database_url="sqlite:///matches.db"
)

# Run pipeline
results = etl.run(
    match_id=1946652,
    use_cache=True,
    export_formats=['database', 'csv', 'json', 'excel']
)

print(f"Success: {results['success']}")
print(f"Exports: {results['exports']}")
```

## Architecture

### ETL Components

```
┌─────────────────────────────────────────────────────────────┐
│                     EXTRACT LAYER                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ WhoScoredExtractor (Playwright-based)                │   │
│  │ - Fetches HTML from WhoScored                        │   │
│  │ - Extracts matchCentreData from JavaScript           │   │
│  │ - Parses events, players, teams                      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                   TRANSFORM LAYER                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ EventProcessor                                       │   │
│  │ - Processes raw events into DataFrame                │   │
│  │ - Calculates spatial metrics (distance, angle, etc.) │   │
│  │ - Identifies pass receivers                          │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ PlayerProcessor                                      │   │
│  │ - Calculates player positions and statistics        │   │
│  │ - Generates pass network data                        │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ TeamProcessor                                        │   │
│  │ - Aggregates team-level statistics                  │   │
│  │ - Calculates possession, territorial stats          │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ StatsAggregator                                      │   │
│  │ - Aggregates comprehensive match statistics         │   │
│  │ - Matches WhoScored interface format                │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                      LOAD LAYER                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ DatabaseLoader (SQLAlchemy)                          │   │
│  │ - Loads to relational databases                      │   │
│  │ - Tables: matches, teams, players, events, stats    │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ FileExporter                                         │   │
│  │ - CSV: events, players, statistics                   │   │
│  │ - JSON: complete match data                          │   │
│  │ - Excel: multi-sheet workbook                        │   │
│  │ - Parquet: columnar format for analytics             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Data Schema

### Database Tables

#### 1. Matches Table
```sql
CREATE TABLE matches (
    match_id INTEGER PRIMARY KEY,
    whoscored_id INTEGER UNIQUE NOT NULL,
    competition VARCHAR(200),
    season VARCHAR(50),
    date DATETIME,
    venue VARCHAR(200),
    home_team_id INTEGER,
    away_team_id INTEGER,
    home_team_name VARCHAR(200),
    away_team_name VARCHAR(200),
    home_score INTEGER,
    away_score INTEGER,
    home_formation VARCHAR(20),
    away_formation VARCHAR(20),
    extracted_at DATETIME
);
```

#### 2. Events Table
```sql
CREATE TABLE events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    player_id INTEGER,
    period INTEGER,
    minute INTEGER,
    second FLOAT,
    type VARCHAR(50),
    outcome VARCHAR(50),
    is_successful BOOLEAN,
    x FLOAT,
    y FLOAT,
    end_x FLOAT,
    end_y FLOAT,
    distance FLOAT,
    is_progressive BOOLEAN,
    is_key_pass BOOLEAN,
    is_assist BOOLEAN,
    is_goal BOOLEAN,
    xg FLOAT,
    qualifiers TEXT
);
```

#### 3. Match Statistics Table
```sql
CREATE TABLE match_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    stat_type VARCHAR(50),  -- 'passing', 'shooting', 'defensive', etc.
    stat_name VARCHAR(100),
    stat_value FLOAT
);
```

### Aggregated Statistics

The `StatsAggregator` produces statistics matching the WhoScored match summary interface:

#### Offensive Metrics
- `shots` - Total shots
- `shots_on_target` - Shots on target
- `shots_off_target` - Shots off target
- `goals` - Goals scored
- `xg` - Expected goals
- `passes` - Total passes
- `pass_accuracy` - Pass accuracy percentage
- `dribbles` - Dribble attempts
- `dribbles_successful` - Successful dribbles

#### Defensive Metrics
- `tackles` - Tackle attempts
- `interceptions` - Interceptions
- `clearances` - Clearances
- `blocks` - Blocked shots/passes

#### Possession Metrics
- `touches` - Total touches
- `dispossessed` - Times dispossessed
- `bad_touches` - Bad touches

#### Discipline
- `fouls` - Fouls committed
- `yellow_cards` - Yellow cards
- `red_cards` - Red cards
- `offsides` - Offsides

#### Shot Breakdown by Zone
- `penalty_area_shots` - Shots from penalty area
- `six_yard_box_shots` - Shots from six yard box
- `outside_box_shots` - Shots from outside box

#### Shot Breakdown by Body Part
- `right_foot_shots` - Right foot shots
- `left_foot_shots` - Left foot shots
- `headed_shots` - Headed shots

#### Shot Breakdown by Situation
- `open_play_shots` - Shots from open play
- `set_piece_shots` - Shots from set pieces
- `counter_attack_shots` - Shots from counter attacks

## Installation

### Requirements

```bash
# Core dependencies
pip install playwright pandas numpy beautifulsoup4 requests lxml

# Install Playwright browsers
python -m playwright install firefox

# Database support (optional)
pip install sqlalchemy psycopg2-binary  # For PostgreSQL
# or use SQLite (included with Python)

# Export formats (optional)
pip install pyarrow  # For Parquet
pip install openpyxl  # For Excel
```

### Full Installation

```bash
pip install -r requirements.txt
python -m playwright install firefox
```

## Usage Examples

### 1. Simple Extraction and Display

```python
from ETL.extractors.whoscored_extractor import WhoScoredExtractor
from ETL.transformers.match_processor import MatchProcessor
from ETL.transformers.stats_aggregator import StatsAggregator

# Extract
extractor = WhoScoredExtractor(headless=True)
data = extractor.extract_all_sections(1946652)

# Transform
processor = MatchProcessor(data)
events_df = processor.get_events_dataframe()

# Aggregate statistics
home_id = data['match_centre']['home_team']['team_id']
away_id = data['match_centre']['away_team']['team_id']
aggregator = StatsAggregator(events_df, home_id, away_id)
stats = aggregator.aggregate_all_stats()

# Display
print(f"Shots: {stats['home']['shots']} - {stats['away']['shots']}")
print(f"xG: {stats['home']['xg']:.2f} - {stats['away']['xg']:.2f}")
```

### 2. Export to Database

```python
from ETL.loaders.data_loader import DataLoader
from ETL.transformers.match_processor import MatchProcessor
from ETL.loaders.database_loader import DatabaseLoader

# Load data
loader = DataLoader()
data = loader.load_whoscored_data(1946652)

# Process
processor = MatchProcessor(data)

# Load to database
db = DatabaseLoader("postgresql://user:pass@localhost/matches")
db.load_complete_match(data, processor)
```

### 3. Export to CSV

```python
from ETL.loaders.file_exporter import FileExporter

exporter = FileExporter(output_dir="./exports")

# Export events
exporter.export_events_csv(events_df, match_id)

# Export statistics
exporter.export_statistics_csv(stats, match_id)

# Export to Excel (multiple sheets)
exporter.export_to_excel(data, processor, stats, match_id)
```

### 4. Complete ETL Pipeline

```python
from whoscored_etl import WhoScoredETL

etl = WhoScoredETL(
    cache_dir="./cache",
    output_dir="./exports",
    database_url="sqlite:///matches.db",
    verbose=True
)

results = etl.run(
    match_id=1946652,
    use_cache=True,
    export_formats=['database', 'csv', 'json', 'excel', 'parquet']
)

if results['success']:
    print(f"ETL completed successfully!")
    print(f"Exports: {results['exports']}")
else:
    print(f"ETL failed: {results['error']}")
```

## Command-Line Interface

### Basic Commands

```bash
# Extract and export to all formats
python whoscored_etl.py 1946652

# Export to SQLite database
python whoscored_etl.py 1946652 --database sqlite:///matches.db

# Export to PostgreSQL
python whoscored_etl.py 1946652 --database postgresql://user:pass@localhost/dbname

# Export specific formats
python whoscored_etl.py 1946652 --export csv,json

# Skip cache
python whoscored_etl.py 1946652 --no-cache

# Verbose logging
python whoscored_etl.py 1946652 --verbose

# Custom output directory
python whoscored_etl.py 1946652 --output-dir ./my_exports

# Display summary without exporting
python whoscored_etl.py 1946652 --summary-only
```

### Help

```bash
python whoscored_etl.py --help
```

## Best Practices

### 1. Respect WhoScored's Terms of Service
- Use rate limiting between requests (10 seconds recommended)
- Cache data to minimize requests
- Avoid large-scale scraping
- Consider using official data providers (Opta, StatsBomb) for commercial use

### 2. Data Quality
- Always validate extracted data
- Check that aggregated statistics match WhoScored's interface
- Handle missing or null data gracefully

### 3. Performance
- Use caching to avoid re-downloading data
- Use Parquet format for large datasets
- Use database indexes for frequent queries

### 4. Error Handling
- Implement retry logic for network failures
- Log all errors for debugging
- Use try-except blocks around extraction

## Troubleshooting

### Issue: "Page failed to load"
**Solution**: WhoScored may be blocking automated requests. Try:
- Using a different browser (chromium instead of firefox)
- Adding delays between requests
- Using rotating proxies
- Running with headless=False to see what's happening

### Issue: "No JSON data found"
**Solution**: The page structure may have changed. Check:
- The HTML source for `matchCentreData`
- The regex pattern in `whoscored_extractor.py`
- Whether JavaScript loaded correctly

### Issue: "Database connection failed"
**Solution**:
- Check database URL format
- Verify database server is running
- Install correct database driver (psycopg2 for PostgreSQL)

### Issue: "Module not found: sqlalchemy"
**Solution**:
```bash
pip install sqlalchemy psycopg2-binary
```

### Issue: "Module not found: pyarrow"
**Solution**:
```bash
pip install pyarrow
```

## Advanced Usage

### Custom Statistics

Extend `StatsAggregator` to add custom metrics:

```python
from ETL.transformers.stats_aggregator import StatsAggregator

class CustomStatsAggregator(StatsAggregator):
    def _count_long_balls(self, events):
        """Count passes over 40 meters."""
        passes = events[events['type_display'] == 'Pass']
        return len(passes[passes['distance'] > 40])

    def aggregate_team_stats(self, team_id):
        stats = super().aggregate_team_stats(team_id)
        team_events = self.events_df[self.events_df['teamId'] == team_id]
        stats['long_balls'] = self._count_long_balls(team_events)
        return stats
```

### Custom Database Schema

Extend `DatabaseLoader` for custom tables:

```python
from ETL.loaders.database_loader import DatabaseLoader
from sqlalchemy import Table, Column, Integer, String

class CustomDatabaseLoader(DatabaseLoader):
    def _define_tables(self):
        super()._define_tables()

        # Add custom table
        self.custom_table = Table(
            'custom_stats', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('match_id', Integer),
            Column('custom_metric', String(100)),
        )
```

### Batch Processing

Process multiple matches:

```python
from whoscored_etl import WhoScoredETL
import time

etl = WhoScoredETL(database_url="sqlite:///matches.db")

match_ids = [1946652, 1716104, 1234567]

for match_id in match_ids:
    result = etl.run(match_id, export_formats=['database'])
    if result['success']:
        print(f"✓ Match {match_id} processed")
    else:
        print(f"✗ Match {match_id} failed: {result['error']}")

    time.sleep(10)  # Rate limiting
```

## API Reference

### WhoScoredETL

Main ETL orchestrator class.

**Constructor**:
```python
WhoScoredETL(cache_dir="./cache", output_dir="./exports",
             database_url=None, verbose=False)
```

**Methods**:
- `run(match_id, use_cache=True, export_formats=None)` - Run complete ETL pipeline

### StatsAggregator

Aggregates event data into match statistics.

**Constructor**:
```python
StatsAggregator(events_df, home_id, away_id)
```

**Methods**:
- `aggregate_all_stats()` - Get all statistics for both teams
- `aggregate_team_stats(team_id)` - Get statistics for one team
- `export_to_dataframe()` - Export as comparison DataFrame
- `export_whoscored_format()` - Export in WhoScored interface format

### DatabaseLoader

Loads data into relational databases.

**Constructor**:
```python
DatabaseLoader(database_url="sqlite:///matches.db")
```

**Methods**:
- `load_complete_match(whoscored_data, match_processor)` - Load all match data
- `load_events(match_id, events_df)` - Load events table
- `load_match_statistics(match_id, team_stats)` - Load statistics table
- `query_match_stats(match_id)` - Query match information
- `query_events(match_id)` - Query match events

### FileExporter

Exports data to various file formats.

**Constructor**:
```python
FileExporter(output_dir="./exports")
```

**Methods**:
- `export_events_csv(events_df, match_id)` - Export events to CSV
- `export_events_parquet(events_df, match_id)` - Export events to Parquet
- `export_statistics_csv(stats, match_id)` - Export statistics to CSV
- `export_complete_match_json(...)` - Export complete data to JSON
- `export_to_excel(...)` - Export to Excel workbook
- `export_all_formats(...)` - Export to all available formats

## Contributing

To extend or modify the ETL pipeline:

1. **Add new extractors**: Create new extractor classes in `ETL/extractors/`
2. **Add new transformers**: Create processor classes in `ETL/transformers/`
3. **Add new loaders**: Create loader classes in `ETL/loaders/`
4. **Update documentation**: Update this guide and inline docstrings

## License

This ETL pipeline is part of the PostMatchReport project.

## Support

For issues, questions, or contributions, please refer to the main project repository.

---

**Built with**: Python, Playwright, Pandas, SQLAlchemy, mplsoccer
