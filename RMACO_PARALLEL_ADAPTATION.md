# Parallelization: Adaptation from Yang et al. (RMACO)

This document describes what was **adapted and used** from the paper:

**Yang, Q., Fang, L., & Duan, X. (2016).** *RMACO: a randomly matched parallel ant colony optimization.* World Wide Web, 19(5), 1009–1022.  
DOI: 10.1007/s11280-015-0369-6

The paper proposes **RMACO** (Randomly Matched parallel ACO) for the **Traveling Salesman Problem (TSP)** using **Max-Min Ant System (MMAS)** and **MPI**. Our implementation targets **Sudoku** and uses **ACS** (Lloyd & Amos) per colony, but we adopt the **parallelization procedure**: dual communication topology (ring + random match), three-source pheromone update, and adaptive exchange cycle.

---

## 1. What We Adopted from the Paper

### 1.1 Dual communication topology (Fig. 1, Section 2.2)

- **Paper:** RMACO uses two topologies:
  - **Ring (solid):** Fixed. Processor \(i\) sends **iteration-best** to processor \((i+1) \bmod n\).
  - **Randomly matched (dotted):** Variable. Each processor sends **best-so-far** to a **randomly matched** partner (match-array).
- **Our implementation:**
  - **Ring:** Colony \(i\) sends **iteration-best** to colony \((i+1) \bmod n\).  
    **Code:** `CommunicateRingTopology()` in `parallelsudokuantsystem.cpp`; `subColonies[nextId]->ReceiveIterationBest(iterationBests[i])` with `nextId = (i + 1) % numSubColonies`.
  - **Random:** Each colony receives **best-so-far** from the predecessor in a **random permutation** (match-array).  
    **Code:** `CommunicateRandomTopology(matchArray)`; match-array is a random permutation of colony IDs; receiver = `matchArray[i]`, sender = `matchArray[(i + n - 1) % n]`.

So we use the **same dual topology**: ring for iteration-best, random match for best-so-far.

### 1.2 Match-array (Section 2.2.1, Fig. 2)

- **Paper:** Master generates a **random number sequence** (array of processor IDs 0..n-1), broadcasts to all; slave at position \(i\) in the array **receives** best-so-far from the processor at position \((i+n-1) \bmod n\), **sends** to the processor at position \((i+1) \bmod n\).
- **Our implementation:** One thread (last to reach the barrier) acts as “master”: generates **match-array** = random permutation of \([0, ..., n-1]\) via `GenerateMatchArray()` (std::shuffle). Each colony `matchArray[i]` receives best-so-far from colony `matchArray[(i + numSubColonies - 1) % numSubColonies]`.  
  **Code:** `GenerateMatchArray()` (iota + shuffle); `CommunicateRandomTopology(matchArray)` uses `fromPos = (i + numSubColonies - 1) % numSubColonies`, `fromColonyId = matchArray[fromPos]`.

So **match-array** and the receive-from-predecessor rule match the paper.

### 1.3 Three-source pheromone update (Equation 5)

- **Paper:** \(\tau_{ij}(t+1) = (1-\rho)\,\tau_{ij}(t) + \Delta\tau_{ij}\), where \(\Delta\tau_{ij} = \Delta\tau_{ij}^1 + \Delta\tau_{ij}^2 + \Delta\tau_{ij}^3\):
  - \(\Delta\tau_{ij}^1\): iteration-best from **this** processor
  - \(\Delta\tau_{ij}^2\): iteration-best **received from ring neighbor**
  - \(\Delta\tau_{ij}^3\): best-so-far **received from randomly matched** processor
- **Our implementation:** Same structure. On **communication** iterations we call `UpdatePheromoneWithCommunication()` which sums contributions from:
  - **Source 1:** local iteration-best (`iterationBest`, `iterationBestScore`)
  - **Source 2:** received iteration-best from ring (`receivedIterationBest`, `receivedIterationBestScore`)
  - **Source 3:** received best-so-far from random topology (`receivedBestSol`, `receivedBestSolScore`)  
  **Code:** `SubColony::UpdatePheromoneWithCommunication()` in `parallelsudokuantsystem.cpp`; `pherValue1`, `pherValue2`, `pherValue3` and per-cell summation into `contributions[j]`, then \(\tau \leftarrow (1-\rho)\tau + \rho\cdot\text{contributions}\).

