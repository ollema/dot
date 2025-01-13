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
      callback = function(event)
        local map = function(keys, func, desc, mode)
          mode = mode or 'n'
          vim.keymap.set(mode, keys, func, { buffer = event.buf, desc = 'lsp: ' .. desc })
        end

        -- jump to the definition of the word under your cursor.
        --  this is where a variable was first declared, or where a function is defined, etc.
        map('gd', require('telescope.builtin').lsp_definitions, '[g]oto [d]efinition')

        -- find references for the word under your cursor.
        map('gr', require('telescope.builtin').lsp_references, '[g]oto [r]eferences')

        -- jump to the implementation of the word under your cursor.
        --  useful when your language has ways of declaring types without an actual implementation.
        map('gI', require('telescope.builtin').lsp_implementations, '[g]oto [I]mplementation')

        -- jump to the type of the word under your cursor.
        --  useful when you're not sure what type a variable is and you want to see
        --  the definition of its *type*, not where it was *defined*.
        map('<leader>D', require('telescope.builtin').lsp_type_definitions, 'type [D]efinition')

        -- fuzzy find all the symbols in your current document.
        --  symbols are things like variables, functions, types, etc.
        map('<leader>ds', require('telescope.builtin').lsp_document_symbols, '[d]ocument [s]ymbols')

        -- fuzzy find all the symbols in your current workspace.
        --  similar to document symbols, except searches over your entire project.
        map('<leader>ws', require('telescope.builtin').lsp_dynamic_workspace_symbols, '[w]orkspace [s]ymbols')

        -- rename the variable under your cursor.
        --  most language servers support renaming across files, etc.
        map('<leader>rn', vim.lsp.buf.rename, '[r]e[n]ame')

        -- execute a code action, usually your cursor needs to be on top of an error
        -- or a suggestion from your LSP for this to activate.
        map('<leader>ca', vim.lsp.buf.code_action, '[c]ode [a]ction', { 'n', 'x' })

        -- this is not Goto Definition, this is Goto Declaration.
        --  For example, in C this would take you to the header.
        map('gD', vim.lsp.buf.declaration, '[g]oto [D]eclaration')
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
