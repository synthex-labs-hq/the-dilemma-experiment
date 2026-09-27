import random

from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.game import Game
from the_dilemma_experiment.domain.match_result import MatchResult
from the_dilemma_experiment.domain.round import Round


class Match:
    """Represents repeated interaction between two agents."""

    def __init__(
        self,
        first_agent: Agent,
        second_agent: Agent,
        game: Game,
        round_count: int,
        noise: float = 0.0,
        seed: int | None = None,
    ) -> None:
        """Create a repeated interaction between two agents."""

        if not isinstance(round_count, int) or isinstance(round_count, bool):
            raise TypeError("round_count must be an integer.")

        if round_count <= 0:
            raise ValueError("round_count must be greater than zero.")

        if first_agent.id == second_agent.id:
            raise ValueError("A match requires two agents with different IDs.")

        if isinstance(noise, bool) or not isinstance(noise, (float, int)):
            raise TypeError("noise must be a float or int.")

        if not (0.0 <= noise <= 1.0):
            raise ValueError("noise must be between 0.0 and 1.0.")

        if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int)):
            raise TypeError("seed must be an integer or None.")

        self._first_agent = first_agent
        self._second_agent = second_agent
        self._game = game
        self._round_count = round_count
        self._noise = float(noise)
        self._seed = seed
        self._rng = random.Random(seed)

        self._rounds: list[Round] = []
        self._result: MatchResult | None = None
        self._executed = False

    @property
    def noise(self) -> float:
        """Return the channel noise probability (0.0 to 1.0)."""
        return self._noise

    @property
    def seed(self) -> int | None:
        """Return the random seed configured for this match."""
        return self._seed

    @property
    def rounds(self) -> tuple[Round, ...]:
        """Return the ordered history of completed rounds."""
        return tuple(self._rounds)

    @property
    def result(self) -> MatchResult | None:
        """Return the aggregate outcome of a completed match, or None if unexecuted."""
        return self._result

    def execute(self) -> tuple[Round, ...]:
        """Execute the configured repeated interaction."""
        if self._executed:
            raise RuntimeError("A match can only be executed once.")

        temporary_rounds: list[Round] = []
        for _ in range(self._round_count):
            round_result = self._execute_round()
            temporary_rounds.append(round_result)

        first_score = sum(r.payoff.first for r in temporary_rounds)
        second_score = sum(r.payoff.second for r in temporary_rounds)

        self._result = MatchResult(
            first_agent_id=self._first_agent.id,
            second_agent_id=self._second_agent.id,
            first_score=first_score,
            second_score=second_score,
        )
        self._rounds = temporary_rounds
        self._executed = True

        return self.rounds

    def _execute_round(self) -> Round:
        """Execute one interaction round and return its completed result."""
        first_context = DecisionContext(opponent_id=self._second_agent.id)
        first_intended = self._first_agent.strategy.choose_action(first_context)

        second_context = DecisionContext(opponent_id=self._first_agent.id)
        second_intended = self._second_agent.strategy.choose_action(second_context)

        first_action = first_intended
        second_action = second_intended

        if self._noise > 0.0:
            if self._rng.random() < self._noise:
                first_action = first_intended.opposite()
            if self._rng.random() < self._noise:
                second_action = second_intended.opposite()

        payoff = self._game.resolve(first_action, second_action)

        round_result = Round(
            first_agent_id=self._first_agent.id,
            second_agent_id=self._second_agent.id,
            first_action=first_action,
            second_action=second_action,
            payoff=payoff,
            first_intended_action=first_intended,
            second_intended_action=second_intended,
        )

        self._first_agent.strategy.observe(self._second_agent.id, second_action)
        self._second_agent.strategy.observe(self._first_agent.id, first_action)

        return round_result
