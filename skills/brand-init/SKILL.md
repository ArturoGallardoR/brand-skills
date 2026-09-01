---
name: brand-init
description: Initialize a structured, versioned brand package and optionally register it in a brand portfolio. Use when starting a brand from scratch, creating a brand project/package, migrating legacy brand context, or before other Brand Skills when no brand.yaml exists. Works cross-platform on Windows PowerShell, macOS, Linux, Claude Code, Codex, Cursor, OpenCode, Empryo, Pi, and other Agent Skills compatible harnesses.
---

# Brand Init

Use [SKILL.core.md](SKILL.core.md) as the canonical brand-package methodology and data model.

## Cross-platform execution rules

- Never require Bash, WSL, Git Bash, `sed`, `awk`, `grep`, `date`, or `${CLAUDE_SKILL_DIR}`.
- Resolve bundled files relative to this skill directory using the harness file tools.
- Prefer the Python 3 helper because it is the single cross-platform implementation.
- On Windows PowerShell, use `scripts/brand.ps1` when a PowerShell entrypoint is preferable. It delegates to the same Python implementation.
- On macOS/Linux, use `python3 scripts/brand.py ...`. The legacy `scripts/brand.sh` remains only for backwards compatibility.
- If Python is unavailable, reproduce the small file operation directly with the harness file tools rather than attempting to install Bash.

## Commands

### Windows PowerShell

```powershell
./scripts/brand.ps1 init --name "Acme" --one-liner "..." --out brand --date "2026-09-01"
./scripts/brand.ps1 list --registry brands/registry.yaml
./scripts/brand.ps1 set --package brand --key one_liner --value "Updated description"
```

Use `--register brands/registry.yaml` on `init` only when managing a portfolio.

### Cross-platform Python

```text
python scripts/brand.py init --name "Acme" --one-liner "..." --out brand --date "2026-09-01"
python scripts/brand.py list --registry brands/registry.yaml
python scripts/brand.py set --package brand --key one_liner --value "Updated description"
```

On systems where the executable is named `python3`, substitute `python3` for `python`.

## Required behavior

1. Read `brand.yaml` first if one already exists; never reinitialize it.
2. Ask only for the minimum fields needed to scaffold the package. Deep discovery belongs to `brand-context`.
3. Create only `brand.yaml` and `assets/` during initialization; downstream skills create their own artifacts.
4. Never overwrite an existing package.
5. Treat the registry as the durable SSOT, not agent memory.
6. After initialization, hand off to `brand-context`, then the relevant strategy/naming/identity skills.
