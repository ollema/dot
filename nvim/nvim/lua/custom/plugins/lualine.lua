local function file_from_path(path)
  return path:match '([^/]+)$'
end

local function get_harpoon_indicator(label)
  return function(harpoon_entry)
    return label .. ' ' .. file_from_path(harpoon_entry.value)
  end
end

return {
  {
    'nvim-lualine/lualine.nvim',
    opts = {
      options = {
        globalstatus = true,
        icons_enabled = false,
        component_separators = { left = '|', right = '|' },
        section_separators = { left = nil, right = nil },
        disabled_filetypes = {
          statusline = {
            'lazy',
            'neotree',
            'snacks_dashboard',
          },
          winbar = {
            'lazy',
            'neotree',
            'snacks_dashboard',
            'snacks_terminal',
          },
        },
      },
      sections = {
        lualine_a = { 'mode' },
        lualine_b = { 'branch' },
        lualine_c = {
          { '%=', separator = '' },
          {
            'harpoon2',
            indicators = {
              get_harpoon_indicator '1',
              get_harpoon_indicator '2',
              get_harpoon_indicator '3',
              get_harpoon_indicator '4',
            },
            active_indicators = {
              get_harpoon_indicator '1',
              get_harpoon_indicator '2',
              get_harpoon_indicator '3',
              get_harpoon_indicator '4',
            },
            _separator = '  ',
            color = { fg = '#414868' },
            color_active = { fg = '#C0CAF5' },
          },
        },
        lualine_x = { 'encoding', 'filetype' },
        lualine_y = {
          {
            'copilot',
            symbols = {
              status = {
                icons = {
                  enabled = '',
                  sleep = '',
                  disabled = '',
                  warning = '',
                  unknown = '',
                },
              },
            },
          },
        },
        lualine_z = { 'location' },
      },
      inactive_sections = {
        lualine_a = {},
        lualine_b = {},
        lualine_c = { 'filename' },
        lualine_x = { 'location' },
        lualine_y = {},
        lualine_z = {},
      },
      winbar = {
        lualine_a = {},
        lualine_b = {},
        lualine_c = {
          {
            'filename',
            path = 1,
            file_status = false,
            newfile_status = false,
            cond = function()
              return vim.bo.buftype == ''
            end,
            color = { fg = '#6b7199', bg = 'none' },
          },
        },
        lualine_x = {},
        lualine_y = {},
        lualine_z = {},
      },
      inactive_winbar = {
        lualine_a = {},
        lualine_b = {},
        lualine_c = {
          {
            'filename',
            path = 1,
            file_status = false,
            newfile_status = false,
            cond = function()
              return vim.bo.buftype == ''
            end,
            color = { fg = '#414868', bg = 'none' },
          },
        },
        lualine_x = {},
        lualine_y = {},
        lualine_z = {},
      },
      extensions = {
        'oil',
      },
    },
  },
  {
    'letieu/harpoon-lualine',
    dependencies = {
      {
        'ThePrimeagen/harpoon',
        branch = 'harpoon2',
      },
    },
  },
  'AndreM222/copilot-lualine',
}
