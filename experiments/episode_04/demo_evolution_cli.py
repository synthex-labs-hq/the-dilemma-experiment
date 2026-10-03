#!/usr/bin/env python3
"""Cinematic Interactive Terminal Demonstration for Episode 4: Natural Selection & Replicator Dynamics.

Pre-calibrated to synchronize with the voiceover narration timeline from video_script_master.md:
1. Act I: The Altruist-Predator Boom & Bust (The Ecological Tragedy)
2. Act II: The Invasion Barrier & Critical Mass (2% failure vs 20% critical mass takeover)
3. Act III: The 8-Archetype Arena under 5% Noise (Generational population shifts)
4. Act IV: The Evolutionary Verdict (Evolutionarily Stable Strategies - ESS)

Usage:
    # Calibrated script pacing (default - holds at each act for voiceover):
    uv run python experiments/episode_04/demo_evolution_cli.py

    # Presenter step mode (press ENTER to advance between acts/generations):
    uv run python experiments/episode_04/demo_evolution_cli.py --step

    # Fast mode (quick testing / CI without delays):
    uv run python experiments/episode_04/demo_evolution_cli.py --fast
"""

import argparse
import sys
import time

from the_dilemma_experiment.domain.evolutionary_tournament import (
    EvolutionaryTournament,
)
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

# ANSI Colors & Formatting
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


def render_bar(share: float, width: int = 30, color: str = CYAN) -> str:
    """Render a colored ASCII proportion bar."""
    filled = round(share * width)
    empty = width - filled
    return f"{color}{'█' * filled}{DIM}{'░' * empty}{RESET}"


def print_banner(step: bool = False, fast: bool = False):
    banner = f"""{MAGENTA}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   ███████╗██╗   ██╗ ██████╗ ██╗     ██╗   ██╗████████╗██╗ ██████╗    ║
║   ██╔════╝██║   ██║██╔═══██╗██║     ██║   ██║╚══██╔══╝██║██╔═══██╗   ║
║   █████╗  ██║   ██║██║   ██║██║     ██║   ██║   ██║   ██║██║   ██║   ║
║   ██╔══╝  ╚██╗ ██╔╝██║   ██║██║     ██║   ██║   ██║   ██║██║   ██║   ║
║   ███████╗ ╚████╔╝ ╚██████╔╝███████╗╚██████╔╝   ██║   ██║╚██████╔╝   ║
║   ╚══════╝  ╚═══╝   ╚═════╝ ╚══════╝ ╚═════╝    ╚═╝   ╚═╝ ╚═════╝    ║
║                                                                      ║
║           NATURAL SELECTION & REPLICATOR DYNAMICS                    ║
║                  EPISODE 4 — SIMULATION ARENA                        ║
╚══════════════════════════════════════════════════════════════════════╝{RESET}"""
    print(banner)
    wait_or_step(3.0, step=step, fast=fast, prompt="Ready to start Act I")


def run_act_1_boom_and_bust(step: bool = False, fast: bool = False):
    print(f"\n{BOLD}{CYAN}══ ACT I: THE ALTRUIST-PREDATOR BOOM & BUST (The Ecological Tragedy) ══{RESET}")
    slow_print(
        f"{DIM}50 Altruists (Always Cooperate) meet 50 Predators (Always Defect).{RESET}",
        0.008,
        fast=fast,
    )
    slow_print(
        f"{DIM}Watch what happens when successful strategies reproduce and unsuccessful ones starve.{RESET}",
        0.008,
        fast=fast,
    )
    wait_or_step(2.5, step=step, fast=fast)

    evo = EvolutionaryTournament(
        initial_population={
            AlwaysCooperateStrategy: 50,
            AlwaysDefectStrategy: 50,
        },
        rounds_per_match=10,
        noise=0.0,
        seed=42,
    )

    print(f"\n{'GEN':<4} | {'STRATEGY ARCHETYPE':<22} | {'POP':<5} | {'SHARE':<6} | {'DEMOGRAPHIC BAR':<38} | {'FITNESS'}")
    print("-" * 92)

    for gen in range(6):
        res = evo.step()
        c_allc = res.population_counts.get("AlwaysCooperateStrategy", 0)
        c_alld = res.population_counts.get("AlwaysDefectStrategy", 0)
        s_allc = res.population_shares.get("AlwaysCooperateStrategy", 0.0)
        s_alld = res.population_shares.get("AlwaysDefectStrategy", 0.0)
        f_allc = res.average_fitness.get("AlwaysCooperateStrategy", 0.0)
        f_alld = res.average_fitness.get("AlwaysDefectStrategy", 0.0)

        # Print Altruist line
        bar_c = render_bar(s_allc, width=28, color=CYAN)
        print(f"G{gen:<3} | {CYAN}{'Always Cooperate (Altruist)':<22}{RESET} | {c_allc:<5} | {s_allc:>5.1%} | {bar_c} | {f_allc:>7.1f} pts")

        # Print Predator line
        bar_d = render_bar(s_alld, width=28, color=RED)
        print(f"     | {RED}{'Always Defect (Predator)':<22}{RESET} | {c_alld:<5} | {s_alld:>5.1%} | {bar_d} | {f_alld:>7.1f} pts")

        if res.newly_extinct:
            for extinct in res.newly_extinct:
                print(f"     {RED}{BOLD}⚡ EXTINCTION ALERT: {extinct} has collapsed to 0!{RESET}")

        print(f"     {DIM}↳ Population Mean Fitness: {res.mean_population_fitness:.1f} pts/agent{RESET}")
        print("-" * 92)

        wait_or_step(2.0, step=step, fast=fast, prompt=f"Advance to Generation {gen + 1}")

    slow_print(
        f"\n{YELLOW}{BOLD}[THE TAKEAWAY]{RESET} {YELLOW}Naive altruism feeds predators. Predators explode, altruists die out. Once prey is gone, predators starve on mutual defection (1 pt/round).{RESET}\n",
        0.008,
        fast=fast,
    )
    wait_or_step(3.5, step=step, fast=fast, prompt="Advance to Act II")


