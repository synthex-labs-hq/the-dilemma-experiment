# The Dilemma Experiment: Can Cooperation Survive?

## Episode 2 — The Tournament

### Opening question

In Episode 1, we proved that reciprocal trust can survive against raw exploitation in a repeated one-on-one duel.

But two agents interacting in a vacuum is not a society.

In the real world, individuals do not interact with a single opponent forever. Economic markets, human societies, international alliances, and multi-agent AI ecosystems are made of dozens, thousands, or millions of participants with wildly different incentives and behavioral styles.

What happens when you drop multiple competing personalities into an arena together?

Can reciprocal cooperation still thrive when surrounded by saints, exploiters, legalists, and chaotic wildcards? Or does the presence of exploiters drag the entire population down into universal defection?

> In Episode 1, we tested two agents in isolation.
>
> But human societies, distributed networks, and multi-agent AI systems are not two-player games.
>
> They are arenas of competing personalities—altruists, exploiters, retaliators, unforgiving legalists, and unpredictable wildcards—all interacting simultaneously.
>
> To understand how cooperation survives at scale, we had to build a society.

---

### Scaling from a duel to a society

To model a society, we must transition from an isolated two-player interaction into an uncoordinated multi-agent environment.

In game theory, the gold standard for testing strategy robustness across diverse populations is the **Round-Robin Tournament**, pioneered by political scientist Robert Axelrod in 1980.

In a round-robin tournament of $N$ participants:
- Every agent is paired against every other agent for a repeated multi-round match.
- An agent does not play against itself (no reflexive self-play).
- The total number of unique pairwise matchups scheduled is:
  $$\text{Total Matches} = \frac{N(N - 1)}{2}$$
- An agent's success is not measured by winning any single duel, but by its **cumulative utility** accumulated across all interactions across the entire population.

---

### Meet the five archetypes

To test how cooperation scales, Episode 2 establishes five distinct behavioral archetypes:

1. **The Altruist (`AlwaysCooperateStrategy`)**:
   Unconditionally cooperates on every single round. It represents unconditional altruism—offering total trust and absorbing complete exploitation.
2. **The Predator (`AlwaysDefectStrategy`)**:
   Unconditionally defects on every single round. It seeks immediate individual gain, attempting to extract the maximum payoff ($+5$) from cooperators while offering zero concessions.
3. **The Reciprocal Cop (`TitForTatStrategy`)**:
   Starts with cooperation on round 1. In every subsequent round, it mirrors whatever the opponent did in their previous round. It is nice, provocable, forgiving, and transparent.
4. **The Unforgiving Grudger (`GrimTriggerStrategy`)**:
   Cooperates on round 1 and continues cooperating as long as the opponent cooperates. However, if the opponent defects even once, it locks into permanent defection against that opponent for the remainder of the match. It has zero forgiveness.
5. **The Chaos Agent (`RandomStrategy`)**:
   Flares unpredictable noise into the arena by choosing cooperation or defection via a pseudo-random coin flip (with a deterministic seed for reproducibility).

---

### From a match to a tournament

Just as in Episode 1, we deliberately avoided heavy frameworks, databases, or premature UI layers. We built the tournament engine using clean, minimal domain models:

```text
+--------------------------------------------------+
|                    Population                    |
|         (Strict ID uniqueness & isolation)       |
+------------------------+-------------------------+
                         |
                         v
+------------------------+-------------------------+
|                    Tournament                    |
|        (Schedules N*(N-1)/2 unique duels)        |
+------------------------+-------------------------+
                         | executes repeated
                         | Match instances
                         v
+------------------------+-------------------------+
|                TournamentResult                  |
|          (Scores, W-T-L, & coop rates)           |
+------------------------+-------------------------+
                         |
                         v
+--------------------------------------------------+
|                LeaderboardEntry                  |
|           (Immutable ranked standings)           |
+--------------------------------------------------+
```

The primary domain concepts include:
- `Population`: Immutable collection of `Agent` entities enforcing strict identity uniqueness and strategy instance isolation.
- `Tournament`: Orchestrator scheduling exactly $\frac{N(N-1)}{2}$ round-robin match pairings using `itertools.combinations`.
- `TournamentResult`: Immutable aggregate outcome storing all executed matches, cumulative scores, and population-wide cooperation metrics.
- `LeaderboardEntry`: Immutable per-agent standing capturing rank, total utility, average score per round, win-tie-loss records, and individual cooperation percentage.

---

### Architectural Decisions (ADR-011 through ADR-014)

Before writing the tournament orchestrator, we formalized four Architecture Decision Records (ADRs) to govern multi-agent boundaries:

#### ADR-011: Population Model & Agent Identity
- `Population` wraps an immutable tuple of `Agent` objects.
- Attempting to register duplicate agent IDs raises an immediate `ValueError`.
- To prevent unintended cross-agent state leakage, passing the same stateful `Strategy` instance to multiple agents raises a `ValueError`. Every agent must own an independent `Strategy` object.

