"""TextNow Factory - Application Entry Point (for Render/Docker deployment)"""
import sys
from pathlib import Path

# Ensure project root is in Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.dashboard_server.tn_web_dashboard import app
from config.settings import WEB_HOST, WEB_PORT, DEBUG

if __name__ == "__main__":
    app.run(host=WEB_HOST, port=WEB_PORT, debug=DEBUG)