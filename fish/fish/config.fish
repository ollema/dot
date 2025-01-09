# set XDG_CONFIG_HOME
set -gx XDG_CONFIG_HOME $HOME/.config

# brew
switch (uname -s)
    case Darwin
        eval "$(/opt/homebrew/bin/brew shellenv)"
    case Linux
        if test -x /home/linuxbrew/.linuxbrew/bin/brew
            eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
        end
end

# set editor
set -gx EDITOR (which nvim)
set -gx VISUAL $EDITOR
set -gx SUDO_EDITOR $EDITOR

# vim mode
fish_vi_key_bindings
for mode in insert default visual
    bind -M $mode \cy forward-char
end

# cursor styles
set -gx fish_vi_force_cursor 1
set -gx fish_cursor_default block
set -gx fish_cursor_insert line blink
set -gx fish_cursor_visual block
set -gx fish_cursor_replace_one underscore

# disable greeting
set -U fish_greeting

# git
alias gg lazygit
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
alias ls "eza --group-directories-first"
alias ll "eza -l --group-directories-first"
alias la "eza -a --group-directories-first"
alias lt "eza --tree --group-directories-first"
alias lla "eza -la --group-directories-first"

# nvim
alias vim nvim

# other
alias reload "exec fish"
alias grep rg
alias find fd

function mwdev
    ssh madlad-server-dev
end

# starship
starship init fish | source

# pnpm
set -gx PNPM_HOME /Users/s0001325/Library/pnpm
if not string match -q -- $PNPM_HOME $PATH
    set -gx PATH $PNPM_HOME $PATH
end

# cargo
if test -x $HOME/.cargo/env.fish
    source $HOME/.cargo/env.fish
end

# tokyonight color palette
set -l foreground c0caf5
set -l selection 283457
set -l comment 565f89
set -l red f7768e
set -l orange ff9e64
set -l yellow e0af68
set -l green 9ece6a
set -l purple 9d7cd8
set -l cyan 7dcfff
set -l pink bb9af7

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
