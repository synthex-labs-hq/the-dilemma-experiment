from the_dilemma_experiment import Action, DecisionContext, Strategy


class TitForTatStrategy(Strategy):
    """Strategy that cooperates on the first move, then mimics the opponent's previous move."""

    def __init__(self) -> None:
        self._opponent_last_actions: dict[str, Action] = {}

    def choose_action(self, context: DecisionContext) -> Action:
        """Cooperate initially, then mirror the opponent's previous action."""
        return self._opponent_last_actions.get(context.opponent_id, Action.COOPERATE)

    def observe(self, opponent_id: str, action: Action) -> None:
        """Remember the opponent's most recently observed action."""
        self._opponent_last_actions[opponent_id] = action
