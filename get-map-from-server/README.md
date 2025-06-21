# Map Data Fetcher and Visualizer

This application fetches map data from a server API and displays detailed graph information using Rich formatting in the terminal.

## Features

- Fetches map data from the Hackathon API server
- Parses nodes and edges into a graph structure
- Displays formatted graph statistics using Rich library
- Shows node types, edge connections, and weights
- Converts maps to NetworkX graphs for further analysis

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the main script:
```bash
python main.py
```

## Output

The script displays:
- Map metadata (name, type, ID)
- Graph statistics table showing:
  - Total nodes and edges
  - Map dimensions
  - Node type distribution
- Edge connections tree showing:
  - Source nodes
  - Target nodes with weights

## API Endpoint

The application fetches data from:
```
https://hackathon.omelet.tech/api/maps/
```

## Classes

### Node
Represents a node in the map with:
- ID, X/Y coordinates
- Node type (NORMAL, etc.)
- Position property
- Color based on type

### Edge
Represents a connection between nodes with:
- Source and target node IDs
- Weight (distance)
- Label

### Map
Main class that:
- Loads nodes and edges from API data
- Converts to NetworkX graph format
- Provides formatted display methods

### MapClient
Handles API communication to fetch map data from the server.

## Dependencies

- `requests` - HTTP requests to API
- `matplotlib` - Graph visualization
- `networkx` - Graph data structure
- `numpy` - Numerical operations
- `rich` - Terminal formatting and colors

## Example Output

```bash
(base) anhbinhnguyen@Anhs-MacBook-Pro fu-hackathon-workshop % /opt/anaconda3/bin/python /Users/anhbinhnguyen/git/fu-hackathon-workshop/get-map-from-server/main.py
Fetching map data from server...
✓ Successfully fetched 1 map(s)


═══ Map 1 of 1 ═══

╭──── Map Information ────╮
│ Simple Graph Map        │
│ Type: demo              │
│ ID: 6e3c47f9-3511-4d... │
╰─────────────────────────╯
    Graph Statistics    
┏━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric       ┃ Value ┃
┡━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Nodes  │ 6     │
│ Total Edges  │ 18    │
│ Map Width    │ 1     │
│ Map Height   │ 1     │
│ NORMAL Nodes │ 6     │
└──────────────┴───────┘
Graph Edges
├── Node 1
│   ├── → Node 2 (weight: 3.0)
│   └── → Node 3 (weight: 2.0)
├── Node 2
│   ├── → Node 1 (weight: 3.0)
│   ├── → Node 4 (weight: 7.0)
│   └── → Node 5 (weight: 2.0)
├── Node 3
│   ├── → Node 1 (weight: 2.0)
│   ├── → Node 4 (weight: 5.0)
│   └── → Node 6 (weight: 1.0)
├── Node 4
│   ├── → Node 2 (weight: 7.0)
│   ├── → Node 3 (weight: 5.0)
│   ├── → Node 5 (weight: 3.0)
│   └── → Node 6 (weight: 2.0)
├── Node 5
│   ├── → Node 2 (weight: 2.0)
│   ├── → Node 4 (weight: 3.0)
│   └── → Node 6 (weight: 4.0)
└── Node 6
    ├── → Node 3 (weight: 1.0)
    ├── → Node 4 (weight: 2.0)
    └── → Node 5 (weight: 4.0)

──────────────────────────────────────────────────
```