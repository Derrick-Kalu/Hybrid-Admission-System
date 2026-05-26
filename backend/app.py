"""
app.py — Flask Application Entry Point
Bingham University Hybrid Admission Pre-Screening System

All data is stored in MongoDB (no SQLite/SQLAlchemy).
"""

# Monkey-patch select.select on Windows to prevent Werkzeug's reloader from throwing
# WSAENOTSOCK (OSError: [WinError 10038]) during socket shutdown in Python 3.14+
import sys
if sys.platform == 'win32':
    import select
    _orig_select = select.select
    def _patched_select(r, w, x, timeout=None):
        try:
            return _orig_select(r, w, x, timeout)
        except OSError as e:
            if getattr(e, 'winerror', None) == 10038 or e.errno == 10038:
                return [], [], []
            raise
    select.select = _patched_select

import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Security configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super-secret-bingham-key-2026')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB upload limit


from db import get_db
try:
    get_db()
    print("[Startup] MongoDB connection established.")
except RuntimeError as e:
    print(f"[Startup] WARNING: {e}")
    print("[Startup] App will start but database operations will fail.")

# ── Register routes ───────────────────────────────────────────────────────────
from routes import api
app.register_blueprint(api, url_prefix='/api')


@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        get_db()
        db_status = 'connected'
    except RuntimeError:
        db_status = 'unavailable'
    return jsonify({'status': 'ok', 'database': db_status})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
# Reload trigger comment
