"""
db.py — MongoDB Operational Database Layer
Bingham University Hybrid Admission System

Provides the single PyMongo client and helper accessors for all
operational collections. This replaces Flask-SQLAlchemy/SQLite entirely.

Collections:
  - applicants            : Registered applicant accounts
  - academic_records      : Course application and O'Level/JAMB data
  - uploaded_documents    : File paths + OCR extracted text
  - screening_results     : Rule-based screening outcomes
  - ml_results            : ML model predictions
  - admin_approvals       : Final admin approve/reject decisions
"""

import os
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError
from dotenv import load_dotenv
import certifi

load_dotenv()

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('MONGO_DB_NAME', 'bingham_admission')

_client = None
_db = None


def get_db():
    """
    Returns the MongoDB operational database instance.
    Initialises the connection on first call.
    Raises RuntimeError if MongoDB is unavailable.
    """
    global _client, _db
    if _db is not None:
        return _db
    
    import time
    from pymongo.read_preferences import ReadPreference
    
    last_error = None
    for attempt in range(3):
        try:
            _client = MongoClient(
                MONGO_URI,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                tlsCAFile=certifi.where() if MONGO_URI.startswith('mongodb+srv') else None
            )
            # Use PRIMARY_PREFERRED read preference so ping succeeds during replica set primary elections
            _client.admin.command('ping', read_preference=ReadPreference.PRIMARY_PREFERRED)
            _db = _client[DB_NAME]
            _ensure_indexes(_db)
            print(f"[MongoDB] Connected to operational DB '{DB_NAME}'")
            return _db
        except (ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError, Exception) as e:
            last_error = e
            if attempt < 2:
                time.sleep(1)
                continue
    
    raise RuntimeError(f"[MongoDB] Cannot connect to database: {last_error}")


def _ensure_indexes(db):
    """Create unique indexes to enforce data integrity."""
    db['applicants'].create_index([('email', ASCENDING)], unique=True)
    db['applicants'].create_index([('jamb_reg_number', ASCENDING)], unique=True)
    db['academic_records'].create_index([('applicant_id', ASCENDING)], unique=True)
    db['screening_results'].create_index([('applicant_id', ASCENDING)], unique=True)
    db['ml_results'].create_index([('applicant_id', ASCENDING)], unique=True)
    db['admin_approvals'].create_index([('applicant_id', ASCENDING)])

    # Seed/reset the administrator account
    admin_email = 'admin@bingham.edu.ng'
    from werkzeug.security import generate_password_hash
    from datetime import datetime, timezone
    db['applicants'].update_one(
        {'email': admin_email},
        {'$set': {
            'full_name': 'BINGHAM ADMISSION OFFICE',
            'phone': '0800BINGHAM',
            'jamb_reg_number': 'ADMIN-PORTAL',
            'password_hash': generate_password_hash('BinghamAdmin2026!'),
            'created_at': datetime.now(timezone.utc)
        }},
        upsert=True
    )
    print(f"[MongoDB] Seeded/updated default administrator account: {admin_email}")


# ─── Collection Accessors ─────────────────────────────────────────────────────

def applicants():
    return get_db()['applicants']

def academic_records():
    return get_db()['academic_records']

def uploaded_documents():
    return get_db()['uploaded_documents']

def screening_results():
    return get_db()['screening_results']

def ml_results():
    return get_db()['ml_results']

def admin_approvals():
    return get_db()['admin_approvals']
