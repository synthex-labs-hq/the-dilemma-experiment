"""Reputation registry, moral standings, and gossip channel domain models."""

import random
from dataclasses import dataclass, field
from enum import Enum

from the_dilemma_experiment.domain.action import Action


class MoralStanding(str, Enum):
    """Discrete second-order moral classification (Nowak & Sigmund 2005)."""

    GOOD = "GOOD"
    BAD = "BAD"


@dataclass(frozen=True, slots=True)
class ReputationEvent:
    """Historical audit record of an observed interaction."""

    donor_id: str
    recipient_id: str
    action: Action
    recipient_standing_at_interaction: MoralStanding
    is_public: bool
    round_number: int


class ReputationRegistry:
    """Centralized public ledger of agent image scores and moral standings."""

    def __init__(self, min_score: int = -5, max_score: int = 5) -> None:
        if min_score >= max_score:
            raise ValueError(
                f"min_score ({min_score}) must be strictly less than max_score ({max_score})."
            )

        self._min_score = min_score
        self._max_score = max_score
        self._scores: dict[str, int] = {}
        self._standings: dict[str, MoralStanding] = {}
        self._history: list[ReputationEvent] = []

    @property
    def min_score(self) -> int:
        return self._min_score

    @property
    def max_score(self) -> int:
        return self._max_score

    @property
    def scores(self) -> dict[str, int]:
        return dict(self._scores)

    @property
    def standings(self) -> dict[str, MoralStanding]:
        return dict(self._standings)

    @property
    def history(self) -> list[ReputationEvent]:
        return list(self._history)

    def register(
        self,
        agent_id: str,
        initial_score: int = 0,
        initial_standing: MoralStanding = MoralStanding.GOOD,
    ) -> None:
        """Register an agent in the public ledger."""
        clamped_score = max(self._min_score, min(self._max_score, initial_score))
        self._scores[agent_id] = clamped_score
        self._standings[agent_id] = initial_standing

    def get_score(self, agent_id: str) -> int:
        """Return the current first-order image score of an agent (defaults to 0 if unregistered)."""
        return self._scores.get(agent_id, 0)

    def get_standing(self, agent_id: str) -> MoralStanding:
        """Return the current second-order moral standing of an agent (defaults to GOOD)."""
        return self._standings.get(agent_id, MoralStanding.GOOD)

    def record_interaction(
        self,
        donor_id: str,
        recipient_id: str,
        action: Action,
        is_public: bool = True,
        round_number: int = 0,
    ) -> None:
        """Record an interaction and update public image score and standing."""
        recipient_standing = self.get_standing(recipient_id)

        # Audit event is always logged
        event = ReputationEvent(
            donor_id=donor_id,
            recipient_id=recipient_id,
            action=action,
            recipient_standing_at_interaction=recipient_standing,
            is_public=is_public,
            round_number=round_number,
        )
        self._history.append(event)

        # If private, public reputation scores and standings do NOT update
        if not is_public:
            return

        # 1. First-Order Image Scoring update (ADR-021)
        current_score = self.get_score(donor_id)
        delta = 1 if action == Action.COOPERATE else -1
        new_score = max(self._min_score, min(self._max_score, current_score + delta))
        self._scores[donor_id] = new_score

        # 2. Second-Order Stern-Judging moral standing update (ADR-022)
        # - Cooperating with GOOD -> GOOD
        # - Defecting against GOOD -> BAD (unprovoked harm)
        # - Cooperating with BAD -> BAD (appeasement of free-rider)
        # - Defecting against BAD -> GOOD (righteous punishment)
        if recipient_standing == MoralStanding.GOOD:
            new_standing = (
                MoralStanding.GOOD if action == Action.COOPERATE else MoralStanding.BAD
            )
        else:  # recipient is BAD
            new_standing = (
                MoralStanding.BAD if action == Action.COOPERATE else MoralStanding.GOOD
            )

        self._standings[donor_id] = new_standing

    def reset(self) -> None:
        """Clear all registered scores, standings, and historical events."""
        self._scores.clear()
        self._standings.clear()
        self._history.clear()


@dataclass(frozen=True)
class GossipChannel:
    """Decentralized or noisy peer-to-peer reputation transmission channel."""

    registry: ReputationRegistry
    error_rate: float = 0.0
    rng: random.Random = field(default_factory=random.Random)

    def __post_init__(self) -> None:
        if not (0.0 <= self.error_rate <= 1.0):
            raise ValueError(
                f"Gossip channel error_rate must be in [0.0, 1.0]. Got {self.error_rate}."
            )

    def query_standing(self, agent_id: str) -> MoralStanding:
        """Query agent standing with observation transmission error rate gamma."""
        true_standing = self.registry.get_standing(agent_id)
        if self.error_rate > 0.0 and self.rng.random() < self.error_rate:
            # Noise inverts reported standing
            return (
                MoralStanding.BAD
                if true_standing == MoralStanding.GOOD
                else MoralStanding.GOOD
            )
        return true_standing

    def query_score(self, agent_id: str) -> int:
        """Query agent score with observation transmission noise."""
        true_score = self.registry.get_score(agent_id)
        if self.error_rate > 0.0 and self.rng.random() < self.error_rate:
            distortion = self.rng.choice([-1, 1])
            noisy_score = true_score + distortion
            return max(
                self.registry.min_score, min(self.registry.max_score, noisy_score)
            )
        return true_score
