# Simulated Annealing (SA) Integration – CP to MT Codebase

This document describes how the Simulated Annealing implementation from the CP (Constraint Programming) codebase is integrated into the MT (Multi-Threaded) codebase and how to use it without affecting effectiveness.

## Implementation

- **Source:** Same algorithm as CP-ACS-Simulated Annealing (`simulatedannealing.cpp` / `simulatedannealing.h`).
- **Behaviour:** Fill empty cells per block, cost = empty cells + row/column duplicates, box-preserving swap neighbourhood, geometric cooling (0.995), stopping temp 0.01, initial temp 1.5. Post-process with `CleanDuplicates()`.

## Where SA Is Used in MT

| Component | When SA runs | Input | Acceptance |
|-----------|----------------|-------|------------|
| **SudokuAntSystem (alg=0)** | Every `safreq` iterations (if `safreq` > 0), after iteration-best update | best-so-far | Default: accept only if improvement or cost 0 (solved). Optional `--saAccept 1`: always accept (CP-like). |
| **ParallelSudokuAntSystem (alg=2)** | Per sub-colony, every `safreq` iterations (if `safreq` > 0) | colony best-so-far | Default: hybrid (improvement **or** same/fewer cells with ≥5 conflict reduction). Optional `--saAccept 1`: always accept (CP-like). |

## Preserving Effectiveness

- **Single-colony (alg=0):** Default: SA result is accepted only when `saScore > bestSol.FixedCellCount()` or `(saScore == bestSol.FixedCellCount() && cost == 0)` (solved), so effectiveness is preserved. Optional **always-accept**: use `--saAccept 1` to always copy the SA result (CP-like).

- **Parallel (alg=2):** Default is **hybrid** acceptance:
  - Accept if strict improvement (more fixed cells), or
  - Accept if same or up to 2 fewer fixed cells **and** conflict count drops by ≥5.
  Use `--saAccept 1` only when you want CP-like “always accept” behaviour (e.g. for reproducibility with CP).

## Command-Line

- **`--safreq n`**  
  - Applies to **both** alg=0 and alg=2.  
  - SA runs every `n` iterations (0 = disabled).  
  - Example: `--safreq 100` for CP-like frequency.

- **`--saAccept n`**  
  - Applies to **alg=0 and alg=2**.  
  - `0` (default): conservative/hybrid acceptance (recommended for effectiveness).  
  - `1`: always accept SA result (CP-like).

## Examples

```bash
# Single-colony with SA every 100 iterations (CP-like frequency); default acceptance
./sudokusolver --alg 0 --file instances/logic-solvable/platinumblond.txt --ants 30 --timeout 120 --safreq 100 --verbose

# Single-colony with SA every 100 iterations and always-accept (CP-like)
./sudokusolver --alg 0 --file instances/logic-solvable/platinumblond.txt --ants 30 --timeout 120 --safreq 100 --saAccept 1 --verbose

# Parallel with SA every 100 iterations, hybrid acceptance (default)
./sudokusolver --alg 2 --file instances/logic-solvable/platinumblond.txt --subcolonies 4 --ants 30 --timeout 120 --safreq 100 --verbose

# Parallel with SA every 100 iterations, always accept (CP-like)
./sudokusolver --alg 2 --file instances/logic-solvable/platinumblond.txt --subcolonies 4 --ants 30 --timeout 120 --safreq 100 --saAccept 1 --verbose
```

## Summary

- SA in MT is the **same implementation** as in CP.
- It is used in **alg=0** (single-colony) and **alg=2** (each sub-colony).
- Acceptance in MT is **conservative by default** (single-colony: only when better or solved; parallel: hybrid) so that using SA does not reduce effectiveness.
- Use `--safreq 100` for CP-like frequency and `--saAccept 1` (alg=2 only) for CP-like acceptance when needed.
