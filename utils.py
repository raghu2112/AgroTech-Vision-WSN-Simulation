# Module docstring explaining the utility functions
"""
Utility functions for WSN simulation.
Includes node deployment, neighbor calculation, and logging.
"""

# Import random module for random node placement
import random
# Import math module for trigonometric and distance calculations
import math
# Import numpy for array manipulation and KMeans input
import numpy as np
# Import KMeans clustering algorithm from scikit-learn
from sklearn.cluster import KMeans
# Import the SensorNode class for type hinting and object creation
from node import SensorNode

# Function to calculate procedural 3D elevation based on X/Y coordinates
def get_elevation(x: float, y: float, field_w: float = 100.0, field_h: float = 100.0) -> float:
    # Scale X coordinate to create rolling hills
    nx = (x / field_w) * 4.0
    # Scale Y coordinate to create rolling hills
    ny = (y / field_h) * 4.0
    
    # Calculate base fractal noise using multiple sine/cosine octaves
    e = (
        1.00 * (math.sin(nx) * math.cos(ny)) +
        0.50 * (math.sin(nx * 2.1 + 1) * math.cos(ny * 2.1 + 2)) +
        0.25 * (math.sin(nx * 4.3 + 2) * math.cos(ny * 4.3 + 3)) +
        0.13 * (math.sin(nx * 8.5 + 3) * math.cos(ny * 8.5 + 4))
    )
    
    # Normalize the noise output to a roughly 0-1 range
    e = (e + 1.88) / 3.76
    # Clamp the values strictly between 0 and 1
    e = max(0.0, min(1.0, e))
    
    # Apply a power function to flatten valleys and sharpen peaks
    e = math.pow(e, 1.8)
    
    # Multiply by the maximum terrain height of 18 meters
    return e * 18.0

# Function to check if the direct path between two 3D points is blocked by terrain
def check_line_of_sight(p1: tuple, p2: tuple, field_w: float = 100.0, field_h: float = 100.0) -> bool:
    # If 3D coordinates aren't fully provided, assume clear line of sight
    if len(p1) < 3 or len(p2) < 3:
        return True
        
    # Unpack source point coordinates
    x1, y1, z1 = p1
    # Unpack destination point coordinates
    x2, y2, z2 = p2
    
    # Calculate the flat 2D distance between points
    dist_xy = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    # If distance is zero, they are at the same spot (clear LOS)
    if dist_xy == 0:
        return True
        
    # Determine number of sample points along the ray (at least 5)
    num_samples = max(5, int(dist_xy / 2))
    # Iterate over interpolation steps along the ray path
    for i in range(1, num_samples):
        # Calculate the interpolation fraction 't'
        t = i / num_samples
        # Interpolate X coordinate along ray
        sx = x1 + t * (x2 - x1)
        # Interpolate Y coordinate along ray
        sy = y1 + t * (y2 - y1)
        # Interpolate Z coordinate (ray height) along ray
        sz = z1 + t * (z2 - z1)
        
        # Get the actual ground elevation at this specific X/Y point
        terrain_z = get_elevation(sx, sy, field_w, field_h)
        # Check if the ground elevation is higher than the ray height
        if terrain_z > sz:
            # Ray is blocked by a hill
            return False
    # No obstructions found, clear line of sight
    return True

# Function to generate and place sensor nodes randomly across the field
def deploy_nodes(n: int, field_w: float = 100.0, field_h: float = 100.0,
                 energy_min: float = 0.5, energy_max: float = 2.0,
                 enable_3d: bool = False) -> list:
    # Initialize empty list to hold deployed node objects
    nodes = []
    # Loop 'n' times to create exactly 'n' nodes
    for i in range(n):
        # Generate random X coordinate, keeping away from exact edges
        x = random.uniform(5, field_w - 5)
        # Generate random Y coordinate, keeping away from exact edges
        y = random.uniform(5, field_h - 5)
        # Calculate Z elevation if 3D is enabled, otherwise use flat 0.0
        z = get_elevation(x, y, field_w, field_h) if enable_3d else 0.0
        # Generate random starting energy within allowed bounds
        energy = random.uniform(energy_min, energy_max)
        # Create the node and append it to the list
        nodes.append(SensorNode(i, x, y, z, energy))
    # Return the fully populated list of nodes
    return nodes

