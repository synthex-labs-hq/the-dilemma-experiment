"""Zero-mock unit tests for ReputationRegistry and GossipChannel (ADR-021, ADR-022)."""

import pytest

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.reputation import (
    GossipChannel,
    MoralStanding,
    ReputationRegistry,
)


def test_reputation_registry_initialization_and_clamping() -> None:
    """Registry validates bounds and clamps initial scores."""
    with pytest.raises(ValueError, match="min_score.*must be strictly less"):
        ReputationRegistry(min_score=5, max_score=5)

    reg = ReputationRegistry(min_score=-3, max_score=3)
    reg.register("agent_1", initial_score=10, initial_standing=MoralStanding.GOOD)
    assert reg.get_score("agent_1") == 3
    assert reg.get_standing("agent_1") == MoralStanding.GOOD

    reg.register("agent_2", initial_score=-10, initial_standing=MoralStanding.BAD)
    assert reg.get_score("agent_2") == -3
    assert reg.get_standing("agent_2") == MoralStanding.BAD

    # Unregistered agent defaults
    assert reg.get_score("unknown") == 0
    assert reg.get_standing("unknown") == MoralStanding.GOOD


def test_first_order_image_scoring_updates() -> None:
    """Public cooperation increments score; public defection decrements score."""
    reg = ReputationRegistry(min_score=-2, max_score=2)
    reg.register("donor", initial_score=0)
    reg.register("recipient", initial_score=0)

    # Public Cooperate: 0 -> 1
    reg.record_interaction("donor", "recipient", Action.COOPERATE, is_public=True)
    assert reg.get_score("donor") == 1

    # Public Cooperate: 1 -> 2 (clamped at max)
    reg.record_interaction("donor", "recipient", Action.COOPERATE, is_public=True)
    assert reg.get_score("donor") == 2

    # Clamped at max 2
    reg.record_interaction("donor", "recipient", Action.COOPERATE, is_public=True)
    assert reg.get_score("donor") == 2

    # Public Defect: 2 -> 1
    reg.record_interaction("donor", "recipient", Action.DEFECT, is_public=True)
    assert reg.get_score("donor") == 1


def test_second_order_stern_judging_transitions() -> None:
    """Verify the four moral transitions of Stern Judging (ADR-022):

    1. C against GOOD -> GOOD
    2. D against GOOD -> BAD (unprovoked harm)
    3. C against BAD  -> BAD (appeasing a bad actor)
    4. D against BAD  -> GOOD (righteous punishment!)
    """
    reg = ReputationRegistry()
    reg.register("donor", initial_standing=MoralStanding.GOOD)
    reg.register("good_target", initial_standing=MoralStanding.GOOD)
    reg.register("bad_target", initial_standing=MoralStanding.BAD)

    # 1. C against GOOD -> stays GOOD
    reg.record_interaction("donor", "good_target", Action.COOPERATE, is_public=True)
    assert reg.get_standing("donor") == MoralStanding.GOOD

    # 2. D against GOOD -> becomes BAD (betrayal of trustworthy peer)
    reg.record_interaction("donor", "good_target", Action.DEFECT, is_public=True)
    assert reg.get_standing("donor") == MoralStanding.BAD

    # 3. D against BAD -> becomes GOOD (righteous punishment restores standing!)
    reg.record_interaction("donor", "bad_target", Action.DEFECT, is_public=True)
    assert reg.get_standing("donor") == MoralStanding.GOOD

    # 4. C against BAD -> becomes BAD (appeasing the defector corrupts standing)
    reg.record_interaction("donor", "bad_target", Action.COOPERATE, is_public=True)
    assert reg.get_standing("donor") == MoralStanding.BAD


def test_private_interactions_do_not_update_public_ledger() -> None:
    """Private unobserved interactions log audit events but leave public scores untouched."""
    reg = ReputationRegistry()
    reg.register("agent_a", initial_score=3, initial_standing=MoralStanding.GOOD)
    reg.register("agent_b", initial_score=0, initial_standing=MoralStanding.GOOD)

    # Defect in the shadows (is_public=False)
    reg.record_interaction("agent_a", "agent_b", Action.DEFECT, is_public=False)

    # Score and standing remain untouched!
    assert reg.get_score("agent_a") == 3
    assert reg.get_standing("agent_a") == MoralStanding.GOOD

    # But event is logged in historical audit trail
    assert len(reg.history) == 1
    assert reg.history[0].is_public is False
    assert reg.history[0].action == Action.DEFECT


def test_gossip_channel_error_rate_and_noise() -> None:
    """Gossip channel transmits noisy reports with error rate gamma."""
    with pytest.raises(ValueError, match=r"error_rate must be in \[0.0, 1.0\]"):
        GossipChannel(registry=ReputationRegistry(), error_rate=1.5)

    reg = ReputationRegistry()
    reg.register("hero", initial_score=4, initial_standing=MoralStanding.GOOD)

    # Zero noise channel is 100% faithful
    clean_channel = GossipChannel(registry=reg, error_rate=0.0)
    assert clean_channel.query_standing("hero") == MoralStanding.GOOD
    assert clean_channel.query_score("hero") == 4

    # 100% noisy channel always inverts standing
    inverted_channel = GossipChannel(registry=reg, error_rate=1.0)
    assert inverted_channel.query_standing("hero") == MoralStanding.BAD
