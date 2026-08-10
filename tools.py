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
        version="0.14.7",
        tag_prefix="",
        binary="btm",
        assets={
            Platform.DARWIN_ARM64: "bottom_aarch64-apple-darwin.tar.gz",
            Platform.LINUX_AMD64: "bottom_x86_64-unknown-linux-musl.tar.gz",
        },
        sha256={
            Platform.DARWIN_ARM64: "aaf5c61c0c29b35a205fe1cff590d900716ea61e7d7c5efc8a3ebfbf624a81a2",
            Platform.LINUX_AMD64: "060f157720194906393d0118e01a84f654b93749575d896b5331499d5ead06ee",
        },
    ),
    Tool(
        name="copilot",
        repo="github/copilot-cli",
        version="1.0.78",
        assets={Platform.LINUX_AMD64: "copilot-linux-x64.tar.gz"},
        sha256={
            Platform.LINUX_AMD64: "8935cbe2916b0b1cb724aaa81fdda29e2ec20b2ea76f1d2708fb788e47acfad9"
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
        version="0.23.5",
        assets={Platform.LINUX_AMD64: "eza_x86_64-unknown-linux-gnu.tar.gz"},
        sha256={
            Platform.LINUX_AMD64: "35c70c5c43c29108075e58b893234c67ef585f0b53a7eaf8e9e7d4eec9f339b4"
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
        version="4.8.1",
        tag_prefix="",
        extra_binaries=["fish_indent", "fish_key_reader"],
        assets={Platform.LINUX_AMD64: "fish-{version}-linux-x86_64.tar.xz"},
        symlinks=[Link(source="fish", target="~/.config/fish")],
        sha256={
            Platform.LINUX_AMD64: "39cab35242ab77bfdbce73b473000c3b045aaf2fe0951b042199bb7fdba3df78"
        },
    ),
    Tool(
        name="fzf",
        repo="junegunn/fzf",
        version="0.74.2",
        assets={
            Platform.DARWIN_ARM64: "fzf-{version}-darwin_arm64.tar.gz",
            Platform.LINUX_AMD64: "fzf-{version}-linux_amd64.tar.gz",
        },
        sha256={
            Platform.DARWIN_ARM64: "d60ddb36356566ac69bae7c3504e888916cf747c9ad2132141c09229b1e28dee",
            Platform.LINUX_AMD64: "b3648f48675612b69ee35371cf6dc99ca96d767e89b912d079080916ac8ba8bd",
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
        version="0.12.4",
        binary="nvim",
        prefix_install=True,
        assets={
            Platform.DARWIN_ARM64: "nvim-macos-arm64.tar.gz",
            Platform.LINUX_AMD64: "nvim-linux-x86_64.tar.gz",
        },
        symlinks=[Link(source="nvim", target="~/.config/nvim")],
        sha256={
            Platform.DARWIN_ARM64: "51ab83afa66d663627c2ab1be43209b0f4e81360d4598b53efaa4d8195f24c89",
            Platform.LINUX_AMD64: "012bf3fcac5ade43914df3f174668bf64d05e049a4f032a388c027b1ebd78628",
        },
    ),
    Tool(
        name="ripgrep",
        repo="BurntSushi/ripgrep",
        version="15.2.0",
        tag_prefix="",
        binary="rg",
        assets={
            Platform.DARWIN_ARM64: "ripgrep-{version}-aarch64-apple-darwin.tar.gz",
            Platform.LINUX_AMD64: "ripgrep-{version}-x86_64-unknown-linux-musl.tar.gz",
        },
        sha256={
            Platform.DARWIN_ARM64: "3750b2e93f37e0c692657da574d7019a101c0084da05a790c83fd335bad973e4",
            Platform.LINUX_AMD64: "33e15bcf1624b25cdd2a55813a47a2f95dbe126268203e76aa6a585d1e7b149c",
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
        version="0.26.12",
        is_zip=True,
        assets={
            Platform.DARWIN_ARM64: "tree-sitter-cli-macos-arm64.zip",
            Platform.LINUX_AMD64: "tree-sitter-cli-linux-x64.zip",
        },
        sha256={
            Platform.DARWIN_ARM64: "3ca18160518d0ac8f631448c771ac102748482af518992adcb09f96423ba153f",
            Platform.LINUX_AMD64: "c33ace12fa7a94d09c97054da621bf7a6a3159f765b1839a898232de283d641d",
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
        version="0.7.0",
        url_template="https://zmx.sh/a/{asset}",
        assets={
            Platform.DARWIN_ARM64: "zmx-{version}-macos-aarch64.tar.gz",
            Platform.LINUX_AMD64: "zmx-{version}-linux-x86_64.tar.gz",
        },
        sha256={
            Platform.DARWIN_ARM64: "a63d6f3edd6d4b38240f8f81513e60e35a898ca520211112d7bc67f610f1f3eb",
            Platform.LINUX_AMD64: "8b8783d7b120c9ffd0acf4aee37969054dc0dfef3c4f3a4728d2efd35f2e97a0",
        },
    ),
]
