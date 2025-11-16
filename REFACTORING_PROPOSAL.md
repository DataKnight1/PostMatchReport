# PostMatchReport - Refactoring & Design Proposal

## Executive Summary

This document outlines a comprehensive refactoring plan to eliminate code repetition, improve maintainability, and implement a clean black & white minimalist design.

---

## 1. CODE REFACTORING RECOMMENDATIONS

### 1.1 Create Centralized Theme Manager

**Problem**: Theme/color management is fragmented across 3+ locations with hardcoded values.

**Solution**: Create `Visual/theme_manager.py`

```python
class ThemeManager:
    """Centralized theme and styling management."""

    THEMES = {
        'dark': {
            'background': '#0a0a0a',      # Pure black
            'surface': '#1a1a1a',         # Card/panel background
            'border': '#333333',          # Subtle borders
            'text_primary': '#ffffff',    # White text
            'text_secondary': '#b3b3b3',  # Gray text
            'pitch': '#1a1a1a',          # Dark pitch
            'pitch_lines': '#404040',    # Pitch lines
        },
        'light': {
            'background': '#ffffff',      # Pure white
            'surface': '#f5f5f5',        # Card/panel background
            'border': '#e0e0e0',         # Subtle borders
            'text_primary': '#000000',   # Black text
            'text_secondary': '#666666', # Gray text
            'pitch': '#f5f5f5',         # Light pitch
            'pitch_lines': '#333333',   # Pitch lines
        }
    }

    def __init__(self, theme='dark'):
        self.theme = theme
        self.colors = self.THEMES[theme]

    def get_color(self, key):
        return self.colors.get(key)

    def apply_to_axis(self, ax):
        """Apply theme to matplotlib axis."""
        ax.set_facecolor(self.colors['surface'])
        for spine in ax.spines.values():
            spine.set_color(self.colors['border'])
        ax.tick_params(colors=self.colors['text_primary'])
        # ... (standardized styling)
```

**Impact**:
- Eliminates ~50+ hardcoded color values
- Single source of truth for theming
- Easy to add new themes

---

### 1.2 Create Pitch Factory/Base Class

**Problem**: Pitch initialization repeated 8+ times with identical code.

**Solution**: Create `Visual/pitch_factory.py`

```python
from mplsoccer import Pitch

class PitchFactory:
    """Factory for creating standardized pitch objects."""

    def __init__(self, theme_manager):
        self.theme = theme_manager

    def create_pitch(self, pitch_type='custom'):
        """Create a standard pitch with theme colors."""
        return Pitch(
            pitch_type=pitch_type,
            pitch_length=105,
            pitch_width=68,
            pitch_color=self.theme.get_color('pitch'),
            line_color=self.theme.get_color('pitch_lines'),
            linewidth=1.5
        )
```

**Usage**:
```python
# Before (repeated 8+ times):
pitch = Pitch(pitch_type='custom', pitch_length=105, pitch_width=68,
             pitch_color=self.pitch_color, line_color=self.line_color, linewidth=1.5)

# After (single line):
pitch = self.pitch_factory.create_pitch()
```

**Impact**:
- Eliminates 8+ duplicate initializations
- Centralizes pitch configuration
- Easier to modify pitch settings globally

---

### 1.3 Create Colorbar Utility Module

**Problem**: Colorbar creation code duplicated 3 times with nearly identical implementations.

**Solution**: Create `Visual/utils/colorbar_utils.py`

