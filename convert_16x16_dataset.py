#!/usr/bin/env python3
"""
Convert 16x16Dataset.csv to individual puzzle instance files.
Each puzzle is saved in the format expected by the solver.
The CSV format is: Sudoku,solution
The puzzle string is 256 characters (16x16) with '0' or '.' for empty cells and '0'-'9', 'A'-'F' for filled cells.
"""

import csv
import os
from pathlib import Path

def convert_puzzle_string_to_grid(puzzle_string):
    """
    Convert puzzle string (256 chars for 16x16) to 16x16 grid format.
    Returns a list of 16 lists, each with 16 values (-1 for empty, 1-16 for filled).
    
    For 16x16 sudoku:
    - '0'-'9' map to values 1-10
    - 'A'-'F' (or 'a'-'f') map to values 11-16
    - '.' or '0' for empty cells -> -1
    """
    if len(puzzle_string) != 256:
        raise ValueError(f"Puzzle string must be 256 characters for 16x16, got {len(puzzle_string)}")
    
    grid = []
    for i in range(16):
        row = []
        for j in range(16):
            char = puzzle_string[i * 16 + j]
            if char == '.' or char == '0':
                # In CSV format, '0' represents empty cells
                row.append(-1)
            elif char in '123456789':
                # '1'-'9' map directly to values 1-9
                row.append(int(char))
            elif char in 'ABCDEF':
                # 'A'-'F' map to values 10-15 (A=10, B=11, ..., F=15)
                row.append(10 + (ord(char) - ord('A')))
            elif char in 'abcdef':
                # 'a'-'f' map to values 10-15 (same as uppercase)
                row.append(10 + (ord(char) - ord('a')))
            elif char == 'G' or char == 'g':
                # 'G' represents value 16
                row.append(16)
            else:
                raise ValueError(f"Invalid character '{char}' in puzzle string at position {i*16+j}")
        grid.append(row)
    
    return grid

def write_puzzle_file(output_path, puzzle_id, grid):
    """
    Write puzzle to file in the expected format:
    Line 1: order (4 for 16x16)
    Line 2: puzzle ID
    Lines 3-18: 16 rows of 16 values (tab-separated)
    """
    with open(output_path, 'w') as f:
        f.write('4\n')  # Order 4 = 16x16 Sudoku
        f.write(f'{puzzle_id}\n')
        
        for row in grid:
            f.write('\t'.join(str(val) for val in row) + '\n')

def main():
    # Paths
    repo_root = Path(__file__).parent
    database_file = repo_root / 'instances' / '16x16Dataset.csv'
    output_dir = repo_root / 'instances' / '16x16-database'
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Read database file
    if not database_file.exists():
        print(f"Error: {database_file} not found!")
        return
    
    print(f"Reading {database_file}...")
    converted = 0
    skipped = 0
    
    with open(database_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for idx, row in enumerate(reader, start=1):
            try:
                # Get puzzle string (first column)
                puzzle_string = row['Sudoku'].strip()
                
                # Validate puzzle string
                if len(puzzle_string) != 256:
                    print(f"Warning: Line {idx+1} has invalid puzzle length ({len(puzzle_string)}), skipping")
                    skipped += 1
                    continue
                
                # Convert to grid
                grid = convert_puzzle_string_to_grid(puzzle_string)
                
                # Generate filename
                puzzle_name = f"16x16_{idx:05d}"
                
                output_file = output_dir / f"{puzzle_name}.txt"
                
                # Write puzzle file
                write_puzzle_file(output_file, idx, grid)
                converted += 1
                
                if converted % 50 == 0:
                    print(f"Converted {converted} puzzles...")
                    
            except Exception as e:
                print(f"Error processing line {idx+1}: {e}")
                skipped += 1
                continue
    
    print(f"\nConversion complete!")
    print(f"  Converted: {converted} puzzles")
    print(f"  Skipped: {skipped} puzzles")
    print(f"  Output directory: {output_dir}")

if __name__ == '__main__':
    main()

