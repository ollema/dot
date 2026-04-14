"""Install CLI tools from GitHub release binaries."""

import io
import os
import platform
import shutil
import stat
import tarfile
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

from tools import TOOLS, Tool

INSTALL_DIR = Path(os.environ.get("INSTALL_DIR", "~/.local/bin")).expanduser()

GITHUB = "https://github.com"


def detect_platform() -> dict[str, str]:
    os_name = platform.system().lower()
    machine = platform.machine().lower()

    if os_name not in ("darwin", "linux"):
        msg = f"unsupported OS: {os_name}"
        raise SystemExit(msg)

    arch_map = {"x86_64": "x86_64", "amd64": "x86_64", "aarch64": "aarch64", "arm64": "aarch64"}
    arch = arch_map.get(machine)
    if not arch:
        msg = f"unsupported architecture: {machine}"
        raise SystemExit(msg)

    arch_go = "amd64" if arch == "x86_64" else "arm64"

    target = "apple-darwin" if os_name == "darwin" else "unknown-linux-musl"

    target_gnu = "apple-darwin" if os_name == "darwin" else "unknown-linux-gnu"

    return {
        "os": os_name,
        "OS": os_name.capitalize(),
        "arch": arch,
        "arch_go": arch_go,
        "target": target,
        "target_gnu": target_gnu,
    }


def resolve_asset(tool: Tool, pf: dict[str, str]) -> str:
    return tool.asset.format(version=tool.version, **pf)


def download(url: str) -> bytes:
    # Fetching release binaries from GitHub over HTTPS; scheme is fixed.
    req = urllib.request.Request(url, headers={"User-Agent": "tools.py"})  # noqa: S310
    with urllib.request.urlopen(req) as resp:  # noqa: S310
        return resp.read()


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
                shutil.copy2(found, dest)
                dest.chmod(dest.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
                installed.append(target)

    return installed


def find_binary(root: Path, name: str) -> Path | None:
    for match in root.rglob(name):
        if match.is_file():
            return match
    return None


def install_tool(tool: Tool, pf: dict[str, str]) -> None:
    if tool.linux_only and pf["os"] != "linux":
        print(f"  {tool.name} — skipped (linux only)")
        return

    asset_name = resolve_asset(tool, pf)
    url = download_url(tool, asset_name)

    print(f"  {tool.name} {tool.version} ({asset_name})")

    try:
        data = download(url)
    except urllib.error.HTTPError as e:
        print(f"    FAILED: {e.code} {e.reason} — {url}")
        return

    installed = extract_and_install(tool, data, asset_name)
    if installed:
        print(f"    -> {', '.join(installed)}")
    else:
        print("    FAILED: no matching binary found in archive")


def main() -> None:
    pf = detect_platform()
    print(f"platform: {pf['os']}/{pf['arch']}")
    print(f"install dir: {INSTALL_DIR}\n")

    INSTALL_DIR.mkdir(parents=True, exist_ok=True)

    for tool in TOOLS:
        install_tool(tool, pf)

    print(f"\ndone. make sure {INSTALL_DIR} is in your PATH.")


if __name__ == "__main__":
    main()
