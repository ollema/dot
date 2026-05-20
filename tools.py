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
        version="0.12.3",
        tag_prefix="",
        binary="btm",
        assets={
            Platform.DARWIN_ARM64: "bottom_aarch64-apple-darwin.tar.gz",
            Platform.LINUX_AMD64: "bottom_x86_64-unknown-linux-musl.tar.gz",
        },
        sha256={
            Platform.DARWIN_ARM64: "106e9493d20192d18dbe46d4c99f680d817c796724103ee258567070fcd16429",
            Platform.LINUX_AMD64: "0d6352079422fda8f4ee242eb849f45a6008db96d6c1cd35e8436babc51bc33f",
        },
    ),
    Tool(
        name="copilot",
        repo="github/copilot-cli",
        version="1.0.49",
        assets={Platform.LINUX_AMD64: "copilot-linux-x64.tar.gz"},
        sha256={
            Platform.LINUX_AMD64: "e61fa2490bc584fe65c4d9f3b2337ef63439cbd9e0a4f6648eb63223e1b32afd"
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
        version="4.7.1",
        tag_prefix="",
        extra_binaries=["fish_indent", "fish_key_reader"],
        assets={Platform.LINUX_AMD64: "fish-{version}-linux-x86_64.tar.xz"},
        symlinks=[Link(source="fish", target="~/.config/fish")],
        sha256={
            Platform.LINUX_AMD64: "345388add316b94a847b08cef01f1b46e85b98215328271ee22a21555a3204df"
        },
    ),
    Tool(
        name="fzf",
        repo="junegunn/fzf",
        version="0.72.0",
        assets={
            Platform.DARWIN_ARM64: "fzf-{version}-darwin_arm64.tar.gz",
            Platform.LINUX_AMD64: "fzf-{version}-linux_amd64.tar.gz",
        },
        sha256={
            Platform.DARWIN_ARM64: "4cbf87e8e8a342614c1e3e74670ceb18c2af998c4d4d0c379cfee9b520774e90",
            Platform.LINUX_AMD64: "0e58e4bd0b3c5d68c56b54c460a6863d0de79633ed18d388575a960ab447b006",
        },
    ),
    Tool(
        name="jq",
        repo="jqlang/jq",
        version="1.8.1",
        tag_prefix="jq-",
        is_raw_binary=True,
        assets={Platform.DARWIN_ARM64: "jq-macos-arm64", Platform.LINUX_AMD64: "jq-linux-amd64"},
        sha256={
            Platform.DARWIN_ARM64: "a9fe3ea2f86dfc72f6728417521ec9067b343277152b114f4e98d8cb0e263603",
            Platform.LINUX_AMD64: "020468de7539ce70ef1bceaf7cde2e8c4f2ca6c3afb84642aabc5c97d9fc2a0d",
        },
    ),
    Tool(
        name="neovim",
        repo="neovim/neovim",
        version="0.12.2",
        binary="nvim",
        prefix_install=True,
        assets={
            Platform.DARWIN_ARM64: "nvim-macos-arm64.tar.gz",
            Platform.LINUX_AMD64: "nvim-linux-x86_64.tar.gz",
        },
        symlinks=[Link(source="nvim", target="~/.config/nvim")],
        sha256={
            Platform.DARWIN_ARM64: "eeddee1009734f9071266e6b1b8a70308cb60cbcc45f5e1c1023adc471450fee",
            Platform.LINUX_AMD64: "31cf85945cb600d96cdf69f88bc68bec814acbff50863c5546adef3a1bcef260",
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
        version="1.25.1",
        assets={
            Platform.DARWIN_ARM64: "starship-aarch64-apple-darwin.tar.gz",
            Platform.LINUX_AMD64: "starship-x86_64-unknown-linux-musl.tar.gz",
        },
        symlinks=[Link(source="starship/starship.toml", target="~/.config/starship.toml")],
        sha256={
            Platform.DARWIN_ARM64: "1062a2363489b9335529b83204472f02633c08fc3609f1b325be5eba36feb631",
            Platform.LINUX_AMD64: "c6ddd3ecb9c0071a2ad38d98cee748160066b7c4f197421268058f4a5d6f8504",
        },
    ),
    Tool(
        name="tree-sitter",
        repo="tree-sitter/tree-sitter",
        version="0.26.9",
        is_zip=True,
        assets={
            Platform.DARWIN_ARM64: "tree-sitter-cli-macos-arm64.zip",
            Platform.LINUX_AMD64: "tree-sitter-cli-linux-x64.zip",
        },
        sha256={
            Platform.DARWIN_ARM64: "86e81a78eee96f4fd730e43589ecc80263f7e34be7a0558ccebff9a492e8ad97",
            Platform.LINUX_AMD64: "0ea5daaef79145fe73786f0e3cdc43b62b22ddb36f7f6676c9f8bb72434d78e9",
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
            Platform.DARWIN_ARM64: "621b85f25a1c73399e4ee46f482afc7cffb4638446e8d0eef5acaa57c2b79b4e",
            Platform.LINUX_AMD64: "46e2b458f3247c117bc39e4eb959b58c4e5ec23fc62d776411e3dcb431bd2e3d",
        },
    ),
]
