# Code Review Walkthrough — Full Codebase

This document walks through **every source file** in `src/` for your code review presentation. Files are ordered by dependency (foundations first, then solvers, then main). Line numbers are approximate; use your editor to jump.

---

## Architecture Overview

- **Three solvers** (all implement `SudokuSolver`): **Algorithm 0** (single-colony ACS), **Algorithm 1** (backtracking), **Algorithm 2** (parallel ACS with ring + random topology).
- **Algorithm 0 & 2** use the same **ACS core** (Lloyd & Amos) and optional **SA** (Stodola et al.); Algorithm 2 adds **RMACO-style** communication (Yang et al.).
- **Board** and **ValueSet** provide the Sudoku grid and constraint propagation; **Timer** and **Arguments** are utilities; **IAntColony** lets ants work with both single and parallel colonies.

---

## 1. `valueset.h` — Cell domain (bitmap)

**Role:** One cell’s set of possible values (e.g. {3,5,7}) as a bitmap for fast set operations.

- **Lines 1–17:** Includes; `MASK0`, `NBITS`; class with `bitmap`, `mask`, `nMax`.
- **Lines 23–30 (`msb`):** Returns position of leftmost set bit (Knuth-style double trick). Used by `Index()` when the set has one element.
- **Lines 35–45 (`popcnt`):** Bit count (Knuth “sideways addition”). Used by `Count()`.
- **Lines 48–50:** Constructors: `ValueSet(nMax, initialVal)` and default. `mask` limits bits to `nMax`.
- **Lines 51–59:** `Init`, `Add`, `Remove` — bitmap update.
- **Lines 61–84 (`toString`):** Debug string: "-" if empty, single char if fixed, else "(digits)".
- **Lines 86–112:** `Contains`, `Count`, `Fixed()` (exactly one value), `Empty()`, `Index()` (value when fixed).
- **Lines 113–162:** Set ops: `Union`, `Intersection`, `Difference`, `Complement`; operators `+`, `^`, `-`, `~`, `<<=` (shift for iterating choices).

**Presentation tip:** Emphasize that ValueSet is the “domain” of one cell; Board uses an array of them and constraint propagation narrows them.

---

## 2. `board.h` — Sudoku grid (interface)

**Role:** Declares the Board API: construction, copy, string I/O, cell access, constraint propagation, indexing.

- **Lines 1–6:** `#pragma once`, includes `ValueSet`, `string`, `vector`.
- **Lines 7–26:** Public API: default/copy/string constructors, `AsString`, `FixedCellCount`, `InfeasibleCellCount`, `SetCell`, `ForceSetCell`, `GetCell`, `GetNumUnits`, `Copy`, `CellCount`, `CheckSolution`; row/col/box index helpers (`RowCell`, `ColCell`, `BoxCell`, `RowForCell`, etc.).
- **Lines 36–39:** SA-related: `isClue`, `IsClue`, `IsEmpty`.
- **Lines 41–50:** Private: `cells` (array of ValueSet), `order`, `numUnits`, `numCells`, `numFixedCells`, `numInfeasible`; `Eliminate`, `Eliminate2`, `ConstrainCell`.

**Presentation tip:** Board = grid + constraint propagation; SetCell triggers ConstrainCell on peers.

---

## 3. `board.cpp` — Board implementation

**Constructor (11–81):**  
- Puzzle size from string length (81→order 3, 256→4, 625→5, … up to 4096→8).  
- `numUnits = order*order`, `numCells = numUnits*numUnits`.  
- All cells initialized to “all values” then clues applied with `SetCell`; clues mark `isClue[i]=true`.

**Copy / destructor (89–110):** Copy replicates structure and `numFixedCells`/`numInfeasible`; destructor frees `cells`.

**Indexing (113–149):**  
- `RowCell(iRow, iCell)` = linear index in row; `ColCell`/`BoxCell` similar.  
- `RowForCell`/`ColForCell`/`BoxForCell` invert (which row/col/box contains a cell).

**AsString (152–218):** Builds human-readable grid: optional numbers vs letters, optional show-unfixed; adds row/col/box separators.

**ConstrainCell (220–279):** Core propagation.  
- Skip if cell empty or fixed.  
- For cell’s row/col/box, collect fixed values and all values.  
- `fixedCellsConstraint = ~(rowFixed+colFixed+boxFixed)` = allowed values.  
- If that set has one value → `SetCell` (unique possibility). Else intersect cell with it; then check if any remaining value is unique in row/col/box (“hidden single”) and SetCell if so. If cell becomes empty, increment `numInfeasible`.

