# Simulated Annealing Flow Explanation

This document explains how Simulated Annealing (SA) works in this codebase, following the flowchart structure.

---

## Overview

Simulated Annealing is a **local search metaheuristic** that refines solutions found by the Ant Colony Optimization algorithm. It takes the **BEST ANT** solution as input and uses a temperature-based acceptance mechanism to explore the solution space.

---

## Flowchart Components

### 1. **INPUT: BEST ANT** 🐜

**What it is**: The best solution found by the Ant Colony System algorithm.

**In Code**:
```cpp
// From parallelsudokuantsystem.cpp line 658
SudokuSA sa(colony->GetBestSol());  // BEST ANT solution passed to SA
```

**Example**:
- ACO finds a solution with 75 cells filled (out of 81)
- This solution is passed to SA for refinement

---

### 2. **INITIALIZATION** ⚙️

**Purpose**: Set up the initial state for the optimization process.

**What happens**:

#### 2.1 Fill Empty Cells
```cpp
FillEmptyCells();  // Line 12 in simulatedannealing.cpp
```
- Fills all empty cells in each 3×3 box (for 9×9 Sudoku) with missing digits
- Ensures each box has all digits 1-9 (no duplicates within boxes)
- Creates a **complete but potentially invalid** solution (may have row/column conflicts)

**Example**:
```
Before: Box 1 has [1, 2, 3, _, _, _, _, _, _]
After:  Box 1 has [1, 2, 3, 4, 5, 6, 7, 8, 9] (randomly shuffled)
```

#### 2.2 Initialize Temperature Parameters
```cpp
double coolingRate = 0.995;      // Temperature reduction factor
double stoppingTemp = 0.01;      // When to stop
double temp = 1.5;               // Initial temperature
```

**Parameters**:
- `temp = 1.5`: High initial temperature (allows exploration)
- `stoppingTemp = 0.01`: Stop when temperature drops this low
- `coolingRate = 0.995`: Each cycle, temperature = temp × 0.995

#### 2.3 Compute Initial Cost
```cpp
int currentCost = ComputeCost();  // Line 17
```

**Cost Function** (from `ComputeCost()`):
- **Empty cells**: +1 per empty cell
- **Row duplicates**: +1 per duplicate value in a row
- **Column duplicates**: +1 per duplicate value in a column

**Example**:
```
Solution has:
- 0 empty cells
- 3 duplicate values in row 2
- 2 duplicate values in column 5
Cost = 0 + 3 + 2 = 5
```

#### 2.4 Initialize Best Solution
```cpp
bestSol.Copy(sol);
bestCost = currentCost;
```

**Early Exit Check**:
```cpp
if (currentCost == 0) {
    return currentCost;  // Already solved!
}
```

---

### 3. **ITERATIVE LOOP: while temp > stopTemp** 🔄

The core optimization loop runs while temperature is above the stopping threshold.

#### Loop Structure
```cpp
while(temp > stoppingTemp) {  // Line 35
    // NEIGHBORHOOD OPERATOR
    // SOLUTION ACCEPTANCE
    // TEMPERATURE COOLING
}
```

**Example Temperature Progression**:
| Cycle | Temperature | Calculation |
|-------|-------------|-------------|
| 0 | 1.500 | Initial |
| 1 | 1.493 | 1.500 × 0.995 |
| 2 | 1.485 | 1.493 × 0.995 |
| 10 | 1.428 | 1.500 × 0.995^10 |
| 100 | 0.905 | 1.500 × 0.995^100 |
| 200 | 0.546 | 1.500 × 0.995^200 |
| 500 | 0.122 | 1.500 × 0.995^500 |
| 1000 | 0.010 | 1.500 × 0.995^1000 ≈ stopTemp |

**Approximate cycles**: ~1000 cycles to reach stopping temperature

---

### 3.1 **NEIGHBORHOOD OPERATOR** 🔀

**Purpose**: Generate a new candidate solution by making a small change.

**Implementation**: `TryRandomSwap(oldCost)` (line 40)

#### How It Works:

