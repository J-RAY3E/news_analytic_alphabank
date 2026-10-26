# Alfa Radar — Frontend

Next.js 14 (App Router) client for Alfa Radar: personalized feed, six-block
insight with typed claim labels, Agent Trace panel, follow-up chat, "test a new
news item" input, client/role switcher and feedback.

See the [root README](../README.md) for the full project, architecture and
`docker compose` quickstart.

## Run (dev)

```bash
npm install
npm run dev        # http://localhost:3000
```

Environment (`.env.local`, gitignored):

- `NEXT_PUBLIC_API_URL` — backend base URL (default `http://localhost:8000`).
- `NEXT_PUBLIC_USE_MOCKS` — `true` runs the UI against bundled mocks in
  `lib/mocks/` with no backend (offline demos); `false` (default in Docker)
  talks to the real API.

## Checks

```bash
npm run lint
npx tsc --noEmit
npm run build
```

## Layout

```
app/            routes: home (radar widget), /radar workspace, /login
components/     feed, insight, claim, trace, chat, news, layout, ui
lib/api/        typed client, react-query hooks, contract types
lib/mocks/      offline mock data + dispatcher
```

Contract types mirror `contracts/openapi.json`. With mocks off, every screen is
served by the FastAPI backend.
