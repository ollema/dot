-- configure and install plugins
--
--  to check the current status of your plugins, run
--    :Lazy
--
--  you can press `?` in this menu for help. Use `:q` to close the window
--
--  to update plugins you can run
--    :Lazy update
--

require('lazy').setup({
  'tpope/vim-sleuth', -- detect tabstop and shiftwidth automatically

  require 'kickstart/plugins/gitsigns',

  require 'kickstart/plugins/which-key',

  require 'kickstart/plugins/telescope',

  require 'kickstart/plugins/lspconfig',

  require 'kickstart/plugins/conform',

  require 'kickstart/plugins/cmp',

  require 'kickstart/plugins/tokyonight',

  require 'kickstart/plugins/todo-comments',

  require 'kickstart/plugins/mini',

  require 'kickstart/plugins/treesitter',

  require 'kickstart.plugins.debug',

  require 'kickstart.plugins.lint',

  require 'kickstart.plugins.autopairs',

  require 'kickstart.plugins.neo-tree',

  { import = 'custom.plugins' },
}, {
  ui = { icons = {} },
})

-- vim: ts=2 sts=2 sw=2 et
