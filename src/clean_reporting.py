"""
# STEP 2: Reporting Data Cleaning & ID Mapping

## Brief Explanation
This script cleans the ReportingInsight.csv dataset and applies PlayerID mappings
from the players cleaning process to ensure referential integrity across tables.
It maintains data consistency when PlayerIDs are merged or updated.

## What We Do
1. Load raw ReportingInsight data and cleaned Players data
2. Load PlayerID mapping dictionary from players cleaning
3. Apply ID mappings to ReportingInsight to resolve conflicts
4. Validate referential integrity (all PlayerIDs in Reporting exist in Players)
5. Normalize and clean reporting data fields
6. Export cleaned reporting table

## What Could Be Modified
- ID mapping application strategy (currently direct replacement)
- Referential integrity validation rules
- Handling of orphaned records (PlayerIDs in Reporting not in Players)
- Normalization rules for report-specific fields
- Date parsing for ReportCreatedOn/ReportModifiedOn
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
import json
from datetime import datetime

# Import utility functions
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from utils import normalize_name, normalize_nationality, parse_date_safe


def load_id_mapping(mapping_path: str) -> Dict[str, str]:
    """
    Load PlayerID mapping dictionary.
    
    Args:
        mapping_path: Path to JSON file with ID mappings
    
    Returns:
        Dictionary mapping old_id -> canonical_id
    """
    with open(mapping_path, 'r') as f:
        return json.load(f)


def apply_id_mapping(df: pd.DataFrame, id_mapping: Dict[str, str]) -> Tuple[pd.DataFrame, Dict]:
    """
    Apply PlayerID mappings to reporting data.
    
    Args:
        df: Reporting DataFrame
        id_mapping: Dictionary mapping old_id -> canonical_id
    
    Returns:
        Tuple of (updated DataFrame, mapping statistics)
    """
    df = df.copy()
    
    stats = {
        'total_rows': len(df),
        'rows_with_mapped_ids': 0,
        'unique_old_ids_found': 0,
        'mapping_applications': 0
    }
    
    # Track which old IDs were found
    old_ids_found = set()
    
    # Apply mappings
    def map_player_id(player_id):
        if pd.isna(player_id) or player_id == '':
            return player_id
        
        player_id_str = str(player_id).strip()
        if player_id_str in id_mapping:
            old_ids_found.add(player_id_str)
            stats['mapping_applications'] += 1
            return id_mapping[player_id_str]
        return player_id
    
    df['PlayerID'] = df['PlayerID'].apply(map_player_id)
    stats['rows_with_mapped_ids'] = (df['PlayerID'].isin(id_mapping.values())).sum()
    stats['unique_old_ids_found'] = len(old_ids_found)
    
    return df, stats


def restore_orphaned_players(df_reporting: pd.DataFrame, df_players: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
    """
    Restore orphaned PlayerIDs by creating minimal player records from Reporting data.
    
    This is a professional approach: when PlayerIDs exist in Reporting but not in Players,
    we create minimal player records using information available in Reporting to maintain
    referential integrity.
    
    Args:
        df_reporting: Reporting DataFrame
        df_players: Players DataFrame
    
    Returns:
        Tuple of (updated players DataFrame, updated reporting DataFrame, restoration stats)
    """
    players_ids = set(df_players['PlayerID'].unique())
    reporting_ids = set(df_reporting['PlayerID'].dropna().unique())
    
    orphaned_ids = reporting_ids - players_ids
    
    stats = {
        'orphaned_found': len(orphaned_ids),
        'players_restored': 0,
        'restored_player_ids': []
    }
    
    if len(orphaned_ids) == 0:
        return df_players, df_reporting, stats
    
    # Extract player information from Reporting for orphaned IDs
    orphaned_data = df_reporting[df_reporting['PlayerID'].isin(orphaned_ids)].copy()
    
    # Create minimal player records
    restored_players = []
    for player_id in orphaned_ids:
        player_reports = orphaned_data[orphaned_data['PlayerID'] == player_id]
        
        # Extract most common/first available information
        player_name = player_reports['PlayerName'].mode()[0] if len(player_reports['PlayerName'].mode()) > 0 else player_reports['PlayerName'].iloc[0]
        player_name = normalize_name(player_name) if pd.notna(player_name) else ''
        
        nationality = player_reports['PlayerFirstNationality'].mode()[0] if len(player_reports['PlayerFirstNationality'].mode()) > 0 else player_reports['PlayerFirstNationality'].iloc[0]
        nationality = normalize_nationality(nationality) if pd.notna(nationality) else ''
        
        # Create minimal player record
        restored_player = {
            'PlayerID': player_id,
            'PlayerName': player_name,
            'PlayerFirstNationality': nationality,
            'DateOfBirth': '',  # Not available in Reporting
            'CurrentTeam': ''   # Not available in Reporting
        }
        restored_players.append(restored_player)
        stats['players_restored'] += 1
        stats['restored_player_ids'].append(player_id)
    
    # Add restored players to Players DataFrame
    if restored_players:
        restored_df = pd.DataFrame(restored_players)
        df_players_updated = pd.concat([df_players, restored_df], ignore_index=True)
    else:
        df_players_updated = df_players.copy()
    
    return df_players_updated, df_reporting, stats


def validate_referential_integrity(df_reporting: pd.DataFrame, df_players: pd.DataFrame) -> Dict:
    """
    Validate that all PlayerIDs in Reporting exist in Players table.
    
    Args:
        df_reporting: Reporting DataFrame
        df_players: Players DataFrame
    
    Returns:
        Dictionary with validation statistics
    """
    players_ids = set(df_players['PlayerID'].unique())
    reporting_ids = set(df_reporting['PlayerID'].dropna().unique())
    
    orphaned_ids = reporting_ids - players_ids
    
    validation = {
        'total_unique_player_ids_in_reporting': len(reporting_ids),
        'total_unique_player_ids_in_players': len(players_ids),
        'orphaned_player_ids': list(orphaned_ids),
        'orphaned_count': len(orphaned_ids),
        'orphaned_rows': df_reporting[df_reporting['PlayerID'].isin(orphaned_ids)].shape[0] if orphaned_ids else 0,
        'integrity_status': 'PASS' if len(orphaned_ids) == 0 else 'WARNING'
    }
    
    return validation


def normalize_reporting_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize reporting data fields.
    
    Args:
        df: Reporting DataFrame
    
    Returns:
        Normalized DataFrame
    """
    df = df.copy()
    
    # Normalize PlayerName
    df['PlayerName'] = df['PlayerName'].apply(normalize_name)
    
    # Normalize PlayerFirstNationality
    df['PlayerFirstNationality'] = df['PlayerFirstNationality'].apply(normalize_nationality)
    
    # Normalize Country field
    df['Country'] = df['Country'].apply(
        lambda x: normalize_nationality(str(x)) if pd.notna(x) else ''
    )
    
    # Parse and standardize dates
    for date_col in ['ReportCreatedOn', 'ReportModifiedOn', 'MatchDate']:
        if date_col in df.columns:
            df[date_col] = df[date_col].apply(
                lambda x: parse_date_safe(x, '%d/%m/%Y %H:%M').strftime('%d/%m/%Y %H:%M') 
                if parse_date_safe(x, '%d/%m/%Y %H:%M') is not None 
                else (parse_date_safe(x, '%d/%m/%Y').strftime('%d/%m/%Y') 
                      if parse_date_safe(x, '%d/%m/%Y') is not None else '')
            )
    
    # Normalize position fields (remove extra spaces)
    for pos_col in ['ReportPrimaryPosition', 'ReportSecondaryPosition']:
        if pos_col in df.columns:
            df[pos_col] = df[pos_col].apply(
                lambda x: str(x).strip() if pd.notna(x) and str(x).strip() != '' else ''
            )
    
    # Normalize ReportFoot
    if 'ReportFoot' in df.columns:
        df['ReportFoot'] = df['ReportFoot'].apply(
            lambda x: str(x).strip().title() if pd.notna(x) else ''
        )
    
    return df


