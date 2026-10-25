import math
from collections.abc import Callable, Mapping

from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.game import Game
from the_dilemma_experiment.domain.generation_result import GenerationResult
from the_dilemma_experiment.domain.population import Population
from the_dilemma_experiment.domain.prisoners_dilemma import PrisonersDilemma
from the_dilemma_experiment.domain.strategy import Strategy
from the_dilemma_experiment.domain.tournament import Tournament

StrategyFactory = Callable[[], Strategy]
StrategySpec = type[Strategy] | StrategyFactory | Strategy


def _normalize_spec(spec: StrategySpec) -> tuple[str, StrategyFactory]:
    """Extract strategy name and fresh instance factory from a strategy specification."""
    if isinstance(spec, type) and issubclass(spec, Strategy):
        return spec.__name__, spec
    if callable(spec):
        sample = spec()
        if not isinstance(sample, Strategy):
            raise TypeError(
                f"Callable strategy factory must return a Strategy instance, got {type(sample)}"
            )
        return sample.__class__.__name__, spec
    if isinstance(spec, Strategy):
        cls = spec.__class__
        # For parameterized strategies, clone using constructor if available
        return cls.__name__, lambda: cls()
    raise TypeError(
        f"Strategy specification must be a Strategy class, factory callable, or Strategy instance; got {type(spec)}"
    )


