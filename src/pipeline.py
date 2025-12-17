"""
Main pipeline orchestrator for the complete data cleaning process.

This script coordinates the execution of both players and reporting data cleaning
pipelines, ensuring proper order and dependency management.
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from clean_players import clean_players_pipeline
from clean_reporting import clean_reporting_pipeline


def run_complete_pipeline():
    """
    Execute the complete data cleaning pipeline.
    
    This function:
    1. Cleans Players data
    2. Cleans Reporting data (depends on Players cleaning)
    3. Generates summary report
    """
    BASE_DIR = Path(__file__).parent.parent
    
    # Define all paths
    paths = {
        'players_raw': BASE_DIR / "data" / "raw" / "Players.csv",
        'reporting_raw': BASE_DIR / "data" / "raw" / "ReportingInsight.csv",
        'players_cleaned': BASE_DIR / "data" / "processed" / "players_cleaned.csv",
        'reporting_cleaned': BASE_DIR / "data" / "processed" / "reporting_cleaned.csv",
        'id_mapping': BASE_DIR / "data" / "processed" / "player_id_map.json",
        'cleaning_log': BASE_DIR / "reports" / "cleaning_log.md"
    }
    
    # Ensure directories exist
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 80)
    print("COMPLETE DATA CLEANING PIPELINE")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Step 1: Clean Players
    print("\n" + "=" * 80)
    print("STEP 1: CLEANING PLAYERS DATA")
    print("=" * 80)
    players_metrics = clean_players_pipeline(
        str(paths['players_raw']),
        str(paths['players_cleaned']),
        str(paths['id_mapping'])
    )
    
    # Step 2: Clean Reporting (depends on Players)
    print("\n" + "=" * 80)
    print("STEP 2: CLEANING REPORTING DATA")
    print("=" * 80)
    reporting_metrics = clean_reporting_pipeline(
        str(paths['reporting_raw']),
        str(paths['players_cleaned']),
        str(paths['id_mapping']),
        str(paths['reporting_cleaned'])
    )
    
    # Generate summary report
    generate_cleaning_log(players_metrics, reporting_metrics, paths['cleaning_log'])
    
    print("\n" + "=" * 80)
    print("PIPELINE COMPLETE")
    print("=" * 80)
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nOutput files:")
    print(f"  - {paths['players_cleaned']}")
    print(f"  - {paths['reporting_cleaned']}")
    print(f"  - {paths['id_mapping']}")
    print(f"  - {paths['cleaning_log']}")


def generate_cleaning_log(players_metrics: dict, reporting_metrics: dict, output_path: Path):
    """
    Generate markdown cleaning log with before/after metrics.
    
    Args:
        players_metrics: Metrics from players cleaning
        reporting_metrics: Metrics from reporting cleaning
        output_path: Path to save markdown log
    """
    log_content = f"""# Data Cleaning Log

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

This document summarizes the data cleaning process for the City Football Group scouting dataset.
The pipeline processed two main datasets: Players and ReportingInsight.

---

## Part 1: Players Data Cleaning

### Before Cleaning

- **Total Rows**: {players_metrics['before']['total_rows']}
- **Exact Duplicates**: {players_metrics['before']['duplicate_rows_exact']}
- **Duplicate PlayerIDs**: {players_metrics['before']['duplicate_player_ids']}
- **Missing PlayerName**: {players_metrics['before']['players_without_name']}
- **Missing DateOfBirth**: {players_metrics['before']['players_without_dob']}
- **Missing Nationality**: {players_metrics['before']['players_without_nationality']}
- **Invalid PlayerID Format**: {players_metrics['before']['invalid_player_ids']}

### After Cleaning

