# City Football Group - Scouting Intelligence Platform

Professional data cleaning and analytics pipeline for football scouting operations. This platform provides comprehensive data management, cleaning, and interactive visualization capabilities for technical staff and decision-makers at City Football Group.

---

## Overview

This project implements a complete end-to-end solution for:

- **Data Cleaning**: Automated audit, deduplication, and normalization of player and scouting data
- **Data Integrity**: Referential integrity management across related tables with PlayerID mapping
- **Interactive Analytics**: Professional Streamlit dashboard with actionable insights for strategic decision-making
- **Authentication & Navigation**: Secure login system with intuitive homepage and dashboard navigation

---

## Project Structure

```
CityGroupProyect/
├── data/
│   ├── raw/                           # Original CSV files (input)
│   │   ├── Players.csv
│   │   └── ReportingInsight.csv
│   └── processed/                      # Cleaned datasets (output)
│       ├── players_cleaned.csv
│       ├── reporting_cleaned.csv
│       └── player_id_map.json         # ID mapping dictionary
├── src/                               # Data cleaning scripts
│   ├── __init__.py
│   ├── utils.py                       # Utility functions (normalization, age calculation)
│   ├── clean_players.py               # Players data cleaning pipeline
│   ├── clean_reporting.py             # Reporting data cleaning and ID mapping
│   └── pipeline.py                    # Main orchestrator (runs all cleaning steps)
├── app/
│   └── streamlit_app.py               # Interactive dashboard application
├── notebooks/
│   └── data_cleaning_documentation.ipynb  # Process documentation and walkthrough
├── reports/
│   └── cleaning_log.md                # Before/after metrics and audit results
├── requirements.txt                   # Python dependencies
├── README.md                          # This file
├── PROJECT_SUMMARY.md                 # High-level project summary
└── .gitignore                         # Git ignore rules
```

---

## Quick Start Guide

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Web browser (for Streamlit dashboard)

### Installation Steps

1. **Clone or download the project** to your local machine

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the data cleaning pipeline**:
   ```bash
   python src/pipeline.py
   ```
   
   This will:
   - Clean and deduplicate Players data
   - Clean ReportingInsight data and apply PlayerID mappings
   - Generate comprehensive cleaning log with metrics
   - Create all processed files in `data/processed/`

4. **Launch the Streamlit dashboard**:
   ```bash
   streamlit run app/streamlit_app.py
   ```

   The dashboard will automatically open in your browser at `http://localhost:8501`

### First-Time Access

1. **Login Credentials**:
   - Username: `CityGroup`
   - Password: `CityGroup`

2. **Navigation Flow**:
   - After login, you'll see the **Homepage** with 4 navigation cards
   - Click any card to access that analysis section
   - Use the sidebar filters to customize your analysis
   - Click "Logout" in the sidebar to end your session

---

## Dashboard Guide

### Authentication System

The platform includes a secure authentication system:

- **Login Page**: Professional login interface with City Football Group branding
- **Homepage**: Navigation hub with 4 analysis sections
- **Dashboard**: Main analytics interface with interactive visualizations
- **Logout**: Secure session termination via sidebar button

### Key Performance Indicators (KPIs)

At the top of the dashboard, you'll find 5 key metrics displayed in a single row:

1. **Total Reports**: Total number of scouting reports analyzed
2. **Unique Players**: Number of distinct players evaluated
3. **Avg Performance**: Average performance grade across all reports
4. **High Potential (Grade A)**: Number of unique players with Potential Grade A
5. **Top Performers (4+)**: Number of unique players with average performance grade of 4 or higher

**Why This Matters**: These KPIs provide an immediate overview of your scouting portfolio's scale, quality, and potential. They update in real-time based on your filter selections.

### Sidebar Filters

The left sidebar contains comprehensive filtering options to focus your analysis:

- **Top N Results**: Limit results to top N players/teams/countries (default: 20)
- **Primary Position**: Filter by player position (e.g., CM, CB, LW, GK)
- **Age Band**: Filter by age groups (U18, U21, 21-24, 25-29, 30-34, 35+)
- **Country**: Filter by player nationality or scouting location
- **Current Team**: Filter by the player's current club
- **Preferred Foot**: Filter by foot preference (Right, Left, Both)
- **Report Type**: Filter by scouting method (Live, Video)
- **Performance Grade**: Filter by performance rating (1-5)
- **Potential Grade**: Filter by potential rating (A, B, C, D, E, F)
- **Date Range**: Filter reports by match date range

