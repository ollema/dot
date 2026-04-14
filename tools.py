"""Tool manifest + model. Consumed by install.py."""

from pydantic import BaseModel, ConfigDict, Field


class Tool(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    repo: str = Field(pattern=r"^[^/\s]+/[^/\s]+$")
    version: str
    asset: str
    binary: str | None = None
    strip_components: int = Field(default=1, ge=0)
    is_zip: bool = False
    is_raw_binary: bool = False
    extra_binaries: list[str] = Field(default_factory=list)
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
