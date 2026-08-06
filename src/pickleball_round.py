import random

PLAYERS = "ABCDEFGH"


class PickleballRound:
    courts: dict
    servers: dict

    def __init__(self):
        raise TypeError("Use PickleballRound.generate() instead of the constructor")

    @classmethod
    def generate(cls):
        self = object.__new__(cls)

        players = list(PLAYERS)
        random.shuffle(players)

        teams = [tuple(players[i:i + 2]) for i in range(0, 8, 2)]
        random.shuffle(teams)

        self.courts = {
            1: (teams[0], teams[1]),
            2: (teams[2], teams[3]),
        }
        self.servers = {
            court: random.choice(court_teams)
            for court, court_teams in self.courts.items()
        }
        return self

    def player_details(self):
        details = {}
        for court, (team_a, team_b) in self.courts.items():
            server = self.servers[court]
            for team in (team_a, team_b):
                for player in team:
                    partner = next(p for p in team if p != player)
                    details[player] = (court, partner, team == server)
        return details

    def _court_player_sets(self):
        return {
            frozenset(team_a) | frozenset(team_b)
            for team_a, team_b in self.courts.values()
        }

    def __eq__(self, other):
        if not isinstance(other, PickleballRound):
            return NotImplemented
        return self._court_player_sets() == other._court_player_sets()

    def __hash__(self):
        return hash(frozenset(self._court_player_sets()))

    def render_lines(self, title=None):
        lines = []
        if title:
            width = max(len(title), 11)
            lines.append(title.center(width))

        for court in sorted(self.courts):
            team_a, team_b = self.courts[court]
            server = self.servers[court]

            def label(player, team):
                return f"{player}*" if team == server else player

            top = " & ".join(label(p, team_a) for p in team_a)
            bottom = " & ".join(label(p, team_b) for p in team_b)
            width = max(len(top), len(bottom), len(f"Court {court}")) + 4

            lines.append(f"Court {court}".center(width))
            lines.append("+" + "-" * (width - 2) + "+")
            lines.append("|" + top.center(width - 2) + "|")
            lines.append("|" + "-" * (width - 2) + "|")
            lines.append("|" + bottom.center(width - 2) + "|")
            lines.append("+" + "-" * (width - 2) + "+")

        return lines

    def __repr__(self):
        return "\n".join(self.render_lines() + ["", "* = serving"])


if __name__ == "__main__":
    round1 = PickleballRound.generate()
    print(round1)
