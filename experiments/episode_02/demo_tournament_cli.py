#!/usr/bin/env python3
"""Cinematic Interactive Terminal Demonstration for Episode 2: The Tournament.

Run this script to capture crisp, high-impact terminal footage of the multi-agent
round-robin tournament in action for video production and screencasts.

Usage:
    uv run python experiments/episode_02/demo_tournament_cli.py
"""

import sys
import time

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.population import Population
from the_dilemma_experiment.domain.prisoners_dilemma import PrisonersDilemma
from the_dilemma_experiment.domain.tournament import Tournament
from the_dilemma_experiment.strategies.always_cooperate import (
    AlwaysCooperateStrategy,
)
from the_dilemma_experiment.strategies.always_defect import (
    AlwaysDefectStrategy,
)
from the_dilemma_experiment.strategies.grim_trigger import (
    GrimTriggerStrategy,
)
from the_dilemma_experiment.strategies.random_strategy import (
    RandomStrategy,
)
from the_dilemma_experiment.strategies.tit_for_tat import (
    TitForTatStrategy,
)

# ANSI Colors for cinematic terminal styling
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
CYAN = "\033[36m"
AMBER = "\033[33m"
GREEN = "\033[32m"
RED = "\033[31m"
MAGENTA = "\033[35m"
WHITE = "\033[97m"
BLUE = "\033[34m"
YELLOW = "\033[93m"


def print_banner():
    banner = f"""{CYAN}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ████████╗██╗  ██╗███████╗   ██████╗ ██╗██╗     ███████╗███╗   ███╗███╗   ███╗║
║   ╚══██╔══╝██║  ██║██╔════╝   ██╔══██╗██║██║     ██╔════╝████╗ ████║████╗ ████║║
║      ██║   ███████║█████╗     ██║  ██║██║██║     █████╗  ██╔████╔██║██╔████╔██║║
║      ██║   ██╔══██║██╔══╝     ██║  ██║██║██║     ██╔══╝  ██║╚██╔╝██║██║╚██╔╝██║║
║      ██║   ██║  ██║███████╗   ██████╔╝██║███████╗███████╗██║ ╚═╝ ██║██║ ╚═╝ ██║║
║      ╚═╝   ╚═╝  ╚═╝╚══════╝   ╚═════╝ ╚═╝╚══════╝╚══════╝╚═╝     ╚═╝╚═╝     ╚═╝║
║                                                                              ║
║               E P I S O D E  2 :  T H E   T O U R N A M E N T                ║
║                      synthex-labs-hq // multi-agent society                  ║
╚══════════════════════════════════════════════════════════════════════════════╝{RESET}
"""
    print(banner)
    time.sleep(0.8)


def format_action(action: Action) -> str:
    if action == Action.COOPERATE:
        return f"{CYAN}C{RESET}"
    return f"{AMBER}D{RESET}"


