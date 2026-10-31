#!/usr/bin/env python3
"""Interactive ANSI terminal visualizer for Episode 10: The Cognitive Revolution (LLM Multi-Agent Societies).

Streams live pre-play natural language negotiations, private chain-of-thought rationales,
action execution, and real-time deception audits between cognitive personas in the Iterated Prisoner's Dilemma.
"""

import argparse
import time

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.cognitive import (
    CognitiveMatch,
    CognitivePersona,
    DeceptionTracker,
    NegotiationChannel,
)
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.round import Round
from the_dilemma_experiment.strategies.cognitive_strategy import (
    CognitiveStrategy,
)

# ANSI Color Codes
CYAN = "\033[96m"
MAGENTA = "\033[95m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
WHITE = "\033[97m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
RESET = "\033[0m"


def print_banner() -> None:
    """Print high-impact sci-fi header banner."""
    print(f"{CYAN}{BOLD}{'═' * 80}{RESET}")
    print(
        f"{CYAN}{BOLD}  THE DILEMMA EXPERIMENT — EPISODE 10: THE COGNITIVE REVOLUTION{RESET}"
    )
    print(
        f"{BLUE}  Natural Language Multi-Agent Negotiation & Strategic Deception Engine{RESET}"
    )
    print(f"{CYAN}{BOLD}{'═' * 80}{RESET}\n")


def make_gauge(rate: float, width: int = 14) -> str:
    """Render a visual gauge representing deception rate."""
    filled = round(rate * width)
    empty = width - filled
    color = RED if rate > 0.3 else (YELLOW if rate > 0.0 else GREEN)
    bar = "█" * filled + "░" * empty
    return f"{color}[{bar}] {rate * 100:>5.1f}%{RESET}"


def run_interactive_match(
    persona_a: CognitivePersona,
    persona_b: CognitivePersona,
    rounds: int = 10,
    delay: float = 0.5,
    step_mode: bool = False,
) -> None:
    """Execute match with real-time streaming dialogue and deception auditing."""
    strat_a = CognitiveStrategy(
        persona=persona_a,
        agent_id="Agent_Alpha",
    )
    strat_b = CognitiveStrategy(
        persona=persona_b,
        agent_id="Agent_Beta",
    )
    agent_a = Agent("Agent_Alpha", strat_a)
    agent_b = Agent("Agent_Beta", strat_b)

    channel = NegotiationChannel()
    tracker = DeceptionTracker()
    match = CognitiveMatch(
        agent_a,
        agent_b,
        round_count=rounds,
        channel=channel,
        deception_tracker=tracker,
    )

    print(
        f"{BOLD}MATCH CONFIGURATION:{RESET} {CYAN}{persona_a.value.upper()}{RESET} (Agent Alpha) vs "
        f"{MAGENTA}{persona_b.value.upper()}{RESET} (Agent Beta) | {WHITE}{rounds} Rounds{RESET}\n"
    )

    score_a = 0
    score_b = 0
    history_rounds: list[Round] = []

    for r_num in range(1, rounds + 1):
        print(f"{WHITE}{BOLD}┌── ROUND {r_num:02d} / {rounds:02d} {'─' * 63}┐{RESET}")

        # Phase 1: Dialogue Exchange
        msg_a, intent_a = strat_a.negotiate(agent_b.id, r_num, channel, history_rounds)
        channel.record_turn(r_num, agent_a.id, agent_b.id, msg_a, intent_a)

        msg_b, intent_b = strat_b.negotiate(agent_a.id, r_num, channel, history_rounds)
        channel.record_turn(r_num, agent_b.id, agent_a.id, msg_b, intent_b)

        intent_a_str = (
            f"{GREEN}PROMISE: COOPERATE{RESET}"
            if intent_a == Action.COOPERATE
            else (
                f"{RED}PROMISE: DEFECT{RESET}"
                if intent_a == Action.DEFECT
                else f"{DIM}NON-COMMITTAL{RESET}"
            )
        )
        intent_b_str = (
            f"{GREEN}PROMISE: COOPERATE{RESET}"
            if intent_b == Action.COOPERATE
            else (
                f"{RED}PROMISE: DEFECT{RESET}"
                if intent_b == Action.DEFECT
                else f"{DIM}NON-COMMITTAL{RESET}"
            )
        )

        print(f"│ {CYAN}{BOLD}[Agent Alpha 💬]:{RESET} \"{msg_a}\"")
        print(f"│   └─ {intent_a_str}")
        print(f"│ {MAGENTA}{BOLD}[Agent Beta  💬]:{RESET} \"{msg_b}\"")
        print(f"│   └─ {intent_b_str}")

        if delay > 0:
            time.sleep(delay)

        # Phase 2: Action Choice
        act_a = strat_a.choose_action(DecisionContext(opponent_id=agent_b.id))
        act_b = strat_b.choose_action(DecisionContext(opponent_id=agent_a.id))

        rat_a = strat_a.get_last_rationale(agent_b.id)
        rat_b = strat_b.get_last_rationale(agent_a.id)

        print("│")
        print(f"│ {DIM}Agent Alpha CoT:{RESET} {ITALIC}{rat_a}{RESET}")
        print(f"│ {DIM}Agent Beta  CoT:{RESET} {ITALIC}{rat_b}{RESET}")

        # Auditing
        audit_a = tracker.record_action(
            r_num, agent_a.id, agent_b.id, intent_a, act_a
        )
        audit_b = tracker.record_action(
            r_num, agent_b.id, agent_a.id, intent_b, act_b
        )

        act_a_str = (
            f"{GREEN}{BOLD}COOPERATE{RESET}"
            if act_a == Action.COOPERATE
            else f"{RED}{BOLD}DEFECT{RESET}"
        )
        act_b_str = (
            f"{GREEN}{BOLD}COOPERATE{RESET}"
            if act_b == Action.COOPERATE
            else f"{RED}{BOLD}DEFECT{RESET}"
        )

        payoff = match.game.resolve(act_a, act_b)
        score_a += payoff.first
        score_b += payoff.second

        strat_a.observe(agent_b.id, act_b)
        strat_b.observe(agent_a.id, act_a)

        history_rounds.append(
            Round(
                first_agent_id=agent_a.id,
                second_agent_id=agent_b.id,
                first_action=act_a,
                second_action=act_b,
                payoff=payoff,
            )
        )

        print("│")
        print(
            f"│ {BOLD}Decisions:{RESET} Alpha [{act_a_str}] vs Beta [{act_b_str}]  ==>  "
            f"Payoff: Alpha +{payoff.first} | Beta +{payoff.second}"
        )

        # Deception alerts
        if audit_a and audit_a.is_deceptive:
            print(
                f"│ {RED}{BOLD}🚨 DECEPTION DETECTED: Agent Alpha violated stated commitment!{RESET}"
            )
        if audit_b and audit_b.is_deceptive:
            print(
                f"│ {RED}{BOLD}🚨 DECEPTION DETECTED: Agent Beta violated stated commitment!{RESET}"
            )

        gauge_a = make_gauge(tracker.get_deception_rate(agent_a.id))
        gauge_b = make_gauge(tracker.get_deception_rate(agent_b.id))

        print(
            f"│ {BOLD}Scoreboard:{RESET} Alpha: {CYAN}{score_a} pts{RESET} (Deception: {gauge_a}) | "
            f"Beta: {MAGENTA}{score_b} pts{RESET} (Deception: {gauge_b})"
        )
        print(f"{WHITE}{BOLD}└{'─' * 78}┘{RESET}\n")

        if step_mode:
            input(f"{YELLOW}Press [Enter] for next round...{RESET}")
        elif delay > 0:
            time.sleep(delay)

    # Final Summary Table
    print(f"\n{CYAN}{BOLD}{'═' * 80}{RESET}")
    print(f"{CYAN}{BOLD}  FINAL TELEMETRY & STRATEGIC AUDIT SUMMARY{RESET}")
    print(f"{CYAN}{BOLD}{'═' * 80}{RESET}")
    print(f"  • Agent Alpha ({persona_a.value}): Final Score = {score_a} | Promises Broken = {tracker.get_broken_count(agent_a.id)} / {tracker.get_promises_count(agent_a.id)}")
    print(f"  • Agent Beta  ({persona_b.value}): Final Score = {score_b} | Promises Broken = {tracker.get_broken_count(agent_b.id)} / {tracker.get_promises_count(agent_b.id)}")

    if score_a > score_b:
        print(f"\n  {GREEN}{BOLD}🏆 OUTCOME: Agent Alpha ({persona_a.value}) triumphs!{RESET}")
    elif score_b > score_a:
        print(f"\n  {MAGENTA}{BOLD}🏆 OUTCOME: Agent Beta ({persona_b.value}) triumphs!{RESET}")
    else:
        print(f"\n  {YELLOW}{BOLD}🤝 OUTCOME: Perfect parity / mutual equilibrium!{RESET}")
    print(f"{CYAN}{BOLD}{'═' * 80}{RESET}\n")


