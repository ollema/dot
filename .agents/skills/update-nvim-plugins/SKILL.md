---
name: update-nvim-plugins
description: Check for and apply upstream commit bumps to Neovim plugins pinned in ~/.dot/nvim/nvim-pack-lock.json (managed by vim.pack, the built-in plugin manager). Use this skill whenever the user wants to update, bump, upgrade, sync, or check versions of their Neovim plugins/packages — phrases like "update my nvim plugins", "are any neovim packages outdated", "bump mini.nvim", "sync my nvim lockfile", "what's new on nvim-treesitter upstream", or "refresh my neovim packages". Compares pinned commits against upstream default-branch HEAD via `gh api`, then drives `vim.pack.update(..., { force = true })` through headless `nvim` so vim.pack itself rewrites the lockfile and fires update hooks.
---

# Updating Neovim plugins in ~/.dot/nvim/nvim-pack-lock.json

`nvim-pack-lock.json` is the lockfile maintained by `vim.pack` — Neovim 0.12's built-in plugin manager. Each entry pins one plugin to a specific git commit (`rev`) of a git remote (`src`). The actual `vim.pack.add({ ... })` calls in `~/.dot/nvim/init.lua` and `~/.dot/nvim/plugin/*.lua` declare *which* plugins exist; the lockfile records *which commit* of each is currently installed.

This skill is for moving those pinned commits forward to match upstream. For adding a new plugin entirely, edit the relevant `vim.pack.add({...})` block and let `vim.pack` populate the lockfile on next startup — that's a different workflow.

## What the repo already knows

Read `~/.dot/nvim/nvim-pack-lock.json` before you start. The other files named here are worth a glance if you haven't seen them.

- Each lockfile entry has the shape `"plugin-name": { "rev": "<40-char sha>", "src": "https://github.com/<owner>/<repo>" }`. The full SHA is what `vim.pack` checks out; short SHAs (first 7-12 chars) are only for display.
- **The lockfile is owned by `vim.pack` and is not meant to be edited by hand.** Per the official guide, `vim.pack.update()` is what rewrites it after a successful update. This skill always routes apply-time changes through `vim.pack.update(..., { force = true })`; the lockfile diff falls out as a side effect. Hand-editing risks getting out of sync with what's on disk (`:checkhealth vim.pack` will flag that drift).
- Which "ref" each plugin tracks is decided by the `vim.pack.add({ ... })` spec, not by the lockfile. The plugins in `~/.dot/nvim/init.lua` and `~/.dot/nvim/plugin/40_plugins.lua` are all added as plain URL strings (no `version` field), so they track the default branch's HEAD. That's why upstream comparison uses `commits/HEAD`, not the latest release tag.
- All currently-pinned plugins live on GitHub, so `gh api` is the right tool for upstream lookups. If a future entry adds a non-GitHub src (e.g. a Sourcehut or self-hosted git URL), fall back to `git ls-remote {src} HEAD` — same idea, just a different transport.
- Plugin update hooks live in `~/.dot/nvim/plugin/40_plugins.lua` — notably, `nvim-treesitter` runs `:TSUpdate` via `Config.on_packchanged(...)` (which wraps the `PackChanged` autocmd) after each update to rebuild parsers. The `PackChanged` event fires only when changes flow through `vim.pack` functions, which is another reason apply goes through `vim.pack.update()` and not file edits.

## Workflow

### 1. Pin down scope

Ask what the user wants: all plugins, a named one (e.g. "bump mini.nvim"), or a subset (e.g. "just the treesitter ones"). For a vague "update my nvim packages", default to "check all and report, confirm before applying". Don't start editing until scope is confirmed — applying an unwanted bump to a treesitter parser can trigger a long rebuild.

### 2. Look up the latest upstream commit for each in-scope plugin

For each plugin, parse `<owner>/<repo>` from the `src` URL (strip leading `https://github.com/` and any trailing `.git`), then run:

```sh
gh api repos/{owner}/{repo}/commits/HEAD --jq '.sha'
```

`commits/HEAD` resolves to the latest commit on the repo's default branch (which may be `main`, `master`, or something else — you don't need to know which; `HEAD` follows the default branch automatically). Capture the full 40-char SHA — that's what goes into the lockfile.

Optionally, to get a sense of how far behind each plugin is, ask:

```sh
gh api repos/{owner}/{repo}/compare/{current_rev}...HEAD --jq '{ahead: .ahead_by, behind: .behind_by}'
```

`ahead` is how many upstream commits are not yet pinned. `behind` is usually 0 unless upstream force-pushed. This is informational only — the skill doesn't gate on it.

If `gh` returns an auth error, run `gh auth status`, surface the problem, and stop. Don't try to scrape commit pages as a fallback.

### 3. Show a diff table, then decide whether to proceed

Use short SHAs (first 7 chars) for readability. The `ahead` count is optional but lands well — it tells the user whether the bump is a 3-commit fast-forward or a 200-commit jump.

