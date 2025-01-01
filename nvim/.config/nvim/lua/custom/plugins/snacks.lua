return {
  'folke/snacks.nvim',
  priority = 1000,
  lazy = false,
  opts = {
    bigfile = { enabled = true }, -- deal with big files
    dashboard = { enabled = true }, -- start screen
    input = { enabled = true }, -- better vim.ui.input
    notifier = { enabled = true }, -- pretty vim.notify
    quickfile = { enabled = true }, -- render single files as quickly as possible
    scroll = { enabled = true }, -- smooth scrolling
    statuscolumn = { enabled = true }, -- pretty stauscolumn
  },

  -- stylua: ignore start
  keys = {
    { "<leader>z",  function() Snacks.zen() end, desc = "Toggle Zen Mode" },
    { "<leader>Z",  function() Snacks.zen.zoom() end, desc = "Toggle Zoom" },
    { "<leader>.",  function() Snacks.scratch() end, desc = "Toggle Scratch Buffer" },
    { "<leader>S",  function() Snacks.scratch.select() end, desc = "Select Scratch Buffer" },
    { "<leader>n",  function() Snacks.notifier.show_history() end, desc = "Notification History" },
    { "<leader>cR", function() Snacks.rename.rename_file() end, desc = "Rename File" },
    { "<leader>gB", function() Snacks.gitbrowse() end, desc = "Git Browse", mode = { "n", "v" } },
    { "<leader>gb", function() Snacks.git.blame_line() end, desc = "Git Blame Line" },
    { "<leader>gf", function() Snacks.lazygit.log_file() end, desc = "Lazygit Current File History" },
    { "<leader>gg", function() Snacks.lazygit() end, desc = "Lazygit" },
    { "<leader>gl", function() Snacks.lazygit.log() end, desc = "Lazygit Log (cwd)" },
    { "<c-/>",      function() Snacks.terminal() end, desc = "Toggle Terminal" },
  },
}
