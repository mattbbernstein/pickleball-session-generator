# Pickleball Session Generator

Generates randomized doubles pickleball session schedules (8 players, 2 courts)
and scores them on how much players rotate courts, partners, and serving turns.

## Web app

A static, dependency-free JS app lives in `web/` and is deployed to GitHub
Pages on every push to `main` that touches that directory (see
`.github/workflows/pages.yml`).

To enable Pages for this repo (one-time): Settings → Pages → Source →
"GitHub Actions".

To run it locally, serve `web/` with any static file server, e.g.:

```bash
npx serve web
```

## Files

- `web/app.js` — round/session generation and the variety heuristic scoring
- `web/index.html` — page shell and options form
