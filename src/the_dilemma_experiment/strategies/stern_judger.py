"""Stern Judging strategy implementing second-order indirect reciprocity."""

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.strategy import Strategy


class SternJudgingStrategy(Strategy):
    """Second-order moral enforcer strategy (Ohtsuki & Iwasa 2006).

    Cooperates with opponents whose public moral standing is GOOD.
    Defects against opponents whose standing is BAD (righteous punishment).
    """

    def choose_action(self, context: DecisionContext) -> Action:
        if context.opponent_standing is not None:
            if str(context.opponent_standing).upper() == "GOOD":
                return Action.COOPERATE
            return Action.DEFECT

        # Fallback if standing is missing but score is present
        if context.opponent_score is not None:
            if context.opponent_score >= 0:
                return Action.COOPERATE
            return Action.DEFECT

        return Action.COOPERATE

    def observe(self, opponent_id: str, action: Action) -> None:
        pass
