#!/bin/bash
# build_helloworld_layer.sh

set -e

echo "Building Hello World debugging layer with platform targeting..."

# Clean previous builds
rm -rf helloworld_layer/
rm -f helloworld-dependencies.zip

# Create layer directory structure
mkdir -p helloworld_layer/python

# Install dependencies with correct platform targeting (from Unit 16)
echo "Installing dependencies with platform targeting..."
python3 -m pip install \
  --platform manylinux2014_x86_64 \
  --only-binary=:all: \
  --target helloworld_layer/python \
  --requirement requirements_helloworld.txt

echo "Installed packages:"
ls -la helloworld_layer/python/

# Conservative optimization (preserve .dist-info metadata)
echo "Optimizing layer..."
find helloworld_layer/python -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find helloworld_layer/python -name "*test*" -type d -exec rm -rf {} + 2>/dev/null || true

# Create layer zip
cd helloworld_layer
zip -r ../helloworld-dependencies.zip python/ > /dev/null
cd ..

# Show layer info
echo "Layer created:"
ls -lh helloworld-dependencies.zip
echo "Layer size: $(du -h helloworld-dependencies.zip | cut -f1)"

echo "Hello World debugging layer ready for deployment!"
