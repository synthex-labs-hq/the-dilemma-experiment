"""Tournament engine for Common Pool Resources (CPR) and Public Goods Games with Sanctions."""

import random
from collections.abc import Sequence
from dataclasses import dataclass

from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.commons import (
    CommonPoolResource,
    PublicGoodsPool,
    SanctionEvent,
    SanctionRegistry,
    SanctionType,
)


@dataclass(frozen=True, slots=True)
class CommonsLeaderboardEntry:
    """Performance summary of an agent in a commons or public goods tournament."""

    rank: int
    agent_id: str
    strategy_name: str
    total_score: float
    average_score: float
    total_contribution: float
    average_contribution: float
    sanctions_inflicted: int
    fines_received: float
    costs_paid: float


@dataclass(frozen=True)
class CommonsTournamentResult:
    """Complete statistical summary of a commons tournament."""

    leaderboard: list[CommonsLeaderboardEntry]
    total_rounds: int
    initial_stock: float
    final_stock: float
    is_depleted: bool
    overall_contribution_rate: float
    total_sanctions: int
    total_fines_imposed: float
    total_sanction_costs: float
    history: list[dict]


class CommonsTournament:
    """Executes multi-round Common Pool Resource extraction and Public Goods Games with Sanctions."""

    def __init__(
        self,
        agents: Sequence[Agent],
        resource: CommonPoolResource | None = None,
        public_goods: PublicGoodsPool | None = None,
        sanctions_enabled: bool = True,
        graduated_sanctions: bool = False,
        sanction_cost_ratio: float = 0.33,
        rng: random.Random | None = None,
    ) -> None:
        if len(agents) < 2:
            raise ValueError(f"Commons tournament requires at least 2 agents. Got {len(agents)}.")

        self._agents = list(agents)
        self._resource = resource if resource is not None else CommonPoolResource()
        self._pgg = public_goods if public_goods is not None else PublicGoodsPool()
        self._sanctions_enabled = sanctions_enabled
        self._graduated = graduated_sanctions
        self._registry = SanctionRegistry(cost_ratio=sanction_cost_ratio)
        self._rng = rng if rng is not None else random.Random()

    @property
    def resource(self) -> CommonPoolResource:
        return self._resource

    @property
    def registry(self) -> SanctionRegistry:
        return self._registry

    def run_rounds(self, rounds: int = 15) -> CommonsTournamentResult:
        """Execute repeated rounds of resource extraction, public goods, and peer sanctions."""
        scores: dict[str, float] = {a.id: 0.0 for a in self._agents}
        total_contribs: dict[str, float] = {a.id: 0.0 for a in self._agents}
        sanctions_count: dict[str, int] = {a.id: 0 for a in self._agents}
        fines_received: dict[str, float] = {a.id: 0.0 for a in self._agents}
        costs_paid: dict[str, float] = {a.id: 0.0 for a in self._agents}

        round_history: list[dict] = []
        initial_stock = self._resource.stock

        for r_idx in range(1, rounds + 1):
            if self._resource.is_depleted:
                # Commons depleted: cannot harvest or generate public goods
                round_history.append(
                    {
                        "round": r_idx,
                        "stock": 0.0,
                        "mean_contribution": 0.0,
                        "cooperation_rate": 0.0,
                        "sanctions_applied": 0,
                    }
                )
                continue

            # 1. Harvest Phase from Common Pool Resource
            round_harvests: dict[str, float] = {}
            for a in self._agents:
                strat = a.strategy
                if hasattr(strat, "decide_harvest"):
                    req = strat.decide_harvest(
                        stock=self._resource.stock,
                        capacity=self._resource.capacity,
                        group_size=len(self._agents),
                    )
                else:
                    req = 2.0
                actual = self._resource.harvest(req)
                round_harvests[a.id] = actual
                scores[a.id] += actual

            # Natural replenishment
            self._resource.regenerate()

            # 2. Public Goods Contribution Phase
            contributions: dict[str, float] = {}
            for a in self._agents:
                strat = a.strategy
                if hasattr(strat, "decide_contribution"):
                    c = strat.decide_contribution(endowment=self._pgg.endowment)
                else:
                    c = self._pgg.endowment
                contributions[a.id] = c
                total_contribs[a.id] += c

            pgg_payoffs = self._pgg.resolve(contributions)
            for aid, pay in pgg_payoffs.items():
                scores[aid] += pay

            # 3. Sanction Phase (Fehr-Gächter peer punishment / Ostrom graduated enforcement)
            round_sanction_events: list[SanctionEvent] = []
            if self._sanctions_enabled:
                for punisher in self._agents:
                    strat = punisher.strategy
                    if hasattr(strat, "should_sanction"):
                        fine_val = getattr(strat, "fine_amount", 3.0)
                        for target in self._agents:
                            if target.id == punisher.id:
                                continue
                            if strat.should_sanction(
                                target_id=target.id,
                                target_contribution=contributions[target.id],
                            ):
                                stype = (
                                    SanctionType.GRADUATED
                                    if self._graduated
                                    else SanctionType.PEER
                                )
                                # Graduated sanctions escalate with prior violations
                                if self._graduated:
                                    infractions = self._registry.record_infraction(target.id)
                                    fine_val = fine_val * (1.0 + 0.5 * (infractions - 1))

                                ev = self._registry.apply_sanction(
                                    punisher_id=punisher.id,
                                    target_id=target.id,
                                    fine_amount=fine_val,
                                    round_number=r_idx,
                                    sanction_type=stype,
                                )
                                round_sanction_events.append(ev)
                                sanctions_count[punisher.id] += 1
                                costs_paid[punisher.id] += ev.cost
                                fines_received[target.id] += ev.fine

                # Apply round deductions to scores
                agent_ids = [a.id for a in self._agents]
                penalties = self._registry.compute_round_penalties(
                    agent_ids=agent_ids, round_number=r_idx
                )
                for aid, delta in penalties.items():
                    scores[aid] += delta

            # Log round summary
            mean_c = sum(contributions.values()) / len(contributions)
            round_history.append(
                {
                    "round": r_idx,
                    "stock": round(self._resource.stock, 2),
                    "mean_contribution": round(mean_c, 2),
                    "cooperation_rate": round(mean_c / self._pgg.endowment, 4),
                    "sanctions_applied": len(round_sanction_events),
                }
            )

        # Build Leaderboard
        sorted_agents = sorted(
            self._agents,
            key=lambda a: (-scores[a.id], a.id),
        )
        leaderboard: list[CommonsLeaderboardEntry] = []
        for rank_idx, a in enumerate(sorted_agents, start=1):
            tot = scores[a.id]
            avg = tot / rounds if rounds > 0 else 0.0
            tot_c = total_contribs[a.id]
            avg_c = tot_c / rounds if rounds > 0 else 0.0
            leaderboard.append(
                CommonsLeaderboardEntry(
                    rank=rank_idx,
                    agent_id=a.id,
                    strategy_name=a.strategy.__class__.__name__,
                    total_score=round(tot, 2),
                    average_score=round(avg, 2),
                    total_contribution=round(tot_c, 2),
                    average_contribution=round(avg_c, 2),
                    sanctions_inflicted=sanctions_count[a.id],
                    fines_received=round(fines_received[a.id], 2),
                    costs_paid=round(costs_paid[a.id], 2),
                )
            )

        total_possible_contribs = len(self._agents) * rounds * self._pgg.endowment
        actual_contribs = sum(total_contribs.values())
        overall_coop = (
            actual_contribs / total_possible_contribs
            if total_possible_contribs > 0
            else 0.0
        )

        total_sanctions = len(self._registry.history)
        total_fines = sum(ev.fine for ev in self._registry.history)
        total_costs = sum(ev.cost for ev in self._registry.history)

        return CommonsTournamentResult(
            leaderboard=leaderboard,
            total_rounds=rounds,
            initial_stock=initial_stock,
            final_stock=round(self._resource.stock, 2),
            is_depleted=self._resource.is_depleted,
            overall_contribution_rate=round(overall_coop, 4),
            total_sanctions=total_sanctions,
            total_fines_imposed=round(total_fines, 2),
            total_sanction_costs=round(total_costs, 2),
            history=round_history,
        )
