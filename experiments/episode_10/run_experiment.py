"""Comprehensive empirical benchmark suite for Episode 10: The Cognitive Revolution (LLM Multi-Agent Societies).

Executes three rigorous experiments:
1. Experiment A: The Value of Cheap Talk (Pre-play negotiation vs silent play)
2. Experiment B: The Machiavellian Index & Strategic Deception Audit
3. Experiment C: Cognitive Multi-Agent Society Tournament (Diplomats vs Machiavellians vs Contractors vs Skeptics)
"""

import json
from pathlib import Path
from typing import Any

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.cognitive import (
    CognitiveMatch,
    CognitivePersona,
    DeceptionTracker,
    NegotiationChannel,
)
from the_dilemma_experiment.strategies.cognitive_strategy import (
    CognitiveStrategy,
)


def run_experiment_a_cheap_talk_value() -> dict[str, Any]:
    """Experiment A: Evaluates pairwise outcomes and cooperation stability across cognitive dyads."""
    personas = [
        CognitivePersona.HONEST_DIPLOMAT,
        CognitivePersona.MACHIAVELLIAN,
        CognitivePersona.PRAGMATIC_CONTRACTOR,
        CognitivePersona.SKEPTICAL_REALIST,
    ]
    results: list[dict[str, Any]] = []

    for p_a in personas:
        for p_b in personas:
            strat_a = CognitiveStrategy(persona=p_a, agent_id=f"AgentA_{p_a.value}")
            strat_b = CognitiveStrategy(persona=p_b, agent_id=f"AgentB_{p_b.value}")
            agent_a = Agent(f"AgentA_{p_a.value}", strat_a)
            agent_b = Agent(f"AgentB_{p_b.value}", strat_b)

            channel = NegotiationChannel()
            tracker = DeceptionTracker()
            match = CognitiveMatch(
                agent_a,
                agent_b,
                round_count=10,
                channel=channel,
                deception_tracker=tracker,
            )
            match_res = match.play()

            coop_rounds = sum(
                1
                for r in match_res.rounds
                if r.first_action == Action.COOPERATE
                and r.second_action == Action.COOPERATE
            )
            coop_rate = coop_rounds / len(match_res.rounds)

            results.append(
                {
                    "persona_a": p_a.value,
                    "persona_b": p_b.value,
                    "score_a": match_res.score_a,
                    "score_b": match_res.score_b,
                    "avg_score_a": match_res.score_a / len(match_res.rounds),
                    "avg_score_b": match_res.score_b / len(match_res.rounds),
                    "cooperation_rate": coop_rate,
                    "deception_rate_a": match_res.deception_a,
                    "deception_rate_b": match_res.deception_b,
                }
            )

    return {"experiment": "Experiment A: The Value of Cheap Talk", "dyads": results}


def run_experiment_b_machiavellian_audit() -> dict[str, Any]:
    """Experiment B: Quantifies the Machiavellian deception index and exploitation quotient against various archetypes."""
    partners = [
        ("HonestDiplomat", CognitivePersona.HONEST_DIPLOMAT),
        ("PragmaticContractor", CognitivePersona.PRAGMATIC_CONTRACTOR),
        ("SkepticalRealist", CognitivePersona.SKEPTICAL_REALIST),
        ("FellowMachiavellian", CognitivePersona.MACHIAVELLIAN),
    ]

    audit_records: list[dict[str, Any]] = []

    for name, persona in partners:
        strat_mach = CognitiveStrategy(
            persona=CognitivePersona.MACHIAVELLIAN,
            agent_id="Machiavelli",
        )
        strat_opp = CognitiveStrategy(
            persona=persona,
            agent_id=name,
        )
        agent_mach = Agent("Machiavelli", strat_mach)
        agent_opp = Agent(name, strat_opp)

        channel = NegotiationChannel()
        tracker = DeceptionTracker()
        match = CognitiveMatch(
            agent_mach,
            agent_opp,
            round_count=20,
            channel=channel,
            deception_tracker=tracker,
        )
        res = match.play()

        promises = tracker.get_promises_count("Machiavelli")
        broken = tracker.get_broken_count("Machiavelli")
        deception_rate = tracker.get_deception_rate("Machiavelli")
        exploitation_ratio = (
            (res.score_a / res.score_b) if res.score_b > 0 else 1.0
        )

        audit_records.append(
            {
                "opponent": name,
                "opponent_persona": persona.value,
                "machiavelli_score": res.score_a,
                "opponent_score": res.score_b,
                "exploitation_ratio": round(exploitation_ratio, 3),
                "promises_made": promises,
                "promises_broken": broken,
                "deception_rate": round(deception_rate, 3),
            }
        )

    return {
        "experiment": "Experiment B: Machiavellian Deception Audit",
        "audits": audit_records,
    }


