if test (uname) = Darwin
    if status is-interactive
        if not ssh-add -l &>/dev/null
            ssh-add --apple-use-keychain ~/.ssh/id_ed25519 ~/.ssh/id_ed25519_zenseact &>/dev/null
        end
    end
end
