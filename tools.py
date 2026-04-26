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
        name="copilot",
        repo="github/copilot-cli",
        version="1.0.36",
        assets={Platform.LINUX_AMD64: "copilot-linux-x64.tar.gz"},
        sha256={
            Platform.LINUX_AMD64: "9b8a00aa6140e0b6eb0245262f7d3f8bdb170a2e782609acdf3d206bbc27b431"
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
        version="4.6.0",
        tag_prefix="",
        extra_binaries=["fish_indent", "fish_key_reader"],
        assets={Platform.LINUX_AMD64: "fish-{version}-linux-x86_64.tar.xz"},
        symlinks=[Link(source="fish", target="~/.config/fish")],
        sha256={
            Platform.LINUX_AMD64: "497c9c4e3fb3c006fe9d2c9a5a5447c1c90490b6b4ce6bfaf75e53b495c82f36"
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
        version="1.25.0",
        assets={
            Platform.DARWIN_ARM64: "starship-aarch64-apple-darwin.tar.gz",
            Platform.LINUX_AMD64: "starship-x86_64-unknown-linux-musl.tar.gz",
        },
        symlinks=[Link(source="starship/starship.toml", target="~/.config/starship.toml")],
        sha256={
            Platform.DARWIN_ARM64: "365301b5f4938322a9f378764b4bc640048bca7d6ac28eaabd406cadd6fc703a",
            Platform.LINUX_AMD64: "0169f187e927a0ee9abf41bb80e316717fea6e37e404267bca5134c6ea10c0ed",
        },
    ),
    Tool(
        name="tree-sitter",
        repo="tree-sitter/tree-sitter",
        version="0.26.8",
        is_zip=True,
        assets={
            Platform.DARWIN_ARM64: "tree-sitter-cli-macos-arm64.zip",
            Platform.LINUX_AMD64: "tree-sitter-cli-linux-x64.zip",
        },
        sha256={
            Platform.DARWIN_ARM64: "9dc0dc3415a1cd30499750579defbf3f8e000a98f12a65cda8e25981f07e7b0f",
            Platform.LINUX_AMD64: "9377d83479ee8e05dce7d2b51442087c7fdd620015834c24fea1a86d4bd0a85b",
        },
    ),
    Tool(
        name="yazi",
        repo="sxyazi/yazi",
        version="26.1.22",
        is_zip=True,
        extra_binaries=["ya"],
        assets={
            Platform.DARWIN_ARM64: "yazi-aarch64-apple-darwin.zip",
            Platform.LINUX_AMD64: "yazi-x86_64-unknown-linux-musl.zip",
        },
        sha256={
            Platform.DARWIN_ARM64: "8355ad582dd9f4ef1f88a228080f2b6116bbb483dd48d1bde555d475f4d2afe4",
            Platform.LINUX_AMD64: "b977351968206c0b78d2ef5bf21351685cc191b58a4c7e1c98c37db5d0a381f8",
        },
    ),
    Tool(
        name="zmx",
        repo="neurosnap/zmx",
        version="0.5.0",
        url_template="https://zmx.sh/a/{asset}",
        assets={
            Platform.DARWIN_ARM64: "zmx-{version}-macos-aarch64.tar.gz",
            Platform.LINUX_AMD64: "zmx-{version}-linux-x86_64.tar.gz",
        },
        sha256={
            Platform.DARWIN_ARM64: "3b9379f0ff0cf107f7f87048d2c45f6fbeabed588d676ad86ac218bed928d107",
            Platform.LINUX_AMD64: "4cc1f6b854dccdcabae4cb91bd0379a23e6f8210048af5d81e0661e594a50c28",
        },
    ),
]