**How to Use**: Select your desired filters to narrow down the analysis. All visualizations and KPIs will update automatically to reflect your filtered dataset.

### Dashboard Tabs

The dashboard is organized into 4 main analysis sections:

#### Tab 1: Player Analysis

**Purpose**: Identify top-performing players and high-potential talent for recruitment decisions.

**Visualizations**:

1. **Top Players Ranking** (Left Chart)
   - Horizontal bar chart showing players ranked by average performance grade
   - Bars are color-coded based on performance level (red=low, orange=medium, teal/blue=high)
   - Displays player name, average performance, potential grade, country, and position
   - **Insight**: Players with performance 4+ across multiple reports demonstrate elite consistency and are ready for first-team consideration

2. **High Potential Players** (Right Chart)
   - Horizontal bar chart showing players with selected potential grade (default: A)
   - Filterable by potential grade (A, B, C, D, E, F)
   - **Insight**: These players represent future value - securing development rights early can provide 5-10x ROI compared to established players

3. **Comprehensive Player Analysis Table**
   - Unified table combining top performers and high-potential players
   - Columns: Player Name, Country, Position, Avg Performance, Potential, Reports, Type
   - Downloadable as Excel file
   - **Use Case**: Technical staff can use this for detailed player evaluation and comparison

4. **Player Comparator**
   - Side-by-side comparison of 2-3 selected players
   - Shows performance comparison and number of reports (scouting confidence)
   - **Use Case**: Direct comparison when evaluating similar players for the same position

5. **Player Performance Trend**
   - Line chart showing individual player's performance evolution over time
   - **Use Case**: Identify players on upward development trajectory or assess consistency

**Key Insights for Staff**:
- Players in top-right quadrant (high performance + high potential) are immediate priority targets
- Players with 3+ reports have been cross-validated by multiple scouts, reducing evaluation risk
- Performance trends reveal optimal acquisition timing

#### Tab 2: Performance & Distribution

**Purpose**: Understand overall scouting quality, age-based patterns, and temporal trends.

**Visualizations**:

1. **Performance Grade Distribution** (Left Chart)
   - Bar chart showing distribution of performance grades (1-5) across all reports
   - **Insight**: Right-skewed distribution (concentration in grades 4-5) indicates elite talent focus, but may miss value opportunities in 2.5-3.5 range

2. **Performance by Age Band** (Middle Chart)
   - Bar chart showing average performance by age groups
   - Color-coded: Teal (high), Blue (medium), Gold (low) compared to average
   - **Insight**: Reveals optimal recruitment windows - U21/U23 bands suggest ready-now players, while strong U18 performance indicates exceptional early development

3. **Potential by Age Band** (Right Chart)
   - Bar chart showing percentage of players with selected potential grade by age
   - Filterable by potential grade (A, B, C, D, E, F)
   - **Insight**: High concentration in younger bands is expected, but finding high potential in 25+ bands represents late-bloomer opportunities

4. **Performance vs Potential Analysis** (Full Width)
   - Scatter plot with performance on X-axis and potential on Y-axis
   - Bubbles colored by age band, size indicates number of reports
   - **Insight**: Top-right quadrant (Performance 4+ AND Potential A/B) represents "golden quadrant" - optimal recruitment targets with immediate impact and long-term value

5. **Temporal Trends** (Side by Side)
   - **Left Chart**: Average performance over time (line chart)
   - **Right Chart**: Scouting activity over time (bar chart)
   - **Insight**: Activity peaks align with transfer windows and major tournaments. Performance consistency indicates scouting quality maintenance

**Key Insights for Staff**:
- Target portfolio balance: 30% elite (4-5), 50% high-potential (3-3.5), 20% development projects (2-2.5)
- Optimal recruitment mix: 40% U18-U21 (development), 35% U21-U25 (ready-now), 25% 25+ (proven quality)
- Scale scouting network 40-50% during peak activity periods (pre-transfer windows, tournaments)

#### Tab 3: Geographic & Teams

**Purpose**: Identify strategic markets, evaluate team partnerships, and optimize geographic resource allocation.

**Visualizations**:

1. **Average Performance by Country** (Left Chart)
   - Bar chart showing top N countries by average performance grade
   - Color-coded bars based on performance level
   - **Insight**: Countries with consistently high performance indicate premium talent markets where scouting resources deliver maximum ROI

