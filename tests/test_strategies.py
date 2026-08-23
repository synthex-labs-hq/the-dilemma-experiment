from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.strategy import Strategy
from the_dilemma_experiment.strategies.always_cooperate import (
    AlwaysCooperateStrategy,
)


def test_always_cooperate_is_concrete_strategy():
    """Verify AlwaysCooperateStrategy inherits from Strategy and can be instantiated."""
    assert issubclass(AlwaysCooperateStrategy, Strategy)
    strategy = AlwaysCooperateStrategy()
    assert isinstance(strategy, Strategy)


def test_always_cooperate_choose_action_returns_cooperate():
    """Verify choose_action returns Action.COOPERATE."""
    strategy = AlwaysCooperateStrategy()
    context = DecisionContext(opponent_id="agent_2")
    assert strategy.choose_action(context) == Action.COOPERATE


def test_always_cooperate_returns_cooperate_for_multiple_contexts():
    """Verify choose_action remains Action.COOPERATE across varied decision contexts."""
    strategy = AlwaysCooperateStrategy()
    contexts = [
        DecisionContext(opponent_id="agent_1"),
        DecisionContext(opponent_id="agent_99"),
        DecisionContext(opponent_id="opponent_xyz"),
    ]

    for ctx in contexts:
        assert strategy.choose_action(ctx) == Action.COOPERATE


def test_always_cooperate_observe_does_not_raise():
    """Verify calling observe() on AlwaysCooperateStrategy executes without exception."""
    strategy = AlwaysCooperateStrategy()
    strategy.observe("agent_2", Action.COOPERATE)
    strategy.observe("agent_2", Action.DEFECT)
    strategy.observe("agent_3", Action.DEFECT)


def test_always_cooperate_has_no_unnecessary_mutable_state():
    """Verify AlwaysCooperateStrategy maintains no instance attributes or mutable state."""
    strategy = AlwaysCooperateStrategy()
    # Check that instance has no instance dictionary or state attributes
    assert not hasattr(strategy, "__dict__") or len(strategy.__dict__) == 0

    # Execute choose_action and observe multiple times
    context = DecisionContext(opponent_id="agent_2")
    strategy.choose_action(context)
    strategy.observe("agent_2", Action.DEFECT)

    # State must remain empty
    assert not hasattr(strategy, "__dict__") or len(strategy.__dict__) == 0
