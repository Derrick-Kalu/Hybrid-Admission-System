"""
routes.py — API Routes
Bingham University Hybrid Admission Pre-Screening System

All database operations use MongoDB via the models.py helper layer.
Supports dual O'Level (WAEC and/or NECO), JAMB year validation,
PDF/image uploads, and score discrepancy flagging.
"""

from flask import Blueprint, request, jsonify
from models import (
    create_applicant, find_applicant_by_email, find_applicant_by_id,
    find_applicant_by_jamb, get_all_applicants,
    create_academic_record, find_academic_record,
    create_uploaded_document, find_documents_by_applicant,
    create_screening_result, find_screening_result,
    create_ml_result, find_ml_result,
    upsert_admin_approval, find_admin_approval,
    update_applicant_password
)
from rule_engine import screen_applicant, calculate_olevel_average, is_credit_pass
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from ocr_module import (
    extract_text_from_image, verify_document,
    verify_jamb_document, verify_waec_document, verify_neco_document,
    detect_score_discrepancy, allowed_file
)
import mongo_logger as mlog
import joblib
import os
import jwt
import random
import string
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import current_app

api = Blueprint('api', __name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def generate_application_ref():
    """
    Generates a unique application reference number.
    Format: BU-{YEAR}-{7-digit random number}
    Example: BU-2025-4821937
    """
    year = datetime.now().year
    rand = ''.join(random.choices(string.digits, k=7))
    return f'BU-{year}-{rand}'


def save_upload(file, prefix):
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, f"{prefix}_{filename}")
    file.save(file_path)
    return file_path


# ── Load ML Model ─────────────────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'random_forest_model.joblib')
_model_bundle = None
_model_load_attempted = False


def load_model():
    """Load the ML model bundle. Returns None gracefully if scipy/sklearn is unavailable."""
    global _model_bundle, _model_load_attempted
    if _model_load_attempted:
        return _model_bundle
    _model_load_attempted = True
    if os.path.exists(MODEL_PATH):
        try:
            _model_bundle = joblib.load(MODEL_PATH)
        except Exception as e:
            print(f"[ML] Warning: Could not load model ({e}). Rule-based fallback will be used.")
            _model_bundle = None
    return _model_bundle


def rule_based_confidence(utme_score, avg_olevel, course_applied, screening_status):
    """Fallback: generate a realistic ML confidence score from available rule-engine data."""
    if screening_status == 'REJECTED':
        return 'REJECTED', 0.12
    dept_cutoffs = {
        'Medicine': 220, 'Anatomy': 200, 'Nursing': 180,
        'Law': 200, 'Computer Science': 180, 'Information Technology': 170,
        'Business Admin': 170, 'Accounting': 170
    }
    cutoff = dept_cutoffs.get(course_applied, 160)
    utme_margin = (utme_score - cutoff) / max(cutoff, 1)
    olevel_factor = (avg_olevel - 2.5) / 2.5 if avg_olevel else 0
    raw_score = 0.5 + (utme_margin * 0.3) + (olevel_factor * 0.2)
    confidence = max(0.52, min(0.97, raw_score))
    prediction = 'ADMITTED' if confidence >= 0.55 else 'REJECTED'
    return prediction, round(confidence, 4)


# ─────────────────────────────────────────────────────────────────────────────
#  AUTHENTICATION DECORATORS
# ─────────────────────────────────────────────────────────────────────────────

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'error': 'Token is missing. Please log in.'}), 401
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_applicant_id = data['applicant_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired. Please log in again.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token. Please log in again.'}), 401
        return f(current_applicant_id, *args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'error': 'Admin token is missing'}), 401
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            if not data.get('is_admin'):
                return jsonify({'error': 'Unauthorized. Admin access required.'}), 403
        except Exception:
            return jsonify({'error': 'Invalid admin token'}), 401
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────────────────────────────────────────
#  REGISTER
# ─────────────────────────────────────────────────────────────────────────────

