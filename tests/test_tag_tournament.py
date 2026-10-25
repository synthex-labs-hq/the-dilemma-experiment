"""Zero-mock unit tests for TagTournament and TagEvolutionaryTournament (ADR-023, ADR-024)."""

import random

import pytest

from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.tag_tournament import (
    TagEvolutionaryTournament,
    TagTournament,
)
from the_dilemma_experiment.strategies.tag_based import (
    FalseBeardStrategy,
    StrictTribalStrategy,
)


def test_tag_tournament_validation() -> None:
    """Tournament requires at least 2 agents."""
    with pytest.raises(ValueError, match="at least 2 agents"):
        TagTournament(agents=[Agent("single", StrictTribalStrategy())])


def test_categorical_tribal_tournament_ingroup_vs_outgroup() -> None:
    """Tribal agents cooperate 100% within their tribe and defect 100% against out-groups."""
    agents = [
        Agent(f"blue_{i}", StrictTribalStrategy(tag="BLUE")) for i in range(4)
    ] + [
        Agent(f"red_{i}", StrictTribalStrategy(tag="RED")) for i in range(4)
    ]

    tourney = TagTournament(agents=agents, rng=random.Random(42))
    res = tourney.run_stranger_pairings(pairings_per_agent=20)

    # In-group cooperation rate must be 1.0 (100%)
    assert res.in_group_cooperation_rate == 1.0
    # Out-group cooperation rate must be 0.0 (0%)
    assert res.out_group_cooperation_rate == 0.0
    # Both tribes must be balanced
    assert res.tag_shannon_diversity > 0.6


def test_false_beard_exploitation_in_tag_tournament() -> None:
    """A False-Beard agent bearing the in-group tag achieves higher individual score by exploiting cooperators."""
    # 5 honest green tribalists + 1 false-beard green defector
    agents = [
        Agent(f"honest_{i}", StrictTribalStrategy(tag="GREEN")) for i in range(5)
    ] + [
        Agent("false_beard", FalseBeardStrategy(tag="GREEN"))
    ]

    tourney = TagTournament(agents=agents, rng=random.Random(123))
    res = tourney.run_stranger_pairings(pairings_per_agent=30)

    # False-Beard must rank #1 due to unreciprocated exploitation of in-group altruism
    top_agent = res.leaderboard[0]
    assert top_agent.agent_id == "false_beard"
    assert top_agent.strategy_name == "FalseBeardStrategy"


def test_tag_evolutionary_tournament_simulation() -> None:
    """Evolutionary tag tournament steps generations, tracks diversity, and computes metrics."""
    sim = TagEvolutionaryTournament(
        population_size=20,
        tag_mutation_rate=0.2,
        tolerance_mutation_rate=0.2,
        initial_tolerance=0.08,
        rng=random.Random(777),
    )

    history = sim.run_simulation(generations=5, pairings_per_agent=6)

    assert len(history) == 5
    assert all(m.generation == i + 1 for i, m in enumerate(history))
    assert all(0.0 <= m.cooperation_rate <= 1.0 for m in history)
    assert all(m.mean_tolerance >= 0.0 for m in history)
