"""Hypocrite strategy: virtue-signaling in public, exploiting in private."""

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.strategy import Strategy


class HypocriteStrategy(Strategy):
    """Observational opportunist strategy.

    Cooperates when an interaction is public to inflate its public image score.
    Defects when an interaction is private to exploit without social consequence.
    """

    def choose_action(self, context: DecisionContext) -> Action:
        # If the interaction is public, put on a cooperative display
        if context.is_public:
            return Action.COOPERATE

        # If unobserved / private, exploit ruthlessly
        return Action.DEFECT

    def observe(self, opponent_id: str, action: Action) -> None:
        pass
