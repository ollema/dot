"""Tool manifest + model. Consumed by install.py."""

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from platforms import Platform


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
    assets: dict[Platform, str]
    sha256: dict[Platform, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _reject_raw_with_extras(self) -> Self:
        if self.is_raw_binary and self.extra_binaries:
            msg = f"{self.name}: is_raw_binary cannot be combined with extra_binaries"
            raise ValueError(msg)
        return self


TOOLS: list[Tool] = [
    Tool(
        name="ripgrep",
        repo="BurntSushi/ripgrep",
        version="14.1.1",
        tag_prefix="",
        binary="rg",
        assets={
            Platform.DARWIN_ARM64: "ripgrep-{version}-aarch64-apple-darwin.tar.gz",
            Platform.LINUX_AMD64: "ripgrep-{version}-x86_64-unknown-linux-musl.tar.gz",
        },
        sha256={
            Platform.DARWIN_ARM64: "24ad76777745fbff131c8fbc466742b011f925bfa4fffa2ded6def23b5b937be",
            Platform.LINUX_AMD64: "4cf9f2741e6c465ffdb7c26f38056a59e2a2544b51f7cc128ef28337eeae4d8e",
        },
    ),
    Tool(
        name="fd",
        repo="sharkdp/fd",
        version="10.2.0",
        assets={
            Platform.DARWIN_ARM64: "fd-v{version}-aarch64-apple-darwin.tar.gz",
            Platform.LINUX_AMD64: "fd-v{version}-x86_64-unknown-linux-musl.tar.gz",
        },
        sha256={
            Platform.DARWIN_ARM64: "ae6327ba8c9a487cd63edd8bddd97da0207887a66d61e067dfe80c1430c5ae36",
            Platform.LINUX_AMD64: "d9bfa25ec28624545c222992e1b00673b7c9ca5eb15393c40369f10b28f9c932",
        },
    ),
    Tool(
        name="eza",
        repo="eza-community/eza",
        version="0.20.14",
        assets={Platform.LINUX_AMD64: "eza_x86_64-unknown-linux-gnu.tar.gz"},
        sha256={
            Platform.LINUX_AMD64: "d86f6641b05c17fba8d55978f038428134d0a246bc53d8695b0193a3a214bce7"
        },
    ),
    Tool(
        name="fzf",
        repo="junegunn/fzf",
        version="0.57.0",
        assets={
            Platform.DARWIN_ARM64: "fzf-{version}-darwin_arm64.tar.gz",
            Platform.LINUX_AMD64: "fzf-{version}-linux_amd64.tar.gz",
        },
        sha256={
            Platform.DARWIN_ARM64: "b4e1c5322652bc2672c32dc37993f8d501df7aecb3fa9e545a3d80eca8ae9a2f",
            Platform.LINUX_AMD64: "a3c087a5f40e8bb4d9bfb26faffa094643df111a469646bef53154a54af9ff92",
        },
    ),
    Tool(
        name="jq",
        repo="jqlang/jq",
        version="1.7.1",
        tag_prefix="jq-",
        is_raw_binary=True,
        assets={Platform.DARWIN_ARM64: "jq-macos-arm64", Platform.LINUX_AMD64: "jq-linux-amd64"},
        sha256={
            Platform.DARWIN_ARM64: "0bbe619e663e0de2c550be2fe0d240d076799d6f8a652b70fa04aea8a8362e8a",
            Platform.LINUX_AMD64: "5942c9b0934e510ee61eb3e30273f1b3fe2590df93933a93d7c58b81d19c8ff5",
        },
    ),
    Tool(
        name="starship",
        repo="starship/starship",
        version="1.21.1",
        assets={
            Platform.DARWIN_ARM64: "starship-aarch64-apple-darwin.tar.gz",
            Platform.LINUX_AMD64: "starship-x86_64-unknown-linux-musl.tar.gz",
        },
        sha256={
            Platform.DARWIN_ARM64: "cf1bf179c10b82ec05915323fbebabcc8f5be9a55678684706af4e1ff117ec89",
            Platform.LINUX_AMD64: "744e21eb2e61b85b0c11378520ebb9e94218de965bca5b8c2266f6c3e23ff5be",
        },
    ),
    Tool(
        name="fish",
        repo="fish-shell/fish-shell",
        version="4.2.1",
        tag_prefix="",
        extra_binaries=["fish_indent", "fish_key_reader"],
        assets={Platform.LINUX_AMD64: "fish-{version}-linux-x86_64.tar.xz"},
        sha256={
            Platform.LINUX_AMD64: "19b88f3a255105226a660a771c81c99196a54f9057567f6dbfcfed68865acdb0"
        },
    ),
]
