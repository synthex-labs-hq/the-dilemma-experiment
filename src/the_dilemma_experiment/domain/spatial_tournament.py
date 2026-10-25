"""Spatial tournament and local imitation evolutionary dynamics."""

import random
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.game import Game
from the_dilemma_experiment.domain.match import Match
from the_dilemma_experiment.domain.prisoners_dilemma import (
    DEFAULT_PAYOFF_MATRIX,
    PrisonersDilemma,
)
from the_dilemma_experiment.domain.strategy import Strategy
from the_dilemma_experiment.domain.topology import SpatialTopology

COOPERATIVE_STRATEGIES: frozenset[str] = frozenset(
    {
        "AlwaysCooperateStrategy",
        "TitForTatStrategy",
        "GenerousTitForTatStrategy",
        "TitForTwoTatsStrategy",
        "WinStayLoseShiftStrategy",
    }
)


class FitnessMode(str, Enum):
    """Fitness evaluation mode for spatial tournament nodes."""

    TOTAL = (
        "total"  # Raw sum of scores across all neighbors (standard on regular lattices)
    )
    AVERAGE = (
        "average"  # Score normalized by node degree (standard on heterogeneous graphs)
    )


@dataclass(frozen=True, slots=True)
class SpatialGenerationResult:
    """Historical telemetry for a single spatial evolutionary generation."""

    generation: int
    strategy_distribution: dict[str, int]
    strategy_proportions: dict[str, float]
    node_strategies: tuple[str, ...]
    node_scores: tuple[float, ...]
    cooperator_clustering_ratio: float
    is_fixated: bool
    dominant_strategy: str


@dataclass(frozen=True)
class SpatialTournamentResult:
    """Complete summary of a multi-generation spatial evolutionary run."""

    generations: list[SpatialGenerationResult]
    converged: bool
    final_generation: int
    dominant_strategy: str

    @property
    def initial_distribution(self) -> dict[str, int]:
        return self.generations[0].strategy_distribution

    @property
    def final_distribution(self) -> dict[str, int]:
        return self.generations[-1].strategy_distribution


