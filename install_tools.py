#!/usr/bin/env python3
"""Install CLI tools from GitHub release binaries."""

from __future__ import annotations

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
from dataclasses import dataclass, field

INSTALL_DIR = os.environ.get("INSTALL_DIR", os.path.expanduser("~/.local/bin"))

GITHUB = "https://github.com"


@dataclass
class Tool:
    name: str
    repo: str
    version: str
    asset: str  # template: {version}, {os}, {OS}, {arch}, {arch_go}, {target}, {target_gnu}
    binary: str | None = None  # binary name inside archive, defaults to name
    strip_components: int = 1  # tar --strip-components equivalent
    is_zip: bool = False
    is_raw_binary: bool = False  # asset is the binary itself, not an archive
    extra_binaries: list[str] = field(default_factory=list)
    linux_only: bool = False
    tag_prefix: str = "v"


TOOLS: list[Tool] = [
    Tool(
        name="ripgrep",
        repo="BurntSushi/ripgrep",
        version="14.1.1",
        binary="rg",
        asset="ripgrep-{version}-{arch}-{target}.tar.gz",
    ),
    Tool(
        name="fd",
        repo="sharkdp/fd",
        version="10.2.0",
        asset="fd-v{version}-{arch}-{target}.tar.gz",
    ),
    Tool(
        name="bat",
        repo="sharkdp/bat",
        version="0.24.0",
        asset="bat-v{version}-{arch}-{target}.tar.gz",
    ),
    Tool(
        name="eza",
        repo="eza-community/eza",
        version="0.20.14",
        asset="eza_{arch}-{target_gnu}.tar.gz",
    ),
    Tool(
        name="fzf",
        repo="junegunn/fzf",
        version="0.57.0",
        asset="fzf-{version}-{os}_{arch_go}.tar.gz",
        strip_components=0,
    ),
    Tool(
        name="jq",
        repo="jqlang/jq",
        version="1.7.1",
        asset="jq-{os}-{arch_go}",
        is_raw_binary=True,
    ),
    Tool(
        name="starship",
        repo="starship/starship",
        version="1.21.1",
        asset="starship-{arch}-{target}.tar.gz",
        strip_components=0,
    ),
    Tool(
        name="fish",
        repo="fish-shell/fish-shell",
        version="4.2.1",
        asset="fish-{version}-linux-{arch_go}.tar.xz",
        extra_binaries=["fish_indent", "fish_key_reader"],
        linux_only=True,
        tag_prefix="",
    ),
]


def detect_platform() -> dict[str, str]:
    os_name = platform.system().lower()
    machine = platform.machine().lower()

    if os_name not in ("darwin", "linux"):
        raise SystemExit(f"unsupported OS: {os_name}")

    arch_map = {"x86_64": "x86_64", "amd64": "x86_64", "aarch64": "aarch64", "arm64": "aarch64"}
    arch = arch_map.get(machine)
    if not arch:
        raise SystemExit(f"unsupported architecture: {machine}")

    arch_go = "amd64" if arch == "x86_64" else "arm64"

    if os_name == "darwin":
        target = "apple-darwin"
    else:
        target = "unknown-linux-musl"

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
    req = urllib.request.Request(url, headers={"User-Agent": "tools.py"})
    with urllib.request.urlopen(req) as resp:
        return resp.read()


def download_url(tool: Tool, asset_name: str) -> str:
    return f"{GITHUB}/{tool.repo}/releases/download/{tool.tag_prefix}{tool.version}/{asset_name}"


def extract_and_install(tool: Tool, data: bytes, asset_name: str) -> list[str]:
    binary_name = tool.binary or tool.name
    targets = [binary_name] + tool.extra_binaries
    installed = []

    if tool.is_raw_binary:
        dest = os.path.join(INSTALL_DIR, binary_name)
        with open(dest, "wb") as f:
            f.write(data)
        os.chmod(dest, os.stat(dest).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        return [binary_name]

    with tempfile.TemporaryDirectory() as tmp:
        if tool.is_zip or asset_name.endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                zf.extractall(tmp)
        else:
            with tarfile.open(fileobj=io.BytesIO(data)) as tf:
                tf.extractall(tmp)

        for target in targets:
            found = find_binary(tmp, target)
            if found:
                dest = os.path.join(INSTALL_DIR, target)
                shutil.copy2(found, dest)
                os.chmod(dest, os.stat(dest).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
                installed.append(target)

    return installed


def find_binary(root: str, name: str) -> str | None:
    for dirpath, _, filenames in os.walk(root):
        if name in filenames:
            return os.path.join(dirpath, name)
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

    os.makedirs(INSTALL_DIR, exist_ok=True)

    for tool in TOOLS:
        install_tool(tool, pf)

    print(f"\ndone. make sure {INSTALL_DIR} is in your PATH.")


if __name__ == "__main__":
    main()