def parse_persona(name: str) -> CognitivePersona:
    """Parse string name to CognitivePersona enum."""
    lookup = {
        "diplomat": CognitivePersona.HONEST_DIPLOMAT,
        "honest_diplomat": CognitivePersona.HONEST_DIPLOMAT,
        "machiavelli": CognitivePersona.MACHIAVELLIAN,
        "machiavellian": CognitivePersona.MACHIAVELLIAN,
        "contractor": CognitivePersona.PRAGMATIC_CONTRACTOR,
        "pragmatic_contractor": CognitivePersona.PRAGMATIC_CONTRACTOR,
        "realist": CognitivePersona.SKEPTICAL_REALIST,
        "skeptical_realist": CognitivePersona.SKEPTICAL_REALIST,
    }
    key = name.strip().lower()
    if key in lookup:
        return lookup[key]
    raise argparse.ArgumentTypeError(
        f"Unknown persona '{name}'. Choose from: diplomat, machiavelli, contractor, realist"
    )


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="The Dilemma Experiment - Episode 10: Cognitive Multi-Agent CLI"
    )
    parser.add_argument(
        "--persona-a",
        type=parse_persona,
        default=CognitivePersona.HONEST_DIPLOMAT,
        help="Persona for Agent Alpha (diplomat, machiavelli, contractor, realist)",
    )
    parser.add_argument(
        "--persona-b",
        type=parse_persona,
        default=CognitivePersona.MACHIAVELLIAN,
        help="Persona for Agent Beta (diplomat, machiavelli, contractor, realist)",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=5,
        help="Number of interaction rounds (default: 5)",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Run without animation delay",
    )
    parser.add_argument(
        "--step",
        action="store_true",
        help="Step through rounds interactively with Enter key",
    )

    args = parser.parse_args()
    print_banner()

    delay = 0.0 if args.fast else (0.0 if args.step else 0.4)
    run_interactive_match(
        persona_a=args.persona_a,
        persona_b=args.persona_b,
        rounds=args.rounds,
        delay=delay,
        step_mode=args.step,
    )


if __name__ == "__main__":
    main()
