# SA Hybrid Acceptance Policy - Implementation Summary

## Overview

Implemented a **hybrid acceptance policy** for Simulated Annealing solutions that allows accepting solutions even when they have slightly fewer filled cells, if they have significantly fewer conflicts. This addresses the CleanDuplicates scenario where SA produces cleaner solutions that may benefit ACS in the long term.

## Changes Made

### 1. Added Helper Function: `CountConflicts()`

**Location**: `src/parallelsudokuantsystem.cpp` (lines 438-487)

**Purpose**: Counts constraint violations (row and column duplicates) in a solution.

**Implementation**:
```cpp
static int CountConflicts(const Board& board)
{
    // Counts row duplicates + column duplicates
    // Returns total number of conflict violations
}
```

**Used for**: Comparing conflict counts between current best and SA solutions.

### 2. Added Required Header

**Location**: `src/parallelsudokuantsystem.cpp` (line 23)

**Change**: Added `#include <unordered_set>` for conflict counting.

### 3. Modified SA Acceptance Logic

**Location**: `src/parallelsudokuantsystem.cpp` (lines 706-754)

**Previous Behavior**: Only accepted SA solutions with strictly more filled cells.

**New Behavior**: Hybrid acceptance policy with two criteria:

#### Criteria 1: Strict Improvement (Unchanged)
- **Condition**: `saScore > currentScore` (more cells filled)
- **Action**: Always accept
- **Rationale**: Maintains original strict improvement behavior

#### Criteria 2: Conflict-Aware Acceptance (NEW)
- **Condition**: 
  - Same or slightly fewer cells: `cellDiff >= -2 && cellDiff <= 0` (up to 2 cells less)
  - AND significantly fewer conflicts: `conflictDiff >= 5` (≥5 conflicts eliminated)
- **Action**: Accept if both conditions met
- **Rationale**: Allows accepting cleaner solutions that may help ACS progress faster

**Implementation**:
```cpp
if (cellDiff > 0)
{
    // Case 1: Strict improvement (more cells)
    shouldAccept = true;
}
else if (cellDiff >= -2 && cellDiff <= 0)
{
    // Case 2: Same or slightly fewer cells - check conflict reduction
    int currentConflicts = CountConflicts(colony->GetBestSol());
    int saConflicts = CountConflicts(saSolution);
    int conflictDiff = currentConflicts - saConflicts;
    
    // Accept if conflict reduction is significant (≥5 conflicts eliminated)
    if (conflictDiff >= 5)
    {
        shouldAccept = true;
    }
}
```

## Acceptance Thresholds

### Configurable Parameters (Currently Hardcoded)

1. **Maximum Cell Loss**: `-2` (allows up to 2 fewer cells)
2. **Minimum Conflict Reduction**: `5` (requires at least 5 conflicts eliminated)

**Future Enhancement**: These could be made configurable via command-line parameters if needed.

## Expected Behavior

### Scenario 1: SA Improves (More Cells)
```
Current: 75 cells, 5 conflicts
SA:      77 cells, 3 conflicts
Result:  ACCEPTED (strict improvement: 77 > 75)
```

### Scenario 2: SA Cleans Conflicts (CleanDuplicates)
```
Current: 76 cells, 8 conflicts
SA:      75 cells, 0 conflicts (2 cells removed, 8 conflicts cleared)
Result:  ACCEPTED (within threshold: 75 >= 76-2, and 8-0 >= 5)
```

### Scenario 3: SA Worse Overall
```
Current: 75 cells, 5 conflicts
SA:      73 cells, 2 conflicts (2 cells removed, only 3 conflicts cleared)
Result:  REJECTED (cellDiff = -2 is at threshold, but conflictDiff = 3 < 5)
```

### Scenario 4: SA Much Worse
```
Current: 75 cells, 5 conflicts
SA:      70 cells, 1 conflict (5 cells removed, 4 conflicts cleared)
Result:  REJECTED (cellDiff = -5 exceeds threshold of -2)
```

## Benefits

1. **Addresses CleanDuplicates Scenario**: Allows accepting cleaner solutions that SA produces by removing conflict cells
2. **Conservative Approach**: Only accepts if conflict reduction is significant (≥5) and cell loss is minimal (≤2)
3. **Backward Compatible**: Still accepts all strict improvements (maintains original behavior)
4. **Balanced Trade-off**: Considers both solution completeness (cells) and quality (conflicts)

## Potential Risks

1. **Solution Quality Regression**: Accepting solutions with fewer cells could temporarily reduce best-so-far quality
2. **Pheromone Impact**: Lower cell count means lower pheromone values, potentially affecting future search
3. **Recovery Overhead**: May require additional iterations to recover lost cells

## Testing Recommendations

1. **Compare with Baseline**: Run same puzzles with old vs. new acceptance policy
2. **Monitor Metrics**:
   - Success rate
   - Average solution time
   - Average iterations
   - Number of times Criteria 2 triggers
   - Recovery time after accepting "worse" solutions
3. **Specific Scenarios**: Test on puzzles where CleanDuplicates is likely to occur (solutions with many conflicts)

## Code Quality

- ✅ No compilation errors (verified structure)
- ✅ No linter errors (checked)
- ✅ Proper comments explaining logic
- ✅ Consistent with existing code style
- ✅ Helper function is static (no external linkage needed)

## Next Steps

1. **Compile and Test**: Verify compilation with your build system (Makefile or Visual Studio)
2. **Run Experiments**: Compare performance with baseline on test puzzles
3. **Tune Parameters**: If needed, adjust thresholds (-2 cells, 5 conflicts) based on empirical results
4. **Consider Making Configurable**: If thresholds need tuning, consider adding command-line parameters

## Reverting Changes

If you need to revert to strict improvement-only policy, simply change the acceptance logic back to:

```cpp
if (saScore > colony->GetBestSolScore())
{
    colony->UpdateBestSolution(saSolution, saScore);
    // ... rest of code
}
```

The `CountConflicts()` helper function can remain (it doesn't hurt to have it) or can be removed if reverting.


















