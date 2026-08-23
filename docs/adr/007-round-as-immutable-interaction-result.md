# ADR-007: Round as Immutable Interaction Result

## Status

Proposed

## Context

The Dilemma Experiment models repeated interactions between agents. Each individual interaction produces actions and payoffs that may later be used for debugging, analysis, visualization, reproducibility, and experiment reporting.

A Round should represent what happened during one completed interaction without becoming responsible for executing the interaction itself.

Historical interaction records should also avoid retaining references to mutable Agent objects, since simulations may eventually contain large populations and large numbers of recorded interactions.

## Decision

A `Round` represents one completed interaction between two participants and is modeled as an immutable value object.

A Round contains:

- first participant ID
- second participant ID
- first participant's Action
- second participant's Action
- resulting Payoff

The Round references participants by ID rather than storing Agent objects.

A Round does not:

- choose actions
- resolve game rules
- invoke strategies
- own randomness
- execute simulation logic
- mutate after creation

The conceptual model is:

`Round = participants + actions + payoff`

## Alternatives Considered

- **Store Agent objects in Round:** Creates unnecessary object references in historical records and couples result data to mutable domain entities.
- **Make Round responsible for execution:** Mixes historical result representation with orchestration responsibilities.
- **Store only actions and payoff:** Loses participant identity, making historical results harder to associate with agents and opponents.

## Consequences

- Round is simple, immutable, and easy to serialize.
- Historical interactions do not retain references to Agent objects.
- Round records can be used independently by metrics, exporters, visualization, and future analysis.
- Match remains responsible for orchestration while Round remains a representation of completed interaction.
