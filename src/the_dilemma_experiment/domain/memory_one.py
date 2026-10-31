"""Memory-one strategy domain models and Markov chain analytical solvers.

Implements the mathematical foundation for Zero-Determinant (ZD) strategies
formalized by William H. Press and Freeman J. Dyson (PNAS 2012).
"""

import random
from collections.abc import Sequence

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.payoff import Payoff
from the_dilemma_experiment.domain.prisoners_dilemma import (
    DEFAULT_PAYOFF_MATRIX,
)
from the_dilemma_experiment.domain.strategy import Strategy

# Canonical state indices:
# 0: CC (both cooperated)
# 1: CD (self cooperated, opponent defected)
# 2: DC (self defected, opponent cooperated)
# 3: DD (both defected)
STATE_CC = 0
STATE_CD = 1
STATE_DC = 2
STATE_DD = 3


class MemoryOneStrategy(Strategy):
    """General memory-one strategy parameterized by conditional cooperation probabilities.

    A memory-one strategy conditions its action solely on the outcome of the
    immediately preceding round between the two players:
        p = (p_CC, p_CD, p_DC, p_DD)
    where p_ab is the probability of cooperating given that the player played 'a'
    and the opponent played 'b' in the previous round.
    """

    def __init__(
        self,
        p_cc: float,
        p_cd: float,
        p_dc: float,
        p_dd: float,
        initial_action: Action = Action.COOPERATE,
        seed: int | None = None,
    ) -> None:
        for val, name in [
            (p_cc, "p_cc"),
            (p_cd, "p_cd"),
            (p_dc, "p_dc"),
            (p_dd, "p_dd"),
        ]:
            if not 0.0 <= val <= 1.0:
                raise ValueError(
                    f"Probability {name} must be within [0.0, 1.0], got {val}"
                )

        self._p_cc = float(p_cc)
        self._p_cd = float(p_cd)
        self._p_dc = float(p_dc)
        self._p_dd = float(p_dd)
        self._initial_action = initial_action
        self._rng = random.Random(seed)

        self._last_own_actions: dict[str, Action] = {}
        self._last_opponent_actions: dict[str, Action] = {}

    @property
    def probabilities(self) -> tuple[float, float, float, float]:
        """Return the memory-one 4-tuple (p_CC, p_CD, p_DC, p_DD)."""
        return (self._p_cc, self._p_cd, self._p_dc, self._p_dd)

    @property
    def initial_action(self) -> Action:
        """Return the opening move on round 1."""
        return self._initial_action

    def choose_action(self, context: DecisionContext) -> Action:
        """Choose action according to conditional memory-one probabilities."""
        opp_id = context.opponent_id
        if opp_id not in self._last_own_actions:
            action = self._initial_action
        else:
            own = self._last_own_actions[opp_id]
            opp = self._last_opponent_actions.get(opp_id, Action.COOPERATE)

            if own == Action.COOPERATE and opp == Action.COOPERATE:
                prob = self._p_cc
            elif own == Action.COOPERATE and opp == Action.DEFECT:
                prob = self._p_cd
            elif own == Action.DEFECT and opp == Action.COOPERATE:
                prob = self._p_dc
            else:
                prob = self._p_dd

            action = (
                Action.COOPERATE
                if self._rng.random() < prob
                else Action.DEFECT
            )

        self._last_own_actions[opp_id] = action
        return action

    def observe(self, opponent_id: str, action: Action) -> None:
        """Observe and record the opponent's action for this interaction."""
        self._last_opponent_actions[opponent_id] = action

    def reset(self) -> None:
        """Clear memory histories."""
        self._last_own_actions.clear()
        self._last_opponent_actions.clear()


def build_markov_transition_matrix(
    p: Sequence[float], q: Sequence[float]
) -> list[list[float]]:
    """Build the 4x4 Markov transition matrix for two memory-one strategies.

    Args:
        p: Player X's probabilities (p_CC, p_CD, p_DC, p_DD).
        q: Player Y's probabilities (q_CC, q_CD, q_DC, q_DD) from Y's own perspective.

    Returns:
        A 4x4 row-stochastic transition matrix M where M[i][j] is the transition
        probability from state i to state j, with canonical states:
        0: CC, 1: CD, 2: DC, 3: DD.
    """
    if len(p) != 4 or len(q) != 4:
        raise ValueError(f"Probabilities must be length 4. Got {len(p)}, {len(q)}")

    # Map Y's probabilities to states from X's perspective:
    # State 0 (CC): Y played C, X played C -> q[0] (q_CC)
    # State 1 (CD): Y played D, X played C -> q[2] (q_DC)
    # State 2 (DC): Y played C, X played D -> q[1] (q_CD)
    # State 3 (DD): Y played D, X played D -> q[3] (q_DD)
    q_mapped = [q[0], q[2], q[1], q[3]]

    matrix: list[list[float]] = []
    for i in range(4):
        p_x = p[i]
        q_y = q_mapped[i]
        row = [
            p_x * q_y,  # Next is CC
            p_x * (1.0 - q_y),  # Next is CD
            (1.0 - p_x) * q_y,  # Next is DC
            (1.0 - p_x) * (1.0 - q_y),  # Next is DD
        ]
        matrix.append(row)
    return matrix


