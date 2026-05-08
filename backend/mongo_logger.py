"""
mongo_logger.py — MongoDB Audit & Accountability Layer
Bingham University Hybrid Admission System

This module provides an immutable audit trail for all critical system events.
It runs ALONGSIDE the SQLite operational database.

MongoDB Collections:
  - audit_logs       : Every API action with timestamps
  - ocr_reports      : Full OCR extraction results per document
  - screening_reports: Rule Engine + ML output per applicant
  - admin_actions    : Every admin approve/reject decision
  - login_attempts   : All login attempts (success & failure)

Configuration:
  Set MONGO_URI environment variable for Atlas or custom URI.
  Defaults to local MongoDB on port 27017.
"""

import os
from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
import certifi

load_dotenv()

# ── Connection Configuration ──────────────────────────────────────────────────
# Override with environment variable for MongoDB Atlas:
# export MONGO_URI="mongodb+srv://user:pass@cluster.mongodb.net/bingham_audit"
MONGO_URI = os.environ.get(
    'MONGO_URI',
    'mongodb://localhost:27017/'
)
DB_NAME = 'bingham_admission_audit'

# Singleton client
_client = None
_db = None


def get_db():
    """
    Returns the MongoDB database instance.
    Initializes the connection on first call.
    Returns None if MongoDB is unavailable (fails silently to protect main app).
    """
    global _client, _db
    if _db is not None:
        return _db
    try:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, tlsCAFile=certifi.where())
        # Ping to confirm connection
        _client.admin.command('ping')
        _db = _client[DB_NAME]
        print(f"[MongoDB] Connected to '{DB_NAME}' at {MONGO_URI}")
        return _db
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"[MongoDB] WARNING: Could not connect — {e}. Audit logging disabled.")
        return None


def _now():
    return datetime.now(timezone.utc)


def _log(collection_name, document):
    """
    Internal helper — inserts a document into a collection.
    Silently skips if MongoDB is unavailable.
    """
    try:
        db = get_db()
        if db is None:
            return
        document['_created_at'] = _now()
        db[collection_name].insert_one(document)
    except Exception as e:
        print(f"[MongoDB] Audit log error ({collection_name}): {e}")


# =============================================
#  PUBLIC LOGGING FUNCTIONS
# =============================================

def log_registration(applicant_id, full_name, email, jamb_reg_number, ip=None):
    """Log a successful applicant registration."""
    _log('audit_logs', {
        'event': 'REGISTRATION',
        'status': 'SUCCESS',
        'applicant_id': applicant_id,
        'full_name': full_name,
        'email': email,
        'jamb_reg_number': jamb_reg_number,
        'ip_address': ip
    })


def log_registration_failed(email, jamb_reg_number, reason, ip=None):
    """Log a failed registration attempt."""
    _log('audit_logs', {
        'event': 'REGISTRATION',
        'status': 'FAILED',
        'email': email,
        'jamb_reg_number': jamb_reg_number,
        'reason': reason,
        'ip_address': ip
    })


def log_login(applicant_id, email, success, reason=None, ip=None):
    """Log every login attempt — success or failure."""
    _log('login_attempts', {
        'event': 'LOGIN',
        'status': 'SUCCESS' if success else 'FAILED',
        'applicant_id': applicant_id,
        'email': email,
        'reason': reason,
        'ip_address': ip
    })


def log_ocr_report(applicant_id, document_type, file_path,
                    ocr_raw_text, ocr_result):
    """
    Log full OCR report for a submitted document.
    document_type: 'JAMB_RESULT' or 'O_LEVEL_RESULT'
    ocr_result: dict returned by verify_jamb_document() or verify_document()
    """
    _log('ocr_reports', {
        'applicant_id': applicant_id,
        'document_type': document_type,
        'file_path': file_path,
        'ocr_raw_text': ocr_raw_text,
        'ocr_verified': ocr_result.get('verified', False),
        'ocr_score_extracted': ocr_result.get('ocr_score'),
        'name_found_on_doc': ocr_result.get('name_found'),
        'is_jamb_document': ocr_result.get('is_jamb_document'),
        'reason': ocr_result.get('reason', '')
    })


def log_screening_report(applicant_id, applicant_name, course,
                          utme_score, jamb_verified, grades,
                          rule_result, ml_prediction=None, ml_confidence=None):
    """Log the complete screening decision for an applicant."""
    _log('screening_reports', {
        'applicant_id': applicant_id,
        'applicant_name': applicant_name,
        'course_applied': course,
        'utme_score': utme_score,
        'jamb_ocr_verified': jamb_verified,
        'o_level_grades': {
            'math': grades[0],
            'english': grades[1],
            'subject_1': grades[2],
            'subject_2': grades[3],
            'subject_3': grades[4],
        },
        'rule_engine': {
            'status': rule_result.get('status'),
            'reason': rule_result.get('reason'),
            'passed_institutional': rule_result.get('passed_institutional'),
            'passed_departmental': rule_result.get('passed_departmental'),
            'recommended_alternative': rule_result.get('recommended_alternative')
        },
        'ml_model': {
            'prediction': ml_prediction,
            'confidence_pct': round(ml_confidence * 100, 2) if ml_confidence else None
        }
    })


def log_admin_action(admin_id, applicant_id, decision, remarks, ip=None):
    """Log every admin approve/reject decision."""
    _log('admin_actions', {
        'event': 'ADMIN_DECISION',
        'admin_id': admin_id,
        'applicant_id': applicant_id,
        'decision': decision,
        'remarks': remarks,
        'ip_address': ip
    })
    # Also in main audit log
    _log('audit_logs', {
        'event': 'ADMIN_DECISION',
        'admin_id': admin_id,
        'applicant_id': applicant_id,
        'decision': decision,
        'ip_address': ip
    })


def log_application_submission(applicant_id, course, screening_status, ip=None):
    """Log the act of submitting an application."""
    _log('audit_logs', {
        'event': 'APPLICATION_SUBMITTED',
        'status': 'SUCCESS',
        'applicant_id': applicant_id,
        'course_applied': course,
        'screening_status': screening_status,
        'ip_address': ip
    })