- **Total Rows**: {players_metrics['after']['total_rows']}
- **Exact Duplicates**: {players_metrics['after']['duplicate_rows_exact']}
- **Duplicate PlayerIDs**: {players_metrics['after']['duplicate_player_ids']}
- **Missing PlayerName**: {players_metrics['after']['players_without_name']}
- **Missing DateOfBirth**: {players_metrics['after']['players_without_dob']}
- **Missing Nationality**: {players_metrics['after']['players_without_nationality']}

### Improvements

- **Duplicates Removed**: {players_metrics['duplicates_removed']}
- **PlayerID Mappings Created**: {players_metrics['id_mappings_created']}
- **Data Quality Improvement**: {((players_metrics['before']['total_rows'] - players_metrics['after']['total_rows']) / players_metrics['before']['total_rows'] * 100):.1f}% reduction in rows

### Missing Values (After Cleaning)

"""
    
    # Add missing values breakdown
    for col, count in players_metrics['after']['missing_values'].items():
        pct = players_metrics['after']['missing_percentage'][col]
        log_content += f"- **{col}**: {count} ({pct:.1f}%)\n"
    
    log_content += f"""
---

## Part 2: Reporting Data Cleaning

### Before Cleaning

- **Total Rows**: {reporting_metrics['before']['total_rows']}
- **Unique Players**: {reporting_metrics['before']['unique_players']}
- **Unique Scouts**: {reporting_metrics['before']['unique_scouts']}
- **Unique Countries**: {reporting_metrics['before']['unique_countries']}

### After Cleaning

- **Total Rows**: {reporting_metrics['after']['total_rows']}
- **Unique Players**: {reporting_metrics['after']['unique_players']}
- **Unique Scouts**: {reporting_metrics['after']['unique_scouts']}
- **Unique Countries**: {reporting_metrics['after']['unique_countries']}

### ID Mapping Statistics

- **ID Mappings Applied**: {reporting_metrics['mapping_stats']['mapping_applications']}
- **Unique Old IDs Found**: {reporting_metrics['mapping_stats']['unique_old_ids_found']}
- **Rows with Mapped IDs**: {reporting_metrics['mapping_stats']['rows_with_mapped_ids']}

### Referential Integrity

- **Status**: {reporting_metrics['integrity']['integrity_status']}
- **Orphaned PlayerIDs**: {reporting_metrics['integrity']['orphaned_count']}
- **Orphaned Rows**: {reporting_metrics['integrity']['orphaned_rows']}

"""
    
    if reporting_metrics['integrity']['orphaned_count'] > 0:
        log_content += f"""
**Warning**: {reporting_metrics['integrity']['orphaned_count']} PlayerIDs in ReportingInsight do not exist in the cleaned Players table.
These may represent players that were removed during cleaning or data inconsistencies.

"""
    
    log_content += f"""
### Report Type Distribution

"""
    for report_type, count in reporting_metrics['after']['report_types'].items():
        log_content += f"- **{report_type}**: {count}\n"
    
    log_content += f"""
### Performance Grade Distribution

"""
    for grade, count in reporting_metrics['after']['performance_grades'].items():
        log_content += f"- **Grade {grade}**: {count}\n"
    
    log_content += f"""
### Potential Grade Distribution

"""
    for grade, count in reporting_metrics['after']['potential_grades'].items():
        log_content += f"- **Grade {grade}**: {count}\n"
    
    log_content += f"""
---

## Summary

The data cleaning pipeline successfully:

1. ✅ Removed {players_metrics['duplicates_removed']} duplicate player records
2. ✅ Created {players_metrics['id_mappings_created']} PlayerID mappings for referential integrity
3. ✅ Applied {reporting_metrics['mapping_stats']['mapping_applications']} ID mappings to reporting data
4. ✅ Validated referential integrity between Players and Reporting tables
5. ✅ Normalized and standardized all data fields

The cleaned datasets are now ready for analysis and visualization.

"""
    
    # Write log
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(log_content)
    
    print(f"\n[Log] Generated cleaning log at {output_path}")


if __name__ == "__main__":
    run_complete_pipeline()


