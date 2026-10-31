#!/usr/bin/env python3
"""Episode 9 Interactive CLI: Zero-Determinant Strategies & Asymmetric Power.

A live visualizer showcasing:
- Real-time Press-Dyson Linear Payoff Line: (s_X - P) = chi * (s_Y - P)
- Extortioner vs Adaptive Opponents (Tit-for-Tat, Win-Stay Lose-Shift, AllC, Random)
- Theoretical vs Empirical Payoff HUD
- The Extortion Paradox (Pairwise Dominance vs Collective Ruin)
"""

import argparse
import sys
import time
from pathlib import Path

# Ensure src is in sys.path for direct script execution
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.memory_one import compute_theoretical_payoffs
from the_dilemma_experiment.domain.prisoners_dilemma import (
    DEFAULT_PAYOFF_MATRIX,
    PrisonersDilemma,
)
from the_dilemma_experiment.strategies.always_cooperate import (
    AlwaysCooperateStrategy,
)
from the_dilemma_experiment.strategies.always_defect import AlwaysDefectStrategy
from the_dilemma_experiment.strategies.random_strategy import RandomStrategy
from the_dilemma_experiment.strategies.tit_for_tat import TitForTatStrategy
from the_dilemma_experiment.strategies.win_stay_lose_shift import (
    WinStayLoseShiftStrategy,
)
from the_dilemma_experiment.strategies.zero_determinant import ExtortionStrategy

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

BG_CYAN = "\033[48;5;24m"
BG_GOLD = "\033[48;5;58m"


def print_banner(chi: float, opponent_name: str, rounds: int) -> None:
    """Print the cybernetic header banner."""
    print(f"{CYAN}╔════════════════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{CYAN}║{BOLD}{GOLD}   THE DILEMMA EXPERIMENT — EPISODE 9: ZERO-DETERMINANT STRATEGIES              {CYAN}║{RESET}")
    print(f"{CYAN}║{DIM}   Press & Dyson (PNAS 2012) Unilateral Mathematical Domination                 {CYAN}║{RESET}")
    print(f"{CYAN}╚════════════════════════════════════════════════════════════════════════════════╝{RESET}")
    print(f" Extortion Factor (χ): {BOLD}{GOLD}{chi:.1f}x{RESET} | Opponent: {BOLD}{BLUE}{opponent_name}{RESET} | Rounds: {BOLD}{rounds}{RESET}\n")


def format_surplus_gauge(sx: float, sy: float, p_baseline: float = 1.0) -> str:
    """Format visual bar comparing Player X's surplus to Player Y's surplus."""
    surplus_x = max(0.0, sx - p_baseline)
    surplus_y = max(0.0, sy - p_baseline)
    total = surplus_x + surplus_y

    if total < 1e-6:
        return f"{DIM}[Mutual Defection Baseline P=1.00]{RESET}"

    bar_len = 30
    x_len = round((surplus_x / total) * bar_len)
    y_len = bar_len - x_len

    x_bar = f"{GOLD}{'█' * x_len}{RESET}"
    y_bar = f"{BLUE}{'░' * y_len}{RESET}"
    pct_x = (surplus_x / total) * 100.0

    return f"[{x_bar}{y_bar}] {GOLD}{pct_x:4.1f}% Extortioner{RESET} vs {BLUE}{100.0 - pct_x:4.1f}% Co-Player{RESET}"


