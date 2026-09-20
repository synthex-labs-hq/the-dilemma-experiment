# The Dilemma Experiment: When Selfish Agents Form a Society

## Episode 2 — The Tournament

### Opening Question

In Episode 1, we watched two solitary agents face off in the Prisoner's Dilemma. We proved that when interactions repeat, reciprocity (`Tit-for-Tat`) can hold the line against raw predation (`Always Defect`).

But a duel between two actors is not a society.

What happens when you drop multiple autonomous agents into an arena together? What happens when naive altruists, ruthless exploiters, reciprocal enforcers, unforgiving grudge-holders, and chaotic random actors must all interact in an uncoordinated round-robin tournament?

Does the most ruthless agent conquer the leaderboard?  
Or can cooperation scale beyond isolated pairs into an emergent civilization?

> In Episode 1, we built the laboratory.  
> In Episode 2, we build the society.  
> 
> Give them rules.  
> Give them memory.  
> Give them neighbors.  
> Then let everyone play everyone.  
> 
> See who survives.

---

### The Cast of Characters: 5 Behavioral Archetypes

To explore population dynamics without introducing premature algorithmic complexity, Episode 2 assembles five distinct behavioral archetypes:

```
  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
  │ AlwaysCooperate  │    │   AlwaysDefect   │    │    TitForTat     │
  │  "The Altruist"  │    │  "The Predator"  │    │ "The Enforcer"   │
  └──────────────────┘    └──────────────────┘    └──────────────────┘
                 ┌──────────────────┐    ┌──────────────────┐
                 │   GrimTrigger    │    │      Random      │
                 │  "The Grudger"   │    │  "The Chaos"     │
                 └──────────────────┘    └──────────────────┘
```

1. **`AlwaysCooperateStrategy` (The Altruist)**: Unconditionally chooses `COOPERATE`. Provides maximum benefit to mutual cooperators, but offers zero resistance against predators.
2. **`AlwaysDefectStrategy` (The Predator)**: Unconditionally chooses `DEFECT`. Seeks immediate maximum payoff on every turn, refusing to ever give an inch.
3. **`TitForTatStrategy` (The Reciprocal Enforcer)**: Starts with `COOPERATE`. In every subsequent round, mirrors the exact action its opponent took in their previous round. It is *nice* (never defects first), *retaliatory* (punishes defection immediately), and *forgiving* (returns to cooperation the moment the opponent cooperates).
4. **`GrimTriggerStrategy` (The Unforgiving Grudger)**: Starts with `COOPERATE`. It continues cooperating indefinitely—until the opponent defects even a single time. From that round forward, it permanently defects for the rest of the match. It is nice, retaliatory, but *completely unforgiving*.
5. **`RandomStrategy` (The Chaos Agent)**: Flips a coin on every round (with a deterministic seed for reproducibility). It tests how robust cooperative structures are when an unpredictable actor enters the room.

---

### Moving from Matches to Tournaments

In Episode 1, we built `Match`, which coordinates repeated rounds between exactly two agents with atomic isolation.

Episode 2 introduces three foundational domain models:

```
        ┌────────────────────────────────┐
        │           Population           │ ── Enforces uniqueness & strategy isolation
        └───────────────┬────────────────┘
                        │
                        ▼
        ┌────────────────────────────────┐
        │           Tournament           │ ── Schedules round-robin pairings N*(N-1)/2
        └───────────────┬────────────────┘
                        │ executes repeated Match instances
                        ▼
        ┌────────────────────────────────┐
        │        TournamentResult        │ ── Aggregates scores, wins/losses, coop rates
        └───────────────┬────────────────┘
                        │
                        ▼
        ┌────────────────────────────────┐
        │        LeaderboardEntry        │ ── Immutable ranked standings
        └────────────────────────────────┘
```

#### 1. Population Model and Agent Isolation (ADR-011)
A `Population` is an immutable collection of `Agent` instances. It guarantees:
- Every agent has a unique string identifier.
- **Instance Isolation**: Every agent must own a distinct `Strategy` object instance. If an experimenter attempts to register two agents sharing the same stateful strategy instance in a population, `Population` rejects it with a `ValueError`. This prevents subtle state leakages where Agent A's memory pollutes Agent B.

#### 2. Round-Robin Tournament Protocol (ADR-012)
A `Tournament` schedules every agent against every other agent in the population:
$$\text{Total Matches} = \frac{N(N - 1)}{2}$$
For 5 agents, exactly 10 round-robin duels are scheduled. Each match runs for a configured number of repeated rounds (e.g. 30 or 50 rounds) through our verified Episode 1 `Match` engine.

#### 3. Strategy Memory Isolation Across Opponents (ADR-014)
When `TitForTat` finishes a match with `AlwaysDefect` and begins a new match with `AlwaysCooperate`, does it hold a grudge against the cooperator?
**No.** Per ADR-014, stateful strategies strictly partition memory by `opponent_id`. When facing a new opponent, history is clean. An agent punishes the individual who wronged it, not the next bystander.

#### 4. Metrics and Leaderboard Aggregation (ADR-013)
`TournamentResult` compiles individual match results into an immutable leaderboard ranked by:
1. `total_score` (descending)
2. `wins` (descending)
3. `agent_id` (alphabetical ascending tie-breaker)

In addition to points, it measures **cooperation rates**:
- Individual cooperation rate: $\text{cooperations} / \text{rounds\_played}$
- Population cooperation rate: total cooperation actions across all agents divided by total actions taken.

---

### The Experiment: Running the Arena

