"""Pull sha256 digests from GitHub's release API and write them into the
TOOLS manifest. Run whenever a tool's version changes."""

import ast
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from rich.table import Table

from tools import TOOLS
from ui import console, install_tracebacks

if TYPE_CHECKING:
    from platforms import Platform

TOOLS_PY = Path(__file__).resolve().parent / "tools.py"


def gh_release_digests(gh: str, repo: str, tag: str) -> dict[str, str]:
    proc = subprocess.run(  # noqa: S603
        [gh, "api", f"repos/{repo}/releases/tags/{tag}"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    digests: dict[str, str] = {}
    for asset in payload["assets"]:
        digest = asset.get("digest") or ""
        prefix, _, hexdigest = digest.partition(":")
        if prefix == "sha256" and hexdigest:
            digests[asset["name"]] = hexdigest
    return digests


def collect_shas(gh: str) -> dict[str, dict[Platform, str]]:
    result: dict[str, dict[Platform, str]] = {}
    with console.status("[bold]fetching digests...") as status:
        for tool in TOOLS:
            tag = f"{tool.tag_prefix}{tool.version}"
            status.update(f"[bold]{tool.name}[/] · {tag}")
            digests = gh_release_digests(gh, tool.repo, tag)
            shas: dict[Platform, str] = {}
            for pf, template in tool.assets.items():
                asset_name = template.format(version=tool.version)
                sha = digests.get(asset_name)
                if sha is None:
                    msg = f"{tool.name}: no sha256 for {asset_name} in {tool.repo}@{tag}"
                    raise RuntimeError(msg)
                shas[pf] = sha
            result[tool.name] = shas
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

    gh = shutil.which("gh")
    if gh is None:
        msg = "gh not found on PATH"
        raise RuntimeError(msg)
    uv = shutil.which("uv")
    if uv is None:
        msg = "uv not found on PATH"
        raise RuntimeError(msg)

    shas = collect_shas(gh)

    with console.status("[bold]rewriting tools.py..."):
        rewrite_manifest(shas)

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