**SetCell (282–307):** If already fixed, return. Set `cells[i]=c`, increment `numFixedCells`, then call `ConstrainCell` on every peer in same box, column, row.

**Getters (309–331):** FixedCellCount, InfeasibleCellCount, CellCount, GetNumUnits.

**CheckSolution (333–371):** Returns true iff (1) every cell fixed, (2) every row/col/box has exactly one of each value, (3) fixed clues in this board match the candidate solution.

**ForceSetCell (373–402):** Like SetCell but allows overwriting; updates `numFixedCells` and propagates to peers. Used by SA (swaps) and CleanDuplicates.

**IsClue / IsEmpty (404–415):** Bounds check and lookup.

**Presentation tip:** Walk one `SetCell` → ConstrainCell chain to show how fixing one cell prunes peers (elimination + unique possibility).

---

## 4. `timer.h` — Wall-clock timer

**Role:** Portable elapsed time in seconds (Windows: QueryPerformanceCounter; else gettimeofday).

- **Lines 1–24:** Includes and `TimeNow()` (platform-specific).
- **Lines 26–34:** Constructor sets `inverseTimerFreq` (Windows: 1/frequency; else 1e-6).
- **Lines 35–47:** `Reset()` stores current time; `Elapsed()` returns seconds since last Reset.

---

## 5. `arguments.h` — Command-line parser

**Role:** Parse `--key` and optional `value`; `GetArg(key, default)` returns typed value.

- **Lines 15–17:** `IsArg(token)` = token starts with `--`.
- **Lines 18–38:** `ProcessArgs`: loop argv; if `--key` then next non-arg is value else value `"1"`; store in `args` map.
- **Lines 44–54:** `GetArg<T>`: if key found, stream parse into default type and return; else return default.

---

## 6. `sudokusolver.h` — Solver interface

**Role:** Abstract interface for all solvers.

- **Lines 5–11:** Pure virtual `Solve(puzzle, maxTime)`, `GetSolutionTime()`, `GetSolution()`. Implemented by BacktrackSearch, SudokuAntSystem, ParallelSudokuAntSystem.

---

## 7. `backtracksearch.h` / `backtracksearch.cpp` — Algorithm 1

**Header:**  
- Inherits `SudokuSolver`.  
- Private: `solutionTimer`, `solTime`, `solution`, `stepCount`, `timedOut`, `timeOut`.  
- Public: `Solve`, getters, `GetStepCount()`.

**cpp — StepSolution (7–70):**  
- Every 5000 steps check timeout; if exceeded set `timedOut` and return.  
- **MRV:** Find unfixed cell with smallest `Count()` (minimum remaining values).  
- If none, puzzle is solved → copy to `solution`, return.  
- Else try each value in that cell: copy board, `SetCell(nextCell, choice)`; if all fixed → solved; if no infeasible cells, recurse `StepSolution(newBoard)`.  
- `choice <<= 1` iterates over single-value bits.

**Solve (72–81):** Reset timer, set `timeOut`, call `StepSolution(puzzle)`; set `solTime`; return `solved`.

**Presentation tip:** “Exact method: depth-first search + MRV + same Board propagation as ACS.”

---

## 8. `antcolonyinterface.h` — Colony interface for ants

**Role:** So that `SudokuAnt` can call back into either `SudokuAntSystem` or `SubColony` without knowing which.

- **Lines 5–13:** Pure virtual `Getq0()`, `random()`, `Pher(i,j)`, `LocalPheromoneUpdate(iCell, iChoice)`. Both single-colony and SubColony implement this.

---

## 9. `sudokuant.h` / `sudokuant.cpp` — Single ant (ACS construction)

**Header:**  
- `sol` (Board), `iCell` (current position), `parent` (IAntColony*), `failCells`, `roulette`/`rouletteVals` (for roulette wheel).  
- `InitSolution(puzzle, startCell)`, `StepSolution()`, `GetSolution()`, `NumCellsFilled() = CellCount() - failCells`.

**cpp — InitSolution (4–16):** Copy puzzle into `sol`, set `iCell=startCell`, `failCells=0`; (re)allocate roulette arrays of size `GetNumUnits()`.

