"""
Safe malware-behavior simulator (educational only).
- Purely simulated: no filesystem/network/OS access.
- Models a network as a graph; nodes transition between states:
  Susceptible -> Infected -> (Detected -> Quarantined) OR (Patched)
- Allows tuning attacker/defender parameters and visualizes results.
"""

import streamlit as st
import networkx as nx
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import random
import time

# -------------------------
# States & dataclasses
# -------------------------
SUSCEPTIBLE = "Susceptible"
INFECTED = "Infected"
PATCHED = "Patched"
QUARANTINED = "Quarantined"
DETECTED = "Detected"  # transient logged detection

STATE_COLORS = {
    SUSCEPTIBLE: "lightgrey",
    INFECTED: "red",
    PATCHED: "green",
    QUARANTINED: "orange",
    DETECTED: "purple",
}

@dataclass
class NodeAttrs:
    state: str = SUSCEPTIBLE
    infection_time: int = -1
    detected_time: int = -1
    quarantined_time: int = -1

@dataclass
class Simulation:
    G: nx.Graph
    node_attrs: Dict[int, NodeAttrs] = field(default_factory=dict)
    time_step: int = 0
    history: List[Dict[str,int]] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)

    def reset_attrs(self):
        self.node_attrs = {n: NodeAttrs() for n in self.G.nodes()}
        self.time_step = 0
        self.history = []
        self.logs = []

    def seed_infections(self, seeds: List[int]):
        for s in seeds:
            self.node_attrs[s].state = INFECTED
            self.node_attrs[s].infection_time = self.time_step
            self.logs.append(f"[t{self.time_step}] Seed infected node {s}")

    def snapshot_counts(self):
        counts = {SUSCEPTIBLE:0, INFECTED:0, PATCHED:0, QUARANTINED:0}
        for n in self.node_attrs:
            s = self.node_attrs[n].state
            counts[s] = counts.get(s,0) + 1
        return counts

# -------------------------
# Core transition logic (purely simulated)
# -------------------------
def step_simulation(sim: Simulation,
                    p_transmit: float,
                    p_detection_per_infected: float,
                    p_patch: float,
                    p_quarantine_success: float,
                    scan_freq: int,
                    max_time: int,
                    defender_action: str):
    """
    Simulate a single timestep for this simulation.
    - p_transmit: per-edge probability an infected node infects a susceptible neighbor
    - p_detection_per_infected: chance an infected node triggers a detection during a scan
    - p_patch: chance a susceptible node gets patched automatically (reduces future infection)
    - p_quarantine_success: when attempted, chance that quarantine is successful
    - scan_freq: perform IDS scan every `scan_freq` steps
    - defender_action: "isolate", "patch-on-detect", "none"
    """
    sim.time_step += 1
    new_states = {}
    G = sim.G

    # Transmission: infected -> susceptible neighbors
    for n in G.nodes():
        attrs = sim.node_attrs[n]
        if attrs.state == INFECTED:
            for nb in G.neighbors(n):
                nb_attrs = sim.node_attrs[nb]
                if nb_attrs.state == SUSCEPTIBLE:
                    if random.random() < p_transmit:
                        new_states[nb] = INFECTED

    # Automatic patching (background immunization)
    for n in G.nodes():
        attrs = sim.node_attrs[n]
        if attrs.state == SUSCEPTIBLE:
            if random.random() < p_patch:
                new_states[n] = PATCHED

    # IDS scanning/detections on schedule
    if scan_freq > 0 and sim.time_step % scan_freq == 0:
        # Each infected node has a detection chance
        for n in G.nodes():
            if sim.node_attrs[n].state == INFECTED:
                if random.random() < p_detection_per_infected:
                    sim.node_attrs[n].detected_time = sim.time_step
                    sim.logs.append(f"[t{sim.time_step}] Detection: node {n} suspected infected")
                    # Defender action
                    if defender_action == "isolate":
                        # Attempt quarantine
                        if random.random() < p_quarantine_success:
                            new_states[n] = QUARANTINED
                            sim.node_attrs[n].quarantined_time = sim.time_step
                            sim.logs.append(f"[t{sim.time_step}] Node {n} quarantined successfully")
                        else:
                            sim.logs.append(f"[t{sim.time_step}] Quarantine attempt failed on node {n}")
                    elif defender_action == "patch-on-detect":
                        new_states[n] = PATCHED
                        sim.logs.append(f"[t{sim.time_step}] Node {n} patched upon detection")

    # Apply new states
    for n, new_state in new_states.items():
        prev = sim.node_attrs[n].state
        if prev != new_state:
            sim.node_attrs[n].state = new_state
            if new_state == INFECTED:
                sim.node_attrs[n].infection_time = sim.time_step
                sim.logs.append(f"[t{sim.time_step}] Node {n} became infected")
            elif new_state == PATCHED:
                sim.logs.append(f"[t{sim.time_step}] Node {n} became patched (immune)")
            elif new_state == QUARANTINED:
                sim.logs.append(f"[t{sim.time_step}] Node {n} quarantined")

    # Record snapshot
    counts = sim.snapshot_counts()
    sim.history.append({"t": sim.time_step, **counts})

    return sim