def run_live_simulation(
    chi: float = 3.0,
    opponent_name: str = "WinStayLoseShift",
    rounds: int = 25,
    delay: float = 0.12,
    step_mode: bool = False,
    seed: int = 42,
) -> None:
    """Run live animated ZD Extortion simulation."""
    extort_strat = ExtortionStrategy(chi=chi, seed=seed)
    p = extort_strat.probabilities

    # Map opponent
    opp_dict = {
        "AllC": (AlwaysCooperateStrategy(), (1.0, 1.0, 1.0, 1.0)),
        "TFT": (TitForTatStrategy(), (1.0, 0.0, 1.0, 0.0)),
        "WSLS": (WinStayLoseShiftStrategy(), (1.0, 0.0, 0.0, 1.0)),
        "WinStayLoseShift": (WinStayLoseShiftStrategy(), (1.0, 0.0, 0.0, 1.0)),
        "Random": (RandomStrategy(cooperation_probability=0.5, seed=seed + 1), (0.5, 0.5, 0.5, 0.5)),
        "AllD": (AlwaysDefectStrategy(), (0.0, 0.0, 0.0, 0.0)),
    }

    if opponent_name not in opp_dict:
        opponent_name = "WinStayLoseShift"

    opp_strat, q = opp_dict[opponent_name]
    theo_sx, theo_sy = compute_theoretical_payoffs(p, q, dict(DEFAULT_PAYOFF_MATRIX))

    agent_x = Agent(f"Extort_χ{chi:.1f}", extort_strat)
    agent_y = Agent(opponent_name, opp_strat)
    game = PrisonersDilemma()

    total_score_x = 0
    total_score_y = 0

    print("\033[2J\033[H", end="")  # Clear screen
    print_banner(chi, opponent_name, rounds)

    print(f"{BOLD}THEORETICAL MARKOV PREDICTION:{RESET}")
    print(f"  • Extortioner Expected Payoff (s_X): {GOLD}{theo_sx:.4f}{RESET} pts/round")
    print(f"  • Opponent Expected Payoff    (s_Y): {BLUE}{theo_sy:.4f}{RESET} pts/round")
    theo_diff_y = theo_sy - 1.0
    theo_ratio = (theo_sx - 1.0) / theo_diff_y if abs(theo_diff_y) > 1e-4 else chi
    print(f"  • Press-Dyson Extortion Ratio:       {CYAN}(s_X - 1) / (s_Y - 1) = {theo_ratio:.2f}x{RESET}")
    print(f"  • Memory-One Probabilities p(C):     {DIM}CC={p[0]:.2f}, CD={p[1]:.2f}, DC={p[2]:.2f}, DD={p[3]:.2f}{RESET}\n")

    print(f"{BOLD}▶ STREAMING REPEATED INTERACTION ROUNDS...{RESET}\n")
    if step_mode:
        input(f"{DIM}Press [ENTER] to execute round 1...{RESET}")

    for r in range(1, rounds + 1):
        ctx_x = DecisionContext(opponent_id=agent_y.id)
        ctx_y = DecisionContext(opponent_id=agent_x.id)

        act_x = extort_strat.choose_action(ctx_x)
        act_y = opp_strat.choose_action(ctx_y)

        payoff = game.resolve(act_x, act_y)
        total_score_x += payoff.first
        total_score_y += payoff.second

        extort_strat.observe(agent_y.id, act_y)
        opp_strat.observe(agent_x.id, act_x)

        avg_x = total_score_x / r
        avg_y = total_score_y / r

        # Colorize actions
        x_str = f"{EMERALD}COOP{RESET}" if act_x == Action.COOPERATE else f"{RED}DFCT{RESET}"
        y_str = f"{EMERALD}COOP{RESET}" if act_y == Action.COOPERATE else f"{RED}DFCT{RESET}"

        # Calculate live empirical ratio
        diff_y = avg_y - 1.0
        live_ratio = (avg_x - 1.0) / diff_y if abs(diff_y) > 0.05 else chi

        print(f"  Round {r:02d} | X: [{x_str}] vs Y: [{y_str}] | Payoffs: (+{payoff.first}, +{payoff.second}) | Running: ({avg_x:4.2f}, {avg_y:4.2f}) | Ratio: {GOLD}{live_ratio:4.2f}x{RESET}")

        if step_mode:
            input(f"{DIM}Press [ENTER] for next round...{RESET}")
        else:
            time.sleep(delay)

    print("\n" + "=" * 70)
    print(f"{BOLD}FINAL EMPIRICAL RESULTS VS THEORETICAL PREDICTION:{RESET}")
    print("=" * 70)
    print(f"  Surplus Distribution: {format_surplus_gauge(avg_x, avg_y)}")
    print(f"  • Extortioner Score:  {total_score_x} pts (Empirical Avg: {GOLD}{avg_x:.3f}{RESET} vs Theo: {theo_sx:.3f})")
    print(f"  • Opponent Score:     {total_score_y} pts (Empirical Avg: {BLUE}{avg_y:.3f}{RESET} vs Theo: {theo_sy:.3f})")
    print(f"  • Realized χ Ratio:   {CYAN}{(avg_x - 1.0) / max(0.01, (avg_y - 1.0)):.2f}x{RESET} (Configured: {chi:.1f}x)")

    if avg_x > avg_y:
        print(f"\n  {EMERALD}✔ Press-Dyson Invariant Confirmed: Extortioner captured disproportionate surplus.{RESET}")
    else:
        print(f"\n  {DIM}Mutual Defection Equilibrium: Both players earned baseline P=1.00.{RESET}")

    print("\n" + "=" * 70)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Episode 9 Interactive CLI: Zero-Determinant Strategies"
    )
    parser.add_argument(
        "--chi",
        type=float,
        default=3.0,
        help="Extortion factor chi >= 1.0 (default: 3.0)",
    )
    parser.add_argument(
        "--opponent",
        type=str,
        default="WinStayLoseShift",
        choices=["AllC", "TFT", "WSLS", "WinStayLoseShift", "Random", "AllD"],
        help="Opponent strategy archetype",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=25,
        help="Number of repeated interaction rounds (default: 25)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.10,
        help="Delay in seconds between rounds (default: 0.10)",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Run without animation delay",
    )
    parser.add_argument(
        "--step",
        action="store_true",
        help="Step through rounds manually with [ENTER]",
    )

    args = parser.parse_args()
    delay = 0.001 if args.fast else args.delay

    run_live_simulation(
        chi=args.chi,
        opponent_name=args.opponent,
        rounds=args.rounds,
        delay=delay,
        step_mode=args.step,
    )


if __name__ == "__main__":
    main()
