#!/usr/bin/env python3
"""Episode 8 Benchmark: The Tragedy of the Commons & Sanctions.

Executes three scientific experiments:
1. The Unregulated Tragedy: Hardin's classic commons collapse without monitoring or fines.
2. Costly Peer Punishment & The Second-Order Free-Rider Problem (Fehr & Gächter 2000).
3. Ostrom's Polycentric Governance: Sustaining common pools with monitoring and sanctions.
"""

import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path

from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.commons import (
    CommonPoolResource,
    PublicGoodsPool,
)
from the_dilemma_experiment.domain.commons_tournament import CommonsTournament
from the_dilemma_experiment.strategies.commons_strategies import (
    OstromSanctionerStrategy,
    OverHarvesterStrategy,
    SecondOrderFreeRiderStrategy,
    SustainableHarvesterStrategy,
)


@dataclass(frozen=True)
class ExperimentSummary:
    name: str
    description: str
    is_depleted: bool
    final_stock: float
    overall_contribution_rate: float
    total_sanctions: int
    total_fines_imposed: float
    total_sanction_costs: float
    leaderboard: list[dict]


def run_unregulated_commons(seed: int = 42) -> ExperimentSummary:
    """Experiment A: Unregulated extraction and public goods without sanctions."""
    agents = [
        Agent(f"Greedy_{i:02d}", OverHarvesterStrategy(max_extract=12.0))
        for i in range(8)
    ] + [
        Agent(f"Sustain_{i:02d}", SustainableHarvesterStrategy(harvest_quota=1.0))
        for i in range(8)
    ]

    cpr = CommonPoolResource(capacity=100.0, stock=100.0, regeneration_rate=0.15)
    pgg = PublicGoodsPool(endowment=10.0, multiplier=1.6)

    tourney = CommonsTournament(
        agents=agents,
        resource=cpr,
        public_goods=pgg,
        sanctions_enabled=False,
        rng=random.Random(seed),
    )
    res = tourney.run_rounds(rounds=15)

    return ExperimentSummary(
        name="Experiment A: The Unregulated Tragedy of the Commons",
        description="Without monitoring or punishment, greedy over-harvesters deplete the reservoir to zero within 2 rounds, causing catastrophic collapse.",
        is_depleted=res.is_depleted,
        final_stock=res.final_stock,
        overall_contribution_rate=res.overall_contribution_rate,
        total_sanctions=res.total_sanctions,
        total_fines_imposed=res.total_fines_imposed,
        total_sanction_costs=res.total_sanction_costs,
        leaderboard=[
            {
                "rank": e.rank,
                "agent_id": e.agent_id,
                "strategy": e.strategy_name,
                "total_score": e.total_score,
                "average_score": e.average_score,
                "total_contribution": e.total_contribution,
            }
            for e in res.leaderboard
        ],
    )


def run_second_order_free_riding(seed: int = 42) -> ExperimentSummary:
    """Experiment B: Costly peer punishment and the second-order free-rider problem."""
    # 6 Altruistic Punishers + 6 Second-Order Free-Riders (Bystanders) + 4 Greedy Defectors
    agents = (
        [
            Agent(
                f"Punisher_{i:02d}",
                OstromSanctionerStrategy(harvest_quota=1.0, fine_amount=4.0),
            )
            for i in range(6)
        ]
        + [
            Agent(
                f"Bystander_{i:02d}",
                SecondOrderFreeRiderStrategy(harvest_quota=1.0),
            )
            for i in range(6)
        ]
        + [
            Agent(
                f"Greedy_{i:02d}",
                OverHarvesterStrategy(max_extract=3.0),
            )
            for i in range(4)
        ]
    )

    cpr = CommonPoolResource(capacity=150.0, stock=150.0, regeneration_rate=0.20)
    pgg = PublicGoodsPool(endowment=10.0, multiplier=1.6)

    tourney = CommonsTournament(
        agents=agents,
        resource=cpr,
        public_goods=pgg,
        sanctions_enabled=True,
        graduated_sanctions=False,
        rng=random.Random(seed),
    )
    res = tourney.run_rounds(rounds=12)

    return ExperimentSummary(
        name="Experiment B: Costly Punishment & The Second-Order Free-Rider Dilemma",
        description="Altruistic punishers bear the cost of fining free-riders, allowing silent bystanders to harvest the benefits of order without paying enforcement costs.",
        is_depleted=res.is_depleted,
        final_stock=res.final_stock,
        overall_contribution_rate=res.overall_contribution_rate,
        total_sanctions=res.total_sanctions,
        total_fines_imposed=res.total_fines_imposed,
        total_sanction_costs=res.total_sanction_costs,
        leaderboard=[
            {
                "rank": e.rank,
                "agent_id": e.agent_id,
                "strategy": e.strategy_name,
                "total_score": e.total_score,
                "average_score": e.average_score,
                "sanctions_inflicted": e.sanctions_inflicted,
                "costs_paid": e.costs_paid,
                "fines_received": e.fines_received,
            }
            for e in res.leaderboard
        ],
    )