#### ADR-012: Round-Robin Pairing Protocol
- For a population of size $N$, the tournament scheduler generates exactly $\frac{N(N-1)}{2}$ unique matches.
- Self-play (`agent_a == agent_b`) is strictly disallowed. To test how a strategy performs against its own kind, multiple distinct agent instances sharing the strategy type are instantiated (e.g., `tft_1`, `tft_2`).
- Each scheduled match reuses the atomic, isolated `Match.execute()` engine built in Episode 1.

#### ADR-013: Tournament Results & Leaderboard Metrics
- Compiles individual match results into an immutable `TournamentResult`.
- Tracks multi-dimensional metrics: cumulative score, average score per round, win/loss/tie tallies, individual cooperation rate, and population-wide cooperation rate.
- Deterministic ranking: sorted by `total_score` (descending), then `wins` (descending), then `agent_id` (alphabetical ascending tie-breaker).

#### ADR-014: Strategy Isolation in Tournaments
- Stateful strategies partition observation memory by `opponent_id`.
- When an agent finishes a match with Opponent A and begins a match with Opponent B, it faces Opponent B with zero carryover prejudice.

---

### Strategy isolation across matches

A subtle challenge in multi-agent tournaments is **cross-opponent memory leakage**.

If `TitForTatStrategy` or `GrimTriggerStrategy` maintained a single flat observation history, a defection by `AlwaysDefect` in Match 1 would cause the agent to defect on round 1 against `AlwaysCooperate` in Match 2!

Under **ADR-014**, all stateful strategies partition their internal state by `opponent_id`. Each agent enters every new matchup clean, reacting strictly to that specific opponent's history.

---

### Implementing the new archetypes

#### 1. Grim Trigger (`GrimTriggerStrategy`)
Cooperates until betrayed once, then defects forever against that opponent:

```python
class GrimTriggerStrategy(Strategy):
    """Cooperates until betrayed once, then defects forever."""

    def __init__(self) -> None:
        self._betrayed_by: set[str] = set()

    def choose_action(self, context: DecisionContext) -> Action:
        if context.opponent_id in self._betrayed_by:
            return Action.DEFECT
        return Action.COOPERATE

    def observe(self, opponent_id: str, action: Action) -> None:
        if action == Action.DEFECT:
            self._betrayed_by.add(opponent_id)
```

#### 2. Random (`RandomStrategy`)
Probabilistic decision making with a deterministic seed:

```python
class RandomStrategy(Strategy):
    """Probabilistic decision making with deterministic seeding."""

    def __init__(
        self,
        seed: int | None = None,
        cooperation_probability: float = 0.5,
    ) -> None:
        if not (0.0 <= cooperation_probability <= 1.0):
            raise ValueError("cooperation_probability must be between 0.0 and 1.0")
        self._random = random.Random(seed)
        self._cooperation_probability = cooperation_probability

    def choose_action(self, context: DecisionContext) -> Action:
        if self._random.random() < self._cooperation_probability:
            return Action.COOPERATE
        return Action.DEFECT
```

---

### The tragedy of the unforgiving

During our simulations, a striking dynamic emerged when **The Grudger (`GrimTrigger`)** interacted with **The Chaos Agent (`Random`)**.

Against cooperators, Grim Trigger is exceptionally effective. It builds deep, compounding mutual trust with `TitForTat` and `AlwaysCooperate`.

However, the moment it interacts with `Random`, the Chaos Agent inevitably defects within the first few rounds. Grim Trigger's fatal flaw immediately activates: **zero forgiveness**.

For all remaining rounds in the match, Grim Trigger refuses to cooperate again—even when the Random agent offers cooperation. It successfully avoids exploitation, but guarantees mutual defection ($+1/+1$).

In a world with even a sliver of noise or unpredictability, **unforgiving perfectionism becomes a self-inflicted punishment trap**.

---

### Empirical Results: The 10-Agent Society

To study how these dynamics interact at scale, we executed a 10-agent tournament ($N=10$, 45 matches, 50 rounds per match = 2,250 total interactions):
- 3 Tit-for-Tat agents (`TFT_Alpha`, `TFT_Beta`, `TFT_Gamma`)
- 2 Grim Trigger agents (`Grim_1`, `Grim_2`)
- 2 Always Defect agents (`Defect_1`, `Defect_2`)
- 2 Always Cooperate agents (`Coop_1`, `Coop_2`)
- 1 Random agent (`Random_1`)

