"""
models.py — MongoDB Document Helper Layer
Bingham University Hybrid Admission Pre-Screening System

Replaces Flask-SQLAlchemy with PyMongo helpers.
Each function corresponds to a MongoDB collection operation.

Collections:
  - applicants
  - academic_records
  - uploaded_documents
  - screening_results
  - ml_results
  - admin_approvals
"""

from datetime import datetime, timezone
from bson import ObjectId
from db import applicants, academic_records, uploaded_documents, \
                screening_results, ml_results, admin_approvals


def _now():
    return datetime.now(timezone.utc)


def _str_id(doc):
    """Convert ObjectId _id to string for JSON responses."""
    if doc and '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc


# ─────────────────────────────────────────────────────────────────────────────
#  APPLICANT COLLECTION
# ─────────────────────────────────────────────────────────────────────────────

def create_applicant(full_name, email, phone, jamb_reg_number, password_hash):
    """Insert a new applicant document. Returns the inserted _id as string."""
    doc = {
        'full_name':        full_name,
        'email':            email.lower().strip(),
        'phone':            phone.strip(),
        'jamb_reg_number':  jamb_reg_number.upper().strip(),
        'password_hash':    password_hash,
        'created_at':       _now()
    }
    result = applicants().insert_one(doc)
    return str(result.inserted_id)


def find_applicant_by_email(email):
    """Find an applicant by email. Returns document dict or None."""
    return applicants().find_one({'email': email.lower().strip()})


def find_applicant_by_id(applicant_id):
    """Find an applicant by string _id. Returns document dict or None."""
    try:
        return applicants().find_one({'_id': ObjectId(applicant_id)})
    except Exception:
        return None


def find_applicant_by_jamb(jamb_reg_number):
    """Find an applicant by JAMB registration number."""
    return applicants().find_one({'jamb_reg_number': jamb_reg_number.upper().strip()})


def get_all_applicants():
    """Return all applicant documents."""
    return list(applicants().find({}))


# ─────────────────────────────────────────────────────────────────────────────
#  ACADEMIC RECORD COLLECTION
# ─────────────────────────────────────────────────────────────────────────────

def create_academic_record(applicant_id, course_applied, utme_score,
                           utme_score_claimed, jamb_doc_path,
                           jamb_ocr_verified, jamb_ocr_raw_text,
                           o_level_math, o_level_english,
                           o_level_subject_1, o_level_grade_1,
                           o_level_subject_2, o_level_grade_2,
                           o_level_subject_3, o_level_grade_3):
    """Insert an academic record for an applicant."""
    doc = {
        'applicant_id':       applicant_id,
        'course_applied':     course_applied,
        'utme_score':         utme_score,
        'utme_score_claimed': utme_score_claimed,
        'jamb_document_path': jamb_doc_path,
        'jamb_ocr_verified':  jamb_ocr_verified,
        'jamb_ocr_raw_text':  jamb_ocr_raw_text,
        'o_level_math':       o_level_math.upper() if o_level_math else '',
        'o_level_english':    o_level_english.upper() if o_level_english else '',
        'o_level_subject_1':  o_level_subject_1,
        'o_level_grade_1':    o_level_grade_1.upper() if o_level_grade_1 else '',
        'o_level_subject_2':  o_level_subject_2,
        'o_level_grade_2':    o_level_grade_2.upper() if o_level_grade_2 else '',
        'o_level_subject_3':  o_level_subject_3,
        'o_level_grade_3':    o_level_grade_3.upper() if o_level_grade_3 else '',
        'created_at':         _now()
    }
    result = academic_records().insert_one(doc)
    return str(result.inserted_id)


def find_academic_record(applicant_id):
    """Return the academic record for an applicant, or None."""
    return academic_records().find_one({'applicant_id': applicant_id})


# ─────────────────────────────────────────────────────────────────────────────
#  UPLOADED DOCUMENT COLLECTION
# ─────────────────────────────────────────────────────────────────────────────

def create_uploaded_document(applicant_id, document_type, file_path,
                             ocr_extracted_text, is_verified):
    """Insert an uploaded document record."""
    doc = {
        'applicant_id':       applicant_id,
        'document_type':      document_type,   # 'JAMB_RESULT' | 'O_LEVEL_RESULT'
        'file_path':          file_path,
        'ocr_extracted_text': ocr_extracted_text,
        'is_verified':        is_verified,
        'created_at':         _now()
    }
    result = uploaded_documents().insert_one(doc)
    return str(result.inserted_id)


def find_documents_by_applicant(applicant_id):
    """Return all uploaded documents for an applicant."""
    return list(uploaded_documents().find({'applicant_id': applicant_id}))


# ─────────────────────────────────────────────────────────────────────────────
#  SCREENING RESULT COLLECTION
# ─────────────────────────────────────────────────────────────────────────────

def create_screening_result(applicant_id, passed_institutional,
                            passed_departmental, recommended_alternative, status):
    """Insert or replace the screening result for an applicant."""
    doc = {
        'applicant_id':                  applicant_id,
        'passed_institutional':          passed_institutional,
        'passed_departmental':           passed_departmental,
        'recommended_alternative_course': recommended_alternative,
        'status':                        status,   # PENDING | QUALIFIED | BORDERLINE | REJECTED
        'created_at':                    _now()
    }
    result = screening_results().insert_one(doc)
    return str(result.inserted_id)


def find_screening_result(applicant_id):
    """Return the screening result for an applicant."""
    return screening_results().find_one({'applicant_id': applicant_id})


# ─────────────────────────────────────────────────────────────────────────────
#  ML RESULT COLLECTION
# ─────────────────────────────────────────────────────────────────────────────

def create_ml_result(applicant_id, predicted_outcome, confidence_score):
    """Insert the ML prediction result for an applicant."""
    doc = {
        'applicant_id':     applicant_id,
        'predicted_outcome': predicted_outcome,   # QUALIFIED | BORDERLINE | REJECTED | ALTERNATIVE_COURSE
        'confidence_score':  confidence_score,
        'created_at':        _now()
    }
    result = ml_results().insert_one(doc)
    return str(result.inserted_id)


def find_ml_result(applicant_id):
    """Return the ML result for an applicant."""
    return ml_results().find_one({'applicant_id': applicant_id})


# ─────────────────────────────────────────────────────────────────────────────
#  ADMIN APPROVAL COLLECTION
# ─────────────────────────────────────────────────────────────────────────────

def upsert_admin_approval(applicant_id, admin_id, decision, remarks):
    """Insert or update the admin approval for an applicant."""
    doc = {
        'applicant_id': applicant_id,
        'admin_id':     admin_id,
        'decision':     decision,   # APPROVED | REJECTED
        'remarks':      remarks,
        'decision_date': _now()
    }
    admin_approvals().update_one(
        {'applicant_id': applicant_id},
        {'$set': doc},
        upsert=True
    )


def find_admin_approval(applicant_id):
    """Return the admin approval for an applicant."""
    return admin_approvals().find_one({'applicant_id': applicant_id})
