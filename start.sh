#!/bin/bash
set -e

echo "Starting MAST Annotator Web..."
echo "Backend will run on port 3000"
echo "Frontend will run on port 9000"

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 3000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 5

# Start frontend with explicit host and port settings
streamlit run ui/streamlit_app.py --server.address=0.0.0.0 --server.port=9000 --server.headless=true &
FRONTEND_PID=$!

# Function to handle cleanup
cleanup() {
    echo "Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

# Set up signal handling
trap cleanup SIGTERM SIGINT

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID