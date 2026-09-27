from enum import Enum


class Action(Enum):
    """Represents the possible actions in the Prisoner's Dilemma."""

    COOPERATE = "COOPERATE"
    DEFECT = "DEFECT"

    def opposite(self) -> "Action":
        """Return the inverted action (COOPERATE -> DEFECT, DEFECT -> COOPERATE)."""
        return Action.DEFECT if self == Action.COOPERATE else Action.COOPERATE
