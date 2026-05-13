---
name: update-nvim-from-minimax
description: Refresh ~/.dot/nvim/ structural files (init.lua, plugin/*, after/*, snippets/) from a newer commit of the upstream MiniMax (nvim-mini/MiniMax) config, then reapply the intentional deviations documented in ~/.dot/nvim/CLAUDE.md. Use this skill whenever the user wants to pull a newer MiniMax baseline into their nvim config, sync their nvim setup with upstream MiniMax, check whether MiniMax has new commits since their pinned baseline, or refresh non-plugin parts of nvim from upstream — phrases like "update my nvim config from upstream", "is MiniMax ahead", "sync nvim with MiniMax", "pull latest MiniMax", "bump the MiniMax baseline", "what's new in MiniMax". This is structural — for plugin commit bumps in nvim-pack-lock.json, use the sibling skill `update-nvim-plugins` instead.
---

# Updating ~/.dot/nvim/ from a newer MiniMax baseline

`~/.dot/nvim/` was bootstrapped from [`nvim-mini/MiniMax`](https://github.com/nvim-mini/MiniMax) and is kept structurally close to upstream. This skill is for advancing the *baseline* — fetching newer versions of `init.lua`, `plugin/*.lua`, `after/**/*.lua`, and `snippets/*.json` from MiniMax — then reapplying the small set of intentional deviations the user has accumulated.

For commit bumps to entries in `nvim-pack-lock.json` (mini.nvim, conform.nvim, treesitter, etc.), use `update-nvim-plugins` — that's a different workflow and the lockfile is owned by `vim.pack`, not by MiniMax.

## What the repo already knows

Read `~/.dot/nvim/CLAUDE.md` first. It's the source of truth for the baseline and the deviations and the whole skill depends on it being accurate.

- The CLAUDE.md "Baseline" section records the pinned MiniMax commit (e.g. `f76d787`) and which config variant is in use (e.g. `configs/nvim-0.13/`). MiniMax ships parallel variants for nvim 0.10–0.13; the user's pin is the one to track.
- The CLAUDE.md "Intentional deviations" section lists every functional change vs that baseline, with the exact code to reapply. Comments and structure are deliberately kept identical to upstream so the diff stays small. If the list has grown stale (deviations made in git that aren't in CLAUDE.md), surface that *before* overlaying — the overlay will silently wipe them otherwise.
- `~/.dot/nvim/nvim-pack-lock.json` is *also* owned by upstream MiniMax in the source tree, but in this repo it's managed by `vim.pack` and routinely diverges. Never overlay the lockfile from MiniMax — that's `update-nvim-plugins`' job.
- Upstream lives at `github.com/nvim-mini/MiniMax`. `gh api` is the right tool for both commit lookups and content fetches. The default branch is `main`.

## Workflow

### 1. Read the baseline from CLAUDE.md

Open `~/.dot/nvim/CLAUDE.md` and pull out:

- The pinned baseline commit SHA (under "Baseline").
- The config variant path (e.g. `configs/nvim-0.13/`).
- The list of deviations, each with file path, change description, and exact code.

If any of these are missing or ambiguous, stop and ask the user to clarify — the skill can't safely overlay without them.

### 2. Look up the latest upstream commit

```sh
gh api repos/nvim-mini/MiniMax/commits/HEAD --jq '.sha'
```

`HEAD` resolves to the latest commit on the default branch. Capture the full SHA.

If `gh` returns an auth error, run `gh auth status`, surface the problem, and stop.

### 3. Show what changed

Compare baseline to latest, scoped to the config variant in use so the user isn't reading about CI changes or README edits:

```sh
gh api "repos/nvim-mini/MiniMax/compare/<baseline>...HEAD?per_page=100" \
  --jq '.commits[] | "\(.sha[0:7]) \(.commit.author.date[0:10]) \(.commit.message | split("\n")[0])"'
```

Then filter for commits that touch the user's variant:

```sh
gh api "repos/nvim-mini/MiniMax/compare/<baseline>...HEAD?per_page=100" \
  --jq '.files[] | select(.filename | startswith("configs/nvim-0.13/")) | .filename' \
  | sort -u
```

Present a short summary to the user. The SHAs and counts below are illustrative
— substitute the real output from the calls above:

```
baseline:  <baseline-sha> (<baseline-date>)
upstream:  <new-sha> (<new-date>)
ahead:     N commits, M touch configs/nvim-0.13/

files changed in your variant since baseline:
  configs/nvim-0.13/nvim-pack-lock.json       ← skip (managed by update-nvim-plugins)
  configs/nvim-0.13/plugin/40_plugins.lua
  ...

notable commits:
  <sha> <one-line message>
  ...
```

Three possible paths from here:

- **Check-only prompt** ("is MiniMax ahead?", "anything new upstream?"). Report and stop. Skip the rest.
- **Nothing has changed in the variant.** Report "baseline is current" and stop.
- **There are upstream changes and the user wants to apply.** Continue.

### 4. Sanity-check that the working tree matches the recorded baseline

Before overlaying, fetch the *baseline* MiniMax files into a temp dir and diff against the current `~/.dot/nvim/`. The diff should reduce to exactly the deviations listed in CLAUDE.md (plus `nvim-pack-lock.json` rev drift, which is expected).

```sh
TMPDIR_BASELINE=$(mktemp -d)
while read -r path; do
  dest="$TMPDIR_BASELINE/${path#configs/nvim-0.13/}"
  mkdir -p "$(dirname "$dest")"
  gh api "repos/nvim-mini/MiniMax/contents/$path?ref=<baseline>" --jq '.content' | base64 -d > "$dest"
done < <(gh api "repos/nvim-mini/MiniMax/git/trees/<baseline>?recursive=1" \
  --jq '.tree[] | select(.type=="blob" and (.path | startswith("configs/nvim-0.13/"))) | .path')
diff -r "$TMPDIR_BASELINE" ~/.dot/nvim --brief
```

Use process substitution (`done < <(…)`) rather than piping into the loop —
keeps the loop body in the parent shell scope, which matters in sandboxed Bash
environments that don't propagate `PATH` to subshell-pipe stages. If your
environment is even more restrictive (no process substitution, no
`PATH`-inheritance), write the fetch to a small script with an explicit
`export PATH=/opt/homebrew/bin:/usr/bin:/bin` at the top and run that.

If the diff includes anything *not* in CLAUDE.md's deviations list, stop and tell the user — there's an undocumented local change that the overlay will silently overwrite. Two recoveries:

- Add the change to CLAUDE.md first (most common: it's a deviation that just wasn't recorded), or
- Discard the local change (e.g. it's experimental).

This check is the safety net. Skipping it is how the user loses uncommitted work.

### 5. Fetch the upstream files at the new tip

Same shape as step 4 but pointed at the latest SHA. Drop into a second temp dir. **Exclude `nvim-pack-lock.json`** — that file is owned by `vim.pack` in this repo.

```sh
TMPDIR_NEW=$(mktemp -d)
while read -r path; do
  dest="$TMPDIR_NEW/${path#configs/nvim-0.13/}"
  mkdir -p "$(dirname "$dest")"
  gh api "repos/nvim-mini/MiniMax/contents/$path?ref=<new-sha>" --jq '.content' | base64 -d > "$dest"
done < <(gh api "repos/nvim-mini/MiniMax/git/trees/<new-sha>?recursive=1" \
  --jq '.tree[] | select(.type=="blob" and (.path | startswith("configs/nvim-0.13/")) and (.path | endswith("nvim-pack-lock.json") | not)) | .path')
```

### 6. Overlay onto nvim/

Copy `$TMPDIR_NEW/*` over `~/.dot/nvim/`, preserving structure. `cp -R "$TMPDIR_NEW/." ~/.dot/nvim/` is the easiest way (note the trailing `/.` to copy contents, not the dir itself).

Don't delete files that exist locally but not in upstream — the user may have added local files (e.g. extra snippet collections, after/lsp/ entries). If upstream *removed* a file, surface that to the user as a question rather than auto-deleting.

### 7. Reapply the deviations

For each entry in CLAUDE.md's "Intentional deviations" section, apply the recorded change to the overlaid file. The Edit tool is fine for additive changes (appending the colorscheme block, adding a lockfile entry). For wrap-style changes (e.g. wrapping a block in `if vim.env.NVIM_NO_EXTERNAL_TREESITTER ~= '1' then ... end`), the trick is:

- Find the anchor (start/end of the block being wrapped) in the *new* upstream file.
- Apply the wrap and re-indent the wrapped lines one level.
- If the block has shifted significantly (upstream rewrote it), the wrap may not apply cleanly — see edge cases below.

Apply each deviation, then move to verification.

### 8. Verify the result

Diff the overlaid + reapplied `nvim/` against the *new* upstream tree:

```sh
diff -r "$TMPDIR_NEW" ~/.dot/nvim --brief
```

The output should match exactly what CLAUDE.md predicts. If something extra differs (e.g. a file the deviations list doesn't mention), the overlay missed something or the reapply went wrong — investigate before continuing.

Also run a quick sanity launch:

```sh
NVIM_NO_EXTERNAL_TREESITTER=1 nvim --headless -c 'quitall' 2>&1
```

This catches syntax errors in the overlaid Lua files without triggering tree-sitter parser builds. Any stderr means the config is broken — surface it and stop.

### 9. Update the baseline pointer in CLAUDE.md

Once the overlay is verified, advance the `Current baseline:` line in `~/.dot/nvim/CLAUDE.md` to the new SHA and date. Leave the `Adopted:` line alone — that's a historical record of the initial bootstrap commit, not the refresh pointer. If MiniMax now ships a config variant the user wants to switch to (e.g. they're on `nvim-0.13` and `nvim-0.14` just appeared), that's a separate decision — surface it, don't switch unilaterally.

### 10. Show the diff and offer to commit

```sh
git diff -- nvim/
```

Summarize: "synced nvim from MiniMax f76d787 → 8135af2 (5 commits)". Existing commit style is short and lowercase. Don't commit unless asked.

## Edge cases

- **A deviation no longer applies cleanly.** Upstream rewrote the surrounding code — e.g. they refactored the tree-sitter block such that the `if vim.env.NVIM_NO_EXTERNAL_TREESITTER` wrap no longer has the right anchor. Surface this to the user with the upstream diff *and* the deviation, and let them decide: re-author the deviation against the new shape, drop the deviation if upstream now does the same thing natively, or skip the bump entirely. Don't try to be clever about merging — wrong choices here are silent.
- **CLAUDE.md is out of date.** The step-4 sanity check will catch this. The right fix is to update CLAUDE.md *first* (a separate commit), then run the skill again. Don't paper over the discrepancy by quietly carrying the undocumented change through the overlay.
- **MiniMax added a new config variant** (e.g. `configs/nvim-0.14/`). The user is still pinned to the old one. Mention the new variant but don't switch — moving variants is a larger decision (different nvim version requirements, possibly different file layouts).
- **MiniMax removed a file** that the user has locally. Could be the user added it themselves (fine, keep it) or upstream genuinely retired a file the user is using (their config will still work, but the file is now orphaned). Ask before deleting.
- **The user's variant has been deprecated upstream** (e.g. `configs/nvim-0.12/` is no longer maintained). The `git/trees` lookup will still return the old files at the baseline ref, but `commits/HEAD` won't show changes to it. Surface this and recommend planning a variant migration.
- **GitHub API rate limit hit.** The fetch step pulls one file per `contents/` call, which can add up. If rate-limited, fall back to cloning the MiniMax repo at the desired ref into a temp dir (`git clone --depth 1 --branch ...` doesn't help here since we need a specific SHA — use `git clone` then `git checkout <sha>` instead) and copy from there.
- **Working tree has uncommitted changes in nvim/ when the skill starts.** Don't overlay on top of dirty state — the user could lose work. Run `git status -- nvim/` first; if there are unstaged or staged changes, surface them and ask the user to commit or stash before continuing.
