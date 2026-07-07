"""
CLI entry point for WSN simulation (non-GUI mode).
Useful for quick testing without Streamlit.
"""

from simulation import WSNSimulation


def main():
    print("=" * 60)
    print("  WSN Smart Agriculture - Dynamic CH Selection Simulator")
    print("=" * 60)

    sim = WSNSimulation(num_nodes=30, energy_threshold=0.3)
    sim.initialize()

    print(f"\nDeployed {sim.num_nodes} nodes. Base station at {sim.base_station}")
    print("Initial CHs:")
    for ch in sim.current_chs:
        print(f"  Node {ch.id} (Energy: {ch.energy:.3f}J)")
    print("\n")

    max_rounds = 500
    rounds_run = sim.run_n_rounds(max_rounds)

    stats = sim.get_stats()
    print(f"\n{'=' * 60}")
    print(f"Simulation ended after {stats['round']} rounds")
    print(f"Alive: {stats['alive_nodes']} | Dead: {stats['dead_nodes']}")
    print(f"Total data packets sent: {stats['total_data_sent']}")
    print(f"\nLast 10 log entries:")
    for log in sim.logs[-10:]:
        print(f"  {log}")


if __name__ == "__main__":
    main()