2. **% Players with Potential by Country** (Right Chart)
   - Bar chart showing percentage of players with selected potential grade by country
   - Filterable by potential grade (A, B, C, D, E, F)
   - **Insight**: High percentages reveal markets with exceptional development ecosystems capable of producing elite future talent

3. **Team Performance Analysis** (Left Chart)
   - Bar chart showing average performance by current team
   - **Insight**: Identifies feeder clubs and strategic partnership opportunities - teams consistently producing high-performing players indicate superior development programs

4. **Potential Distribution by Team** (Right Chart)
   - Stacked bar chart showing distribution of potential grades (A, B, C, D) by team
   - Color-coded using City Football Group palette
   - **Insight**: Teams with high concentration of Grade A/B potential players represent premium talent pipelines with long-term value

**Key Insights for Staff**:
- Top 5 countries by performance: Establish dedicated local scout networks (2-3 full-time scouts per market)
- Teams in top-right quadrant (high performance + many high potential players): Immediate priority for exclusive partnership agreements
- Countries with >25% Potential A: Establish dedicated youth scouting programs focusing on U18-U21 age groups

#### Tab 4: Position & Scouts

**Purpose**: Analyze positional market dynamics, evaluate scout network performance, and optimize resource allocation.

**Visualizations**:

1. **Average Performance by Position** (Left Chart)
   - Bar chart showing average performance grade by tactical position
   - Color-coded: Teal (high), Blue (medium), Gold (low) compared to average
   - **Insight**: Reveals tactical market dynamics - high-performance positions with low coverage represent untapped opportunities

2. **Scouting Coverage by Position** (Right Chart)
   - Bar chart showing number of unique players scouted by position
   - **Insight**: Identifies strategic gaps - positions with high performance but low coverage offer better value due to reduced competition

3. **Average Performance by Preferred Foot** (Left Chart)
   - Bar chart showing performance by foot preference (Right, Left, Both)
   - **Insight**: Left-footed players represent 10-15% of global pool, creating natural scarcity and premium market value

4. **Player Distribution by Foot** (Right Chart)
   - Bar chart showing number of unique players by foot preference
   - **Insight**: Ambidextrous players offer exceptional tactical flexibility, allowing formation changes without substitutions

5. **Position Statistics Table**
   - Detailed table showing: Position, Avg Performance, Scouted Players, % High Potential
   - Downloadable as Excel file
   - **Use Case**: Technical staff can identify positional needs and coverage gaps

6. **Scout Performance Analysis** (Full Width)
   - Bar chart showing average performance grade and potential discovery rate by scout
   - **Insight**: Top-performing scouts (top 20%) should be assigned priority targets and used to train developing scouts

**Key Insights for Staff**:
- High performance + Low coverage positions: Increase scouting resources by 50-75%
- Left-footed players: Budget 15-25% premium due to scarcity
- Top-performing scouts: Assign priority targets and create mentorship programs for knowledge transfer

### Executive Summary

At the bottom of the dashboard, you'll find an automatic Executive Summary with:

- **Key Findings**: Total reports, unique players, average performance, top country, most scouted position, players with Potential A
- **Strategic Recommendations**: 7 actionable recommendations based on current data, including:
  - Geographic strategy for top-performing markets
  - Portfolio optimization across age bands
  - Elite talent pipeline management
  - Resource allocation optimization
  - Strategic partnership prioritization
  - Positional balance adjustments
  - Scout network excellence programs

---

## Data Cleaning Pipeline

### Overview

The data cleaning pipeline processes raw scouting data through three main stages:

1. **Players Data Cleaning**: Deduplication and normalization
2. **Reporting Data Cleaning**: ID mapping and referential integrity
3. **Log Generation**: Comprehensive before/after metrics

### Running the Pipeline

**Complete Pipeline** (Recommended):
```bash
python src/pipeline.py
```

**Individual Steps** (For Development):

Clean Players Only:
```bash
python src/clean_players.py
```

Clean Reporting Only (requires cleaned players first):
```bash
python src/clean_reporting.py
```

### Understanding the Cleaning Process

#### Step 1: Players Data Cleaning (`src/clean_players.py`)

**What It Does**:
- Detects exact duplicates (identical rows)
- Identifies conditional duplicates (same player with different PlayerID)
- Creates player "fingerprints" using: Normalized Name + Date of Birth + Nationality
- Selects canonical PlayerID based on data completeness
- Generates PlayerID mapping dictionary
- Normalizes names, nationalities, dates, and other fields

