local function file_from_path(path)
  return path:match '([^/]+)$'
end

local function get_harpoon_indicator(label)
  return function(harpoon_entry)
    return label .. ' ' .. file_from_path(harpoon_entry.value)
  end
end

local toggleterm_status = function()
  return '#' .. vim.b.toggle_number
end

local toggleterm_extension = {
  sections = {
    lualine_a = { 'mode' },
    lualine_b = { toggleterm_status },
  },
  inactive_sections = {
    lualine_b = { toggleterm_status },
  },
  filetypes = { 'toggleterm' },
}

return {
  {
    'nvim-lualine/lualine.nvim',
    opts = {
      options = {
        icons_enabled = false,
        component_separators = { left = '|', right = '|' },
        section_separators = { left = nil, right = nil },
        disabled_filetypes = {
          statusline = {
            'snacks_dashboard',
          },
        },
      },
      sections = {
        lualine_a = { 'mode' },
        lualine_b = { 'branch' },
        lualine_c = {
          { 'filename', separator = '' },
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
              get_harpoon_indicator '[1]',
              get_harpoon_indicator '[2]',
              get_harpoon_indicator '[3]',
              get_harpoon_indicator '[4]',
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
            -- Default values
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
      extensions = {
        'lazy',
        'neo-tree',
        'oil',
        toggleterm_extension,
        'trouble',
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
