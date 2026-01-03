#!/bin/bash

# Brez Scales - Streamlit Dashboard Runner
# Run this script to start the dashboard

echo "🚀 Starting Brez Scales Dashboard..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

# Load environment variables from project root
export $(cat ../../../../.env | grep -v '^#' | xargs)

# Run Streamlit
echo ""
echo "✅ Dashboard starting at http://localhost:8501"
echo ""
streamlit run app.py --server.port 8501 --server.headless true
