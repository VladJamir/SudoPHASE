# Adaptation from Stodola et al.: Hybrid ACO–SA for Sudoku

This document describes what was **adapted and used** from the paper:

**Stodola, P., Michenka, K., Nohel, J., & Rybanský, M. (2020).** *Hybrid Algorithm Based on Ant Colony Optimization and Simulated Annealing Applied to the Dynamic Traveling Salesman Problem.* Entropy, 22(8), 884.  
https://doi.org/10.3390/e22080884

The paper proposes an **ACO-SA hybrid** for the Dynamic Traveling Salesman Problem (DTSP). Although our implementation targets **Sudoku** (and uses **ACS** from Lloyd & Amos rather than the paper’s ACO variant), the **procedure for hybridizing Simulated Annealing with ACO** is the one we follow. This file maps the paper’s ideas to our code and states what is adapted, what is preserved, and what differs.

---

## 1. What We Adopted from the Paper

### 1.1 Hybridization procedure (Section 3.3, Algorithm 6)

- **Paper:** ACO is the main heuristic; SA is a **local optimization** applied to the **best solution found by the colony** in the current (or recent) phase. That best solution is used as the **initial solution** for SA. If SA improves it, the improved solution replaces the best and is then used to update the pheromone matrix.
- **Our implementation:**
  - **Single-colony (Algorithm 0):** Every `saFrequency` iterations we run SA on the **best-so-far** solution (`bestSol`). If the SA result is accepted (under the chosen policy), we set `bestSol = saSolution`; the subsequent global pheromone update uses this (possibly improved) best-so-far.  
    **Code:** `sudokuantsystem.cpp`: after iteration-best update, `if (saFrequency > 0 && iter % saFrequency == 0 && iter != 0)` → `SudokuSA sa(bestSol); ... sa.Anneal();` then conditional `bestSol.Copy(saSolution)`.
  - **Parallel (Algorithm 2):** Each sub-colony runs SA on its **best-so-far** (`GetBestSol()`). If the SA result is accepted, we call `UpdateBestSolution(saSolution, saScore)`; the (possibly improved) best-so-far is then used in that colony’s standard pheromone update.  
    **Code:** `parallelsudokuantsystem.cpp`: `if (saFrequency > 0 && iter % saFrequency == 0 && iter != 0)` → `SudokuSA sa(colony->GetBestSol()); ... colony->UpdateBestSolution(saSolution, saScore)`.

So we **apply SA to the best solution** (per colony) and **use the (possibly improved) best for pheromone update**, matching the paper’s hybridization logic.

### 1.2 Frequency of SA execution (Table 5: `sa_freq`)

- **Paper:** SA is not run every generation; it is run every **`sa_freq`**-th generation (e.g. every 5th generation). This controls how often the best solution is refined by SA.
- **Our implementation:** We use **`saFrequency`** (command-line **`--safreq n`**): SA runs every **`saFrequency`** ACS iterations (and only when `iter != 0`). So **`sa_freq` → `saFrequency`** (same role: periodic application of SA within the ACO/ACS loop).

**Where `saFrequency` appears in the code (reference-paper component):**

| Role | File | Detail |
|------|------|--------|
| **Command-line** | `src/solvermain.cpp` | `int saFreq = a.GetArg("safreq", 0);` — read from `--safreq n` (default 0 = disabled). |
| **Passed into solvers** | `src/solvermain.cpp` | `SudokuAntSystem(..., saFreq, ...)` and `ParallelSudokuAntSystem(..., saFreq, ...)` so the constructor parameter `safreq` receives the value. |
| **Single-colony member** | `src/sudokuantsystem.h` | `int saFrequency;` — stored in class. Constructor: `saFrequency(safreq)`. |
| **Parallel member** | `src/parallelsudokuantsystem.h` | `int saFrequency;` — stored in class. Constructor (in .cpp): `saFrequency(safreq)`. |
| **When SA runs (alg 0)** | `src/sudokuantsystem.cpp` | `if (!solved && saFrequency > 0 && iter % saFrequency == 0 && iter != 0)` → then `SudokuSA sa(bestSol); sa.Anneal();` etc. |
| **When SA runs (alg 2)** | `src/parallelsudokuantsystem.cpp` | `if (saFrequency > 0 && iter % saFrequency == 0 && iter != 0)` → then `SudokuSA sa(colony->GetBestSol());` etc. |

