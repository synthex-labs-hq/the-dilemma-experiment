# ADR-019: Spatial Topology Abstraction

## Status

Accepted

## Context

In Episodes 1 through 4, multi-agent interactions assumed a **well-mixed population** (panmictic interaction):
- In Episode 2 (Tournament), every agent competed against every other agent in an all-to-all complete graph ($K_N$).
- In Episode 4 (Replicator Dynamics), global population shares determined reproductive fitness based on aggregate tournament scores.

In real-world biological systems, social organizations, and distributed networks, agents are constrained by **spatial geometry** and **network topology**:
1. Agents do not interact with all members of a population; they interact only with their immediate local neighbors.
2. A cooperator surrounded by other cooperators forms a protected interior cluster, while boundary agents absorb defection.
3. Network topologies (e.g. 2D lattices, small-world graphs, scale-free networks) fundamentally alter the evolutionary stability of cooperative strategies.

To investigate spatial reciprocity (Martin Nowak & Robert May 1992, Francisco Santos & Jorge Pacheco 2005), we require a formal, deterministic, dependency-free domain abstraction representing spatial topologies.

## Decision

1. **Topology Domain Abstraction (`SpatialTopology`)**:
   - Define a pure domain interface `SpatialTopology` representing a discrete graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$:
     - `nodes`: Set or sequence of discrete node identifiers $\{0, 1, \dots, N-1\}$.
     - `neighbors(node_id: int) -> list[int]`: Returns the sorted list of adjacent node IDs.
     - `degree(node_id: int) -> int`: Returns the number of adjacent neighbors.
     - Total capacity $N = |\mathcal{V}|$ is invariant.

2. **2D Toroidal Grid (`ToroidalGrid2D`)**:
   - Standard 2D lattice defined by `width` ($W$) and `height` ($H$), total nodes $N = W \times H$.
   - Each node possesses integer coordinates $(x, y) \in [0, W-1] \times [0, H-1]$.
   - Linear index mapping: $\text{node\_id} = y \cdot W + x$.
   - **Periodic Boundary Conditions (Torus)**:
     - Coordinate wrap-around: $x' = (x + \Delta x) \pmod W$, $y' = (y + \Delta y) \pmod H$.
     - Eliminates artificial edge and corner boundary distortions.
   - **Neighborhood Rules (`NeighborhoodType`)**:
     - `VON_NEUMANN`: 4 orthogonal neighbors (North, South, East, West).
     - `MOORE`: 8 neighbors (North, South, East, West, and 4 diagonals: NW, NE, SW, SE).

3. **Complex Network Topologies (`NetworkGraph`)**:
   - Pure Python standard library implementation of complex graph topologies:
     - **Ring Lattice**: Each node connected to $k$ nearest neighbors ($k/2$ on each side).
     - **Small-World Graph (Watts-Strogatz)**: Regular ring lattice with edges rewired with probability $\beta \in [0.0, 1.0]$.
     - **Scale-Free Network (Barabási-Albert)**: Preferential attachment generating power-law degree distribution with parameter $m$.
   - All stochastic generators accept a deterministic `random.Random` instance per ADR-003.

4. **Pure Python & Zero External Dependencies (ADR-006)**:
   - Implemented exclusively using Python 3.12 standard library (`dataclasses`, `enum`, `math`, `random`).
   - No external heavy dependencies (e.g. `networkx` or `scipy`), ensuring lightning-fast execution and zero-bloat portability.

## Consequences

### Positive
- Enables rigorous modeling of spatial clusters, territory expansion, and local defense against defector invasions.
- Supports both regular geometric grids (Nowak-May 1992) and heterogeneous social network topologies (Santos-Pacheco 2005).
- 100% deterministic, seed-controlled replayability (ADR-003).
- Fast execution suitable for real-time terminal demos and web UI rendering.

### Negative / Trade-offs
- Custom graph generator implementations require rigorous zero-mock testing to verify graph properties (connectedness, degree distributions, rewiring invariance).
