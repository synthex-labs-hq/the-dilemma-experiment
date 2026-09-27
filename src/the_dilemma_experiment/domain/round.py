from dataclasses import dataclass

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.payoff import Payoff


@dataclass(frozen=True)
class Round:
    """Represents an immutable interaction result for one completed round between two participants."""

    first_agent_id: str
    second_agent_id: str
    first_action: Action
    second_action: Action
    payoff: Payoff
    first_intended_action: Action | None = None
    second_intended_action: Action | None = None

    @property
    def is_noisy(self) -> bool:
        """Return True if either participant's intended action was altered by noise."""
        first_flipped = (
            self.first_intended_action is not None
            and self.first_intended_action != self.first_action
        )
        second_flipped = (
            self.second_intended_action is not None
            and self.second_intended_action != self.second_action
        )
        return first_flipped or second_flipped
