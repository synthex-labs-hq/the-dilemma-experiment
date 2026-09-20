# ADR-014: Strategy Isolation in Tournaments

## Status

Accepted

## Context

ADR-010 established that `Strategy` state is strictly owned by the individual `Strategy` instance and that `Match` does not reset or roll back strategy state.

In a round-robin tournament, an agent interacts sequentially with multiple distinct opponents:
1. `Agent A` plays against `Agent B` for $R$ rounds.
2. Later, `Agent A` plays against `Agent C` for $R$ rounds.

This raises two fundamental questions:
- Does an agent's memory of its interaction with `Agent B` influence its first move against `Agent C`?
- How should multi-tournament trials maintain state isolation between runs?

## Decision

1. **Opponent-Scoped Memory Model**:
   Stateful strategies that remember history (e.g., `TitForTatStrategy`, `GrimTriggerStrategy`) must partition their internal observation state by `opponent_id`.
   When `choose_action()` is called with a `DecisionContext` containing `opponent_id`, the strategy queries history specific to that opponent.
   Therefore, encountering a new opponent in a tournament naturally begins with a clean history without requiring artificial reset hooks on the strategy.

2. **No Memory Leaks Across Unrelated Opponents**:
   A strategy must not retaliate against `Agent C` simply because `Agent B` defected in a prior match (unless an explicit reputation or gossip mechanism is under test in a future episode).

3. **Fresh Population for Independent Trials**:
   If an experimenter runs multiple repeated tournament trials (e.g. Monte Carlo simulations), each tournament run must be initialized with a freshly instantiated `Population`.
   `Tournament` does not inject or require a `reset()` method on `Strategy`, preserving our standard-library-first, minimal-abstraction philosophy.

## Consequences

### Positive
- Matches real-world game theory assumptions where agents recognize their specific counterpart in each match.
- Eliminates the need for complex lifecycle hooks (`reset()`, `tear_down()`) on the `Strategy` interface.
- Leaves the door open for future reputation models (Episode 6) where strategies explicitly query third-party history.

### Negative / Trade-offs
- Stateful strategies must remember to key internal state by `opponent_id` rather than using a single global scalar or list.
