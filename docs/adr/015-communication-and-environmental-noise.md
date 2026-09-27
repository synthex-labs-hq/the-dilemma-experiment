# ADR-015: Communication and Environmental Noise

## Status

Accepted

## Context

In real-world multi-agent systems, economic markets, and international relations, communication and action execution are never completely lossless. Misunderstandings, execution errors, transmission drops, and perception biases introduce stochastic perturbations into interactions.

In game theory literature, this is known as the "trembling hand" problem (Reinhard Selten, 1975) or "noisy communication channels" (Axelrod & Dion, 1988; Nowak & Sigmund, 1992).

Prior to Episode 3, `Match` and `Tournament` assumed a 100% deterministic, noiseless channel: an agent's chosen action was guaranteed to be both resolved by the `Game` and observed by the opponent with zero distortion.

We must introduce noise to model imperfect environments, evaluate the fragility of zero-tolerance strategies (`GrimTrigger`, `TitForTat`), and test forgiveness mechanisms.

## Decision

1. **Noise Owned by the Interaction Channel (`Match`)**:
   Noise is an environmental property of the interaction channel, not an intrinsic property of individual agent strategies. Therefore, `Match` receives an optional `noise: float = 0.0` parameter ($0.0 \le \epsilon \le 1.0$).

2. **Symmetric Action Inversion**:
   In each round, each agent's chosen action is evaluated against the channel noise probability $\epsilon$:
   - With probability $\epsilon$, the action is inverted (`COOPERATE` $\to$ `DEFECT`, `DEFECT` $\to$ `COOPERATE`).
   - With probability $1 - \epsilon$, the action is transmitted faithfully.

3. **Resolved Actions Govern Game Rules and Observation**:
   - The `Game.resolve()` rules engine computes payoffs strictly based on the *transmitted* (resolved) actions.
   - Opponents observe what was actually received (`round.second_action` / `round.first_action`), modeling real-world perception where internal intentions cannot be directly inspected.

4. **Auditability in `Round`**:
   The immutable `Round` record is enhanced with optional intended action fields:
   - `first_intended_action: Action | None = None`
   - `second_intended_action: Action | None = None`
   - `is_noisy` convenience property returning `True` if either agent's intended action was flipped.
   Existing callers accessing `round.first_action`, `round.second_action`, and `round.payoff` remain 100% backwards-compatible.

5. **Deterministic Seeding Across Tournaments**:
   - `Match` accepts an optional `seed: int | None = None` and encapsulates its own `random.Random(seed)`.
   - `Tournament` accepts `noise: float = 0.0` and `seed: int | None = None`. When executing matches, `Tournament` derives individual match seeds deterministically from its master seed, preserving ADR-003 reproducibility.

## Consequences

### Positive
- Realistic modeling of communication noise and execution errors.
- Full backwards compatibility with existing noiseless tests and simulations.
- Complete audit trail of intended vs. transmitted actions for analytics and CLI demonstrations.
- Deterministic reproducibility under controlled seeds.

### Negative / Trade-offs
- Slight overhead in `Match._execute_round()` due to RNG evaluation when noise $> 0.0$.
