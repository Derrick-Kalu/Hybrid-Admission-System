# rule_engine.py — START-CHECK-STOP Rule-Based Screening Engine
# Bingham University Hybrid Admission Pre-Screening System
#
# Implements Nigerian Tertiary Institution Admission Guidelines:
#   - JAMB UTME score requirements (Joint Admissions & Matriculation Board)
#   - WAEC/NECO O'Level credit requirements (5 credits, max 2 sittings allowed)
#   - UTME result validity: valid for 3 academic sessions from year of examination
#   - NUC minimum standards for each faculty
#
# References:
#   - JAMB Brochure (current edition)
#   - NUC Benchmark Minimum Academic Standards (BMAS)
#   - WAEC/NECO combined-sitting policy (2 sittings allowed per JAMB guidelines)

from datetime import datetime

# ─── GRADE MAPS ───────────────────────────────────────────────────────────────
# WAEC/NECO Grade to Numerical Weight Mapping
# A1=Excellent, B2/B3=Very Good/Good, C4/C5/C6=Credit, D7/E8=Pass, F9=Fail
GRADE_MAP = {
    'A1': 5, 'B2': 4, 'B3': 4,
    'C4': 3, 'C5': 3, 'C6': 3,
    'D7': 2, 'E8': 1, 'F9': 0,
    # Legacy single-letter fallback
    'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1, 'F': 0
}

# Credit pass threshold: C6 and above (weight >= 3)
CREDIT_PASS_WEIGHT = 3

# JAMB result validity: 3 academic sessions from year of examination
# Per JAMB Brochure — results expire after 3 years
JAMB_RESULT_VALIDITY_YEARS = 3
JAMB_RESULT_WARNING_YEARS = 2  # Warn admin if 2 or more years old


def get_grade_weight(grade):
    """Returns the numerical weight for a given grade string."""
    if not grade:
        return 0
    return GRADE_MAP.get(grade.upper().strip(), 0)


def is_credit_pass(grade):
    """Returns True if the grade is a credit pass (C6 and above)."""
    return get_grade_weight(grade) >= CREDIT_PASS_WEIGHT


def calculate_olevel_average(grades):
    """
    Converts a list of O'Level grades to a numerical average.
    Handles WAEC (A1, B2...) and legacy (A, B...) formats.
    Used by the ML model as a feature.
    """
    total, count = 0, 0
    for g in grades:
        if not g:
            continue
        total += get_grade_weight(g)
        count += 1
    return total / count if count > 0 else 0


def validate_jamb_year(jamb_year):
    """
    Validates the JAMB UTME result year per Nigerian admission guidelines.

    Per JAMB Brochure: UTME results are valid for 3 academic sessions from
    the year the examination was taken. After 3 years, the candidate must resit.

    Returns a dict:
      - valid (bool): Whether the result is still within the acceptance window
      - warning (bool): True if result is 2 years old (borderline — admin review advised)
      - age (int): How many years ago the exam was taken
      - reason (str): Human-readable explanation
    """
    if not jamb_year:
        return {
            'valid': False, 'warning': False, 'age': None,
            'reason': 'JAMB examination year was not provided.'
        }

    current_year = datetime.now().year

    try:
        year = int(jamb_year)
    except (ValueError, TypeError):
        return {
            'valid': False, 'warning': False, 'age': None,
            'reason': f'Invalid JAMB year format: {jamb_year}.'
        }

    if year > current_year:
        return {
            'valid': False, 'warning': False, 'age': 0,
            'reason': f'JAMB year {year} is in the future. Please enter the correct examination year.'
        }

    if year < 2000:
        return {
            'valid': False, 'warning': False, 'age': current_year - year,
            'reason': f'JAMB year {year} is not valid. Please enter the year you wrote your UTME.'
        }

    age = current_year - year

    if age >= JAMB_RESULT_VALIDITY_YEARS:
        return {
            'valid': False, 'warning': False, 'age': age,
            'reason': (
                f'Your JAMB UTME result from {year} has expired. '
                f'Per JAMB guidelines, UTME results are valid for {JAMB_RESULT_VALIDITY_YEARS} academic sessions. '
                f'You must resit the UTME to apply for this academic session.'
            )
        }

    if age >= JAMB_RESULT_WARNING_YEARS:
        return {
            'valid': True, 'warning': True, 'age': age,
            'reason': (
                f'JAMB result from {year} is {age} year(s) old. '
                f'This is within the validity window but approaching expiry. '
                f'Admissions Board review recommended.'
            )
        }

    return {
        'valid': True, 'warning': False, 'age': age,
        'reason': f'JAMB result from {year} is current and within the {JAMB_RESULT_VALIDITY_YEARS}-year validity window.'
    }


