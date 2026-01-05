
import multiprocessing
from multiprocessing.shared_memory import SharedMemory
import numpy as np
import math
import logging
from .config import REPULSIVE_MULTIPLIER, ATTRACTIVE_MULTIPLIER

# Globals for workers
worker_layout_shm = None
worker_layout_pos = None

def init_worker_layout(shm_name, shape, dtype):
    global worker_layout_shm, worker_layout_pos
    worker_layout_shm = SharedMemory(name=shm_name)
    worker_layout_pos = np.ndarray(shape, dtype=dtype, buffer=worker_layout_shm.buf)

def compute_repulsive_forces_chunk(args):
    """
    Compute repulsive forces for a chunk of nodes against all other nodes.
    Optimized for CPU using NumPy vectorization and low memory footprint.
    """
    start_idx, end_idx, k, multiplier = args
    global worker_layout_pos
    pos = worker_layout_pos
    n = len(pos)
    forces = np.zeros((end_idx - start_idx, 2), dtype=np.float32)
    
    chunk_pos = pos[start_idx:end_idx]
    
    # Iterate over the chunk
    for i in range(len(chunk_pos)):
        # Current node position
        p = chunk_pos[i]
        
        # Vectorized calculation against ALL other nodes
        # diff: (N, 2)
        diff = p - pos
        
        # dist_sq: (N,)
        dist_sq = np.sum(diff**2, axis=1)
        
        # Filter valid distances (avoid self-interaction and division by zero)
        mask = dist_sq > 1e-9
        
        if np.any(mask):
            dist = np.sqrt(dist_sq[mask])
            
            # Force magnitude: k^2 / dist
            f = (k**2 / dist) * multiplier
            
            # Direction: diff / dist
            # We combine: (diff / dist) * f = diff * (f / dist) = diff * (k^2 / dist^2)
            # This avoids one division and sqrt if we used dist_sq, but we need dist for the formula k^2/dist
            
            # Normalized direction * force
            # (diff[mask] / dist[:, None]) * f[:, None]
            # = diff[mask] * (f / dist)[:, None]
            
            force_vecs = diff[mask] * (f / dist)[:, np.newaxis]
            
            # Sum forces for this node
            forces[i] = np.sum(force_vecs, axis=0)
            
    return forces

def compute_layout(pos, adj, args, progress):
    # Prepare for vectorized calculations
    node_ids = list(pos.keys())
    pos_array = np.array([pos[node] for node in node_ids], dtype=np.float32)
    edges_list = [(i, j) for i in adj for j in adj[i] if i < j]
    edge_indices = np.array([(node_ids.index(i), node_ids.index(j)) for i, j in edges_list])

    # Compute force-directed positions using Fruchterman-Reingold
    logging.info("Computing force-directed positions using CPU (Parallelized)...")

    n = len(pos)
    iterations = 20 if n < 0 else 50 # Simplified logic as SMALL_GRAPH_THRESHOLD was 0
    AREA = 4 * n * n
    k = math.sqrt(AREA / n) if n > 0 else 1.0
    initial_temp = math.sqrt(AREA) * 0.1

    layout_task = progress.add_task("[cyan]Computing Layout...", total=iterations)

    # Determine number of workers
    num_workers = multiprocessing.cpu_count()
    chunk_size = (n + num_workers - 1) // num_workers

    # Create SharedMemory
    shm = SharedMemory(create=True, size=pos_array.nbytes)
    # Create numpy array backed by shared memory
    shm_pos_array = np.ndarray(pos_array.shape, dtype=pos_array.dtype, buffer=shm.buf)
    # Copy initial data
    shm_pos_array[:] = pos_array[:]

    try:
        with multiprocessing.Pool(processes=num_workers, initializer=init_worker_layout, initargs=(shm.name, pos_array.shape, pos_array.dtype)) as pool:
            for iteration in range(iterations):
                # Temperature cools down as iterations progress (Simulated Annealing)
                temp = initial_temp * (1 - iteration / iterations)
                
                # Update shared memory with current positions
                if iteration > 0:
                    shm_pos_array[:] = pos_array[:]
                
                # Prepare arguments for chunks
                chunk_args = []
                for i in range(num_workers):
                    start = i * chunk_size
                    end = min((i + 1) * chunk_size, n)
                    if start < end:
                        chunk_args.append((start, end, k, REPULSIVE_MULTIPLIER))
                
                # Compute repulsive forces in parallel
                results = pool.map(compute_repulsive_forces_chunk, chunk_args)
                
                # Combine results
                forces_array = np.vstack(results)

                # Attractive forces (vectorized)
                # Only connected nodes attract each other (Hooke's law-like)
                if len(edge_indices) > 0:
                    # Calculate differences for connected nodes
                    edge_diffs = pos_array[edge_indices[:, 0]] - pos_array[edge_indices[:, 1]]
                    # Calculate distances, ensuring a minimum distance to avoid instability
                    dist = np.maximum(np.sqrt(np.sum(edge_diffs**2, axis=1)), 0.01)
                    # Force magnitude: distance^2 / k
                    f_attr = (dist**2 / k) * ATTRACTIVE_MULTIPLIER
                    # Normalize direction vectors
                    directions = edge_diffs / dist[:, np.newaxis]
                    forces_attr = directions * f_attr[:, np.newaxis]
                    # Apply attractive forces to both nodes in the edge (action-reaction)
                    np.add.at(forces_array, edge_indices[:, 0], -forces_attr)
                    np.add.at(forces_array, edge_indices[:, 1], forces_attr)

                # Update positions (vectorized)
                # Calculate total displacement magnitude for each node
                disp = np.sqrt(np.sum(forces_array**2, axis=1))
                # Limit displacement by current temperature to prevent overshooting
                scale = np.where(disp > 0, np.minimum(disp, temp) / disp, 0)
                pos_array += forces_array * scale[:, np.newaxis]

                progress.update(layout_task, advance=1)

                # Early stopping
                # Check if the system has cooled down enough (convergence)
                total_disp = np.sum(disp)
                if total_disp < 0.01 * n:
                    progress.console.log("[green]Layout converged early!")
                    progress.update(layout_task, completed=iterations)
                    break
    finally:
        shm.close()
        shm.unlink()

    # Update pos from pos_array
    for idx, node in enumerate(node_ids):
        pos[node] = pos_array[idx]
        
    return pos