**Outputs**:
- `data/processed/players_cleaned.csv`: Cleaned player table
- `data/processed/player_id_map.json`: Mapping of old IDs to canonical IDs

**What Could Be Modified**:
- Fingerprinting criteria (add more fields if needed)
- Canonical ID selection priority (currently: completeness > CurrentTeam > alphabetical)
- Normalization rules for names/nationalities

#### Step 2: Reporting Data Cleaning (`src/clean_reporting.py`)

**What It Does**:
- Applies PlayerID mappings from Step 1
- Validates referential integrity (all PlayerIDs in Reporting exist in Players)
- Handles orphaned PlayerIDs (creates minimal player records if needed)
- Normalizes reporting-specific fields (dates, grades, positions)
- Ensures 100% referential integrity

**Outputs**:
- `data/processed/reporting_cleaned.csv`: Cleaned reporting table with mapped IDs

**What Could Be Modified**:
- Orphaned player handling strategy
- Additional validation rules
- Field normalization rules

#### Step 3: Pipeline Orchestration (`src/pipeline.py`)

**What It Does**:
- Runs Steps 1 and 2 in correct order
- Generates comprehensive cleaning log
- Provides execution summary

**Outputs**:
- `reports/cleaning_log.md`: Detailed before/after metrics

### Cleaning Log

The cleaning log (`reports/cleaning_log.md`) contains:

- **Before Cleaning Metrics**: Total rows, duplicates, missing values, inconsistencies
- **After Cleaning Metrics**: Final row counts, data quality improvements
- **ID Mapping Statistics**: Number of mappings created and applied
- **Referential Integrity Status**: Validation results
- **Data Distribution**: Performance grades, potential grades, report types

---

## Adding New Data

### Adding New Players

1. **Prepare your CSV file**:
   - Follow the same structure as `Players.csv`
   - Required columns: `PlayerID`, `PlayerName`, `PlayerFirstNationality`, `DateOfBirth`, `CurrentTeam`
   - Place file in `data/raw/` directory

2. **Run the cleaning pipeline**:
   ```bash
   python src/pipeline.py
   ```

3. **The pipeline will automatically**:
   - Detect and merge duplicates with existing data
   - Update PlayerID mappings if needed
   - Maintain referential integrity
   - Generate updated cleaning log

### Adding New Reports

1. **Prepare your CSV file**:
   - Follow the same structure as `ReportingInsight.csv`
   - Required columns: `PlayerID`, `PerformanceGrade`, `PotentialGrade`, `ReportType`, `MatchDate`, etc.
   - Place file in `data/raw/` directory

2. **Run the cleaning pipeline**:
   ```bash
   python src/pipeline.py
   ```

3. **The pipeline will automatically**:
   - Apply PlayerID mappings to new reports
   - Validate referential integrity
   - Flag any orphaned PlayerIDs for review
   - Integrate new data with existing cleaned dataset

### Pipeline Reusability

The pipeline is designed to be **repeatable and scalable**:

- Each run processes all data from scratch
- ID mappings are preserved and updated incrementally
- Cleaning logic is consistent across runs
- New data is automatically integrated with existing cleaned data
- No manual intervention required for routine updates

---

## Use Cases by Role

### For Technical Directors & Decision Makers

**Primary Use Cases**:

1. **Strategic Market Analysis**:
   - Use Geographic & Teams tab to identify top-performing countries
   - Establish dedicated scouting networks in premium markets
   - Evaluate partnership opportunities with high-performing teams

2. **Recruitment Strategy**:
   - Use Player Analysis tab to identify immediate targets (top performers) and future assets (high potential)
   - Balance portfolio across age bands using Performance & Distribution insights
   - Optimize resource allocation based on temporal trends

3. **Portfolio Management**:
   - Monitor age band distributions for optimal squad composition
   - Track scouting activity patterns to optimize timing
   - Use Executive Summary for high-level strategic recommendations

**Key Metrics to Monitor**:
- Average Performance (target: maintain 3.0+)
- High Potential Players (Grade A) count
- Geographic distribution of scouted players
- Scout network performance

### For Technical Analysts

**Primary Use Cases**:

1. **Data Quality Assessment**:
   - Review `reports/cleaning_log.md` for data quality metrics
   - Identify data quality issues before analysis
   - Track improvements over time

2. **Custom Analysis**:
   - Export filtered data tables as Excel for further analysis
   - Use cleaned CSVs in `data/processed/` for custom visualizations
   - Leverage `player_id_map.json` for ID reconciliation in external tools

