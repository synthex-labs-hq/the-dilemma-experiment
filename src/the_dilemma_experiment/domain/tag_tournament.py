"""Tag-based tournament engines for static stranger interactions and evolutionary dynamics."""

import random
from collections.abc import Sequence
from dataclasses import dataclass

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.game import Game
from the_dilemma_experiment.domain.prisoners_dilemma import (
    DEFAULT_PAYOFF_MATRIX,
    PrisonersDilemma,
)
from the_dilemma_experiment.domain.tag import (
    TagProfile,
    TagToleranceStrategy,
    calculate_shannon_diversity,
    compute_tag_distance,
)


@dataclass(frozen=True, slots=True)
class TagLeaderboardEntry:
    """Performance summary of an agent in a tag tournament."""

    rank: int
    agent_id: str
    strategy_name: str
    tag: float | str
    tolerance: float
    total_score: int
    matches_played: int
    average_score: float
    in_group_matches: int
    out_group_matches: int
    in_group_cooperation_rate: float
    out_group_cooperation_rate: float


@dataclass(frozen=True)
class TagTournamentResult:
    """Summary of a static tag-based tournament."""

    leaderboard: list[TagLeaderboardEntry]
    total_matches: int
    total_cooperations: int
    total_defections: int
    overall_cooperation_rate: float
    in_group_cooperation_rate: float
    out_group_cooperation_rate: float
    mean_tolerance: float
    tag_shannon_diversity: float


