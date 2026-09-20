# ADR-011: Population Model and Agent Identity

## Status

Accepted

## Context

Episode 1 established the core two-agent interaction model where an `Agent` binds a unique string identifier `id` to a `Strategy` implementation.

In Episode 2, we scale from isolated 1-on-1 matches to multi-agent environments where collections of agents compete across repeated interactions. This introduces several structural requirements:
1. Managing collections of agents with validation that guarantees identity uniqueness.
2. Preventing unintended state coupling caused by sharing stateful `Strategy` instances across multiple agents.
3. Enabling deterministic iteration and lookup by agent ID.
4. Preserving the domain core's principle of immutability.

## Decision

1. **Immutable `Population` Value Object**:
   We introduce a `Population` class that encapsulates a finite collection of `Agent` instances.
   Once instantiated, a `Population` is immutable (backed by an internal tuple of agents).

2. **Strict Identity Uniqueness**:
   Instantiating a `Population` validates that all contained `Agent.id` values are unique non-empty strings. Supplying duplicate agent IDs raises a `ValueError`.

3. **Instance Isolation Check**:
   Instantiating a `Population` validates that each agent possesses a distinct `Strategy` object instance (`id(agent.strategy)` must be unique across all agents in the population). Sharing a single stateful strategy instance across multiple agents violates agent isolation and raises a `ValueError`.

4. **Deterministic Ordering**:
   A `Population` preserves insertion order, guaranteeing that iteration over agents and scheduled pairings are strictly deterministic across runs.

5. **Interface**:
   - `agents`: Returns an immutable tuple of `Agent` instances.
   - `size`: Property returning the total count of agents.
   - `get(agent_id: str) -> Agent`: Retrieves an agent by its unique ID or raises `KeyError`.
   - `contains(agent_id: str) -> bool`: Checks whether an ID exists in the population.
   - Implements `__len__`, `__iter__`, and `__getitem__`.

## Consequences

### Positive
- Prevents identity collisions before matches or tournaments execute.
- Eliminates subtle state leak bugs caused by sharing mutable strategy instances.
- Guarantees deterministic iteration ordering for tournament scheduling.
- Remains lightweight and compliant with standard-library-first design.

### Negative / Trade-offs
- Callers must instantiate separate strategy instances when creating multiple agents of the same behavioral type (e.g., `Agent("tft_1", TitForTatStrategy())` and `Agent("tft_2", TitForTatStrategy())`), rather than passing a shared reference.
