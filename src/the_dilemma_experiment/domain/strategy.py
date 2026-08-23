from abc import ABC, abstractmethod

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.context import DecisionContext


class Strategy(ABC):
    """Abstract base class defining the decision-making strategy contract."""

    @abstractmethod
    def choose_action(self, context: DecisionContext) -> Action:
        """Select the strategy's next action given the decision context."""
        ...

    def observe(self, opponent_id: str, action: Action) -> None:
        """Observe an opponent's action to update internal strategy state if needed."""
