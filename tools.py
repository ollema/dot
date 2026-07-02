"""Tool manifest + model. Consumed by install.py."""

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from platforms import Platform


class Link(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str  # path relative to repo root
    target: str  # path with ~ to be expanded


class Tool(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    repo: str = Field(pattern=r"^[^/\s]+/[^/\s]+$")
    version: str
    tag_prefix: str = "v"
    binary: str | None = None
    extra_binaries: list[str] = Field(default_factory=list)
    is_zip: bool = False
    is_raw_binary: bool = False
    prefix_install: bool = False
    assets: dict[Platform, str]
    sha256: dict[Platform, str] = Field(default_factory=dict)
    symlinks: list[Link] = Field(default_factory=list)
    # Override for projects that publish binaries outside GitHub releases. When
    # set, {version} and {asset} are substituted; install + update_shas fetch
    # from here instead of github.com/{repo}/releases/download/...
    url_template: str | None = None

    @model_validator(mode="after")
    def _reject_incompatible_flags(self) -> Self:
        if self.is_raw_binary and self.extra_binaries:
            msg = f"{self.name}: is_raw_binary cannot be combined with extra_binaries"
            raise ValueError(msg)
        if self.is_raw_binary and self.prefix_install:
            msg = f"{self.name}: is_raw_binary and prefix_install are mutually exclusive"
            raise ValueError(msg)
        return self


TOOLS: list[Tool] = [
    Tool(
        name="bat",
        repo="sharkdp/bat",
        version="0.26.1",
        assets={
            Platform.DARWIN_ARM64: "bat-v{version}-aarch64-apple-darwin.tar.gz",
            Platform.LINUX_AMD64: "bat-v{version}-x86_64-unknown-linux-musl.tar.gz",
        },
        symlinks=[Link(source="bat", target="~/.config/bat")],
        sha256={
            Platform.DARWIN_ARM64: "e30beff26779c9bf60bb541e1d79046250cb74378f2757f8eb250afddb19e114",
            Platform.LINUX_AMD64: "0dcd8ac79732c0d5b136f11f4ee00e581440e16a44eab5b3105b611bbf2cf191",
        },
    ),
    Tool(
        name="bottom",
        repo="ClementTsang/bottom",
        version="0.14.3",
        tag_prefix="",
        binary="btm",
        assets={
            Platform.DARWIN_ARM64: "bottom_aarch64-apple-darwin.tar.gz",
            Platform.LINUX_AMD64: "bottom_x86_64-unknown-linux-musl.tar.gz",
        },
        sha256={
            Platform.DARWIN_ARM64: "ef37c83382359e3b098e1311e3ea933c4f5d0e3042709887a68c102d607c973d",
            Platform.LINUX_AMD64: "5d57590147c7cfe83b4cb249be0d06b6c31b4efe706cc403d6e8c0806299423e",
        },
    ),
    Tool(
        name="copilot",
        repo="github/copilot-cli",
        version="1.0.68",
        assets={Platform.LINUX_AMD64: "copilot-linux-x64.tar.gz"},
        sha256={
            Platform.LINUX_AMD64: "b9531ebf40c2e4c084e5204c9875924a036647bb7f014c4651cf1da2a2053f88"
        },
    ),
    Tool(
        name="delta",
        repo="dandavison/delta",
        version="0.19.2",
        tag_prefix="",
        assets={
            Platform.DARWIN_ARM64: "delta-{version}-aarch64-apple-darwin.tar.gz",
            Platform.LINUX_AMD64: "delta-{version}-x86_64-unknown-linux-musl.tar.gz",
        },
        sha256={
            Platform.DARWIN_ARM64: "9be36612a5a13e9e386dc498fb8e50dc87c72ee42b63db0ea05b32f99a72a69a",
            Platform.LINUX_AMD64: "f1ea01ca7728ce3462debc359f39dfc7cbbc1a63224b71fefabf92042864aa1b",
        },
    ),
    Tool(
        name="eza",
        repo="eza-community/eza",
        version="0.23.4",
        assets={Platform.LINUX_AMD64: "eza_x86_64-unknown-linux-gnu.tar.gz"},
        sha256={
            Platform.LINUX_AMD64: "0c38665440226cd8bef5d1d4f3bc6ff77c927fb0d68b752739105db7ab5b358d"
        },
    ),
    Tool(
        name="fd",
        repo="sharkdp/fd",
        version="10.4.2",
        assets={
            Platform.DARWIN_ARM64: "fd-v{version}-aarch64-apple-darwin.tar.gz",
            Platform.LINUX_AMD64: "fd-v{version}-x86_64-unknown-linux-musl.tar.gz",
        },
        sha256={
            Platform.DARWIN_ARM64: "623dc0afc81b92e4d4606b380d7bc91916ba7b97814263e554d50923a39e480a",
            Platform.LINUX_AMD64: "e3257d48e29a6be965187dbd24ce9af564e0fe67b3e73c9bdcd180f4ec11bdde",
        },
    ),
    Tool(
        name="fish",
        repo="fish-shell/fish-shell",
        version="4.8.0",
        tag_prefix="",
        extra_binaries=["fish_indent", "fish_key_reader"],
        assets={Platform.LINUX_AMD64: "fish-{version}-linux-x86_64.tar.xz"},
        symlinks=[Link(source="fish", target="~/.config/fish")],
        sha256={
            Platform.LINUX_AMD64: "98f7916878fc76be797cabf284f185b56f31a35681e3aec9b9faf7a4a6aa0d74"
        },
    ),
    Tool(
        name="fzf",
        repo="junegunn/fzf",
        version="0.73.1",
        assets={
            Platform.DARWIN_ARM64: "fzf-{version}-darwin_arm64.tar.gz",
            Platform.LINUX_AMD64: "fzf-{version}-linux_amd64.tar.gz",
        },
        sha256={
            Platform.DARWIN_ARM64: "d27fd68c04fb9b42f7c73a3f7d38069a74d308e40174f64a072c747213e97286",
            Platform.LINUX_AMD64: "f3252c2c366bc1700d3c85781ec8c9695998927ac127870eb049ceea2d540f8a",
        },
    ),
    Tool(
        name="jq",
        repo="jqlang/jq",
        version="1.8.2",
        tag_prefix="jq-",
        is_raw_binary=True,
        assets={Platform.DARWIN_ARM64: "jq-macos-arm64", Platform.LINUX_AMD64: "jq-linux-amd64"},
        sha256={
            Platform.DARWIN_ARM64: "2d75340ba57a4b4b4c8708a21c2dc8e958a48aaa8bba13b27f77f6e4c0eca07e",
            Platform.LINUX_AMD64: "b1c22172dd303f3be49e935aa56aa48a8b7a46e0bc838b4997d3bb451495870f",
        },
    ),
    Tool(
        name="neovim",
        repo="neovim/neovim",
        version="0.12.3",
        binary="nvim",
        prefix_install=True,
        assets={
            Platform.DARWIN_ARM64: "nvim-macos-arm64.tar.gz",
            Platform.LINUX_AMD64: "nvim-linux-x86_64.tar.gz",
        },
        symlinks=[Link(source="nvim", target="~/.config/nvim")],
        sha256={
            Platform.DARWIN_ARM64: "532da1d00e465a660fa01c3d4991333d09c52107dce7df937368545daca0a14e",
            Platform.LINUX_AMD64: "c441b547142860bf01bcce39e36cbed185c41112813e15443b16e5237750724d",
        },
    ),
    Tool(
        name="ripgrep",
        repo="BurntSushi/ripgrep",
        version="15.1.0",
        tag_prefix="",
        binary="rg",
        assets={
            Platform.DARWIN_ARM64: "ripgrep-{version}-aarch64-apple-darwin.tar.gz",
            Platform.LINUX_AMD64: "ripgrep-{version}-x86_64-unknown-linux-musl.tar.gz",
        },
        sha256={
            Platform.DARWIN_ARM64: "378e973289176ca0c6054054ee7f631a065874a352bf43f0fa60ef079b6ba715",
            Platform.LINUX_AMD64: "1c9297be4a084eea7ecaedf93eb03d058d6faae29bbc57ecdaf5063921491599",
        },
    ),
    Tool(
        name="starship",
        repo="starship/starship",
        version="1.26.0",
        assets={
            Platform.DARWIN_ARM64: "starship-aarch64-apple-darwin.tar.gz",
            Platform.LINUX_AMD64: "starship-x86_64-unknown-linux-musl.tar.gz",
        },
        symlinks=[Link(source="starship/starship.toml", target="~/.config/starship.toml")],
        sha256={
            Platform.DARWIN_ARM64: "c40b27b11f580411e068f2fa6c1be7830a387c0bc47a94d1d37f32b054c5361d",
            Platform.LINUX_AMD64: "b7c232b0e8249d8e55a40beb79c5c43a7d370f3f9408bd215deb0170daeaadf3",
        },
    ),
    Tool(
        name="tree-sitter",
        repo="tree-sitter/tree-sitter",
        version="0.26.10",
        is_zip=True,
        assets={
            Platform.DARWIN_ARM64: "tree-sitter-cli-macos-arm64.zip",
            Platform.LINUX_AMD64: "tree-sitter-cli-linux-x64.zip",
        },
        sha256={
            Platform.DARWIN_ARM64: "47a1ee94f39611d28c79baa61a3f7bdb5fd1b076428f18fd8082628dc2eca2da",
            Platform.LINUX_AMD64: "5aca1172aae08050d0d1184046377d850c04065205185ebafde361afff8d9f62",
        },
    ),
    Tool(
        name="yazi",
        repo="sxyazi/yazi",
        version="26.5.6",
        is_zip=True,
        extra_binaries=["ya"],
        assets={
            Platform.DARWIN_ARM64: "yazi-aarch64-apple-darwin.zip",
            Platform.LINUX_AMD64: "yazi-x86_64-unknown-linux-musl.zip",
        },
        sha256={
            Platform.DARWIN_ARM64: "7abd71725e2fe27bed036becbf6ce79fa17964eb68491d34190011c94b8c7ca8",
            Platform.LINUX_AMD64: "1031a02560d053301537195a6661d227c15cb4ce5c30481050b31e2b88681bff",
        },
    ),
    Tool(
        name="zmx",
        repo="neurosnap/zmx",
        version="0.6.0",
        url_template="https://zmx.sh/a/{asset}",
        assets={
            Platform.DARWIN_ARM64: "zmx-{version}-macos-aarch64.tar.gz",
            Platform.LINUX_AMD64: "zmx-{version}-linux-x86_64.tar.gz",
        },
        sha256={
            Platform.DARWIN_ARM64: "7f1e4d967d41dea0df76bc7c5dd0d5795e7e54fd657a5f0c74fbfb2c0699390e",
            Platform.LINUX_AMD64: "7ee4b12150dd0d736d271ba1cb06942244c10b857841a663517297ac65c720dd",
        },
    ),
]
