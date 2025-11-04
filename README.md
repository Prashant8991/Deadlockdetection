# Advanced Deadlock Detection & Avoidance System

A comprehensive system for analyzing, detecting, and avoiding deadlocks in concurrent systems using Wait-For Graph analysis and Banker's Algorithm.

## Features

### Core Functionality
- **Deadlock Detection**: Detects circular waits using Wait-For Graph cycle analysis
- **Deadlock Avoidance**: Validates safe states using Banker's Algorithm
- **Multiple Cycle Finding**: Identifies all deadlock cycles in complex systems
- **Step-by-step Analysis**: Detailed iteration logs showing algorithm progression

### Visualization
- **Wait-For Graph Display**: Visual representation of process dependencies
- **Color-Coded Nodes**: Easy identification of deadlocked processes
- **Resource Flow Arrows**: Shows allocation and request relationships
- **Interactive UI**: Dark-themed professional interface

### Analysis Features
- **Safe Sequence Computation**: Finds valid execution order for processes
- **Resource Shortage Analysis**: Identifies blocking resource constraints
- **Iteration Logging**: See exactly what happens at each algorithm step
- **Example Datasets**: Pre-loaded test cases for quick learning

## Quick Start

### Running the GUI Application

```bash
python3 gui_enhanced.py
```

The application will launch with two tabs:
1. **Deadlock Detection Tab**: Analyze systems for circular waits
2. **Deadlock Avoidance Tab**: Check if states are safe

### Load Example Scenarios

Each tab has a "Load Example" button that pre-fills data:
- Example 1: 3 processes, 3 resources with deadlock scenario
- Example 2: 3 processes, 3 resources with safe state scenario

### Test the Algorithms

Run the comprehensive test suite:

```bash
python3 test_algorithms.py
```

This runs 5 test cases covering:
- Circular deadlock detection
- No-deadlock scenarios
- Safe state verification
- Unsafe state detection
- Complex multi-process systems

## Algorithm Explanation

### Deadlock Detection: Wait-For Graph

The system detects deadlocks by:
1. Building a Wait-For Graph from allocation and request matrices
2. Finding all cycles using Depth-First Search
3. Marking processes in cycles as deadlocked

**Complexity**: O(V + E) where V = processes, E = wait relationships

```
Example:
P0 holds R0, requests R1
P1 holds R1, requests R0

Wait-For Graph: P0 → P1 → P0
Result: Circular wait detected (Deadlock!)
```

### Deadlock Avoidance: Banker's Algorithm

The system checks safe states using:
1. Calculate remaining needs for each process
2. Iteratively allocate to processes that can complete
3. If all processes complete, system is safe
4. If any process cannot complete, system is unsafe

**Complexity**: O(n² × m) where n = processes, m = resources

```
Example:
Available: [10, 5, 7]
Process P0 needs [7, 5, 3] and holds [0, 1, 0]
Process P1 needs [3, 2, 2] and holds [2, 0, 0]

Iteration 1: Allocate P0 (needs ≤ available)
Iteration 2: Allocate P1 (needs ≤ updated available)

Result: Safe sequence found (P0 → P1)
```

## Input Format

### Matrices Format

All matrices should be entered as space-separated values, one row per line:

```
Example Allocation Matrix (3x2):
1 0
0 1
0 0
```

### Vector Format

Vectors should be space-separated on a single line:

```
Example Available Vector (3 resources):
10 5 7
```

## System Requirements

- Python 3.6 or higher
- tkinter (usually included with Python)
- No external dependencies

## File Structure

```
project/
├── gui_enhanced.py              # Main enhanced GUI application
├── detection.py                 # Deadlock detection algorithms
├── avoidance.py                 # Deadlock avoidance (Banker's)
├── test_algorithms.py           # Comprehensive test suite
├── README.md                    # This file
└── IMPROVEMENTS.md              # Detailed algorithm improvements
```

## How to Use

### Step 1: Enter System Configuration

- **Processes**: Number of processes (e.g., 3)
- **Resources**: Number of resource types (e.g., 3)
- **Available**: Available instances of each resource

### Step 2: Input Matrices

For Detection:
- **Allocation Matrix**: What each process currently holds
- **Request Matrix**: What each process is requesting

For Avoidance:
- **Allocation Matrix**: Current allocations
- **Max Need Matrix**: Maximum each process might ever need

### Step 3: Run Analysis

Click the analysis button to:
- Visualize the Wait-For Graph
- See detailed analysis results
- View all deadlock cycles (if any)
- Check safe sequences (if applicable)

### Step 4: Review Results

- **Deadlock Detection**: Shows all cycles and affected processes
- **Safe State Check**: Shows the safe sequence or unsafe conditions

## Example Scenarios

### Scenario 1: Circular Deadlock
```
3 Processes (P0, P1, P2)
2 Resources (R0, R1)

P0 holds R0, requests R1
P1 holds R1, requests R0

Result: Deadlock! (P0 ↔ P1)
```

### Scenario 2: Safe State
```
3 Processes (P0, P1, P2)
3 Resources (A, B, C)

Available: [10, 5, 7]
Safe sequence: P0 → P1 → P2

Result: System is SAFE
```

## Troubleshooting

### GUI won't start
- Ensure you have tkinter: `python3 -m tkinter`
- Try: `sudo apt-get install python3-tk` (Linux)

### Matrix format error
- Ensure each row has the correct number of values
- Separate values with spaces
- No extra spaces or commas

### Invalid number of resources
- Allocation columns must match number of resources
- Request columns must match number of resources

## Algorithm Improvements Over Original

| Aspect | Original | Enhanced |
|--------|----------|----------|
| Cycle Detection | Incomplete | Full DFS-based |
| Deadlock Finding | Limited | All deadlocked processes |
| Analysis Depth | Basic | Iteration-by-iteration |
| Visualization | Simple | Professional graphics |
| UI Theme | Default | Dark professional theme |
| Examples | None | Pre-loaded scenarios |

## Performance

- Detection: O(V + E) - Very fast even for large systems
- Avoidance: O(n² × m) - Instant for typical sizes
- Tested up to 10 processes and 10 resources
- Real-time GUI response for all operations

## Learning Resources

The test suite (`test_algorithms.py`) demonstrates:
- Deadlock scenarios and how they're detected
- Safe vs unsafe states
- Complex multi-process systems
- How the algorithms handle edge cases

Run it to understand the concepts better!

## Advanced Usage

### Programmatic API

```python
from detection import detect_deadlock_and_cycle
from avoidance import is_safe_state

# Detection
deadlocked, procs, cycles = detect_deadlock_and_cycle(
    processes, resources, allocation, request
)

# Avoidance
safe, sequence, details = is_safe_state(
    processes, resources, available, allocation, max_need
)
```

## License

Educational use. Part of operating systems curriculum demonstrating resource allocation and deadlock concepts.

## Questions or Issues?

Review IMPROVEMENTS.md for detailed algorithm documentation or run test_algorithms.py to see working examples.
