# ADR-009: Strategy State and Lifecycle

## Status

Proposed

## Context

During the implementation of repeated Match execution and retry semantics, the relationship between Match execution, Agent identity, and Strategy state was identified.

In Episode 1:
- `Agent` binds an identifier to a `Strategy`.
- `Strategy` implementations may be stateless (e.g., `AlwaysCooperateStrategy`, `AlwaysDefectStrategy`) or stateful (e.g., `TitForTatStrategy`, which tracks opponent-specific history).
- `Match` owns repeated interaction orchestration, temporary execution state, and committed history/results.

When a `Match` attempt fails mid-execution (e.g., due to an exception raised by a strategy or game), `Match`-owned temporary state is discarded, ensuring `Match` state is restored atomically upon retry. However, any strategy observations made prior to the failure persist on the participating `Strategy` instances.

This requires explicitly establishing ownership, boundary, and lifecycle rules for `Strategy` state across matches and retries.

## Decision

1. **Strategy Ownership**: A `Strategy` instance is owned by an `Agent`. Strategy state belongs strictly to the individual `Strategy` instance.
2. **Match Boundary**: A `Match` invokes `choose_action()` and `observe()` on `Strategy` instances but does not own `Strategy` lifecycle or state.
3. **No Strategy Lifecycle Operations in Match**: `Match` must not reset, clone, snapshot, restore, or roll back `Strategy` state.
4. **State Persistence Across Matches**: Reusing the same `Agent` and `Strategy` instance across multiple `Match` instances preserves `Strategy` state. A stateful strategy will retain memory from prior matches when reused with the same opponent.
5. **Strategy Instance Isolation**: Stateful strategies should use independent `Strategy` instances per `Agent`. For example:
   ```python
   # Recommended (independent instances)
   agent_a = Agent("agent_a", TitForTatStrategy())
   agent_b = Agent("agent_b", TitForTatStrategy())

   # Discouraged (shared instance)
   shared_strategy = TitForTatStrategy()
   agent_a = Agent("agent_a", shared_strategy)
   agent_b = Agent("agent_b", shared_strategy)
   ```
   This rule is an architectural usage guideline and is not enforced at runtime in Episode 1.
6. **Match Retry Scope**: Match retry restores only `Match`-owned state. `Strategy` state is NOT rolled back when a `Match` attempt fails.
7. **Minimal Abstraction Policy**: Episode 1 deliberately does not introduce `reset()`, `clone()`, `snapshot()`, `restore()`, or transactional strategy mechanisms. Such lifecycle methods will be reconsidered only when higher-level simulation, tournament, or experiment orchestrators create a concrete requirement.

## Alternatives Considered

- **Implement `Strategy.reset()` or `Strategy.clone()`**: Couples `Match` or `Agent` to strategy lifecycle management and introduces premature abstractions before tournament requirements are established.
- **Implement transactional strategy rollback on Match failure**: Adds complex state management, cloning, or snapshot mechanisms to the domain core.
- **Enforce single-agent ownership of Strategy instances at runtime**: Introduces runtime checks or factory patterns that bloat the lightweight Episode 1 domain models.

## Consequences

### Positive
- Clear, unambiguous ownership of strategy state.
- `Match` remains focused strictly on interaction orchestration.
- Supports persistent per-opponent memory across repeated matches.
- Lays the foundation for future reputation-based and evolutionary behavior.
- Keeps `Strategy` implementations lightweight and self-contained.

### Negative / Trade-offs
- Failed `Match` attempts cannot automatically restore `Strategy` state.
- Reusing an `Agent` instance carries state between separate matches.
- Sharing a single stateful `Strategy` instance across multiple agents creates unintended state coupling.
- A future higher-level lifecycle abstraction (e.g., tournament runner) may need to manage strategy recreation or resetting.
