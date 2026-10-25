"""Graph-based spatial topology implementations for complex networks."""

import random
from collections.abc import Sequence
from dataclasses import dataclass, field

from the_dilemma_experiment.domain.topology import SpatialTopology


@dataclass(frozen=True)
class NetworkGraph(SpatialTopology):
    """General graph topology supporting arbitrary adjacency lists."""

    _node_count: int
    _adj: dict[int, list[int]] = field(repr=False)
    _edges: list[tuple[int, int]] = field(repr=False)

    @property
    def node_count(self) -> int:
        return self._node_count

    def nodes(self) -> Sequence[int]:
        return range(self._node_count)

    def neighbors(self, node_id: int) -> list[int]:
        if node_id not in self._adj:
            raise IndexError(
                f"Node ID {node_id} out of bounds for graph size {self._node_count}."
            )
        return list(self._adj[node_id])

    def degree(self, node_id: int) -> int:
        return len(self.neighbors(node_id))

    def edges(self) -> list[tuple[int, int]]:
        return list(self._edges)

    @classmethod
    def from_edges(cls, n: int, edges: Sequence[tuple[int, int]]) -> "NetworkGraph":
        """Build a graph from an explicit list of undirected edges."""
        if n < 2:
            raise ValueError(f"Graph must have at least 2 nodes. Got {n}.")

        adj: dict[int, set[int]] = {i: set() for i in range(n)}
        unique_edges: set[tuple[int, int]] = set()

        for u, v in edges:
            if u == v:
                continue  # skip self-loops
            if not (0 <= u < n and 0 <= v < n):
                raise ValueError(
                    f"Edge ({u}, {v}) references out-of-bounds node for n={n}."
                )
            adj[u].add(v)
            adj[v].add(u)
            unique_edges.add((min(u, v), max(u, v)))

        sorted_adj = {i: sorted(adj[i]) for i in range(n)}
        return cls(_node_count=n, _adj=sorted_adj, _edges=sorted(unique_edges))

    @classmethod
    def ring_lattice(cls, n: int, k: int) -> "NetworkGraph":
        """Generate a regular ring lattice of n nodes where each node is connected to k neighbors.

        k must be an even integer and k < n.
        """
        if n < 3:
            raise ValueError(f"Ring lattice requires at least 3 nodes. Got {n}.")
        if k % 2 != 0:
            raise ValueError(f"k must be an even integer. Got {k}.")
        if k >= n:
            raise ValueError(f"k must be strictly less than n. Got k={k}, n={n}.")

        edges: set[tuple[int, int]] = set()
        half_k = k // 2
        for i in range(n):
            for d in range(1, half_k + 1):
                j = (i + d) % n
                edges.add((min(i, j), max(i, j)))

        return cls.from_edges(n, list(edges))

    @classmethod
    def small_world(
        cls, n: int, k: int, beta: float, rng: random.Random | None = None
    ) -> "NetworkGraph":
        """Generate a Watts-Strogatz small-world network.

        - n: Number of nodes
        - k: Each node connects to k nearest neighbors in ring lattice (k even)
        - beta: Rewiring probability in [0.0, 1.0]
        - rng: Deterministic random.Random instance (ADR-003)
        """
        if not (0.0 <= beta <= 1.0):
            raise ValueError(
                f"Rewiring probability beta must be in [0.0, 1.0]. Got {beta}."
            )

        if rng is None:
            rng = random.Random()

        # Start with regular ring lattice
        base = cls.ring_lattice(n, k)
        edges = set(base.edges())
        half_k = k // 2

        # Rewire edges with probability beta
        for i in range(n):
            for d in range(1, half_k + 1):
                orig_j = (i + d) % n
                edge = (min(i, orig_j), max(i, orig_j))
                if edge in edges and rng.random() < beta:
                    edges.remove(edge)
                    # Candidate destinations (excluding self and existing neighbors)
                    existing_neighbors = {v for u, v in edges if u == i} | {
                        u for u, v in edges if v == i
                    }
                    candidates = [
                        node
                        for node in range(n)
                        if node != i and node not in existing_neighbors
                    ]
                    if candidates:
                        new_j = rng.choice(candidates)
                        edges.add((min(i, new_j), max(i, new_j)))
                    else:
                        edges.add(edge)  # Fallback if no valid rewiring target

        return cls.from_edges(n, list(edges))

    @classmethod
    def scale_free(
        cls, n: int, m: int, rng: random.Random | None = None
    ) -> "NetworkGraph":
        """Generate a Barabási-Albert scale-free network using preferential attachment.

        - n: Final number of nodes
        - m: Number of edges to attach from a new node to existing nodes (1 <= m < n)
        - rng: Deterministic random.Random instance (ADR-003)
        """
        if m < 1:
            raise ValueError(f"m must be at least 1. Got {m}.")
        if n <= m:
            raise ValueError(f"n must be strictly greater than m. Got n={n}, m={m}.")

        if rng is None:
            rng = random.Random()

        # Seed with a complete graph of m0 = m + 1 nodes
        m0 = m + 1
        edges: set[tuple[int, int]] = set()
        for i in range(m0):
            for j in range(i + 1, m0):
                edges.add((i, j))

        # Repeated-nodes list for O(1) proportional degree sampling
        repeated_nodes: list[int] = []
        for u, v in edges:
            repeated_nodes.append(u)
            repeated_nodes.append(v)

        # Add remaining nodes one by one
        for source in range(m0, n):
            targets: set[int] = set()
            while len(targets) < m:
                target = rng.choice(repeated_nodes)
                if target != source:
                    targets.add(target)

            for target in targets:
                edges.add((min(source, target), max(source, target)))
                repeated_nodes.append(source)
                repeated_nodes.append(target)

        return cls.from_edges(n, list(edges))
