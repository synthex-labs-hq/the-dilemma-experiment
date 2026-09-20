# ADR-012: Tournament Round-Robin Protocol

## Status

Accepted

## Context

In game-theoretic studies of cooperation (specifically Robert Axelrod's seminal 1980 tournaments), strategies are evaluated by interacting repeatedly with all other participants in a round-robin format.

To simulate this within The Dilemma Experiment:
1. We need a clean orchestrator (`Tournament`) that accepts a `Population`, a `Game`, and a configuration for `rounds_per_match`.
2. We must define the scheduling rules for agent pairings (which agents play against whom and how many times).
3. We must preserve atomic match execution and deterministic sequencing.

## Decision

1. **Round-Robin Pairing Without Self-Play**:
   In our standard tournament protocol, every distinct pair of agents $(A, B)$ where $A \neq B$ plays exactly one `Match` of $R$ rounds. For a population of $N$ agents, the total number of matches scheduled is:
   $$\frac{N(N - 1)}{2}$$
   An agent does not play against its own identity instance. (If an experimenter desires to test strategy self-play, they include multiple distinct agents instantiated with that strategy, e.g., `tft_1` and `tft_2`).

2. **Deterministic Canonical Pairing Order**:
   Matches are scheduled in deterministic lexicographical or population-order combinations using Python's `itertools.combinations(population.agents, 2)`.

3. **Leveraging Atomic Match Execution**:
   Each pairing is orchestrated using the Episode 1 `Match` domain object (`Match(first_agent, second_agent, game, round_count=rounds_per_match)`).
   If any individual match fails during tournament execution, the failure is immediately propagated, ensuring invalid or partial tournament data is never marked as complete.

4. **Minimum Population Constraint**:
   A tournament requires at least 2 distinct agents. Attempting to initialize a tournament with a population smaller than 2 raises a `ValueError`.

5. **Rounds Per Match Constraint**:
   `rounds_per_match` must be an integer greater than or equal to 1.

## Consequences

### Positive
- Matches standard Axelrod round-robin tournament mechanics.
- Reuses the thoroughly tested and verified `Match` execution core without duplicating game logic.
- Exactly $N(N - 1)/2$ matches are scheduled in predictable, reproducible order.

### Negative / Trade-offs
- $O(N^2)$ computational complexity with respect to population size $N$. For very large populations ($N > 1000$), future episodes may introduce spatial or random-sample matchmakers.
