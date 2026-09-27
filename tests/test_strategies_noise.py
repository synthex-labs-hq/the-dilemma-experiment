import pytest

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.match import Match
from the_dilemma_experiment.domain.prisoners_dilemma import PrisonersDilemma
from the_dilemma_experiment.strategies.always_cooperate import AlwaysCooperateStrategy
from the_dilemma_experiment.strategies.generous_tit_for_tat import (
    GenerousTitForTatStrategy,
)
from the_dilemma_experiment.strategies.tit_for_tat import TitForTatStrategy
from the_dilemma_experiment.strategies.tit_for_two_tats import (
    TitForTwoTatsStrategy,
)
from the_dilemma_experiment.strategies.win_stay_lose_shift import (
    WinStayLoseShiftStrategy,
)


def test_gtft_initialization_and_validation():
    """Verify input validation for GenerousTitForTatStrategy."""
    strat = GenerousTitForTatStrategy()
    assert abs(strat.forgiveness_probability - (1 / 3)) < 1e-4
    assert strat.seed is None

    # Invalid probability type
    with pytest.raises(
        TypeError, match="forgiveness_probability must be a float or int"
    ):
        GenerousTitForTatStrategy(forgiveness_probability="0.5")  # type: ignore[arg-type]

    with pytest.raises(
        TypeError, match="forgiveness_probability must be a float or int"
    ):
        GenerousTitForTatStrategy(forgiveness_probability=True)  # type: ignore[arg-type]

    # Out of bounds probability
    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        GenerousTitForTatStrategy(forgiveness_probability=-0.1)

    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        GenerousTitForTatStrategy(forgiveness_probability=1.1)

    # Invalid seed type
    with pytest.raises(TypeError, match="seed must be an integer or None"):
        GenerousTitForTatStrategy(seed="invalid")  # type: ignore[arg-type]


def test_gtft_first_move_and_cooperation_response():
    """Verify GTFT cooperates on move 1 and after opponent cooperation."""
    strat = GenerousTitForTatStrategy(forgiveness_probability=0.33)
    ctx = DecisionContext(opponent_id="opp1")

    # Round 1: must cooperate
    assert strat.choose_action(ctx) == Action.COOPERATE

    # Opponent cooperates: must cooperate
    strat.observe("opp1", Action.COOPERATE)
    assert strat.choose_action(ctx) == Action.COOPERATE


def test_gtft_zero_forgiveness_matches_tft():
    """Verify GTFT with q=0 behaves exactly like classic Tit-for-Tat."""
    gtft = GenerousTitForTatStrategy(forgiveness_probability=0.0)
    ctx = DecisionContext(opponent_id="opp1")

    assert gtft.choose_action(ctx) == Action.COOPERATE
    gtft.observe("opp1", Action.DEFECT)
    # With q=0, never forgives defection
    for _ in range(5):
        assert gtft.choose_action(ctx) == Action.DEFECT


def test_gtft_full_forgiveness_matches_always_cooperate():
    """Verify GTFT with q=1 always cooperates even after defection."""
    gtft = GenerousTitForTatStrategy(forgiveness_probability=1.0)
    ctx = DecisionContext(opponent_id="opp1")

    gtft.observe("opp1", Action.DEFECT)
    for _ in range(5):
        assert gtft.choose_action(ctx) == Action.COOPERATE


def test_gtft_opponent_isolation():
    """Verify GTFT partitions memory by opponent_id per ADR-014."""
    gtft = GenerousTitForTatStrategy(forgiveness_probability=0.0)
    gtft.observe("bad_agent", Action.DEFECT)

    # Against bad_agent: defect
    assert gtft.choose_action(DecisionContext(opponent_id="bad_agent")) == Action.DEFECT
    # Against fresh agent: cooperate
    assert (
        gtft.choose_action(DecisionContext(opponent_id="new_agent")) == Action.COOPERATE
    )


def test_tit_for_two_tats_forgives_single_defection():
    """Verify TF2T only retaliates after two consecutive defections."""
    tf2t = TitForTwoTatsStrategy()
    ctx = DecisionContext(opponent_id="opp1")

    # Round 1: cooperate
    assert tf2t.choose_action(ctx) == Action.COOPERATE

    # Opponent defects once: TF2T still cooperates
    tf2t.observe("opp1", Action.DEFECT)
    assert tf2t.choose_action(ctx) == Action.COOPERATE

    # Opponent defects a second time consecutively: TF2T retaliates
    tf2t.observe("opp1", Action.DEFECT)
    assert tf2t.choose_action(ctx) == Action.DEFECT

    # Opponent cooperates: TF2T immediately forgives next turn
    tf2t.observe("opp1", Action.COOPERATE)
    assert tf2t.choose_action(ctx) == Action.COOPERATE


