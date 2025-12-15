"""
# STEP 1: Player Data Audit & Cleaning

## Brief Explanation
This script performs comprehensive data cleaning on the Players.csv dataset.
It identifies and resolves duplicates, missing values, inconsistencies, and data quality issues
to create a reliable and accurate player master table.

## What We Do
1. Load and audit the raw Players dataset
2. Detect exact and conditional duplicates
3. Normalize names, nationalities, and other fields
4. Create a PlayerID mapping dictionary for duplicate resolution
5. Generate cleaned player table with deduplication
6. Export cleaning log with before/after metrics

## What Could Be Modified
- Duplicate detection criteria (currently based on name + DOB + nationality)
- Normalization rules for names/nationalities
- Canonical ID selection logic (currently prioritizes completeness + CurrentTeam)
- Missing value imputation strategies
- Date format handling for different input formats
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
from utils import (
    normalize_name, normalize_nationality, create_player_fingerprint,
    determine_canonical_player_id, parse_date_safe, validate_player_id
)


def audit_players_data(df: pd.DataFrame) -> Dict:
    """
    Perform comprehensive audit of players dataset.
    
    Args:
        df: Raw players DataFrame
    
    Returns:
        Dictionary with audit metrics
    """
    audit = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'duplicate_rows_exact': df.duplicated().sum(),
        'missing_values': df.isnull().sum().to_dict(),
        'missing_percentage': (df.isnull().sum() / len(df) * 100).to_dict(),
        'duplicate_player_ids': df['PlayerID'].duplicated().sum(),
        'invalid_player_ids': 0,
        'players_without_name': (df['PlayerName'].isna() | (df['PlayerName'] == '')).sum(),
        'players_without_dob': (df['DateOfBirth'].isna() | (df['DateOfBirth'] == '')).sum(),
        'players_without_nationality': (df['PlayerFirstNationality'].isna() | (df['PlayerFirstNationality'] == '')).sum(),
    }
    
    # Validate PlayerID format
    invalid_ids = []
    for idx, player_id in df['PlayerID'].items():
        if not validate_player_id(player_id):
            invalid_ids.append(idx)
    audit['invalid_player_ids'] = len(invalid_ids)
    
    return audit


def detect_duplicate_players(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Detect duplicate players and create ID mapping.
    
    Args:
        df: Players DataFrame
    
    Returns:
        Tuple of (cleaned DataFrame, ID mapping dictionary)
    """
    # Create fingerprints for duplicate detection
    df['fingerprint'] = df.apply(create_player_fingerprint, axis=1)
    
    # Find duplicate groups
    duplicate_groups = df[df.duplicated(subset=['fingerprint'], keep=False)].copy()
    
    # Group by fingerprint
    fingerprint_groups = duplicate_groups.groupby('fingerprint')
    
    # Create ID mapping: old_id -> canonical_id
    id_mapping = {}
    ids_to_remove = set()
    
    for fingerprint, group in fingerprint_groups:
        if len(group) > 1:
            # Determine canonical ID
            canonical_id = determine_canonical_player_id(group)
            
            # Map all other IDs to canonical
            for idx, row in group.iterrows():
                if row['PlayerID'] != canonical_id:
                    id_mapping[row['PlayerID']] = canonical_id
                    ids_to_remove.add(idx)
    
    # Remove duplicate rows (keep first occurrence of each fingerprint)
    df_cleaned = df.drop_duplicates(subset=['fingerprint'], keep='first').copy()
    
    # Also remove explicitly marked rows
    df_cleaned = df_cleaned[~df_cleaned.index.isin(ids_to_remove)].copy()
    
    # Drop fingerprint column (temporary)
    df_cleaned = df_cleaned.drop(columns=['fingerprint'], errors='ignore')
    
    return df_cleaned, id_mapping


