return {
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "tokyonight-night",
    },
  },
  {
    "folke/snacks.nvim",
    opts = {
      image = {},
    },
  },
  {
    "saghen/blink.cmp",
    opts = {
      completion = {
        menu = {
          auto_show = function()
            return vim.bo.filetype ~= "gitcommit"
          end,
        },
      },
    },
  },
}
