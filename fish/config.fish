if test (uname) = Darwin
    /opt/homebrew/bin/brew shellenv | source
end

fish_add_path -g $HOME/.local/bin

set -gx EDITOR nvim
set -gx VISUAL nvim
set -gx COLORTERM truecolor

if status is-interactive
    # disable the greeting message
    set -g fish_greeting

    # ls aliases
    alias ls 'eza'
    abbr -a ll 'eza -l --git --group-directories-first'
    abbr -a lla 'eza -la --git --group-directories-first'
    abbr -a lt 'eza --tree --level=2 --group-directories-first'

    # cat alias
    alias cat 'bat'

    # vim alias
    alias vim 'nvim'

    # git aliases
    abbr -a gs git status
    abbr -a ga git add .
    abbr -a gc git commit
    abbr -a gcm git commit -m
    abbr -a gac "git add .; git commit --amend --no-edit"
    abbr -a gp git push
    abbr -a gl git log --oneline --graph --decorate

    # sane defaults
    abbr -a mkdir mkdir -p
    abbr -a df df -h
    abbr -a du du -h

    # autossh for zmx sessions (ash d.term, ash t.dev, etc.)
    abbr -a ash "autossh -M 0 -q"

    # helpful aliases
    alias reload "exec fish"

    # load environment variables
    test -e {$HOME}/.env; and source {$HOME}/.env

    # use Everforest Dark Hard theme for fish
    fish_config theme choose "Everforest Dark Hard"

    # starship prompt
    starship init fish | source
end