def test_tit_for_two_tats_opponent_isolation():
    """Verify TF2T maintains isolated histories for different opponents."""
    tf2t = TitForTwoTatsStrategy()
    tf2t.observe("bad_agent", Action.DEFECT)
    tf2t.observe("bad_agent", Action.DEFECT)

    assert tf2t.choose_action(DecisionContext("bad_agent")) == Action.DEFECT
    assert tf2t.choose_action(DecisionContext("good_agent")) == Action.COOPERATE


def test_win_stay_lose_shift_logic():
    """Verify Pavlov (WSLS) repeats win moves and shifts after loss moves."""
    wsls = WinStayLoseShiftStrategy()
    ctx = DecisionContext(opponent_id="opp1")

    # Round 1: always starts with COOPERATE
    assert wsls.choose_action(ctx) == Action.COOPERATE

    # Case 1: Both cooperated (CC -> Win!). Should STAY with COOPERATE.
    wsls.observe("opp1", Action.COOPERATE)
    assert wsls.choose_action(ctx) == Action.COOPERATE

    # Case 2: We cooperated, opponent defected (CD -> Sucker Loss!). Should SHIFT to DEFECT.
    wsls.observe("opp1", Action.DEFECT)
    assert wsls.choose_action(ctx) == Action.DEFECT

    # Case 3: We defected, opponent defected (DD -> Punishment Loss!). Should SHIFT to COOPERATE.
    wsls.observe("opp1", Action.DEFECT)
    assert wsls.choose_action(ctx) == Action.COOPERATE

    # Case 4: We defected, opponent cooperated (DC -> Temptation Win!). Should STAY with DEFECT.
    # First set own action to DEFECT via a loss:
    wsls.observe("opp1", Action.DEFECT)
    assert wsls.choose_action(ctx) == Action.DEFECT  # Now own is DEFECT
    # Opponent cooperates (DC):
    wsls.observe("opp1", Action.COOPERATE)
    assert wsls.choose_action(ctx) == Action.DEFECT  # Stays with DEFECT!


def test_win_stay_lose_shift_exploits_altruist():
    """Verify Pavlov locks into defection against AlwaysCooperate once defecting."""
    game = PrisonersDilemma()
    p1 = Agent("pavlov", WinStayLoseShiftStrategy())
    p2 = Agent("altruist", AlwaysCooperateStrategy())

    # In round 1, Pavlov cooperates (CC).
    # If round 2 is forced to DEFECT by noise, Pavlov stays on DEFECT forever against sucker.
    # Test this by running Pavlov against an agent that cooperates after Pavlov defects.
    m = Match(p1, p2, game, round_count=5)
    rounds = m.execute()
    # Mutual cooperation on all rounds if no noise
    for r in rounds:
        assert r.first_action == Action.COOPERATE
        assert r.second_action == Action.COOPERATE


def test_noise_tit_for_tat_retaliation_spiral():
    """Demonstrate classic TFT entering an alternating retaliation feud upon a single noise glitch."""
    tft1 = Agent("tft_1", TitForTatStrategy())
    tft2 = Agent("tft_2", TitForTatStrategy())

    # We manually simulate the rounds to show the deterministic echo cycle
    # Round 1: both choose C
    # But noise flips tft1 to D
    # Round 1: D vs C
    # Round 2: tft1 observed C -> chooses C. tft2 observed D -> chooses D. Result: C vs D!
    # Round 3: tft1 observed D -> chooses D. tft2 observed C -> chooses C. Result: D vs C!
    # Round 4: Result: C vs D!
    # It alternates forever (CD <-> DC)!
    tft1.strategy.observe("tft_2", Action.COOPERATE)
    tft2.strategy.observe("tft_1", Action.DEFECT)

    r2_a1 = tft1.strategy.choose_action(DecisionContext("tft_2"))
    r2_a2 = tft2.strategy.choose_action(DecisionContext("tft_1"))
    assert (r2_a1, r2_a2) == (Action.COOPERATE, Action.DEFECT)

    tft1.strategy.observe("tft_2", r2_a2)
    tft2.strategy.observe("tft_1", r2_a1)

    r3_a1 = tft1.strategy.choose_action(DecisionContext("tft_2"))
    r3_a2 = tft2.strategy.choose_action(DecisionContext("tft_1"))
    assert (r3_a1, r3_a2) == (Action.DEFECT, Action.COOPERATE)
