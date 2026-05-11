"""
Utility functions for WSN simulation.
Includes node deployment, neighbor calculation, and logging.
"""

import random
import math
import numpy as np
from sklearn.cluster import KMeans
from node import SensorNode

def deploy_nodes(n: int, field_w: float = 100.0, field_h: float = 100.0,
                 energy_min: float = 0.5, energy_max: float = 2.0) -> list:
    """Deploy N sensor nodes randomly across the field."""
    nodes = []
    for i in range(n):
        x = random.uniform(5, field_w - 5)
        y = random.uniform(5, field_h - 5)
        energy = random.uniform(energy_min, energy_max)
        nodes.append(SensorNode(i, x, y, energy))
    return nodes


def compute_neighbors(nodes: list, comm_range: float = 30.0):
    """Count neighbors within communication range for each node."""
    alive = [n for n in nodes if n.is_alive]
    for node in alive:
        node.neighbors = sum(
            1 for other in alive
            if other.id != node.id and node.distance_to(other) <= comm_range
        )


def cluster_nodes_and_select_chs(nodes: list, base_station: tuple,
                                 w1=0.5, w2=0.3, w3=0.2) -> list:
    """Group alive nodes into K clusters using KMeans, and select one CH per cluster."""
    alive = [n for n in nodes if n.is_alive]
    if not alive:
        return []

    # Reset flags
    for n in nodes:
        n.is_ch = False
        n.cluster_id = -1

    # Optimal K: 10% of alive nodes (common heuristic)
    k = max(1, int(len(alive) * 0.10))

    if len(alive) <= k:
        for n in alive:
            n.is_ch = True
            n.cluster_id = n.id
        return alive

    coords = np.array([[n.x, n.y] for n in alive])
    kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels = kmeans.fit_predict(coords)

    chs = []
    for cluster_idx in range(k):
        cluster_nodes = [alive[i] for i, label in enumerate(labels) if label == cluster_idx]
        if not cluster_nodes:
            continue
            
        # Select best candidate in cluster
        best_ch = max(cluster_nodes, key=lambda n: n.ch_score(base_station, w1, w2, w3))
        best_ch.is_ch = True
        
        for n in cluster_nodes:
            n.cluster_id = best_ch.id
            
        chs.append(best_ch)

    return chs


def get_alive_nodes(nodes: list) -> list:
    return [n for n in nodes if n.is_alive]


def get_dead_nodes(nodes: list) -> list:
    return [n for n in nodes if not n.is_alive]


def format_log(round_num: int, msg: str) -> str:
    return f"[Round {round_num:04d}] {msg}"

