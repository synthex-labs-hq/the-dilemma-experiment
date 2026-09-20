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


# --- RandomStrategy Tests ---


def test_random_strategy_is_concrete_strategy():
    """Verify RandomStrategy inherits from Strategy and can be instantiated."""
    from the_dilemma_experiment.strategies.random_strategy import RandomStrategy

    assert issubclass(RandomStrategy, Strategy)
    strategy = RandomStrategy()
    assert isinstance(strategy, Strategy)
    assert strategy.cooperation_probability == 0.5


def test_random_strategy_probability_validation():
    """Verify RandomStrategy raises ValueError when probability is out of bounds."""
    import pytest

    from the_dilemma_experiment.strategies.random_strategy import RandomStrategy

    with pytest.raises(ValueError, match="cooperation_probability must be between 0.0 and 1.0"):
        RandomStrategy(cooperation_probability=-0.1)

    with pytest.raises(ValueError, match="cooperation_probability must be between 0.0 and 1.0"):
        RandomStrategy(cooperation_probability=1.1)


def test_random_strategy_deterministic_with_seed():
    """Verify RandomStrategy produces identical sequences when given the same seed."""
    from the_dilemma_experiment.strategies.random_strategy import RandomStrategy

    strat1 = RandomStrategy(seed=42)
    strat2 = RandomStrategy(seed=42)

    context = DecisionContext(opponent_id="opp")
    actions1 = [strat1.choose_action(context) for _ in range(50)]
    actions2 = [strat2.choose_action(context) for _ in range(50)]

    assert actions1 == actions2
    # Verify sequence has both cooperate and defect
    assert Action.COOPERATE in actions1
    assert Action.DEFECT in actions1


def test_random_strategy_extreme_probabilities():
    """Verify cooperation_probability=1.0 always cooperates and 0.0 always defects."""
    from the_dilemma_experiment.strategies.random_strategy import RandomStrategy

    always_c = RandomStrategy(cooperation_probability=1.0)
    always_d = RandomStrategy(cooperation_probability=0.0)
    context = DecisionContext(opponent_id="opp")

    for _ in range(20):
        assert always_c.choose_action(context) == Action.COOPERATE
        assert always_d.choose_action(context) == Action.DEFECT


def test_random_strategy_observe_does_not_raise():
    """Verify observe does not fail on RandomStrategy."""
    from the_dilemma_experiment.strategies.random_strategy import RandomStrategy

    strategy = RandomStrategy()
    strategy.observe("opp_1", Action.COOPERATE)
    strategy.observe("opp_1", Action.DEFECT)


# --- GrimTriggerStrategy Tests ---


def test_grim_trigger_is_concrete_strategy():
    """Verify GrimTriggerStrategy inherits from Strategy and can be instantiated."""
    from the_dilemma_experiment.strategies.grim_trigger import GrimTriggerStrategy

    assert issubclass(GrimTriggerStrategy, Strategy)
    strategy = GrimTriggerStrategy()
    assert isinstance(strategy, Strategy)


def test_grim_trigger_cooperates_initially():
    """Verify GrimTriggerStrategy starts by cooperating with an unseen opponent."""
    from the_dilemma_experiment.strategies.grim_trigger import GrimTriggerStrategy

    strategy = GrimTriggerStrategy()
    context = DecisionContext(opponent_id="opp_1")
    assert strategy.choose_action(context) == Action.COOPERATE


def test_grim_trigger_continues_cooperating_if_opponent_cooperates():
    """Verify GrimTrigger continues cooperating as long as opponent cooperates."""
    from the_dilemma_experiment.strategies.grim_trigger import GrimTriggerStrategy

    strategy = GrimTriggerStrategy()
    context = DecisionContext(opponent_id="opp_1")

    for _ in range(5):
        assert strategy.choose_action(context) == Action.COOPERATE
        strategy.observe("opp_1", Action.COOPERATE)


def test_grim_trigger_defects_permanently_after_single_defection():
    """Verify GrimTrigger permanently defects against an opponent who defected once."""
    from the_dilemma_experiment.strategies.grim_trigger import GrimTriggerStrategy

    strategy = GrimTriggerStrategy()
    context = DecisionContext(opponent_id="traitor")

    assert strategy.choose_action(context) == Action.COOPERATE
    # Opponent defects
    strategy.observe("traitor", Action.DEFECT)

    # GrimTrigger must now defect permanently, even if opponent subsequently cooperates
    assert strategy.choose_action(context) == Action.DEFECT
    strategy.observe("traitor", Action.COOPERATE)
    assert strategy.choose_action(context) == Action.DEFECT
    strategy.observe("traitor", Action.COOPERATE)
    assert strategy.choose_action(context) == Action.DEFECT


def test_grim_trigger_opponent_isolation():
    """Verify GrimTrigger isolates betrayal history by opponent_id per ADR-014."""
    from the_dilemma_experiment.strategies.grim_trigger import GrimTriggerStrategy

    strategy = GrimTriggerStrategy()
    context_a = DecisionContext(opponent_id="bad_agent")
    context_b = DecisionContext(opponent_id="good_agent")

    # Opponent A defects
    strategy.observe("bad_agent", Action.DEFECT)

    # GrimTrigger defects against Opponent A
    assert strategy.choose_action(context_a) == Action.DEFECT

    # But still cooperates with Opponent B who never defected
    assert strategy.choose_action(context_b) == Action.COOPERATE


def test_grim_trigger_match_against_always_defect():
    """Verify GrimTrigger against AlwaysDefect in a 3-round match."""
    from the_dilemma_experiment.strategies.grim_trigger import GrimTriggerStrategy

    grim_agent = Agent("grim", GrimTriggerStrategy())
    defect_agent = Agent("defector", AlwaysDefectStrategy())
    game = PrisonersDilemma()

    match = Match(grim_agent, defect_agent, game, round_count=3)
    rounds = match.execute()

    # Round 1: Grim cooperates, Defector defects -> Payoff (0, 5)
    assert rounds[0].first_action == Action.COOPERATE
    assert rounds[0].second_action == Action.DEFECT
    assert (rounds[0].payoff.first, rounds[0].payoff.second) == (0, 5)

    # Round 2 & 3: Grim retaliates by defecting forever -> Payoff (1, 1)
    assert rounds[1].first_action == Action.DEFECT
    assert rounds[1].second_action == Action.DEFECT
    assert (rounds[1].payoff.first, rounds[1].payoff.second) == (1, 1)

    assert rounds[2].first_action == Action.DEFECT
    assert rounds[2].second_action == Action.DEFECT
    assert (rounds[2].payoff.first, rounds[2].payoff.second) == (1, 1)

    assert match.result.first_score == 2
    assert match.result.second_score == 7

