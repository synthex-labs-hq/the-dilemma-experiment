"""Zero-mock unit tests for Zero-Determinant strategies and Markov solvers."""

import pytest

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.match import Match
from the_dilemma_experiment.domain.memory_one import (
    MemoryOneStrategy,
    build_markov_transition_matrix,
    compute_theoretical_payoffs,
    solve_stationary_distribution,
)
from the_dilemma_experiment.domain.prisoners_dilemma import PrisonersDilemma
from the_dilemma_experiment.domain.tournament import Tournament
from the_dilemma_experiment.strategies.always_cooperate import AlwaysCooperateStrategy
from the_dilemma_experiment.strategies.always_defect import AlwaysDefectStrategy
from the_dilemma_experiment.strategies.random_strategy import RandomStrategy
from the_dilemma_experiment.strategies.tit_for_tat import TitForTatStrategy
from the_dilemma_experiment.strategies.win_stay_lose_shift import (
    WinStayLoseShiftStrategy,
)
from the_dilemma_experiment.strategies.zero_determinant import (
    EqualizerStrategy,
    ExtortionStrategy,
    GenerousZDStrategy,
)


def test_memory_one_validation_and_decision() -> None:
    """Verify validation and state transitions for MemoryOneStrategy."""
    with pytest.raises(ValueError, match="Probability p_cc"):
        MemoryOneStrategy(p_cc=1.5, p_cd=0.0, p_dc=0.5, p_dd=0.0)

    strat = MemoryOneStrategy(
        p_cc=1.0,
        p_cd=0.0,
        p_dc=1.0,
        p_dd=0.0,
        initial_action=Action.COOPERATE,
        seed=42,
    )
    context = DecisionContext(opponent_id="opp_1")

    # Round 1: Opening move
    act1 = strat.choose_action(context)
    assert act1 == Action.COOPERATE

    # Observe opponent cooperated -> state is CC -> p_cc=1.0 -> COOPERATE
    strat.observe("opp_1", Action.COOPERATE)
    act2 = strat.choose_action(context)
    assert act2 == Action.COOPERATE

    # Observe opponent defected -> state is CD -> p_cd=0.0 -> DEFECT
    strat.observe("opp_1", Action.DEFECT)
    act3 = strat.choose_action(context)
    assert act3 == Action.DEFECT

    # Reset clears history
    strat.reset()
    act_reset = strat.choose_action(context)
    assert act_reset == Action.COOPERATE


def test_markov_transition_matrix_properties() -> None:
    """Verify Markov transition matrix is 4x4, row-stochastic, and bounded."""
    p = (0.8, 0.2, 0.6, 0.1)
    q = (0.7, 0.3, 0.5, 0.0)
    matrix = build_markov_transition_matrix(p, q)

    assert len(matrix) == 4
    for row in matrix:
        assert len(row) == 4
        assert sum(row) == pytest.approx(1.0, abs=1e-12)
        assert all(0.0 <= x <= 1.0 for x in row)


def test_stationary_distribution_solver() -> None:
    """Verify Gaussian elimination solver on ergodic and absorbing chains."""
    # Ergodic chain
    m = [
        [0.7, 0.1, 0.1, 0.1],
        [0.2, 0.5, 0.2, 0.1],
        [0.3, 0.1, 0.4, 0.2],
        [0.1, 0.1, 0.2, 0.6],
    ]
    v = solve_stationary_distribution(m)
    assert sum(v) == pytest.approx(1.0, abs=1e-12)
    # Check v M = v
    for col in range(4):
        col_sum = sum(v[row] * m[row][col] for row in range(4))
        assert col_sum == pytest.approx(v[col], abs=1e-9)

    # Absorbing chain (state 3 is absorbing)
    m_abs = [
        [0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 1.0],
    ]
    v_abs = solve_stationary_distribution(m_abs)
    assert v_abs == [0.0, 0.0, 0.0, 1.0]


