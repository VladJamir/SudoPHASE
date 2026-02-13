# Figure 5: Components and their Relationships in a Research Manuscript

## Overview

This diagram illustrates the interconnected components and their relationships in the research manuscript on **Parallel Ant Colony System with Simulated Annealing for Sudoku Puzzle Solving**.

---

## Visual Diagram (Mermaid)

```mermaid
graph TB
    subgraph Problem["Statement of the Problem"]
        P[Problem:<br/>Sudoku Solving<br/>NP-Complete]
        SP1[Sub-problem 1:<br/>Large Grid Complexity]
        SP2[Sub-problem 2:<br/>Sequential ACS Limitations]
        SP3[Sub-problem 3:<br/>Local Optima Trapping]
        H[Hardness Group:<br/>NP-Complete<br/>Exponential Search Space]
        A[Analysis:<br/>Computational Complexity<br/>Performance Bottlenecks]
    end

    subgraph Objectives["Objectives of the Study"]
        GO[General Objective:<br/>Develop Parallel ACS<br/>for Sudoku Solving]
        SO1[Specific Objective 1:<br/>Design Multi-threaded<br/>ACS Architecture]
        SO2[Specific Objective 2:<br/>Integrate Simulated<br/>Annealing Refinement]
        SO3[Specific Objective 3:<br/>Implement Communication<br/>Topologies]
        N[Noun:<br/>Algorithm<br/>System<br/>Performance]
        V[Verb:<br/>Develop<br/>Integrate<br/>Evaluate]
        R[Relationship:<br/>Algorithm → Performance<br/>Integration → Quality]
    end

    subgraph Scope["Scope & Limitations"]
        D[Delimitations:<br/>16×16 Sudoku Grids<br/>Multi-threaded Architecture]
        INC[Inclusions:<br/>Constraint Propagation<br/>ACS + SA Hybrid<br/>Ring & Random Topologies]
        EXC[Exclusions:<br/>GPU Implementation<br/>Distributed Systems<br/>Other Metaheuristics]
        DS[Dataset:<br/>16×16 Instances<br/>3000+ Puzzles<br/>Various Difficulty Levels]
    end

    subgraph Literature["Review of Related Literature"]
        RL[Related Literature:<br/>ACO for CSP<br/>Parallel Metaheuristics<br/>Sudoku Solving Methods]
        CT[Concepts & Techniques:<br/>Ant Colony Optimization<br/>Simulated Annealing<br/>Constraint Programming]
        RR[Results & Recommendations:<br/>ACS Performance Studies<br/>Parallel ACO Benchmarks]
        OP[Open Problems:<br/>Scalability Issues<br/>Communication Overhead<br/>Hybrid Integration]
    end

    subgraph Framework["Theoretical & Conceptual Framework"]
        TYPE[Type Abstract:<br/>MT-CP-ACS-SA<br/>Hybrid Metaheuristic]
        REU[Reused:<br/>Standard ACS<br/>Constraint Propagation<br/>SA Cooling Schedule]
        MOD[Modified:<br/>Multi-threaded ACS<br/>Three-source Pheromone<br/>Adaptive Communication]
        NOV[Novel:<br/>Ring + Random Topology<br/>SA-ACS Integration<br/>Selective Pheromone Update]
    end

    subgraph Methodology["Methodology"]
        SOL[Solution:<br/>Parallel ACS Algorithm<br/>with SA Refinement]
        ALG[Algorithms:<br/>Algorithm 0: Standard ACS<br/>Algorithm 1: Backtracking<br/>Algorithm 2: Parallel ACS]
        PROOF[Proof/Protocols:<br/>Thread Synchronization<br/>Pheromone Update Rules<br/>Termination Conditions]
    end

    subgraph Outputs["Results & Recommendations"]
        OUT[Outputs:<br/>Performance Metrics<br/>Solution Quality<br/>Scalability Analysis]
        RES[Results:<br/>Speedup Achieved<br/>Success Rates<br/>Parameter Sensitivity]
        REC[Recommendations:<br/>Optimal Parameters<br/>Future Extensions<br/>Application Domains]
        OP2[Open Problems:<br/>GPU Parallelization<br/>Dynamic Topologies<br/>Other CSP Applications]
    end

    %% Problem relationships
    P -->|composed of| SP1
    P -->|composed of| SP2
    P -->|composed of| SP3
    SP1 -->|generates| GO
    SP2 -->|generates| GO
    SP3 -->|generates| GO
    H -->|identifies| TYPE
    A -.->|uses| P
    A -.->|uses| RL

    %% Objectives relationships
    GO -->|composed of| SO1
    GO -->|composed of| SO2
    GO -->|composed of| SO3
    SO1 -->|composed of| N
    SO1 -->|composed of| V
    SO2 -->|composed of| N
    SO2 -->|composed of| V
    SO3 -->|composed of| N
    SO3 -->|composed of| V
    N -->|defines| R
    V -->|defines| R
    R -->|defines| N
    R -->|defines| V
    SO1 -->|generates| SOL
    SO2 -->|generates| SOL
    SO3 -->|generates| SOL

    %% Scope relationships
    SO1 -->|influences| D
    SO2 -->|influences| D
    SO3 -->|influences| D
    D -->|composed of| INC
    D -->|composed of| EXC
    INC -->|generates| DS
    EXC -->|generates| DS
    DS -.->|uses| SOL

    %% Literature relationships
    RL -->|composed of| CT
    RL -->|composed of| RR
    RL -->|composed of| OP
    A -.->|uses| RL
    RL -.->|returns to| REU

    %% Framework relationships
    REU -->|contributes to| TYPE
    MOD -->|contributes to| TYPE
    NOV -->|contributes to| TYPE
    TYPE -->|connects to| N
    TYPE -->|connects to| V
    TYPE -->|connects to| SOL
    H -->|identifies/uses| TYPE

    %% Methodology relationships
    SOL -->|composed of| ALG
    SOL -->|composed of| PROOF
    ALG -.->|uses| Methodology

    %% Outputs relationships
    SOL -->|generates| OUT
    OUT -->|composed of| RES
    OUT -->|composed of| REC
    OUT -->|composed of| OP2

    %% Styling
    classDef problemStyle fill:#ffcccc,stroke:#cc0000,stroke-width:2px
    classDef objectiveStyle fill:#ccffcc,stroke:#00cc00,stroke-width:2px
    classDef scopeStyle fill:#ccccff,stroke:#0000cc,stroke-width:2px
    classDef literatureStyle fill:#ffffcc,stroke:#cccc00,stroke-width:2px
    classDef frameworkStyle fill:#ffccff,stroke:#cc00cc,stroke-width:2px
    classDef methodologyStyle fill:#ccffff,stroke:#00cccc,stroke-width:2px
    classDef outputStyle fill:#ccffcc,stroke:#00cc00,stroke-width:2px

    class P,SP1,SP2,SP3,H,A problemStyle
    class GO,SO1,SO2,SO3,N,V,R objectiveStyle
    class D,INC,EXC,DS scopeStyle
    class RL,CT,RR,OP literatureStyle
    class TYPE,REU,MOD,NOV frameworkStyle
    class SOL,ALG,PROOF methodologyStyle
    class OUT,RES,REC,OP2 outputStyle
```

