# ADR-003: Simulation-Owned Deterministic Randomness

## Status

Proposed

## Context

Experiments involving stochastic operations (such as random pairing or probabilistic strategies) must be strictly reproducible. Relying on global unseeded state or decentralized random number generation breaks scientific reproducibility across repeated runs under the same supported environment.

## Decision

The Simulation owns the random number generator used during execution.

- The experiment configuration provides an explicit seed.
- Stochastic behaviour must use the controlled randomness source rather than implicit global randomness.
- The same code version, configuration, and seed should produce reproducible results within the supported runtime environment.
- Do not introduce multiple independent RNG streams yet.

## Alternatives Considered

- **Global Python random state (`random.seed()`):** Creates hidden side effects across modules and risks non-reproducible behavior if external components mutate global state.
- **Each strategy owns its own RNG:** Hard to seed deterministically across population dynamics and configuration boundaries.
- **Separate RNG streams for every stochastic component:** Adds unnecessary complexity for Episode 1 requirements.

## Consequences

- Deterministic reproducibility is expected when the same code version, supported Python runtime, configuration, and seed are used.
- Deterministic behavior simplified under a single simulation-controlled RNG source.
- Avoids premature complexity of multi-stream random generators.
