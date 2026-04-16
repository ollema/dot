function gd --description "Show and preview git diffs through fzf"
    set -l git_args --color=always

    for arg in $argv
        if test "$arg" = --side
            set -x DELTA_FEATURES "$DELTA_FEATURES side-by-side"
        else
            set -a git_args $arg
        end
    end

    set -l git_args_str (string escape -- $git_args | string join ' ')

    git diff $git_args --name-only \
        | fzf \
            --preview "git diff $git_args_str -- ':/{-1}' | delta --width=\$FZF_PREVIEW_COLUMNS" \
            --preview-window="right,75%"
    or true
end