def audit_reporting_data(df: pd.DataFrame) -> Dict:
    """
    Perform audit of reporting dataset.
    
    Args:
        df: Reporting DataFrame
    
    Returns:
        Dictionary with audit metrics
    """
    audit = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_values': df.isnull().sum().to_dict(),
        'missing_percentage': (df.isnull().sum() / len(df) * 100).to_dict(),
        'unique_players': df['PlayerID'].nunique(),
        'unique_scouts': df['ScoutID'].nunique() if 'ScoutID' in df.columns else 0,
        'unique_countries': df['Country'].nunique() if 'Country' in df.columns else 0,
        'report_types': df['ReportType'].value_counts().to_dict() if 'ReportType' in df.columns else {},
        'performance_grades': df['PerformanceGrade'].value_counts().to_dict() if 'PerformanceGrade' in df.columns else {},
        'potential_grades': df['PotentialGrade'].value_counts().to_dict() if 'PotentialGrade' in df.columns else {},
    }
    
    return audit


def clean_reporting_pipeline(
    reporting_input_path: str,
    players_cleaned_path: str,
    id_mapping_path: str,
    output_path: str
) -> Dict:
    """
    Main pipeline function for cleaning reporting data.
    
    Args:
        reporting_input_path: Path to raw ReportingInsight.csv
        players_cleaned_path: Path to cleaned Players.csv
        id_mapping_path: Path to PlayerID mapping JSON
        output_path: Path to save cleaned reporting CSV
    
    Returns:
        Dictionary with cleaning metrics
    """
    print("=" * 80)
    print("REPORTING DATA CLEANING PIPELINE")
    print("=" * 80)
    
    # Load data
    print("\n[1/5] Loading raw data...")
    df_reporting_raw = pd.read_csv(reporting_input_path)
    df_players_cleaned = pd.read_csv(players_cleaned_path)
    print(f"   Loaded {len(df_reporting_raw)} reporting rows")
    print(f"   Loaded {len(df_players_cleaned)} player records")
    
    # Audit before
    print("\n[2/5] Auditing reporting data...")
    audit_before = audit_reporting_data(df_reporting_raw)
    print(f"   Total rows: {audit_before['total_rows']}")
    print(f"   Unique players: {audit_before['unique_players']}")
    print(f"   Unique scouts: {audit_before['unique_scouts']}")
    
    # Load ID mapping
    print("\n[3/5] Loading PlayerID mapping...")
    id_mapping = load_id_mapping(id_mapping_path)
    print(f"   Loaded {len(id_mapping)} ID mappings")
    
    # Apply ID mapping
    print("\n[4/5] Applying PlayerID mappings...")
    df_reporting_cleaned, mapping_stats = apply_id_mapping(df_reporting_raw, id_mapping)
    print(f"   Applied {mapping_stats['mapping_applications']} ID mappings")
    print(f"   Found {mapping_stats['unique_old_ids_found']} old IDs in reporting data")
    
    # Restore orphaned players (professional approach)
    print("\n[5/6] Restoring orphaned players from Reporting data...")
    df_players_updated, df_reporting_cleaned, restoration_stats = restore_orphaned_players(
        df_reporting_cleaned, df_players_cleaned
    )
    if restoration_stats['players_restored'] > 0:
        print(f"   Restored {restoration_stats['players_restored']} players from Reporting data")
        print(f"   Restored IDs: {', '.join(restoration_stats['restored_player_ids'])}")
        # Update players_cleaned.csv with restored players
        players_cleaned_path = Path(players_cleaned_path)
        df_players_updated.to_csv(players_cleaned_path, index=False)
        print(f"   Updated {players_cleaned_path.name} with restored players")
    else:
        print(f"   No orphaned players found - referential integrity maintained")
    
    # Validate referential integrity (should now pass)
    print("\n[6/6] Validating referential integrity...")
    integrity = validate_referential_integrity(df_reporting_cleaned, df_players_updated)
    print(f"   Integrity status: {integrity['integrity_status']}")
    if integrity['orphaned_count'] > 0:
        print(f"   WARNING: {integrity['orphaned_count']} orphaned PlayerIDs still found")
        print(f"   Orphaned rows: {integrity['orphaned_rows']}")
    else:
        print(f"   [PASS] All PlayerIDs in Reporting exist in Players table")
    
    # Normalize data
    print("\n[Normalizing] Cleaning and standardizing fields...")
    df_reporting_cleaned = normalize_reporting_data(df_reporting_cleaned)
    
    # Final audit
    audit_after = audit_reporting_data(df_reporting_cleaned)
    
    # Save cleaned data
    print(f"\n[Saving] Writing cleaned data to {output_path}...")
    df_reporting_cleaned.to_csv(output_path, index=False)
    print(f"   Saved {len(df_reporting_cleaned)} rows")
    
    # Prepare metrics
    metrics = {
        'before': audit_before,
        'after': audit_after,
        'mapping_stats': mapping_stats,
        'restoration_stats': restoration_stats,
        'integrity': integrity,
        'timestamp': datetime.now().isoformat()
    }
    
    print("\n" + "=" * 80)
    print("CLEANING COMPLETE")
    print("=" * 80)
    print(f"\nSummary:")
    print(f"  Rows processed: {metrics['after']['total_rows']}")
    print(f"  ID mappings applied: {metrics['mapping_stats']['mapping_applications']}")
    print(f"  Referential integrity: {metrics['integrity']['integrity_status']}")
    
    return metrics


if __name__ == "__main__":
    # Define paths
    BASE_DIR = Path(__file__).parent.parent
    REPORTING_INPUT = BASE_DIR / "data" / "raw" / "ReportingInsight.csv"
    PLAYERS_CLEANED = BASE_DIR / "data" / "processed" / "players_cleaned.csv"
    ID_MAPPING = BASE_DIR / "data" / "processed" / "player_id_map.json"
    OUTPUT = BASE_DIR / "data" / "processed" / "reporting_cleaned.csv"
    
    # Ensure output directory exists
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    
    # Run pipeline
    metrics = clean_reporting_pipeline(
        str(REPORTING_INPUT),
        str(PLAYERS_CLEANED),
        str(ID_MAPPING),
        str(OUTPUT)
    )

