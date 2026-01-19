# Paquita Database Instance Categorization

## Overview

The Paquita database contains **1,285 Sudoku puzzle instances** (9×9 grids) with difficulty ratings ranging from **105 to 118**. Each instance in the original database file (`paquita_database.txt`) has the format:

```
puzzle_string;timestamp;code;difficulty_rating
```

## Categorization Schemes

### 1. By Difficulty Rating (Primary Method)

The difficulty rating is the numeric value at the end of each database entry (ranging from 105 to 118). This appears to be a standardized difficulty metric, where **higher numbers indicate harder puzzles**.

#### Rating Distribution

| Rating | Count | Percentage | Category |
|--------|-------|------------|----------|
| 105 | 457 | 35.6% | Easy |
| 106 | 89 | 6.9% | Easy-Medium |
| 108 | 54 | 4.2% | Medium |
| 109 | 131 | 10.2% | Medium |
| 110 | 32 | 2.5% | Medium-Hard |
| 111 | 193 | 15.0% | Medium-Hard |
| 112 | 13 | 1.0% | Hard |
| 114 | 1 | 0.1% | Hard |
| 115 | 27 | 2.1% | Hard |
| 116 | 184 | 14.3% | Hard |
| 117 | 56 | 4.4% | Very Hard |
| 118 | 48 | 3.7% | Very Hard |

#### Difficulty Level Categories

Based on the rating distribution and typical Sudoku difficulty scales:

**Easy (Rating 105-106)**
- Ratings: 105, 106
- Total instances: 546 (42.5%)
- Characteristics: Most common rating, likely solvable with basic techniques

**Medium (Rating 108-110)**
- Ratings: 108, 109, 110
- Total instances: 217 (16.9%)
- Characteristics: Moderate difficulty, may require intermediate techniques

**Medium-Hard (Rating 111)**
- Rating: 111
- Total instances: 193 (15.0%)
- Characteristics: Transitional difficulty level

**Hard (Rating 112-116)**
- Ratings: 112, 114, 115, 116
- Total instances: 225 (17.5%)
- Characteristics: Challenging puzzles requiring advanced techniques

**Very Hard (Rating 117-118)**
- Ratings: 117, 118
- Total instances: 104 (8.1%)
- Characteristics: Extremely challenging puzzles

### 2. By Fixed Cell Percentage (Alternative Method)

You can also categorize instances by counting the number of given cells (non-empty cells) in each puzzle:

**Calculation**: 
```
Fixed Percentage = (Number of given cells / 81) × 100
```

**Typical Categories**:
- **Easy** (60%+ fixed cells): ~49+ given cells
- **Medium** (40-60% fixed cells): ~32-48 given cells  
- **Hard** (20-40% fixed cells): ~16-32 given cells
- **Very Hard** (<20% fixed cells): <16 given cells

*Note: Fixed cell percentage alone may not perfectly correlate with difficulty rating, as puzzle structure and clue placement also affect difficulty.*

### 3. By Instance ID (Sequential)

Instances are numbered sequentially from `paquita_00001.txt` to `paquita_01285.txt`. However, **instance ID does not correlate with difficulty** - they are simply ordered by their position in the original database file.

## Recommended Categorization for Analysis

For experimental or benchmarking purposes, we recommend using the **Difficulty Rating** system as the primary categorization method:

### Suggested Groups

1. **Group 1 - Easy**: Ratings 105-106 (546 instances, 42.5%)
2. **Group 2 - Medium**: Ratings 108-110 (217 instances, 16.9%)
3. **Group 3 - Medium-Hard**: Rating 111 (193 instances, 15.0%)
4. **Group 4 - Hard**: Ratings 112-116 (225 instances, 17.5%)
5. **Group 5 - Very Hard**: Ratings 117-118 (104 instances, 8.1%)

## Usage Examples

### Python Script to Categorize Instances

```python
def categorize_paquita_instance(rating):
    """Categorize instance by difficulty rating"""
    if rating <= 106:
        return "Easy"
    elif rating <= 110:
        return "Medium"
    elif rating == 111:
        return "Medium-Hard"
    elif rating <= 116:
        return "Hard"
    else:
        return "Very Hard"

# Parse database file
with open('instances/paquita_database.txt', 'r') as f:
    for line in f:
        parts = line.strip().split(';')
        if len(parts) >= 4:
            rating = int(parts[3])
            category = categorize_paquita_instance(rating)
            print(f"Rating: {rating}, Category: {category}")
```

### Extraction by Category

To extract all instances of a specific difficulty category:

1. Parse `paquita_database.txt` to extract puzzle strings with their ratings
2. Filter by rating range
3. Convert to individual puzzle files if needed

## Notes

- The difficulty rating system (105-118) appears to be a proprietary or research-based metric
- Higher ratings generally indicate harder puzzles
- The distribution shows a concentration in the easier ranges (105, 111, 116), which is typical for puzzle databases
- All instances are standard 9×9 Sudoku puzzles
- Instances have been converted to individual `.txt` files in the `instances/paquita-database/` directory