def run_cinematic_tournament():
    print_banner()

    print(f"{BOLD}{WHITE}>>> INITIALIZING MULTI-AGENT POPULATION...{RESET}")
    time.sleep(0.5)

    archetypes = [
        ("AlwaysCooperate", AlwaysCooperateStrategy(), "The Altruist", CYAN),
        ("AlwaysDefect", AlwaysDefectStrategy(), "The Predator", RED),
        ("TitForTat", TitForTatStrategy(), "The Reciprocal Cop", GREEN),
        ("GrimTrigger", GrimTriggerStrategy(), "The Unforgiving Grudger", MAGENTA),
        ("Random", RandomStrategy(seed=42), "The Chaos Agent", YELLOW),
    ]

    agents = []
    for name, strat, archetype, color in archetypes:
        print(f"  • Registered Agent: {color}{BOLD}{name:<16}{RESET} [{archetype}]")
        agents.append(Agent(name, strat))
        time.sleep(0.3)

    print(f"\n{BOLD}{WHITE}>>> SCHEDULING ROUND-ROBIN TOURNAMENT...{RESET}")
    game = PrisonersDilemma()
    rounds = 30
    population = Population(agents)
    tournament = Tournament(population, game, rounds_per_match=rounds)

    total_pairings = (len(agents) * (len(agents) - 1)) // 2
    print(f"  {DIM}Total Participants:{RESET} {BOLD}{len(agents)}{RESET}")
    print(f"  {DIM}Matches Scheduled:{RESET}  {BOLD}{total_pairings}{RESET} round-robin duels")
    print(f"  {DIM}Rounds Per Match:{RESET}   {BOLD}{rounds}{RESET}")
    print(f"  {DIM}Total Interactions:{RESET} {BOLD}{total_pairings * rounds}{RESET} rounds")
    print(f"\n{MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{BOLD}{WHITE}                   L I V E   M A T C H   T I C K E R                          {RESET}")
    print(f"{MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")
    time.sleep(1.0)

    # Execute tournament
    result = tournament.execute()

    for idx, match in enumerate(tournament.matches, 1):
        res = match.result
        if not res:
            continue

        p1, p2 = res.first_agent_id, res.second_agent_id
        s1, s2 = res.first_score, res.second_score

        # Sample a few moves
        sample_moves = "".join(
            f"{format_action(r.first_action)}/{format_action(r.second_action)} "
            for r in match.rounds[:6]
        )

        outcome_badge = f"{GREEN}DRAW{RESET}" if s1 == s2 else (
            f"{CYAN}{p1} WINS{RESET}" if s1 > s2 else f"{AMBER}{p2} WINS{RESET}"
        )

        print(
            f"  {DIM}Match {idx:02d}/{total_pairings:02d}:{RESET} "
            f"{BOLD}{p1:>15}{RESET} vs {BOLD}{p2:<15}{RESET} "
            f"│ Score: {BOLD}{s1:3d}{RESET} - {BOLD}{s2:3d}{RESET} "
            f"│ {outcome_badge:<16} "
            f"│ Sample: [{sample_moves}...]"
        )
        time.sleep(0.4)

    print(f"\n{MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{BOLD}{WHITE}               F I N A L   T O U R N A M E N T   S T A N D I N G S            {RESET}")
    print(f"{MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")
    time.sleep(1.0)

    print(
        f"  {BOLD}{'RANK':<6} {'AGENT':<18} {'STRATEGY':<22} {'TOTAL':<8} {'AVG/RND':<9} {'W-T-L':<9} {'COOP RATE':<10}{RESET}"
    )
    print(f"  {DIM}{'─'*6} {'─'*18} {'─'*22} {'─'*8} {'─'*9} {'─'*9} {'─'*10}{RESET}")

    medals = ["🥇", "🥈", "🥉", "  ", "  "]
    for entry in result.leaderboard:
        medal = medals[entry.rank - 1]
        wtl = f"{entry.wins}-{entry.ties}-{entry.losses}"
        coop_pct = f"{entry.cooperation_rate * 100:.1f}%"

        color = GREEN if entry.rank <= 2 else (YELLOW if entry.rank == 3 else RESET)

        print(
            f"  {color}{medal} #{entry.rank:<3} "
            f"{BOLD}{entry.agent_id:<18}{RESET} "
            f"{DIM}{entry.strategy_name:<22}{RESET} "
            f"{BOLD}{entry.total_score:<8}{RESET} "
            f"{entry.average_score_per_round:<9.2f} "
            f"{wtl:<9} "
            f"{CYAN}{coop_pct:<10}{RESET}"
        )
        time.sleep(0.4)

    time.sleep(0.8)
    print(f"\n{CYAN}──────────────────────────────────────────────────────────────────────────────{RESET}")
    print(f"  {BOLD}THE AXELROD PARADOX IN ACTION:{RESET}")
    print(f"  Notice: {BOLD}AlwaysDefect{RESET} won the most direct match duels ({result.get_entry('AlwaysDefect').wins} wins),")
    print(f"  YET {BOLD}GrimTrigger{RESET} & {BOLD}TitForTat{RESET} accumulate top cumulative utility by sustaining")
    print(f"  mutual cooperation without succumbing to endless exploitation.")
    print(f"  {DIM}Population Cooperation Rate:{RESET} {BOLD}{result.population_cooperation_rate * 100:.1f}%{RESET}")
    print(f"{CYAN}──────────────────────────────────────────────────────────────────────────────{RESET}\n")


if __name__ == "__main__":
    run_cinematic_tournament()
