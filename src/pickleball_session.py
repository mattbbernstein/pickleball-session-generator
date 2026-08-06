import math
from collections import Counter
from statistics import fmean

from pickleball_round import PickleballRound, PLAYERS

GAP = "   "

NUM_COURTS = 2


def _spread(sequence, num_options):
    """Normalized entropy: 1.0 when values are as evenly distributed as possible."""
    achievable = min(num_options, len(sequence))
    if achievable < 2:
        return 1.0
    total = len(sequence)
    entropy = -sum(
        (count / total) * math.log(count / total)
        for count in Counter(sequence).values()
    )
    return entropy / math.log(achievable)


def _switch_rate(sequence):
    if len(sequence) < 2:
        return 1.0
    changes = sum(1 for a, b in zip(sequence, sequence[1:]) if a != b)
    return changes / (len(sequence) - 1)


def _variety(sequence, num_options):
    return (_spread(sequence, num_options) + _switch_rate(sequence)) / 2


class PickleballSession:
    rounds: list

    COURT_WEIGHT = 1.0
    PARTNER_WEIGHT = 2.0
    SERVE_WEIGHT = 1.0

    def __init__(self):
        raise TypeError("Use PickleballSession.generate() instead of the constructor")

    MAX_UNIQUE_ROUNDS = 35

    @classmethod
    def generate(cls, num_rounds=6):
        if num_rounds > cls.MAX_UNIQUE_ROUNDS:
            raise ValueError(
                f"num_rounds must be <= {cls.MAX_UNIQUE_ROUNDS} "
                f"({cls.MAX_UNIQUE_ROUNDS} is the number of distinct court groupings)"
            )

        self = object.__new__(cls)

        self.rounds = []
        while len(self.rounds) < num_rounds:
            candidate = PickleballRound.generate()
            if candidate not in self.rounds:
                self.rounds.append(candidate)
        return self

    def _player_timelines(self):
        details = [round_.player_details() for round_ in self.rounds]
        return {
            player: [detail[player] for detail in details]
            for player in PLAYERS
        }

    def score(self, court_weight=None, partner_weight=None, serve_weight=None):
        """Higher is better: rewards varied courts, partners, and serving turns."""
        court_weight = self.COURT_WEIGHT if court_weight is None else court_weight
        partner_weight = self.PARTNER_WEIGHT if partner_weight is None else partner_weight
        serve_weight = self.SERVE_WEIGHT if serve_weight is None else serve_weight

        total_weight = court_weight + partner_weight + serve_weight
        if total_weight <= 0:
            raise ValueError("At least one weight must be positive")

        court_scores = []
        partner_scores = []
        serve_scores = []

        for timeline in self._player_timelines().values():
            courts = [court for court, _, _ in timeline]
            partners = [partner for _, partner, _ in timeline]
            serving = [is_serving for _, _, is_serving in timeline]

            court_scores.append(_variety(courts, NUM_COURTS))
            partner_scores.append(_variety(partners, len(PLAYERS) - 1))
            serve_scores.append(_variety(serving, 2))

        return (
            court_weight * fmean(court_scores)
            + partner_weight * fmean(partner_scores)
            + serve_weight * fmean(serve_scores)
        ) / total_weight

    def __repr__(self):
        blocks = [
            round_.render_lines(title=f"Round {i}")
            for i, round_ in enumerate(self.rounds, start=1)
        ]

        height = max(len(block) for block in blocks)
        widths = []
        for block in blocks:
            width = max(len(line) for line in block)
            widths.append(width)
            block.extend([""] * (height - len(block)))

        rows = []
        for row in range(height):
            rows.append(GAP.join(
                block[row].ljust(widths[i]) for i, block in enumerate(blocks)
            ))

        rows.append("")
        rows.append("* = serving")
        return "\n".join(rows)


if __name__ == "__main__":
    session = PickleballSession.generate()
    print(session)
    print(f"score = {session.score():.3f}")
