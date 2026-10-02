#!/usr/bin/env python3
"""Cinematic Interactive Terminal Demonstration for Episode 3: Noise & Forgiveness.

Pre-calibrated to synchronize with the voiceover narration timeline from
video_script_master.md:
1. Act I: The Noise Glitch & Tit-for-Tat Echo Trap (holds for voiceover narration)
2. Act II: Grim Trigger's Fatal Unforgiving Collapse (holds on zero-tolerance paradox)
3. Act III: The Forgiveness Antidotes (GTFT Olive Branch & Pavlov Reflex)
4. Act IV: The 8-Archetype Tournament Leaderboard under 5% Noise (Predator surge)

Usage:
    # Calibrated script pacing (default - holds at each act for voiceover):
    uv run python experiments/episode_03/demo_noise_cli.py

    # Presenter step mode (press ENTER to advance between acts):
    uv run python experiments/episode_03/demo_noise_cli.py --step

    # Fast mode (quick testing / CI without delays):
    uv run python experiments/episode_03/demo_noise_cli.py --fast
"""

import argparse
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


def slow_print(text: str, delay: float = 0.015, fast: bool = False):
    if fast:
        print(text)
        return
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def wait_or_step(duration: float, step: bool = False, fast: bool = False, prompt: str = ""):
    """Hold execution to match spoken voiceover pacing or wait for Enter."""
    if fast:
        time.sleep(0.05)
        return

    if step:
        msg = f"\n{DIM}[Press ENTER to advance...]{RESET}" if not prompt else f"\n{DIM}[{prompt} - Press ENTER]{RESET}"
        try:
            input(msg)
            # Clear the prompt line to keep terminal recording clean
            sys.stdout.write("\033[F\033[K")
            sys.stdout.flush()
        except (KeyboardInterrupt, EOFError):
            print()
            sys.exit(0)
    else:
        time.sleep(duration)


def print_banner(step: bool = False, fast: bool = False):
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
    wait_or_step(3.0, step=step, fast=fast, prompt="Ready to start Act I")


def run_act_1_echo_spiral(step: bool = False, fast: bool = False):
    print(f"\n{BOLD}{CYAN}══ ACT I: THE GLITCH & THE ECHO TRAP (Tit-for-Tat vs Tit-for-Tat) ══{RESET}")
    slow_print(
        f"{DIM}Two reciprocal agents enter the arena. Both want to cooperate. Watch what happens when a 2% transmission glitch strikes.{RESET}",
        0.008,
        fast=fast,
    )
    wait_or_step(2.5, step=step, fast=fast)

    print(f"\n{'RND':<4} | {'TFT ALPHA':<12} | {'TFT BETA':<12} | {'PAYOFF':<10} | {'CHANNEL STATUS'}")
    print("-" * 72)

    rounds_data = [
        (1, Action.COOPERATE, Action.COOPERATE, False, "Clean transmission", 0.9),
        (2, Action.COOPERATE, Action.COOPERATE, False, "Clean transmission", 0.9),
        (3, Action.COOPERATE, Action.COOPERATE, False, "Clean transmission", 0.9),
        (4, Action.COOPERATE, Action.COOPERATE, False, "Clean transmission", 0.9),
        (5, Action.DEFECT, Action.COOPERATE, True, "⚡ NOISE GLITCH: Alpha C -> DEFECT!", 3.0),
        (6, Action.COOPERATE, Action.DEFECT, False, "Beta retaliates against Round 5", 1.2),
        (7, Action.DEFECT, Action.COOPERATE, False, "Alpha retaliates against Round 6", 1.2),
        (8, Action.COOPERATE, Action.DEFECT, False, "Beta retaliates against Round 7", 1.2),
        (9, Action.DEFECT, Action.COOPERATE, False, "Alpha retaliates against Round 8", 1.2),
        (10, Action.COOPERATE, Action.DEFECT, False, "Beta retaliates against Round 9", 1.2),
    ]

    for rnd, a1, a2, is_glitch, note, delay in rounds_data:
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

        status = (
            f"{MAGENTA}{BOLD}{note}{RESET}"
            if is_glitch
            else (f"{DIM}{note}{RESET}" if "Clean" in note else f"{YELLOW}{note}{RESET}")
        )

        print(f"#{rnd:<3} | {c1}   | {c2}   | {payoff_str:<19} | {status}")
        if not fast:
            time.sleep(delay)

    print("-" * 72)
    slow_print(
        f"{RED}{BOLD}➔ THE ECHO TRAP:{RESET} A single glitch locks classic Tit-for-Tat into an endless alternating vendetta.",
        0.008,
        fast=fast,
    )
    slow_print(
        f"{DIM}Mutual cooperation drops from +3.0/round to an unstable +2.5/round forever.{RESET}\n",
        0.008,
        fast=fast,
    )

    # HOLD ON ECHO TRAP: Gives speaker 15 seconds to explain the Hatfield & McCoy retaliation feud
    wait_or_step(
        15.0,
        step=step,
        fast=fast,
        prompt="Holding on Echo Trap. Press ENTER when ready for Act II (Grim Trigger)",
    )


