if status is-interactive
  # commands to run in interactive sessions can go here
end

# set XDG_CONFIG_HOME
set -gx XDG_CONFIG_HOME $HOME/.config

# brew
eval "$(/opt/homebrew/bin/brew shellenv)"

set -gx EDITOR (which nvim)
set -gx VISUAL $EDITOR
set -gx SUDO_EDITOR $EDITOR

# cursor styles
set -gx fish_vi_force_cursor 1
set -gx fish_cursor_default block
set -gx fish_cursor_insert line blink
set -gx fish_cursor_visual block
set -gx fish_cursor_replace_one underscore

# disable greeting
set -U fish_greeting

# fish
alias reload "exec fish"

# git
alias gg "lazygit"
abbr gs "git status"
abbr ga "git add ."
abbr gcm "git commit -m"
abbr gca "git commit --amend"
abbr gac "git add .; git commit --amend --no-edit"
abbr gp "git push"
abbr gl "git log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr)%Creset' --abbrev-commit --date=relative"
abbr gd "git diff"
abbr gf "git fetch"

# ls
set -gx EZA_CONFIG_DIR $XDG_CONFIG_HOME/eza
alias ls "eza --group-directories-first";
alias ll "eza -l --group-directories-first";
alias la "eza -a --group-directories-first";
alias lt "eza --tree --group-directories-first";
alias lla "eza -la --group-directories-first";

# nvim
alias vim "nvim"

# other
alias grep "rg"

# vim mode
fish_vi_key_bindings
bind -M insert -k nul accept-autosuggestion

function on_fish_bind_mode --on-variable fish_bind_mode
  # export the vi_mode_symbol variable which Starship can use
  set --global --export vi_mode_symbol ""
  set --local bg_color

  set --local char
  if test "$fish_key_bindings" = fish_vi_key_bindings
    switch $fish_bind_mode
      case default
        set bg_color blue
        set char " N "
      case insert
        set bg_color green
        set char " I "
      case replace replace_one
        set bg_color green
        set char " R "
      case visual
        set bg_color brmagenta
        set char " V "
      case '*'
      set bg_color cyan
      set char " ? "
    end

    set vi_mode_symbol (set_color '#1a1b26' --background $bg_color normal)$char(set_color normal)
  end
end

# starship
starship init fish | source

# pnpm
set -gx PNPM_HOME "/Users/s0001325/Library/pnpm"
if not string match -q -- $PNPM_HOME $PATH
  set -gx PATH "$PNPM_HOME" $PATH
end

# tokyonight color palette
set -l foreground c8d3f5
set -l selection 2d3f76
set -l comment 636da6
set -l red ff757f
set -l orange ff966c
set -l yellow ffc777
set -l green c3e88d
set -l purple fca7ea
set -l cyan 86e1fc
set -l pink c099ff

# syntax highlighting colors
set -g fish_color_normal $foreground
set -g fish_color_command $cyan
set -g fish_color_keyword $pink
set -g fish_color_quote $yellow
set -g fish_color_redirection $foreground
set -g fish_color_end $orange
set -g fish_color_option $pink
set -g fish_color_error $red
set -g fish_color_param $purple
set -g fish_color_comment $comment
set -g fish_color_selection --background=$selection
set -g fish_color_search_match --background=$selection
set -g fish_color_operator $green
set -g fish_color_escape $pink
set -g fish_color_autosuggestion $comment

# completion pager colors
set -g fish_pager_color_progress $comment
set -g fish_pager_color_prefix $cyan
set -g fish_pager_color_completion $foreground
set -g fish_pager_color_description $comment
set -g fish_pager_color_selected_background --background=$selection

