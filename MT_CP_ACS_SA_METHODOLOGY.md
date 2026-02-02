# Multithreaded Constraint Programming-Ant Colony System-Simulated Annealing Algorithm

## Algorithm Overview

The Multithreaded Constraint Programming-Ant Colony System-Simulated Annealing (MT-CP-ACS-SA) algorithm integrates constraint propagation, ant colony optimization, and simulated annealing within a parallel multi-threaded framework. The algorithm operates in three main phases: (1) an initial constraint propagation pass, (2) parallel ant-based solution construction with periodic simulated annealing refinement, and (3) inter-thread communication with global pheromone updates.

## Line-by-Line Algorithm Description

### Initial Pass: Constraint Propagation (Lines 1-6)

The algorithm begins with a preprocessing phase that exploits the deterministic nature of constraint satisfaction. **Line 1** reads the input puzzle, establishing the initial problem state. **Lines 2-4** perform constraint propagation: for each cell with a fixed value, the algorithm propagates constraints to eliminate invalid values from neighboring cells' domains. This forward-checking mechanism reduces the search space before the stochastic search begins. **Line 5** initializes the global pheromone matrix τ[i][k] to a uniform initial value τ₀, where i represents a cell index and k represents a possible value. This uniform initialization ensures equal exploration probability across all value assignments initially. **Line 6** initializes the global iteration counter g to zero, tracking the number of main loop iterations.

### Main Loop: Parallel Thread Execution (Lines 7-56)

The main search loop (**Line 7**) continues until either the puzzle is solved or a timeout is reached, providing both solution quality and computational resource bounds. Within this loop, multiple threads execute concurrently, each maintaining an independent ant colony with its own pheromone matrix.

#### Ant-Based Solution Construction (Lines 8-21)

**Line 8** initiates parallel execution across all threads, where each thread operates independently with its own ant population and pheromone matrix. This parallelization enables simultaneous exploration of different regions of the solution space. **Line 9** provides each ant with a local copy of the puzzle, ensuring thread-safety and preventing race conditions during solution construction. **Line 10** assigns each ant to a different starting cell, promoting diversity in the initial search directions.

**Lines 11-20** implement the core ant construction process. **Line 11** iterates through all cells in the puzzle, ensuring each ant constructs a complete solution. **Line 12** processes each ant sequentially within a thread, allowing ants to build solutions independently. **Lines 13-18** handle the value selection and constraint propagation for each cell. **Line 13** checks whether the current cell's value is fixed (either initially or by constraint propagation). If not fixed, **Line 14** selects a value from the cell's domain using the ACS decision rule, which balances exploitation (choosing values with high pheromone) and exploration (probabilistic selection). **Line 15** fixes the selected value in the cell, and **Line 16** propagates constraints to update neighboring cells' domains, maintaining constraint consistency throughout construction. **Line 17** applies the local pheromone update using Equation ①: τ[i][k] ← 0.9·τ[i][k] + 0.1·τ₀. This update reduces pheromone on the chosen path, encouraging subsequent ants to explore alternative assignments and preventing premature convergence. **Line 19** moves to the next cell in the construction sequence, and **Line 20** completes the ant processing loop.

#### Simulated Annealing Refinement (Lines 22-42)

After each iteration of ant construction, the algorithm applies simulated annealing to refine the best solution found. **Line 22** identifies the iteration-best ant within each thread, representing the highest-quality solution constructed in the current iteration. **Line 23** checks whether simulated annealing should be applied based on the frequency parameter SA_freq, ensuring SA is applied periodically rather than every iteration to balance computational cost and solution quality.

When SA is triggered, **Line 24** generates an initial candidate solution b from the iteration-best ant. **Line 25** initializes the temperature T to the starting temperature T₀, which controls the acceptance probability of worse solutions. **Lines 26-39** implement the simulated annealing cooling schedule. **Line 26** continues the SA loop while the temperature exceeds the minimum threshold β. **Line 27** generates a neighbor solution b' using a neighborhood operator, typically swapping values or reassigning cells while maintaining constraint satisfaction. **Line 28** calculates the cost difference ΔC = Cost_b' - Cost_b, where cost represents the number of constraint violations or unfilled cells.

