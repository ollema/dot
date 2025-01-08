stow:
    stow --target ~/.config eza
    stow --target ~/.config fish
    stow --target ~/.config lazygit
    stow --target ~/.config ghostty
    stow --target ~/.config nvim
    stow --target ~/.config starship

dump:
    brew bundle dump --force --formula --file={{ justfile_directory() }}/Brewfile
    cat {{ justfile_directory() }}/Brewfile

check:
    brew bundle check --file={{ justfile_directory() }}/Brewfile

install:
    brew bundle install --file={{ justfile_directory() }}/Brewfile