```
plugin                          current   latest    ahead   status
conform.nvim                    086a40d   086a40d   0       up to date
everforest                      aeef62e   b1c2d3e   12      outdated
friendly-snippets               6cd7280   6cd7280   0       up to date
mini.nvim                       29447d7   f4e5d6c   34      outdated
nvim-lspconfig                  4b7fbaa   9a8b7c6   8       outdated
nvim-treesitter                 4916d65   2718e29   156     outdated  ⚠ runs :TSUpdate hook
nvim-treesitter-textobjects     851e865   851e865   0       up to date
```

Call out the `nvim-treesitter` hook explicitly if it's in the bump set — `:TSUpdate` recompiles every installed parser and can take several minutes. The user may want to defer it or run it in a separate session.

Three possible paths from here — pick the right one before touching anything:

- **Check-only prompt** ("what's outdated?", "any new commits on X?", "compare pinned to upstream"). Report the table and stop. Skip steps 4–5 entirely.
- **Nothing is outdated on an edit-intent prompt.** Report "nothing to bump" and stop. Don't run the headless update — there's nothing for `vim.pack` to do.
- **At least one plugin is outdated and the user wants to apply.** Let the user pick which bumps to apply (default to "all outdated", make it easy to veto any — especially `nvim-treesitter` if they don't want to wait for parser rebuilds), then continue.

### 4. Apply the bump via headless `nvim`

Hand off to `vim.pack` — it fetches new commits, rewrites the lockfile, and fires the `PackChanged` autocmds (so `:TSUpdate` runs after a `nvim-treesitter` bump). Run from `~/.dot` (or any directory — `nvim` reads `XDG_CONFIG_HOME` for the config, not the cwd):

```sh
nvim --headless -c 'lua vim.pack.update(nil, { force = true })' -c 'quitall'
```

- First argument `nil` means "every plugin known to `vim.pack`". For a scoped update, pass an explicit list of plugin names (matching the lockfile keys, not the repo names):

  ```sh
  nvim --headless -c 'lua vim.pack.update({ "mini.nvim", "everforest" }, { force = true })' -c 'quitall'
  ```

- `{ force = true }` skips the interactive confirmation buffer (where the user would normally `:write` to confirm or `:quit` to cancel). With `force`, the update is applied immediately — this is the documented way to script `vim.pack.update` ("Useful when scripting", per the official guide).
- `quitall` exits once the update finishes. Treesitter parser rebuilds (`:TSUpdate`) run synchronously inside this invocation, so the command can take a while on big bumps — don't kill it.

Capture stderr — `vim.pack` reports clone errors, hook failures, and parser build errors there. If something fails partway through, the lockfile may be in a mixed state (some plugins bumped, others not); surface that to the user with the stderr rather than papering over it. `:checkhealth vim.pack` is the recovery tool if the user wants to investigate.

If headless invocation isn't viable (e.g. `nvim` isn't on PATH in the current shell, or treesitter parser builds need an interactive environment), fall back to instructing the user to open Neovim and run `:lua vim.pack.update()` interactively — then `:write` in the confirmation buffer to apply, or `:quit` to cancel.

### 5. Show the diff and offer to commit

```sh
git diff nvim/nvim-pack-lock.json
```

The diff should match the preview from step 3 — same `rev` changes, same set of plugins. If it doesn't, something's off (e.g. upstream advanced between the preview and the apply); call that out so the user knows what they're actually committing.

Summarize in one line: "bumped mini.nvim 29447d7 → f4e5d6c, nvim-treesitter 4916d65 → 2718e29 (parsers rebuilt)". The existing commit style in this repo is short and lowercase — messages like `update versions` or `bump nvim plugins` fit. Don't commit unless the user explicitly asks.

If a `:TSUpdate` ran, mention it in the summary — it produces no file changes itself but is the slowest part of the workflow and useful context.

## Edge cases

- **`compare` returns `ahead: 0, behind: N`.** Upstream rewrote history (force-push). The pinned commit no longer exists on the default branch but might still exist as a dangling commit. Surface this to the user and stop — silently moving to a new tip might skip a deliberate pin.
- **Plugin's `src` is not a GitHub URL.** Use `git ls-remote {src} HEAD` to get the latest SHA on the default branch. The apply step is unchanged — `vim.pack.update()` handles any git remote, not just GitHub.
- **A plugin's hook (e.g. `:TSUpdate`) fails during step 4.** The lockfile may have been rewritten for some plugins before the failing one. Surface the stderr and stop — don't retry blindly. `:checkhealth vim.pack` and `:checkhealth nvim-treesitter` are the right diagnostic entry points.
- **User asks to pin a specific non-HEAD commit, tag, or branch.** This isn't an `update` operation — it's a *config change*. The right move is to add a `version = "<sha|tag|branch>"` field to the matching `vim.pack.add({ ... })` spec in `~/.dot/nvim/init.lua` or `~/.dot/nvim/plugin/40_plugins.lua`, then run headless `vim.pack.update()` so `vim.pack` reconciles to that target. The lockfile updates as a side effect. Don't try to set this by hand-editing the lockfile.
- **Lockfile is out of sync with what's checked out on disk** (e.g. someone hand-edited it, or a previous run crashed mid-apply). The documented recovery is `vim.pack.update(nil, { target = 'lockfile' })`, which forces the on-disk clones to match what the lockfile records. Confirm with the user before running it — it can move clones *backwards* if the lockfile is older than disk.
