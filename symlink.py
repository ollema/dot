"""Symlink dotfiles from this repository to their target locations."""

import shutil
import sys
from pathlib import Path

from tools import TOOLS, Link

REPO_ROOT = Path(__file__).resolve().parent

STANDALONE_LINKS: list[Link] = [
    Link(source="ghostty", target="~/.config/ghostty"),
    Link(source="git/shared", target="~/.config/git/shared"),
]

LINKS: list[Link] = [link for tool in TOOLS for link in tool.symlinks] + STANDALONE_LINKS


def resolve(link: Link) -> tuple[Path, Path]:
    source = REPO_ROOT / link.source
    target = Path(link.target).expanduser()
    return source, target


def apply_link(link: Link, *, dry_run: bool) -> None:
    source, target = resolve(link)
    prefix = "[dry-run] " if dry_run else ""
    print(f"  {link.source} -> {link.target}")

    if not source.exists():
        print(f"    ERROR: source missing: {source}")
        return

    if target.is_symlink() and target.readlink() == source:
        print("    ok (already linked)")
        return

    parent = target.parent
    existed = target.exists(follow_symlinks=False)

    if dry_run:
        if existed:
            kind = "dir" if target.is_dir() and not target.is_symlink() else "file/symlink"
            print(f"    {prefix}would replace existing {kind}")
        else:
            print(f"    {prefix}would create")
        return

    parent.mkdir(parents=True, exist_ok=True)

    if existed:
        if target.is_symlink() or target.is_file():
            target.unlink()
            action = "replaced existing file/symlink"
        else:
            shutil.rmtree(target)
            action = "replaced existing dir"
    else:
        action = "created"

    target.symlink_to(source)
    print(f"    {action}")


def main() -> None:
    dry_run = "--dry-run" in sys.argv[1:]

    header = f"linking from {REPO_ROOT}"
    if dry_run:
        header += " (dry-run)"
    print(header + "\n")

    for link in LINKS:
        apply_link(link, dry_run=dry_run)

    print("\ndone.")


if __name__ == "__main__":
    main()