def normalize_players_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize player data fields.
    
    Args:
        df: Players DataFrame
    
    Returns:
        Normalized DataFrame
    """
    df = df.copy()
    
    # Normalize PlayerName
    df['PlayerName'] = df['PlayerName'].apply(normalize_name)
    
    # Normalize PlayerFirstNationality
    df['PlayerFirstNationality'] = df['PlayerFirstNationality'].apply(normalize_nationality)
    
    # Normalize CurrentTeam (remove extra spaces)
    df['CurrentTeam'] = df['CurrentTeam'].apply(
        lambda x: ' '.join(str(x).split()) if pd.notna(x) and str(x).strip() != '' else ''
    )
    
    # Standardize DateOfBirth format (ensure consistent format)
    df['DateOfBirth'] = df['DateOfBirth'].apply(
        lambda x: parse_date_safe(x).strftime('%d/%m/%Y') if parse_date_safe(x) is not None else ''
    )
    
    # Remove rows with completely empty PlayerName (invalid records)
    df = df[df['PlayerName'] != ''].copy()
    
    return df


def clean_players_pipeline(input_path: str, output_path: str, mapping_path: str) -> Dict:
    """
    Main pipeline function for cleaning players data.
    
    Args:
        input_path: Path to raw Players.csv
        output_path: Path to save cleaned players CSV
        mapping_path: Path to save PlayerID mapping JSON
    
    Returns:
        Dictionary with cleaning metrics
    """
    print("=" * 80)
    print("PLAYER DATA CLEANING PIPELINE")
    print("=" * 80)
    
    # Load data
    print("\n[1/4] Loading raw data...")
    df_raw = pd.read_csv(input_path)
    print(f"   Loaded {len(df_raw)} rows")
    
    # Audit
    print("\n[2/4] Auditing data...")
    audit_before = audit_players_data(df_raw)
    print(f"   Total rows: {audit_before['total_rows']}")
    print(f"   Exact duplicates: {audit_before['duplicate_rows_exact']}")
    print(f"   Duplicate PlayerIDs: {audit_before['duplicate_player_ids']}")
    print(f"   Missing PlayerName: {audit_before['players_without_name']}")
    print(f"   Missing DateOfBirth: {audit_before['players_without_dob']}")
    print(f"   Missing Nationality: {audit_before['players_without_nationality']}")
    
    # Detect and resolve duplicates
    print("\n[3/4] Detecting and resolving duplicates...")
    df_cleaned, id_mapping = detect_duplicate_players(df_raw)
    print(f"   Found {len(id_mapping)} PlayerID mappings to resolve")
    print(f"   Removed {len(df_raw) - len(df_cleaned)} duplicate rows")
    
    # Normalize data
    print("\n[4/4] Normalizing data...")
    df_cleaned = normalize_players_data(df_cleaned)
    
    # Final audit
    audit_after = audit_players_data(df_cleaned)
    
    # Save cleaned data
    print(f"\n[Saving] Writing cleaned data to {output_path}...")
    df_cleaned.to_csv(output_path, index=False)
    print(f"   Saved {len(df_cleaned)} rows")
    
    # Save ID mapping
    print(f"\n[Saving] Writing ID mapping to {mapping_path}...")
    with open(mapping_path, 'w') as f:
        json.dump(id_mapping, f, indent=2)
    print(f"   Saved {len(id_mapping)} ID mappings")
    
    # Prepare metrics
    metrics = {
        'before': audit_before,
        'after': audit_after,
        'duplicates_removed': len(df_raw) - len(df_cleaned),
        'id_mappings_created': len(id_mapping),
        'timestamp': datetime.now().isoformat()
    }
    
    print("\n" + "=" * 80)
    print("CLEANING COMPLETE")
    print("=" * 80)
    print(f"\nSummary:")
    print(f"  Rows before: {metrics['before']['total_rows']}")
    print(f"  Rows after: {metrics['after']['total_rows']}")
    print(f"  Duplicates removed: {metrics['duplicates_removed']}")
    print(f"  ID mappings created: {metrics['id_mappings_created']}")
    
    return metrics


if __name__ == "__main__":
    # Define paths
    BASE_DIR = Path(__file__).parent.parent
    INPUT_PATH = BASE_DIR / "data" / "raw" / "Players.csv"
    OUTPUT_PATH = BASE_DIR / "data" / "processed" / "players_cleaned.csv"
    MAPPING_PATH = BASE_DIR / "data" / "processed" / "player_id_map.json"
    
    # Ensure output directory exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    MAPPING_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Run pipeline
    metrics = clean_players_pipeline(
        str(INPUT_PATH),
        str(OUTPUT_PATH),
        str(MAPPING_PATH)
    )

