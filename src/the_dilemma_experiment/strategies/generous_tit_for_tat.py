import random

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.strategy import Strategy


class GenerousTitForTatStrategy(Strategy):
    """Strategy that cooperates on the first move and after opponent cooperation.

    When the opponent defects, it cooperates with probability q (forgiveness_probability),
    and defects with probability (1 - q).

    Default forgiveness_probability is 1/3 (~0.3333), which is the canonical
    game-theoretic optimal forgiveness rate for Axelrod's standard payoff matrix
    (min(1 - (T-R)/(R-S), (R-P)/(T-P))).
    """

    def __init__(
        self,
        forgiveness_probability: float = 1 / 3,
        seed: int | None = None,
    ) -> None:
        if isinstance(forgiveness_probability, bool) or not isinstance(
            forgiveness_probability, (float, int)
        ):
            raise TypeError("forgiveness_probability must be a float or int.")
        if not (0.0 <= forgiveness_probability <= 1.0):
            raise ValueError(
                f"forgiveness_probability must be between 0.0 and 1.0, got {forgiveness_probability}"
            )
        if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int)):
            raise TypeError("seed must be an integer or None.")

        self._forgiveness_probability = float(forgiveness_probability)
        self._seed = seed
        self._random = random.Random(seed)
        self._opponent_last_actions: dict[str, Action] = {}

    @property
    def forgiveness_probability(self) -> float:
        """The probability of forgiving an opponent's defection."""
        return self._forgiveness_probability

    @property
    def seed(self) -> int | None:
        """The configured random seed."""
        return self._seed

    def choose_action(self, context: DecisionContext) -> Action:
        """Cooperate initially or if opponent cooperated; forgive defection with probability q."""
        last_action = self._opponent_last_actions.get(context.opponent_id)
        if last_action is None or last_action == Action.COOPERATE:
            return Action.COOPERATE

        # Opponent defected: forgive with probability q
        if self._random.random() < self._forgiveness_probability:
            return Action.COOPERATE
        return Action.DEFECT

    def observe(self, opponent_id: str, action: Action) -> None:
        """Remember the opponent's most recently observed action."""
        self._opponent_last_actions[opponent_id] = action
