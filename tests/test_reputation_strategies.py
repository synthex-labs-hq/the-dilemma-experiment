"""Zero-mock unit tests for reputation strategies (ImageScorer, SternJudger, Hypocrite)."""

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.strategies.hypocrite import HypocriteStrategy
from the_dilemma_experiment.strategies.image_scorer import ImageScorerStrategy
from the_dilemma_experiment.strategies.stern_judger import SternJudgingStrategy


def test_image_scorer_strategy_threshold_discrimination() -> None:
    """ImageScorer cooperates if opponent score >= threshold; otherwise defects."""
    scorer = ImageScorerStrategy(threshold=1)

    # Opponent with score 2 >= 1 -> Cooperate
    ctx_high = DecisionContext(opponent_id="stranger_1", opponent_score=2)
    assert scorer.choose_action(ctx_high) == Action.COOPERATE

    # Opponent with score 1 >= 1 -> Cooperate
    ctx_equal = DecisionContext(opponent_id="stranger_2", opponent_score=1)
    assert scorer.choose_action(ctx_equal) == Action.COOPERATE

    # Opponent with score 0 < 1 -> Defect
    ctx_low = DecisionContext(opponent_id="stranger_3", opponent_score=0)
    assert scorer.choose_action(ctx_low) == Action.DEFECT

    # Opponent with score -3 < 1 -> Defect
    ctx_negative = DecisionContext(opponent_id="predator", opponent_score=-3)
    assert scorer.choose_action(ctx_negative) == Action.DEFECT

    # Default benefit of doubt when no score provided
    ctx_empty = DecisionContext(opponent_id="new_agent")
    assert scorer.choose_action(ctx_empty) == Action.COOPERATE


def test_stern_judging_strategy_second_order_decisions() -> None:
    """SternJudger cooperates with GOOD agents and defects against BAD agents."""
    judger = SternJudgingStrategy()

    # GOOD opponent -> Cooperate
    ctx_good = DecisionContext(opponent_id="good_guy", opponent_standing="GOOD")
    assert judger.choose_action(ctx_good) == Action.COOPERATE

    # BAD opponent -> Righteous punishment (Defect)
    ctx_bad = DecisionContext(opponent_id="free_rider", opponent_standing="BAD")
    assert judger.choose_action(ctx_bad) == Action.DEFECT

    # Fallback to score if standing missing
    ctx_score_pos = DecisionContext(opponent_id="citizen", opponent_score=3)
    assert judger.choose_action(ctx_score_pos) == Action.COOPERATE

    ctx_score_neg = DecisionContext(opponent_id="crook", opponent_score=-2)
    assert judger.choose_action(ctx_score_neg) == Action.DEFECT


def test_hypocrite_strategy_public_vs_private_behavior() -> None:
    """Hypocrite cooperates in the public eye, but defects in the shadows."""
    hypocrite = HypocriteStrategy()

    # In public (is_public=True) -> Put on a virtuous display
    ctx_public = DecisionContext(opponent_id="victim", is_public=True)
    assert hypocrite.choose_action(ctx_public) == Action.COOPERATE

    # In private (is_public=False) -> Exploit ruthlessly
    ctx_private = DecisionContext(opponent_id="victim", is_public=False)
    assert hypocrite.choose_action(ctx_private) == Action.DEFECT
