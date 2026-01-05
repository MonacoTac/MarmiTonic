
import os
import math
import time
import logging
import multiprocessing
from PIL import Image, ImageDraw
from .utils import clip_line, line_intersects_rect
from .config import TILE_SIZE, DPI, SCALE

# Global variable for worker process
worker_render_pos = None

def init_worker(pos_data):
    global worker_render_pos
    worker_render_pos = pos_data

def render_zone_task(args):
    global worker_render_pos
    zone, zone_size, dpi, output_dir, level, num_zones_y = args
    pos = worker_render_pos
    if not zone["nodes"] and not zone["edges"]:
        return None

    i, j = map(int, zone["id"].split('_'))
    zone_pixels_width = zone_size
    zone_pixels_height = zone_size

    # Use PIL to render this zone
    zone_pos = {node_id: pos[node_id] for node_id in zone["nodes"]}
    zone_edges = zone["edges"]

    # Transform positions to zone coordinates
    transformed_pos = {}
    for node_id, position in zone_pos.items():
        # Transform to zone coordinate system (0 to zone_size)
        x_norm = (position[0] - zone["x_min"]) / (zone["x_max"] - zone["x_min"])
        # Flip Y axis for image coordinates (0 is top)
        y_norm = (zone["y_max"] - position[1]) / (zone["y_max"] - zone["y_min"])
        transformed_pos[node_id] = [x_norm * zone_pixels_width, y_norm * zone_pixels_height]

    # Transform edge positions with clipping
    transformed_edges = []
    
    # Calculate pixel size in world units for padding
    px_w = (zone["x_max"] - zone["x_min"]) / zone_pixels_width
    py_h = (zone["y_max"] - zone["y_min"]) / zone_pixels_height
    padding_x = px_w * 0.5 
    padding_y = py_h * 0.5

    for source, target in zone_edges:
        if source in pos and target in pos:
            x1, y1 = pos[source]
            x2, y2 = pos[target]
            
            clipped = clip_line(x1, y1, x2, y2, 
                              zone["x_min"] - padding_x, zone["y_min"] - padding_y, 
                              zone["x_max"] + padding_x, zone["y_max"] + padding_y)
            
            if clipped:
                cx1, cy1, cx2, cy2 = clipped
                
                # Transform clipped coordinates to zone coordinates
                tx1 = (cx1 - zone["x_min"]) / (zone["x_max"] - zone["x_min"]) * zone_pixels_width
                # Flip Y axis for image coordinates
                ty1 = (zone["y_max"] - cy1) / (zone["y_max"] - zone["y_min"]) * zone_pixels_height
                tx2 = (cx2 - zone["x_min"]) / (zone["x_max"] - zone["x_min"]) * zone_pixels_width
                ty2 = (zone["y_max"] - cy2) / (zone["y_max"] - zone["y_min"]) * zone_pixels_height
                
                transformed_edges.append(((tx1, ty1), (tx2, ty2)))

    # Render with PIL
    img = Image.new('RGB', (zone_pixels_width, zone_pixels_height), 'white')
    draw = ImageDraw.Draw(img)

    # Draw edges
    edge_color = (128, 128, 128)
    for (x1, y1), (x2, y2) in transformed_edges:
        draw.line([(x1, y1), (x2, y2)], fill=edge_color, width=1)

    # Draw nodes
    node_color = (173, 216, 230) # Light Blue
    point_radius = 10
    for node_id, (x, y) in transformed_pos.items():
        draw.ellipse([(x - point_radius, y - point_radius), (x + point_radius, y + point_radius)], fill=node_color)

    # Save to file structure for DZI
    row_idx = num_zones_y - 1 - j
    filename = os.path.join(output_dir, str(level), f"{i}_{row_idx}.png")
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    img.save(filename, format='PNG')

    return (i, j, filename, zone_pixels_width, zone_pixels_height)

def generate_tile_task(args):
    level, i, j, output_dir, tile_size = args
    prev_level_dir = os.path.join(output_dir, str(level + 1))
    level_dir = os.path.join(output_dir, str(level))
    
    # Create a new blank tile
    new_tile = Image.new('RGB', (tile_size * 2, tile_size * 2), 'white')
    
    # Load 4 children from previous level
    # (2i, 2j), (2i+1, 2j), (2i, 2j+1), (2i+1, 2j+1)
    children = [
        (2*i, 2*j, 0, 0),
        (2*i+1, 2*j, tile_size, 0),
        (2*i, 2*j+1, 0, tile_size),
        (2*i+1, 2*j+1, tile_size, tile_size)
    ]
    
    has_content = False
    for ci, cj, x, y in children:
        child_path = os.path.join(prev_level_dir, f"{ci}_{cj}.png")
        if os.path.exists(child_path):
            try:
                child_img = Image.open(child_path)
                new_tile.paste(child_img, (x, y))
                has_content = True
            except Exception:
                pass
    
    if has_content:
        # Resize to tile_size
        new_tile = new_tile.resize((tile_size, tile_size), Image.LANCZOS)
        new_tile.save(os.path.join(level_dir, f"{i}_{j}.png"), format='PNG')

