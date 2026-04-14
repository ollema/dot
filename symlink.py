#!/usr/bin/env python3
"""Symlink dotfiles from this repository to their target locations."""

from __future__ import annotations

import os
import shutil
import sys
from dataclasses import dataclass

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))


@dataclass
class Link:
    source: str  # path relative to repo root
    target: str  # path with ~ to be expanded


LINKS: list[Link] = [
    Link(source="fish", target="~/.config/fish"),
    Link(source="ghostty", target="~/.config/ghostty"),
    Link(source="starship/starship.toml", target="~/.config/starship.toml"),
]


def resolve(link: Link) -> tuple[str, str]:
    source = os.path.join(REPO_ROOT, link.source)
    target = os.path.expanduser(link.target)
    return source, target


def apply_link(link: Link, dry_run: bool) -> None:
    source, target = resolve(link)
    prefix = "[dry-run] " if dry_run else ""
    print(f"  {link.source} -> {link.target}")

    if not os.path.exists(source):
        print(f"    ERROR: source missing: {source}")
        return

    if os.path.islink(target) and os.readlink(target) == source:
        print("    ok (already linked)")
        return

    parent = os.path.dirname(target)
    existed = os.path.lexists(target)

    if dry_run:
        if existed:
            kind = "dir" if os.path.isdir(target) and not os.path.islink(target) else "file/symlink"
            print(f"    {prefix}would replace existing {kind}")
        else:
            print(f"    {prefix}would create")
        return

    os.makedirs(parent, exist_ok=True)

    if existed:
        if os.path.islink(target) or os.path.isfile(target):
            os.unlink(target)
            action = "replaced existing file/symlink"
        else:
            shutil.rmtree(target)
            action = "replaced existing dir"
    else:
        action = "created"

    os.symlink(source, target)
    print(f"    {action}")


def main() -> None:
    dry_run = "--dry-run" in sys.argv[1:]

    header = f"linking from {REPO_ROOT}"
    if dry_run:
        header += " (dry-run)"
    print(header + "\n")

    for link in LINKS:
        apply_link(link, dry_run)

    print("\ndone.")


if __name__ == "__main__":
    main()