```python
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

def add_colorbar(ax, mappable, location='lower center', width='40%', height='4%',
                 label='', theme_manager=None):
    """Add standardized colorbar to axis.

    Args:
        ax: Matplotlib axis
        mappable: The mappable object (e.g., hexbin, scatter)
        location: Position of colorbar
        width/height: Colorbar dimensions
        label: Colorbar label
        theme_manager: ThemeManager instance for styling

    Returns:
        Colorbar object
    """
    cax = inset_axes(ax, width=width, height=height, loc=location,
                     bbox_to_anchor=(0, 0.05, 1, 1), bbox_transform=ax.transAxes)
    cb = ax.figure.colorbar(mappable, cax=cax, orientation='horizontal')

    if theme_manager:
        cb.outline.set_edgecolor(theme_manager.get_color('border'))
        cb.ax.tick_params(colors=theme_manager.get_color('text_primary'), labelsize=8)
        if label:
            cb.set_label(label, color=theme_manager.get_color('text_primary'), size=9)

    return cb
```

**Impact**:
- Eliminates 3 duplicate implementations
- Consistent colorbar styling
- ~60 lines of code reduction

---

### 1.4 Create Shot Outcome Utility

**Problem**: Shot outcome detection logic duplicated in 2+ files.

**Solution**: Create `Visual/utils/shot_utils.py`

```python
def get_shot_marker(row):
    """Get marker style for shot based on outcome."""
    if row.get('is_goal', False):
        return 'football'  # or custom marker
    elif row.get('is_on_target', False):
        return 'o'  # circle
    else:
        return 'x'  # cross

def get_shot_color(row, team_color):
    """Get color for shot based on outcome."""
    if row.get('is_goal', False):
        return '#00ff00'  # Green for goals
    else:
        return team_color

def filter_90min(df, time_column='cumulative_mins'):
    """Filter dataframe to 90 minutes only."""
    return df[df[time_column] <= 90]
```

**Impact**:
- Eliminates duplicate logic
- Consistent shot visualization
- Easier to add new shot types

---

### 1.5 Consolidate Logo Resolution

**Problem**: Two overlapping methods for logo handling.

**Solution**: Simplify to single method in `ReportGenerator`

```python
def _resolve_team_logo(self, team_id, team_name, provided_url=None, override_path=None):
    """
    Single method to resolve team logo with priority:
    1. Override path (parameter)
    2. Provided URL (from data source)
    3. Local lookup by ID
    4. Local lookup by name
    """
    # Check override first
    if override_path:
        return self._process_logo_path(override_path, 'override', team_id)

    # Check provided URL
    if provided_url:
        return self._process_logo_path(provided_url, 'data', team_id)

    # Local lookup
    return self._find_local_logo(team_id, team_name)
```

**Impact**:
- Reduces from 77 lines to ~40 lines
- Clear priority order
- Single code path

---

### 1.6 Remove Duplicate Pass Network

**Problem**: Two versions of pass network (`create_pass_network` and `create_pass_network_simple`).

**Solution**: Keep enhanced version only, add `simple_mode` parameter if needed.

```python
def create_pass_network(self, ax, positions, connections, team_color, team_name,
                       simple_mode=False):
    """Create pass network with optional simple mode."""
    # ... existing enhanced implementation
    if not simple_mode:
        # Volume-based styling
        # Current enhanced features
    else:
        # Simplified version
```

**Impact**:
- Eliminates 45+ duplicate lines
- Single method to maintain
- Optional complexity

---

### 1.7 Create Base Visualization Class

**Problem**: Dark theme application repeated for 12 subplots.

**Solution**: Create `Visual/base_visualization.py`

```python
class BaseVisualization:
    """Base class for all visualizations."""

    def __init__(self, theme_manager, pitch_factory):
        self.theme = theme_manager
        self.pitch_factory = pitch_factory

    def prepare_axis(self, ax, title=''):
        """Standard axis preparation with theme."""
        ax.set_facecolor(self.theme.get_color('surface'))
        self.theme.apply_to_axis(ax)
        if title:
            ax.set_title(title, color=self.theme.get_color('text_primary'),
                        fontsize=12, fontweight='bold', pad=10)

    def create_pitch(self):
        """Create themed pitch."""
        return self.pitch_factory.create_pitch()
```