We executed our simulation across two experimental configurations:
1. **Experiment 1**: The 5 Archetypes (1 of each, 50 rounds per match = 500 total rounds).
2. **Experiment 2**: A 10-Agent Heterogeneous Society (3 Tit-for-Tat, 2 Grim Trigger, 2 Always Defect, 2 Always Cooperate, 1 Random).

Here are the exact results generated by our simulation engine:

#### Experiment 1: The 5-Way Clash

| Rank | Agent | Strategy | Total Score | Avg / Rnd | W - T - L | Coop Rate |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| 🥇 **#1** | **GrimTrigger** | `GrimTriggerStrategy` | **514** | 2.57 | 1 - 2 - 1 | 51.0% |
| 🥈 **#2** | **AlwaysDefect** | `AlwaysDefectStrategy` | **508** | 2.54 | 4 - 0 - 0 | 0.0% |
| 🥉 **#3** | **TitForTat** | `TitForTatStrategy` | **460** | 2.30 | 0 - 3 - 1 | 62.5% |
| **#4** | **AlwaysCooperate** | `AlwaysCooperateStrategy`| **375** | 1.88 | 0 - 2 - 2 | 100.0% |
| **#5** | **Random** | `RandomStrategy` | **361** | 1.80 | 1 - 1 - 2 | 51.5% |

#### Experiment 2: The 10-Agent Society

When we increase the society to 10 agents, something extraordinary happens:

| Rank | Agent | Strategy | Total Score | Avg / Rnd | W - T - L | Coop Rate |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| 🥇 **#1** | **Grim_1** | `GrimTriggerStrategy` | **1163** | 2.58 | 1 - 6 - 2 | 67.3% |
| 🥈 **#2** | **Grim_2** | `GrimTriggerStrategy` | **1139** | 2.53 | 1 - 6 - 2 | 67.3% |
| 🥉 **#3** | **TFT_Gamma** | `TitForTatStrategy` | **1109** | 2.46 | 0 - 7 - 2 | 72.4% |
| **#4** | **TFT_Alpha** | `TitForTatStrategy` | **1108** | 2.46 | 0 - 7 - 2 | 72.7% |
| **#5** | **TFT_Beta** | `TitForTatStrategy` | **1107** | 2.46 | 0 - 6 - 3 | 72.9% |
| **#6** | **Coop_1** | `AlwaysCooperateStrategy`| **975** | 2.17 | 0 - 6 - 3 | 100.0% |
| **#7** | **Defect_1** | `AlwaysDefectStrategy` | **970** | 2.16 | **8 - 1 - 0** | 0.0% |
| **#8** | **Coop_2** | `AlwaysCooperateStrategy`| **969** | 2.15 | 0 - 6 - 3 | 100.0% |
| **#9** | **Defect_2** | `AlwaysDefectStrategy` | **954** | 2.12 | **8 - 1 - 0** | 0.0% |
| **#10**| **Random_1** | `RandomStrategy` | **849** | 1.89 | 3 - 2 - 4 | 48.9% |

---

### The Revelation: The Axelrod Paradox

Look closely at the numbers above. Two astonishing mathematical truths emerge from this simulation:

#### 1. Winning Every Duel Loses the War
Notice the match record of `Defect_1` and `Defect_2`: **8 wins, 1 tie, 0 losses**.  
They did not lose a single match to any opponent in the entire tournament.

Yet on the tournament leaderboard, they finish at **Rank #7 and Rank #9**!

Now look at `TFT_Alpha`: **0 wins, 7 ties, 2 losses**.  
It did not win a single duel against anyone.  
Yet it crushed the predators, outscoring `Defect_1` by **138 points**!

> **The Axelrod Paradox**:  
> In an iterated dilemma, you do not need to "beat" your counterpart to succeed.  
> Reciprocal strategies never score higher than their counterpart in any single match. Against another cooperator, they tie ($3, 3$). Against a defector, they tie or lose slightly ($1, 1$).  
> But because they cultivate stable cooperation with other reciprocal agents, they harvest massive points $(3 \text{ pts/round})$ while predators trap each other in mutual punishment $(1 \text{ pt/round})$.

#### 2. The Fatal Flaw of the Unforgiving Grudger
In our clean simulation, `GrimTrigger` edged ahead of `TitForTat` because against `Random`, once `Random` defected, `Grim` slammed the door shut forever, whereas `TitForTat` tried to cooperate whenever `Random` played cooperate (and got exploited again).

However, `GrimTrigger` carries a catastrophic vulnerability:
**It has zero forgiveness.**  
If even a single accidental betrayal occurs—a temporary network packet drop, a noisy sensor, or an unintended bug—`GrimTrigger` burns the relationship forever.

And that sets the stage for our next great challenge.

---

### What's Coming in Episode 3: The Broken Telephone

What happens when our computational world is no longer perfect?

In Episode 3, we introduce **Noise (The Trembling Hand)**:
- What if an agent decides to cooperate, but with a 2% probability, an electrical glitch or communication failure flips their action to `DEFECT`?
- How will `Tit-for-Tat` respond when its trusted ally accidentally hits `DEFECT`?
- Will mutual retaliation spiral into endless conflict?
- And what new hero strategy emerges to fix the broken telephone?

---

### Reproducibility & Code

All code, tests, and simulation runners are 100% open source and reproducible.

Run the test suite (102 passing tests):
```bash
uv run pytest
```

Run the live cinematic terminal tournament:
```bash
uv run python experiments/episode_02/demo_tournament_cli.py
```

Run the experiment data generator:
```bash
uv run python experiments/episode_02/run_experiment.py
```

Follow the repository: [synthex-labs-hq/the-dilemma-experiment](https://github.com/synthex-labs-hq/the-dilemma-experiment).