def run_act_2_grim_trigger(step: bool = False, fast: bool = False):
    print(f"\n{BOLD}{AMBER}══ ACT II: GRIM TRIGGER'S FATAL UNFORGIVING COLLAPSE ══{RESET}")
    slow_print(
        f"{DIM}Grim Trigger plays against an unconditional Altruist. Grim has ZERO forgiveness.{RESET}",
        0.008,
        fast=fast,
    )
    wait_or_step(2.0, step=step, fast=fast)

    print(f"\n{'RND':<4} | {'GRIM TRIGGER':<14} | {'ALTRUIST':<12} | {'PAYOFF':<10} | {'CHANNEL STATUS'}")
    print("-" * 72)

    rounds_data = [
        (1, Action.COOPERATE, Action.COOPERATE, False, "Mutual trust established", 0.9),
        (2, Action.COOPERATE, Action.COOPERATE, False, "Mutual trust", 0.9),
        (3, Action.COOPERATE, Action.DEFECT, True, "⚡ NOISE GLITCH: Altruist C -> DEFECT!", 2.2),
        (4, Action.DEFECT, Action.COOPERATE, False, "Grim locks into PERMANENT DEFECT", 1.5),
        (5, Action.DEFECT, Action.COOPERATE, False, "Altruist offers C; Grim burns bridge", 1.0),
        (6, Action.DEFECT, Action.COOPERATE, False, "Altruist offers C; Grim burns bridge", 1.0),
        (7, Action.DEFECT, Action.COOPERATE, False, "Eternal exploitation until round 50...", 1.0),
    ]

    for rnd, a1, a2, is_glitch, note, delay in rounds_data:
        c1 = f"{CYAN}COOPERATE{RESET}" if a1 == Action.COOPERATE else f"{RED}DEFECT   {RESET}"
        c2 = f"{CYAN}COOPERATE{RESET}" if a2 == Action.COOPERATE else f"{AMBER}DEFECT   {RESET}"

        if a1 == Action.COOPERATE and a2 == Action.COOPERATE:
            payoff_str = f"{GREEN}+3 / +3{RESET}"
        elif a1 == Action.DEFECT and a2 == Action.COOPERATE:
            payoff_str = f"{YELLOW}+5 /  0{RESET}"
        else:
            payoff_str = f"{RED}+1 / +1{RESET}"

        status = (
            f"{MAGENTA}{BOLD}{note}{RESET}"
            if is_glitch
            else (f"{DIM}{note}{RESET}" if "trust" in note else f"{RED}{note}{RESET}")
        )

        print(f"#{rnd:<3} | {c1}     | {c2}   | {payoff_str:<19} | {status}")
        if not fast:
            time.sleep(delay)

    print("-" * 72)
    slow_print(
        f"{RED}{BOLD}➔ ZERO-TOLERANCE PARADOX:{RESET} Grim Trigger avoids exploitation, but 1 bit of noise permanently destroys trust.\n",
        0.008,
        fast=fast,
    )

    # HOLD ON GRIM TRIGGER: Gives speaker 13 seconds for voiceover on why zero-tolerance fails
    wait_or_step(
        13.0,
        step=step,
        fast=fast,
        prompt="Holding on Grim Trigger. Press ENTER when ready for Act III (Forgiveness)",
    )


