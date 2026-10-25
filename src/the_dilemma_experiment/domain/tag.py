"""Domain models for arbitrary surface tags, tolerance metrics, and diversity calculations."""

import math
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.strategy import Strategy


class TagKind(str, Enum):
    """Classification of tag coordinate space."""

    CONTINUOUS = "CONTINUOUS"
    CATEGORICAL = "CATEGORICAL"


def continuous_tag_distance(tag_a: float, tag_b: float, torus: bool = False) -> float:
    """Calculate distance between two continuous tags in [0.0, 1.0]."""
    diff = abs(tag_a - tag_b)
    if torus:
        return min(diff, 1.0 - diff)
    return diff


def categorical_tag_distance(tag_a: str | int, tag_b: str | int) -> float:
    """Calculate discrete Hamming distance between two categorical tags."""
    return 0.0 if tag_a == tag_b else 1.0


def compute_tag_distance(
    tag_a: float | str,
    tag_b: float | str,
    torus: bool = False,
) -> float:
    """Calculate distance between any two tags based on their types."""
    if isinstance(tag_a, (int, float)) and isinstance(tag_b, (int, float)) and not isinstance(tag_a, bool) and not isinstance(tag_b, bool):
        # If both are floats (or within [0, 1] range)
        return continuous_tag_distance(float(tag_a), float(tag_b), torus=torus)
    return categorical_tag_distance(tag_a, tag_b)


@dataclass(frozen=True, slots=True)
class TagProfile:
    """Phenotypic marker and tolerance threshold of an agent (Riolo et al. 2001)."""

    tag: float | str
    tolerance: float = 0.0

    def is_in_group(self, other_tag: float | str, torus: bool = False) -> bool:
        """Return True if distance between self and other tag is within tolerance threshold."""
        dist = compute_tag_distance(self.tag, other_tag, torus=torus)
        return dist <= self.tolerance


def calculate_shannon_diversity(
    tags: Sequence[float | str],
    bins: int = 10,
) -> float:
    """Compute Shannon entropy H = -sum(p * ln(p)) over tag distribution."""
    if not tags:
        return 0.0

    n = len(tags)
    if all(isinstance(t, (int, float)) for t in tags):
        # Continuous tags: partition [0.0, 1.0] into equal bins
        bin_counts = [0] * bins
        for t in tags:
            val = float(t)
            # clamp to [0.0, 1.0]
            val = max(0.0, min(1.0, val))
            idx = int(val * bins)
            if idx == bins:
                idx = bins - 1
            bin_counts[idx] += 1
        probabilities = [count / n for count in bin_counts if count > 0]
    else:
        # Categorical tags: count frequencies of discrete labels
        freqs: dict[str, int] = {}
        for t in tags:
            label = str(t)
            freqs[label] = freqs.get(label, 0) + 1
        probabilities = [count / n for count in freqs.values()]

    entropy = -sum(p * math.log(p) for p in probabilities if p > 0)
    return round(entropy, 4)


@dataclass
class TagToleranceStrategy(Strategy):
    """Cooperates if distance between self tag and opponent tag is <= tolerance (Riolo et al. 2001)."""

    tag: float = 0.5
    tolerance: float = 0.1
    torus: bool = False

    def choose_action(self, context: DecisionContext) -> Action:
        if context.opponent_tag is None:
            return Action.COOPERATE

        profile = TagProfile(tag=self.tag, tolerance=self.tolerance)
        if profile.is_in_group(context.opponent_tag, torus=self.torus):
            return Action.COOPERATE
        return Action.DEFECT
