function zmx-select --description 'Fuzzy-pick or create a zmx session'
    set -l display (zmx list 2>/dev/null | while read -l line
        set -l parts (string split \t -- $line)
        set -l name (string replace -r '^session_name=' '' -- $parts[1])
        set -l pid (string replace -r '^pid=' '' -- $parts[2])
        set -l clients (string replace -r '^clients=' '' -- $parts[3])
        set -l dir (string replace -r '^started_in=' '' -- $parts[5])
        printf "%-20s  pid:%-8s  clients:%-2s  %s\n" $name $pid $clients $dir
    end)

    set -l output (string join \n -- $display | fzf \
        --print-query \
        --expect=ctrl-n \
        --height=80% \
        --reverse \
        --prompt="zmx> " \
        --header="Enter: select | Ctrl-N: create new" \
        --preview='zmx history {1}' \
        --preview-window=right:60%:follow)
    set -l rc $status

    set -l query $output[1]
    set -l key $output[2]
    set -l selected $output[3]

    if test "$key" = ctrl-n; and test -n "$query"
        zmx attach $query
    else if test $rc -eq 0; and test -n "$selected"
        set -l name (string split --no-empty ' ' -- $selected)[1]
        zmx attach $name
    else if test -n "$query"
        zmx attach $query
    else
        return 130
    end
end
