from collections.abc import Mapping
from types import MappingProxyType

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.game import Game
from the_dilemma_experiment.domain.payoff import Payoff

REQUIRED_COMBINATIONS: frozenset[tuple[Action, Action]] = frozenset(
    {
        (Action.COOPERATE, Action.COOPERATE),
        (Action.COOPERATE, Action.DEFECT),
        (Action.DEFECT, Action.COOPERATE),
        (Action.DEFECT, Action.DEFECT),
    }
)

DEFAULT_PAYOFF_MATRIX: MappingProxyType[tuple[Action, Action], Payoff] = (
    MappingProxyType(
        {
            (Action.COOPERATE, Action.COOPERATE): Payoff(3, 3),
            (Action.COOPERATE, Action.DEFECT): Payoff(0, 5),
            (Action.DEFECT, Action.COOPERATE): Payoff(5, 0),
            (Action.DEFECT, Action.DEFECT): Payoff(1, 1),
        }
    )
)


class PrisonersDilemma(Game):
    """Concrete Game implementation for the Prisoner's Dilemma."""

    def __init__(
        self, payoff_matrix: Mapping[tuple[Action, Action], Payoff] | None = None
    ) -> None:
        matrix = DEFAULT_PAYOFF_MATRIX if payoff_matrix is None else payoff_matrix
        self._validate_matrix(matrix)
        self._payoff_matrix: dict[tuple[Action, Action], Payoff] = dict(matrix)

    @property
    def payoff_matrix(self) -> MappingProxyType[tuple[Action, Action], Payoff]:
        """Return a read-only view of the configured payoff matrix."""
        return MappingProxyType(self._payoff_matrix)

    def resolve(self, first_action: Action, second_action: Action) -> Payoff:
        """Resolve two actions into a Payoff according to the configured payoff matrix."""
        return self._payoff_matrix[(first_action, second_action)]

    def _validate_matrix(self, matrix: Mapping[tuple[Action, Action], Payoff]) -> None:
        if not isinstance(matrix, Mapping):
            raise TypeError("Payoff matrix must be a mapping.")

        keys = set(matrix.keys())
        if keys != REQUIRED_COMBINATIONS:
            missing = REQUIRED_COMBINATIONS - keys
            unexpected = keys - REQUIRED_COMBINATIONS
            err_msgs = []
            if missing:
                err_msgs.append(f"missing combinations: {missing}")
            if unexpected:
                err_msgs.append(f"unexpected combinations: {unexpected}")
            raise ValueError(f"Invalid payoff matrix keys ({', '.join(err_msgs)}).")

        for key, value in matrix.items():
            if not isinstance(value, Payoff):
                raise TypeError(
                    f"Payoff matrix value for {key} must be a Payoff instance, got {type(value).__name__}."
                )
