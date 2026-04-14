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
uv run pytest
uv run ruff check
uv run ruff format
uv run ty check install.py symlink.py tests
```
