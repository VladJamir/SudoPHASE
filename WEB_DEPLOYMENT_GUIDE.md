# Web Deployment Guide: Sudoku Solver Web Application

## Overview

This guide outlines the deployment strategy for exposing your MT-CP-ACS-SA Sudoku solver as a web-based application (SudoPHASE). The architecture follows a client-server model where a web frontend communicates with a backend API that wraps your C++ solver.

---

## System Architecture

### Three-Tier Architecture

```
┌─────────────┐
│    USER     │ (Browser/Client)
└──────┬──────┘
       │ HTTP/HTTPS
       │ (JSON)
       ▼
┌─────────────────────────────┐
│   SudoPHASE Web App         │
│   (Frontend + API Gateway)  │
│   - React/Vue/Angular       │
│   - REST API (Node.js/Python/Go)
└──────┬──────────────────────┘
       │ Process Spawning / FFI
       │ (JSON/Protocol Buffer)
       ▼
┌─────────────────────────────┐
│   C++ Solver Executable     │
│   (MT-CP-ACS-SA Algorithm)  │
│   - Compiled binary         │
│   - Multi-threaded          │
└─────────────────────────────┘
```

---

## Deployment Options

### Option 1: REST API + Process Spawning (Recommended for MVP)

**Technology Stack:**
- **Backend API**: Node.js (Express) or Python (Flask/FastAPI)
- **Frontend**: React, Vue.js, or vanilla JavaScript
- **Communication**: Spawn C++ executable as child process
- **Data Format**: JSON

**Pros:**
- ✅ Simple to implement
- ✅ Language-agnostic (any language can spawn processes)
- ✅ Easy debugging (can test C++ binary independently)
- ✅ Minimal code changes needed

**Cons:**
- ❌ Process creation overhead (acceptable for Sudoku solving)
- ❌ Limited real-time progress updates
- ❌ Higher memory usage (one process per request)

**Implementation:**

```javascript
// Node.js Example (Express)
const express = require('express');
const { spawn } = require('child_process');
const app = express();

app.post('/api/solve', async (req, res) => {
    const { puzzle, algorithm, timeout, params } = req.body;
    
    // Spawn C++ solver process
    const solver = spawn('./sudokusolver', [
        '--puzzle', puzzle,
        '--alg', algorithm || '2',
        '--timeout', timeout || '120',
        '--subcolonies', params?.subcolonies || '4',
        '--ants', params?.ants || '30',
        '--verbose'
    ]);
    
    let output = '';
    let error = '';
    
    solver.stdout.on('data', (data) => {
        output += data.toString();
    });
    
    solver.stderr.on('data', (data) => {
        error += data.toString();
    });
    
    solver.on('close', (code) => {
        // Parse output
        const solution = parseSolution(output);
        res.json({
            success: code === 0,
            solution: solution,
            time: extractTime(output),
            iterations: extractIterations(output)
        });
    });
});
```

---

### Option 2: REST API + C++ Library (Better Performance)

**Technology Stack:**
- **Backend API**: Python (Flask/FastAPI) with ctypes or cffi
- **Alternative**: Go with CGO, or Node.js with node-ffi/napi
- **Frontend**: React/Vue.js
- **Communication**: Direct function calls via FFI (Foreign Function Interface)

**Pros:**
- ✅ Lower overhead (no process creation)
- ✅ Faster response times
- ✅ Better resource utilization
- ✅ Can expose more functionality

**Cons:**
- ❌ Requires refactoring C++ code into a library
- ❌ Platform-specific compilation (Windows/Linux)
- ❌ More complex build process

**Implementation Steps:**

1. **Refactor C++ into a library:**

```cpp
// solver_api.h
extern "C" {
    struct SolveResult {
        int success;
        char* solution;
        double time;
        int iterations;
    };
    
    SolveResult* solve_sudoku(
        const char* puzzle_string,
        int algorithm,
        int timeout,
        int subcolonies,
        int ants,
        float q0,
        float rho,
        float evap,
        int safreq
    );
    
    void free_result(SolveResult* result);
}
```

2. **Python wrapper (using ctypes):**

