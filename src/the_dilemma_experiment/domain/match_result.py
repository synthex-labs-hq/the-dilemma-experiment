from dataclasses import dataclass


@dataclass(frozen=True)
class MatchResult:
    """Represents the aggregate outcome of one completed Match."""

    first_agent_id: str
    second_agent_id: str
    first_score: int
    second_score: int

    def __post_init__(self) -> None:
        if not isinstance(self.first_agent_id, str):
            raise TypeError("first_agent_id must be a string.")

        if not isinstance(self.second_agent_id, str):
            raise TypeError("second_agent_id must be a string.")

        if self.first_agent_id == self.second_agent_id:
            raise ValueError("first_agent_id and second_agent_id must be different.")

        if not isinstance(self.first_score, int) or isinstance(self.first_score, bool):
            raise TypeError("first_score must be an integer.")

        if not isinstance(self.second_score, int) or isinstance(
            self.second_score, bool
        ):
            raise TypeError("second_score must be an integer.")
