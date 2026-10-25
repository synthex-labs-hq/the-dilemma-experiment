"""Image Scorer strategy implementing first-order indirect reciprocity."""

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.strategy import Strategy


class ImageScorerStrategy(Strategy):
    """First-order reputation strategy (Nowak & Sigmund 1998).

    Cooperates with an opponent if the opponent's public image score meets or
    exceeds a defined threshold (default >= 0); otherwise defects.
    """

    def __init__(self, threshold: int = 0) -> None:
        if not isinstance(threshold, int) or isinstance(threshold, bool):
            raise TypeError("threshold must be an integer.")
        self._threshold = threshold

    @property
    def threshold(self) -> int:
        return self._threshold

    def choose_action(self, context: DecisionContext) -> Action:
        # If public score is available in context, discriminate based on threshold
        if context.opponent_score is not None:
            if context.opponent_score >= self._threshold:
                return Action.COOPERATE
            return Action.DEFECT

        # Default if no public record: grant benefit of the doubt
        return Action.COOPERATE

    def observe(self, opponent_id: str, action: Action) -> None:
        # Memory-less relative to pairwise history; relies purely on public image score
        pass