def run_experiment_c_cognitive_society_tournament() -> dict[str, Any]:
    """Experiment C: 20-agent round-robin tournament across cognitive personas."""
    personas = [
        ("Diplomat", CognitivePersona.HONEST_DIPLOMAT, 5),
        ("Machiavelli", CognitivePersona.MACHIAVELLIAN, 5),
        ("Contractor", CognitivePersona.PRAGMATIC_CONTRACTOR, 5),
        ("Realist", CognitivePersona.SKEPTICAL_REALIST, 5),
    ]

    population: list[Agent] = []
    for prefix, persona, count in personas:
        for i in range(1, count + 1):
            agent_id = f"{prefix}_{i:02d}"
            strat = CognitiveStrategy(persona=persona, agent_id=agent_id)
            population.append(Agent(agent_id, strat))

    total_scores: dict[str, int] = {a.id: 0 for a in population}
    agent_personas: dict[str, str] = {
        a.id: a.strategy.persona.value  # type: ignore[attr-defined]
        for a in population
    }
    match_counts: dict[str, int] = {a.id: 0 for a in population}
    global_tracker = DeceptionTracker()
    global_channel = NegotiationChannel()

    # Round-robin: each agent plays every other agent
    for i in range(len(population)):
        for j in range(i + 1, len(population)):
            agent_i = population[i]
            agent_j = population[j]

            # Fresh state for pairwise match
            agent_i.strategy.reset()  # type: ignore[attr-defined]
            agent_j.strategy.reset()  # type: ignore[attr-defined]

            match = CognitiveMatch(
                agent_a=agent_i,
                agent_b=agent_j,
                round_count=10,
                channel=global_channel,
                deception_tracker=global_tracker,
            )
            res = match.play()

            total_scores[agent_i.id] += res.score_a
            total_scores[agent_j.id] += res.score_b
            match_counts[agent_i.id] += 1
            match_counts[agent_j.id] += 1

    # Aggregate persona group statistics
    persona_stats: dict[str, dict[str, Any]] = {}
    for p in [
        CognitivePersona.HONEST_DIPLOMAT.value,
        CognitivePersona.MACHIAVELLIAN.value,
        CognitivePersona.PRAGMATIC_CONTRACTOR.value,
        CognitivePersona.SKEPTICAL_REALIST.value,
    ]:
        agents_in_group = [a.id for a in population if agent_personas[a.id] == p]
        group_scores = [total_scores[aid] for aid in agents_in_group]
        group_deception = [
            global_tracker.get_deception_rate(aid) for aid in agents_in_group
        ]
        group_broken = [
            global_tracker.get_broken_count(aid) for aid in agents_in_group
        ]

        avg_score = sum(group_scores) / len(group_scores)
        avg_deception = sum(group_deception) / len(group_deception)
        total_broken = sum(group_broken)

        persona_stats[p] = {
            "agent_count": len(agents_in_group),
            "mean_total_score": round(avg_score, 1),
            "mean_score_per_match": round(avg_score / 19, 2),
            "mean_score_per_round": round(avg_score / (19 * 10), 3),
            "mean_deception_rate": round(avg_deception, 3),
            "total_promises_broken": total_broken,
        }

    # Individual Leaderboard
    leaderboard = [
        {
            "rank": 0,
            "agent_id": a.id,
            "persona": agent_personas[a.id],
            "total_score": total_scores[a.id],
            "avg_per_round": round(total_scores[a.id] / (19 * 10), 3),
            "deception_rate": round(global_tracker.get_deception_rate(a.id), 3),
        }
        for a in population
    ]
    leaderboard.sort(key=lambda x: x["total_score"], reverse=True)
    for idx, entry in enumerate(leaderboard, start=1):
        entry["rank"] = idx

    return {
        "experiment": "Experiment C: Cognitive Multi-Agent Society Tournament",
        "total_agents": len(population),
        "total_pairwise_matches": (len(population) * (len(population) - 1)) // 2,
        "persona_summary": persona_stats,
        "leaderboard_top_10": leaderboard[:10],
    }


def main() -> None:
    """Execute all Episode 10 experiments and persist results."""
    print("=" * 70)
    print("THE DILEMMA EXPERIMENT — EPISODE 10 BENCHMARK SUITE")
    print("The Cognitive Revolution: LLM Multi-Agent Societies")
    print("=" * 70)

    print("\n[1/3] Running Experiment A: The Value of Cheap Talk...")
    exp_a = run_experiment_a_cheap_talk_value()
    print("      ✓ Dyadic dialogue matrix computed.")

    print("\n[2/3] Running Experiment B: The Machiavellian Deception Audit...")
    exp_b = run_experiment_b_machiavellian_audit()
    print("      ✓ Strategic deception metrics logged.")

    print(
        "\n[3/3] Running Experiment C: Cognitive Multi-Agent Society Tournament (20 agents, 190 matches)..."
    )
    exp_c = run_experiment_c_cognitive_society_tournament()
    print("      ✓ Tournament completed and society metrics aggregated.")

    combined_results = {
        "metadata": {
            "series": "The Dilemma Experiment",
            "episode": 10,
            "title": "The Cognitive Revolution: LLM Multi-Agent Societies",
            "framework_version": "1.0.0",
        },
        "experiment_a": exp_a,
        "experiment_b": exp_b,
        "experiment_c": exp_c,
    }

    out_file = Path("experiments/episode_10/experiment_results.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(combined_results, f, indent=2)

    print(f"\n[DONE] Experiment results saved to {out_file.resolve()}\n")

    # Print summary highlights
    print("SUMMARY HIGHLIGHTS:")
    print("-" * 50)
    print("SOCIETY PERSONA PERFORMANCE (Experiment C):")
    for persona, stats in exp_c["persona_summary"].items():
        print(
            f"  • {persona.upper():<22}: Mean Score={stats['mean_total_score']:>6.1f} | "
            f"Per Round={stats['mean_score_per_round']:.3f} | "
            f"Deception Rate={stats['mean_deception_rate'] * 100:>5.1f}% | "
            f"Broken Promises={stats['total_promises_broken']}"
        )
    print("-" * 50)


if __name__ == "__main__":
    main()
