#!/usr/bin/env python3
"""Episode 8 Interactive CLI: The Tragedy of the Commons & Ostrom Sanctions.

A live visualizer showcasing:
- Real-time Common Pool Resource Gauge (Dynamic replenishment & depletion)
- Public Goods Game contribution pot and multiplier distribution
- Costly Peer Punishment & Second-Order Free-Riding
- Catastrophic Commons Collapse vs Ostrom Sustainable Governance
"""

import argparse
import sys
import time
from pathlib import Path

# Ensure src is in sys.path for direct script execution
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.commons import (
    CommonPoolResource,
    PublicGoodsPool,
    SanctionRegistry,
)
from the_dilemma_experiment.strategies.commons_strategies import (
    OstromSanctionerStrategy,
    OverHarvesterStrategy,
    SecondOrderFreeRiderStrategy,
    SustainableHarvesterStrategy,
)

# ANSI Styling
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"

# Palette
CYAN = "\033[38;5;51m"
BLUE = "\033[38;5;39m"
EMERALD = "\033[38;5;48m"
RED = "\033[38;5;196m"
GOLD = "\033[38;5;220m"
PURPLE = "\033[38;5;141m"
DARK_GRAY = "\033[38;5;238m"
LIGHT_GRAY = "\033[38;5;250m"

BG_RED = "\033[48;5;52m"
BG_GREEN = "\033[48;5;22m"
BG_GOLD = "\033[48;5;58m"


def format_reservoir_gauge(stock: float, capacity: float, bar_width: int = 30) -> str:
    """Render a dynamic colored progress bar for common pool resource stock."""
    pct = max(0.0, min(100.0, (stock / capacity) * 100.0))
    filled_len = int(bar_width * (pct / 100.0))
    empty_len = bar_width - filled_len

    if pct >= 60.0:
        bar_color = EMERALD
    elif pct >= 25.0:
        bar_color = GOLD
    else:
        bar_color = RED

    filled_chars = "█" * filled_len
    empty_chars = "░" * empty_len
    bar = f"[{bar_color}{filled_chars}{DARK_GRAY}{empty_chars}{RESET}]"

    status_tag = ""
    if pct <= 0.001:
        status_tag = f" {BG_RED}{BOLD} COLLAPSED {RESET}"
    elif pct < 25.0:
        status_tag = f" {RED}{BOLD}CRITICAL{RESET}"
    elif pct >= 75.0:
        status_tag = f" {EMERALD}{BOLD}OPTIMAL{RESET}"

    return f"{bar} {bar_color}{BOLD}{pct:5.1f}%{RESET} ({stock:5.1f}/{capacity:5.1f}){status_tag}"


def print_header(rounds: int, sanctions_active: bool) -> None:
    """Render the stylish laboratory terminal header."""
    print(f"{CYAN}{BOLD}╔════════════════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{CYAN}{BOLD}║         THE DILEMMA EXPERIMENT — EPISODE 8: TRAGEDY OF THE COMMONS             ║{RESET}")
    print(f"{CYAN}{BOLD}║         Resource Exhaustion, Public Goods & Ostrom Polycentric Sanctions       ║{RESET}")
    print(f"{CYAN}{BOLD}╚════════════════════════════════════════════════════════════════════════════════╝{RESET}")
    print(f" {DIM}Theory: Garrett Hardin (1968), Elinor Ostrom (1990) & Fehr-Gächter (Nature 2000){RESET}")
    s_status = f"{EMERALD}{BOLD}ENABLED{RESET}" if sanctions_active else f"{RED}{BOLD}DISABLED (ANARCHY){RESET}"
    print(f" {LIGHT_GRAY}Config: {BOLD}{rounds}{RESET} Rounds | Sanction Regime: {s_status}\n")


