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
- [Episode 6 — Indirect Reciprocity, Reputation & Gossip: Public Ledgers and Moral Systems](docs/episodes/06-indirect-reciprocity-and-reputation.md)
- [Episode 7 — Tags, Tribalism & In-Group Favoritism: The Green Beard Effect](docs/episodes/07-tags-tribalism-and-in-group-favoritism.md)
- [Episode 8 — The Tragedy of the Commons & Sanctions: Elinor Ostrom's Eight Principles](docs/episodes/08-the-tragedy-of-the-commons-and-sanctions.md)
- [Episode 9 — Zero-Determinant Strategies & Asymmetric Power: The Press-Dyson Extortion Engine](docs/episodes/09-zero-determinant-strategies-and-asymmetric-power.md)
- [Episode 10 — The Grand Finale: The Cognitive Revolution (LLM Multi-Agent Societies)](docs/episodes/10-the-cognitive-revolution-llm-multi-agent-societies.md)

### Implemented Strategies:

- `AlwaysCooperateStrategy` (The Altruist)
- `AlwaysDefectStrategy` (The Predator)
- `TitForTatStrategy` (The Reciprocal Enforcer)
- `GrimTriggerStrategy` (The Unforgiving Grudger)
- `RandomStrategy` (The Chaos Agent)
- `GenerousTitForTatStrategy` (The Forgiving Cooperator)
- `TitForTwoTatsStrategy` (The Patient Cooperator)
- `WinStayLoseShiftStrategy` (Pavlov / Adaptive Cooperator)
- `ImageScorerStrategy` (First-Order Reputation Scorer)
- `SternJudgingStrategy` (Second-Order Moral Enforcer)
- `HypocriteStrategy` (Public Virtuous / Shadow Defector)
- `RioloToleranceStrategy` (Continuous Tag & Tolerance Discriminator)
- `StrictTribalStrategy` (Categorical In-Group Cooperator / Out-Group Defector)
- `FalseBeardStrategy` (The Parasitic Chameleon Defector)
- `TagReciprocalStrategy` (In-Group Tit-For-Tat / Out-Group Hostility)
- `SustainableHarvesterStrategy` (Responsible Commons Harvester)
- `OverHarvesterStrategy` (Tragedy of the Commons Exploiter)
- `OstromSanctionerStrategy` (Altruistic Peer Punisher & Guard)
- `SecondOrderFreeRiderStrategy` (Cooperative Free-Rider on Sanctions)
- `AntisocialPunisherStrategy` (Spiteful Punisher of Cooperators)
- `ExtortionStrategy` (Zero-Determinant Extortioner)
- `EqualizerStrategy` (Zero-Determinant Unilateral Payoff Clamper)
- `GenerousZDStrategy` (Zero-Determinant Generous Cooperator)
- `CognitiveStrategy` (LLM Cognitive Persona: Diplomat, Machiavellian, Contractor, Realist)

## Project Status

- **Episode 1**: Completed & tagged at `v0.1.0-episode-1`
- **Episode 2**: Completed & tagged at `v0.2.0-episode-2`
- **Episode 3**: Completed & tagged at `v0.3.0-episode-3` (119 passing unit tests)
- **Episode 4**: Completed & tagged at `v0.4.0-episode-4` (126 passing unit tests)
- **Episode 5**: Completed & tagged at `v0.5.0-episode-5` (139 passing unit tests)
- **Episode 6**: Completed & tagged at `v0.6.0-episode-6` (152 passing unit tests)
- **Episode 7**: Completed & tagged at `v0.7.0-episode-7` (167 passing unit tests)
- **Episode 8**: Completed & tagged at `v0.8.0-episode-8` (181 passing unit tests)
- **Episode 9**: Completed & tagged at `v0.9.0-episode-9` (189 passing unit tests)
- **Episode 10**: Completed & tagged at `v1.0.0-episode-10` (196 passing unit tests)

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

