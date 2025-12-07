#!/bin/bash
# Quick setup script for P2C2R Pygame Demo

echo "=========================================="
echo "🚀 P2C2R Pygame Demo - Quick Setup"
echo "=========================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.9"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo "✓ Python $python_version detected (>= 3.9)"
else
    echo "✗ Python 3.9+ required. Found: $python_version"
    echo "  Please install Python 3.9 or higher"
    exit 1
fi
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
echo "  - numpy (ML computations)"
echo "  - scikit-learn (ML models)"
echo "  - pygame (game engine)"
echo ""

if pip3 install -r requirements.txt; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    echo "  Try manually: pip3 install pygame numpy scikit-learn"
    exit 1
fi
echo ""

# Test imports
echo "🧪 Testing imports..."
if python3 -c "import pygame; import numpy; import sklearn; print('✓ All imports successful')"; then
    echo ""
else
    echo "✗ Import test failed"
    exit 1
fi

# Ready to run
echo "=========================================="
echo "✓ Setup complete! Ready to run."
echo "=========================================="
echo ""
echo "🎮 To run the demo:"
echo "   python3 examples/pygame_raytracing_demo.py"
echo ""
echo "📚 For more information:"
echo "   - README: examples/PYGAME_DEMO_README.md"
echo "   - Visual Guide: docs/PYGAME_DEMO_VISUAL_GUIDE.md"
echo ""
echo "Controls:"
echo "   Arrow Keys: Move"
echo "   Space: Shoot"
echo "   T: Toggle P2C2R (see the difference!)"
echo "   R: Reset"
echo "   ESC: Quit"
echo ""
echo "=========================================="
