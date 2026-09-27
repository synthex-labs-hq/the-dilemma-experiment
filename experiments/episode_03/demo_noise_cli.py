#!/usr/bin/env python3
"""Cinematic Interactive Terminal Demonstration for Episode 3: Noise & Forgiveness.

Run this script to capture crisp, high-impact terminal footage of:
1. Act I: The Noise Glitch & Tit-for-Tat Echo Trap (Alternating Feud)
2. Act II: Grim Trigger's Fatal Unforgiving Collapse
3. Act III: The Forgiveness Antidotes (GTFT Olive Branch & Pavlov Reflex)
4. Act IV: The 8-Archetype Tournament Leaderboard under 5% Noise

Usage:
    uv run python experiments/episode_03/demo_noise_cli.py
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
from the_dilemma_experiment.strategies.generous_tit_for_tat import (
    GenerousTitForTatStrategy,
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
from the_dilemma_experiment.strategies.tit_for_two_tats import (
    TitForTwoTatsStrategy,
)
from the_dilemma_experiment.strategies.win_stay_lose_shift import (
    WinStayLoseShiftStrategy,
)

# ANSI Colors
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
CYAN = "\033[36m"
AMBER = "\033[33m"
GREEN = "\033[32m"
RED = "\033[31m"
MAGENTA = "\033[35m"
WHITE = "\033[97m"
YELLOW = "\033[93m"


def slow_print(text: str, delay: float = 0.015):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def print_banner():
    banner = f"""{MAGENTA}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║         ███╗   ██╗ ██████╗ ██╗███████╗███████╗                       ║
