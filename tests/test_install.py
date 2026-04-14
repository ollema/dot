import io
import stat
import tarfile
import urllib.error
import urllib.request
import zipfile
from email.message import Message
from typing import TYPE_CHECKING, Self

import pytest
from pydantic import ValidationError

import install

if TYPE_CHECKING:
    from pathlib import Path


def make_tool(**overrides: object) -> install.Tool:
    base = install.Tool(
        name="rg",
        repo="BurntSushi/ripgrep",
        version="14.1.1",
        asset="ripgrep-{version}-{arch}-{target}.tar.gz",
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
            (
                "Darwin",
                "arm64",
                {"os": "darwin", "arch": "aarch64", "arch_go": "arm64", "target": "apple-darwin"},
            ),
            (
                "Darwin",
                "x86_64",
                {"os": "darwin", "arch": "x86_64", "arch_go": "amd64", "target": "apple-darwin"},
            ),
            (
                "Linux",
                "aarch64",
                {
                    "os": "linux",
                    "arch": "aarch64",
                    "arch_go": "arm64",
                    "target": "unknown-linux-musl",
                },
            ),
            (
                "Linux",
                "amd64",
                {
                    "os": "linux",
                    "arch": "x86_64",
                    "arch_go": "amd64",
                    "target": "unknown-linux-musl",
                },
            ),
        ],
    )
    def test_supported_platforms(
        self,
        monkeypatch: pytest.MonkeyPatch,
        system: str,
        machine: str,
        expected: dict[str, str],
    ) -> None:
        monkeypatch.setattr(install.platform, "system", lambda: system)
        monkeypatch.setattr(install.platform, "machine", lambda: machine)
        pf = install.detect_platform()
        for k, v in expected.items():
            assert pf[k] == v

    def test_capitalized_os_field(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(install.platform, "system", lambda: "Darwin")
        monkeypatch.setattr(install.platform, "machine", lambda: "arm64")
        assert install.detect_platform()["OS"] == "Darwin"

    def test_darwin_target_gnu_is_apple_darwin(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(install.platform, "system", lambda: "Darwin")
        monkeypatch.setattr(install.platform, "machine", lambda: "arm64")
        assert install.detect_platform()["target_gnu"] == "apple-darwin"

    def test_linux_target_gnu(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(install.platform, "system", lambda: "Linux")
        monkeypatch.setattr(install.platform, "machine", lambda: "x86_64")
        assert install.detect_platform()["target_gnu"] == "unknown-linux-gnu"

    def test_unsupported_os(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(install.platform, "system", lambda: "Windows")
        monkeypatch.setattr(install.platform, "machine", lambda: "x86_64")
        with pytest.raises(SystemExit, match="unsupported OS"):
            install.detect_platform()

    def test_unsupported_arch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(install.platform, "system", lambda: "Linux")
        monkeypatch.setattr(install.platform, "machine", lambda: "riscv64")
        with pytest.raises(SystemExit, match="unsupported architecture"):
            install.detect_platform()


class TestResolveAsset:
    def test_fills_all_placeholders(self) -> None:
        pf = {
            "os": "linux",
            "OS": "Linux",
            "arch": "x86_64",
            "arch_go": "amd64",
            "target": "unknown-linux-musl",
            "target_gnu": "unknown-linux-gnu",
        }
        tool = make_tool(asset="ripgrep-{version}-{arch}-{target}.tar.gz")
        assert install.resolve_asset(tool, pf) == "ripgrep-14.1.1-x86_64-unknown-linux-musl.tar.gz"

    def test_uses_tool_version(self) -> None:
        tool = make_tool(version="2.0.0", asset="thing-{version}.tar.gz")
        empty_pf = {
            "os": "",
            "OS": "",
            "arch": "",
            "arch_go": "",
            "target": "",
            "target_gnu": "",
        }
        assert install.resolve_asset(tool, empty_pf) == "thing-2.0.0.tar.gz"


class TestDownloadUrl:
    def test_default_v_prefix(self) -> None:
        tool = make_tool(version="14.1.1")
        assert (
            install.download_url(tool, "foo.tar.gz")
            == "https://github.com/BurntSushi/ripgrep/releases/download/v14.1.1/foo.tar.gz"
        )

    def test_empty_tag_prefix(self) -> None:
        tool = make_tool(version="1.7.1", tag_prefix="jq-")
        assert install.download_url(tool, "jq").startswith(
            "https://github.com/BurntSushi/ripgrep/releases/download/jq-1.7.1/",
        )


class TestFindBinary:
    def test_finds_at_root(self, tmp_path: Path) -> None:
        (tmp_path / "rg").write_text("x")
        assert install.find_binary(tmp_path, "rg") == tmp_path / "rg"

    def test_finds_nested(self, tmp_path: Path) -> None:
        nested = tmp_path / "a" / "b" / "c"
        nested.mkdir(parents=True)
        (nested / "rg").write_text("x")
        assert install.find_binary(tmp_path, "rg") == nested / "rg"

    def test_returns_none_when_missing(self, tmp_path: Path) -> None:
        (tmp_path / "other").write_text("x")
        assert install.find_binary(tmp_path, "rg") is None


class TestExtractAndInstall:
    def test_tar_archive_copies_and_marks_exec(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(install, "INSTALL_DIR", tmp_path)
        data = _make_tar_bytes({"ripgrep-14.1.1/rg": b"binary"})
        tool = make_tool()
        installed = install.extract_and_install(tool, data, "ripgrep.tar.gz")
        assert installed == ["rg"]
        dest = tmp_path / "rg"
        assert dest.read_bytes() == b"binary"
        assert dest.stat().st_mode & stat.S_IXUSR

    def test_zip_archive(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(install, "INSTALL_DIR", tmp_path)
        data = _make_zip_bytes({"fzf": b"binary"})
        tool = make_tool(name="fzf", repo="junegunn/fzf", asset="fzf.zip", is_zip=True)
        installed = install.extract_and_install(tool, data, "fzf.zip")
        assert installed == ["fzf"]
        assert (tmp_path / "fzf").read_bytes() == b"binary"

    def test_zip_detected_from_extension(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(install, "INSTALL_DIR", tmp_path)
        data = _make_zip_bytes({"fzf": b"binary"})
        tool = make_tool(name="fzf", repo="junegunn/fzf", asset="fzf.zip")
        installed = install.extract_and_install(tool, data, "fzf.zip")
        assert installed == ["fzf"]

    def test_raw_binary(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(install, "INSTALL_DIR", tmp_path)
        tool = make_tool(name="jq", repo="jqlang/jq", asset="jq", is_raw_binary=True)
        installed = install.extract_and_install(tool, b"jqbinary", "jq")
        assert installed == ["jq"]
        dest = tmp_path / "jq"
        assert dest.read_bytes() == b"jqbinary"
        assert dest.stat().st_mode & stat.S_IXUSR

    def test_binary_override(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(install, "INSTALL_DIR", tmp_path)
        data = _make_tar_bytes({"pkg/custombin": b"x"})
        tool = make_tool(binary="custombin")
        installed = install.extract_and_install(tool, data, "pkg.tar.gz")
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
        tool = make_tool()
        installed = install.extract_and_install(tool, data, "pkg.tar.gz")
        assert installed == []


class TestToolModel:
    def test_rejects_unknown_field(self) -> None:
        with pytest.raises(ValidationError):
            install.Tool.model_validate(
                {"name": "x", "repo": "a/b", "version": "1", "asset": "x", "bogus": True},
            )

    def test_rejects_bad_repo_pattern(self) -> None:
        with pytest.raises(ValidationError):
            install.Tool(name="x", repo="not-a-valid-repo", version="1", asset="x")

    def test_rejects_missing_required_field(self) -> None:
        with pytest.raises(ValidationError):
            install.Tool.model_validate({"name": "x", "repo": "a/b", "version": "1"})

    def test_rejects_negative_strip_components(self) -> None:
        with pytest.raises(ValidationError):
            install.Tool(name="x", repo="a/b", version="1", asset="x", strip_components=-1)


class TestToolsList:
    def test_tools_module_has_valid_entries(self) -> None:
        import tools

        assert len(tools.TOOLS) > 0
        assert all(isinstance(t, install.Tool) for t in tools.TOOLS)


class TestInstallTool:
    def _pf(self, os_name: str = "darwin") -> dict[str, str]:
        return {
            "os": os_name,
            "OS": os_name.capitalize(),
            "arch": "aarch64",
            "arch_go": "arm64",
            "target": "apple-darwin",
            "target_gnu": "apple-darwin",
        }

    def test_linux_only_skipped_on_darwin(self, capsys: pytest.CaptureFixture[str]) -> None:
        tool = make_tool(linux_only=True)
        install.install_tool(tool, self._pf("darwin"))
        out = capsys.readouterr().out
        assert "skipped (linux only)" in out

    def test_http_error_prints_failed(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        def fake_urlopen(req: urllib.request.Request) -> object:
            raise urllib.error.HTTPError(req.full_url, 404, "Not Found", Message(), None)

        monkeypatch.setattr(install.urllib.request, "urlopen", fake_urlopen)
        tool = make_tool()
        install.install_tool(tool, self._pf("linux"))
        out = capsys.readouterr().out
        assert "FAILED: 404 Not Found" in out

    def test_happy_path_with_mocked_download(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
        tmp_path: Path,
    ) -> None:
        data = _make_tar_bytes({"ripgrep/rg": b"binary"})

        class FakeResp:
            def __enter__(self) -> Self:
                return self

            def __exit__(self, *_: object) -> bool:
                return False

            def read(self) -> bytes:
                return data

        monkeypatch.setattr(
            install.urllib.request,
            "urlopen",
            lambda _req: FakeResp(),
        )
        monkeypatch.setattr(install, "INSTALL_DIR", tmp_path)
        tool = make_tool()
        install.install_tool(tool, self._pf("linux"))
        out = capsys.readouterr().out
        assert "-> rg" in out
        assert (tmp_path / "rg").exists()
