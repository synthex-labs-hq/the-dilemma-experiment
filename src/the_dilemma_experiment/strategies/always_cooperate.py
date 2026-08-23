from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.strategy import Strategy


class AlwaysCooperateStrategy(Strategy):
    """Stateless strategy that always chooses Action.COOPERATE."""

    def choose_action(self, context: DecisionContext) -> Action:
        return Action.COOPERATE