# Function to count reachable neighbors for every active node
def compute_neighbors(nodes: list, comm_range: float = 30.0, enable_3d: bool = False, field_w: float = 100.0, field_h: float = 100.0):
    # Filter list to only include alive nodes
    alive = [n for n in nodes if n.is_alive]
    # Iterate through every alive node
    for node in alive:
        # Reset neighbor count for this specific node
        count = 0
        # Iterate through every other alive node to check distance
        for other in alive:
            # Check if it's a different node and within communication range
            if other.id != node.id and node.distance_to(other) <= comm_range:
                # If 3D mode is on, verify Line of Sight
                if enable_3d:
                    # Increment count only if LOS is clear
                    if check_line_of_sight((node.x, node.y, node.z), (other.x, other.y, other.z), field_w, field_h):
                        count += 1
                # If 2D mode, automatically increment since range is satisfied
                else:
                    count += 1
        # Store final computed neighbor count in the node object
        node.neighbors = count

# Function to run K-Means clustering and nominate Cluster Heads (CHs)
def cluster_nodes_and_select_chs(nodes: list, base_station: tuple,
                                 w1=0.5, w2=0.3, w3=0.2) -> list:
    # Filter out dead nodes
    alive = [n for n in nodes if n.is_alive]
    # Return empty list if network is completely dead
    if not alive:
        return []

    # Reset clustering flags on all nodes
    for n in nodes:
        # Revoke previous CH status
        n.is_ch = False
        # Unbind from previous cluster
        n.cluster_id = -1

    # Calculate optimal 'K' value (10% of alive nodes)
    k = max(1, int(len(alive) * 0.10))

    # Fallback: if there are fewer nodes than K, make everyone a CH
    if len(alive) <= k:
        # Loop through all remaining nodes
        for n in alive:
            # Elevate to CH status
            n.is_ch = True
            # Assign self as cluster ID
            n.cluster_id = n.id
        # Return all alive nodes as CHs
        return alive

    # Extract 2D coordinates for scikit-learn clustering
    coords = np.array([[n.x, n.y] for n in alive])
    # Initialize KMeans algorithm with specified K
    kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
    # Fit the model and get cluster labels for each node
    labels = kmeans.fit_predict(coords)

    # Initialize empty list to track selected Cluster Heads
    chs = []
    # Loop over each distinct cluster group
    for cluster_idx in range(k):
        # Extract all nodes belonging to the current cluster group
        cluster_nodes = [alive[i] for i, label in enumerate(labels) if label == cluster_idx]
        # Skip empty clusters (edge case)
        if not cluster_nodes:
            continue
            
        # Elect the best CH candidate using the weighted scoring function
        best_ch = max(cluster_nodes, key=lambda n: n.ch_score(base_station, w1, w2, w3))
        # Mark the winner as an active Cluster Head
        best_ch.is_ch = True
        
        # Assign the winner's ID to all members of this cluster
        for n in cluster_nodes:
            # Bind member to the elected CH
            n.cluster_id = best_ch.id
            
        # Append the new CH to the tracking list
        chs.append(best_ch)

    # Return the complete list of active Cluster Heads
    return chs

# Helper function to extract only the living nodes from a list
def get_alive_nodes(nodes: list) -> list:
    # Filter and return list of alive nodes
    return [n for n in nodes if n.is_alive]

# Helper function to extract only the dead nodes from a list
def get_dead_nodes(nodes: list) -> list:
    # Filter and return list of dead nodes
    return [n for n in nodes if not n.is_alive]

# Helper function to format system logs cleanly
def format_log(round_num: int, msg: str) -> str:
    # Prepend round number to log string
    return f"[Round {round_num:04d}] {msg}"


