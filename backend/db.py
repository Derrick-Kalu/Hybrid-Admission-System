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
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
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
    try:
        _client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000,
            tlsCAFile=certifi.where() if MONGO_URI.startswith('mongodb+srv') else None
        )
        _client.admin.command('ping')
        _db = _client[DB_NAME]
        _ensure_indexes(_db)
        print(f"[MongoDB] Connected to operational DB '{DB_NAME}'")
        return _db
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        raise RuntimeError(f"[MongoDB] Cannot connect to database: {e}")


def _ensure_indexes(db):
    """Create unique indexes to enforce data integrity."""
    db['applicants'].create_index([('email', ASCENDING)], unique=True)
    db['applicants'].create_index([('jamb_reg_number', ASCENDING)], unique=True)
    db['academic_records'].create_index([('applicant_id', ASCENDING)], unique=True)
    db['screening_results'].create_index([('applicant_id', ASCENDING)], unique=True)
    db['ml_results'].create_index([('applicant_id', ASCENDING)], unique=True)
    db['admin_approvals'].create_index([('applicant_id', ASCENDING)])


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
