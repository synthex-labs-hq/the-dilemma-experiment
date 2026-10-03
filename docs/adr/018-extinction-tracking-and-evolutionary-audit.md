# ADR-018: Extinction Tracking and Evolutionary Audit

## Status

Accepted

## Context

To understand evolutionary phenomena—such as the boom-and-bust cycles of predators, the invasion threshold of reciprocal strategies, and the emergence of Evolutionarily Stable Strategies (ESS)—experiments and interactive visualizers require a comprehensive, auditable record of every generation.

Without fine-grained generational tracking:
- Researchers cannot determine the precise generation an archetype collapsed or went extinct.
- CLI visualizers cannot cleanly render generational bar charts or trigger extinction alerts.
- Reproducibility between simulation runs cannot be mathematically audited.

We need an immutable data structure representing the state and outcome of each generation, alongside an evolutionary orchestrator supporting both batch simulation and step-by-step interactive inspection.

## Decision

1. **Immutable `GenerationResult`**:
   Each completed generation produces an immutable `GenerationResult` value object containing:
   - `generation: int`: Generation index ($0, 1, 2, \dots$).
   - `population_counts: dict[str, int]`: Mapping of strategy archetype name to agent count in this generation.
   - `population_shares: dict[str, float]`: Demographic proportions ($N_i / N$).
   - `average_fitness: dict[str, float]`: Mean tournament score per agent for each strategy.
   - `mean_population_fitness: float`: Mean fitness across the entire population.
   - `extinct_strategies: tuple[str, ...]`: Alphabetically sorted tuple of all strategy archetypes that currently have zero population.
   - `newly_extinct: tuple[str, ...]`: Tuple of strategy archetypes that went extinct during *this specific* generation transition.
   - `active_strategies: tuple[str, ...]`: Alphabetically sorted tuple of strategies with $N_i > 0$.
   - `tournament_result: TournamentResult | None`: Full underlying tournament result record, enabling deep drill-down into individual match records if needed.

2. **Step-by-Step and Batch Evolutionary Orchestration**:
   The `EvolutionaryTournament` class manages multi-generation lifecycles:
   - `step() -> GenerationResult`: Executes exactly one generation, updates population shares via Replicator Dynamics (ADR-017), and returns the new `GenerationResult`.
   - `run(generations: int) -> list[GenerationResult]`: Executes generations in sequence until either the target generation count is reached or the population converges.
   - `history: tuple[GenerationResult, ...]`: Complete chronological ledger of all completed generations.
   - `is_converged: bool`: Returns `True` if fixation is achieved (single strategy remaining) or all surviving strategies have identical fitness.

3. **Deterministic Generation Seeding**:
   - `EvolutionaryTournament` accepts an optional master `seed: int | None = None`.
   - Each generation derives its tournament seed deterministically using a dedicated generation index derivation:
     $$\text{gen\_seed} = \text{hash}((\text{master\_seed}, \text{gen\_idx})) \pmod{2^{31} - 1}$$
   - This ensures identical replayability and verification across any environment.

## Consequences

### Positive
- Complete audit trail of evolutionary trajectories from generation 0 to convergence.
- Real-time step-by-step execution for presenter terminal demonstrations (`demo_evolution_cli.py --step`).
- Explicit distinction between historical extinctions and newly triggered extinctions for sound and visual alerts.
- Fully compatible with standard serialization (`to_dict()`, JSON).

### Negative / Trade-offs
- Storing full `TournamentResult` objects across hundreds of generations can consume memory if millions of rounds are kept. `EvolutionaryTournament` allows configuring whether to retain detailed `TournamentResult` or only aggregate metrics per generation.
