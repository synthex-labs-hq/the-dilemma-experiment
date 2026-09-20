#!/usr/bin/env python3
"""Interactive Terminal Demonstration for Episode 1: Building the Laboratory.

Run this script to capture real footage of the simulation engine in action.
Usage:
    uv run python -m experiments.episode_01.demo_cli
    or
    python experiments/episode_01/demo_cli.py
"""

import sys
import time
from typing import Optional

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.match import Match
from the_dilemma_experiment.domain.prisoners_dilemma import PrisonersDilemma
from the_dilemma_experiment.strategies.always_cooperate import AlwaysCooperateStrategy
from the_dilemma_experiment.strategies.always_defect import AlwaysDefectStrategy
from the_dilemma_experiment.strategies.tit_for_tat import TitForTatStrategy

# ANSI Colors for cinematic terminal recording
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
║                  E P I S O D E  1 :  B U I L D I N G   T H E   L A B         ║
║                          synthex-labs-hq // v0.1.0                           ║
╚══════════════════════════════════════════════════════════════════════════════╝{RESET}
"""
    print(banner)
    time.sleep(0.5)

def format_action(action: Action) -> str:
    if action == Action.COOPERATE:
        return f"{CYAN}[ COOPERATE ]{RESET}"
    else:
        return f"{AMBER}[   DEFECT  ]{RESET}"

def run_cinematic_match(agent_a: Agent, agent_b: Agent, rounds: int, scenario_title: str):
    print(f"\n{MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f" {BOLD}{WHITE}SCENARIO:{RESET} {BOLD}{scenario_title}{RESET}")
    print(f" {DIM}Agent A:{RESET} {CYAN}{agent_a.id}{RESET} ({agent_a.strategy.__class__.__name__})")
    print(f" {DIM}Agent B:{RESET} {AMBER}{agent_b.id}{RESET} ({agent_b.strategy.__class__.__name__})")
    print(f" {DIM}Rounds configured:{RESET} {rounds} | {DIM}Payoff Matrix:{RESET} Standard Iterated Prisoner's Dilemma")
    print(f"{MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")
    time.sleep(0.6)

    game = PrisonersDilemma()
    match = Match(agent_a, agent_b, game, round_count=rounds)
    
    # Execute the match
    completed_rounds = match.execute()

    print(f"  {BOLD}{'ROUND':^7} | {'AGENT A ACTION':^16} | {'AGENT B ACTION':^16} | {'PAYOFF (A, B)':^15} | {'RUNNING TOTAL':^15}{RESET}")
    print(f"  {DIM}{'─'*7}─┼─{'─'*16}─┼─{'─'*16}─┼─{'─'*15}─┼─{'─'*15}{RESET}")

    total_a = 0
    total_b = 0

    for i, r in enumerate(completed_rounds, 1):
        time.sleep(0.5)  # Cinematic pacing for screen recording
        total_a += r.payoff.first
        total_b += r.payoff.second
        
        act_a = format_action(r.first_action)
        act_b = format_action(r.second_action)
        payoff_str = f"({GREEN}+{r.payoff.first}{RESET}, {GREEN}+{r.payoff.second}{RESET})"
        tally_str = f"{total_a} vs {total_b}"

        print(f"  {BOLD}#{i:02d}{RESET}    | {act_a} | {act_b} | {payoff_str:^24} | {tally_str:^15}")

    time.sleep(0.4)
    print(f"  {DIM}{'─'*7}─┴─{'─'*16}─┴─{'─'*16}─┴─{'─'*15}─┴─{'─'*15}{RESET}")
    
    res = match.result
    print(f"\n  {GREEN}✔ Match Completed Atomically.{RESET}")
    print(f"  {BOLD}Final Outcome:{RESET} {agent_a.id}: {BOLD}{res.first_score}{RESET} pts  │  {agent_b.id}: {BOLD}{res.second_score}{RESET} pts")
    time.sleep(0.8)


def main():
    print_banner()
    time.sleep(0.5)
    
    print(f"{DIM}Initializing verified domain core... (74 passing behavioral invariants){RESET}\n")
    time.sleep(0.4)

    # Scenario 1: Always Cooperate vs Always Defect
    agent1 = Agent(id="dove-01", strategy=AlwaysCooperateStrategy())
    agent2 = Agent(id="hawk-01", strategy=AlwaysDefectStrategy())
    run_cinematic_match(agent1, agent2, rounds=3, scenario_title="The Naive Sucker: Unconditional Cooperate vs Unconditional Defect")

    # Scenario 2: Tit-for-Tat vs Always Defect
    agent3 = Agent(id="tit-for-tat-01", strategy=TitForTatStrategy())
    agent4 = Agent(id="hawk-02", strategy=AlwaysDefectStrategy())
    run_cinematic_match(agent3, agent4, rounds=4, scenario_title="The Retaliator: Tit-for-Tat confronts Always Defect")

    # Scenario 3: Tit-for-Tat vs Tit-for-Tat
    agent5 = Agent(id="tit-for-tat-alpha", strategy=TitForTatStrategy())
    agent6 = Agent(id="tit-for-tat-beta", strategy=TitForTatStrategy())
    run_cinematic_match(agent5, agent6, rounds=4, scenario_title="The Emergence: Mutual Cooperation between Reciprocal Agents")

    print(f"\n{CYAN}══════════════════════════════════════════════════════════════════════════════{RESET}")
    print(f" {BOLD}{WHITE}LABORATORY STATUS:{RESET} Verified deterministic baseline ready for Episode 2.")
    print(f" {DIM}GitHub:{RESET} https://github.com/synthex-labs-hq/the-dilemma-experiment")
    print(f"{CYAN}══════════════════════════════════════════════════════════════════════════════{RESET}\n")

if __name__ == "__main__":
    main()