```python
# solver_wrapper.py
from ctypes import CDLL, Structure, c_int, c_char_p, c_double, POINTER
import json

class SolveResult(Structure):
    _fields_ = [
        ("success", c_int),
        ("solution", c_char_p),
        ("time", c_double),
        ("iterations", c_int)
    ]

lib = CDLL('./libsudokusolver.so')  # or .dll on Windows

def solve(puzzle_string, algorithm=2, timeout=120, **params):
    result = lib.solve_sudoku(
        puzzle_string.encode('utf-8'),
        algorithm,
        timeout,
        params.get('subcolonies', 4),
        params.get('ants', 30),
        params.get('q0', 0.9),
        params.get('rho', 0.9),
        params.get('evap', 0.005),
        params.get('safreq', 0)
    )
    
    solution_data = {
        'success': result.contents.success,
        'solution': result.contents.solution.decode('utf-8'),
        'time': result.contents.time,
        'iterations': result.contents.iterations
    }
    
    lib.free_result(result)
    return solution_data
```

---

### Option 3: WebAssembly (WASM) - Browser-Based (Advanced)

**Technology Stack:**
- **Compiler**: Emscripten (C++ to WebAssembly)
- **Frontend**: React/Vue.js with WASM module
- **Communication**: Direct JavaScript-WASM calls

**Pros:**
- ✅ Runs entirely in browser (no server needed for solving)
- ✅ Offline capability
- ✅ Lower server load
- ✅ Fast (near-native performance)

**Cons:**
- ❌ Limited threading support in WASM (Parallel ACS may be restricted)
- ❌ Larger download size (~1-5MB)
- ❌ Complex build configuration
- ❌ May need to disable multithreading

**Implementation:**

```bash
# Compile with Emscripten
emcc solver.cpp -o solver.js \
    -s EXPORTED_FUNCTIONS='["_solve_sudoku"]' \
    -s EXPORTED_RUNTIME_METHODS='["ccall", "cwrap"]' \
    -s ALLOW_MEMORY_GROWTH=1 \
    -O3
```

---

## Recommended Approach: Option 1 (Process Spawning)

For your thesis deployment, **Option 1** is recommended because:

1. **Quick to implement** - Minimal code changes
2. **Stable** - Process isolation prevents crashes
3. **Multi-threaded ready** - Your parallel solver works without modification
4. **Easy debugging** - Can test C++ binary separately
5. **Platform portable** - Works on Linux/Windows/macOS

---

## Implementation Guide

### Phase 1: Backend API Setup

#### 1.1 Project Structure

```
web-app/
├── backend/
│   ├── src/
│   │   ├── server.js          # Express server
│   │   ├── solver.js          # Solver wrapper
│   │   └── parser.js          # Output parser
│   ├── package.json
│   └── solver/                # C++ executable
│       └── sudokusolver       # Compiled binary
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SudokuGrid.jsx
│   │   │   ├── SolverPanel.jsx
│   │   │   └── ResultsPanel.jsx
│   │   ├── App.jsx
│   │   └── api.js            # API client
│   └── package.json
└── README.md
```

#### 1.2 Backend API (Node.js/Express)

**Install dependencies:**
```bash
npm init -y
npm install express cors dotenv
npm install --save-dev nodemon
```

**server.js:**
```javascript
const express = require('express');
const cors = require('cors');
const { solveSudoku } = require('./solver');

const app = express();
app.use(cors());
app.use(express.json());

app.post('/api/solve', async (req, res) => {
    try {
        const {
            puzzle,           // String: "53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79"
            algorithm = 2,    // 0=ACS, 1=Backtrack, 2=Parallel ACS
            timeout = 120,    // seconds
            params = {}
        } = req.body;

        // Validate puzzle
        if (!puzzle || puzzle.length === 0) {
            return res.status(400).json({ error: 'Puzzle string required' });
        }

        const result = await solveSudoku({
            puzzle,
            algorithm,
            timeout,
            subcolonies: params.subcolonies || 4,
            ants: params.ants || 30,
            q0: params.q0 || 0.9,
            rho: params.rho || 0.9,
            evap: params.evap || 0.005,
            safreq: params.safreq || 0
        });

        res.json(result);
    } catch (error) {
        console.error('Solver error:', error);
        res.status(500).json({ error: error.message });
    }
});

app.get('/api/health', (req, res) => {
    res.json({ status: 'ok' });
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
```

