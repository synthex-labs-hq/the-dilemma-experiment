from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.strategy import Strategy


class GrimTriggerStrategy(Strategy):
    """Strategy that cooperates until the opponent defects once, then defects forever.

    Also known as 'Grudger' or 'Grim'. It is nice (starts by cooperating) and
    retaliatory, but completely unforgiving.
    """

    def __init__(self) -> None:
        self._betrayed_by: set[str] = set()

    def choose_action(self, context: DecisionContext) -> Action:
        """Cooperate unless the opponent has previously defected."""
        if context.opponent_id in self._betrayed_by:
            return Action.DEFECT
        return Action.COOPERATE

    def observe(self, opponent_id: str, action: Action) -> None:
        """Observe opponent action; permanently remember if defection occurs."""
        if action == Action.DEFECT:
            self._betrayed_by.add(opponent_id)
