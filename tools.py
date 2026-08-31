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
        version="0.14.9",
        tag_prefix="",
        binary="btm",
        assets={
            Platform.DARWIN_ARM64: "bottom_aarch64-apple-darwin.tar.gz",
            Platform.LINUX_AMD64: "bottom_x86_64-unknown-linux-musl.tar.gz",
        },
        sha256={
            Platform.DARWIN_ARM64: "28358e19a3d62b3778fc0d1778b0028a682059145c9ac38ac5076bf124d77714",
            Platform.LINUX_AMD64: "b4bee5b193e7d3f6e090ac14f0ca15acec2e7fe4ef64988e0bfc492e16c28c9a",
        },
    ),
    Tool(
        name="copilot",
        repo="github/copilot-cli",
        version="1.0.82",
        assets={Platform.LINUX_AMD64: "copilot-linux-x64.tar.gz"},
        sha256={
            Platform.LINUX_AMD64: "37fa67686a9e4ed8d46dcd6a9c80ab524dea840ecaa0a3f7edf8d09f961b97a9"
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
        version="10.5.0",
        assets={
            Platform.DARWIN_ARM64: "fd-v{version}-aarch64-apple-darwin.tar.gz",
            Platform.LINUX_AMD64: "fd-v{version}-x86_64-unknown-linux-musl.tar.gz",
        },
        sha256={
            Platform.DARWIN_ARM64: "b67e1836c468e42e411984b56e52fa7abec08c2bd22c867398e7cc134aac5e12",
            Platform.LINUX_AMD64: "761c72dc8e120d85b22292063be8a796e2eeb20eb3e4f38b8fa2343ccf3514a7",
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
        version="0.74.3",
        assets={
            Platform.DARWIN_ARM64: "fzf-{version}-darwin_arm64.tar.gz",
            Platform.LINUX_AMD64: "fzf-{version}-linux_amd64.tar.gz",
        },
        sha256={
            Platform.DARWIN_ARM64: "1f8501cea4f9c0c2d6110d0ff75d0ec9451cd9d7524d9a26244a154ea89f3bd5",
            Platform.LINUX_AMD64: "3501a595e4b5c40a6b047340a0e8f805c46fd4e61ef95ef8a136ba8c61cf6f22",
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
        version="0.12.5",
        binary="nvim",
        prefix_install=True,
        assets={
            Platform.DARWIN_ARM64: "nvim-macos-arm64.tar.gz",
            Platform.LINUX_AMD64: "nvim-linux-x86_64.tar.gz",
        },
        symlinks=[Link(source="nvim", target="~/.config/nvim")],
        sha256={
            Platform.DARWIN_ARM64: "65fb000099e47ca1b762584c484cc833f40e30851a0ec450d4174e16317c1f9b",
            Platform.LINUX_AMD64: "bce0f56eda1f1b1db6eee8f4133d7a38813ea07933837dd1777411ca384c6875",
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
        version="0.27.0",
        is_zip=True,
        assets={
            Platform.DARWIN_ARM64: "tree-sitter-cli-macos-arm64.zip",
            Platform.LINUX_AMD64: "tree-sitter-cli-linux-x64.zip",
        },
        sha256={
            Platform.DARWIN_ARM64: "f278063d8544160f6f89f7f8dba6ba112cb0dd1669757788d2bb7a8a613d2c58",
            Platform.LINUX_AMD64: "e4a3826bcd0fe099ee3a5617767374939cbc23c4a35b5b53f5fc04142525a2c1",
        },
    ),
    Tool(
        name="yazi",
        repo="sxyazi/yazi",
        version="26.8.15",
        is_zip=True,
        extra_binaries=["ya"],
        assets={
            Platform.DARWIN_ARM64: "yazi-aarch64-apple-darwin.zip",
            Platform.LINUX_AMD64: "yazi-x86_64-unknown-linux-musl.zip",
        },
        sha256={
            Platform.DARWIN_ARM64: "3f54907ea08abe96506f4b22239340ed8923a6aeaeae78f33d59bce57daca4cd",
            Platform.LINUX_AMD64: "a6702034790afcdbb546b73b288c9b184a751fa3f2f17f0ad4d26fc302fb8d45",
        },
    ),
    Tool(
        name="zmx",
        repo="neurosnap/zmx",
        version="0.7.1",
        url_template="https://zmx.sh/a/{asset}",
        assets={
            Platform.DARWIN_ARM64: "zmx-{version}-macos-aarch64.tar.gz",
            Platform.LINUX_AMD64: "zmx-{version}-linux-x86_64.tar.gz",
        },
        sha256={
            Platform.DARWIN_ARM64: "86ce4c0eeb6b8448d058390fabe4a5aff323c4fc1e64ed578d48ab75a0f59a79",
            Platform.LINUX_AMD64: "ec82d753e12537b79a76bce73399d57698e529f4744eb5a1a9bcfa6fda7c4b25",
        },
    ),
]
