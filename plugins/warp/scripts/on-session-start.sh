#!/bin/bash
# Hook script for Claude Code SessionStart event
# Shows welcome message, Warp detection status, and emits plugin version

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/build-payload.sh"

# Read hook input from stdin
INPUT=$(cat)

# Read plugin version from plugin.json
PLUGIN_VERSION=$(jq -r '.version // "unknown"' "$SCRIPT_DIR/../.claude-plugin/plugin.json" 2>/dev/null)

# Emit structured notification with plugin version so Warp can track it
BODY=$(build_payload "$INPUT" "session_start" \
    --arg plugin_version "$PLUGIN_VERSION")
"$SCRIPT_DIR/warp-notify.sh" "warp://cli-agent" "$BODY"

# Output system message for the Claude Code UI
if [ "$TERM_PROGRAM" = "WarpTerminal" ]; then
    # Running in Warp - notifications will work
    cat << EOF
{
  "systemMessage": "🔔 Warp plugin v${PLUGIN_VERSION} active. You'll receive native Warp notifications when tasks complete or input is needed."
}
EOF
else
    # Not running in Warp - suggest installing
    cat << EOF
{
  "systemMessage": "ℹ️ Warp plugin v${PLUGIN_VERSION} installed but you're not running in Warp terminal. Install Warp (https://warp.dev) to get native notifications when Claude completes tasks or needs input."
}
EOF
fi
