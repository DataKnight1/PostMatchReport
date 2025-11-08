# PostMatchReport Visualization Architecture

## Overview
The PostMatchReport application generates comprehensive football match reports using a modular visualization system. All visualizations can be displayed independently in an enhanced UI.

---

## 1. Visualization Components

### Module Structure
Located in `/home/user/PostMatchReport/Visual/`:
- `pitch_visualizations.py` - Pitch-based visualizations
- `statistical_visualizations.py` - Stats panels and comparisons
- `heatmap_visualizations.py` - Heatmaps and density maps
- `advanced_visualizations.py` - Momentum, xG timelines, zone maps
- `tactical_visualizations.py` - Tactical analysis (zonal control)

---

## 2. Individual Visualization Components

### A. PITCH_VISUALIZATIONS (PitchVisualizations class)

#### 1. **xG Shot Map** `create_xg_shot_map()`
- **Purpose**: Visualize all shots from both teams on the pitch
- **Features**:
  - Color-mapped by Expected Goals (xG)
  - Size scaled by xG value
  - Different markers: circle (header), square (set-piece), hexagon (other)
  - Distinguishes goals (★), on-target (●), off-target (×)
  - Away shots mirrored to top half
  - Inset colorbar showing xG gradient
- **Data Required**: shots_home, shots_away DataFrames with columns: x, y, xg, type_display, qualifiers_dict
- **Called In Report**: Row 1, Column 1 (ax2)

#### 2. **Pass Network** `create_pass_network()`
- **Purpose**: Visualize team passing patterns and player connections
- **Features**:
  - Line widths based on pass volume (up to 10px)
  - Marker sizes based on pass frequency (up to 3000px)
  - Transparency scaled to pass volume
  - Hexagon player markers with initials/shirt numbers
  - Volume-based scaling for both connections and players
- **Data Required**: avg_positions_df (player positions), pass_connections_df (connections)
- **Columns Needed**: 
  - Positions: x, y, name, shirt_no, count
  - Connections: x, y, x_end, y_end, pass_count
- **Called In Report**: Row 2, Columns 0 & 2 (ax4, ax6) - home and away

#### 3. **Simple Pass Network** `create_pass_network_simple()`
- Alternate version with basic styling (backward compatible)

#### 4. **Shot Map** `create_shot_map()`
- Simpler version without xG color mapping
- Used for visualization without xG data

---

### B. STATISTICAL_VISUALIZATIONS (StatisticalVisualizations class)

#### **Match Summary Panel** `create_match_summary_panel()`
- **Purpose**: Display overall match statistics and information
- **Features**:
  - Team names, final score, venue, date
  - Team badges/logos (with fallback circles)
  - Possession bar chart
  - xG bar chart
  - Detailed stats table with columns:
    - Possession, xG, Shots, Shots on Target
    - Passes Completed, Pass Accuracy, Key Passes, Assists
    - Tackles, Interceptions, Clearances, Blocks
  - Zebra-striped row backgrounds for readability
  - Team color highlights
- **Data Required**: match_summary dict from MatchProcessor with:
  - teams.home/away.name, id
  - match_info (score, venue, date, competition)
  - team_colors (home_color, away_color)
  - team_logos (home, away paths)
  - possession (home, away percentages)
  - xg (home_xg, away_xg)
  - shots_data (home_shots, away_shots)
  - team_stats with passing, shooting, defensive stats
- **Called In Report**: Row 1, Column 0 (ax1)

#### **Stats Comparison Bars** `create_stats_comparison_bars()`
- Simple horizontal bar comparison between teams
- Rarely used in current layout

---

### C. HEATMAP_VISUALIZATIONS (HeatmapVisualizations class)

#### 1. **Defensive Actions Heatmap** `create_defensive_actions_heatmap()`
- **Purpose**: Show where team makes defensive actions (tackles, blocks, etc.)
- **Features**:
  - 2D histogram binning (21×14 grid = 105×68m pitch)
  - Gaussian filter smoothing (sigma=1.0)
  - Team-color tinted colormap (transparent to opaque)
  - Optional colorbar with density scale
  - 20% alpha base for visibility
- **Data Required**: actions_df with columns: x, y (coordinates of defensive actions)
- **Called In Report**: Row 4, Columns 0 & 2 (ax10, ax12) - home and away

#### 2. **Touch Heatmap** `create_touch_heatmap()`
- **Purpose**: Show areas where team has most touches/ball contact
- **Features**:
  - Same grid binning (21×14)
  - YlOrRd (Yellow-Orange-Red) colormap
  - Gaussian filter (sigma=1.5)
  - 80% alpha for visibility
  - Optional colorbar
- **Data Required**: events_df with columns: x, y (all team events/touches)
- **Fallback**: Used in Row 4, Column 1 when zone matrix unavailable (ax11)