def print_scoreboard(
    agents: list[Agent],
    scores: dict[str, float],
    total_contribs: dict[str, float],
    sanctions_count: dict[str, int],
    fines_received: dict[str, float],
    costs_paid: dict[str, float],
) -> None:
    """Render the current leaderboard and enforcement metrics."""
    print(f"{BOLD}┌─ COMMONS SCOREBOARD & ENFORCEMENT AUDIT ───────────────────────────────────────┐{RESET}")
    print(f"{BOLD}│ AGENT ID       ROLE/STRATEGY   POINTS   CONTRIBS   FINES REC'D  COSTS PAID     │{RESET}")
    print("├───────────────────────────────────────────────────────────────────────────────┤")

    sorted_agents = sorted(agents, key=lambda a: (-scores[a.id], a.id))
    for a in sorted_agents:
        strat = a.strategy
        sname = strat.__class__.__name__.replace("Strategy", "")
        pts = scores[a.id]
        c = total_contribs[a.id]
        f_rec = fines_received[a.id]
        c_pd = costs_paid[a.id]

        if "Ostrom" in sname:
            role_badge = f"{EMERALD}ENFORCER  {RESET}"
        elif "Second" in sname:
            role_badge = f"{GOLD}BYSTANDER {RESET}"
        elif "Over" in sname:
            role_badge = f"{RED}FREE-RIDER{RESET}"
        else:
            role_badge = f"{CYAN}SUSTAINER {RESET}"

        print(
            f"│ {BOLD}{a.id:<14}{RESET} {role_badge} "
            f"{GOLD}{pts:>7.2f}{RESET}  "
            f"{EMERALD}{c:>7.1f}{RESET}    "
            f"{RED}{f_rec:>7.1f}{RESET}      "
            f"{PURPLE}{c_pd:>6.2f}{RESET}       │"
        )
    print(f"{BOLD}└───────────────────────────────────────────────────────────────────────────────┘{RESET}\n")


