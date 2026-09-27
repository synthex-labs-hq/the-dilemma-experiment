# ADR-016: Noise-Resilient Forgiving Strategies

## Status

Accepted

## Context

Under noiseless conditions (Episodes 1 & 2), `TitForTatStrategy` and `GrimTriggerStrategy` demonstrated strong performance. However, when channel noise ($\epsilon > 0$) is present:
- **`GrimTriggerStrategy` undergoes catastrophic breakdown**: A single accidental defection by either player locks the pair into permanent mutual defection ($DD$), yielding minimum payoffs ($1.0$/round).
- **`TitForTatStrategy` enters retaliatory echo cycles**: An accidental defection by Agent A induces retaliation by Agent B, which induces retaliation by Agent A, locking the agents into an alternating echo feud ($CD \leftrightarrow DC$), dropping average score to $2.5$/round, or collapsing into mutual defection ($DD$).

To survive in noisy environments, strategies must possess forgiveness, patience, or self-correcting reflex mechanisms.

## Decision

We introduce three canonical noise-resilient strategies:

1. **`GenerousTitForTatStrategy` (GTFT)**:
   - Starts with `COOPERATE`.
   - If the opponent cooperated on their previous round, GTFT cooperates.
   - If the opponent defected on their previous round, GTFT cooperates with a calibrated forgiveness probability $q \in (0, 1)$ (default $q = 1/3 \approx 0.3333$, derived from Axelrod & Dion 1988 for standard payoffs $T=5, R=3, P=1, S=0$).
   - This breaks echo cascades by periodically extending an unprovoked olive branch.

2. **`TitForTwoTatsStrategy` (TF2T)**:
   - Starts with `COOPERATE` for the first two rounds.
   - Retaliates with `DEFECT` if and only if the opponent defected on *both* of the last two consecutive rounds.
   - Tolerates single isolated transmission errors without retaliating, preventing echo spirals against cooperative partners.

3. **`WinStayLoseShiftStrategy` (WSLS / Pavlov)**:
   - Proposed by Martin Nowak & Karl Sigmund (1993).
   - Starts with `COOPERATE`.
   - Evaluates the outcome of the previous round:
     - **Win** (satisfying outcome: $CC \to +3$, or $DC \to +5$): Repeats ("Stays") with its own previous action.
     - **Lose** (unsatisfying outcome: $CD \to 0$, or $DD \to +1$): Shifts ("Switches") to the opposite action.
   - Self-corrects after noise: Two Pavlov agents encountering a single error return to mutual cooperation within two rounds ($CD \to DD \to CC$). Furthermore, it exploits persistent suckers (`AlwaysCooperate`) while defending itself against persistent exploiters (`AlwaysDefect`).

4. **Consistency and Determinism**:
   - Probabilistic strategies (`GenerousTitForTatStrategy`) accept an optional explicit `seed: int | None = None` per ADR-003.
   - All stateful strategies partition their observation memory strictly by `opponent_id` per ADR-014.

## Consequences

### Positive
- Explores three distinct paradigms: probabilistic forgiveness (GTFT), bounded patience (TF2T), and reinforcement reflex (Pavlov/WSLS).
- Demonstrates how forgiveness restores social welfare in noisy multi-agent ecosystems.
- Strictly adheres to established strategy interface contracts and seed reproducibility.

### Negative / Trade-offs
- `TitForTwoTats` is susceptible to exploitation by alternating defectors ($DCDCDC$).
- `WinStayLoseShift` requires tracking both own last action and opponent's last action per opponent.