def run_act_2_invasion_barrier(step: bool = False, fast: bool = False):
    print(f"\n{BOLD}{CYAN}══ ACT II: THE INVASION BARRIER & CRITICAL MASS ══{RESET}")
    slow_print(
        f"{DIM}Can reciprocal trust (Tit-for-Tat) invade a world of 100% selfish defectors?{RESET}",
        0.008,
        fast=fast,
    )
    wait_or_step(2.0, step=step, fast=fast)

    # Part 1: Sub-critical threshold (2% TFT)
    print(f"\n{BOLD}[SCENARIO A: 2% Isolated Infiltrators — Below Critical Mass]{RESET}")
    slow_print(f"{DIM}2 Tit-for-Tat agents enter 98 Always Defect agents.{RESET}", 0.008, fast=fast)

    evo1 = EvolutionaryTournament(
        initial_population={AlwaysDefectStrategy: 98, TitForTatStrategy: 2},
        rounds_per_match=10,
        noise=0.0,
        seed=42,
    )
    res1 = evo1.step()
    c_tft = res1.population_counts.get("TitForTatStrategy", 0)
    c_alld = res1.population_counts.get("AlwaysDefectStrategy", 0)
    print(f"Gen 0: TFT={c_tft} (2.0%) | AllD={c_alld} (98.0%)")
    print(f" -> TFT Fitness: {res1.average_fitness.get('TitForTatStrategy', 0.0):.1f} pts | AllD Fitness: {res1.average_fitness.get('AlwaysDefectStrategy', 0.0):.1f} pts")
    print(f" -> {RED}RESULT: TFT suffers sucker payoff on Round 1. Isolated cooperators cannot survive.{RESET}")

    wait_or_step(2.5, step=step, fast=fast, prompt="Ready for Scenario B (Clustered Threshold)")

    # Part 2: Super-critical threshold (20% TFT cluster)
    print(f"\n{BOLD}[SCENARIO B: 20% Clustered Infiltrators — Above Critical Mass]{RESET}")
    slow_print(f"{DIM}20 Tit-for-Tat agents enter 80 Always Defect agents. They interact with each other!{RESET}", 0.008, fast=fast)

    evo2 = EvolutionaryTournament(
        initial_population={AlwaysDefectStrategy: 80, TitForTatStrategy: 20},
        rounds_per_match=10,
        noise=0.0,
        seed=42,
    )

    print(f"\n{'GEN':<4} | {'TIT-FOR-TAT (COOPERATIVE)':<28} | {'ALWAYS DEFECT (PREDATOR)':<28}")
    print("-" * 68)

    for gen in range(11):
        res = evo2.step()
        c_tft = res.population_counts.get("TitForTatStrategy", 0)
        c_alld = res.population_counts.get("AlwaysDefectStrategy", 0)
        bar_tft = render_bar(c_tft / 100.0, width=16, color=CYAN)
        bar_alld = render_bar(c_alld / 100.0, width=16, color=RED)

        print(f"G{gen:<3} | {c_tft:>3} ({c_tft/100:>5.1%}) {bar_tft} | {c_alld:>3} ({c_alld/100:>5.1%}) {bar_alld}")

        if evo2.is_converged and c_alld == 0:
            print(f"\n{GREEN}{BOLD}⚡ COMPLETE CONQUEST: Always Defect driven to 0% EXTINCTION!{RESET}")
            break

        wait_or_step(1.2, step=step, fast=fast)

    slow_print(
        f"\n{GREEN}{BOLD}[THE TAKEAWAY]{RESET} {GREEN}Trust cannot invade alone. But when a small cluster of cooperators support each other, mutual cooperation explodes and drives predators extinct.{RESET}\n",
        0.008,
        fast=fast,
    )
    wait_or_step(3.5, step=step, fast=fast, prompt="Advance to Act III")


