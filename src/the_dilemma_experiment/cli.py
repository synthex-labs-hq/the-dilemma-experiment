"""Unified Command-Line Interface (CLI) for The Dilemma Experiment."""

import argparse
import subprocess
import sys
from pathlib import Path


def run_ui_command(args: argparse.Namespace) -> None:
    """Launch the Web Arena UI and FastAPI simulation server."""
    root_dir = Path(__file__).resolve().parent.parent.parent
    launcher = root_dir / "run_ui.sh"

    if args.prod:
        cmd = ["uvicorn", "the_dilemma_experiment.api.app:app", "--host", args.host, "--port", str(args.port)]
        print(f"Starting standalone Dilemma Arena on http://{args.host}:{args.port}...")
        try:
            import uvicorn
            uvicorn.run("the_dilemma_experiment.api.app:app", host=args.host, port=args.port)
        except ImportError:
            subprocess.run(["uv", "run"] + cmd, cwd=root_dir, check=False)
    else:
        if launcher.exists() and launcher.is_file():
            subprocess.run([str(launcher)], cwd=root_dir, check=False)
        else:
            print("Running FastAPI backend directly...")
            import uvicorn
            uvicorn.run("the_dilemma_experiment.api.app:app", host=args.host, port=args.port)


def run_demo_command(args: argparse.Namespace) -> None:
    """Run interactive terminal demo for an episode."""
    ep_num = args.episode
    root_dir = Path(__file__).resolve().parent.parent.parent

    demo_files = {
        3: root_dir / "experiments" / "episode_03" / "demo_noise_cli.py",
        4: root_dir / "experiments" / "episode_04" / "demo_evolution_cli.py",
        6: root_dir / "experiments" / "episode_06" / "demo_reputation_cli.py",
        7: root_dir / "experiments" / "episode_07" / "demo_tribalism_cli.py",
        8: root_dir / "experiments" / "episode_08" / "demo_commons_cli.py",
        9: root_dir / "experiments" / "episode_09" / "demo_zd_cli.py",
        10: root_dir / "experiments" / "episode_10" / "demo_llm_society_cli.py",
    }

    if ep_num in demo_files and demo_files[ep_num].exists():
        script = demo_files[ep_num]
        print(f"Launching Episode {ep_num} CLI Demo...")
        subprocess.run([sys.executable, str(script)], cwd=root_dir, check=False)
    else:
        print(f"Episode {ep_num} does not have a dedicated interactive CLI demo.")
        print(f"Available episode CLI demos: {list(demo_files.keys())}")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="the-dilemma",
        description="The Dilemma Experiment - Evolutionary Game Theory & Multi-Agent Platform",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # UI Subcommand
    ui_parser = subparsers.add_parser("ui", help="Launch the interactive Web Arena simulation platform")
    ui_parser.add_argument("--host", default="0.0.0.0", help="Host address (default: 0.0.0.0)")
    ui_parser.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    ui_parser.add_argument("--prod", action="store_true", help="Launch standalone single-port production server")

    # Demo Subcommand
    demo_parser = subparsers.add_parser("demo", help="Run interactive terminal simulation for an episode")
    demo_parser.add_argument("episode", type=int, help="Episode number (e.g. 3, 4, 6, 7, 8, 9, 10)")

    # Version Subcommand
    subparsers.add_parser("version", help="Print version information")

    args = parser.parse_args()

    if args.command == "ui":
        run_ui_command(args)
    elif args.command == "demo":
        run_demo_command(args)
    elif args.command == "version":
        print("The Dilemma Experiment v1.1.0 (Interactive Web Arena Suite)")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
