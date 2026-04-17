import hashlib
import io
import stat
import tarfile
import urllib.error
import urllib.request
import zipfile
from email.message import Message
from typing import TYPE_CHECKING, Self

import pytest
from rich.progress import TaskID

import install
import platforms
from platforms import Platform

if TYPE_CHECKING:
    from pathlib import Path
    from typing import ClassVar


class _FakeProgress:
    def update(self, *_args: object, **_kwargs: object) -> None: ...
    def remove_task(self, *_args: object, **_kwargs: object) -> None: ...


_FAKE_PROGRESS = _FakeProgress()
_FAKE_TASK_ID = TaskID(0)


def make_tool(**overrides: object) -> install.Tool:
    base = install.Tool(
        name="rg",
        repo="BurntSushi/ripgrep",
        version="14.1.1",
        assets={
            Platform.DARWIN_ARM64: "ripgrep-{version}-aarch64-apple-darwin.tar.gz",
            Platform.LINUX_AMD64: "ripgrep-{version}-x86_64-unknown-linux-musl.tar.gz",
        },
    )
    return base.model_copy(update=overrides) if overrides else base


def _make_tar_bytes(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tf:
        for path, data in files.items():
            info = tarfile.TarInfo(name=path)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def _make_zip_bytes(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for path, data in files.items():
            zf.writestr(path, data)
    return buf.getvalue()


class TestDetectPlatform:
    @pytest.mark.parametrize(
        ("system", "machine", "expected"),
        [
            ("Darwin", "arm64", Platform.DARWIN_ARM64),
            ("Darwin", "aarch64", Platform.DARWIN_ARM64),
            ("Linux", "amd64", Platform.LINUX_AMD64),
            ("Linux", "x86_64", Platform.LINUX_AMD64),
        ],
    )
    def test_supported_platforms(
        self,
        monkeypatch: pytest.MonkeyPatch,
        system: str,
        machine: str,
        expected: Platform,
    ) -> None:
        monkeypatch.setattr(platforms.platform, "system", lambda: system)
        monkeypatch.setattr(platforms.platform, "machine", lambda: machine)
        assert platforms.detect() == expected

    @pytest.mark.parametrize(
        ("system", "machine"),
        [
            ("Windows", "x86_64"),
            ("Linux", "riscv64"),
            ("Darwin", "x86_64"),
        ],
    )
    def test_unsupported(self, monkeypatch: pytest.MonkeyPatch, system: str, machine: str) -> None:
        monkeypatch.setattr(platforms.platform, "system", lambda: system)
        monkeypatch.setattr(platforms.platform, "machine", lambda: machine)
        with pytest.raises(SystemExit, match="unsupported platform"):
            platforms.detect()


class TestResolveAsset:
    def test_renders_version_placeholder(self) -> None:
        tool = make_tool()
        assert (
            install.resolve_asset(tool, Platform.LINUX_AMD64)
            == "ripgrep-14.1.1-x86_64-unknown-linux-musl.tar.gz"
        )
        assert (
            install.resolve_asset(tool, Platform.DARWIN_ARM64)
            == "ripgrep-14.1.1-aarch64-apple-darwin.tar.gz"
        )


class TestDownloadUrl:
    @pytest.mark.parametrize(
        ("tag_prefix", "expected_tag"),
        [("v", "v14.1.1"), ("", "14.1.1"), ("jq-", "jq-14.1.1")],
    )
    def test_respects_tag_prefix(self, tag_prefix: str, expected_tag: str) -> None:
        tool = make_tool(tag_prefix=tag_prefix)
        assert install.download_url(tool, "foo.tar.gz") == (
            f"https://github.com/BurntSushi/ripgrep/releases/download/{expected_tag}/foo.tar.gz"
        )


class TestFindBinary:
    def test_finds_nested_file(self, tmp_path: Path) -> None:
        nested = tmp_path / "a" / "b" / "c"
        nested.mkdir(parents=True)
        (nested / "rg").write_text("x")
        assert install.find_binary(tmp_path, "rg") == nested / "rg"


class TestExtractAndInstall:
    def test_tar_archive_copies_and_marks_exec(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(install, "INSTALL_DIR", tmp_path)
        data = _make_tar_bytes({"ripgrep-14.1.1/rg": b"binary"})
        installed = install.extract_and_install(make_tool(binary="rg"), data, "ripgrep.tar.gz")
        assert installed == ["rg"]
        dest = tmp_path / "rg"
        assert dest.read_bytes() == b"binary"
        assert dest.stat().st_mode & stat.S_IXUSR

    def test_zip_archive(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(install, "INSTALL_DIR", tmp_path)
        data = _make_zip_bytes({"fzf": b"binary"})
        tool = make_tool(
            name="fzf",
            repo="junegunn/fzf",
            assets={Platform.LINUX_AMD64: "fzf.zip"},
            is_zip=True,
        )
        installed = install.extract_and_install(tool, data, "fzf.zip")
        assert installed == ["fzf"]
        assert (tmp_path / "fzf").read_bytes() == b"binary"

    def test_zip_detected_from_extension(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(install, "INSTALL_DIR", tmp_path)
        data = _make_zip_bytes({"fzf": b"binary"})
        tool = make_tool(
            name="fzf",
            repo="junegunn/fzf",
            assets={Platform.LINUX_AMD64: "fzf.zip"},
        )
        installed = install.extract_and_install(tool, data, "fzf.zip")
        assert installed == ["fzf"]

    def test_raw_binary(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(install, "INSTALL_DIR", tmp_path)
        tool = make_tool(
            name="jq",
            repo="jqlang/jq",
            assets={Platform.LINUX_AMD64: "jq"},
            is_raw_binary=True,
        )
        installed = install.extract_and_install(tool, b"jqbinary", "jq")
        assert installed == ["jq"]
        dest = tmp_path / "jq"
        assert dest.read_bytes() == b"jqbinary"
        assert dest.stat().st_mode & stat.S_IXUSR

    def test_binary_override(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(install, "INSTALL_DIR", tmp_path)
        data = _make_tar_bytes({"pkg/custombin": b"x"})
        installed = install.extract_and_install(make_tool(binary="custombin"), data, "pkg.tar.gz")
        assert installed == ["custombin"]

    def test_extra_binaries_all_copied(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(install, "INSTALL_DIR", tmp_path)
        data = _make_tar_bytes(
            {
                "pkg/fish": b"fish",
                "pkg/fish_indent": b"indent",
                "pkg/fish_key_reader": b"reader",
            },
        )
        tool = make_tool(
            name="fish",
            repo="fish-shell/fish-shell",
            extra_binaries=["fish_indent", "fish_key_reader"],
        )
        installed = install.extract_and_install(tool, data, "pkg.tar.gz")
        assert installed == ["fish", "fish_indent", "fish_key_reader"]
        for b in installed:
            assert (tmp_path / b).exists()

    def test_missing_binary_in_archive(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(install, "INSTALL_DIR", tmp_path)
        data = _make_tar_bytes({"pkg/something-else": b"x"})
        assert install.extract_and_install(make_tool(), data, "pkg.tar.gz") == []

    def test_prefix_install_extracts_full_tree(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        install_dir = tmp_path / "bin"
        install_dir.mkdir()
        monkeypatch.setattr(install, "INSTALL_DIR", install_dir)
        data = _make_tar_bytes(
            {
                "nvim-linux-x86_64/bin/nvim": b"binary",
                "nvim-linux-x86_64/share/nvim/runtime/syntax.vim": b"syntax",
                "nvim-linux-x86_64/lib/nvim/parser/c.so": b"parser",
            },
        )
        tool = make_tool(name="neovim", repo="neovim/neovim", binary="nvim", prefix_install=True)
        installed = install.extract_and_install(tool, data, "nvim-linux-x86_64.tar.gz")
        assert installed == ["nvim"]
        nvim = install_dir / "nvim"
        assert nvim.read_bytes() == b"binary"
        assert nvim.stat().st_mode & stat.S_IXUSR
        assert (tmp_path / "share" / "nvim" / "runtime" / "syntax.vim").read_bytes() == b"syntax"
        assert (tmp_path / "lib" / "nvim" / "parser" / "c.so").read_bytes() == b"parser"


def _fake_download(data: bytes) -> type:
    class FakeResp:
        headers: ClassVar[dict[str, str]] = {"Content-Length": str(len(data))}

        def __enter__(self) -> Self:
            self._stream = io.BytesIO(data)
            return self

        def __exit__(self, *_: object) -> bool:
            return False

        def read(self, size: int = -1) -> bytes:
            return self._stream.read(size)

    return FakeResp


class TestInstallTool:
    def test_missing_asset_for_platform_skipped(self) -> None:
        tool = make_tool(
            assets={Platform.LINUX_AMD64: "only-linux.tar.gz"},
        )
        result = install.install_tool(tool, Platform.DARWIN_ARM64, _FAKE_PROGRESS, _FAKE_TASK_ID)
        assert result.state == "skip"
        assert "not available on darwin-arm64" in result.detail

    def test_http_error_prints_failed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def fake_urlopen(req: urllib.request.Request, **_: object) -> object:
            raise urllib.error.HTTPError(req.full_url, 404, "Not Found", Message(), None)

        monkeypatch.setattr(install.urllib.request, "urlopen", fake_urlopen)
        result = install.install_tool(
            make_tool(), Platform.LINUX_AMD64, _FAKE_PROGRESS, _FAKE_TASK_ID
        )
        assert result.state == "fail"
        assert "404 Not Found" in result.detail


class TestShaVerification:
    def _install_with(
        self,
        tool: install.Tool,
        data: bytes,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> install.Result:
        fake = _fake_download(data)
        monkeypatch.setattr(install.urllib.request, "urlopen", lambda _req, **_kw: fake())
        monkeypatch.setattr(install, "INSTALL_DIR", tmp_path)
        return install.install_tool(tool, Platform.LINUX_AMD64, _FAKE_PROGRESS, _FAKE_TASK_ID)

    def test_matching_sha_installs(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        data = _make_tar_bytes({"ripgrep/rg": b"binary"})
        tool = make_tool(
            binary="rg",
            sha256={Platform.LINUX_AMD64: hashlib.sha256(data).hexdigest()},
        )
        result = self._install_with(tool, data, tmp_path, monkeypatch)
        assert result.state == "ok"
        assert result.detail == "rg"
        assert (tmp_path / "rg").exists()

    def test_mismatched_sha_aborts_and_skips_write(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        data = _make_tar_bytes({"ripgrep/rg": b"binary"})
        tool = make_tool(binary="rg", sha256={Platform.LINUX_AMD64: "0" * 64})
        result = self._install_with(tool, data, tmp_path, monkeypatch)
        assert result.state == "fail"
        assert "sha256 mismatch" in result.detail
        assert not (tmp_path / "rg").exists()

    def test_missing_sha_for_platform_aborts(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        data = _make_tar_bytes({"ripgrep/rg": b"binary"})
        tool = make_tool(binary="rg", sha256={Platform.DARWIN_ARM64: "a" * 64})
        result = self._install_with(tool, data, tmp_path, monkeypatch)
        assert result.state == "fail"
        assert "no sha256 recorded" in result.detail
        assert not (tmp_path / "rg").exists()


class TestToolValidation:
    def test_raw_binary_with_extras_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="cannot be combined with extra_binaries"):
            install.Tool(
                name="rg",
                repo="BurntSushi/ripgrep",
                version="1.0.0",
                is_raw_binary=True,
                extra_binaries=["other"],
                assets={Platform.LINUX_AMD64: "foo"},
            )

    def test_raw_binary_and_prefix_install_are_mutually_exclusive(self) -> None:
        with pytest.raises(ValueError, match="mutually exclusive"):
            install.Tool(
                name="rg",
                repo="BurntSushi/ripgrep",
                version="1.0.0",
                is_raw_binary=True,
                prefix_install=True,
                assets={Platform.LINUX_AMD64: "foo"},
            )


class TestManifestIntegrity:
    @pytest.fixture(scope="class")
    def tools_list(self) -> list[install.Tool]:
        import tools

        return tools.TOOLS

    def test_every_tool_renders_fully_on_every_supported_platform(
        self, tools_list: list[install.Tool]
    ) -> None:
        for tool in tools_list:
            for pf in tool.assets:
                asset = install.resolve_asset(tool, pf)
                assert "{" not in asset, f"{tool.name} left an unresolved placeholder: {asset}"
                url = install.download_url(tool, asset)
                assert url.startswith(f"https://github.com/{tool.repo}/releases/download/"), url

    def test_every_tool_has_sha_for_every_declared_platform(
        self, tools_list: list[install.Tool]
    ) -> None:
        for tool in tools_list:
            for pf in tool.assets:
                assert pf in tool.sha256, f"{tool.name} missing sha256 for {pf.value}"
                assert len(tool.sha256[pf]) == 64, (  # noqa: PLR2004
                    f"{tool.name}[{pf.value}] sha256 is not 64 hex chars"
                )
