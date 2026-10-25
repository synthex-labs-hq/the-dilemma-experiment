"""Zero-mock unit tests for CommonsTournament engine (ADR-025, ADR-026)."""

import pytest

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


def test_commons_tournament_validation() -> None:
    """Tournament requires at least 2 agents."""
    with pytest.raises(ValueError, match="at least 2 agents"):
        CommonsTournament(agents=[Agent("single", SustainableHarvesterStrategy())])


def test_unregulated_tragedy_of_the_commons() -> None:
    """Without sanctions, greedy over-harvesters completely deplete the common pool."""
    # 5 over-harvesters extract 15 each per round from 50 capacity pool
    agents = [
        Agent(f"greedy_{i}", OverHarvesterStrategy(max_extract=15.0))
        for i in range(5)
    ]
    cpr = CommonPoolResource(capacity=50.0, stock=50.0, regeneration_rate=0.10)
    pgg = PublicGoodsPool(endowment=10.0, multiplier=1.6)

    tourney = CommonsTournament(
        agents=agents,
        resource=cpr,
        public_goods=pgg,
        sanctions_enabled=False,
    )
    res = tourney.run_rounds(rounds=5)

    # Commons must be depleted
    assert res.is_depleted is True
    assert res.final_stock == 0.0
    # Over-harvesters contributed 0% to public goods
    assert res.overall_contribution_rate == 0.0


def test_ostrom_sanctions_suppress_free_riders() -> None:
    """With Ostrom sanctions active, punishers heavily fine free-riders."""
    agents = [
        Agent(f"sanctioner_{i}", OstromSanctionerStrategy(fine_amount=6.0))
        for i in range(4)
    ] + [
        Agent("free_rider", OverHarvesterStrategy())
    ]
    cpr = CommonPoolResource(capacity=100.0, stock=100.0, regeneration_rate=0.20)
    pgg = PublicGoodsPool(endowment=10.0, multiplier=1.6)

    tourney = CommonsTournament(
        agents=agents,
        resource=cpr,
        public_goods=pgg,
        sanctions_enabled=True,
    )
    res = tourney.run_rounds(rounds=10)

    # Sanctions were applied against the free-rider
    assert res.total_sanctions > 0
    assert res.total_fines_imposed > 0.0

    # The free-rider's score must be crushed by cumulative fines
    freerider_entry = next(e for e in res.leaderboard if e.agent_id == "free_rider")
    sanctioner_entries = [e for e in res.leaderboard if "sanctioner" in e.agent_id]
    assert freerider_entry.fines_received > 0.0
    assert freerider_entry.total_score < sanctioner_entries[0].total_score


def test_second_order_free_riding_advantage() -> None:
    """Second-order free-riders (who cooperate but do not sanction) out-score altruistic punishers when free-riders exist."""
    agents = [
        Agent("punisher", OstromSanctionerStrategy(fine_amount=3.0)),
        Agent("bystander", SecondOrderFreeRiderStrategy()),
        Agent("crook", OverHarvesterStrategy(max_extract=4.0)),
    ]
    cpr = CommonPoolResource(capacity=100.0, stock=100.0, regeneration_rate=0.20)
    pgg = PublicGoodsPool(endowment=10.0, multiplier=1.6)

    tourney = CommonsTournament(
        agents=agents,
        resource=cpr,
        public_goods=pgg,
        sanctions_enabled=True,
    )
    res = tourney.run_rounds(rounds=8)

    punisher = next(e for e in res.leaderboard if e.agent_id == "punisher")
    bystander = next(e for e in res.leaderboard if e.agent_id == "bystander")

    # Punisher incurred costs to enforce order; bystander paid 0 enforcement cost
    assert punisher.costs_paid > 0.0
    assert bystander.costs_paid == 0.0
    assert bystander.total_score > punisher.total_score
