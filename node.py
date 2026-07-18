"""
SensorNode class for WSN simulation.
Each node has an ID, position, energy level, and status.
"""

# Import the math module for distance and exponential calculations
import math

# Define the main SensorNode class for the wireless network simulation
class SensorNode:
    # Represents a wireless sensor node in the network.

    # Energy costs (in Joules, simplified)
    # Energy required to transmit a packet of data
    E_TX = 0.005
    # Energy required to receive a packet of data
    E_RX = 0.003
    # Energy required to sense the surrounding environment
    E_SENSE = 0.001
    # Additional baseline energy cost for operating as a cluster head
    E_CH = 0.008

    # Initialize a new sensor node with its position and energy
    def __init__(self, node_id: int, x: float, y: float, z: float, energy: float):
        # Assign a unique identifier to the node
        self.id = node_id
        # Set the X coordinate on the grid
        self.x = x
        # Set the Y coordinate on the grid
        self.y = y
        # Set the Z coordinate for elevation
        self.z = z
        # Set the current residual energy level
        self.energy = energy
        # Store the starting energy level for percentage calculations
        self.initial_energy = energy
        # Flag indicating if the node is still functioning
        self.is_alive = True
        # Flag indicating if the node is currently a Cluster Head
        self.is_ch = False
        # The ID of the cluster this node belongs to
        self.cluster_id = -1
        # The next hop node object for routing data to the base station
        self.next_hop = None
        # Count of other alive nodes within communication range
        self.neighbors = 0
        # Total number of packets successfully sent by this node
        self.data_sent = 0
        # Total number of simulation rounds this node served as a CH
        self.rounds_as_ch = 0

    # Calculate the 3D Euclidean distance to another point
    def distance_to(self, other) -> float:
        # Check if the target is another SensorNode instance
        if isinstance(other, SensorNode):
            # Calculate difference in X coordinates
            dx = self.x - other.x
            # Calculate difference in Y coordinates
            dy = self.y - other.y
            # Calculate difference in Z coordinates, defaulting to 0 if missing
            dz = self.z - getattr(other, 'z', 0.0)
            # Return the Pythagorean distance
            return math.sqrt(dx*dx + dy*dy + dz*dz)
        # Otherwise assume the target is an (X, Y, Z) tuple
        dx = self.x - other[0]
        dy = self.y - other[1]
        # Extract Z from tuple if available, else use 0
        dz = self.z - (other[2] if len(other) > 2 else 0.0)
        # Return the Pythagorean distance
        return math.sqrt(dx*dx + dy*dy + dz*dz)

    # Deduct a specific amount of energy from the node's battery
    def consume_energy(self, amount: float):
        # Subtract the specified amount
        self.energy -= amount
        # Check if the battery is completely empty
        if self.energy <= 0:
            # Floor the energy at 0
            self.energy = 0
            # Mark the node as dead
            self.is_alive = False
            # Revoke cluster head status if dead
            self.is_ch = False

    # Simulate sensing the environment and transmitting data to a cluster head
    def sense_and_transmit(self, distance: float, event_detected: bool = True):
        # Abort if the node is already dead
        if not self.is_alive:
            return
        # Baseline cost for powering the sensing equipment
        e_cost = self.E_SENSE
        # If an event occurred, add transmission costs
        if event_detected:
            # Calculate transmission energy scaling quadratically with distance
            e_cost += self.E_TX * (1 + 0.001 * distance ** 2)
            # Increment the packet sent counter
            self.data_sent += 1
        # Deduct the total consumed energy from the battery
        self.consume_energy(e_cost)

    # Perform the duties of a Cluster Head for one round
    def act_as_ch(self, packets_received: int, distance_to_next_hop: float):
        # Abort if the node is dead or no data was received
        if not self.is_alive or packets_received == 0:
            return
        # Calculate energy spent receiving incoming packets from members
        e_receive = self.E_RX * packets_received
        # Calculate baseline processing cost for aggregating data
        e_aggregate = self.E_CH
        # Calculate energy spent forwarding the aggregated data to the next hop
        e_forward = self.E_TX * (1 + 0.001 * distance_to_next_hop ** 2)
        # Deduct the total CH operation energy from the battery
        self.consume_energy(e_receive + e_aggregate + e_forward)
        # Increment the counter for rounds served as a CH
        self.rounds_as_ch += 1
        # Increment the total packets sent counter
        self.data_sent += 1

    # Calculate this node's fitness to become a Cluster Head
    def ch_score(self, base_station: tuple, w1=0.5, w2=0.3, w3=0.2, max_dist=150.0) -> float:
        # Dead nodes cannot be cluster heads
        if not self.is_alive:
            return -1
        # Calculate normalized residual energy ratio
        norm_energy = self.energy / self.initial_energy
        # Calculate absolute distance to the base station
        dist = self.distance_to(base_station)
        # Calculate normalized proximity metric (closer is better)
        norm_proximity = max(0, 1 - dist / max_dist)
        # Calculate normalized density metric (more neighbors is better)
        norm_neighbors = min(self.neighbors / 10.0, 1.0)
        # Return the weighted sum of all three metrics
        return w1 * norm_energy + w2 * norm_proximity + w3 * norm_neighbors

    # Provide a readable string representation of the node state
    def __repr__(self):
        # Determine human-readable status string
        status = "ALIVE" if self.is_alive else "DEAD"
        # Determine human-readable role string
        role = "CH" if self.is_ch else "Node"
        # Return formatted summary string
        return f"[{role} {self.id}] E={self.energy:.3f}J ({status}) @ ({self.x:.1f},{self.y:.1f})"

