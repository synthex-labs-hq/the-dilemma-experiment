#!/usr/bin/env python3
"""Episode 6 Benchmark: Indirect Reciprocity, Reputation Ledgers, and Gossip Noise.

Executes three scientific experiments:
1. The Stranger Trap: Complete privacy (p=0.0) where strangers cannot build reputation.
2. First-Order Image Scoring & The Enforcer's Dilemma: Nowak-Sigmund score ledger and friendly-fire.
3. Second-Order Stern Judging, Hypocrite Infiltration, and Gossip Channel Noise.
"""

import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path

from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.reputation import (
    GossipChannel,
    ReputationRegistry,
)
from the_dilemma_experiment.domain.reputation_tournament import (
    ReputationTournament,
)
from the_dilemma_experiment.strategies.always_cooperate import (
    AlwaysCooperateStrategy,
)
from the_dilemma_experiment.strategies.always_defect import (
    AlwaysDefectStrategy,
)
from the_dilemma_experiment.strategies.hypocrite import HypocriteStrategy
from the_dilemma_experiment.strategies.image_scorer import ImageScorerStrategy
from the_dilemma_experiment.strategies.stern_judger import SternJudgingStrategy


@dataclass(frozen=True)
class ExperimentSummary:
    name: str
    description: str
    cooperation_rate: float
    total_matches: int
    public_matches: int
    leaderboard: list[dict]


def run_stranger_trap(seed: int = 42) -> ExperimentSummary:
    """Experiment A: Stranger Trap without reputation ledger (Total Privacy p=0.0)."""
    agents = [
        Agent(f"Altruist_{i:02d}", AlwaysCooperateStrategy()) for i in range(10)
    ] + [
        Agent(f"Predator_{i:02d}", AlwaysDefectStrategy()) for i in range(10)
    ]

    rng = random.Random(seed)
    tourney = ReputationTournament(agents=agents, public_probability=0.0, rng=rng)
    result = tourney.run_stranger_rounds(pairings_per_agent=40, rounds_per_match=1)

    return ExperimentSummary(
        name="Experiment A: The Stranger Trap (Zero Reputation)",
        description="Under zero transparency (p=0.0), strangers cannot assess past deeds. Predators mercilessly exploit unconditional cooperators.",
        cooperation_rate=result.cooperation_rate,
        total_matches=result.total_matches,
        public_matches=result.public_matches,
        leaderboard=[
            {
                "rank": e.rank,
                "agent_id": e.agent_id,
                "strategy": e.strategy_name,
                "total_score": e.total_score,
                "average_score": e.average_score,
                "final_image_score": e.final_image_score,
                "final_standing": e.final_standing.value,
            }
            for e in result.leaderboard
        ],
    )


def run_image_scoring_enforcer_dilemma(seed: int = 42) -> ExperimentSummary:
    """Experiment B: First-Order Image Scoring and the Enforcer's Dilemma."""
    agents = [
        Agent(f"Scorer_{i:02d}", ImageScorerStrategy(threshold=0)) for i in range(14)
    ] + [
        Agent(f"Predator_{i:02d}", AlwaysDefectStrategy()) for i in range(6)
    ]

    rng = random.Random(seed)
    tourney = ReputationTournament(agents=agents, public_probability=1.0, rng=rng)
    result = tourney.run_stranger_rounds(pairings_per_agent=40, rounds_per_match=1)

    return ExperimentSummary(
        name="Experiment B: First-Order Image Scoring & The Enforcer's Dilemma",
        description="Public image scores isolate predators, but punishing defectors penalizes the punisher (-1 score), triggering friendly-fire among honest scorers.",
        cooperation_rate=result.cooperation_rate,
        total_matches=result.total_matches,
        public_matches=result.public_matches,
        leaderboard=[
            {
                "rank": e.rank,
                "agent_id": e.agent_id,
                "strategy": e.strategy_name,
                "total_score": e.total_score,
                "average_score": e.average_score,
                "final_image_score": e.final_image_score,
                "final_standing": e.final_standing.value,
            }
            for e in result.leaderboard
        ],
    )


