from abc import ABC, abstractmethod

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.payoff import Payoff


class Game(ABC):
    """Abstract base class defining the contract for game resolution."""

    @abstractmethod
    def resolve(self, first_action: Action, second_action: Action) -> Payoff:
        """Resolve two actions into a Payoff according to game rules."""
        ...