```text
================================================================================
EXPERIMENT 2 LEADERBOARD (10-Agent Society, 50 rounds/match):
================================================================================
RANK  | AGENT            | SCORE   | AVG/RND  | W-T-L     | COOP % 
--------------------------------------------------------------------------------
#1    | Grim_1           | 1163    | 2.58     | 1-6-2     | 67.3  %
#2    | Grim_2           | 1139    | 2.53     | 1-6-2     | 67.3  %
#3    | TFT_Gamma        | 1109    | 2.46     | 0-7-2     | 72.4  %
#4    | TFT_Alpha        | 1108    | 2.46     | 0-7-2     | 72.7  %
#5    | TFT_Beta         | 1107    | 2.46     | 0-6-3     | 72.9  %
#6    | Coop_1           | 975     | 2.17     | 0-6-3     | 100.0 %
#7    | Defect_1         | 970     | 2.16     | 8-1-0     | 0.0   %
#8    | Coop_2           | 969     | 2.15     | 0-6-3     | 100.0 %
#9    | Defect_2         | 954     | 2.12     | 8-1-0     | 0.0   %
#10   | Random_1         | 849     | 1.89     | 3-2-4     | 48.9  %
================================================================================
Population Cooperation Rate: 64.0%
```

---

### The Axelrod Paradox in action

Look closely at `Defect_1`'s record: **8 wins, 1 tie, 0 losses**.
The predator defeated every single agent it faced head-to-head. It did not lose a single duel.

Yet on the final tournament leaderboard, **it finished in 7th place**.

Meanwhile, `TFT_Alpha` won **zero duels** (0 wins, 7 ties, 2 losses). It never beat a single opponent.
Yet it outscored the undefeated predator by **138 cumulative points**, taking a top podium spot.

Why?

```text
Predator vs Anyone:
Wins the opening round (+5), then locks into mutual defection (+1, +1, +1...)
➔ Low cumulative yield.

Tit-for-Tat vs Tit-for-Tat:
Ties every round (+3, +3, +3, +3...)
➔ Massive compounding wealth.
```

Predators win individual battles by burning their relationships. After round one, no reciprocal agent will ever cooperate with them again. They spend their existence trapped in mutual punishment.

Reciprocal agents never "defeat" their partner. But because they cultivate stable, predictable cooperation with other reciprocal actors, they generate **compounding mutual wealth**.

> You do not have to beat your partner to win the tournament.

---

### What Episode 2 can actually do

Episode 2 is fully implemented, verified with 102 passing unit tests, and tagged at `v0.2.0-episode-2`.

Here is what the Episode 2 simulation engine supports:
- **Arbitrary Population Sizing**: Support for populations of any size with strict agent ID validation and strategy isolation.
- **Round-Robin Scheduling**: Automatic generation of $\frac{N(N-1)}{2}$ match pairings with atomic execution.
- **Multi-Metric Leaderboards**: Aggregate scores, per-round averages, win-tie-loss records, individual cooperation rates, and population cooperation rates.
- **Interactive Terminal Demonstration**: Run the live tournament CLI:
  ```bash
  uv run python experiments/episode_02/demo_tournament_cli.py
  ```
- **Deterministic Testing**: Zero-mock verification passing in under 0.20 seconds:
  ```bash
  uv run pytest
  ```

---

# Episode 2 Isn't the Finished World

> Episode 2 gave us a society.
>
> But it is still a pristine, idealized society.

It is important to recognize the boundary of Episode 2. Episode 2 does **not** contain:
- Noise, miscommunication, or transmission errors (actions are transmitted with 100% fidelity).
- Evolutionary reproduction, mutation, or population turnover (agent counts remain static).
- Spatial lattices or local clustering (all agents interact in a fully mixed, well-stirred pool).
- Adaptive learning or dynamic memory thresholds.

---

### The next question is much bigger

Our Episode 2 tournament assumed a clean computational world where an agent's intended action is always executed perfectly.

But in real distributed systems, economics, and human communication, **noise is inevitable**.

What happens if an agent *intends* to cooperate, but a 2% transmission glitch flips their move to defection?
- How will `TitForTat` react when an ally accidentally defects?
- Will a single misunderstanding trigger an endless death spiral of mutual retaliation?
- Can forgiveness survive in the presence of noise?

---

### Episode 3: The Broken Telephone

Episode 3 will introduce **Noise & Miscommunication** into our laboratory:

1. **The Noisy Channel**: Introducing probabilistic execution error $\epsilon$ into match resolution.
2. **The Feud Spiral**: Measuring how quickly reciprocal strategies collapse when mistakes occur.
3. **Generous Tit-for-Tat (`GenerousTitForTat`)**: Forgiving defections with probability $p$ to break revenge cycles.
4. **Pavlov (`WinStayLoseShift`)**: Re-evaluating actions based on outcome satisfaction.

---

### A note from the builder

*The Dilemma Experiment is built manually, incrementally, and transparently.*

*Every architectural choice is documented via Architecture Decision Records (ADRs under `docs/adr/`), verified with zero-mock behavioral unit tests, and committed with conventional commit history.*

*Follow the project development on GitHub: [synthex-labs-hq/the-dilemma-experiment](https://github.com/synthex-labs-hq/the-dilemma-experiment).*
