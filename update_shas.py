"""Download every release asset referenced by tools.py, hash it, and write
the results back into the TOOLS manifest. Run whenever a tool's version changes."""

import ast
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from install import download, download_url
from tools import TOOLS

if TYPE_CHECKING:
    from platforms import Platform

TOOLS_PY = Path(__file__).resolve().parent / "tools.py"


def collect_shas() -> dict[str, dict[Platform, str]]:
    result: dict[str, dict[Platform, str]] = {}
    for tool in TOOLS:
        entries: dict[Platform, str] = {}
        for pf, template in tool.assets.items():
            asset = template.format(version=tool.version)
            url = download_url(tool, asset)
            print(f"  {tool.name:10s} {pf.value:14s} {asset}")
            data = download(url)
            entries[pf] = hashlib.sha256(data).hexdigest()
        result[tool.name] = entries
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


def main() -> None:
    print("fetching release assets and computing sha256 for each supported platform:\n")
    shas = collect_shas()
    print("\nrewriting tools.py...")
    rewrite_manifest(shas)
    print("running ruff format...")
    uv = shutil.which("uv")
    if uv is None:
        msg = "uv not found on PATH"
        raise RuntimeError(msg)
    subprocess.run([uv, "run", "ruff", "format", str(TOOLS_PY)], check=True)  # noqa: S603
    print("done.")


if __name__ == "__main__":
    sys.exit(main())
