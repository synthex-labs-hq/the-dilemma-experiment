#!/usr/bin/env python3
"""Episode 7 Interactive CLI: Tags, Tribalism & In-Group Favoritism.

A live visualizer showcasing:
- Categorical Tribes (Red, Blue, Green, Gold)
- In-Group Altruism vs Out-Group Parochial Enmity
- False-Beard Green-Beard Invasions
- Shannon Diversity Index and Tribal Scoreboards
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
from the_dilemma_experiment.domain.tag import (
    calculate_shannon_diversity,
    compute_tag_distance,
)
from the_dilemma_experiment.strategies.tag_based import (
    FalseBeardStrategy,
    StrictTribalStrategy,
)

# ANSI Styling
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"

# Tribal Colors
COLOR_RED = "\033[38;5;196m"
COLOR_BLUE = "\033[38;5;39m"
COLOR_GREEN = "\033[38;5;48m"
COLOR_GOLD = "\033[38;5;220m"
COLOR_PURPLE = "\033[38;5;141m"
DARK_GRAY = "\033[38;5;238m"
LIGHT_GRAY = "\033[38;5;250m"

BG_RED = "\033[48;5;52m"
BG_GREEN = "\033[48;5;22m"
BG_BLUE = "\033[48;5;17m"
BG_GOLD = "\033[48;5;58m"


def format_tribal_badge(tag: str, is_false_beard: bool = False) -> str:
    """Render a colored badge for an agent's tribal tag."""
    t_upper = str(tag).upper()
    if is_false_beard:
        return f"{COLOR_PURPLE}{BOLD}🟣 [GREEN*]{RESET}"
    if "RED" in t_upper:
        return f"{COLOR_RED}{BOLD}🔴 [RED]   {RESET}"
    if "BLUE" in t_upper:
        return f"{COLOR_BLUE}{BOLD}🔵 [BLUE]  {RESET}"
    if "GREEN" in t_upper:
        return f"{COLOR_GREEN}{BOLD}🟢 [GREEN] {RESET}"
    if "GOLD" in t_upper:
        return f"{COLOR_GOLD}{BOLD}🟡 [GOLD]  {RESET}"
    return f"{LIGHT_GRAY}{BOLD}⚪ [{tag:<6}]{RESET}"


def print_header(pairings: int, false_beard_active: bool) -> None:
    """Render the stylish laboratory terminal header."""
    print(f"{COLOR_BLUE}{BOLD}╔════════════════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{COLOR_BLUE}{BOLD}║         THE DILEMMA EXPERIMENT — EPISODE 7: TAGS & TRIBALISM                   ║{RESET}")
    print(f"{COLOR_BLUE}{BOLD}║         In-Group Favoritism, Arbitrary Markers & False-Beard Invasions         ║{RESET}")
    print(f"{COLOR_BLUE}{BOLD}╚════════════════════════════════════════════════════════════════════════════════╝{RESET}")
    print(f" {DIM}Theory: Riolo, Cohen & Axelrod (Nature 2001) & Hamilton's Green Beard (1964){RESET}")
    fb_status = f"{COLOR_PURPLE}{BOLD}INFILTRATOR PRESENT{RESET}" if false_beard_active else f"{DIM}INACTIVE{RESET}"
    print(
        f" {LIGHT_GRAY}Config: {BOLD}{pairings}{RESET} Pairings/Agent | "
        f"False-Beard Cheater: {fb_status}\n"
    )