def test_extortion_press_dyson_exact_linear_invariant() -> None:
    """Verify Press-Dyson relation (s_X - P) = chi * (s_Y - P) holds exactly."""
    # Standard payoffs: R=3, S=0, T=5, P=1
    p_matrix = PrisonersDilemma().payoff_matrix

    # Test multiple extortion coefficients
    for chi in [1.0, 1.5, 2.0, 3.0, 4.0]:
        extortioner = ExtortionStrategy(chi=chi, payoff_matrix=dict(p_matrix))
        p = extortioner.probabilities

        # Opponent strategies defined as memory-one probabilities:
        opponents = {
            "AllC": (1.0, 1.0, 1.0, 1.0),
            "TFT": (1.0, 0.0, 1.0, 0.0),
            "Random_50": (0.5, 0.5, 0.5, 0.5),
            "WSLS": (1.0, 0.0, 0.0, 1.0),
            "Grim": (1.0, 0.0, 0.0, 0.0),
            "AllD": (0.0, 0.0, 0.0, 0.0),
            "Mixed": (0.8, 0.2, 0.7, 0.1),
        }

        for opp_name, q in opponents.items():
            s_x, s_y = compute_theoretical_payoffs(p, q, dict(p_matrix))
            # Verify Press-Dyson relation: (s_X - 1.0) - chi * (s_Y - 1.0) == 0
            diff = (s_x - 1.0) - chi * (s_y - 1.0)
            assert diff == pytest.approx(0.0, abs=1e-9), (
                f"Failed for chi={chi} against {opp_name}: s_X={s_x}, s_Y={s_y}, diff={diff}"
            )
            # Extortioner must always score >= opponent in pairwise matchup
            assert s_x >= s_y - 1e-9


def test_equalizer_exact_pinning() -> None:
    """Verify Equalizer strategy unilaterally pins opponent's score to constant c."""
    p_matrix = PrisonersDilemma().payoff_matrix

    for target_c in [1.2, 1.8, 2.0, 2.5]:
        equalizer = EqualizerStrategy(target_score=target_c, payoff_matrix=dict(p_matrix))
        p = equalizer.probabilities

        opponents = {
            "AllC": (1.0, 1.0, 1.0, 1.0),
            "TFT": (1.0, 0.0, 1.0, 0.0),
            "Random_50": (0.5, 0.5, 0.5, 0.5),
            "WSLS": (1.0, 0.0, 0.0, 1.0),
            "Grim": (1.0, 0.0, 0.0, 0.0),
            "AllD": (0.0, 0.0, 0.0, 0.0),
        }

        for opp_name, q in opponents.items():
            _s_x, s_y = compute_theoretical_payoffs(p, q, dict(p_matrix))
            # Opponent's score s_Y must be exactly equal to target_c
            assert s_y == pytest.approx(target_c, abs=1e-9), (
                f"Failed for c={target_c} against {opp_name}: got s_Y={s_y}"
            )


def test_generous_zd_exact_cooperation_and_invariant() -> None:
    """Verify Generous ZD achieves mutual cooperation and satisfies (s_X - R) = chi * (s_Y - R)."""
    p_matrix = PrisonersDilemma().payoff_matrix

    for chi in [1.0, 2.0, 3.0]:
        generous = GenerousZDStrategy(chi=chi, payoff_matrix=dict(p_matrix))
        p = generous.probabilities

        # Invariant (s_X - 3.0) - chi * (s_Y - 3.0) == 0 holds against all opponents
        all_opponents = {
            "AllC": (1.0, 1.0, 1.0, 1.0),
            "TFT": (1.0, 0.0, 1.0, 0.0),
            "WSLS": (1.0, 0.0, 0.0, 1.0),
            "AllD": (0.0, 0.0, 0.0, 0.0),
            "Random_50": (0.5, 0.5, 0.5, 0.5),
            "Grim": (1.0, 0.0, 0.0, 0.0),
        }
        for opp_name, q in all_opponents.items():
            s_x, s_y = compute_theoretical_payoffs(p, q, dict(p_matrix))
            diff = (s_x - 3.0) - chi * (s_y - 3.0)
            assert diff == pytest.approx(0.0, abs=1e-9), (
                f"Failed invariant for chi={chi} against {opp_name}: s_X={s_x}, s_Y={s_y}, diff={diff}"
            )

        # For chi > 1, Generous ZD acts as an attractor to full mutual cooperation against TFT/WSLS
        if chi > 1.0:
            for opp_name in ["AllC", "TFT", "WSLS"]:
                s_x, s_y = compute_theoretical_payoffs(p, all_opponents[opp_name], dict(p_matrix))
                assert s_x == pytest.approx(3.0, abs=1e-9)
                assert s_y == pytest.approx(3.0, abs=1e-9)


