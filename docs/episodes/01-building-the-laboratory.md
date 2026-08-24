# The Dilemma Experiment: Can Cooperation Survive?

## Episode 1 — Building the Laboratory

### Opening question

In a world driven by individual self-interest, how does cooperation ever emerge?

Why do uncoordinated individuals, competing for finite rewards, often find ways to trust one another and work together? Conversely, why do highly cooperative environments suddenly collapse into mutual hostility and distrust?

These are not merely abstract academic dilemmas; they govern international diplomacy, economic markets, evolutionary biology, distributed computing, and multi-agent artificial intelligence. **The Dilemma Experiment** was founded to explore these fundamental dynamics through reproducible, open-source computational simulations.

> I've spent most of my career building software systems where rules, state, incentives, and interactions have to be made explicit.
>
> The Prisoner's Dilemma struck me as an interesting place to apply that mindset to something much messier: behavior.
>
> Instead of starting with an AI model and asking it to behave intelligently, I wanted to start with something much simpler:
>
> Give agents rules.  
> Give them memory.  
> Give them incentives.  
> Then let them interact.  
>
> See what happens.

---

### What happens when selfish agents interact repeatedly?

At the foundation of decision theory lies the classic **Prisoner's Dilemma**. Two participants must independently decide whether to `COOPERATE` or `DEFECT` without communicating. The rewards and penalties are structured such that in the standard Prisoner's Dilemma, defection is the dominant strategy for a one-shot interaction, even though mutual cooperation produces a far higher collective outcome.

| | Opponent Cooperates | Opponent Defects |
| :--- | :---: | :---: |
| **Agent Cooperates** | Reward: (3, 3) | Sucker's Payoff: (0, 5) |
| **Agent Defects** | Temptation: (5, 0) | Punishment: (1, 1) |

No matter what the opponent chooses in a single round, defecting yields a higher individual payoff ($5 > 3$ if they cooperate, $1 > 0$ if they defect). Without repeated interaction or external enforcement mechanisms, rational payoff-maximizing agents are driven toward mutual defection, trapping them in a suboptimal outcome $(1, 1)$ when mutual cooperation could have yielded $(3, 3)$.

---

### The repeated game changes everything

When interactions repeat over time, the mathematical landscape shifts dramatically.

