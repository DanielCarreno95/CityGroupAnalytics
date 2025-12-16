"""
City Football Group - Professional Scouting Intelligence Platform

World-class scouting analytics dashboard for technical staff and decision-makers.
Delivers actionable insights for strategic player evaluation and recruitment.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from datetime import datetime
import sys
import io
from io import BytesIO

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# ===========================================
# PAGE CONFIGURATION
# ===========================================
st.set_page_config(
    page_title="CFG Scouting Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===========================================
# AUTHENTICATION CONFIGURATION
# ===========================================
VALID_USERNAME = "CityGroup"
VALID_PASSWORD = "CityGroup"

# ===========================================
# CITY FOOTBALL GROUP COLOR PALETTE
# ===========================================
CFG_COLORS = {
    'primary': '#5CABE8',      # Sky blue
    'secondary': '#1E3A5F',    # Dark blue
    'accent': '#FFFFFF',       # White
    'success': '#00D4AA',      # Teal
    'warning': '#FFB800',      # Gold
    'danger': '#E63946',       # Red
    'background': '#FFFFFF',   # White background
    'text': '#1E3A5F',         # Dark blue text
    'text_secondary': '#2C3E50', # Dark gray
    'light_gray': '#F5F7FA',   # Light gray
    'border': '#E1E8ED',       # Border gray
    'grid': '#E8ECF0'          # Grid color
}

# ===========================================
# CUSTOM CSS - PROFESSIONAL WHITE DESIGN
# ===========================================
st.markdown(f"""
<style>
    /* Main background - WHITE */
    .main {{
        background-color: {CFG_COLORS['background']} !important;
    }}
    
    /* All text dark and visible */
    h1, h2, h3, h4, h5, h6, p, div, span, label {{
        color: {CFG_COLORS['text']} !important;
    }}
    
    /* Header styling */
    h1 {{
        color: {CFG_COLORS['secondary']} !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.02em !important;
    }}
    
    h2 {{
        color: {CFG_COLORS['primary']} !important;
        font-weight: 600 !important;
        font-size: 1.75rem !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        border-bottom: 2px solid {CFG_COLORS['primary']} !important;
        padding-bottom: 0.5rem !important;
    }}
    
    h3 {{
        color: {CFG_COLORS['secondary']} !important;
        font-weight: 600 !important;
        font-size: 1.3rem !important;
    }}
    
    /* KPI Cards - Professional Design */
    [data-testid="stMetricValue"] {{
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: {CFG_COLORS['secondary']} !important;
    }}
    
    [data-testid="stMetricLabel"] {{
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: {CFG_COLORS['text']} !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }}
    
    [data-testid="stMetricDelta"] {{
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        color: {CFG_COLORS['text']} !important;
    }}
    
    /* Metric containers */
    div[data-testid="stMetricContainer"] {{
        background: {CFG_COLORS['accent']} !important;
        padding: 1.5rem !important;
        border-radius: 8px !important;
        border: 2px solid {CFG_COLORS['border']} !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        margin-bottom: 1rem !important;
    }}
    
    /* Info boxes - visible text */
    .stInfo, .stSuccess, .stWarning {{
        background-color: {CFG_COLORS['light_gray']} !important;
        border-left: 4px solid {CFG_COLORS['primary']} !important;
        border-radius: 6px !important;
        padding: 1rem !important;
        color: {CFG_COLORS['text']} !important;
    }}
    
    .stSuccess {{
        border-left-color: {CFG_COLORS['success']} !important;
        background-color: #E6F7F4 !important;
    }}
    
    .stWarning {{
        border-left-color: {CFG_COLORS['warning']} !important;
        background-color: #FFF8E6 !important;
    }}
    
    /* Captions */
    .stCaption {{
        color: {CFG_COLORS['text_secondary']} !important;
        font-size: 0.9rem !important;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {CFG_COLORS['light_gray']} !important;
    }}
    
    /* Sidebar text */
    [data-testid="stSidebar"] * {{
        color: {CFG_COLORS['text']} !important;
    }}
    
    /* Remove default Streamlit styling */
    .stApp {{
        background-color: {CFG_COLORS['background']} !important;
    }}
    
    /* Table styling */
    .dataframe {{
        color: {CFG_COLORS['text']} !important;
    }}
</style>
""", unsafe_allow_html=True)


# ===========================================
# DATA LOADING
# ===========================================
@st.cache_data
def load_data():
    """Load cleaned datasets with caching."""
    BASE_DIR = Path(__file__).parent.parent
    reporting_path = BASE_DIR / "data" / "processed" / "reporting_cleaned.csv"
    players_path = BASE_DIR / "data" / "processed" / "players_cleaned.csv"
    
    try:
        df_reporting = pd.read_csv(reporting_path)
        df_players = pd.read_csv(players_path)
        
        # Parse dates
        date_cols = ['ReportCreatedOn', 'ReportModifiedOn', 'MatchDate']
        for col in date_cols:
            if col in df_reporting.columns:
                df_reporting[col] = pd.to_datetime(df_reporting[col], format='%d/%m/%Y %H:%M', errors='coerce')
                if df_reporting[col].isna().all():
                    df_reporting[col] = pd.to_datetime(df_reporting[col], format='%d/%m/%Y', errors='coerce')
        
        # Merge with players data to get CurrentTeam
        df_merged = df_reporting.merge(
            df_players[['PlayerID', 'DateOfBirth', 'CurrentTeam']],
            on='PlayerID',
            how='left'
        )
        
        return df_merged, df_players
    except FileNotFoundError as e:
        st.error(f"Data files not found. Please run the cleaning pipeline first: {e}")
        st.stop()


# ===========================================
# HELPER FUNCTIONS
# ===========================================
def get_performance_color(value: float, min_val: float = 1.0, max_val: float = 5.0) -> str:
    """Get color from CFG palette based on performance value."""
    if pd.isna(value):
        return CFG_COLORS['light_gray']
    
    # Normalize value to 0-1 range
    normalized = (value - min_val) / (max_val - min_val)
    normalized = max(0, min(1, normalized))  # Clamp between 0 and 1
    
    # Map to CFG colors: low (danger) -> medium (warning) -> high (success/primary)
    if normalized < 0.33:
        # Low performance - red to gold gradient
        ratio = normalized / 0.33
        return CFG_COLORS['danger']
    elif normalized < 0.66:
        # Medium performance - gold
        return CFG_COLORS['warning']
    else:
        # High performance - teal to blue gradient
        ratio = (normalized - 0.66) / 0.34
        if ratio < 0.5:
            return CFG_COLORS['success']
        else:
            return CFG_COLORS['primary']

def render_performance_color_legend():
    """Render legend explaining performance color coding for bar charts."""
    st.markdown(f"""
    <div style='display: flex; gap: 0.75rem; align-items: center; font-size: 0.85rem; color: {CFG_COLORS['text_secondary']};'>
        <div style='display:flex; align-items:center; gap:0.25rem;'><span style='width:14px;height:14px;background:{CFG_COLORS['danger']};display:inline-block;border:1px solid {CFG_COLORS['border']}'></span> Low</div>
        <div style='display:flex; align-items:center; gap:0.25rem;'><span style='width:14px;height:14px;background:{CFG_COLORS['warning']};display:inline-block;border:1px solid {CFG_COLORS['border']}'></span> Medium</div>
        <div style='display:flex; align-items:center; gap:0.25rem;'><span style='width:14px;height:14px;background:{CFG_COLORS['success']};display:inline-block;border:1px solid {CFG_COLORS['border']}'></span> High</div>
        <div style='display:flex; align-items:center; gap:0.25rem;'><span style='width:14px;height:14px;background:{CFG_COLORS['primary']};display:inline-block;border:1px solid {CFG_COLORS['border']}'></span> Elite</div>
    </div>
    """, unsafe_allow_html=True)


def download_excel(df: pd.DataFrame, filename: str = "scouting_data.xlsx"):
    """Convert DataFrame to Excel and return download button."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    output.seek(0)
    return st.download_button(
        label="Download as Excel",
        data=output.getvalue(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def navigate_to_tab(tab_id: str):
    """Navigate reliably to a dashboard tab using session state and query params."""
    st.session_state['current_page'] = 'dashboard'
    st.session_state['selected_tab'] = tab_id
    st.query_params.update(page='dashboard', tab=tab_id)
    st.rerun()


# ===========================================
def create_filters_sidebar(df: pd.DataFrame):
    """Create professional filters in sidebar with session controls first."""
    # Session controls first
    st.sidebar.markdown("### **SESSION**")
    if st.sidebar.button("**Home**", use_container_width=True, key='home_button'):
        st.session_state['current_page'] = 'home'
        st.query_params.clear()
        st.rerun()
    if st.sidebar.button("**Logout**", use_container_width=True, key='logout_button'):
        st.session_state['authenticated'] = False
        st.session_state['current_page'] = 'login'
        st.query_params.clear()
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### **ANALYSIS FILTERS**")
    
    # Top N filter
    top_n = st.sidebar.number_input("**Top N Results**", min_value=5, max_value=100, value=20, step=5, key='top_n_filter')
    
    # Position filter
    positions = ['All'] + sorted(df['ReportPrimaryPosition'].dropna().unique().tolist())
    selected_position = st.sidebar.selectbox("**Primary Position**", positions, key='pos_filter')
    
    # Age band filter
    age_bands = ['All'] + sorted(df['AgeBand'].dropna().unique().tolist())
    selected_age = st.sidebar.selectbox("**Age Band**", age_bands, key='age_filter')
    
    # Country filter
    countries = ['All'] + sorted(df['Country'].dropna().unique().tolist())
    selected_country = st.sidebar.selectbox("**Country**", countries, key='country_filter')
    
    # Team filter (from CurrentTeam)
    teams = ['All'] + sorted(df['CurrentTeam'].dropna().unique().tolist())
    selected_team = st.sidebar.selectbox("**Current Team**", teams, key='team_filter')
    
    # Foot filter
    feet = ['All'] + sorted(df['ReportFoot'].dropna().unique().tolist())
    selected_foot = st.sidebar.selectbox("**Preferred Foot**", feet, key='foot_filter')
    
    # Report type filter
    report_types = ['All'] + sorted(df['ReportType'].dropna().unique().tolist())
    selected_report_type = st.sidebar.selectbox("**Report Type**", report_types, key='report_filter')
    
    # Performance grade filter
    grades = ['All'] + sorted([str(int(g)) for g in df['PerformanceGrade'].dropna().unique()])
    selected_grade = st.sidebar.selectbox("**Performance Grade**", grades, key='perf_filter')
    
    # Potential grade filter
    pot_grades = ['All'] + sorted(df['PotentialGrade'].dropna().unique().tolist())
    selected_pot_grade = st.sidebar.selectbox("**Potential Grade**", pot_grades, key='pot_filter')
    
    # Date range filter
    if 'MatchDate' in df.columns and df['MatchDate'].notna().any():
        min_date = df['MatchDate'].min().date()
        max_date = df['MatchDate'].max().date()
        date_range = st.sidebar.date_input(
            "**Date Range**",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key='date_filter'
        )
    else:
        date_range = None
    
    # Apply filters
    df_filtered = df.copy()
    
    if selected_position != 'All':
        df_filtered = df_filtered[df_filtered['ReportPrimaryPosition'] == selected_position]
    
    if selected_age != 'All':
        df_filtered = df_filtered[df_filtered['AgeBand'] == selected_age]
    
    if selected_country != 'All':
        df_filtered = df_filtered[df_filtered['Country'] == selected_country]
    
    if selected_team != 'All':
        df_filtered = df_filtered[df_filtered['CurrentTeam'] == selected_team]
    
    if selected_foot != 'All':
        df_filtered = df_filtered[df_filtered['ReportFoot'] == selected_foot]
    
    if selected_report_type != 'All':
        df_filtered = df_filtered[df_filtered['ReportType'] == selected_report_type]
    
    if selected_grade != 'All':
        df_filtered = df_filtered[df_filtered['PerformanceGrade'] == float(selected_grade)]
    
    if selected_pot_grade != 'All':
        df_filtered = df_filtered[df_filtered['PotentialGrade'] == selected_pot_grade]
    
    if date_range and len(date_range) == 2:
        df_filtered = df_filtered[
            (df_filtered['MatchDate'] >= pd.Timestamp(date_range[0])) &
            (df_filtered['MatchDate'] <= pd.Timestamp(date_range[1]))
        ]
    
    return df_filtered, top_n


# ===========================================
# KPI DISPLAY - PROFESSIONAL DESIGN
# ===========================================
def display_kpis(df: pd.DataFrame):
    """Display professional KPI cards with correct calculations in single row layout."""
    total_reports = len(df)
    unique_players = df['PlayerID'].nunique()
    avg_performance = df['PerformanceGrade'].mean()
    high_potential = df[df['PotentialGrade'] == 'A']['PlayerID'].nunique()
    total_players = df['PlayerID'].nunique()
    high_pot_pct = (high_potential / total_players * 100) if total_players > 0 else 0
    top_performers = df[df['PerformanceGrade'] >= 4]['PlayerID'].nunique()
    top_perf_pct = (top_performers / total_players * 100) if total_players > 0 else 0
    
    # Single row: 5 KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("TOTAL REPORTS", f"{total_reports:,}")
    with col2:
        st.metric("UNIQUE PLAYERS", f"{unique_players:,}")
    with col3:
        st.metric("AVG PERFORMANCE", f"{avg_performance:.2f}")
    with col4:
        st.metric("HIGH POTENTIAL (A)", f"{high_potential}", delta=f"{high_pot_pct:.1f}%")
    with col5:
        st.metric("TOP PERFORMERS (4+)", f"{top_performers}", delta=f"{top_perf_pct:.1f}%")


# ===========================================
# VISUALIZATION FUNCTIONS - PROFESSIONAL
# ===========================================
def plot_top_players_ranking(df: pd.DataFrame, top_n: int = 20):
    """Plot top players by average performance with professional design."""
    # Calculate average performance per player
    player_stats = df.groupby(['PlayerID', 'PlayerName', 'Country', 'ReportPrimaryPosition']).agg({
        'PerformanceGrade': 'mean',
        'PotentialGrade': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'N/A',
        'ReportID': 'count'
    }).reset_index()
    player_stats.columns = ['PlayerID', 'PlayerName', 'Country', 'Position', 'AvgPerformance', 'Potential', 'ReportCount']
    
    player_stats = player_stats.sort_values('AvgPerformance', ascending=False).head(top_n)
    
    # Create color array based on performance
    colors = [get_performance_color(val) for val in player_stats['AvgPerformance']]
    
    # Create bar chart with visible axes and labels
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=player_stats['AvgPerformance'],
        y=player_stats['PlayerName'],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color=CFG_COLORS['border'], width=1)
        ),
        text=[f"{val:.2f}" for val in player_stats['AvgPerformance']],
        textposition='outside',
        textfont=dict(size=11, color=CFG_COLORS['text'], weight='bold'),
        hovertemplate='<b>%{y}</b><br>Performance: %{x:.2f}<br>Potential: %{customdata[0]}<br>Country: %{customdata[1]}<br>Position: %{customdata[2]}<extra></extra>',
        customdata=player_stats[['Potential', 'Country', 'Position']].values
    ))
    
    fig.update_layout(
        title=dict(
            text=f"<b>TOP {top_n} PLAYERS BY AVERAGE PERFORMANCE</b>",
            x=0.5,
            font=dict(size=16, color=CFG_COLORS['secondary'])
        ),
        xaxis=dict(
            title=dict(text="Average Performance Grade", font=dict(color=CFG_COLORS['text'], size=12)),
            tickfont=dict(color=CFG_COLORS['text'], size=11),
            gridcolor=CFG_COLORS['grid'],
            gridwidth=1,
            showgrid=True,
            zeroline=True,
            zerolinecolor=CFG_COLORS['border'],
            zerolinewidth=1
        ),
        yaxis=dict(
            title=dict(text="", font=dict(color=CFG_COLORS['text'], size=12)),
            tickfont=dict(color=CFG_COLORS['text'], size=10),
            categoryorder='total ascending'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=CFG_COLORS['text'], size=12),
        height=450,
        margin=dict(l=180, r=30, t=60, b=40)
    )
    
    return fig, player_stats


