#!/usr/bin/env python3
"""Cross-platform repository validator for Brand Skills (Python stdlib only)."""
from __future__ import annotations

import json
import re
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    skills_root = root / "skills"
    manifest_path = root / ".claude-plugin" / "marketplace.json"
    failed = False

    print("-> Validating skills/*/SKILL.md frontmatter")
    disk_skills: set[str] = set()
    for directory in sorted(path for path in skills_root.iterdir() if path.is_dir()):
        name = directory.name
        disk_skills.add(name)
        skill_file = directory / "SKILL.md"
        ok = True
        if not skill_file.is_file():
            print(f"  X {name}: missing SKILL.md")
            failed = True
            continue
        text = skill_file.read_text(encoding="utf-8")
        if not re.search(r"(?m)^name:\s*\S+", text):
            print(f"  X {name}: SKILL.md missing 'name:'")
            failed = True
            ok = False
        if not re.search(r"(?m)^description:\s*\S+", text):
            print(f"  X {name}: SKILL.md missing 'description:'")
            failed = True
            ok = False
        if ok:
            print(f"  OK {name}")

    print("-> Cross-checking marketplace manifest <-> disk")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"  X cannot read {manifest_path}: {exc}")
        return 1

    plugins = manifest.get("plugins") or []
    if not plugins:
        print("  X marketplace manifest has no plugins")
        return 1

    plugin = plugins[0]
    listed_raw = plugin.get("skills") or []
    if listed_raw and plugin.get("strict") is not True:
        print('  X manifest lists "skills" explicitly but "strict" is not true; plugin will fail to load')
        failed = True

    listed_skills = {
        str(item).replace("\\", "/").removeprefix("./skills/").strip("/")
        for item in listed_raw
    }

    for name in sorted(listed_skills - disk_skills):
        print(f"  X manifest lists skills/{name} but it is missing on disk")
        failed = True
    for name in sorted(disk_skills - listed_skills):
        print(f"  X skills/{name} on disk but not in manifest")
        failed = True

    if failed:
        print("X validation failed")
        return 1
    print("OK all skills valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
