from dataclasses import FrozenInstanceError

import pytest

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.game import Game
from the_dilemma_experiment.domain.payoff import Payoff
from the_dilemma_experiment.domain.prisoners_dilemma import (
    DEFAULT_PAYOFF_MATRIX,
    PrisonersDilemma,
)


def test_payoff_stores_values_and_is_immutable():
    """Verify Payoff stores first and second integer values and is immutable."""
    payoff = Payoff(first=3, second=5)
    assert payoff.first == 3
    assert payoff.second == 5

    with pytest.raises(FrozenInstanceError):
        payoff.first = 10  # type: ignore[misc]


def test_payoff_rejects_non_integers():
    """Verify Payoff raises TypeError if non-integer types are provided."""
    with pytest.raises(TypeError, match="must be an integer"):
        Payoff(first="3", second=5)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="must be an integer"):
        Payoff(first=3, second=True)  # type: ignore[arg-type]


def test_game_cannot_be_instantiated_directly():
    """Verify Abstract Game class cannot be instantiated without resolve implementation."""

    class IncompleteGame(Game):
        pass

    with pytest.raises(TypeError):
        IncompleteGame()  # type: ignore[abstract]


def test_default_payoff_matrix_is_immutable():
    """Verify DEFAULT_PAYOFF_MATRIX cannot be mutated externally."""
    with pytest.raises(TypeError):
        DEFAULT_PAYOFF_MATRIX[(Action.COOPERATE, Action.COOPERATE)] = Payoff(99, 99)  # type: ignore[index]

    with pytest.raises(TypeError):
        del DEFAULT_PAYOFF_MATRIX[(Action.COOPERATE, Action.COOPERATE)]  # type: ignore[attr-defined]


def test_game_payoff_matrix_view_is_read_only():
    """Verify public game.payoff_matrix property view is read-only and raises TypeError on mutation."""
    game = PrisonersDilemma()

    with pytest.raises(TypeError):
        game.payoff_matrix[(Action.COOPERATE, Action.COOPERATE)] = Payoff(99, 99)  # type: ignore[index]

    with pytest.raises(TypeError):
        del game.payoff_matrix[(Action.COOPERATE, Action.COOPERATE)]  # type: ignore[attr-defined]


def test_prisoners_dilemma_default_matrix_outcomes():
    """Verify default Prisoner's Dilemma matrix produces all four expected outcomes."""
    game = PrisonersDilemma()

    assert game.resolve(Action.COOPERATE, Action.COOPERATE) == Payoff(3, 3)
    assert game.resolve(Action.COOPERATE, Action.DEFECT) == Payoff(0, 5)
    assert game.resolve(Action.DEFECT, Action.COOPERATE) == Payoff(5, 0)
    assert game.resolve(Action.DEFECT, Action.DEFECT) == Payoff(1, 1)


def test_prisoners_dilemma_accepts_mapping_and_dict():
    """Verify PrisonersDilemma accepts immutable Mapping (like DEFAULT_PAYOFF_MATRIX) and standard dict."""
    # Accepting DEFAULT_PAYOFF_MATRIX (MappingProxyType)
    game_default = PrisonersDilemma(payoff_matrix=DEFAULT_PAYOFF_MATRIX)
    assert game_default.resolve(Action.COOPERATE, Action.COOPERATE) == Payoff(3, 3)

    # Accepting dict
    custom_dict = dict(DEFAULT_PAYOFF_MATRIX)
    game_dict = PrisonersDilemma(payoff_matrix=custom_dict)
    assert game_dict.resolve(Action.COOPERATE, Action.COOPERATE) == Payoff(3, 3)


def test_prisoners_dilemma_custom_matrix():
    """Verify custom payoff matrix is respected."""
    custom_matrix = {
        (Action.COOPERATE, Action.COOPERATE): Payoff(2, 2),
        (Action.COOPERATE, Action.DEFECT): Payoff(-1, 3),
        (Action.DEFECT, Action.COOPERATE): Payoff(3, -1),
        (Action.DEFECT, Action.DEFECT): Payoff(0, 0),
    }
    game = PrisonersDilemma(payoff_matrix=custom_matrix)

    assert game.resolve(Action.COOPERATE, Action.COOPERATE) == Payoff(2, 2)
    assert game.resolve(Action.COOPERATE, Action.DEFECT) == Payoff(-1, 3)
    assert game.resolve(Action.DEFECT, Action.COOPERATE) == Payoff(3, -1)
    assert game.resolve(Action.DEFECT, Action.DEFECT) == Payoff(0, 0)


def test_prisoners_dilemma_rejects_missing_combinations():
    """Verify PrisonersDilemma rejects matrix with missing combinations."""
    incomplete_matrix = {
        (Action.COOPERATE, Action.COOPERATE): Payoff(3, 3),
        (Action.COOPERATE, Action.DEFECT): Payoff(0, 5),
    }
    with pytest.raises(ValueError, match="missing combinations"):
        PrisonersDilemma(payoff_matrix=incomplete_matrix)  # type: ignore[arg-type]


def test_prisoners_dilemma_rejects_unexpected_combinations():
    """Verify PrisonersDilemma rejects matrix with unexpected extra combinations."""
    extra_matrix = dict(DEFAULT_PAYOFF_MATRIX)
    extra_matrix[("INVALID", Action.COOPERATE)] = Payoff(1, 1)  # type: ignore[index]

    with pytest.raises(ValueError, match="unexpected combinations"):
        PrisonersDilemma(payoff_matrix=extra_matrix)


def test_prisoners_dilemma_rejects_invalid_value_types():
    """Verify PrisonersDilemma rejects non-Payoff matrix values."""
    invalid_val_matrix = {
        (Action.COOPERATE, Action.COOPERATE): (3, 3),  # type: ignore[dict-item]
        (Action.COOPERATE, Action.DEFECT): Payoff(0, 5),
        (Action.DEFECT, Action.COOPERATE): Payoff(5, 0),
        (Action.DEFECT, Action.DEFECT): Payoff(1, 1),
    }
    with pytest.raises(TypeError, match="must be a Payoff instance"):
        PrisonersDilemma(payoff_matrix=invalid_val_matrix)  # type: ignore[arg-type]


def test_prisoners_dilemma_resolution_does_not_mutate_matrix():
    """Verify resolution does not mutate configured matrix and external mutations do not affect game."""
    matrix = dict(DEFAULT_PAYOFF_MATRIX)
    game = PrisonersDilemma(payoff_matrix=matrix)

    initial_payoff = game.resolve(Action.COOPERATE, Action.DEFECT)
    assert initial_payoff == Payoff(0, 5)

    # Mutate source matrix externally
    matrix[(Action.COOPERATE, Action.DEFECT)] = Payoff(99, 99)

    # Game matrix should remain unchanged
    assert game.resolve(Action.COOPERATE, Action.DEFECT) == Payoff(0, 5)


def test_action_reversal_reverses_payoffs():
    """Verify reversing action order correctly reverses individual payoffs."""
    game = PrisonersDilemma()

    c_d_payoff = game.resolve(Action.COOPERATE, Action.DEFECT)
    d_c_payoff = game.resolve(Action.DEFECT, Action.COOPERATE)

    assert c_d_payoff == Payoff(0, 5)
    assert d_c_payoff == Payoff(5, 0)
    assert c_d_payoff.first == d_c_payoff.second
    assert c_d_payoff.second == d_c_payoff.first
