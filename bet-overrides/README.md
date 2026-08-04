# bet-overrides/

This directory holds Bet's own additions on top of `skyline69/balatro-mod-index`
(the `upstream` remote). It exists so that `git fetch upstream && git merge
upstream/main` stays a clean, conflict-free merge in the common case: nothing
in here shares a path with anything upstream owns (`mods/`, `schema/`,
`.github/workflows/check-mod.yml`, `.github/workflows/update-mod-versions.yml`,
`README.md`, `AGENTS.md`, `CLAUDE.md`). If a merge ever DOES conflict, it can
only be because upstream itself created a `bet-overrides/` folder, which is
not a realistic risk for a third-party public index — see
`.github/workflows/sync-upstream.yml`, which opens a PR instead of
force-merging on anything that isn't a clean fast-forward, specifically to
catch that edge case with a human in the loop rather than silently.

## Two ways to use this folder

**1. Overlay an existing upstream mod** (it's already in `mods/<slug>/`):

```
bet-overrides/<Author>@<ModName>/bet.json
```

`bet.json` fields, all optional (only set what you're overriding):

| Field | Type | Meaning |
|---|---|---|
| `allowedInRanked` | boolean | Whether this mod is allowed in ranked play. Defaults to `false` if never set. |
| `sha256` | string | SHA-256 of the current `downloadURL` archive, hex-encoded. There's no hash field in upstream's `meta.json` at all, and `build-index.yml` deliberately does NOT fetch+hash every mod's archive on every build (slow, and most of the ~800 upstream mods will never be ranked-relevant) — curate this by hand for anything you actually mark `allowedInRanked`. |
| `rankedNotes` | string | Free-text note shown to admins on the ranked-mod-profiles admin page. |
| `categoryOverride` | string[] | Replaces upstream's `categories` in the built index, if upstream's own categorization is wrong/unhelpful for our purposes. |

**2. Add a Bet-exclusive mod** (not in upstream's index at all):

```
bet-overrides/<Author>@<ModName>/meta.json       # same shape as upstream's meta.json -- see schema/meta.schema.json
bet-overrides/<Author>@<ModName>/bet.json         # same fields as above
bet-overrides/<Author>@<ModName>/description.md   # optional
```

`build-index.yml` left-joins `mods/*` with `bet-overrides/*` by folder slug: an
upstream-only folder gets `allowedInRanked: false` / no hash; an overlaid
folder merges upstream's `meta.json` with this folder's `bet.json`; a
`bet-overrides`-only folder (no matching `mods/` folder) is built entirely
from its own `meta.json` + `bet.json`. See `.github/scripts/build_index.py`
for the exact merge logic and `dist/mods-index.json`'s output shape (that
file is what `BalatroMultiplayerServer`'s hourly sync job actually fetches
— see that repo's `apps/server/src/features/mods/mods-sync.service.ts`).

## Example

`bet-overrides/1RedOne@FickleFox/bet.json` in this same commit overlays the
real upstream `mods/1RedOne@FickleFox/` entry as a working example of case 1
above — replace/remove it once real ranked-mod curation starts.
