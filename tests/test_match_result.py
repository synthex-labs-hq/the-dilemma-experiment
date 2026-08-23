from dataclasses import FrozenInstanceError

import pytest

from the_dilemma_experiment.domain.match_result import MatchResult


def test_match_result_valid_construction():
    """Verify MatchResult retains valid participant IDs and scores."""
    result = MatchResult(
        first_agent_id="agent_1",
        second_agent_id="agent_2",
        first_score=15,
        second_score=10,
    )
    assert result.first_agent_id == "agent_1"
    assert result.second_agent_id == "agent_2"
    assert result.first_score == 15
    assert result.second_score == 10


def test_match_result_accepts_negative_scores():
    """Verify MatchResult accepts negative integer scores."""
    result = MatchResult(
        first_agent_id="agent_1",
        second_agent_id="agent_2",
        first_score=-5,
        second_score=-10,
    )
    assert result.first_score == -5
    assert result.second_score == -10


def test_match_result_rejects_non_string_first_id():
    """Verify MatchResult rejects non-string first_agent_id."""
    with pytest.raises(TypeError, match="first_agent_id must be a string"):
        MatchResult(
            first_agent_id=123,  # type: ignore[arg-type]
            second_agent_id="agent_2",
            first_score=5,
            second_score=5,
        )


def test_match_result_rejects_non_string_second_id():
    """Verify MatchResult rejects non-string second_agent_id."""
    with pytest.raises(TypeError, match="second_agent_id must be a string"):
        MatchResult(
            first_agent_id="agent_1",
            second_agent_id=456,  # type: ignore[arg-type]
            first_score=5,
            second_score=5,
        )


def test_match_result_rejects_identical_ids():
    """Verify MatchResult rejects self-interaction where both agent IDs are identical."""
    with pytest.raises(
        ValueError, match="first_agent_id and second_agent_id must be different"
    ):
        MatchResult(
            first_agent_id="agent_1",
            second_agent_id="agent_1",
            first_score=5,
            second_score=5,
        )


def test_match_result_rejects_non_integer_first_score():
    """Verify MatchResult rejects non-integer first_score."""
    with pytest.raises(TypeError, match="first_score must be an integer"):
        MatchResult(
            first_agent_id="agent_1",
            second_agent_id="agent_2",
            first_score="15",  # type: ignore[arg-type]
            second_score=10,
        )


def test_match_result_rejects_non_integer_second_score():
    """Verify MatchResult rejects non-integer second_score."""
    with pytest.raises(TypeError, match="second_score must be an integer"):
        MatchResult(
            first_agent_id="agent_1",
            second_agent_id="agent_2",
            first_score=15,
            second_score="10",  # type: ignore[arg-type]
        )


def test_match_result_rejects_boolean_first_score():
    """Verify MatchResult explicitly rejects boolean first_score."""
    with pytest.raises(TypeError, match="first_score must be an integer"):
        MatchResult(
            first_agent_id="agent_1",
            second_agent_id="agent_2",
            first_score=True,  # type: ignore[arg-type]
            second_score=10,
        )


def test_match_result_rejects_boolean_second_score():
    """Verify MatchResult explicitly rejects boolean second_score."""
    with pytest.raises(TypeError, match="second_score must be an integer"):
        MatchResult(
            first_agent_id="agent_1",
            second_agent_id="agent_2",
            first_score=15,
            second_score=False,  # type: ignore[arg-type]
        )


def test_match_result_is_immutable():
    """Verify MatchResult is frozen and field assignment raises FrozenInstanceError."""
    result = MatchResult(
        first_agent_id="agent_1",
        second_agent_id="agent_2",
        first_score=15,
        second_score=10,
    )
    with pytest.raises(FrozenInstanceError):
        result.first_agent_id = "agent_3"  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        result.first_score = 20  # type: ignore[misc]