So the **three-source formula** and the roles of iteration-best (ring) and best-so-far (random) match the paper. (We use ACS pheromone rule and reward formula per Lloyd & Amos; the *structure* of three sources is from Yang et al.)

### 1.4 Adaptive exchange cycle (Corollary 3, Section 2.3.2; Section 3.1)

- **Paper:** **Non-fixed exchange cycle.** Early iterations: **long** cycle (e.g. interval 100); mid-to-late: **short** cycle (e.g. interval 10). RM experiment: “exchange cycle before 200 iteration interval = 100, after 200 iteration interval = 10”.
- **Our implementation:** We use the **same rule**.  
  **Code:** `CalculateInterval(iter)` in `parallelsudokuantsystem.cpp`: if `iteration < 200` return 100, else return 10. Communication happens when `iter % interval == 0`.

So **adaptive exchange cycle** and the 200/100/10 scheme are taken from the paper.

### 1.5 When to exchange (Algorithm: if i % interval == 0)

- **Paper:** After path construction, if the **exchange cycle** is reached (\(i \bmod \text{interval} = 0\)), all sub-colonies exchange information; then pheromone is updated with Equation (5). Otherwise pheromone is updated with Equation (4) (local only).
- **Our implementation:** After each iteration we compute `interval = CalculateInterval(iter)`. If `iter % interval == 0` we do barrier, ring exchange, random exchange, then **three-source** pheromone update. Otherwise we do **standard (Algorithm 0)** pheromone update only.  
  **Code:** In `SubColonyWorker`, `if (iter % interval == 0)` → barrier, master runs `CommunicateRingTopology()` and `CommunicateRandomTopology(matchArray)`, then each colony calls `UpdatePheromoneWithCommunication()`; else `UpdatePheromone()` and bestPher decay.

So the **exchange condition** (interval-based) and the **split** between local-only vs three-source update match the paper.

---

## 2. What We Adapted (Problem and ACO Variant)

- **Problem:** Paper uses TSP (tours, path cost); we use Sudoku (board, cells filled / conflicts). So “solution” and “cost” are different; the **communication procedure** (what to exchange and when) is the same.
- **ACO variant:** Paper uses **MMAS** (pheromone bounds, iteration-best deposit rule, etc.); we use **ACS** per colony (Lloyd & Amos: best-so-far only, BVE, etc.). So per-colony **pheromone rules** follow our ACS reference; the **parallel layout** (sub-colonies, ring, random match, three-source combination) follows Yang et al.
- **Concurrency:** Paper uses **MPI** (distributed); we use **threads** (shared memory). So “processor” → “thread/sub-colony”, “broadcast match-array” → one thread generating match-array and all threads using it after barrier.

---

## 3. Where the paper’s concepts appear in the code

| Paper concept | Our implementation |
|---------------|--------------------|
| Ring topology (iteration-best) | `CommunicateRingTopology()`; colony \(i\) → \((i+1) \bmod n\) |
| Randomly matched (best-so-far) | `GenerateMatchArray()` + `CommunicateRandomTopology(matchArray)`; receive from predecessor in permutation |
| Match-array | `std::vector<int> matchArray`; `std::iota` + `std::shuffle` |
| \(\Delta\tau^1 + \Delta\tau^2 + \Delta\tau^3\) | `UpdatePheromoneWithCommunication()`; `pherValue1` + `pherValue2` + `pherValue3` per cell |
| Adaptive interval (before 200: 100; after 200: 10) | `CalculateInterval(iter)`: `iteration < 200 ? 100 : 10` |
| Exchange when \(i \bmod \text{interval} = 0\) | `if (iter % interval == 0)` then barrier, exchange, three-source update |
| iteration-best / best-so-far | `iterationBest` / `bestSol`; received: `receivedIterationBest` / `receivedBestSol` |

---

## 4. References

- **Yang, Q., Fang, L., & Duan, X. (2016).** RMACO: a randomly matched parallel ant colony optimization. *World Wide Web*, 19(5), 1009–1022.  
  Used for: parallelization procedure—dual topology (ring + random match), three-source pheromone update (Eq. 5), adaptive exchange cycle (Corollary 3), match-array. Adapted: problem (Sudoku vs TSP), ACO variant (ACS vs MMAS), concurrency (threads vs MPI).

- **Lloyd, H., & Amos, M. (2021).** Solving Sudoku with Ant Colony Optimization. *IEEE Transactions on Games*.  
  Used for: per-colony ACS (pheromone, BVE). See `ACO_PAPER_VERIFICATION.md`.