**StepSolution (18–84):**  
- If current cell **empty** (propagation removed all options) → increment `failCells`.  
- Else if current cell **not fixed**:  
  - **ACS rule (Lloyd & Amos):** With probability `q0`: **greedy** — choose value with max pheromone in cell’s domain; else **roulette** — cumulative pheromone, then random in [0,totPher], pick first option above that.  
  - `sol.SetCell(iCell, chosen)` (triggers propagation).  
  - **Local pheromone update:** `LocalPheromoneUpdate(iCell, choice)` (τ ← 0.9τ + 0.1τ₀).  
- Advance `iCell`; wrap to 0 after last cell.

**Presentation tip:** “One ant = one solution attempt; quality = NumCellsFilled = cells filled minus fail cells.”

---

## 10. `sudokuantsystem.h` / `sudokuantsystem.cpp` — Algorithm 0 (single-colony ACS)

**Header:**  
- Inherits `SudokuSolver` and `IAntColony`.  
- Parameters: `numAnts`, `q0`, `rho`, `pher0`, `bestEvap`, `saFrequency`, `saAlwaysAccept`.  
- State: `bestSol`, `bestPher`, `iterationsCompleted`, `solutionTimer`, `solTime`, `antList`, `randGen`, `randomDist`, `pher` (matrix).  
- Methods: `InitPheromone`, `ClearPheromone`, `UpdatePheromone`, `PherAdd`, `LocalPheromoneUpdate`; constructor creates ants with `this` as colony.

**cpp — InitPheromone (7–16):** Allocate `pher[numCells][valuesPerCell]`, all set to `pher0`.

**ClearPheromone (18–24):** Free matrix.

**PherAdd (26–30):** Δτ = `numCells/(numCells - cellsFilled)` (Lloyd & Amos Eq. 5).

**UpdatePheromone (32–40):** For each fixed cell in `bestSol`, τ_ij ← (1−ρ)τ_ij + ρ·bestPher (only best-so-far reinforced; Eq. 6).

**LocalPheromoneUpdate (42–46):** τ ← 0.9τ + 0.1·pher0 (Eq. 3).

**Solve (47–172):**  
- Init pheromone, reset timer, `solTime=0`.  
- **Loop:**  
  - Each ant gets random start cell, then all ants step through all cells (one step per cell per ant).  
  - Find best ant by `NumCellsFilled()`; compute `pherToAdd = PherAdd(bestVal)`.  
  - If `pherToAdd > bestPher`: update `bestSol`, `bestPher`; if all cells filled → solved, record time, break.  
  - **SA (optional):** If `saFrequency > 0` and `iter % saFrequency == 0` and iter≠0: run `SudokuSA(bestSol).Anneal()`; accept by policy (`saAlwaysAccept` or improvement/cost 0); if accepted and solved, break.  
  - If not solved: `UpdatePheromone()`, `bestPher *= (1 - bestEvap)` (BVE), increment iter.  
  - Every 100 iters check timeout; if exceeded set `solTime` and break.  
- Set `iterationsCompleted`, `ClearPheromone`, return solved.

**Presentation tip:** “Algorithm 0 = one colony, best-so-far only global update, optional SA on best-so-far every saFrequency iters.”

---

## 11. `simulatedannealing.h` / `simulatedannealing.cpp` — SA for Sudoku

**Header:**  
- `sol`, `bestSol`, `currentSol`, `bestCost`, `acceptanceProbability`.  
- `Anneal()`, `ComputeCost()`, `FillEmptyCells()`, `GetSolution()`; private: `TryRandomSwap`, `CleanDuplicates`, `LocalConflicts`.

**cpp — Anneal (15–76):**  
- `FillEmptyCells()` so every box has digits 1..n (box constraint satisfied).  
- T=1.5, T_min=0.01, cooling 0.995.  
- **Loop while T > T_min:** One transformation: `TryRandomSwap` (neighbor); Δ = newCost − currentCost. **Metropolis:** if Δ≤0 accept; else accept with prob exp(−Δ/T). Track best; if cost 0 return. Then cool T.  
- `CleanDuplicates()` at end; return bestCost.

**ComputeCost (78–128):** Cost = empty cells + row duplicates + column duplicates (no box duplicates after FillEmptyCells).

**FillEmptyCells (130–186):** Per box: find fixed values, list empty cells and missing digits, shuffle missing, assign to empty cells (box stays valid).

**TryRandomSwap (191–282):**  
- Find rows/cols with duplicates; collect non-clue cells in those rows/cols as “conflicted”.  
- Pick random conflicted cell, then random non-clue partner in same box.  
- Swap; return cost = oldCost + (after − before) local conflicts (incremental).

