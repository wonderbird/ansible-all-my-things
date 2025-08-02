#!/bin/bash
# Setup command restrictions for AI agent
# Creates blocking functions for forbidden commands
#
# Note: Uses functions instead of aliases because:
# - Functions work in non-interactive shells (where aliases don't)
# - Functions take precedence over external commands
# - Functions are harder to bypass than aliases

set -euo pipefail

# Array of forbidden commands
FORBIDDEN_COMMANDS=(
    "ansible"
    "vagrant" 
    "docker"
    "tart"
    "aws"
    "hcloud"
)

# Handle status mode - show which commands are actually blocked
if [[ "${1:-}" == "--status" ]]; then
    echo "Command restriction status:"
    for service in "${FORBIDDEN_COMMANDS[@]}"; do
        if declare -F "$service" >/dev/null 2>&1; then
            echo "  $service: BLOCKED"
        else
            echo "  $service: NOT BLOCKED (run 'source <(./scripts/setup-command-restrictions.sh)' to block)"
        fi
    done
    exit 0
fi

# Function to create blocking function for a service
create_blocking_function() {
    local service="$1"
    echo "$service() { echo \"ERROR: Command \\\"$service\\\" must be executed by user per project rules\" >&2; return 1; }"
}

# Main execution
echo "# AI Agent Command Restrictions"
echo ""

# Create blocking functions for all forbidden commands
for service in "${FORBIDDEN_COMMANDS[@]}"; do
    create_blocking_function "$service"
done

echo ""
echo "# Restriction setup complete"
echo "echo 'Command restrictions active for AI agent session'"