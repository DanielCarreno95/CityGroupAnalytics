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
    
    This function handles two types of duplicates:
    1. Same player with different PlayerIDs (fingerprint-based detection)
    2. Same PlayerID with different player data (data integrity issue - generates new IDs)
    
    Args:
        df: Players DataFrame (should be normalized first)
    
    Returns:
        Tuple of (cleaned DataFrame, ID mapping dictionary)
    """
    df = df.copy()
    
    # Step 1: Handle whitespace and normalize string fields first
    # Convert empty strings and whitespace-only strings to NaN for proper handling
    string_cols = ['PlayerName', 'PlayerFirstNationality', 'CurrentTeam']
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: '' if pd.isna(x) or str(x).strip() == '' else str(x).strip()
            )
            # Convert empty strings to NaN for proper null handling
            df[col] = df[col].replace('', np.nan)
    
    # Step 2: Create fingerprints for duplicate detection (same player, different IDs)
    df['fingerprint'] = df.apply(create_player_fingerprint, axis=1)
    
    # Step 3: Handle duplicate PlayerIDs (same ID, different players - data integrity issue)
    # This is a critical issue: same PlayerID should represent the same player
    # If we find same PlayerID with different fingerprints, we need to generate new unique IDs
    id_mapping = {}
    duplicate_player_ids = df[df.duplicated(subset=['PlayerID'], keep=False)].copy()
    
    if len(duplicate_player_ids) > 0:
        # Group by PlayerID to find conflicts
        player_id_groups = duplicate_player_ids.groupby('PlayerID')
        
        # Get all existing PlayerIDs to avoid collisions
        existing_ids = set(df['PlayerID'].unique())
        
        for player_id, group in player_id_groups:
            if len(group) > 1:
                # Same PlayerID but different fingerprints = different players
                # Keep the first occurrence, generate new IDs for others
                first_idx = group.index[0]
                canonical_id = group.loc[first_idx, 'PlayerID']
                
                # For other records with same PlayerID but different fingerprints, generate new IDs
                counter = 1
                for idx in group.index[1:]:
                    # Generate new unique PlayerID by appending suffix
                    # Format: PLY_XXXXXXXX -> PLY_XXXXXXXX_01, PLY_XXXXXXXX_02, etc.
                    new_id = f"{canonical_id}_{counter:02d}"
                    
                    # Ensure uniqueness (in case of collisions)
                    while new_id in existing_ids or new_id in id_mapping.values():
                        counter += 1
                        new_id = f"{canonical_id}_{counter:02d}"
                    
                    # Add to existing IDs set
                    existing_ids.add(new_id)
                    
                    # Map old ID to new ID (but we'll update directly in dataframe)
                    # Store mapping for reporting purposes
                    old_id = group.loc[idx, 'PlayerID']
                    if old_id not in id_mapping:
                        id_mapping[old_id] = new_id
                    
                    # Update the PlayerID in the dataframe
                    df.loc[idx, 'PlayerID'] = new_id
                    counter += 1
    
    # Step 4: Handle duplicate fingerprints (same player, different PlayerIDs)
    # Find duplicate groups by fingerprint
    duplicate_groups = df[df.duplicated(subset=['fingerprint'], keep=False)].copy()
    
    if len(duplicate_groups) > 0:
        # Group by fingerprint
        fingerprint_groups = duplicate_groups.groupby('fingerprint')
        
        for fingerprint, group in fingerprint_groups:
            if len(group) > 1:
                # Determine canonical ID (best record)
                canonical_id = determine_canonical_player_id(group)
                
                # Map all other IDs to canonical
                for idx, row in group.iterrows():
                    if row['PlayerID'] != canonical_id:
                        # Only map if not already mapped (avoid overwriting)
                        if row['PlayerID'] not in id_mapping:
                            id_mapping[row['PlayerID']] = canonical_id
    
    # Step 5: Apply ID mappings to resolve conflicts
    # Update PlayerIDs based on mapping
    df['PlayerID'] = df['PlayerID'].apply(
        lambda x: id_mapping.get(x, x) if pd.notna(x) else x
    )
    
    # Step 6: Remove duplicate rows
    # First, remove exact duplicates (identical rows)
    df_cleaned = df.drop_duplicates(keep='first').copy()
    
    # Then, remove duplicates by fingerprint (keep best record)
    # Sort by completeness to keep best records
    def calculate_completeness(row):
        score = 0
        for col in ['PlayerName', 'PlayerFirstNationality', 'DateOfBirth', 'CurrentTeam']:
            val = row.get(col, '')
            if pd.notna(val) and str(val).strip() != '':
                score += 1
        return score
    
    df_cleaned['_completeness'] = df_cleaned.apply(calculate_completeness, axis=1)
    df_cleaned = df_cleaned.sort_values(
        by=['fingerprint', '_completeness', 'CurrentTeam', 'PlayerID'],
        ascending=[True, False, False, True],
        na_position='last'
    )
    
    # Keep first occurrence of each fingerprint (which is now the best record)
    df_cleaned = df_cleaned.drop_duplicates(subset=['fingerprint'], keep='first').copy()
    
    # Drop temporary columns
    df_cleaned = df_cleaned.drop(columns=['fingerprint', '_completeness'], errors='ignore')
    
    # Step 7: Final validation - ensure no duplicate PlayerIDs remain
    # This is CRITICAL: we must have 0 duplicate PlayerIDs
    remaining_duplicates = df_cleaned[df_cleaned.duplicated(subset=['PlayerID'], keep=False)]
    if len(remaining_duplicates) > 0:
        # This should not happen, but if it does, generate new IDs
        print(f"WARNING: {len(remaining_duplicates)} duplicate PlayerIDs still remain after cleaning")
        print("   Resolving remaining duplicates by generating new unique IDs...")
        
        # Get all existing PlayerIDs to avoid collisions
        existing_ids = set(df_cleaned['PlayerID'].unique())
        
        for player_id in remaining_duplicates['PlayerID'].unique():
            group = df_cleaned[df_cleaned['PlayerID'] == player_id]
            if len(group) > 1:
                # Keep first record, generate new IDs for others
                counter = 1
                for idx in group.index[1:]:
                    # Generate new unique PlayerID by appending suffix
                    new_id = f"{player_id}_{counter:02d}"
                    
                    # Ensure uniqueness
                    while new_id in existing_ids:
                        counter += 1
                        new_id = f"{player_id}_{counter:02d}"
                    
                    # Add to existing IDs
                    existing_ids.add(new_id)
                    
                    # Update the PlayerID
                    old_id = df_cleaned.loc[idx, 'PlayerID']
                    df_cleaned.loc[idx, 'PlayerID'] = new_id
                    
                    # Track mapping
                    if old_id not in id_mapping:
                        id_mapping[old_id] = new_id
                    
                    counter += 1
        
        # Verify no duplicates remain
        final_duplicates = df_cleaned[df_cleaned.duplicated(subset=['PlayerID'], keep=False)]
        if len(final_duplicates) > 0:
            print(f"   ERROR: Still {len(final_duplicates)} duplicate PlayerIDs after resolution!")
        else:
            print(f"   [OK] All duplicate PlayerIDs resolved")
    
    return df_cleaned, id_mapping


def normalize_players_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize player data fields.
    
    This function:
    - Strips whitespace from all string fields
    - Converts empty strings and whitespace-only strings to empty string (not NaN for consistency)
    - Normalizes names, nationalities, dates
    - Removes invalid records
    
    Args:
        df: Players DataFrame
    
    Returns:
        Normalized DataFrame
    """
    df = df.copy()
    
    # Step 1: Strip whitespace from all string columns globally
    string_cols = ['PlayerName', 'PlayerFirstNationality', 'CurrentTeam', 'DateOfBirth']
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: str(x).strip() if pd.notna(x) else ''
            )
            # Convert whitespace-only strings to empty string
            df[col] = df[col].apply(
                lambda x: '' if isinstance(x, str) and x.strip() == '' else x
            )
    
    # Step 2: Normalize PlayerName
    df['PlayerName'] = df['PlayerName'].apply(normalize_name)
    
    # Step 3: Normalize PlayerFirstNationality
    df['PlayerFirstNationality'] = df['PlayerFirstNationality'].apply(normalize_nationality)
    
    # Step 4: Normalize CurrentTeam (remove extra spaces)
    df['CurrentTeam'] = df['CurrentTeam'].apply(
        lambda x: ' '.join(str(x).split()) if pd.notna(x) and str(x).strip() != '' else ''
    )
    
    # Step 5: Standardize DateOfBirth format (ensure consistent format)
    df['DateOfBirth'] = df['DateOfBirth'].apply(
        lambda x: parse_date_safe(x).strftime('%d/%m/%Y') if parse_date_safe(x) is not None else ''
    )
    
    # Step 6: Remove rows with completely empty PlayerName (invalid records)
    df = df[df['PlayerName'] != ''].copy()
    
    # Step 7: Convert empty strings to NaN for proper null handling in analysis
    # But keep as empty string for CSV output consistency
    # (We'll handle this in the final output)
    
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
    print("\n[1/5] Loading raw data...")
    df_raw = pd.read_csv(input_path)
    print(f"   Loaded {len(df_raw)} rows")
    
    # Audit before cleaning
    print("\n[2/5] Auditing raw data...")
    audit_before = audit_players_data(df_raw)
    print(f"   Total rows: {audit_before['total_rows']}")
    print(f"   Exact duplicates: {audit_before['duplicate_rows_exact']}")
    print(f"   Duplicate PlayerIDs: {audit_before['duplicate_player_ids']}")
    print(f"   Missing PlayerName: {audit_before['players_without_name']}")
    print(f"   Missing DateOfBirth: {audit_before['players_without_dob']}")
    print(f"   Missing Nationality: {audit_before['players_without_nationality']}")
    
    # Normalize data first (before duplicate detection)
    print("\n[3/5] Normalizing data (whitespace, names, dates)...")
    df_normalized = normalize_players_data(df_raw)
    print(f"   Normalized {len(df_normalized)} rows")
    
    # Detect and resolve duplicates (on normalized data)
    print("\n[4/5] Detecting and resolving duplicates...")
    df_cleaned, id_mapping = detect_duplicate_players(df_normalized)
    print(f"   Found {len(id_mapping)} PlayerID mappings to resolve")
    print(f"   Removed {len(df_normalized) - len(df_cleaned)} duplicate rows")
    
    # Final normalization pass (ensure consistency)
    print("\n[5/5] Final normalization pass...")
    df_cleaned = normalize_players_data(df_cleaned)
    
    # Final audit
    print("\n[Validation] Verifying data quality...")
    audit_after = audit_players_data(df_cleaned)
    
    # Critical validation: Ensure 0 duplicate PlayerIDs
    duplicate_count = audit_after['duplicate_player_ids']
    if duplicate_count > 0:
        print(f"   ERROR: {duplicate_count} duplicate PlayerIDs still exist!")
        print("   This should not happen. Please review the deduplication logic.")
    else:
        print(f"   [OK] No duplicate PlayerIDs (verified: {duplicate_count})")
    
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