def run_act_3_forgiveness(step: bool = False, fast: bool = False):
    print(f"\n{BOLD}{GREEN}══ ACT III: THE HEALERS ENTER (Generous TFT & Pavlov / WSLS) ══{RESET}")
    slow_print(
        f"{DIM}How algorithms heal broken trust: Probabilistic Forgiveness and Win-Stay Lose-Shift reflex.{RESET}",
        0.008,
        fast=fast,
    )
    wait_or_step(2.5, step=step, fast=fast)

    # Duel A: Generous TFT
    print(f"\n{BOLD}{CYAN}--- SCENE 1: Generous Tit-for-Tat Extends the Olive Branch ---{RESET}")
    print(f"{'RND':<4} | {'GENEROUS TFT':<14} | {'TIT-FOR-TAT':<12} | {'PAYOFF':<10} | {'DYNAMICS'}")
    print("-" * 72)

    gtft_data = [
        (1, Action.COOPERATE, Action.COOPERATE, False, "Mutual cooperation", 0.9),
        (2, Action.COOPERATE, Action.DEFECT, True, "⚡ NOISE: TFT C -> DEFECT!", 1.8),
        (3, Action.COOPERATE, Action.DEFECT, False, "🕊️ GTFT FORGIVES (q=33%)! TFT mirrors R2", 2.2),
        (4, Action.COOPERATE, Action.COOPERATE, False, "✨ HEALED! Both return to mutual C", 1.5),
        (5, Action.COOPERATE, Action.COOPERATE, False, "Cooperation completely restored", 1.0),
    ]

    for rnd, a1, a2, is_glitch, note, delay in gtft_data:
        c1 = f"{GREEN}COOPERATE{RESET}" if a1 == Action.COOPERATE else f"{AMBER}DEFECT   {RESET}"
        c2 = f"{CYAN}COOPERATE{RESET}" if a2 == Action.COOPERATE else f"{AMBER}DEFECT   {RESET}"
        payoff_str = (
            f"{GREEN}+3 / +3{RESET}"
            if (a1 == Action.COOPERATE and a2 == Action.COOPERATE)
            else f"{YELLOW} 0 / +5{RESET}"
        )
        status = (
            f"{MAGENTA}{BOLD}{note}{RESET}"
            if is_glitch
            else (
                f"{GREEN}{BOLD}{note}{RESET}"
                if "HEALED" in note or "FORGIVES" in note
                else f"{DIM}{note}{RESET}"
            )
        )

        print(f"#{rnd:<3} | {c1}     | {c2}   | {payoff_str:<19} | {status}")
        if not fast:
            time.sleep(delay)

    # HOLD ON GTFT OLIVE BRANCH: 10 seconds for narration
    wait_or_step(
        10.0,
        step=step,
        fast=fast,
        prompt="Holding on Generous TFT. Press ENTER for Scene 2 (Pavlov)",
    )

    # Duel B: Pavlov
    print(f"\n{BOLD}{CYAN}--- SCENE 2: Win-Stay, Lose-Shift (Pavlov) Self-Correction ---{RESET}")
    print(f"{'RND':<4} | {'PAVLOV ALPHA':<14} | {'PAVLOV BETA':<12} | {'PAYOFF':<10} | {'DYNAMICS'}")
    print("-" * 72)

    pavlov_data = [
        (1, Action.COOPERATE, Action.COOPERATE, False, "Win (CC) -> Both Stay C", 0.9),
        (2, Action.DEFECT, Action.COOPERATE, True, "⚡ NOISE: Alpha C -> DEFECT!", 1.8),
        (3, Action.DEFECT, Action.DEFECT, False, "Alpha Stays (DC=Win); Beta Shifts (CD=Loss)", 2.2),
        (4, Action.COOPERATE, Action.COOPERATE, False, "✨ Both Shift (DD=Loss) -> Back to CC!", 2.2),
        (5, Action.COOPERATE, Action.COOPERATE, False, "Win (CC) -> Continuous mutual trust", 1.0),
    ]

    for rnd, a1, a2, is_glitch, note, delay in pavlov_data:
        c1 = f"{CYAN}COOPERATE{RESET}" if a1 == Action.COOPERATE else f"{AMBER}DEFECT   {RESET}"
        c2 = f"{CYAN}COOPERATE{RESET}" if a2 == Action.COOPERATE else f"{AMBER}DEFECT   {RESET}"
        if a1 == Action.COOPERATE and a2 == Action.COOPERATE:
            payoff_str = f"{GREEN}+3 / +3{RESET}"
        elif a1 == Action.DEFECT and a2 == Action.DEFECT:
            payoff_str = f"{RED}+1 / +1{RESET}"
        else:
            payoff_str = f"{YELLOW}+5 /  0{RESET}"
        status = (
            f"{MAGENTA}{BOLD}{note}{RESET}"
            if is_glitch
            else (f"{GREEN}{BOLD}{note}{RESET}" if "Back to CC" in note else f"{DIM}{note}{RESET}")
        )

        print(f"#{rnd:<3} | {c1}     | {c2}   | {payoff_str:<19} | {status}")
        if not fast:
            time.sleep(delay)

    print("-" * 72)
    slow_print(
        f"{GREEN}{BOLD}➔ THE MATHEMATICAL CURE:{RESET} Forgiveness dampens echo noise. Pavlov self-heals in exactly 2 rounds.\n",
        0.008,
        fast=fast,
    )

    # HOLD ON PAVLOV: 14 seconds for voiceover conclusion on forgiveness
    wait_or_step(
        14.0,
        step=step,
        fast=fast,
        prompt="Holding on Pavlov. Press ENTER when ready for Act IV (Leaderboard)",
    )


