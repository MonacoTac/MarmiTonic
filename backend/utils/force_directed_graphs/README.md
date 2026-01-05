# Force Directed Graph Simulation

This project provides a high-performance Python implementation for visualizing large graphs using force-directed layout algorithms. It leverages multiprocessing and shared memory for efficient computation and renders the final output as a Deep Zoom Image (DZI) for interactive exploration.

## Features

- **Efficient Layout Calculation:** Uses a force-directed algorithm optimized with multiprocessing and shared memory to handle large graphs.
- **SQLite Backend:** Stores graph data in an SQLite database to manage memory usage effectively.
- **High-Resolution Rendering:** Renders the graph into tiled images (Deep Zoom format) allowing for smooth zooming and panning of massive graphs.
- **Interactive Viewer:** Includes a simple web server to serve the visualization locally.

## Requirements

- Python 3.8+
- `numpy`
- `Pillow`
- `rich`

## Installation

1. Clone the repository.
2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Prepare Data

First, you need to ingest your graph data into an SQLite database. The project includes a parser for the Facebook combined dataset format (edge list).

```bash
python parse_facebook.py --input_file facebook_combined.txt --db_path facebook.db
```

- `--input_file`: Path to your input text file containing edges (e.g., `facebook_combined.txt`).
- `--db_path`: Path where the SQLite database will be created.

### 2. Run Simulation

Run the simulation to compute the layout and render the graph.

```bash
python run.py facebook.db
```

This script will:
- Load data from the specified database.
- Compute the force-directed layout.
- Render the visualization to `output.dzi` and `output_files/`.

### 3. View Results

Start the local web server to view the generated visualization.

```bash
python serve_visualization.py
```

This will start a server at `http://localhost:8000` and automatically open your default web browser to the visualization.

## Project Structure

- `run.py`: Main entry point for running the simulation and rendering.
- `parse_facebook.py`: Utility to parse edge lists and populate the SQLite database.
- `serve_visualization.py`: Simple HTTP server to view the results.
- `force_directed_graphs/`: Package containing the core logic.
  - `layout.py`: Implementation of the force-directed layout algorithm.
  - `render.py`: Logic for rendering the graph into tiles.
  - `data.py`: Database interaction and data loading.
  - `main.py`: Orchestrates the simulation process.
- `output.dzi` & `output_files/`: Generated Deep Zoom Image files.
