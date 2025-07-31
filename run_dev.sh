#!/bin/bash

# Development startup script for MAST Annotator Web
# This script properly sets up the Python path and starts both services

export PYTHONPATH="$(pwd):$PYTHONPATH"
export MAST_FAKE_MODE=1
export MAST_STORAGE_PATH="$(pwd)/data/jobs"

echo "Starting MAST Annotator Web in development mode..."
echo "Backend will run on http://localhost:3000"
echo "Frontend will run on http://localhost:9000"
echo ""

# Start the FastAPI backend in the background
echo "Starting backend..."
uvicorn app.main:app --reload --port 3000 &
BACKEND_PID=$!

# Give the backend time to start
sleep 3

# Start the Streamlit frontend
echo "Starting frontend..."
streamlit run ui/streamlit_app.py --server.port 9000

# Clean up background process when script exits
kill $BACKEND_PID 2>/dev/null