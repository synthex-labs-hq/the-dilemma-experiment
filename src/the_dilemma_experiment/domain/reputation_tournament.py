"""Reputation tournament engine for indirect reciprocity and stranger matches."""

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
from the_dilemma_experiment.domain.reputation import (
    GossipChannel,
    MoralStanding,
    ReputationRegistry,
)


@dataclass(frozen=True, slots=True)
class ReputationLeaderboardEntry:
    """Performance summary of an agent in a reputation tournament."""

    rank: int
    agent_id: str
    strategy_name: str
    total_score: int
    match_count: int
    average_score: float
    final_image_score: int
    final_standing: MoralStanding


@dataclass(frozen=True)
class ReputationTournamentResult:
    """Complete summary of a reputation tournament."""

    leaderboard: list[ReputationLeaderboardEntry]
    total_matches: int
    public_matches: int
    private_matches: int
    total_cooperations: int
    total_defections: int
    cooperation_rate: float
    registry: ReputationRegistry


class ReputationTournament:
    """Executes repeated stranger matches governed by public reputation and gossip."""

    def __init__(
        self,
        agents: Sequence[Agent],
        registry: ReputationRegistry | None = None,
        gossip_channel: GossipChannel | None = None,
        game: Game | None = None,
        public_probability: float = 1.0,
        rng: random.Random | None = None,
    ) -> None:
        if len(agents) < 2:
            raise ValueError(f"Reputation tournament requires at least 2 agents. Got {len(agents)}.")
        if not (0.0 <= public_probability <= 1.0):
            raise ValueError(
                f"public_probability must be in [0.0, 1.0]. Got {public_probability}."
            )

        self._agents = list(agents)
        self._registry = registry if registry is not None else ReputationRegistry()
        self._gossip = gossip_channel
        self._game: Game = game if game is not None else PrisonersDilemma(DEFAULT_PAYOFF_MATRIX)
        self._public_probability = public_probability
        self._rng = rng if rng is not None else random.Random()

        # Register all agents in the public ledger
        for agent in self._agents:
            self._registry.register(agent.id)

    @property
    def registry(self) -> ReputationRegistry:
        return self._registry

    def run_stranger_rounds(
        self,
        pairings_per_agent: int = 10,
        rounds_per_match: int = 1,
    ) -> ReputationTournamentResult:
        """Run random pairings between strangers, updating reputation after each interaction."""
        scores: dict[str, int] = {a.id: 0 for a in self._agents}
        matches_played: dict[str, int] = {a.id: 0 for a in self._agents}

        total_matches = 0
        public_matches = 0
        total_coop = 0
        total_defect = 0

        total_pairings = (len(self._agents) * pairings_per_agent) // 2
        for match_idx in range(total_pairings):
            # Select two distinct random strangers
            a_idx, b_idx = self._rng.sample(range(len(self._agents)), 2)
            agent_a = self._agents[a_idx]
            agent_b = self._agents[b_idx]

            is_public = self._rng.random() < self._public_probability
            total_matches += 1
            if is_public:
                public_matches += 1

            for r in range(rounds_per_match):
                # Query opponent reputation (via noisy gossip channel if provided, else ledger)
                if self._gossip is not None:
                    b_score = self._gossip.query_score(agent_b.id)
                    b_standing = self._gossip.query_standing(agent_b.id).value
                    a_score = self._gossip.query_score(agent_a.id)
                    a_standing = self._gossip.query_standing(agent_a.id).value
                else:
                    b_score = self._registry.get_score(agent_b.id)
                    b_standing = self._registry.get_standing(agent_b.id).value
                    a_score = self._registry.get_score(agent_a.id)
                    a_standing = self._registry.get_standing(agent_a.id).value

                # Contexts provided to each agent
                ctx_a = DecisionContext(
                    opponent_id=agent_b.id,
                    opponent_score=b_score,
                    opponent_standing=b_standing,
                    is_public=is_public,
                )
                ctx_b = DecisionContext(
                    opponent_id=agent_a.id,
                    opponent_score=a_score,
                    opponent_standing=a_standing,
                    is_public=is_public,
                )

                act_a = agent_a.strategy.choose_action(ctx_a)
                act_b = agent_b.strategy.choose_action(ctx_b)

                total_coop += (1 if act_a == Action.COOPERATE else 0) + (
                    1 if act_b == Action.COOPERATE else 0
                )
                total_defect += (1 if act_a == Action.DEFECT else 0) + (
                    1 if act_b == Action.DEFECT else 0
                )

                payoff = self._game.resolve(act_a, act_b)
                scores[agent_a.id] += payoff.first
                scores[agent_b.id] += payoff.second

                agent_a.strategy.observe(agent_b.id, act_b)
                agent_b.strategy.observe(agent_a.id, act_a)

                # Record in public ledger
                self._registry.record_interaction(
                    donor_id=agent_a.id,
                    recipient_id=agent_b.id,
                    action=act_a,
                    is_public=is_public,
                    round_number=r,
                )
                self._registry.record_interaction(
                    donor_id=agent_b.id,
                    recipient_id=agent_a.id,
                    action=act_b,
                    is_public=is_public,
                    round_number=r,
                )

            matches_played[agent_a.id] += 1
            matches_played[agent_b.id] += 1

        # Build leaderboard
        sorted_agents = sorted(
            self._agents,
            key=lambda a: (-scores[a.id], a.id),
        )
        leaderboard: list[ReputationLeaderboardEntry] = []
        for rank_idx, a in enumerate(sorted_agents, start=1):
            mp = matches_played[a.id]
            avg = scores[a.id] / mp if mp > 0 else 0.0
            leaderboard.append(
                ReputationLeaderboardEntry(
                    rank=rank_idx,
                    agent_id=a.id,
                    strategy_name=a.strategy.__class__.__name__,
                    total_score=scores[a.id],
                    match_count=mp,
                    average_score=round(avg, 2),
                    final_image_score=self._registry.get_score(a.id),
                    final_standing=self._registry.get_standing(a.id),
                )
            )

        total_actions = total_coop + total_defect
        coop_rate = total_coop / total_actions if total_actions > 0 else 0.0

        return ReputationTournamentResult(
            leaderboard=leaderboard,
            total_matches=total_matches,
            public_matches=public_matches,
            private_matches=total_matches - public_matches,
            total_cooperations=total_coop,
            total_defections=total_defect,
            cooperation_rate=round(coop_rate, 4),
            registry=self._registry,
        )
