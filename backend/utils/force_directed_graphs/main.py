
import argparse
import logging
import time
import sys
import sqlite3
import multiprocessing
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.logging import RichHandler
from rich.table import Table

from .data import setup_database, load_graph_data, update_database
from .layout import compute_layout
from .render import render_visualization

console = Console()

def main():
    parser = argparse.ArgumentParser(description='Visualize a graph from SQLite database using force-directed layout.')
    parser.add_argument('db_path', nargs='?', default='test_large.db', help='Path to the SQLite database file.')
    parser.add_argument('output_image_path', nargs='?', default='output.png', help='Path to save the output image.')

    args = parser.parse_args()

    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=False)]
    )

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            tm = time.time()
            conn, cursor = setup_database(args.db_path)
            nodes, labels, edges, adj, pos = load_graph_data(cursor, progress)
            
            # Prepare edges_list for rendering
            edges_list = [(i, j) for i in adj for j in adj[i] if i < j]
            tm2 = time.time()
            logging.log(25, f'Loaded data: {tm2-tm}')
            
            pos = compute_layout(pos, adj, args, progress)

            tm3 = time.time()
            logging.log(25, f'Computed layout: {tm3-tm2}')

            tm_update_start = time.time()
            update_database(conn, cursor, pos, progress)
            tm_update_end = time.time()

            tm_render_start = time.time()
            render_stats = render_visualization(pos, edges_list, labels, args, progress)
            tm_render_end = time.time()

            total_time = time.time() - tm
            logging.log(25, f'Total time: {total_time}')

            # Display stats table
            table = Table(title="Execution Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")

            table.add_row("Nodes", str(len(nodes)))
            table.add_row("Edges", str(len(edges_list)))
            table.add_row("Total Time", f"{total_time:.2f}s")
            table.add_row("Loading Time", f"{tm2 - tm:.2f}s")
            table.add_row("Layout Time", f"{tm3 - tm2:.2f}s")
            table.add_row("DB Update Time", f"{tm_update_end - tm_update_start:.2f}s")
            table.add_row("Total Render Time", f"{tm_render_end - tm_render_start:.2f}s")
            
            if render_stats:
                table.add_row("  - Base Layer Time", f"{render_stats['base_layer_time']:.2f}s")
                table.add_row("  - Pyramid Time", f"{render_stats['pyramid_time']:.2f}s")
                table.add_row("Active Zones (Chunks)", str(render_stats['num_zones']))
                if render_stats['num_zones'] > 0:
                    avg_per_zone = render_stats['base_layer_time'] / render_stats['num_zones'] * 1000
                    table.add_row("Avg Time per Zone", f"{avg_per_zone:.2f}ms")
                table.add_row("Image Size", f"{render_stats['image_size'][0]}x{render_stats['image_size'][1]}")
                table.add_row("Max Zoom Level", str(render_stats['max_level']))

            console.print(table)

    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()
