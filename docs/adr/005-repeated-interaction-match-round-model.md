# ADR-005: Repeated Interaction as Match → Rounds

## Status

Proposed

## Context

Key game-theoretic strategies, such as Tit-for-Tat, rely on repeated interactions between identical agents to establish history, memory, and reciprocity. Distinguishing between multiple pairings (matches) and sequential interactions within a pairing (rounds) is essential for correct domain modeling.

## Decision

Repeated interaction is modeled as: `Simulation` → `Match` → `Rounds`.

- A `Match` represents repeated interaction between two agents.
- A `Match` contains a configurable number of `Rounds`.
- Match count and rounds per match must be independently configurable.
- The experiment must distinguish between the number of matches and the number of individual rounds.


## Alternatives Considered

- **Every interaction is a single independent round:** Prevents stateful strategies from observing history across interactions with the same opponent.
- **Round-robin tournament as the default:** Imposes fixed pairing constraints that limit stochastic or configurable scheduling models.
- **One global match involving the entire population:** Erases boundaries between distinct pairings and opponent memories.

## Consequences

- Accurately models repeated games, supporting conditional/reactive strategies.
- Provides a clear structural distinction between simulation orchestration, match pairing, and sequential round execution.
- Allows match count and rounds per match to be configured independently.