# -------------------------
# Visualization helpers
# -------------------------
def history_df(sim: Simulation) -> pd.DataFrame:
    if not sim.history:
        return pd.DataFrame(columns=["t", SUSCEPTIBLE, INFECTED, PATCHED, QUARANTINED])
    return pd.DataFrame(sim.history)

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Safe Malware Behavior Simulator", layout="wide")
st.title("📚 Safe Malware Behavior Simulator — Educational (no real malware)")

with st.sidebar:
    st.header("Network topology")
    topology = st.selectbox("Topology type", ["Random", "Grid"])
    n_nodes = st.slider("Number of nodes", min_value=10, max_value=200, value=50, step=5)
    if topology == "Random":
        p_edge = st.slider("Edge probability (ER)", 0.01, 0.5, 0.08)
    elif topology == "Grid":
        grid_dim = st.slider("Grid dimension (rows/cols)", 3, 20, 7)

    st.header("Attacker parameters")
    init_infected = st.slider("Initial infected nodes (seed)", 1, 10, 2)
    p_transmit = st.slider("Per-edge transmit probability", 0.0, 1.0, 0.15)
    stealth_factor = st.slider("Stealth (reduces detectability)", 0.0, 1.0, 0.2,
                               help="Higher stealth reduces per-scan detection probability")

    st.header("Defender parameters")
    scan_freq = st.slider("IDS scan frequency (timesteps)", 1, 10, 3)
    p_detection_base = st.slider("Base detection chance per infected per-scan", 0.0, 1.0, 0.4)
    p_detection_per_infected = max(0.0, p_detection_base * (1.0 - stealth_factor))
    st.write(f"Effective per-infected detection probability: **{p_detection_per_infected:.3f}**")
    p_patch = st.slider("Background patching (per-node per-step)", 0.0, 0.5, 0.02)
    p_quarantine_success = st.slider("Quarantine success chance", 0.0, 1.0, 0.8)
    defender_action = st.selectbox("Action on detection", ["isolate", "patch-on-detect", "none"])

    st.header("Run controls")
    max_steps = st.slider("Max timesteps", 5, 500, 100)
    run_mode = st.radio("Run mode", ["Step", "Auto-run"], index=1)
    random_seed = st.number_input("Random seed (0 for random)", min_value=0, max_value=999999, value=42)

# Build graph
if topology.startswith("Random"):
    G = nx.erdos_renyi_graph(n_nodes, p_edge, seed=None if random_seed==0 else int(random_seed))
elif topology.startswith("Scale-free"):
    G = nx.barabasi_albert_graph(n_nodes, m_links, seed=None if random_seed==0 else int(random_seed))