1. **Identify Conflict Cells**:
   - Finds cells involved in row or column conflicts (duplicates)
   - Prioritizes cells with more conflicts

2. **Select First Cell**:
   - Randomly picks a cell from conflicted cells
   - Example: Cell at position (2, 5) has value 7, conflicts with row 2

3. **Select Second Cell** (Swap Partner):
   - Must be in the **same 3×3 box** as first cell
   - Must be **non-fixed** (not a clue)
   - Example: Cell at position (1, 4) in same box, has value 3

4. **Perform Swap**:
   ```cpp
   // Swap values between two cells
   ValueSet v1 = sol.GetCell(idx1);  // Cell 1 has value 7
   ValueSet v2 = sol.GetCell(idx2);  // Cell 2 has value 3
   sol.ForceSetCell(idx1, v2);       // Cell 1 now has value 3
   sol.ForceSetCell(idx2, v1);       // Cell 2 now has value 7
   ```

5. **Compute New Cost**:
   - Calculates cost **incrementally** (only checks affected cells)
   - Returns: `oldCost + (after - before)`

**Example**:
```
Before swap:
  Row 2: [1, 2, 7, 4, 5, 7, 8, 9, 3]  (duplicate 7 at positions 2 and 5)
  Cost = 5

After swapping cell(2,2) and cell(1,4):
  Row 2: [1, 2, 3, 4, 5, 7, 8, 9, 3]  (duplicate 3 at positions 2 and 8)
  New cost = 5 + (1 - 1) = 5  (same cost, different conflict)
```

---

### 3.2 **SOLUTION ACCEPTANCE** ✅❌

**Purpose**: Decide whether to accept or reject the new candidate solution.

**Decision Logic**:

```cpp
int delta = newCost - currentCost;  // Cost difference

if (delta <= 0) {
    // BETTER or EQUAL solution - ALWAYS ACCEPT
    currentCost = newCost;
    if (currentCost < bestCost) {
        bestSol.Copy(sol);  // Update best solution
        bestCost = currentCost;
    }
}
else {
    // WORSE solution - ACCEPT WITH PROBABILITY
    acceptanceProbability = exp(-delta / temp);
    double rnd = (double) rand() / RAND_MAX;
    if (rnd < acceptanceProbability) {
        currentCost = newCost;  // Accept worse solution
    }
    else {
        sol.Copy(currentSol);  // Reject - revert to previous
    }
}
```

#### Case 1: Better or Equal Solution (delta ≤ 0)

**Always Accepted** ✅

**Example**:
```
Current cost: 5
New cost: 3
Delta: -2 (better!)

Result: ACCEPT, update currentCost = 3
```

#### Case 2: Worse Solution (delta > 0)

**Accepted with Probability** 🎲

**Acceptance Probability Formula**:
```
P(accept) = exp(-delta / temp)
```

**Key Insight**: 
- **High temperature**: More likely to accept worse solutions (exploration)
- **Low temperature**: Less likely to accept worse solutions (exploitation)
- **Large delta**: Less likely to accept (bigger cost increase)

**Example Calculations**:

| Temperature | Delta | exp(-delta/temp) | Accept? |
|-------------|-------|------------------|---------|
| 1.5 (high) | 2 | exp(-2/1.5) = 0.264 | 26.4% chance |
| 1.5 (high) | 5 | exp(-5/1.5) = 0.036 | 3.6% chance |
| 0.5 (medium) | 2 | exp(-2/0.5) = 0.018 | 1.8% chance |
| 0.1 (low) | 2 | exp(-2/0.1) = 0.000002 | ~0% chance |

**Example Scenario**:
```
Current cost: 5
New cost: 7
Delta: +2 (worse)
Temperature: 1.5

Acceptance probability = exp(-2/1.5) = 0.264

Random number generated: 0.15
Since 0.15 < 0.264: ACCEPT (lucky!)
Update: currentCost = 7

Next iteration:
Random number generated: 0.80
Since 0.80 > 0.264: REJECT
Revert: sol = previous solution, currentCost = 5
```

**Why Accept Worse Solutions?**
- Allows **escaping local optima**
- Early in search (high temp): explore widely
- Later in search (low temp): focus on good solutions

