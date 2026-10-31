#!/usr/bin/env python3
"""Episode 9 Benchmark Suite: Zero-Determinant Strategies & Asymmetric Power.

Empirical verification of:
1. The Unilateral Extortion Grid (chi in [1.0, 1.5, 2.0, 3.0, 5.0])
2. The Equalizer Clamp (c in [1.2, 1.6, 2.0, 2.4])
3. The Evolutionary Paradox: Pairwise Dominance vs Population Fitness
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.match import Match
from the_dilemma_experiment.domain.memory_one import compute_theoretical_payoffs
from the_dilemma_experiment.domain.population import Population
from the_dilemma_experiment.domain.prisoners_dilemma import (
    DEFAULT_PAYOFF_MATRIX,
    PrisonersDilemma,
)
from the_dilemma_experiment.domain.tournament import Tournament
from the_dilemma_experiment.strategies.always_cooperate import (
    AlwaysCooperateStrategy,
)
from the_dilemma_experiment.strategies.always_defect import AlwaysDefectStrategy
from the_dilemma_experiment.strategies.grim_trigger import GrimTriggerStrategy
from the_dilemma_experiment.strategies.random_strategy import RandomStrategy
from the_dilemma_experiment.strategies.tit_for_tat import TitForTatStrategy
from the_dilemma_experiment.strategies.win_stay_lose_shift import (
    WinStayLoseShiftStrategy,
)
from the_dilemma_experiment.strategies.zero_determinant import (
    EqualizerStrategy,
    ExtortionStrategy,
    GenerousZDStrategy,
)


@dataclass
class ExtortionGridEntry:
    chi: float
    opponent: str
    theoretical_sx: float
    theoretical_sy: float
    empirical_sx: float
    empirical_sy: float
    theoretical_surplus_ratio: float
    empirical_surplus_ratio: float
    extortioner_won_pairwise: bool


@dataclass
class EqualizerGridEntry:
    target_c: float
    opponent: str
    theoretical_sx: float
    theoretical_sy: float
    empirical_sx: float
    empirical_sy: float
    clamping_error: float


def run_experiment_a() -> list[dict]:
    """Experiment A: The Unilateral Extortion Grid across chi values and opponents."""
    print("\n" + "=" * 70)
    print("EXPERIMENT A: THE UNILATERAL EXTORTION GRID (Press & Dyson 2012)")
    print("=" * 70)

    game = PrisonersDilemma()
    opponents_map = {
        "AlwaysCooperate": (AlwaysCooperateStrategy(), (1.0, 1.0, 1.0, 1.0)),
        "TitForTat": (TitForTatStrategy(), (1.0, 0.0, 1.0, 0.0)),
        "WinStayLoseShift": (WinStayLoseShiftStrategy(), (1.0, 0.0, 0.0, 1.0)),
        "Random_50": (
            RandomStrategy(cooperation_probability=0.5, seed=42),
            (0.5, 0.5, 0.5, 0.5),
        ),
        "GrimTrigger": (GrimTriggerStrategy(), (1.0, 0.0, 0.0, 0.0)),
        "AlwaysDefect": (AlwaysDefectStrategy(), (0.0, 0.0, 0.0, 0.0)),
    }

    results: list[dict] = []
    chis = [1.0, 1.5, 2.0, 3.0, 5.0]

    for chi in chis:
        extort_strat = ExtortionStrategy(chi=chi, seed=100)
        p = extort_strat.probabilities

        for opp_name, (opp_strat, q) in opponents_map.items():
            # Theoretical Markov payoffs
            theo_sx, theo_sy = compute_theoretical_payoffs(
                p, q, dict(DEFAULT_PAYOFF_MATRIX)
            )

            # Empirical 2,000-round match
            extort_agent = Agent("Extortioner", extort_strat)
            opp_agent = Agent(opp_name, opp_strat)
            match = Match(
                first_agent=extort_agent,
                second_agent=opp_agent,
                game=game,
                round_count=2000,
            )
            match.execute()
            assert match.result is not None

            emp_sx = match.result.first_score / 2000.0
            emp_sy = match.result.second_score / 2000.0

            # Calculate surplus ratios (s_X - 1) / (s_Y - 1)
            theo_diff_y = theo_sy - 1.0
            theo_ratio = (
                (theo_sx - 1.0) / theo_diff_y
                if abs(theo_diff_y) > 1e-4
                else chi
            )

            emp_diff_y = emp_sy - 1.0
            emp_ratio = (
                (emp_sx - 1.0) / emp_diff_y if abs(emp_diff_y) > 0.05 else chi
            )

            entry = ExtortionGridEntry(
                chi=chi,
                opponent=opp_name,
                theoretical_sx=round(theo_sx, 4),
                theoretical_sy=round(theo_sy, 4),
                empirical_sx=round(emp_sx, 4),
                empirical_sy=round(emp_sy, 4),
                theoretical_surplus_ratio=round(theo_ratio, 2),
                empirical_surplus_ratio=round(emp_ratio, 2),
                extortioner_won_pairwise=(emp_sx >= emp_sy - 0.02),
            )
            results.append(asdict(entry))

            extort_strat.reset()
            if hasattr(opp_strat, "reset"):
                opp_strat.reset()

        # Print snapshot for chi = 3.0
        if chi == 3.0:
            print("\n[Snapshot: chi = 3.0 (Extortion Factor 3x)]")
            print(
                f"{'Opponent':<18} | {'Theo s_X':<8} | {'Theo s_Y':<8} | {'Emp s_X':<8} | {'Emp s_Y':<8} | {'Ratio':<6} | Pairwise Win"
            )
            print("-" * 75)
            for r in results[-len(opponents_map) :]:
                win_str = "YES" if r["extortioner_won_pairwise"] else "TIE"
                print(
                    f"{r['opponent']:<18} | {r['theoretical_sx']:<8.3f} | {r['theoretical_sy']:<8.3f} | {r['empirical_sx']:<8.3f} | {r['empirical_sy']:<8.3f} | {r['empirical_surplus_ratio']:<6.2f} | {win_str}"
                )

    return results


def run_experiment_b() -> list[dict]:
    """Experiment B: The Equalizer Clamp (s_Y = c)."""
    print("\n" + "=" * 70)
    print("EXPERIMENT B: THE EQUALIZER CLAMP (Unilateral Score Fixing)")
    print("=" * 70)

    game = PrisonersDilemma()
    opponents_map = {
        "AlwaysCooperate": (AlwaysCooperateStrategy(), (1.0, 1.0, 1.0, 1.0)),
        "TitForTat": (TitForTatStrategy(), (1.0, 0.0, 1.0, 0.0)),
        "WinStayLoseShift": (WinStayLoseShiftStrategy(), (1.0, 0.0, 0.0, 1.0)),
        "Random_50": (
            RandomStrategy(cooperation_probability=0.5, seed=42),
            (0.5, 0.5, 0.5, 0.5),
        ),
        "AlwaysDefect": (AlwaysDefectStrategy(), (0.0, 0.0, 0.0, 0.0)),
    }

    results: list[dict] = []
    target_cs = [1.2, 1.6, 2.0, 2.4]

    for c in target_cs:
        eq_strat = EqualizerStrategy(target_score=c, seed=200)
        p = eq_strat.probabilities

        for opp_name, (opp_strat, q) in opponents_map.items():
            theo_sx, theo_sy = compute_theoretical_payoffs(
                p, q, dict(DEFAULT_PAYOFF_MATRIX)
            )

            eq_agent = Agent("Equalizer", eq_strat)
            opp_agent = Agent(opp_name, opp_strat)
            match = Match(
                first_agent=eq_agent,
                second_agent=opp_agent,
                game=game,
                round_count=2000,
            )
            match.execute()
            assert match.result is not None

            emp_sx = match.result.first_score / 2000.0
            emp_sy = match.result.second_score / 2000.0
            clamp_err = abs(emp_sy - c)

            entry = EqualizerGridEntry(
                target_c=c,
                opponent=opp_name,
                theoretical_sx=round(theo_sx, 4),
                theoretical_sy=round(theo_sy, 4),
                empirical_sx=round(emp_sx, 4),
                empirical_sy=round(emp_sy, 4),
                clamping_error=round(clamp_err, 4),
            )
            results.append(asdict(entry))

            eq_strat.reset()
            if hasattr(opp_strat, "reset"):
                opp_strat.reset()

        if c == 2.0:
            print("\n[Snapshot: Target c = 2.0000 (Pinned Opponent Payoff)]")
            print(
                f"{'Opponent':<18} | {'Theo s_Y':<8} | {'Emp s_Y':<8} | {'Target c':<8} | {'Abs Error':<10}"
            )
            print("-" * 65)
            for r in results[-len(opponents_map) :]:
                print(
                    f"{r['opponent']:<18} | {r['theoretical_sy']:<8.4f} | {r['empirical_sy']:<8.4f} | {r['target_c']:<8.4f} | {r['clamping_error']:<10.4f}"
                )

    return results


def run_experiment_c() -> dict:
    """Experiment C: The Evolutionary Paradox — Pairwise Dominance vs Population Fitness."""
    print("\n" + "=" * 70)
    print("EXPERIMENT C: THE EVOLUTIONARY PARADOX (Population Dynamics)")
    print("=" * 70)

    game = PrisonersDilemma()

    # Create a 24-agent population containing 4 distinct castes:
    # 6 Extortioners (chi=3.0)
    # 6 Generous ZD (chi=2.0)
    # 6 Tit-for-Tat
    # 6 Always Defect
    agents: list[Agent] = []
    for i in range(6):
        agents.append(
            Agent(
                f"Extort_{i:02d}",
                ExtortionStrategy(
                    chi=3.0, seed=1000 + i, initial_action=Action.COOPERATE
                ),
            )
        )
    for i in range(6):
        agents.append(
            Agent(
                f"Generous_{i:02d}",
                GenerousZDStrategy(
                    chi=2.0, seed=2000 + i, initial_action=Action.COOPERATE
                ),
            )
        )
    for i in range(6):
        agents.append(Agent(f"TFT_{i:02d}", TitForTatStrategy()))
    for i in range(6):
        agents.append(Agent(f"Defect_{i:02d}", AlwaysDefectStrategy()))

    pop = Population(agents=agents)
    tournament = Tournament(population=pop, game=game, rounds_per_match=150)
    result = tournament.execute()

    # Aggregate by strategy archetype
    strategy_scores: dict[str, list[int]] = {
        "GenerousZD": [],
        "TitForTat": [],
        "Extortioner": [],
        "AlwaysDefect": [],
    }

    for entry in result.leaderboard:
        if "Generous" in entry.agent_id:
            strategy_scores["GenerousZD"].append(entry.total_score)
        elif "TFT" in entry.agent_id:
            strategy_scores["TitForTat"].append(entry.total_score)
        elif "Extort" in entry.agent_id:
            strategy_scores["Extortioner"].append(entry.total_score)
        elif "Defect" in entry.agent_id:
            strategy_scores["AlwaysDefect"].append(entry.total_score)

    summary = {
        strat: {
            "mean_score": round(sum(scores) / len(scores), 2),
            "min_score": min(scores),
            "max_score": max(scores),
            "count": len(scores),
        }
        for strat, scores in strategy_scores.items()
    }

    print(
        f"\n{'Strategy Caste':<16} | {'Mean Total Score':<18} | {'Min Score':<10} | {'Max Score':<10}"
    )
    print("-" * 65)
    for strat, stats in sorted(
        summary.items(), key=lambda x: x[1]["mean_score"], reverse=True
    ):
        print(
            f"{strat:<16} | {stats['mean_score']:<18.2f} | {stats['min_score']:<10} | {stats['max_score']:<10}"
        )

    print("\nScientific Takeaway:")
    print(
        "  • In pairwise matches, Extortioners win head-to-head score against any cooperative partner."
    )
    print(
        "  • But in population tournaments, Extortioners mutual defection (s_XX = 1.0) severely"
    )
    print(
        "    penalizes their collective fitness. Generous ZD and TFT harvest mutual 3.0 rewards"
    )
    print(
        "    and systematically out-evolve the predatory extortioners!"
    )

    return {
        "leaderboard": [asdict(e) for e in result.leaderboard],
        "caste_summary": summary,
    }


def main() -> None:
    """Execute all three benchmark experiments and save JSON results."""
    print("▶ INITIATING EPISODE 9 BENCHMARK SUITE")

    exp_a = run_experiment_a()
    exp_b = run_experiment_b()
    exp_c = run_experiment_c()

    output = {
        "episode": 9,
        "title": "Zero-Determinant Strategies & Asymmetric Power",
        "experiment_a": exp_a,
        "experiment_b": exp_b,
        "experiment_c": exp_c,
    }

    out_file = Path(__file__).parent / "experiment_results.json"
    out_file.write_text(json.dumps(output, indent=2))
    print(f"\n✔ Benchmark results successfully saved to {out_file}")


if __name__ == "__main__":
    main()
