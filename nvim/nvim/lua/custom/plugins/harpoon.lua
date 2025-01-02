return {
  'theprimeagen/harpoon',
  branch = 'harpoon2',
  dependencies = { 'nvim-lua/plenary.nvim' },

  config = function()
    local harpoon = require 'harpoon'
    harpoon:setup {
      settings = {
        save_on_toggle = true,
      },
    }

    vim.keymap.set('n', '<leader>ha', function()
      harpoon:list():add()
    end, { desc = '[H]arpoon: [A]dd mark' })

    vim.keymap.set('n', '<leader>hh', function()
      harpoon.ui:toggle_quick_menu(harpoon:list())
    end, { desc = '[H]arpoon: open [H]arpoon quick menu' })

    vim.keymap.set('n', '1', function()
      harpoon:list():select(1)
    end, { desc = 'Select Harpoon 1' })

    vim.keymap.set('n', '2', function()
      harpoon:list():select(2)
    end, { desc = 'Select Harpoon 2' })

    vim.keymap.set('n', '3', function()
      harpoon:list():select(3)
    end, { desc = 'Select Harpoon 3' })

    vim.keymap.set('n', '4', function()
      harpoon:list():select(4)
    end, { desc = 'Select Harpoon 4' })
  end,
}
