function gocd() {
    dir=$(git worktree list | fzf | awk '{print $1}')
    if [ -z "$dir" ]; then
        echo "No selection made."
        return 1
    fi
    cd "$dir"
}