def run_ostrom_governance_comparison(seed: int = 42) -> dict:
    """Experiment C: Comparison of Unregulated Anarchy vs Ostrom Polycentric Governance."""
    regimes = [
        ("Unregulated Anarchy", False),
        ("Ostrom Sanctioned", True),
    ]

    results = []
    for name, sanctions_on in regimes:
        agents = (
            [
                Agent(
                    f"Sustain_{i:02d}",
                    OstromSanctionerStrategy(harvest_quota=1.0, fine_amount=4.0)
                    if sanctions_on
                    else SustainableHarvesterStrategy(harvest_quota=1.0),
                )
                for i in range(14)
            ]
            + [
                Agent(f"Greedy_{i:02d}", OverHarvesterStrategy(max_extract=4.0))
                for i in range(4)
            ]
        )
        cpr = CommonPoolResource(capacity=200.0, stock=200.0, regeneration_rate=0.20)
        pgg = PublicGoodsPool(endowment=10.0, multiplier=1.6)

        tourney = CommonsTournament(
            agents=agents,
            resource=cpr,
            public_goods=pgg,
            sanctions_enabled=sanctions_on,
            rng=random.Random(seed),
        )
        res = tourney.run_rounds(rounds=15)

        total_welfare = sum(e.total_score for e in res.leaderboard)
        results.append(
            {
                "regime": name,
                "final_stock": res.final_stock,
                "is_depleted": res.is_depleted,
                "overall_cooperation": res.overall_contribution_rate,
                "total_welfare": round(total_welfare, 2),
                "total_sanctions": res.total_sanctions,
                "total_fines": res.total_fines_imposed,
            }
        )

    return {"regimes": results}


def main() -> None:
    print("=" * 70)
    print("THE DILEMMA EXPERIMENT — EPISODE 8 BENCHMARK SUITE")
    print("THE TRAGEDY OF THE COMMONS & SANCTIONS")
    print("=" * 70)

    print("\n[1/3] Running Experiment A: The Unregulated Tragedy of the Commons...")
    exp_a = run_unregulated_commons()
    print(f"  -> Depleted: {exp_a.is_depleted} (Final Stock: {exp_a.final_stock})")
    print(f"  -> Overall Contribution Rate: {exp_a.overall_contribution_rate * 100:.1f}%")
    print("  -> Top 3 Agents:")
    for entry in exp_a.leaderboard[:3]:
        print(f"     Rank {entry['rank']}: {entry['agent_id']} ({entry['strategy']}) - Score: {entry['total_score']}")

    print("\n[2/3] Running Experiment B: Costly Punishment & 2nd-Order Free-Riding...")
    exp_b = run_second_order_free_riding()
    print(f"  -> Total Sanctions: {exp_b.total_sanctions} (Fines: {exp_b.total_fines_imposed}, Costs: {exp_b.total_sanction_costs})")
    print("  -> Top 3 Agents:")
    for entry in exp_b.leaderboard[:3]:
        print(f"     Rank {entry['rank']}: {entry['agent_id']} ({entry['strategy']}) - Score: {entry['total_score']} (Costs Paid: {entry['costs_paid']})")

    print("\n[3/3] Running Experiment C: Ostrom Governance Regimes Comparison...")
    exp_c = run_ostrom_governance_comparison()
    for reg in exp_c["regimes"]:
        print(f"  -> Regime: {reg['regime']:<22} | Final Stock: {reg['final_stock']:>5.1f} | Coop: {reg['overall_cooperation'] * 100:>5.1f}% | Welfare: {reg['total_welfare']}")

    # Save benchmark results
    out_dir = Path(__file__).resolve().parent
    out_file = out_dir / "experiment_results.json"
    results = {
        "episode": 8,
        "title": "The Tragedy of the Commons & Sanctions",
        "experiment_a": asdict(exp_a),
        "experiment_b": asdict(exp_b),
        "experiment_c": exp_c,
    }
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n[OK] Benchmark completed successfully. Saved results to {out_file}")


if __name__ == "__main__":
    main()
