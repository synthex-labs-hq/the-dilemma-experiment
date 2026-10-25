"""Spatial topology domain contracts and primitives."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum


class NeighborhoodType(str, Enum):
    """Neighborhood boundary rule for 2D spatial lattices."""

    VON_NEUMANN = "von_neumann"  # 4 orthogonal neighbors (N, S, E, W)
    MOORE = "moore"  # 8 neighbors (N, S, E, W + 4 diagonals)


@dataclass(frozen=True, slots=True)
class Coordinate2D:
    """Discrete 2D coordinate on a spatial grid."""

    x: int
    y: int


class SpatialTopology(ABC):
    """Abstract base class for spatial structures and network graphs."""

    @property
    @abstractmethod
    def node_count(self) -> int:
        """Total number of nodes in the topology."""
        ...

    @abstractmethod
    def nodes(self) -> Sequence[int]:
        """Sequence of all node IDs [0, 1, ..., N-1]."""
        ...

    @abstractmethod
    def neighbors(self, node_id: int) -> list[int]:
        """Return the sorted list of adjacent neighbor node IDs."""
        ...

    @abstractmethod
    def degree(self, node_id: int) -> int:
        """Return the degree (number of neighbors) of a node."""
        ...

    @abstractmethod
    def edges(self) -> list[tuple[int, int]]:
        """Return all unique undirected edges (u, v) where u < v."""
        ...
