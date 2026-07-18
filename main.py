# Module docstring explaining the purpose of main.py
"""
CLI entry point for WSN simulation (non-GUI mode).
Useful for quick testing without Streamlit.
"""

# Import the core simulation engine class
from simulation import WSNSimulation


# Define the main execution function
def main():
    # Print header border
    print("=" * 60)
    # Print application title
    print("  WSN Smart Agriculture - Dynamic CH Selection Simulator")
    # Print header border
    print("=" * 60)

    # Initialize a new simulation instance with 30 nodes and a 0.3J energy threshold
    sim = WSNSimulation(num_nodes=30, energy_threshold=0.3)
    # Trigger the initial node deployment and clustering setup
    sim.initialize()

    # Print confirmation of node deployment and base station location
    print(f"\nDeployed {sim.num_nodes} nodes. Base station at {sim.base_station}")
    # Print header for initial Cluster Heads list
    print("Initial CHs:")
    # Loop over all elected Cluster Heads
    for ch in sim.current_chs:
        # Print the ID and current energy level of each CH
        print(f"  Node {ch.id} (Energy: {ch.energy:.3f}J)")
    # Print extra newlines for formatting
    print("\n")

    # Set the absolute maximum number of rounds to simulate
    max_rounds = 500
    # Execute the simulation for up to max_rounds or until the network dies
    rounds_run = sim.run_n_rounds(max_rounds)

    # Fetch final summary statistics from the simulation engine
    stats = sim.get_stats()
    # Print footer border
    print(f"\n{'=' * 60}")
    # Print total number of rounds successfully executed
    print(f"Simulation ended after {stats['round']} rounds")
    # Print final survival counts
    print(f"Alive: {stats['alive_nodes']} | Dead: {stats['dead_nodes']}")
    # Print final total data throughput
    print(f"Total data packets sent: {stats['total_data_sent']}")
    # Print header for final logs
    print(f"\nLast 10 log entries:")
    # Loop over the final 10 log entries
    for log in sim.logs[-10:]:
        # Print each log entry
        print(f"  {log}")


# Ensure the main function only runs if the script is executed directly
if __name__ == "__main__":
    # Call main execution block
    main()
