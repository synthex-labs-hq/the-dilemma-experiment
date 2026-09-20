import random

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.strategy import Strategy


class RandomStrategy(Strategy):
    """Strategy that chooses Action.COOPERATE or Action.DEFECT probabilistically."""

    def __init__(
        self,
        seed: int | None = None,
        cooperation_probability: float = 0.5,
    ) -> None:
        if not (0.0 <= cooperation_probability <= 1.0):
            raise ValueError(
                f"cooperation_probability must be between 0.0 and 1.0, got {cooperation_probability}"
            )
        self._random = random.Random(seed)
        self._cooperation_probability = cooperation_probability

    @property
    def cooperation_probability(self) -> float:
        """The configured probability of choosing COOPERATE."""
        return self._cooperation_probability

    def choose_action(self, context: DecisionContext) -> Action:
        """Select COOPERATE with probability p, otherwise DEFECT."""
        if self._random.random() < self._cooperation_probability:
            return Action.COOPERATE
        return Action.DEFECT
