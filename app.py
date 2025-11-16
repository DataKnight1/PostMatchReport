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

from Reporting.report_generator import ReportGenerator
from ETL.transformers.match_processor import MatchProcessor


# Page configuration
st.set_page_config(
    page_title="PostMatchReport",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Black & White Minimalist Design
st.markdown("""
    <style>
    /* Global Styles */
    .main {
        background-color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
        color: #000000;
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
        border-radius: 4px;
    }

    .stButton>button:hover {
        background-color: #333333;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    /* Inputs */
    .stNumberInput input,
    .stTextInput input,
    .stSelectbox select {
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 0.5rem;
        background-color: #ffffff;
    }

    .stNumberInput input:focus,
    .stTextInput input:focus,
    .stSelectbox select:focus {
        border-color: #000000;
        box-shadow: 0 0 0 1px #000000;
        outline: none;
    }

    /* Checkbox */
    .stCheckbox {
        color: #333333;
    }

    /* Cards/Panels */
    .match-info {
        background-color: #fafafa;
        border: 1px solid #e0e0e0;
        padding: 2rem;
        margin: 2rem 0;
        border-radius: 4px;
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
        border-radius: 4px;
    }

    .streamlit-expanderHeader:hover {
        background-color: #f5f5f5;
    }

    /* Info boxes */
    .stAlert {
        background-color: #fafafa;
        border: 1px solid #e0e0e0;
        color: #333333;
        border-radius: 4px;
    }

    /* Download button */
    .stDownloadButton>button {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #000000;
        font-weight: 600;
    }

    .stDownloadButton>button:hover {
        background-color: #000000;
        color: #ffffff;
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

        # Options
        st.subheader("Options")

        theme_option = st.selectbox(
            "Report Theme",
            options=["Dark", "Light", "Monochrome"],
            index=0,
            help="Choose visualization theme (Monochrome = black & white)"
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
        generate_button = st.button("🔄 Generate Report", type="primary")

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

        with st.expander("📊 What's in the report?"):
            st.markdown("""
            The report includes 12 visualizations:
            1. Match Summary Statistics
            2. Shot Map
            3. Match Momentum Graph
            4. Pass Networks (both teams)
            5. Key Passes & Assists
            6. Zone 14 & Half-Spaces (both teams)
            7. Penalty Box Entries
            8. Defensive Actions Heatmaps (both teams)
            9. Pitch Control Map
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

        with st.spinner("🔄 Generating match report... This may take a few minutes..."):
            try:
                # Generate report
                fotmob_id_value = fotmob_id if fotmob_id > 0 else None
                theme_value = theme_option.lower()

                fig, match_summary = generate_report_cached(whoscored_id, fotmob_id_value, theme=theme_value)

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

                # Display report
                st.subheader("📊 Match Report")

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
                fig.savefig(buf, format='png', dpi=dpi_setting, bbox_inches='tight', facecolor='#f0f0f0')
                buf.seek(0)

                filename = f"{home_name}_{away_name}_{datetime.now().strftime('%Y%m%d')}_MatchReport.png"
                filename = filename.replace(' ', '_')

                st.download_button(
                    label="📥 Download Report",
                    data=buf,
                    file_name=filename,
                    mime="image/png"
                )

                # Close figure to free memory
                plt.close(fig)

                st.success("✅ Report generated successfully!")

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
