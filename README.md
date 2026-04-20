# dot

dotfiles

## Usage

```sh
uv run symlink.py --dry-run   # preview symlinks
uv run symlink.py             # apply them
uv run install.py             # download binaries listed in tools.toml into ~/.local/bin
```

## Development

```sh
uv sync --dev
uv run prek install          # install git hook (runs on every commit)
uv run prek run --all-files  # format, lint, type-check and test
```

Run a single check directly:

```sh
uv run ruff check
uv run ruff format
uv run ty check install.py symlink.py tools.py tests
uv run pytest
```

## List of tools installed with Homebrew

These are either:
- not available as precompiled binaries for macos
- not needed on the the linux systems
- already installed on the linux systems

```bash
> brew leaves
autossh
eza
ffmpeg
gh
git-lfs
```
