# Best Value Evaporation (BVE): Explanation with Examples

## Overview

**Best Value Evaporation** (BVE) is a decay mechanism applied to `bestPher`, which is the pheromone value associated with the best-so-far solution. This decay prevents the algorithm from getting locked into local optima by gradually reducing the influence of older solutions over time.

---

## What is `bestPher`?

`bestPher` is a scalar value representing the **quality** of the best-so-far solution, calculated using:

```
bestPher = numCells / (numCells - cellsFilled)
```

This formula produces exponentially increasing values as solutions approach completion:
- 50 cells filled: `81/(81-50) = 2.61`
- 75 cells filled: `81/(81-75) = 13.5`
- 80 cells filled: `81/(81-80) = 81.0`

---

## The Evaporation Formula

### Basic Formula

```cpp
bestPher *= (1.0f - bestEvap)
```

Where:
- `bestEvap = 0.005` (default, 0.5% decay per iteration)
- Applied **after** standard global pheromone updates
- Applied **only** on non-communication iterations (when using standard Algorithm 0 update)

### Implementation Location

In the code (`parallelsudokuantsystem.cpp`, line 651):

```cpp
// Standard Algorithm 0 Global Pheromone Update
colony->UpdatePheromone();

// Decay Best Pheromone (only on non-comm iterations)
colony->bestPher *= (1.0f - colony->bestEvap);
```

**Important**: BVE is **NOT** applied after communication updates, only after standard updates.

---

## Why is Best Value Evaporation Needed?

### Problem Without Decay: Lock-In Effect

If `bestPher` never decays, the algorithm can become "locked" to an early good solution:

**Scenario**: Algorithm finds a solution with 70 cells filled at iteration 10.

| Iteration | bestPher | Pheromone Reinforcement | Result |
|-----------|----------|------------------------|--------|
| 10 | 7.36 | Strong (7.36) | Good exploration |
| 11-20 | 7.36 (constant) | Strong (7.36) | Pheromones converge |
| 21-50 | 7.36 (constant) | Strong (7.36) | **LOCKED IN** |
| 51 | 7.36 | Cannot escape | Algorithm stuck |

**Problem**: After ~20 iterations, pheromones converge to the `bestPher` value. Even if a better solution is found later, the pheromone matrix is already locked to the old pattern, making it difficult to escape.

### Solution With Decay: Gradual Weakening

BVE gradually reduces `bestPher`, making it easier to replace with better solutions:

| Iteration | bestPher (with 0.5% decay) | Effect |
|-----------|---------------------------|--------|
| 10 | 7.36 | Initial strong solution |
| 20 | 7.36 × 0.995^10 = **7.00** | Slightly weakened |
| 30 | 7.36 × 0.995^20 = **6.65** | Noticeably weaker |
| 40 | 7.36 × 0.995^30 = **6.32** | Much weaker |
| 50 | 7.36 × 0.995^40 = **6.00** | Significantly reduced |

**Benefit**: At iteration 51, if a better solution with `pherToAdd = 9.0` is found:
- Current `bestPher = 6.00` (decayed from 7.36)
- New `pherToAdd = 9.0`
- Since `9.0 > 6.0`, the update occurs easily ✅

---

## Detailed Example: 5 Iterations

Let's trace a complete example with a 9×9 Sudoku (81 cells):

### Parameters
- `numCells = 81`
- `bestEvap = 0.005` (0.5% decay)
- `rho = 0.9` (standard evaporation rate)
- Initial `bestPher = 0.0`

---

### Iteration 1

**Step 1: Solution Construction**
- Best ant fills: **50 cells**
- Calculate new pheromone value: `pherToAdd = 81/(81-50) = 2.61`
- Compare: `2.61 > 0.0` → **UPDATE**
  - `bestPher = 2.61`
  - `bestSol` = solution with 50 cells

**Step 2: Standard Pheromone Update**
- For cells in best-so-far solution:
  - Example: `pher[10][5] = 0.5` (cell 10 has digit 5 in best-so-far)
  - Update: `pher[10][5] = 0.5 × 0.1 + 0.9 × 2.61 = 0.05 + 2.35 = **2.40**`

