
import sqlite3
import logging
import random
import numpy as np
from collections import defaultdict

def setup_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Alter nodes table to add x and y columns if not present
    logging.info("Checking and altering nodes table...")
    cursor.execute("PRAGMA table_info(nodes)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'x' not in columns:
        cursor.execute("ALTER TABLE nodes ADD COLUMN x REAL")
    if 'y' not in columns:
        cursor.execute("ALTER TABLE nodes ADD COLUMN y REAL")
    conn.commit()
    return conn, cursor

def load_graph_data(cursor, progress):
    task_id = progress.add_task("[green]Loading Data...", total=None)

    # Read nodes
    progress.update(task_id, description="[green]Reading nodes from database...")
    cursor.execute("SELECT id, label FROM nodes")
    nodes = cursor.fetchall()
    labels = {node[0]: node[1] for node in nodes}

    # Read edges
    progress.update(task_id, description="[green]Reading edges from database...")
    cursor.execute("SELECT source, target FROM edges")
    edges = cursor.fetchall()

    # Create adjacency list
    progress.update(task_id, description="[green]Creating adjacency list...")
    adj = defaultdict(list)
    for source, target in edges:
        adj[source].append(target)
        adj[target].append(source)

    # Initialize positions
    progress.update(task_id, description="[green]Initializing positions...")
    pos = {}
    for node_id in labels:
        cursor.execute("SELECT x, y FROM nodes WHERE id = ?", (node_id,))
        result = cursor.fetchone()
        if result and result[0] is not None and result[1] is not None:
            # Handle bytes data from SQLite
            x_val = result[0] if isinstance(result[0], float) else float(result[0]) if isinstance(result[0], (int, str)) else result[0]
            y_val = result[1] if isinstance(result[1], float) else float(result[1]) if isinstance(result[1], (int, str)) else result[1]
            if isinstance(x_val, bytes):
                x_val = np.frombuffer(x_val, dtype=np.float32)[0]
            if isinstance(y_val, bytes):
                y_val = np.frombuffer(y_val, dtype=np.float32)[0]
            pos[node_id] = [float(x_val), float(y_val)]
        else:
            pos[node_id] = [random.uniform(-10, 10), random.uniform(-10, 10)]
            
    progress.update(task_id, description="[green]Data loaded", completed=1, total=1)
    return nodes, labels, edges, adj, pos

def update_database(conn, cursor, pos, progress):
    # Update database with positions
    task_id = progress.add_task("[blue]Updating database...", total=len(pos))
    
    # Use executemany for better performance and progress tracking
    # Convert pos dict to list of tuples
    data = [(position[0], position[1], node_id) for node_id, position in pos.items()]
    
    # Split into chunks to update progress
    chunk_size = 1000
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        cursor.executemany("UPDATE nodes SET x = ?, y = ? WHERE id = ?", chunk)
        progress.update(task_id, advance=len(chunk))
        
    conn.commit()
    progress.update(task_id, description="[blue]Database updated", completed=len(pos))
