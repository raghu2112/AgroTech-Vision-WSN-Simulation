# Module docstring explaining the simulation engine
"""
WSN Simulation Engine.
Manages rounds, cluster head selection, data transmission, and metrics tracking.
"""

# Import the SensorNode definition
from node import SensorNode
# Import helper functions for setup and calculations
from utils import deploy_nodes, compute_neighbors, cluster_nodes_and_select_chs, get_alive_nodes, format_log


# Define the core simulation engine class
class WSNSimulation:
    # Main simulation controller for the WSN network.

    # Initialize all simulation parameters and network state
    def __init__(self, num_nodes: int = 30, field_size: tuple = (100, 100),
                 base_station: tuple = None, energy_threshold: float = 0.3,
                 comm_range: float = 30.0, w1: float = 0.5, w2: float = 0.3,
                 w3: float = 0.2, rotation_interval: int = 5, auto_recluster: bool = True,
                 multi_hop: bool = True, event_driven: bool = True, enable_3d: bool = False):
        # Store total number of nodes to deploy
        self.num_nodes = num_nodes
        # Unpack field dimensions
        self.field_w, self.field_h = field_size
        # Flag indicating if 3D terrain is used
        self.enable_3d = enable_3d
        # Place base station based on 3D or 2D mode
        if self.enable_3d:
            # Set 3D base station coordinates
            self.base_station = base_station if base_station else (self.field_w / 2, self.field_h * 1.1, 50.0)
        else:
            # Set 2D base station coordinates
            self.base_station = base_station if base_station else (self.field_w / 2, self.field_h * 1.1)
        # Threshold to force reclustering if CH drops below this energy level
        self.energy_threshold = energy_threshold
        # Maximum transmission distance between nodes
        self.comm_range = comm_range
        # Weights for the Cluster Head selection algorithm
        self.w1, self.w2, self.w3 = w1, w2, w3
        # Number of rounds between forced cluster rotations
        self.rotation_interval = rotation_interval
        # Toggle automatic reclustering on/off
        self.auto_recluster = auto_recluster
        # Toggle multi-hop routing between CHs on/off
        self.multi_hop = multi_hop
        # Toggle event-driven data sensing on/off
        self.event_driven = event_driven
        # Placeholder for the current localized anomaly zone
        self.current_event_zone = None

        # State Variables
        # List of all node objects
        self.nodes = []
        # List of nodes currently serving as Cluster Heads
        self.current_chs = []
        # Current simulation round counter
        self.round_num = 0
        # List of system log strings
        self.logs = []
        # Flag indicating if simulation is active
        self.is_running = False

        # Metrics history
        # History of alive node counts per round
        self.alive_history = []
        # History of total remaining network energy
        self.energy_history = []
        # History of CH counts per round
        self.ch_count_history = []
        # History of dead node IDs per round
        self.dead_history = []
        # History of energy variance across nodes
        self.energy_var_history = []
        # History of cumulative packets sent
        self.packets_history = []

    # Reset and prepare the simulation for the first run
    def initialize(self):
        # Generate and place the sensor nodes
        self.nodes = deploy_nodes(self.num_nodes, self.field_w, self.field_h, enable_3d=self.enable_3d)
        # Reset round counter to zero
        self.round_num = 0
        # Clear log history
        self.logs = []
        # Clear tracking arrays
        self.alive_history = []
        self.energy_history = []
        self.ch_count_history = []
        self.dead_history = []
        self.energy_var_history = []
        self.packets_history = []

        # Find reachable neighbors for all nodes
        compute_neighbors(self.nodes, self.comm_range, enable_3d=self.enable_3d, field_w=self.field_w, field_h=self.field_h)
        # Perform initial K-Means clustering
        self.current_chs = cluster_nodes_and_select_chs(
            self.nodes, self.base_station, self.w1, self.w2, self.w3
        )
        # Log the successful setup
        self._log(f"Initial Multi-Cluster setup: {len(self.current_chs)} Clusters formed.")
        # Mark simulation as actively running
        self.is_running = True
        # Record baseline metrics at round 0
        self._record_metrics()

    # Execute a single simulation step
    def run_round(self) -> bool:
        # Abort if simulation is stopped
        if not self.is_running:
            return False

        # Check for remaining alive nodes
        alive = get_alive_nodes(self.nodes)
        # Stop simulation if network is dead
        if len(alive) == 0:
            self._log("All nodes are dead. Simulation ended.")
            self.is_running = False
            return False

        # Increment round counter
        self.round_num += 1

        # --- Event Generation ---
        # If event-driven mode is on, create a random anomaly
        if self.event_driven:
            import random
            # Random X center for event
            ex = random.uniform(0, self.field_w)
            # Random Y center for event
            ey = random.uniform(0, self.field_h)
            # Set event radius
            er = 30.0
            # Store event area
            self.current_event_zone = (ex, ey, er)
            self._log(f"[EVENT] Anomaly detected at ({ex:.1f}, {ey:.1f}) R={er}m")
        # If disabled, clear event zone
        else:
            self.current_event_zone = None

        # --- Dynamic CH Rotation & Re-clustering ---
        # Check if periodic rotation is due
        needs_rotation = self.auto_recluster and (self.round_num % self.rotation_interval == 0)
        # Check if any current CH is failing or dead
        ch_failing = any(ch.energy < self.energy_threshold or not ch.is_alive for ch in self.current_chs)

        # Trigger reclustering if required
        if not self.current_chs or needs_rotation or ch_failing:
            # Recompute neighbor counts
            compute_neighbors(self.nodes, self.comm_range, enable_3d=self.enable_3d, field_w=self.field_w, field_h=self.field_h)
            # Run clustering algorithm
            self.current_chs = cluster_nodes_and_select_chs(
                self.nodes, self.base_station, self.w1, self.w2, self.w3
            )
            
            # Stop if no CH could be elected
            if not self.current_chs:
                self._log("No eligible CHs found. Network dead.")
                self.is_running = False
                return False
            # Log successful reclustering
            self._log(f">> Re-clustered network into {len(self.current_chs)} clusters.")
            # Log new CH identities
            for ch in self.current_chs:
                self._log(f"[ROLE] Node {ch.id} elected as Cluster Head")

        # --- Multi-Hop Routing ---
        # If multi-hop is enabled, map routes between CHs
        if self.multi_hop:
            # Evaluate paths for each CH
            for ch in self.current_chs:
                # Calculate direct distance to BS
                dist_to_bs = ch.distance_to(self.base_station)
                # Track best relay candidate
                best_next_hop = None
                # Initialize shortest path metric
                best_dist = dist_to_bs
                # Compare against all other CHs
                for other_ch in self.current_chs:
                    if other_ch.id != ch.id:
                        # Only forward if the other CH is closer to the base station
                        if other_ch.distance_to(self.base_station) < dist_to_bs:
                            # Calculate distance to relay candidate
                            dist_to_other = ch.distance_to(other_ch)
                            
                            # Assume Line of Sight is true initially
                            has_los = True
                            # Verify LoS if 3D terrain is active
                            if self.enable_3d:
                                from utils import check_line_of_sight
                                has_los = check_line_of_sight((ch.x, ch.y, ch.z), (other_ch.x, other_ch.y, other_ch.z), self.field_w, self.field_h)
                                
                            # Update best route if LOS is clear and it's the shortest path
                            if has_los and dist_to_other < best_dist:
                                best_dist = dist_to_other
                                best_next_hop = other_ch
                # Assign the chosen relay node
                ch.next_hop = best_next_hop
        # If multi-hop disabled, all CHs communicate directly with BS
        else:
            for ch in self.current_chs:
                ch.next_hop = None

        # --- Data transmission phase (Local cluster communication) ---
        # Get list of normal nodes
        members = [n for n in alive if not n.is_ch]
        # Initialize packet counter for each CH
        ch_packets_received = {ch.id: 0 for ch in self.current_chs}
        
        # Iterate over all member nodes
        for node in members:
            # Find the assigned CH for this node
            local_ch = next((ch for ch in self.current_chs if ch.id == node.cluster_id), None)
            if local_ch:
                # Calculate transmission distance to CH
                dist_to_ch = node.distance_to(local_ch)
                # Assume event detected by default
                event_detected = True
                # If event-driven mode is on, verify proximity to anomaly
                if self.event_driven and self.current_event_zone:
                    ex, ey, er = self.current_event_zone
                    # If outside event radius, no data is sent
                    if node.distance_to((ex, ey)) > er:
                        event_detected = False
                        
                # Perform sensing and transmission
                node.sense_and_transmit(dist_to_ch, event_detected)
                
                # If a packet was actually sent, log it at the CH
                if event_detected:
                    ch_packets_received[local_ch.id] += 1

        # Sort CHs starting from farthest to closest to prevent dropping packets
        sorted_chs = sorted(self.current_chs, key=lambda ch: ch.distance_to(self.base_station), reverse=True)
        
        # Process forwarding for all CHs
        for ch in sorted_chs:
            # Count packets received from own members
            packets_to_process = ch_packets_received[ch.id]
            
            # If using multi-hop and a valid relay exists
            if self.multi_hop and ch.next_hop and ch.next_hop.is_alive:
                # Calculate distance to relay CH
                dist_to_next = ch.distance_to(ch.next_hop)
                target_ch_id = ch.next_hop.id
                # Pass accumulated packets to the next CH
                if target_ch_id in ch_packets_received and packets_to_process > 0:
                    ch_packets_received[target_ch_id] += 1
            # Otherwise transmit directly to Base Station
            else:
                dist_to_next = ch.distance_to(self.base_station)
                
            # Perform CH duties (receive, aggregate, transmit)
            ch.act_as_ch(packets_to_process, dist_to_next)

        # --- Status update ---
        # Fetch the previously known dead nodes
        prev_dead = set(self.dead_history[-1]) if self.dead_history else set()
        # Find nodes that died in this specific round
        newly_dead = [n for n in self.nodes if not n.is_alive and n.id not in prev_dead]
        # Log newly dead nodes
        for n in newly_dead:
            self._log(f"[DEAD] Node {n.id} has died")

        # Recalculate alive node count
        alive_count = len(get_alive_nodes(self.nodes))

        # Log summary every 10 rounds
        if self.round_num % 10 == 0:
            self._log(f"Round {self.round_num}: Alive={alive_count}, CHs={len(self.current_chs)}")

        # Save metrics for plotting
        self._record_metrics()
        # Indicate successful completion of the round
        return True

    # Convenience method to run multiple rounds sequentially
    def run_n_rounds(self, n: int) -> int:
        # Counter for successful rounds
        count = 0
        # Loop for requested number of rounds
        for _ in range(n):
            # Attempt to run a round
            if self.run_round():
                # Increment on success
                count += 1
            else:
                # Break early if simulation ends
                break
        # Return total executed rounds
        return count

    # Return a dictionary of summary statistics
    def get_stats(self) -> dict:
        # Fetch currently alive nodes
        alive = get_alive_nodes(self.nodes)
        # Calculate sum of all remaining energy
        total_energy = sum(n.energy for n in alive)
        # Pack stats into a dictionary and return
        return {
            "round": self.round_num,
            "alive_nodes": len(alive),
            "dead_nodes": self.num_nodes - len(alive),
            "total_energy": total_energy,
            "avg_energy": total_energy / len(alive) if alive else 0,
            "num_chs": len(self.current_chs),
            "is_running": self.is_running,
            "total_data_sent": sum(n.data_sent for n in self.nodes),
        }

    # Internal helper to append current state to history arrays
    def _record_metrics(self):
        # Fetch currently alive nodes
        alive = get_alive_nodes(self.nodes)
        # Log count of alive nodes
        self.alive_history.append(len(alive))
        # Log sum of all energy
        self.energy_history.append(sum(n.energy for n in self.nodes))
        # Log count of cluster heads
        self.ch_count_history.append(len(self.current_chs))
        # Log IDs of dead nodes
        dead_ids = [n.id for n in self.nodes if not n.is_alive]
        self.dead_history.append(dead_ids)
        
        # Calculate energy variance to track load balancing
        if alive:
            # Calculate mean energy
            mean_e = sum(n.energy for n in alive) / len(alive)
            # Calculate variance from mean
            var_e = sum((n.energy - mean_e)**2 for n in alive) / len(alive)
        else:
            var_e = 0.0
        # Log variance metric
        self.energy_var_history.append(var_e)
        
        # Log total cumulative data packets sent
        self.packets_history.append(sum(n.data_sent for n in self.nodes))

    # Internal helper to format and store logs
    def _log(self, msg: str):
        # Create formatted string with timestamp
        entry = format_log(self.round_num, msg)
        # Append to log list
        self.logs.append(entry)

