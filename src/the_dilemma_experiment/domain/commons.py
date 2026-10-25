"""Domain models for Common Pool Resources (CPR), Public Goods Games (PGG), and Sanctions."""

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum


class SanctionType(str, Enum):
    """Classification of institutional or peer punishment mechanisms."""

    PEER = "PEER"
    GRADUATED = "GRADUATED"
    INSTITUTIONAL = "INSTITUTIONAL"


@dataclass
class CommonPoolResource:
    """A depletable shared resource pool with dynamic carrying capacity and replenishment."""

    capacity: float = 100.0
    stock: float = 100.0
    regeneration_rate: float = 0.20

    def __post_init__(self) -> None:
        if self.capacity <= 0:
            raise ValueError(f"capacity must be positive. Got {self.capacity}.")
        if self.regeneration_rate < 0:
            raise ValueError(f"regeneration_rate cannot be negative. Got {self.regeneration_rate}.")
        self.stock = max(0.0, min(self.capacity, self.stock))

    def harvest(self, requested_amount: float) -> float:
        """Extract requested amount from stock; clamped to remaining stock."""
        if requested_amount < 0:
            raise ValueError("Harvest amount cannot be negative.")
        actual = min(self.stock, requested_amount)
        self.stock = max(0.0, self.stock - actual)
        return round(actual, 4)

    def regenerate(self) -> float:
        """Regenerate stock: S_next = min(capacity, S * (1 + rho))."""
        if self.stock > 0:
            new_stock = min(self.capacity, self.stock * (1.0 + self.regeneration_rate))
            self.stock = round(new_stock, 4)
        return self.stock

    @property
    def is_depleted(self) -> bool:
        """Return True if common pool has been exhausted."""
        return self.stock <= 0.001

    @property
    def fullness_percentage(self) -> float:
        """Return stock as a percentage of carrying capacity."""
        return round((self.stock / self.capacity) * 100.0, 2)


@dataclass(frozen=True, slots=True)
class PublicGoodsPool:
    """Standard N-player linear Public Goods Game engine."""

    endowment: float = 10.0
    multiplier: float = 1.6

    def __post_init__(self) -> None:
        if self.endowment <= 0:
            raise ValueError(f"Endowment must be positive. Got {self.endowment}.")
        if self.multiplier <= 1.0:
            raise ValueError(f"Multiplier must be strictly greater than 1.0. Got {self.multiplier}.")

    def resolve(self, contributions: dict[str, float]) -> dict[str, float]:
        """Compute net payoffs: pi_i = endowment - c_i + (multiplier / N) * sum(c)."""
        n = len(contributions)
        if n < 2:
            raise ValueError("Public Goods Game requires at least 2 players.")

        # Clamp contributions between 0 and endowment
        clamped = {
            pid: max(0.0, min(self.endowment, amt))
            for pid, amt in contributions.items()
        }
        total_pot = sum(clamped.values())
        multiplied_pot = total_pot * self.multiplier
        share_per_player = multiplied_pot / n

        payoffs: dict[str, float] = {}
        for pid, c in clamped.items():
            net = (self.endowment - c) + share_per_player
            payoffs[pid] = round(net, 4)

        return payoffs


@dataclass(frozen=True, slots=True)
class SanctionEvent:
    """Historical audit record of a punitive fine."""

    punisher_id: str
    target_id: str
    cost: float
    fine: float
    round_number: int
    sanction_type: SanctionType = SanctionType.PEER


class SanctionRegistry:
    """Manages costly peer-to-peer and graduated sanctions (Fehr & Gächter 2000; Ostrom 1990)."""

    def __init__(self, cost_ratio: float = 0.33) -> None:
        """Initialize registry. cost_ratio is cost per unit fine (e.g. 1 point cost to dock 3 points fine)."""
        if cost_ratio <= 0:
            raise ValueError("cost_ratio must be positive.")
        self._cost_ratio = cost_ratio
        self._history: list[SanctionEvent] = []
        self._infraction_counts: dict[str, int] = {}

    @property
    def history(self) -> list[SanctionEvent]:
        return list(self._history)

    def record_infraction(self, agent_id: str) -> int:
        """Increment and return prior infraction count for graduated sanctions."""
        self._infraction_counts[agent_id] = self._infraction_counts.get(agent_id, 0) + 1
        return self._infraction_counts[agent_id]

    def apply_sanction(
        self,
        punisher_id: str,
        target_id: str,
        fine_amount: float = 3.0,
        round_number: int = 0,
        sanction_type: SanctionType = SanctionType.PEER,
    ) -> SanctionEvent:
        """Apply a sanction: punisher pays fine_amount * cost_ratio, target loses fine_amount."""
        cost = round(fine_amount * self._cost_ratio, 4)
        event = SanctionEvent(
            punisher_id=punisher_id,
            target_id=target_id,
            cost=cost,
            fine=fine_amount,
            round_number=round_number,
            sanction_type=sanction_type,
        )
        self._history.append(event)
        return event

    def compute_round_penalties(self, agent_ids: Sequence[str], round_number: int) -> dict[str, float]:
        """Return net score deductions (negative values) for punisher costs and target fines in a given round."""
        penalties: dict[str, float] = {aid: 0.0 for aid in agent_ids}
        for ev in self._history:
            if ev.round_number == round_number:
                if ev.punisher_id in penalties:
                    penalties[ev.punisher_id] -= ev.cost
                if ev.target_id in penalties:
                    penalties[ev.target_id] -= ev.fine
        return {aid: round(val, 4) for aid, val in penalties.items()}

    def reset(self) -> None:
        """Clear all historical sanctions and infraction logs."""
        self._history.clear()
        self._infraction_counts.clear()
