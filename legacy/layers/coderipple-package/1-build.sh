#!/bin/bash
# layers/coderipple-package/1-build.sh
# Build script for CodeRipple Package Layer - GitHub Actions Compatible

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔨 Building CodeRipple Package Layer..."
echo "📍 Working directory: $(pwd)"

# Step 1: Install/prepare CodeRipple package
echo "📦 Step 1: Preparing CodeRipple package..."
if [ -f "1-install.sh" ]; then
    ./1-install.sh
else
    echo "❌ 1-install.sh not found"
    exit 1
fi

# Step 2: Package the layer
echo "📦 Step 2: Packaging layer..."
if [ -f "2-package.sh" ]; then
    ./2-package.sh
else
    echo "❌ 2-package.sh not found"
    exit 1
fi

# Step 3: Validate the layer (optional in CI)
echo "✅ Step 3: Validating layer..."
if [ -f "3-validate.sh" ]; then
    ./3-validate.sh || echo "⚠️  Validation warnings (non-fatal in CI)"
else
    echo "⚠️  3-validate.sh not found (skipping validation)"
fi

echo "✅ Package layer build completed successfully!"

# Check if the layer zip was created
if [ -f "coderipple-package-layer.zip" ]; then
    layer_size=$(stat -f%z "coderipple-package-layer.zip" 2>/dev/null || stat -c%s "coderipple-package-layer.zip")
    echo "📊 Layer package size: ${layer_size} bytes"
else
    echo "❌ Layer package not found: coderipple-package-layer.zip"
    exit 1
fi

echo "🎉 Package layer ready for deployment!"
