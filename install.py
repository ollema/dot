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
from pathlib import Path

import platforms
from platforms import Platform
from tools import TOOLS, Tool

INSTALL_DIR = Path(os.environ.get("INSTALL_DIR", "~/.local/bin")).expanduser()

GITHUB = "https://github.com"


def resolve_asset(tool: Tool, pf: Platform) -> str:
    return tool.assets[pf].format(version=tool.version)


def download(url: str) -> bytes:
    # Fetching release binaries from GitHub over HTTPS; scheme is fixed.
    req = urllib.request.Request(url, headers={"User-Agent": "tools.py"})  # noqa: S310
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
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
                atomic_install(found, dest)
                installed.append(target)

    return installed


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


def install_tool(tool: Tool, pf: Platform) -> None:
    if pf not in tool.assets:
        print(f"  {tool.name} — skipped (not available on {pf.value})")
        return

    asset_name = resolve_asset(tool, pf)
    url = download_url(tool, asset_name)

    print(f"  {tool.name} {tool.version} ({asset_name})")

    try:
        data = download(url)
    except urllib.error.HTTPError as e:
        print(f"    FAILED: {e.code} {e.reason} — {url}")
        return

    expected = tool.sha256.get(pf)
    if not expected:
        print(f"    FAILED: no sha256 recorded for {asset_name}")
        return
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        print(f"    FAILED: sha256 mismatch (expected {expected}, got {actual})")
        return

    installed = extract_and_install(tool, data, asset_name)
    if installed:
        print(f"    -> {', '.join(installed)}")
    else:
        print("    FAILED: no matching binary found in archive")


def main() -> None:
    pf = platforms.detect()
    print(f"platform: {pf.value}")
    print(f"install dir: {INSTALL_DIR}\n")

    INSTALL_DIR.mkdir(parents=True, exist_ok=True)

    for tool in TOOLS:
        install_tool(tool, pf)

    print(f"\ndone. make sure {INSTALL_DIR} is in your PATH.")


if __name__ == "__main__":
    main()
