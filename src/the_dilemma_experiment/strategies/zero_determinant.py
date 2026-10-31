"""Zero-Determinant (ZD) strategies for the Iterated Prisoner's Dilemma.

Based on Press & Dyson (PNAS 2012) and Stewart & Plotkin (PNAS 2012, 2013).
"""

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.memory_one import MemoryOneStrategy
from the_dilemma_experiment.domain.payoff import Payoff
from the_dilemma_experiment.domain.prisoners_dilemma import (
    DEFAULT_PAYOFF_MATRIX,
)


class ExtortionStrategy(MemoryOneStrategy):
    """Press-Dyson Extortioner Strategy (ZD_chi).

    Unilaterally enforces a linear relationship between payoffs:
        (s_X - P) = chi * (s_Y - P)
    where chi >= 1.0 is the extortion factor and P is the mutual defection payoff.

    For any co-player, cooperating yields a positive surplus over P, but the
    extortioner captures chi times that surplus. If the co-player defects, both
    receive P = 1.0. Thus, cooperating remains the co-player's best selfish response.
    """

    def __init__(
        self,
        chi: float = 3.0,
        phi: float | None = None,
        initial_action: Action = Action.COOPERATE,
        seed: int | None = None,
        payoff_matrix: (
            dict[tuple[Action, Action], Payoff] | None
        ) = None,
    ) -> None:
        if chi < 1.0:
            raise ValueError(f"Extortion factor chi must be >= 1.0, got {chi}")

        mat = DEFAULT_PAYOFF_MATRIX if payoff_matrix is None else payoff_matrix
        r = float(mat[(Action.COOPERATE, Action.COOPERATE)].first)
        s = float(mat[(Action.COOPERATE, Action.DEFECT)].first)
        t = float(mat[(Action.DEFECT, Action.COOPERATE)].first)
        p = float(mat[(Action.DEFECT, Action.DEFECT)].first)

        # Upper bound for phi to ensure all probabilities remain in [0.0, 1.0]
        # Max term is (P - S) + chi * (T - P)
        phi_max = 1.0 / ((p - s) + chi * (t - p))
        chosen_phi = phi_max if phi is None else float(phi)
        if chosen_phi <= 0.0 or chosen_phi > phi_max + 1e-9:
            raise ValueError(
                f"Scaling factor phi must be in (0, {phi_max:.4f}], got {chosen_phi}"
            )

        p_cc = 1.0 - chosen_phi * (chi - 1.0) * (r - p)
        p_cd = 1.0 - chosen_phi * ((p - s) + chi * (t - p))
        p_dc = chosen_phi * ((t - p) + chi * (p - s))
        p_dd = 0.0

        # Clamp tiny floating point errors to [0.0, 1.0]
        p_cc = min(1.0, max(0.0, p_cc))
        p_cd = min(1.0, max(0.0, p_cd))
        p_dc = min(1.0, max(0.0, p_dc))

        self.chi = chi
        self.phi = chosen_phi

        super().__init__(
            p_cc=p_cc,
            p_cd=p_cd,
            p_dc=p_dc,
            p_dd=p_dd,
            initial_action=initial_action,
            seed=seed,
        )


