---
name: add-tool
description: Register a new CLI tool in ~/.dot/tools.py from its GitHub releases. Use this skill whenever the user wants to add, register, install, vendor, or pin a new command-line tool to the dotfiles manifest — phrases like "add bat to my tools", "let's start managing zoxide", "vendor `dust` from upstream", "I want `yq` available on my machines", or any request to introduce a new entry to tools.py. Discovers the repo and release via `gh`, asks which platforms to support, picks the right asset per platform, and runs `uv run update_shas.py` to populate hashes. For bumping versions of tools that are already pinned, use the sibling `update-tools` skill instead.
---

# Adding a new tool to ~/.dot/tools.py

`tools.py` is a hand-edited manifest of CLI tools installed from GitHub release binaries. Adding a new entry means picking the right asset name for each supported platform, choosing the right `tag_prefix` and archive flags, slotting the entry into alphabetical order, and letting `update_shas.py` populate the sha256 hashes.

For *bumping* an already-listed tool, use the sibling `update-tools` skill — this skill is only for net-new entries.

## What the repo already knows

Read `~/.dot/tools.py` before you start; the surrounding files matter too if you haven't seen them.

- `Tool(...)` is a Pydantic model in `~/.dot/tools.py`. Fields: `name`, `repo` (`org/name`), `version`, `tag_prefix` (default `"v"`), `binary` (defaults to `name`), `extra_binaries` (other binaries shipped in the same archive), `is_zip`, `is_raw_binary`, `assets` (per-platform asset filename or template), `sha256` (populated by `update_shas.py`), `symlinks`. `extra="forbid"` — typos in field names will Pydantic-error at import time.
- `Platform` (in `~/.dot/platforms.py`) only has two members: `DARWIN_ARM64` and `LINUX_AMD64`. There is no x86 macOS or arm Linux support, so don't try to add asset entries for them.
- The download URL is built in `~/.dot/install.py:35` as `github.com/{repo}/releases/download/{tag_prefix}{version}/{asset}`. Anywhere this skill HEAD-checks a URL, it must follow the same shape.
- `TOOLS` is sorted alphabetically by `name`. Insert your new entry in the right slot — don't append to the end.
- Python in this repo always runs via `uv run` from `~/.dot`. Don't activate the venv by hand.
- The `is_raw_binary=True` constraint forbids `extra_binaries` (model validator). A raw-binary release ships exactly one executable.

## Workflow

### 1. Capture the tool name and (if needed) discover the repo

If the user says "add `bat` from sharkdp/bat", you have everything you need — skip ahead.

If they only give a name ("add `dust`"), find the canonical repo:

```sh
gh search repos dust --limit 5 --json fullName,description,stargazersCount --jq 'sort_by(-.stargazersCount)'
```

Sort by stars descending; the canonical project is almost always the top hit. Show the user the candidates and confirm before continuing — common names ("dust", "git", "fd") have many forks, and picking the wrong one is unrecoverable later in the workflow.

If `gh` isn't authenticated, run `gh auth status`, surface the problem, and stop.

### 2. Ask which platforms to support

