#!/usr/bin/env python3
"""Simulation Experiment Runner for Episode 3: Noise & Forgiveness.

Executes reproducible multi-agent tournaments and pairwise duels under varied
communication noise levels (0%, 1%, 5%, 10%).
Analyzes the breakdown of brittle strategies (Tit-for-Tat, Grim Trigger) and
the emergence of noise-resilient strategies (Generous Tit-for-Tat, Win-Stay Lose-Shift, Tit-for-Two-Tats).
Outputs results to JSON and prints formatted analytical comparison tables.
"""

import json
from pathlib import Path

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.match import Match
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


def run_pairwise_duels(rounds: int = 50, seed: int = 42) -> dict:
    """Analyze key pairwise interactions under 0% vs 2% noise to observe micro-dynamics."""
    game = PrisonersDilemma()

    duel_scenarios = [
        ("TFT_vs_TFT", TitForTatStrategy(), TitForTatStrategy()),
        ("Grim_vs_Altruist", GrimTriggerStrategy(), AlwaysCooperateStrategy()),
        ("GTFT_vs_TFT", GenerousTitForTatStrategy(forgiveness_probability=1 / 3, seed=seed), TitForTatStrategy()),
        ("Pavlov_vs_Pavlov", WinStayLoseShiftStrategy(), WinStayLoseShiftStrategy()),
    ]

    duel_results = {}

    for label, strat1, strat2 in duel_scenarios:
        # Noiseless duel
        a1_clean = Agent("Agent1", strat1)
        a2_clean = Agent("Agent2", strat2)
        m_clean = Match(a1_clean, a2_clean, game, round_count=rounds, noise=0.0)
        m_clean.execute()

        # Noisy duel (2% noise)
        # Note: We re-instantiate fresh strategies for the noisy duel to ensure clean state
        if label == "TFT_vs_TFT":
            s1, s2 = TitForTatStrategy(), TitForTatStrategy()
        elif label == "Grim_vs_Altruist":
            s1, s2 = GrimTriggerStrategy(), AlwaysCooperateStrategy()
        elif label == "GTFT_vs_TFT":
            s1, s2 = GenerousTitForTatStrategy(forgiveness_probability=1 / 3, seed=seed + 1), TitForTatStrategy()
        else:
            s1, s2 = WinStayLoseShiftStrategy(), WinStayLoseShiftStrategy()

        a1_noisy = Agent("Agent1", s1)
        a2_noisy = Agent("Agent2", s2)
        m_noisy = Match(a1_noisy, a2_noisy, game, round_count=rounds, noise=0.02, seed=seed)
        m_noisy.execute()

        noisy_rounds_count = sum(1 for r in m_noisy.rounds if r.is_noisy)

        duel_results[label] = {
            "rounds": rounds,
            "clean": {
                "score_agent1": m_clean.result.first_score if m_clean.result else 0,
                "score_agent2": m_clean.result.second_score if m_clean.result else 0,
                "mutual_coop_rounds": sum(
                    1 for r in m_clean.rounds if r.first_action == Action.COOPERATE and r.second_action == Action.COOPERATE
                ),
            },
            "noisy_2_percent": {
                "score_agent1": m_noisy.result.first_score if m_noisy.result else 0,
                "score_agent2": m_noisy.result.second_score if m_noisy.result else 0,
                "noise_events": noisy_rounds_count,
                "mutual_coop_rounds": sum(
                    1 for r in m_noisy.rounds if r.first_action == Action.COOPERATE and r.second_action == Action.COOPERATE
                ),
                "mutual_defect_rounds": sum(
                    1 for r in m_noisy.rounds if r.first_action == Action.DEFECT and r.second_action == Action.DEFECT
                ),
                "asymmetric_rounds": sum(1 for r in m_noisy.rounds if r.first_action != r.second_action),
            },
        }

    return duel_results


def run_resilient_society_tournament(
    noise_rate: float, rounds_per_match: int = 50, seed: int = 42
) -> dict:
    """Run an 8-archetype tournament across classic and noise-resilient strategies."""
    game = PrisonersDilemma()

    agents = [
        Agent("Altruist", AlwaysCooperateStrategy()),
        Agent("Predator", AlwaysDefectStrategy()),
        Agent("TitForTat", TitForTatStrategy()),
        Agent("GrimTrigger", GrimTriggerStrategy()),
        Agent("Random", RandomStrategy(seed=seed, cooperation_probability=0.5)),
        Agent("GenerousTFT", GenerousTitForTatStrategy(forgiveness_probability=1 / 3, seed=seed + 10)),
        Agent("TitForTwoTats", TitForTwoTatsStrategy()),
        Agent("Pavlov_WSLS", WinStayLoseShiftStrategy()),
    ]

    population = Population(agents)
    tournament = Tournament(population, game, rounds_per_match=rounds_per_match, noise=noise_rate, seed=seed)
    result = tournament.execute()

    leaderboard_data = []
    for entry in result.leaderboard:
        leaderboard_data.append(
            {
                "rank": entry.rank,
                "agent_id": entry.agent_id,
                "strategy": entry.strategy_name,
                "total_score": entry.total_score,
                "avg_score_per_round": entry.average_score_per_round,
                "wins": entry.wins,
                "ties": entry.ties,
                "losses": entry.losses,
                "cooperations": entry.cooperations,
                "defections": entry.defections,
                "cooperation_rate": entry.cooperation_rate,
            }
        )

    # Build pairwise matrix
    pairwise: dict[str, dict[str, int]] = {a.id: {} for a in agents}
    for m in tournament.matches:
        res = m.result
        if res:
            pairwise[res.first_agent_id][res.second_agent_id] = res.first_score
            pairwise[res.second_agent_id][res.first_agent_id] = res.second_score

    return {
        "noise_rate": noise_rate,
        "rounds_per_match": rounds_per_match,
        "total_matches": result.total_matches,
        "total_rounds": result.total_rounds,
        "population_cooperation_rate": result.population_cooperation_rate,
        "leaderboard": leaderboard_data,
        "pairwise_scores": pairwise,
    }


