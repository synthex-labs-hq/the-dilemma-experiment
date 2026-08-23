# ADR-006: Standard Library First

## Status

Proposed

## Context

Episode 1 focuses on core domain modeling, object architecture, and foundational simulation mechanics. Adding third-party libraries prematurely increases footprint and shifts focus away from clean domain design.

## Decision

Episode 1 should use Python's standard library wherever practical.

- No runtime dependencies are currently required.
- Existing development dependencies remain `pytest` and `ruff`.
- Third-party dependencies may be introduced later only when a concrete requirement justifies them.
- Do not introduce additional dependencies during the initial domain-modeling phase unless a concrete requirement is identified and the dependency is explicitly justified.

## Alternatives Considered

- **Scientific Python stack from the beginning:** Introduces heavy dependencies before data processing scale or complex matrix operations require them.
- **Add likely-future dependencies proactively:** Increases project bloat without immediate necessity.
- **Build around third-party frameworks:** Risks coupling domain concepts to external library abstractions.

## Consequences

- Lightweight repository footprint, fast installation, and zero runtime dependency overhead.
- Promotes clean, idiomatic Python standard library domain structures.
- Future dependencies can be added deliberately when concrete needs arise in subsequent episodes.
