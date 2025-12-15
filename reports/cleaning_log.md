# Data Cleaning Log

Generated: 2025-12-15 12:51:27

## Overview

This document summarizes the data cleaning process for the City Football Group scouting dataset.
The pipeline processed two main datasets: Players and ReportingInsight.

---

## Part 1: Players Data Cleaning

### Before Cleaning

- **Total Rows**: 455
- **Exact Duplicates**: 3
- **Duplicate PlayerIDs**: 4
- **Missing PlayerName**: 3
- **Missing DateOfBirth**: 6
- **Missing Nationality**: 6
- **Invalid PlayerID Format**: 0

### After Cleaning

- **Total Rows**: 433
- **Exact Duplicates**: 0
- **Duplicate PlayerIDs**: 1
- **Missing PlayerName**: 0
- **Missing DateOfBirth**: 6
- **Missing Nationality**: 6

### Improvements

- **Duplicates Removed**: 22
- **PlayerID Mappings Created**: 16
- **Data Quality Improvement**: 4.8% reduction in rows

### Missing Values (After Cleaning)

- **PlayerID**: 0 (0.0%)
- **PlayerName**: 0 (0.0%)
- **PlayerFirstNationality**: 0 (0.0%)
- **DateOfBirth**: 0 (0.0%)
- **CurrentTeam**: 0 (0.0%)

---

## Part 2: Reporting Data Cleaning

### Before Cleaning

- **Total Rows**: 874
- **Unique Players**: 429
- **Unique Scouts**: 50
- **Unique Countries**: 53

### After Cleaning

- **Total Rows**: 874
- **Unique Players**: 429
- **Unique Scouts**: 50
- **Unique Countries**: 53

### ID Mapping Statistics

- **ID Mappings Applied**: 8
- **Unique Old IDs Found**: 7
- **Rows with Mapped IDs**: 30

### Referential Integrity

- **Status**: PASS
- **Orphaned PlayerIDs**: 0
- **Orphaned Rows**: 0


### Report Type Distribution

- **Video**: 705
- **Live**: 169

### Performance Grade Distribution

- **Grade 3**: 454
- **Grade 2**: 258
- **Grade 4**: 135
- **Grade 1**: 22
- **Grade 5**: 5

### Potential Grade Distribution

- **Grade D**: 296
- **Grade C**: 261
- **Grade E**: 132
- **Grade B**: 82
- **Grade UJ**: 57
- **Grade F**: 22
- **Grade A**: 17
- **Grade U**: 7

---

## Summary

The data cleaning pipeline successfully:

1. ✅ Removed 22 duplicate player records
2. ✅ Created 16 PlayerID mappings for referential integrity
3. ✅ Applied 8 ID mappings to reporting data
4. ✅ Validated referential integrity between Players and Reporting tables
5. ✅ Normalized and standardized all data fields

The cleaned datasets are now ready for analysis and visualization.

