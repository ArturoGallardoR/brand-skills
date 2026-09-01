#!/usr/bin/env python3
"""Cross-platform brand package scaffold/index helper.

Works on Windows PowerShell, macOS, and Linux with Python 3 and no third-party
packages. It mirrors brand.sh while avoiding Bash/Unix-only dependencies.
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
import unicodedata
from datetime import date as _date
from pathlib import Path

ARTIFACTS = (
    "context",
    "naming",
    "strategy",
    "architecture",
    "identity",
    "voice",
    "messaging",
    "positioning",
    "story",
    "guidelines",
    "audit",
)


def fail(message: str) -> "NoReturn":
    print(f"brand.py: {message}", file=sys.stderr)
    raise SystemExit(1)


def clean_scalar(value: str) -> str:
    """Keep the line-oriented YAML format safe from accidental line injection."""
    return " ".join(str(value).replace("\r", " ").replace("\n", " ").split())


def slugify(value: str) -> str:
    ascii_value = (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )
    return re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def cmd_init(args: argparse.Namespace) -> None:
    name = clean_scalar(args.name)
    slug = clean_scalar(args.slug or slugify(name))
    if not slug:
        fail("could not derive a non-empty slug; pass --slug explicitly")
    oneliner = clean_scalar(args.one_liner or "")
    out = Path(args.out or "brand")
    run_date = args.date or _date.today().isoformat()
    manifest = out / "brand.yaml"

    if manifest.exists():
        fail(f"package already exists at {out}/ (refusing to overwrite)")

    (out / "assets").mkdir(parents=True, exist_ok=True)
    lines = [
        "schema_version: 1",
        f"slug: {slug}",
        f"name: {name}",
        f"one_liner: {oneliner}",
        'tagline: ""',
        'archetype: ""',
        "status: draft",
        'stage: ""',
        'industry: ""',
        "languages: [en]",
        "links:",
        '  domain: ""',
        '  repo: ""',
        f"created: {run_date}",
        f"updated: {run_date}",
        "version: 1",
        "artifacts:",
    ]
    lines.extend(f"  {artifact}: false" for artifact in ARTIFACTS)
    write_text(manifest, "\n".join(lines) + "\n")
    print(f"created package: {out}/ (brand.yaml + assets/)")

    if args.register:
        registry = Path(args.register)
        registry.parent.mkdir(parents=True, exist_ok=True)
        if not registry.exists():
            write_text(registry, "schema_version: 1\nbrands:\n")

        text = registry.read_text(encoding="utf-8")
        slug_re = re.compile(rf"^\s*-\s*slug:\s*{re.escape(slug)}\s*$", re.MULTILINE)
        if slug_re.search(text):
            print(f"registry: {slug} already present in {registry} (skipped)")
        else:
            if text and not text.endswith("\n"):
                text += "\n"
            text += (
                f"  - slug: {slug}\n"
                f"    name: {name}\n"
                f"    one_liner: {oneliner}\n"
                f"    path: {out}\n"
                "    status: draft\n"
                f"    created: {run_date}\n"
            )
            write_text(registry, text)
            print(f"registry: registered {slug} in {registry}")


def cmd_list(args: argparse.Namespace) -> None:
    registry = Path(args.registry or "brands/registry.yaml")
    if not registry.is_file():
        fail(f"no registry at {registry}")

    current: dict[str, str] | None = None
    rows: list[dict[str, str]] = []
    for line in registry.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\s*-\s*slug:\s*(.*)$", line)
        if match:
            if current:
                rows.append(current)
            current = {"slug": match.group(1).strip()}
            continue
        if current is None:
            continue
        match = re.match(r"^\s+(name|one_liner|path|status):\s*(.*)$", line)
        if match:
            current[match.group(1)] = match.group(2).strip()
    if current:
        rows.append(current)

    for row in rows:
        print(
            f"{row.get('slug', '')} · {row.get('name', '')} · "
            f"{row.get('one_liner', '')} · {row.get('path', '')} "
            f"[{row.get('status', '')}]"
        )


def cmd_set(args: argparse.Namespace) -> None:
    package = Path(args.package)
    key = args.key
    value = clean_scalar(args.value or "")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
        fail(f"invalid key: {key!r}")
    manifest = package / "brand.yaml"
    if not manifest.is_file():
        fail(f"no brand.yaml in {package}")

    lines = manifest.read_text(encoding="utf-8").splitlines()
    pattern = re.compile(rf"^{re.escape(key)}:")
    found = False
    for index, line in enumerate(lines):
        if pattern.match(line):
            lines[index] = f"{key}: {value}"
            found = True
            break
    if not found:
        fail(f"key {key!r} not found in {manifest}")

    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="\n", delete=False, dir=manifest.parent
    ) as handle:
        handle.write("\n".join(lines) + "\n")
        temp_path = Path(handle.name)
    temp_path.replace(manifest)
    print(f"set {key} in {manifest}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="brand.py", description="Scaffold and index Brand Skills packages."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Create a brand package")
    init.add_argument("--name", required=True)
    init.add_argument("--slug")
    init.add_argument("--one-liner", default="")
    init.add_argument("--out", default="brand")
    init.add_argument("--date")
    init.add_argument("--register")
    init.set_defaults(func=cmd_init)

    list_parser = sub.add_parser("list", help="List brands in a registry")
    list_parser.add_argument("--registry", default="brands/registry.yaml")
    list_parser.set_defaults(func=cmd_list)

    set_parser = sub.add_parser("set", help="Update a top-level brand.yaml scalar")
    set_parser.add_argument("--package", required=True)
    set_parser.add_argument("--key", required=True)
    set_parser.add_argument("--value", default="")
    set_parser.set_defaults(func=cmd_set)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
