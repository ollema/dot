from pathlib import Path

import pytest

import symlink

FakeRepo = tuple[Path, Path]


@pytest.fixture
def fake_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> FakeRepo:
    """Point REPO_ROOT at a tmp dir and redirect HOME so ~ expands into tmp too."""
    repo = tmp_path / "repo"
    home = tmp_path / "home"
    repo.mkdir()
    home.mkdir()
    monkeypatch.setattr(symlink, "REPO_ROOT", repo)
    monkeypatch.setenv("HOME", str(home))
    return repo, home


class TestResolve:
    def test_source_is_joined_to_repo_root(self, fake_repo: FakeRepo) -> None:
        repo, _ = fake_repo
        link = symlink.Link(source="fish", target="~/.config/fish")
        source, _target = symlink.resolve(link)
        assert source == repo / "fish"

    def test_target_expands_tilde(self, fake_repo: FakeRepo) -> None:
        _repo, home = fake_repo
        link = symlink.Link(source="fish", target="~/.config/fish")
        _source, target = symlink.resolve(link)
        assert target == home / ".config" / "fish"


class TestApplyLink:
    def _link(self, source: str = "fish", target: str = "~/.config/fish") -> symlink.Link:
        return symlink.Link(source=source, target=target)

    def test_missing_source_errors(
        self, fake_repo: FakeRepo, capsys: pytest.CaptureFixture[str]
    ) -> None:
        symlink.apply_link(self._link(), dry_run=False)
        out = capsys.readouterr().out
        assert "ERROR: source missing" in out

    def test_creates_new_symlink(self, fake_repo: FakeRepo) -> None:
        repo, home = fake_repo
        (repo / "fish").mkdir()
        symlink.apply_link(self._link(), dry_run=False)
        target = home / ".config" / "fish"
        assert target.is_symlink()
        assert target.readlink() == repo / "fish"

    def test_already_linked_is_noop(
        self, fake_repo: FakeRepo, capsys: pytest.CaptureFixture[str]
    ) -> None:
        repo, home = fake_repo
        (repo / "fish").mkdir()
        (home / ".config").mkdir()
        (home / ".config" / "fish").symlink_to(repo / "fish")
        mtime_before = (home / ".config" / "fish").lstat().st_mtime
        symlink.apply_link(self._link(), dry_run=False)
        out = capsys.readouterr().out
        assert "ok (already linked)" in out
        assert (home / ".config" / "fish").lstat().st_mtime == mtime_before

    def test_replaces_stale_symlink(
        self, fake_repo: FakeRepo, capsys: pytest.CaptureFixture[str]
    ) -> None:
        repo, home = fake_repo
        (repo / "fish").mkdir()
        (home / ".config").mkdir()
        stale_target = home / "elsewhere"
        stale_target.mkdir()
        (home / ".config" / "fish").symlink_to(stale_target)
        symlink.apply_link(self._link(), dry_run=False)
        out = capsys.readouterr().out
        assert "replaced existing file/symlink" in out
        assert (home / ".config" / "fish").readlink() == repo / "fish"

    def test_replaces_regular_file(
        self, fake_repo: FakeRepo, capsys: pytest.CaptureFixture[str]
    ) -> None:
        repo, home = fake_repo
        (repo / "starship.toml").write_text("source")
        (home / ".config").mkdir()
        (home / ".config" / "starship.toml").write_text("old")
        link = symlink.Link(source="starship.toml", target="~/.config/starship.toml")
        symlink.apply_link(link, dry_run=False)
        out = capsys.readouterr().out
        assert "replaced existing file/symlink" in out
        target = home / ".config" / "starship.toml"
        assert target.is_symlink()
        assert target.read_text() == "source"

    def test_replaces_real_directory(
        self, fake_repo: FakeRepo, capsys: pytest.CaptureFixture[str]
    ) -> None:
        repo, home = fake_repo
        (repo / "fish").mkdir()
        (repo / "fish" / "config.fish").write_text("ok")
        real_dir = home / ".config" / "fish"
        real_dir.mkdir(parents=True)
        (real_dir / "leftover").write_text("x")
        symlink.apply_link(self._link(), dry_run=False)
        out = capsys.readouterr().out
        assert "replaced existing dir" in out
        assert real_dir.is_symlink()
        assert (real_dir / "config.fish").read_text() == "ok"

    def test_auto_creates_parent_dir(self, fake_repo: FakeRepo) -> None:
        repo, home = fake_repo
        (repo / "fish").mkdir()
        assert not (home / ".config").exists()
        symlink.apply_link(self._link(), dry_run=False)
        assert (home / ".config" / "fish").is_symlink()

    def test_dry_run_would_create(
        self, fake_repo: FakeRepo, capsys: pytest.CaptureFixture[str]
    ) -> None:
        repo, home = fake_repo
        (repo / "fish").mkdir()
        symlink.apply_link(self._link(), dry_run=True)
        out = capsys.readouterr().out
        assert "would create" in out
        assert not (home / ".config").exists()

    def test_dry_run_would_replace_dir(
        self, fake_repo: FakeRepo, capsys: pytest.CaptureFixture[str]
    ) -> None:
        repo, home = fake_repo
        (repo / "fish").mkdir()
        (home / ".config" / "fish").mkdir(parents=True)
        original_inode = (home / ".config" / "fish").stat().st_ino
        symlink.apply_link(self._link(), dry_run=True)
        out = capsys.readouterr().out
        assert "would replace existing dir" in out
        assert (home / ".config" / "fish").stat().st_ino == original_inode
        assert not (home / ".config" / "fish").is_symlink()

    def test_dry_run_would_replace_file_or_symlink(
        self, fake_repo: FakeRepo, capsys: pytest.CaptureFixture[str]
    ) -> None:
        repo, home = fake_repo
        (repo / "fish").mkdir()
        (home / ".config").mkdir()
        (home / ".config" / "fish").symlink_to("/nonexistent/elsewhere")
        symlink.apply_link(self._link(), dry_run=True)
        out = capsys.readouterr().out
        assert "would replace existing file/symlink" in out
        assert (home / ".config" / "fish").readlink() == Path("/nonexistent/elsewhere")


class TestMain:
    def test_dry_run_flag(
        self,
        fake_repo: FakeRepo,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        repo, _ = fake_repo
        for link in symlink.LINKS:
            src = repo / link.source
            if link.source.endswith(".toml"):
                src.parent.mkdir(parents=True, exist_ok=True)
                src.write_text("x")
            else:
                src.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(symlink.sys, "argv", ["symlink.py", "--dry-run"])
        symlink.main()
        out = capsys.readouterr().out
        assert "(dry-run)" in out
        assert "done." in out