**Lines 29-34** handle the acceptance of improving or equal solutions. If ΔC ≤ 0 (the neighbor is better or equal), **Line 30** accepts the neighbor by setting b ← b'. **Lines 31-33** check if a complete solution is found (Cost_b = 0), and if so, terminate the SA process immediately. **Lines 35-37** implement the probabilistic acceptance of worse solutions: if ΔC > 0, the neighbor is accepted with probability exp(-ΔC/T), allowing the algorithm to escape local optima. As temperature decreases, this probability diminishes, transitioning from exploration to exploitation. **Line 38** performs temperature cooling, typically using a geometric schedule T ← α·T where α < 1, or an exponential schedule.

**Line 40** applies a CleanDuplicates operation to remove redundant or conflicting assignments from the solution b, ensuring constraint consistency. **Line 41** updates the thread's best ant with the refined solution b, incorporating the SA improvements into the colony's knowledge base.

#### Inter-Thread Communication and Global Updates (Lines 44-54)

The algorithm employs periodic synchronization to exchange information between threads. **Line 44** checks whether the communication interval has been reached, determining when threads should exchange solutions. When communication occurs, **Line 45** synchronizes all threads at a barrier, ensuring all threads have completed their current iteration before exchanging information. This barrier synchronization prevents race conditions and ensures consistent solution exchange.

**Line 46** generates a random matching array that determines the communication topology for best-so-far solutions. **Line 47** exchanges iteration-best solutions using a ring topology, where each thread sends its iteration-best to the next thread in the ring. This topology ensures fast propagation of recent discoveries while maintaining a structured communication pattern. **Line 48** exchanges best-so-far solutions using a random topology based on the matching array, promoting diverse information exchange and preventing premature convergence to similar solutions across threads.

**Line 49** performs the global pheromone update using Equation ⑫, which incorporates information from three sources: the local iteration-best, the received iteration-best from the ring topology, and the received best-so-far from the random topology. This three-source update is formulated as τ_ij(t+1) = (1-ρ_comm)·τ_ij(t) + Δτ_ij, where Δτ_ij = Δτ_ij^1 + Δτ_ij^2 + Δτ_ij^3, and ρ_comm is the communication evaporation rate (typically 0.05, lighter than the standard rate to preserve shared information longer).

When communication does not occur (**Line 51**), **Line 52** applies the standard global pheromone update using Equation ⑦: τ_ij(t+1) = (1-ρ)·τ_ij(t) + ρ·Δτ_best, where ρ is the standard evaporation rate (typically 0.9) and Δτ_best is the pheromone contribution from the local best-so-far solution. This update reinforces only the best solution found by each thread independently. **Line 53** performs best value evaporation, decaying the best pheromone value to gradually reduce the influence of older high-quality solutions and encourage continued exploration.

**Line 55** increments the global iteration counter g, and **Line 56** completes the main loop, returning to **Line 7** to check termination conditions.

## Key Design Features

The MT-CP-ACS-SA algorithm integrates multiple optimization techniques through several key design decisions. The constraint propagation phase (Lines 2-4) reduces the search space deterministically before stochastic search begins, improving efficiency. The parallel thread architecture (Line 8) enables simultaneous exploration of diverse solution regions, with each thread maintaining independent pheromone matrices to preserve search diversity. The periodic simulated annealing application (Lines 23-41) provides local refinement without excessive computational overhead, while the dual communication topology (Lines 47-48) balances structured information flow (ring) with diverse exploration (random). The three-source pheromone update (Line 49) effectively combines local discoveries with information from neighboring threads, while the selective application of communication updates (Lines 44-54) maintains computational efficiency by avoiding synchronization overhead on every iteration.

## Detailed ACS Process

The Ant Colony System (ACS) component of MT-CP-ACS-SA implements a sophisticated pheromone-based search mechanism that guides ants through the solution space. This section provides a comprehensive discussion of the ACS implementation.

