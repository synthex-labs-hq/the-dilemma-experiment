# The Dilemma Experiment

An open-source simulation exploring how cooperation emerges, survives, and collapses among self-interested agents.

---

## 🎮 The Dilemma Arena (Interactive Web Platform)

Version `1.1.0` introduces **The Dilemma Arena**, an interactive cybernetic web simulation platform built with **FastAPI**, **React 19**, **TypeScript**, and **Modern Vanilla CSS**.

![The Dilemma Arena Architecture](docs/architecture/ui-arena-overview.png) *(or run locally via the instructions below)*

### Core Simulation Workspaces:

1. **⚔️ The Arena (Pairwise Strategic Duel)**:
   - Pit any two game-theoretic strategies against each other.
   - Turn-by-turn playback theater with pause/resume, round scrub slider, and variable playback speeds (`1x`, `5x`, `MAX`).
   - Visual action halos, payoff chips, dialogue quote bubbles, rationale logs, and deception auditing.
   - Interactive SVG cumulative score trajectory chart with live synchronized cursor.

2. **🏆 Tournament Hub (Multi-Agent Societies)**:
   - Multi-caste population composer with count steppers and one-click society presets (*Axelrod Classic*, *Forgiving Society*, *ZD Gauntlet*).
   - Real-time round-robin society leaderboard with dynamic column sorting.
   - **$N \times N$ Head-to-Head Cross-Table Matrix**: Color-coded pairwise outcome grid (`W`, `L`, `🤝`) with individual agent inspection drawers.

3. **🧪 Episode Laboratories**:
   - **Episode 05 Spatial 2D Grid Visualizer**: 2D toroidal grid simulation displaying the *Fortress Effect*, cooperator clusters, and spatial clustering coefficients ($\mathcal{C}_{ratio}$) across generations.
   - **Episode 08 Commons Pool & Ostrom Sanctions Lab**: Real-time CPR stock depletion curves ($R_t$), harvest rate steppers, and institutional sanction auditing demonstrating how peer enforcement avoids the *Tragedy of the Commons*.

4. **🛠️ Strategy Sandbox & The Gauntlet**:
   - **Visual Trait Builder**: Customize opening move, retaliation severity, stochastic forgiveness, and memory length.
   - **Live Python Code Contract**: Generates valid Python 3.12 `Strategy` code in real time.
   - **The Gauntlet Benchmark Suite**: Pits custom strategies against the 5 canonical Axelrodian guardians (`tit_for_tat`, `always_defect`, `win_stay_lose_shift`, `extortioner`, `generous_zd`) and scores the 4 Axelrodian axioms: *Niceness*, *Retaliatory Speed*, *Forgiving Capacity*, and *Exploitation Resistance*.

---

## 🚀 Quickstart: Launching The Arena

### Method 1: Unified Launcher Script (Recommended)

To start both the FastAPI backend (`:8000`) and the Vite React frontend (`:5173`) concurrently with hot reloading:

```bash
./run_ui.sh
```

To build and run the single-port standalone production server on `http://localhost:8000`:

```bash
./run_ui.sh --prod
```

### Method 2: Python CLI

The package provides a built-in CLI command:

```bash
# Launch interactive simulation platform
uv run the-dilemma ui

# Launch single-port standalone production server
uv run the-dilemma ui --prod

# Run terminal CLI demo for any episode (e.g., Episode 10 LLM cognitive society)
uv run the-dilemma demo 10

# Print package version
uv run the-dilemma version
```

---

## 📚 Episodes Curriculum

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

### Implemented Strategies (24+ Roster):

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
- `ConfigurableCustomStrategy` (Visual Trait Builder Sandbox Agent)

---

## 🧪 Project Status

- **Episode 1**: Completed & tagged at `v0.1.0-episode-1`
- **Episode 2**: Completed & tagged at `v0.2.0-episode-2`
- **Episode 3**: Completed & tagged at `v0.3.0-episode-3` (119 tests)
- **Episode 4**: Completed & tagged at `v0.4.0-episode-4` (126 tests)
- **Episode 5**: Completed & tagged at `v0.5.0-episode-5` (139 tests)
- **Episode 6**: Completed & tagged at `v0.6.0-episode-6` (152 tests)
- **Episode 7**: Completed & tagged at `v0.7.0-episode-7` (167 tests)
- **Episode 8**: Completed & tagged at `v0.8.0-episode-8` (181 tests)
- **Episode 9**: Completed & tagged at `v0.9.0-episode-9` (189 tests)
- **Episode 10**: Completed & tagged at `v1.0.0-episode-10` (196 tests)
- **Web Arena Suite**: Completed & tagged at `v1.1.0` (206 passing tests, full-stack platform)

---

## 🛠️ Development & Testing

This project uses Python 3.12 and `uv` for Python package management, and `pnpm` for the frontend.

Synchronize dependencies:
```bash
uv sync
pnpm --dir ui/frontend install
```

Run Python test suite (206 zero-mock tests):
```bash
uv run pytest
```

Run linter & formatter:
```bash
uv run ruff check
```

Build React production bundle:
```bash
pnpm --dir ui/frontend build
```

---

## 🏛️ Project Structure

```
the-dilemma-experiment/
├── src/the_dilemma_experiment/     # Core domain simulation engine
│   ├── api/app.py                  # Zero-mock FastAPI simulation backend
│   ├── cli.py                      # Unified CLI entry point
│   ├── domain/                     # Match, Tournament, Commons, Spatial, Cognitive
│   └── strategies/                 # 24+ Game theoretic strategies
├── ui/
│   ├── frontend/                   # React 19 + TypeScript + Vanilla CSS
│   │   ├── src/components/         # ScoreChart, CrossTableMatrix, SpatialGridLab, CommonsResourceLab
│   │   ├── src/views/              # ArenaView, TournamentsView, EpisodesView, SandboxView
│   │   └── src/index.css           # Cybernetic design system tokens
│   └── server/                     # FastAPI ASGI re-export
├── tests/                          # 206 Automated zero-mock unit tests
├── experiments/                    # 10 milestone experiment reproduction suites
├── run_ui.sh                       # Unified launcher script (dev & prod)
├── pyproject.toml
└── README.md
```

---

## 📜 Philosophy

Each experiment follows:

$$\text{Question} \longrightarrow \text{Hypothesis} \longrightarrow \text{Model} \longrightarrow \text{Experiment} \longrightarrow \text{Results} \longrightarrow \text{Surprises} \longrightarrow \text{Limitations}$$

The goal is to build reproducible simulations and understand what emerges from the assumptions we make.

## 📄 License

This project is licensed under the [MIT License](LICENSE).
