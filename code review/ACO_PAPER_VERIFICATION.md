# ACO Component: Verification Against Lloyd & Amos (IEEE Trans. on Games)

This document verifies that the **single-colony ACS (Algorithm 0)** and the **per-colony ACS core** in the parallel solver (Algorithm 2) correctly implement the Ant Colony Optimization for Sudoku described in:

**Lloyd, H., & Amos, M. (2021).** *Solving Sudoku with Ant Colony Optimization.* IEEE Transactions on Games.  
(Code reference: https://github.com/huwlloyd-mmu/sudoku_acs)

---

## 1. Algorithm Structure (Algorithm 1 in Paper)

| Paper (Algorithm 1) | Implementation | Location |
|---------------------|----------------|----------|
| 1. Read puzzle | `Board board(puzzleString)` | `solvermain.cpp` |
| 2–4. For all cells with fixed values, propagate constraints | Done in `Board` constructor via `SetCell()`; each `SetCell` calls `ConstrainCell()` on peers | `board.cpp` (constructor, `SetCell`, `ConstrainCell`) |
| 5. Initialize global pheromone matrix | `InitPheromone(..., pher0)` with `pher0 = 1.0f / board.CellCount()` | `solvermain.cpp` (102, 106), `sudokuantsystem.cpp` (5–15), `parallelsudokuantsystem.cpp` (104–117) |
| 6. **while** puzzle not solved | `while (!solved)` | `sudokuantsystem.cpp` (57); parallel: `SubColonyWorker` loop |
| 7. Give each ant a local copy of puzzle | `a->InitSolution(puzzle, startCell)` copies board into each ant | `sudokuantsystem.cpp` (62–65), `sudokuant.cpp` (4–6) |
| 8. Assign each ant to a different cell | `dist(randGen)` for start cell per ant | `sudokuantsystem.cpp` (61, 64) |
| 9. **for** number of cells | Loop over `puzzle.CellCount()` | `sudokuantsystem.cpp` (67) |
| 10. **for** each ant | `for (auto a : antList)` | `sudokuantsystem.cpp` (70–73) |
| 11. **if** current cell value not fixed | `!sol.GetCell(iCell).Fixed()` | `sudokuant.cpp` (24) |
| 12. Choose value from current cell's value set | Greedy (q₀) or roulette by pheromone | `sudokuant.cpp` (27–77) |
| 13. Fix cell value | `sol.SetCell(iCell, best)` or `rouletteVals[i]` | `sudokuant.cpp` (46, 72) |
| 14. Propagate constraints | `Board::SetCell()` calls `ConstrainCell()` on box/col/row peers | `board.cpp` (282–307) |
| 15. Update local pheromone | `LocalPheromoneUpdate(iCell, choice)` | `sudokuant.cpp` (47, 74), Eq. (3) below |
| 17. Move to next cell | `++iCell` with wrap | `sudokuant.cpp` (80–82) |
| 20. Find best ant | Max of `NumCellsFilled()` | `sudokuantsystem.cpp` (76–85), `sudokuant.h` (19) |
| 21. Global pheromone update | Only best-so-far; Eq. (6) | `sudokuantsystem.cpp` (28–37, 141), `parallelsudokuantsystem.cpp` (142–152) |
| 22. Best value evaporation | `bestPher *= (1 - bestEvap)` | `sudokuantsystem.cpp` (141), `parallelsudokuantsystem.cpp` (704) |

---

## 2. Formal Specifications (Paper Equations)

### Line 5: Pheromone matrix τ

- **Paper:** τᵢₖ for cell i, value k; τ₀ = 1/c, c = d².
- **Code:** `pher[i][j]` with j = 0..numUnits-1 (value index). Initialized to `pher0` where `pher0 = 1.0f / board.CellCount()`.
- **Status:** ✅ Correct.

### Line 12: Value selection (Paper Eq. 1 & 2)

- **Paper:** With probability q₀ choose argmax_{k∈vᵢ} τᵢₖ; else choose by probabilities pᵢₖ = τᵢₖ / Σ_{j∈vᵢ} τᵢⱼ.
- **Code:** `if (parent->random() < parent->Getq0())` → greedy (max pheromone); else cumulative pheromone then `rouletteVal = totPher * parent->random()` and select first option with cumulative > rouletteVal.
- **Status:** ✅ Correct (q₀, greedy, and proportional probabilities match).

### Fail cells (Paper: Line 20)

- **Paper:** If a cell’s value set becomes empty it is a “fail cell”; solution quality uses number of fixed cells (effectively subtracting fail cells).
- **Code:** When `sol.GetCell(iCell).Empty()` the ant does not set a value and increments `failCells`. Quality = `NumCellsFilled() = sol.CellCount() - failCells`.
- **Status:** ✅ Correct.

### Line 15: Local pheromone update (Paper Eq. 3)

- **Paper:** τᵢₛ ← (1 − ξ)τᵢₛ + ξτ₀ with ξ = 0.1.
- **Code:** `pher[iCell][iChoice] = pher[iCell][iChoice] * 0.9f + pher0 * 0.1f` (ξ = 0.1).
- **Status:** ✅ Correct.

### Line 20 / Eq. 4–5: Best ant and pheromone addition

- **Paper:** f_best = max_n f_n; Δτ = c / (c − f_best).
- **Code:** Best ant = argmax `NumCellsFilled()`; `PherAdd(cellsFilled) = numCells / (float)(numCells - cellsFilled)`.
- **Status:** ✅ Correct.

### Line 21: Global pheromone update (Paper Eq. 6)

- **Paper:** In ACS, update only on components of the best solution: τᵢₛ ← (1 − ρ)τᵢₛ + ρ·Δτ_best; ρ = 0.9; no global evaporation elsewhere.
- **Code:** Only cells in `bestSol` are updated: `pher[i][bestSol.GetCell(i).Index()] = pher[i][...] * (1.0f - rho) + rho * bestPher` with default `rho = 0.9`.
- **Status:** ✅ Correct.

### Line 22: Best value evaporation (Paper Eq. 7, BVE)

- **Paper:** Δτ_best ← Δτ_best × (1 − ρBVE), ρBVE = 0.005, to reduce lock-in.
- **Code:** `bestPher *= (1.0f - bestEvap)` with default `evap = 0.005f` (`--evap 0.005`).
- **Status:** ✅ Correct.

---

## 3. Parameters (Paper vs Code)

| Parameter | Paper | Code default | Location |
|-----------|--------|--------------|----------|
| τ₀        | 1/c    | `1.0f/board.CellCount()` | `solvermain.cpp` 102, 106 |
| q₀        | 0.9    | `--q0` default 0.9      | `solvermain.cpp` 87 |
| ρ         | 0.9    | `--rho` default 0.9     | `solvermain.cpp` 88 |
| ξ (local) | 0.1    | Hardcoded 0.9, 0.1      | `sudokuant` local update |
| ρBVE      | 0.005  | `--evap` default 0.005  | `solvermain.cpp` 89 |
| m (ants)  | 10     | `--ants` default 10      | `solvermain.cpp` 85 |

---

## 4. Constraint propagation (Section III-A)

- **Paper:** Two rules: (1) Elimination: fix value → remove from peers’ value sets; (2) Unique possibility: if a value has only one possible cell in a unit, fix it. Applied recursively.
- **Code:** `Board::SetCell` updates the cell then calls `ConstrainCell(k)` for each peer in the same box, column, and row. `ConstrainCell` (and related logic) removes the fixed value from peers and applies unique-possibility fixing.
- **Status:** ✅ CP is applied after each ant’s value assignment, matching the paper’s “fix cell value; propagate constraints.”

---

## 5. Summary

- **Single-colony ACS (Algorithm 0)** and the **core ACS inside each sub-colony (Algorithm 2)** match the Lloyd & Amos algorithm and equations:
  - Pheromone matrix and τ₀ = 1/c
  - Pseudo-random proportional rule (q₀, greedy/roulette)
  - Local update (ξ = 0.1)
  - Best-ant selection and Δτ = c/(c − f_best)
  - Global update only on best-so-far (ρ = 0.9)
  - Best value evaporation (ρBVE = 0.005)
- Constraint propagation is integrated with solution construction (fix → propagate).
- Solution quality uses filled cells and correctly accounts for fail cells.

**Reference:** Lloyd, H., & Amos, M. (2021). Solving Sudoku with Ant Colony Optimization. *IEEE Transactions on Games.*
