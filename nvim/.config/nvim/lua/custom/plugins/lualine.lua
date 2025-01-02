local toggleterm_status = function()
  return '#' .. vim.b.toggle_number
end

local toggleterm_extension = {
  sections = {
    lualine_a = { 'mode' },
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
        lualine_c = { 'filename' },
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
  'AndreM222/copilot-lualine',
}