**LocalConflicts (284–311):** Count row and column duplicates involving cell `idx`.

**CleanDuplicates (314–448):** Count per-cell conflict participation; in each row/col, for each duplicate value remove the cell with highest conflict count (one per duplicate group).

**Presentation tip:** “SA = fill boxes, then minimize row/col conflicts by same-box swaps; Metropolis; CleanDuplicates leaves some cells empty for ACS to refill.”

---

## 12. `parallelsudokuantsystem.h` — Parallel ACS (interface)

**SubColony (18–93):**  
- One colony: `colonyId`, ACS params, `iterationBest`/`bestSol`, `receivedIterationBest`/`receivedBestSol` and scores; `antList`, `pher`, `contributions`/`hasContribution`.  
- `RunIteration`, `UpdatePheromone`, `UpdatePheromoneWithCommunication`, getters, `ReceiveIterationBest`/`ReceiveBestSol`, `UpdateBestSolution`, `Initialize`, `LocalPheromoneUpdate`.

**ParallelSudokuAntSystem (95–149):**  
- `numSubColonies`, `subColonies`, `globalBest`, `iterationsCompleted`, `communicationOccurred`, `solTime`, `solutionTimer`, `masterRandGen`; mutex/cv/atomic for barrier and stop.  
- `CalculateInterval`, `GenerateMatchArray`, `CommunicateRingTopology`, `CommunicateRandomTopology`; `SubColonyWorker`; helpers (CheckTimeout, ReportProgress, CheckSolutionFound, PerformBarrierSynchronization, ExecuteMasterThreadTasks, ExecuteWorkerThreadWait).  
- `saFrequency`, `saAlwaysAccept`; constructor, `Solve`, getters, `PrintColonyDetails`.

---

## 13. `parallelsudokuantsystem.cpp` — Parallel ACS (implementation)

**SubColony constructor (28–38):** Store params; init RNG with `rd()+id` for diversity.

**SubColony destructor (40–50):** Delete ants, clear pheromone, free contributions arrays.

**Initialize (56–99):** Set `numCells`/`numUnits`, create ants (pointing to this), `InitPheromone`, allocate contributions/hasContribution, copy puzzle into iterationBest/bestSol/received*; init scores and bestPher.

**InitPheromone / ClearPheromone (101–124):** Same idea as single-colony; ClearPheromone sets `pher=nullptr`.

**PherAdd (126–129):** Same formula as Algorithm 0.

**UpdatePheromone (137–152):** Standard ACS: only best-so-far; τ_ij ← (1−ρ)τ_ij + ρ·bestPher for fixed cells in bestSol.

**UpdatePheromoneWithCommunication (161–212):**  
- Compute pherValue1/2/3 from iterationBestScore, receivedIterationBestScore, receivedBestSolScore (PherAdd each).  
- For each cell: sum contributions from local iteration-best, received iteration-best, received best-so-far into `contributions[digit]`; then for each digit with contribution, τ_ij ← (1−ρ)τ_ij + ρ·contributions[j].  
- (Yang et al. Eq. 5: three-source update.)

**LocalPheromoneUpdate (214–217):** Same as Algorithm 0 (0.9τ + 0.1·pher0).

**RunIteration (221–268):**  
- All ants init with random start cell; then all step through all cells.  
- Find best ant; set iterationBest and iterationBestScore.  
- If PherAdd(bestVal) > bestPher, update bestSol, bestSolScore, bestPher (Algorithm 0 logic).

**ReceiveIterationBest / ReceiveBestSol (270–285):** Copy solution and score into received* (for three-source update only).

**UpdateBestSolution (287–298):** Copy solution and score into bestSol/bestSolScore; update bestPher if better (used after SA).

**ParallelSudokuAntSystem constructor (311–334):** Validate numSubColonies ≥ 1; create SubColony per colony; init masterRandGen.

**CalculateInterval (356–362):** iter < 200 → 100, else 10 (Yang et al. adaptive exchange).

**GenerateMatchArray (364–371):** Random permutation of 0..n-1 (iota + shuffle).

**CommunicateRingTopology (379–396):** Collect all iteration-bests; colony i sends to (i+1) mod n.

**CommunicateRandomTopology (412–431):** Collect all best-so-far; colony `matchArray[i]` receives from `matchArray[(i+n-1)%n]`.

**CountConflicts (446–491):** Row duplicates + column duplicates (for SA acceptance policy).

**CheckTimeout (497–504):** If elapsed ≥ maxTime, set stopFlag, notify_all, return true.