def run_act_3_8_archetype_arena(step: bool = False, fast: bool = False):
    print(f"\n{BOLD}{CYAN}══ ACT III: THE 8-ARCHETYPE ARENA UNDER 5% NOISE ══{RESET}")
    slow_print(
        f"{DIM}All 8 archetypes enter an evolutionary battlefield with a 5% communication error rate.{RESET}",
        0.008,
        fast=fast,
    )
    slow_print(
        f"{DIM}Who survives? Brittle legalists, exploiters, or forgiving cooperators?{RESET}",
        0.008,
        fast=fast,
    )
    wait_or_step(2.5, step=step, fast=fast)

    init_pop = {
        AlwaysCooperateStrategy: 12,
        AlwaysDefectStrategy: 13,
        TitForTatStrategy: 12,
        GrimTriggerStrategy: 12,
        (lambda: RandomStrategy(cooperation_probability=0.5, seed=42)): 12,
        (lambda: GenerousTitForTatStrategy(forgiveness_probability=0.33, seed=43)): 13,
        TitForTwoTatsStrategy: 12,
        WinStayLoseShiftStrategy: 12,
    }

    evo = EvolutionaryTournament(
        initial_population=init_pop,
        rounds_per_match=15,
        noise=0.05,
        seed=42,
    )

    checkpoints = [0, 2, 5, 10, 15, 20, 25]

    for gen in range(26):
        res = evo.step()
        if gen in checkpoints:
            print(f"\n{BOLD}{MAGENTA}── GENERATION {gen:02d} STATUS ──{RESET}")
            # Sort strategies by count descending
            sorted_strats = sorted(
                res.population_counts.items(),
                key=lambda x: -x[1],
            )
            for strat, count in sorted_strats:
                share = count / res.total_population
                # Color code
                if "Generous" in strat or "TwoTats" in strat or "WinStay" in strat:
                    color = GREEN
                elif "Defect" in strat or "Random" in strat:
                    color = RED
                elif "Grim" in strat:
                    color = AMBER
                else:
                    color = CYAN

                bar = render_bar(share, width=22, color=color)
                fit = res.average_fitness.get(strat, 0.0)
                print(f"  {color}{strat:<26}{RESET} | {count:>2} agents ({share:>5.1%}) | {bar} | {fit:>6.1f} pts")

            wait_or_step(2.5, step=step, fast=fast, prompt=f"Advance from Gen {gen}")

    wait_or_step(3.0, step=step, fast=fast, prompt="Advance to Act IV: Verdict")


def run_act_4_verdict(step: bool = False, fast: bool = False):
    print(f"\n{BOLD}{CYAN}══ ACT IV: THE EVOLUTIONARY VERDICT & ESS ══{RESET}")
    print(f"""
{WHITE}{BOLD}┌────────────────────────────────────────────────────────────────────────┐
│                      FINAL EVOLUTIONARY TAKEAWAYS                      │
├────────────────────────────────────────────────────────────────────────┤
│ 1. {CYAN}NAIVE ALTRUISM IS NOT AN ESS{WHITE}                                       │
│    Unconditional cooperation feeds predators. It creates its own       │
│    demographic collapse.                                               │
│                                                                        │
│ 2. {RED}EXPLOITATION BURNS ITS OWN BRIDGE{WHITE}                                   │
│    Predators multiply until victims are extinct, then starve on mutual  │
│    distrust. Pure selfishness is ecologically self-defeating.          │
│                                                                        │
│ 3. {AMBER}THE INVASION THRESHOLD{WHITE}                                              │
│    A single good guy in a bad neighborhood perishes. But a cluster     │
│    of reciprocal agents conquers the world.                            │
│                                                                        │
│ 4. {GREEN}FORGIVENESS IS THE ONLY STABLE EQUILIBRIUM (ESS){WHITE}                     │
│    In noisy environments, zero-tolerance dies. The strategies that    │
│    survive natural selection are: Clear, Retaliatory, and Forgiving.   │
└────────────────────────────────────────────────────────────────────────┘{RESET}
""")
    wait_or_step(2.0, step=step, fast=fast)


def main():
    parser = argparse.ArgumentParser(
        description="Interactive Terminal Demo for Episode 4: Natural Selection & Evolution"
    )
    parser.add_argument(
        "--step",
        action="store_true",
        help="Interactive presenter mode (press ENTER to advance between scenes)",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Fast mode without pauses (for testing / CI)",
    )
    args = parser.parse_args()

    print_banner(step=args.step, fast=args.fast)
    run_act_1_boom_and_bust(step=args.step, fast=args.fast)
    run_act_2_invasion_barrier(step=args.step, fast=args.fast)
    run_act_3_8_archetype_arena(step=args.step, fast=args.fast)
    run_act_4_verdict(step=args.step, fast=args.fast)


if __name__ == "__main__":
    main()
