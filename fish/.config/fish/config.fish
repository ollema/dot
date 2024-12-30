if status is-interactive
  # commands to run in interactive sessions can go here
end

# cursor styles
set -gx fish_vi_force_cursor 1
set -gx fish_cursor_default block
set -gx fish_cursor_insert line blink
set -gx fish_cursor_visual block
set -gx fish_cursor_replace_one underscore

# disable greeting
set -U fish_greeting

alias reload "exec fish"


# git
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
set -gx EZA_CONFIG_DIR $HOME/.config/eza
alias ls "eza --group-directories-first";
alias ll "eza -l --group-directories-first";
alias la "eza -a --group-directories-first";
alias lt "eza --tree --group-directories-first";
alias lla "eza -la --group-directories-first";

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

# brew
eval "$(/opt/homebrew/bin/brew shellenv)"

# starship
starship init fish | source

# pnpm
set -gx PNPM_HOME "/Users/s0001325/Library/pnpm"
if not string match -q -- $PNPM_HOME $PATH
  set -gx PATH "$PNPM_HOME" $PATH
end

