"""Shared Rich console, progress, and styling helpers for the .dot scripts."""

from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.traceback import install as _install_tb

console = Console()


def install_tracebacks() -> None:
    _install_tb(show_locals=False, suppress=["urllib"])


def make_progress() -> Progress:
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold]{task.description}"),
        BarColumn(bar_width=None),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=True,
    )


def status_style(state: str) -> str:
    match state:
        case "ok":
            return "[green]ok[/]"
        case "skip":
            return "[yellow]skip[/]"
        case "fail":
            return "[red]fail[/]"
        case _:
            return state
