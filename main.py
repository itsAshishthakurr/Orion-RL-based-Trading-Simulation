import argparse
from simulation.runner import SimulationRunner
from simulation.leaderboard import Leaderboard


def main():
    parser = argparse.ArgumentParser(description="Orion Trading Simulation")
    parser.add_argument(
        "--difficulty",
        type=str,
        default="easy",
        choices=["easy", "medium", "hard"],
        help="Difficulty level: easy, medium, or hard",
    )
    args = parser.parse_args()

    print("Orion Trading Simulation Starting...")
    print()
    print(f"Difficulty: {args.difficulty.upper()}")
    print()

    runner = SimulationRunner(difficulty=args.difficulty)
    results = runner.run_episode()

    lb = Leaderboard()
    lb.display(results, args.difficulty)


if __name__ == "__main__":
    main()