def print_scoreboard(
    agents: list[Agent],
    scores: dict[str, int],
    in_group_coops: dict[str, int],
    in_group_matches: dict[str, int],
    out_group_coops: dict[str, int],
    out_group_matches: dict[str, int],
) -> None:
    """Render the current tribal leaderboard and cooperation statistics."""
    tags = [str(getattr(a.strategy, "tag", "NONE")) for a in agents]
    diversity = calculate_shannon_diversity(tags)

    print(f"{BOLD}┌─ TRIBAL LEDGER & POPULATION CENSUS ───────────────────────────────────────────┐{RESET}")
    print(f"{BOLD}│ AGENT ID       TRIBE BADGE     POINTS   IN-GROUP COOP   OUT-GROUP COOP  ROLE  │{RESET}")
    print("├───────────────────────────────────────────────────────────────────────────────┤")

    sorted_agents = sorted(agents, key=lambda a: (-scores[a.id], a.id))
    for a in sorted_agents:
        strat = a.strategy
        tag = str(getattr(strat, "tag", "NONE"))
        is_fb = isinstance(strat, FalseBeardStrategy)
        badge = format_tribal_badge(tag, is_false_beard=is_fb)
        pts = scores[a.id]

        in_m = in_group_matches[a.id]
        in_c = in_group_coops[a.id]
        in_pct = f"{int((in_c / in_m) * 100):3d}%" if in_m > 0 else "N/A "

        out_m = out_group_matches[a.id]
        out_c = out_group_coops[a.id]
        out_pct = f"{int((out_c / out_m) * 100):3d}%" if out_m > 0 else "N/A "

        role = f"{COLOR_PURPLE}CHEATER{RESET}" if is_fb else f"{DIM}LOYALIST{RESET}"

        print(
            f"│ {BOLD}{a.id:<14}{RESET} {badge} "
            f"{COLOR_GOLD}{pts:>5d}{RESET} pts     {COLOR_GREEN}{in_pct}{RESET}           {COLOR_RED}{out_pct}{RESET}     {role} │"
        )
    print("├───────────────────────────────────────────────────────────────────────────────┤")
    print(f"│ {LIGHT_GRAY}Tag Shannon Diversity Index: {COLOR_BLUE}{BOLD}{diversity:.4f}{RESET} (Max balanced: 1.386)                 │")
    print(f"{BOLD}└───────────────────────────────────────────────────────────────────────────────┘{RESET}\n")


