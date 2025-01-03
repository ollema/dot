-- general
vim.opt.undofile = true -- save undo history
vim.opt.backup = false -- don't store backup while overwriting the file
vim.opt.writebackup = false -- don't store backup while overwriting the file
vim.opt.mouse = 'a' -- enable mouse support
vim.cmd 'filetype plugin indent on' -- enable all filetype plugins
vim.opt.shell = '/opt/homebrew/bin/fish'
vim.opt.updatetime = 250 -- reduce time for displaying signs
vim.opt.timeoutlen = 300 -- time to wait for a mapped sequence to complete
vim.opt.shortmess:append 'WcC' -- Reduce command line messages
vim.opt.splitkeep = 'screen' -- Reduce scroll during window split

-- appearance
vim.breakindent = true -- indent wrapped lines to match the start
vim.opt.cursorline = true -- highlight the current line
vim.opt.linebreak = true -- wrap long lines at 'breakat' characters (if 'wrap' is set)
vim.opt.number = true -- show line numbers
vim.opt.relativenumber = true -- show relative line numbers
vim.opt.splitbelow = true -- open new splits below the current one
vim.opt.splitright = true -- open new splits to the right of the current one
vim.opt.ruler = false -- don't show the cursor position in the command line
vim.opt.showmode = false -- don't show the mode in the command line
vim.opt.wrap = false -- don't wrap lines at word boundaries
vim.opt.signcolumn = 'yes' -- always show the sign column (otherwise it will shift the text)
vim.opt.fillchars = 'eob: ' -- fill the end of the buffer with spaces
vim.opt.scrolloff = 10 -- keep 10 lines above/below cursor
vim.opt.list = true -- show some helper symbols
vim.opt.listchars = { tab = '» ', trail = '·', nbsp = '␣' } -- customize helper symbols

-- editing
vim.opt.ignorecase = true -- ignore case when searching
vim.opt.incsearch = true -- show search matches as you type
vim.opt.infercase = true -- infer letter cases for a richer built-in keyword completion
vim.opt.smartcase = true -- override 'ignorecase' if the search pattern contains uppercase characters
vim.opt.smartindent = true -- auto-indent new lines
vim.opt.tabstop = 2 -- number of spaces that a <Tab> in the file counts for
vim.opt.completeopt = 'menuone,noinsert,noselect' -- customize completions
vim.opt.virtualedit = 'block' -- allow the cursor to move to any position in visual block mode
vim.opt.formatoptions = 'qjl1' -- don't autoformat comments
vim.opt.inccommand = 'split' -- preview substitutions as you type