**All visualization classes inherit**:
```python
class PitchVisualizations(BaseVisualization):
    def create_xg_shot_map(self, ax, ...):
        self.prepare_axis(ax, "Shot Map (xG)")
        pitch = self.create_pitch()
        # ... visualization logic
```

**Impact**:
- Eliminates 12 manual `_apply_dark()` calls
- Consistent axis styling
- Cleaner inheritance structure

---

### 1.8 Clean Up Project Files

**Problem**: ~70KB of temporary/backup files in repository.

**Solution**: Remove and update `.gitignore`

**Files to remove**:
```
_restore_report_generator.py
_stats_full.py
tmp_inspect.py
_*.txt (12 files)
dark_report_*.png (4 files)
test_cli.png
test_cli.svg
```

**Update `.gitignore`**:
```gitignore
# Temporary files
_*.py
_*.txt
tmp_*.py

# Test outputs
test_*.png
test_*.svg
dark_report_*.png

# Cache
cache/
*.pyc
__pycache__/
```

**Impact**:
- Cleaner repository
- Reduced confusion
- Professional structure

---

## 2. BLACK & WHITE MINIMALIST DESIGN

### 2.1 Design Philosophy

**Principles**:
- **Monochrome**: Pure black (#000000) and white (#ffffff)
- **Typography-focused**: Clean, readable text
- **Minimal borders**: Subtle separators only when necessary
- **Generous whitespace**: Let content breathe
- **Functional**: Every element serves a purpose

---

### 2.2 Color Palette

```python
MONOCHROME_THEME = {
    # Backgrounds
    'bg_primary': '#ffffff',      # Main background
    'bg_secondary': '#fafafa',    # Cards/panels
    'bg_tertiary': '#f5f5f5',     # Hover states

    # Text
    'text_primary': '#000000',    # Headings, important text
    'text_secondary': '#666666',  # Body text
    'text_tertiary': '#999999',   # Subtle text

    # Borders & Lines
    'border_subtle': '#e0e0e0',   # Minimal borders
    'border_medium': '#cccccc',   # Visible separators
    'border_strong': '#000000',   # Emphasis

    # Interactive
    'interactive': '#000000',     # Buttons (black)
    'interactive_hover': '#333333',  # Hover state

    # Pitch visualization
    'pitch_bg': '#fafafa',
    'pitch_lines': '#666666',
}
```

---

### 2.3 Web App Layout (Streamlit)

**New `app.py` design**:

```python
# Custom CSS
st.markdown("""
    <style>
    /* Global */
    .main {
        background-color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* Typography */
    h1 {
        color: #000000;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 0.5em;
    }

    h2 {
        color: #000000;
        font-weight: 600;
        letter-spacing: -0.01em;
        margin-top: 2em;
        margin-bottom: 0.5em;
        border-bottom: 1px solid #e0e0e0;
        padding-bottom: 0.3em;
    }

    h3 {
        color: #333333;
        font-weight: 600;
        margin-top: 1.5em;
    }

    p {
        color: #666666;
        line-height: 1.6;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #fafafa;
        border-right: 1px solid #e0e0e0;
    }

    [data-testid="stSidebar"] h1 {
        font-size: 1.5rem;
        margin-bottom: 2rem;
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        background-color: #000000;
        color: #ffffff;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        transition: all 0.2s;
    }

    .stButton>button:hover {
        background-color: #333333;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    /* Inputs */
    .stNumberInput input,
    .stTextInput input {
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 0.5rem;
    }

    .stNumberInput input:focus,
    .stTextInput input:focus {
        border-color: #000000;
        box-shadow: 0 0 0 1px #000000;
    }

    /* Cards/Panels */
    .match-info {
        background-color: #fafafa;
        border: 1px solid #e0e0e0;
        padding: 2rem;
        margin: 2rem 0;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #000000;
        font-weight: 700;
    }

    [data-testid="stMetricLabel"] {
        color: #666666;
        font-weight: 500;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
    }

    /* Dividers */
    hr {
        border: none;
        border-top: 1px solid #e0e0e0;
        margin: 2rem 0;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #fafafa;
        border: 1px solid #e0e0e0;
        color: #000000;
        font-weight: 600;
    }

    /* Remove emoji from title */
    .main h1::before {
        content: '';
    }
    </style>
""", unsafe_allow_html=True)
```

---

### 2.4 Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│ SIDEBAR (Light Gray #fafafa)                            │
│                                                          │
│  PostMatchReport                                         │
│  ────────────────────                                    │
│                                                          │
│  MATCH IDs                                               │
│  □ WhoScored ID: [1821302]                              │
│  □ FotMob ID:    [3900958]                              │
│                                                          │
│  SETTINGS                                                │
│  □ Quality: [Medium]                                     │
│  ☑ Use Cache                                             │
│                                                          │
│  [  GENERATE REPORT  ] (Black button)                    │
│                                                          │
│  ℹ Help                                                  │
│  📊 About                                                │
│                                                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ MAIN CONTENT (Pure White #ffffff)                       │
│                                                          │
│  PostMatchReport                                         │
│  ─────────────────────────────────────                   │
│                                                          │
│  ┌─────────────────────────────────────────────┐        │
│  │ Liverpool 2 - 2 Manchester United           │        │
│  │ Premier League • 2025-01-05                 │        │
│  └─────────────────────────────────────────────┘        │
│                                                          │
│  POSSESSION      xG         SHOTS      VENUE             │
│  64% - 36%    1.8 - 1.2    15 - 8    Anfield            │
│                                                          │
│  ───────────────────────────────────────────────         │
│                                                          │
│  Match Report                                            │
│  ─────────────                                           │
│                                                          │
│  [Full report visualization]                             │
│                                                          │
│  [  DOWNLOAD REPORT  ] (Black button)                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

### 2.5 Report Visualization Changes

**Before**: Colored team visualizations (red vs blue)
**After**: Black & white with patterns

```python
# Team differentiation without color
TEAM_STYLES = {
    'home': {
        'color': '#000000',
        'marker': 'o',          # Circle
        'linestyle': '-',       # Solid
        'pattern': '///',       # Diagonal lines
        'alpha': 0.8
    },
    'away': {
        'color': '#666666',     # Gray
        'marker': 's',          # Square
        'linestyle': '--',      # Dashed
        'pattern': '...',       # Dots
        'alpha': 0.6
    }
}
```

**Shot Map**:
- Goals: Black filled circles
- On target: Black hollow circles
- Off target: Gray X marks
- xG size: Vary marker size

**Pass Networks**:
- Home team: Black solid lines, circle nodes
- Away team: Gray dashed lines, square nodes
- Line thickness: Pass volume

**Heatmaps**:
- Single color gradient: White → Gray → Black
- Remove colorbars (use grayscale naturally)

---

### 2.6 Typography Scale

```python
TYPOGRAPHY = {
    'title': {
        'size': 16,
        'weight': 'bold',
        'color': '#000000'
    },
    'subtitle': {
        'size': 12,
        'weight': '600',
        'color': '#333333'
    },
    'body': {
        'size': 10,
        'weight': 'normal',
        'color': '#666666'
    },
    'caption': {
        'size': 8,
        'weight': 'normal',
        'color': '#999999'
    }
}
```

---

## 3. IMPLEMENTATION PLAN

### Phase 1: Core Utilities (1-2 hours)
1. Create `Visual/theme_manager.py`
2. Create `Visual/pitch_factory.py`
3. Create `Visual/utils/` with utilities
4. Update `.gitignore`

### Phase 2: Refactor Visualizations (2-3 hours)
1. Create `BaseVisualization` class
2. Update all visualization classes to inherit
3. Remove duplicate methods
4. Integrate theme manager

### Phase 3: Update Report Generator (1 hour)
1. Integrate new utilities
2. Remove `_apply_dark()` calls
3. Simplify logo resolution
4. Update theme handling

### Phase 4: Web App Redesign (1-2 hours)
1. Implement new CSS
2. Update layout structure
3. Test responsive design
4. Update copy/messaging

### Phase 5: Cleanup (30 min)
1. Remove temporary files
2. Update documentation
3. Test full pipeline

**Total Estimated Time**: 6-8 hours

---

## 4. EXPECTED BENEFITS

### Code Quality
- **~500 lines removed** (duplicates, temp files)
- **Maintainability**: Single source of truth for theming
- **Extensibility**: Easy to add new visualizations
- **Testability**: Isolated utilities easier to test

### User Experience
- **Professional**: Clean, timeless design
- **Accessible**: High contrast black/white
- **Fast**: Minimal styling overhead
- **Printable**: B&W optimized for printing

### Performance
- **Smaller bundle**: Less CSS, cleaner code
- **Faster renders**: Simplified styling
- **Better caching**: Consistent theme application

---

## 5. MIGRATION STRATEGY

### Backward Compatibility
- Keep old theme as `'dark'` and `'light'`
- Add new theme `'monochrome'`
- Gradual deprecation warnings

### Testing Checklist
- [ ] All 12 visualizations render correctly
- [ ] Theme switching works
- [ ] Logo resolution functions
- [ ] Web app responsive on mobile
- [ ] Print-friendly output
- [ ] Cache still functional
- [ ] CLI interface unchanged

---

## 6. NEXT STEPS

1. **Review this proposal** - Approve overall direction
2. **Prioritize phases** - Which to implement first?
3. **Create feature branch** - `refactor/monochrome-theme`
4. **Implement incrementally** - Phase by phase
5. **Test thoroughly** - Each phase independently
6. **Deploy** - Merge when stable

---

## APPENDIX A: File Structure After Refactoring

```
PostMatchReport/
├── ETL/
│   ├── extractors/
│   ├── transformers/
│   └── loaders/
├── Visual/
│   ├── base_visualization.py          # NEW
│   ├── theme_manager.py               # NEW
│   ├── pitch_factory.py               # NEW
│   ├── utils/                         # NEW
│   │   ├── __init__.py
│   │   ├── colorbar_utils.py
│   │   ├── shot_utils.py
│   │   └── data_utils.py
│   ├── pitch_visualizations.py        # REFACTORED
│   ├── statistical_visualizations.py  # REFACTORED
│   ├── heatmap_visualizations.py      # REFACTORED
│   ├── advanced_visualizations.py     # REFACTORED
│   └── tactical_visualizations.py     # REFACTORED
├── Reporting/
│   └── report_generator.py            # REFACTORED
├── config/
│   ├── settings.py
│   └── logos/
├── app.py                             # REDESIGNED
├── main.py
└── .gitignore                         # UPDATED
```

---

## APPENDIX B: Example Before/After

### Before (report_generator.py):
```python
# Lines 190-220 (repeated 12 times)
def _apply_dark(ax):
    if self.theme != 'dark':
        return
    try:
        for spine in ax.spines.values():
            spine.set_color('#9aa6b2')
    except Exception:
        pass
    # ... 20 more lines

# Lines 217-226
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor(self.bg_color)
self.stats_viz.create_match_summary_panel(ax1, match_summary, text_color=self.text_color)
_apply_dark(ax1)  # REPEATED 12 TIMES
```

### After (report_generator.py):
```python
# Lines simplified
ax1 = fig.add_subplot(gs[0, 0])
self.stats_viz.create_match_summary_panel(
    ax1, match_summary
)  # Theme applied automatically in base class
```

**Reduction**: From ~15 lines per subplot to ~3 lines
**Total saved**: ~144 lines in report_generator.py alone

---

*End of Proposal*