class SpatialTournament:
    """Executes spatial interactions and local imitation dynamics on a topology."""

    def __init__(
        self,
        topology: SpatialTopology,
        initial_strategies: Sequence[type[Strategy]],
        game: Game | None = None,
        rounds_per_match: int = 1,
        fitness_mode: FitnessMode = FitnessMode.TOTAL,
        noise_rate: float = 0.0,
        rng: random.Random | None = None,
    ) -> None:
        if len(initial_strategies) != topology.node_count:
            raise ValueError(
                f"Initial strategies count ({len(initial_strategies)}) must match topology node count ({topology.node_count})."
            )

        self._topology = topology
        self._current_strategies: list[type[Strategy]] = list(initial_strategies)
        self._game: Game = (
            game if game is not None else PrisonersDilemma(DEFAULT_PAYOFF_MATRIX)
        )
        self._rounds_per_match = rounds_per_match
        self._fitness_mode = fitness_mode
        self._noise_rate = noise_rate
        self._rng = rng if rng is not None else random.Random()
        self._generation_index = 0
        self._history: list[SpatialGenerationResult] = []

        # Record initial baseline (generation 0 before any matches)
        initial_telemetry = self._compute_telemetry(
            gen_idx=0,
            strategies=self._current_strategies,
            scores=[0.0] * self._topology.node_count,
        )
        self._history.append(initial_telemetry)

    @property
    def topology(self) -> SpatialTopology:
        return self._topology

    @property
    def current_strategies(self) -> list[type[Strategy]]:
        return list(self._current_strategies)

    @property
    def history(self) -> list[SpatialGenerationResult]:
        return list(self._history)

    def step(self) -> SpatialGenerationResult:
        """Advance the spatial simulation by one generation."""
        node_count = self._topology.node_count
        raw_scores = [0.0] * node_count

        # 1. Symmetric edge match execution (ADR-020)
        edges = self._topology.edges()
        for u, v in edges:
            strat_u_cls = self._current_strategies[u]
            strat_v_cls = self._current_strategies[v]

            agent_u = Agent(id=f"node_{u}", strategy=strat_u_cls())
            agent_v = Agent(id=f"node_{v}", strategy=strat_v_cls())

            match_seed = (
                self._rng.randint(0, 2**31 - 1) if self._noise_rate > 0.0 else None
            )
            match = Match(
                first_agent=agent_u,
                second_agent=agent_v,
                game=self._game,
                round_count=self._rounds_per_match,
                noise=self._noise_rate,
                seed=match_seed,
            )
            match.execute()
            if match.result is not None:
                raw_scores[u] += float(match.result.first_score)
                raw_scores[v] += float(match.result.second_score)

        # 2. Fitness evaluation (Total vs Average)
        fitness_scores = [0.0] * node_count
        for i in range(node_count):
            if self._fitness_mode == FitnessMode.AVERAGE:
                deg = self._topology.degree(i)
                fitness_scores[i] = raw_scores[i] / deg if deg > 0 else 0.0
            else:
                fitness_scores[i] = raw_scores[i]

        # 3. Synchronous local imitation (Nowak-May 1992)
        next_strategies: list[type[Strategy]] = [
            self._current_strategies[0]
        ] * node_count
        for u in range(node_count):
            current_cls = self._current_strategies[u]
            current_score = fitness_scores[u]

            best_score = current_score
            best_candidates: list[type[Strategy]] = [current_cls]

            neighbors = self._topology.neighbors(u)
            for v in neighbors:
                v_score = fitness_scores[v]
                v_cls = self._current_strategies[v]

                if v_score > best_score:
                    best_score = v_score
                    best_candidates = [v_cls]
                elif v_score == best_score:
                    if v_cls not in best_candidates:
                        best_candidates.append(v_cls)

            # Inertia rule: if current strategy achieved the best score, retain it!
            if current_cls in best_candidates:
                next_strategies[u] = current_cls
            else:
                # Deterministic tie-breaking: alphabetically by strategy class name
                best_candidates.sort(key=lambda cls: cls.__name__)
                next_strategies[u] = best_candidates[0]

        self._generation_index += 1
        self._current_strategies = next_strategies

        telemetry = self._compute_telemetry(
            gen_idx=self._generation_index,
            strategies=self._current_strategies,
            scores=fitness_scores,
        )
        self._history.append(telemetry)
        return telemetry

    def run(self, max_generations: int) -> SpatialTournamentResult:
        """Run the spatial tournament until max_generations or fixation."""
        if max_generations < 1:
            raise ValueError(
                f"max_generations must be at least 1. Got {max_generations}."
            )

        for _ in range(max_generations):
            latest = self.step()
            if latest.is_fixated:
                break

        final_gen = self._history[-1]
        return SpatialTournamentResult(
            generations=list(self._history),
            converged=final_gen.is_fixated,
            final_generation=final_gen.generation,
            dominant_strategy=final_gen.dominant_strategy,
        )

    def _compute_telemetry(
        self,
        gen_idx: int,
        strategies: list[type[Strategy]],
        scores: list[float],
    ) -> SpatialGenerationResult:
        node_count = len(strategies)
        strat_names = [cls.__name__ for cls in strategies]

        dist: dict[str, int] = {}
        for name in strat_names:
            dist[name] = dist.get(name, 0) + 1

        props = {name: count / node_count for name, count in dist.items()}
        sorted_dist = sorted(dist.items(), key=lambda item: (-item[1], item[0]))
        dominant_strat = sorted_dist[0][0]
        is_fixated = len(dist) == 1

        # Cooperator clustering ratio
        coop_nodes = [
            i for i, name in enumerate(strat_names) if name in COOPERATIVE_STRATEGIES
        ]
        if not coop_nodes:
            clustering_ratio = 0.0
        else:
            total_coop_edges = 0
            total_possible_coop_edges = 0
            for u in coop_nodes:
                nbrs = self._topology.neighbors(u)
                total_possible_coop_edges += len(nbrs)
                total_coop_edges += sum(
                    1 for v in nbrs if strat_names[v] in COOPERATIVE_STRATEGIES
                )
            clustering_ratio = (
                total_coop_edges / total_possible_coop_edges
                if total_possible_coop_edges > 0
                else 0.0
            )

        return SpatialGenerationResult(
            generation=gen_idx,
            strategy_distribution=dist,
            strategy_proportions=props,
            node_strategies=tuple(strat_names),
            node_scores=tuple(scores),
            cooperator_clustering_ratio=clustering_ratio,
            is_fixated=is_fixated,
            dominant_strategy=dominant_strat,
        )
