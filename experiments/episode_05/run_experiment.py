#!/usr/bin/env python3
"""Batch experiment runner for Episode 5: Spatial Networks & Topologies.

Executes three benchmark experiments:
- Experiment A: The Altruist Fortress (Cluster size threshold vs Extinction).
- Experiment B: Reciprocal Spatial Conquest (TitForTat territorial expansion).
- Experiment C: Network Topology Vulnerability (Small-world rewiring beta).

Produces: experiments/episode_05/experiment_results.json
"""

import json
import random
from pathlib import Path

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

OUTPUT_FILE = Path(__file__).parent / "experiment_results.json"


def run_experiment_a_altruist_fortress() -> dict:
    """Experiment A: Can a cluster of pure Altruists survive in a sea of Predators?"""
    width, height = 20, 20  # 400 agents
    grid = ToroidalGrid2D(
        width=width, height=height, neighborhood_type=NeighborhoodType.MOORE
    )

    # 400 defectors
    strategies = [AlwaysDefectStrategy] * grid.node_count

    # Plant a 3x3 cluster (9 agents, 2.25% of population) at center (10, 10)
    cluster_nodes = grid.get_cluster_node_ids(center_x=10, center_y=10, radius=1)
    for node_id in cluster_nodes:
        strategies[node_id] = AlwaysCooperateStrategy

    tourney = SpatialTournament(
        topology=grid,
        initial_strategies=strategies,
        rounds_per_match=1,
    )

    history_snapshots = []
    for gen in range(15):
        current_gen = tourney.history[-1]
        dist = current_gen.strategy_distribution
        history_snapshots.append(
            {
                "generation": gen,
                "altruists": dist.get("AlwaysCooperateStrategy", 0),
                "predators": dist.get("AlwaysDefectStrategy", 0),
                "clustering_ratio": round(current_gen.cooperator_clustering_ratio, 4),
            }
        )
        tourney.step()

    final_dist = tourney.history[-1].strategy_distribution
    return {
        "title": "Experiment A: The Altruist Fortress",
        "description": "A 3x3 cluster (9 agents = 2.25%) of Altruists surrounded by 391 Predators on a 20x20 Moore lattice.",
        "grid_size": f"{width}x{height} (400 nodes)",
        "initial_altruists": 9,
        "initial_predators": 391,
        "final_altruists": final_dist.get("AlwaysCooperateStrategy", 0),
        "final_predators": final_dist.get("AlwaysDefectStrategy", 0),
        "fortress_survived": final_dist.get("AlwaysCooperateStrategy", 0) > 0,
        "history": history_snapshots,
    }


def run_experiment_b_reciprocal_conquest() -> dict:
    """Experiment B: Reciprocal Spatial Expansion (TitForTat 3x3 cluster on 20x20 grid)."""
    width, height = 20, 20  # 400 agents
    grid = ToroidalGrid2D(
        width=width, height=height, neighborhood_type=NeighborhoodType.MOORE
    )

    strategies = [AlwaysDefectStrategy] * grid.node_count
    cluster_nodes = grid.get_cluster_node_ids(center_x=10, center_y=10, radius=1)
    for node_id in cluster_nodes:
        strategies[node_id] = TitForTatStrategy

    tourney = SpatialTournament(
        topology=grid,
        initial_strategies=strategies,
        rounds_per_match=5,
    )

    history_snapshots = []
    for gen in range(15):
        current_gen = tourney.history[-1]
        dist = current_gen.strategy_distribution
        history_snapshots.append(
            {
                "generation": gen,
                "tit_for_tat": dist.get("TitForTatStrategy", 0),
                "predators": dist.get("AlwaysDefectStrategy", 0),
                "clustering_ratio": round(current_gen.cooperator_clustering_ratio, 4),
            }
        )
        if current_gen.is_fixated:
            break
        tourney.step()

    final_dist = tourney.history[-1].strategy_distribution
    return {
        "title": "Experiment B: Reciprocal Spatial Expansion",
        "description": "A 3x3 cluster (9 agents = 2.25%) of Tit-for-Tat in 391 Predators with 5 repeated rounds per match.",
        "grid_size": f"{width}x{height} (400 nodes)",
        "initial_tit_for_tat": 9,
        "initial_predators": 391,
        "final_tit_for_tat": final_dist.get("TitForTatStrategy", 0),
        "final_predators": final_dist.get("AlwaysDefectStrategy", 0),
        "conquered_all": final_dist.get("TitForTatStrategy", 0) == 400,
        "generations_to_fixation": len(history_snapshots) - 1,
        "history": history_snapshots,
    }


def run_experiment_c_small_world_vulnerability() -> dict:
    """Experiment C: How small-world shortcuts (beta) degrade the local spatial fortress."""
    n = 100
    k = 8  # 8 neighbors per node
    betas = [0.0, 0.05, 0.1, 0.25, 0.5]
    results_by_beta = []

    for beta in betas:
        rng = random.Random(42)
        graph = NetworkGraph.small_world(n=n, k=k, beta=beta, rng=rng)

        # 20% contiguous cooperators (TFT) along ring indices 40-59
        strategies = [AlwaysDefectStrategy] * n
        for i in range(40, 60):
            strategies[i] = TitForTatStrategy

        tourney = SpatialTournament(
            topology=graph,
            initial_strategies=strategies,
            rounds_per_match=5,
            fitness_mode=FitnessMode.AVERAGE,
            rng=rng,
        )
        res = tourney.run(max_generations=20)
        final_tft = res.final_distribution.get("TitForTatStrategy", 0)

        results_by_beta.append(
            {
                "beta": beta,
                "initial_tft": 20,
                "final_tft": final_tft,
                "final_predators": res.final_distribution.get(
                    "AlwaysDefectStrategy", 0
                ),
                "tft_survival_rate": round(final_tft / n, 4),
            }
        )

    return {
        "title": "Experiment C: Small-World Network Vulnerability",
        "description": "Testing how rewiring probability beta (shortcuts) impacts the survival of a 20% cooperative cluster.",
        "node_count": n,
        "results_by_beta": results_by_beta,
    }


def main() -> None:
    print("Running Episode 5 Spatial Benchmark Experiments...")

    exp_a = run_experiment_a_altruist_fortress()
    print(
        f"✓ {exp_a['title']}: Fortress survived = {exp_a['fortress_survived']} (9 Altruists held against 391 Predators)"
    )

    exp_b = run_experiment_b_reciprocal_conquest()
    print(
        f"✓ {exp_b['title']}: Conquered all in {exp_b['generations_to_fixation']} generations (9 -> {exp_b['final_tit_for_tat']})"
    )

    exp_c = run_experiment_c_small_world_vulnerability()
    print(f"✓ {exp_c['title']}: Tested {len(exp_c['results_by_beta'])} rewiring levels")

    payload = {
        "episode": "05",
        "title": "Spatial Networks & Topologies",
        "experiments": [exp_a, exp_b, exp_c],
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"\nAll benchmark results successfully written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
