"""Download every release asset referenced by tools.py, hash it, and write
the results back into the TOOLS manifest. Run whenever a tool's version changes."""

import ast
import hashlib
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import TYPE_CHECKING

from rich.table import Table

from install import download_streaming, download_url
from tools import TOOLS
from ui import console, install_tracebacks, make_progress

if TYPE_CHECKING:
    from rich.progress import TaskID

    from platforms import Platform

TOOLS_PY = Path(__file__).resolve().parent / "tools.py"
MAX_WORKERS = 8


def collect_shas() -> dict[str, dict[Platform, str]]:
    jobs: list[tuple[str, Platform, str, str]] = []
    for tool in TOOLS:
        for pf, template in tool.assets.items():
            asset = template.format(version=tool.version)
            jobs.append((tool.name, pf, asset, download_url(tool, asset)))

    shas: dict[tuple[str, Platform], str] = {}

    with make_progress() as progress:
        overall = progress.add_task("all assets", total=len(jobs))
        task_ids: dict[tuple[str, Platform], TaskID] = {
            (name, pf): progress.add_task(f"{name} · {pf.value}", total=None)
            for name, pf, _, _ in jobs
        }

        def fetch(name: str, pf: Platform, url: str) -> tuple[str, Platform, str]:
            tid = task_ids[(name, pf)]

            def advance(n: int, total: int) -> None:
                progress.update(tid, total=total or None, advance=n)

            data = download_streaming(url, advance)
            return name, pf, hashlib.sha256(data).hexdigest()

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = [pool.submit(fetch, name, pf, url) for name, pf, _, url in jobs]
            for fut in as_completed(futures):
                name, pf, sha = fut.result()
                shas[(name, pf)] = sha
                progress.advance(overall)

    result: dict[str, dict[Platform, str]] = {tool.name: {} for tool in TOOLS}
    for name, pf, _, _ in jobs:
        result[name][pf] = shas[(name, pf)]
    return result


def rewrite_manifest(shas_by_tool: dict[str, dict[Platform, str]]) -> None:
    source = TOOLS_PY.read_text()
    tree = ast.parse(source)

    tools_assign: ast.Assign | ast.AnnAssign | None = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "TOOLS" for t in node.targets
        ):
            tools_assign = node
            break
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "TOOLS"
        ):
            tools_assign = node
            break
    if tools_assign is None or not isinstance(tools_assign.value, ast.List):
        msg = "could not locate TOOLS = [...] assignment in tools.py"
        raise SystemExit(msg)

    for elt in tools_assign.value.elts:
        if not isinstance(elt, ast.Call):
            continue
        name_kw = next(kw for kw in elt.keywords if kw.arg == "name")
        name_const = name_kw.value
        if not (isinstance(name_const, ast.Constant) and isinstance(name_const.value, str)):
            msg = f"expected str Constant for name kwarg, got {ast.dump(name_const)}"
            raise TypeError(msg)
        sha_dict = shas_by_tool[name_const.value]
        sha_ast = ast.Dict(
            keys=[
                ast.Attribute(value=ast.Name(id="Platform"), attr=pf.name, ctx=ast.Load())
                for pf in sha_dict
            ],
            values=[ast.Constant(value=v) for v in sha_dict.values()],
        )
        elt.keywords = [kw for kw in elt.keywords if kw.arg != "sha256"]
        elt.keywords.append(ast.keyword(arg="sha256", value=sha_ast))

    new_block = ast.unparse(tools_assign)
    lines = source.splitlines(keepends=True)
    start = tools_assign.lineno - 1
    end = tools_assign.end_lineno
    if end is None:
        msg = "TOOLS assignment has no end_lineno"
        raise RuntimeError(msg)
    trailing_nl = "\n" if not new_block.endswith("\n") else ""
    rewritten = "".join(lines[:start]) + new_block + trailing_nl + "".join(lines[end:])
    TOOLS_PY.write_text(rewritten)


def render_summary(shas_by_tool: dict[str, dict[Platform, str]]) -> Table:
    table = Table(title="sha256", title_justify="left")
    table.add_column("tool", style="bold")
    table.add_column("platform")
    table.add_column("sha256", style="dim")
    for name in sorted(shas_by_tool):
        for pf, sha in shas_by_tool[name].items():
            table.add_row(name, pf.value, sha[:16] + "…")
    return table


def main() -> int:
    install_tracebacks()
    console.rule("[bold]update-shas[/]")

    shas = collect_shas()

    with console.status("[bold]rewriting tools.py..."):
        rewrite_manifest(shas)

    uv = shutil.which("uv")
    if uv is None:
        msg = "uv not found on PATH"
        raise RuntimeError(msg)
    with console.status("[bold]running ruff format..."):
        subprocess.run(  # noqa: S603
            [uv, "run", "ruff", "format", str(TOOLS_PY)],
            check=True,
            capture_output=True,
        )

    console.print(render_summary(shas))
    console.print("[green]done.[/]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
