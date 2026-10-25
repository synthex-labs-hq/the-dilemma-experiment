# The Dilemma Experiment

An open-source simulation exploring how cooperation emerges, survives, and collapses among self-interested agents.

## About

The Dilemma Experiment is a reproducible simulation project exploring cooperation, betrayal, trust, reputation, strategy, and emergent social behaviour.

The project begins with the repeated Prisoner's Dilemma and will evolve through a series of experiments.

## Episodes

- [Episode 1 — Building the Laboratory: Can Cooperation Survive?](docs/episodes/01-building-the-laboratory.md)
- [Episode 2 — The Tournament: When Selfish Agents Form a Society](docs/episodes/02-the-tournament.md)
- [Episode 3 — Noise & Forgiveness: Why Pure Reciprocity Collapses When Communication Breaks](docs/episodes/03-noise-and-forgiveness.md)
- [Episode 4 — Natural Selection & Evolution: Replicator Dynamics and the Survival of Cooperation](docs/episodes/04-natural-selection-and-evolution.md)
- [Episode 5 — Spatial Networks & Topologies: The Fortress of Geography](docs/episodes/05-spatial-networks-and-topologies.md)

### Implemented Strategies:

- `AlwaysCooperateStrategy` (The Altruist)
- `AlwaysDefectStrategy` (The Predator)
- `TitForTatStrategy` (The Reciprocal Enforcer)
- `GrimTriggerStrategy` (The Unforgiving Grudger)
- `RandomStrategy` (The Chaos Agent)
- `GenerousTitForTatStrategy` (The Forgiving Cooperator)
- `TitForTwoTatsStrategy` (The Patient Cooperator)
- `WinStayLoseShiftStrategy` (Pavlov / Adaptive Cooperator)

## Project Status

- **Episode 1**: Completed & tagged at `v0.1.0-episode-1`
- **Episode 2**: Completed & tagged at `v0.2.0-episode-2`
- **Episode 3**: Completed & tagged at `v0.3.0-episode-3` (119 passing unit tests)
- **Episode 4**: Completed & tagged at `v0.4.0-episode-4` (126 passing unit tests)
- **Episode 5**: Completed & tagged at `v0.5.0-episode-5` (139 passing unit tests)

## Development

This project uses Python 3.12 and `uv` for Python environment and dependency management.

Create/synchronize the development environment:

```bash
uv sync
```

Run tests:

```bash
uv run pytest
```

Run Ruff:

```bash
uv run ruff check
```

## Project Structure

```
the-dilemma-experiment/
├── src/
│   └── the_dilemma_experiment/
│       └── __init__.py
├── tests/
├── experiments/
│   ├── episode_01/
│   │   └── ...
├── pyproject.toml
├── README.md
└── ...
```

## Philosophy

Each experiment follows:

Question → Hypothesis → Model → Experiment → Results → Surprises → Limitations

The goal is to build reproducible simulations and understand what emerges from the assumptions we make.


## License

This project is licensed under the [MIT License](LICENSE).

