#!/usr/bin/env python3
"""Episode 7 Benchmark: Tags, Tribalism, and In-Group Favoritism.

Executes three scientific experiments:
1. Categorical Tribalism: 4 distinct tribes and the in-group favoritism gradient.
2. The Green-Beard Dilemma: The False-Beard invasion and exploitation of in-group altruism.
3. Evolutionary Tag Dynamics: Replication of Riolo, Cohen & Axelrod (Nature 2001).
"""

import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path

from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.tag_tournament import (
    TagEvolutionaryTournament,
    TagTournament,
)
from the_dilemma_experiment.strategies.tag_based import (
    FalseBeardStrategy,
    StrictTribalStrategy,
)


@dataclass(frozen=True)
class ExperimentSummary:
    name: str
    description: str
    overall_cooperation_rate: float
    in_group_cooperation_rate: float
    out_group_cooperation_rate: float
    tag_shannon_diversity: float
    total_matches: int
    leaderboard: list[dict]


def run_categorical_tribalism(seed: int = 42) -> ExperimentSummary:
    """Experiment A: Categorical tribalism with 4 distinct tribes (Red, Blue, Green, Gold)."""
    tribes = ["RED", "BLUE", "GREEN", "GOLD"]
    agents = []
    for t in tribes:
        for i in range(5):
            agents.append(
                Agent(f"{t.capitalize()}_{i:02d}", StrictTribalStrategy(tag=t))
            )

    rng = random.Random(seed)
    tourney = TagTournament(agents=agents, rng=rng)
    res = tourney.run_stranger_pairings(pairings_per_agent=30, rounds_per_match=1)

    return ExperimentSummary(
        name="Experiment A: Categorical Tribalism & In-Group Favoritism",
        description="Four distinct tribes interact as strangers. Agents cooperate 100% within their tribe and defect 100% against all out-groups.",
        overall_cooperation_rate=res.overall_cooperation_rate,
        in_group_cooperation_rate=res.in_group_cooperation_rate,
        out_group_cooperation_rate=res.out_group_cooperation_rate,
        tag_shannon_diversity=res.tag_shannon_diversity,
        total_matches=res.total_matches,
        leaderboard=[
            {
                "rank": e.rank,
                "agent_id": e.agent_id,
                "tribe": str(e.tag),
                "total_score": e.total_score,
                "average_score": e.average_score,
                "in_group_matches": e.in_group_matches,
                "out_group_matches": e.out_group_matches,
            }
            for e in res.leaderboard
        ],
    )


def run_false_beard_invasion(seed: int = 42) -> ExperimentSummary:
    """Experiment B: The Green-Beard Dilemma & False-Beard Infiltration."""
    # 16 honest Green tribalists + 4 False-Beard defectors wearing Green
    agents = [
        Agent(f"HonestGreen_{i:02d}", StrictTribalStrategy(tag="GREEN"))
        for i in range(16)
    ] + [
        Agent(f"FalseBeard_{i:02d}", FalseBeardStrategy(tag="GREEN"))
        for i in range(4)
    ]

    rng = random.Random(seed)
    tourney = TagTournament(agents=agents, rng=rng)
    res = tourney.run_stranger_pairings(pairings_per_agent=40, rounds_per_match=1)

    return ExperimentSummary(
        name="Experiment B: The Green-Beard Dilemma & False-Beard Invasion",
        description="Cheaters displaying the in-group green tag defect against all peers, extracting incoming altruism while contributing nothing.",
        overall_cooperation_rate=res.overall_cooperation_rate,
        in_group_cooperation_rate=res.in_group_cooperation_rate,
        out_group_cooperation_rate=res.out_group_cooperation_rate,
        tag_shannon_diversity=res.tag_shannon_diversity,
        total_matches=res.total_matches,
        leaderboard=[
            {
                "rank": e.rank,
                "agent_id": e.agent_id,
                "strategy": e.strategy_name,
                "tag": str(e.tag),
                "total_score": e.total_score,
                "average_score": e.average_score,
            }
            for e in res.leaderboard
        ],
    )


def run_riolo_evolutionary_dynamics(
    generations: int = 40,
    seed: int = 42,
) -> dict:
    """Experiment C: Replication of Riolo, Cohen & Axelrod (Nature 2001) evolutionary tag dynamics."""
    sim = TagEvolutionaryTournament(
        population_size=50,
        tag_mutation_rate=0.1,
        tag_mutation_std=0.05,
        tolerance_mutation_rate=0.1,
        tolerance_mutation_std=0.02,
        initial_tolerance=0.08,
        torus=True,
        rng=random.Random(seed),
    )

    history = sim.run_simulation(
        generations=generations,
        pairings_per_agent=10,
    )

    return {
        "generations": [
            {
                "generation": m.generation,
                "cooperation_rate": round(m.cooperation_rate, 4),
                "mean_tag": m.mean_tag,
                "mean_tolerance": m.mean_tolerance,
                "tag_diversity": m.tag_diversity,
                "top_score": m.top_score,
            }
            for m in history
        ]
    }


def main() -> None:
    print("=" * 70)
    print("THE DILEMMA EXPERIMENT — EPISODE 7 BENCHMARK SUITE")
    print("TAGS, TRIBALISM & IN-GROUP FAVORITISM")
    print("=" * 70)

    print("\n[1/3] Running Experiment A: Categorical Tribalism (4 Tribes)...")
    exp_a = run_categorical_tribalism()
    print(f"  -> Total Matches: {exp_a.total_matches}")
    print(f"  -> Overall Cooperation Rate: {exp_a.overall_cooperation_rate * 100:.1f}%")
    print(f"  -> In-Group Cooperation Rate: {exp_a.in_group_cooperation_rate * 100:.1f}%")
    print(f"  -> Out-Group Cooperation Rate: {exp_a.out_group_cooperation_rate * 100:.1f}%")
    print(f"  -> Tag Shannon Diversity: {exp_a.tag_shannon_diversity:.4f}")

    print("\n[2/3] Running Experiment B: The False-Beard Invasion...")
    exp_b = run_false_beard_invasion()
    print(f"  -> Total Matches: {exp_b.total_matches}")
    print("  -> Top 4 Agents:")
    for entry in exp_b.leaderboard[:4]:
        print(f"     Rank {entry['rank']}: {entry['agent_id']} ({entry['strategy']}) - Score: {entry['total_score']}")

    print("\n[3/3] Running Experiment C: Riolo Evolutionary Dynamics (40 Gens)...")
    exp_c = run_riolo_evolutionary_dynamics(generations=40)
    final_gen = exp_c["generations"][-1]
    print("  -> Completed 40 generations of tag and tolerance evolution.")
    print(f"  -> Final Gen Coop Rate: {final_gen['cooperation_rate'] * 100:.1f}%")
    print(f"  -> Final Mean Tolerance: {final_gen['mean_tolerance']:.4f}")
    print(f"  -> Final Tag Diversity: {final_gen['tag_diversity']:.4f}")

    # Save benchmark results
    out_dir = Path(__file__).resolve().parent
    out_file = out_dir / "experiment_results.json"
    results = {
        "episode": 7,
        "title": "Tags, Tribalism & In-Group Favoritism",
        "experiment_a": asdict(exp_a),
        "experiment_b": asdict(exp_b),
        "experiment_c": exp_c,
    }
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n[OK] Benchmark completed successfully. Saved results to {out_file}")


if __name__ == "__main__":
    main()
