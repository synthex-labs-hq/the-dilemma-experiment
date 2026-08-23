# The Dilemma Experiment

An open-source simulation exploring how cooperation emerges, survives, and collapses among self-interested agents.

## About

The Dilemma Experiment is a reproducible simulation project exploring cooperation, betrayal, trust, reputation, strategy, and emergent social behaviour.

The project begins with the repeated Prisoner's Dilemma and will evolve through a series of experiments.

## Episode 1 — Can Cooperation Survive?

The first experiment explores how different strategies behave when repeatedly interacting in the Prisoner's Dilemma.

Initial strategies:

- Always Cooperate
- Always Defect
- Tit-for-Tat
- Random

## Project Status

🚧 Early development

Episode 1 is currently being built.

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

Not licensed yet. The repository is currently private and is intended to become open source as the project matures.