def generate_pyramid_levels(output_dir, max_level, tile_size, num_cols, num_rows, progress):
    """
    Generate lower resolution levels for the image pyramid.
    """
    logging.info("Generating image pyramid levels (Parallelized)...")
    
    pyramid_task = progress.add_task("[magenta]Generating Pyramid Levels...", total=max_level)
    
    num_workers = multiprocessing.cpu_count()

    with multiprocessing.Pool(processes=num_workers) as pool:
        for level in range(max_level - 1, -1, -1):
            # Calculate dimensions for this level
            level_cols = math.ceil(num_cols / 2)
            level_rows = math.ceil(num_rows / 2)
            
            level_dir = os.path.join(output_dir, str(level))
            os.makedirs(level_dir, exist_ok=True)
            
            # Prepare tasks
            tasks = []
            for i in range(level_cols):
                for j in range(level_rows):
                    tasks.append((level, i, j, output_dir, tile_size))
            
            # Execute tasks in parallel
            pool.map(generate_tile_task, tasks)
            
            # Update for next iteration
            num_cols = level_cols
            num_rows = level_rows
            progress.update(pyramid_task, advance=1)

def generate_dzi_file(output_path, width, height, tile_size):
    """Generate the .dzi XML file."""
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<Image xmlns="http://schemas.microsoft.com/deepzoom/2008"
       Format="png"
       Overlap="0"
       TileSize="{tile_size}"
       >
    <Size Height="{height}" Width="{width}"/>
</Image>"""
    
    with open(output_path, 'w') as f:
        f.write(content)

def generate_html_viewer(output_path, dzi_filename):
    """Generate a simple HTML viewer using OpenSeadragon."""
    content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Graph Visualization</title>
    <script src="https://openseadragon.github.io/openseadragon/openseadragon.min.js"></script>
    <style>
        body {{ margin: 0; background-color: #000; color: #fff; font-family: sans-serif; }}
        #viewer {{ width: 100vw; height: 100vh; }}
    </style>
</head>
<body>
    <div id="viewer"></div>
    <script type="text/javascript">
        var viewer = OpenSeadragon({{
            id: "viewer",
            prefixUrl: "https://openseadragon.github.io/openseadragon/images/",
            tileSources: "{dzi_filename}",
            showNavigator: true
        }});
    </script>
</body>
</html>"""
    
    with open(output_path, 'w') as f:
        f.write(content)