class TagTournament:
    """Executes stranger matches where agents condition choices on observed tags and tolerance."""

    def __init__(
        self,
        agents: Sequence[Agent],
        game: Game | None = None,
        torus: bool = False,
        rng: random.Random | None = None,
    ) -> None:
        if len(agents) < 2:
            raise ValueError(f"Tag tournament requires at least 2 agents. Got {len(agents)}.")

        self._agents = list(agents)
        self._game: Game = game if game is not None else PrisonersDilemma(DEFAULT_PAYOFF_MATRIX)
        self._torus = torus
        self._rng = rng if rng is not None else random.Random()

    def run_stranger_pairings(
        self,
        pairings_per_agent: int = 20,
        rounds_per_match: int = 1,
    ) -> TagTournamentResult:
        """Run random pairings between strangers, providing tags in DecisionContext."""
        scores: dict[str, int] = {a.id: 0 for a in self._agents}
        matches_played: dict[str, int] = {a.id: 0 for a in self._agents}

        in_group_matches: dict[str, int] = {a.id: 0 for a in self._agents}
        out_group_matches: dict[str, int] = {a.id: 0 for a in self._agents}
        in_group_coops: dict[str, int] = {a.id: 0 for a in self._agents}
        out_group_coops: dict[str, int] = {a.id: 0 for a in self._agents}

        total_matches = 0
        total_coops = 0
        total_defects = 0

        total_in_group_coops = 0
        total_in_group_actions = 0
        total_out_group_coops = 0
        total_out_group_actions = 0

        # Extract tags and tolerances
        agent_profiles: dict[str, TagProfile] = {}
        for a in self._agents:
            strat = a.strategy
            t_val = getattr(strat, "tag", 0.0)
            tol_val = getattr(strat, "tolerance", 0.0)
            agent_profiles[a.id] = TagProfile(tag=t_val, tolerance=tol_val)

        total_pairings = (len(self._agents) * pairings_per_agent) // 2

        for _ in range(total_pairings):
            a_idx, b_idx = self._rng.sample(range(len(self._agents)), 2)
            agent_a = self._agents[a_idx]
            agent_b = self._agents[b_idx]
            prof_a = agent_profiles[agent_a.id]
            prof_b = agent_profiles[agent_b.id]

            total_matches += 1
            matches_played[agent_a.id] += 1
            matches_played[agent_b.id] += 1

            dist = compute_tag_distance(prof_a.tag, prof_b.tag, torus=self._torus)
            a_considers_b_ingroup = dist <= prof_a.tolerance
            b_considers_a_ingroup = dist <= prof_b.tolerance

            if a_considers_b_ingroup:
                in_group_matches[agent_a.id] += 1
            else:
                out_group_matches[agent_a.id] += 1

            if b_considers_a_ingroup:
                in_group_matches[agent_b.id] += 1
            else:
                out_group_matches[agent_b.id] += 1

            for _ in range(rounds_per_match):
                ctx_a = DecisionContext(
                    opponent_id=agent_b.id,
                    opponent_tag=prof_b.tag,
                    self_tag=prof_a.tag,
                )
                ctx_b = DecisionContext(
                    opponent_id=agent_a.id,
                    opponent_tag=prof_a.tag,
                    self_tag=prof_b.tag,
                )

                act_a = agent_a.strategy.choose_action(ctx_a)
                act_b = agent_b.strategy.choose_action(ctx_b)

                # Track action counts
                if act_a == Action.COOPERATE:
                    total_coops += 1
                    if a_considers_b_ingroup:
                        in_group_coops[agent_a.id] += 1
                        total_in_group_coops += 1
                    else:
                        out_group_coops[agent_a.id] += 1
                        total_out_group_coops += 1
                else:
                    total_defects += 1

                if a_considers_b_ingroup:
                    total_in_group_actions += 1
                else:
                    total_out_group_actions += 1

                if act_b == Action.COOPERATE:
                    total_coops += 1
                    if b_considers_a_ingroup:
                        in_group_coops[agent_b.id] += 1
                        total_in_group_coops += 1
                    else:
                        out_group_coops[agent_b.id] += 1
                        total_out_group_coops += 1
                else:
                    total_defects += 1

                if b_considers_a_ingroup:
                    total_in_group_actions += 1
                else:
                    total_out_group_actions += 1

                payoff = self._game.resolve(act_a, act_b)
                scores[agent_a.id] += payoff.first
                scores[agent_b.id] += payoff.second

                agent_a.strategy.observe(agent_b.id, act_b)
                agent_b.strategy.observe(agent_a.id, act_a)

        # Build leaderboard
        sorted_agents = sorted(
            self._agents,
            key=lambda a: (-scores[a.id], a.id),
        )
        leaderboard: list[TagLeaderboardEntry] = []
        for rank_idx, a in enumerate(sorted_agents, start=1):
            mp = matches_played[a.id]
            avg = scores[a.id] / mp if mp > 0 else 0.0
            in_m = in_group_matches[a.id]
            out_m = out_group_matches[a.id]
            in_rate = in_group_coops[a.id] / in_m if in_m > 0 else 0.0
            out_rate = out_group_coops[a.id] / out_m if out_m > 0 else 0.0

            prof = agent_profiles[a.id]
            leaderboard.append(
                TagLeaderboardEntry(
                    rank=rank_idx,
                    agent_id=a.id,
                    strategy_name=a.strategy.__class__.__name__,
                    tag=prof.tag,
                    tolerance=prof.tolerance,
                    total_score=scores[a.id],
                    matches_played=mp,
                    average_score=round(avg, 2),
                    in_group_matches=in_m,
                    out_group_matches=out_m,
                    in_group_cooperation_rate=round(in_rate, 4),
                    out_group_cooperation_rate=round(out_rate, 4),
                )
            )

        total_actions = total_coops + total_defects
        coop_rate = total_coops / total_actions if total_actions > 0 else 0.0
        in_rate_all = (
            total_in_group_coops / total_in_group_actions
            if total_in_group_actions > 0
            else 0.0
        )
        out_rate_all = (
            total_out_group_coops / total_out_group_actions
            if total_out_group_actions > 0
            else 0.0
        )

        all_tags = [agent_profiles[a.id].tag for a in self._agents]
        all_tols = [agent_profiles[a.id].tolerance for a in self._agents]
        mean_tol = sum(all_tols) / len(all_tols) if all_tols else 0.0
        diversity = calculate_shannon_diversity(all_tags)

        return TagTournamentResult(
            leaderboard=leaderboard,
            total_matches=total_matches,
            total_cooperations=total_coops,
            total_defections=total_defects,
            overall_cooperation_rate=round(coop_rate, 4),
            in_group_cooperation_rate=round(in_rate_all, 4),
            out_group_cooperation_rate=round(out_rate_all, 4),
            mean_tolerance=round(mean_tol, 4),
            tag_shannon_diversity=diversity,
        )


@dataclass(frozen=True)
class TagGenerationMetrics:
    """Statistical summary of one generation in an evolutionary tag tournament."""

    generation: int
    cooperation_rate: float
    mean_tag: float
    mean_tolerance: float
    tag_diversity: float
    top_score: int