def run_interactive_simulation(
    pairings: int = 15,
    include_false_beard: bool = True,
    delay: float = 0.12,
    step_mode: bool = False,
    seed: int = 42,
) -> None:
    """Run the live interactive tag-based tribalism simulation."""
    rng = random.Random(seed)
    game = PrisonersDilemma(DEFAULT_PAYOFF_MATRIX)

    # Build multi-tribal society
    agents: list[Agent] = [
        Agent("Red_01", StrictTribalStrategy(tag="RED")),
        Agent("Red_02", StrictTribalStrategy(tag="RED")),
        Agent("Blue_01", StrictTribalStrategy(tag="BLUE")),
        Agent("Blue_02", StrictTribalStrategy(tag="BLUE")),
        Agent("Green_01", StrictTribalStrategy(tag="GREEN")),
        Agent("Green_02", StrictTribalStrategy(tag="GREEN")),
        Agent("Gold_01", StrictTribalStrategy(tag="GOLD")),
        Agent("Gold_02", StrictTribalStrategy(tag="GOLD")),
    ]

    if include_false_beard:
        # Infiltrator: wears Green, but defects unconditionally
        agents.append(Agent("Chameleon", FalseBeardStrategy(tag="GREEN")))

    scores = {a.id: 0 for a in agents}
    in_group_coops = {a.id: 0 for a in agents}
    in_group_matches = {a.id: 0 for a in agents}
    out_group_coops = {a.id: 0 for a in agents}
    out_group_matches = {a.id: 0 for a in agents}

    total_pairings = (len(agents) * pairings) // 2

    print("\033[2J\033[H", end="")  # Clear screen
    print_header(pairings, include_false_beard)
    print_scoreboard(
        agents,
        scores,
        in_group_coops,
        in_group_matches,
        out_group_coops,
        out_group_matches,
    )

    print(f"{BOLD}{COLOR_GOLD}▶ COMMENCING TRIBAL INTERACTION STREAM...{RESET}\n")
    if step_mode:
        input(f"{DIM}Press [ENTER] to step through encounters...{RESET}")

    for match_idx in range(1, total_pairings + 1):
        a, b = rng.sample(agents, 2)
        tag_a = str(getattr(a.strategy, "tag", "NONE"))
        tag_b = str(getattr(b.strategy, "tag", "NONE"))

        dist = compute_tag_distance(tag_a, tag_b)
        is_same_tribe = dist == 0.0

        ctx_a = DecisionContext(opponent_id=b.id, opponent_tag=tag_b, self_tag=tag_a)
        ctx_b = DecisionContext(opponent_id=a.id, opponent_tag=tag_a, self_tag=tag_b)

        act_a = a.strategy.choose_action(ctx_a)
        act_b = b.strategy.choose_action(ctx_b)

        payoff = game.resolve(act_a, act_b)
        scores[a.id] += payoff.first
        scores[b.id] += payoff.second

        # Update stats
        if is_same_tribe:
            in_group_matches[a.id] += 1
            in_group_matches[b.id] += 1
            if act_a == Action.COOPERATE:
                in_group_coops[a.id] += 1
            if act_b == Action.COOPERATE:
                in_group_coops[b.id] += 1
        else:
            out_group_matches[a.id] += 1
            out_group_matches[b.id] += 1
            if act_a == Action.COOPERATE:
                out_group_coops[a.id] += 1
            if act_b == Action.COOPERATE:
                out_group_coops[b.id] += 1

        # Render encounter
        badge_a = format_tribal_badge(
            tag_a, is_false_beard=isinstance(a.strategy, FalseBeardStrategy)
        )
        badge_b = format_tribal_badge(
            tag_b, is_false_beard=isinstance(b.strategy, FalseBeardStrategy)
        )

        if is_same_tribe:
            if act_a == Action.COOPERATE and act_b == Action.COOPERATE:
                tag_label = f"{BG_GREEN}{BOLD} 🤝 IN-GROUP ALLIANCE {RESET}"
            else:
                tag_label = f"{BG_RED}{BOLD} ⚠️ IN-GROUP BETRAYAL {RESET}"
        else:
            tag_label = f"{DARK_GRAY}[OUT-GROUP ENMITY]{RESET}"

        act_a_str = (
            f"{COLOR_GREEN}COOP{RESET}"
            if act_a == Action.COOPERATE
            else f"{COLOR_RED}DFCT{RESET}"
        )
        act_b_str = (
            f"{COLOR_GREEN}COOP{RESET}"
            if act_b == Action.COOPERATE
            else f"{COLOR_RED}DFCT{RESET}"
        )

        print(
            f"{DIM}#{match_idx:03d}{RESET} {tag_label} "
            f"{BOLD}{a.id:<10}{RESET} {badge_a} ({act_a_str}) vs "
            f"{BOLD}{b.id:<10}{RESET} {badge_b} ({act_b_str}) "
            f"-> {COLOR_GOLD}+{payoff.first}{RESET} / {COLOR_GOLD}+{payoff.second}{RESET}"
        )

        # False-Beard Infiltration Alert
        if is_same_tribe and (
            isinstance(a.strategy, FalseBeardStrategy)
            or isinstance(b.strategy, FalseBeardStrategy)
        ):
            print(
                f"     {COLOR_PURPLE}{BOLD}⚠️ FALSE-BEARD EXPLOITATION:{RESET} "
                f"{ITALIC}Infiltrator wearing Green extracted altruism while paying zero donation cost!{RESET}"
            )

        # Refresh scoreboard periodically
        if match_idx % 6 == 0 or match_idx == total_pairings:
            print()
            print_scoreboard(
                agents,
                scores,
                in_group_coops,
                in_group_matches,
                out_group_coops,
                out_group_matches,
            )

        if step_mode:
            input(f"{DIM}[Press ENTER to advance]{RESET}")
        elif delay > 0:
            time.sleep(delay)

    print(f"\n{BOLD}{COLOR_GREEN}✔ TRIBAL SIMULATION CONCLUDED.{RESET}")
    print(f"{COLOR_BLUE}{BOLD}Scientific Conclusions:{RESET}")
    print(
        f"  • {BOLD}Parochial Altruism{RESET}: Arbitrary markers partition fluid stranger societies into high-trust enclaves."
    )
    print(
        f"  • {BOLD}Out-Group Hostility{RESET}: Cooperation between different tribes falls to 0%, proving tags generate automatic xenophobia."
    )
    print(
        f"  • {BOLD}The False-Beard Parasite{RESET}: Cheaters bearing in-group tags devastate loyalist fitness, proving green-beards require dynamic evolutionary cycles to survive."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Episode 7 Interactive CLI: Tags, Tribalism & False-Beard Invasions."
    )
    parser.add_argument("--pairings", type=int, default=15, help="Pairings per agent")
    parser.add_argument(
        "--no-cheater",
        action="store_true",
        help="Disable False-Beard cheater infiltrator",
    )
    parser.add_argument(
        "--delay", type=float, default=0.10, help="Seconds between matches"
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
        include_false_beard=not args.no_cheater,
        delay=delay,
        step_mode=args.step,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
