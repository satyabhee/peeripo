# PeerIPO

Private, opt-in friend-group app that turns location (Life360), grades (Canvas),
listening habits (Spotify), manually-scored events, and manually-scored "aura"
into a fake stock price per friend.

## Layout

- `backend/` — FastAPI app + Postgres models. Source of truth for users, opt-ins,
  events, aura reviews, and stock price history.
- `worker/` — scheduled jobs that pull external data and compute prices:
  - `life360_poller.py` — pulls circle member locations (unofficial API, using
    the admin's own login since they're already a Circle member).
  - `canvas_poller.py` — pulls grades via Canvas's official REST API using each
    friend's self-generated personal access token.
  - `spotify_poller.py` — pulls listening stats via Spotify's official OAuth API.
  - `screenshot_watcher.py` — watches a folder for group-chat screenshots (dropped
    in via a phone automation you control) and uses Claude's vision to suggest
    "aura" scores for admin approval. Never talks to Instagram directly.
  - `stock_engine.py` — Kalman-smooths raw location pings into place-time
    estimates, rolls everything into a daily fundamentals score, and feeds that
    into a geometric Brownian motion model to produce the actual stock price.
  - `kalman.py`, `geofence.py` — supporting math (constant-velocity Kalman
    filter, haversine distance for geofencing).
- `frontend/` — Next.js app: leaderboard, per-friend stock chart, opt-in
  settings page, admin page for approving aura suggestions.

## Setup

1. `cp .env.example .env` and fill in credentials. Generate `TOKEN_ENCRYPTION_KEY`
   with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`.
2. `docker compose up -d db backend worker screenshot-watcher`
3. `cd frontend && npm install && npm run dev`

## Known tradeoffs (read before extending)

- Canvas and Spotify integrations use official, sanctioned APIs with per-user
  tokens each friend generates and can revoke themselves — no scraping.
- Aura scoring intentionally never automates access to Instagram. It only reads
  screenshots you already have on disk, to avoid the account-ban/ToS risk of an
  unofficial Instagram API client.
- Every data category has a per-user opt-in row (`opt_ins` table); the pollers
  and stock engine only pull data for users who've explicitly enabled it.
