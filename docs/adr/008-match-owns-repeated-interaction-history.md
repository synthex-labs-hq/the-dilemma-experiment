# ADR-008: Match Owns Repeated Interaction History

## Status

Proposed

## Context

The Prisoner's Dilemma is a repeated game in which the same pair of agents interacts across multiple rounds. Strategies such as Tit-for-Tat depend on observations from previous rounds, while the experiment also needs a record of completed interactions for analysis and reproducibility.

The architecture must distinguish between:

1. interaction history belonging to the Match, and
2. decision-making state belonging to an individual Strategy.

A Match should coordinate the interaction lifecycle without embedding game-specific payoff rules or strategy behaviour.

## Decision

A `Match` represents repeated interaction between two Agents and owns the ordered history of completed Rounds.

The Match is responsible for orchestrating each interaction:

1. Request an Action from the first Agent's Strategy.
2. Request an Action from the second Agent's Strategy.
3. Resolve both Actions through the configured Game.
4. Record the resulting interaction as a Round.
5. Notify both Strategies of the completed interaction.
6. Repeat for the configured number of rounds.

Both Strategies must choose their Actions before either Strategy is informed of the opponent's current Action.

Strategy observation therefore occurs only after Game resolution.

The Match does not:

- implement game-specific payoff rules
- own strategy decision logic
- own the simulation's controlled random number generator
- modify Agent identity
- expose current-round actions to a Strategy before its decision

## Alternatives Considered

- **Simulation owns individual round execution:** Makes the simulation orchestrator responsible for lower-level interaction mechanics and weakens the Match boundary.
- **Round owns execution:** Couples a historical result object to orchestration responsibilities.
- **Strategy owns Match history:** Couples decision-making state to the entire interaction record and makes shared match history difficult to manage.
- **Strategies observe before both decisions are made:** Allows current-round information to influence decisions and violates the simultaneous-action model of the Prisoner's Dilemma.

## Consequences

- Match provides a clear boundary for repeated interaction between two agents.
- Round remains a simple immutable record of completed interaction.
- Strategies can maintain private decision-making state independently from Match history.
- The observation order preserves simultaneous decision-making semantics.
- Match history can later support metrics, debugging, visualization, and experiment analysis.
- The design remains specific to Episode 1 and may be revised if future experiments require materially different interaction models.
