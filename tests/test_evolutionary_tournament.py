import pytest

from the_dilemma_experiment.domain.evolutionary_tournament import (
    EvolutionaryTournament,
)
from the_dilemma_experiment.domain.generation_result import GenerationResult
from the_dilemma_experiment.strategies.always_cooperate import (
    AlwaysCooperateStrategy,
)
from the_dilemma_experiment.strategies.always_defect import (
    AlwaysDefectStrategy,
)
from the_dilemma_experiment.strategies.tit_for_tat import (
    TitForTatStrategy,
)


def test_evolutionary_tournament_validation():
    """Verify input validation for EvolutionaryTournament initialization."""
    # Empty population
    with pytest.raises(ValueError, match="non-empty mapping"):
        EvolutionaryTournament(initial_population={})

    # Population size < 2
    with pytest.raises(ValueError, match="at least 2 agents"):
        EvolutionaryTournament(initial_population={AlwaysCooperateStrategy: 1})

    # Negative count
    with pytest.raises(ValueError, match="non-negative integer"):
        EvolutionaryTournament(
            initial_population={AlwaysCooperateStrategy: -5, AlwaysDefectStrategy: 10}
        )

    # rounds_per_match < 1
    with pytest.raises(ValueError, match="rounds_per_match must be an integer >= 1"):
        EvolutionaryTournament(
            initial_population={AlwaysCooperateStrategy: 5, AlwaysDefectStrategy: 5},
            rounds_per_match=0,
        )

    # Invalid noise
    with pytest.raises(ValueError, match="noise must be between 0.0 and 1.0"):
        EvolutionaryTournament(
            initial_population={AlwaysCooperateStrategy: 5, AlwaysDefectStrategy: 5},
            noise=1.5,
        )

    with pytest.raises(TypeError, match="noise must be a float or int"):
        EvolutionaryTournament(
            initial_population={AlwaysCooperateStrategy: 5, AlwaysDefectStrategy: 5},
            noise="bad",  # type: ignore[arg-type]
        )

    # Invalid seed
    with pytest.raises(TypeError, match="seed must be an integer or None"):
        EvolutionaryTournament(
            initial_population={AlwaysCooperateStrategy: 5, AlwaysDefectStrategy: 5},
            seed="seed",  # type: ignore[arg-type]
        )

    # Invalid game
    with pytest.raises(TypeError, match="Game instance"):
        EvolutionaryTournament(
            initial_population={AlwaysCooperateStrategy: 5, AlwaysDefectStrategy: 5},
            game="not_game",  # type: ignore[arg-type]
        )

    # Invalid strategy spec
    with pytest.raises(TypeError, match="Strategy specification"):
        EvolutionaryTournament(
            initial_population={"NotAStrategy": 10, AlwaysDefectStrategy: 10}  # type: ignore[arg-type]
        )


def test_population_conservation_across_generations():
    """Verify that total population N is strictly conserved across all generations per ADR-017."""
    n_pop = 25
    evo = EvolutionaryTournament(
        initial_population={
            AlwaysCooperateStrategy: 10,
            AlwaysDefectStrategy: 10,
            TitForTatStrategy: 5,
        },
        rounds_per_match=5,
        seed=42,
    )

    assert evo.carrying_capacity == n_pop
    results = evo.run(generations=6)

    for res in results:
        assert res.total_population == n_pop
        assert sum(res.population_counts.values()) == n_pop
        assert sum(evo.current_counts.values()) == n_pop


def test_altruist_predator_extinction_dynamic():
    """Verify that AlwaysDefect exploits and drives AlwaysCooperate to extinction."""
    evo = EvolutionaryTournament(
        initial_population={
            AlwaysCooperateStrategy: 10,
            AlwaysDefectStrategy: 10,
        },
        rounds_per_match=5,
        seed=100,
    )

    results = evo.run(generations=10)

    # AlwaysDefect should increase in generation 1 because it exploits AlwaysCooperate
    first_gen = results[0]
    assert first_gen.population_counts["AlwaysCooperateStrategy"] == 10
    assert first_gen.population_counts["AlwaysDefectStrategy"] == 10
    assert (
        first_gen.average_fitness["AlwaysDefectStrategy"]
        > first_gen.average_fitness["AlwaysCooperateStrategy"]
    )

    # Within a few generations, AlwaysCooperate must go extinct
    final_gen = results[-1]
    assert "AlwaysCooperateStrategy" in final_gen.extinct_strategies
    assert evo.is_converged
    assert evo.current_counts["AlwaysDefectStrategy"] == 20
    assert evo.current_counts["AlwaysCooperateStrategy"] == 0


def test_neutral_equilibrium_between_cooperators():
    """Verify that AlwaysCooperate and TitForTat maintain stable counts in a defect-free noiseless world."""
    evo = EvolutionaryTournament(
        initial_population={
            AlwaysCooperateStrategy: 10,
            TitForTatStrategy: 10,
        },
        rounds_per_match=5,
        noise=0.0,
    )

    results = evo.run(generations=4)

    # In a pure cooperator world with no noise, both score identical 3 pts/round
    for res in results:
        assert (
            res.average_fitness["AlwaysCooperateStrategy"]
            == res.average_fitness["TitForTatStrategy"]
        )
        assert res.population_counts["AlwaysCooperateStrategy"] == 10
        assert res.population_counts["TitForTatStrategy"] == 10


def test_deterministic_reproducibility_with_seed():
    """Verify that two evolutionary runs with identical seeds produce identical trajectories."""
    init_pop = {
        AlwaysCooperateStrategy: 8,
        AlwaysDefectStrategy: 8,
        TitForTatStrategy: 8,
    }

    evo1 = EvolutionaryTournament(init_pop, rounds_per_match=5, noise=0.05, seed=12345)
    evo2 = EvolutionaryTournament(init_pop, rounds_per_match=5, noise=0.05, seed=12345)

    res1 = evo1.run(generations=5)
    res2 = evo2.run(generations=5)

    assert len(res1) == len(res2)
    for r1, r2 in zip(res1, res2, strict=True):
        assert r1.generation == r2.generation
        assert r1.population_counts == r2.population_counts
        assert r1.average_fitness == r2.average_fitness
        assert r1.extinct_strategies == r2.extinct_strategies


def test_strategy_factory_callables_and_instances():
    """Verify EvolutionaryTournament accepts strategy factory callables and strategy instances."""
    evo = EvolutionaryTournament(
        initial_population={
            (lambda: TitForTatStrategy()): 10,
            AlwaysDefectStrategy(): 10,
        },
        rounds_per_match=3,
        seed=1,
    )

    assert evo.carrying_capacity == 20
    res = evo.step()
    assert isinstance(res, GenerationResult)
    assert "TitForTatStrategy" in res.population_counts
    assert "AlwaysDefectStrategy" in res.population_counts


def test_generation_result_to_dict():
    """Verify GenerationResult serialization via to_dict()."""
    evo = EvolutionaryTournament(
        initial_population={
            AlwaysCooperateStrategy: 10,
            AlwaysDefectStrategy: 10,
        },
        rounds_per_match=3,
        retain_tournament_results=True,
    )

    res = evo.step()
    d_no_tourn = res.to_dict(include_tournament=False)
    assert d_no_tourn["generation"] == 0
    assert d_no_tourn["total_population"] == 20
    assert "tournament" not in d_no_tourn

    d_tourn = res.to_dict(include_tournament=True)
    assert "tournament" in d_tourn
    assert d_tourn["tournament"]["total_matches"] == 190  # 20*19/2
