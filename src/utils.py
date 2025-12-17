"""
Utility functions for data cleaning and normalization.

This module provides reusable functions for:
- Name and nationality normalization
- Player fingerprinting for duplicate detection
- Date parsing and validation
- PlayerID validation
- Canonical ID selection
"""

import pandas as pd
import numpy as np
import re
from typing import Optional
from datetime import datetime


def normalize_name(name: str) -> str:
    """
    Normalize player name by removing titles, suffixes, and extra whitespace.
    
    Handles:
    - Titles: Dr., Mr., Mrs., Ms., etc.
    - Suffixes: DVM, Jr., Sr., II, III, etc.
    - Extra whitespace
    - Case normalization
    
    Args:
        name: Raw player name string
        
    Returns:
        Normalized name string, or empty string if invalid
    """
    if pd.isna(name) or name == '':
        return ''
    
    # Convert to string and strip whitespace
    name_str = str(name).strip()
    
    # If only whitespace, return empty
    if name_str == '' or name_str.isspace():
        return ''
    
    # Remove common titles
    titles = ['Dr.', 'Mr.', 'Mrs.', 'Ms.', 'Miss', 'Prof.', 'Professor']
    for title in titles:
        # Remove title at the beginning
        name_str = re.sub(rf'^{re.escape(title)}\s+', '', name_str, flags=re.IGNORECASE)
    
    # Remove common suffixes
    suffixes = ['DVM', 'Jr.', 'Sr.', 'II', 'III', 'IV', 'MD', 'PhD']
    for suffix in suffixes:
        # Remove suffix at the end
        name_str = re.sub(rf'\s+{re.escape(suffix)}$', '', name_str, flags=re.IGNORECASE)
    
    # Normalize whitespace (multiple spaces to single space)
    name_str = ' '.join(name_str.split())
    
    # Title case (first letter of each word capitalized)
    name_str = name_str.title()
    
    return name_str.strip()


def normalize_nationality(nationality: str) -> str:
    """
    Normalize nationality strings for consistent matching.
    
    Handles:
    - Common variations (e.g., "Congo DR" -> "DR Congo", "Côte d'Ivoire" -> "Ivory Coast")
    - Extra whitespace
    - Case normalization
    
    Args:
        nationality: Raw nationality string
        
    Returns:
        Normalized nationality string, or empty string if invalid
    """
    if pd.isna(nationality) or nationality == '':
        return ''
    
    # Convert to string and strip whitespace
    nat_str = str(nationality).strip()
    
    # If only whitespace, return empty
    if nat_str == '' or nat_str.isspace():
        return ''
    
    # Common nationality mappings
    nationality_mappings = {
        'Congo DR': 'DR Congo',
        'DR Congo': 'DR Congo',
        'Congo': 'DR Congo',
        "Côte d'Ivoire": 'Ivory Coast',
        'Ivory Coast': 'Ivory Coast',
        'SWEDEN': 'Sweden',
        'sweden': 'Sweden',
        'Belgium ': 'Belgium',
        'Belgium': 'Belgium',
    }
    
    # Check if we have a mapping
    if nat_str in nationality_mappings:
        return nationality_mappings[nat_str]
    
    # Normalize whitespace
    nat_str = ' '.join(nat_str.split())
    
    # Title case
    nat_str = nat_str.title()
    
    return nat_str.strip()


def parse_date_safe(date_str: str, date_format: Optional[str] = None) -> Optional[datetime]:
    """
    Safely parse date string with multiple format attempts.
    
    Args:
        date_str: Date string to parse
        date_format: Optional specific format to try first
        
    Returns:
        datetime object if successful, None otherwise
    """
    if pd.isna(date_str) or date_str == '' or str(date_str).strip() == '':
        return None
    
    date_str = str(date_str).strip()
    
    # List of formats to try
    formats = []
    if date_format:
        formats.append(date_format)
    
    formats.extend([
        '%d/%m/%Y',
        '%Y-%m-%d',
        '%d-%m-%Y',
        '%m/%d/%Y',
        '%Y/%m/%d',
        '%d/%m/%Y %H:%M',
        '%Y-%m-%d %H:%M:%S',
        '%d-%m-%Y %H:%M',
    ])
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except (ValueError, TypeError):
            continue
    
    return None


def validate_player_id(player_id: str) -> bool:
    """
    Validate PlayerID format.
    
    Expected format: PLY_ followed by alphanumeric characters
    
    Args:
        player_id: PlayerID string to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if pd.isna(player_id) or player_id == '':
        return False
    
    player_id_str = str(player_id).strip()
    
    # Check format: PLY_ followed by alphanumeric
    pattern = r'^PLY_[A-Z0-9]+$'
    return bool(re.match(pattern, player_id_str))


def create_player_fingerprint(row: pd.Series) -> str:
    """
    Create a unique fingerprint for a player based on normalized data.
    
    Fingerprint components:
    - Normalized PlayerName
    - DateOfBirth (normalized)
    - Normalized PlayerFirstNationality
    
    This fingerprint is used to identify duplicate players (same person with different PlayerIDs).
    
    Args:
        row: DataFrame row containing player data
        
    Returns:
        Fingerprint string (hash-like identifier)
    """
    # Normalize name
    name = normalize_name(row.get('PlayerName', ''))
    
    # Normalize date of birth
    dob = row.get('DateOfBirth', '')
    dob_parsed = parse_date_safe(dob)
    dob_str = dob_parsed.strftime('%d/%m/%Y') if dob_parsed else ''
    
    # Normalize nationality
    nationality = normalize_nationality(row.get('PlayerFirstNationality', ''))
    
    # Create fingerprint: name|dob|nationality
    fingerprint = f"{name}|{dob_str}|{nationality}"
    
    return fingerprint.lower().strip()


def determine_canonical_player_id(group: pd.DataFrame) -> str:
    """
    Determine the canonical (best) PlayerID from a group of duplicate players.
    
    Selection criteria (in order of priority):
    1. Data completeness (fewest null/empty values)
    2. CurrentTeam presence (prefers records with team information)
    3. Alphabetical order (tiebreaker)
    
    Args:
        group: DataFrame containing duplicate player records
        
    Returns:
        Canonical PlayerID string
    """
    if len(group) == 0:
        raise ValueError("Cannot determine canonical ID from empty group")
    
    if len(group) == 1:
        return group['PlayerID'].iloc[0]
    
    # Calculate completeness score for each row
    def calculate_completeness(row):
        score = 0
        # Count non-null, non-empty values
        for col in ['PlayerName', 'PlayerFirstNationality', 'DateOfBirth', 'CurrentTeam']:
            val = row.get(col, '')
            if pd.notna(val) and str(val).strip() != '':
                score += 1
        return score
    
    group = group.copy()
    group['completeness'] = group.apply(calculate_completeness, axis=1)
    
    # Sort by completeness (descending), then by CurrentTeam presence, then alphabetically
    group = group.sort_values(
        by=['completeness', 'CurrentTeam', 'PlayerID'],
        ascending=[False, False, True],
        na_position='last'
    )
    
    # Return the PlayerID of the best record
    return group['PlayerID'].iloc[0]