---

## Text-Based Component Relationships

### 1. Statement of the Problem

**Main Problem:**
- **Problem**: Solving large-scale Sudoku puzzles (16×16) efficiently using metaheuristic approaches
- **Complexity**: NP-Complete problem with exponential search space

**Sub-problems:**
- **Sub-problem 1**: Computational complexity of large grid sizes (16×16, 25×25)
- **Sub-problem 2**: Limitations of sequential Ant Colony System (ACS) in terms of convergence speed
- **Sub-problem 3**: Local optima trapping in metaheuristic search

**Hardness Classification:**
- **Hardness (group)**: NP-Complete constraint satisfaction problem
- **Search Space**: Exponential growth with grid size (16^256 for 16×16 grids)

**Analysis:**
- **Analysis** → uses → **Problem**: Computational complexity analysis
- **Analysis** → uses → **Related Literature**: Performance bottleneck identification

**Flow:**
- **Sub-problem** → generates → **General Objective**

---

### 2. Objectives of the Study

**General Objective:**
- Develop a Parallel Ant Colony System with Simulated Annealing for efficient Sudoku puzzle solving

**Specific Objectives:**
- **Specific Objective 1**: Design and implement a multi-threaded ACS architecture with independent sub-colonies
- **Specific Objective 2**: Integrate Simulated Annealing for local solution refinement
- **Specific Objective 3**: Implement adaptive communication topologies (ring and random) for inter-thread information exchange

