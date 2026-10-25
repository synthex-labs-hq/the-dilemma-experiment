#!/usr/bin/env python3
"""Episode 6 Interactive CLI: Indirect Reciprocity, Public Ledgers & Gossip Noise.

A live visualizer showcasing:
- Real-time Credit Score & Standing Tickers
- Public Ledger vs Private Shadow Encounters
- Second-Order Moral Judgment & Hypocrite Alerts
- Whispered Gossip Distortion
"""

import argparse
import random
import time

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.prisoners_dilemma import (
    DEFAULT_PAYOFF_MATRIX,
    PrisonersDilemma,
)
from the_dilemma_experiment.domain.reputation import (
    GossipChannel,
    MoralStanding,
    ReputationRegistry,
)
from the_dilemma_experiment.strategies.always_defect import (
    AlwaysDefectStrategy,
)
from the_dilemma_experiment.strategies.hypocrite import HypocriteStrategy
from the_dilemma_experiment.strategies.image_scorer import ImageScorerStrategy
from the_dilemma_experiment.strategies.stern_judger import SternJudgingStrategy

# ANSI Colors & Formatting
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
BG_DARK = "\033[48;5;234m"
BG_RED = "\033[48;5;52m"
BG_GREEN = "\033[48;5;22m"


def format_score_bar(score: int, min_val: int = -5, max_val: int = 5) -> str:
    """Render a visual gauge for an agent's credit/image score."""
    total_slots = 11  # from min_val to max_val
    clamped = max(min_val, min(max_val, score))
    idx = clamped - min_val

    slots = []
    for i in range(total_slots):
        val = min_val + i
        if i == idx:
            dot = f"{GOLD}{BOLD}●{RESET}"
        elif val < 0:
            dot = f"{RED}-{RESET}"
        elif val == 0:
            dot = f"{DARK_GRAY}|{RESET}"
        else:
            dot = f"{EMERALD}+{RESET}"
        slots.append(dot)

    bar = "".join(slots)
    sign = "+" if score > 0 else ""
    return f"[{bar}] {BOLD}{sign}{score:2d}{RESET}"


def format_standing_badge(standing: MoralStanding) -> str:
    """Render a colored badge for Nowak-Sigmund moral standing."""
    if standing == MoralStanding.GOOD:
        return f"{BG_GREEN}{BOLD}{EMERALD} GOOD {RESET}"
    return f"{BG_RED}{BOLD}{RED}  BAD {RESET}"


def print_header(pairings: int, public_prob: float, error_rate: float) -> None:
    """Render the stylish laboratory terminal header."""
    print(f"{CYAN}{BOLD}╔════════════════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{CYAN}{BOLD}║         THE DILEMMA EXPERIMENT — EPISODE 6: INDIRECT RECIPROCITY               ║{RESET}")
    print(f"{CYAN}{BOLD}║         Public Ledgers, Second-Order Moral Judgment & Gossip Noise             ║{RESET}")
    print(f"{CYAN}{BOLD}╚════════════════════════════════════════════════════════════════════════════════╝{RESET}")
    print(f" {DIM}Theory: Nowak & Sigmund (1998, 2005) Image Scoring & Leimar-Hammerstein Standing{RESET}")
    print(
        f" {LIGHT_GRAY}Config: {BOLD}{pairings}{RESET} Pairings/Agent | "
        f"Public Visibility: {BOLD}{int(public_prob * 100)}%{RESET} | "
        f"Gossip Distortion: {BOLD}{int(error_rate * 100)}%{RESET}\n"
    )