#### 3. **Pitch Control Map** `create_pitch_control_map()`
- **Purpose**: Show territorial dominance (possession by region)
- **Features**:
  - Coarse grid (7×6 zones = 15×11m zones)
  - Home control colored with home_color (0.2-0.6 alpha)
  - Away control colored with away_color (0.2-0.6 alpha)
  - Contested zones in gray (0.1 alpha)
  - Legend distinguishing home, away, contested
  - Dynamic alpha based on dominance (60%+ vs 40%-)
- **Data Required**: home_events, away_events with columns: x, y (all events)
- **Called In Report**: Row 3, Column 1 (ax8)

---

### D. ADVANCED_VISUALIZATIONS (AdvancedVisualizations class)

#### 1. **Match Momentum Graph** `create_momentum_graph()`
- **Purpose**: Show match momentum swing over time
- **Features**:
  - Net momentum around zero line
  - Weighted attacking actions (shots=5, final third=1, box=1, key passes=2)
  - xG weighted: 5 + (5 × xG value)
  - Gaussian smoothing (sigma=1.0) to reduce noise
  - Fill between home/away areas
  - Goal markers (★) with minute labels
  - Half-time line at 45 minutes
  - 90-minute timeline with legend
- **Data Required**: events_df with columns:
  - teamId, cumulative_mins, type_display, x, y
  - is_key_pass, xg
- **Called In Report**: Row 1, Column 2 (ax3)

#### 2. **Cumulative xG** `create_cumulative_xg()`
- **Purpose**: Show cumulative expected goals progression over match
- **Features**:
  - Step chart (cumulative values)
  - Filled areas under each team's line
  - Heuristic xG estimator (when per-shot data missing):
    - Penalty: 0.76 xG
    - In box: +0.10 base
    - Final third: +0.05 base
    - Distance adjustments: -8m: +0.20, -12m: +0.12, -18m: +0.07, -25m: +0.03
    - Angle bonus: >0.35rad: +0.05, >0.25rad: +0.03
    - Head shot: ×0.7 multiplier
    - Outcome adjustments: saved/post: +0.03, miss: -0.01
  - Goal markers (★) on step line
  - 90-minute timeline
  - Legend with team names
- **Data Required**: shots_df with columns:
  - teamId, cumulative_mins, xg, type_display, x, y
  - qualifiers_dict, dist_to_goal, angle, outcome_display
- **Called In Report**: Row 2, Column 1 (ax5)

#### 3. **Zone 14 & Half-Spaces Map** `create_zone14_map()`
- **Purpose**: Show passes in critical attacking areas
- **Features**:
  - Zone 14 (central penalty area extension): 70-87.5m × 20.4-47.6m (orange highlight)
  - Left half-space: 70-87.5m × 10.2-27.2m (team color)
  - Right half-space: 70-87.5m × 40.8-57.8m (team color)
  - Plots passes in these zones with movement lines
  - Scatter points showing pass start positions
  - Color-coded by team
- **Data Required**: passes_df with columns:
  - x, y (pass start), endX, endY (pass end)
- **Called In Report**: Row 3, Columns 0 & 2 (ax7, ax9) - home and away

#### 4. **xG Timeline** `create_xg_timeline()`
- **Purpose**: Timeline showing when shots occurred
- **Features**:
  - Two-row timeline (home top, away bottom)
  - Markers for goals (★), on-target (●), off-target (×)
  - Sized by xG value
  - Half-time line at 45 minutes
  - Legend with outcome types
- **Data Required**: shots_df with columns:
  - teamId, cumulative_mins, type_display, xg
- **Not Currently Used**: Available for alternative layouts

---

### E. TACTICAL_VISUALIZATIONS (TacticalVisualizer class)

#### **Zonal Control Map** `create_zonal_control_map()`
- **Purpose**: Show territorial control by regions
- **Features**:
  - Configurable grid (default: 6×4 zones)
  - Zone ownership (Home: 'H', Away: 'A', Contested: 'C')
  - Color-coded zones (home/away colors at 0.3 alpha, contested gray at 0.2)
  - Pitch markings overlay (lines, circles, arcs, boxes, goals)
  - Team names with attack direction arrows
  - Legend showing zone types
  - Footer with grid dimensions
  - Minimalist design (light background)
- **Data Required**: zone_matrix (2D numpy array of 'H', 'A', 'C' strings)
- **Called In Report**: Row 4, Column 1 (ax11) - primary visualization

---

## 3. Current Report Layout (4 Rows × 3 Columns)