**Component Structure:**
- **Specific Objective** → composed of → **Noun** (Algorithm, System, Performance)
- **Specific Objective** → composed of → **Verb** (Develop, Integrate, Evaluate)
- **Noun** ↔ **Verb** ↔ **Relationship** (bidirectional definition)

**Flow:**
- **Specific Objective** → generates → **Solution**

---

### 3. Scope & Limitations

**Delimitations:**
- **Delimitations**: Focus on 16×16 Sudoku grids, multi-threaded CPU implementation, ACS-based approach

**Composition:**
- **Delimitations** → composed of → **Inclusions**: Constraint propagation, ACS+SA hybrid, ring & random topologies
- **Delimitations** → composed of → **Exclusions**: GPU implementation, distributed systems, other metaheuristics (GA, PSO)

**Dataset Generation:**
- **Inclusions** + **Exclusions** → generates → **Dataset**
- **Dataset**: 16×16 instances, 3000+ puzzles, various difficulty levels

**Flow:**
- **Dataset** → uses → **Solution**

---

### 4. Review of Related Literature

**Related Literature:**
- Ant Colony Optimization for Constraint Satisfaction Problems
- Parallel Metaheuristics and their classification
- Existing Sudoku solving methods (exact and metaheuristic)

**Composition:**
- **Related Literature** → composed of → **Concepts & Techniques**: ACO, SA, Constraint Programming
- **Related Literature** → composed of → **Results & Recommendations**: ACS performance studies, parallel ACO benchmarks
- **Related Literature** → composed of → **Open Problems**: Scalability issues, communication overhead, hybrid integration

**Relationships:**
- **Analysis** → uses → **Related Literature**
- **Related Literature** → returns to → **Reused** (in Theoretical Framework)

---

### 5. Theoretical & Conceptual Framework

**Type Abstract:**
- **Type <abstract>**: MT-CP-ACS-SA (Multithreaded Constraint Programming-Ant Colony System-Simulated Annealing)

**Component Sources:**
- **Reused**: Standard ACS algorithm, constraint propagation techniques, SA cooling schedules
- **Modified**: Multi-threaded ACS architecture, three-source pheromone update mechanism, adaptive communication intervals
- **Novel**: Combined ring + random topology, SA-ACS integration strategy, selective pheromone update protocol

**Connections:**
- **Type <abstract>** ↔ **Noun** (defines algorithm components)
- **Type <abstract>** ↔ **Verb** (defines operations)
- **Type <abstract>** → connects to → **Solution**

**Identification:**
- **Hardness (group)** → identifies/uses → **Type <abstract>**

---

### 6. Methodology

**Solution:**
- **Solution**: Parallel ACS Algorithm with Simulated Annealing Refinement

**Composition:**
- **Solution** → composed of → **Algorithms**:
  - Algorithm 0: Standard Ant Colony System
  - Algorithm 1: Backtracking Search
  - Algorithm 2: Parallel ACS with Communication
- **Solution** → composed of → **Proof/Protocols**:
  - Thread synchronization mechanisms
  - Pheromone update mathematical formulations
  - Termination conditions and convergence criteria

**Self-reference:**
- **Algorithms** → uses → **Methodology** (methodology defines how algorithms are applied)

---

### 7. Results & Recommendations

**Outputs:**
- **Outputs**: Performance metrics, solution quality measures, scalability analysis

**Composition:**
- **Outputs** → composed of → **Results & Recommendations**:
  - Speedup achieved through parallelization
  - Success rates across different puzzle difficulties
  - Parameter sensitivity analysis
- **Outputs** → composed of → **Open Problems (offshoot)**:
  - GPU parallelization opportunities
  - Dynamic topology adaptation
  - Application to other CSP domains

**Flow:**
- **Solution** → generates → **Outputs**

---

## Relationship Types

### Solid Lines (Composition/Structure)
- **Problem** → composed of → **Sub-problem**
- **General Objective** → composed of → **Specific Objective**
- **Delimitations** → composed of → **Inclusions/Exclusions**
- **Related Literature** → composed of → **Concepts/Results/Open Problems**
- **Solution** → composed of → **Algorithms/Proof**
- **Outputs** → composed of → **Results/Recommendations/Open Problems**

### Dashed Arrows (Generation/Usage)
- **Sub-problem** → generates → **General Objective**
- **Specific Objective** → generates → **Solution**
- **Inclusions/Exclusions** → generates → **Dataset**
- **Dataset** → uses → **Solution**
- **Solution** → generates → **Outputs**
- **Analysis** → uses → **Problem** and **Related Literature**
- **Hardness (group)** → identifies/uses → **Type <abstract>**
- **Related Literature** → returns to → **Reused**