---

### 3.3 **TEMPERATURE COOLING** ❄️

**Purpose**: Gradually reduce temperature to shift from exploration to exploitation.

**Implementation**:
```cpp
temp = temp * coolingRate;  // Line 73
// coolingRate = 0.995
```

**Cooling Schedule**: Geometric cooling
- Each cycle: `temp = temp × 0.995`
- Temperature decreases **exponentially**

**Effect on Acceptance**:

| Temperature | Accept delta=+2? | Accept delta=+5? |
|-------------|------------------|------------------|
| 1.5 | 26.4% | 3.6% |
| 1.0 | 13.5% | 0.7% |
| 0.5 | 1.8% | 0.00005% |
| 0.1 | ~0% | ~0% |

**Behavior Evolution**:
- **Early cycles** (temp ≈ 1.5): Accepts many worse solutions → **exploration**
- **Middle cycles** (temp ≈ 0.5): Accepts few worse solutions → **transition**
- **Late cycles** (temp ≈ 0.01): Accepts almost no worse solutions → **exploitation**

---

## Complete Example: 5 Cycles

Let's trace through 5 cycles of Simulated Annealing:

### Initial State
- **Input**: Solution with 75 cells filled, cost = 8
- **Temperature**: 1.5
- **Best cost**: 8

---

### Cycle 1

**Temperature**: 1.5

**Neighborhood Operator**:
- Swaps two cells in box 1
- **New cost**: 6 (better!)

**Solution Acceptance**:
- Delta = 6 - 8 = -2 (better)
- **ACCEPT** ✅
- Update: currentCost = 6
- Update: bestCost = 6, bestSol = new solution

**Temperature Cooling**:
- New temp = 1.5 × 0.995 = **1.493**

---

### Cycle 2

**Temperature**: 1.493

**Neighborhood Operator**:
- Swaps two cells in box 3
- **New cost**: 7 (worse)

**Solution Acceptance**:
- Delta = 7 - 6 = +1 (worse)
- Acceptance probability = exp(-1/1.493) = **0.513**
- Random number: 0.35
- Since 0.35 < 0.513: **ACCEPT** ✅
- Update: currentCost = 7

**Temperature Cooling**:
- New temp = 1.493 × 0.995 = **1.485**

---

### Cycle 3

**Temperature**: 1.485

**Neighborhood Operator**:
- Swaps two cells in box 5
- **New cost**: 9 (worse)

**Solution Acceptance**:
- Delta = 9 - 7 = +2 (worse)
- Acceptance probability = exp(-2/1.485) = **0.260**
- Random number: 0.75
- Since 0.75 > 0.260: **REJECT** ❌
- Revert: sol = previous solution, currentCost = 7

**Temperature Cooling**:
- New temp = 1.485 × 0.995 = **1.478**

---

### Cycle 4

**Temperature**: 1.478

**Neighborhood Operator**:
- Swaps two cells in box 2
- **New cost**: 5 (better!)

**Solution Acceptance**:
- Delta = 5 - 7 = -2 (better)
- **ACCEPT** ✅
- Update: currentCost = 5
- Update: bestCost = 5, bestSol = new solution

**Temperature Cooling**:
- New temp = 1.478 × 0.995 = **1.471**

---

### Cycle 5

**Temperature**: 1.471

**Neighborhood Operator**:
- Swaps two cells in box 7
- **New cost**: 6 (worse)

**Solution Acceptance**:
- Delta = 6 - 5 = +1 (worse)
- Acceptance probability = exp(-1/1.471) = **0.512**
- Random number: 0.20
- Since 0.20 < 0.512: **ACCEPT** ✅
- Update: currentCost = 6

**Temperature Cooling**:
- New temp = 1.471 × 0.995 = **1.464**

**Continue until temp < 0.01...**

---

## 4. **OUTPUT: CANDIDATE SOLUTION** 🎯

**When Loop Ends**:
- Temperature drops below `stoppingTemp` (0.01)
- OR solution found (cost = 0)

