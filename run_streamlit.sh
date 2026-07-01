#!/bin/bash

# Acute Ischemic Stroke Segmentation - Streamlit Dashboard Launcher

echo "=========================================="
echo "Acute Ischemic Stroke Segmentation"
echo "=========================================="
echo ""

if ! command -v streamlit &> /dev/null; then
    echo "Streamlit not found! Installing..."
    pip install -r requirements_streamlit.txt
    echo ""
fi

echo "Checking API health..."
API_URL="https://herutriana44-acute-ischemic-stroke-segmentation.hf.space"
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" $API_URL/health 2>/dev/null)

if [ "$HEALTH_CHECK" = "200" ]; then
    echo "API healthy: $API_URL"
else
    echo "Warning: API tidak bisa dijangkau (mungkin cold start HF Space)"
fi

echo ""
echo "Starting Streamlit dashboard..."
echo "URL: http://localhost:8501"
echo "Tekan Ctrl+C untuk stop"
echo "=========================================="
echo ""

streamlit run streamlit_app.py \
    --server.port 8501 \
    --server.address localhost \
    --browser.gatherUsageStats false