def print_roster_snapshot(registry: ReputationRegistry, agents: list[Agent], scores: dict[str, int]) -> None:
    """Render the current leaderboard and reputation standings."""
    print(f"{BOLD}┌─ REPUTATION LEDGER & SCOREBOARD ───────────────────────────────────────────────┐{RESET}")
    print(f"{BOLD}│ AGENT ID      STRATEGY       POINTS  IMAGE GAUGE          STANDING    STATUS  │{RESET}")
    print("├───────────────────────────────────────────────────────────────────────────────┤")

    sorted_agents = sorted(agents, key=lambda a: (-scores[a.id], a.id))
    for a in sorted_agents:
        strat = a.strategy.__class__.__name__.replace("Strategy", "")
        sc = registry.get_score(a.id)
        st = registry.get_standing(a.id)
        pts = scores[a.id]
        bar = format_score_bar(sc)
        badge = format_standing_badge(st)

        # Highlight strategy type
        if "Stern" in strat:
            strat_color = CYAN
        elif "Image" in strat:
            strat_color = BLUE
        elif "Hypo" in strat:
            strat_color = PURPLE
        else:
            strat_color = RED

        print(
            f"│ {BOLD}{a.id:<13}{RESET} {strat_color}{strat:<13}{RESET} "
            f"{GOLD}{pts:>5d}{RESET} pts  {bar}  {badge} │"
        )
    print(f"{BOLD}└───────────────────────────────────────────────────────────────────────────────┘{RESET}\n")


