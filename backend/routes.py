"""
routes.py — API Routes
Bingham University Hybrid Admission Pre-Screening System

All database operations use MongoDB via the models.py helper layer.
"""

from flask import Blueprint, request, jsonify
from models import (
    create_applicant, find_applicant_by_email, find_applicant_by_id,
    find_applicant_by_jamb, get_all_applicants,
    create_academic_record, find_academic_record,
    create_uploaded_document, find_documents_by_applicant,
    create_screening_result, find_screening_result,
    create_ml_result, find_ml_result,
    upsert_admin_approval, find_admin_approval
)
from rule_engine import screen_applicant, calculate_olevel_average, is_credit_pass
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from ocr_module import extract_text_from_image, verify_document, verify_jamb_document
import mongo_logger as mlog
import joblib
import os
import jwt
from functools import wraps
from flask import current_app
from datetime import datetime, timedelta, timezone

api = Blueprint('api', __name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# ── Load ML Model ─────────────────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'random_forest_model.joblib')
_model_bundle = None


def load_model():
    global _model_bundle
    if _model_bundle is None and os.path.exists(MODEL_PATH):
        _model_bundle = joblib.load(MODEL_PATH)
    return _model_bundle


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(file, prefix):
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, f"{prefix}_{filename}")
    file.save(file_path)
    return file_path


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
        mlog.log_registration_failed(email, jamb_reg_number,
                                     'Email already exists', ip=request.remote_addr)
        return jsonify({'error': 'An account with this email address already exists'}), 400

    if find_applicant_by_jamb(jamb_reg_number):
        mlog.log_registration_failed(email, jamb_reg_number,
                                     'JAMB reg number already exists', ip=request.remote_addr)
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
    data     = request.json
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

    mlog.log_login(None, email, success=False,
                   reason='Invalid email or password', ip=request.remote_addr)
    return jsonify({'error': 'Invalid email or password. Please try again.'}), 401


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
            return jsonify({'error': 'Invalid JAMB document. Only JPG/PNG files are accepted.'}), 400
    else:
        return jsonify({'error': 'JAMB result slip is required.'}), 400

    utme_score         = jamb_ocr_result.get('ocr_score')
    utme_score_claimed = int(data.get('utme_score_declared', 0) or 0)
    if utme_score is None:
        utme_score = utme_score_claimed

    # ── Section 2: O'Level Document ──────────────────────────────────────────
    olevel_ocr_flags = []
    if 'olevel_document' in request.files:
        olevel_file = request.files['olevel_document']
        if olevel_file and olevel_file.filename and allowed_file(olevel_file.filename):
            olevel_doc_path = save_upload(olevel_file, f"olevel_{applicant_id}")
            olevel_text     = extract_text_from_image(olevel_doc_path)
            name_keywords   = [p for p in applicant['full_name'].split() if len(p) > 2]
            olevel_ver      = verify_document(olevel_text, name_keywords[:2])

            create_uploaded_document(
                applicant_id=applicant_id,
                document_type='O_LEVEL_RESULT',
                file_path=olevel_doc_path,
                ocr_extracted_text=olevel_text,
                is_verified=olevel_ver['verified']
            )
            if not olevel_ver['verified']:
                olevel_ocr_flags = olevel_ver.get('missing_keywords', [])

    # ── Section 3: Save JAMB document record ─────────────────────────────────
    if jamb_doc_path:
        create_uploaded_document(
            applicant_id=applicant_id,
            document_type='JAMB_RESULT',
            file_path=jamb_doc_path,
            ocr_extracted_text=jamb_raw_text,
            is_verified=jamb_ocr_result['verified']
        )

    # ── Section 4: Academic Record ────────────────────────────────────────────
    create_academic_record(
        applicant_id=applicant_id,
        course_applied=data.get('course_applied'),
        utme_score=utme_score,
        utme_score_claimed=utme_score_claimed,
        jamb_doc_path=jamb_doc_path,
        jamb_ocr_verified=jamb_ocr_result['verified'],
        jamb_ocr_raw_text=jamb_raw_text,
        o_level_math=data.get('o_level_math', ''),
        o_level_english=data.get('o_level_english', ''),
        o_level_subject_1=data.get('o_level_subject_1', ''),
        o_level_grade_1=data.get('o_level_grade_1', ''),
        o_level_subject_2=data.get('o_level_subject_2', ''),
        o_level_grade_2=data.get('o_level_grade_2', ''),
        o_level_subject_3=data.get('o_level_subject_3', ''),
        o_level_grade_3=data.get('o_level_grade_3', ''),
    )

    # ── Section 5: Rule-Based Screening ──────────────────────────────────────
    grades = [
        data.get('o_level_math'), data.get('o_level_english'),
        data.get('o_level_grade_1'), data.get('o_level_grade_2'), data.get('o_level_grade_3')
    ]
    applicant_data = {
        'utme_score':    utme_score or 0,
        'course_applied': data.get('course_applied'),
        'o_level_grades': grades,
        'has_math':      is_credit_pass(data.get('o_level_math', '')),
        'has_english':   is_credit_pass(data.get('o_level_english', '')),
        'jamb_verified': jamb_ocr_result['verified']
    }
    screening_outcome = screen_applicant(applicant_data)

    create_screening_result(
        applicant_id=applicant_id,
        passed_institutional=screening_outcome['passed_institutional'],
        passed_departmental=screening_outcome['passed_departmental'],
        recommended_alternative=screening_outcome.get('recommended_alternative'),
        status=screening_outcome['status']
    )

    # ── Section 6: ML Evaluation ──────────────────────────────────────────────
    ml_pred = None
    ml_conf = None
    if screening_outcome['status'] != 'REJECTED' and bundle is not None:
        avg_olevel = calculate_olevel_average(grades)
        # Encode course for the model
        try:
            course_encoded = bundle['feature_encoder'].transform([data.get('course_applied', '')])[0]
        except Exception:
            course_encoded = 0
        # Use departmental cutoff lookup or default
        dept_cutoffs = {
            'Computer Science': 200, 'Medicine and Surgery': 280,
            'Law': 220, 'Accounting': 200, 'Civil Engineering': 210,
            'Nursing Science': 200, 'Mass Communication': 180,
            'Business Administration': 180, 'Economics': 190, 'Architecture': 200
        }
        dept_cutoff = dept_cutoffs.get(data.get('course_applied', ''), 180)

        features = [[utme_score or 0, avg_olevel, course_encoded, dept_cutoff]]
        clf      = bundle['model']
        le       = bundle['label_encoder']
        pred_enc = clf.predict(features)[0]
        proba    = clf.predict_proba(features)[0].max()
        ml_pred  = le.inverse_transform([pred_enc])[0]
        ml_conf  = float(proba)

        create_ml_result(
            applicant_id=applicant_id,
            predicted_outcome=ml_pred,
            confidence_score=ml_conf
        )

    # ── Audit logs ────────────────────────────────────────────────────────────
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
        'message':         'Application submitted successfully',
        'screening_status': screening_outcome['status'],
        'reason':          screening_outcome['reason'],
        'jamb_ocr_score':  utme_score,
        'jamb_verified':   jamb_ocr_result['verified'],
        'jamb_ocr_reason': jamb_ocr_result.get('reason', ''),
        'ml_prediction':   ml_pred,
        'ml_confidence':   round(ml_conf * 100, 2) if ml_conf else None,
        'olevel_flags':    olevel_ocr_flags,
        'applicant_id':    applicant_id
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
        'full_name':        applicant['full_name'],
        'jamb_reg_number':  applicant['jamb_reg_number'],
        'course_applied':   ar['course_applied'] if ar else None,
        'utme_score':       ar['utme_score'] if ar else None,
        'jamb_ocr_verified': ar['jamb_ocr_verified'] if ar else False,
        'screening_status': sr['status'] if sr else 'NOT_SUBMITTED',
        'ml_prediction':    ml['predicted_outcome'] if ml else None,
        'ml_confidence':    round(ml['confidence_score'] * 100, 2) if ml else None,
        'admin_decision':   adm['decision'] if adm else 'PENDING_APPROVAL',
        'admin_remarks':    adm['remarks'] if adm else ''
    })


