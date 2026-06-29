---
name: update-tools
description: Check for and apply GitHub release version bumps to tools in ~/.dot/tools.py. Use this skill whenever the user wants to update, bump, upgrade, or check versions of CLI tools managed by this repo (fd, fzf, ripgrep, jq, fish, eza, starship, copilot, and friends), or asks things like "what's outdated", "any new releases", or "refresh the tool manifest". Handles discovery via `gh api`, edits tools.py, and runs update_shas.py to refresh sha256 hashes.
---

# Updating tool versions in ~/.dot/tools.py

`tools.py` is a hand-edited manifest of CLI tools installed from GitHub release binaries. Each entry pins a `version`; `update_shas.py` re-downloads the binaries for that version and rewrites the matching `sha256=...` blocks. Nothing in the repo tells you which tools are behind upstream — that's what this skill is for.

## What the repo already knows

Read `~/.dot/tools.py` before you start; the other files named here are worth a glance if you haven't seen them.

- Each `Tool(...)` entry has `name`, `repo` (e.g. `"sharkdp/fd"`), `version`, and `tag_prefix`. The GitHub tag for a release is `tag_prefix + version`. The download URL is `github.com/{repo}/releases/download/{tag_prefix}{version}/{asset}` — see `~/.dot/install.py:35` for the exact construction.
- `tag_prefix` varies across entries. The three shapes you'll see:
  - `"v"` — most tools. Tag is `v10.4.2`, `version="10.4.2"`.
  - `""` — fish, ripgrep. Tag is the bare version, e.g. `4.6.0`.
  - `"jq-"` — jq. Tag is `jq-1.8.1`, `version="1.8.1"`.
- `assets` maps each `Platform` (only `DARWIN_ARM64` and `LINUX_AMD64` are supported) to a filename template, which may contain `{version}` — formatted with the current version at install time.
- `update_shas.py` ONLY refreshes sha256 hashes for the versions already written into `tools.py`. It does not change versions. Changing the version is your job; it reads what you wrote and downloads accordingly.
- `TOOLS` is kept alphabetical by `name`. Don't reorder.
- Python in this repo is always invoked via `uv run` (the venv is not activated manually).

## Workflow

### 1. Pin down scope

Ask what the user wants: all tools, a named tool, or a subset. If they said "bump fd", that's clear; if they said "update my tools", default to "check all and show what's outdated, then confirm". Don't start editing until scope is confirmed.

### 2. Look up the latest upstream version for each in-scope tool

For each tool, run:

```sh
gh api repos/{repo}/releases/latest --jq .tag_name
```

`/releases/latest` already filters out prereleases and drafts, so you don't need extra logic for that. If your environment doesn't permit `gh api`, `gh release view --repo {repo} --json tagName --jq .tagName` returns the same value — use whichever `gh` subcommand is available.

If `gh` returns an auth error, run `gh auth status` to diagnose, surface the problem, and stop. Don't hand-parse HTML as a fallback.

### 3. Compute the new version

Strip the `tag_prefix` from `tag_name`:

```python
new_version = tag_name.removeprefix(tool.tag_prefix)
```

Worked examples:

| repo | tag_prefix | tag_name (latest) | new_version |
|------|------------|-------------------|-------------|
| `sharkdp/fd` | `"v"` | `v10.5.0` | `10.5.0` |
| `fish-shell/fish-shell` | `""` | `4.6.0` | `4.6.0` |
| `jqlang/jq` | `"jq-"` | `jq-1.8.1` | `1.8.1` |

If stripping the prefix leaves something that doesn't look like a version (contains letters, `-rc1`, `-beta`, etc.), stop and ask the user — the repo may have changed its tagging scheme.

### 4. Show a diff table, then decide whether to proceed

```
tool       current   latest    status
fd         10.4.2    10.5.0    outdated
fzf        0.71.0    0.71.0    up to date
ripgrep    15.1.0    15.2.0    outdated
...
```

Three possible paths from here — pick the right one before touching anything:

- **Check-only prompt** ("what's outdated?", "any new versions of X?", "compare pinned to upstream"). Report the table and stop. Skip steps 5–8 entirely.
- **Nothing is outdated on an edit-intent prompt.** Report "nothing to bump" and stop. Don't run `update_shas.py` just to "refresh" — it only updates hashes for versions you changed, so running it on a no-op yields an empty diff.
- **At least one tool is outdated and the user wants edits.** Let the user pick which bumps to apply (default to "all outdated", make it easy to veto any), then continue to step 5.

### 5. Edit `tools.py`

For each tool to bump, use the `Edit` tool. To guarantee you land on the right entry, anchor the old string on two fields (name + version) with full indentation from the file:

```
old_string:
        name="fd",
        repo="sharkdp/fd",
        version="10.4.2",
new_string:
        name="fd",
        repo="sharkdp/fd",
        version="10.5.0",
```

Do not touch `sha256=...`. That's `update_shas.py`'s job. Editing both by hand invites drift.

### 6. Spot-check the asset URL still resolves

Asset filenames occasionally change between releases (e.g., a project renames `x86_64-unknown-linux-musl` to `linux-x64`). Before running the hash refresh — which tries to download every asset for every platform and aborts on the first failure — HEAD one URL per bumped tool to catch 404s early:

```sh
curl -sI -o /dev/null -w "%{http_code}\n" \
  "https://github.com/{repo}/releases/download/{tag_prefix}{new_version}/{asset_with_version_substituted}"
```

If `curl` isn't available, `gh release view {tag_prefix}{new_version} --repo {repo} --json assets --jq '.assets[].name'` achieves the same thing by listing the actual assets in the release — verify your expected asset name is in that list.

If the asset name isn't in the release, the asset template in `tools.py` needs manual adjustment. Show the user what's actually published (via the same `.assets[].name` query) and stop — don't guess the new template.

### 7. Refresh the sha256 hashes

From `~/.dot`:

```sh
uv run update_shas.py
```

This downloads every asset for every platform and rewrites the sha256 blocks via AST surgery, then runs `ruff format`. Pass its output through. If a single tool's download fails, the script currently aborts — surface the failing tool and leave the remaining work in place for the user to fix.

### 8. Show the diff and offer to commit

```sh
git diff tools.py
```

Summarize in one line: "bumped fd 10.4.2 → 10.5.0, ripgrep 15.1.0 → 15.2.0; hashes refreshed." Don't commit unless the user explicitly asks. The existing commit style is short and lowercase — messages like `update versions` or `update tools`.

## Edge cases

- **A new release has no asset for one of our supported platforms.** Flag it, skip that tool's bump, and move on. The user can decide whether to pin to the last shared version or drop the platform.
- **`gh` is not authenticated.** Run `gh auth status`, surface the problem, and stop.
- **User asks for a specific non-latest version.** Skip step 2 entirely — jump to step 5 with the requested version, then do 6–8.

## Worked example

User: "bump fd to the latest version."

1. Scope: just fd.
2. `gh api repos/sharkdp/fd/releases/latest --jq .tag_name` → `v10.5.0`.
3. `tag_prefix="v"` → new version `10.5.0`.
4. Current in `tools.py`: `10.4.2`. Outdated. Show the one-row diff table, confirm.
5. Edit `tools.py`: `version="10.4.2",` → `version="10.5.0",` inside the fd block.
6. HEAD-check `https://github.com/sharkdp/fd/releases/download/v10.5.0/fd-v10.5.0-aarch64-apple-darwin.tar.gz` — 200 OK.
7. `uv run update_shas.py` — rewrites both sha256 entries for fd.
8. Show `git diff tools.py`; offer to commit as `update versions`.
