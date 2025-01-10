return {
  'folke/snacks.nvim',
  priority = 1000,
  lazy = false,
  dev = true,
  opts = {
    bigfile = { enabled = true },
    dashboard = { enabled = true },
    quickfile = { enabled = true },
    statuscolumn = { enabled = true },
    words = { enabled = true },
    terminal = {
      win = { style = 'terminal' },
    },
  },

  keys = {
    {
      '<leader>cR',
      function()
        Snacks.rename.rename_file()
      end,
      desc = '[R]ename File',
    },
    {
      '<leader>gf',
      function()
        Snacks.lazygit.log_file()
      end,
      desc = 'lazy[g]it current [f]ile history',
    },
    {
      '<leader>gg',
      function()
        Snacks.lazygit()
      end,
      desc = 'to[g]gle lazy[g]it',
    },
    {
      '<leader>gl',
      function()
        Snacks.lazygit.log()
      end,
      desc = 'lazy[g]it [l]og (cwd)',
    },
    { '<leader>t1', '1<cmd>lua Snacks.terminal.toggle()<cr>', desc = '[t]oggle terminal [1]' },
    { '<leader>t2', '2<cmd>lua Snacks.terminal.toggle()<cr>', desc = '[t]oggle terminal [2]' },
    { '<leader>t3', '3<cmd>lua Snacks.terminal.toggle()<cr>', desc = '[t]oggle terminal [3]' },
    { '<leader>t4', '4<cmd>lua Snacks.terminal.toggle()<cr>', desc = '[t]oggle terminal [4]' },
    {
      '<C-\\>',
      function()
        Snacks.terminal.toggle_all()
      end,
      desc = 'toggle all terminals',
      mode = { 'n', 't' },
    },
    {
      ']]',
      function()
        Snacks.words.jump(vim.v.count1)
      end,
      desc = 'next reference',
      mode = { 'n', 't' },
    },
    {
      '[[',
      function()
        Snacks.words.jump(-vim.v.count1)
      end,
      desc = 'prev reference',
      mode = { 'n', 't' },
    },
  },
  init = function()
    vim.api.nvim_create_autocmd('User', {
      pattern = 'VeryLazy',
      callback = function()
        Snacks.toggle.option('wrap', { name = '[t]oggle [w]rap' }):map '<leader>tw'
        Snacks.toggle.diagnostics():map '<leader>td'
        Snacks.toggle.inlay_hints():map '<leader>th'
      end,
    })
  end,
}