def plot_performance_distribution(df: pd.DataFrame):
    """Plot performance grade distribution with visible axes."""
    perf_dist = df['PerformanceGrade'].value_counts().sort_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=perf_dist.index,
        y=perf_dist.values,
        marker=dict(
            color=perf_dist.values,
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title="Count")
        ),
        text=perf_dist.values,
        textposition='outside',
        textfont=dict(size=12, color=CFG_COLORS['text'], weight='bold'),
        hovertemplate='<b>Grade %{x}</b><br>Count: %{y}<br>Percentage: %{customdata:.1f}%<extra></extra>',
        customdata=(perf_dist.values / len(df) * 100)
    ))
    
    fig.update_layout(
        title=dict(
            text="<b>PERFORMANCE GRADE DISTRIBUTION</b>",
            x=0.5,
            font=dict(size=18, color=CFG_COLORS['secondary'])
        ),
        xaxis=dict(
            title=dict(text="Performance Grade", font=dict(color=CFG_COLORS['text'], size=12)),
            tickfont=dict(color=CFG_COLORS['text'], size=11),
            gridcolor=CFG_COLORS['grid'],
            gridwidth=1,
            showgrid=True,
            zeroline=True,
            zerolinecolor=CFG_COLORS['border'],
            zerolinewidth=1
        ),
        yaxis=dict(
            title=dict(text="Number of Reports", font=dict(color=CFG_COLORS['text'], size=12)),
            tickfont=dict(color=CFG_COLORS['text'], size=11),
            gridcolor=CFG_COLORS['grid'],
            gridwidth=1,
            showgrid=True,
            zeroline=True,
            zerolinecolor=CFG_COLORS['border'],
            zerolinewidth=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=CFG_COLORS['text'], size=12),
        height=450,
        margin=dict(l=50, r=30, t=60, b=40)
    )
    
    return fig


def plot_country_performance(df: pd.DataFrame, top_n: int = 15):
    """Plot average performance by country - single chart."""
    country_stats = df.groupby('Country').agg({
        'PerformanceGrade': 'mean',
        'PlayerID': 'nunique'
    }).reset_index()
    
    country_stats.columns = ['Country', 'AvgPerformance', 'UniquePlayers']
    country_stats = country_stats[country_stats['UniquePlayers'] >= 5].sort_values('AvgPerformance', ascending=False).head(top_n)
    
    # Create colors based on performance
    colors_perf = [get_performance_color(val) for val in country_stats['AvgPerformance']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=country_stats['Country'],
        y=country_stats['AvgPerformance'],
        name='Performance',
        marker=dict(color=colors_perf, line=dict(color=CFG_COLORS['border'], width=1)),
        text=[f"{val:.2f}" for val in country_stats['AvgPerformance']],
        textposition='outside',
        textfont=dict(size=10, color=CFG_COLORS['text'], weight='bold'),
        hovertemplate='<b>%{x}</b><br>Performance: %{y:.2f}<br>Players: %{customdata}<extra></extra>',
        customdata=country_stats['UniquePlayers']
    ))
    
    fig.update_layout(
        title=dict(
            text="<b>AVERAGE PERFORMANCE BY COUNTRY</b>",
            x=0.5,
            font=dict(size=16, color=CFG_COLORS['secondary'])
        ),
        xaxis=dict(
            title=dict(text="Country", font=dict(color=CFG_COLORS['text'], size=12)),
            tickangle=45,
            tickfont=dict(color=CFG_COLORS['text'], size=10)
        ),
        yaxis=dict(
            title=dict(text="Performance Grade", font=dict(color=CFG_COLORS['text'], size=12)),
            gridcolor=CFG_COLORS['grid'],
            tickfont=dict(color=CFG_COLORS['text'], size=11),
            showgrid=True,
            zeroline=True,
            zerolinecolor=CFG_COLORS['border']
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=CFG_COLORS['text'], size=12),
        height=450,
        margin=dict(l=50, r=30, t=60, b=40),
        showlegend=False
    )
    
    return fig


def plot_country_potential(df: pd.DataFrame, top_n: int = 15, potential_filter: str = 'A'):
    """Plot % players with potential grade by country - single chart."""
    country_stats = df.groupby('Country').agg({
        'PlayerID': 'nunique'
    }).reset_index()
    
    # Calculate % of unique players with specified potential grade
    high_pot_dict = {}
    for country in country_stats['Country']:
        country_df = df[df['Country'] == country]
        unique_players = country_df['PlayerID'].unique()
        players_with_grade = country_df[country_df['PotentialGrade'] == potential_filter]['PlayerID'].unique()
        if len(unique_players) > 0:
            high_pot_dict[country] = (len(players_with_grade) / len(unique_players)) * 100
        else:
            high_pot_dict[country] = 0
    
    country_stats['PotentialPct'] = country_stats['Country'].map(high_pot_dict)
    country_stats.columns = ['Country', 'UniquePlayers', 'PotentialPct']
    country_stats = country_stats[country_stats['UniquePlayers'] >= 5].sort_values('PotentialPct', ascending=False).head(top_n)
    
    # Color based on value (high/medium/low)
    avg_pct = country_stats['PotentialPct'].mean()
    colors = []
    for val in country_stats['PotentialPct']:
        if val >= avg_pct * 1.5:
            colors.append(CFG_COLORS['success'])  # High - teal
        elif val >= avg_pct * 0.5:
            colors.append(CFG_COLORS['primary'])   # Medium - blue
        else:
            colors.append(CFG_COLORS['warning'])   # Low - orange
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=country_stats['Country'],
        y=country_stats['PotentialPct'],
        name=f'Potential {potential_filter}',
        marker=dict(color=colors, line=dict(color=CFG_COLORS['border'], width=1)),
        text=[f"{val:.2f}%" for val in country_stats['PotentialPct']],
        textposition='outside',
        textfont=dict(size=10, color=CFG_COLORS['text'], weight='bold'),
        hovertemplate='<b>%{x}</b><br>Potential {potential_filter}: %{y:.2f}%<br>Players: %{customdata}<extra></extra>',
        customdata=country_stats['UniquePlayers']
    ))
    
    fig.update_layout(
        title=dict(
            text=f"<b>% PLAYERS WITH POTENTIAL {potential_filter} BY COUNTRY</b>",
            x=0.5,
            font=dict(size=16, color=CFG_COLORS['secondary'])
        ),
        xaxis=dict(
            title=dict(text="Country", font=dict(color=CFG_COLORS['text'], size=12)),
            tickangle=45,
            tickfont=dict(color=CFG_COLORS['text'], size=10)
        ),
        yaxis=dict(
            title=dict(text="Percentage", font=dict(color=CFG_COLORS['text'], size=12)),
            gridcolor=CFG_COLORS['grid'],
            tickfont=dict(color=CFG_COLORS['text'], size=11),
            showgrid=True,
            zeroline=True,
            zerolinecolor=CFG_COLORS['border']
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=CFG_COLORS['text'], size=12),
        height=450,
        margin=dict(l=50, r=30, t=60, b=40),
        showlegend=False
    )
    
    return fig


def plot_position_performance(df: pd.DataFrame):
    """Plot average performance by position - single chart."""
    position_stats = df.groupby('ReportPrimaryPosition').agg({
        'PerformanceGrade': 'mean'
    }).reset_index()
    
    position_stats.columns = ['Position', 'AvgPerformance']
    position_stats = position_stats.sort_values('AvgPerformance', ascending=False)
    
    # Color based on value (high/medium/low)
    avg_perf = position_stats['AvgPerformance'].mean()
    colors = []
    for val in position_stats['AvgPerformance']:
        if val >= avg_perf * 1.05:
            colors.append(CFG_COLORS['success'])  # High - teal
        elif val >= avg_perf * 0.95:
            colors.append(CFG_COLORS['primary'])   # Medium - blue
        else:
            colors.append(CFG_COLORS['warning'])   # Low - gold
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=position_stats['Position'],
        y=position_stats['AvgPerformance'],
        marker=dict(color=colors, line=dict(color=CFG_COLORS['border'], width=1)),
        text=[f"{val:.2f}" for val in position_stats['AvgPerformance']],
        textposition='outside',
        textfont=dict(size=11, color=CFG_COLORS['text'], weight='bold'),
        hovertemplate='<b>%{x}</b><br>Performance: %{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text="<b>AVERAGE PERFORMANCE BY POSITION</b>", x=0.5, font=dict(size=14, color=CFG_COLORS['secondary'])),
        xaxis=dict(title=dict(text="Position", font=dict(color=CFG_COLORS['text'], size=11)), 
                  tickangle=45, tickfont=dict(color=CFG_COLORS['text'], size=10)),
        yaxis=dict(title=dict(text="Performance Grade", font=dict(color=CFG_COLORS['text'], size=11)), 
                  gridcolor=CFG_COLORS['grid'], tickfont=dict(color=CFG_COLORS['text'], size=10),
                  showgrid=True, zeroline=True, zerolinecolor=CFG_COLORS['border']),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=CFG_COLORS['text'], size=12),
        height=450,
        margin=dict(l=50, r=30, t=60, b=40),
        showlegend=False
    )
    
    return fig


def plot_position_coverage(df: pd.DataFrame):
    """Plot scouting coverage by position - single chart."""
    position_stats = df.groupby('ReportPrimaryPosition').agg({
        'PlayerID': 'nunique'
    }).reset_index()
    
    position_stats.columns = ['Position', 'UniquePlayers']
    position_stats = position_stats.sort_values('UniquePlayers', ascending=False)
    
    # Color based on value (high/medium/low)
    avg_players = position_stats['UniquePlayers'].mean()
    colors = []
    for val in position_stats['UniquePlayers']:
        if val >= avg_players * 1.2:
            colors.append(CFG_COLORS['success'])  # High - teal
        elif val >= avg_players * 0.8:
            colors.append(CFG_COLORS['primary'])   # Medium - blue
        else:
            colors.append(CFG_COLORS['warning'])   # Low - gold
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=position_stats['Position'],
        y=position_stats['UniquePlayers'],
        marker=dict(color=colors, line=dict(color=CFG_COLORS['border'], width=1)),
        text=position_stats['UniquePlayers'],
        textposition='outside',
        textfont=dict(size=11, color=CFG_COLORS['text'], weight='bold'),
        hovertemplate='<b>%{x}</b><br>Unique Players: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text="<b>SCOUTING COVERAGE BY POSITION</b>", x=0.5, font=dict(size=14, color=CFG_COLORS['secondary'])),
        xaxis=dict(title=dict(text="Position", font=dict(color=CFG_COLORS['text'], size=11)), 
                  tickangle=45, tickfont=dict(color=CFG_COLORS['text'], size=10)),
        yaxis=dict(title=dict(text="Unique Players", font=dict(color=CFG_COLORS['text'], size=11)), 
                  gridcolor=CFG_COLORS['grid'], tickfont=dict(color=CFG_COLORS['text'], size=10),
                  showgrid=True, zeroline=True, zerolinecolor=CFG_COLORS['border']),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=CFG_COLORS['text'], size=12),
        height=450,
        margin=dict(l=50, r=30, t=60, b=40),
        showlegend=False
    )
    
    return fig


def plot_age_band_performance(df: pd.DataFrame):
    """Plot performance by age band - single chart."""
    age_stats = df.groupby('AgeBand').agg({
        'PerformanceGrade': 'mean'
    }).reset_index()
    
    age_order = ['U18', 'U21', '21-24', '25-29', '30-34', '35+']
    age_stats['AgeBand'] = pd.Categorical(age_stats['AgeBand'], categories=age_order, ordered=True)
    age_stats = age_stats.sort_values('AgeBand')
    
    # Color based on value (high/medium/low)
    avg_perf = age_stats['PerformanceGrade'].mean()
    colors = []
    for val in age_stats['PerformanceGrade']:
        if val >= avg_perf * 1.1:
            colors.append(CFG_COLORS['success'])  # High - teal
        elif val >= avg_perf * 0.9:
            colors.append(CFG_COLORS['primary'])   # Medium - blue
        else:
            colors.append(CFG_COLORS['warning'])   # Low - orange
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=age_stats['AgeBand'],
        y=age_stats['PerformanceGrade'],
        marker=dict(color=colors, line=dict(color=CFG_COLORS['border'], width=1)),
        text=[f"{val:.2f}" for val in age_stats['PerformanceGrade']],
        textposition='outside',
        textfont=dict(size=11, color=CFG_COLORS['text'], weight='bold'),
        hovertemplate='<b>%{x}</b><br>Performance: %{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text="<b>PERFORMANCE BY AGE BAND</b>", x=0.5, font=dict(size=14, color=CFG_COLORS['secondary'])),
        xaxis=dict(title=dict(text="Age Band", font=dict(color=CFG_COLORS['text'], size=11)), tickfont=dict(color=CFG_COLORS['text'], size=10)),
        yaxis=dict(title=dict(text="Performance Grade", font=dict(color=CFG_COLORS['text'], size=11)), 
                  gridcolor=CFG_COLORS['grid'], tickfont=dict(color=CFG_COLORS['text'], size=10),
                  showgrid=True, zeroline=True, zerolinecolor=CFG_COLORS['border']),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=CFG_COLORS['text'], size=12),
        height=450,
        margin=dict(l=50, r=30, t=60, b=40),
        showlegend=False
    )
    
    return fig