**solver.js:**
```javascript
const { spawn } = require('child_process');
const path = require('path');

function solveSudoku(options) {
    return new Promise((resolve, reject) => {
        const solverPath = path.join(__dirname, '../solver/sudokusolver');
        const args = [
            '--puzzle', options.puzzle,
            '--alg', options.algorithm.toString(),
            '--timeout', options.timeout.toString(),
            '--subcolonies', options.subcolonies.toString(),
            '--ants', options.ants.toString(),
            '--q0', options.q0.toString(),
            '--rho', options.rho.toString(),
            '--evap', options.evap.toString(),
            '--verbose'
        ];

        if (options.safreq > 0) {
            args.push('--safreq', options.safreq.toString());
        }

        const solver = spawn(solverPath, args, {
            cwd: path.dirname(solverPath),
            timeout: (options.timeout + 10) * 1000 // Add 10s buffer
        });

        let stdout = '';
        let stderr = '';

        solver.stdout.on('data', (data) => {
            stdout += data.toString();
        });

        solver.stderr.on('data', (data) => {
            stderr += data.toString();
        });

        solver.on('close', (code) => {
            try {
                const result = parseSolverOutput(stdout, stderr, code);
                resolve(result);
            } catch (error) {
                reject(new Error(`Failed to parse output: ${error.message}`));
            }
        });

        solver.on('error', (error) => {
            reject(new Error(`Solver process error: ${error.message}`));
        });
    });
}

function parseSolverOutput(stdout, stderr, exitCode) {
    // Parse verbose output format:
    // Solution:
    // [grid representation]
    // solved in X.XX
    // iterations: N
    
    const lines = stdout.split('\n');
    let solution = '';
    let time = 0;
    let iterations = 0;
    let success = exitCode === 0;

    let inSolution = false;
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        if (line.startsWith('Solution:')) {
            inSolution = true;
            continue;
        }
        
        if (inSolution && line.length > 0 && !line.includes('solved in')) {
            solution += line + '\n';
            continue;
        }
        
        if (line.startsWith('solved in')) {
            const match = line.match(/solved in ([\d.]+)/);
            if (match) time = parseFloat(match[1]);
            inSolution = false;
            continue;
        }
        
        if (line.startsWith('iterations:')) {
            const match = line.match(/iterations: (\d+)/);
            if (match) iterations = parseInt(match[1]);
            continue;
        }
        
        if (line.includes('failed')) {
            success = false;
            const match = line.match(/failed in time ([\d.]+)/);
            if (match) time = parseFloat(match[1]);
        }
    }

    // Clean up solution string
    solution = solution.trim();

    return {
        success,
        solution,
        time,
        iterations,
        rawOutput: stdout
    };
}

module.exports = { solveSudoku };
```

---

### Phase 2: Frontend Setup

#### 2.1 React Frontend

**Install dependencies:**
```bash
npx create-react-app frontend
cd frontend
npm install axios
```

**src/api.js:**
```javascript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';

export const solveSudoku = async (puzzle, options = {}) => {
    const response = await axios.post(`${API_BASE_URL}/solve`, {
        puzzle,
        algorithm: options.algorithm || 2,
        timeout: options.timeout || 120,
        params: {
            subcolonies: options.subcolonies || 4,
            ants: options.ants || 30,
            q0: options.q0 || 0.9,
            rho: options.rho || 0.9,
            evap: options.evap || 0.005,
            safreq: options.safreq || 0
        }
    });
    return response.data;
};
```

**src/components/SudokuGrid.jsx:**
```jsx
import React, { useState } from 'react';
import { solveSudoku } from '../api';

function SudokuGrid() {
    const [puzzle, setPuzzle] = useState('');
    const [solution, setSolution] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    const handleSolve = async () => {
        setLoading(true);
        setResult(null);
        try {
            const response = await solveSudoku(puzzle, {
                algorithm: 2,
                timeout: 120,
                subcolonies: 4,
                ants: 30
            });
            setSolution(response.solution);
            setResult(response);
        } catch (error) {
            console.error('Solve error:', error);
            alert('Failed to solve puzzle: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="sudoku-solver">
            <h1>SudoPHASE - Sudoku Solver</h1>
            <div>
                <label>Puzzle String:</label>
                <textarea
                    value={puzzle}
                    onChange={(e) => setPuzzle(e.target.value)}
                    placeholder="Enter puzzle string (use . for empty cells)"
                    rows="3"
                />
            </div>
            <button onClick={handleSolve} disabled={loading || !puzzle}>
                {loading ? 'Solving...' : 'Solve'}
            </button>
            {result && (
                <div>
                    <h2>Result</h2>
                    <p>Status: {result.success ? 'Solved!' : 'Failed'}</p>
                    <p>Time: {result.time}s</p>
                    <p>Iterations: {result.iterations}</p>
                    <pre>{solution}</pre>
                </div>
            )}
        </div>
    );
}

export default SudokuGrid;
```

---

### Phase 3: Deployment

#### 3.1 Local Development

1. **Build C++ solver:**
```bash
cd <your-solver-directory>
make -f Makefile
cp sudokusolver ../web-app/backend/solver/
```

2. **Start backend:**
```bash
cd web-app/backend
npm install
npm start
```

