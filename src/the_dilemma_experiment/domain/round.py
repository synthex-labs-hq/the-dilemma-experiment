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
