import itertools
from collections import defaultdict

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.game import Game
from the_dilemma_experiment.domain.match import Match
from the_dilemma_experiment.domain.match_result import MatchResult
from the_dilemma_experiment.domain.population import Population
from the_dilemma_experiment.domain.tournament_result import (
    LeaderboardEntry,
    TournamentResult,
)


class Tournament:
    """Orchestrates a round-robin tournament across an agent population."""

    def __init__(
        self,
        population: Population,
        game: Game,
        rounds_per_match: int,
    ) -> None:
        if not isinstance(population, Population):
            raise TypeError(f"population must be a Population instance, got {type(population)}")
        if population.size < 2:
            raise ValueError(
                f"Tournament requires a population of at least 2 agents, got {population.size}"
            )
        if not isinstance(game, Game):
            raise TypeError(f"game must be a Game instance, got {type(game)}")
        if not isinstance(rounds_per_match, int) or rounds_per_match < 1:
            raise ValueError(f"rounds_per_match must be an integer >= 1, got {rounds_per_match}")

        self._population = population
        self._game = game
        self._rounds_per_match = rounds_per_match
        self._matches: tuple[Match, ...] = ()
        self._result: TournamentResult | None = None
        self._has_executed: bool = False

    @property
    def population(self) -> Population:
        """The population of participating agents."""
        return self._population

    @property
    def game(self) -> Game:
        """The game rules engine."""
        return self._game

    @property
    def rounds_per_match(self) -> int:
        """Number of repeated rounds played in each match."""
        return self._rounds_per_match

    @property
    def matches(self) -> tuple[Match, ...]:
        """All executed Match instances in the tournament."""
        return self._matches

    @property
    def result(self) -> TournamentResult | None:
        """The tournament results, or None if not yet executed."""
        return self._result

    def execute(self) -> TournamentResult:
        """Execute the round-robin tournament atomically.

        Every unique pair of agents plays exactly one Match of rounds_per_match rounds.
        Returns an immutable TournamentResult.
        """
        if self._has_executed:
            raise RuntimeError("Tournament has already been executed")

        pairings = list(itertools.combinations(self._population.agents, 2))
        temporary_matches: list[Match] = []
        temporary_match_results: list[MatchResult] = []

        scores: dict[str, int] = defaultdict(int)
        wins: dict[str, int] = defaultdict(int)
        ties: dict[str, int] = defaultdict(int)
        losses: dict[str, int] = defaultdict(int)
        cooperations: dict[str, int] = defaultdict(int)
        defections: dict[str, int] = defaultdict(int)
        rounds_played: dict[str, int] = defaultdict(int)
        matches_played: dict[str, int] = defaultdict(int)

        # Initialize all participants in dictionaries to guarantee entries even if 0
        for agent in self._population.agents:
            scores[agent.id] = 0
            wins[agent.id] = 0
            ties[agent.id] = 0
            losses[agent.id] = 0
            cooperations[agent.id] = 0
            defections[agent.id] = 0
            rounds_played[agent.id] = 0
            matches_played[agent.id] = 0

        # Execute each scheduled match
        for agent_a, agent_b in pairings:
            match = Match(
                first_agent=agent_a,
                second_agent=agent_b,
                game=self._game,
                round_count=self._rounds_per_match,
            )
            completed_rounds = match.execute()
            res = match.result
            if res is None:
                raise RuntimeError("Match completed without producing a result")

            temporary_matches.append(match)
            temporary_match_results.append(res)

            scores[res.first_agent_id] += res.first_score
            scores[res.second_agent_id] += res.second_score
            matches_played[res.first_agent_id] += 1
            matches_played[res.second_agent_id] += 1

            if res.first_score > res.second_score:
                wins[res.first_agent_id] += 1
                losses[res.second_agent_id] += 1
            elif res.second_score > res.first_score:
                wins[res.second_agent_id] += 1
                losses[res.first_agent_id] += 1
            else:
                ties[res.first_agent_id] += 1
                ties[res.second_agent_id] += 1

            for r in completed_rounds:
                if r.first_action == Action.COOPERATE:
                    cooperations[r.first_agent_id] += 1
                else:
                    defections[r.first_agent_id] += 1

                if r.second_action == Action.COOPERATE:
                    cooperations[r.second_agent_id] += 1
                else:
                    defections[r.second_agent_id] += 1

                rounds_played[r.first_agent_id] += 1
                rounds_played[r.second_agent_id] += 1

        total_actions = sum(cooperations.values()) + sum(defections.values())
        population_coop_rate = (
            sum(cooperations.values()) / total_actions if total_actions > 0 else 0.0
        )

        # Sort agents per ADR-013: total_score desc, wins desc, agent_id asc
        sorted_agents = sorted(
            self._population.agents,
            key=lambda a: (-scores[a.id], -wins[a.id], a.id),
        )

        leaderboard_entries: list[LeaderboardEntry] = []
        for rank, agent in enumerate(sorted_agents, 1):
            aid = agent.id
            rp = rounds_played[aid]
            avg_score = scores[aid] / rp if rp > 0 else 0.0
            coop_rate = cooperations[aid] / rp if rp > 0 else 0.0

            entry = LeaderboardEntry(
                rank=rank,
                agent_id=aid,
                strategy_name=agent.strategy.__class__.__name__,
                total_score=scores[aid],
                matches_played=matches_played[aid],
                rounds_played=rp,
                average_score_per_round=round(avg_score, 4),
                wins=wins[aid],
                ties=ties[aid],
                losses=losses[aid],
                cooperations=cooperations[aid],
                defections=defections[aid],
                cooperation_rate=round(coop_rate, 4),
            )
            leaderboard_entries.append(entry)

        total_matches = len(temporary_matches)
        total_rounds = sum(len(m.rounds) for m in temporary_matches)

        tournament_result = TournamentResult(
            match_results=tuple(temporary_match_results),
            leaderboard=tuple(leaderboard_entries),
            total_matches=total_matches,
            total_rounds=total_rounds,
            population_cooperation_rate=round(population_coop_rate, 4),
        )

        # Atomic commit
        self._matches = tuple(temporary_matches)
        self._result = tournament_result
        self._has_executed = True

        return self._result