def plot_age_band_potential(df: pd.DataFrame, potential_filter: str = 'A'):
    """Plot % players with potential grade by age band - single chart."""
    if potential_filter != 'All':
        df_filtered = df[df['PotentialGrade'] == potential_filter].copy()
    else:
        df_filtered = df.copy()
    
    age_stats = df_filtered.groupby('AgeBand').agg({
        'PlayerID': 'nunique'
    }).reset_index()
    
    age_stats_full = df.groupby('AgeBand').agg({
        'PlayerID': 'nunique'
    }).reset_index()
    age_stats_full.columns = ['AgeBand', 'TotalPlayers']
    
    age_stats = age_stats.merge(age_stats_full, on='AgeBand', how='left')
    age_stats['HighPotentialPct'] = (age_stats['PlayerID'] / age_stats['TotalPlayers'] * 100).fillna(0)
    
    age_order = ['U18', 'U21', '21-24', '25-29', '30-34', '35+']
    age_stats['AgeBand'] = pd.Categorical(age_stats['AgeBand'], categories=age_order, ordered=True)
    age_stats = age_stats.sort_values('AgeBand')
    
    # Color based on value (high/medium/low)
    avg_pct = age_stats['HighPotentialPct'].mean()
    colors = []
    for val in age_stats['HighPotentialPct']:
        if val >= avg_pct * 1.2:
            colors.append(CFG_COLORS['success'])  # High - teal
        elif val >= avg_pct * 0.8:
            colors.append(CFG_COLORS['primary'])   # Medium - blue
        else:
            colors.append(CFG_COLORS['warning'])   # Low - orange
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=age_stats['AgeBand'],
        y=age_stats['HighPotentialPct'],
        marker=dict(color=colors, line=dict(color=CFG_COLORS['border'], width=1)),
        text=[f"{val:.1f}%" for val in age_stats['HighPotentialPct']],
        textposition='outside',
        textfont=dict(size=11, color=CFG_COLORS['text'], weight='bold'),
        hovertemplate='<b>%{x}</b><br>Potential {potential_filter}: %{y:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text=f"<b>% PLAYERS WITH POTENTIAL {potential_filter} BY AGE</b>", x=0.5, font=dict(size=14, color=CFG_COLORS['secondary'])),
        xaxis=dict(title=dict(text="Age Band", font=dict(color=CFG_COLORS['text'], size=11)), tickfont=dict(color=CFG_COLORS['text'], size=10)),
        yaxis=dict(title=dict(text="Percentage", font=dict(color=CFG_COLORS['text'], size=11)), 
                  gridcolor=CFG_COLORS['grid'], tickfont=dict(color=CFG_COLORS['text'], size=10),
                  showgrid=True, zeroline=True, zerolinecolor=CFG_COLORS['border']),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=CFG_COLORS['text'], size=12),
        height=450,
        margin=dict(l=50, r=30, t=60, b=40),
        showlegend=False
    )
    
    return fig


def plot_age_band_coverage(df: pd.DataFrame):
    """Plot unique players by age band - single chart."""
    age_stats = df.groupby('AgeBand').agg({
        'PlayerID': 'nunique'
    }).reset_index()
    
    age_order = ['U18', 'U21', '21-24', '25-29', '30-34', '35+']
    age_stats['AgeBand'] = pd.Categorical(age_stats['AgeBand'], categories=age_order, ordered=True)
    age_stats = age_stats.sort_values('AgeBand')
    
    # Color based on value (high/medium/low)
    avg_players = age_stats['PlayerID'].mean()
    colors = []
    for val in age_stats['PlayerID']:
        if val >= avg_players * 1.2:
            colors.append(CFG_COLORS['success'])  # High - teal
        elif val >= avg_players * 0.8:
            colors.append(CFG_COLORS['primary'])   # Medium - blue
        else:
            colors.append(CFG_COLORS['warning'])   # Low - orange
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=age_stats['AgeBand'],
        y=age_stats['PlayerID'],
        marker=dict(color=colors, line=dict(color=CFG_COLORS['border'], width=1)),
        text=age_stats['PlayerID'],
        textposition='outside',
        textfont=dict(size=11, color=CFG_COLORS['text'], weight='bold'),
        hovertemplate='<b>%{x}</b><br>Unique Players: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text="<b>SCOUTING COVERAGE BY AGE BAND</b>", x=0.5, font=dict(size=14, color=CFG_COLORS['secondary'])),
        xaxis=dict(title=dict(text="Age Band", font=dict(color=CFG_COLORS['text'], size=11)), tickfont=dict(color=CFG_COLORS['text'], size=10)),
        yaxis=dict(title=dict(text="Unique Players", font=dict(color=CFG_COLORS['text'], size=11)), 
                  gridcolor=CFG_COLORS['grid'], tickfont=dict(color=CFG_COLORS['text'], size=10),
                  showgrid=True, zeroline=True, zerolinecolor=CFG_COLORS['border']),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=CFG_COLORS['text'], size=12),
        height=450,
        margin=dict(l=50, r=30, t=60, b=40),
        showlegend=False
    )
    
    return fig


def plot_foot_performance(df: pd.DataFrame):
    """Plot average performance by preferred foot as a pie chart."""
    foot_stats = df.groupby('ReportFoot').agg({
        'PerformanceGrade': 'mean'
    }).reset_index()
    
    foot_stats.columns = ['ReportFoot', 'AvgPerformance']
    foot_stats = foot_stats.sort_values('AvgPerformance', ascending=False)
    
    colors = [CFG_COLORS['primary'], CFG_COLORS['success'], CFG_COLORS['warning']]
    
    fig = go.Figure(go.Pie(
        labels=foot_stats['ReportFoot'],
        values=foot_stats['AvgPerformance'],
        marker=dict(colors=colors[:len(foot_stats)], line=dict(color=CFG_COLORS['border'], width=1)),
        hovertemplate='<b>%{label}</b><br>Avg Performance: %{value:.2f}<extra></extra>',
        textinfo='label+percent',
        textfont=dict(color=CFG_COLORS['text'])
    ))
    
    fig.update_layout(
        title=dict(text="<b>AVERAGE PERFORMANCE BY PREFERRED FOOT</b>", x=0.5, font=dict(size=14, color=CFG_COLORS['secondary'])),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=CFG_COLORS['text'], size=12),
        height=450,
        showlegend=True
    )
    
    return fig


def plot_foot_distribution(df: pd.DataFrame):
    """Plot player distribution by preferred foot as a pie chart."""
    foot_stats = df.groupby('ReportFoot').agg({
        'PlayerID': 'nunique'
    }).reset_index()
    
    foot_stats.columns = ['ReportFoot', 'UniquePlayers']
    foot_stats = foot_stats.sort_values('UniquePlayers', ascending=False)
    
    colors = [CFG_COLORS['primary'], CFG_COLORS['success'], CFG_COLORS['warning']]
    
    fig = go.Figure(go.Pie(
        labels=foot_stats['ReportFoot'],
        values=foot_stats['UniquePlayers'],
        marker=dict(colors=colors[:len(foot_stats)], line=dict(color=CFG_COLORS['border'], width=1)),
        hovertemplate='<b>%{label}</b><br>Players: %{value}<extra></extra>',
        textinfo='label+percent',
        textfont=dict(color=CFG_COLORS['text'])
    ))
    
    fig.update_layout(
        title=dict(text="<b>PLAYER DISTRIBUTION BY FOOT</b>", x=0.5, font=dict(size=14, color=CFG_COLORS['secondary'])),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=CFG_COLORS['text'], size=12),
        height=450,
        showlegend=True
    )
    
    return fig


