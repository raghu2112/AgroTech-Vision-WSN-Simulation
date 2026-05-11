"""
WSN Simulation Engine.
Manages rounds, cluster head selection, data transmission, and metrics tracking.
"""

from node import SensorNode
from utils import deploy_nodes, compute_neighbors, cluster_nodes_and_select_chs, get_alive_nodes, format_log


class WSNSimulation:
    """Main simulation controller for the WSN network."""

    def __init__(self, num_nodes: int = 30, field_size: tuple = (100, 100),
                 base_station: tuple = (50, 110), energy_threshold: float = 0.3,
                 comm_range: float = 30.0, w1: float = 0.5, w2: float = 0.3,
                 w3: float = 0.2):
        self.num_nodes = num_nodes
        self.field_w, self.field_h = field_size
        self.base_station = base_station
        self.energy_threshold = energy_threshold
        self.comm_range = comm_range
        self.w1, self.w2, self.w3 = w1, w2, w3

        # State
        self.nodes = []
        self.current_chs = []
        self.round_num = 0
        self.logs = []
        self.is_running = False

        # Metrics history
        self.alive_history = []
        self.energy_history = []  # Total network energy per round
        self.ch_count_history = []      # Number of CHs per round
        self.dead_history = []

    def initialize(self):
        """Deploy nodes and select initial CHs."""
        self.nodes = deploy_nodes(self.num_nodes, self.field_w, self.field_h)
        self.round_num = 0
        self.logs = []
        self.alive_history = []
        self.energy_history = []
        self.ch_count_history = []
        self.dead_history = []

        compute_neighbors(self.nodes, self.comm_range)
        self.current_chs = cluster_nodes_and_select_chs(
            self.nodes, self.base_station, self.w1, self.w2, self.w3
        )
        self._log(f"Initial Multi-Cluster setup: {len(self.current_chs)} Clusters formed.")
        self.is_running = True
        self._record_metrics()

    def run_round(self) -> bool:
        """Execute one simulation round. Returns False if network is dead."""
        if not self.is_running:
            return False

        alive = get_alive_nodes(self.nodes)
        if len(alive) == 0:
            self._log("All nodes are dead. Simulation ended.")
            self.is_running = False
            return False

        self.round_num += 1

        # --- Dynamic CH Rotation & Re-clustering ---
        # Re-cluster every 5 rounds OR if any CH is dead/below energy threshold
        needs_rotation = (self.round_num % 5 == 0)
        ch_failing = any(ch.energy < self.energy_threshold or not ch.is_alive for ch in self.current_chs)

        if not self.current_chs or needs_rotation or ch_failing:
            compute_neighbors(self.nodes, self.comm_range)
            self.current_chs = cluster_nodes_and_select_chs(
                self.nodes, self.base_station, self.w1, self.w2, self.w3
            )
            
            if not self.current_chs:
                self._log("No eligible CHs found. Network dead.")
                self.is_running = False
                return False
            self._log(f">> Re-clustered network into {len(self.current_chs)} clusters.")

        # --- Data transmission phase (Local cluster communication) ---
        members = [n for n in alive if not n.is_ch]
        for node in members:
            # Find the actual CH object for this node
            local_ch = next((ch for ch in self.current_chs if ch.id == node.cluster_id), None)
            if local_ch:
                dist_to_ch = node.distance_to(local_ch)
                node.sense_and_transmit(dist_to_ch)

        # CHs aggregate and forward to base station
        for ch in self.current_chs:
            # Count members in this cluster
            member_count = sum(1 for n in members if n.cluster_id == ch.id)
            dist_to_bs = ch.distance_to(self.base_station)
            ch.act_as_ch(member_count, dist_to_bs)

        # --- Status update ---
        prev_dead = set(self.dead_history[-1]) if self.dead_history else set()
        newly_dead = [n for n in self.nodes if not n.is_alive and n.id not in prev_dead]
        for n in newly_dead:
            self._log(f"[DEAD] Node {n.id} has died")

        alive_count = len(get_alive_nodes(self.nodes))

        if self.round_num % 10 == 0:
            self._log(f"Round {self.round_num}: Alive={alive_count}, CHs={len(self.current_chs)}")

        self._record_metrics()
        return True

    def run_n_rounds(self, n: int) -> int:
        """Run up to n rounds. Returns number of rounds actually run."""
        count = 0
        for _ in range(n):
            if self.run_round():
                count += 1
            else:
                break
        return count

    def get_stats(self) -> dict:
        """Get current simulation statistics."""
        alive = get_alive_nodes(self.nodes)
        total_energy = sum(n.energy for n in alive)
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

    def _record_metrics(self):
        alive = get_alive_nodes(self.nodes)
        self.alive_history.append(len(alive))
        self.energy_history.append(sum(n.energy for n in self.nodes))
        self.ch_count_history.append(len(self.current_chs))
        dead_ids = [n.id for n in self.nodes if not n.is_alive]
        self.dead_history.append(dead_ids)

    def _log(self, msg: str):
        entry = format_log(self.round_num, msg)
        self.logs.append(entry)
