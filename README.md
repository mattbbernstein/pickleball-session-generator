# Pickleball Session Generator

Generates randomized doubles pickleball session schedules (8 players, 2 courts)
and scores them on how much players rotate courts, partners, and serving turns.

## Setup

Requires [uv](https://docs.astral.sh/uv/). uv creates and manages the `.venv`
automatically — no manual `venv`/`pip` steps needed:

```bash
uv sync --group build
```

(Omit `--group build` if you only want to run the script and don't need
PyInstaller for building an executable.)

## Usage

Run interactively (prompts for options):
```bash
uv run src/best_session.py
```

Or pass arguments directly:
```bash
uv run src/best_session.py 1000 --rounds 6 --court-weight 1 --partner-weight 2 --serve-weight 1
```

## Building a standalone executable

```bash
uv run build.py
```

The executable is written to `dist/pickleball-session-generator`
(`dist/pickleball-session-generator.exe` on Windows). PyInstaller does not
cross-compile — build on macOS for a macOS binary, on Windows for a
Windows `.exe`.

## Web app

A static, dependency-free JS port of the same logic lives in `web/` and is
deployed to GitHub Pages on every push to `main` that touches that
directory (see `.github/workflows/pages.yml`).

To enable Pages for this repo (one-time): Settings → Pages → Source →
"GitHub Actions".

To run it locally:

```bash
cd web && python3 -m http.server 8000
```

then open <http://localhost:8000>.

## Files

- `src/pickleball_round.py` — `PickleballRound`: one round's court/team/serve assignment
- `src/pickleball_session.py` — `PickleballSession`: N rounds plus the variety heuristic score
- `src/best_session.py` — CLI/interactive entry point: generates N sessions, prints the best
- `build.py` — cross-platform PyInstaller build script (stays in project root)
- `web/` — static HTML/JS port of the generator, deployed to GitHub Pages
