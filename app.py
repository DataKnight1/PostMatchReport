"""
PostMatchReport - Enhanced Streamlit Web Application
Beautiful, professional web app with separate component views and complete report generation.
"""

import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime
import json
import os
import pandas as pd

from Reporting.report_generator import ReportGenerator
from ETL.transformers.match_processor import MatchProcessor
from Visual.pitch_visualizations import PitchVisualizations
from Visual.statistical_visualizations import StatisticalVisualizations
from Visual.heatmap_visualizations import HeatmapVisualizations
from Visual.advanced_visualizations import AdvancedVisualizations
from Visual.tactical_visualizations import TacticalVisualizer


# Page configuration
st.set_page_config(
    page_title="PostMatchReport - Professional Football Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Dark Mode Design
st.markdown("""
    <style>
    /* Global Styles - Dark Mode */
    .main {
        background-color: #22272e;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #e6edf3;
    }

    /* Typography */
    h1 {
        color: #e6edf3;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 0.5em;
    }

    h2 {
        color: #e6edf3;
        font-weight: 600;
        letter-spacing: -0.01em;
        margin-top: 2em;
        margin-bottom: 0.5em;
        border-bottom: 1px solid #444c56;
        padding-bottom: 0.3em;
    }

    h3 {
        color: #9aa6b2;
        font-weight: 600;
        margin-top: 1.5em;
    }

    p {
        color: #9aa6b2;
        line-height: 1.6;
    }

    /* Sidebar - Dark */
    [data-testid="stSidebar"] {
        background-color: #2b313a;
        border-right: 1px solid #444c56;
    }

    [data-testid="stSidebar"] h1 {
        font-size: 1.5rem;
        margin-bottom: 2rem;
        color: #e6edf3;
    }

    /* Buttons - Light on Dark */
    .stButton>button {
        width: 100%;
        background-color: #539bf5;
        color: #ffffff;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        transition: all 0.2s;
        border-radius: 4px;
    }

    .stButton>button:hover {
        background-color: #6cb6ff;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(83, 155, 245, 0.3);
    }

    /* Inputs - Dark with Light Text */
    .stNumberInput input,
    .stTextInput input,
    .stSelectbox select {
        border: 1px solid #444c56;
        border-radius: 4px;
        padding: 0.5rem;
        background-color: #2b313a;
        color: #e6edf3;
    }

    .stNumberInput input:focus,
    .stTextInput input:focus,
    .stSelectbox select:focus {
        border-color: #539bf5;
        box-shadow: 0 0 0 1px #539bf5;
        outline: none;
    }

    /* Checkbox */
    .stCheckbox {
        color: #9aa6b2;
    }

    /* Cards/Panels - Dark */
    .match-info {
        background-color: #2b313a;
        border: 1px solid #444c56;
        padding: 2rem;
        margin: 2rem 0;
        border-radius: 4px;
    }

    /* Metrics - Light Text */
    [data-testid="stMetricValue"] {
        color: #e6edf3;
        font-weight: 700;
    }

    [data-testid="stMetricLabel"] {
        color: #9aa6b2;
        font-weight: 500;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
    }

    /* Dividers */
    hr {
        border: none;
        border-top: 1px solid #444c56;
        margin: 2rem 0;
    }

    /* Expanders - Dark */
    .streamlit-expanderHeader {
        background-color: #2b313a;
        border: 1px solid #444c56;
        color: #e6edf3;
        font-weight: 600;
        border-radius: 4px;
    }

    .streamlit-expanderHeader:hover {
        background-color: #373e47;
    }

    /* Info boxes - Dark */
    .stAlert {
        background-color: #2b313a;
        border: 1px solid #444c56;
        color: #9aa6b2;
        border-radius: 4px;
    }

    /* Download button - Outlined */
    .stDownloadButton>button {
        background-color: #2b313a;
        color: #e6edf3;
        border: 1px solid #539bf5;
        font-weight: 600;
    }

    .stDownloadButton>button:hover {
        background-color: #539bf5;
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def load_match_data(whoscored_id: int, fotmob_id: int = None, use_cache: bool = True):
    """Load and process match data with caching."""
    generator = ReportGenerator(cache_dir="./cache", theme='dark')
    whoscored_data, fotmob_data = generator.data_loader.load_all_data(
        whoscored_id, fotmob_id, use_cache=use_cache
    )

    # Check if WhoScored data was successfully loaded
    if not whoscored_data.get('match_centre', {}).get('success'):
        error_msg = whoscored_data.get('match_centre', {}).get('error', 'Unknown error loading match data')
        raise ValueError(f"Failed to load WhoScored data: {error_msg}")

    processor = MatchProcessor(whoscored_data, fotmob_data)
    match_summary = processor.get_complete_match_summary()

    # Double-check match summary has required data
    if not match_summary.get('success'):
        raise ValueError("Match data processing failed")

    return whoscored_data, fotmob_data, processor, match_summary


@st.cache_data(ttl=3600)
def generate_complete_report(whoscored_id: int, fotmob_id: int = None, theme: str = 'dark', dpi: int = 100):
    """Generate complete report with all visualizations."""
    generator = ReportGenerator(cache_dir="./cache", theme=theme)
    fig = generator.generate_report(
        whoscored_id=whoscored_id,
        fotmob_id=fotmob_id,
        output_file=None,
        use_cache=True,
        dpi=dpi
    )
    return fig


def generate_individual_visualization(processor, match_summary, viz_type: str, theme: str = 'dark'):
    """Generate individual visualization based on type (no reloads)."""
    fig, ax = plt.subplots(figsize=(12, 8), facecolor=('#0e1117' if theme == 'dark' else 'white'))

    # Theme colors for pitch modules
    if theme == 'dark':
        pitch_color, line_color = '#2b313a', '#d0d7de'
        text_color = '#e6edf3'
    else:
        pitch_color, line_color = '#d6c39f', '#0e1117'
        text_color = 'black'

    pitch_viz = PitchVisualizations(pitch_color=pitch_color, line_color=line_color)
    stats_viz = StatisticalVisualizations()
    heatmap_viz = HeatmapVisualizations(pitch_color=pitch_color, line_color=line_color)
    advanced_viz = AdvancedVisualizations(pitch_color=pitch_color, line_color=line_color)
    tactical_viz = TacticalVisualizer()

    # Team context
    home_id = match_summary['teams']['home']['id']
    away_id = match_summary['teams']['away']['id']
    home_name = match_summary['teams']['home']['name']
    away_name = match_summary['teams']['away']['name']
    home_color = match_summary.get('team_colors', {}).get('home_color', '#FF0000')
    away_color = match_summary.get('team_colors', {}).get('away_color', '#0000FF')

    try:
        if viz_type == "shot_map":
            shots_home = processor.get_shots(home_id)
            shots_away = processor.get_shots(away_id)
            pitch_viz.create_xg_shot_map(ax, shots_home, shots_away, home_color, away_color)

        elif viz_type == "match_summary":
            stats_viz.create_match_summary_panel(ax, match_summary, text_color=text_color)

        elif viz_type == "momentum":
            events_df = processor.get_events_dataframe()
            advanced_viz.create_momentum_graph(
                ax, events_df, home_id, away_id, home_color, away_color, home_name, away_name
            )

        elif viz_type == "pass_network_home":
            positions, connections = processor.get_pass_network_data(home_id, min_passes=3)
            pitch_viz.create_pass_network(ax, positions, connections, home_color, home_name)

        elif viz_type == "pass_network_away":
            positions, connections = processor.get_pass_network_data(away_id, min_passes=3)
            pitch_viz.create_pass_network(ax, positions, connections, away_color, away_name)

        elif viz_type == "xg_timeline":
            shots_home = processor.get_shots(home_id)
            shots_away = processor.get_shots(away_id)
            all_shots = (
                pd.concat([shots_home, shots_away])
                if (shots_home is not None and not shots_home.empty) or (shots_away is not None and not shots_away.empty)
                else pd.DataFrame()
            )
            advanced_viz.create_cumulative_xg(
                ax, all_shots, home_id, away_id, home_color, away_color, home_name, away_name
            )

        elif viz_type == "zone14_home":
            passes_home = processor.get_passes(team_id=home_id, successful_only=True)
            advanced_viz.create_zone14_map(ax, passes_home, home_color, home_name)

        elif viz_type == "zone14_away":
            passes_away = processor.get_passes(team_id=away_id, successful_only=True)
            advanced_viz.create_zone14_map(ax, passes_away, away_color, away_name)

        elif viz_type == "pitch_control":
            events_df = processor.get_events_dataframe()
            heatmap_viz.create_pitch_control_map(
                ax,
                events_df[events_df['teamId'] == home_id],
                events_df[events_df['teamId'] == away_id],
                home_color,
                away_color,
            )

        elif viz_type == "defensive_home":
            def_actions = processor.get_defensive_actions(home_id)
            heatmap_viz.create_defensive_actions_heatmap(ax, def_actions, home_color, home_name)

        elif viz_type == "defensive_away":
            def_actions = processor.get_defensive_actions(away_id)
            heatmap_viz.create_defensive_actions_heatmap(ax, def_actions, away_color, away_name)

        elif viz_type == "zonal_control":
            zone_matrix = processor.event_processor.calculate_zonal_control(home_id, away_id, grid_cols=6, grid_rows=4)
            home_team_info = {"name": home_name, "id": home_id}
            away_team_info = {"name": away_name, "id": away_id}
            tactical_viz.create_zonal_control_map(
                ax, zone_matrix, home_team_info, away_team_info, home_color, away_color, 'right', 'left'
            )

    except Exception as e:
        ax.text(
            0.5,
            0.5,
            f"Error generating visualization:\n{str(e)}",
            ha='center',
            va='center',
            transform=ax.transAxes,
            color=(text_color or 'black'),
        )

    plt.tight_layout()
    return fig


@st.cache_data(ttl=3600)
def generate_specific_visualization(whoscored_id: int, fotmob_id: int = None,
                                    viz_type: str = 'pass_network', theme: str = 'dark'):
    """
    Generate specific visualization with caching.

    Args:
        whoscored_id: WhoScored match ID
        fotmob_id: FotMob match ID
        viz_type: Type of visualization to generate
        theme: 'dark' or 'light'

    Returns:
        Matplotlib Figure and match summary
    """
    # Initialize generator
    generator = ReportGenerator(cache_dir="./cache", theme=theme)

    # Load data
    whoscored_data, fotmob_data = generator.data_loader.load_all_data(
        whoscored_id, fotmob_id, use_cache=True
    )

    # Process data
    processor = MatchProcessor(whoscored_data, fotmob_data)
    match_summary = processor.get_complete_match_summary()

    if not match_summary.get('success'):
        raise ValueError("Failed to process match data")

    # Extract team info
    home_id = match_summary['teams']['home']['id']
    away_id = match_summary['teams']['away']['id']
    home_name = match_summary['teams']['home']['name']
    away_name = match_summary['teams']['away']['name']
    home_color = match_summary['team_colors'].get('home_color', '#FF0000')
    away_color = match_summary['team_colors'].get('away_color', '#0000FF')

    # Set theme colors
    if theme == 'dark':
        bg_color = '#22272e'
        text_color = '#e6edf3'
    else:
        bg_color = '#f0f0f0'
        text_color = 'black'

    def _apply_dark_theme(ax):
        """Apply dark theme to axes."""
        if theme != 'dark':
            return
        try:
            for spine in ax.spines.values():
                spine.set_color('#9aa6b2')
        except Exception:
            pass
        ax.tick_params(colors=text_color)
        for lbl in ax.get_xticklabels() + ax.get_yticklabels():
            try:
                lbl.set_color(text_color)
            except Exception:
                pass
        try:
            ax.set_title(ax.get_title(), color=text_color)
            ax.xaxis.label.set_color(text_color)
            ax.yaxis.label.set_color(text_color)
            leg = ax.get_legend()
            if leg is not None:
                for text in leg.get_texts():
                    text.set_color(text_color)
                leg.get_frame().set_edgecolor('#9aa6b2')
        except Exception:
            pass

    # Create figure based on viz type
    if viz_type == 'statistics':
        fig = plt.figure(figsize=(10, 6), facecolor=bg_color)
        ax = fig.add_subplot(111)
        ax.set_facecolor(bg_color)
        generator.stats_viz.create_match_summary_panel(ax, match_summary, text_color=text_color)
        _apply_dark_theme(ax)

    elif viz_type == 'shot_map':
        shots_home = processor.get_shots(home_id)
        shots_away = processor.get_shots(away_id)
        fig = plt.figure(figsize=(12, 8), facecolor=bg_color)
        ax = fig.add_subplot(111)
        ax.set_facecolor(bg_color)
        generator.pitch_viz.create_xg_shot_map(ax, shots_home, shots_away, home_color, away_color)
        _apply_dark_theme(ax)

    elif viz_type == 'pass_network':
        home_positions, home_connections = processor.get_pass_network_data(home_id, min_passes=3)
        away_positions, away_connections = processor.get_pass_network_data(away_id, min_passes=3)
        fig = plt.figure(figsize=(16, 8), facecolor=bg_color)

        ax1 = fig.add_subplot(121)
        ax1.set_facecolor(bg_color)
        generator.pitch_viz.create_pass_network(ax1, home_positions, home_connections, home_color, home_name)
        _apply_dark_theme(ax1)

        ax2 = fig.add_subplot(122)
        ax2.set_facecolor(bg_color)
        generator.pitch_viz.create_pass_network(ax2, away_positions, away_connections, away_color, away_name)
        _apply_dark_theme(ax2)

    elif viz_type == 'momentum':
        events_df = processor.get_events_dataframe()
        fig = plt.figure(figsize=(12, 6), facecolor=bg_color)
        ax = fig.add_subplot(111)
        ax.set_facecolor(bg_color)
        generator.advanced_viz.create_momentum_graph(ax, events_df, home_id, away_id,
                                                     home_color, away_color, home_name, away_name)
        _apply_dark_theme(ax)

    elif viz_type == 'xg_timeline':
        shots_home = processor.get_shots(home_id)
        shots_away = processor.get_shots(away_id)
        all_shots = pd.concat([shots_home, shots_away]) if not shots_home.empty and not shots_away.empty else (shots_home if not shots_home.empty else shots_away)
        fig = plt.figure(figsize=(12, 6), facecolor=bg_color)
        ax = fig.add_subplot(111)
        ax.set_facecolor(bg_color)
        generator.advanced_viz.create_cumulative_xg(ax, all_shots, home_id, away_id,
                                                    home_color, away_color, home_name, away_name)
        _apply_dark_theme(ax)

    elif viz_type == 'zone14':
        passes_home = processor.get_passes(home_id, successful_only=True)
        passes_away = processor.get_passes(away_id, successful_only=True)
        fig = plt.figure(figsize=(16, 8), facecolor=bg_color)

        ax1 = fig.add_subplot(121)
        ax1.set_facecolor(bg_color)
        generator.advanced_viz.create_zone14_map(ax1, passes_home, home_color, home_name)
        _apply_dark_theme(ax1)

        ax2 = fig.add_subplot(122)
        ax2.set_facecolor(bg_color)
        generator.advanced_viz.create_zone14_map(ax2, passes_away, away_color, away_name)
        _apply_dark_theme(ax2)

    elif viz_type == 'defensive_actions':
        def_actions_home = processor.get_defensive_actions(home_id)
        def_actions_away = processor.get_defensive_actions(away_id)
        fig = plt.figure(figsize=(16, 8), facecolor=bg_color)

        ax1 = fig.add_subplot(121)
        ax1.set_facecolor(bg_color)
        generator.heatmap_viz.create_defensive_actions_heatmap(ax1, def_actions_home, home_color, home_name)
        _apply_dark_theme(ax1)

        ax2 = fig.add_subplot(122)
        ax2.set_facecolor(bg_color)
        generator.heatmap_viz.create_defensive_actions_heatmap(ax2, def_actions_away, away_color, away_name)
        _apply_dark_theme(ax2)

    elif viz_type == 'pitch_control':
        events_df = processor.get_events_dataframe()
        fig = plt.figure(figsize=(12, 8), facecolor=bg_color)
        ax = fig.add_subplot(111)
        ax.set_facecolor(bg_color)
        generator.heatmap_viz.create_pitch_control_map(ax,
                                                       events_df[events_df['teamId']==home_id],
                                                       events_df[events_df['teamId']==away_id],
                                                       home_color, away_color)
        _apply_dark_theme(ax)

    elif viz_type == 'zonal_control':
        events_df = processor.get_events_dataframe()
        zone_matrix = processor.event_processor.calculate_zonal_control(home_id, away_id, grid_cols=6, grid_rows=4)
        fig = plt.figure(figsize=(12, 8), facecolor=bg_color)
        ax = fig.add_subplot(111)
        ax.set_facecolor(bg_color)
        home_team_info = {'name': home_name, 'id': home_id}
        away_team_info = {'name': away_name, 'id': away_id}
        generator.tactical_viz.create_zonal_control_map(ax, zone_matrix, home_team_info, away_team_info,
                                                        home_color, away_color, 'right', 'left')
        _apply_dark_theme(ax)

    # Add watermark
    fig.text(0.5, 0.01, 'PostMatchReport - Advanced Football Analytics',
            ha='center', fontsize=8, alpha=0.6, style='italic',
            color='white' if theme=='dark' else 'black')

    return fig, match_summary


def fig_to_base64(fig, dpi=100):
    """Convert matplotlib figure to base64 string."""
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode()
    buf.close()
    return img_str


def main():
    """Main application with enhanced UI."""

    # Header
    st.markdown("<h1>⚽ PostMatchReport</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #9aa6b2; margin-bottom: 2rem;'>Professional Football Analytics Platform</p>", unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("<div style='text-align: center; padding: 1rem;'>", unsafe_allow_html=True)
        st.image("https://img.icons8.com/color/96/000000/soccer-ball.png", width=80)
        st.markdown("<h2 style='color: #e6edf3; text-align: center;'>Match Configuration</h2>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("---")

        # Match IDs
        st.markdown("<h3 style='color: #9aa6b2;'>Match IDs</h3>", unsafe_allow_html=True)

        whoscored_id = st.number_input(
            "WhoScored Match ID",
            min_value=1,
            value=1821302,
            help="Enter the WhoScored match ID from the URL"
        )

        fotmob_id = st.number_input(
            "FotMob Match ID (Optional)",
            min_value=0,
            value=3900958,
            help="Enter the FotMob match ID for enhanced stats"
        )

        st.markdown("---")

        # Options
        st.subheader("Options")

        theme = st.selectbox(
            "Report Theme",
            options=["dark", "light"],
            index=0,
            help="Choose visualization theme"
        )

        dpi_setting = st.select_slider(
            "Report Quality",
            options=[80, 100, 150, 200, 300],
            value=150,
            help="Higher DPI = better quality but slower generation"
        )

        use_cache = st.checkbox(
            "Use Cached Data",
            value=True,
            help="Load previously extracted data if available"
        )

        st.markdown("---")

        # Load Data Button
        load_button = st.button("Load Match Data", type="primary")

        st.markdown("---")

        # Help
        with st.expander("How to find Match IDs"):
            st.markdown("""
            **WhoScored:**
            - Go to whoscored.com
            - Navigate to a match page
            - Copy ID from URL: `Matches/{ID}/...`

            **FotMob:**
            - Go to fotmob.com
            - Navigate to a match page
            - Copy ID from URL: `matches/{ID}/...`
            """)

        with st.expander("Visualizations Included"):
            st.markdown("""
            **12 Professional Visualizations:**
            1. Match Summary Panel
            2. Shot Map with xG
            3. Match Momentum Graph
            4. Pass Networks (Both Teams)
            5. Cumulative xG Timeline
            6. Zone 14 Analysis (Both Teams)
            7. Pitch Control Heatmap
            8. Defensive Actions (Both Teams)
            9. Zonal Control Map
            """)

    # Main content
    if not load_button and 'match_loaded' not in st.session_state:
        # Welcome screen
        st.markdown("""
        <div class="component-card">
            <h2>Welcome to PostMatchReport!</h2>
            <p style='font-size: 1.2rem; color: #9aa6b2; line-height: 1.8;'>
                Generate comprehensive football match reports with 12 professional visualizations.
                View each component separately or generate a complete combined report.
            </p>
            <br>
            <h3>Features</h3>
            <ul style='font-size: 1.1rem; color: #9aa6b2; line-height: 2;'>
                <li><strong>Individual Component View</strong> - Explore each visualization separately</li>
                <li><strong>Complete Report Generation</strong> - professional 4x3 grid layout</li>
                <li><strong>Dark & Light Themes</strong> - Choose your preferred style</li>
                <li><strong>High-Quality Export</strong> - Up to 300 DPI resolution</li>
                <li><strong>Smart Caching</strong> - Fast reloading of previous matches</li>
            </ul>
            <br>
            <p style='font-size: 1.1rem; color: #539bf5; font-weight: 600;'>
                Enter Match IDs in the sidebar and click "Load Match Data" to begin
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Example cards
        st.markdown("<h2 style='margin-top: 3rem;'>What You'll Get</h2>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div class="stats-card">
                <h3>🎯 Shot Analysis</h3>
                <p>All shots with xG values, outcomes, and field positions</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="stats-card">
                <h3>🔗 Pass Networks</h3>
                <p>Team passing patterns and player connections with average positions</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="stats-card">
                <h3>🔥 Heat Maps</h3>
                <p>Defensive pressure, pitch control, and territorial analysis</p>
            </div>
            """, unsafe_allow_html=True)

        return

    # Load match data
    if load_button or 'match_loaded' in st.session_state:
        if load_button:
            if whoscored_id < 1:
                st.error("❌ Please enter a valid WhoScored Match ID")
                return

            with st.spinner("Loading match data..."):
                try:
                    fotmob_id_value = fotmob_id if fotmob_id > 0 else None
                    whoscored_data, fotmob_data, processor, match_summary = load_match_data(
                        whoscored_id, fotmob_id_value, use_cache
                    )

                    # Store in session state
                    st.session_state['match_loaded'] = True
                    st.session_state['whoscored_id'] = whoscored_id
                    st.session_state['fotmob_id'] = fotmob_id_value
                    st.session_state['processor'] = processor
                    st.session_state['match_summary'] = match_summary
                    st.session_state['theme'] = theme
                    st.session_state['dpi'] = dpi_setting

                    st.success("✅ Match data loaded successfully!")

                except Exception as e:
                    st.error(f"❌ Error loading match data: {str(e)}")
                    st.exception(e)
                    return

        # Retrieve from session state
        processor = st.session_state['processor']
        match_summary = st.session_state['match_summary']
        theme = st.session_state.get('theme', 'dark')
        dpi_setting = st.session_state.get('dpi', 150)

        # Check if match data was successfully loaded
        if not match_summary.get('success'):
            st.error("❌ Failed to load match data. Please check the Match ID and try again.")
            if 'match_loaded' in st.session_state:
                del st.session_state['match_loaded']
            return

        # Match info header
        home_name = match_summary['teams']['home']['name']
        away_name = match_summary['teams']['away']['name']
        score = match_summary['match_info'].get('score', '0:0')
        home_score, away_score = score.split(':') if ':' in score else ('0', '0')
        competition = match_summary['match_info'].get('competition') or {}
        league = competition.get('name', 'N/A')
        date = match_summary['match_info'].get('date', 'N/A')[:10] if match_summary['match_info'].get('date') else 'N/A'
        venue = match_summary['match_info'].get('venue', 'N/A')

        st.markdown(f"""
        <div class="match-info">
            <h2 style='text-align: center;'>
                {home_name} <span style='font-weight: 900;'>{home_score} - {away_score}</span> {away_name}
            </h2>
            <p style='text-align: center;'>
                <strong>{league}</strong> • {date} • {venue}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Key stats
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            home_poss = match_summary['possession'].get('home', 50)
            away_poss = match_summary['possession'].get('away', 50)
            st.metric(
                "Possession",
                f"{home_poss:.0f}% - {away_poss:.0f}%"
            )

        with col2:
            home_xg = match_summary['xg'].get('home_xg', 0)
            away_xg = match_summary['xg'].get('away_xg', 0)
            st.metric(
                "Expected Goals (xG)",
                f"{home_xg:.2f} - {away_xg:.2f}"
            )

        with col3:
            shots_data = match_summary.get('shots_data') or {}
            home_shots = shots_data.get('home_shots', 0)
            away_shots = shots_data.get('away_shots', 0)
            st.metric(
                "Shots",
                f"{home_shots} - {away_shots}"
            )

        with col4:
            home_sot = shots_data.get('home_shots_on_target', 0)
            away_sot = shots_data.get('away_shots_on_target', 0)
            st.metric(
                "On Target",
                f"{home_sot} - {away_sot}"
            )
        st.markdown("---")

        # Tabbed interface
        tab1, tab2, tab3 = st.tabs(["Individual Components","Complete Report","Download & Export"])

        with tab1:
            st.markdown("<h2>View Individual Visualizations</h2>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 1.1rem; color: #9aa6b2;'>Explore each analysis component separately with full detail</p>", unsafe_allow_html=True)

            # Component categories
            st.markdown("<h3 style='margin-top: 2rem;'>Overview & Statistics</h3>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Match Summary Panel", use_container_width=True):
                    with st.spinner("Generating Match Summary..."):
                        fig = generate_individual_visualization(processor, match_summary, "match_summary", theme)
                        st.pyplot(fig)
                        plt.close(fig)

            with col2:
                if st.button("Match Momentum Graph", use_container_width=True):
                    with st.spinner("Generating Momentum Graph..."):
                        fig = generate_individual_visualization(processor, match_summary, "momentum", theme)
                        st.pyplot(fig)
                        plt.close(fig)

            st.markdown("<h3 style='margin-top: 2rem;'>Attacking Analysis</h3>", unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("Shot Map with xG", use_container_width=True):
                    with st.spinner("Generating Shot Map..."):
                        fig = generate_individual_visualization(processor, match_summary, "shot_map", theme)
                        st.pyplot(fig)
                        plt.close(fig)

            with col2:
                if st.button(f"Pass Network - {home_name}", use_container_width=True):
                    with st.spinner(f"Generating Pass Network for {home_name}..."):
                        fig = generate_individual_visualization(processor, match_summary, "pass_network_home", theme)
                        st.pyplot(fig)
                        plt.close(fig)

            with col3:
                if st.button(f"Pass Network - {away_name}", use_container_width=True):
                    with st.spinner(f"Generating Pass Network for {away_name}..."):
                        fig = generate_individual_visualization(processor, match_summary, "pass_network_away", theme)
                        st.pyplot(fig)
                        plt.close(fig)

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("Cumulative xG Timeline", use_container_width=True):
                    with st.spinner("Generating xG Timeline..."):
                        fig = generate_individual_visualization(processor, match_summary, "xg_timeline", theme)
                        st.pyplot(fig)
                        plt.close(fig)

            with col2:
                if st.button(f"Zone 14 - {home_name}", use_container_width=True):
                    with st.spinner(f"Generating Zone 14 for {home_name}..."):
                        fig = generate_individual_visualization(processor, match_summary, "zone14_home", theme)
                        st.pyplot(fig)
                        plt.close(fig)

            with col3:
                if st.button(f"Zone 14 - {away_name}", use_container_width=True):
                    with st.spinner(f"Generating Zone 14 for {away_name}..."):
                        fig = generate_individual_visualization(processor, match_summary, "zone14_away", theme)
                        st.pyplot(fig)
                        plt.close(fig)

            st.markdown("<h3 style='margin-top: 2rem;'>Defensive & Territorial Analysis</h3>", unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("Pitch Control Map", use_container_width=True):
                    with st.spinner("Generating Pitch Control..."):
                        fig = generate_individual_visualization(processor, match_summary, "pitch_control", theme)
                        st.pyplot(fig)
                        plt.close(fig)

            with col2:
                if st.button(f"Defensive Actions - {home_name}", use_container_width=True):
                    with st.spinner(f"Generating Defensive Heatmap for {home_name}..."):
                        fig = generate_individual_visualization(processor, match_summary, "defensive_home", theme)
                        st.pyplot(fig)
                        plt.close(fig)

            with col3:
                if st.button(f"Defensive Actions - {away_name}", use_container_width=True):
                    with st.spinner(f"Generating Defensive Heatmap for {away_name}..."):
                        fig = generate_individual_visualization(processor, match_summary, "defensive_away", theme)
                        st.pyplot(fig)
                        plt.close(fig)

            col1, col2, col3 = st.columns([1, 1, 1])

            with col2:
                if st.button("Zonal Control Map", use_container_width=True):
                    with st.spinner("Generating Zonal Control..."):
                        fig = generate_individual_visualization(processor, match_summary, "zonal_control", theme)
                        st.pyplot(fig)
                        plt.close(fig)

        with tab2:
            st.markdown("<h2>Complete Match Report</h2>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 1.1rem; color: #9aa6b2;'>All 12 visualizations in a professional 4x3 grid layout</p>", unsafe_allow_html=True)

            generate_report_btn = st.button("Generate Complete Report", type="primary", use_container_width=True)

            if generate_report_btn or 'complete_report' in st.session_state:
                if generate_report_btn:
                    with st.spinner("Generating complete report... This may take a minute..."):
                        try:
                            fig = generate_complete_report(
                                st.session_state['whoscored_id'],
                                st.session_state['fotmob_id'],
                                theme,
                                dpi_setting
                            )
                            st.session_state['complete_report'] = fig
                            st.success("Complete report generated!")
                        except Exception as e:
                            st.error(f"❌ Error generating report: {str(e)}")
                            st.exception(e)

                if 'complete_report' in st.session_state:
                    fig = st.session_state['complete_report']

                    # Display report
                    img_str = fig_to_base64(fig, dpi=dpi_setting)
                    st.markdown(
                        f'<img src="data:image/png;base64,{img_str}" style="width:100%; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.2);">',
                        unsafe_allow_html=True
                    )

        with tab3:
            st.markdown("<h2>Download & Export Options</h2>", unsafe_allow_html=True)

            if 'complete_report' in st.session_state:
                st.markdown("""
                <div class="download-section">
                    <h3>Your report is ready!</h3>
                    <p style='font-size: 1.1rem; color: #9aa6b2;'>Download the complete match report in high quality</p>
                </div>
                """, unsafe_allow_html=True)

                # Display stats summary
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    home_poss = match_summary['possession'].get('home', 50)
                    away_poss = match_summary['possession'].get('away', 50)
                    st.metric(
                        "Possession",
                        f"{home_poss:.0f}% - {away_poss:.0f}%"
                    )

                with col2:
                    home_xg = match_summary['xg'].get('home_xg', 0)
                    away_xg = match_summary['xg'].get('away_xg', 0)
                    st.metric(
                        "xG",
                        f"{home_xg:.2f} - {away_xg:.2f}"
                    )

                with col3:
                    shots_data = match_summary.get('shots_data') or {}
                    home_shots = shots_data.get('home_shots', 0)
                    away_shots = shots_data.get('away_shots', 0)
                    st.metric(
                        "Shots",
                        f"{home_shots} - {away_shots}"
                    )

                with col4:
                    st.metric(
                        "Venue",
                        venue
                    )

                st.markdown("---")
                selected_viz_type = 'full_report'
                # Display report with appropriate title
                viz_display_names = {"full_report": "Full Match Report","statistics": "Match Statistics","shot_map": "Shot Map","pass_network": "Pass Network","momentum": "Match Momentum","xg_timeline": "xG Timeline","zone14": "Zone 14 & Half-Spaces","defensive_actions": "Defensive Actions","pitch_control": "Pitch Control","zonal_control": "Zonal Control"}

                st.subheader(viz_display_names.get(selected_viz_type, "Match Report"))
                # Convert figure to image
                img_str = fig_to_base64(fig, dpi=dpi_setting)

                # Display image
                st.markdown(
                    f'<img src="data:image/png;base64,{img_str}" style="width:100%">',
                    unsafe_allow_html=True
                )

                # Download button
                st.markdown("---")

                # Create downloadable file
                buf = BytesIO()
                bg_save = '#22272e' if theme == 'dark' else '#f0f0f0'
                fig.savefig(buf, format='png', dpi=dpi_setting, bbox_inches='tight', facecolor=bg_save)
                buf.seek(0)

                viz_filename_suffix = "full_report"
                filename = f"{home_name}_{away_name}_{datetime.now().strftime('%Y%m%d')}_{viz_filename_suffix}.png"
                filename = filename.replace(' ', '_')

                download_label = "Download Full Report"
                col1, col2, col3 = st.columns([1, 2, 1])

                with col2:
                    st.download_button(
                        label=download_label,
                        data=buf,
                        file_name=filename,
                        mime="image/png",
                        use_container_width=True
                    )

                st.success("Full report generated successfully!")

                # Export options
                st.markdown("---")
                st.markdown("<h3>Export Settings</h3>", unsafe_allow_html=True)

                col1, col2 = st.columns(2)

                with col1:
                    st.info(f"**Resolution:** {dpi_setting} DPI")
                    st.info(f"**Theme:** {theme.capitalize()}")

                with col2:
                    st.info(f"**Format:** PNG")
                    st.info(f"**Match:** {home_name} vs {away_name}")

            else:
                st.info("👆 Generate the complete report first in the 'Complete Report' tab to enable download options")
    # Footer
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <p style='font-size: 1.1rem; font-weight: 600; color: #9aa6b2;'>PostMatchReport - Professional Football Analytics</p>
        <p style='font-size: 0.9rem; color: #6e7681;'>Data from WhoScored & FotMob • Built with Python & Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    # Create cache directory
    os.makedirs("./cache", exist_ok=True)

    # Run app
    main()





