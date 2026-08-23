from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.strategy import Strategy


class AlwaysDefectStrategy(Strategy):
    """Stateless strategy that always chooses Action.DEFECT."""

    def choose_action(self, context: DecisionContext) -> Action:
        return Action.DEFECT
