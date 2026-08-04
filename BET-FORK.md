# This is Bet's fork of balatro-mod-index

This repo is a fork of [`skyline69/balatro-mod-index`](https://github.com/skyline69/balatro-mod-index)
(MIT-licensed), forked for [Bet](https://github.com/) -- the Balatro mod
manager / anti-cheat launcher this index primarily serves. Everything
upstream owns (`mods/`, `schema/`, `README.md`, `AGENTS.md`, `CLAUDE.md`,
`.github/workflows/check-mod.yml`, `.github/workflows/update-mod-versions.yml`,
`.github/scripts/update_mod_versions.py`) is left untouched and stays in
sync with upstream automatically -- see `.github/workflows/sync-upstream.yml`.

This file, and everything under `bet-overrides/` and the two `bet-*.yml`
workflows, are Bet's own additions and deliberately live in paths upstream
will never write to, specifically so future upstream syncs stay conflict-free.
See `bet-overrides/README.md` for the actual override format.

## Status

Live at `Balatro-Multiplayer/BETModIndex`. `upstream` stays pointed at
`skyline69/balatro-mod-index`; `origin` is this fork. `sync-upstream.yml` and
`build-index.yml` both use the default `GITHUB_TOKEN` (contents: write,
pull-requests: write) -- no extra secrets needed for the fork itself.
`build-index.yml` has run at least once, so a `dist` branch exists containing
`mods-index.json`, fetchable at
`https://raw.githubusercontent.com/Balatro-Multiplayer/BETModIndex/dist/mods-index.json`
-- that's the value `BalatroMultiplayerAPI-Server`'s `apps/server/.env` sets
`BET_MOD_INDEX_URL` to (see that repo's `.env.example`,
`src/env.ts`, and `src/features/mods/mods-sync.service.ts` -- its hourly sync
job no-ops with a log line if this is ever unset).

## Local testing

```sh
python3 .github/scripts/build_index.py   # writes dist/mods-index.json (gitignored)
```

No dependencies beyond the Python 3 standard library.
