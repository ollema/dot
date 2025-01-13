return {
  {
    'folke/which-key.nvim',
    event = 'VimEnter',
    opts = {
      delay = 0,
      icons = {
        mappings = false,
        keys = {},
      },
      spec = {
        { '<leader>c', group = '[c]ode', mode = { 'n', 'x' } },
        { '<leader>d', group = '[d]ocument' },
        { '<leader>g', group = '[g]it' },
        { '<leader>h', group = '[h]arpoon' },
        { '<leader>r', group = '[r]ename' },
        { '<leader>s', group = '[s]earch' },
        { '<leader>t', group = '[t]oggle' },
        { '<leader>w', group = '[w]orkspace' },
      },
    },
  },
}
