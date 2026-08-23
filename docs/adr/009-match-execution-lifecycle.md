# ADR-009: Match Execution Lifecycle

## Status

Proposed

## Context

The Dilemma Experiment models repeated interactions between two Agents. A Match must coordinate the lifecycle of those interactions while preserving the boundaries established between Agent, Strategy, Game, Payoff, and Round.

A Match needs to coordinate action selection, game resolution, historical Round recording, and strategy observation.

Because Strategies may maintain mutable state during repeated interactions, the lifecycle of a Match must also be explicitly defined. Re-executing the same Match could produce ambiguous behavior because strategy state may already have been changed by the previous execution.

## Decision

A `Match` represents one repeated interaction sequence between exactly two Agents using one configured Game.

A Match owns:

- first Agent
- second Agent
- configured Game
- configured round count
- ordered history of completed Rounds
- execution lifecycle

For each round, Match performs the following steps:

1. The first Agent's Strategy chooses an Action.
2. The second Agent's Strategy chooses an Action.
3. Both Actions are resolved through the configured Game.
4. A Round is created containing both participant IDs, both Actions, and the resulting Payoff.
5. The Round is added to Match history.
6. Each Strategy observes the opponent's completed Action.

Both Actions must be chosen before either Strategy is informed of the opponent's current Action.

The first Agent always chooses before the second Agent during execution. This ordering is deterministic and does not expose the first Action to the second Strategy.

A Match may be executed exactly once.

After successful execution:

- the Match is considered completed
- the ordered Round history is preserved
- a second call to `execute()` raises an error

A Match must contain at least one round.

Self-interaction is not allowed. The two participating Agents must have different IDs.

A Match does not:

- implement game-specific payoff rules
- implement strategy decision logic
- own simulation-level randomness
- select participants from a population
- schedule population interactions
- collect population-level metrics

Exceptions raised by Strategies or the configured Game are allowed to propagate. Episode 1 does not introduce failure recovery or partial execution semantics.

## Alternatives Considered

- **Allow repeated execution:** Creates ambiguous behavior because Strategy state may already have changed during the first execution.
- **Reset Match state before re-execution:** Requires defining how Strategy state should also be reset and couples Match to Strategy implementation details.
- **Append additional rounds on repeated execution:** Makes the configured round count and Match lifecycle ambiguous.
- **Simulation executes individual rounds directly:** Weakens the Match boundary by moving interaction orchestration into the higher-level simulation layer.
- **Introduce a separate MatchExecutor or RoundRunner:** Adds unnecessary abstraction for Episode 1.

## Consequences

- Match provides a clear boundary for repeated interaction between two Agents.
- Strategy state remains owned by individual Strategy instances.
- Round remains an immutable historical record of a completed interaction.
- Match lifecycle is deterministic and unambiguous.
- Re-execution is prevented, avoiding accidental reuse of stateful Strategies.
- Simulation can later orchestrate many Match instances without owning low-level interaction execution.
- Future experiments may revise the lifecycle model if materially different interaction requirements emerge.
