from dataclasses import dataclass


@dataclass(frozen=True)
class DecisionContext:
    """Represents the context provided to a Strategy when deciding an Action."""

    opponent_id: str
