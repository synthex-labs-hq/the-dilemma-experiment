#!/usr/bin/env python3
"""Cinematic Interactive Terminal Demonstration for Episode 5: Spatial Networks & Topologies.

Pre-calibrated to synchronize with the voiceover narration timeline from video_script_master.md:
1. Act I: The Fortress of Geography (The Altruist Cluster vs Predator Sea)
2. Act II: The Reciprocal Conquest (Tit-for-Tat Territorial Expansion Wave)
3. Act III: The Small-World Infection (How Network Shortcuts Breach the Fortress)
4. Act IV: The Spatial Verdict (The 3 Laws of Geographic Trust)

Usage:
    # Calibrated script pacing (default - holds at each act for voiceover):
    uv run python experiments/episode_05/demo_spatial_cli.py

    # Presenter step mode (press ENTER to advance between acts/generations):
    uv run python experiments/episode_05/demo_spatial_cli.py --step

    # Fast mode (quick testing / CI without delays):
    uv run python experiments/episode_05/demo_spatial_cli.py --fast
"""

import argparse
import sys
import time

from the_dilemma_experiment.domain.network_graph import NetworkGraph
from the_dilemma_experiment.domain.spatial_grid import ToroidalGrid2D
from the_dilemma_experiment.domain.spatial_tournament import (
    FitnessMode,
    SpatialTournament,
)
from the_dilemma_experiment.domain.topology import NeighborhoodType
from the_dilemma_experiment.strategies.always_cooperate import (
    AlwaysCooperateStrategy,
)
from the_dilemma_experiment.strategies.always_defect import (
    AlwaysDefectStrategy,
)
from the_dilemma_experiment.strategies.tit_for_tat import (
    TitForTatStrategy,
)

# ANSI Colors & Formatting
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
CYAN = "\033[36m"
AMBER = "\033[33m"
GREEN = "\033[32m"
RED = "\033[31m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
WHITE = "\033[37m"
BG_DARK = "\033[40m"


def clear_screen() -> None:
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def print_banner() -> None:
    banner = f"""
{CYAN}{BOLD}╔════════════════════════════════════════════════════════════════════════════╗
║                        THE DILEMMA EXPERIMENT                              ║
║           Episode 5: Spatial Networks, Lattices & Topologies               ║
║         "Geography as a Shield: How Spatial Clusters Protect Trust"        ║
╚════════════════════════════════════════════════════════════════════════════╝{RESET}
"""
    print(banner)


def render_grid_canvas(
    grid: ToroidalGrid2D,
    node_strategies: tuple[str, ...],
    generation: int,
    clustering_ratio: float,
) -> None:
    """Render a compact, high-contrast ANSI 2D grid."""
    print(
        f"\n  {BOLD}Generation {generation:02d}{RESET}  │  "
        f"Cooperator Clustering: {GREEN if clustering_ratio > 0.5 else AMBER}{clustering_ratio * 100:5.1f}%{RESET}  │  "
        f"Lattice: {grid.width}x{grid.height} ({grid.node_count} nodes)"
    )

    border = "  ┌" + "──" * grid.width + "┐"
    print(f"{DIM}{border}{RESET}")

    for y in range(grid.height):
        row_str = "  │"
        for x in range(grid.width):
            node_id = grid.coord_to_id(x, y)
            strat = node_strategies[node_id]
            if strat in ("AlwaysCooperateStrategy", "TitForTatStrategy"):
                cell = f"{GREEN}██{RESET}"
            else:  # AlwaysDefectStrategy
                cell = f"{RED}··{RESET}"
            row_str += cell
        row_str += f"{DIM}│{RESET}"
        print(row_str)

    bottom_border = "  └" + "──" * grid.width + "┘"
    print(f"{DIM}{bottom_border}{RESET}")

    # Legend
    print(
        f"  Legend: {GREEN}██ Cooperator (Trust){RESET}   {RED}·· Predator (Defection){RESET}"
    )


def pause(duration: float, step_mode: bool, cue_text: str = "") -> None:
    if step_mode:
        prompt = f"\n{AMBER}[STEP PAUSE] {cue_text} (Press ENTER to continue)...{RESET}"
        input(prompt)
    else:
        if cue_text:
            print(f"{DIM}── {cue_text} ──{RESET}")
        time.sleep(duration)


