#!/usr/bin/env python3
"""
Convert HardestDatabase110626.txt to individual puzzle instance files.
Each puzzle is saved in the format expected by the solver.
"""

import os
import re
from pathlib import Path

def convert_puzzle_string_to_grid(puzzle_string):
    """
    Convert puzzle string (81 chars with '.' for empty) to 9x9 grid format.
    Returns a list of 9 lists, each with 9 values (-1 for empty, 1-9 for filled).
    """
    if len(puzzle_string) != 81:
        raise ValueError(f"Puzzle string must be 81 characters, got {len(puzzle_string)}")
    
    grid = []
    for i in range(9):
        row = []
        for j in range(9):
            char = puzzle_string[i * 9 + j]
            if char == '.':
                row.append(-1)
            elif char in '123456789':
                row.append(int(char))
            else:
                raise ValueError(f"Invalid character '{char}' in puzzle string")
        grid.append(row)
    
    return grid

def write_puzzle_file(output_path, puzzle_id, grid):
    """
    Write puzzle to file in the expected format:
    Line 1: order (3 for 9x9)
    Line 2: puzzle ID
    Lines 3-11: 9 rows of 9 values (tab-separated)
    """
    with open(output_path, 'w') as f:
        f.write('3\n')  # Order 3 = 9x9 Sudoku
        f.write(f'{puzzle_id}\n')
        
        for row in grid:
            f.write('\t'.join(str(val) for val in row) + '\n')

def extract_puzzle_name(line):
    """
    Extract a clean puzzle name from the metadata.
    Tries to get the label or generates a name from the line number.
    """
    # Try to extract label from metadata (e.g., "tarx0134" or "HardestSudokusThread-00001")
    parts = line.split(',')
    if len(parts) > 1:
        metadata = parts[1]
        # Look for patterns like "tarx0134" or use the thread ID
        match = re.search(r'(tarx\d+|pearly\d+-\d+|HardestSudokusThread-\d+)', metadata)
        if match:
            name = match.group(1).replace(';', '_').replace('-', '_')
            return name
    
    return None

def main():
    # Paths
    repo_root = Path(__file__).parent
    database_file = repo_root / 'HardestDatabase110626.txt'
    output_dir = repo_root / 'instances' / 'hardest-database'
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Read database file
    if not database_file.exists():
        print(f"Error: {database_file} not found!")
        return
    
    print(f"Reading {database_file}...")
    with open(database_file, 'r') as f:
        lines = f.readlines()
    
    # Skip header lines (first 2 lines)
    puzzle_lines = [line.strip() for line in lines[2:] if line.strip()]
    
    print(f"Found {len(puzzle_lines)} puzzles to convert")
    
    converted = 0
    skipped = 0
    
    for idx, line in enumerate(puzzle_lines, start=1):
        try:
            # Extract puzzle string (everything before the first comma)
            if ',' not in line:
                print(f"Warning: Line {idx} has no comma, skipping")
                skipped += 1
                continue
            
            puzzle_string = line.split(',')[0].strip()
            
            # Validate puzzle string
            if len(puzzle_string) != 81:
                print(f"Warning: Line {idx} has invalid puzzle length ({len(puzzle_string)}), skipping")
                skipped += 1
                continue
            
            # Convert to grid
            grid = convert_puzzle_string_to_grid(puzzle_string)
            
            # Generate filename
            puzzle_name = extract_puzzle_name(line)
            if not puzzle_name:
                puzzle_name = f"hardest_{idx:05d}"
            
            output_file = output_dir / f"{puzzle_name}.txt"
            
            # Write puzzle file
            write_puzzle_file(output_file, idx, grid)
            converted += 1
            
            if converted % 50 == 0:
                print(f"Converted {converted} puzzles...")
                
        except Exception as e:
            print(f"Error processing line {idx}: {e}")
            skipped += 1
            continue
    
    print(f"\nConversion complete!")
    print(f"  Converted: {converted} puzzles")
    print(f"  Skipped: {skipped} puzzles")
    print(f"  Output directory: {output_dir}")

if __name__ == '__main__':
    main()

















