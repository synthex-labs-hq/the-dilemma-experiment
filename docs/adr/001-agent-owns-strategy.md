# ADR-001: Agent Owns Strategy

## Status

Proposed

## Context

In game-theoretic simulations, participants need both identity (tracking scores, history, or metadata) and behavioral decision-making (selecting moves based on history or state). Coupling identity and strategy into a single abstraction limits flexibility when multiple participants use the same behavioral strategy.

## Decision

An `Agent` represents an individual participant and owns a `Strategy` instance.

- `Agent` and `Strategy` are separate domain concepts.
- The `Strategy` defines decision-making behaviour.
- The `Agent` provides identity and owns the strategy instance.
- This allows agents using the same strategy type to maintain independent strategy state.

## Alternatives Considered

- **Agent is itself a strategy:** Conflates identity with decision rules and complicates state isolation.
- **Strategy is globally shared/stateless:** Prevents strategies from encapsulating agent-specific state or memory.
- **Simulation owns strategy state:** Obscures domain encapsulation by moving participant logic into the orchestrator.

## Consequences

- Clean separation between agent identity and decision logic.
- Multiple agents can instantiate the same strategy class independently without state bleeding between participants.
- Introduces object composition where `Agent` delegates decision choices to its encapsulated `Strategy`.