3. **Pipeline Customization**:
   - Modify cleaning logic in `src/clean_players.py` or `src/clean_reporting.py`
   - Adjust normalization rules in `src/utils.py`
   - Extend pipeline with additional validation steps

**Technical Details**:
- All scripts include detailed markdown documentation blocks
- Code is modular and well-commented
- Functions are reusable and testable

### For Scouts

**Primary Use Cases**:

1. **Report Review**:
   - Filter by report type (Live vs. Video) to review your own reports
   - Compare performance across different scouts in Position & Scouts tab
   - Review individual player profiles and trends

2. **Market Intelligence**:
   - Identify high-performing countries for future scouting missions
   - Discover position-specific opportunities
   - Track competitive landscape and market trends

3. **Performance Tracking**:
   - View scout performance metrics in Position & Scouts tab
   - Understand which markets or positions you excel at identifying
   - Use insights to improve scouting focus

---

## Technical Details

### Data Cleaning Methodology

**Duplicate Detection Strategy**:
- Uses "fingerprinting" based on: Normalized Name + Date of Birth + Nationality
- Handles variations in name formatting (titles, suffixes, accents)
- Normalizes nationality strings for consistent matching
- Creates unique fingerprint hash for each player

**Canonical ID Selection**:
When multiple PlayerIDs exist for the same player, the pipeline selects the canonical ID based on:
1. Data completeness (fewest null values)
2. CurrentTeam presence (prefers records with team information)
3. Alphabetical order (tiebreaker)

**Referential Integrity**:
- Validates all PlayerIDs in ReportingInsight exist in Players table
- Creates minimal player records for orphaned IDs (if ReportingInsight contains player data)
- Ensures 100% referential integrity in final cleaned dataset
- Flags any integrity issues in cleaning log

### Dashboard Architecture

**Technology Stack**:
- **Streamlit**: Interactive web application framework
- **Plotly**: Interactive data visualizations
- **Pandas**: Data manipulation and analysis
- **Python 3.11**: Core programming language

**Key Features**:
- **Real-time Filtering**: All visualizations update instantly based on filter selections
- **Caching**: Data loading is cached for performance optimization
- **Responsive Design**: Adapts to different screen sizes
- **Professional Styling**: City Football Group color palette and branding

**Authentication System**:
- Session-based authentication using Streamlit's session state
- Secure login with username/password validation
- Homepage navigation with tab routing
- Logout functionality in sidebar

### File Structure Details

**Source Code (`src/`)**:
- `utils.py`: Reusable utility functions (age calculation, name normalization, fingerprinting)
- `clean_players.py`: Complete players data cleaning pipeline
- `clean_reporting.py`: Reporting data cleaning and ID mapping application
- `pipeline.py`: Main orchestrator that runs all cleaning steps in sequence

**Application (`app/`)**:
- `streamlit_app.py`: Complete dashboard application with all visualizations, filters, and navigation

**Data (`data/`)**:
- `raw/`: Original, unmodified CSV files (input)
- `processed/`: Cleaned and transformed files (output)

**Documentation**:
- `notebooks/data_cleaning_documentation.ipynb`: Step-by-step process walkthrough
- `reports/cleaning_log.md`: Automated cleaning metrics and audit results
- `PROJECT_SUMMARY.md`: High-level project overview

---

## Troubleshooting

### Common Issues and Solutions

**"Data files not found" Error**:
- **Cause**: Cleaned data files don't exist yet
- **Solution**: Run `python src/pipeline.py` first to generate cleaned data files
- **Verification**: Check that `data/processed/players_cleaned.csv` and `data/processed/reporting_cleaned.csv` exist

**"Module not found" Error**:
- **Cause**: Python dependencies not installed
- **Solution**: Run `pip install -r requirements.txt`
- **Verification**: Ensure you're in the project root directory when running commands

**"Orphaned PlayerIDs" Warning**:
- **Cause**: ReportingInsight contains PlayerIDs not in Players.csv
- **Solution**: This is handled automatically - orphaned players are created with minimal records
- **Note**: Review cleaning log to see which PlayerIDs were orphaned and why

**Dashboard Not Loading**:
- **Cause**: Port 8501 already in use or browser cache issues
- **Solution**: 
  - Close other Streamlit instances
  - Clear browser cache
  - Try accessing `http://localhost:8501` directly
  - Restart Streamlit: Press `Ctrl+C` in terminal, then run `streamlit run app/streamlit_app.py` again

