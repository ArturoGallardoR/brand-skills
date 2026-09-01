# Windows / PowerShell support

This fork supports native Windows PowerShell without WSL, Git Bash, or Unix command-line tools.

## Install globally

```powershell
npx skills add ArturoGallardoR/brand-skills -g
```

## Runtime requirements

- PowerShell 7+ is recommended on Windows.
- Python 3 is required only for the deterministic helper scripts (`brand-init` scaffolding, naming availability checks, and repository validation). The wrappers automatically use `py -3` when available, then fall back to `python`.
- Node/npm is needed only for the `npx skills` installer, not for Brand Skills reasoning itself.

No WSL, Bash, `whois`, `curl`, `grep`, `sed`, or `awk` is required on Windows.

## Native PowerShell helpers

```powershell
# Brand package initialization
./skills/brand-init/scripts/brand.ps1 init --name "Acme" --out brand --date "2026-09-01"

# Brand registry
./skills/brand-init/scripts/brand.ps1 list --registry brands/registry.yaml

# Naming availability screening
./skills/naming/scripts/check-availability.ps1 "acme" domain npm github pypi telegram

# Repository validation
./scripts/validate-skills.ps1
```

The `.ps1` files are thin launchers over Python stdlib implementations. This keeps behavior identical across Windows, macOS, Linux, and agent harnesses while retaining the original `.sh` helpers for backwards compatibility.

## Agent/harness compatibility

The `brand-init` and `naming` entrypoints no longer depend on `${CLAUDE_SKILL_DIR}` or Bash-only `allowed-tools`. They explicitly instruct agents to resolve bundled files relative to the skill directory and choose the native Windows/PowerShell or portable Python helper.

This makes the suite suitable for Empryo, Pi, Codex, OpenCode, Cursor, Claude Code, and other Agent Skills compatible harnesses, assuming the harness can read/write files and execute local commands when a helper is needed.

## CI

GitHub Actions validates the portable helpers on:

- `windows-latest`
- `ubuntu-latest`
- `macos-latest`

Windows CI also invokes the PowerShell validation wrapper directly. Unix CI keeps checking the legacy Bash validator so compatibility is not regressed in either direction.
