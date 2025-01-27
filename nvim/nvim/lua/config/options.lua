-- disable snacks animations
vim.g.snacks_animate = false

-- use fish as the shell for the integrated terminal
vim.opt.shell = "fish"

-- use inline suggestions instead of completion engine
vim.g.ai_cmp = false

-- use basedpyright instead of pyright
vim.g.lazyvim_python_lsp = "basedpyright"
-- use ruff instead of ruff_lsp
vim.g.lazyvim_python_ruff = "ruff"
