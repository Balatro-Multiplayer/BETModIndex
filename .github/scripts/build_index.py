#!/usr/bin/env python3
"""Builds dist/mods-index.json -- the single combined artifact
BalatroMultiplayerServer's mods-sync.service.ts fetches over plain HTTPS
(no GitHub token, no API rate limits) to populate its mod_registry table.

Left-joins mods/<slug>/meta.json (upstream, skyline69/balatro-mod-index) with
bet-overrides/<slug>/bet.json (this fork's overlay -- see bet-overrides/README.md)
by folder slug:
  - upstream-only slug  -> allowedInRanked defaults to false, no hash
  - overlaid slug        -> upstream meta.json fields + bet.json's overrides
  - bet-overrides-only    -> entirely from bet-overrides/<slug>/{meta.json,bet.json}
    slug (Bet-exclusive mod, not in upstream's index at all)

Deliberately stdlib-only (json/hashlib/pathlib/datetime) -- this only needs to
run in CI on every push to main, no point adding a dependency footprint for
something this small.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODS_DIR = REPO_ROOT / "mods"
OVERRIDES_DIR = REPO_ROOT / "bet-overrides"
DIST_DIR = REPO_ROOT / "dist"
OUTPUT_PATH = DIST_DIR / "mods-index.json"

# Used to build thumbnail URLs pointing at this repo's own raw content (on
# `main`, where mods/*/thumbnail.jpg actually lives -- not `dist`, which only
# ever holds mods-index.json). mods-sync.service.ts treats a null
# thumbnailUrl as "no thumbnail", not an error, so this can be safely blanked
# out again if this repo is ever forked further under a different name/org.
RAW_BASE_URL: str | None = "https://raw.githubusercontent.com/Balatro-Multiplayer/BETModIndex/main"


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_description(folder: Path) -> str | None:
    desc_path = folder / "description.md"
    if not desc_path.exists():
        return None
    text = desc_path.read_text(encoding="utf-8").strip()
    return text or None


def thumbnail_url(folder: Path, slug: str) -> str | None:
    if not (folder / "thumbnail.jpg").exists():
        return None
    if RAW_BASE_URL is None:
        return None
    return f"{RAW_BASE_URL}/{folder.relative_to(REPO_ROOT).parent.name}/{slug}/thumbnail.jpg"


def released_at_iso(meta: dict) -> str | None:
    ts = meta.get("last-updated")
    if not isinstance(ts, (int, float)):
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def build_entry(slug: str, meta: dict, folder: Path, override: dict) -> dict:
    version = override.get("version") or meta.get("version")
    download_url = meta.get("downloadURL")

    return {
        "id": slug,
        "title": meta.get("title", slug),
        "author": meta.get("author", "unknown"),
        "categories": override.get("categoryOverride") or meta.get("categories", []),
        "requiresSteamodded": bool(meta.get("requires-steamodded", True)),
        "requiresTalisman": bool(meta.get("requires-talisman", False)),
        "repoUrl": meta.get("repo"),
        "thumbnailUrl": thumbnail_url(folder, slug),
        "description": read_description(folder),
        "latestVersion": version,
        "latestDownloadUrl": download_url,
        # No hash here -- BalatroMultiplayerAPI-Server's mods-sync.service.ts
        # computes sha256 itself by fetching latestDownloadUrl, rather than
        # trusting a value curated in this index. See bet-overrides/README.md.
        "allowedInRanked": bool(override.get("allowedInRanked", False)),
        "versions": (
            [
                {
                    "version": version,
                    "downloadUrl": download_url,
                    "releasedAt": released_at_iso(meta),
                }
            ]
            if version
            else []
        ),
    }


def load_override(slug: str) -> tuple[dict, Path | None]:
    folder = OVERRIDES_DIR / slug
    bet_json = folder / "bet.json"
    if not bet_json.exists():
        return {}, None
    return read_json(bet_json), folder


def main() -> int:
    if not MODS_DIR.exists():
        print(f"error: {MODS_DIR} does not exist", file=sys.stderr)
        return 1

    entries: dict[str, dict] = {}

    # Pass 1: every upstream mod, optionally overlaid. A handful of upstream
    # meta.json files are known to have slipped past check-mod.yml with
    # invalid JSON (trailing commas, stray control characters) -- skip those
    # with a warning rather than failing the whole build over an unrelated
    # mod we may not even care about.
    skipped = 0
    for mod_folder in sorted(MODS_DIR.iterdir()):
        if not mod_folder.is_dir():
            continue
        meta_path = mod_folder / "meta.json"
        if not meta_path.exists():
            continue
        slug = mod_folder.name
        try:
            meta = read_json(meta_path)
        except json.JSONDecodeError as e:
            print(f"warning: skipping {slug} -- invalid JSON in meta.json: {e}", file=sys.stderr)
            skipped += 1
            continue
        override, _ = load_override(slug)
        entries[slug] = build_entry(slug, meta, mod_folder, override)

    # Pass 2: Bet-exclusive mods -- a bet-overrides/<slug>/ with its own
    # meta.json and no matching mods/<slug>/ folder at all.
    if OVERRIDES_DIR.exists():
        for override_folder in sorted(OVERRIDES_DIR.iterdir()):
            if not override_folder.is_dir():
                continue
            slug = override_folder.name
            if slug in entries:
                continue
            meta_path = override_folder / "meta.json"
            if not meta_path.exists():
                continue  # a bet.json-only overlay with no matching upstream mod is just orphaned, skip it
            meta = read_json(meta_path)
            override, _ = load_override(slug)
            entries[slug] = build_entry(slug, meta, override_folder, override)

    output = {
        "generatedAt": datetime.now(tz=timezone.utc).isoformat(),
        "mods": [entries[slug] for slug in sorted(entries)],
    }

    DIST_DIR.mkdir(exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
        f.write("\n")

    print(f"Wrote {len(output['mods'])} mods to {OUTPUT_PATH}" + (f" ({skipped} skipped)" if skipped else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