def run_act_1_the_altruist_fortress(step_mode: bool, delay_mult: float) -> None:
    print(
        f"\n{BOLD}{CYAN}═══ ACT I: THE ALTRUIST FORTRESS (GEOGRAPHY AS A SHIELD) ═══{RESET}"
    )
    print(
        "In Episode 4's well-mixed soup, 9 Altruists in 91 Predators were wiped out in 3 generations.\n"
        "Now, we plant that exact same 9% cluster in a 2D spatial lattice.\n"
        "Watch what happens to the perimeter vs the interior:"
    )

    grid = ToroidalGrid2D(width=12, height=12, neighborhood_type=NeighborhoodType.MOORE)
    strategies = [AlwaysDefectStrategy] * grid.node_count
    cluster_nodes = grid.get_cluster_node_ids(center_x=6, center_y=6, radius=1)
    for n in cluster_nodes:
        strategies[n] = AlwaysCooperateStrategy

    tourney = SpatialTournament(
        topology=grid,
        initial_strategies=strategies,
        rounds_per_match=1,
    )

    # Initial state
    init_state = tourney.history[0]
    render_grid_canvas(
        grid=grid,
        node_strategies=init_state.node_strategies,
        generation=0,
        clustering_ratio=init_state.cooperator_clustering_ratio,
    )
    pause(
        2.5 * delay_mult, step_mode, "Vo: A tiny 3x3 island of trust in a sea of greed"
    )

    # Step through 5 generations
    for gen in range(1, 6):
        res = tourney.step()
        render_grid_canvas(
            grid=grid,
            node_strategies=res.node_strategies,
            generation=gen,
            clustering_ratio=res.cooperator_clustering_ratio,
        )
        dist = res.strategy_distribution
        ac = dist.get("AlwaysCooperateStrategy", 0)
        ad = dist.get("AlwaysDefectStrategy", 0)
        print(f"  Census: Cooperators={ac} ({(ac / 144) * 100:.1f}%) | Predators={ad}")
        pause(
            1.2 * delay_mult,
            step_mode,
            f"Generation {gen}: The fortress holds its boundary",
        )

    print(
        f"\n{GREEN}{BOLD}✓ DISCOVERY:{RESET} In a spatial world, the fortress NEVER dies. "
        f"Interior altruists earn +24, shielding the boundary from collapse!"
    )
    pause(2.0 * delay_mult, step_mode, "Vo: End of Act I")


def run_act_2_the_reciprocal_conquest(step_mode: bool, delay_mult: float) -> None:
    print(
        f"\n{BOLD}{CYAN}═══ ACT II: THE RECIPROCAL CONQUEST (TIT-FOR-TAT EXPANSION) ═══{RESET}"
    )
    print(
        "Altruists can defend, but cannot conquer.\n"
        "Now we place 9 Tit-for-Tat reciprocal agents in a 14x14 grid (196 agents).\n"
        "With repeated interactions (R=5), watch the territorial wave front expand:"
    )

    grid = ToroidalGrid2D(width=14, height=14, neighborhood_type=NeighborhoodType.MOORE)
    strategies = [AlwaysDefectStrategy] * grid.node_count
    cluster_nodes = grid.get_cluster_node_ids(center_x=7, center_y=7, radius=1)
    for n in cluster_nodes:
        strategies[n] = TitForTatStrategy

    tourney = SpatialTournament(
        topology=grid,
        initial_strategies=strategies,
        rounds_per_match=5,
    )

    init_state = tourney.history[0]
    render_grid_canvas(
        grid=grid,
        node_strategies=init_state.node_strategies,
        generation=0,
        clustering_ratio=init_state.cooperator_clustering_ratio,
    )
    pause(2.5 * delay_mult, step_mode, "Vo: A 9-agent seed of reciprocal trust")

    for gen in range(1, 8):
        res = tourney.step()
        render_grid_canvas(
            grid=grid,
            node_strategies=res.node_strategies,
            generation=gen,
            clustering_ratio=res.cooperator_clustering_ratio,
        )
        dist = res.strategy_distribution
        tft = dist.get("TitForTatStrategy", 0)
        ad = dist.get("AlwaysDefectStrategy", 0)
        print(
            f"  Census: Tit-for-Tat={tft} ({(tft / 196) * 100:.1f}%) | Predators={ad}"
        )
        pause(
            1.2 * delay_mult, step_mode, f"Generation {gen}: Cooperative wave expanding"
        )
        if res.is_fixated:
            break

    print(
        f"\n{GREEN}{BOLD}✓ DISCOVERY:{RESET} Reciprocal trust converts boundary predators! "
        f"In just a few generations, 9 agents conquered the entire world (100% fixation)!"
    )
    pause(2.0 * delay_mult, step_mode, "Vo: End of Act II")


