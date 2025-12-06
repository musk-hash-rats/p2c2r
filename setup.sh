#!/bin/bash
# Quick setup script for P2C2G development

echo "🚀 P2C2G Project Setup"
echo "====================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo ""
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install package in development mode
echo ""
echo "Installing p2c2g package in development mode..."
pip install -e .

# Run tests to verify setup
echo ""
echo "Running tests to verify setup..."
pytest tests/ -v

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment manually, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the PoC:"
echo "  python p2c2g_poc.py"
echo "  or"
echo "  python -m p2c2g"
echo ""
echo "To run tests:"
echo "  pytest tests/"
echo ""