In a repeated interaction (an iterated Prisoner's Dilemma), an agent's current action can influence its opponent's future choices. Betrayal today invites retaliation tomorrow; cooperation today builds trust for the future. The shadow of the future introduces the possibility of reciprocity.

Under repeated play, strategies are no longer static choices—they become dynamic algorithms that react to historical observations.

---

### Meet Tit-for-Tat

Among the baseline strategies in Episode 1, three define the spectrum of behavioral archetypes:

1. `AlwaysCooperateStrategy`: Unconditionally chooses `COOPERATE` on every round, regardless of history.
2. `AlwaysDefectStrategy`: Unconditionally chooses `DEFECT` on every round, seeking immediate exploitation.
3. `TitForTatStrategy`: Starts by offering `COOPERATE` on the first round with a new opponent. In subsequent rounds, it simply repeats whatever action the opponent chose in their most recent interaction.

What makes `TitForTatStrategy` compelling is not artificial intelligence, but its combination of extreme simplicity plus memory. It requires no complex forecasting or heuristic optimization, embodying five core principles:
- **Nice**: It starts with cooperation and is never the first to defect.
- **Reciprocal**: It mirrors the opponent's previous action precisely.
- **Retaliatory**: It immediately punishes opponent defection on the very next round.
- **Forgiving**: It immediately returns to cooperation as soon as the opponent cooperates again.
- **Simple**: Its behavior is transparent and predictable, making it easy for opponents to recognize its willingness to cooperate.

---

### From a game to an experiment

To move from game-theoretic mathematics to software engineering, we must build a clean computational framework.

An experiment requires an environment where interaction rules are strict, historical observations are verifiable, execution is deterministic, and state boundaries are unambiguous. Before running large-scale multi-agent evolutionary tournaments, we must first build the laboratory.

That is the purpose of **Episode 1**.

---

### Episode 1: Building the Laboratory

> I deliberately kept Episode 1 boring.
>
> No database.  
> No web API.  
> No visualization.  
> No LLM.  
> No fancy agent framework.  
>
> Just the smallest set of objects required to represent the experiment correctly.

Rather than jumping straight to complex population scheduling or visualization UIs, Episode 1 focuses exclusively on creating a clean, minimal domain core.

```
       ┌────────────────────────┐
       │         Agent          │
       └───────────┬────────────┘
                   │ owns
                   ▼
       ┌────────────────────────┐
       │        Strategy        │
       └────────────────────────┘
                   ▲
                   │ decides Action via DecisionContext
       ┌───────────┴────────────┐
       │         Match          │ ── coordinates repeated rounds
       └───────────┬────────────┘
                   │ resolves actions via Game
                   ▼
       ┌────────────────────────┐
       │    PrisonersDilemma    │
       └───────────┬────────────┘
                   │ produces Payoff
                   ▼
       ┌────────────────────────┐
       │         Round          │ ── recorded into Match history
       └────────────────────────┘
```

The primary domain concepts include:
- `Action`: Standard library Enum representing `COOPERATE` and `DEFECT`.
- `Agent`: Immutable participant entity binding a string `id` to a `Strategy`.
- `DecisionContext`: Immutable context supplied to a `Strategy` containing the `opponent_id`.
- `Strategy`: Abstract base contract (`choose_action` and `observe`).
- `Payoff`: Immutable value object holding integer utilities `first` and `second`.
- `Game`: Abstract game resolution contract (`resolve(first_action, second_action) -> Payoff`).
- `PrisonersDilemma`: Concrete `Game` owning the verified $2 \times 2$ payoff matrix.
- `Round`: Immutable historical record of one completed interaction.
- `MatchResult`: Immutable aggregate outcome storing participant IDs and total scores.
- `Match`: Orchestrator governing repeated interaction between exactly two agents.

---

### A Round should remember—not decide

A central architectural decision in Episode 1 (ADR-007) is that a `Round` is a historical result—not an active execution agent.

A `Round` is an immutable dataclass storing:
- `first_agent_id`: `str`
- `second_agent_id`: `str`
- `first_action`: `Action`
- `second_action`: `Action`
- `payoff`: `Payoff`

`Round` contains no game logic, no strategy logic, and no execution state. It serves strictly as a transparent, immutable historical record of what occurred during a single interaction.

---

### The Match owns the interaction

Repeated interactions are coordinated by the `Match` class (ADR-008).

A `Match` accepts two `Agent` instances, a `Game` rules engine, and a `round_count`. Its execution lifecycle follows a strict sequence:

1. **Simultaneous Choice**: Both strategies choose their actions via `choose_action()` before either strategy is informed of the opponent's choice.
2. **Game Resolution**: `PrisonersDilemma.resolve()` computes the resulting `Payoff`.
3. **Round Creation**: An immutable `Round` is instantiated with participants, actions, and payoff.
4. **Observation Notification**: `Match` calls `observe()` on both strategies, allowing them to record the opponent's action.
5. **Iteration**: The sequence repeats for the configured `round_count`.
6. **Completion**: Aggregate scores are committed to an immutable `MatchResult`.

---

### Then we encountered a more subtle problem

During the implementation of repeated `Match` execution, we encountered a critical lifecycle edge case: **What happens if a match fails mid-execution?**

If a strategy or game throws an exception during round 3 of a 5-round match, committing partial round history would represent **invalid experimental data**, not merely an implementation inconvenience. A truncated match distorts score totals, corrupts statistical averages, and invalidates trial reproducibility.

> Either the configured interaction completes, or its Match-owned history is not committed.

To guarantee data integrity, `Match` (ADR-009) implements **atomic execution isolation**:
- `Match.execute()` accumulates completed rounds in a local temporary buffer (`temporary_rounds`).
- Match-owned history (`self.rounds`) and final results (`self.result`) are updated **only** after all rounds finish successfully.
- If execution fails mid-match, the `Match` instance remains completely clean (`rounds == ()`, `result is None`), enabling caller retries from round 1.
- Re-executing an already completed `Match` raises a `RuntimeError`.

---

### But what about strategy memory?

While `Match`-owned temporary state is discarded upon failure, what happens to internal strategy state modified by `observe()` calls before the failure?

This required formalizing **Strategy State and Lifecycle Ownership** (ADR-010):
- `Strategy` state is strictly owned by the individual `Strategy` instance bound to an `Agent`.
- `Match` does **not** reset, clone, snapshot, or roll back strategy state.
- If a `Match` fails and is retried, any strategy observations made before the failure persist on the strategy instance.
- Similarly, reusing the same `Agent` instance across separate matches carries over its strategy memory (e.g., `TitForTatStrategy` remembers past interactions with that opponent).

Episode 1 deliberately refrains from introducing complex `reset()` or `clone()` APIs on `Strategy`. Clean-slate matches are created simply by instantiating fresh `Agent` and `Strategy` objects at the orchestrator layer.

---

### What Episode 1 can actually do

Episode 1 is fully implemented, verified with 74 passing behavioral tests, and tagged at `v0.1.0-episode-1`.

Here is what the Episode 1 domain core currently supports:
- **Baseline Matches**: Executing multi-round matches between any combination of `AlwaysCooperateStrategy`, `AlwaysDefectStrategy`, and `TitForTatStrategy`.
- **End-to-End Scenarios**:
  - *Stable Cooperation*: `AlwaysCooperate` vs `AlwaysCooperate` yields mutual $(3, 3)$ payoffs across all rounds, producing aggregate scores of $(9, 9)$ over 3 rounds.
  - *Persistent Exploitation*: `AlwaysDefect` vs `AlwaysCooperate` yields $(5, 0)$ payoffs every round, producing scores of $(15, 0)$ over 3 rounds.
  - *Reciprocal Retaliation*: `TitForTat` vs `AlwaysDefect` cooperates on round 1, observes defection, and defects on rounds 2 and 3, limiting exploitation to $(2, 7)$ over 3 rounds.
- **Deterministic & Isolated Execution**: Atomic match retry, read-only matrix views, immutable historical objects, and strict simultaneous decision ordering.

---

# Episode 1 Isn't the Experiment

> Episode 1 isn't the experiment.
>
> It's the laboratory.

It is vital to understand the boundary of Episode 1. Episode 1 does **not** contain:
- Population registries
- Round-robin tournament scheduling
- Matchmaking or population dynamics
- Strategy evolutionary selection
- Reputation tracking across multi-agent populations
- Experiment configuration files or CLI runners
- Metrics collection, data export, or visualization UIs

Episode 1 is strictly the **domain-core foundation**—the verified, deterministic laboratory apparatus upon which higher-level experiments will be built.

---

### The next question is much bigger

Now that the 1-on-1 interaction mechanics are solidified, we can ask larger questions:

- What happens when a population of 100 agents interact in a round-robin tournament?
- Can a small cluster of `TitForTat` agents invade and displace a dominant population of `AlwaysDefect` agents?
- What proportion of cooperative strategies is required to maintain population-level stability?
- How does noise (accidental defections or miscommunications) impact mutual trust?

---

### Episode 2: The Population

Episode 1 focused on two-agent interaction mechanics. **Episode 2** will build the multi-agent simulation engine around this Episode 1 domain core:

1. **Population Management**: Registries holding diverse populations of agents.
2. **Tournament Scheduling**: Round-robin and spatial matchmakers that pair agents for repeated `Match` execution.
3. **Simulation Engine**: Orchestrators running multi-generation evolutionary tournaments.
4. **Metrics & Data Collection**: Aggregating cooperation rates, score distributions, and population trajectories.

> Episode 1 had two agents.
>
> Episode 2 gives us a population.
>
> And once there are many agents, many strategies, and many repeated interactions, we can finally start measuring what happens when cooperation and defection compete at scale.

---

### A note from the builder

*The Dilemma Experiment is built manually, incrementally, and transparently.*

*Every architectural choice is documented via Architecture Decision Records (ADRs under `docs/adr/`), verified with zero-mock behavioral unit tests, and committed with conventional commit history.*

*Follow the project development on GitHub: [synthex-labs-hq/the-dilemma-experiment](https://github.com/synthex-labs-hq/the-dilemma-experiment).*