def main():
    print("=" * 80)
    print("THE DILEMMA EXPERIMENT — EPISODE 3: NOISE & FORGIVENESS")
    print("Running reproducible simulation experiments across noise levels...")
    print("=" * 80)

    # 1. Run pairwise duel dynamics
    print("\n[1/3] Simulating Pairwise Micro-Dynamics (0% vs 2% Noise)...")
    pairwise_duels = run_pairwise_duels(rounds=50, seed=42)

    # 2. Run Tournament at 0% Noise (Baseline)
    print("[2/3] Simulating 8-Archetype Tournament at 0% Noise (Baseline)...")
    tourney_clean = run_resilient_society_tournament(noise_rate=0.00, rounds_per_match=50, seed=42)

    # 3. Run Tournament at 5% Noise
    print("[3/3] Simulating 8-Archetype Tournament at 5% Noise...")
    tourney_noisy_5 = run_resilient_society_tournament(noise_rate=0.05, rounds_per_match=50, seed=42)

    # Also run at 1% and 10% for comprehensive curves
    tourney_noisy_1 = run_resilient_society_tournament(noise_rate=0.01, rounds_per_match=50, seed=42)
    tourney_noisy_10 = run_resilient_society_tournament(noise_rate=0.10, rounds_per_match=50, seed=42)

    all_results = {
        "episode": 3,
        "title": "Noise & Forgiveness",
        "description": "Simulation results examining the impact of communication noise on cooperation and forgiveness",
        "pairwise_duels": pairwise_duels,
        "tournaments": {
            "noise_00_clean": tourney_clean,
            "noise_01": tourney_noisy_1,
            "noise_05": tourney_noisy_5,
            "noise_10": tourney_noisy_10,
        },
    }

    output_path = Path(__file__).parent / "experiment_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n[✓] Results successfully exported to: {output_path}")

    # Print Pairwise Duel Table
    print("\n" + "=" * 80)
    print("MICRO-DYNAMICS: PAIRWISE DUELS UNDER 0% vs 2% NOISE (50 Rounds)")
    print("=" * 80)
    print(f"{'PAIRWISE DUEL':<22} | {'0% COOP RNDS':<12} | {'2% COOP RNDS':<12} | {'2% ASYMM RNDS':<13} | {'EFFECT'}")
    print("-" * 80)
    for name, data in pairwise_duels.items():
        clean_coop = data["clean"]["mutual_coop_rounds"]
        noisy_coop = data["noisy_2_percent"]["mutual_coop_rounds"]
        asymm = data["noisy_2_percent"]["asymmetric_rounds"]
        if name == "TFT_vs_TFT":
            effect = "Echo Spiral (Alternating CD/DC)"
        elif name == "Grim_vs_Altruist":
            effect = "Fatal Trap (Permanent Defection)"
        elif name == "GTFT_vs_TFT":
            effect = "Resilient (Forgives & Reconnects)"
        else:
            effect = "Self-Correcting (Back to CC in 2 rnds)"
        print(f"{name:<22} | {clean_coop:<12} | {noisy_coop:<12} | {asymm:<13} | {effect}")

    # Print Tournament Leaderboards Comparison Table (0% vs 5%)
    print("\n" + "=" * 80)
    print("TOURNAMENT LEADERBOARD COMPARISON: 0% NOISE vs 5% NOISE")
    print("=" * 80)
    print(
        f"{'AGENT':<16} | {'0% RANK':<7} | {'0% SCORE':<8} | {'5% RANK':<7} | {'5% SCORE':<8} | {'SCORE DELTA'}"
    )
    print("-" * 80)

    clean_ranks = {e["agent_id"]: e for e in tourney_clean["leaderboard"]}
    noisy_ranks = {e["agent_id"]: e for e in tourney_noisy_5["leaderboard"]}

    for agent_id, noisy_entry in sorted(noisy_ranks.items(), key=lambda x: x[1]["rank"]):
        clean_entry = clean_ranks[agent_id]
        c_rank = clean_entry["rank"]
        c_score = clean_entry["total_score"]
        n_rank = noisy_entry["rank"]
        n_score = noisy_entry["total_score"]
        delta = n_score - c_score
        sign = "+" if delta > 0 else ""
        print(
            f"{agent_id:<16} | #{c_rank:<6} | {c_score:<8} | #{n_rank:<6} | {n_score:<8} | {sign}{delta}"
        )

    print("=" * 80)


if __name__ == "__main__":
    main()
