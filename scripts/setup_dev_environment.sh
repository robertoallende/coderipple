#!/bin/bash
# CodeRipple Development Environment Setup
# Sets up a complete development environment with Python 3.13 validation

echo "🚀 Setting up CodeRipple development environment..."
echo ""

# Check Python version first
echo "🐍 Validating Python version..."
python3 scripts/validate_python_version.py
if [ $? -ne 0 ]; then
    echo "❌ Python version validation failed. Please install Python 3.13.x"
    exit 1
fi
echo ""

# Navigate to coderipple library directory
echo "📁 Setting up coderipple library environment..."
cd coderipple

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment with Python 3.13..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✅ CodeRipple development environment ready!"
echo ""
echo "To activate the environment:"
echo "  cd coderipple"
echo "  source venv/bin/activate"
echo ""
echo "To run tests:"
echo "  ./run_tests.sh"
echo ""
echo "To run the system:"
echo "  python run_coderipple.py"
