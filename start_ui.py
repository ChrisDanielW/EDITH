"""
Quick start script for EDITH Web UI
Launches the Flask API server
"""

import subprocess
import sys
import os
from pathlib import Path

print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   👓 EDITH - Even Disconnected, I'm The Helper              ║
║                                                              ║
║   Starting Web Interface...                                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

# Check if Flask is installed
try:
    import flask
    from flask_cors import CORS
    print("✅ Flask dependencies found")
except ImportError:
    print("❌ Missing Flask dependencies!")
    print("\nInstalling required packages...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", 
        "flask", "flask-cors"
    ])
    print("✅ Installation complete!")

# Change to project root
project_root = Path(__file__).parent
os.chdir(project_root)

print("\n🚀 Launching EDITH API Server...")
print("📡 API: http://localhost:5000/api")
print("🌐 UI:  http://localhost:5000")
print("\n💡 Press Ctrl+C to stop the server\n")
print("="*60 + "\n")

# Run the Flask app
try:
    subprocess.run([sys.executable, "src/api/app.py"])
except KeyboardInterrupt:
    print("\n\n👋 Shutting down EDITH...")
    print("Goodbye!\n")
