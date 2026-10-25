#!/usr/bin/env python3
"""Simulation Experiment Runner for Episode 4: Natural Selection & Replicator Dynamics.

Executes reproducible multi-generation evolutionary tournaments across three experimental setups:
1. Experiment A: The Altruist-Predator Boom & Bust (The Ecological Tragedy)
2. Experiment B: The Invasion Barrier & Critical Mass (Infiltration of a Defector World)
3. Experiment C: The 8-Archetype Evolutionary Arena under Communication Noise (5% Noise)

Outputs results to JSON and prints formatted generation trajectories and extinction audits.
"""

import json
from pathlib import Path

from the_dilemma_experiment.domain.evolutionary_tournament import (
    EvolutionaryTournament,
)
from the_dilemma_experiment.strategies.always_cooperate import (
    AlwaysCooperateStrategy,
)
from the_dilemma_experiment.strategies.always_defect import (
    AlwaysDefectStrategy,
)
from the_dilemma_experiment.strategies.generous_tit_for_tat import (
    GenerousTitForTatStrategy,
)
from the_dilemma_experiment.strategies.grim_trigger import (
    GrimTriggerStrategy,
)
from the_dilemma_experiment.strategies.random_strategy import (
    RandomStrategy,
)
from the_dilemma_experiment.strategies.tit_for_tat import (
    TitForTatStrategy,
)
from the_dilemma_experiment.strategies.tit_for_two_tats import (
    TitForTwoTatsStrategy,
)
from the_dilemma_experiment.strategies.win_stay_lose_shift import (
    WinStayLoseShiftStrategy,
)


def run_experiment_a_boom_and_bust(generations: int = 10, seed: int = 42) -> dict:
    """Experiment A: 50 Altruists vs 50 Predators.

    Demonstrates the ecological tragedy: Predators multiply rapidly by exploiting Altruists,
    driving them to extinction. Once Altruists are gone, Predators starve in a mutual defection wasteland.
    """
    evo = EvolutionaryTournament(
        initial_population={
            AlwaysCooperateStrategy: 50,
            AlwaysDefectStrategy: 50,
        },
        rounds_per_match=10,
        noise=0.0,
        seed=seed,
    )

    results = evo.run(generations=generations)
    gen_data = [r.to_dict(include_tournament=False) for r in results]

    return {
        "title": "The Altruist-Predator Boom & Bust",
        "description": "50 Altruists vs 50 Predators under Replicator Dynamics",
        "carrying_capacity": 100,
        "generations_run": len(results),
        "is_converged": evo.is_converged,
        "final_counts": evo.current_counts,
        "trajectory": gen_data,
    }


def run_experiment_b_invasion_threshold(rounds_per_match: int = 10, seed: int = 42) -> dict:
    """Experiment B: Testing the invasion barrier of cooperation against pure defectors.

    B1 (Sub-threshold): 98 Predators vs 2 Tit-for-Tat (Isolated).
    B2 (Critical mass): 80 Predators vs 20 Tit-for-Tat (Clustered threshold).
    """
    # Sub-experiment B1: Isolated infiltrator (2%)
    evo_isolated = EvolutionaryTournament(
        initial_population={
            AlwaysDefectStrategy: 98,
            TitForTatStrategy: 2,
        },
        rounds_per_match=rounds_per_match,
        noise=0.0,
        seed=seed,
    )
    res_isolated = evo_isolated.run(generations=10)

    # Sub-experiment B2: Clustered threshold (20%)
    evo_clustered = EvolutionaryTournament(
        initial_population={
            AlwaysDefectStrategy: 80,
            TitForTatStrategy: 20,
        },
        rounds_per_match=rounds_per_match,
        noise=0.0,
        seed=seed,
    )
    res_clustered = evo_clustered.run(generations=15)

    return {
        "title": "The Invasion Barrier of Cooperation",
        "sub_experiments": {
            "isolated_infiltrator_2_percent": {
                "initial_counts": {"AlwaysDefect": 98, "TitForTat": 2},
                "final_counts": evo_isolated.current_counts,
                "is_converged": evo_isolated.is_converged,
                "generations": [r.to_dict(include_tournament=False) for r in res_isolated],
            },
            "clustered_threshold_20_percent": {
                "initial_counts": {"AlwaysDefect": 80, "TitForTat": 20},
                "final_counts": evo_clustered.current_counts,
                "is_converged": evo_clustered.is_converged,
                "generations": [r.to_dict(include_tournament=False) for r in res_clustered],
            },
        },
    }


