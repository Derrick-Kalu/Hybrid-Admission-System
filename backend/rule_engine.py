# Rule-Based Engine implementing START-CHECK-STOP Logic

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
    Converts a list of O'Level grades (e.g., ['A1', 'B2', 'C4']) to a numerical average.
    Handles both new (A1, B2...) and legacy (A, B...) formats.
    """
    total = 0
    count = 0
    for g in grades:
        if not g:
            continue
        w = get_grade_weight(g)
        total += w
        count += 1
    return total / count if count > 0 else 0

def screen_applicant(applicant_data):
    """
    Implements the START-CHECK-STOP logic.

    applicant_data = {
        'utme_score': int,               # OCR-extracted or fallback score
        'course_applied': str,
        'o_level_grades': list of str,   # e.g., ['A1', 'B2', 'C4', 'C5', 'C6']
        'has_math': bool,                # Math grade is a credit pass
        'has_english': bool,             # English grade is a credit pass
        'jamb_verified': bool,           # True if JAMB OCR verification passed
    }
    """

    # ── GATE 0: JAMB Document Integrity ──────────────────────────────────────
    if not applicant_data.get('jamb_verified', False):
        return {
            'passed_institutional': False,
            'passed_departmental': False,
            'recommended_alternative': None,
            'status': 'REJECTED',
            'reason': 'JAMB result could not be verified. Ensure you upload a clear, authentic JAMB result slip.'
        }

    # ── GATE 1: Institutional General Cut-off ────────────────────────────────
    GENERAL_CUTOFF = 160
    if applicant_data['utme_score'] < GENERAL_CUTOFF:
        return {
            'passed_institutional': False,
            'passed_departmental': False,
            'recommended_alternative': None,
            'status': 'REJECTED',
            'reason': f"UTME score of {applicant_data['utme_score']} is below the institutional minimum of {GENERAL_CUTOFF}."
        }

    # ── GATE 2: Compulsory O'Level Requirements ──────────────────────────────
    if not applicant_data['has_math']:
        return {
            'passed_institutional': False,
            'passed_departmental': False,
            'recommended_alternative': None,
            'status': 'REJECTED',
            'reason': 'Credit pass in Mathematics (C6 or above) is required for all programmes.'
        }

    if not applicant_data['has_english']:
        return {
            'passed_institutional': False,
            'passed_departmental': False,
            'recommended_alternative': None,
            'status': 'REJECTED',
            'reason': 'Credit pass in English Language (C6 or above) is required for all programmes.'
        }

    # ── GATE 3: Minimum 5 Credits Check ─────────────────────────────────────
    all_grades = applicant_data.get('o_level_grades', [])
    credit_count = sum(1 for g in all_grades if is_credit_pass(g))
    if credit_count < 5:
        return {
            'passed_institutional': False,
            'passed_departmental': False,
            'recommended_alternative': None,
            'status': 'REJECTED',
            'reason': f'Minimum of 5 credit passes required. Only {credit_count} credit pass(es) found.'
        }

    # ── GATE 4: Departmental Cut-offs ────────────────────────────────────────
    DEPARTMENTAL_RULES = {
        'Medicine': 220,
        'Anatomy': 200,
        'Nursing': 180,
        'Law': 200,
        'Computer Science': 180,
        'Information Technology': 170,
        'Business Admin': 170,
        'Accounting': 170
    }

    course = applicant_data['course_applied']
    dept_cutoff = DEPARTMENTAL_RULES.get(course, 160)
    utme = applicant_data['utme_score']

    if utme >= dept_cutoff:
        return {
            'passed_institutional': True,
            'passed_departmental': True,
            'recommended_alternative': None,
            'status': 'QUALIFIED',
            'reason': f"Congratulations! You met all requirements for {course}. UTME: {utme}."
        }

    # ── GATE 5: Borderline Check (within 10 marks of cutoff) ─────────────────
    if dept_cutoff - utme <= 10:
        return {
            'passed_institutional': True,
            'passed_departmental': False,
            'recommended_alternative': None,
            'status': 'BORDERLINE',
            'reason': f"UTME score ({utme}) is within 10 marks of the {course} cut-off ({dept_cutoff}). Application will be reviewed by the Admissions Board."
        }

    # ── GATE 6: Alternative Course Recommendation ─────────────────────────────
    ALTERNATIVES = {
        'Medicine':  [('Anatomy', 190), ('Nursing', 170)],
        'Law':       [('Business Admin', 170)],
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
            'reason': f"UTME score ({utme}) did not meet the {course} cut-off ({dept_cutoff}). Recommended alternative: {alternative}."
        }

    return {
        'passed_institutional': True,
        'passed_departmental': False,
        'recommended_alternative': None,
        'status': 'REJECTED',
        'reason': f"UTME score ({utme}) did not meet the {course} departmental cut-off ({dept_cutoff}), and no suitable alternative programme is available."
    }
