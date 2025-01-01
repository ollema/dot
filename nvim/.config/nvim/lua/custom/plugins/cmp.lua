return {
  {
    'hrsh7th/nvim-cmp',
    event = 'InsertEnter',
    dependencies = {
      'onsails/lspkind.nvim',
      'hrsh7th/cmp-nvim-lsp',
      'hrsh7th/cmp-path',
      'hrsh7th/cmp-buffer',
      { 'L3MON4D3/LuaSnip', build = 'make install_jsregexp' },
      'saadparwaiz1/cmp_luasnip',
      'roobert/tailwindcss-colorizer-cmp.nvim',
      'zbirenbaum/copilot.lua',
      'litoj/cmp-copilot',
    },
    config = function()
      local cmp = require 'cmp'
      local luasnip = require 'luasnip'
      local lspkind = require 'lspkind'

      require('copilot').setup {
        suggestion = { enabled = false },
        panel = { enabled = false },
      }
      require('cmp_copilot').setup()

      lspkind.init {
        symbol_map = {
          Copilot = '',
        },
      }
      vim.api.nvim_set_hl(0, 'CmpItemKindCopilot', { fg = '#6CC644' })

      luasnip.config.setup {
        history = true,
        updateevents = 'TextChanged,TextChangedI',
        override_builtin = true,
      }

      require('tailwindcss-colorizer-cmp').setup {
        color_square_width = 2,
      }

      cmp.setup {
        snippet = {
          expand = function(args)
            luasnip.lsp_expand(args.body)
          end,
        },

        completion = { completeopt = 'menu,menuone,noinsert' },

        mapping = cmp.mapping.preset.insert {
          ['<C-n>'] = cmp.mapping.select_next_item { behavior = cmp.SelectBehavior.Insert },
          ['<C-p>'] = cmp.mapping.select_prev_item { behavior = cmp.SelectBehavior.Insert },
          ['<C-b>'] = cmp.mapping.scroll_docs(-4),
          ['<C-f>'] = cmp.mapping.scroll_docs(4),
          ['<C-y>'] = cmp.mapping(
            cmp.mapping.confirm {
              behavior = cmp.ConfirmBehavior.Insert,
              select = true,
            },
            { 'i', 'c' }
          ),
          ['<C-Space>'] = cmp.mapping.complete {},
          ['<C-l>'] = cmp.mapping(function()
            if luasnip.expand_or_locally_jumpable() then
              luasnip.expand_or_jump()
            end
          end, { 'i', 's' }),
          ['<C-h>'] = cmp.mapping(function()
            if luasnip.locally_jumpable(-1) then
              luasnip.jump(-1)
            end
          end, { 'i', 's' }),
        },

        sources = {
          {
            name = 'lazydev',
            group_index = 0,
          },
          { name = 'copilot' },
          { name = 'nvim_lsp' },
          { name = 'luasnip' },
          { name = 'buffer' },
          { name = 'path' },
        },

        formatting = {
          fields = { 'abbr', 'kind', 'menu' },
          expandable_indicator = true,
          format = function(entry, vim_item)
            vim_item = lspkind.cmp_format {
              mode = 'symbol_text',
              menu = {
                buffer = '[buf]',
                nvim_lsp = '[LSP]',
                path = '[path]',
                luasnip = '[snip]',
                copilot = '[Copilot]',
              },
            }(entry, vim_item)
            return require('tailwindcss-colorizer-cmp').formatter(entry, vim_item)
          end,
        },

        sorting = {
          priority_weight = 2,
          comparators = {
            require('cmp_copilot.comparators').prioritize,
            cmp.config.compare.offset,
            cmp.config.compare.exact,
            cmp.config.compare.score,
            cmp.config.compare.recently_used,
            cmp.config.compare.locality,
            cmp.config.compare.kind,
            cmp.config.compare.sort_text,
            cmp.config.compare.length,
            cmp.config.compare.order,
          },
        },
      }
    end,
  },
}
-- vim: ts=2 sts=2 sw=2 et