def render_visualization(pos, edges_list, labels, args, progress):
    n = len(pos)
    
    # Calculate bounding box
    min_x = min(p[0] for p in pos.values())
    max_x = max(p[0] for p in pos.values())
    min_y = min(p[1] for p in pos.values())
    max_y = max(p[1] for p in pos.values())

    width = max_x - min_x
    height = max_y - min_y
    padding = 0.1 * max(width, height) if max(width, height) > 0 else 0.1
    effective_width = width + 2 * padding
    effective_height = height + 2 * padding

    # Zoned rendering for Deep Zoom
    logging.info("Generating Deep Zoom visualization...")
    
    total_pixels_width = int(effective_width * SCALE * DPI)
    total_pixels_height = int(effective_height * SCALE * DPI)
    
    zone_size = TILE_SIZE
    
    num_zones_x = math.ceil(total_pixels_width / zone_size)
    num_zones_y = math.ceil(total_pixels_height / zone_size)
    
    # Calculate max level
    max_dimension = max(total_pixels_width, total_pixels_height)
    max_level = math.ceil(math.log2(max_dimension))
    
    logging.info(f"Image size: {total_pixels_width}x{total_pixels_height}")
    logging.info(f"Tiles: {num_zones_x}x{num_zones_y}, Max Level: {max_level}")

    # Prepare output directory structure
    base_name = os.path.splitext(os.path.basename(args.output_image_path))[0]
    output_dir = os.path.join(os.path.dirname(args.output_image_path), f"{base_name}_files")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create zones dictionary
    zones = {}
    
    # Helper to get zone index from coordinates
    def get_zone_index(x, y):
        # Calculate pixel coordinates
        px = (x - (min_x - padding)) / effective_width * total_pixels_width
        py = (y - (min_y - padding)) / effective_height * total_pixels_height
        
        i = int(px / zone_size)
        j = int(py / zone_size)
        
        # Clamp to valid range
        i = max(0, min(i, num_zones_x - 1))
        j = max(0, min(j, num_zones_y - 1))
        return i, j

    # Helper to get zone bounds
    def get_zone_bounds(i, j):
        unit_x_min = min_x - padding + (i * zone_size / total_pixels_width) * effective_width
        unit_x_max = min_x - padding + ((i + 1) * zone_size / total_pixels_width) * effective_width
        unit_y_min = min_y - padding + (j * zone_size / total_pixels_height) * effective_height
        unit_y_max = min_y - padding + ((j + 1) * zone_size / total_pixels_height) * effective_height
        return unit_x_min, unit_x_max, unit_y_min, unit_y_max

    # Populate zones with nodes
    logging.info("Assigning nodes to zones...")
    for node_id, position in pos.items():
        i, j = get_zone_index(position[0], position[1])
        key = (i, j)
        if key not in zones:
            ux_min, ux_max, uy_min, uy_max = get_zone_bounds(i, j)
            zones[key] = {
                "id": f"{i}_{j}",
                "x_min": ux_min, "x_max": ux_max,
                "y_min": uy_min, "y_max": uy_max,
                "nodes": [], "edges": []
            }
        zones[key]["nodes"].append(node_id)

    # Populate zones with edges
    logging.info("Assigning edges to zones...")
    for source, target in edges_list:
        x1, y1 = pos[source]
        x2, y2 = pos[target]
        
        i1, j1 = get_zone_index(x1, y1)
        i2, j2 = get_zone_index(x2, y2)
        
        # Determine range of zones this edge might cover
        min_i, max_i = min(i1, i2), max(i1, i2)
        min_j, max_j = min(j1, j2), max(j1, j2)
        
        for i in range(min_i, max_i + 1):
            for j in range(min_j, max_j + 1):
                key = (i, j)
                if key not in zones:
                    ux_min, ux_max, uy_min, uy_max = get_zone_bounds(i, j)
                    zones[key] = {
                        "id": f"{i}_{j}",
                        "x_min": ux_min, "x_max": ux_max,
                        "y_min": uy_min, "y_max": uy_max,
                        "nodes": [], "edges": []
                    }
                
                zone = zones[key]
                if ((zone["x_min"] <= x1 <= zone["x_max"] and zone["y_min"] <= y1 <= zone["y_max"] and
                        zone["x_min"] <= x2 <= zone["x_max"] and zone["y_min"] <= y2 <= zone["y_max"]) or
                    line_intersects_rect(x1, y1, x2, y2, zone["x_min"], zone["y_min"], zone["x_max"], zone["y_max"])):
                    zone["edges"].append((source, target))

    # Convert zones dict to list for processing
    zones_list = list(zones.values())
    logging.log(25, f"Active zones: {len(zones_list)}")

    # Render base layer zones
    total_zones = len(zones_list)
    render_task = progress.add_task("[yellow]Rendering Base Layer...", total=total_zones)

    t_render_start = time.time()
    
    # Ensure max_level directory exists
    os.makedirs(os.path.join(output_dir, str(max_level)), exist_ok=True)

    num_workers = multiprocessing.cpu_count()
    with multiprocessing.Pool(processes=num_workers, initializer=init_worker, initargs=(pos,)) as pool:
        for i, result in enumerate(pool.imap(render_zone_task, [(zone, zone_size, DPI, output_dir, max_level, num_zones_y) for zone in zones_list])):
            progress.update(render_task, advance=1)
    
    t_render_end = time.time()
    base_layer_time = t_render_end - t_render_start
    logging.log(25, f"Base layer rendering time: {base_layer_time:.2f}s")
    
    # Generate pyramid levels
    t_pyramid_start = time.time()
    generate_pyramid_levels(output_dir, max_level, TILE_SIZE, num_zones_x, num_zones_y, progress)
    t_pyramid_end = time.time()
    
    # Generate DZI file
    dzi_path = os.path.join(os.path.dirname(args.output_image_path), f"{base_name}.dzi")
    generate_dzi_file(dzi_path, total_pixels_width, total_pixels_height, TILE_SIZE)
    
    # Generate HTML viewer
    html_path = os.path.join(os.path.dirname(args.output_image_path), f"{base_name}.html")
    generate_html_viewer(html_path, f"{base_name}.dzi")

    logging.info("Visualization completed successfully.")
    
    return {
        "num_zones": total_zones,
        "base_layer_time": base_layer_time,
        "pyramid_time": t_pyramid_end - t_pyramid_start,
        "image_size": (total_pixels_width, total_pixels_height),
        "max_level": max_level
    }