### Pheromone Matrix Initialization

The algorithm maintains a pheromone matrix τ[i][k] where i represents a cell index and k represents a possible value (digit). **Initialization** sets all pheromone values uniformly to τ₀ = 1/numCells, ensuring equal exploration probability across all value assignments initially. This uniform initialization prevents bias toward any particular solution region at the start of the search. Each thread maintains its own independent pheromone matrix, preserving search diversity across parallel colonies.

### Solution Construction Process

Each ant constructs a complete solution through an iterative process. **Initialization** (Line 9-10) provides each ant with a local copy of the puzzle and assigns it to a different starting cell, promoting diversity in initial search directions. The construction proceeds in **rounds** (Line 11): for each cell in the puzzle, all ants simultaneously take one step (Line 12), visiting cells in a circular order that wraps around after reaching the last cell.

### ACS Decision Rule: Exploitation vs. Exploration

The core of the ACS process lies in the **decision rule** (Line 14) that determines how an ant selects a value for an unfixed cell. The implementation uses the standard ACS pseudo-random proportional rule, which balances exploitation and exploration through a parameter q₀ (typically 0.9).

**Exploitation Mode** (greedy selection): When a random number r ∈ [0,1] satisfies r < q₀ (occurring with probability q₀ = 90% by default), the ant selects the value with the highest pheromone concentration from the cell's domain. This greedy selection exploits accumulated knowledge, reinforcing promising solution components. The implementation iterates through all possible values in the cell's domain, comparing pheromone values τ[i][k] and selecting the maximum.

**Exploration Mode** (roulette wheel selection): When r ≥ q₀ (occurring with probability 1-q₀ = 10% by default), the ant uses probabilistic selection based on pheromone concentrations. The implementation constructs a cumulative probability distribution: for each valid value k in the cell's domain, it calculates the cumulative sum of pheromone values. A random value is then generated uniformly from [0, totalPheromone], and the first value whose cumulative pheromone exceeds this random value is selected. This roulette wheel mechanism ensures that values with higher pheromone have higher selection probability, while still allowing exploration of less-promising alternatives.

The q₀ parameter critically controls the exploration-exploitation trade-off: higher q₀ values (e.g., 0.9) favor exploitation, leading to faster convergence but potentially premature stagnation, while lower values favor exploration, maintaining diversity at the cost of slower convergence.

### Constraint Propagation Integration

After value selection (Line 15), the algorithm immediately propagates constraints (Line 16), eliminating invalid values from neighboring cells' domains. This forward-checking mechanism maintains constraint consistency throughout construction, reducing the search space dynamically. If constraint propagation results in an empty domain for any cell, the ant increments a failure counter, which affects solution quality evaluation.

### Local Pheromone Update

Following each value selection, the algorithm applies a **local pheromone update** (Line 17) using Equation ①: τ[i][k] ← 0.9·τ[i][k] + 0.1·τ₀. This update reduces pheromone on the chosen path by evaporating 90% of the current value and replacing it with 10% of the initial pheromone level. This mechanism serves multiple purposes: (1) it prevents all ants from converging to the same path too quickly, (2) it encourages subsequent ants to explore alternative assignments, and (3) it maintains a minimum pheromone level τ₀, ensuring all paths remain selectable with non-zero probability.

The local update is applied immediately after each ant's decision, creating a dynamic feedback mechanism where frequently chosen paths become less attractive, naturally distributing ants across different solution regions.

### Solution Evaluation and Iteration-Best Selection

After all ants complete solution construction (Lines 11-20), the algorithm evaluates each ant's solution quality (Line 22). The evaluation metric is the number of successfully filled cells, calculated as total cells minus failed cells (cells that became empty due to constraint propagation). The ant with the maximum filled cells is designated as the **iteration-best**, representing the highest-quality solution found in the current iteration.

### Pheromone Value Calculation