```
┌──────────────────────────────────────────────────┐
│ ROW 1: Match Overview                            │
├──────────────────┬──────────────────┬────────────┤
│ Match Summary    │ xG Shot Map      │ Momentum   │
│ (Stats Panel)    │                  │ Graph      │
├──────────────────┼──────────────────┼────────────┤
│ ROW 2: Attacking Patterns                       │
├──────────────────┬──────────────────┬────────────┤
│ Home Pass        │ Cumulative xG    │ Away Pass  │
│ Network          │ Chart            │ Network    │
├──────────────────┼──────────────────┼────────────┤
│ ROW 3: Territory Control                        │
├──────────────────┬──────────────────┬────────────┤
│ Home Zone 14     │ Pitch Control    │ Away Zone  │
│ & Half-Spaces    │ Map              │ 14 & HS    │
├──────────────────┼──────────────────┼────────────┤
│ ROW 4: Defensive Analysis                       │
├──────────────────┬──────────────────┬────────────┤
│ Home Defensive   │ Zonal Control    │ Away Def.  │
│ Actions Heatmap  │ Map              │ Actions HM │
└──────────────────┴──────────────────┴────────────┘
```

---

## 4. Data Flow Architecture

```
ETL Pipeline
    ↓
Match Processor (MatchProcessor)
    ├─→ get_complete_match_summary()      [for Stats Panel]
    ├─→ get_shots()                       [for Shot Map, Cumulative xG]
    ├─→ get_passes()                      [for Zone 14 Maps]
    ├─→ get_events_dataframe()            [for Momentum, Pitch Control]
    ├─→ get_defensive_actions()           [for Defensive Heatmaps]
    ├─→ get_pass_network_data()           [for Pass Networks]
    └─→ calculate_zonal_control()         [for Zonal Control Map]
    ↓
Report Generator (ReportGenerator)
    ├─→ PitchVisualizations
    ├─→ StatisticalVisualizations
    ├─→ HeatmapVisualizations
    ├─→ AdvancedVisualizations
    └─→ TacticalVisualizer
    ↓
Matplotlib Figure (12 subplots)
```

---

## 5. How to Display Visualizations Separately

Each visualization component can be instantiated and called independently:

```python
# Example: Show only Pass Network
from Visual.pitch_visualizations import PitchVisualizations
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, 1, figsize=(10, 8))
pitch_viz = PitchVisualizations(pitch_color='#2b313a', line_color='#d0d7de')

# Get data from MatchProcessor
home_positions, home_connections = processor.get_pass_network_data(home_id)

# Draw visualization
pitch_viz.create_pass_network(ax, home_positions, home_connections, '#FF0000', 'Home Team')
plt.show()
```

All 12 visualizations can be accessed similarly with their respective classes and methods.

---

## 6. Visualization Methods by Class

### PitchVisualizations
- `create_shot_map()`
- `create_xg_shot_map()` ← Preferred shot visualization
- `create_pass_network()` ← Preferred pass network
- `create_pass_network_simple()`

### StatisticalVisualizations
- `create_match_summary_panel()`
- `create_stats_comparison_bars()`

### HeatmapVisualizations
- `create_defensive_actions_heatmap()`
- `create_touch_heatmap()`
- `create_pitch_control_map()`

### AdvancedVisualizations
- `create_momentum_graph()`
- `create_xg_timeline()`
- `create_zone14_map()`
- `create_cumulative_xg()`

### TacticalVisualizations
- `create_zonal_control_map()`

---

## 7. Key Data Structures

### Pitch Dimensions (Standard)
- Length: 105m
- Width: 68m

### Coordinate System
- Origin (0,0) at bottom-left
- x-axis: along length (0-105)
- y-axis: along width (0-68)

### Important Zone Definitions
- **Penalty Box**: x ≥ 88.5m, 13.8 ≤ y ≤ 54.2m
- **Final Third**: x ≥ 70m
- **Zone 14**: x: 70-87.5m, y: 20.4-47.6m
- **Left Half-Space**: x: 70-87.5m, y: 10.2-27.2m
- **Right Half-Space**: x: 70-87.5m, y: 40.8-57.8m

---

## 8. Color Scheme

### Theme Support
- **Dark Mode**: 
  - Background: #22272e
  - Text: #e6edf3
  - Pitch: #2b313a
  - Lines: #d0d7de
  
- **Light Mode**:
  - Background: #f0f0f0
  - Text: black
  - Pitch: #d6c39f
  - Lines: #0e1117

### Dynamic Colors
- Home team color: Provided by FotMob data
- Away team color: Provided by FotMob data
- Defaults: #FF0000 (home), #0000FF (away)

---

## Summary: Individual Visualization Display Strategy

For an enhanced UI with separate visualization panels, you can:

1. **Create separate Streamlit/UI pages** for each visualization category
2. **Use tabs** to organize visualizations by type
3. **Create a dashboard** with selectable visualizations
4. **Build a custom gallery** letting users pick individual components
5. **Enable/disable visualizations** dynamically based on available data

Each visualization component is fully independent and can be rendered to its own `matplotlib.Axes` object, making them easy to integrate into any UI framework.