### Influence Arrows
- **Specific Objective** → influences → **Delimitations**

### Bidirectional Relationships
- **Noun** ↔ **Verb** ↔ **Relationship** (mutual definition)
- **Type <abstract>** ↔ **Noun/Verb** (defines and is defined by)

---

## Key Research Flow

1. **Problem Identification** → Analysis of Sudoku solving complexity and sequential ACS limitations
2. **Objective Setting** → Development of parallel ACS with SA integration objectives
3. **Scope Definition** → Delimitation to 16×16 grids and multi-threaded architecture
4. **Literature Review** → Survey of ACO, parallel metaheuristics, and Sudoku solving methods
5. **Framework Development** → Integration of reused, modified, and novel components into MT-CP-ACS-SA
6. **Methodology Design** → Specification of algorithms, protocols, and implementation details
7. **Solution Implementation** → Parallel ACS with communication topologies and SA refinement
8. **Evaluation & Output** → Performance analysis, results, and recommendations for future work

---

## Notes

- This diagram follows the structure of Figure 5 from the reference, adapted to the specific research on Parallel Ant Colony System for Sudoku solving
- All components are derived from the actual research documentation and implementation
- Relationships reflect the logical flow from problem identification through solution development to results
- The diagram can be used in the thesis manuscript to illustrate the research structure and component relationships

---

# Figure 2: Map of Precedences of Objectives and Results-so-far

## Overview

This diagram illustrates the precedence relationships between the study objectives and the data/conditions required for transitioning from one objective to the next in the research on **Multi-threaded Hybrid CP-ACS-SA Framework for Sudoku Solving**.

---

## Visual Diagram (Mermaid)

```mermaid
graph LR
    O1["Objective 1:<br/>Develop Multi-threaded<br/>Hybrid CP-ACS-SA Framework<br/>with Dual Communication<br/>Topologies"]
    
    O2["Objective 2:<br/>Compare Performance of<br/>Multi-threaded CP-ACS-SA<br/>against Single-colony ACS<br/>and Other Solvers"]
    
    O3["Objective 3:<br/>Conduct Ablation Study<br/>to Evaluate Performance<br/>Contribution of Each<br/>Model Component"]
    
    O4["Objective 4:<br/>Deploy Final Solver<br/>through Web-based<br/>Platform"]
    
    R1["Results-so-far 1:<br/>• Functional MT-CP-ACS-SA<br/>  Framework<br/>• Dual Topology Implementation<br/>  (Ring & Random)<br/>• Thread Synchronization<br/>• Constraint Propagation<br/>• SA Integration"]
    
    R2["Results-so-far 2:<br/>• Performance Metrics<br/>• Comparison Results<br/>• Baseline Measurements<br/>• Benchmark Data<br/>• Statistical Analysis"]
    
    R3["Results-so-far 3:<br/>• Component Contribution<br/>  Analysis<br/>• Ablation Results<br/>• Feature Importance<br/>• Optimal Configuration"]
    
    R4["Results-so-far 4:<br/>• Web Application<br/>• User Interface<br/>• API Endpoints<br/>• Deployment Infrastructure<br/>• Documentation"]
    
    O1 -->|"{data: Working Framework<br/>condition: Framework<br/>Functional & Tested}"| O2
    O1 -->|"{data: Stable Framework<br/>condition: Core Features<br/>Validated}"| O4
    O2 -->|"{data: Performance Results<br/>condition: Baseline<br/>Comparisons Complete}"| O3
    O3 -->|"{data: Optimized Configuration<br/>condition: Ablation<br/>Study Complete}"| O4
    
    O1 -.->|generates| R1
    O2 -.->|generates| R2
    O3 -.->|generates| R3
    O4 -.->|generates| R4
    
    R1 -.->|feeds into| O2
    R1 -.->|feeds into| O4
    R2 -.->|feeds into| O3
    R3 -.->|feeds into| O4
    
    %% Styling
    classDef objectiveStyle fill:#e1f5ff,stroke:#01579b,stroke-width:3px,color:#000
    classDef resultStyle fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    
    class O1,O2,O3,O4 objectiveStyle
    class R1,R2,R3,R4 resultStyle
```

---

