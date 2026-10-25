from dataclasses import dataclass


@dataclass(frozen=True)
class DecisionContext:
    """Represents the context provided to a Strategy when deciding an Action."""

    opponent_id: str
    opponent_score: int | None = None
    opponent_standing: str | None = None
    is_public: bool = True
    opponent_tag: float | str | None = None
    self_tag: float | str | None = None
    resource_stock: float | None = None
    endowment: float | None = None
    group_size: int | None = None