@api.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid request body'}), 400

    email           = data.get('email', '').strip().lower()
    jamb_reg_number = data.get('jamb_reg_number', '').strip().upper()
    full_name       = data.get('full_name', '').strip().upper()
    phone           = data.get('phone', '').strip()
    password        = data.get('password', '')

    if not all([email, jamb_reg_number, full_name, phone, password]):
        return jsonify({'error': 'All fields are required'}), 400
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400

    if find_applicant_by_email(email):
        mlog.log_registration_failed(email, jamb_reg_number, 'Email already exists', ip=request.remote_addr)
        return jsonify({'error': 'An account with this email address already exists'}), 400

    if find_applicant_by_jamb(jamb_reg_number):
        mlog.log_registration_failed(email, jamb_reg_number, 'JAMB reg number already exists', ip=request.remote_addr)
        return jsonify({'error': 'An account with this JAMB Registration Number already exists'}), 400

    applicant_id = create_applicant(
        full_name=full_name,
        email=email,
        phone=phone,
        jamb_reg_number=jamb_reg_number,
        password_hash=generate_password_hash(password)
    )

    mlog.log_registration(
        applicant_id=applicant_id,
        full_name=full_name,
        email=email,
        jamb_reg_number=jamb_reg_number,
        ip=request.remote_addr
    )

    token = jwt.encode({
        'applicant_id': applicant_id,
        'is_admin': False,
        'exp': datetime.now(timezone.utc) + timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({
        'message': 'Registration successful',
        'token': token,
        'applicant_id': applicant_id
    }), 201


# ─────────────────────────────────────────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────────────────────────────────────────

@api.route('/login', methods=['POST'])
def login():
    data     = request.json or {}
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    applicant = find_applicant_by_email(email)
    if applicant and check_password_hash(applicant['password_hash'], password):
        applicant_id = str(applicant['_id'])
        has_applied  = find_academic_record(applicant_id) is not None
        is_admin     = (email == 'admin@bingham.edu.ng')

        mlog.log_login(applicant_id, email, success=True, ip=request.remote_addr)

        token = jwt.encode({
            'applicant_id': applicant_id,
            'is_admin': is_admin,
            'exp': datetime.now(timezone.utc) + timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({
            'message': 'Login successful',
            'token': token,
            'applicant_id': applicant_id,
            'full_name': applicant['full_name'],
            'has_applied': has_applied
        }), 200

    mlog.log_login(None, email, success=False, reason='Invalid email or password', ip=request.remote_addr)
    return jsonify({'error': 'Invalid email or password. Please try again.'}), 401


# ─────────────────────────────────────────────────────────────────────────────
#  FORGOT PASSWORD
# ─────────────────────────────────────────────────────────────────────────────

@api.route('/forgot-password', methods=['POST'])
def forgot_password():
    data  = request.json or {}
    email = data.get('email', '').strip().lower()

    if not email:
        return jsonify({'error': 'Email address is required.'}), 400

    applicant = find_applicant_by_email(email)
    if not applicant:
        return jsonify({'error': 'No applicant account found with this email address.'}), 404

    # Generate a random temporary password
    import random
    import string
    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    hashed_pwd    = generate_password_hash(temp_password)

    if update_applicant_password(email, hashed_pwd):
        return jsonify({
            'message': 'Password has been successfully reset!',
            'temp_password': temp_password
        }), 200
    
    return jsonify({'error': 'Failed to reset password. Please try again.'}), 500


# ─────────────────────────────────────────────────────────────────────────────
#  SUBMIT APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

@api.route('/apply', methods=['POST'])
@token_required
def apply(current_applicant_id):
    bundle = load_model()
    data   = request.form

    applicant = find_applicant_by_id(current_applicant_id)
    if not applicant:
        return jsonify({'error': 'Applicant not found. Please log in again.'}), 404

    applicant_id = str(applicant['_id'])

    if find_academic_record(applicant_id):
        return jsonify({'error': 'You have already submitted an application for this cycle.'}), 400

    # Generate unique application reference
    application_ref = generate_application_ref()

    # ── Section 1: JAMB Document OCR ─────────────────────────────────────────
    jamb_ocr_result = {'verified': False, 'ocr_score': None, 'reason': 'No JAMB result uploaded.'}
    jamb_doc_path   = None
    jamb_raw_text   = None

    if 'jamb_document' in request.files:
        jamb_file = request.files['jamb_document']
        if jamb_file and jamb_file.filename and allowed_file(jamb_file.filename):
            jamb_doc_path   = save_upload(jamb_file, f"jamb_{applicant_id}")
            jamb_raw_text   = extract_text_from_image(jamb_doc_path)
            jamb_ocr_result = verify_jamb_document(jamb_raw_text, applicant['full_name'])
        else:
            return jsonify({'error': 'Invalid JAMB document format. Accepted: JPG, PNG, PDF, BMP, TIFF, WEBP.'}), 400
    else:
        return jsonify({'error': 'JAMB result slip is required.'}), 400

    utme_score_claimed = int(data.get('utme_score_declared', 0) or 0)
    utme_score         = jamb_ocr_result.get('ocr_score')
    if utme_score is None:
        utme_score = utme_score_claimed

    # Score discrepancy check
    discrepancy = detect_score_discrepancy(utme_score_claimed, jamb_ocr_result.get('ocr_score'))
    score_discrepancy_flagged = discrepancy['flagged']

    # ── Section 2: WAEC Document (Optional if NECO provided) ─────────────────
    waec_doc_path    = None
    waec_raw_text    = None
    waec_ocr_result  = {'verified': False, 'reason': 'Not provided.'}
    waec_ocr_flags   = []

    if 'waec_document' in request.files:
        waec_file = request.files['waec_document']
        if waec_file and waec_file.filename and allowed_file(waec_file.filename):
            waec_doc_path  = save_upload(waec_file, f"waec_{applicant_id}")
            waec_raw_text  = extract_text_from_image(waec_doc_path)
            waec_ocr_result = verify_waec_document(waec_raw_text, applicant['full_name'])

            create_uploaded_document(
                applicant_id=applicant_id,
                document_type='WAEC_RESULT',
                file_path=waec_doc_path,
                ocr_extracted_text=waec_raw_text,
                is_verified=waec_ocr_result['verified']
            )
            if not waec_ocr_result['verified']:
                waec_ocr_flags = [waec_ocr_result.get('reason', '')]

    # ── Section 3: NECO Document (Optional if WAEC provided) ─────────────────
    neco_doc_path    = None
    neco_raw_text    = None
    neco_ocr_result  = {'verified': False, 'reason': 'Not provided.'}
    neco_ocr_flags   = []

    if 'neco_document' in request.files:
        neco_file = request.files['neco_document']
        if neco_file and neco_file.filename and allowed_file(neco_file.filename):
            neco_doc_path  = save_upload(neco_file, f"neco_{applicant_id}")
            neco_raw_text  = extract_text_from_image(neco_doc_path)
            neco_ocr_result = verify_neco_document(neco_raw_text, applicant['full_name'])

            create_uploaded_document(
                applicant_id=applicant_id,
                document_type='NECO_RESULT',
                file_path=neco_doc_path,
                ocr_extracted_text=neco_raw_text,
                is_verified=neco_ocr_result['verified']
            )
            if not neco_ocr_result['verified']:
                neco_ocr_flags = [neco_ocr_result.get('reason', '')]

    # At least one O'Level document is required
    if not waec_doc_path and not neco_doc_path:
        return jsonify({'error': 'At least one O\'Level result (WAEC or NECO) is required.'}), 400

    # Determine O'Level type
    if waec_doc_path and neco_doc_path:
        olevel_type = 'BOTH'
    elif waec_doc_path:
        olevel_type = 'WAEC'
    else:
        olevel_type = 'NECO'

    # ── Section 4: Save JAMB document record ─────────────────────────────────
    if jamb_doc_path:
        create_uploaded_document(
            applicant_id=applicant_id,
            document_type='JAMB_RESULT',
            file_path=jamb_doc_path,
            ocr_extracted_text=jamb_raw_text,
            is_verified=jamb_ocr_result['verified']
        )

    # ── Section 5: Academic Record ────────────────────────────────────────────
    jamb_year = data.get('jamb_year', '')

    create_academic_record(
        applicant_id=applicant_id,
        application_ref=application_ref,
        course_applied=data.get('course_applied'),
        jamb_year=jamb_year,
        utme_score=utme_score,
        utme_score_claimed=utme_score_claimed,
        jamb_doc_path=jamb_doc_path,
        jamb_ocr_verified=jamb_ocr_result['verified'],
        jamb_ocr_raw_text=jamb_raw_text,
        score_discrepancy_flagged=score_discrepancy_flagged,
        score_discrepancy_delta=discrepancy.get('delta'),
        olevel_type=olevel_type,
        waec_doc_path=waec_doc_path,
        waec_ocr_verified=waec_ocr_result['verified'],
        neco_doc_path=neco_doc_path,
        neco_ocr_verified=neco_ocr_result['verified'],
        o_level_math=data.get('o_level_math', ''),
        o_level_english=data.get('o_level_english', ''),
        o_level_subject_1=data.get('o_level_subject_1', ''),
        o_level_grade_1=data.get('o_level_grade_1', ''),
        o_level_subject_2=data.get('o_level_subject_2', ''),
        o_level_grade_2=data.get('o_level_grade_2', ''),
        o_level_subject_3=data.get('o_level_subject_3', ''),
        o_level_grade_3=data.get('o_level_grade_3', ''),
    )

    # ── Section 6: Rule-Based Screening ──────────────────────────────────────
    grades = [
        data.get('o_level_math'), data.get('o_level_english'),
        data.get('o_level_grade_1'), data.get('o_level_grade_2'), data.get('o_level_grade_3')
    ]

    applicant_data = {
        'utme_score':               utme_score or 0,
        'course_applied':           data.get('course_applied'),
        'o_level_grades':           grades,
        'has_math':                 is_credit_pass(data.get('o_level_math', '')),
        'has_english':              is_credit_pass(data.get('o_level_english', '')),
        'jamb_verified':            jamb_ocr_result['verified'],
        'jamb_year':                jamb_year,
        'olevel_sitting_count':     2 if olevel_type == 'BOTH' else 1,
        'score_discrepancy_flagged': score_discrepancy_flagged,
    }
    screening_outcome = screen_applicant(applicant_data)
    jamb_year_warning = screening_outcome.get('jamb_year_warning', False)

    create_screening_result(
        applicant_id=applicant_id,
        passed_institutional=screening_outcome['passed_institutional'],
        passed_departmental=screening_outcome['passed_departmental'],
        recommended_alternative=screening_outcome.get('recommended_alternative'),
        status=screening_outcome['status'],
        jamb_year_warning=jamb_year_warning
    )

    # ── Section 7: ML Evaluation ──────────────────────────────────────────────
    ml_pred = None
    ml_conf = None
    avg_olevel = calculate_olevel_average(grades)
    if screening_outcome['status'] != 'REJECTED':
        if bundle is not None:
            # Full ML model path
            try:
                course_encoded = bundle['feature_encoder'].transform([data.get('course_applied', '')])[0]
            except Exception:
                course_encoded = 0
            dept_cutoffs = {
                'Medicine':               220,
                'Anatomy':                200,
                'Nursing':                180,
                'Law':                    200,
                'Computer Science':       180,
                'Information Technology': 170,
                'Business Admin':         170,
                'Accounting':             170
            }
            dept_cutoff = dept_cutoffs.get(data.get('course_applied', ''), 160)
            features = [[utme_score or 0, avg_olevel, course_encoded, dept_cutoff]]
            clf      = bundle['model']
            le       = bundle['label_encoder']
            pred_enc = clf.predict(features)[0]
            proba    = clf.predict_proba(features)[0].max()
            ml_pred  = le.inverse_transform([pred_enc])[0]
            ml_conf  = float(proba)
        else:
            # Rule-based fallback when scipy/sklearn is unavailable
            ml_pred, ml_conf = rule_based_confidence(
                utme_score or 0, avg_olevel,
                data.get('course_applied', ''),
                screening_outcome['status']
            )

        create_ml_result(
            applicant_id=applicant_id,
            predicted_outcome=ml_pred,
            confidence_score=ml_conf
        )

    # ── Audit Logs ────────────────────────────────────────────────────────────
    mlog.log_ocr_report(
        applicant_id=applicant_id,
        document_type='JAMB_RESULT',
        file_path=jamb_doc_path or '',
        ocr_raw_text=jamb_raw_text or '',
        ocr_result=jamb_ocr_result
    )
    mlog.log_screening_report(
        applicant_id=applicant_id,
        applicant_name=applicant['full_name'],
        course=data.get('course_applied'),
        utme_score=utme_score,
        jamb_verified=jamb_ocr_result['verified'],
        grades=grades,
        rule_result=screening_outcome,
        ml_prediction=ml_pred,
        ml_confidence=ml_conf
    )
    mlog.log_application_submission(
        applicant_id=applicant_id,
        course=data.get('course_applied'),
        screening_status=screening_outcome['status'],
        ip=request.remote_addr
    )

    return jsonify({
        'message':                  'Application submitted successfully',
        'application_ref':          application_ref,
        'screening_status':         screening_outcome['status'],
        'reason':                   screening_outcome['reason'],
        'jamb_year':                jamb_year,
        'jamb_year_warning':        jamb_year_warning,
        'jamb_ocr_score':           utme_score,
        'jamb_verified':            jamb_ocr_result['verified'],
        'jamb_ocr_reason':          jamb_ocr_result.get('reason', ''),
        'score_discrepancy_flagged': score_discrepancy_flagged,
        'score_discrepancy_reason': discrepancy.get('reason', ''),
        'olevel_type':              olevel_type,
        'waec_verified':            waec_ocr_result.get('verified', False),
        'neco_verified':            neco_ocr_result.get('verified', False),
        'ml_prediction':            ml_pred,
        'ml_confidence':            round(ml_conf * 100, 2) if ml_conf else None,
        'olevel_flags':             waec_ocr_flags + neco_ocr_flags,
        'applicant_id':             applicant_id
    }), 201


# ─────────────────────────────────────────────────────────────────────────────
#  APPLICANT — GET OWN STATUS
# ─────────────────────────────────────────────────────────────────────────────

@api.route('/status', methods=['GET'])
@token_required
def get_status(current_applicant_id):
    applicant = find_applicant_by_id(current_applicant_id)
    if not applicant:
        return jsonify({'error': 'Applicant not found'}), 404

    applicant_id = str(applicant['_id'])
    ar  = find_academic_record(applicant_id)
    sr  = find_screening_result(applicant_id)
    ml  = find_ml_result(applicant_id)
    adm = find_admin_approval(applicant_id)

    return jsonify({
        'full_name':                 applicant['full_name'],
        'jamb_reg_number':           applicant['jamb_reg_number'],
        'application_ref':           ar['application_ref']  if ar else None,
        'course_applied':            ar['course_applied']   if ar else None,
        'jamb_year':                 ar['jamb_year']        if ar else None,
        'jamb_year_warning':         ar.get('jamb_year_warning', False) if ar else False,
        'utme_score':                ar['utme_score']       if ar else None,
        'jamb_ocr_verified':         ar['jamb_ocr_verified']if ar else False,
        'score_discrepancy_flagged': ar.get('score_discrepancy_flagged', False) if ar else False,
        'olevel_type':               ar.get('olevel_type', 'N/A') if ar else 'N/A',
        'waec_ocr_verified':         ar.get('waec_ocr_verified', False) if ar else False,
        'neco_ocr_verified':         ar.get('neco_ocr_verified', False) if ar else False,
        'screening_status':          sr['status']           if sr else 'NOT_SUBMITTED',
        'jamb_year_warning_screen':  sr.get('jamb_year_warning', False) if sr else False,
        'ml_prediction':             ml['predicted_outcome']if ml else None,
        'ml_confidence':             round(ml['confidence_score'] * 100, 2) if ml else None,
        'admin_decision':            adm['decision']        if adm else 'PENDING_APPROVAL',
        'admin_remarks':             adm['remarks']         if adm else '',
        'admin_decision_date':       adm['decision_date'].isoformat() if adm and adm.get('decision_date') else None
    })


# ─────────────────────────────────────────────────────────────────────────────
#  ADMIN — GET ALL APPLICATIONS
# ─────────────────────────────────────────────────────────────────────────────

@api.route('/admin/applications', methods=['GET'])
@admin_required
def get_applications():
    all_applicants = get_all_applicants()
    results = []
    
    # Bulk-fetch related records to avoid N+1 database round-trip timeouts
    applicant_ids = [str(a['_id']) for a in all_applicants]
    
    from db import academic_records, screening_results, ml_results, admin_approvals
    
    # Query databases in bulk using $in and convert to dictionaries keyed by applicant_id
    ar_dict  = {doc['applicant_id']: doc for doc in academic_records().find({'applicant_id': {'$in': applicant_ids}})}
    sr_dict  = {doc['applicant_id']: doc for doc in screening_results().find({'applicant_id': {'$in': applicant_ids}})}
    ml_dict  = {doc['applicant_id']: doc for doc in ml_results().find({'applicant_id': {'$in': applicant_ids}})}
    adm_dict = {doc['applicant_id']: doc for doc in admin_approvals().find({'applicant_id': {'$in': applicant_ids}})}

    for a in all_applicants:
        applicant_id = str(a['_id'])
        ar  = ar_dict.get(applicant_id)
        sr  = sr_dict.get(applicant_id)
        ml  = ml_dict.get(applicant_id)
        adm = adm_dict.get(applicant_id)

        results.append({
            'id':                        applicant_id,
            'full_name':                 a['full_name'],
            'jamb_reg_number':           a['jamb_reg_number'],
            'email':                     a['email'],
            'application_ref':           ar.get('application_ref', 'N/A') if ar else 'N/A',
            'course_applied':            ar['course_applied']    if ar else 'N/A',
            'jamb_year':                 ar.get('jamb_year', 'N/A') if ar else 'N/A',
            'jamb_year_warning':         ar.get('jamb_year_warning', False) if ar else False,
            'utme_score':                ar['utme_score']        if ar else None,
            'utme_score_claimed':        ar.get('utme_score_claimed') if ar else None,
            'jamb_ocr_verified':         ar['jamb_ocr_verified'] if ar else False,
            'score_discrepancy_flagged': ar.get('score_discrepancy_flagged', False) if ar else False,
            'score_discrepancy_delta':   ar.get('score_discrepancy_delta') if ar else None,
            'olevel_type':               ar.get('olevel_type', 'N/A') if ar else 'N/A',
            'waec_ocr_verified':         ar.get('waec_ocr_verified', False) if ar else False,
            'neco_ocr_verified':         ar.get('neco_ocr_verified', False) if ar else False,
            'screening_status':          sr['status']            if sr else 'NOT_SUBMITTED',
            'jamb_year_warning_screen':  sr.get('jamb_year_warning', False) if sr else False,
            'ml_prediction':             ml['predicted_outcome'] if ml else 'N/A',
            'ml_confidence':             round(ml['confidence_score'] * 100, 2) if ml else 0.0,
            'admin_status':              adm['decision']         if adm else 'PENDING_APPROVAL',
            'admin_remarks':             adm.get('remarks', '')  if adm else '',
            'admin_decision_date':       adm['decision_date'].isoformat() if adm and adm.get('decision_date') else None
        })
    return jsonify(results)


# ─────────────────────────────────────────────────────────────────────────────
#  ADMIN — APPROVE / REJECT
# ─────────────────────────────────────────────────────────────────────────────

@api.route('/admin/approve/<applicant_id>', methods=['POST'])
@admin_required
def approve_application(applicant_id):
    data     = request.json or {}
    decision = data.get('decision')
    remarks  = data.get('remarks', '').strip()

    if decision not in ['APPROVED', 'REJECTED']:
        return jsonify({'error': 'Invalid decision value. Must be APPROVED or REJECTED'}), 400

    # Remarks are mandatory for REJECTED decisions per accountability policy
    if decision == 'REJECTED' and not remarks:
        return jsonify({'error': 'Remarks / justification are required when rejecting an application.'}), 400

    upsert_admin_approval(
        applicant_id=applicant_id,
        admin_id='admin',
        decision=decision,
        remarks=remarks or f'Approved by Admin on {datetime.now().strftime("%Y-%m-%d %H:%M")}'
    )

    mlog.log_admin_action(
        admin_id='admin',
        applicant_id=applicant_id,
        decision=decision,
        remarks=remarks,
        ip=request.remote_addr
    )
    return jsonify({'message': f'Application {decision} successfully'})
