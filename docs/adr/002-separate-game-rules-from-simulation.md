# ADR-002: Separate Game Rules from Simulation

## Status

Proposed

## Context

The initial focus of the project is the Prisoner's Dilemma, but future episodes may involve other game-theoretic models (e.g., Stag Hunt, Snowdrift, Public Goods). Embedding payoff matrices or resolution logic directly inside the simulation engine or strategy implementations tightens coupling and makes future extension difficult.

## Decision

Game rules are separated from simulation orchestration.

- A `Strategy` chooses an `Action`.
- The `Game` resolves the actions into `Payoffs`.
- The `Simulation` controls population interaction, scheduling, execution, and orchestration.
- The `Simulation` must not contain Prisoner's Dilemma payoff logic.
- The architecture should allow future games to reuse the simulation machinery without modifying orchestration logic.

## Alternatives Considered

- **Put game rules directly in Simulation:** Hardcodes payoff logic into execution loops, preventing reuse across game types.
- **Put payoff logic inside Strategy:** Requires strategies to know global outcome matrices, violating encapsulation.
- **Build a generic rules-engine framework immediately:** Introduces premature abstraction and over-engineering before multiple games exist.

## Consequences

- Clear domain boundaries between strategy decision-making, game resolution, and simulation execution.
- Enables swapping game definitions while keeping simulation orchestration intact.
- Avoids complex framework abstractions while preserving extensibility.
