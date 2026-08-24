from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.match import Match
from the_dilemma_experiment.domain.prisoners_dilemma import PrisonersDilemma
from the_dilemma_experiment.domain.strategy import Strategy
from the_dilemma_experiment.strategies.always_cooperate import (
    AlwaysCooperateStrategy,
)
from the_dilemma_experiment.strategies.always_defect import (
    AlwaysDefectStrategy,
)
from the_dilemma_experiment.strategies.tit_for_tat import TitForTatStrategy


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
    assert not hasattr(strategy, "__dict__") or len(strategy.__dict__) == 0

    context = DecisionContext(opponent_id="agent_2")
    strategy.choose_action(context)
    strategy.observe("agent_2", Action.DEFECT)

    assert not hasattr(strategy, "__dict__") or len(strategy.__dict__) == 0


def test_always_defect_is_concrete_strategy():
    """Verify AlwaysDefectStrategy inherits from Strategy and can be instantiated."""
    assert issubclass(AlwaysDefectStrategy, Strategy)
    strategy = AlwaysDefectStrategy()
    assert isinstance(strategy, Strategy)


def test_always_defect_choose_action_returns_defect():
    """Verify choose_action returns Action.DEFECT."""
    strategy = AlwaysDefectStrategy()
    context = DecisionContext(opponent_id="agent_2")
    assert strategy.choose_action(context) == Action.DEFECT


def test_always_defect_returns_defect_for_multiple_contexts():
    """Verify choose_action remains Action.DEFECT across varied decision contexts."""
    strategy = AlwaysDefectStrategy()
    contexts = [
        DecisionContext(opponent_id="agent_1"),
        DecisionContext(opponent_id="agent_99"),
        DecisionContext(opponent_id="opponent_xyz"),
    ]

    for ctx in contexts:
        assert strategy.choose_action(ctx) == Action.DEFECT


def test_always_defect_observe_does_not_raise():
    """Verify calling observe() on AlwaysDefectStrategy executes without exception."""
    strategy = AlwaysDefectStrategy()
    strategy.observe("agent_2", Action.COOPERATE)
    strategy.observe("agent_2", Action.DEFECT)
    strategy.observe("agent_3", Action.COOPERATE)


def test_always_defect_has_no_unnecessary_mutable_state():
    """Verify AlwaysDefectStrategy maintains no instance attributes or mutable state."""
    strategy = AlwaysDefectStrategy()
    assert not hasattr(strategy, "__dict__") or len(strategy.__dict__) == 0

    context = DecisionContext(opponent_id="agent_2")
    strategy.choose_action(context)
    strategy.observe("agent_2", Action.COOPERATE)

    assert not hasattr(strategy, "__dict__") or len(strategy.__dict__) == 0


def test_tit_for_tat_is_concrete_strategy():
    """Verify TitForTatStrategy inherits from Strategy."""
    strategy = TitForTatStrategy()

    assert isinstance(strategy, Strategy)


def test_tit_for_tat_cooperates_with_unknown_opponent():
    """Verify TitForTat cooperates when it has no previous observation."""
    strategy = TitForTatStrategy()
    context = DecisionContext(opponent_id="agent_2")

    assert strategy.choose_action(context) == Action.COOPERATE


def test_tit_for_tat_mirrors_opponents_last_action():
    """Verify TitForTat mirrors the opponent's most recently observed action."""
    strategy = TitForTatStrategy()
    context = DecisionContext(opponent_id="agent_2")

    strategy.observe("agent_2", Action.DEFECT)
    assert strategy.choose_action(context) == Action.DEFECT

    strategy.observe("agent_2", Action.COOPERATE)
    assert strategy.choose_action(context) == Action.COOPERATE


def test_tit_for_tat_tracks_opponents_independently():
    """Verify each opponent has independent last-action state."""
    strategy = TitForTatStrategy()

    strategy.observe("agent_2", Action.DEFECT)
    strategy.observe("agent_3", Action.COOPERATE)

    assert (
        strategy.choose_action(DecisionContext(opponent_id="agent_2")) == Action.DEFECT
    )

    assert (
        strategy.choose_action(DecisionContext(opponent_id="agent_3"))
        == Action.COOPERATE
    )


def test_tit_for_tat_keeps_only_latest_opponent_action():
    """Verify a new observation replaces the opponent's previous action."""
    strategy = TitForTatStrategy()

    strategy.observe("agent_2", Action.DEFECT)
    strategy.observe("agent_2", Action.COOPERATE)

    assert (
        strategy.choose_action(DecisionContext(opponent_id="agent_2"))
        == Action.COOPERATE
    )


def test_strategy_state_persists_across_matches_for_reused_agent():
    """Verify strategy state belongs to the reused Agent/Strategy instance and persists across Matches."""
    tft_agent = Agent("agent_tft", TitForTatStrategy())
    defect_agent = Agent("agent_defect", AlwaysDefectStrategy())
    game = PrisonersDilemma()

    match1 = Match(
        first_agent=tft_agent,
        second_agent=defect_agent,
        game=game,
        round_count=1,
    )
    rounds1 = match1.execute()
    assert rounds1[0].first_action == Action.COOPERATE

    # Match 2 reuses the same tft_agent and defect_agent instances
    match2 = Match(
        first_agent=tft_agent,
        second_agent=defect_agent,
        game=game,
        round_count=1,
    )
    rounds2 = match2.execute()

    # TFT remembers opponent's DEFECT from Match 1 and defects on first action of Match 2
    assert rounds2[0].first_action == Action.DEFECT


def test_independent_strategy_instances_are_isolated():
    """Verify that separate TitForTatStrategy instances do not share state."""
    strategy_a = TitForTatStrategy()
    strategy_b = TitForTatStrategy()

    agent_a = Agent("agent_a", strategy_a)
    agent_b = Agent("agent_b", strategy_b)

    # Strategy A observes an opponent DEFECT via standard strategy notification
    agent_a.strategy.observe("opponent_x", Action.DEFECT)

    # Strategy A chooses DEFECT for opponent_x
    assert (
        agent_a.strategy.choose_action(DecisionContext(opponent_id="opponent_x"))
        == Action.DEFECT
    )

    # Strategy B, having no observation for opponent_x, chooses COOPERATE
    assert (
        agent_b.strategy.choose_action(DecisionContext(opponent_id="opponent_x"))
        == Action.COOPERATE
    )
