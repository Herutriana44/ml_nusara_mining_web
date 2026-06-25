#!/bin/bash

# NUSARA Mining Streamlit Dashboard Launcher
# Quick start script for running the Streamlit dashboard

echo "=========================================="
echo "NUSARA Mining Inference Dashboard"
echo "=========================================="
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not found!"
    echo ""
    echo "Installing dependencies..."
    pip install -r requirements_streamlit.txt
    echo ""
fi

# Check if API is reachable
echo "🔍 Checking API health..."
API_URL="https://herutriana44-ai-nusara-mining-api.hf.space"
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" $API_URL/health 2>/dev/null)

if [ "$HEALTH_CHECK" = "200" ]; then
    echo "✅ API is reachable and healthy"
else
    echo "⚠️  Warning: Could not reach API at $API_URL"
    echo "   The API might be sleeping (HuggingFace Space cold start)"
    echo "   Dashboard will still start, but predictions may fail initially"
fi

echo ""
echo "🚀 Starting Streamlit dashboard..."
echo "   Dashboard will open at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

# Start streamlit
streamlit run streamlit_app.py \
    --server.port 8501 \
    --server.address localhost \
    --browser.gatherUsageStats false
