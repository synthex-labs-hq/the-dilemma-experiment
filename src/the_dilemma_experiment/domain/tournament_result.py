from dataclasses import dataclass

from the_dilemma_experiment.domain.match_result import MatchResult


@dataclass(frozen=True)
class LeaderboardEntry:
    """Individual agent's performance record in a completed tournament."""

    rank: int
    agent_id: str
    strategy_name: str
    total_score: int
    matches_played: int
    rounds_played: int
    average_score_per_round: float
    wins: int
    ties: int
    losses: int
    cooperations: int
    defections: int
    cooperation_rate: float


class TournamentResult:
    """Immutable aggregate outcome and statistics of a completed tournament."""

    def __init__(
        self,
        match_results: tuple[MatchResult, ...],
        leaderboard: tuple[LeaderboardEntry, ...],
        total_matches: int,
        total_rounds: int,
        population_cooperation_rate: float,
    ) -> None:
        self._match_results = tuple(match_results)
        self._leaderboard = tuple(leaderboard)
        self._total_matches = total_matches
        self._total_rounds = total_rounds
        self._population_cooperation_rate = population_cooperation_rate
        self._entries_by_agent: dict[str, LeaderboardEntry] = {
            entry.agent_id: entry for entry in self._leaderboard
        }

    @property
    def match_results(self) -> tuple[MatchResult, ...]:
        """All individual match results in the tournament."""
        return self._match_results

    @property
    def leaderboard(self) -> tuple[LeaderboardEntry, ...]:
        """Ranked leaderboard entries, sorted by total score descending."""
        return self._leaderboard

    @property
    def winner(self) -> LeaderboardEntry:
        """The top-ranking entry on the leaderboard."""
        if not self._leaderboard:
            raise ValueError("No entries on leaderboard")
        return self._leaderboard[0]

    @property
    def total_matches(self) -> int:
        """Total number of matches executed in the tournament."""
        return self._total_matches

    @property
    def total_rounds(self) -> int:
        """Total number of rounds executed across all matches."""
        return self._total_rounds

    @property
    def population_cooperation_rate(self) -> float:
        """Overall proportion of cooperation choices across all actions."""
        return self._population_cooperation_rate

    def get_entry(self, agent_id: str) -> LeaderboardEntry:
        """Retrieve the leaderboard entry for a specific agent ID."""
        if agent_id not in self._entries_by_agent:
            raise KeyError(f"Agent '{agent_id}' not found in leaderboard")
        return self._entries_by_agent[agent_id]

    def __repr__(self) -> str:
        winner_id = self.winner.agent_id if self._leaderboard else "None"
        return (
            f"TournamentResult(total_matches={self._total_matches}, "
            f"total_rounds={self._total_rounds}, winner='{winner_id}', "
            f"cooperation_rate={self._population_cooperation_rate:.2%})"
        )
