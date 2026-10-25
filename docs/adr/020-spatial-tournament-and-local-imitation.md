# ADR-020: Spatial Tournament and Local Imitation Dynamics

## Status

Accepted

## Context

In Episode 4 (Replicator Dynamics, ADR-017), reproduction occurred at a global population level: strategies reproduced in proportion to their share of total global wealth across a well-mixed society.

In spatial evolutionary biology and cellular automata models of game theory (Nowak & May 1992 *Nature*, Ohtsuki et al. 2006 *Nature*):
1. Interactions occur strictly between topologically connected neighbors.
2. Reproduction and behavioral imitation are localized: an individual observes the success of its immediate neighbors and adopts the strategy of the most successful neighbor (unconditional imitation / "imitate the best").
3. Local clusters of cooperators can protect each other from exterior exploiters because interior cooperators earn consistent mutual dividends without directly suffering exploitation.

To simulate spatial evolution, we require a deterministic, synchronous, double-buffered spatial tournament and local evolutionary update engine.

## Decision

1. **Edge-Based Symmetric Match Scheduling**:
   - For a topology $\mathcal{G} = (\mathcal{V}, \mathcal{E})$, each undirected edge $\{u, v\} \in \mathcal{E}$ (with $u < v$) represents a repeated interaction match.
   - A single `Match.execute()` is run per edge using fresh, isolated `Strategy` instances (ADR-001, ADR-010).
   - The match result yields payoff $S_{uv}$ for agent $u$ and $S_{vu}$ for agent $v$.
   - Symmetrical single-evaluation ensures computational efficiency: an edge is simulated exactly once per generation.

2. **Local Fitness Accumulation**:
   - For each node $u \in \mathcal{V}$:
     - Total score: $S(u) = \sum_{v \in \mathcal{N}(u)} S_{uv}$.
     - Average score per neighbor: $\bar{S}(u) = \frac{S(u)}{|\mathcal{N}(u)|}$.
   - For regular lattices (where degree is uniform across all nodes), total score and average score produce identical rankings.
   - For heterogeneous graphs (e.g., scale-free networks), normalized average score prevents high-degree hubs from trivially dominating simply due to degree volume. Both modes (`TOTAL` vs `AVERAGE`) are supported via `FitnessMode`.

3. **Synchronous Nowak-May Local Imitation Dynamics**:
   - Generational transitions occur synchronously using double-buffering: the strategy of every node at generation $t+1$ is determined purely from the states and payoffs of generation $t$.
   - For each node $u \in \mathcal{V}$:
     - Candidate set: $\mathcal{C}(u) = \mathcal{N}(u) \cup \{u\}$.
     - Candidate fitness: For each $c \in \mathcal{C}(u)$, evaluate fitness $F(c)$.
     - Strategy adoption: Node $u$ adopts the strategy archetype of $\arg\max_{c \in \mathcal{C}(u)} F(c)$.
   - **Deterministic Tie-Breaking**:
     1. Inertia / Incumbency: If the current occupant of node $u$ achieves a fitness equal to the maximum in $\mathcal{C}(u)$, node $u$ retains its strategy.
     2. If multiple external neighbors tie for the maximum fitness strictly greater than $u$'s fitness, the tie is broken deterministically by strategy archetype name alphabetically.

4. **Spatial Spatial Clustering Telemetry**:
   - In addition to demographic shares $N_i(t)$, each generation computes the **Cooperator Clustering Ratio**:
     $$\mathcal{K}_C(t) = \frac{\sum_{u \in \mathcal{V}_C} |\{v \in \mathcal{N}(u) \mid v \in \mathcal{V}_C\}|}{\sum_{u \in \mathcal{V}_C} |\mathcal{N}(u)|}$$
     where $\mathcal{V}_C$ is the set of nodes playing cooperative strategies.
   - When $\mathcal{K}_C(t) > \frac{N_C(t)}{N}$, cooperators are geographically clustered rather than randomly dispersed, validating the fortress hypothesis.

## Consequences

### Positive
- Faithfully reproduces classic spatial evolutionary game theory dynamics (Nowak-May 1992).
- Zero non-deterministic drift; 100% reproducible with deterministic random seeds.
- Synchronous double-buffering avoids asynchronous update sequence artifacts.
- Measures both demographic survival and topological cluster formation.

### Negative / Trade-offs
- Synchronous imitation can exhibit cyclic fractal patterns or periodic orbits (Nowak-May spatial chaos) that do not converge to fixation. This is scientifically authentic and forms a core narrative discovery for the episode.
