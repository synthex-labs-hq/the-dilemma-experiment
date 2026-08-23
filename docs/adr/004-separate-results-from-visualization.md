# ADR-004: Separate Simulation Results from Visualization

## Status

Proposed

## Context

Simulation outputs need to be consumed by diverse tools, including data exporters (JSON, CSV), static plotting libraries, interactive notebooks, or web interfaces. Coupling simulation execution directly to visual presentation libraries forces unnecessary dependencies on core simulation logic.

## Decision

The simulation produces structured experiment results, and visualization/presentation consumes those results separately.

- The simulation must not depend on matplotlib, notebooks, web visualization, or other presentation tooling.
- Results should be usable by multiple future consumers such as JSON, CSV, plotting, notebooks, web visualization, and content production.

## Alternatives Considered

- **Simulation directly generates charts:** Tightly couples plotting dependencies into the simulation core and restricts output formats.
- **Metrics module owns visualization:** Mixes data collection with rendering logic.
- **Notebook is the experiment implementation:** Limits execution to interactive environments and hinders automated testing or batch running.

## Consequences

- The core simulation engine remains lightweight, clean, and free of heavy rendering dependencies.
- Structured result objects enable easy serialization and consumption across diverse presentation layers.
- Presentation layers can evolve independently without altering simulation mechanics.