The algorithm calculates a pheromone value for each solution using the formula: Δτ = numCells / (numCells - cellsFilled). This formula produces exponentially increasing pheromone values as solutions approach completion. For example, in a 9×9 Sudoku (81 cells), a solution with 50 filled cells yields Δτ = 81/31 ≈ 2.61, while 75 filled cells yields Δτ = 81/6 = 13.5, and 80 filled cells yields Δτ = 81/1 = 81.0. This exponential growth ensures that near-complete solutions receive substantially more reinforcement, guiding the search toward completion.

### Global Pheromone Updates

The algorithm employs two types of global pheromone updates, applied mutually exclusively based on communication intervals.

**Standard Global Update** (Equation ⑦, Line 52): On non-communication iterations, the algorithm applies the standard ACS global update: τ_ij(t+1) = (1-ρ)·τ_ij(t) + ρ·Δτ_best, where ρ = 0.9 is the evaporation rate and Δτ_best is the pheromone value of the local best-so-far solution. This update reinforces only the edges (cell-value pairs) present in the best-so-far solution, with 90% of the new pheromone coming from the best solution and 10% retained from the previous value. The update is selective: only cells with fixed values in the best-so-far solution receive reinforcement, leaving other pheromone values unchanged. This selective update maintains computational efficiency while focusing reinforcement on promising solution components.

**Three-Source Communication Update** (Equation ⑫, Line 49): On communication intervals, the algorithm applies a more sophisticated update that incorporates information from three sources: (1) the local iteration-best solution, (2) the received iteration-best from the ring topology neighbor, and (3) the received best-so-far from the random topology partner. The update formula is: τ_ij(t+1) = (1-ρ_comm)·τ_ij(t) + ρ_comm(Δτ_ij^1 + Δτ_ij^2 + Δτ_ij^3), where Δτ_ij = Δτ_ij^1 + Δτ_ij^2 + Δτ_ij^3. Each source contributes its pheromone value (calculated using the same formula) to cells where it has fixed values. When multiple sources agree on a value for a cell, their contributions are summed, creating stronger reinforcement for consensus solutions. The communication evaporation rate ρ_comm = 0.05 is significantly lighter than the standard rate, preserving shared information longer and allowing inter-thread knowledge to accumulate.

The implementation uses **selective evaporation**: only cell-value pairs that receive contributions are updated, avoiding unnecessary computation on unchanged pheromone values. This selective approach maintains efficiency while enabling rich information integration from multiple sources.

### Best-So-Far Tracking and Decay

The algorithm maintains a **best-so-far** solution for each thread, representing the highest-quality solution ever found by that colony. When an iteration-best solution has a higher pheromone value than the current best-so-far, both the solution and its pheromone value are updated together (Lines 272-277). This ensures consistency between the solution representation and its associated pheromone value.

On non-communication iterations, after the standard global update, the best pheromone value undergoes **decay** (Line 53): bestPher ← bestPher × (1 - bestEvap), where bestEvap is typically 0.005. This gradual decay reduces the influence of older high-quality solutions over time, encouraging continued exploration and preventing the algorithm from becoming overly focused on solutions that may no longer be optimal as the search progresses.

### Integration with Constraint Programming

The ACS process is tightly integrated with constraint propagation throughout solution construction. Before value selection, constraint propagation has already reduced each cell's domain to valid values only. After value selection, immediate constraint propagation updates neighboring cells' domains, potentially eliminating values and reducing future search space. This integration ensures that ants only consider constraint-satisfying assignments, dramatically reducing the effective search space compared to unconstrained search.

### Computational Characteristics

The ACS construction process has time complexity O(nAnts × nCells × nValues) per iteration, where nValues represents the average domain size. The pheromone updates have complexity O(nCells) for standard updates and O(nCells × nSources) for communication updates, where nSources = 3. The space complexity is O(nCells × nValues) per thread for pheromone storage. The parallel architecture enables near-linear speedup with the number of threads, subject to communication overhead that occurs periodically rather than every iteration.

## Detailed Simulated Annealing Process

