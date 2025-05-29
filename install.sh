#!/bin/bash
# install.sh - StreamBoard Quick Install Script

echo "
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ███████╗████████╗██████╗ ███████╗ █████╗ ███╗   ███╗   ║
║   ██╔════╝╚══██╔══╝██╔══██╗██╔════╝██╔══██╗████╗ ████║   ║
║   ███████╗   ██║   ██████╔╝█████╗  ███████║██╔████╔██║   ║
║   ╚════██║   ██║   ██╔══██╗██╔══╝  ██╔══██║██║╚██╔╝██║   ║
║   ███████║   ██║   ██║  ██║███████╗██║  ██║██║ ╚═╝ ██║   ║
║   ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝   ║
║                                                           ║
║              BOARD - Analytics Made Simple                ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"

echo "🚀 Starting StreamBoard installation..."
echo ""

# Check Python version
echo "✓ Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python $required_version or higher is required (found $python_version)"
    exit 1
fi
echo "  Found Python $python_version"

# Create virtual environment
echo ""
echo "✓ Creating virtual environment..."
python3 -m venv streamboard_env

# Activate virtual environment
echo "✓ Activating virtual environment..."
source streamboard_env/bin/activate

# Upgrade pip
echo ""
echo "✓ Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "✓ Installing StreamBoard dependencies..."
pip install -r requirements.txt --quiet

# Create necessary directories
echo ""
echo "✓ Creating directory structure..."
mkdir -p .streamlit
mkdir -p config
mkdir -p services
mkdir -p utils
mkdir -p data

# Create config file if it doesn't exist
if [ ! -f .streamlit/config.toml ]; then
    echo "✓ Creating StreamBoard configuration..."
    cp .streamlit/config.toml.example .streamlit/config.toml 2>/dev/null || true
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "✓ Creating environment configuration..."
    cat > .env << EOL
# StreamBoard Environment Configuration
# Add your API credentials here

# Google Analytics
GA4_PROPERTY_ID=your_property_id_here

# AWS Configuration
AWS_REGION=us-east-1

# Application Settings
STREAMBOARD_PORT=8501
STREAMBOARD_ENV=development
EOL
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║   ✅  StreamBoard installation complete!                  ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "🎯 Next steps:"
echo ""
echo "1. Configure your API credentials in the .env file"
echo "2. Run 'streamboard start' to launch the dashboard"
echo "3. Open http://localhost:8501 in your browser"
echo ""
echo "📚 Documentation: https://github.com/streamboard/streamboard"
echo "💬 Community: https://discord.gg/streamboard"
echo ""

# Create streamboard command
cat > streamboard << 'EOL'
#!/bin/bash
source streamboard_env/bin/activate
if [ "$1" == "start" ]; then
    echo "🚀 Starting StreamBoard on http://localhost:8501"
    streamlit run app.py
elif [ "$1" == "stop" ]; then
    echo "⏹️  Stopping StreamBoard..."
    pkill -f "streamlit run"
elif [ "$1" == "status" ]; then
    if pgrep -f "streamlit run" > /dev/null; then
        echo "✅ StreamBoard is running"
    else
        echo "❌ StreamBoard is not running"
    fi
else
    echo "Usage: streamboard [start|stop|status]"
fi
EOL

chmod +x streamboard

echo "💡 Tip: Run './streamboard start' to launch your dashboard!"