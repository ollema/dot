return {
  'folke/snacks.nvim',
  priority = 1000,
  lazy = false,
  dev = true,
  opts = {
    dashboard = { enabled = true },
    terminal = {
      win = { style = 'terminal' },
    },
  },

  -- stylua: ignore start
  keys = {
    { "<leader>cR", function() Snacks.rename.rename_file() end, desc = "Rename File" },
    { "<leader>gg", function() Snacks.lazygit() end, desc = "Lazygit" },
    { "<leader>t1", "1<cmd>lua Snacks.terminal.toggle()<cr>", desc = "Toggle Terminal 1" },
    { "<leader>t2", "2<cmd>lua Snacks.terminal.toggle()<cr>", desc = "Toggle Terminal 2" },
    { "<leader>t3", "3<cmd>lua Snacks.terminal.toggle()<cr>", desc = "Toggle Terminal 3" },
    { "<leader>t4", "4<cmd>lua Snacks.terminal.toggle()<cr>", desc = "Toggle Terminal 4" },
    { "<C-\\>", function() Snacks.terminal.toggle_all() end, desc = "Toggle All Terminals", mode = {"n", "t"} },
  },
}
