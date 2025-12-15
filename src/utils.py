"""
Utility functions for data cleaning and processing pipeline.

This module contains helper functions used across the data cleaning pipeline
for player data audit, normalization, and transformation.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Tuple, Optional
import re


def calculate_age_from_dob(date_of_birth: str, reference_date: Optional[str] = None) -> Optional[int]:
    """
    Calculate age from date of birth string.
    
    Args:
        date_of_birth: Date string in format DD/MM/YYYY
        reference_date: Reference date for age calculation (default: today)
    
    Returns:
        Age in years or None if date is invalid
    """
    if pd.isna(date_of_birth) or date_of_birth == '':
        return None
    
    try:
        # Parse date
        dob = datetime.strptime(date_of_birth, '%d/%m/%Y')
        ref = datetime.strptime(reference_date, '%d/%m/%Y') if reference_date else datetime.now()
        
        # Calculate age
        age = ref.year - dob.year - ((ref.month, ref.day) < (dob.month, dob.day))
        return age if age >= 0 else None
    except (ValueError, TypeError):
        return None


def normalize_name(name: str) -> str:
    """
    Normalize player name for comparison (remove extra spaces, titles, etc.).
    
    Args:
        name: Raw player name
    
    Returns:
        Normalized name string
    """
    if pd.isna(name) or name == '':
        return ''
    
    # Remove common titles
    name = re.sub(r'^(Dr\.|Mr\.|Mrs\.|Ms\.|Miss)\s+', '', str(name), flags=re.IGNORECASE)
    name = re.sub(r'\s+(DVM|MD|Jr\.|Sr\.|III|II|IV)$', '', str(name), flags=re.IGNORECASE)
    
    # Normalize whitespace
    name = ' '.join(name.split())
    
    # Remove leading/trailing whitespace
    return name.strip()


def normalize_nationality(nationality: str) -> str:
    """
    Normalize nationality strings (handle variations, extra spaces).
    
    Args:
        nationality: Raw nationality string
    
    Returns:
        Normalized nationality string
    """
    if pd.isna(nationality) or nationality == '':
        return ''
    
    nationality = str(nationality).strip()
    
    # Handle common variations
    nationality_map = {
        'Congo DR': 'DR Congo',
        'Côte d\'Ivoire': 'Ivory Coast',
        'Czech Republic': 'Czechia',
        'SWEDEN': 'Sweden',
        'Belgium ': 'Belgium'
    }
    
    return nationality_map.get(nationality, nationality)


def create_player_fingerprint(row: pd.Series) -> str:
    """
    Create a fingerprint for player identification based on key attributes.
    
    Args:
        row: DataFrame row with player information
    
    Returns:
        Fingerprint string for duplicate detection
    """
    name = normalize_name(row.get('PlayerName', ''))
    dob = str(row.get('DateOfBirth', ''))
    nationality = normalize_nationality(row.get('PlayerFirstNationality', ''))
    
    # Create fingerprint (name + dob + nationality)
    fingerprint = f"{name}|{dob}|{nationality}".lower()
    return fingerprint


def determine_canonical_player_id(duplicate_group: pd.DataFrame) -> str:
    """
    Determine which PlayerID should be kept as canonical for a group of duplicates.
    
    Selection criteria (in order):
    1. ID with most complete data (fewest nulls)
    2. ID with CurrentTeam filled
    3. ID that appears first in ReportingInsight (if available)
    4. Alphabetically first ID
    
    Args:
        duplicate_group: DataFrame with duplicate players
    
    Returns:
        Canonical PlayerID to keep
    """
    # Score each row based on data completeness
    scores = []
    for idx, row in duplicate_group.iterrows():
        score = 0
        # Prefer rows with CurrentTeam
        if pd.notna(row.get('CurrentTeam')) and str(row.get('CurrentTeam')).strip() != '':
            score += 10
        # Prefer rows with DateOfBirth
        if pd.notna(row.get('DateOfBirth')) and str(row.get('DateOfBirth')).strip() != '':
            score += 5
        # Prefer rows with PlayerName (should always be present, but check)
        if pd.notna(row.get('PlayerName')) and str(row.get('PlayerName')).strip() != '':
            score += 3
        scores.append((score, idx))
    
    # Sort by score (descending), then by PlayerID (ascending)
    scores.sort(key=lambda x: (-x[0], duplicate_group.loc[x[1], 'PlayerID']))
    
    return duplicate_group.loc[scores[0][1], 'PlayerID']


def parse_date_safe(date_str: str, format_str: str = '%d/%m/%Y') -> Optional[datetime]:
    """
    Safely parse date string.
    
    Args:
        date_str: Date string to parse
        format_str: Expected date format
    
    Returns:
        Parsed datetime object or None
    """
    if pd.isna(date_str) or date_str == '':
        return None
    
    try:
        return datetime.strptime(str(date_str).strip(), format_str)
    except (ValueError, TypeError):
        return None


def get_age_band_from_age(age: Optional[int]) -> str:
    """
    Convert numeric age to age band category.
    
    Args:
        age: Age in years
    
    Returns:
        Age band string (U18, U21, 21-24, 25-29, 30-34, 35+)
    """
    if age is None:
        return 'Unknown'
    
    if age < 18:
        return 'U18'
    elif age < 21:
        return 'U21'
    elif age < 25:
        return '21-24'
    elif age < 30:
        return '25-29'
    elif age < 35:
        return '30-34'
    else:
        return '35+'


def validate_player_id(player_id: str) -> bool:
    """
    Validate PlayerID format.
    
    Args:
        player_id: PlayerID string to validate
    
    Returns:
        True if valid format, False otherwise
    """
    if pd.isna(player_id) or player_id == '':
        return False
    
    # Expected format: PLY_ followed by alphanumeric
    pattern = r'^PLY_[A-Z0-9]+$'
    return bool(re.match(pattern, str(player_id).strip()))