class TagEvolutionaryTournament:
    """Simulates multi-generation evolution of tags and tolerances (Riolo et al. 2001)."""

    def __init__(
        self,
        population_size: int = 50,
        tag_mutation_rate: float = 0.1,
        tag_mutation_std: float = 0.05,
        tolerance_mutation_rate: float = 0.1,
        tolerance_mutation_std: float = 0.02,
        initial_tolerance: float = 0.05,
        torus: bool = False,
        rng: random.Random | None = None,
    ) -> None:
        if population_size < 4:
            raise ValueError("Population size must be at least 4.")

        self._pop_size = population_size
        self._tag_mut_rate = tag_mutation_rate
        self._tag_mut_std = tag_mutation_std
        self._tol_mut_rate = tolerance_mutation_rate
        self._tol_mut_std = tolerance_mutation_std
        self._torus = torus
        self._rng = rng if rng is not None else random.Random()

        # Initialize population with random tags in [0, 1] and uniform initial tolerance
        self._population: list[tuple[float, float]] = [
            (self._rng.random(), initial_tolerance) for _ in range(population_size)
        ]

    @property
    def population(self) -> list[tuple[float, float]]:
        return list(self._population)

    def step_generation(
        self,
        pairings_per_agent: int = 10,
        generation_idx: int = 1,
    ) -> TagGenerationMetrics:
        """Run one generation: pairings, payoffs, selection, and mutation."""
        agents = [
            Agent(
                f"Agent_{i:03d}",
                TagToleranceStrategy(
                    tag=tag_val,
                    tolerance=tol_val,
                    torus=self._torus,
                ),
            )
            for i, (tag_val, tol_val) in enumerate(self._population)
        ]

        tourney = TagTournament(agents=agents, torus=self._torus, rng=self._rng)
        res = tourney.run_stranger_pairings(pairings_per_agent=pairings_per_agent)

        scores = [e.total_score for e in res.leaderboard]
        min_score = min(scores) if scores else 0
        # Shift scores so fitness is non-negative
        shifted_fitness = [max(1, e.total_score - min_score + 1) for e in res.leaderboard]
        total_fitness = sum(shifted_fitness)

        # Selection (roulette proportional)
        next_gen: list[tuple[float, float]] = []
        for _ in range(self._pop_size):
            r_pick = self._rng.uniform(0, total_fitness)
            cumulative = 0
            chosen_agent_entry = res.leaderboard[0]
            for idx, entry in enumerate(res.leaderboard):
                cumulative += shifted_fitness[idx]
                if cumulative >= r_pick:
                    chosen_agent_entry = entry
                    break

            # Inherit tag and tolerance
            child_tag = float(chosen_agent_entry.tag)
            child_tol = float(chosen_agent_entry.tolerance)

            # Mutate tag
            if self._rng.random() < self._tag_mut_rate:
                noise = self._rng.gauss(0, self._tag_mut_std)
                child_tag = (child_tag + noise) % 1.0

            # Mutate tolerance
            if self._rng.random() < self._tol_mut_rate:
                tol_noise = self._rng.gauss(0, self._tol_mut_std)
                child_tol = max(0.0, child_tol + tol_noise)

            next_gen.append((round(child_tag, 4), round(child_tol, 4)))

        self._population = next_gen

        mean_tag = sum(t for t, _ in self._population) / len(self._population)
        mean_tol = sum(tol for _, tol in self._population) / len(self._population)
        diversity = calculate_shannon_diversity([t for t, _ in self._population])

        return TagGenerationMetrics(
            generation=generation_idx,
            cooperation_rate=res.overall_cooperation_rate,
            mean_tag=round(mean_tag, 4),
            mean_tolerance=round(mean_tol, 4),
            tag_diversity=diversity,
            top_score=max(scores) if scores else 0,
        )

    def run_simulation(
        self,
        generations: int = 50,
        pairings_per_agent: int = 10,
    ) -> list[TagGenerationMetrics]:
        """Run evolutionary simulation across multiple generations."""
        history: list[TagGenerationMetrics] = []
        for g in range(1, generations + 1):
            metrics = self.step_generation(
                pairings_per_agent=pairings_per_agent,
                generation_idx=g,
            )
            history.append(metrics)
        return history
