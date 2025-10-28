#!/bin/bash
# ForgeWeb Development Setup Script

echo "🚀 Setting up ForgeWeb development environment..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install requests python-dotenv pillow

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "✏️  Please edit .env file with your configuration"
fi

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p assets/images
mkdir -p assets/css
mkdir -p assets/js
mkdir -p templates
mkdir -p uploads
mkdir -p user_assets

# Create requirements.txt
echo "📋 Creating requirements.txt..."
cat > requirements.txt << EOF
requests>=2.31.0
python-dotenv>=1.0.0
pillow>=10.0.0
EOF

echo "✅ Development environment setup complete!"
echo ""
echo "To start developing:"
echo "1. Edit .env file with your settings"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python admin/file-api.py"
echo ""
echo "🌐 Admin Interface: http://localhost:8000/admin/"
echo "🔍 Site Preview: http://localhost:8000/"