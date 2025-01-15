return {
  'folke/snacks.nvim',
  priority = 1000,
  lazy = false,
  dev = true,
  opts = {
    bigfile = { enabled = true },
    dashboard = { enabled = true },
    picker = { enabled = true },
    quickfile = { enabled = true },
    statuscolumn = { enabled = true },
    terminal = {
      win = { style = 'terminal' },
    },
    words = { enabled = true },
  },
  -- stylua: ignore
  keys = {
    -- lazygit
    { '<leader>gf', function() Snacks.lazygit.log_file() end, desc = 'Current File History' },
    { '<leader>gg', function() Snacks.lazygit() end, desc = 'Toggle lazygit' },
    { '<leader>gl', function() Snacks.lazygit.log() end, desc = 'Log' },

    -- picker
    { "<leader>,", function() Snacks.picker.buffers() end, desc = "Buffers" },
    { "<leader>/", function() Snacks.picker.grep() end, desc = "Grep" },
    { "<leader>:", function() Snacks.picker.command_history() end, desc = "Command History" },
    { "<leader><leader>", function() Snacks.picker.files() end, desc = "Find Files" },

    -- picker: find
    { "<leader>fb", function() Snacks.picker.buffers() end, desc = "Buffers" },
    { "<leader>fc", function() Snacks.picker.files({ cwd = vim.fn.stdpath("config") }) end, desc = "Find Config File" },
    { "<leader>fg", function() Snacks.picker.git_files() end, desc = "Find Git Files" },
    { "<leader>fr", function() Snacks.picker.recent() end, desc = "Recent" },

    -- picker: grep
    { "<leader>sb", function() Snacks.picker.lines() end, desc = "Buffer Lines" },
    { "<leader>sB", function() Snacks.picker.grep_buffers() end, desc = "Grep Open Buffers" },
    { "<leader>sg", function() Snacks.picker.grep() end, desc = "Grep" },
    { "<leader>sw", function() Snacks.picker.grep_word() end, desc = "Visual Selection or Word", mode = { "n", "x" } },

    -- picker: search
    { "<leader>sd", function() Snacks.picker.diagnostics() end, desc = "Diagnostics" },
    { "<leader>sh", function() Snacks.picker.help() end, desc = "Help Pages" },
    { "<leader>sk", function() Snacks.picker.keymaps() end, desc = "Keymaps" },
    { "<leader>sR", function() Snacks.picker.resume() end, desc = "Resume" },
    { "<leader>sq", function() Snacks.picker.qflist() end, desc = "Quickfix List" },
    { "<leader>sp", function() Snacks.picker.projects() end, desc = "Projects" },

    -- terminal
    { '<leader>t1', '1<cmd>lua Snacks.terminal.toggle()<cr>', desc = 'Toggle Terminal 1' },
    { '<leader>t2', '2<cmd>lua Snacks.terminal.toggle()<cr>', desc = 'Toggle Terminal 2' },
    { '<leader>t3', '3<cmd>lua Snacks.terminal.toggle()<cr>', desc = 'Toggle Terminal 3' },
    { '<leader>t4', '4<cmd>lua Snacks.terminal.toggle()<cr>', desc = 'Toggle Terminal 4' },
    { '<C-\\>', function() Snacks.terminal.toggle_all() end, desc = 'Toggle All Terminals', mode = { 'n', 't' } },
  },
  init = function()
    vim.api.nvim_create_autocmd('User', {
      pattern = 'VeryLazy',
      callback = function()
        -- toggle
        Snacks.toggle.option('wrap', { name = 'Line Wrap' }):map '<leader>tw'
        Snacks.toggle.diagnostics():map '<leader>td'
        Snacks.toggle.inlay_hints():map '<leader>th'
      end,
    })
  end,
}