def run_interactive_simulation(
    rounds: int = 12,
    sanctions_enabled: bool = True,
    capacity: float = 120.0,
    regeneration_rate: float = 0.20,
    delay: float = 0.15,
    step_mode: bool = False,
    seed: int = 42,
) -> None:
    """Run the live interactive Commons & Sanctions simulation."""
    cpr = CommonPoolResource(
        capacity=capacity,
        stock=capacity,
        regeneration_rate=regeneration_rate,
    )
    pgg = PublicGoodsPool(endowment=10.0, multiplier=1.6)
    registry = SanctionRegistry(cost_ratio=0.33)

    agents: list[Agent] = [
        Agent("Ostrom_01", OstromSanctionerStrategy(harvest_quota=2.0, fine_amount=4.0)),
        Agent("Ostrom_02", OstromSanctionerStrategy(harvest_quota=2.0, fine_amount=4.0)),
        Agent("Bystander_01", SecondOrderFreeRiderStrategy(harvest_quota=2.0)),
        Agent("Bystander_02", SecondOrderFreeRiderStrategy(harvest_quota=2.0)),
        Agent("Sustain_01", SustainableHarvesterStrategy(harvest_quota=2.0)),
        Agent("Greedy_01", OverHarvesterStrategy(max_extract=8.0)),
        Agent("Greedy_02", OverHarvesterStrategy(max_extract=8.0)),
    ]

    scores = {a.id: 0.0 for a in agents}
    total_contribs = {a.id: 0.0 for a in agents}
    sanctions_count = {a.id: 0 for a in agents}
    fines_received = {a.id: 0.0 for a in agents}
    costs_paid = {a.id: 0.0 for a in agents}

    print("\033[2J\033[H", end="")  # Clear screen
    print_header(rounds, sanctions_enabled)

    print(f"{BOLD}RESERVOIR STATUS:{RESET} {format_reservoir_gauge(cpr.stock, cpr.capacity)}")
    print_scoreboard(
        agents,
        scores,
        total_contribs,
        sanctions_count,
        fines_received,
        costs_paid,
    )

    print(f"{BOLD}{GOLD}▶ COMMENCING COMMONS EXTRACTION & SANCTION STREAM...{RESET}\n")
    if step_mode:
        input(f"{DIM}Press [ENTER] to begin round 1...{RESET}")

    for r_idx in range(1, rounds + 1):
        print(f"{BOLD}{CYAN}═══ ROUND {r_idx:02d} / {rounds:02d} ═════════════════════════════════════════════════════════{RESET}")

        if cpr.is_depleted:
            print(f"{BG_RED}{BOLD} 🚨 COMMONS TRAGEDY: Resource pool is completely dry (0.0)! {RESET}")
            print(f"{RED}No agent can harvest. System collapse has occurred.{RESET}\n")
            if step_mode:
                input(f"{DIM}[Press ENTER to advance]{RESET}")
            continue

        # 1. Extraction Phase
        round_harvests: dict[str, float] = {}
        for a in agents:
            strat = a.strategy
            req = strat.decide_harvest(
                stock=cpr.stock,
                capacity=cpr.capacity,
                group_size=len(agents),
            )
            actual = cpr.harvest(req)
            round_harvests[a.id] = actual
            scores[a.id] += actual

        cpr.regenerate()
        print(f"  {BOLD}Reservoir After Harvest & Regen:{RESET} {format_reservoir_gauge(cpr.stock, cpr.capacity)}")

        # 2. Public Goods Phase
        contributions: dict[str, float] = {}
        for a in agents:
            c = a.strategy.decide_contribution(endowment=pgg.endowment)
            contributions[a.id] = c
            total_contribs[a.id] += c

        payoffs = pgg.resolve(contributions)
        for aid, pay in payoffs.items():
            scores[aid] += pay

        total_pot = sum(contributions.values())
        print(
            f"  {LIGHT_GRAY}Public Goods Pool:{RESET} Contributed: {GOLD}{total_pot:.1f}{RESET} -> "
            f"Multiplied: {EMERALD}{total_pot * pgg.multiplier:.1f}{RESET} "
            f"({LIGHT_GRAY}Share: +{payoffs[agents[0].id]:.2f} pts each{RESET})"
        )

        # 3. Sanction Phase
        sanction_events = []
        if sanctions_enabled:
            for punisher in agents:
                strat = punisher.strategy
                if hasattr(strat, "should_sanction"):
                    for target in agents:
                        if target.id == punisher.id:
                            continue
                        if strat.should_sanction(
                            target_id=target.id,
                            target_contribution=contributions[target.id],
                        ):
                            ev = registry.apply_sanction(
                                punisher_id=punisher.id,
                                target_id=target.id,
                                fine_amount=strat.fine_amount,
                                round_number=r_idx,
                            )
                            sanction_events.append(ev)
                            sanctions_count[punisher.id] += 1
                            costs_paid[punisher.id] += ev.cost
                            fines_received[target.id] += ev.fine

            # Deduct penalties
            agent_ids = [a.id for a in agents]
            penalties = registry.compute_round_penalties(agent_ids, r_idx)
            for aid, delta in penalties.items():
                scores[aid] += delta

            for ev in sanction_events:
                print(
                    f"     {PURPLE}{BOLD}🔨 COSTLY SANCTION:{RESET} "
                    f"{BOLD}{ev.punisher_id}{RESET} fined {RED}{ev.target_id}{RESET} "
                    f"-{ev.fine:.1f} pts ({DIM}Punisher paid cost -{ev.cost:.2f}{RESET})"
                )

        print()
        if r_idx % 3 == 0 or r_idx == rounds:
            print_scoreboard(
                agents,
                scores,
                total_contribs,
                sanctions_count,
                fines_received,
                costs_paid,
            )

        if step_mode:
            input(f"{DIM}[Press ENTER to advance]{RESET}")
        elif delay > 0:
            time.sleep(delay)

    print(f"\n{BOLD}{EMERALD}✔ SIMULATION COMPLETE.{RESET}")
    print(f"{CYAN}{BOLD}Scientific Takeaways:{RESET}")
    print(
        f"  • {BOLD}The Unregulated Tragedy{RESET}: Without monitoring or sanctions, rational free-riding empties the commons."
    )
    print(
        f"  • {BOLD}The Second-Order Free-Rider Dilemma{RESET}: Silent bystanders outscore altruistic punishers because punishers pay enforcement costs."
    )
    print(
        f"  • {BOLD}Ostrom's Triumph{RESET}: Fines and monitoring protect the reservoir, proving self-governing institutions can prevent collapse."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Episode 8 Interactive CLI: The Tragedy of the Commons & Sanctions."
    )
    parser.add_argument("--rounds", type=int, default=12, help="Number of rounds")
    parser.add_argument(
        "--no-sanctions", action="store_true", help="Disable peer sanctions"
    )
    parser.add_argument(
        "--capacity",
        type=float,
        default=120.0,
        help="Carrying capacity of common pool",
    )
    parser.add_argument(
        "--delay", type=float, default=0.12, help="Seconds between rounds"
    )
    parser.add_argument(
        "--step", action="store_true", help="Interactive step-by-step mode"
    )
    parser.add_argument("--fast", action="store_true", help="Fast execution mode")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")

    args = parser.parse_args()
    delay = 0.0 if args.fast else args.delay

    run_interactive_simulation(
        rounds=args.rounds,
        sanctions_enabled=not args.no_sanctions,
        capacity=args.capacity,
        delay=delay,
        step_mode=args.step,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
