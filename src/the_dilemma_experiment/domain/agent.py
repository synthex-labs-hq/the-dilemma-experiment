from dataclasses import dataclass

from the_dilemma_experiment.domain.strategy import Strategy


@dataclass(frozen=True)
class Agent:
    """Represents an individual participant in the experiment."""

    id: str
    strategy: Strategy
