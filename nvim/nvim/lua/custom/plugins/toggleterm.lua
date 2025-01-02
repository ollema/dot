return {
  'akinsho/toggleterm.nvim',
  event = 'VeryLazy',
  opts = {
    open_mapping = [[<c-\>]],
    direction = 'horizontal',
  },
  config = function(_, opts)
    require('toggleterm').setup(opts)

    local Terminal = require('toggleterm.terminal').Terminal

    local term1 = Terminal:new {
      count = 1,
      hidden = true,
      direction = 'horizontal',
    }

    local term2 = Terminal:new {
      count = 2,
      hidden = true,
      direction = 'horizontal',
    }

    local term3 = Terminal:new {
      count = 3,
      hidden = true,
      direction = 'horizontal',
    }

    local term4 = Terminal:new {
      count = 4,
      hidden = true,
      direction = 'horizontal',
    }

    vim.keymap.set('n', '<leader>t1', function()
      term1:toggle()
    end, {
      desc = 'toggle terminal 1',
    })

    vim.keymap.set('n', '<leader>t2', function()
      term2:toggle()
    end, {
      desc = 'toggle terminal 2',
    })

    vim.keymap.set('n', '<leader>t3', function()
      term3:toggle()
    end, {
      desc = 'toggle terminal 3',
    })

    vim.keymap.set('n', '<leader>t4', function()
      term4:toggle()
    end, {
      desc = 'toggle terminal 4',
    })
  end,
}
