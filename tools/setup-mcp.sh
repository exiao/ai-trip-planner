#!/bin/bash

# MCP Configuration Setup Script for Arize Tracing Assistant
# This script detects the correct Python/uvx installation and generates the proper MCP configuration

set -e

echo "🔍 Detecting Python and uvx installations..."

# Function to check if a command exists and is executable
check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        echo "✅ Found: $1"
        return 0
    else
        echo "❌ Not found: $1"
        return 1
    fi
}

# Function to test if uvx can run the arize-tracing-assistant
test_uvx() {
    local uvx_path="$1"
    echo "🧪 Testing $uvx_path with arize-tracing-assistant..."
    
    # First check if uvx can be executed at all
    if ! "$uvx_path" --version >/dev/null 2>&1; then
        echo "❌ $uvx_path is not executable"
        return 1
    fi
    
    # Test with a longer timeout since uvx might need to install packages
    if timeout 30s "$uvx_path" arize-tracing-assistant@latest --help >/dev/null 2>&1; then
        echo "✅ $uvx_path works with arize-tracing-assistant"
        return 0
    else
        echo "❌ $uvx_path failed with arize-tracing-assistant (this might be normal if packages need to be installed)"
        # Don't fail completely, just note it
        return 1
    fi
}

# Detect Python installations
echo ""
echo "🐍 Checking Python installations..."

PYTHON_PATHS=()
UVX_PATHS=()

# Check common Python locations
for python_cmd in python3 python; do
    if check_command "$python_cmd"; then
        PYTHON_PATHS+=("$(which "$python_cmd")")
    fi
done

# Check for uvx in common locations
echo ""
echo "📦 Checking for uvx installations..."

# Check if uvx is in PATH
if check_command uvx; then
    UVX_PATHS+=("$(which uvx)")
fi

# Check common Python framework locations (macOS)
for version in 3.13 3.12 3.11 3.10 3.9; do
    uvx_path="/Library/Frameworks/Python.framework/Versions/$version/bin/uvx"
    if [[ -f "$uvx_path" ]]; then
        echo "✅ Found uvx at: $uvx_path"
        UVX_PATHS+=("$uvx_path")
    fi
done

# Check user local installations
for python_path in "${PYTHON_PATHS[@]}"; do
    if [[ -n "$python_path" ]]; then
        # Get the directory containing the python executable
        python_dir=$(dirname "$python_path")
        uvx_path="$python_dir/uvx"
        if [[ -f "$uvx_path" ]]; then
            echo "✅ Found uvx at: $uvx_path"
            UVX_PATHS+=("$uvx_path")
        fi
    fi
done

# Test each uvx installation
echo ""
echo "🧪 Testing uvx installations..."

WORKING_UVX=""
WORKING_PATH=""

for uvx_path in "${UVX_PATHS[@]}"; do
    if test_uvx "$uvx_path"; then
        WORKING_UVX="$uvx_path"
        # Extract the directory containing uvx for PATH
        WORKING_PATH=$(dirname "$uvx_path")
        break
    fi
done

# If no uvx passed the test, use the first one found (it might work in Cursor's environment)
if [[ -z "$WORKING_UVX" && ${#UVX_PATHS[@]} -gt 0 ]]; then
    echo ""
    echo "⚠️  No uvx installation passed the test, but we found some installations."
    echo "📝 Using the first available uvx (it might work in Cursor's environment):"
    WORKING_UVX="${UVX_PATHS[0]}"
    WORKING_PATH=$(dirname "$WORKING_UVX")
    echo "   Using: $WORKING_UVX"
fi

if [[ -z "$WORKING_UVX" ]]; then
    echo ""
    echo "❌ No uvx installation found!"
    echo "💡 Try installing uvx with: pip install uvx"
    echo "💡 Or install arize-tracing-assistant with: pip install arize-tracing-assistant"
    exit 1
fi

echo ""
echo "🎉 Found working uvx: $WORKING_UVX"
echo "📁 uvx directory: $WORKING_PATH"

# Create .cursor directory if it doesn't exist
CURSOR_DIR=".cursor"
if [[ ! -d "$CURSOR_DIR" ]]; then
    echo "📁 Creating .cursor directory..."
    mkdir -p "$CURSOR_DIR"
fi

# Generate MCP configuration
MCP_CONFIG_FILE="$CURSOR_DIR/mcp.json"

echo ""
echo "⚙️  Generating MCP configuration..."

# Create the MCP configuration
cat > "$MCP_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "arize-tracing-assistant": {
      "command": "uvx",
      "args": [
        "arize-tracing-assistant@latest"
      ],
      "env": {
        "PATH": "$WORKING_PATH:/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
EOF

echo "✅ MCP configuration created at: $MCP_CONFIG_FILE"

# Display the configuration
echo ""
echo "📋 Generated configuration:"
echo "----------------------------------------"
cat "$MCP_CONFIG_FILE"
echo "----------------------------------------"

echo ""
echo "🎯 Next steps:"
echo "1. Restart Cursor completely"
echo "2. Go to Settings → Tools & MCP"
echo "3. Verify arize-tracing-assistant appears and is connected"
echo ""
echo "🔧 If it still doesn't work, try using the absolute path:"
echo "   \"command\": \"$WORKING_UVX\""
echo ""

# Optional: Create a backup of the current config
if [[ -f "$MCP_CONFIG_FILE" ]]; then
    BACKUP_FILE="${MCP_CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "💾 Creating backup of existing config at: $BACKUP_FILE"
    cp "$MCP_CONFIG_FILE" "$BACKUP_FILE"
fi

echo "✨ Setup complete!"
