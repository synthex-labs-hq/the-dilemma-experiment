"""Zero-mock unit tests for commons and public goods strategies (ADR-025, ADR-026)."""

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.strategies.commons_strategies import (
    AntisocialPunisherStrategy,
    OstromSanctionerStrategy,
    OverHarvesterStrategy,
    SecondOrderFreeRiderStrategy,
    SustainableHarvesterStrategy,
)


def test_sustainable_harvester_strategy() -> None:
    """SustainableHarvester extracts within fair share and fully contributes to public goods."""
    strat = SustainableHarvesterStrategy(harvest_quota=4.0, contribution_ratio=1.0)

    # 100 stock / 10 agents = 10 fair share -> capped by quota of 4.0
    assert strat.decide_harvest(stock=100.0, capacity=100.0, group_size=10) == 4.0
    # 20 stock / 10 agents = 2.0 fair share -> limited by stock share
    assert strat.decide_harvest(stock=20.0, capacity=100.0, group_size=10) == 2.0
    # Full contribution
    assert strat.decide_contribution(endowment=10.0) == 10.0
    assert strat.choose_action(DecisionContext("peer")) == Action.COOPERATE


def test_over_harvester_strategy() -> None:
    """OverHarvester extracts maximum possible quota and contributes nothing."""
    strat = OverHarvesterStrategy(max_extract=12.0)
    assert strat.decide_harvest(stock=100.0, capacity=100.0, group_size=10) == 12.0
    assert strat.decide_contribution(endowment=10.0) == 0.0
    assert strat.choose_action(DecisionContext("peer")) == Action.DEFECT


def test_ostrom_sanctioner_strategy() -> None:
    """OstromSanctioner fines free-riders while sparing compliant peers."""
    strat = OstromSanctionerStrategy(sanction_threshold=5.0)

    # Free-rider contributed 0 -> Sanction!
    assert strat.should_sanction(target_id="freerider", target_contribution=0.0) is True
    # Low contributor contributed 3.0 < 5.0 -> Sanction!
    assert strat.should_sanction(target_id="slacker", target_contribution=3.0) is True
    # Honest cooperator contributed 8.0 >= 5.0 -> Do NOT sanction
    assert strat.should_sanction(target_id="cooperator", target_contribution=8.0) is False


def test_second_order_free_rider_strategy() -> None:
    """SecondOrderFreeRider cooperates in extraction and public goods, but never sanctions."""
    strat = SecondOrderFreeRiderStrategy()
    assert strat.decide_contribution(endowment=10.0) == 10.0
    # Even if target contributed 0, silent bystander refuses to pay sanction cost
    assert strat.should_sanction(target_id="freerider", target_contribution=0.0) is False


def test_antisocial_punisher_strategy() -> None:
    """AntisocialPunisher spitefully punishes generous contributors."""
    strat = AntisocialPunisherStrategy()
    # Free-rider contributed 0 -> Do NOT sanction (fellow defector)
    assert strat.should_sanction(target_id="freerider", target_contribution=0.0) is False
    # Generous contributor contributed 10.0 >= 7.0 -> Spiteful sanction!
    assert strat.should_sanction(target_id="generous", target_contribution=10.0) is True
