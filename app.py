"""
PostMatchReport - Streamlit Web Application
Interactive web app for generating and viewing match reports.
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


# Page configuration
st.set_page_config(
    page_title="PostMatchReport",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f0f0f0;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
    }
    h2 {
        color: #34495e;
    }
    .match-info {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def generate_report_cached(whoscored_id: int, fotmob_id: int = None, *, theme: str = 'dark'):
    """
    Generate report with caching.

    Args:
        whoscored_id: WhoScored match ID
        fotmob_id: FotMob match ID

    Returns:
        Matplotlib Figure and match summary
    """
    # Use new ReportGenerator
    generator = ReportGenerator(cache_dir="./cache", theme=theme)

    # Generate complete report
    fig = generator.generate_report(
        whoscored_id=whoscored_id,
        fotmob_id=fotmob_id,
        output_file=None,
        use_cache=True,
        dpi=100
    )

    # Load data for summary info
    whoscored_data, fotmob_data = generator.data_loader.load_all_data(
        whoscored_id, fotmob_id, use_cache=True
    )

    # Process data for summary
    processor = MatchProcessor(whoscored_data, fotmob_data)
    match_summary = processor.get_complete_match_summary()

    return fig, match_summary


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
    """
    Convert matplotlib figure to base64 string.

    Args:
        fig: Matplotlib figure
        dpi: DPI for image

    Returns:
        Base64 encoded string
    """
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight', facecolor='#f0f0f0')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode()
    buf.close()
    return img_str


def main():
    """Main application."""

    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/soccer-ball.png", width=80)
        st.title("⚽ PostMatchReport")
        st.markdown("---")

        st.header("Match Selection")

        # Manual ID input
        st.subheader("Enter Match IDs")

        whoscored_id = st.number_input(
            "WhoScored Match ID",
            min_value=1,
            value=1821302,
            help="Enter the WhoScored match ID from the URL (Default: Liverpool vs Man Utd, Jan 5 2025)"
        )

        fotmob_id = st.number_input(
            "FotMob Match ID (Optional)",
            min_value=0,
            value=3900958,
            help="Enter the FotMob match ID for enhanced stats (xG, colors, etc.)"
        )

        st.markdown("---")

        # Visualization Type Selection
        st.subheader("📊 Visualization Type")

        viz_option = st.radio(
            "Select what to generate:",
            options=[
                "Full Report",
                "Statistics",
                "Shot Map",
                "Pass Network",
                "Match Momentum",
                "xG Timeline",
                "Zone 14 & Half-Spaces",
                "Defensive Actions",
                "Pitch Control",
                "Zonal Control"
            ],
            index=0,
            help="Choose the type of visualization to generate"
        )

        st.markdown("---")

        # Options
        st.subheader("Options")

        theme_option = st.selectbox(
            "Theme",
            options=["Dark", "Light"],
            index=0,
            help="Choose the theme for visualizations"
        )

        dpi_setting = st.select_slider(
            "Report Quality",
            options=[80, 100, 150, 200, 300],
            value=100,
            help="Higher DPI = better quality but slower generation"
        )

        use_cache = st.checkbox(
            "Use Cached Data",
            value=True,
            help="Load previously extracted data if available"
        )

        st.markdown("---")

        # Generate button
        generate_button = st.button("🔄 Generate Visualization", type="primary")

        st.markdown("---")

        # Help section
        with st.expander("ℹ️ How to find Match IDs"):
            st.markdown("""
            **WhoScored:**
            1. Go to [WhoScored.com](https://www.whoscored.com)
            2. Navigate to a match page
            3. Look at the URL: `whoscored.com/Matches/{ID}/...`
            4. Copy the ID number

            **FotMob:**
            1. Go to [FotMob.com](https://www.fotmob.com)
            2. Navigate to a match page
            3. Look at the URL: `fotmob.com/matches/{ID}/...`
            4. Copy the ID number
            """)

        with st.expander("📊 What's available?"):
            st.markdown("""
            **Full Report:** Complete 12-panel match report with all visualizations

            **Statistics:** Match summary with key stats, possession, xG, shots, etc.

            **Shot Map:** All shots from both teams with xG values and outcomes

            **Pass Network:** Team passing patterns showing player positions and connections

            **Match Momentum:** Timeline showing match flow and team control

            **xG Timeline:** Cumulative expected goals (xG) throughout the match

            **Zone 14 & Half-Spaces:** Key attacking areas analysis for both teams

            **Defensive Actions:** Heatmaps showing tackles, interceptions, and pressure

            **Pitch Control:** Territory control map showing dominant areas

            **Zonal Control:** Grid-based control analysis across the pitch
            """)

    # Main content
    st.title("🏟️ Football Match Report Generator")

    # Introduction
    if not generate_button:
        st.markdown("""
        <div class="match-info">
        <h3>Welcome to PostMatchReport!</h3>
        <p>Generate comprehensive football match reports with advanced visualizations.</p>
        <p><strong>Features:</strong></p>
        <ul>
            <li>12 detailed visualizations per match</li>
            <li>Pass networks and player positioning</li>
            <li>Shot maps with xG data</li>
            <li>Defensive actions and territorial control</li>
            <li>Match momentum analysis</li>
        </ul>
        <p>Enter match IDs in the sidebar and click "Generate Report" to begin.</p>
        </div>
        """, unsafe_allow_html=True)

        # Example section
        st.subheader("📸 Example Reports")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.info("**Pass Network**\nVisualize team passing patterns and player connections")

        with col2:
            st.info("**Shot Map**\nAll shots with xG values and outcomes")

        with col3:
            st.info("**Heat Maps**\nDefensive pressure and pitch control zones")

    # Generate report
    if generate_button:
        if whoscored_id < 1:
            st.error("Please enter a valid WhoScored Match ID")
            return

        # Map visualization options to internal keys
        viz_type_map = {
            "Full Report": "full_report",
            "Statistics": "statistics",
            "Shot Map": "shot_map",
            "Pass Network": "pass_network",
            "Match Momentum": "momentum",
            "xG Timeline": "xg_timeline",
            "Zone 14 & Half-Spaces": "zone14",
            "Defensive Actions": "defensive_actions",
            "Pitch Control": "pitch_control",
            "Zonal Control": "zonal_control"
        }

        selected_viz_type = viz_type_map[viz_option]
        theme = theme_option.lower()

        spinner_text = "🔄 Generating visualization... This may take a few minutes..." if selected_viz_type != "full_report" else "🔄 Generating full match report... This may take a few minutes..."

        with st.spinner(spinner_text):
            try:
                # Generate report or specific visualization
                fotmob_id_value = fotmob_id if fotmob_id > 0 else None

                if selected_viz_type == "full_report":
                    fig, match_summary = generate_report_cached(whoscored_id, fotmob_id_value, theme=theme)
                else:
                    fig, match_summary = generate_specific_visualization(whoscored_id, fotmob_id_value,
                                                                         viz_type=selected_viz_type, theme=theme)

                # Extract data from match_summary
                home_name = match_summary['teams']['home']['name']
                away_name = match_summary['teams']['away']['name']
                score = match_summary['match_info'].get('score', '0:0')
                home_score, away_score = score.split(':') if ':' in score else ('0', '0')
                competition = match_summary['match_info'].get('competition') or {}
                league = competition.get('name', 'N/A')
                date = match_summary['match_info'].get('date', 'N/A')[:10] if match_summary['match_info'].get('date') else 'N/A'
                venue = match_summary['match_info'].get('venue', 'N/A')

                # Display match info
                st.markdown(f"""
                <div class="match-info">
                <h2>⚽ {home_name} {home_score} - {away_score} {away_name}</h2>
                <p><strong>League:</strong> {league} | <strong>Date:</strong> {date}</p>
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

                # Display report with appropriate title
                viz_display_names = {
                    "full_report": "📊 Full Match Report",
                    "statistics": "📈 Match Statistics",
                    "shot_map": "🎯 Shot Map",
                    "pass_network": "🔗 Pass Network",
                    "momentum": "📊 Match Momentum",
                    "xg_timeline": "📈 xG Timeline",
                    "zone14": "⚡ Zone 14 & Half-Spaces",
                    "defensive_actions": "🛡️ Defensive Actions",
                    "pitch_control": "🗺️ Pitch Control",
                    "zonal_control": "🎯 Zonal Control"
                }

                st.subheader(viz_display_names.get(selected_viz_type, "📊 Match Report"))

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

                viz_filename_suffix = viz_option.replace(' ', '_').replace('&', 'and')
                filename = f"{home_name}_{away_name}_{datetime.now().strftime('%Y%m%d')}_{viz_filename_suffix}.png"
                filename = filename.replace(' ', '_')

                download_label = f"📥 Download {viz_option}" if selected_viz_type != "full_report" else "📥 Download Full Report"
                st.download_button(
                    label=download_label,
                    data=buf,
                    file_name=filename,
                    mime="image/png"
                )

                # Close figure to free memory
                plt.close(fig)

                success_message = f"✅ {viz_option} generated successfully!" if selected_viz_type != "full_report" else "✅ Full report generated successfully!"
                st.success(success_message)

            except Exception as e:
                st.error(f"❌ Error generating report: {str(e)}")
                st.exception(e)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #7f8c8d; padding: 20px;'>
        <p>PostMatchReport | Advanced Football Analytics</p>
        <p>Data from WhoScored & FotMob</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    # Create cache directory
    os.makedirs("./cache", exist_ok=True)

    # Run app
    main()