def run_act_4_noisy_tournament(step: bool = False, fast: bool = False):
    print(f"\n{BOLD}{YELLOW}══ ACT IV: 8-ARCHETYPE TOURNAMENT LEADERBOARD UNDER 5% NOISE ══{RESET}")
    slow_print(
        f"{DIM}Running full round-robin tournament (28 matches, 1,400 rounds) at epsilon = 0.05...{RESET}",
        0.008,
        fast=fast,
    )
    wait_or_step(2.0, step=step, fast=fast)

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
            highlight = f"{GREEN}{BOLD}"
        elif row.rank == 2:
            badge = "🥈"
            highlight = f"{RED}{BOLD}"  # Highlight the predator surge!
        elif row.rank == 3:
            badge = "🥉"
            highlight = f"{CYAN}{BOLD}"
        else:
            badge = f" #{row.rank}"
            highlight = RESET

        print(
            f"{badge:<5} | {highlight}{row.agent_id:<16}{RESET} | {row.total_score:<7} | "
            f"{row.average_score_per_round:<8.2f} | {wtl:<9} | {row.cooperation_rate * 100:<6.1f}%"
        )
        if not fast:
            time.sleep(0.4)

    print("=" * 76)
    print(
        f"\n{BOLD}{CYAN}TOTAL MATCHES:{RESET} 28 | {BOLD}{CYAN}TOTAL ROUNDS:{RESET} 1,400 | "
        f"{BOLD}{CYAN}POPULATION COOPERATION:{RESET} {result.population_cooperation_rate * 100:.1f}%\n"
    )

    wait_or_step(
        15.0,
        step=step,
        fast=fast,
        prompt="Holding on final Leaderboard. Press ENTER to exit",
    )


def main():
    parser = argparse.ArgumentParser(
        description="Episode 3: Noise & Forgiveness Interactive Terminal Demonstration"
    )
    parser.add_argument(
        "--step",
        "-s",
        action="store_true",
        help="Interactive presenter mode: wait for ENTER between acts and key scenes",
    )
    parser.add_argument(
        "--fast",
        "-f",
        action="store_true",
        help="Fast mode: run without pacing delays (for quick test/CI)",
    )
    args = parser.parse_args()

    print_banner(step=args.step, fast=args.fast)
    run_act_1_echo_spiral(step=args.step, fast=args.fast)
    run_act_2_grim_trigger(step=args.step, fast=args.fast)
    run_act_3_forgiveness(step=args.step, fast=args.fast)
    run_act_4_noisy_tournament(step=args.step, fast=args.fast)


if __name__ == "__main__":
    main()
