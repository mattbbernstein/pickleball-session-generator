import argparse
import sys

from pickleball_session import PickleballSession


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate N sessions and print the one with the highest heuristic score."
    )
    parser.add_argument(
        "n", type=int, nargs="?", default=1000,
        help="number of sessions to generate (default: 1000)",
    )
    parser.add_argument(
        "-r", "--rounds", type=int, default=6,
        help="number of rounds per session (default: 6)",
    )
    parser.add_argument("-c", "--court-weight", type=float, default=None)
    parser.add_argument("-p", "--partner-weight", type=float, default=None)
    parser.add_argument("-s", "--serve-weight", type=float, default=None)
    return parser.parse_args()


def prompt_yes_no(question, default=False):
    suffix = "[yes/no, Default: No]" if not default else "[yes/no, Default: Yes]"
    answer = input(f"{question} {suffix}: ").strip().lower()
    if not answer:
        return default
    return answer.startswith("y")


def prompt_int(question, default):
    answer = input(f"{question} [Default: {default}]: ").strip()
    if not answer:
        return default
    try:
        return int(answer)
    except ValueError:
        print(f"Not a number, using default ({default}).")
        return default


def prompt_weight(name, default):
    while True:
        answer = input(f"{name} weight, 1-3 [Default: {default}]: ").strip()
        if not answer:
            return default
        try:
            value = int(answer)
        except ValueError:
            print("Please enter a whole number between 1 and 3.")
            continue
        if value not in (1, 2, 3):
            print("Please enter a whole number between 1 and 3.")
            continue
        return value


def prompt_args():
    args = argparse.Namespace(
        n=1000, rounds=6, court_weight=None, partner_weight=None, serve_weight=None
    )

    if not prompt_yes_no("Customize options?"):
        return args

    args.n = prompt_int("How many sessions to generate?", args.n)
    args.rounds = prompt_int("How many rounds per session?", args.rounds)

    if prompt_yes_no("Customize weights?"):
        args.court_weight = prompt_weight("Court", PickleballSession.COURT_WEIGHT)
        args.partner_weight = prompt_weight("Partner", PickleballSession.PARTNER_WEIGHT)
        args.serve_weight = prompt_weight("Serve", PickleballSession.SERVE_WEIGHT)

    return args


def main():
    args = prompt_args() if len(sys.argv) == 1 else parse_args()

    best_session = None
    best_score = None
    for _ in range(args.n):
        session = PickleballSession.generate(num_rounds=args.rounds)
        score = session.score(
            court_weight=args.court_weight,
            partner_weight=args.partner_weight,
            serve_weight=args.serve_weight,
        )
        if best_score is None or score > best_score:
            best_session, best_score = session, score

    print(best_session)
    print(f"score = {best_score:.3f}")

    if sys.stdin.isatty():
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