## Text-Based Precedence Map

### Objective 1: Develop Multi-threaded Hybrid CP-ACS-SA Framework
**Description:** Develop a multi-threaded hybrid CP-ACS-SA framework for Sudoku solving integrated with dual communication topologies (unidirectional ring and random).

**Prerequisites:** None (Initial Objective)

**Results-so-far 1:**
- Functional MT-CP-ACS-SA Framework
- Dual Topology Implementation (Ring & Random)
- Thread Synchronization Mechanisms
- Constraint Propagation Integration
- Simulated Annealing Integration
- Core Algorithm Implementation

**Transition Conditions:**
- Framework is functional and tested
- Core features are validated
- Basic performance validation completed

---

### Objective 2: Compare Performance
**Description:** Compare the performance of the proposed multi-threaded CP-ACS-SA against a single-colony ACS solver and other well-known Sudoku solvers.

**Prerequisites:** 
- **From Objective 1:** Working Framework (data: functional MT-CP-ACS-SA system, condition: framework is functional and tested)

**Results-so-far 2:**
- Performance Metrics (execution time, success rate, convergence speed)
- Comparison Results (vs. single-colony ACS, vs. other solvers)
- Baseline Measurements
- Benchmark Dataset Results
- Statistical Analysis (significance tests, confidence intervals)

**Transition Conditions:**
- Baseline comparisons completed
- Performance data collected and analyzed
- Statistical significance established

---

### Objective 3: Conduct Ablation Study
**Description:** Conduct an ablation study to evaluate the performance contribution of each model component.

**Prerequisites:**
- **From Objective 2:** Performance Results (data: comparison results and baseline measurements, condition: baseline comparisons complete)

**Results-so-far 3:**
- Component Contribution Analysis
- Ablation Study Results (individual component impact)
- Feature Importance Rankings
- Optimal Configuration Identification
- Component Interaction Analysis

**Transition Conditions:**
- Ablation study complete
- Component contributions quantified
- Optimal configuration identified

---

### Objective 4: Deploy Web-based Platform
**Description:** Deploy the final solver through a web-based platform.

**Prerequisites:**
- **From Objective 1:** Stable Framework (data: core framework implementation, condition: core features validated)
- **From Objective 3:** Optimized Configuration (data: ablation results and optimal configuration, condition: ablation study complete)

**Results-so-far 4:**
- Web Application (frontend and backend)
- User Interface (puzzle input, visualization, results display)
- API Endpoints (solver service, result retrieval)
- Deployment Infrastructure (hosting, scalability)
- User Documentation and Tutorials

**Transition Conditions:**
- Web platform is functional
- Deployment is successful
- User testing completed

---

## Precedence Relationships Summary

### Direct Precedences (Sequential Flow)
1. **Objective 1 → Objective 2**
   - **Data:** Working Framework (functional MT-CP-ACS-SA system)
   - **Condition:** Framework is functional and tested

2. **Objective 2 → Objective 3**
   - **Data:** Performance Results (comparison results, baseline measurements)
   - **Condition:** Baseline comparisons complete

3. **Objective 3 → Objective 4**
   - **Data:** Optimized Configuration (ablation results, optimal component configuration)
   - **Condition:** Ablation study complete

### Parallel/Alternative Precedences
4. **Objective 1 → Objective 4** (Alternative path)
   - **Data:** Stable Framework (core framework implementation)
   - **Condition:** Core features validated
   - **Note:** This allows early deployment of a basic version, with optimization from Objective 3 integrated later

### Results Feedback Loop
- **Results-so-far 1** feeds into Objectives 2 and 4
- **Results-so-far 2** feeds into Objective 3
- **Results-so-far 3** feeds into Objective 4 (optimization)
- **Results-so-far 4** represents the final deliverable

---

## Key Dependencies

### Critical Path
**Objective 1 → Objective 2 → Objective 3 → Objective 4**

This represents the primary research progression where each objective builds upon the previous one's results.

### Parallel Development Opportunity
**Objective 1 → Objective 4** (early deployment path)

This allows for early web platform development using the initial framework, which can later be optimized based on ablation study results.

---

## Notes

- The precedence map follows the structure of Figure 2, showing sequential relationships between objectives
- Each transition is labeled with the required data and conditions
- Results-so-far are shown as outputs that feed into subsequent objectives
- The diagram illustrates both the critical path and alternative development paths
- This map can be used to track research progress and identify dependencies between objectives



