"""Symlink dotfiles from this repository to their target locations."""

import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from rich.table import Table

from tools import TOOLS, Link
from ui import console, install_tracebacks

REPO_ROOT = Path(__file__).resolve().parent

STANDALONE_LINKS: list[Link] = [
    Link(source="ghostty", target="~/.config/ghostty"),
    Link(source="git/shared", target="~/.config/git/shared"),
    Link(source="ssh/config", target="~/.ssh/config"),
]

LINKS: list[Link] = [link for tool in TOOLS for link in tool.symlinks] + STANDALONE_LINKS


@dataclass
class LinkResult:
    link: Link
    status: str


def resolve(link: Link) -> tuple[Path, Path]:
    source = REPO_ROOT / link.source
    target = Path(link.target).expanduser()
    return source, target


def apply_link(link: Link, *, dry_run: bool) -> LinkResult:
    source, target = resolve(link)

    if not source.exists():
        return LinkResult(link, f"[red]source missing: {source}[/]")

    if target.is_symlink() and target.readlink() == source:
        return LinkResult(link, "[dim]already linked[/]")

    parent = target.parent
    existed = target.exists(follow_symlinks=False)

    if dry_run:
        if existed:
            kind = "dir" if target.is_dir() and not target.is_symlink() else "file/symlink"
            return LinkResult(link, f"[yellow](dry-run) would replace existing {kind}[/]")
        return LinkResult(link, "[cyan](dry-run) would create[/]")

    parent.mkdir(parents=True, exist_ok=True)

    if existed:
        if target.is_symlink() or target.is_file():
            target.unlink()
            status = "[yellow]replaced file/symlink[/]"
        else:
            shutil.rmtree(target)
            status = "[yellow]replaced dir[/]"
    else:
        status = "[green]created[/]"

    target.symlink_to(source)
    return LinkResult(link, status)


def render_table(results: list[LinkResult], *, dry_run: bool) -> Table:
    title = "symlinks" + (" (dry-run)" if dry_run else "")
    table = Table(title=title, title_justify="left")
    table.add_column("source", style="bold")
    table.add_column("target")
    table.add_column("status", overflow="fold")
    for r in results:
        table.add_row(r.link.source, r.link.target, r.status)
    return table


def main() -> None:
    install_tracebacks()
    dry_run = "--dry-run" in sys.argv[1:]

    suffix = " [yellow](dry-run)[/]" if dry_run else ""
    console.rule(f"[bold]symlink[/] · [dim]{REPO_ROOT}[/]{suffix}")

    results = [apply_link(link, dry_run=dry_run) for link in LINKS]
    console.print(render_table(results, dry_run=dry_run))
    console.print("[green]done.[/]")


if __name__ == "__main__":
    main()
