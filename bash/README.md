# Bash Scripts

Self-contained bash scripts for system automation and CLI tasks.

## Running Scripts

```bash
chmod +x bash/script.sh
./bash/script.sh [OPTIONS]
```

## Available Scripts

*No scripts yet.*

---

## Creating Scripts

### Required Structure

```bash
#!/usr/bin/env bash
# Description: What this script does
# Usage: ./script.sh [OPTIONS]

set -euo pipefail

show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]
Description.

Options:
    -h, --help      Show help
    -v, --verbose   Verbose output
EOF
}

main() {
    echo "Hello!"
}

main "$@"
```

### Requirements Checklist

- ✅ Shebang: `#!/usr/bin/env bash` (not `#!/bin/sh`)
- ✅ `set -euo pipefail` at top
- ✅ Header comments (description, usage)
- ✅ `show_help()` function
- ✅ Quote variables: `"$var"`
- ✅ Functions for complex logic
- ✅ Executable: `chmod +x`
- ✅ Passes `shellcheck`

---

## Error Handling

### Standard Pattern

```bash
set -euo pipefail  # Fail fast

error() {
    echo "Error: $*" >&2
    exit 1
}

# Usage
[ -f "$file" ] || error "File not found: $file"
command -v jq &> /dev/null || error "jq not installed"
```

### Checking Dependencies

```bash
for cmd in jq curl git; do
    command -v "$cmd" &> /dev/null || {
        echo "Error: $cmd not installed" >&2
        exit 1
    }
done
```

---

## Argument Parsing

```bash
VERBOSE=false
OUTPUT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        -*)
            echo "Error: Unknown option: $1" >&2
            exit 1
            ;;
        *)
            ARGS+=("$1")
            shift
            ;;
    esac
done
```

---

## Output Patterns

### Colors (Optional)

```bash
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

error() { echo -e "${RED}Error:${NC} $*" >&2; exit 1; }
success() { echo -e "${GREEN}$*${NC}"; }
warning() { echo -e "${YELLOW}Warning:${NC} $*" >&2; }
```

### Verbose Mode

```bash
verbose() {
    [ "$VERBOSE" = true ] && echo "[VERBOSE] $*" >&2
}
```

---

## File Operations

```bash
# Read file line by line
while IFS= read -r line; do
    echo "$line"
done < "$file"

# Temporary files
temp=$(mktemp)
trap 'rm -f "$temp"' EXIT

# Path manipulation
dir=$(dirname "$path")
filename=$(basename "$path")
extension="${filename##*.}"
basename="${filename%.*}"
```

---

## Common Patterns

### User Confirmation

```bash
read -r -p "Continue? [y/N] " response
case "$response" in
    [yY][eE][sS]|[yY])
        # proceed
        ;;
    *)
        exit 0
        ;;
esac
```

### Retry Logic

```bash
retry() {
    local max=$1; shift
    local attempt=1

    while [ $attempt -le $max ]; do
        if "$@"; then return 0; fi
        ((attempt++))
        sleep 2
    done

    error "Failed after $max attempts"
}

retry 3 curl -f https://example.com/file
```

### JSON with jq

```bash
# Parse JSON
name=$(jq -r '.name' < file.json)

# Filter
jq '.items[] | select(.active == true)' < data.json

# Create JSON
jq -n --arg name "value" '{name: $name, count: 42}'
```

---

## Testing

```bash
# Syntax check
bash -n bash/script.sh

# Lint with shellcheck
shellcheck bash/script.sh

# Test help
./bash/script.sh --help

# Optional: BATS tests
# tests/bash/test_script.bats
```

See [tests/README.md](../tests/README.md) for details.

---

## Style Guidelines

- `UPPERCASE` for environment vars and constants
- `lowercase` for local variables
- Always quote variables: `"$var"`
- Use `$(command)` not backticks
- Use `[[ ]]` not `[ ]` for tests
- Use functions for complex logic

---

## Anti-Patterns

❌ `#!/bin/sh` instead of `#!/usr/bin/env bash`
❌ Missing `set -euo pipefail`
❌ Unquoted variables: `$var`
❌ No `show_help()` function
❌ Using `cd` without error check
❌ Parsing `ls` output
❌ Using `==` in `[ ]` (use `=` or `[[ ]]`)

---

## Resources

- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
- [ShellCheck](https://www.shellcheck.net/)
- [Bash Hackers Wiki](https://wiki.bash-hackers.org/)