Always ask: macOS (`DARWIN_ARM64`), Linux (`LINUX_AMD64`), or both. Default suggestion is **both** unless the release obviously lacks an asset for one platform (you'll find that out in step 4 and can revisit).

### 3. Fetch the latest release

```sh
gh api repos/{repo}/releases/latest --jq '{tag: .tag_name, assets: [.assets[].name]}'
```

This returns the tag name and the full asset list in one call — the two things you need for every remaining step.

### 4. Derive each `Tool(...)` field

Walk these in order. Show the user the derived block before you write anything.

| Field | How to derive |
|---|---|
| `name` | Lowercase tool name. Matches the binary unless the user says otherwise (e.g. ripgrep → `rg` lives in `binary`, name is `ripgrep`). |
| `repo` | Confirmed `org/name` from step 1. |
| `tag_prefix` | See decision tree below. |
| `version` | `tag_name.removeprefix(tag_prefix)`. Sanity check it looks like a version — bare digits and dots, maybe a trailing letter. If you see `-rc1`, `-beta`, etc., stop and ask: this skill targets stable releases. |
| `assets` | One entry per chosen platform. Use the matching heuristic below. If the version literal appears in the asset name, replace it with `{version}` so the template survives future bumps. |
| `is_raw_binary` | `True` iff the asset has no archive extension (`.tar.gz`, `.tar.xz`, `.tgz`, `.zip`). The asset is the binary itself. |
| `is_zip` | `True` iff the asset ends in `.zip` and is **not** raw. |
| `binary` | Omit unless the binary name differs from `name` (e.g. ripgrep → `rg`). |
| `extra_binaries` | Empty by default. Only add if the user calls out related binaries shipped together (`fish_indent`, `fish_key_reader`). |
| `symlinks` | Empty by default. Only add if the user wants a config file linked into `~/.config/`. |
| `sha256` | **Leave it off entirely.** `update_shas.py` writes it in step 7. |

### `tag_prefix` decision tree

Look at `tag_name`:

- Starts with `v` followed by something that looks like a version (`v10.5.0`, `v0.24.0`) → `tag_prefix="v"`. This is the default; don't even set the field — `Tool` defaults to `"v"`.
- Bare version with no prefix (`4.6.0`, `15.1.0`) → `tag_prefix=""`.
- Anything else (`jq-1.8.1`, `release-2024-03-01`) → set `tag_prefix` to the literal prefix that comes before the version part, including any trailing dash.

### Asset matching heuristic

Per platform, pick the highest-scoring asset from the release's asset list:

- **`DARWIN_ARM64`** — must contain one of: `aarch64-apple-darwin`, `darwin-arm64`, `darwin_arm64`, `arm64-apple-darwin`, `macos-arm64`, `darwin-aarch64`. Reject anything containing `x86_64`, `amd64`, `intel`, `i686`.
- **`LINUX_AMD64`** — must contain one of: `x86_64-unknown-linux-musl` (preferred), `x86_64-unknown-linux-gnu`, `linux-x64`, `linux_amd64`, `linux-amd64`, `x86_64-linux`. Reject `aarch64`, `arm64`, `i686`, `armv7`.

Tiebreakers when multiple assets match:

- Linux: prefer `musl` over `gnu` — static binaries port across distros without glibc surprises.
- Prefer `.tar.gz` over `.tar.xz` over `.zip` (extraction code paths are tested most heavily on `.tar.gz`).
- Prefer files without `-debug`, `-static-debug`, `-sources`, `.sha256`, `.sig`, `.asc` suffixes — those aren't installable binaries.

If nothing matches a platform, show the full asset list and ask the user to pick. Don't guess.

### 5. HEAD-check each chosen asset URL

Catch typos and renamed assets before `update_shas.py` tries to download them:

```sh
curl -sI -o /dev/null -w "%{http_code}\n" \
  "https://github.com/{repo}/releases/download/{tag_prefix}{version}/{asset_with_version_substituted}"
```

A `200` (or `302` → `200`) is fine. Anything else: stop and show the user the actual asset list (`gh release view {tag} --repo {repo} --json assets --jq '.assets[].name'`) so they can correct your match.

### 6. Edit `tools.py` — insert alphabetically

Find the existing entry whose `name` would sort *just after* the new tool. Use `Edit` with the start of that entry as the anchor, prepending your new `Tool(...)` block. If your new tool sorts last (after every existing entry), anchor on the closing `]` instead.

Example — adding `bat` (sorts before `copilot`):

```
old_string:
    Tool(
        name="copilot",
new_string:
    Tool(
        name="bat",
        repo="sharkdp/bat",
        version="0.24.0",
        assets={
            Platform.DARWIN_ARM64: "bat-v{version}-aarch64-apple-darwin.tar.gz",
            Platform.LINUX_AMD64: "bat-v{version}-x86_64-unknown-linux-musl.tar.gz",
        },
    ),
    Tool(
        name="copilot",
```

Don't write `sha256={...}`. Don't write fields that match their defaults (`tag_prefix="v"`, empty lists/dicts) — keep the entry minimal. The Pydantic model fills them in.

### 7. Populate sha256 hashes

From `~/.dot`:

```sh
uv run update_shas.py
```

This downloads every asset for every platform listed in `tools.py`, hashes them, rewrites the `sha256={...}` blocks via AST surgery, and runs `ruff format`. If a download fails for your new tool, the script aborts — that almost always means an asset name is wrong; go back to step 5 and re-verify.

### 8. Sanity check, show diff, offer to commit

```sh
uv run python -c "import tools; print([t.name for t in tools.TOOLS])"
git diff tools.py
```

The first line confirms the file imports cleanly (Pydantic validation passes) and the names are alphabetical. The second shows just your new entry plus its sha lines.

Summarise in one line ("added bat 0.24.0 for darwin-arm64, linux-amd64") and offer to commit. The commit style in this repo is short and lowercase (`add bat`, `add zoxide`).

## Edge cases

- **Release has no asset for one of the requested platforms.** Tell the user, and offer to pin only the platforms where an asset exists. Don't make up a match.
- **Asset is a raw binary (e.g. jq, yq).** Set `is_raw_binary=True`; do not set `extra_binaries` (model validator forbids the combination). The `binary` field still defaults to `name`, so a raw release whose binary file is literally named `yq` needs no extra config.
- **Binary name differs from the project name** (ripgrep → `rg`, the-silver-searcher → `ag`). Set `binary="rg"`. Keep `name` as the project name so the entry is recognisable in the manifest.
- **Archive ships multiple binaries you want** (fish ships `fish`, `fish_indent`, `fish_key_reader`). Put the primary in `binary` (or let it default to `name`) and the rest in `extra_binaries=[...]`. They're all installed from the same archive.
- **Asset name doesn't include the version.** Just use the literal asset name without a `{version}` placeholder. The template is only useful when the version actually appears in the filename.
- **User wants pre-release / nightly.** `gh api .../releases/latest` filters those out. If the user explicitly wants one, switch to `gh api repos/{repo}/releases --jq '.[0]'` and confirm the tag with the user before continuing.

## Worked example: adding `bat`

User: "add `bat` to my tools."

1. Repo: `sharkdp/bat` (well-known; no `gh search` needed).
2. Platforms: ask. User says both.
3. `gh api repos/sharkdp/bat/releases/latest --jq '{tag: .tag_name, assets: [.assets[].name]}'` →
   ```
   {"tag": "v0.24.0", "assets": ["bat-v0.24.0-aarch64-apple-darwin.tar.gz", "bat-v0.24.0-x86_64-unknown-linux-gnu.tar.gz", "bat-v0.24.0-x86_64-unknown-linux-musl.tar.gz", ...]}
   ```
4. Derived:
   - `tag_prefix="v"` (default — omit), `version="0.24.0"`.
   - `DARWIN_ARM64`: `bat-v{version}-aarch64-apple-darwin.tar.gz`.
   - `LINUX_AMD64`: `bat-v{version}-x86_64-unknown-linux-musl.tar.gz` (musl > gnu).
   - Archive is `.tar.gz` → no `is_zip`, no `is_raw_binary`.
   - Binary name matches project name → no `binary` override.
5. HEAD-check both URLs → 200.
6. Insert before `copilot` in `tools.py` (b < c).
7. `uv run update_shas.py` → fills in two sha256 lines for bat.
8. `git diff tools.py` shows the new block; offer to commit as `add bat`.