def plot_team_performance(df: pd.DataFrame, top_n: int = 15):
    """Plot team performance analysis with visible axes."""
    # Filter out teams with no name
    df_teams = df[df['CurrentTeam'].notna() & (df['CurrentTeam'] != '')].copy()
    
    if len(df_teams) == 0:
        st.warning("No team data available for analysis.")
        return
    
    # Calculate High Potential correctly: % of unique players with Potential A
    team_stats = df_teams.groupby('CurrentTeam').agg({
        'PerformanceGrade': 'mean',
        'PlayerID': 'nunique'
    }).reset_index()
    
    # Calculate % of unique players with Potential A - FIXED
    high_pot_dict = {}
    for team in team_stats['CurrentTeam']:
        team_df = df_teams[df_teams['CurrentTeam'] == team]
        # Get unique players for this team
        unique_players_list = team_df['PlayerID'].unique()
        unique_players_count = len(unique_players_list)
        
        # Get unique players with Potential A for this team
        players_with_a_df = team_df[team_df['PotentialGrade'] == 'A']
        players_with_a_list = players_with_a_df['PlayerID'].unique()
        players_with_a_count = len(players_with_a_list)
        
        if unique_players_count > 0:
            high_pot_dict[team] = (players_with_a_count / unique_players_count) * 100
        else:
            high_pot_dict[team] = 0
    
    team_stats['HighPotentialPct'] = team_stats['CurrentTeam'].map(high_pot_dict)
    team_stats.columns = ['Team', 'AvgPerformance', 'UniquePlayers', 'HighPotentialPct']
    team_stats = team_stats[team_stats['UniquePlayers'] >= 3].sort_values('AvgPerformance', ascending=False).head(top_n)
    
    # Create colors based on performance
    colors_perf = [get_performance_color(val) for val in team_stats['AvgPerformance']]
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Average Performance by Team', '% High Potential Players by Team'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    fig.add_trace(
        go.Bar(
            x=team_stats['Team'],
            y=team_stats['AvgPerformance'],
            name='Performance',
            marker=dict(color=colors_perf, line=dict(color=CFG_COLORS['border'], width=1)),
            text=[f"{val:.2f}" for val in team_stats['AvgPerformance']],
            textposition='outside',
            textfont=dict(size=9, color=CFG_COLORS['text'], weight='bold'),
            hovertemplate='<b>%{x}</b><br>Performance: %{y:.2f}<br>Players: %{customdata}<extra></extra>',
            customdata=team_stats['UniquePlayers']
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=team_stats['Team'],
            y=team_stats['HighPotentialPct'],
            name='High Potential',
            marker_color=CFG_COLORS['success'],
            text=[f"{val:.2f}%" for val in team_stats['HighPotentialPct']],
            textposition='outside',
            textfont=dict(size=9, color=CFG_COLORS['text']),
            hovertemplate='<b>%{x}</b><br>High Potential: %{y:.2f}%<extra></extra>'
        ),
        row=1, col=2
    )
    
    fig.update_xaxes(
        tickangle=45, 
        row=1, col=1,
        tickfont=dict(color=CFG_COLORS['text'], size=9),
        title=dict(font=dict(color=CFG_COLORS['text'], size=11))
    )
    fig.update_xaxes(
        tickangle=45, 
        row=1, col=2,
        tickfont=dict(color=CFG_COLORS['text'], size=9),
        title=dict(font=dict(color=CFG_COLORS['text'], size=11))
    )
    fig.update_yaxes(
        title=dict(text="Performance Grade", font=dict(color=CFG_COLORS['text'], size=12)), 
        row=1, col=1, 
        gridcolor=CFG_COLORS['grid'],
        tickfont=dict(color=CFG_COLORS['text'], size=11),
        showgrid=True,
        zeroline=True,
        zerolinecolor=CFG_COLORS['border']
    )
    fig.update_yaxes(
        title=dict(text="Percentage", font=dict(color=CFG_COLORS['text'], size=12)), 
        row=1, col=2, 
        gridcolor=CFG_COLORS['grid'],
        tickfont=dict(color=CFG_COLORS['text'], size=11),
        showgrid=True,
        zeroline=True,
        zerolinecolor=CFG_COLORS['border']
    )
    
    fig.update_layout(
        title=dict(
            text="<b>TEAM PERFORMANCE ANALYSIS</b>",
            x=0.5,
            font=dict(size=18, color=CFG_COLORS['secondary'])
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=CFG_COLORS['text'], size=12),
        height=500,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.warning("""
    **STRATEGIC INSIGHT:** Team performance analysis identifies feeder clubs and strategic partnership opportunities. Clubs consistently producing 
    high-performing players indicate superior development programs, competitive environments, or tactical systems that develop players effectively. 
    These relationships can provide first-option rights, loan pathways, and preferential access to emerging talent.
    
    **ACTION PLAN:** 1) Top 10 teams by average performance: Initiate formal partnership discussions (loan agreements, first-option clauses, 
    development partnerships), 2) Establish regular communication channels with technical directors of high-performing clubs, 3) Create loan-to-buy 
    pathways for promising players from these clubs, 4) Offer CFG academy integration opportunities as value proposition, 5) Monitor these clubs 
    quarterly for emerging talent, 6) Consider investment or ownership stakes in clubs showing exceptional development track records, 7) Develop 
    reciprocal scouting networks: share insights in exchange for priority access to their talent pool.
    """)


def plot_scatter_performance_vs_potential(df: pd.DataFrame):
    """Plot scatter chart: Performance vs Potential with age bands."""
    # Create player-level aggregation
    player_stats = df.groupby(['PlayerID', 'PlayerName', 'AgeBand', 'Country', 'ReportPrimaryPosition']).agg({
        'PerformanceGrade': 'mean',
        'PotentialGrade': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'N/A',
        'ReportID': 'count'
    }).reset_index()
    player_stats.columns = ['PlayerID', 'PlayerName', 'AgeBand', 'Country', 'Position', 'AvgPerformance', 'Potential', 'ReportCount']
    
    # Map potential grades to numbers for visualization
    potential_map = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1, 'F': 0, 'U': 0, 'UJ': 0, 'N/A': 0}
    player_stats['PotentialNum'] = player_stats['Potential'].map(potential_map)
    
    # Filter out N/A
    player_stats = player_stats[player_stats['Potential'] != 'N/A']
    
    fig = go.Figure()
    
    # Color by age band
    age_bands = player_stats['AgeBand'].unique()
    colors_map = {
        'U18': CFG_COLORS['success'],
        'U21': CFG_COLORS['primary'],
        '21-24': CFG_COLORS['warning'],
        '25-29': CFG_COLORS['secondary'],
        '30-34': CFG_COLORS['text_secondary'],
        '35+': CFG_COLORS['danger']
    }
    
    for age_band in age_bands:
        age_data = player_stats[player_stats['AgeBand'] == age_band]
        if len(age_data) == 0:
            continue
        fig.add_trace(go.Scatter(
            x=age_data['AvgPerformance'],
            y=age_data['PotentialNum'],
            mode='markers',
            name=age_band,
            marker=dict(
                size=age_data['ReportCount'] * 2 + 12,
                color=colors_map.get(age_band, CFG_COLORS['primary']),
                opacity=0.8,
                line=dict(width=2, color=CFG_COLORS['border']),
                sizemode='diameter'
            ),
            text=age_data['PlayerName'],
            hovertemplate='<b>%{text}</b><br>Performance: %{x:.2f}<br>Potential: %{customdata[0]}<br>Age: %{customdata[1]}<br>Position: %{customdata[2]}<br>Reports: %{customdata[3]}<extra></extra>',
            customdata=age_data[['Potential', 'AgeBand', 'Position', 'ReportCount']].values
        ))
    
    fig.update_layout(
        title=dict(
            text="<b>PERFORMANCE vs POTENTIAL ANALYSIS</b>",
            x=0.5,
            font=dict(size=16, color=CFG_COLORS['secondary'])
        ),
        xaxis=dict(
            title=dict(text="Average Performance Grade", font=dict(color=CFG_COLORS['text'], size=12)),
            tickfont=dict(color=CFG_COLORS['text'], size=11),
            gridcolor=CFG_COLORS['grid'],
            showgrid=True,
            zeroline=True,
            zerolinecolor=CFG_COLORS['border']
        ),
        yaxis=dict(
            title=dict(text="Potential Grade", font=dict(color=CFG_COLORS['text'], size=12)),
            tickfont=dict(color=CFG_COLORS['text'], size=11),
            tickmode='array',
            tickvals=[0, 1, 2, 3, 4, 5],
            ticktext=['F/U', 'E', 'D', 'C', 'B', 'A'],
            gridcolor=CFG_COLORS['grid'],
            showgrid=True,
            zeroline=True,
            zerolinecolor=CFG_COLORS['border']
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=CFG_COLORS['text'], size=12),
        height=450,
        margin=dict(l=50, r=30, t=60, b=40),
        legend=dict(
            title=dict(text="Age Band", font=dict(color=CFG_COLORS['text'], size=11)),
            font=dict(color=CFG_COLORS['text'], size=10)
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.success("""
    **STRATEGIC INSIGHT:** This analysis identifies the "golden quadrant" - players combining elite current performance with exceptional 
    development ceiling. Players in the top-right quadrant (Performance 4+ AND Potential A/B) represent the optimal recruitment targets: 
    immediate competitive impact with long-term value appreciation. Bubble size reflects scouting confidence through multiple evaluations.
    
    **ACTION PLAN:** 1) Top-right quadrant (High Perf + High Pot): Immediate priority targets - initiate transfer discussions within 30 days, 
    2) Top-left (High Perf + Lower Pot): Proven quality for immediate needs - assess contract situation and market value, 3) Bottom-right 
    (Lower Perf + High Pot): Development projects - evaluate loan-to-buy or academy integration pathways, 4) Large bubbles (5+ reports): 
    High confidence targets - proceed to contract negotiations, 5) Small bubbles (1-2 reports): Require additional scouting validation before 
    commitment, 6) Cross-reference with age bands: U21 players in top-right quadrant are premium assets with 10+ year value horizon.
    """)


def plot_high_potential_players(df: pd.DataFrame, top_n: int = 20, potential_filter: str = 'A'):
    """Plot players with specified potential grade."""
    # Get all players with specified potential grade
    high_pot_players = df[df['PotentialGrade'] == potential_filter].groupby(['PlayerID', 'PlayerName', 'Country', 'ReportPrimaryPosition', 'AgeBand']).agg({
        'PerformanceGrade': ['mean', 'count'],
        'PotentialGrade': 'first'
    }).reset_index()
    high_pot_players.columns = ['PlayerID', 'PlayerName', 'Country', 'Position', 'AgeBand', 'AvgPerformance', 'ReportCount', 'Potential']
    
    high_pot_players = high_pot_players.sort_values('AvgPerformance', ascending=False).head(top_n)
    
    if len(high_pot_players) == 0:
        st.warning(f"No players with Potential {potential_filter} found in the filtered dataset.")
        # Return empty figure and empty dataframe to prevent unpacking error
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title=dict(
                text=f"<b>HIGH POTENTIAL PLAYERS (Grade {potential_filter}) - TOP {top_n}</b>",
                x=0.5,
                font=dict(size=14, color=CFG_COLORS['secondary'])
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=450
        )
        empty_df = pd.DataFrame(columns=['PlayerID', 'PlayerName', 'Country', 'Position', 'AgeBand', 'AvgPerformance', 'ReportCount', 'Potential'])
        return empty_fig, empty_df
    
    # Create colors based on performance
    colors = [get_performance_color(val) for val in high_pot_players['AvgPerformance']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=high_pot_players['AvgPerformance'],
        y=high_pot_players['PlayerName'],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color=CFG_COLORS['border'], width=1)
        ),
        text=[f"{val:.2f}" for val in high_pot_players['AvgPerformance']],
        textposition='outside',
        textfont=dict(size=11, color=CFG_COLORS['text'], weight='bold'),
        hovertemplate='<b>%{y}</b><br>Performance: %{x:.2f}<br>Country: %{customdata[0]}<br>Position: %{customdata[1]}<br>Age: %{customdata[2]}<br>Reports: %{customdata[3]}<extra></extra>',
        customdata=high_pot_players[['Country', 'Position', 'AgeBand', 'ReportCount']].values
    ))
    
    fig.update_layout(
        title=dict(
            text=f"<b>HIGH POTENTIAL PLAYERS (Grade {potential_filter}) - TOP {top_n}</b>",
            x=0.5,
            font=dict(size=14, color=CFG_COLORS['secondary'])
        ),
        xaxis=dict(
            title=dict(text="Average Performance Grade", font=dict(color=CFG_COLORS['text'], size=12)),
            tickfont=dict(color=CFG_COLORS['text'], size=11),
            gridcolor=CFG_COLORS['grid'],
            gridwidth=1,
            showgrid=True,
            zeroline=True,
            zerolinecolor=CFG_COLORS['border'],
            zerolinewidth=1
        ),
        yaxis=dict(
            title=dict(text="", font=dict(color=CFG_COLORS['text'], size=12)),
            tickfont=dict(color=CFG_COLORS['text'], size=10),
            categoryorder='total ascending'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=CFG_COLORS['text'], size=12),
        height=450,
        margin=dict(l=180, r=30, t=60, b=40)
    )
    
    return fig, high_pot_players


