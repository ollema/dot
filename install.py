"""Install CLI tools from GitHub release binaries."""

import hashlib
import io
import os
import shutil
import stat
import tarfile
import tempfile
import urllib.error
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from rich.table import Table

import platforms
from platforms import Platform
from tools import TOOLS, Tool
from ui import console, install_tracebacks, make_progress, status_style

if TYPE_CHECKING:
    from collections.abc import Callable

INSTALL_DIR = Path(os.environ.get("INSTALL_DIR", "~/.local/bin")).expanduser()
GITHUB = "https://github.com"
MAX_WORKERS = 8
CHUNK = 64 * 1024


@dataclass
class Result:
    tool: str
    version: str
    asset: str
    state: str
    detail: str


def resolve_asset(tool: Tool, pf: Platform) -> str:
    return tool.assets[pf].format(version=tool.version)


def download_streaming(url: str, on_chunk: Callable[[int, int], None]) -> bytes:
    # Fetching release binaries from GitHub over HTTPS; scheme is fixed.
    req = urllib.request.Request(url, headers={"User-Agent": "tools.py"})  # noqa: S310
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
        total = int(resp.headers.get("Content-Length", 0))
        buf = bytearray()
        while chunk := resp.read(CHUNK):
            buf.extend(chunk)
            on_chunk(len(chunk), total)
        return bytes(buf)


def download(url: str) -> bytes:
    return download_streaming(url, lambda _n, _t: None)


def download_url(tool: Tool, asset_name: str) -> str:
    return f"{GITHUB}/{tool.repo}/releases/download/{tool.tag_prefix}{tool.version}/{asset_name}"


def extract_and_install(tool: Tool, data: bytes, asset_name: str) -> list[str]:
    binary_name = tool.binary or tool.name
    targets = [binary_name, *tool.extra_binaries]
    installed: list[str] = []

    if tool.is_raw_binary:
        dest = INSTALL_DIR / binary_name
        dest.write_bytes(data)
        dest.chmod(dest.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        return [binary_name]

    if tool.prefix_install:
        return install_prefix(tool, data)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        if tool.is_zip or asset_name.endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                zf.extractall(tmp_root)  # noqa: S202
        else:
            with tarfile.open(fileobj=io.BytesIO(data)) as tf:
                tf.extractall(tmp_root, filter="data")

        for target in targets:
            found = find_binary(tmp_root, target)
            if found:
                dest = INSTALL_DIR / target
                atomic_install(found, dest)
                installed.append(target)

    return installed


def install_prefix(tool: Tool, data: bytes) -> list[str]:
    # Tools like neovim ship binary + runtime siblings (share/, lib/); the binary
    # resolves VIMRUNTIME via realpath(argv[0])/../share/nvim/runtime. Extract the
    # whole distribution into INSTALL_DIR.parent so the relative layout survives.
    target_root = INSTALL_DIR.parent
    binaries = [tool.binary or tool.name, *tool.extra_binaries]

    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        with tarfile.open(fileobj=io.BytesIO(data)) as tf:
            tf.extractall(tmp_root, filter="data")
        entries = list(tmp_root.iterdir())
        if len(entries) != 1 or not entries[0].is_dir():
            names = [e.name for e in entries]
            msg = f"{tool.name}: expected single top-level dir in archive, got {names}"
            raise RuntimeError(msg)
        top = entries[0]

        for item in top.iterdir():
            dest = target_root / item.name
            if item.name == "bin" and item.is_dir():
                dest.mkdir(parents=True, exist_ok=True)
                for src in item.iterdir():
                    if src.is_file():
                        atomic_install(src, dest / src.name)
            elif item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)

    return [b for b in binaries if (target_root / "bin" / b).exists()]


def atomic_install(src: Path, dest: Path) -> None:
    # Write to a sibling then os.replace, so we can overwrite a running
    # binary (Linux ETXTBSY): rename unlinks the old dentry while the live
    # process keeps executing from its inode.
    tmp = dest.with_name(f".{dest.name}.new")
    shutil.copy2(src, tmp)
    tmp.chmod(tmp.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    tmp.replace(dest)


def find_binary(root: Path, name: str) -> Path | None:
    for match in root.rglob(name):
        if match.is_file():
            return match
    return None


def install_tool(tool: Tool, pf: Platform, progress, task_id) -> Result:  # noqa: ANN001, PLR0911
    if pf not in tool.assets:
        progress.remove_task(task_id)
        return Result(tool.name, tool.version, "-", "skip", f"not available on {pf.value}")

    asset_name = resolve_asset(tool, pf)
    url = download_url(tool, asset_name)

    def advance(n: int, total: int) -> None:
        progress.update(task_id, total=total or None, advance=n)

    try:
        data = download_streaming(url, advance)
    except urllib.error.HTTPError as e:
        return Result(tool.name, tool.version, asset_name, "fail", f"{e.code} {e.reason}")
    except urllib.error.URLError as e:
        return Result(tool.name, tool.version, asset_name, "fail", f"network: {e.reason}")

    expected = tool.sha256.get(pf)
    if not expected:
        return Result(tool.name, tool.version, asset_name, "fail", "no sha256 recorded")
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        return Result(tool.name, tool.version, asset_name, "fail", "sha256 mismatch")

    installed = extract_and_install(tool, data, asset_name)
    if not installed:
        return Result(tool.name, tool.version, asset_name, "fail", "no matching binary in archive")
    return Result(tool.name, tool.version, asset_name, "ok", ", ".join(installed))


def render_summary(results: list[Result]) -> Table:
    table = Table(title="install summary", title_justify="left", show_lines=False)
    table.add_column("tool", style="bold")
    table.add_column("version")
    table.add_column("asset", overflow="fold")
    table.add_column("status")
    table.add_column("detail", overflow="fold")
    for r in sorted(results, key=lambda r: r.tool):
        table.add_row(r.tool, r.version, r.asset, status_style(r.state), r.detail)
    return table


def main() -> None:
    install_tracebacks()
    pf = platforms.detect()
    console.rule(f"[bold]install[/] · platform [cyan]{pf.value}[/] · dir [dim]{INSTALL_DIR}[/]")

    INSTALL_DIR.mkdir(parents=True, exist_ok=True)

    with make_progress() as progress:
        tasks = {tool.name: progress.add_task(tool.name, total=None) for tool in TOOLS}
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = [
                pool.submit(install_tool, tool, pf, progress, tasks[tool.name]) for tool in TOOLS
            ]
            results = [fut.result() for fut in as_completed(futures)]

    console.print(render_summary(results))
    failed = sum(1 for r in results if r.state == "fail")
    if failed:
        console.print(f"[red]{failed} failed[/] — see detail column above.")
    console.print(f"[green]done.[/] ensure [cyan]{INSTALL_DIR}[/] is in your PATH.")


if __name__ == "__main__":
    main()
