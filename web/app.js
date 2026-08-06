const PLAYERS = "ABCDEFGH".split("");
const NUM_COURTS = 2;
const MAX_UNIQUE_ROUNDS = 35;

const COURT_WEIGHT = 1.0;
const PARTNER_WEIGHT = 2.0;
const SERVE_WEIGHT = 1.0;

function shuffle(array) {
  const result = array.slice();
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

function courtPlayerSets(round) {
  return Object.values(round.courts).map(
    ([teamA, teamB]) => new Set([...teamA, ...teamB])
  );
}

function sameCourtGrouping(a, b) {
  const setsA = courtPlayerSets(a);
  const setsB = courtPlayerSets(b);
  return setsA.every((setA) =>
    setsB.some((setB) => setsEqual(setA, setB))
  );
}

function setsEqual(a, b) {
  if (a.size !== b.size) return false;
  for (const item of a) if (!b.has(item)) return false;
  return true;
}

function generateRound() {
  const players = shuffle(PLAYERS);
  const teamsUnshuffled = [];
  for (let i = 0; i < 8; i += 2) {
    teamsUnshuffled.push([players[i], players[i + 1]]);
  }
  const teams = shuffle(teamsUnshuffled);

  const courts = {
    1: [teams[0], teams[1]],
    2: [teams[2], teams[3]],
  };
  const servers = {};
  for (const court of Object.keys(courts)) {
    const courtTeams = courts[court];
    servers[court] = courtTeams[Math.floor(Math.random() * courtTeams.length)];
  }
  return { courts, servers };
}

function playerDetails(round) {
  const details = {};
  for (const court of Object.keys(round.courts)) {
    const [teamA, teamB] = round.courts[court];
    const server = round.servers[court];
    for (const team of [teamA, teamB]) {
      for (const player of team) {
        const partner = team.find((p) => p !== player);
        details[player] = {
          court: Number(court),
          partner,
          isServing: team === server,
        };
      }
    }
  }
  return details;
}

function renderRoundLines(round, title) {
  const lines = [];
  if (title) {
    const width = Math.max(title.length, 11);
    lines.push(center(title, width));
  }

  for (const court of Object.keys(round.courts).sort()) {
    const [teamA, teamB] = round.courts[court];
    const server = round.servers[court];

    const label = (player, team) => (team === server ? `${player}*` : player);

    const top = teamA.map((p) => label(p, teamA)).join(" & ");
    const bottom = teamB.map((p) => label(p, teamB)).join(" & ");
    const width =
      Math.max(top.length, bottom.length, `Court ${court}`.length) + 4;

    lines.push(center(`Court ${court}`, width));
    lines.push("+" + "-".repeat(width - 2) + "+");
    lines.push("|" + center(top, width - 2) + "|");
    lines.push("|" + "-".repeat(width - 2) + "|");
    lines.push("|" + center(bottom, width - 2) + "|");
    lines.push("+" + "-".repeat(width - 2) + "+");
  }

  return lines;
}

function center(text, width) {
  if (text.length >= width) return text;
  const totalPad = width - text.length;
  const left = Math.floor(totalPad / 2);
  const right = totalPad - left;
  return " ".repeat(left) + text + " ".repeat(right);
}

function generateSession(numRounds) {
  if (numRounds > MAX_UNIQUE_ROUNDS) {
    throw new Error(
      `numRounds must be <= ${MAX_UNIQUE_ROUNDS} (${MAX_UNIQUE_ROUNDS} is the number of distinct court groupings)`
    );
  }

  const rounds = [];
  while (rounds.length < numRounds) {
    const candidate = generateRound();
    const isDuplicate = rounds.some((existing) =>
      sameCourtGrouping(existing, candidate)
    );
    if (!isDuplicate) rounds.push(candidate);
  }
  return rounds;
}

function playerTimelines(rounds) {
  const detailsPerRound = rounds.map(playerDetails);
  const timelines = {};
  for (const player of PLAYERS) {
    timelines[player] = detailsPerRound.map((d) => d[player]);
  }
  return timelines;
}

function mean(values) {
  return values.reduce((a, b) => a + b, 0) / values.length;
}

function spread(sequence, numOptions) {
  const achievable = Math.min(numOptions, sequence.length);
  if (achievable < 2) return 1.0;
  const total = sequence.length;
  const counts = new Map();
  for (const value of sequence) {
    counts.set(value, (counts.get(value) || 0) + 1);
  }
  let entropy = 0;
  for (const count of counts.values()) {
    const p = count / total;
    entropy -= p * Math.log(p);
  }
  return entropy / Math.log(achievable);
}

function switchRate(sequence) {
  if (sequence.length < 2) return 1.0;
  let changes = 0;
  for (let i = 1; i < sequence.length; i++) {
    if (sequence[i] !== sequence[i - 1]) changes++;
  }
  return changes / (sequence.length - 1);
}

function variety(sequence, numOptions) {
  return (spread(sequence, numOptions) + switchRate(sequence)) / 2;
}

function scoreSession(rounds, weights) {
  const courtWeight = weights.courtWeight ?? COURT_WEIGHT;
  const partnerWeight = weights.partnerWeight ?? PARTNER_WEIGHT;
  const serveWeight = weights.serveWeight ?? SERVE_WEIGHT;

  const totalWeight = courtWeight + partnerWeight + serveWeight;
  if (totalWeight <= 0) {
    throw new Error("At least one weight must be positive");
  }

  const courtScores = [];
  const partnerScores = [];
  const serveScores = [];

  for (const timeline of Object.values(playerTimelines(rounds))) {
    const courts = timeline.map((d) => d.court);
    const partners = timeline.map((d) => d.partner);
    const serving = timeline.map((d) => d.isServing);

    courtScores.push(variety(courts, NUM_COURTS));
    partnerScores.push(variety(partners, PLAYERS.length - 1));
    serveScores.push(variety(serving, 2));
  }

  return (
    (courtWeight * mean(courtScores) +
      partnerWeight * mean(partnerScores) +
      serveWeight * mean(serveScores)) /
    totalWeight
  );
}

function generateBestSession(numSessions, numRounds, weights) {
  let bestRounds = null;
  let bestScore = null;
  for (let i = 0; i < numSessions; i++) {
    const rounds = generateSession(numRounds);
    const score = scoreSession(rounds, weights);
    if (bestScore === null || score > bestScore) {
      bestRounds = rounds;
      bestScore = score;
    }
  }
  return { rounds: bestRounds, score: bestScore };
}

function renderSessionText(rounds) {
  const gap = "   ";
  const blocks = rounds.map((round, i) =>
    renderRoundLines(round, `Round ${i + 1}`)
  );

  const height = Math.max(...blocks.map((b) => b.length));
  const widths = blocks.map((block) =>
    Math.max(...block.map((line) => line.length))
  );
  blocks.forEach((block, i) => {
    while (block.length < height) block.push("");
  });

  const rows = [];
  for (let row = 0; row < height; row++) {
    rows.push(
      blocks.map((block, i) => block[row].padEnd(widths[i])).join(gap)
    );
  }
  rows.push("");
  rows.push("* = serving");
  return rows.join("\n");
}

function main() {
  const form = document.getElementById("options-form");
  const output = document.getElementById("output");
  const scoreEl = document.getElementById("score");

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const numSessions = Number(document.getElementById("num-sessions").value);
    const numRounds = Number(document.getElementById("num-rounds").value);
    const courtWeight = Number(document.getElementById("court-weight").value);
    const partnerWeight = Number(
      document.getElementById("partner-weight").value
    );
    const serveWeight = Number(document.getElementById("serve-weight").value);

    output.textContent = "Generating...";
    scoreEl.textContent = "";

    setTimeout(() => {
      try {
        const { rounds, score } = generateBestSession(numSessions, numRounds, {
          courtWeight,
          partnerWeight,
          serveWeight,
        });
        output.textContent = renderSessionText(rounds);
        scoreEl.textContent = `score = ${score.toFixed(3)}`;
      } catch (err) {
        output.textContent = `Error: ${err.message}`;
      }
    }, 0);
  });

  form.dispatchEvent(new Event("submit"));
}

document.addEventListener("DOMContentLoaded", main);