# ─────────────────────────────────────────────────────────────────────────────
#  ADMIN — GET ALL APPLICATIONS
# ─────────────────────────────────────────────────────────────────────────────

@api.route('/admin/applications', methods=['GET'])
@admin_required
def get_applications():
    all_applicants = get_all_applicants()
    results = []
    for a in all_applicants:
        applicant_id = str(a['_id'])
        ar  = find_academic_record(applicant_id)
        sr  = find_screening_result(applicant_id)
        ml  = find_ml_result(applicant_id)
        adm = find_admin_approval(applicant_id)

        results.append({
            'id':              applicant_id,
            'full_name':       a['full_name'],
            'jamb_reg_number': a['jamb_reg_number'],
            'email':           a['email'],
            'course_applied':  ar['course_applied'] if ar else 'N/A',
            'utme_score':      ar['utme_score'] if ar else None,
            'jamb_ocr_verified': ar['jamb_ocr_verified'] if ar else False,
            'screening_status': sr['status'] if sr else 'NOT_SUBMITTED',
            'ml_prediction':   ml['predicted_outcome'] if ml else 'N/A',
            'ml_confidence':   round(ml['confidence_score'] * 100, 2) if ml else 0.0,
            'admin_status':    adm['decision'] if adm else 'PENDING_APPROVAL'
        })
    return jsonify(results)


# ─────────────────────────────────────────────────────────────────────────────
#  ADMIN — APPROVE / REJECT
# ─────────────────────────────────────────────────────────────────────────────

@api.route('/admin/approve/<applicant_id>', methods=['POST'])
@admin_required
def approve_application(applicant_id):
    data     = request.json
    decision = data.get('decision')

    if decision not in ['APPROVED', 'REJECTED']:
        return jsonify({'error': 'Invalid decision value. Must be APPROVED or REJECTED'}), 400

    upsert_admin_approval(
        applicant_id=applicant_id,
        admin_id='admin',
        decision=decision,
        remarks=data.get('remarks', '')
    )

    mlog.log_admin_action(
        admin_id='admin',
        applicant_id=applicant_id,
        decision=decision,
        remarks=data.get('remarks', ''),
        ip=request.remote_addr
    )
    return jsonify({'message': f'Application {decision} successfully'})