The Simulated Annealing (SA) component provides local refinement of ACS solutions through temperature-controlled local search with probabilistic acceptance of worse solutions. SA is applied periodically (every SA_freq iterations) to the best-so-far solution from each thread's colony (Line 23).

### Initialization

**Solution Preparation** (Line 24): SA receives the iteration-best solution and fills empty cells within each sub-grid (box) by randomly assigning missing values, ensuring box constraints are satisfied while row/column constraints may be violated. This focuses SA on resolving conflicts rather than filling cells.

**Temperature Parameters** (Line 25): Initial temperature T₀ = 1.5, stopping temperature β = 0.01, and geometric cooling rate α = 0.995. The cooling schedule T(k) = T₀·α^k requires approximately 1000 cycles to reach β, providing sufficient exploration (early cycles) and exploitation (late cycles).

**Cost Function** (Line 28): The cost function evaluates solution quality by counting missing values in rows and columns. For each row, the number of missing values from the set {1...n} is counted, and these counts are summed to yield RowCost C_r. Similarly, for each column, missing values are counted and summed to yield ColCost C_l. The total cost is C = C_r + C_l (Equation 9). Since `FillEmptyCells()` ensures sub-grid constraints are satisfied and all cells are filled before annealing, sub-grid cost remains zero and only row/column violations contribute to cost. Cost = 0 indicates a valid complete solution, triggering early termination (Lines 31-33).

### Main Annealing Loop

The core process (Lines 26-39) iterates while temperature exceeds β, applying neighborhood operations and probabilistic acceptance.

**Neighborhood Operator** (Line 27): Constraint-preserving swaps between cells in the same box maintain sub-grid satisfaction. The operator (1) detects conflicts in rows/columns to identify problematic cells, (2) randomly selects a conflicted cell, (3) selects a swap partner from the same box (non-fixed), and (4) computes cost incrementally as oldCost + (after_conflicts - before_conflicts), achieving O(1) cost updates.

**Solution Acceptance** (Lines 29-37): Improving solutions (ΔC ≤ 0) are always accepted. Worsening solutions (ΔC > 0) are accepted with probability P = exp(-ΔC/T). At high temperature (T ≈ 1.5), worse solutions have significant acceptance probability (e.g., exp(-2/1.5) ≈ 0.264), enabling exploration. As temperature decreases, acceptance probability diminishes rapidly, transitioning to exploitation. This mechanism enables escape from local optima.

**Temperature Cooling** (Line 38): After each neighborhood operation, temperature is updated using geometric cooling: T_new = α·T (Equation 11), where the cooling factor α satisfies 0 < α < 1. When α is large, the cooling rate is slow (more exploration), and when α is small, the cooling rate is fast (quicker transition to exploitation). The implementation uses α = 0.995, providing gradual temperature reduction. The annealing process terminates when either the puzzle is solved (cost = 0) or the temperature reaches the stopping temperature β, which controls the duration and number of cycles the SA will execute.

### Post-Processing and Integration

**Conflict Resolution** (Line 40): After annealing, duplicate removal identifies conflicts and clears cells with highest conflict counts, trading conflicts for empty cells that ACS can fill in subsequent iterations.

**Integration** (Line 41): The best solution encountered during annealing is integrated into the colony's knowledge base for global pheromone updates, maintaining best-solution tracking throughout the process.

### Computational Characteristics

Time complexity is O(nCycles × nCells) per application, where nCycles ≈ 1000. Space complexity is O(nCells). Periodic application (every SA_freq iterations) keeps overhead manageable relative to ACS computation.

## Computational Complexity

The time complexity per iteration is O(nAnts × nCells × nValues) for ant construction, O(nCells) for constraint propagation, O(nCycles × nCells) for simulated annealing (when applied, where nCycles ≈ 1000), and O(nThreads × nCells) for communication. The space complexity is O(nThreads × nCells × nValues) for pheromone matrices and O(nThreads × nCells) for solution storage. The parallel architecture provides near-linear speedup with the number of threads, subject to communication overhead.

