# 🌍 AgroTech Vision: WSN Simulation Platform

**True Multi-Cluster Edge Computing • Energy-Efficient Routing • Production-Grade IoT Simulation**

---

## 📖 Overview

AgroTech Vision is a high-fidelity, production-grade simulation environment designed to model, visualize, and analyze energy-efficient **Wireless Sensor Networks (WSNs)** in smart agriculture.

Originally a simple prototype, this system has been architecturally upgraded into a **True Multi-Cluster Architecture**. It uses machine learning (K-Means) for spatial partitioning and dynamic, algorithmic rotation of Cluster Heads (CHs) to maximize network lifetime. The entire engine is wrapped in a state-of-the-art, multi-page web application featuring custom Glassmorphism CSS, interactive telemetry, and real-time Plotly rendering.

---

## 🧠 Core Architecture & Algorithms

### 1. K-Means Topology Partitioning
Unlike legacy protocols that use a single global aggregation node, this network dynamically segments itself into localized clusters.
*   **Optimal K Determination**: The system dynamically calculates the optimal number of clusters ($K$) as $10\%$ of the currently alive nodes. This ensures that as nodes inevitably die, the network re-scales gracefully without stranding isolated nodes.
*   **Spatial Grouping**: `scikit-learn`'s KMeans algorithm partitions the coordinates of all active nodes, minimizing intra-cluster transmission distances.

### 2. Localized Cluster Head (CH) Election
Within every generated cluster, a single CH is elected based on a customizable, weighted scoring algorithm:
```text
Score = (w1 × Normalized_Residual_Energy) 
      + (w2 × Normalized_Proximity_to_Base_Station) 
      + (w3 × Normalized_Neighbor_Density)
```
Nodes transmit their sensor data exclusively to their *local* CH, drastically reducing transmission (TX) energy costs compared to direct-to-Base-Station routing.

### 3. Dynamic CH Rotation Protocol
To prevent premature death of aggregation nodes, the network implements rigid rotation constraints:
*   **Periodic Rotation**: The entire network re-clusters and elects new CHs every 5 simulation rounds.
*   **Threshold Fail-over**: If *any* active CH drops below the defined Minimum Energy Threshold (or dies unexpectedly), an immediate emergency re-clustering is triggered globally to ensure zero data loss.

### 4. Realistic Energy Decay Model
Nodes consume energy strictly based on their physical operations and distances:
*   $E_{SENSE}$: Base cost to sample environmental data.
*   $E_{TX}$: Cost to transmit data (scales with the square of the transmission distance).
*   $E_{RX}$: Cost for a CH to receive data from its members.
*   $E_{CH}$: Fixed processing overhead for data aggregation.

---

## 🛠️ Technology Stack

This project was built entirely in Python, pushing standard libraries and frameworks to their absolute visual and functional limits.

### Backend & Simulation Engine
*   **Python 3.x**: Core runtime.
*   **Scikit-Learn (`sklearn`)**: Drives the geometric KMeans clustering for network partitioning.
*   **Pandas**: Aggregates time-series simulation data (Alive Nodes, Active CHs, Residual Energy) into dataframes for historical tracking.
*   **Math & Random**: Handles euclidean distance calculations and stochastic node deployment.

### Frontend & UI/UX
*   **Streamlit**: The backbone of the web framework. Heavily modified using Session State (`st.session_state`) to bypass the default sidebar layout and create a true Multi-Page Application (SPA) flow (Landing → Setup → Loading → Dashboard).
*   **Custom CSS (Glassmorphism)**: Raw CSS was injected to remove Streamlit "chrome" (headers/footers), enforce Google Fonts (`Space Grotesk` & `Inter`), and render floating frosted-glass cards with interactive hover-lift states and CSS-animated alert pulses.
*   **Plotly Graph Objects (`plotly.graph_objects`)**: Powers the interactive "Live Topology Map" and "Network Trends" charts. Features distinct `Viridis` color mapping for separate clusters, physical line-drawing for packet routing, and locked-axis constraints to prevent accidental viewport distortion.

---

## 📁 Detailed Project Structure

```text
mini project/
├── app.py           # The Dashboard Controller. Manages routing, CSS injection, Plotly rendering, and the simulation UI state.
├── simulation.py    # The Simulation Engine. Manages the event loop, triggers re-clustering, routes data payloads, and logs historical metrics.
├── utils.py         # The Algorithmic Core. Houses the `cluster_nodes_and_select_chs` KMeans logic and node deployment functions.
├── node.py          # The Entity Class. Defines `SensorNode` state, energy consumption physics, and CH scoring math.
├── requirements.txt # Python package dependencies.
└── README.md        # This documentation file.
```

---

## 🚀 Setup & Installation

### 1. Create a Virtual Environment (Recommended)
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Platform
```bash
streamlit run app.py
```
The application will automatically open in your default browser at `http://localhost:8501`.

---

## 🎮 Platform Walkthrough

1.  **Landing Portal**: Welcome screen. Click *Initialize Environment Setup*.
2.  **Simulation Parameters**: You will be presented with an industrial configuration screen. Use the number inputs to precisely define:
    *   *Total Nodes* & *Comm Range* (Topology constraints).
    *   *CH Energy Threshold* (Rotation aggressiveness).
    *   *Selection Algorithm Weights* ($w1, w2, w3$).
3.  **Network Operations Center (NOC)**: 
    *   **Live Topology Map**: Watch clusters form dynamically. Standard nodes (colored by cluster) are linked to their local CH (Diamond marker), which links to the Base Station.
    *   **Simulation Controls**: Use `Step Forward (1)` to carefully observe data transmission, or `Fast Forward (10)` to watch the network rapidly deplete and dynamically re-cluster.
    *   **Node Introspection**: Select any specific node ID from the dropdown at the bottom of the dashboard to pull up its exact telemetry (Identity, Role, Residual Energy, and Topology Data).

---

## 📚 Academic Context

This implementation fully satisfies modern WSN academic requirements:
*   **Scalable Architecture**: Dynamic K-Means clustering prevents bottlenecks.
*   **Balanced Energy Distribution**: Algorithmic CH rotation prevents aggregation nodes from dying prematurely.
*   **Realistic Constraints**: Dead nodes are completely purged from topology calculations, and transmissions physically scale with squared distance.