def run_act_3_the_small_world_infection(step_mode: bool, delay_mult: float) -> None:
    print(
        f"\n{BOLD}{CYAN}═══ ACT III: THE SMALL-WORLD INFECTION (NETWORKS VS LATTICES) ═══{RESET}"
    )
    print(
        "What happens when society isn't a neat grid, but a Small-World network with shortcuts?\n"
        "Testing a 100-node network with rewiring probability beta:"
    )

    betas = [0.0, 0.1, 0.3]
    for beta in betas:
        graph = NetworkGraph.small_world(n=100, k=8, beta=beta)
        strategies = [AlwaysDefectStrategy] * 100
        for i in range(40, 60):  # 20% cluster
            strategies[i] = TitForTatStrategy

        tourney = SpatialTournament(
            topology=graph,
            initial_strategies=strategies,
            rounds_per_match=5,
            fitness_mode=FitnessMode.AVERAGE,
        )
        res = tourney.run(max_generations=15)
        final_tft = res.final_distribution.get("TitForTatStrategy", 0)

        status_color = GREEN if final_tft > 50 else (AMBER if final_tft > 0 else RED)
        print(
            f"  • Beta={beta:3.1f} ({int(beta * 100)}% shortcuts): "
            f"Final TFT={status_color}{final_tft:3d}/100 ({final_tft}%){RESET} "
            f"│ {'✓ Fortress Intact' if final_tft == 100 else '⚠ Boundary Leaked / Breached'}"
        )
        pause(1.0 * delay_mult, step_mode, f"Small-World beta={beta}")

    print(
        f"\n{AMBER}{BOLD}✓ DISCOVERY:{RESET} Long-range shortcuts act as infection vectors. "
        f"When networks become too interconnected, defector pathogens breach local cluster shields!"
    )
    pause(2.0 * delay_mult, step_mode, "Vo: End of Act III")


def run_act_4_the_spatial_verdict(step_mode: bool, delay_mult: float) -> None:
    print(f"\n{BOLD}{CYAN}═══ ACT IV: THE 3 LAWS OF SPATIAL TRUST ═══{RESET}")
    print(f"""
  {BOLD}1. The Shield of Geometry:{RESET}
     A cooperator in a crowd dies. A cooperator in a cluster thrives.
     Interior mutual aid funds the defense of the exterior.

  {BOLD}2. Reciprocal Outward Conversion:{RESET}
     Pure altruism holds territory; retaliatory reciprocity (Tit-for-Tat) conquers it.
     Boundary predators realize cooperation pays higher dividends and convert.

  {BOLD}3. The Small-World Vulnerability:{RESET}
     Hyper-connectivity can be lethal. Without local boundaries and cluster protection,
     defector pathogens travel across shortcuts to exploit innocent clusters.
""")
    pause(2.0 * delay_mult, step_mode, "Vo: Conclusion & Episode 6 Teaser")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Episode 5 Spatial Networks Interactive CLI Demonstration"
    )
    parser.add_argument(
        "--step", action="store_true", help="Manual step-by-step presenter mode"
    )
    parser.add_argument(
        "--fast", action="store_true", help="Fast execution mode without delays"
    )
    args = parser.parse_args()

    delay_mult = 0.0 if args.fast else 1.0

    clear_screen()
    print_banner()
    pause(1.5 * delay_mult, args.step, "Vo: Welcome to Episode 5")

    run_act_1_the_altruist_fortress(args.step, delay_mult)
    run_act_2_the_reciprocal_conquest(args.step, delay_mult)
    run_act_3_the_small_world_infection(args.step, delay_mult)
    run_act_4_the_spatial_verdict(args.step, delay_mult)

    print(f"\n{GREEN}{BOLD}Demonstration complete.{RESET}\n")


if __name__ == "__main__":
    main()
