"""Zero-mock unit tests for tag domain representations, distances, and diversity metrics (ADR-023)."""

import pytest

from the_dilemma_experiment.domain.tag import (
    TagProfile,
    calculate_shannon_diversity,
    categorical_tag_distance,
    compute_tag_distance,
    continuous_tag_distance,
)


def test_continuous_tag_distance_standard() -> None:
    """Standard continuous distance is absolute Euclidean difference."""
    assert continuous_tag_distance(0.2, 0.5) == pytest.approx(0.3)
    assert continuous_tag_distance(0.8, 0.1) == pytest.approx(0.7)
    assert continuous_tag_distance(0.4, 0.4) == pytest.approx(0.0)


def test_continuous_tag_distance_torus() -> None:
    """Toroidal continuous distance wraps around the [0.0, 1.0] boundary."""
    # Distance between 0.05 and 0.95 on torus is 0.1, not 0.9
    assert continuous_tag_distance(0.05, 0.95, torus=True) == pytest.approx(0.1)
    # Direct distance when shorter is still used
    assert continuous_tag_distance(0.2, 0.4, torus=True) == pytest.approx(0.2)


def test_categorical_tag_distance() -> None:
    """Categorical distance is 0 for matching tags, 1 for different tags."""
    assert categorical_tag_distance("RED", "RED") == 0.0
    assert categorical_tag_distance("RED", "BLUE") == 1.0
    assert categorical_tag_distance(1, 1) == 0.0
    assert categorical_tag_distance(1, 2) == 1.0


def test_compute_tag_distance_polymorphism() -> None:
    """compute_tag_distance dispatches appropriately based on input types."""
    assert compute_tag_distance(0.3, 0.5) == pytest.approx(0.2)
    assert compute_tag_distance("TRIBE_A", "TRIBE_A") == 0.0
    assert compute_tag_distance("TRIBE_A", "TRIBE_B") == 1.0


def test_tag_profile_in_group_check() -> None:
    """TagProfile accurately evaluates whether peers fall within tolerance."""
    profile = TagProfile(tag=0.5, tolerance=0.1)
    assert profile.is_in_group(0.55) is True
    assert profile.is_in_group(0.42) is True
    assert profile.is_in_group(0.65) is False
    assert profile.is_in_group(0.35) is False


def test_shannon_diversity_empty_and_uniform() -> None:
    """Shannon entropy handles edge cases properly."""
    assert calculate_shannon_diversity([]) == 0.0
    # Uniform tags: all identical -> entropy is 0.0
    assert calculate_shannon_diversity(["BLUE", "BLUE", "BLUE"]) == 0.0


def test_shannon_diversity_continuous_and_categorical() -> None:
    """Shannon entropy computes positive entropy for diverse distributions."""
    # Balanced 2-group categorical distribution -> H = ln(2) = ~0.6931
    cat_diversity = calculate_shannon_diversity(["RED", "RED", "BLUE", "BLUE"])
    assert cat_diversity == pytest.approx(0.6931, rel=1e-3)

    # Distributed continuous tags
    cont_diversity = calculate_shannon_diversity([0.1, 0.3, 0.5, 0.7, 0.9])
    assert cont_diversity > 0.0