**Final Steps**:
```cpp
CleanDuplicates();  // Line 93 - Remove conflicts by clearing worst duplicate cells
return bestCost;    // Return cost of best solution found
```

**Output**:
- **Best solution** found during annealing process
- **Cost** of that solution (0 = solved, >0 = conflicts remain)

---

### What Happens When Cost > 0? ⚠️

**Important**: Even if Simulated Annealing doesn't find a perfect solution (cost > 0), the solution is **still useful** and can be integrated back into ACO!

#### Step 1: CleanDuplicates() - Conflict Resolution

Before returning, `CleanDuplicates()` is called to **reduce conflicts**:

**How it works**:
1. **Identifies duplicates** in rows and columns
2. **Counts conflicts** for each cell (how many duplicates it participates in)
3. **Removes worst duplicates** by clearing the cell with highest conflict count
4. **Result**: Fewer conflicts, but may create empty cells

**Example**:
```
Before CleanDuplicates():
  Row 2: [1, 2, 7, 4, 5, 7, 8, 9, 3]  (duplicate 7 at positions 2 and 5)
  Row 3: [2, 3, 4, 5, 6, 2, 8, 9, 1]  (duplicate 2 at positions 0 and 5)
  Cost = 2 conflicts

After CleanDuplicates():
  Row 2: [1, 2, 7, 4, 5, _, 8, 9, 3]  (removed duplicate at position 5)
  Row 3: [2, 3, 4, 5, 6, _, 8, 9, 1]  (removed duplicate at position 5)
  Cost = 0 conflicts, but 2 empty cells
```

**Key Point**: `CleanDuplicates()` **trades conflicts for empty cells**. This is acceptable because:
- Empty cells can be filled by ACO in future iterations
- Conflicts are harder to resolve and indicate invalid solutions

#### Step 2: Return Solution with Cost > 0

```cpp
return bestCost;  // May be > 0 if conflicts remain
```

**Example Scenarios**:

| Scenario | bestCost | Meaning |
|----------|----------|---------|
| Perfect | 0 | No conflicts, all cells filled |
| Good | 2 | 2 empty cells (after CleanDuplicates) |
| Acceptable | 5 | 5 empty cells, but no conflicts |
| Poor | 10 | 10 empty cells, but still better than input |

#### Step 3: Integration Back to ACO

**Code**:
```cpp
// From parallelsudokuantsystem.cpp lines 658-675
SudokuSA sa(colony->GetBestSol());
int cost = sa.Anneal();              // Returns bestCost (may be > 0)
Board saSolution = sa.GetSolution();
int saScore = saSolution.FixedCellCount();  // Count filled cells

// Update if SA solution has MORE filled cells
if (saScore > colony->GetBestSolScore()) {
    colony->UpdateBestSolution(saSolution, saScore);
    
    // Only stop if cost = 0 AND all cells filled
    if (cost == 0 && saScore == puzzle.CellCount()) {
        stopFlag.store(true);  // Solved!
    }
}
```

**Integration Criteria**:
- **Uses**: `saScore` (number of filled cells), **NOT** `cost`
- **Updates if**: `saScore > colony->GetBestSolScore()`
- **Stops only if**: `cost == 0` AND `saScore == puzzle.CellCount()`

**Why This Works**:

1. **Even with cost > 0, solution can be better**:
   ```
   ACO best: 75 cells filled, 3 conflicts
   SA output: 78 cells filled, 0 conflicts (cost = 2 empty cells)
   
   saScore (78) > ACO best (75) → UPDATE ✅
   ```

2. **CleanDuplicates() makes solution valid**:
   - Removes conflicts (invalid → valid)
   - Creates empty cells (can be filled by ACO)
   - Better than keeping conflicts

3. **ACO can continue improving**:
   - SA provides a **valid partial solution**
   - ACO uses pheromones to fill remaining empty cells
   - Next SA application may complete it

**Complete Example**:

