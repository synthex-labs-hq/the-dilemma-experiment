from dataclasses import FrozenInstanceError

import pytest

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.payoff import Payoff
from the_dilemma_experiment.domain.round import Round


def test_round_stores_participant_ids_correctly():
    """Verify Round stores first and second participant IDs as strings."""
    round_result = Round(
        first_agent_id="agent_alpha",
        second_agent_id="agent_beta",
        first_action=Action.COOPERATE,
        second_action=Action.DEFECT,
        payoff=Payoff(0, 5),
    )
    assert round_result.first_agent_id == "agent_alpha"
    assert round_result.second_agent_id == "agent_beta"


def test_round_stores_actions_correctly():
    """Verify Round stores first and second actions correctly."""
    round_result = Round(
        first_agent_id="agent_1",
        second_agent_id="agent_2",
        first_action=Action.COOPERATE,
        second_action=Action.COOPERATE,
        payoff=Payoff(3, 3),
    )
    assert round_result.first_action == Action.COOPERATE
    assert round_result.second_action == Action.COOPERATE


def test_round_stores_payoff_correctly():
    """Verify Round stores the Payoff instance correctly."""
    expected_payoff = Payoff(5, 0)
    round_result = Round(
        first_agent_id="agent_1",
        second_agent_id="agent_2",
        first_action=Action.DEFECT,
        second_action=Action.COOPERATE,
        payoff=expected_payoff,
    )
    assert round_result.payoff == expected_payoff
    assert round_result.payoff.first == 5
    assert round_result.payoff.second == 0


def test_round_is_immutable():
    """Verify Round is immutable and attribute assignment raises FrozenInstanceError."""
    round_result = Round(
        first_agent_id="agent_1",
        second_agent_id="agent_2",
        first_action=Action.DEFECT,
        second_action=Action.DEFECT,
        payoff=Payoff(1, 1),
    )
    with pytest.raises(FrozenInstanceError):
        round_result.first_agent_id = "agent_3"  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        round_result.first_action = Action.COOPERATE  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        round_result.payoff = Payoff(3, 3)  # type: ignore[misc]


def test_round_constructed_with_ids_actions_payoff_without_agent_objects():
    """Verify Round can be constructed strictly with string IDs, Actions, and Payoff without Agent objects."""
    agent_id_1 = "id_101"
    agent_id_2 = "id_102"
    action_1 = Action.COOPERATE
    action_2 = Action.DEFECT
    payoff = Payoff(0, 5)

    round_result = Round(
        first_agent_id=agent_id_1,
        second_agent_id=agent_id_2,
        first_action=action_1,
        second_action=action_2,
        payoff=payoff,
    )

    assert round_result.first_agent_id == "id_101"
    assert round_result.second_agent_id == "id_102"
    assert round_result.first_action == Action.COOPERATE
    assert round_result.second_action == Action.DEFECT
    assert round_result.payoff == Payoff(0, 5)
