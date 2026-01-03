#!/bin/bash

# =============================================================================
# COMMAND CENTER - Setup Script
# =============================================================================
# This script sets up the automation engine and scheduler
# =============================================================================

set -e

echo "======================================"
echo "🤖 COMMAND CENTER SETUP"
echo "======================================"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "📁 Base directory: $BASE_DIR"
echo "📁 Script directory: $SCRIPT_DIR"

# Create necessary directories
echo ""
echo "📂 Creating directories..."
mkdir -p "$SCRIPT_DIR/logs"
mkdir -p "$BASE_DIR/clients/brez-scales/data"
mkdir -p "$BASE_DIR/clients/brez-scales/reports"

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r "$SCRIPT_DIR/requirements.txt" --quiet

# Install schedule if not present
pip3 install schedule --quiet

echo ""
echo "✅ Dependencies installed!"

# Test the engine
echo ""
echo "🧪 Testing automation engine..."
python3 "$SCRIPT_DIR/automation_engine.py" --mode=check --period=last_3d

echo ""
echo "======================================"
echo "✅ SETUP COMPLETE!"
echo "======================================"
echo ""
echo "To start the scheduler manually:"
echo "  python3 $SCRIPT_DIR/scheduler.py"
echo ""
echo "To install as a background service (macOS):"
echo "  cp $SCRIPT_DIR/com.brezscales.automation.plist ~/Library/LaunchAgents/"
echo "  launchctl load ~/Library/LaunchAgents/com.brezscales.automation.plist"
echo ""
echo "To stop the service:"
echo "  launchctl unload ~/Library/LaunchAgents/com.brezscales.automation.plist"
echo ""
