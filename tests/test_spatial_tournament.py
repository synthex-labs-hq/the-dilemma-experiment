"""Zero-mock unit tests for spatial tournament and local imitation dynamics."""

import random

import pytest

from the_dilemma_experiment.domain.network_graph import NetworkGraph
from the_dilemma_experiment.domain.spatial_grid import ToroidalGrid2D
from the_dilemma_experiment.domain.spatial_tournament import (
    FitnessMode,
    SpatialTournament,
)
from the_dilemma_experiment.domain.topology import NeighborhoodType
from the_dilemma_experiment.strategies.always_cooperate import (
    AlwaysCooperateStrategy,
)
from the_dilemma_experiment.strategies.always_defect import (
    AlwaysDefectStrategy,
)
from the_dilemma_experiment.strategies.tit_for_tat import (
    TitForTatStrategy,
)


def test_spatial_tournament_initialization_validation() -> None:
    """Strategy count must match topology node count exactly."""
    grid = ToroidalGrid2D(width=3, height=3)  # 9 nodes
    with pytest.raises(ValueError, match="Initial strategies count"):
        SpatialTournament(
            topology=grid,
            initial_strategies=[AlwaysCooperateStrategy] * 8,
        )


def test_spatial_tournament_homogeneous_fixation() -> None:
    """A homogeneous society begins fixated and remains invariant across generations."""
    grid = ToroidalGrid2D(width=4, height=4)  # 16 nodes
    tourney = SpatialTournament(
        topology=grid,
        initial_strategies=[AlwaysCooperateStrategy] * 16,
    )

    res0 = tourney.history[0]
    assert res0.is_fixated is True
    assert res0.dominant_strategy == "AlwaysCooperateStrategy"
    assert res0.cooperator_clustering_ratio == 1.0

    step1 = tourney.step()
    assert step1.is_fixated is True
    assert step1.dominant_strategy == "AlwaysCooperateStrategy"


def test_the_fortress_effect_cluster_stability_and_expansion() -> None:
    """Validate spatial cluster mechanics:

    1. Altruist Fortress: 9 AlwaysCooperate nodes in 91 Defectors survive indefinitely
       (in a well-mixed soup from Ep 4, they are wiped out in 3 generations).
    2. Reciprocal Conquest: A 3x3 cluster of TitForTat with R=5 expands outward
       and completely conquers the grid in 4 generations (9 -> 25 -> 49 -> 81 -> 100).
    """
    width, height = 10, 10
    grid = ToroidalGrid2D(
        width=width, height=height, neighborhood_type=NeighborhoodType.MOORE
    )

    # 1. Altruist fortress: 9 AlwaysCooperate surrounded by 91 Defectors
    altruist_strategies = [AlwaysDefectStrategy] * grid.node_count
    cluster_nodes = grid.get_cluster_node_ids(center_x=5, center_y=5, radius=1)
    for node_id in cluster_nodes:
        altruist_strategies[node_id] = AlwaysCooperateStrategy

    altruist_tourney = SpatialTournament(
        topology=grid,
        initial_strategies=altruist_strategies,
        rounds_per_match=1,
    )
    for _ in range(5):
        altruist_tourney.step()

    altruist_final = altruist_tourney.history[-1].strategy_distribution
    # The fortress holds: Altruists do NOT go extinct!
    assert altruist_final["AlwaysCooperateStrategy"] == 9
    assert altruist_final["AlwaysDefectStrategy"] == 91

    # 2. Reciprocal Conquest: 9 TitForTat in 91 Defectors with repeated matches
    tft_strategies = [AlwaysDefectStrategy] * grid.node_count
    for node_id in cluster_nodes:
        tft_strategies[node_id] = TitForTatStrategy

    tft_tourney = SpatialTournament(
        topology=grid,
        initial_strategies=tft_strategies,
        rounds_per_match=5,
    )
    result = tft_tourney.run(max_generations=5)
    # TitForTat completely converts the population to 100% cooperation!
    assert result.converged is True
    assert result.dominant_strategy == "TitForTatStrategy"
    assert result.final_distribution["TitForTatStrategy"] == 100


def test_spatial_tournament_inertia_rule() -> None:
    """When a node's current score ties with the highest neighbor score, it retains its strategy."""
    grid = ToroidalGrid2D(width=4, height=4)
    # Split grid 50/50 vertically
    strategies: list[type] = []
    for y in range(4):
        for x in range(4):
            if x < 2:
                strategies.append(AlwaysCooperateStrategy)
            else:
                strategies.append(TitForTatStrategy)

    tourney = SpatialTournament(topology=grid, initial_strategies=strategies)
    # All interactions are C vs C, so every agent earns identical scores (8 neighbors * 3 = 24)
    # With everyone tied, inertia dictates zero changes
    res1 = tourney.step()
    assert res1.strategy_distribution["AlwaysCooperateStrategy"] == 8
    assert res1.strategy_distribution["TitForTatStrategy"] == 8


def test_spatial_tournament_on_network_graph() -> None:
    """Spatial tournament functions seamlessly on arbitrary network topologies."""
    ring = NetworkGraph.ring_lattice(n=20, k=4)
    rng = random.Random(999)

    # Alternate C and D along the ring
    strats = [
        AlwaysCooperateStrategy if i % 2 == 0 else AlwaysDefectStrategy
        for i in range(20)
    ]

    tourney = SpatialTournament(
        topology=ring,
        initial_strategies=strats,
        fitness_mode=FitnessMode.AVERAGE,
        rng=rng,
    )
    result = tourney.run(max_generations=10)

    assert len(result.generations) > 1
    assert result.final_generation <= 10
