from dataclasses import dataclass


@dataclass(frozen=True)
class Payoff:
    """Represents the payoff received by two participants in a game resolution."""

    first: int
    second: int

    def __post_init__(self) -> None:
        if not isinstance(self.first, int) or isinstance(self.first, bool):
            raise TypeError("Payoff 'first' must be an integer.")
        if not isinstance(self.second, int) or isinstance(self.second, bool):
            raise TypeError("Payoff 'second' must be an integer.")
