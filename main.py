"""Main entry point for the Followupper application."""

from src.api import app
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


if __name__ == "__main__":
    print("🚀 Starting Followupper API server...")
    print("📡 API available at: http://localhost:5000")
    print("🔗 Health check: http://localhost:5000/api/health")
    print("🌐 Frontend should connect to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
