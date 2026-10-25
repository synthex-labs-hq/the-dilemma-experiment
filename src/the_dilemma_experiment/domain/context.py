from dataclasses import dataclass


@dataclass(frozen=True)
class DecisionContext:
    """Represents the context provided to a Strategy when deciding an Action."""

    opponent_id: str
    opponent_score: int | None = None
    opponent_standing: str | None = None
    is_public: bool = True
