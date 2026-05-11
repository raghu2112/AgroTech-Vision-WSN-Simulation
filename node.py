"""
SensorNode class for WSN simulation.
Each node has an ID, position, energy level, and status.
"""

import math


class SensorNode:
    """Represents a wireless sensor node in the network."""

    # Energy costs (in Joules, simplified)
    E_TX = 0.005     # Energy to transmit data
    E_RX = 0.003     # Energy to receive data
    E_SENSE = 0.001  # Energy to sense environment
    E_CH = 0.008     # Extra energy cost for being cluster head

    def __init__(self, node_id: int, x: float, y: float, energy: float):
        self.id = node_id
        self.x = x
        self.y = y
        self.energy = energy
        self.initial_energy = energy
        self.is_alive = True
        self.is_ch = False
        self.cluster_id = -1  # Which CH this node belongs to
        self.neighbors = 0
        self.data_sent = 0
        self.rounds_as_ch = 0

    def distance_to(self, other) -> float:
        """Euclidean distance to another node or (x,y) tuple."""
        if isinstance(other, SensorNode):
            return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
        # Assume (x, y) tuple
        return math.sqrt((self.x - other[0]) ** 2 + (self.y - other[1]) ** 2)

    def consume_energy(self, amount: float):
        """Deduct energy; mark dead if depleted."""
        self.energy -= amount
        if self.energy <= 0:
            self.energy = 0
            self.is_alive = False
            self.is_ch = False

    def sense_and_transmit(self, distance: float):
        """Simulate sensing data and transmitting to CH."""
        if not self.is_alive:
            return
        # Energy model: E_tx = E_elec + E_amp * d^2
        e_cost = self.E_SENSE + self.E_TX * (1 + 0.001 * distance ** 2)
        self.consume_energy(e_cost)
        self.data_sent += 1

    def act_as_ch(self, member_count: int, distance_to_bs: float):
        """Simulate CH duties: receive from members, aggregate, forward to BS."""
        if not self.is_alive:
            return
        e_receive = self.E_RX * member_count
        e_aggregate = self.E_CH
        e_forward = self.E_TX * (1 + 0.001 * distance_to_bs ** 2)
        self.consume_energy(e_receive + e_aggregate + e_forward)
        self.rounds_as_ch += 1
        self.data_sent += 1

    def ch_score(self, base_station: tuple, w1=0.5, w2=0.3, w3=0.2, max_dist=150.0) -> float:
        """
        Compute cluster head selection score.
        Score = w1 * normalized_energy + w2 * (1 - dist/max_dist) + w3 * normalized_neighbors
        Higher score = better CH candidate.
        """
        if not self.is_alive:
            return -1
        norm_energy = self.energy / self.initial_energy
        dist = self.distance_to(base_station)
        norm_proximity = max(0, 1 - dist / max_dist)
        norm_neighbors = min(self.neighbors / 10.0, 1.0)  # Cap at 10
        return w1 * norm_energy + w2 * norm_proximity + w3 * norm_neighbors

    def __repr__(self):
        status = "ALIVE" if self.is_alive else "DEAD"
        role = "CH" if self.is_ch else "Node"
        return f"[{role} {self.id}] E={self.energy:.3f}J ({status}) @ ({self.x:.1f},{self.y:.1f})"
