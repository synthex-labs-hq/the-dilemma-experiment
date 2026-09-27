from collections import defaultdict

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.strategy import Strategy


class TitForTwoTatsStrategy(Strategy):
    """Strategy that cooperates unless the opponent defected twice in a row.

    More forgiving than Tit-for-Tat: it gives the opponent two chances,
    preventing retaliation from being triggered by a single noisy glitch.
    """

    def __init__(self) -> None:
        self._opponent_history: dict[str, list[Action]] = defaultdict(list)

    def choose_action(self, context: DecisionContext) -> Action:
        """Cooperate unless the last two observed opponent actions were DEFECT."""
        history = self._opponent_history[context.opponent_id]
        if (
            len(history) >= 2
            and history[-1] == Action.DEFECT
            and history[-2] == Action.DEFECT
        ):
            return Action.DEFECT
        return Action.COOPERATE

    def observe(self, opponent_id: str, action: Action) -> None:
        """Record the opponent's action in their history (keeping last 2 actions)."""
        history = self._opponent_history[opponent_id]
        history.append(action)
        if len(history) > 2:
            self._opponent_history[opponent_id] = history[-2:]
