# 🌍 AgroTech Vision: WSN Simulation Platform

**True Multi-Cluster Edge Computing • Energy-Efficient Routing • Production-Grade IoT Simulation**

---

## 📖 Overview

AgroTech Vision is a high-fidelity, production-grade simulation environment designed to model, visualize, and analyze energy-efficient **Wireless Sensor Networks (WSNs)** in smart agriculture.

Originally a simple prototype, this system has been architecturally upgraded into a **True Multi-Cluster Architecture**. It uses machine learning (K-Means) for spatial partitioning, dynamic, algorithmic rotation of Cluster Heads (CHs) to maximize network lifetime, and advanced **Multi-Hop Routing** and **Event-Driven Sensing** capabilities. The entire engine is wrapped in a state-of-the-art, modular, multi-page web application featuring our bespoke **Scientific Light** design system with rich 3D visualization.

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

### 3. Advanced Networking: Multi-Hop Routing & Event-Driven Sensing
*   **Multi-Hop Routing**: Cluster Heads can dynamically route data through other intermediate CHs if it provides a shorter or clearer path to the Base Station, conserving long-distance transmission energy.
*   **Event-Driven Sensing**: Sensors can be configured to only sample and transmit data when a spatial event (anomaly) occurs within their detection radius, eliminating redundant periodic transmissions and significantly extending network lifetime.

### 4. 3D Topography & Line-of-Sight (LoS)
The simulation optionally features mathematically generated 3D terrain. When 3D mode is active:
*   Nodes are placed on rolling hills and valleys based on procedural elevation algorithms.
*   **Line-of-Sight Checks**: The routing engine verifies physical LoS between nodes. If a hill blocks the signal path, the node must route around the obstacle.

### 5. Dynamic CH Rotation Protocol
To prevent premature death of aggregation nodes, the network implements rigid rotation constraints:
*   **Periodic Rotation**: The entire network re-clusters and elects new CHs every 5 simulation rounds.
*   **Threshold Fail-over**: If *any* active CH drops below the defined Minimum Energy Threshold (or dies unexpectedly), an immediate emergency re-clustering is triggered globally to ensure zero data loss.

### 6. Realistic Energy Decay Model
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
*   **Math & Random**: Handles euclidean distance calculations, stochastic node deployment, and 3D elevation mathematics.

### Frontend & UI/UX (Scientific Light Theme)
*   **Streamlit**: The backbone of the web framework. Structured as a modular Single Page Application (SPA) utilizing `st.session_state` routing.
*   **Custom CSS (Glassmorphism & Scientific Design)**: A custom `ui/style.css` stylesheet completely overrides Streamlit's default components, enforcing Google Fonts (`Space Grotesk` & `Inter`), and rendering clean, enterprise-grade white cards with subtle green (`#2E7D32`) and blue (`#2563EB`) accents. CSS is cached (`@st.cache_data`) for high performance.
*   **Plotly Graph Objects (`plotly.graph_objects`)**: Powers the interactive "Live Topology Map" (capable of toggling between 2D scatter plots and highly detailed 3D terrain meshes), Node Inspector highlights, and detailed Analytics charts.

---

## 📁 Detailed Project Structure

```text
mini project/
├── app.py                 # Clean SPA Router mapping to specific UI views.
├── simulation.py          # The Simulation Engine (Event loop, Routing, 3D LoS checks).
├── utils.py               # The Algorithmic Core (KMeans, deployment, elevation logic).
├── node.py                # The Entity Class (SensorNode state, energy physics).
├── main.py                # CLI entry point for headless debugging/testing.
├── requirements.txt       # Python package dependencies.
├── README.md              # Project documentation.
└── ui/                    # Dedicated Frontend Module
    ├── style.css          # Scientific Light CSS design tokens and variables.
    ├── components.py      # Reusable UI elements (Navbar, Metric Cards, Plotly Theming).
    └── views/             # Individual Screen Logic
        ├── landing.py     # Home / Introduction View.
        ├── setup.py       # 4-column configuration form for simulation parameters.
        ├── loading.py     # Network instantiation and provisioning sequence.
        ├── dashboard.py   # Main NOC (2D/3D Topology Toggle, Controls, Analytics).
        └── inspector.py   # Deep-dive Node Telemetry View.
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

1.  **Landing Portal**: Welcome screen. Click *Initialize Simulation*.
2.  **Simulation Parameters**: You will be presented with a clean, industrial 4-column configuration screen. Use the inputs to define Topology constraints, Clustering rules, Advanced Network toggles (Multi-Hop, Event-Driven, 3D Topography), and Algorithm Weights ($w1, w2, w3$).
3.  **Loading Screen**: Watch the system securely deploy nodes, compute graphs, and elect clusters in the background.
4.  **Network Operations Center (NOC)**: 
    *   **Live Topology Map**: Toggle between 2D mode and rich 3D topographic view. Watch clusters form dynamically. Normal nodes are linked to their local CH (Diamond marker), which routes data (possibly multi-hop via orange arcs) to the Base Station.
    *   **Simulation Controls**: Use `Step Forward (1)` or `Auto-Run` to observe data transmission, energy consumption, and dynamic re-clustering.
5.  **Node Inspector**: Dedicated view to select any specific node ID to pull up its exact live telemetry, activity logs, and a focused topology highlight.

---

## 📚 Academic & Portfolio Context

This implementation fully satisfies modern WSN academic requirements and serves as a stellar software engineering portfolio piece:
*   **Scalable Architecture**: Dynamic K-Means clustering prevents bottlenecks.
*   **Advanced Routing & Physics**: Multi-hop routing combined with 3D Line-of-Sight algorithms.
*   **MVC Modularity**: Frontend completely decoupled from backend physics.
*   **Production Quality UI**: Custom CSS bridges the gap between rapid prototyping (Streamlit) and premium SaaS aesthetics.

