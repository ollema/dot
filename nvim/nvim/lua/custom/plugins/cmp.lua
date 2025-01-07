return {
  'saghen/blink.cmp',
  dependencies = 'rafamadriz/friendly-snippets',
  version = '*',
  event = 'InsertEnter',
  opts = {
    keymap = { preset = 'default' },
    appearance = {
      nerd_font_variant = 'mono',
    },
    completion = {
      menu = {
        draw = {
          treesitter = { 'lsp' },
        },
      },
      documentation = {
        auto_show = true,
        auto_show_delay_ms = 200,
      },
      ghost_text = {
        enabled = true,
      },
    },
    sources = {
      default = { 'lsp', 'path', 'snippets', 'buffer' },
    },
  },
  opts_extend = { 'sources.default' },
}