def run_interactive_simulation(
    pairings: int = 20,
    public_prob: float = 0.8,
    error_rate: float = 0.1,
    delay: float = 0.15,
    step_mode: bool = False,
    seed: int = 42,
) -> None:
    """Run the live interactive indirect reciprocity tournament."""
    rng = random.Random(seed)
    game = PrisonersDilemma(DEFAULT_PAYOFF_MATRIX)
    registry = ReputationRegistry(min_score=-5, max_score=5)
    gossip = GossipChannel(
        registry=registry, error_rate=error_rate, rng=random.Random(seed + 99)
    )

    agents = [
        Agent("Judger_01", SternJudgingStrategy()),
        Agent("Judger_02", SternJudgingStrategy()),
        Agent("Judger_03", SternJudgingStrategy()),
        Agent("Scorer_01", ImageScorerStrategy(threshold=0)),
        Agent("Scorer_02", ImageScorerStrategy(threshold=0)),
        Agent("Hypo_01", HypocriteStrategy()),
        Agent("Hypo_02", HypocriteStrategy()),
        Agent("Predator_01", AlwaysDefectStrategy()),
    ]

    for a in agents:
        registry.register(a.id)

    scores = {a.id: 0 for a in agents}
    total_pairings = (len(agents) * pairings) // 2

    print("\033[2J\033[H", end="")  # Clear screen
    print_header(pairings, public_prob, error_rate)
    print_roster_snapshot(registry, agents, scores)

    print(f"{BOLD}{GOLD}▶ STARTING LIVE TRANSACTION STREAM...{RESET}\n")
    if step_mode:
        input(f"{DIM}Press [ENTER] to start stepping through encounters...{RESET}")

    for match_idx in range(1, total_pairings + 1):
        # Pick two distinct strangers
        a, b = rng.sample(agents, 2)
        is_public = rng.random() < public_prob

        # Query reputation via gossip
        registry.get_score(b.id)
        b_standing_true = registry.get_standing(b.id)
        b_score_heard = gossip.query_score(b.id)
        b_standing_heard = gossip.query_standing(b.id)

        registry.get_score(a.id)
        a_standing_true = registry.get_standing(a.id)
        a_score_heard = gossip.query_score(a.id)
        a_standing_heard = gossip.query_standing(a.id)

        # Contexts
        ctx_a = DecisionContext(
            opponent_id=b.id,
            opponent_score=b_score_heard,
            opponent_standing=b_standing_heard.value,
            is_public=is_public,
        )
        ctx_b = DecisionContext(
            opponent_id=a.id,
            opponent_score=a_score_heard,
            opponent_standing=a_standing_heard.value,
            is_public=is_public,
        )

        act_a = a.strategy.choose_action(ctx_a)
        act_b = b.strategy.choose_action(ctx_b)

        payoff = game.resolve(act_a, act_b)
        scores[a.id] += payoff.first
        scores[b.id] += payoff.second

        # Record in public ledger
        registry.record_interaction(
            donor_id=a.id,
            recipient_id=b.id,
            action=act_a,
            is_public=is_public,
            round_number=match_idx,
        )
        registry.record_interaction(
            donor_id=b.id,
            recipient_id=a.id,
            action=act_b,
            is_public=is_public,
            round_number=match_idx,
        )

        # Format match log
        env_tag = (
            f"{EMERALD}[PUBLIC AUDIT]{RESET}"
            if is_public
            else f"{DARK_GRAY}[SHADOW/PRIV]{RESET}"
        )
        act_a_str = (
            f"{EMERALD}🤝 COOPERATE{RESET}"
            if act_a == Action.COOPERATE
            else f"{RED}🗡️ DEFECT   {RESET}"
        )
        act_b_str = (
            f"{EMERALD}🤝 COOPERATE{RESET}"
            if act_b == Action.COOPERATE
            else f"{RED}🗡️ DEFECT   {RESET}"
        )

        print(
            f"{DIM}#{match_idx:03d}{RESET} {env_tag} "
            f"{BOLD}{a.id:<9}{RESET} ({act_a_str}) vs {BOLD}{b.id:<9}{RESET} ({act_b_str}) "
            f"-> Payoffs: {GOLD}+{payoff.first}{RESET} / {GOLD}+{payoff.second}{RESET}"
        )

        # Special Alert: Hypocrite in the dark
        if not is_public and (
            ("Hypo" in a.id and act_a == Action.DEFECT)
            or ("Hypo" in b.id and act_b == Action.DEFECT)
        ):
            print(
                f"     {BG_RED}{BOLD} ⚠️ HYPOCRITE UNMASKED {RESET} "
                f"{PURPLE}Exploited darkness to defect while maintaining virtuous public image!{RESET}"
            )

        # Special Alert: Gossip Distortion
        if (
            b_standing_heard != b_standing_true
            or a_standing_heard != a_standing_true
        ):
            print(
                f"     {GOLD}{BOLD} 📻 GOSSIP CORRUPTION {RESET} "
                f"{ITALIC}Whispered rumors inverted an agent's true standing during matching!{RESET}"
            )

        # Refresh ledger every 5 matches or on step
        if match_idx % 5 == 0 or match_idx == total_pairings:
            print()
            print_roster_snapshot(registry, agents, scores)

        if step_mode:
            input(f"{DIM}[Press ENTER to advance]{RESET}")
        elif delay > 0:
            time.sleep(delay)

    print(f"\n{BOLD}{EMERALD}✔ SIMULATION COMPLETE.{RESET}")
    print(f"{CYAN}{BOLD}Final Verdict:{RESET}")
    print(
        f"  • {BOLD}Stern Judgers{RESET} successfully solve the Enforcer's Dilemma by distinguishing punishment from defection."
    )
    print(
        f"  • {BOLD}Hypocrites{RESET} flourish when shadows exist (is_public < 1.0), masking predation behind a cooperative public facade."
    )
    print(
        f"  • {BOLD}Predators{RESET} are swiftly ostracized once their score drops below zero in a transparent society."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Episode 6 Interactive CLI: Indirect Reciprocity & Gossip Visualizer."
    )
    parser.add_argument("--pairings", type=int, default=20, help="Pairings per agent")
    parser.add_argument(
        "--public-prob",
        type=float,
        default=0.8,
        help="Probability of public visibility [0.0 - 1.0]",
    )
    parser.add_argument(
        "--error-rate",
        type=float,
        default=0.1,
        help="Gossip transmission error rate [0.0 - 1.0]",
    )
    parser.add_argument(
        "--delay", type=float, default=0.12, help="Seconds between matches"
    )
    parser.add_argument(
        "--step", action="store_true", help="Interactive step-by-step mode"
    )
    parser.add_argument("--fast", action="store_true", help="Fast execution mode")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")

    args = parser.parse_args()
    delay = 0.0 if args.fast else args.delay

    run_interactive_simulation(
        pairings=args.pairings,
        public_prob=args.public_prob,
        error_rate=args.error_rate,
        delay=delay,
        step_mode=args.step,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