def run_stern_judging_and_hypocrites(seed: int = 42) -> dict[str, list[dict]]:
    """Experiment C: Second-Order Stern Judging vs Hypocrites across visibility levels and gossip noise."""
    visibility_levels = [0.0, 0.25, 0.50, 0.75, 1.0]
    gossip_error_rates = [0.0, 0.05, 0.15, 0.25]

    results_matrix: list[dict] = []

    for p in visibility_levels:
        for err in gossip_error_rates:
            agents = (
                [Agent(f"Stern_{i:02d}", SternJudgingStrategy()) for i in range(10)]
                + [Agent(f"Hypocrite_{i:02d}", HypocriteStrategy()) for i in range(5)]
                + [Agent(f"Predator_{i:02d}", AlwaysDefectStrategy()) for i in range(5)]
            )
            reg = ReputationRegistry(min_score=-10, max_score=10)
            gossip = GossipChannel(registry=reg, error_rate=err, rng=random.Random(seed + 111))
            tourney = ReputationTournament(
                agents=agents,
                registry=reg,
                gossip_channel=gossip,
                public_probability=p,
                rng=random.Random(seed + 222),
            )
            res = tourney.run_stranger_rounds(pairings_per_agent=30, rounds_per_match=1)

            stern_avg = (
                sum(e.total_score for e in res.leaderboard if "Stern" in e.agent_id) / 10
            )
            hypo_avg = (
                sum(e.total_score for e in res.leaderboard if "Hypocrite" in e.agent_id) / 5
            )
            pred_avg = (
                sum(e.total_score for e in res.leaderboard if "Predator" in e.agent_id) / 5
            )

            results_matrix.append(
                {
                    "public_probability": p,
                    "gossip_error_rate": err,
                    "cooperation_rate": res.cooperation_rate,
                    "stern_average_score": round(stern_avg, 2),
                    "hypocrite_average_score": round(hypo_avg, 2),
                    "predator_average_score": round(pred_avg, 2),
                }
            )

    return {"matrix": results_matrix}


def main() -> None:
    print("=" * 70)
    print("THE DILEMMA EXPERIMENT — EPISODE 6 BENCHMARK SUITE")
    print("INDIRECT RECIPROCITY, REPUTATION LEDGERS & GOSSIP NOISE")
    print("=" * 70)

    print("\n[1/3] Running Experiment A: The Stranger Trap (p=0.0)...")
    exp_a = run_stranger_trap()
    print(f"  -> Total Matches: {exp_a.total_matches}")
    print(f"  -> System Cooperation Rate: {exp_a.cooperation_rate * 100:.1f}%")
    print("  -> Top 3 Agents:")
    for entry in exp_a.leaderboard[:3]:
        print(f"     Rank {entry['rank']}: {entry['agent_id']} ({entry['strategy']}) - Score: {entry['total_score']}")

    print("\n[2/3] Running Experiment B: First-Order Image Scoring & The Enforcer's Dilemma (p=1.0)...")
    exp_b = run_image_scoring_enforcer_dilemma()
    print(f"  -> Total Matches: {exp_b.total_matches}")
    print(f"  -> System Cooperation Rate: {exp_b.cooperation_rate * 100:.1f}%")
    print("  -> Top 3 Agents:")
    for entry in exp_b.leaderboard[:3]:
        print(f"     Rank {entry['rank']}: {entry['agent_id']} ({entry['strategy']}) - Score: {entry['total_score']} [Image: {entry['final_image_score']}]")

    print("\n[3/3] Running Experiment C: Stern Judging vs Hypocrites across Visibility & Gossip Noise...")
    exp_c = run_stern_judging_and_hypocrites()
    print(f"  -> Simulated {len(exp_c['matrix'])} parametric configurations.")

    # Save benchmark results
    out_dir = Path(__file__).resolve().parent
    out_file = out_dir / "experiment_results.json"
    results = {
        "episode": 6,
        "title": "Indirect Reciprocity, Reputation & Gossip",
        "experiment_a": asdict(exp_a),
        "experiment_b": asdict(exp_b),
        "experiment_c": exp_c,
    }
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n[OK] Benchmark completed successfully. Saved results to {out_file}")


if __name__ == "__main__":
    main()