class EvolutionaryTournament:
    """Simulates multi-generation natural selection via Replicator Dynamics."""

    def __init__(
        self,
        initial_population: Mapping[StrategySpec, int],
        rounds_per_match: int = 10,
        game: Game | None = None,
        noise: float = 0.0,
        seed: int | None = None,
        retain_tournament_results: bool = False,
    ) -> None:
        if not isinstance(initial_population, Mapping) or not initial_population:
            raise ValueError("initial_population must be a non-empty mapping of strategies to counts")

        if not isinstance(rounds_per_match, int) or rounds_per_match < 1:
            raise ValueError(
                f"rounds_per_match must be an integer >= 1, got {rounds_per_match}"
            )

        if game is not None and not isinstance(game, Game):
            raise TypeError(f"game must be a Game instance, got {type(game)}")

        if isinstance(noise, bool) or not isinstance(noise, (float, int)):
            raise TypeError("noise must be a float or int")
        if not (0.0 <= noise <= 1.0):
            raise ValueError("noise must be between 0.0 and 1.0")

        if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int)):
            raise TypeError("seed must be an integer or None")

        self._game = game if game is not None else PrisonersDilemma()
        self._rounds_per_match = rounds_per_match
        self._noise = float(noise)
        self._seed = seed
        self._retain_tournament_results = retain_tournament_results

        # Normalize strategies and factories
        self._factories: dict[str, StrategyFactory] = {}
        self._current_counts: dict[str, int] = {}

        for spec, count in initial_population.items():
            if not isinstance(count, int) or count < 0:
                raise ValueError(f"Count for strategy must be a non-negative integer, got {count}")
            name, factory = _normalize_spec(spec)
            if name in self._factories and count > 0:
                # Merge count if duplicate name registered
                self._current_counts[name] += count
            else:
                self._factories[name] = factory
                self._current_counts[name] = count

        self._carrying_capacity = sum(self._current_counts.values())
        if self._carrying_capacity < 2:
            raise ValueError(
                f"Total population size must be at least 2 agents, got {self._carrying_capacity}"
            )

        self._generation_index = 0
        self._history: list[GenerationResult] = []
        self._all_strategy_names = tuple(sorted(self._factories.keys()))
        self._extinct_strategies: set[str] = {
            name for name, c in self._current_counts.items() if c == 0
        }

    @property
    def carrying_capacity(self) -> int:
        """Fixed total population carrying capacity (N)."""
        return self._carrying_capacity

    @property
    def rounds_per_match(self) -> int:
        """Rounds per match in each generation's tournament."""
        return self._rounds_per_match

    @property
    def noise(self) -> float:
        """Noise rate applied to matches."""
        return self._noise

    @property
    def seed(self) -> int | None:
        """Master random seed."""
        return self._seed

    @property
    def current_generation(self) -> int:
        """Index of the current generation."""
        return self._generation_index

    @property
    def current_counts(self) -> dict[str, int]:
        """Current population count per strategy archetype."""
        return dict(self._current_counts)

    @property
    def current_shares(self) -> dict[str, float]:
        """Current population share (proportion) per strategy archetype."""
        return {
            name: round(c / self._carrying_capacity, 4)
            for name, c in self._current_counts.items()
        }

    @property
    def history(self) -> tuple[GenerationResult, ...]:
        """Chronological ledger of all completed generation results."""
        return tuple(self._history)

    @property
    def extinct_strategies(self) -> tuple[str, ...]:
        """Alphabetically sorted tuple of all extinct strategy archetype names."""
        return tuple(sorted(self._extinct_strategies))

    @property
    def active_strategies(self) -> tuple[str, ...]:
        """Alphabetically sorted tuple of all currently active strategy archetype names."""
        return tuple(sorted(name for name, c in self._current_counts.items() if c > 0))

    @property
    def is_converged(self) -> bool:
        """Check whether the population has reached an absorbing fixation state."""
        active = [name for name, c in self._current_counts.items() if c > 0]
        return len(active) <= 1

    def step(self) -> GenerationResult:
        """Advance the simulation by exactly one generation using Replicator Dynamics."""
        active_strategies = [name for name, c in self._current_counts.items() if c > 0]
        n_pop = self._carrying_capacity

        # Instantiate fresh agents for each active seat
        agents: list[Agent] = []
        agent_strategy_map: dict[str, str] = {}

        for strat_name in sorted(active_strategies):
            count = self._current_counts[strat_name]
            factory = self._factories[strat_name]
            for idx in range(count):
                agent_id = f"{strat_name}_{self._generation_index}_{idx}"
                agent = Agent(agent_id, factory())
                agents.append(agent)
                agent_strategy_map[agent_id] = strat_name

        # Derive generation tournament seed deterministically
        gen_seed = (
            (self._seed * 31 + self._generation_index * 10007) % (2**31 - 1)
            if self._seed is not None
            else None
        )

        population = Population(agents)
        tournament = Tournament(
            population=population,
            game=self._game,
            rounds_per_match=self._rounds_per_match,
            noise=self._noise,
            seed=gen_seed,
        )
        tournament_result = tournament.execute()

        # Compute empirical scores and fitness per strategy
        strategy_total_scores: dict[str, int] = {name: 0 for name in self._all_strategy_names}
        for entry in tournament_result.leaderboard:
            strat = agent_strategy_map[entry.agent_id]
            strategy_total_scores[strat] += entry.total_score

        strategy_avg_fitness: dict[str, float] = {}
        for name in self._all_strategy_names:
            c = self._current_counts[name]
            strategy_avg_fitness[name] = round(strategy_total_scores[name] / c, 4) if c > 0 else 0.0

        total_pop_score = sum(strategy_total_scores.values())
        mean_pop_fitness = total_pop_score / n_pop if n_pop > 0 else 0.0

        # Calculate Replicator Dynamics offspring counts via Largest Remainder Method
        next_counts: dict[str, int] = {name: 0 for name in self._all_strategy_names}

        if total_pop_score > 0 and len(active_strategies) > 1:
            quotas: dict[str, float] = {}
            base_seats: dict[str, int] = {}
            remainders: dict[str, float] = {}

            for strat in active_strategies:
                q = (strategy_total_scores[strat] / total_pop_score) * n_pop
                quotas[strat] = q
                base_seats[strat] = math.floor(q)
                remainders[strat] = q - base_seats[strat]

            allocated_seats = sum(base_seats.values())
            leftover = n_pop - allocated_seats

            # Sort active strategies by remainder desc, breaking ties alphabetically
            sorted_by_remainder = sorted(
                active_strategies,
                key=lambda s: (-remainders[s], s),
            )

            for strat in active_strategies:
                next_counts[strat] = base_seats[strat]

            for i in range(leftover):
                winner_strat = sorted_by_remainder[i % len(sorted_by_remainder)]
                next_counts[winner_strat] += 1
        else:
            # Fixation or zero fitness: maintain current counts
            for strat in self._all_strategy_names:
                next_counts[strat] = self._current_counts[strat]

        # Audit newly extinct strategies
        newly_extinct: list[str] = []
        for name in sorted(self._all_strategy_names):
            if self._current_counts[name] > 0 and next_counts[name] == 0:
                newly_extinct.append(name)
                self._extinct_strategies.add(name)

        gen_result = GenerationResult(
            generation=self._generation_index,
            population_counts=dict(self._current_counts),
            population_shares={
                name: round(c / n_pop, 4) for name, c in self._current_counts.items()
            },
            average_fitness=dict(strategy_avg_fitness),
            mean_population_fitness=round(mean_pop_fitness, 4),
            extinct_strategies=tuple(sorted(self._extinct_strategies)),
            newly_extinct=tuple(newly_extinct),
            active_strategies=tuple(sorted(active_strategies)),
            total_population=n_pop,
            tournament_result=tournament_result if self._retain_tournament_results else None,
        )

        self._history.append(gen_result)
        self._current_counts = next_counts
        self._generation_index += 1

        return gen_result

    def run(self, generations: int) -> list[GenerationResult]:
        """Execute multiple generations until completion or convergence."""
        if not isinstance(generations, int) or generations < 1:
            raise ValueError(f"generations must be an integer >= 1, got {generations}")

        results: list[GenerationResult] = []
        for _ in range(generations):
            res = self.step()
            results.append(res)
            if self.is_converged:
                break
        return results
