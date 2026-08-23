from dataclasses import FrozenInstanceError

import pytest

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.strategy import Strategy


class DummyCooperateStrategy(Strategy):
    """Simple test strategy that always cooperates."""

    def choose_action(self, context: DecisionContext) -> Action:
        return Action.COOPERATE


class StatefulTestStrategy(Strategy):
    """Test strategy with instance-specific opponent memory."""

    def __init__(self) -> None:
        self.history: list[tuple[str, Action]] = []

    def choose_action(self, context: DecisionContext) -> Action:
        return Action.COOPERATE

    def observe(self, opponent_id: str, action: Action) -> None:
        self.history.append((opponent_id, action))


def test_action_values():
    """Verify Action exposes exactly COOPERATE and DEFECT values."""
    assert set(Action) == {Action.COOPERATE, Action.DEFECT}
    assert Action.COOPERATE.value == "COOPERATE"
    assert Action.DEFECT.value == "DEFECT"
    assert len(Action) == 2


def test_decision_context_stores_opponent_id():
    """Verify DecisionContext stores the opponent ID and is immutable."""
    context = DecisionContext(opponent_id="agent_42")
    assert context.opponent_id == "agent_42"
    with pytest.raises(FrozenInstanceError):
        context.opponent_id = "agent_99"  # type: ignore[misc]


def test_concrete_dummy_strategy_implements_contract():
    """Verify a concrete dummy strategy implements the Strategy contract."""
    strategy = DummyCooperateStrategy()
    context = DecisionContext(opponent_id="opponent_1")
    assert strategy.choose_action(context) == Action.COOPERATE

    # Verify base observe method can be called without error
    strategy.observe("opponent_1", Action.DEFECT)


def test_agent_stores_supplied_id():
    """Verify Agent stores its supplied ID."""
    strategy = DummyCooperateStrategy()
    agent = Agent(id="agent_100", strategy=strategy)
    assert agent.id == "agent_100"


def test_agent_owns_exact_strategy_instance():
    """Verify Agent owns the exact Strategy instance supplied to it."""
    strategy = DummyCooperateStrategy()
    agent = Agent(id="agent_1", strategy=strategy)
    assert agent.strategy is strategy


def test_multiple_agents_separate_strategy_instances():
    """Verify multiple agents can own separate strategy instances without state sharing."""
    strat_1 = StatefulTestStrategy()
    strat_2 = StatefulTestStrategy()
    agent_1 = Agent(id="agent_1", strategy=strat_1)
    agent_2 = Agent(id="agent_2", strategy=strat_2)

    assert agent_1.strategy is not agent_2.strategy

    agent_1.strategy.observe("opponent_x", Action.DEFECT)

    assert strat_1.history == [("opponent_x", Action.DEFECT)]
    assert strat_2.history == []


def test_strategy_state_not_stored_globally_or_on_agent():
    """Verify strategy state remains isolated on Strategy instance, not on Agent or global."""
    strat = StatefulTestStrategy()
    agent = Agent(id="agent_1", strategy=strat)

    agent.strategy.observe("opponent_y", Action.COOPERATE)

    # State is encapsulated within the strategy instance
    assert strat.history == [("opponent_y", Action.COOPERATE)]
    # Agent object does not hold strategy history attributes
    assert not hasattr(agent, "history")