else:
    # create grid
    dim = grid_dim
    G = nx.grid_2d_graph(dim, dim)
    # convert 2D tuple nodes to ints
    G = nx.convert_node_labels_to_integers(G)
    # reduce nodes if needed
    if n_nodes and len(G) > n_nodes:
        G = G.subgraph(list(G.nodes())[:n_nodes]).copy()

# Initialize or reset simulation object in session_state
if "sim" not in st.session_state or st.button("Reset simulation"):
    sim = Simulation(G)
    sim.reset_attrs()
    # seed random
    if random_seed != 0:
        random.seed(int(random_seed))
        np.random.seed(int(random_seed))
    # random initial seeds
    seeds = random.sample(list(G.nodes()), k=min(init_infected, G.number_of_nodes()))
    sim.seed_infections(seeds)
    st.session_state.sim = sim
else:
    sim: Simulation = st.session_state.sim
    # If topology or node count changed since last run, rebuild and reset
    if set(sim.G.nodes()) != set(G.nodes()) or sim.G.number_of_edges() != G.number_of_edges():
        sim = Simulation(G)
        sim.reset_attrs()
        if random_seed != 0:
            random.seed(int(random_seed))
            np.random.seed(int(random_seed))
        seeds = random.sample(list(G.nodes()), k=min(init_infected, G.number_of_nodes()))
        sim.seed_infections(seeds)
        st.session_state.sim = sim

# Controls and simulation loop
col = st.columns([1])
with col[0]:
    st.subheader("Simulation controls & status")
    st.write(f"Time step: **{sim.time_step}**")
    counts = sim.snapshot_counts()
    st.metric("Infected", counts[INFECTED], delta=None)
    st.metric("Susceptible", counts[SUSCEPTIBLE], delta=None)
    st.metric("Patched", counts[PATCHED], delta=None)

    if run_mode == "Step":
        if st.button("Advance 1 step"):
            sim = step_simulation(sim,
                                  p_transmit=p_transmit,
                                  p_detection_per_infected=p_detection_per_infected,
                                  p_patch=p_patch,
                                  p_quarantine_success=p_quarantine_success,
                                  scan_freq=scan_freq,
                                  max_time=max_steps,
                                  defender_action=defender_action)
            st.session_state.sim = sim
    else:
        if st.button("Auto-run to completion"):
            # auto-run until max_steps or no infections remain
            for _ in range(max_steps - sim.time_step):
                prev_infected = sim.snapshot_counts()[INFECTED]
                sim = step_simulation(sim,
                                      p_transmit=p_transmit,
                                      p_detection_per_infected=p_detection_per_infected,
                                      p_patch=p_patch,
                                      p_quarantine_success=p_quarantine_success,
                                      scan_freq=scan_freq,
                                      max_time=max_steps,
                                      defender_action=defender_action)
                # stop early if no infected remain
                if sim.snapshot_counts()[INFECTED] == 0:
                    break
            st.session_state.sim = sim

    st.markdown("### Recent logs (most recent 10)")
    for line in sim.logs[-10:][::-1]:
        st.write(line)

# History plots
st.subheader("Epidemic-like curve (history)")
df_hist = history_df(sim)
if not df_hist.empty:
    st.line_chart(df_hist.set_index("t")[[SUSCEPTIBLE, INFECTED, PATCHED, QUARANTINED]])
else:
    st.write("No history yet. Advance the simulation to see trends.")

# Details & export (safe)
st.subheader("Node table (safe)")
df_nodes = pd.DataFrame([
    {"node": n, "state": sim.node_attrs[n].state,
     "infected_at": sim.node_attrs[n].infection_time,
     "detected_at": sim.node_attrs[n].detected_time,
     "quarantined_at": sim.node_attrs[n].quarantined_time}
    for n in sim.node_attrs
])
st.dataframe(df_nodes)

