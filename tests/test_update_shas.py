import hashlib
import io
import textwrap
from typing import TYPE_CHECKING, ClassVar, Self

import pytest

import tools as tools_module
import update_shas
from platforms import Platform

if TYPE_CHECKING:
    import urllib.request
    from pathlib import Path


def _fake_resp(data: bytes) -> type:
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


class TestDownloadAndHash:
    def test_substitutes_version_and_asset_and_hashes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        payload = b"example-binary-content"
        captured: list[str] = []

        def fake_urlopen(req: urllib.request.Request, **_: object) -> object:
            captured.append(req.full_url)
            return _fake_resp(payload)()

        monkeypatch.setattr(update_shas.urllib.request, "urlopen", fake_urlopen)

        tool = tools_module.Tool(
            name="zmx",
            repo="neurosnap/zmx",
            version="0.5.0",
            url_template="https://zmx.sh/a/{asset}",
            assets={Platform.LINUX_AMD64: "zmx-{version}-linux-x86_64.tar.gz"},
        )

        shas = update_shas.download_and_hash(tool)

        assert shas == {Platform.LINUX_AMD64: hashlib.sha256(payload).hexdigest()}
        assert captured == ["https://zmx.sh/a/zmx-0.5.0-linux-x86_64.tar.gz"]

    def test_hashes_each_declared_platform_independently(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        payloads = {
            "https://example.com/1.0.0/d-1.0.0.bin": b"darwin-bytes",
            "https://example.com/1.0.0/l-1.0.0.bin": b"linux-bytes",
        }

        def fake_urlopen(req: urllib.request.Request, **_: object) -> object:
            return _fake_resp(payloads[req.full_url])()

        monkeypatch.setattr(update_shas.urllib.request, "urlopen", fake_urlopen)

        tool = tools_module.Tool(
            name="fake",
            repo="owner/fake",
            version="1.0.0",
            url_template="https://example.com/{version}/{asset}",
            assets={
                Platform.DARWIN_ARM64: "d-{version}.bin",
                Platform.LINUX_AMD64: "l-{version}.bin",
            },
        )

        shas = update_shas.download_and_hash(tool)

        assert shas[Platform.DARWIN_ARM64] == hashlib.sha256(b"darwin-bytes").hexdigest()
        assert shas[Platform.LINUX_AMD64] == hashlib.sha256(b"linux-bytes").hexdigest()

    def test_raises_when_url_template_missing(self) -> None:
        tool = tools_module.Tool(
            name="plain",
            repo="owner/repo",
            version="1.0.0",
            assets={Platform.LINUX_AMD64: "foo"},
        )
        with pytest.raises(ValueError, match="requires url_template"):
            update_shas.download_and_hash(tool)


class TestCollectShasBranching:
    def test_url_template_tool_skips_gh_api(self, monkeypatch: pytest.MonkeyPatch) -> None:
        gh_calls: list[tuple[str, str]] = []

        def fake_gh(_gh: str, repo: str, tag: str) -> dict[str, str]:
            gh_calls.append((repo, tag))
            return {"asset-gnu.tar.gz": "a" * 64}

        download_calls: list[str] = []

        def fake_download_and_hash(tool: tools_module.Tool) -> dict[Platform, str]:
            download_calls.append(tool.name)
            return dict.fromkeys(tool.assets, "b" * 64)

        monkeypatch.setattr(update_shas, "gh_release_digests", fake_gh)
        monkeypatch.setattr(update_shas, "download_and_hash", fake_download_and_hash)
        monkeypatch.setattr(
            update_shas,
            "TOOLS",
            [
                tools_module.Tool(
                    name="gh-tool",
                    repo="owner/ghtool",
                    version="1.0.0",
                    assets={Platform.LINUX_AMD64: "asset-gnu.tar.gz"},
                ),
                tools_module.Tool(
                    name="curl-tool",
                    repo="owner/curltool",
                    version="2.0.0",
                    url_template="https://example.com/{asset}",
                    assets={Platform.LINUX_AMD64: "curl-tool-{version}.tar.gz"},
                ),
            ],
        )

        result = update_shas.collect_shas("fake-gh-path")

        assert result["gh-tool"] == {Platform.LINUX_AMD64: "a" * 64}
        assert result["curl-tool"] == {Platform.LINUX_AMD64: "b" * 64}
        assert gh_calls == [("owner/ghtool", "v1.0.0")]
        assert download_calls == ["curl-tool"]


class TestRewriteManifest:
    @pytest.fixture
    def synthetic_tools_py(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
        target = tmp_path / "tools.py"
        target.write_text(
            textwrap.dedent("""\
                from platforms import Platform

                TOOLS = [
                    Tool(
                        name="foo",
                        repo="owner/foo",
                        version="1.0.0",
                        assets={Platform.LINUX_AMD64: "foo.tar.gz"},
                    ),
                    Tool(
                        name="bar",
                        repo="owner/bar",
                        version="2.0.0",
                        assets={Platform.LINUX_AMD64: "bar.tar.gz"},
                        sha256={Platform.LINUX_AMD64: "stale-placeholder"},
                    ),
                ]
            """)
        )
        monkeypatch.setattr(update_shas, "TOOLS_PY", target)
        return target

    def test_adds_sha_to_tool_that_had_none(self, synthetic_tools_py: Path) -> None:
        update_shas.rewrite_manifest(
            {
                "foo": {Platform.LINUX_AMD64: "a" * 64},
                "bar": {Platform.LINUX_AMD64: "b" * 64},
            }
        )
        text = synthetic_tools_py.read_text()
        assert "a" * 64 in text
        assert "b" * 64 in text

    def test_replaces_existing_sha_rather_than_duplicating(self, synthetic_tools_py: Path) -> None:
        update_shas.rewrite_manifest(
            {
                "foo": {Platform.LINUX_AMD64: "a" * 64},
                "bar": {Platform.LINUX_AMD64: "b" * 64},
            }
        )
        text = synthetic_tools_py.read_text()
        assert "stale-placeholder" not in text
        assert text.count("sha256=") == len(["foo", "bar"])

    def test_is_idempotent(self, synthetic_tools_py: Path) -> None:
        shas = {
            "foo": {Platform.LINUX_AMD64: "a" * 64},
            "bar": {Platform.LINUX_AMD64: "b" * 64},
        }
        update_shas.rewrite_manifest(shas)
        first = synthetic_tools_py.read_text()
        update_shas.rewrite_manifest(shas)
        assert synthetic_tools_py.read_text() == first

    def test_rejects_file_without_tools_assignment(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        target = tmp_path / "tools.py"
        target.write_text("OTHER = []\n")
        monkeypatch.setattr(update_shas, "TOOLS_PY", target)
        with pytest.raises(SystemExit, match="could not locate TOOLS"):
            update_shas.rewrite_manifest({})