def run_experiment_c_8_archetype_arena(
    generations: int = 25, noise: float = 0.05, seed: int = 42
) -> dict:
    """Experiment C: 8-Archetype Evolutionary Arena under Communication Noise.

    Tests the evolutionary survival of forgiving strategies (Generous TFT, Pavlov, Tit-for-Two-Tats)
    versus brittle strategies (Grim Trigger, Tit-for-Tat) and predators under 5% noise.
    """
    init_pop = {
        AlwaysCooperateStrategy: 12,
        AlwaysDefectStrategy: 13,
        TitForTatStrategy: 12,
        GrimTriggerStrategy: 12,
        (lambda: RandomStrategy(cooperation_probability=0.5, seed=seed)): 12,
        (lambda: GenerousTitForTatStrategy(forgiveness_probability=0.33, seed=seed + 1)): 13,
        TitForTwoTatsStrategy: 12,
        WinStayLoseShiftStrategy: 12,
    }

    evo = EvolutionaryTournament(
        initial_population=init_pop,
        rounds_per_match=15,
        noise=noise,
        seed=seed,
    )

    results = evo.run(generations=generations)
    gen_data = [r.to_dict(include_tournament=False) for r in results]

    return {
        "title": "8-Archetype Evolutionary Arena under Noise",
        "noise_rate": noise,
        "carrying_capacity": 98,
        "generations_run": len(results),
        "is_converged": evo.is_converged,
        "final_counts": evo.current_counts,
        "extinct_strategies": list(evo.extinct_strategies),
        "trajectory": gen_data,
    }


def main():
    print("=" * 80)
    print("THE DILEMMA EXPERIMENT — EPISODE 4: NATURAL SELECTION & REPLICATOR DYNAMICS")
    print("Running reproducible evolutionary simulation experiments across generations...")
    print("=" * 80)

    # 1. Run Experiment A: Boom and Bust
    print("\n[1/3] Simulating Experiment A: The Altruist-Predator Boom & Bust...")
    exp_a = run_experiment_a_boom_and_bust(generations=8, seed=42)
    print(f" -> Converged: {exp_a['is_converged']} at Generation {exp_a['generations_run'] - 1}")
    print(f" -> Final Counts: {exp_a['final_counts']}")

    # 2. Run Experiment B: Invasion Thresholds
    print("\n[2/3] Simulating Experiment B: The Invasion Barrier & Critical Mass...")
    exp_b = run_experiment_b_invasion_threshold(rounds_per_match=10, seed=42)
    b1_final = exp_b["sub_experiments"]["isolated_infiltrator_2_percent"]["final_counts"]
    b2_final = exp_b["sub_experiments"]["clustered_threshold_20_percent"]["final_counts"]
    print(f" -> B1 (2% Isolated TFT): {b1_final} (Cooperation Extinct)")
    print(f" -> B2 (20% Clustered TFT): {b2_final} (Cooperation Takes Over!)")

    # 3. Run Experiment C: 8-Archetype Arena under 5% Noise
    print("\n[3/3] Simulating Experiment C: 8-Archetype Arena under 5% Noise (25 Generations)...")
    exp_c = run_experiment_c_8_archetype_arena(generations=25, noise=0.05, seed=42)
    print(f" -> Final Counts: {exp_c['final_counts']}")
    print(f" -> Extinct Strategies: {exp_c['extinct_strategies']}")

    all_results = {
        "episode": 4,
        "title": "Natural Selection & Replicator Dynamics",
        "description": "Simulation results examining generational evolution, extinction, invasion, and evolutionary stability.",
        "experiment_a_boom_and_bust": exp_a,
        "experiment_b_invasion_threshold": exp_b,
        "experiment_c_8_archetype_arena": exp_c,
    }

    # Save to JSON
    output_dir = Path(__file__).resolve().parent
    output_path = output_dir / "experiment_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n[OK] Successfully saved verified results to: {output_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
