# ADR-013: Tournament Results and Leaderboard Metrics

## Status

Accepted

## Context

In Episode 1, `MatchResult` captured the aggregate outcome of a single match between two agents (participant IDs and final scores).

In Episode 2, a tournament produces dozens or hundreds of individual match outcomes. To extract scientific insights, we need:
1. An aggregate value object that encapsulates all completed matches.
2. Per-agent performance metrics (total score, average score per round, win/tie/loss records).
3. Behavioral cooperation metrics (individual cooperation rate, population-level cooperation rate).
4. A deterministic leaderboard sorted by score with defined tie-breaking rules.
5. Immutability so results cannot be mutated post-execution.

## Decision

1. **Immutable `LeaderboardEntry`**:
   An immutable dataclass representing the summarized performance of a single agent:
   - `rank: int` (1-indexed)
   - `agent_id: str`
   - `strategy_name: str`
   - `total_score: int`
   - `matches_played: int`
   - `rounds_played: int`
   - `average_score_per_round: float`
   - `wins: int`
   - `ties: int`
   - `losses: int`
   - `cooperations: int`
   - `defections: int`
   - `cooperation_rate: float` (ratio of `cooperations / rounds_played`)

2. **Ranking and Tie-Breaking**:
   Leaderboard entries are sorted by:
   1. `total_score` (descending)
   2. `wins` (descending)
   3. `agent_id` (alphabetical ascending, for deterministic reproducibility)

3. **Immutable `TournamentResult` Value Object**:
   A read-only object containing:
   - `match_results`: A tuple of all completed `MatchResult` objects.
   - `leaderboard`: A tuple of `LeaderboardEntry` objects sorted by rank.
   - `total_matches`: Total number of matches executed.
   - `total_rounds`: Total number of rounds across all matches.
   - `population_cooperation_rate`: Overall proportion of `COOPERATE` choices across all rounds played by all agents.
   - `get_entry(agent_id: str) -> LeaderboardEntry`: Direct lookup by agent ID.

4. **Separation of Computation and Presentation**:
   `TournamentResult` contains purely numerical and structural domain data. Formatted tables, terminal ASCII rendering, and chart plotting remain in application/experiment scripts (`experiments/episode_02/`).

## Consequences

### Positive
- Rich, multi-dimensional metrics beyond simple win/loss tallies.
- Cooperation rates allow testing key game-theoretic hypotheses (e.g., whether high cooperation correlates with high total score).
- Deterministic ranking ensures reproducible tournament reporting.
- Clean separation between core metrics and terminal/visual rendering.

### Negative / Trade-offs
- Aggregating detailed round-by-round statistics requires iterating over all completed matches during `TournamentResult` construction.
