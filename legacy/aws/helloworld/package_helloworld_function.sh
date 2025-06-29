#!/bin/bash
# package_helloworld_function.sh

set -e

echo "Packaging Hello World Lambda function..."

# Clean previous builds
rm -rf helloworld_function/
rm -f helloworld-function.zip

# Create function package
mkdir helloworld_function
cp lambda_function.py helloworld_function/

# Create deployment package
cd helloworld_function
zip -r ../helloworld-function.zip . > /dev/null
cd ..

echo "Function package created:"
ls -lh helloworld-function.zip

echo "Hello World function ready for deployment!"
