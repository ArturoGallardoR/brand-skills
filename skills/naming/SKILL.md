---
name: naming
description: Create and vet names for products, SaaS, brands, open-source projects, bots, and apps using metaphor-driven exploration, prior-art research, availability checks, and scored finalists. Use whenever a user needs to name or rename something. Works cross-platform on Windows PowerShell, macOS, Linux, Claude Code, Codex, Cursor, OpenCode, Empryo, Pi, and other Agent Skills compatible harnesses.
---

# Naming

Use [SKILL.core.md](SKILL.core.md) as the canonical naming methodology, reference map, filters, scoring model, and decision gates.

## Cross-platform execution rules

These rules override shell-specific examples in `SKILL.core.md`:

- Do not require Bash, WSL, Git Bash, `whois`, `curl`, `grep`, `sed`, `awk`, `gh`, or `${CLAUDE_SKILL_DIR}`.
- Resolve bundled files relative to this skill directory using the harness file tools.
- Use the bundled Python 3 availability helper for registry/domain screening. It uses Python stdlib HTTP/RDAP and therefore works natively from Windows PowerShell, cmd.exe, macOS, and Linux.
- On Windows PowerShell, `scripts/check-availability.ps1` is the preferred entrypoint. It delegates to the same Python implementation.
- On macOS/Linux, use `python3 scripts/check_availability.py ...`. The legacy `.sh` helper remains only for backwards compatibility.
- Use the harness/browser/search tools for prior-art searches, trademark screening, app stores, social handles, and any check that requires web research. Never downgrade those checks to memory-only guesses.
- If an automated endpoint is unreachable, mark the result `UNCLEAR`; never convert a network/tool failure into `AVAILABLE` or `TAKEN`.

## Availability helper

### Windows PowerShell

```powershell
./scripts/check-availability.ps1 "candidate" domain npm github pypi telegram
```

### Cross-platform Python

```text
python scripts/check_availability.py candidate domain npm github pypi telegram
```

On systems where the executable is named `python3`, substitute `python3` for `python`.

Supported automated platforms: `domain`, `npm`, `pypi`, `github`, `crates`, `rubygems`, `wp`, `telegram`.

Domain checks use RDAP rather than a local `whois` executable. npm, PyPI, GitHub, crates.io, and RubyGems use public HTTP APIs. These are screening checks, not trademark clearance.

## Mandatory workflow

1. Build the naming brief before generating names.
2. Explore metaphors/territories before candidate generation.
3. Generate and filter candidates internally; do not dump raw brainstorm lists on the user.
4. Before availability checks, perform prior-art searches in the product category, general web, GitHub by name/stars, and trademark sources when the name is headed to market.
5. Run platform availability checks for every surviving semifinalist. Use the platform helper above where supported.
6. Drop direct competitors and serious same-audience namespace conflicts.
7. Score only survivors and present 3 to 5 vetted finalists with story, availability status, risks, and taglines.
8. If fewer than three strong candidates survive, loop back to new territories rather than lowering the bar.

## Reference loading

Load only the references needed for the current stage, as directed by `SKILL.core.md`. Do not load the entire naming reference library into context at once.
