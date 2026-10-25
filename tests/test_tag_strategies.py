"""Zero-mock unit tests for tag-based strategies (ADR-023)."""

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.strategies.tag_based import (
    FalseBeardStrategy,
    RioloToleranceStrategy,
    StrictTribalStrategy,
    TagReciprocalStrategy,
)


def test_riolo_tolerance_strategy_discrimination() -> None:
    """RioloToleranceStrategy cooperates if opponent tag is within tolerance."""
    strat = RioloToleranceStrategy(tag=0.5, tolerance=0.1)

    # Opponent within tolerance (dist = 0.05 <= 0.1)
    ctx_near = DecisionContext(opponent_id="stranger", opponent_tag=0.55)
    assert strat.choose_action(ctx_near) == Action.COOPERATE

    # Opponent on the exact boundary (dist = 0.10 <= 0.1)
    ctx_edge = DecisionContext(opponent_id="stranger", opponent_tag=0.60)
    assert strat.choose_action(ctx_edge) == Action.COOPERATE

    # Opponent outside tolerance (dist = 0.15 > 0.1)
    ctx_far = DecisionContext(opponent_id="stranger", opponent_tag=0.65)
    assert strat.choose_action(ctx_far) == Action.DEFECT

    # Fallback when no tag is observed
    ctx_notag = DecisionContext(opponent_id="stranger", opponent_tag=None)
    assert strat.choose_action(ctx_notag) == Action.COOPERATE


def test_strict_tribal_strategy() -> None:
    """StrictTribalStrategy cooperates with matching tags, defects against out-group."""
    strat = StrictTribalStrategy(tag="BLUE")

    # In-group match
    ctx_same = DecisionContext(opponent_id="peer", opponent_tag="BLUE")
    assert strat.choose_action(ctx_same) == Action.COOPERATE

    # Out-group mismatch
    ctx_diff = DecisionContext(opponent_id="foreigner", opponent_tag="RED")
    assert strat.choose_action(ctx_diff) == Action.DEFECT


def test_false_beard_strategy_unconditional_defection() -> None:
    """FalseBeardStrategy bears a cooperative tag but defects unconditionally."""
    strat = FalseBeardStrategy(tag="GREEN")

    ctx_same = DecisionContext(opponent_id="peer", opponent_tag="GREEN")
    assert strat.choose_action(ctx_same) == Action.DEFECT

    ctx_diff = DecisionContext(opponent_id="foreigner", opponent_tag="RED")
    assert strat.choose_action(ctx_diff) == Action.DEFECT


def test_tag_reciprocal_strategy_ingroup_tit_for_tat() -> None:
    """TagReciprocalStrategy cooperates on first move with in-group, then mirrors, while defecting against out-group."""
    strat = TagReciprocalStrategy(tag="ALPHA", tolerance=0.0)

    # Out-group opponent -> unconditional defection
    ctx_out = DecisionContext(opponent_id="out_peer", opponent_tag="BETA")
    assert strat.choose_action(ctx_out) == Action.DEFECT

    # In-group opponent on turn 1 -> Cooperate
    ctx_in = DecisionContext(opponent_id="in_peer", opponent_tag="ALPHA")
    assert strat.choose_action(ctx_in) == Action.COOPERATE

    # In-group opponent defects -> Mirror defection
    strat.observe("in_peer", Action.DEFECT)
    assert strat.choose_action(ctx_in) == Action.DEFECT

    # In-group opponent cooperates -> Mirror cooperation
    strat.observe("in_peer", Action.COOPERATE)
    assert strat.choose_action(ctx_in) == Action.COOPERATE