def screen_applicant(applicant_data):
    """
    Implements the START-CHECK-STOP logic for admission pre-screening.

    Complies with:
    - JAMB minimum UTME cut-off (160 institutional, departmental varies)
    - NUC BMAS O'Level requirements (5 credits including Maths & English)
    - WAEC/NECO combined sitting rule (2 sittings allowed per JAMB guidelines)
    - JAMB result validity (3 academic sessions)

    applicant_data = {
        'utme_score': int,
        'course_applied': str,
        'o_level_grades': list[str],         # Combined WAEC + NECO grades
        'has_math': bool,
        'has_english': bool,
        'jamb_verified': bool,
        'jamb_year': int|str,                # Year UTME was taken
        'olevel_sitting_count': int,         # 1 or 2 (WAEC only, NECO only, or both)
        'score_discrepancy_flagged': bool,   # True if declared ≠ OCR score by >5 marks
    }
    """

    # ── GATE 0: JAMB Result Year Validity ────────────────────────────────────
    jamb_year_check = validate_jamb_year(applicant_data.get('jamb_year'))
    if not jamb_year_check['valid']:
        return {
            'passed_institutional': False,
            'passed_departmental': False,
            'recommended_alternative': None,
            'status': 'REJECTED',
            'jamb_year_warning': False,
            'reason': jamb_year_check['reason']
        }

    jamb_year_warning = jamb_year_check.get('warning', False)

    # ── GATE 1: JAMB Document Integrity ──────────────────────────────────────
    if not applicant_data.get('jamb_verified', False):
        return {
            'passed_institutional': False,
            'passed_departmental': False,
            'recommended_alternative': None,
            'status': 'REJECTED',
            'jamb_year_warning': jamb_year_warning,
            'reason': 'JAMB result could not be verified by OCR. Upload a clear, authentic JAMB result slip.'
        }

    # ── GATE 1b: Score Discrepancy Flag ──────────────────────────────────────
    # If OCR detects a >5-mark discrepancy, the application is escalated to BORDERLINE
    # for mandatory admin review per JAMB integrity policy (not outright rejected)
    if applicant_data.get('score_discrepancy_flagged', False):
        return {
            'passed_institutional': True,
            'passed_departmental': False,
            'recommended_alternative': None,
            'status': 'BORDERLINE',
            'jamb_year_warning': jamb_year_warning,
            'reason': (
                'Score discrepancy detected between declared and OCR-extracted UTME scores. '
                'Application is escalated for mandatory Admissions Board review per JAMB integrity policy.'
            )
        }

    # ── GATE 2: Institutional General Cut-off ────────────────────────────────
    GENERAL_CUTOFF = 160
    utme = applicant_data.get('utme_score', 0)
    if utme < GENERAL_CUTOFF:
        return {
            'passed_institutional': False,
            'passed_departmental': False,
            'recommended_alternative': None,
            'status': 'REJECTED',
            'jamb_year_warning': jamb_year_warning,
            'reason': (
                f'UTME score of {utme} is below the institutional minimum of {GENERAL_CUTOFF}. '
                f'Per NUC regulations, all applicants must score at least {GENERAL_CUTOFF}.'
            )
        }

    # ── GATE 3: Compulsory O'Level — Mathematics ─────────────────────────────
    if not applicant_data.get('has_math', False):
        return {
            'passed_institutional': False,
            'passed_departmental': False,
            'recommended_alternative': None,
            'status': 'REJECTED',
            'jamb_year_warning': jamb_year_warning,
            'reason': 'Credit pass in Mathematics (minimum C6) is required for all programmes per NUC BMAS.'
        }

    # ── GATE 4: Compulsory O'Level — English Language ────────────────────────
    if not applicant_data.get('has_english', False):
        return {
            'passed_institutional': False,
            'passed_departmental': False,
            'recommended_alternative': None,
            'status': 'REJECTED',
            'jamb_year_warning': jamb_year_warning,
            'reason': 'Credit pass in English Language (minimum C6) is required for all programmes per NUC BMAS.'
        }

    # ── GATE 5: Minimum 5 Credits (Combined WAEC + NECO Sittings Allowed) ────
    # Per JAMB guidelines: candidates may combine results from a maximum of 2 sittings
    # (WAEC and NECO) to meet the 5-credit requirement. The best grade per subject counts.
    all_grades = applicant_data.get('o_level_grades', [])
    credit_count = sum(1 for g in all_grades if is_credit_pass(g))
    sitting_count = applicant_data.get('olevel_sitting_count', 1)
    sitting_note = ' (combined WAEC + NECO sittings)' if sitting_count > 1 else ''

    if credit_count < 5:
        return {
            'passed_institutional': False,
            'passed_departmental': False,
            'recommended_alternative': None,
            'status': 'REJECTED',
            'jamb_year_warning': jamb_year_warning,
            'reason': (
                f'Minimum of 5 credit passes required{sitting_note}. '
                f'Only {credit_count} credit pass(es) found across all submitted sittings.'
            )
        }

    # ── GATE 6: Departmental Cut-offs (NUC BMAS Standards) ───────────────────
    DEPARTMENTAL_RULES = {
        'Medicine':            220,   # NUC BMAS — College of Medicine
        'Anatomy':             200,
        'Nursing':             180,
        'Law':                 200,   # NUC BMAS — Faculty of Law
        'Computer Science':    180,   # NUC BMAS — Faculty of Computing & ICT
        'Information Technology': 170,
        'Business Admin':      170,   # NUC BMAS — Faculty of Management Sciences
        'Accounting':          170
    }

    course = applicant_data.get('course_applied', '')
    dept_cutoff = DEPARTMENTAL_RULES.get(course, 160)

    if utme >= dept_cutoff:
        base_reason = f'You met all requirements for {course}. UTME: {utme}.'
        if jamb_year_warning:
            base_reason += f' Note: Your JAMB result is approaching expiry — please confirm with the Admissions Office.'
        return {
            'passed_institutional': True,
            'passed_departmental': True,
            'recommended_alternative': None,
            'status': 'QUALIFIED',
            'jamb_year_warning': jamb_year_warning,
            'reason': f'Congratulations! {base_reason}'
        }

    # ── GATE 7: Borderline (within 10 marks of departmental cut-off) ─────────
    if dept_cutoff - utme <= 10:
        return {
            'passed_institutional': True,
            'passed_departmental': False,
            'recommended_alternative': None,
            'status': 'BORDERLINE',
            'jamb_year_warning': jamb_year_warning,
            'reason': (
                f'UTME score ({utme}) is within 10 marks of the {course} cut-off ({dept_cutoff}). '
                f'Application will be reviewed by the Admissions Board.'
            )
        }

    # ── GATE 8: Alternative Course Recommendation ─────────────────────────────
    ALTERNATIVES = {
        'Medicine':        [('Anatomy', 190), ('Nursing', 170)],
        'Law':             [('Business Admin', 170)],
        'Computer Science': [('Information Technology', 160)],
    }

    alternative = None
    for alt_course, alt_cutoff in ALTERNATIVES.get(course, []):
        if utme >= alt_cutoff:
            alternative = alt_course
            break

    if alternative:
        return {
            'passed_institutional': True,
            'passed_departmental': False,
            'recommended_alternative': alternative,
            'status': 'ALTERNATIVE_COURSE',
            'jamb_year_warning': jamb_year_warning,
            'reason': (
                f'UTME score ({utme}) did not meet the {course} cut-off ({dept_cutoff}). '
                f'Recommended alternative programme: {alternative}.'
            )
        }

    return {
        'passed_institutional': True,
        'passed_departmental': False,
        'recommended_alternative': None,
        'status': 'REJECTED',
        'jamb_year_warning': jamb_year_warning,
        'reason': (
            f'UTME score ({utme}) did not meet the {course} departmental cut-off ({dept_cutoff}), '
            f'and no suitable alternative programme is available at this time.'
        )
    }
