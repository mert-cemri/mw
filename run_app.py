#!/usr/bin/env python3
"""
Simple runner for MAST Annotator Web application.
Sets up Python path and runs the application.
"""
import os
import sys
import subprocess
import time

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    """Main entry point."""
    print("Starting MAST Annotator Web...")
    print("Backend: http://localhost:3000")  
    print("Frontend: http://localhost:9000")
    print("Press Ctrl+C to stop")
    print()
    
    # Set environment
    env = os.environ.copy()
    env['PYTHONPATH'] = current_dir + ':' + env.get('PYTHONPATH', '')
    env['MAST_FAKE_MODE'] = '0'  # Enable real LLM judge mode 
    env['MAST_STORAGE_PATH'] = os.path.join(current_dir, 'data', 'jobs')  # Local storage
    
    # Start backend
    print("Starting backend...")
    backend_process = subprocess.Popen([
        sys.executable, '-m', 'uvicorn', 
        'app.main:app', '--reload', '--port', '3000'
    ], env=env)
    
    # Wait a bit for backend to start
    time.sleep(3)
    
    # Start frontend
    print("Starting frontend...")
    try:
        frontend_process = subprocess.Popen([
            sys.executable, '-m', 'streamlit', 'run', 
            'ui/streamlit_app.py', '--server.port', '9000'
        ], env=env)
        
        # Wait for frontend to finish
        frontend_process.wait()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Clean up
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
        
        print("Stopped.")

if __name__ == "__main__":
    main()