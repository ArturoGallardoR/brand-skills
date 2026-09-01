#!/usr/bin/env python3
"""Cross-platform quick availability checks for candidate brand/product names.

Uses only Python's standard library, so it can run directly from PowerShell,
cmd.exe, Bash, zsh, or any agent harness with Python 3. Automated checks are a
screening aid, not trademark clearance.
"""
from __future__ import annotations

import argparse
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_PLATFORMS = ("domain", "github", "npm")
VALID_PLATFORMS = ("domain", "npm", "pypi", "github", "crates", "rubygems", "wp", "telegram")
USER_AGENT = "brand-skills-availability/1.0 (+https://github.com/ArturoGallardoR/brand-skills)"


def request(url: str, *, timeout: float, read_body: bool = False) -> tuple[int, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = ""
            if read_body:
                body = response.read(1_000_000).decode("utf-8", errors="replace")
            return int(response.status), body
    except urllib.error.HTTPError as exc:
        body = ""
        if read_body:
            try:
                body = exc.read(1_000_000).decode("utf-8", errors="replace")
            except Exception:
                pass
        return int(exc.code), body
    except (urllib.error.URLError, TimeoutError, OSError):
        return 0, ""


def available(label: str) -> None:
    print(f"  AVAILABLE  {label}")


def taken(label: str) -> None:
    print(f"  TAKEN      {label}")


def unclear(label: str) -> None:
    print(f"  UNCLEAR    {label}")


def status_from_api(label: str, url: str, timeout: float) -> None:
    code, _ = request(url, timeout=timeout)
    if code == 404:
        available(label)
    elif 200 <= code < 400:
        taken(f"{label} (HTTP {code})")
    elif code == 0:
        unclear(f"{label} (no HTTP response; verify manually)")
    else:
        unclear(f"{label} (HTTP {code}; verify manually)")


def check_domain(name: str, timeout: float) -> None:
    # RDAP checks registration state and avoids a whois executable dependency on Windows.
    for tld in ("com", "dev", "io"):
        domain = f"{name}.{tld}"
        code, _ = request(f"https://rdap.org/domain/{urllib.parse.quote(domain)}", timeout=timeout)
        if code == 404:
            available(domain)
        elif 200 <= code < 400:
            taken(domain)
        elif code == 0:
            unclear(f"{domain} (RDAP unreachable; verify at registrar)")
        else:
            unclear(f"{domain} (RDAP HTTP {code}; verify at registrar)")


def check_npm(name: str, timeout: float) -> None:
    encoded = urllib.parse.quote(name, safe="")
    status_from_api(f"npm: {name}", f"https://registry.npmjs.org/{encoded}", timeout)


def check_pypi(name: str, timeout: float) -> None:
    encoded = urllib.parse.quote(name, safe="")
    status_from_api(f"PyPI: {name}", f"https://pypi.org/pypi/{encoded}/json", timeout)


def check_github(name: str, timeout: float) -> None:
    encoded = urllib.parse.quote(name, safe="")
    status_from_api(f"GitHub account/org: {name}", f"https://api.github.com/users/{encoded}", timeout)


def check_crates(name: str, timeout: float) -> None:
    encoded = urllib.parse.quote(name, safe="")
    status_from_api(f"crates.io: {name}", f"https://crates.io/api/v1/crates/{encoded}", timeout)


def check_rubygems(name: str, timeout: float) -> None:
    encoded = urllib.parse.quote(name, safe="")
    status_from_api(f"RubyGems: {name}", f"https://rubygems.org/api/v1/gems/{encoded}.json", timeout)


def check_wp(name: str, timeout: float) -> None:
    query = urllib.parse.urlencode({"action": "plugin_information", "slug": name})
    code, body = request(
        f"https://api.wordpress.org/plugins/info/1.2/?{query}",
        timeout=timeout,
        read_body=True,
    )
    if code == 0:
        unclear(f"WP plugin: {name} (no HTTP response; verify manually)")
    elif "plugin not found" in body.lower() or "not found" in body.lower():
        available(f"WP plugin: {name}")
    elif 200 <= code < 400:
        taken(f"WP plugin: {name}")
    else:
        unclear(f"WP plugin: {name} (HTTP {code}; verify manually)")


def check_telegram(name: str, timeout: float) -> None:
    code, body = request(
        f"https://t.me/{urllib.parse.quote(name, safe='')}",
        timeout=timeout,
        read_body=True,
    )
    if code == 0:
        unclear(f"Telegram: @{name} (no HTTP response; verify in app)")
    elif "tgme_page_title" in body:
        taken(f"Telegram: @{name}")
    else:
        unclear(f"Telegram: @{name} (no public profile found; may be available, verify in app)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Quick cross-platform availability checks for a candidate name."
    )
    parser.add_argument("name")
    parser.add_argument("platforms", nargs="*", choices=VALID_PLATFORMS)
    parser.add_argument("--timeout", type=float, default=12.0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    platforms = args.platforms or list(DEFAULT_PLATFORMS)
    print(f"Checking availability for: {args.name}")
    print("---")

    checks = {
        "domain": check_domain,
        "npm": check_npm,
        "pypi": check_pypi,
        "github": check_github,
        "crates": check_crates,
        "rubygems": check_rubygems,
        "wp": check_wp,
        "telegram": check_telegram,
    }
    for platform in platforms:
        checks[platform](args.name, args.timeout)

    print("---")
    print("Note: automated checks can give false positives. Always verify manually before committing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
