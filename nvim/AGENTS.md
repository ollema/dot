# nvim/AGENTS.md

This config was bootstrapped from [MiniMax](https://github.com/nvim-mini/MiniMax)
and is kept structurally identical to upstream. Comments, ordering, and the
MiniMax-managed blocks are deliberately left untouched so refreshes are cheap.

This file lists every intentional deviation so they can be reapplied after
syncing from upstream.

## Baseline

- Upstream: `nvim-mini/MiniMax`, `configs/nvim-0.13/`
- Adopted: 2026-04-17 in commit `7b7cb0f use minimax config` at MiniMax `f76d787`
- Current baseline: `8135af2` (2026-05-09) — bump this when refreshing from
  upstream

To refresh: copy `configs/nvim-0.13/` from a newer MiniMax commit on top of
`nvim/`, then reapply the two functional deviations below. Plugin revs in
`nvim-pack-lock.json` are maintained separately via the `update-nvim-plugins`
skill and are not deviations.

## Intentional deviations

Only two functional changes; everything else (comments, banners, structure)
matches upstream.

### `plugin/40_plugins.lua`

1. **Optional tree-sitter (commit `f7871eb`).** Wrap the entire
   `now_if_args(function() … end)` tree-sitter block in:

   ```lua
   if vim.env.NVIM_NO_EXTERNAL_TREESITTER ~= '1' then
     -- … original now_if_args(...) block, indented one more level …
   end
   ```

   Lets sandboxes/CI skip the external tree-sitter parser install by exporting
   `NVIM_NO_EXTERNAL_TREESITTER=1`. Required for environments without a C
   compiler.

2. **Everforest colorscheme (commits `8e19b8c`, `7053422`).** Append a new
   `-- Colorscheme ===` section at the end of the file (do not touch the
   `-- Honorable mentions` block above it):

   ```lua
   -- Colorscheme ================================================================

   Config.now(function()
     add({ { src = 'https://github.com/sainnhe/everforest', name = 'everforest' } })
     vim.o.background = 'dark'
     vim.g.everforest_background = 'hard'
     vim.g.everforest_better_performance = 1
     vim.cmd('color everforest')
   end)
   ```

   The default MiniMax theme (`miniwinter` via `mini.hues`) is replaced at
   runtime by this final `Config.now` call.

### `nvim-pack-lock.json`

The lockfile is **not overlaid** during a MiniMax refresh — `vim.pack` owns it,
and `update-nvim-plugins` is the right tool for rev bumps. The only deviation
worth noting is that this repo carries an extra `everforest` entry (paired with
the colorscheme deviation above) that has no counterpart in upstream MiniMax's
lockfile:

```json
"everforest": {
  "rev": "<latest>",
  "src": "https://github.com/sainnhe/everforest"
}
```

A refresh should leave this entry alone — verify it's still present after the
overlay (it will be, since the overlay skips this file), don't try to re-add
it.

## Verifying after a refresh

1. `diff -r <fresh MiniMax configs/nvim-0.13/> nvim/` — expect only the
   tree-sitter `if` wrapper, the appended colorscheme block, and the
   `everforest` lockfile entry.
2. Launch `nvim` and confirm the everforest colorscheme loads.
3. With `NVIM_NO_EXTERNAL_TREESITTER=1 nvim`, confirm startup does not try to
   install tree-sitter parsers.
