from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.strategy import Strategy


class WinStayLoseShiftStrategy(Strategy):
    """Win-Stay, Lose-Shift strategy (also known as Pavlov).

    Proposed by Martin Nowak and Karl Sigmund (1993).
    - Starts with COOPERATE on round 1.
    - If the last round was a 'Win' (CC -> Reward or DC -> Temptation):
      STAY with the same action as its own last move.
    - If the last round was a 'Loss' (CD -> Sucker or DD -> Punishment):
      SHIFT to the opposite action.

    Self-corrects after isolated noise errors against cooperative partners within
    two rounds, avoiding the eternal retaliation cycles of classic Tit-for-Tat.
    """

    def __init__(self) -> None:
        self._last_own_actions: dict[str, Action] = {}
        self._last_opponent_actions: dict[str, Action] = {}

    def choose_action(self, context: DecisionContext) -> Action:
        """Select action based on the win-stay, lose-shift principle."""
        opp_id = context.opponent_id
        if opp_id not in self._last_own_actions:
            action = Action.COOPERATE
        else:
            own = self._last_own_actions[opp_id]
            opp = self._last_opponent_actions.get(opp_id, Action.COOPERATE)

            # Win conditions: CC or DC
            if (own == Action.COOPERATE and opp == Action.COOPERATE) or (
                own == Action.DEFECT and opp == Action.COOPERATE
            ):
                action = own  # Stay
            else:
                action = own.opposite()  # Shift

        self._last_own_actions[opp_id] = action
        return action

    def observe(self, opponent_id: str, action: Action) -> None:
        """Observe and store the opponent's action."""
        self._last_opponent_actions[opponent_id] = action
