"""Supported target platforms for release-binary installation."""

import platform
from enum import Enum


class Platform(Enum):
    DARWIN_ARM64 = "darwin-arm64"
    LINUX_AMD64 = "linux-amd64"


def detect() -> Platform:
    os_name = platform.system().lower()
    machine = platform.machine().lower()
    if os_name == "darwin" and machine in ("arm64", "aarch64"):
        return Platform.DARWIN_ARM64
    if os_name == "linux" and machine in ("x86_64", "amd64"):
        return Platform.LINUX_AMD64
    msg = f"unsupported platform: {os_name}/{machine}"
    raise SystemExit(msg)