║         ████╗  ██║██╔═══██╗██║██╔════╝██╔════╝                       ║
║         ██╔██╗ ██║██║   ██║██║███████╗█████╗                         ║
║         ██║╚██╗██║██║   ██║██║╚════██║██╔══╝                         ║
║         ██║ ╚████║╚██████╔╝██║███████║███████╗                       ║
║         ╚═╝  ╚═══╝ ╚═════╝ ╚═╝╚══════╝╚══════╝                       ║
║                                                                      ║
║        THE BROKEN WIRE & THE MATHEMATICS OF FORGIVENESS              ║
║                  EPISODE 3 — SIMULATION ARENA                        ║
╚══════════════════════════════════════════════════════════════════════╝{RESET}"""
    print(banner)
    time.sleep(0.6)


def run_act_1_echo_spiral():
    print(f"\n{BOLD}{CYAN}══ ACT I: THE GLITCH & THE ECHO TRAP (Tit-for-Tat vs Tit-for-Tat) ══{RESET}")
    slow_print(f"{DIM}Two reciprocal agents enter the arena. Both want to cooperate. Watch what happens when a 2% transmission glitch strikes.{RESET}", 0.008)
    time.sleep(0.4)

    print(f"\n{'RND':<4} | {'TFT ALPHA':<12} | {'TFT BETA':<12} | {'PAYOFF':<10} | {'CHANNEL STATUS'}")
    print("-" * 72)

    rounds_data = [
        (1, Action.COOPERATE, Action.COOPERATE, False, "Clean transmission"),
        (2, Action.COOPERATE, Action.COOPERATE, False, "Clean transmission"),
        (3, Action.COOPERATE, Action.COOPERATE, False, "Clean transmission"),
        (4, Action.COOPERATE, Action.COOPERATE, False, "Clean transmission"),
        (5, Action.DEFECT, Action.COOPERATE, True, "⚡ NOISE GLITCH: Alpha C -> DEFECT!"),
        (6, Action.COOPERATE, Action.DEFECT, False, "Beta retaliates against Round 5"),
        (7, Action.DEFECT, Action.COOPERATE, False, "Alpha retaliates against Round 6"),
        (8, Action.COOPERATE, Action.DEFECT, False, "Beta retaliates against Round 7"),
        (9, Action.DEFECT, Action.COOPERATE, False, "Alpha retaliates against Round 8"),
        (10, Action.COOPERATE, Action.DEFECT, False, "Beta retaliates against Round 9"),
    ]

    for rnd, a1, a2, is_glitch, note in rounds_data:
        c1 = f"{CYAN}COOPERATE{RESET}" if a1 == Action.COOPERATE else f"{AMBER}DEFECT   {RESET}"
        c2 = f"{CYAN}COOPERATE{RESET}" if a2 == Action.COOPERATE else f"{AMBER}DEFECT   {RESET}"

        if a1 == Action.COOPERATE and a2 == Action.COOPERATE:
            payoff_str = f"{GREEN}+3 / +3{RESET}"
        elif a1 == Action.DEFECT and a2 == Action.COOPERATE:
            payoff_str = f"{YELLOW}+5 /  0{RESET}"
        elif a1 == Action.COOPERATE and a2 == Action.DEFECT:
            payoff_str = f"{RED} 0 / +5{RESET}"
        else:
            payoff_str = f"{RED}+1 / +1{RESET}"

        status = f"{MAGENTA}{BOLD}{note}{RESET}" if is_glitch else (f"{DIM}{note}{RESET}" if "Clean" in note else f"{YELLOW}{note}{RESET}")

        print(f"#{rnd:<3} | {c1}   | {c2}   | {payoff_str:<19} | {status}")
        time.sleep(0.35 if not is_glitch else 0.8)

    print("-" * 72)
    slow_print(f"{RED}{BOLD}➔ THE ECHO TRAP:{RESET} A single glitch locks classic Tit-for-Tat into an endless alternating vendetta.", 0.01)
    slow_print(f"{DIM}Mutual cooperation drops from +3.0/round to an unstable +2.5/round forever.{RESET}\n", 0.008)
    time.sleep(0.6)


def run_act_2_grim_trigger():
    print(f"\n{BOLD}{AMBER}══ ACT II: GRIM TRIGGER'S FATAL UNFORGIVING COLLAPSE ══{RESET}")
    slow_print(f"{DIM}Grim Trigger plays against an unconditional Altruist. Grim has ZERO forgiveness.{RESET}", 0.008)
    time.sleep(0.4)

    print(f"\n{'RND':<4} | {'GRIM TRIGGER':<14} | {'ALTRUIST':<12} | {'PAYOFF':<10} | {'CHANNEL STATUS'}")
    print("-" * 72)

    rounds_data = [
        (1, Action.COOPERATE, Action.COOPERATE, False, "Mutual trust established"),
        (2, Action.COOPERATE, Action.COOPERATE, False, "Mutual trust"),
        (3, Action.COOPERATE, Action.DEFECT, True, "⚡ NOISE GLITCH: Altruist C -> DEFECT!"),
        (4, Action.DEFECT, Action.COOPERATE, False, "Grim locks into PERMANENT DEFECT"),
        (5, Action.DEFECT, Action.COOPERATE, False, "Altruist offers C; Grim burns bridge"),
        (6, Action.DEFECT, Action.COOPERATE, False, "Altruist offers C; Grim burns bridge"),
        (7, Action.DEFECT, Action.COOPERATE, False, "Eternal exploitation until round 50..."),
    ]

    for rnd, a1, a2, is_glitch, note in rounds_data:
        c1 = f"{CYAN}COOPERATE{RESET}" if a1 == Action.COOPERATE else f"{RED}DEFECT   {RESET}"
        c2 = f"{CYAN}COOPERATE{RESET}" if a2 == Action.COOPERATE else f"{AMBER}DEFECT   {RESET}"

        if a1 == Action.COOPERATE and a2 == Action.COOPERATE:
            payoff_str = f"{GREEN}+3 / +3{RESET}"
        elif a1 == Action.DEFECT and a2 == Action.COOPERATE:
            payoff_str = f"{YELLOW}+5 /  0{RESET}"
        else:
            payoff_str = f"{RED}+1 / +1{RESET}"

        status = f"{MAGENTA}{BOLD}{note}{RESET}" if is_glitch else (f"{DIM}{note}{RESET}" if "trust" in note else f"{RED}{note}{RESET}")

        print(f"#{rnd:<3} | {c1}     | {c2}   | {payoff_str:<19} | {status}")
        time.sleep(0.35 if not is_glitch else 0.8)

    print("-" * 72)
    slow_print(f"{RED}{BOLD}➔ ZERO-TOLERANCE PARADOX:{RESET} Grim Trigger avoids exploitation, but 1 bit of noise permanently destroys trust.", 0.01)
    time.sleep(0.6)


def run_act_3_forgiveness():
    print(f"\n{BOLD}{GREEN}══ ACT III: THE HEALERS ENTER (Generous TFT & Pavlov / WSLS) ══{RESET}")
    slow_print(f"{DIM}How algorithms heal broken trust: Probabilistic Forgiveness and Win-Stay Lose-Shift reflex.{RESET}", 0.008)
    time.sleep(0.4)

    # Duel A: Generous TFT
    print(f"\n{BOLD}{CYAN}--- SCENE 1: Generous Tit-for-Tat Extends the Olive Branch ---{RESET}")
    print(f"{'RND':<4} | {'GENEROUS TFT':<14} | {'TIT-FOR-TAT':<12} | {'PAYOFF':<10} | {'DYNAMICS'}")
    print("-" * 72)

    gtft_data = [
        (1, Action.COOPERATE, Action.COOPERATE, False, "Mutual cooperation"),
        (2, Action.COOPERATE, Action.DEFECT, True, "⚡ NOISE: TFT C -> DEFECT!"),
        (3, Action.COOPERATE, Action.DEFECT, False, "🕊️ GTFT FORGIVES (q=33%)! TFT mirrors R2"),
        (4, Action.COOPERATE, Action.COOPERATE, False, "✨ HEALED! Both return to mutual C"),
        (5, Action.COOPERATE, Action.COOPERATE, False, "Cooperation completely restored"),
    ]

    for rnd, a1, a2, is_glitch, note in gtft_data:
        c1 = f"{GREEN}COOPERATE{RESET}" if a1 == Action.COOPERATE else f"{AMBER}DEFECT   {RESET}"
        c2 = f"{CYAN}COOPERATE{RESET}" if a2 == Action.COOPERATE else f"{AMBER}DEFECT   {RESET}"
        payoff_str = f"{GREEN}+3 / +3{RESET}" if (a1 == Action.COOPERATE and a2 == Action.COOPERATE) else f"{YELLOW} 0 / +5{RESET}"
        status = f"{MAGENTA}{BOLD}{note}{RESET}" if is_glitch else (f"{GREEN}{BOLD}{note}{RESET}" if "HEALED" in note or "FORGIVES" in note else f"{DIM}{note}{RESET}")

        print(f"#{rnd:<3} | {c1}     | {c2}   | {payoff_str:<19} | {status}")
        time.sleep(0.4 if not is_glitch else 0.8)

    time.sleep(0.4)
    # Duel B: Pavlov
    print(f"\n{BOLD}{CYAN}--- SCENE 2: Win-Stay, Lose-Shift (Pavlov) Self-Correction ---{RESET}")
    print(f"{'RND':<4} | {'PAVLOV ALPHA':<14} | {'PAVLOV BETA':<12} | {'PAYOFF':<10} | {'DYNAMICS'}")
    print("-" * 72)

    pavlov_data = [
        (1, Action.COOPERATE, Action.COOPERATE, False, "Win (CC) -> Both Stay C"),
        (2, Action.DEFECT, Action.COOPERATE, True, "⚡ NOISE: Alpha C -> DEFECT!"),
        (3, Action.DEFECT, Action.DEFECT, False, "Alpha Stays (DC=Win); Beta Shifts (CD=Loss)"),
        (4, Action.COOPERATE, Action.COOPERATE, False, "✨ Both Shift (DD=Loss) -> Back to CC!"),
        (5, Action.COOPERATE, Action.COOPERATE, False, "Win (CC) -> Continuous mutual trust"),
    ]

    for rnd, a1, a2, is_glitch, note in pavlov_data:
        c1 = f"{CYAN}COOPERATE{RESET}" if a1 == Action.COOPERATE else f"{AMBER}DEFECT   {RESET}"
        c2 = f"{CYAN}COOPERATE{RESET}" if a2 == Action.COOPERATE else f"{AMBER}DEFECT   {RESET}"
        if a1 == Action.COOPERATE and a2 == Action.COOPERATE:
            payoff_str = f"{GREEN}+3 / +3{RESET}"
        elif a1 == Action.DEFECT and a2 == Action.DEFECT:
            payoff_str = f"{RED}+1 / +1{RESET}"
        else:
            payoff_str = f"{YELLOW}+5 /  0{RESET}"
        status = f"{MAGENTA}{BOLD}{note}{RESET}" if is_glitch else (f"{GREEN}{BOLD}{note}{RESET}" if "Back to CC" in note else f"{DIM}{note}{RESET}")

        print(f"#{rnd:<3} | {c1}     | {c2}   | {payoff_str:<19} | {status}")
        time.sleep(0.4 if not is_glitch else 0.8)

    print("-" * 72)
    slow_print(f"{GREEN}{BOLD}➔ THE MATHEMATICAL CURE:{RESET} Forgiveness dampens echo noise. Pavlov self-heals in exactly 2 rounds.", 0.01)
    time.sleep(0.6)


def run_act_4_noisy_tournament():
    print(f"\n{BOLD}{YELLOW}══ ACT IV: 8-ARCHETYPE TOURNAMENT LEADERBOARD UNDER 5% NOISE ══{RESET}")
    slow_print(f"{DIM}Running full round-robin tournament (28 matches, 1,400 rounds) at epsilon = 0.05...{RESET}", 0.008)
    time.sleep(0.4)

    game = PrisonersDilemma()
    agents = [
        Agent("Altruist", AlwaysCooperateStrategy()),
        Agent("Predator", AlwaysDefectStrategy()),
        Agent("TitForTat", TitForTatStrategy()),
        Agent("GrimTrigger", GrimTriggerStrategy()),
        Agent("Random", RandomStrategy(seed=42, cooperation_probability=0.5)),
        Agent("GenerousTFT", GenerousTitForTatStrategy(forgiveness_probability=1 / 3, seed=52)),
        Agent("TitForTwoTats", TitForTwoTatsStrategy()),
        Agent("Pavlov_WSLS", WinStayLoseShiftStrategy()),
    ]
    tourney = Tournament(Population(agents), game, rounds_per_match=50, noise=0.05, seed=42)
    result = tourney.execute()

    print("\n" + "=" * 76)
    print(f"{'RANK':<5} | {'AGENT':<16} | {'SCORE':<7} | {'AVG/RND':<8} | {'W-T-L':<9} | {'COOP %':<7}")
    print("=" * 76)

    for row in result.leaderboard:
        wtl = f"{row.wins}-{row.ties}-{row.losses}"
        if row.rank == 1:
            badge = "🥇"
        elif row.rank == 2:
            badge = "🥈"
        elif row.rank == 3:
            badge = "🥉"
        else:
            badge = f" #{row.rank}"

        print(
            f"{badge:<5} | {row.agent_id:<16} | {row.total_score:<7} | "
            f"{row.average_score_per_round:<8.2f} | {wtl:<9} | {row.cooperation_rate * 100:<6.1f}%"
        )
        time.sleep(0.12)

    print("=" * 76)
    print(f"\n{BOLD}{CYAN}TOTAL MATCHES:{RESET} 28 | {BOLD}{CYAN}TOTAL ROUNDS:{RESET} 1,400 | {BOLD}{CYAN}POPULATION COOPERATION:{RESET} {result.population_cooperation_rate * 100:.1f}%\n")


def main():
    print_banner()
    run_act_1_echo_spiral()
    run_act_2_grim_trigger()
    run_act_3_forgiveness()
    run_act_4_noisy_tournament()


if __name__ == "__main__":
    main()
