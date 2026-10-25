"""2D Toroidal Grid spatial topology implementation."""

from collections.abc import Sequence
from dataclasses import dataclass, field

from the_dilemma_experiment.domain.topology import (
    Coordinate2D,
    NeighborhoodType,
    SpatialTopology,
)


@dataclass(frozen=True)
class ToroidalGrid2D(SpatialTopology):
    """A 2D regular lattice with periodic toroidal boundary conditions.

    Coordinates wrap around seamlessly:
    - x' = x % width
    - y' = y % height
    """

    width: int
    height: int
    neighborhood_type: NeighborhoodType = NeighborhoodType.MOORE
    _edges: list[tuple[int, int]] = field(default_factory=list, repr=False, init=False)
    _neighbor_cache: dict[int, list[int]] = field(
        default_factory=dict, repr=False, init=False
    )

    def __post_init__(self) -> None:
        if self.width < 3 or self.height < 3:
            raise ValueError(
                f"Toroidal grid dimensions must be at least 3x3 to avoid self-loops. Got {self.width}x{self.height}."
            )

        # Precompute neighbor adjacency and unique edges
        neighbor_cache: dict[int, list[int]] = {}
        edge_set: set[tuple[int, int]] = set()

        if self.neighborhood_type == NeighborhoodType.VON_NEUMANN:
            offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        else:  # MOORE
            offsets = [
                (-1, -1),
                (0, -1),
                (1, -1),
                (-1, 0),
                (1, 0),
                (-1, 1),
                (0, 1),
                (1, 1),
            ]

        for y in range(self.height):
            for x in range(self.width):
                node_id = self.coord_to_id(x, y)
                nbrs: list[int] = []
                for dx, dy in offsets:
                    nx = (x + dx) % self.width
                    ny = (y + dy) % self.height
                    neighbor_id = self.coord_to_id(nx, ny)
                    nbrs.append(neighbor_id)
                    u, v = min(node_id, neighbor_id), max(node_id, neighbor_id)
                    if u != v:
                        edge_set.add((u, v))
                neighbor_cache[node_id] = sorted(nbrs)

        object.__setattr__(self, "_neighbor_cache", neighbor_cache)
        object.__setattr__(self, "_edges", sorted(edge_set))

    @property
    def node_count(self) -> int:
        return self.width * self.height

    def nodes(self) -> Sequence[int]:
        return range(self.node_count)

    def coord_to_id(self, x: int, y: int) -> int:
        """Convert 2D grid coordinates (x, y) to linear node ID."""
        return (y % self.height) * self.width + (x % self.width)

    def id_to_coord(self, node_id: int) -> Coordinate2D:
        """Convert linear node ID to 2D grid coordinate (x, y)."""
        if node_id < 0 or node_id >= self.node_count:
            raise IndexError(
                f"Node ID {node_id} out of bounds for grid size {self.node_count}."
            )
        y = node_id // self.width
        x = node_id % self.width
        return Coordinate2D(x=x, y=y)

    def neighbors(self, node_id: int) -> list[int]:
        if node_id not in self._neighbor_cache:
            raise IndexError(
                f"Node ID {node_id} out of bounds for grid size {self.node_count}."
            )
        return list(self._neighbor_cache[node_id])

    def degree(self, node_id: int) -> int:
        return len(self.neighbors(node_id))

    def edges(self) -> list[tuple[int, int]]:
        return list(self._edges)

    def get_cluster_node_ids(
        self, center_x: int, center_y: int, radius: int
    ) -> list[int]:
        """Return all node IDs within a square cluster of given radius around center."""
        cluster_ids: list[int] = []
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x = (center_x + dx) % self.width
                y = (center_y + dy) % self.height
                cluster_ids.append(self.coord_to_id(x, y))
        return sorted(set(cluster_ids))