3. **Start frontend:**
```bash
cd web-app/frontend
npm install
npm start
```

4. **Access:** http://localhost:3000

#### 3.2 Production Deployment Options

**A. Docker Deployment (Recommended)**

**Dockerfile (Backend):**
```dockerfile
FROM node:18-alpine

# Install build dependencies for C++
RUN apk add --no-cache g++ make

WORKDIR /app

# Copy backend code
COPY backend/package*.json ./
RUN npm install --production

# Copy C++ solver source and build
COPY src/ ./src/
COPY Makefile ./
RUN make -f Makefile && cp sudokusolver ./solver/

COPY backend/ ./

EXPOSE 3001
CMD ["node", "server.js"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "3001:3001"
    environment:
      - NODE_ENV=production
      - PORT=3001

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend
```

**B. Cloud Platform Deployment**

**Heroku:**
```bash
# Add buildpacks for C++ and Node.js
heroku buildpacks:add heroku/nodejs
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-apt

# Deploy
git push heroku main
```

**AWS (EC2/ECS):**
- Use EC2 with Ubuntu
- Install Node.js and build tools
- Deploy using Docker or directly

**DigitalOcean App Platform:**
- Supports Docker deployments
- Automatic scaling
- Simple configuration

#### 3.3 Environment Configuration

**.env (Backend):**
```
PORT=3001
NODE_ENV=production
SOLVER_PATH=./solver/sudokusolver
MAX_TIMEOUT=300
```

**.env (Frontend):**
```
REACT_APP_API_URL=http://localhost:3001/api
```

---

## API Specification

### POST /api/solve

**Request:**
```json
{
    "puzzle": "53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79",
    "algorithm": 2,
    "timeout": 120,
    "params": {
        "subcolonies": 4,
        "ants": 30,
        "q0": 0.9,
        "rho": 0.9,
        "evap": 0.005,
        "safreq": 0
    }
}
```

**Response:**
```json
{
    "success": true,
    "solution": "534678912\n672195348\n198342567...",
    "time": 14.523,
    "iterations": 1247,
    "rawOutput": "..."
}
```

---

## Security Considerations

1. **Input Validation:**
   - Validate puzzle string format and length
   - Sanitize all inputs
   - Limit timeout values (max 5 minutes)

2. **Rate Limiting:**
   - Implement rate limiting (e.g., 10 requests/minute per IP)
   - Use express-rate-limit middleware

3. **Resource Limits:**
   - Set process memory limits
   - Limit concurrent solver instances
   - Queue system for high load

4. **Error Handling:**
   - Don't expose internal errors to users
   - Log errors server-side
   - Graceful degradation

---

## Performance Optimization

1. **Caching:**
   - Cache solutions for identical puzzles (Redis)
   - Cache puzzle validation results

2. **Connection Pooling:**
   - Reuse solver processes (process pool)
   - Consider using worker threads (Node.js)

3. **Async Processing:**
   - For long-running solves, use job queue (Bull/BullMQ)
   - WebSocket for progress updates

4. **Load Balancing:**
   - Multiple backend instances
   - Nginx reverse proxy

---

## Testing Strategy

1. **Unit Tests:**
   - Test API endpoints
   - Test parser functions
   - Test puzzle validation

2. **Integration Tests:**
   - Test full solve flow
   - Test error handling
   - Test timeout scenarios

3. **Load Testing:**
   - Use Apache Bench or Artillery
   - Test concurrent requests
   - Measure response times

---

## Monitoring & Logging

1. **Logging:**
   - Use Winston or Pino for structured logging
   - Log solve times, success rates
   - Log errors with stack traces

2. **Monitoring:**
   - Use PM2 for process management
   - Monitor CPU/memory usage
   - Track API response times

3. **Analytics:**
   - Track puzzle difficulty
   - Track algorithm usage
   - Track solve success rates

---

## Quick Start Checklist

- [ ] Build C++ solver executable
- [ ] Create backend API (Node.js/Python)
- [ ] Implement solver wrapper with process spawning
- [ ] Create frontend (React/Vue)
- [ ] Test local deployment
- [ ] Add input validation and error handling
- [ ] Set up production environment
- [ ] Configure logging and monitoring
- [ ] Deploy to cloud platform
- [ ] Test production deployment

---

## Next Steps

1. **Start with MVP**: Get basic solve functionality working
2. **Add UI polish**: Better grid visualization, progress indicators
3. **Add features**: Puzzle generator, difficulty selection, history
4. **Optimize**: Caching, connection pooling, performance tuning
5. **Scale**: Load balancing, containerization, auto-scaling

Good luck with your deployment! 🚀


















