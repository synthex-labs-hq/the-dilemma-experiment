"""Zero-mock unit tests for spatial topologies (2D Toroidal Grid & Network Graphs)."""

import random

import pytest

from the_dilemma_experiment.domain.network_graph import NetworkGraph
from the_dilemma_experiment.domain.spatial_grid import ToroidalGrid2D
from the_dilemma_experiment.domain.topology import Coordinate2D, NeighborhoodType


def test_toroidal_grid_validation() -> None:
    """Toroidal grid requires dimensions of at least 3x3."""
    with pytest.raises(ValueError, match="at least 3x3"):
        ToroidalGrid2D(width=2, height=3)

    with pytest.raises(ValueError, match="at least 3x3"):
        ToroidalGrid2D(width=4, height=2)

    grid = ToroidalGrid2D(width=5, height=5)
    assert grid.node_count == 25
    assert len(grid.nodes()) == 25


def test_toroidal_grid_coordinate_conversions() -> None:
    """Linear ID and 2D coordinate mappings must be bijective inverses."""
    grid = ToroidalGrid2D(width=4, height=6)
    for y in range(6):
        for x in range(4):
            node_id = grid.coord_to_id(x, y)
            coord = grid.id_to_coord(node_id)
            assert coord == Coordinate2D(x=x, y=y)

    with pytest.raises(IndexError):
        grid.id_to_coord(-1)

    with pytest.raises(IndexError):
        grid.id_to_coord(24)


def test_toroidal_grid_von_neumann_neighborhood() -> None:
    """Von Neumann neighborhood must return exactly 4 orthogonal wrapped neighbors."""
    grid = ToroidalGrid2D(
        width=4, height=4, neighborhood_type=NeighborhoodType.VON_NEUMANN
    )
    # Corner node at (0, 0)
    corner_id = grid.coord_to_id(0, 0)
    nbrs = grid.neighbors(corner_id)
    assert len(nbrs) == 4

    expected_coords = {(3, 0), (1, 0), (0, 3), (0, 1)}
    actual_coords = {(grid.id_to_coord(n).x, grid.id_to_coord(n).y) for n in nbrs}
    assert actual_coords == expected_coords
    assert grid.degree(corner_id) == 4

    # Total edges for Von Neumann on 4x4 should be 4*4*4/2 = 32
    assert len(grid.edges()) == 32


def test_toroidal_grid_moore_neighborhood() -> None:
    """Moore neighborhood must return exactly 8 wrapped neighbors."""
    grid = ToroidalGrid2D(width=5, height=5, neighborhood_type=NeighborhoodType.MOORE)
    center_id = grid.coord_to_id(2, 2)
    nbrs = grid.neighbors(center_id)
    assert len(nbrs) == 8

    # Corner wrap check (0, 0)
    corner_id = grid.coord_to_id(0, 0)
    corner_nbrs = grid.neighbors(corner_id)
    assert len(corner_nbrs) == 8
    expected_corner_coords = {
        (4, 4),
        (0, 4),
        (1, 4),
        (4, 0),
        (1, 0),
        (4, 1),
        (0, 1),
        (1, 1),
    }
    actual_corner_coords = {
        (grid.id_to_coord(n).x, grid.id_to_coord(n).y) for n in corner_nbrs
    }
    assert actual_corner_coords == expected_corner_coords

    # Total edges for Moore on 5x5 should be 5*5*8/2 = 100
    assert len(grid.edges()) == 100


def test_toroidal_grid_cluster_extraction() -> None:
    """Square cluster helper extracts accurate node sets."""
    grid = ToroidalGrid2D(width=10, height=10)
    # 3x3 cluster with radius 1 around (5, 5)
    cluster = grid.get_cluster_node_ids(center_x=5, center_y=5, radius=1)
    assert len(cluster) == 9

    # Radius 0 is just center node
    single = grid.get_cluster_node_ids(center_x=5, center_y=5, radius=0)
    assert single == [grid.coord_to_id(5, 5)]


def test_ring_lattice_generation() -> None:
    """Ring lattice connects each node to k nearest neighbors."""
    graph = NetworkGraph.ring_lattice(n=10, k=4)
    assert graph.node_count == 10
    assert len(graph.edges()) == 20  # 10 * 4 / 2

    for node in graph.nodes():
        assert graph.degree(node) == 4
        # Neighbors of 0 in ring of 10 with k=4 should be 1, 2, 8, 9
        if node == 0:
            assert set(graph.neighbors(0)) == {1, 2, 8, 9}

    with pytest.raises(ValueError, match="even integer"):
        NetworkGraph.ring_lattice(n=10, k=3)

    with pytest.raises(ValueError, match="strictly less than n"):
        NetworkGraph.ring_lattice(n=6, k=6)


def test_small_world_network_determinism() -> None:
    """Watts-Strogatz small world generator produces reproducible networks with fixed seeds."""
    rng1 = random.Random(42)
    rng2 = random.Random(42)

    g1 = NetworkGraph.small_world(n=20, k=4, beta=0.2, rng=rng1)
    g2 = NetworkGraph.small_world(n=20, k=4, beta=0.2, rng=rng2)

    assert g1.edges() == g2.edges()
    assert g1.node_count == 20
    assert len(g1.edges()) == 40

    with pytest.raises(ValueError, match=r"beta must be in \[0.0, 1.0\]"):
        NetworkGraph.small_world(n=10, k=4, beta=1.5)


def test_scale_free_network_preferential_attachment() -> None:
    """Barabási-Albert scale-free network generates power-law degree distributions."""
    rng = random.Random(101)
    g = NetworkGraph.scale_free(n=50, m=3, rng=rng)

    assert g.node_count == 50
    # Every node has at least degree m
    degrees = [g.degree(i) for i in g.nodes()]
    assert all(deg >= 3 for deg in degrees)

    # In scale-free graphs, maximum degree is substantially higher than mean degree
    mean_deg = sum(degrees) / len(degrees)
    max_deg = max(degrees)
    assert max_deg > mean_deg * 2

    with pytest.raises(ValueError, match="m must be at least 1"):
        NetworkGraph.scale_free(n=10, m=0)

    with pytest.raises(ValueError, match="strictly greater than m"):
        NetworkGraph.scale_free(n=3, m=3)