**Step 3: Best Value Evaporation**
- `bestPher = 2.61 × (1 - 0.005) = 2.61 × 0.995 = **2.60**`

**After Iteration 1**: `bestPher = 2.60`

---

### Iteration 2

**Step 1: Solution Construction**
- Best ant fills: **55 cells**
- Calculate: `pherToAdd = 81/(81-55) = 3.12`
- Compare: `3.12 > 2.60` → **UPDATE**
  - `bestPher = 3.12`
  - `bestSol` = solution with 55 cells

**Step 2: Pheromone Update**
- `pher[10][5] = 2.40 × 0.1 + 0.9 × 3.12 = 0.24 + 2.81 = **3.05**`

**Step 3: Best Value Evaporation**
- `bestPher = 3.12 × 0.995 = **3.10**`

**After Iteration 2**: `bestPher = 3.10`

---

### Iteration 3 (No Improvement)

**Step 1: Solution Construction**
- Best ant fills: **52 cells** (worse than iteration 2!)
- Calculate: `pherToAdd = 81/(81-52) = 2.79`
- Compare: `2.79 < 3.10` → **NO UPDATE**
  - `bestPher` stays at **3.10**
  - `bestSol` stays at 55 cells

**Step 2: Pheromone Update**
- Still reinforce the best-so-far (55 cells):
  - `pher[10][5] = 3.05 × 0.1 + 0.9 × 3.10 = 0.31 + 2.79 = **3.10**`

**Step 3: Best Value Evaporation**
- `bestPher = 3.10 × 0.995 = **3.08**`

**Key Point**: Even though this iteration was worse, we still reinforce the best-so-far, but `bestPher` decays slightly. This makes it **easier** to find a better solution later.

**After Iteration 3**: `bestPher = 3.08`

---

### Iteration 4 (Improvement)

**Step 1: Solution Construction**
- Best ant fills: **60 cells** (better!)
- Calculate: `pherToAdd = 81/(81-60) = 3.86`
- Compare: `3.86 > 3.08` → **UPDATE**
  - `bestPher = 3.86`
  - `bestSol` = solution with 60 cells

**Step 2: Pheromone Update**
- `pher[10][5] = 3.10 × 0.1 + 0.9 × 3.86 = 0.31 + 3.47 = **3.78**`

**Step 3: Best Value Evaporation**
- `bestPher = 3.86 × 0.995 = **3.84**`

**After Iteration 4**: `bestPher = 3.84`

---

### Iteration 5 (No Improvement Again)

**Step 1: Solution Construction**
- Best ant fills: **58 cells** (worse)
- Calculate: `pherToAdd = 81/(81-58) = 3.52`
- Compare: `3.52 < 3.84` → **NO UPDATE**
  - `bestPher` stays at **3.84**

**Step 2: Pheromone Update**
- `pher[10][5] = 3.78 × 0.1 + 0.9 × 3.84 = 0.38 + 3.46 = **3.84**`

**Step 3: Best Value Evaporation**
- `bestPher = 3.84 × 0.995 = **3.82**`

**After Iteration 5**: `bestPher = 3.82`

---

## Summary Table: Evolution Over Time

| Iteration | Cells Filled | pherToAdd | bestPher (before decay) | bestPher (after decay) | Update? |
|-----------|--------------|-----------|------------------------|------------------------|---------|
| 1 | 50 | 2.61 | 2.61 | 2.60 | ✅ Yes |
| 2 | 55 | 3.12 | 3.12 | 3.10 | ✅ Yes |
| 3 | 52 | 2.79 | 3.10 | 3.08 | ❌ No (2.79 < 3.10) |
| 4 | 60 | 3.86 | 3.86 | 3.84 | ✅ Yes (3.86 > 3.08) |
| 5 | 58 | 3.52 | 3.84 | 3.82 | ❌ No (3.52 < 3.84) |

**Key Observation**: Decay makes it progressively easier to update `bestPher`. Notice that at iteration 3, `bestPher` was 3.10 (before decay), but by iteration 4, it had decayed to 3.08, making the update with 3.86 easier.

---

## Mathematical Analysis: Decay Over Many Iterations

If `bestPher` starts at value `P₀` and no improvement is found for `n` iterations:

