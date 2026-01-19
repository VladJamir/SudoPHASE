# Simulated Annealing Integration into Parallel ACS

## Overview

This document describes the integration of Simulated Annealing (SA) from the CP-ACS-Simulated Annealing codebase into the Multi-threaded Ant Colony System implementation.

## Integration Strategy

The SA component has been integrated into the parallel ACS system to provide local search refinement capabilities. Each sub-colony can independently apply SA to its best solution at configurable intervals.

## Key Changes

### 1. New Files Added

- `src/simulatedannealing.h` - SA class header
- `src/simulatedannealing.cpp` - SA implementation (copied from CP-ACS codebase)

### 2. Modified Files

#### `src/parallelsudokuantsystem.h`
- Added `saFrequency` member variable to `ParallelSudokuAntSystem` class
- Updated constructor to accept `safreq` parameter (default: 0 = disabled)
- Made `PherAdd()` public in `SubColony` class for SA integration
- Added `UpdateBestSolution()` method to `SubColony` class

#### `src/parallelsudokuantsystem.cpp`
- Updated constructor to initialize `saFrequency`
- Added SA application logic in `SubColonyWorker()` method
- Implemented `UpdateBestSolution()` method in `SubColony` class
- Added `#include "simulatedannealing.h"`

#### `src/solvermain.cpp`
- Added `--safreq` command-line argument parsing
- Updated `ParallelSudokuAntSystem` instantiation to pass `safreq` parameter

#### `Makefile`
- Added `simulatedannealing.o` compilation target
- Updated linker command to include `simulatedannealing.o`

#### `README.md`
- Documented `--safreq` parameter

## How It Works

### SA Application Flow

1. **Periodic Application**: SA is applied every `safreq` iterations (if `safreq > 0`)
2. **Target Solution**: SA operates on each sub-colony's `best-so-far` solution
3. **Independent Execution**: Each sub-colony applies SA independently in its own thread
4. **Solution Update**: If SA finds an improved solution, the sub-colony's best solution is updated
5. **Early Termination**: If SA finds a complete solution (cost = 0), all threads stop immediately

### Integration Point

SA is applied in the `SubColonyWorker()` method, after pheromone updates and before progress reporting:

```cpp
// --- STEP 4: Apply Simulated Annealing (if enabled and at frequency interval) ---
if (saFrequency > 0 && iter % saFrequency == 0 && iter != 0)
{
    // Apply SA to best-so-far solution
    SudokuSA sa(colony->GetBestSol());
    int cost = sa.Anneal();
    Board saSolution = sa.GetSolution();
    
    // Update best solution if SA found improvement
    int saScore = saSolution.FixedCellCount();
    if (saScore > colony->GetBestSolScore())
    {
        colony->UpdateBestSolution(saSolution, saScore);
        
        // Check if SA found complete solution
        if (cost == 0 && saScore == puzzle.CellCount())
        {
            stopFlag.store(true);
            break;
        }
    }
}
```

## Usage

### Basic Usage (SA Disabled - Default)

```bash
./sudokusolver --alg 2 --file puzzle.txt --subcolonies 4 --ants 30 --timeout 120
```

### With Simulated Annealing

```bash
# Apply SA every 100 iterations (similar to original CP-ACS codebase)
./sudokusolver --alg 2 --file puzzle.txt --subcolonies 4 --ants 30 --timeout 120 --safreq 100 --verbose

# Apply SA more frequently (every 50 iterations)
./sudokusolver --alg 2 --file puzzle.txt --subcolonies 4 --ants 30 --timeout 120 --safreq 50 --verbose

# Apply SA less frequently (every 200 iterations)
./sudokusolver --alg 2 --file puzzle.txt --subcolonies 4 --ants 30 --timeout 120 --safreq 200 --verbose
```

## Design Decisions

### 1. Independent SA Application Per Sub-Colony

Each sub-colony applies SA to its own best solution independently. This maintains the parallel nature of the algorithm while allowing each colony to refine its solutions locally.

**Benefits:**
- No synchronization overhead for SA
- Each colony can escape local optima independently
- Maintains diversity across sub-colonies

### 2. SA Applied to Best-So-Far Solution

SA operates on the `best-so-far` solution (not `iteration-best`), similar to the original CP-ACS implementation.

**Rationale:**
- Best-so-far represents the colony's best discovery
- More stable target for local search
- Consistent with original CP-ACS design

### 3. Configurable Frequency

SA frequency is configurable via `--safreq` parameter, allowing users to tune the balance between ACS exploration and SA exploitation.

**Recommendations:**
- **Easy puzzles**: SA not needed (safreq = 0)
- **Medium puzzles**: safreq = 100-150
- **Hard puzzles**: safreq = 50-100 (more frequent refinement)

### 4. Thread-Safe Implementation

SA is applied independently in each thread without shared state, making it naturally thread-safe.

## Performance Considerations

### Overhead

- **SA Computation Time**: SA adds computational overhead proportional to puzzle difficulty
- **Frequency Impact**: Higher frequency (lower safreq) = more overhead but potentially better solutions
- **Parallel Benefit**: Overhead is distributed across threads

### Recommendations

1. **Start with safreq = 0** (disabled) to establish baseline performance
2. **Try safreq = 100** for medium puzzles (similar to original CP-ACS)
3. **Adjust based on results**: 
   - If solutions improve significantly → keep SA enabled
   - If overhead is too high → increase safreq (less frequent)
   - If still struggling → decrease safreq (more frequent)

## Comparison with Original CP-ACS

| Aspect | CP-ACS (Codebase 1) | Parallel ACS + SA (This Integration) |
|--------|---------------------|-------------------------------------|
| **SA Frequency** | Fixed: every 100 iterations | Configurable via `--safreq` |
| **SA Target** | Single best solution | Best solution per sub-colony |
| **Parallelism** | None | Each sub-colony applies SA independently |
| **Thread Safety** | N/A (single-threaded) | Thread-safe (independent execution) |
| **Default** | SA enabled (every 100 iter) | SA disabled (safreq = 0) |

## Future Enhancements

Potential improvements for future versions:

1. **Adaptive SA Frequency**: Adjust frequency based on solution quality improvement rate
2. **SA Parameter Tuning**: Make SA cooling rate and temperature configurable
3. **Selective SA Application**: Only apply SA to sub-colonies that show promise
4. **SA on Communication Solutions**: Apply SA to received solutions from other colonies
5. **Hybrid SA Strategy**: Different SA frequencies for different sub-colonies

## Testing

To verify the integration works correctly:

```bash
# Test with SA disabled (should work as before)
./sudokusolver --alg 2 --file instances/logic-solvable/platinumblond.txt --subcolonies 4 --ants 10 --timeout 30 --verbose

# Test with SA enabled
./sudokusolver --alg 2 --file instances/logic-solvable/platinumblond.txt --subcolonies 4 --ants 10 --timeout 30 --safreq 100 --verbose

# Compare results
```

## Notes

- SA is **disabled by default** (safreq = 0) to maintain backward compatibility
- SA application is **independent per sub-colony** - no synchronization required
- SA can find complete solutions, triggering immediate termination
- The integration maintains the original parallel ACS communication and pheromone update mechanisms