```
ACO Iteration 100:
  Input to SA: 75 cells filled, 5 conflicts
  SA runs: Finds solution with 78 cells filled, 2 conflicts
  CleanDuplicates(): Removes conflicts → 76 cells filled, 0 conflicts
  cost = 2 (2 empty cells)
  saScore = 76
  
  Integration:
    saScore (76) > ACO best (75) → UPDATE ✅
    cost = 2 > 0 → Continue (don't stop)

ACO Iteration 200:
  Input to SA: 76 cells filled, 0 conflicts
  SA runs: Finds solution with 80 cells filled, 0 conflicts
  CleanDuplicates(): No conflicts to clean → 80 cells filled
  cost = 1 (1 empty cell)
  saScore = 80
  
  Integration:
    saScore (80) > ACO best (76) → UPDATE ✅
    cost = 1 > 0 → Continue

ACO Iteration 300:
  Input to SA: 80 cells filled, 0 conflicts
  SA runs: Finds solution with 81 cells filled, 0 conflicts
  CleanDuplicates(): No conflicts → 81 cells filled
  cost = 0 (solved!)
  saScore = 81
  
  Integration:
    saScore (81) > ACO best (80) → UPDATE ✅
    cost = 0 AND saScore == 81 → STOP! 🎉
```

---

### Summary: Cost > 0 Handling

| Aspect | Details |
|--------|---------|
| **CleanDuplicates()** | Removes conflicts by clearing worst duplicate cells |
| **Result** | Fewer conflicts, but may have empty cells |
| **Cost** | Counts empty cells + remaining conflicts |
| **Integration** | Uses `saScore` (filled cells), not `cost` |
| **Update Condition** | `saScore > current best` (even if cost > 0) |
| **Stop Condition** | `cost == 0` AND `saScore == puzzle.CellCount()` |
| **Why It Works** | Valid partial solutions are better than invalid ones |

**Key Insight**: A solution with **cost > 0 but more filled cells** is still valuable because:
1. It's **valid** (no conflicts after CleanDuplicates)
2. It has **more information** (more cells filled)
3. ACO can **continue improving** it in future iterations

---

## Key Concepts Summary

| Concept | Description | Example |
|---------|-------------|---------|
| **Temperature** | Controls acceptance of worse solutions | High (1.5) = explore, Low (0.01) = exploit |
| **Cooling Rate** | How fast temperature decreases | 0.995 = 0.5% reduction per cycle |
| **Neighborhood** | Small change to current solution | Swap two values in same box |
| **Acceptance** | Probability of accepting worse solution | exp(-delta/temp) |
| **Cost Function** | Measures solution quality | Empty cells + row/column duplicates |

---

## Why Simulated Annealing Works

1. **Exploration Phase** (High Temperature):
   - Accepts many worse solutions
   - Explores diverse regions of solution space
   - Escapes local optima

2. **Exploitation Phase** (Low Temperature):
   - Accepts few worse solutions
   - Focuses on refining good solutions
   - Converges to local optimum

3. **Balance**:
   - Starts with exploration (find promising regions)
   - Gradually shifts to exploitation (refine best region)
   - Temperature schedule controls this transition

---

## Integration with ACO

**When Applied**:
- At regular intervals (e.g., every 100 iterations)
- Only if `saFrequency > 0`
- Applied to **best-so-far solution** from ACO

**Purpose**:
- **Local refinement** of ACO solutions
- Fixes conflicts that ACO might miss
- Can complete partial solutions

**Example**:
```
ACO Iteration 100:
  Best solution: 75 cells filled, some conflicts
  Apply SA → Refines to 78 cells, fewer conflicts
  Update ACO best solution

ACO Iteration 200:
  Best solution: 78 cells filled
  Apply SA → Refines to 81 cells (SOLVED!)
  Return complete solution
```

---

## Parameters

| Parameter | Value | Effect |
|-----------|-------|--------|
| `temp` | 1.5 | Initial temperature (exploration) |
| `stoppingTemp` | 0.01 | When to stop (exploitation) |
| `coolingRate` | 0.995 | Temperature reduction per cycle |
| `saFrequency` | 0-1000 | How often to apply SA (0 = disabled) |

---

This Simulated Annealing implementation provides a powerful local search mechanism that complements the global search of Ant Colony Optimization, helping to refine and complete solutions found by the ACO algorithm.