```
bestPher(n) = P₀ × (1 - bestEvap)^n
bestPher(n) = P₀ × (0.995)^n
```

### Example: Decay Over 100 Iterations

Starting with `bestPher = 7.36` (70 cells filled):

| Iterations | Calculation | Decayed Value | Reduction |
|------------|-------------|---------------|-----------|
| 0 | 7.36 × 0.995^0 | **7.36** | 0% |
| 10 | 7.36 × 0.995^10 | **7.00** | 4.9% |
| 20 | 7.36 × 0.995^20 | **6.65** | 9.6% |
| 50 | 7.36 × 0.995^50 | **5.71** | 22.4% |
| 100 | 7.36 × 0.995^100 | **4.43** | 39.8% |
| 200 | 7.36 × 0.995^200 | **2.67** | 63.7% |

**Insight**: After 100 iterations without improvement, `bestPher` has reduced by almost 40%, making it much easier for new discoveries to replace it.

---

## Why 0.5% (0.005) Decay Rate?

The default `bestEvap = 0.005` (0.5% per iteration) is a careful balance:

1. **Too Small (< 0.001)**: Decay is negligible, doesn't help escape local optima
2. **Too Large (> 0.01)**: Decay is too aggressive, loses information too quickly, reduces convergence
3. **0.005 (0.5%)**: Provides gradual weakening over time:
   - Small enough to preserve good solutions
   - Large enough to allow escape from local optima
   - Results in ~39% reduction after 100 iterations (good exploration window)

---

## When is BVE Applied?

### Applied:
- ✅ After **standard global pheromone updates** (Algorithm 0 style)
- ✅ On **non-communication iterations** (independent thread work)
- ✅ Every iteration when using standard update

### NOT Applied:
- ❌ After **communication pheromone updates** (three-source update)
- ❌ When `bestPher` is updated to a new value (replaced, not decayed)

### Code Logic:

```cpp
if (iter % interval == 0) {
    // Communication iteration
    PerformBarrierSynchronization();
    UpdatePheromoneWithCommunication();  // Three-source update
    // BVE NOT applied here
} else {
    // Standard iteration
    UpdatePheromone();  // Standard Algorithm 0 update
    colony->bestPher *= (1.0f - colony->bestEvap);  // BVE applied here
}
```

---

## Benefits of Best Value Evaporation

1. **Prevents Lock-In**: Gradually weakens old solutions, preventing premature convergence
2. **Maintains Exploration**: Keeps the algorithm exploring alternative solutions
3. **Enables Escape**: Makes it easier to replace good-but-not-optimal solutions
4. **Balances Exploration-Exploitation**: Preserves information while allowing discovery
5. **Adaptive**: Automatically adjusts as search progresses

---

## Comparison: With vs. Without BVE

### Scenario: Algorithm finds 70 cells filled at iteration 10, then no improvement for 90 iterations

#### Without BVE:

| Iteration | bestPher | Pheromone Strength | Status |
|-----------|----------|-------------------|--------|
| 10 | 7.36 | Strong | Good |
| 50 | 7.36 | Very Strong | Locked |
| 100 | 7.36 | Extremely Strong | **Stuck** |

**Result**: Algorithm cannot escape, even if better solutions exist in different regions.

#### With BVE (0.5% decay):

| Iteration | bestPher | Pheromone Strength | Status |
|-----------|----------|-------------------|--------|
| 10 | 7.36 | Strong | Good |
| 50 | 5.71 | Moderate | Exploring |
| 100 | 4.43 | Weaker | **Ready for replacement** |

**Result**: Algorithm can discover and adopt better solutions.

---

## Key Takeaways

1. **Formula**: `bestPher *= (1 - bestEvap)` where `bestEvap = 0.005`
2. **When**: After standard pheromone updates (non-communication iterations)
3. **Purpose**: Prevent lock-in, maintain exploration, enable escape from local optima
4. **Effect**: Gradual 0.5% reduction per iteration (~39% over 100 iterations)
5. **Benefit**: Balances exploitation (preserves good solutions) with exploration (allows discovery)

Best Value Evaporation is a **critical mechanism** for maintaining the exploration-exploitation balance in Ant Colony Optimization algorithms!


















