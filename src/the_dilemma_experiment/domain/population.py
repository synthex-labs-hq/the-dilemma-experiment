from collections.abc import Iterable, Iterator
from typing import overload

from the_dilemma_experiment.domain.agent import Agent


class Population:
    """Immutable collection of distinct Agent instances for multi-agent simulations."""

    def __init__(self, agents: Iterable[Agent]) -> None:
        agents_tuple = tuple(agents)
        if not agents_tuple:
            raise ValueError("Population must contain at least one agent")

        seen_ids: set[str] = set()
        seen_strategies: set[int] = set()

        for agent in agents_tuple:
            if not isinstance(agent, Agent):
                raise TypeError(f"All members of Population must be Agent instances, got {type(agent)}")
            if not agent.id or not isinstance(agent.id, str):
                raise ValueError("Agent id must be a non-empty string")
            if agent.id in seen_ids:
                raise ValueError(f"Duplicate agent id '{agent.id}' found in population")
            seen_ids.add(agent.id)

            strategy_obj_id = id(agent.strategy)
            if strategy_obj_id in seen_strategies:
                raise ValueError(
                    f"Agent '{agent.id}' shares a Strategy instance with another agent in the population. "
                    "Per ADR-011, each agent must possess a distinct Strategy instance."
                )
            seen_strategies.add(strategy_obj_id)

        self._agents: tuple[Agent, ...] = agents_tuple
        self._agents_by_id: dict[str, Agent] = {a.id: a for a in agents_tuple}

    @property
    def agents(self) -> tuple[Agent, ...]:
        """Immutable sequence of agents in the population."""
        return self._agents

    @property
    def size(self) -> int:
        """The number of agents in the population."""
        return len(self._agents)

    def get(self, agent_id: str) -> Agent:
        """Retrieve an agent by ID or raise KeyError."""
        if agent_id not in self._agents_by_id:
            raise KeyError(f"Agent '{agent_id}' not found in population")
        return self._agents_by_id[agent_id]

    def contains(self, agent_id: str) -> bool:
        """Check if an agent ID exists in the population."""
        return agent_id in self._agents_by_id

    def __len__(self) -> int:
        return len(self._agents)

    def __iter__(self) -> Iterator[Agent]:
        return iter(self._agents)

    @overload
    def __getitem__(self, index: int) -> Agent: ...

    @overload
    def __getitem__(self, index: slice) -> tuple[Agent, ...]: ...

    @overload
    def __getitem__(self, index: str) -> Agent: ...

    def __getitem__(self, index: int | slice | str) -> Agent | tuple[Agent, ...]:
        if isinstance(index, str):
            return self.get(index)
        return self._agents[index]

    def __contains__(self, item: object) -> bool:
        if isinstance(item, str):
            return item in self._agents_by_id
        if isinstance(item, Agent):
            return item in self._agents
        return False

    def __repr__(self) -> str:
        ids = [a.id for a in self._agents]
        return f"Population(size={len(self._agents)}, agents={ids})"