So the **paper’s `sa_freq`** is implemented as the member **`saFrequency`**, set from **`--safreq`**, and the condition **`iter % saFrequency == 0`** implements “every sa_freq-th (generation/iteration)”.

### 1.3 Simulated Annealing structure (Algorithm 4, Section 3.2)

- **Paper:** SA has an initial solution, a temperature schedule (T_max, T_min, cooling), and in each “generation” it performs **transformations** (neighbor solutions) and **replacements** (accept/reject). Acceptance is by the **Metropolis criterion**.
- **Our implementation:**  
  - **Initial solution:** The current best-so-far board passed into `SudokuSA(sol)` (single-colony: `bestSol`; parallel: colony’s best-so-far).  
  - **Temperature schedule:** Implemented in `SudokuSA::Anneal()` with `temp = 1.5` (T_max), `stoppingTemp = 0.01` (T_min), `coolingRate = 0.995` (γ).  
  - **Loop:** `while (temp > stoppingTemp)`; inside, one transformation per temperature step (neighbor by `TryRandomSwap`), then accept/reject; then `temp = temp * coolingRate`.  
  So we keep the **same high-level SA structure**: initial solution, temperature loop, transform → evaluate → accept/reject → cool.

### 1.4 Metropolis criterion (Equation 5)

- **Paper:**  
  - If new cost ≤ current cost: accept (p = 1).  
  - If new cost > current cost: accept with probability p = exp(-(c' - c) / T).
- **Our implementation:**  
  **Code:** `simulatedannealing.cpp`: `if (delta <= 0)` accept and update; `else { acceptanceProbability = exp(-delta / temp); ... if (rnd < acceptanceProbability) accept; else reject (restore currentSol). }`  
  So we use the **same Metropolis rule**: always accept improving or equal; probabilistically accept worsening by exp(-ΔC/T).

### 1.5 SA temperature parameters (Table 3)

| Paper symbol | Paper role            | Our variable    | Our value  | Location                    |
|-------------|------------------------|-----------------|------------|-----------------------------|
| T_max       | Initial temperature    | `temp` (initial)| 1.5        | `simulatedannealing.cpp`    |
| T_min       | Stopping temperature   | `stoppingTemp`  | 0.01       | `simulatedannealing.cpp`    |
| γ (gamma)   | Cooling coefficient    | `coolingRate`   | 0.995      | `simulatedannealing.cpp`    |

We do **not** expose n1_max / n2_max as separate parameters; we perform **one transformation per temperature step** and one accept/reject per step, then cool. So the “generation” in the paper corresponds to one temperature level; within it we do one transform and one replacement (simplified compared to the paper’s n1_max/n2_max).

---

## 2. What We Adapted (Problem and Operators)

### 2.1 Problem: Sudoku instead of TSP/DTSP

- **Paper:** Cost = tour length (TSP); solution = route (sequence of vertices). Dynamic variant: vertices change between iterations.
- **Our implementation:**  
  - **Solution:** A Sudoku board (cell–value assignments).  
  - **Cost:** `ComputeCost()` = empty cells + row duplicate count + column duplicate count (no box duplicates, because we keep box constraints satisfied in SA).  
  So the **hybridization procedure** (SA on best solution, result used for pheromone) is the same; only the **solution representation and cost** are adapted to Sudoku.

### 2.2 Neighborhood / transformation (Algorithm 5 vs our operator)

- **Paper (Algorithm 5):** For TSP, “Transform_Solution” selects a vertex, computes a movement **range** (depending on temperature, e.g. σ from Formula 6), and **moves that vertex** along the route (position change in the permutation). So the neighborhood is **position moves in a route**.
- **Our implementation:** We use a **Sudoku-specific** neighborhood: **swap two non-clue cells within the same box** (`TryRandomSwap`). We choose a conflicted cell (in a row/column with duplicates), then a swap partner in the same box. This preserves **box constraints** and only tries to reduce row/column conflicts.  
  So the **idea** (transform current solution into a neighbor; temperature can be used to control “step size” in the paper) is the same; the **concrete operator** is adapted to Sudoku (box-preserving swap instead of route-position move).

### 2.3 Initial solution for SA: filled board

- **Paper:** SA starts from a complete TSP route.
- **Our implementation:** The ACS best-so-far may have **empty cells**. We first **fill empty cells** per box so that each box has digits 1..n without violating box constraints (`FillEmptyCells()`). SA then works on a **fully filled** board and minimizes row/column conflicts (and empty count if any). This is an adaptation so that SA always has a well-defined cost (conflicts + empties) and a feasible neighborhood (swaps inside boxes).

### 2.4 Post-processing: CleanDuplicates

- **Paper:** No direct analogue; TSP solution is a single route.
- **Our implementation:** After the annealing loop we run `CleanDuplicates()`: among duplicate values in rows/columns we clear the “worst” cell (most conflicts) so that the board can have empty cells again for ACS to refine. This is **Sudoku-specific** and not in the paper.

---

## 3. Acceptance of SA result in the hybrid (Beyond the paper)

- **Paper:** If SA improves the solution, the improved solution replaces r_best and is used for pheromone update; otherwise r_best is unchanged.
- **Our implementation:** We support two policies (both compatible with the idea “use SA to refine best”):  
  1. **Conservative / hybrid (default):** Accept SA result only if it is strictly better (e.g. more cells filled) or same quality with cost 0 (solved); in parallel we also allow “same or slightly fewer cells but ≥5 conflicts reduced” (hybrid acceptance).  
  2. **Always-accept (`--saAccept 1`):** Always replace best-so-far with the SA output (CP-like), so pheromone is always updated from the SA solution.  
  So the **integration point** (SA output can replace best and drive pheromone) is as in the paper; we add **configurable acceptance** for when SA does not strictly improve (e.g. to avoid degrading solution quality when SA returns a “cleaner” but slightly worse board).

---

## 4. Summary table: Paper → Our code

| Paper concept                    | Our implementation |
|---------------------------------|--------------------|
| Apply SA to best solution       | SA on `bestSol` (alg 0) or colony’s best-so-far (alg 2) |
| Use (possibly improved) best for pheromone | After SA, if accepted, `bestSol` or colony best is updated; next pheromone update uses it |
| sa_freq                         | `saFrequency` / `--safreq`; SA every n iterations |
| T_max, T_min, γ                 | `temp=1.5`, `stoppingTemp=0.01`, `coolingRate=0.995` |
| Metropolis p = exp(-ΔC/T)       | `acceptanceProbability = exp(-delta / temp)` |
| Transform solution              | `TryRandomSwap`: same-box swap (Sudoku); not TSP vertex move |
| Cost                            | `ComputeCost()`: empties + row/column duplicates |
| Best solution tracking          | `bestSol` / colony best-so-far; updated only when SA result is accepted (under chosen policy) |

---

## 5. References

- **Stodola, P., Michenka, K., Nohel, J., & Rybanský, M. (2020).** Hybrid Algorithm Based on Ant Colony Optimization and Simulated Annealing Applied to the Dynamic Traveling Salesman Problem. *Entropy*, 22(8), 884.  
  Used for: hybridization procedure (SA on best solution, result used for pheromone), SA frequency (`sa_freq`), SA structure and Metropolis criterion, temperature parameters (T_max, T_min, γ).  
  Adapted: problem (Sudoku vs TSP), cost function, neighborhood (box-swap vs route vertex move), and optional acceptance policies.

- **Lloyd, H., & Amos, M. (2021).** Solving Sudoku with Ant Colony Optimization. *IEEE Transactions on Games*.  
  Used for: ACS core (pheromone, decision rule, BVE). See `ACO_PAPER_VERIFICATION.md`.
