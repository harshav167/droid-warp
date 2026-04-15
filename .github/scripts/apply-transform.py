#!/usr/bin/env python3
"""
Transform upstream warpdotdev/claude-code-warp into droid-compatible plugin.

Runs after `git merge upstream/main`. Idempotent — safe to run repeatedly.
Keeps the diff from upstream as small as possible so merges stay clean.

Changes:
1. hooks.json: ${CLAUDE_PLUGIN_ROOT} -> ${DROID_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}
   Works in droid (DROID_PLUGIN_ROOT is set) and Claude Code (fallback).
2. plugin.json: name/description/homepage -> droid-warp branding.
"""
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
HOOKS = REPO / "plugins/warp/hooks/hooks.json"
MANIFEST = REPO / "plugins/warp/.claude-plugin/plugin.json"

OLD_VAR = "${CLAUDE_PLUGIN_ROOT}"
NEW_VAR = "${DROID_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}"

DROID_NAME = "droid-warp"
DROID_DESC = (
    "Warp terminal integration for Factory droid - native notifications "
    "(forked from warpdotdev/claude-code-warp)"
)
DROID_HOMEPAGE = "https://github.com/harshav167/droid-warp"

changed = False


def patch_hooks() -> None:
    global changed
    if not HOOKS.exists():
        print(f"skip: {HOOKS} not found", file=sys.stderr)
        return
    text = HOOKS.read_text()
    if NEW_VAR in text and OLD_VAR not in text.replace(NEW_VAR, ""):
        return  # already transformed
    new = text.replace(OLD_VAR, NEW_VAR)
    if new != text:
        HOOKS.write_text(new)
        print(f"patched {HOOKS.relative_to(REPO)}")
        changed = True


def patch_manifest() -> None:
    global changed
    if not MANIFEST.exists():
        print(f"skip: {MANIFEST} not found", file=sys.stderr)
        return
    raw = MANIFEST.read_text()
    data = json.loads(raw)
    desired = {
        "name": DROID_NAME,
        "description": DROID_DESC,
        "homepage": DROID_HOMEPAGE,
    }
    if all(data.get(k) == v for k, v in desired.items()):
        return
    data.update(desired)
    # Preserve 2-space indent + trailing newline to match upstream style.
    MANIFEST.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"patched {MANIFEST.relative_to(REPO)}")
    changed = True


def main() -> int:
    patch_hooks()
    patch_manifest()
    if changed:
        print("transform applied")
    else:
        print("transform already applied — no changes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
