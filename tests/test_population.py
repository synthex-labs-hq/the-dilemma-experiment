import pytest

from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.population import Population
from the_dilemma_experiment.strategies.always_cooperate import (
    AlwaysCooperateStrategy,
)
from the_dilemma_experiment.strategies.always_defect import (
    AlwaysDefectStrategy,
)
from the_dilemma_experiment.strategies.tit_for_tat import (
    TitForTatStrategy,
)


def test_population_creation_success():
    """Verify valid agents can create an immutable Population."""
    a1 = Agent("a1", AlwaysCooperateStrategy())
    a2 = Agent("a2", AlwaysDefectStrategy())
    a3 = Agent("a3", TitForTatStrategy())

    pop = Population([a1, a2, a3])

    assert pop.size == 3
    assert len(pop) == 3
    assert pop.agents == (a1, a2, a3)


def test_population_rejects_empty():
    """Verify empty iterable raises ValueError."""
    with pytest.raises(ValueError, match="at least one agent"):
        Population([])


def test_population_rejects_non_agent_elements():
    """Verify non-Agent objects raise TypeError."""
    with pytest.raises(TypeError, match="must be Agent instances"):
        Population(["not_an_agent"])  # type: ignore[arg-type]


def test_population_rejects_duplicate_agent_ids():
    """Verify duplicate agent IDs raise ValueError per ADR-011."""
    a1 = Agent("duplicate_id", AlwaysCooperateStrategy())
    a2 = Agent("duplicate_id", AlwaysDefectStrategy())

    with pytest.raises(ValueError, match="Duplicate agent id 'duplicate_id'"):
        Population([a1, a2])


def test_population_rejects_shared_strategy_instances():
    """Verify sharing the same strategy instance raises ValueError per ADR-011."""
    shared_strategy = TitForTatStrategy()
    a1 = Agent("a1", shared_strategy)
    a2 = Agent("a2", shared_strategy)

    with pytest.raises(ValueError, match="shares a Strategy instance"):
        Population([a1, a2])


def test_population_lookup_by_id():
    """Verify get() and bracket notation retrieve the correct agent."""
    a1 = Agent("alpha", AlwaysCooperateStrategy())
    a2 = Agent("beta", AlwaysDefectStrategy())
    pop = Population([a1, a2])

    assert pop.get("alpha") is a1
    assert pop["alpha"] is a1
    assert pop.get("beta") is a2
    assert pop["beta"] is a2

    with pytest.raises(KeyError, match="not found"):
        pop.get("gamma")

    with pytest.raises(KeyError, match="not found"):
        _ = pop["gamma"]


def test_population_indexing_and_slicing():
    """Verify integer indexing and slicing."""
    a1 = Agent("a1", AlwaysCooperateStrategy())
    a2 = Agent("a2", AlwaysDefectStrategy())
    a3 = Agent("a3", TitForTatStrategy())
    pop = Population([a1, a2, a3])

    assert pop[0] is a1
    assert pop[1] is a2
    assert pop[2] is a3
    assert pop[0:2] == (a1, a2)


def test_population_membership_contains():
    """Verify 'in' operator for IDs and Agent instances."""
    a1 = Agent("a1", AlwaysCooperateStrategy())
    a2 = Agent("a2", AlwaysDefectStrategy())
    pop = Population([a1, a2])

    assert "a1" in pop
    assert "a2" in pop
    assert "unknown" not in pop

    assert a1 in pop
    assert a2 in pop
    assert Agent("other", AlwaysCooperateStrategy()) not in pop


def test_population_iteration():
    """Verify population is iterable in insertion order."""
    agents = [
        Agent(f"agent_{i}", AlwaysCooperateStrategy())
        for i in range(5)
    ]
    pop = Population(agents)

    iterated = list(pop)
    assert iterated == agents


def test_population_repr():
    """Verify readable string representation."""
    a1 = Agent("x", AlwaysCooperateStrategy())
    a2 = Agent("y", AlwaysDefectStrategy())
    pop = Population([a1, a2])

    assert "Population(size=2, agents=['x', 'y'])" in repr(pop)