def solve_stationary_distribution(
    matrix: Sequence[Sequence[float]],
    max_iter: int = 2000,
    tol: float = 1e-12,
) -> list[float]:
    """Compute the stationary probability distribution v satisfying v M = v.

    Uses Gaussian elimination with partial pivoting as primary solver,
    falling back to power iteration if the transition matrix has non-unique
    absorbing states or rank deficiency.

    Args:
        matrix: 4x4 row-stochastic transition matrix.
        max_iter: Max iterations for power iteration fallback.
        tol: Convergence tolerance.

    Returns:
        Probability vector v = (v_CC, v_CD, v_DC, v_DD) summing to 1.0.
    """
    n = len(matrix)
    # Form linear system (M^T - I) v = 0 with sum(v) = 1
    A = [
        [matrix[j][i] - (1.0 if i == j else 0.0) for j in range(n)]
        for i in range(n - 1)
    ]
    A.append([1.0] * n)
    b = [0.0] * (n - 1) + [1.0]

    singular = False
    for i in range(n):
        max_row = i
        for k in range(i + 1, n):
            if abs(A[k][i]) > abs(A[max_row][i]):
                max_row = k
        A[i], A[max_row] = A[max_row], A[i]
        b[i], b[max_row] = b[max_row], b[i]

        pivot = A[i][i]
        if abs(pivot) < 1e-12:
            singular = True
            break
        for j in range(i, n):
            A[i][j] /= pivot
        b[i] /= pivot
        for k in range(n):
            if k != i:
                factor = A[k][i]
                for j in range(i, n):
                    A[k][j] -= factor * A[i][j]
                b[k] -= factor * b[i]

    if not singular and all(x >= -1e-6 for x in b):
        total = sum(b)
        if total > 0:
            return [max(0.0, x / total) for x in b]

    # Fallback: Power iteration / Cesaro averaging
    v = [1.0 / n] * n
    for _ in range(max_iter):
        next_v = [sum(v[j] * matrix[j][i] for j in range(n)) for i in range(n)]
        diff = sum(abs(next_v[i] - v[i]) for i in range(n))
        v = next_v
        if diff < tol:
            break
    total = sum(v)
    return [x / total for x in v]


def compute_theoretical_payoffs(
    p: Sequence[float],
    q: Sequence[float],
    payoff_matrix: (
        dict[tuple[Action, Action], Payoff] | None
    ) = None,
) -> tuple[float, float]:
    """Compute exact theoretical infinite-horizon payoffs per round for (X, Y).

    Args:
        p: Player X's probabilities (p_CC, p_CD, p_DC, p_DD).
        q: Player Y's probabilities (q_CC, q_CD, q_DC, q_DD).
        payoff_matrix: Optional custom payoff matrix; defaults to standard (R=3, S=0, T=5, P=1).

    Returns:
        Tuple of (s_X, s_Y), expected payoffs per round.
    """
    matrix = build_markov_transition_matrix(p, q)
    v = solve_stationary_distribution(matrix)

    mat = DEFAULT_PAYOFF_MATRIX if payoff_matrix is None else payoff_matrix
    r = mat[(Action.COOPERATE, Action.COOPERATE)].first
    s = mat[(Action.COOPERATE, Action.DEFECT)].first
    t = mat[(Action.DEFECT, Action.COOPERATE)].first
    p_val = mat[(Action.DEFECT, Action.DEFECT)].first

    # Payoff vectors:
    # State 0 (CC): X gets R, Y gets R
    # State 1 (CD): X gets S, Y gets T
    # State 2 (DC): X gets T, Y gets S
    # State 3 (DD): X gets P, Y gets P
    s_x = v[0] * r + v[1] * s + v[2] * t + v[3] * p_val
    s_y = v[0] * r + v[1] * t + v[2] * s + v[3] * p_val
    return (s_x, s_y)