class EqualizerStrategy(MemoryOneStrategy):
    """Press-Dyson Equalizer Strategy.

    Unilaterally sets the co-player's expected payoff to a fixed constant c:
        s_Y = c
    regardless of the co-player's strategy or decisions, provided P <= c <= R.
    """

    def __init__(
        self,
        target_score: float = 2.0,
        phi: float | None = None,
        initial_action: Action = Action.COOPERATE,
        seed: int | None = None,
        payoff_matrix: (
            dict[tuple[Action, Action], Payoff] | None
        ) = None,
    ) -> None:
        mat = DEFAULT_PAYOFF_MATRIX if payoff_matrix is None else payoff_matrix
        r = float(mat[(Action.COOPERATE, Action.COOPERATE)].first)
        s = float(mat[(Action.COOPERATE, Action.DEFECT)].first)
        t = float(mat[(Action.DEFECT, Action.COOPERATE)].first)
        p = float(mat[(Action.DEFECT, Action.DEFECT)].first)

        c = float(target_score)
        if not (p <= c <= r):
            raise ValueError(
                f"Target score c must be between mutual defection P={p} and mutual coop R={r}, got {c}"
            )

        phi_max = min(1.0 / (t - c), 1.0 / (c - s))
        chosen_phi = phi_max if phi is None else float(phi)
        if chosen_phi <= 0.0 or chosen_phi > phi_max + 1e-9:
            raise ValueError(
                f"Scaling factor phi must be in (0, {phi_max:.4f}], got {chosen_phi}"
            )

        p_cc = 1.0 - chosen_phi * (r - c)
        p_cd = 1.0 - chosen_phi * (t - c)
        p_dc = chosen_phi * (c - s)
        p_dd = chosen_phi * (c - p)

        p_cc = min(1.0, max(0.0, p_cc))
        p_cd = min(1.0, max(0.0, p_cd))
        p_dc = min(1.0, max(0.0, p_dc))
        p_dd = min(1.0, max(0.0, p_dd))

        self.target_score = c
        self.phi = chosen_phi

        super().__init__(
            p_cc=p_cc,
            p_cd=p_cd,
            p_dc=p_dc,
            p_dd=p_dd,
            initial_action=initial_action,
            seed=seed,
        )


class GenerousZDStrategy(MemoryOneStrategy):
    """Stewart & Plotkin Generous Zero-Determinant Strategy.

    Anchors the linear relationship at the mutual cooperation baseline R:
        (s_X - R) = chi * (s_Y - R)  (chi >= 1.0)
    which guarantees p_CC = 1.0 and p_DD > 0.

    Against cooperative co-players, it achieves full cooperation (R, R).
    Against uncooperative players, it absorbs disproportionate losses to
    encourage mutual cooperation while remaining robust against noise.
    """

    def __init__(
        self,
        chi: float = 2.0,
        phi: float | None = None,
        initial_action: Action = Action.COOPERATE,
        seed: int | None = None,
        payoff_matrix: (
            dict[tuple[Action, Action], Payoff] | None
        ) = None,
    ) -> None:
        if chi < 1.0:
            raise ValueError(f"Generosity factor chi must be >= 1.0, got {chi}")

        mat = DEFAULT_PAYOFF_MATRIX if payoff_matrix is None else payoff_matrix
        r = float(mat[(Action.COOPERATE, Action.COOPERATE)].first)
        s = float(mat[(Action.COOPERATE, Action.DEFECT)].first)
        t = float(mat[(Action.DEFECT, Action.COOPERATE)].first)
        p = float(mat[(Action.DEFECT, Action.DEFECT)].first)

        # Vector u:
        # u1 = 0
        # u2 = (S - R) - chi * (T - R) = -(R - S) - chi * (T - R)
        # u3 = (T - R) - chi * (S - R) = (T - R) + chi * (R - S)
        # u4 = (P - R) - chi * (P - R) = (chi - 1) * (R - P)
        r_minus_s = r - s
        t_minus_r = t - r
        r_minus_p = r - p

        phi_max = 1.0 / (t_minus_r + chi * r_minus_s)
        chosen_phi = phi_max if phi is None else float(phi)
        if chosen_phi <= 0.0 or chosen_phi > phi_max + 1e-9:
            raise ValueError(
                f"Scaling factor phi must be in (0, {phi_max:.4f}], got {chosen_phi}"
            )

        p_cc = 1.0
        p_cd = 1.0 - chosen_phi * (r_minus_s + chi * t_minus_r)
        p_dc = chosen_phi * (t_minus_r + chi * r_minus_s)
        p_dd = chosen_phi * (chi - 1.0) * r_minus_p

        p_cc = min(1.0, max(0.0, p_cc))
        p_cd = min(1.0, max(0.0, p_cd))
        p_dc = min(1.0, max(0.0, p_dc))
        p_dd = min(1.0, max(0.0, p_dd))

        self.chi = chi
        self.phi = chosen_phi

        super().__init__(
            p_cc=p_cc,
            p_cd=p_cd,
            p_dc=p_dc,
            p_dd=p_dd,
            initial_action=initial_action,
            seed=seed,
        )
