import pytest

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.match import Match
from the_dilemma_experiment.domain.population import Population
from the_dilemma_experiment.domain.prisoners_dilemma import PrisonersDilemma
from the_dilemma_experiment.domain.round import Round
from the_dilemma_experiment.domain.tournament import Tournament
from the_dilemma_experiment.strategies.always_cooperate import AlwaysCooperateStrategy
from the_dilemma_experiment.strategies.always_defect import AlwaysDefectStrategy
from the_dilemma_experiment.strategies.tit_for_tat import TitForTatStrategy


def test_action_opposite():
    """Verify Action.opposite() inverts actions correctly."""
    assert Action.COOPERATE.opposite() == Action.DEFECT
    assert Action.DEFECT.opposite() == Action.COOPERATE


def test_round_intended_actions_and_noise_flag():
    """Verify Round tracks intended actions and detects noise alteration."""
    game = PrisonersDilemma()
    payoff = game.resolve(Action.COOPERATE, Action.COOPERATE)

    # Clean round without noise
    clean_round = Round(
        first_agent_id="a1",
        second_agent_id="a2",
        first_action=Action.COOPERATE,
        second_action=Action.COOPERATE,
        payoff=payoff,
        first_intended_action=Action.COOPERATE,
        second_intended_action=Action.COOPERATE,
    )
    assert not clean_round.is_noisy

    # Noisy round where first action was flipped
    noisy_round_1 = Round(
        first_agent_id="a1",
        second_agent_id="a2",
        first_action=Action.DEFECT,
        second_action=Action.COOPERATE,
        payoff=game.resolve(Action.DEFECT, Action.COOPERATE),
        first_intended_action=Action.COOPERATE,
        second_intended_action=Action.COOPERATE,
    )
    assert noisy_round_1.is_noisy

    # Noisy round where second action was flipped
    noisy_round_2 = Round(
        first_agent_id="a1",
        second_agent_id="a2",
        first_action=Action.COOPERATE,
        second_action=Action.DEFECT,
        payoff=game.resolve(Action.COOPERATE, Action.DEFECT),
        first_intended_action=Action.COOPERATE,
        second_intended_action=Action.COOPERATE,
    )
    assert noisy_round_2.is_noisy

    # Backwards-compatible round where intended actions are None
    legacy_round = Round(
        first_agent_id="a1",
        second_agent_id="a2",
        first_action=Action.COOPERATE,
        second_action=Action.COOPERATE,
        payoff=payoff,
    )
    assert not legacy_round.is_noisy


def test_match_noise_validation():
    """Verify Match validates noise and seed parameters."""
    game = PrisonersDilemma()
    a1 = Agent("a1", AlwaysCooperateStrategy())
    a2 = Agent("a2", AlwaysDefectStrategy())

    # noise must be float/int, not bool
    with pytest.raises(TypeError, match="noise must be a float or int"):
        Match(a1, a2, game, 5, noise=True)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="noise must be a float or int"):
        Match(a1, a2, game, 5, noise="0.5")  # type: ignore[arg-type]

    # noise must be between 0.0 and 1.0
    with pytest.raises(ValueError, match="noise must be between 0.0 and 1.0"):
        Match(a1, a2, game, 5, noise=-0.01)

    with pytest.raises(ValueError, match="noise must be between 0.0 and 1.0"):
        Match(a1, a2, game, 5, noise=1.01)

    # seed must be int or None
    with pytest.raises(TypeError, match="seed must be an integer or None"):
        Match(a1, a2, game, 5, noise=0.1, seed="invalid")  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="seed must be an integer or None"):
        Match(a1, a2, game, 5, noise=0.1, seed=True)  # type: ignore[arg-type]


def test_match_zero_noise_identity():
    """Verify Match with noise=0.0 produces identical intended and executed actions."""
    game = PrisonersDilemma()
    a1 = Agent("a1", AlwaysCooperateStrategy())
    a2 = Agent("a2", AlwaysDefectStrategy())

    match = Match(a1, a2, game, round_count=10, noise=0.0)
    rounds = match.execute()

    assert match.noise == 0.0
    for r in rounds:
        assert not r.is_noisy
        assert r.first_action == Action.COOPERATE
        assert r.first_intended_action == Action.COOPERATE
        assert r.second_action == Action.DEFECT
        assert r.second_intended_action == Action.DEFECT


def test_match_full_noise_inversion():
    """Verify Match with noise=1.0 flips every single intended action."""
    game = PrisonersDilemma()
    a1 = Agent("a1", AlwaysCooperateStrategy())
    a2 = Agent("a2", AlwaysDefectStrategy())

    match = Match(a1, a2, game, round_count=10, noise=1.0, seed=42)
    rounds = match.execute()

    for r in rounds:
        assert r.is_noisy
        # a1 intended COOPERATE, was flipped to DEFECT
        assert r.first_intended_action == Action.COOPERATE
        assert r.first_action == Action.DEFECT
        # a2 intended DEFECT, was flipped to COOPERATE
        assert r.second_intended_action == Action.DEFECT
        assert r.second_action == Action.COOPERATE
        # Payoff reflects executed actions (DEFECT vs COOPERATE -> 5, 0)
        assert r.payoff.first == 5
        assert r.payoff.second == 0


def test_match_noise_determinism():
    """Verify Match with fixed seed produces strictly identical noisy execution."""
    game = PrisonersDilemma()

    def run_noisy_match(seed: int):
        a1 = Agent("a1", AlwaysCooperateStrategy())
        a2 = Agent("a2", AlwaysCooperateStrategy())
        m = Match(a1, a2, game, round_count=20, noise=0.25, seed=seed)
        m.execute()
        return [(r.first_action, r.second_action, r.is_noisy) for r in m.rounds]

    run1 = run_noisy_match(seed=999)
    run2 = run_noisy_match(seed=999)
    run3 = run_noisy_match(seed=123)

    assert run1 == run2
    assert run1 != run3


def test_tournament_noise_and_seed_determinism():
    """Verify Tournament accepts noise and seed and executes deterministically."""
    game = PrisonersDilemma()
    agents_1 = [
        Agent("a1", AlwaysCooperateStrategy()),
        Agent("a2", AlwaysDefectStrategy()),
        Agent("a3", TitForTatStrategy()),
    ]
    pop1 = Population(agents_1)
    t1 = Tournament(pop1, game, rounds_per_match=15, noise=0.1, seed=42)
    res1 = t1.execute()

    assert t1.noise == 0.1
    assert t1.seed == 42
    assert res1.noise == 0.1

    agents_2 = [
        Agent("a1", AlwaysCooperateStrategy()),
        Agent("a2", AlwaysDefectStrategy()),
        Agent("a3", TitForTatStrategy()),
    ]
    pop2 = Population(agents_2)
    t2 = Tournament(pop2, game, rounds_per_match=15, noise=0.1, seed=42)
    res2 = t2.execute()

    # Exact deterministic identity across all leaderboard metrics
    for e1, e2 in zip(res1.leaderboard, res2.leaderboard):
        assert e1.agent_id == e2.agent_id
        assert e1.total_score == e2.total_score
        assert e1.cooperation_rate == e2.cooperation_rate
