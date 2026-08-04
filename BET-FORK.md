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

## One-time setup once this repo exists on GitHub

1. Create the fork as `<org>/BETModIndex` (or whatever name/org you actually
   use -- update this doc and `.github/scripts/build_index.py`'s
   `RAW_BASE_URL` placeholder to match).
2. Push this local clone's history to it (`git remote add origin <url> && git
   push origin main`). `upstream` should stay pointed at
   `skyline69/balatro-mod-index`.
3. `sync-upstream.yml` and `build-index.yml` both use the default
   `GITHUB_TOKEN` (contents: write, pull-requests: write) -- no extra secrets
   needed for the fork itself.
4. After the first `build-index.yml` run, a `dist` branch will exist
   containing `mods-index.json`. Set
   `BET_MOD_INDEX_URL=https://raw.githubusercontent.com/<org>/BETModIndex/dist/mods-index.json`
   in `BalatroMultiplayerServer`'s `apps/server/.env` (see that repo's
   `src/env.ts` and `src/features/mods/mods-sync.service.ts`) -- its hourly
   sync job no-ops with a log line until this is set.

## Local testing

```sh
python3 .github/scripts/build_index.py   # writes dist/mods-index.json (gitignored)
```

No dependencies beyond the Python 3 standard library.