def plot_player_comparison(df: pd.DataFrame, player_ids: list):
    """Compare 2-3 players side by side with key metrics."""
    if len(player_ids) < 2 or len(player_ids) > 3:
        st.warning("Please select 2 or 3 players to compare.")
        return
    
    comparison_data = []
    for player_id in player_ids:
        player_df = df[df['PlayerID'] == player_id]
        if len(player_df) == 0:
            continue
        
        player_name = player_df['PlayerName'].iloc[0]
        comparison_data.append({
            'Player': player_name,
            'Avg Performance': round(player_df['PerformanceGrade'].mean(), 2),
            'Potential': player_df['PotentialGrade'].mode()[0] if len(player_df['PotentialGrade'].mode()) > 0 else 'N/A',
            'Reports': len(player_df),
            'Country': player_df['Country'].iloc[0],
            'Position': player_df['ReportPrimaryPosition'].mode()[0] if len(player_df['ReportPrimaryPosition'].mode()) > 0 else 'N/A',
            'Age Band': player_df['AgeBand'].mode()[0] if len(player_df['AgeBand'].mode()) > 0 else 'N/A'
        })
    
    if len(comparison_data) < 2:
        st.warning("Not enough data for comparison.")
        return
    
    comp_df = pd.DataFrame(comparison_data)
    
    # Create comparison chart
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Average Performance Comparison', 'Number of Reports'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    colors_comp = [CFG_COLORS['primary'], CFG_COLORS['success'], CFG_COLORS['warning']]
    
    fig.add_trace(
        go.Bar(
            x=comp_df['Player'],
            y=comp_df['Avg Performance'],
            name='Performance',
            marker=dict(color=colors_comp[:len(comp_df)], line=dict(color=CFG_COLORS['border'], width=1)),
            text=[f"{val:.2f}" for val in comp_df['Avg Performance']],
            textposition='outside',
            textfont=dict(size=12, color=CFG_COLORS['text'], weight='bold'),
            hovertemplate='<b>%{x}</b><br>Performance: %{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=comp_df['Player'],
            y=comp_df['Reports'],
            name='Reports',
            marker=dict(color=colors_comp[:len(comp_df)], line=dict(color=CFG_COLORS['border'], width=1)),
            text=comp_df['Reports'],
            textposition='outside',
            textfont=dict(size=12, color=CFG_COLORS['text'], weight='bold'),
            hovertemplate='<b>%{x}</b><br>Reports: %{y}<extra></extra>'
        ),
        row=1, col=2
    )
    
    fig.update_xaxes(tickangle=45, row=1, col=1, tickfont=dict(color=CFG_COLORS['text'], size=11))
    fig.update_xaxes(tickangle=45, row=1, col=2, tickfont=dict(color=CFG_COLORS['text'], size=11))
    fig.update_yaxes(
        title=dict(text="Performance Grade", font=dict(color=CFG_COLORS['text'], size=12)), 
        row=1, col=1, 
        gridcolor=CFG_COLORS['grid'],
        tickfont=dict(color=CFG_COLORS['text'], size=11),
        showgrid=True,
        zeroline=True,
        zerolinecolor=CFG_COLORS['border']
    )
    fig.update_yaxes(
        title=dict(text="Number of Reports", font=dict(color=CFG_COLORS['text'], size=12)), 
        row=1, col=2, 
        gridcolor=CFG_COLORS['grid'],
        tickfont=dict(color=CFG_COLORS['text'], size=11),
        showgrid=True,
        zeroline=True,
        zerolinecolor=CFG_COLORS['border']
    )
    
    fig.update_layout(
        title=dict(
            text="<b>PLAYER COMPARISON</b>",
            x=0.5,
            font=dict(size=18, color=CFG_COLORS['secondary'])
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=CFG_COLORS['text'], size=12),
        height=500,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Comparison table
    st.dataframe(comp_df, use_container_width=True, hide_index=True)
    
    st.info("""
    **STRATEGIC INSIGHT:** Head-to-head player comparison enables data-driven decision-making when evaluating similar profiles for the same 
    squad position. This analysis factors in current match performance, future development potential, and scouting network confidence 
    (validation through multiple reports). Players with 3+ reports have been cross-validated by different scouts, reducing evaluation risk.
    
    **ACTION PLAN:** 1) Higher performance + More reports: Primary target - proven quality with high confidence, proceed to transfer negotiations, 
    2) Higher performance + Fewer reports: Validate with additional scouting sessions before commitment, 3) Lower performance + Higher potential: 
    Assess squad needs - if immediate impact required, prioritize higher performance; if building for future, prioritize potential, 4) Equal 
    performance: Use potential grade and report count as tiebreakers, 5) Consider contract status, market value, and positional fit in final 
    decision, 6) For squad depth positions: Prioritize higher performance; for future starters: Prioritize potential grade.
    """)


def plot_player_trend(df: pd.DataFrame, player_id: str):
    """Plot performance evolution over time for a specific player."""
    player_df = df[df['PlayerID'] == player_id].copy()
    
    if len(player_df) == 0:
        st.warning("Player not found in dataset.")
        return
    
    if 'MatchDate' not in player_df.columns or player_df['MatchDate'].isna().all():
        st.warning("Date data not available for this player.")
        return
    
    player_name = player_df['PlayerName'].iloc[0]
    player_df = player_df[player_df['MatchDate'].notna()].sort_values('MatchDate')
    
    if len(player_df) < 2:
        st.warning("Not enough data points for trend analysis.")
        return
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=player_df['MatchDate'],
        y=player_df['PerformanceGrade'],
        mode='lines+markers',
        name='Performance',
        line=dict(color=CFG_COLORS['primary'], width=3),
        marker=dict(size=10, color=CFG_COLORS['primary']),
        hovertemplate='<b>Date: %{x}</b><br>Performance: %{y}<br>Potential: %{customdata}<extra></extra>',
        customdata=player_df['PotentialGrade']
    ))
    
    # Add average line
    avg_perf = player_df['PerformanceGrade'].mean()
    fig.add_hline(
        y=avg_perf,
        line_dash="dash",
        line_color=CFG_COLORS['danger'],
        line_width=2,
        annotation_text=f"Average: {avg_perf:.2f}",
        annotation_position="right",
        annotation_font=dict(color=CFG_COLORS['text'], size=11)
    )
    
    fig.update_layout(
        title=dict(
            text=f"<b>PERFORMANCE TREND: {player_name}</b>",
            x=0.5,
            font=dict(size=18, color=CFG_COLORS['secondary'])
        ),
        xaxis=dict(
            title=dict(text="Date", font=dict(color=CFG_COLORS['text'], size=12)),
            tickfont=dict(color=CFG_COLORS['text'], size=11),
            gridcolor=CFG_COLORS['grid'],
            showgrid=True
        ),
        yaxis=dict(
            title=dict(text="Performance Grade", font=dict(color=CFG_COLORS['text'], size=12)),
            tickfont=dict(color=CFG_COLORS['text'], size=11),
            gridcolor=CFG_COLORS['grid'],
            showgrid=True,
            zeroline=True,
            zerolinecolor=CFG_COLORS['border']
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=CFG_COLORS['text'], size=12),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.success(f"""
    **STRATEGIC INSIGHT:** Performance trajectory analysis reveals player development patterns and consistency levels critical for recruitment 
    decisions. Upward trends indicate players hitting their development curve at the right time, while downward trends may signal plateau, 
    injury recovery, or tactical mismatch. Consistent high performance ({avg_perf:.2f}+) demonstrates reliability under pressure - essential 
    for competitive environments.
    
    **ACTION PLAN:** 1) Upward trend + High average ({avg_perf:.2f}+): Peak development window - optimal acquisition timing, initiate discussions 
    immediately, 2) Consistent high performance: Reliable squad player - assess for immediate needs or depth, 3) Volatile trends: Investigate 
    causes (tactical changes, injuries, competition level) through additional scouting, 4) Downward trend: Risk assessment required - may 
    represent value opportunity if temporary, 5) Recent performance spike: Validate sustainability with extended observation period, 6) 
    Long-term consistency: Lower risk profile - suitable for clubs prioritizing stability over upside.
    """)




def plot_scout_analysis(df: pd.DataFrame):
    """Analyze which scouts find the best talent."""
    if 'ScoutID' not in df.columns:
        st.warning("Scout data not available.")
        return
    
    scout_stats = df.groupby('ScoutID').agg({
        'PerformanceGrade': 'mean',
        'PlayerID': 'nunique',
        'PotentialGrade': lambda x: (x == 'A').sum() / len(x) * 100 if len(x) > 0 else 0,
        'ReportID': 'count'
    }).reset_index()
    scout_stats.columns = ['ScoutID', 'AvgPerformance', 'UniquePlayers', 'HighPotentialPct', 'TotalReports']
    scout_stats = scout_stats[scout_stats['TotalReports'] >= 5].sort_values('AvgPerformance', ascending=False).head(20)
    
    colors_scout = [get_performance_color(val) for val in scout_stats['AvgPerformance']]
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Average Performance by Scout', 'High Potential Discovery Rate'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    fig.add_trace(
        go.Bar(
            x=scout_stats['ScoutID'],
            y=scout_stats['AvgPerformance'],
            name='Performance',
            marker=dict(color=colors_scout, line=dict(color=CFG_COLORS['border'], width=1)),
            text=[f"{val:.2f}" for val in scout_stats['AvgPerformance']],
            textposition='outside',
            textfont=dict(size=9, color=CFG_COLORS['text'], weight='bold'),
            hovertemplate='<b>%{x}</b><br>Performance: %{y:.2f}<br>Players: %{customdata[0]}<br>Reports: %{customdata[1]}<extra></extra>',
            customdata=scout_stats[['UniquePlayers', 'TotalReports']].values
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=scout_stats['ScoutID'],
            y=scout_stats['HighPotentialPct'],
            name='High Potential',
            marker_color=CFG_COLORS['success'],
            text=[f"{val:.2f}%" for val in scout_stats['HighPotentialPct']],
            textposition='outside',
            textfont=dict(size=9, color=CFG_COLORS['text'], weight='bold'),
            hovertemplate='<b>%{x}</b><br>High Potential: %{y:.2f}%<extra></extra>'
        ),
        row=1, col=2
    )
    
    fig.update_xaxes(tickangle=45, row=1, col=1, tickfont=dict(color=CFG_COLORS['text'], size=9))
    fig.update_xaxes(tickangle=45, row=1, col=2, tickfont=dict(color=CFG_COLORS['text'], size=9))
    fig.update_yaxes(
        title=dict(text="Performance Grade", font=dict(color=CFG_COLORS['text'], size=12)), 
        row=1, col=1, 
        gridcolor=CFG_COLORS['grid'],
        tickfont=dict(color=CFG_COLORS['text'], size=11),
        showgrid=True,
        zeroline=True,
        zerolinecolor=CFG_COLORS['border']
    )
    fig.update_yaxes(
        title=dict(text="Percentage", font=dict(color=CFG_COLORS['text'], size=12)), 
        row=1, col=2, 
        gridcolor=CFG_COLORS['grid'],
        tickfont=dict(color=CFG_COLORS['text'], size=11),
        showgrid=True,
        zeroline=True,
        zerolinecolor=CFG_COLORS['border']
    )
    
    fig.update_layout(
        title=dict(
            text="<b>SCOUT PERFORMANCE ANALYSIS</b>",
            x=0.5,
            font=dict(size=18, color=CFG_COLORS['secondary'])
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=CFG_COLORS['text'], size=12),
        height=500,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.warning("""
    **STRATEGIC INSIGHT:** Scout performance metrics reveal the effectiveness of our scouting network and identify specialists who consistently 
    identify elite talent. Top-performing scouts (high average performance grades + high potential discovery rates) represent our most valuable 
    human capital. Understanding scout expertise by market, position, or age band enables strategic assignment of priority targets.
    
    **ACTION PLAN:** 1) Top 20% scouts: Assign priority transfer targets and high-value prospects, 2) Market specialists: Deploy scouts with 
    proven track records in specific countries/leagues for strategic market penetration, 3) Position experts: Leverage scouts showing expertise 
    in specific positions (e.g., full-backs, creative midfielders) for targeted recruitment, 4) Knowledge transfer: Pair top scouts with developing 
    scouts for mentorship and calibration, 5) Performance-based incentives: Reward scouts with high potential discovery rates (Grade A/B finds), 
    6) Underperforming scouts: Provide additional training and calibration sessions, reassign to different markets if needed, 7) Create scout 
    specialization matrix: Map each scout's strengths (geography, position, age band) for optimal target assignment.
    """)


def plot_team_performance_simple(df: pd.DataFrame, top_n: int = 15):
    """Plot simple team performance analysis - only average performance."""
    df_teams = df[df['CurrentTeam'].notna() & (df['CurrentTeam'] != '')].copy()
    
    if len(df_teams) == 0:
        st.warning("No team data available for analysis.")
        return
    
    team_stats = df_teams.groupby('CurrentTeam').agg({
        'PerformanceGrade': 'mean',
        'PlayerID': 'nunique'
    }).reset_index()
    team_stats.columns = ['Team', 'AvgPerformance', 'UniquePlayers']
    team_stats = team_stats[team_stats['UniquePlayers'] >= 3].sort_values('AvgPerformance', ascending=False).head(top_n)
    
    # Create colors based on performance
    colors_perf = [get_performance_color(val) for val in team_stats['AvgPerformance']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=team_stats['Team'],
        y=team_stats['AvgPerformance'],
        name='Performance',
        marker=dict(color=colors_perf, line=dict(color=CFG_COLORS['border'], width=1)),
        text=[f"{val:.2f}" for val in team_stats['AvgPerformance']],
        textposition='outside',
        textfont=dict(size=10, color=CFG_COLORS['text'], weight='bold'),
        hovertemplate='<b>%{x}</b><br>Performance: %{y:.2f}<br>Players: %{customdata}<extra></extra>',
        customdata=team_stats['UniquePlayers']
    ))
    
    fig.update_layout(
        title=dict(
            text="<b>AVERAGE PERFORMANCE BY TEAM</b>",
            x=0.5,
            font=dict(size=16, color=CFG_COLORS['secondary'])
        ),
        xaxis=dict(
            title=dict(text="Team", font=dict(color=CFG_COLORS['text'], size=12)),
            tickangle=45,
            tickfont=dict(color=CFG_COLORS['text'], size=10),
        ),
        yaxis=dict(
            title=dict(text="Performance Grade", font=dict(color=CFG_COLORS['text'], size=12)),
            tickfont=dict(color=CFG_COLORS['text'], size=11),
            gridcolor=CFG_COLORS['grid'],
            showgrid=True,
            zeroline=True,
            zerolinecolor=CFG_COLORS['border']
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=CFG_COLORS['text'], size=12),
        height=450,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    **WHY THIS MATTERS:** Teams with consistently high-performing players may indicate strong development 
    programs or competitive environments. This helps identify feeder clubs or strategic partnerships.
    
    **RECOMMENDATION:** Consider establishing relationships with top-performing teams. These clubs may 
    produce multiple quality players and represent reliable talent pipelines.
    """)


def plot_team_potential_distribution(df: pd.DataFrame, top_n: int = 15):
    """Plot potential grade distribution (A, B, C, D) by team."""
    df_teams = df[df['CurrentTeam'].notna() & (df['CurrentTeam'] != '')].copy()
    
    if len(df_teams) == 0:
        st.warning("No team data available for analysis.")
        return
    
    # Get top teams by performance
    team_stats = df_teams.groupby('CurrentTeam').agg({
        'PerformanceGrade': 'mean',
        'PlayerID': 'nunique'
    }).reset_index()
    team_stats = team_stats[team_stats['PlayerID'] >= 3].sort_values('PerformanceGrade', ascending=False).head(top_n)
    top_teams = team_stats['CurrentTeam'].tolist()
    
    # Calculate potential distribution for each team
    potential_data = []
    for team in top_teams:
        team_df = df_teams[df_teams['CurrentTeam'] == team]
        unique_players = team_df['PlayerID'].nunique()
        
        for grade in ['A', 'B', 'C', 'D']:
            players_with_grade = team_df[team_df['PotentialGrade'] == grade]['PlayerID'].nunique()
            count = players_with_grade
            potential_data.append({
                'Team': team,
                'Potential': grade,
                'Count': count,
                'Percentage': (count / unique_players * 100) if unique_players > 0 else 0
            })
    
    pot_df = pd.DataFrame(potential_data)
    
    # Create stacked bar chart
    fig = go.Figure()
    
    colors_pot = {
        'A': CFG_COLORS['success'],      # Teal
        'B': CFG_COLORS['primary'],      # Sky blue
        'C': CFG_COLORS['warning'],      # Gold
        'D': CFG_COLORS['text_secondary']  # Dark gray (replacing red)
    }
    
    for grade in ['A', 'B', 'C', 'D']:
        grade_df = pot_df[pot_df['Potential'] == grade]
        fig.add_trace(go.Bar(
            x=grade_df['Team'],
            y=grade_df['Count'],
            name=f'Grade {grade}',
            marker_color=colors_pot[grade],
            hovertemplate='<b>%{x}</b><br>Grade {grade}: %{y} players<br>Percentage: %{customdata:.1f}%<extra></extra>',
            customdata=grade_df['Percentage']
        ))
    
    fig.update_layout(
        title=dict(
            text="<b>POTENTIAL DISTRIBUTION BY TEAM</b>",
            x=0.5,
            font=dict(size=16, color=CFG_COLORS['secondary'])
        ),
        xaxis=dict(
            title=dict(text="Team", font=dict(color=CFG_COLORS['text'], size=12)),
            tickangle=45,
            tickfont=dict(color=CFG_COLORS['text'], size=10)
        ),
        yaxis=dict(
            title=dict(text="Number of Players", font=dict(color=CFG_COLORS['text'], size=12)),
            tickfont=dict(color=CFG_COLORS['text'], size=11),
            gridcolor=CFG_COLORS['grid'],
            showgrid=True,
            zeroline=True,
            zerolinecolor=CFG_COLORS['border']
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=CFG_COLORS['text'], size=12),
        height=450,
        margin=dict(l=50, r=30, t=100, b=40),
        barmode='stack',
        legend=dict(
            title=dict(text="Potential Grade", font=dict(color=CFG_COLORS['text'], size=11)),
            orientation="h",
            yanchor="top",
            y=1.15,
            xanchor="center",
            x=0.5,
            font=dict(color=CFG_COLORS['text'], size=10),
            bgcolor='white',
            bordercolor=CFG_COLORS['border'],
            borderwidth=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.success("""
    **STRATEGIC INSIGHT:** Potential distribution by team reveals which clubs have exceptional development programs capable of nurturing elite 
    talent. Teams with high concentration of Grade A/B potential players demonstrate superior coaching, tactical development, or competitive 
    environments that accelerate player growth. These clubs represent premium talent pipelines with long-term value.
    
    **ACTION PLAN:** 1) Teams with >30% Grade A/B potential: Establish exclusive development partnerships with first-option rights, 2) Create 
    structured loan programs: Send CFG academy players to these clubs for development, receive their top prospects in return, 3) Quarterly 
    monitoring: Assign dedicated scouts to track these clubs' youth systems and emerging talent, 4) Investment opportunities: Evaluate 
    strategic investments or partnerships with clubs showing exceptional development metrics, 5) Knowledge exchange: Offer CFG coaching 
    methodology in exchange for priority access to their talent pipeline, 6) Long-term agreements: Negotiate 3-5 year partnerships with 
    performance-based incentives for talent development, 7) Cross-club integration: Explore opportunities to integrate these clubs into CFG 
    network for shared development pathways.
    """)


def plot_team_scatter(df: pd.DataFrame, top_n: int = 20):
    """Scatter plot: Team performance vs number of high potential players."""
    df_teams = df[df['CurrentTeam'].notna() & (df['CurrentTeam'] != '')].copy()
    
    if len(df_teams) == 0:
        st.warning("No team data available.")
        return
    
    team_stats = df_teams.groupby('CurrentTeam').agg({
        'PerformanceGrade': 'mean',
        'PlayerID': 'nunique'
    }).reset_index()
    
    # Calculate high potential players per team
    high_pot_dict = {}
    for team in team_stats['CurrentTeam']:
        team_df = df_teams[df_teams['CurrentTeam'] == team]
        unique_players = team_df['PlayerID'].nunique()
        players_with_a = team_df[team_df['PotentialGrade'] == 'A']['PlayerID'].nunique()
        high_pot_dict[team] = players_with_a
    
    team_stats['HighPotentialCount'] = team_stats['CurrentTeam'].map(high_pot_dict)
    team_stats = team_stats[team_stats['PlayerID'] >= 3].sort_values('PerformanceGrade', ascending=False).head(top_n)
    
    colors_team = [get_performance_color(val) for val in team_stats['PerformanceGrade']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=team_stats['PerformanceGrade'],
        y=team_stats['HighPotentialCount'],
        mode='markers+text',
        name='Teams',
        marker=dict(
            size=team_stats['PlayerID'] * 2 + 15,
            color=colors_team,
            opacity=0.7,
            line=dict(width=2, color=CFG_COLORS['border'])
        ),
        text=team_stats['CurrentTeam'],
        textposition='top center',
        textfont=dict(size=9, color=CFG_COLORS['text']),
        hovertemplate='<b>%{text}</b><br>Performance: %{x:.2f}<br>High Potential Players: %{y}<br>Total Players: %{customdata}<extra></extra>',
        customdata=team_stats['PlayerID']
    ))
    
    fig.update_layout(
        title=dict(
            text="<b>TEAM ANALYSIS: PERFORMANCE vs HIGH POTENTIAL PLAYERS</b>",
            x=0.5,
            font=dict(size=18, color=CFG_COLORS['secondary'])
        ),
        xaxis=dict(
            title=dict(text="Average Performance Grade", font=dict(color=CFG_COLORS['text'], size=12)),
            tickfont=dict(color=CFG_COLORS['text'], size=11),
            gridcolor=CFG_COLORS['grid'],
            showgrid=True,
            zeroline=True,
            zerolinecolor=CFG_COLORS['border']
        ),
        yaxis=dict(
            title=dict(text="Number of High Potential Players (Grade A)", font=dict(color=CFG_COLORS['text'], size=12)),
            tickfont=dict(color=CFG_COLORS['text'], size=11),
            gridcolor=CFG_COLORS['grid'],
            showgrid=True,
            zeroline=True,
            zerolinecolor=CFG_COLORS['border']
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=CFG_COLORS['text'], size=12),
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.success("""
    **STRATEGIC INSIGHT:** The team scatter analysis identifies the "elite talent factories" - clubs that combine proven current quality with 
    exceptional development capacity. Teams in the top-right quadrant (high average performance + high concentration of elite potential) represent 
    the most valuable strategic partnerships. These clubs consistently produce players ready for immediate impact while maintaining strong 
    development pipelines for future talent.
    
    **ACTION PLAN:** 1) Top-right quadrant teams: Immediate priority for exclusive partnership agreements with multi-year commitments, 2) Establish 
    formal development pathways: Create structured loan-to-buy programs with these clubs, 3) First-option rights: Negotiate preferential access 
    to emerging talent before market competition, 4) Investment evaluation: Assess strategic investment or ownership opportunities in these 
    clubs, 5) Knowledge sharing: Offer CFG technical resources (analytics, coaching, sports science) in exchange for talent pipeline access, 
    6) Cross-network integration: Explore opportunities to integrate these clubs into CFG's global network, 7) Dedicated relationship managers: 
    Assign staff to maintain regular communication and monitor emerging talent, 8) Bubble size consideration: Larger bubbles indicate more 
    comprehensive scouting - validate partnership value through extended observation periods.
    """)


def plot_trend_analysis(df: pd.DataFrame):
    """Plot temporal trends in scouting activity - compact side by side."""
    if 'MatchDate' not in df.columns or df['MatchDate'].isna().all():
        st.warning("Date data not available for temporal analysis.")
        return None, None
    
    df_with_date = df[df['MatchDate'].notna()].copy()
    df_with_date['Month'] = df_with_date['MatchDate'].dt.to_period('M')
    
    monthly_stats = df_with_date.groupby('Month').agg({
        'PerformanceGrade': 'mean',
        'PlayerID': 'nunique',
        'ReportID': 'count'
    }).reset_index()
    monthly_stats['Month'] = monthly_stats['Month'].astype(str)
    
    # Performance trend - line chart
    fig_perf = go.Figure()
    fig_perf.add_trace(go.Scatter(
        x=monthly_stats['Month'],
        y=monthly_stats['PerformanceGrade'],
        mode='lines+markers',
        name='Performance',
        line=dict(color=CFG_COLORS['primary'], width=3),
        marker=dict(size=8, color=CFG_COLORS['primary']),
        hovertemplate='<b>%{x}</b><br>Performance: %{y:.2f}<extra></extra>'
    ))
    
    fig_perf.update_layout(
        title=dict(text="<b>AVERAGE PERFORMANCE OVER TIME</b>", x=0.5, font=dict(size=14, color=CFG_COLORS['secondary'])),
        xaxis=dict(title=dict(text="Month", font=dict(color=CFG_COLORS['text'], size=11)), 
                  tickangle=45, tickfont=dict(color=CFG_COLORS['text'], size=10)),
        yaxis=dict(title=dict(text="Performance Grade", font=dict(color=CFG_COLORS['text'], size=11)), 
                  gridcolor=CFG_COLORS['grid'], tickfont=dict(color=CFG_COLORS['text'], size=10),
                  showgrid=True, zeroline=True, zerolinecolor=CFG_COLORS['border']),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=CFG_COLORS['text'], size=12),
        height=450,
        margin=dict(l=50, r=30, t=60, b=60),
        showlegend=False
    )
    
    # Activity trend - bar chart
    fig_activity = go.Figure()
    fig_activity.add_trace(go.Bar(
        x=monthly_stats['Month'],
        y=monthly_stats['ReportID'],
        name='Reports',
        marker_color=CFG_COLORS['success'],
        text=monthly_stats['ReportID'],
        textposition='outside',
        textfont=dict(size=10, color=CFG_COLORS['text']),
        hovertemplate='<b>%{x}</b><br>Reports: %{y}<extra></extra>'
    ))
    
    fig_activity.update_layout(
        title=dict(text="<b>SCOUTING ACTIVITY OVER TIME</b>", x=0.5, font=dict(size=14, color=CFG_COLORS['secondary'])),
        xaxis=dict(title=dict(text="Month", font=dict(color=CFG_COLORS['text'], size=11)), 
                  tickangle=45, tickfont=dict(color=CFG_COLORS['text'], size=10)),
        yaxis=dict(title=dict(text="Number of Reports", font=dict(color=CFG_COLORS['text'], size=11)), 
                  gridcolor=CFG_COLORS['grid'], tickfont=dict(color=CFG_COLORS['text'], size=10),
                  showgrid=True, zeroline=True, zerolinecolor=CFG_COLORS['border']),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=CFG_COLORS['text'], size=12),
        height=450,
        margin=dict(l=50, r=30, t=60, b=60),
        showlegend=False
    )
    
    return fig_perf, fig_activity


# ===========================================
# HEADER FUNCTION (Reusable)
# ===========================================
def display_header():
    """Display professional header - reusable across pages."""
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1>CITY FOOTBALL GROUP</h1>
        <h2 style='color: #5CABE8; font-size: 1.5rem; font-weight: 400; margin-top: -0.5rem;'>
            Scouting Intelligence Platform
        </h2>
        <p style='color: #6B7280; font-size: 1rem; margin-top: 1rem;'>
            Professional scouting analytics platform for strategic decision-making
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")


# ===========================================
# LOGIN PAGE
# ===========================================
def login_page():
    """Display login page with City Football Group background."""
    # Background image CSS - Using City Football Group colors with football field image
    # Note: Behance URL is a page, not a direct image, so using football field image with CFG color overlay
    st.markdown(f"""
    <style>
        .stApp {{
            background: linear-gradient(rgba(30, 58, 95, 0.90), rgba(92, 171, 232, 0.90)), 
                        url('https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1920&q=80');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .login-container {{
            background-color: rgba(255, 255, 255, 0.95);
            padding: 3rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            max-width: 500px;
            margin: 5rem auto;
        }}
        .login-title {{
            text-align: center;
            color: {CFG_COLORS['secondary']};
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        .login-subtitle {{
            text-align: center;
            color: {CFG_COLORS['primary']};
            font-size: 1.2rem;
            font-weight: 400;
            margin-bottom: 2rem;
        }}
    </style>
    """, unsafe_allow_html=True)
    
    # Login form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="login-container">
            <div class="login-title">CITY FOOTBALL GROUP</div>
            <div class="login-subtitle">Scouting Intelligence Platform</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("**Username**", key="username_input")
            password = st.text_input("**Password**", type="password", key="password_input")
            submit_button = st.form_submit_button("**Login**", use_container_width=True)
            
            if submit_button:
                if username == VALID_USERNAME and password == VALID_PASSWORD:
                    st.session_state['authenticated'] = True
                    st.session_state['current_page'] = 'home'
                    st.rerun()
                else:
                    st.error("Invalid username or password. Please try again.")


# ===========================================
# HOMEPAGE
# ===========================================
def homepage():
    """Display homepage with navigation to tabs."""
    # Background image CSS for homepage
    st.markdown(f"""
    <style>
        .stApp {{
            background: linear-gradient(rgba(30, 58, 95, 0.90), rgba(92, 171, 232, 0.90)), 
                        url('https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1920&q=80');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .homepage-content {{
            background-color: rgba(255, 255, 255, 0.98);
            padding: 2rem;
            border-radius: 10px;
            margin: 1rem 0;
        }}
    </style>
    """, unsafe_allow_html=True)
    
    display_header()
    
    st.markdown("### **DASHBOARD NAVIGATION**")
    st.caption("Select an analysis section to explore")
    
    # Create navigation cards
    tabs_info = [
        {
            'name': 'Player Analysis',
            'description': 'Top performers, high potential players, and comprehensive player comparisons',
            'tab_id': 'player_analysis'
        },
        {
            'name': 'Performance & Distribution',
            'description': 'Performance distributions, age band analysis, and temporal trends',
            'tab_id': 'performance_distribution'
        },
        {
            'name': 'Geographic & Teams',
            'description': 'Country performance analysis, team evaluations, and geographic talent mapping',
            'tab_id': 'geographic_teams'
        },
        {
            'name': 'Position & Scouts',
            'description': 'Position analysis, preferred foot evaluation, and scout performance metrics',
            'tab_id': 'position_scouts'
        }
    ]
    
    # Display navigation cards in 2x2 grid
    col1, col2 = st.columns(2)
    
    for idx, tab_info in enumerate(tabs_info):
        with col1 if idx % 2 == 0 else col2:
            # Create styled card with button
            st.markdown(f"""
            <div style='
                background-color: {CFG_COLORS['light_gray']};
                border: 2px solid {CFG_COLORS['border']};
                border-radius: 8px;
                padding: 1.5rem;
                margin-bottom: 1rem;
            '>
                <h4 style='color: {CFG_COLORS['secondary']}; margin-bottom: 0.5rem;'>{tab_info['name']}</h4>
                <p style='color: {CFG_COLORS['text_secondary']}; font-size: 0.9rem; margin: 0.5rem 0 1rem 0;'>{tab_info['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Navigation button
            if st.button(f"**Access {tab_info['name']}**", key=f"nav_{tab_info['tab_id']}", use_container_width=True):
                navigate_to_tab(tab_info['tab_id'])


# ===========================================
# DASHBOARD PAGE
# ===========================================
def dashboard_page():
    """Display main dashboard with tabs."""
    # UI theming for sidebar and tabs
    st.markdown(f"""
    <style>
    /* Sidebar styling */
    [data-testid="stSidebar"] > div:first-child {{
        background: rgba(92, 171, 232, 0.12);
        border-right: 2px solid {CFG_COLORS['secondary']};
        padding: 1rem;
    }}
    /* Tabs styling */
    .stTabs [data-baseweb="tab"] {{
        font-size: 1rem;
        font-weight: 700;
        padding: 0.75rem 1rem;
        border: 1px solid {CFG_COLORS['secondary']} !important;
        border-bottom: 2px solid {CFG_COLORS['secondary']} !important;
        background: #F5FAFF;
        color: {CFG_COLORS['text_secondary']};
    }}
    .stTabs [aria-selected="true"] {{
        background: white !important;
        color: {CFG_COLORS['primary']} !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    display_header()
    
    # Load data
    df_merged, df_players = load_data()
    
    # Create filters
    df_filtered, top_n = create_filters_sidebar(df_merged)
    
    # Display KPIs
    st.markdown("### **KEY PERFORMANCE INDICATORS**")
    display_kpis(df_filtered)
    st.markdown("---")
    
    # Determine which tab to show based on navigation
    query_params = st.query_params
    selected_tab_id = None
    
    if 'selected_tab' in st.session_state:
        selected_tab_id = st.session_state['selected_tab']
        # Keep it in session state for this render
    elif 'tab' in query_params:
        selected_tab_id = query_params['tab']
        st.session_state['selected_tab'] = selected_tab_id
    
    # Create 4 main tabs with a top-right Home button for quick navigation
    tab_cols = st.columns([5, 1])
    with tab_cols[1]:
        if st.button("Home", key="home_tab_button"):
            st.session_state['current_page'] = 'home'
            st.query_params.clear()
            st.rerun()
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Player Analysis",
        "Performance & Distribution",
        "Geographic & Teams",
        "Position & Scouts"
    ])
    
    # Use JavaScript to select the correct tab based on navigation
    if selected_tab_id:
        tab_mapping = {
            'player_analysis': 0,
            'performance_distribution': 1,
            'geographic_teams': 2,
            'position_scouts': 3
        }
        tab_index = tab_mapping.get(selected_tab_id, 0)
        tab_labels = ["Player Analysis", "Performance & Distribution", "Geographic & Teams", "Position & Scouts"]
        target_label = tab_labels[tab_index] if tab_index < len(tab_labels) else ""
        
        # JavaScript with MutationObserver + retries to reliably click the correct tab
        st.markdown(f"""
        <script>
            (function() {{
                const targetIndex = {tab_index};
                const targetLabel = "{target_label}";
                
                function trySelect() {{
                    const tabs = Array.from(document.querySelectorAll('button[role="tab"], [data-baseweb="tab"]'));
                    if (tabs.length > targetIndex) {{
                        // Prefer label match; fallback to index
                        const byLabel = tabs.find(t => t.innerText.trim() === targetLabel);
                        const tab = byLabel || tabs[targetIndex];
                        if (tab) {{
                            tab.click();
                            return true;
                        }}
                    }}
                    return false;
                }}
                
                // Immediate attempt
                if (!trySelect()) {{
                    // Observe DOM for tabs to appear
                    const observer = new MutationObserver(() => {{
                        if (trySelect()) {{
                            observer.disconnect();
                        }}
                    }});
                    observer.observe(document.body, {{ childList: true, subtree: true }});
                    // Safety timeout after 3s
                    setTimeout(() => observer.disconnect(), 3000);
                }}
            }})();
        </script>
        """, unsafe_allow_html=True)
        
        # Clear selected_tab after using it
        if 'selected_tab' in st.session_state:
            del st.session_state['selected_tab']
    
    # ===========================================
    # TAB 1: PLAYER ANALYSIS
    # ===========================================
    with tab1:
        # Filters row
        col_filter1, col_filter2, col_filter3 = st.columns([2, 1, 1])
        with col_filter1:
            st.markdown("### **TOP PLAYERS ANALYSIS**")
        with col_filter2:
            top_n_chart = st.number_input("**Top N Players**", min_value=5, max_value=100, value=10, step=5, key='top_n_chart')
        with col_filter3:
            pot_filter = st.selectbox("**Potential Grade**", ['A', 'B', 'C', 'D', 'E', 'F'], key='pot_filter_main', index=0)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Two charts side by side
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("#### **TOP PLAYERS RANKING**")
            st.caption("Best average performance in the scouting pool")
            fig_top, player_stats = plot_top_players_ranking(df_filtered, top_n_chart)
            st.plotly_chart(fig_top, use_container_width=True)
            st.markdown("""
            <div style='font-size: 0.85rem; color: #6B7280; padding: 0.5rem; background-color: #F3F4F6; border-radius: 5px; margin-top: 0.5rem;'>
            <strong>Strategic Insight:</strong> These players demonstrate elite-level consistency across multiple match evaluations, indicating 
            they can perform at the highest level week-in, week-out. Performance grades of 4+ across multiple reports suggest players ready 
            for immediate first-team consideration or high-value transfer targets.<br>
            <strong>Action Plan:</strong> 1) Request full 90-minute match footage for comprehensive tactical analysis, 2) Schedule live 
            scouting missions for next 3-5 fixtures to assess consistency, 3) Initiate preliminary discussions with player representatives 
            to gauge market availability and interest, 4) Cross-reference with contract status and release clauses for transfer feasibility.
            </div>
            """, unsafe_allow_html=True)
        
        with col_chart2:
            st.markdown("#### **HIGH POTENTIAL PLAYERS**")
            st.caption(f"Players with potential grade {pot_filter}")
            fig_pot, high_pot_stats = plot_high_potential_players(df_filtered, top_n_chart, pot_filter)
            st.plotly_chart(fig_pot, use_container_width=True)
            st.markdown(f"""
            <div style='font-size: 0.85rem; color: #6B7280; padding: 0.5rem; background-color: #F3F4F6; border-radius: 5px; margin-top: 0.5rem;'>
            <strong>Strategic Insight:</strong> Potential Grade {pot_filter} players represent the future value proposition of our scouting portfolio. 
            These talents have been identified by our scouts as having exceptional development ceiling, regardless of current match performance. 
            In modern football economics, securing development rights early can provide 5-10x return on investment compared to established players.<br>
            <strong>Action Plan:</strong> 1) Prioritize these players for extended scouting periods (minimum 6-8 match observations), 2) Engage 
            with player development programs and academies to understand training methodology, 3) Assess family/agent willingness for early 
            commitment, 4) Evaluate loan-to-buy or development partnership structures with current clubs, 5) For Grade A potential: consider 
            immediate acquisition and integration into CFG academy system for controlled development pathway.
            </div>
            """, unsafe_allow_html=True)
        
        render_performance_color_legend()
        
        st.markdown("---")
        
        # Unified table below both charts
        st.markdown("### **COMPREHENSIVE PLAYER ANALYSIS TABLE**")
        st.caption("Detailed information for technical staff decision-making")
        
        # Merge both datasets for unified table
        player_stats['Type'] = 'Top Performer'
        high_pot_stats['Type'] = f'High Potential ({pot_filter})'
        
        # Prepare unified table with relevant columns for staff
        unified_table = pd.concat([
            player_stats[['PlayerName', 'Country', 'Position', 'AvgPerformance', 'Potential', 'ReportCount', 'Type']].rename(columns={
                'PlayerName': 'Player',
                'AvgPerformance': 'Avg Performance',
                'ReportCount': 'Reports'
            }),
            high_pot_stats[['PlayerName', 'Country', 'Position', 'AvgPerformance', 'Potential', 'ReportCount', 'Type']].rename(columns={
                'PlayerName': 'Player',
                'AvgPerformance': 'Avg Performance',
                'ReportCount': 'Reports'
            })
        ], ignore_index=True)
        
        # Remove duplicates (players that appear in both)
        unified_table = unified_table.drop_duplicates(subset=['Player'], keep='first')
        
        # Add additional useful columns
        for idx, row in unified_table.iterrows():
            player_df = df_filtered[df_filtered['PlayerName'] == row['Player']]
            if len(player_df) > 0:
                unified_table.at[idx, 'Current Team'] = player_df['CurrentTeam'].mode()[0] if len(player_df['CurrentTeam'].mode()) > 0 else 'N/A'
                unified_table.at[idx, 'Age Band'] = player_df['AgeBand'].mode()[0] if len(player_df['AgeBand'].mode()) > 0 else 'N/A'
                unified_table.at[idx, 'Preferred Foot'] = player_df['ReportFoot'].mode()[0] if len(player_df['ReportFoot'].mode()) > 0 else 'N/A'
        
        # Reorder columns for better readability
        unified_table = unified_table[['Player', 'Type', 'Country', 'Position', 'Current Team', 'Age Band', 'Preferred Foot', 
                                       'Avg Performance', 'Potential', 'Reports']]
        
        # Round performance
        unified_table['Avg Performance'] = unified_table['Avg Performance'].round(2)
        
        # Sort by performance
        unified_table = unified_table.sort_values('Avg Performance', ascending=False)
        
        col_table, col_dl = st.columns([3, 1])
        with col_table:
            st.dataframe(unified_table, use_container_width=True, hide_index=True)
        with col_dl:
            st.markdown("<br>", unsafe_allow_html=True)
            download_excel(unified_table, f"comprehensive_players_{datetime.now().strftime('%Y%m%d')}.xlsx")
        
        st.markdown("---")
        
        # Section 3: Player Comparator
        st.markdown("### **PLAYER COMPARATOR**")
        st.caption("Compare 2-3 players side by side to identify best value")
        
        # Get list of players for selection (without IDs)
        available_players = df_filtered.groupby(['PlayerID', 'PlayerName']).agg({
            'PerformanceGrade': 'mean'
        }).reset_index()
        available_players = available_players.sort_values('PerformanceGrade', ascending=False)
        # Create mapping: player name -> player ID
        player_name_to_id = {row['PlayerName']: row['PlayerID'] for _, row in available_players.iterrows()}
        player_options = available_players['PlayerName'].tolist()
        
        col_sel1, col_sel2, col_sel3 = st.columns(3)
        selected_players = []
        with col_sel1:
            p1 = st.selectbox("**Player 1**", ['Select...'] + player_options[:50], key='comp_p1')
            if p1 != 'Select...':
                selected_players.append(player_name_to_id[p1])
        with col_sel2:
            p2 = st.selectbox("**Player 2**", ['Select...'] + player_options[:50], key='comp_p2')
            if p2 != 'Select...':
                selected_players.append(player_name_to_id[p2])
        with col_sel3:
            p3 = st.selectbox("**Player 3 (Optional)**", ['Select...'] + player_options[:50], key='comp_p3')
            if p3 != 'Select...':
                selected_players.append(player_name_to_id[p3])
        
        if len(selected_players) >= 2:
            plot_player_comparison(df_filtered, selected_players)
        
        st.markdown("---")
        
        # Section 4: Player Trend Analysis
        st.markdown("### **PLAYER PERFORMANCE TREND**")
        st.caption("Track individual player performance evolution over time")
        
        # Reuse player options from comparator (without IDs)
        trend_player = st.selectbox("**Select Player for Trend Analysis**", ['Select...'] + player_options[:50], key='trend_player')
        if trend_player != 'Select...':
            trend_player_id = player_name_to_id[trend_player]
            plot_player_trend(df_filtered, trend_player_id)
    
    # ===========================================
    # TAB 2: PERFORMANCE & DISTRIBUTION
    # ===========================================
    with tab2:
        # Row 1: 3 most important charts (3 columns)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### **PERFORMANCE DISTRIBUTION**")
            st.caption("Distribution of performance grades")
            fig_dist = plot_performance_distribution(df_filtered)
            st.plotly_chart(fig_dist, use_container_width=True)
            st.markdown("""
            <div style='font-size: 0.85rem; color: #6B7280; padding: 0.5rem; background-color: #F3F4F6; border-radius: 5px; margin-top: 0.5rem;'>
            <strong>Strategic Insight:</strong> This distribution reflects the quality calibration of our scouting network. A right-skewed distribution 
            (concentration in grades 4-5) indicates our scouts are identifying elite-level talent, which is optimal for a top-tier club. However, 
            this may also suggest we're missing value opportunities in the 2.5-3.5 range where development potential could be higher.<br>
            <strong>Action Plan:</strong> 1) If >60% of reports are grade 4-5: validate scout calibration through cross-scout validation sessions, 
            2) If >40% are grade 1-2: review initial player selection criteria and scout training on identifying development potential, 3) Target 
            a balanced portfolio: 30% elite (4-5), 50% high-potential (3-3.5), 20% development projects (2-2.5), 4) Implement quarterly scout 
            calibration workshops to ensure consistent grading standards across the network.
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### **PERFORMANCE BY AGE BAND**")
            st.caption("Average performance by age groups")
            fig_age_perf = plot_age_band_performance(df_filtered)
            st.plotly_chart(fig_age_perf, use_container_width=True)
            st.markdown("""
            <div style='font-size: 0.85rem; color: #6B7280; padding: 0.5rem; background-color: #F3F4F6; border-radius: 5px; margin-top: 0.5rem;'>
            <strong>Strategic Insight:</strong> Age band performance analysis reveals the optimal recruitment windows for different player profiles. 
            Peak performance in U21/U23 bands suggests players ready for immediate first-team impact, while strong U18 performance indicates 
            exceptional early development. Understanding these patterns helps optimize our recruitment strategy across development stages.<br>
            <strong>Action Plan:</strong> 1) High U18 performance: Prioritize for academy integration or development partnerships, 2) Strong U21/U23 
            bands: Target for immediate squad depth or loan-to-buy structures, 3) Peak 25-29 performance: Focus on proven quality for immediate 
            competitive impact, 4) Balance recruitment: 40% U18-U21 (development), 35% U21-U25 (ready-now), 25% 25+ (proven quality), 5) Adjust 
            scouting calendar to align with key tournaments for each age band (U17 World Cup, U21 Euros, etc.).
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("#### **POTENTIAL BY AGE BAND**")
            st.caption("% players with selected potential")
            pot_grades_chart = ['All', 'A', 'B', 'C', 'D', 'E', 'F']
            selected_pot_chart = st.selectbox("**Potential**", pot_grades_chart, key='pot_filter_chart', index=1, label_visibility="collapsed")
            fig_age_pot = plot_age_band_potential(df_filtered, selected_pot_chart)
            st.plotly_chart(fig_age_pot, use_container_width=True)
            st.markdown(f"""
            <div style='font-size: 0.85rem; color: #6B7280; padding: 0.5rem; background-color: #F3F4F6; border-radius: 5px; margin-top: 0.5rem;'>
            <strong>Strategic Insight:</strong> Potential Grade {selected_pot_chart} concentration by age band identifies the optimal development 
            windows for future talent acquisition. High concentration in younger bands (U18-U21) is expected, but finding Grade {selected_pot_chart} 
            players in older bands (25+) represents exceptional late-bloomer opportunities with lower market competition.<br>
            <strong>Action Plan:</strong> 1) For U18-U21 with high {selected_pot_chart}%: Establish development partnerships or pre-contract agreements, 
            2) For U21-U25 with {selected_pot_chart} potential: Target for controlled development pathways (loans with buy-options), 3) For 25+ with 
            {selected_pot_chart} potential: Immediate value opportunity - assess for squad depth or resale value, 4) Allocate 60% of scouting resources 
            to age bands showing >20% {selected_pot_chart} concentration, 5) Create age-specific development roadmaps for each {selected_pot_chart} 
            player cohort.
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Row 2: Performance vs Potential (full width, centered)
        st.markdown("### **PERFORMANCE vs POTENTIAL ANALYSIS**")
        st.caption("Relationship between performance and potential by age bands")
        plot_scatter_performance_vs_potential(df_filtered)
        
        st.markdown("---")
        
        # Row 3: Temporal Trends (side by side)
        st.markdown("### **TEMPORAL TRENDS ANALYSIS**")
        st.caption("Evolution of average scouting performance and activity over time")
        
        col_trend1, col_trend2 = st.columns(2)
        fig_perf_trend, fig_activity_trend = plot_trend_analysis(df_filtered)
        
        if fig_perf_trend is not None and fig_activity_trend is not None:
            with col_trend1:
                st.plotly_chart(fig_perf_trend, use_container_width=True)
            with col_trend2:
                st.plotly_chart(fig_activity_trend, use_container_width=True)
            
            st.markdown("""
            <div style='font-size: 0.85rem; color: #6B7280; padding: 0.5rem; background-color: #F3F4F6; border-radius: 5px; margin-top: 0.5rem;'>
            <strong>Strategic Insight:</strong> Temporal analysis reveals the rhythm of our scouting operations and identifies optimal windows for 
            talent acquisition. Activity peaks typically align with transfer windows, major tournaments, or key competition phases. Performance 
            trends indicate whether our scouting quality remains consistent throughout the year or fluctuates with activity levels.<br>
            <strong>Action Plan:</strong> 1) Pre-transfer window peaks: Ensure maximum scout deployment 2-3 months before windows open, 2) Tournament 
            periods: Increase scouting presence during U17/U21 World Cups, continental championships for comprehensive talent assessment, 3) 
            Performance consistency: If quality drops during high-activity periods, increase scout training and calibration, 4) Resource allocation: 
            Scale scout network based on identified activity patterns, 5) Off-peak periods: Use for scout training, data analysis, and relationship 
            building with clubs, 6) Seasonal patterns: Adjust scouting calendar to align with competition schedules in target markets, 7) Quality 
            control: Implement performance thresholds - if average grade drops below 3.0 during any period, review scout assignments and criteria.
            </div>
            """, unsafe_allow_html=True)
    
    # ===========================================
    # TAB 3: GEOGRAPHIC & TEAMS
    # ===========================================
    with tab3:
        # Top N filter
        col_filter_top, col_filter_empty = st.columns([1, 4])
        with col_filter_top:
            top_n_geo = st.number_input("**Top N**", min_value=5, max_value=50, value=10, step=5, key='top_n_geo')
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Row 1: Geographic Intelligence (2 columns)
        col_geo1, col_geo2 = st.columns(2)
        
        with col_geo1:
            st.markdown("### **AVERAGE PERFORMANCE BY COUNTRY**")
            st.caption("Comparative analysis of performance by country")
            fig_country_perf = plot_country_performance(df_filtered, top_n_geo)
            st.plotly_chart(fig_country_perf, use_container_width=True)
            render_performance_color_legend()
            st.markdown("""
            <div style='font-size: 0.85rem; color: #6B7280; padding: 0.5rem; background-color: #F3F4F6; border-radius: 5px; margin-top: 0.5rem;'>
            <strong>Strategic Insight:</strong> Geographic performance analysis identifies the world's premium talent markets where our scouting 
            resources deliver maximum ROI. Countries with consistently high average performance grades indicate superior competitive environments, 
            development systems, or tactical sophistication that produces elite-level players. This data drives strategic market prioritization 
            and resource allocation across our global scouting network.<br>
            <strong>Action Plan:</strong> 1) Top 5 countries by performance: Establish dedicated local scout networks with 2-3 full-time scouts 
            per market, 2) Market penetration: Increase scouting frequency in top-performing countries by 40-50%, 3) Local partnerships: 
            Develop relationships with top academies and clubs in these markets for preferential access, 4) Cultural integration: Hire local 
            scouts who understand market dynamics, language, and cultural nuances, 5) Competition analysis: Monitor why these countries produce 
            high-quality players (coaching methodology, competitive structure, development pathways), 6) Investment opportunities: Evaluate 
            establishing CFG academies or partnerships in top-performing markets, 7) Market expansion: If new country shows high performance 
            with low scouting coverage, prioritize resource allocation for market entry.
            </div>
            """, unsafe_allow_html=True)
        
        with col_geo2:
            st.markdown("### **% PLAYERS WITH POTENTIAL BY COUNTRY**")
            st.caption("% players with selected potential grade by country")
            pot_grades_geo = ['A', 'B', 'C', 'D', 'E', 'F']
            selected_pot_geo = st.selectbox("**Potential Grade**", pot_grades_geo, key='pot_filter_geo', index=0, label_visibility="collapsed")
            fig_country_pot = plot_country_potential(df_filtered, top_n_geo, selected_pot_geo)
            st.plotly_chart(fig_country_pot, use_container_width=True)
            st.markdown(f"""
            <div style='font-size: 0.85rem; color: #6B7280; padding: 0.5rem; background-color: #F3F4F6; border-radius: 5px; margin-top: 0.5rem;'>
            <strong>Strategic Insight:</strong> Potential Grade {selected_pot_geo} concentration by country reveals markets with exceptional 
            development ecosystems capable of producing elite future talent. High percentages indicate countries where our scouts consistently 
            identify players with exceptional ceilings, regardless of current performance. These markets represent strategic long-term investments 
            for talent acquisition.<br>
            <strong>Action Plan:</strong> 1) Countries with >25% Potential {selected_pot_geo}: Establish dedicated youth scouting programs focusing 
            on U18-U21 age groups, 2) Early engagement: Develop relationships with academies and youth systems in these markets for pre-contract 
            opportunities, 3) Development partnerships: Create structured pathways for {selected_pot_geo} potential players from these countries 
            to CFG network, 4) Market-specific strategies: For Grade A concentration, prioritize immediate acquisition; for Grade B/C, focus on 
            loan-to-buy structures, 5) Local presence: Consider establishing CFG academy branches or partnerships in top {selected_pot_geo} 
            concentration markets, 6) Competition monitoring: Track which clubs are successfully recruiting from these markets and analyze 
            their strategies, 7) Long-term investment: Countries showing consistent {selected_pot_geo} production warrant multi-year scouting 
            commitments and relationship building.
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Row 2: Team Analysis (2 columns - simplified)
        col_team1, col_team2 = st.columns(2)
        
        with col_team1:
            st.markdown("### **TEAM PERFORMANCE ANALYSIS**")
            st.caption("Average performance by current team")
            plot_team_performance_simple(df_filtered, top_n_geo)
            render_performance_color_legend()
        
        with col_team2:
            st.markdown("### **POTENTIAL DISTRIBUTION BY TEAM**")
            st.caption("Distribution of potential grades (A, B, C, D) by team")
            plot_team_potential_distribution(df_filtered, top_n_geo)
        
        st.markdown("---")
        
        # Country statistics table
        st.markdown("### **COUNTRY STATISTICS**")
        country_list = df_filtered['Country'].unique()
        country_stats_list = []
        for country in country_list:
            country_df = df_filtered[df_filtered['Country'] == country]
            unique_players = country_df['PlayerID'].nunique()
            players_with_a = country_df[country_df['PotentialGrade'] == 'A']['PlayerID'].nunique()
            high_pot_pct = (players_with_a / unique_players * 100) if unique_players > 0 else 0
            country_stats_list.append({
                'Country': country,
                'Avg Performance': round(country_df['PerformanceGrade'].mean(), 2),
                'Scouted Players': unique_players,
                '% High Potential': round(high_pot_pct, 2)
            })
        country_stats = pd.DataFrame(country_stats_list)
        country_stats = country_stats.sort_values('Avg Performance', ascending=False)
        
        col_table3, col_dl3 = st.columns([3, 1])
        with col_table3:
            st.dataframe(country_stats, use_container_width=True, hide_index=True)
        with col_dl3:
            st.markdown("<br>", unsafe_allow_html=True)
            download_excel(country_stats, f"country_stats_{datetime.now().strftime('%Y%m%d')}.xlsx")
    
    # ===========================================
    # TAB 4: POSITION & SCOUTS
    # ===========================================
    with tab4:
        # Row 1: Position Analysis (2 columns)
        col_pos1, col_pos2 = st.columns(2)
        
        with col_pos1:
            st.markdown("#### **AVERAGE PERFORMANCE BY POSITION**")
            st.caption("Performance grade by tactical position")
            fig_pos_perf = plot_position_performance(df_filtered)
            st.plotly_chart(fig_pos_perf, use_container_width=True)
        
        with col_pos2:
            st.markdown("#### **SCOUTING COVERAGE BY POSITION**")
            st.caption("Number of unique players scouted by position")
            fig_pos_cov = plot_position_coverage(df_filtered)
            st.plotly_chart(fig_pos_cov, use_container_width=True)
        
        # Position Analysis conclusions
        st.markdown("""
        <div style='font-size: 0.85rem; color: #6B7280; padding: 0.5rem; background-color: #F3F4F6; border-radius: 5px; margin-top: 0.5rem;'>
        <strong>Strategic Insight:</strong> Positional analysis reveals tactical market dynamics and identifies both premium talent sources and 
        strategic gaps in our scouting coverage. High-performance positions with low coverage represent untapped market opportunities where 
        competition for talent may be lower. Conversely, positions with high coverage but lower performance may indicate oversaturated markets 
        or need for improved selection criteria.<br>
        <strong>Action Plan:</strong> 1) High performance + Low coverage: Immediate opportunity - increase scouting resources by 50-75% for these 
        positions, 2) High performance + High coverage: Competitive markets - focus on early identification and relationship building, 3) Low 
        coverage positions: Strategic gap - assign dedicated scouts to build market presence, 4) Position-specific strategies: For full-backs 
        and wingers showing high performance, prioritize these as they're increasingly valuable in modern football, 5) Squad needs alignment: 
        Cross-reference with first-team positional requirements to prioritize scouting allocation, 6) Market timing: Positions with low coverage 
        may offer better value due to reduced competition, 7) Development focus: High-potential positions with low coverage warrant academy 
        development programs to create internal talent pipeline.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Row 2: Foot Analysis (2 columns)
        col_foot1, col_foot2 = st.columns(2)
        
        with col_foot1:
            st.markdown("#### **AVERAGE PERFORMANCE BY PREFERRED FOOT**")
            st.caption("Performance grade by preferred foot")
            fig_foot_perf = plot_foot_performance(df_filtered)
            st.plotly_chart(fig_foot_perf, use_container_width=True)
        
        with col_foot2:
            st.markdown("#### **PLAYER DISTRIBUTION BY FOOT**")
            st.caption("Number of unique players by preferred foot")
            fig_foot_dist = plot_foot_distribution(df_filtered)
            st.plotly_chart(fig_foot_dist, use_container_width=True)
        
        # Foot Analysis conclusions
        st.markdown("""
        <div style='font-size: 0.85rem; color: #6B7280; padding: 0.5rem; background-color: #F3F4F6; border-radius: 5px; margin-top: 0.5rem;'>
        <strong>Strategic Insight:</strong> Foot preference analysis reveals tactical market dynamics and squad balance opportunities. Left-footed 
        players represent approximately 10-15% of the global player pool, creating natural scarcity and premium market value. Ambidextrous players 
        offer exceptional tactical flexibility, allowing managers to adapt formations and maintain width without substitutions. High-performing 
        left-footed or ambidextrous players are premium assets with reduced market competition.<br>
        <strong>Action Plan:</strong> 1) High-performing left-footed players: Immediate priority targets - scarcity creates premium value and 
        reduced competition, 2) Ambidextrous players with high performance: Exceptional value - prioritize for tactical flexibility and squad 
        depth, 3) Squad balance: Assess current squad's foot distribution - if right-footed heavy, prioritize left-footed targets for balance, 
        4) Position-specific: Left-footed full-backs, wingers, and central defenders are particularly valuable in modern systems requiring width, 
        5) Market premium: Budget 15-25% premium for left-footed players due to scarcity, 6) Development focus: Identify and develop left-footed 
        players early in academy system, 7) Tactical advantage: Ambidextrous players provide managers with formation flexibility - value beyond 
        pure performance metrics.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Row 3: Scout Analysis (full width)
        st.markdown("### **SCOUT PERFORMANCE ANALYSIS**")
        st.caption("Identify which scouts find the best talent")
        plot_scout_analysis(df_filtered)
        
        st.markdown("---")
        
        # Row 4: Position Statistics Table (between Scout Analysis and Executive Summary)
        st.markdown("### **POSITION STATISTICS**")
        position_list = df_filtered['ReportPrimaryPosition'].unique()
        position_stats_list = []
        for position in position_list:
            pos_df = df_filtered[df_filtered['ReportPrimaryPosition'] == position]
            unique_players = pos_df['PlayerID'].nunique()
            players_with_a = pos_df[pos_df['PotentialGrade'] == 'A']['PlayerID'].nunique()
            high_pot_pct = (players_with_a / unique_players * 100) if unique_players > 0 else 0
            position_stats_list.append({
                'Position': position,
                'Avg Performance': round(pos_df['PerformanceGrade'].mean(), 2),
                'Scouted Players': unique_players,
                '% High Potential': round(high_pot_pct, 2)
            })
        position_stats = pd.DataFrame(position_stats_list)
        position_stats = position_stats.sort_values('Avg Performance', ascending=False)
        
        col_table4, col_dl4 = st.columns([3, 1])
        with col_table4:
            st.dataframe(position_stats, use_container_width=True, hide_index=True)
        with col_dl4:
            st.markdown("<br>", unsafe_allow_html=True)
            download_excel(position_stats, f"position_stats_{datetime.now().strftime('%Y%m%d')}.xlsx")
    
    # Executive Summary
    st.markdown("---")
    st.markdown("### **EXECUTIVE SUMMARY**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### **KEY FINDINGS**")
        top_country = df_filtered.groupby('Country')['PerformanceGrade'].mean().idxmax()
        top_position = df_filtered.groupby('ReportPrimaryPosition')['PerformanceGrade'].mean().idxmax()
        high_pot_count = df_filtered[df_filtered['PotentialGrade'] == 'A']['PlayerID'].nunique()
        
        st.markdown(f"""
        - **Total Reports Analyzed**: {len(df_filtered):,}
        - **Unique Players Evaluated**: {df_filtered['PlayerID'].nunique():,}
        - **Average Performance**: {df_filtered['PerformanceGrade'].mean():.2f}
        - **Top Performing Country**: {top_country}
        - **Most Scouted Position**: {top_position}
        - **Players with Potential A**: {high_pot_count}
        """)
    
    with col2:
        st.markdown("#### **STRATEGIC RECOMMENDATIONS**")
        st.markdown(f"""
        1. **Geographic Strategy - {top_country}**: Establish dedicated scouting network (2-3 full-time scouts) in top-performing market. 
           Consider CFG academy partnership or local presence for long-term talent pipeline development.
        
        2. **Portfolio Optimization**: Balance recruitment across age bands - target 40% U18-U21 (development), 35% U21-U25 (ready-now), 
           25% 25+ (proven quality) for optimal squad composition and value appreciation.
        
        3. **Elite Talent Pipeline**: {high_pot_count} Grade A potential players identified - initiate immediate follow-up protocol: 
           extended scouting (6-8 matches), development pathway assessment, and early engagement discussions with representatives.
        
        4. **Resource Allocation**: Optimize scout deployment based on temporal trends - scale network 40-50% during identified peak 
           activity periods (pre-transfer windows, major tournaments) for maximum coverage.
        
        5. **Strategic Partnerships**: Prioritize relationship building with top-performing teams (top 10 by average performance) - 
           negotiate loan-to-buy pathways, first-option rights, and development partnerships for sustainable talent access.
        
        6. **Positional Balance**: Address coverage gaps in high-performing positions - increase scouting resources 50-75% for positions 
           showing high quality but low current coverage to capitalize on market opportunities.
        
        7. **Scout Network Excellence**: Leverage top-performing scouts (top 20%) for priority targets and use their expertise to 
           train developing scouts through mentorship programs, ensuring knowledge transfer and network calibration.
        """)


# ===========================================
# MAIN APPLICATION
# ===========================================
def main():
    """Main application function with authentication and routing."""
    # Check authentication
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    
    # Check current page
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'login'
    
    # Handle query parameters for tab navigation
    query_params = st.query_params
    if 'page' in query_params and query_params['page'] == 'dashboard':
        st.session_state['current_page'] = 'dashboard'
        if 'tab' in query_params:
            st.session_state['selected_tab'] = query_params['tab']
    
    # Route to appropriate page
    if not st.session_state['authenticated']:
        login_page()
        return
    
    if st.session_state['current_page'] == 'home':
        homepage()
        return
    
    # Dashboard page (default after login)
    dashboard_page()


if __name__ == "__main__":
    main()