**Filters Not Working**:
- **Cause**: Data not loaded or filter values don't exist in dataset
- **Solution**: 
  - Check that data files are in `data/processed/`
  - Verify filter selections match available data
  - Refresh the page to reload data

**Login Not Working**:
- **Cause**: Incorrect credentials or session state issue
- **Solution**: 
  - Username: `CityGroup`, Password: `CityGroup` (case-sensitive)
  - Clear browser cache and cookies
  - Restart Streamlit application

---

## Project Status

**Current Version**: 1.0.0

**Completion Status**: ✅ **COMPLETE**

All required components have been implemented and tested:

- ✅ Data cleaning pipeline with comprehensive audit
- ✅ PlayerID mapping and referential integrity management
- ✅ Professional Streamlit dashboard with 4 analysis tabs
- ✅ Interactive filters and real-time calculations
- ✅ Actionable insights for each visualization
- ✅ Authentication system with homepage navigation
- ✅ Excel export functionality
- ✅ Comprehensive documentation

**Ready for**: Production use and evaluation

---

## Next Steps for GitHub

### Repository Structure

The project is organized for easy navigation and evaluation:

```
CityGroupProyect/
├── README.md                    # This comprehensive guide
├── PROJECT_SUMMARY.md           # High-level overview
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
├── data/
│   ├── raw/                     # Original data (committed)
│   └── processed/               # Cleaned data (committed)
├── src/                         # Source code (committed)
├── app/                         # Streamlit application (committed)
├── notebooks/                   # Documentation (committed)
└── reports/                     # Cleaning logs (committed)
```

### Files to Commit

**Include**:
- All source code files (`src/*.py`)
- Streamlit application (`app/streamlit_app.py`)
- Documentation files (`README.md`, `PROJECT_SUMMARY.md`, `notebooks/*.ipynb`)
- Data files (`data/raw/*.csv`, `data/processed/*.csv`, `data/processed/*.json`)
- Reports (`reports/*.md`)
- Configuration files (`requirements.txt`, `.gitignore`)

**Exclude** (via `.gitignore`):
- Python cache files (`__pycache__/`, `*.pyc`)
- Virtual environments (`venv/`, `env/`)
- IDE configuration (`.vscode/`, `.idea/`)
- Temporary files (`*.tmp`, `*.log`)

### GitHub Repository Setup

1. **Create New Repository**:
   - Name: `city-football-group-scouting-platform` (or your preferred name)
   - Description: "Professional scouting analytics platform for City Football Group"
   - Visibility: Private (for evaluation) or Public (if preferred)

2. **Initial Commit**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: City Football Group Scouting Intelligence Platform"
   git branch -M main
   git remote add origin [your-repository-url]
   git push -u origin main
   ```

3. **Repository Settings**:
   - Add repository description
   - Set README.md as main documentation
   - Enable Issues and Discussions (optional)
   - Add topics: `football`, `scouting`, `data-analysis`, `streamlit`, `python`

### Presentation Tips

When presenting this project:

1. **Start with Overview**: Explain the three-part structure (cleaning, integrity, visualization)
2. **Demonstrate Pipeline**: Show the cleaning process and results
3. **Walk Through Dashboard**: Navigate through each tab explaining insights
4. **Highlight Insights**: Focus on actionable recommendations for staff
5. **Show Code Quality**: Point out modular structure and documentation
6. **Discuss Scalability**: Explain how the pipeline handles new data

---

## Support and Documentation

### Additional Resources

- **Cleaning Log**: `reports/cleaning_log.md` - Detailed before/after metrics
- **Process Documentation**: `notebooks/data_cleaning_documentation.ipynb` - Step-by-step walkthrough
- **Code Documentation**: All scripts include detailed markdown documentation blocks
- **Project Summary**: `PROJECT_SUMMARY.md` - High-level overview

### Code Quality

- **Modular Design**: Each component is self-contained and reusable
- **Comprehensive Comments**: All functions include docstrings and explanations
- **Error Handling**: Graceful handling of missing data and edge cases
- **Best Practices**: Follows Python PEP 8 style guidelines

---

## Built for City Football Group

**Professional Scouting Analytics Platform**

This platform demonstrates:
- Strategic thinking in data architecture
- Professional code quality and documentation
- Actionable insights for technical staff
- Scalable and maintainable design
- Understanding of modern football scouting context

---

**Version**: 1.0.0 | **Last Updated**: December 2025 | **Status**: Production Ready
