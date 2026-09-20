#!/usr/bin/env python3
"""Simulation Experiment Runner for Episode 2: The Tournament.

Executes reproducible multi-agent tournaments across distinct population mixes,
analyzing leaderboard standings, cooperation rates, and pairwise payoff matrices.
Outputs results to JSON and prints formatted analytical tables.
"""

import json
from pathlib import Path

from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.population import Population
from the_dilemma_experiment.domain.prisoners_dilemma import PrisonersDilemma
from the_dilemma_experiment.domain.tournament import Tournament
from the_dilemma_experiment.strategies.always_cooperate import (
    AlwaysCooperateStrategy,
)
from the_dilemma_experiment.strategies.always_defect import (
    AlwaysDefectStrategy,
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


def run_archetype_tournament(rounds_per_match: int = 50, seed: int = 42) -> dict:
    """Run classic round-robin among the 5 core behavioral archetypes."""
    game = PrisonersDilemma()

    agents = [
        Agent("AlwaysCooperate", AlwaysCooperateStrategy()),
        Agent("AlwaysDefect", AlwaysDefectStrategy()),
        Agent("TitForTat", TitForTatStrategy()),
        Agent("GrimTrigger", GrimTriggerStrategy()),
        Agent("Random", RandomStrategy(seed=seed, cooperation_probability=0.5)),
    ]

    population = Population(agents)
    tournament = Tournament(population, game, rounds_per_match=rounds_per_match)
    result = tournament.execute()

    leaderboard_data = []
    for entry in result.leaderboard:
        leaderboard_data.append({
            "rank": entry.rank,
            "agent_id": entry.agent_id,
            "strategy": entry.strategy_name,
            "total_score": entry.total_score,
            "avg_score_per_round": entry.average_score_per_round,
            "wins": entry.wins,
            "ties": entry.ties,
            "losses": entry.losses,
            "cooperations": entry.cooperations,
            "defections": entry.defections,
            "cooperation_rate": entry.cooperation_rate,
        })

    # Build pairwise matrix
    pairwise: dict[str, dict[str, int]] = {a.id: {} for a in agents}
    for m in tournament.matches:
        res = m.result
        if res:
            pairwise[res.first_agent_id][res.second_agent_id] = res.first_score
            pairwise[res.second_agent_id][res.first_agent_id] = res.second_score

    return {
        "experiment_name": "5_archetype_round_robin",
        "rounds_per_match": rounds_per_match,
        "total_matches": result.total_matches,
        "total_rounds": result.total_rounds,
        "population_cooperation_rate": result.population_cooperation_rate,
        "leaderboard": leaderboard_data,
        "pairwise_scores": pairwise,
    }


def run_balanced_population_tournament(rounds_per_match: int = 50, seed: int = 42) -> dict:
    """Run tournament with a balanced society (3 TFT, 2 Grim, 2 Defect, 2 Coop, 1 Random)."""
    game = PrisonersDilemma()

    agents = [
        Agent("TFT_Alpha", TitForTatStrategy()),
        Agent("TFT_Beta", TitForTatStrategy()),
        Agent("TFT_Gamma", TitForTatStrategy()),
        Agent("Grim_1", GrimTriggerStrategy()),
        Agent("Grim_2", GrimTriggerStrategy()),
        Agent("Defect_1", AlwaysDefectStrategy()),
        Agent("Defect_2", AlwaysDefectStrategy()),
        Agent("Coop_1", AlwaysCooperateStrategy()),
        Agent("Coop_2", AlwaysCooperateStrategy()),
        Agent("Random_1", RandomStrategy(seed=seed)),
    ]

    population = Population(agents)
    tournament = Tournament(population, game, rounds_per_match=rounds_per_match)
    result = tournament.execute()

    leaderboard_data = []
    for entry in result.leaderboard:
        leaderboard_data.append({
            "rank": entry.rank,
            "agent_id": entry.agent_id,
            "strategy": entry.strategy_name,
            "total_score": entry.total_score,
            "avg_score_per_round": entry.average_score_per_round,
            "wins": entry.wins,
            "ties": entry.ties,
            "losses": entry.losses,
            "cooperations": entry.cooperations,
            "defections": entry.defections,
            "cooperation_rate": entry.cooperation_rate,
        })

    return {
        "experiment_name": "10_agent_society",
        "rounds_per_match": rounds_per_match,
        "total_matches": result.total_matches,
        "total_rounds": result.total_rounds,
        "population_cooperation_rate": result.population_cooperation_rate,
        "leaderboard": leaderboard_data,
    }


def main():
    print("Running Experiment 1: The 5 Archetypes...")
    exp1 = run_archetype_tournament(rounds_per_match=50, seed=42)

    print("Running Experiment 2: 10-Agent Heterogeneous Society...")
    exp2 = run_balanced_population_tournament(rounds_per_match=50, seed=42)

    out_dir = Path(__file__).parent
    results_path = out_dir / "experiment_results.json"
    data = {
        "experiment_1": exp1,
        "experiment_2": exp2,
    }

    with open(results_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\nResults successfully written to {results_path}")
    print("\n" + "=" * 80)
    print("EXPERIMENT 1 LEADERBOARD (5 Archetypes, 50 rounds/match):")
    print("=" * 80)
    print(f"{'RANK':<5} | {'AGENT':<16} | {'SCORE':<7} | {'AVG/RND':<8} | {'W-T-L':<9} | {'COOP %':<7}")
    print("-" * 80)
    for row in exp1["leaderboard"]:
        wtl = f"{row['wins']}-{row['ties']}-{row['losses']}"
        print(f"#{row['rank']:<4} | {row['agent_id']:<16} | {row['total_score']:<7} | {row['avg_score_per_round']:<8.2f} | {wtl:<9} | {row['cooperation_rate']*100:<6.1f}%")

    print("\n" + "=" * 80)
    print("EXPERIMENT 2 LEADERBOARD (10-Agent Society, 50 rounds/match):")
    print("=" * 80)
    print(f"{'RANK':<5} | {'AGENT':<16} | {'SCORE':<7} | {'AVG/RND':<8} | {'W-T-L':<9} | {'COOP %':<7}")
    print("-" * 80)
    for row in exp2["leaderboard"]:
        wtl = f"{row['wins']}-{row['ties']}-{row['losses']}"
        print(f"#{row['rank']:<4} | {row['agent_id']:<16} | {row['total_score']:<7} | {row['avg_score_per_round']:<8.2f} | {wtl:<9} | {row['cooperation_rate']*100:<6.1f}%")


if __name__ == "__main__":
    main()
