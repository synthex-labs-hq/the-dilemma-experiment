"""Tag-based strategies: In-group favoritism, tolerance thresholds, and false-beard cheaters."""

from dataclasses import dataclass

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.strategy import Strategy
from the_dilemma_experiment.domain.tag import TagProfile, TagToleranceStrategy

# Alias for Riolo et al. (2001) tolerance strategy
RioloToleranceStrategy = TagToleranceStrategy


@dataclass
class StrictTribalStrategy(Strategy):
    """Categorical tribalist: Cooperates exclusively with members sharing the exact same tag."""

    tag: str = "BLUE"

    def choose_action(self, context: DecisionContext) -> Action:
        if context.opponent_tag is None:
            return Action.COOPERATE

        if str(context.opponent_tag) == str(self.tag):
            return Action.COOPERATE
        return Action.DEFECT


@dataclass
class FalseBeardStrategy(Strategy):
    """Displays a tag to attract cooperation from tolerant in-group members, but always defects."""

    tag: float | str = 0.5

    def choose_action(self, context: DecisionContext) -> Action:
        # Classical green-beard cheater: takes donations, never gives
        return Action.DEFECT


@dataclass
class TagReciprocalStrategy(Strategy):
    """In-group reciprocity: plays Tit-for-Tat against in-group peers, defects against out-group."""

    tag: float | str = "GREEN"
    tolerance: float = 0.0

    def __post_init__(self) -> None:
        self._history: dict[str, Action] = {}

    def observe(self, opponent_id: str, action: Action) -> None:
        self._history[opponent_id] = action

    def choose_action(self, context: DecisionContext) -> Action:
        if context.opponent_tag is None:
            return Action.COOPERATE

        profile = TagProfile(tag=self.tag, tolerance=self.tolerance)
        if not profile.is_in_group(context.opponent_tag):
            # Unconditional out-group hostility
            return Action.DEFECT

        # In-group reciprocal response
        last_action = self._history.get(context.opponent_id)
        if last_action is None:
            return Action.COOPERATE
        return last_action
