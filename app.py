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

from generate_report import MatchReportGenerator
from match_data_processor import MatchDataProcessor
from match_visualizations import create_full_match_report


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
def generate_report_cached(whoscored_id: int, fotmob_id: int = None):
    """
    Generate report with caching.

    Args:
        whoscored_id: WhoScored match ID
        fotmob_id: FotMob match ID

    Returns:
        Matplotlib Figure
    """
    generator = MatchReportGenerator(cache_dir="./cache")

    # Extract data
    whoscored_data, fotmob_data = generator.extract_all_data(
        whoscored_id, fotmob_id, use_cache=True
    )

    # Process data
    processor = MatchDataProcessor(whoscored_data, fotmob_data)
    team_info = processor.get_team_info()

    # Create report
    fig = create_full_match_report(processor, team_info, figsize=(20, 22))

    return fig, team_info


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
            value=1716104,
            help="Enter the WhoScored match ID from the URL"
        )

        fotmob_id = st.number_input(
            "FotMob Match ID (Optional)",
            min_value=0,
            value=0,
            help="Enter the FotMob match ID for enhanced stats (xG, colors, etc.)"
        )

        st.markdown("---")

        # Options
        st.subheader("Options")
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

                fig, team_info = generate_report_cached(whoscored_id, fotmob_id_value)

                # Display match info
                st.markdown(f"""
                <div class="match-info">
                <h2>⚽ {team_info['home']['name']} {team_info['home']['score']} - {team_info['away']['score']} {team_info['away']['name']}</h2>
                <p><strong>League:</strong> {team_info.get('league', 'N/A')} | <strong>Date:</strong> {team_info.get('date', 'N/A')[:10]}</p>
                </div>
                """, unsafe_allow_html=True)

                # Display stats summary
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Possession",
                        f"{team_info['possession']['home_possession']:.0f}% - {team_info['possession']['away_possession']:.0f}%"
                    )

                with col2:
                    st.metric(
                        "xG",
                        f"{team_info['xg']['home_xg']:.2f} - {team_info['xg']['away_xg']:.2f}"
                    )

                with col3:
                    st.metric(
                        "Shots",
                        f"{team_info['shots']['home_shots']} - {team_info['shots']['away_shots']}"
                    )

                with col4:
                    st.metric(
                        "Venue",
                        team_info.get('venue', 'N/A')
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

                filename = f"{team_info['home']['name']}_{team_info['away']['name']}_{datetime.now().strftime('%Y%m%d')}_MatchReport.png"
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