**ReportProgress (510–528):** Colony 0 only, every 50 iters; under lock, compute global best score and cerr progress.

**CheckSolutionFound (534–544):** If colony’s best has all cells filled, set stopFlag, notify_all, return true.

**ExecuteMasterThreadTasks (550–581):** Set communicationOccurred; generate matchArray; CommunicateRingTopology; CommunicateRandomTopology; check if any colony has complete solution (set stopFlag); reset barrier, notify_all.

**ExecuteWorkerThreadWait (562–579):** Wait on cv with 100ms timeout until barrier==0 or stopFlag; if timeout exceeded set stopFlag and notify.

**PerformBarrierSynchronization (585–619):** Lock; if stopFlag exit. Atomic increment barrier; if arrived==numSubColonies run ExecuteMasterThreadTasks, else ExecuteWorkerThreadWait. Unlock on exit.

**SubColonyWorker (639–754):**  
- Initialize colony with puzzle; iter=0.  
- **Loop while !stopFlag:** CheckTimeout; iter++; RunIteration.  
- **Pheromone:** If iter%interval==0: PerformBarrierSynchronization, then UpdatePheromoneWithCommunication; else UpdatePheromone and bestPher decay.  
- **SA (optional):** If saFrequency and iter%saFrequency==0 and iter≠0: SA on colony’s bestSol; accept by saAlwaysAccept or hybrid (more cells, or same/fewer with ≥5 conflict reduction); if accepted, UpdateBestSolution; if SA solved, stopFlag and break.  
- ReportProgress; CheckSolutionFound; break if found.

**Solve (764–824):** Set maxTime, reset timer, stopFlag=false, barrier=0; copy puzzle to globalBest. Launch numSubColonies threads running SubColonyWorker. Join all. Collect best solution and max iteration across colonies; set solTime; return true if globalBestScore == puzzle.CellCount().

**PrintColonyDetails (826–836):** Print per-colony iteration, iteration-best score, best-so-far score.

**Presentation tip:** “Algorithm 2 = N colonies in N threads; each runs Algorithm 0; every ‘interval’ iterations we barrier, ring-exchange iteration-best, random-exchange best-so-far, then three-source pheromone update; optional SA per colony with hybrid acceptance.”

---

## 14. `solvermain.cpp` — Entry point and CLI

**ReadFile (13–50):** Open file; read order and cell values (-1 → '.'); encode as string (order 3: 1–9 chars; 4: 0–9,a–f; else a–y). Return puzzle string.

**main (52–214):**  
- **Parse args:** puzzle (--puzzle string or --file), or --blank --order for empty grid. Build Board.  
- **Algorithm selection:** --alg 0/1/2 (default 0); timeout, ants, subcolonies, q0, rho, evap, safreq, saAccept, verbose, showinitial.  
- **Solver creation:** alg 0 → SudokuAntSystem(ants, q0, rho, 1/cellCount, evap, safreq, saAccept); alg 1 → BacktrackSearch; alg 2 → ParallelSudokuAntSystem(subcolonies, ants, q0, rho, 1/cellCount, evap, safreq, saAccept).  
- **Solve:** solver->Solve(board, timeOut); solution = GetSolution(); solTime = GetSolutionTime().  
- **Validate:** If success and !board.CheckSolution(solution), mark failure.  
- **Output:** If !verbose: one line “0/1” and time; if alg 1 add step count. If verbose: success/fail message, iterations (and for alg 2 “communication: yes/no”), solution grid and time.

**Presentation tip:** “One binary, three algorithms; same Board and propagation; ACS params and SA frequency from CLI.”

---

## Quick reference — where is what?

| Concept | File(s) |
|--------|---------|
| Cell domain (bit set) | valueset.h |
| Grid + propagation | board.h, board.cpp |
| Exact solver (MRV backtrack) | backtracksearch.h/cpp |
| One ant (ACS step) | sudokuant.h/cpp |
| Single-colony ACS + SA | sudokuantsystem.h/cpp |
| SA (fill, swap, Metropolis, clean) | simulatedannealing.h/cpp |
| Colony interface for ants | antcolonyinterface.h |
| Parallel colonies + ring/random + 3-source | parallelsudokuantsystem.h/cpp |
| CLI + solver choice | solvermain.cpp |
| Timer, args | timer.h, arguments.h |
| Solver interface | sudokusolver.h |

Use this document to drive your code review: go file-by-file in the order above and use the section headers and line references to “discuss every line” in a structured way.
