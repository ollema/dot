return {
  'neovim/nvim-lspconfig',
  dependencies = {
    'saghen/blink.cmp',
    { 'williamboman/mason.nvim', config = true },
    'williamboman/mason-lspconfig.nvim',
    'WhoIsSethDaniel/mason-tool-installer.nvim',
    { 'j-hui/fidget.nvim', config = true },
  },
  config = function()
    vim.api.nvim_create_autocmd('LspAttach', {
      group = vim.api.nvim_create_augroup('kickstart-lsp-attach', { clear = true }),
      -- stylua: ignore
      callback = function(event)
        local map = function(keys, func, desc, mode)
          mode = mode or 'n'
          vim.keymap.set(mode, keys, func, { buffer = event.buf, desc = 'LSP: ' .. desc })
        end

        map('<leader>cl', '<cmd>LspInfo<cr>', 'Info')

        map('gd', function() Snacks.picker.lsp_definitions() end, 'Goto Definition')
        map('gr', function() Snacks.picker.lsp_references() end, 'Goto References')
        map('gI', function() Snacks.picker.lsp_implementations() end, 'Goto Implementation')
        map('gy', function() Snacks.picker.lsp_type_definitions() end, 'Goto T[y]pe Definition')
        map('gD', vim.lsp.buf.declaration, 'Goto Declaration')

        map('K', function() return vim.lsp.buf.hover() end, 'Hover')
        map('gK', function() return vim.lsp.buf.signature_help() end, 'Signature Help')

        map('<leader>ca', vim.lsp.buf.code_action, 'Code Action', { 'n', 'x' })
        map('<leader>cA', function() vim.lsp.buf.code_action({ apply = true, context = { only = { "source" }, diagnostics = {}, }, }) end, 'Source Action')
        map('<leader>cr', vim.lsp.buf.rename, 'Rename variable')
        map('<leader>cR', function() Snacks.rename.rename_file() end, 'Rename file')

        map(']]', function() Snacks.words.jump(vim.v.count1) end, 'Next Reference', { 'n', 't' })
        map('[[', function() Snacks.words.jump(-vim.v.count1) end, 'Prev Reference', { 'n', 't' })
      end,
    })

    local servers = {
      basedpyright = {},
      jsonls = {
        filetypes = { 'json', 'jsonc' },
        settings = {
          json = {
            validate = { enable = true },
            schemas = {
              {
                fileMatch = { 'package.json' },
                url = 'https://json.schemastore.org/package.json',
              },
              {
                fileMatch = { 'tsconfig*.json' },
                url = 'https://json.schemastore.org/tsconfig.json',
              },
              {
                fileMatch = {
                  '.prettierrc',
                  '.prettierrc.json',
                  'prettier.config.json',
                },
                url = 'https://json.schemastore.org/prettierrc.json',
              },
              {
                fileMatch = { '.eslintrc', '.eslintrc.json' },
                url = 'https://json.schemastore.org/eslintrc.json',
              },
              {
                fileMatch = { 'members.json' },
                url = '/Users/s0001325/repos/ufpersonslist/members.schema.json',
              },
            },
          },
        },
      },
      lua_ls = {},
      ruff = {
        init_options = {
          settings = {
            configurationPreference = 'editorOnly',
            lineLength = 100,
            organizeImports = false,
            lint = {
              enable = false,
            },
          },
        },
      },
      stylua = {},
      svelte = {},
      ts_ls = {},
    }

    require('mason-tool-installer').setup {
      ensure_installed = vim.tbl_keys(servers),
    }

    ---@diagnostic disable-next-line: missing-fields
    require('mason-lspconfig').setup {
      handlers = {
        function(server)
          local config = servers[server] or {}
          config.capabilities = require('blink.cmp').get_lsp_capabilities(config.capabilities)
          require('lspconfig')[server].setup(config)
        end,
      },
    }
  end,
}