def test_empirical_match_converges_to_theoretical() -> None:
    """Verify empirical multi-round match closely matches the Markov theoretical prediction."""
    chi = 3.0
    extortioner_strat = ExtortionStrategy(chi=chi, seed=123)
    random_strat = RandomStrategy(cooperation_probability=0.5, seed=456)

    agent_a = Agent("Extortioner", extortioner_strat)
    agent_b = Agent("Random50", random_strat)

    # 4,000 rounds match
    game = PrisonersDilemma()
    match = Match(first_agent=agent_a, second_agent=agent_b, game=game, round_count=4000)
    match.execute()
    assert match.result is not None

    p = extortioner_strat.probabilities
    q = (0.5, 0.5, 0.5, 0.5)
    theo_x, theo_y = compute_theoretical_payoffs(p, q, dict(game.payoff_matrix))

    empirical_avg_x = match.result.first_score / 4000.0
    empirical_avg_y = match.result.second_score / 4000.0

    # Within 4% of theoretical expected payoff
    assert empirical_avg_x == pytest.approx(theo_x, rel=0.04)
    assert empirical_avg_y == pytest.approx(theo_y, rel=0.04)

    # Check empirical extortion ratio: (s_X - 1.0) / (s_Y - 1.0)
    emp_diff_x = empirical_avg_x - 1.0
    emp_diff_y = empirical_avg_y - 1.0
    emp_ratio = emp_diff_x / emp_diff_y
    assert emp_ratio == pytest.approx(chi, rel=0.10)


def test_extortioner_in_population_tournament() -> None:
    """Verify that Extortioner wins pairwise matches against cooperators, illustrating the ZD paradox."""
    game = PrisonersDilemma()
    agents = [
        Agent("Extort_1", ExtortionStrategy(chi=3.0, seed=1)),
        Agent("TFT_1", TitForTatStrategy()),
        Agent("WSLS_1", WinStayLoseShiftStrategy()),
        Agent("AllC_1", AlwaysCooperateStrategy()),
        Agent("AllD_1", AlwaysDefectStrategy()),
    ]

    from the_dilemma_experiment.domain.population import Population

    pop = Population(agents=agents)
    tournament = Tournament(population=pop, game=game, rounds_per_match=200)
    tournament.execute()

    # Find matches involving Extort_1
    extort_matches = [
        m for m in tournament.matches
        if m.result is not None and "Extort_1" in (m.result.first_agent_id, m.result.second_agent_id)
    ]

    for m in extort_matches:
        assert m.result is not None
        if m.result.first_agent_id == "Extort_1":
            extort_score = m.result.first_score
            opp_score = m.result.second_score
            opp_id = m.result.second_agent_id
        else:
            extort_score = m.result.second_score
            opp_score = m.result.first_score
            opp_id = m.result.first_agent_id

        # In matches against AllC, WSLS, and TFT, Extortioner achieves pairwise victory (extort >= opp)
        if opp_id in ("AllC_1", "WSLS_1", "TFT_1"):
            assert extort_score >= opp_score
