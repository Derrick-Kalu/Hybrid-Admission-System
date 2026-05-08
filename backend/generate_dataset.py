"""
generate_dataset.py
Generates a realistic simulated admission dataset for Bingham University
and saves it to ../data/admission_dataset.csv for use in Jupyter Notebook.
"""

import pandas as pd
import numpy as np
import os
import random

np.random.seed(42)
random.seed(42)

NUM_SAMPLES = 1000

COURSES = [
    ("Computer Science",       200, ["Mathematics", "Physics"]),
    ("Medicine and Surgery",   280, ["Biology", "Chemistry"]),
    ("Law",                    220, ["Literature", "Government"]),
    ("Accounting",             200, ["Mathematics", "Economics"]),
    ("Civil Engineering",      210, ["Mathematics", "Physics"]),
    ("Nursing Science",        200, ["Biology", "Chemistry"]),
    ("Mass Communication",     180, ["English Language", "Literature"]),
    ("Business Administration",180, ["Economics", "Commerce"]),
    ("Economics",              190, ["Mathematics", "Economics"]),
    ("Architecture",           200, ["Mathematics", "Fine Art"]),
]

GRADES = ['A1', 'B2', 'B3', 'C4', 'C5', 'C6', 'D7', 'E8', 'F9']
GRADE_WEIGHTS = {
    'A1': 5, 'B2': 4, 'B3': 4, 'C4': 3, 'C5': 3, 'C6': 3,
    'D7': 2, 'E8': 1, 'F9': 0
}
GRADE_PROBS = [0.10, 0.15, 0.15, 0.20, 0.15, 0.10, 0.07, 0.05, 0.03]

FIRST_NAMES = [
    "Emmanuel", "Blessing", "Chukwuemeka", "Amaka", "Oluwaseun",
    "Fatima", "Ibrahim", "Grace", "Daniel", "Josephine",
    "Victor", "Ngozi", "Solomon", "Adaeze", "Tunde",
    "Chioma", "Kelvin", "Aisha", "Peter", "Funmilayo"
]
LAST_NAMES = [
    "Okafor", "Adeyemi", "Nwosu", "Bello", "Eze",
    "Abubakar", "Okonkwo", "Ibrahim", "Chukwu", "Adeleke",
    "Ogundele", "Musa", "Anyanwu", "Olawale", "Nzekwe"
]

def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def random_jamb_reg():
    year = 2025
    digits = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    suffix = random.choice(['CF', 'EG', 'FG', 'HJ'])
    return f"{year}{digits}{suffix}"

def random_grade(mean_weight=3.5):
    """Returns a grade string biased around mean_weight."""
    return random.choices(GRADES, weights=GRADE_PROBS)[0]

def grade_weight(grade):
    return GRADE_WEIGHTS.get(grade, 0)

rows = []

for i in range(NUM_SAMPLES):
    # Pick a course
    course_name, dept_cutoff, req_subjects = random.choice(COURSES)

    # Simulate UTME score (normal distribution, clipped)
    utme = int(np.clip(np.random.normal(loc=210, scale=35), 120, 320))

    # Simulate 5 O'Level grades (Maths, English, + 3 subjects)
    grades = [random_grade() for _ in range(5)]
    math_grade, english_grade = grades[0], grades[1]
    subj_grades = grades[2:]

    # Calculate average O'Level weight (0–5 scale)
    avg_olevel = round(np.mean([grade_weight(g) for g in grades]), 2)

    # Determine outcome using the same logic as the rule engine + ML
    credit_passes = sum(1 for g in grades if grade_weight(g) >= 3)
    has_math_credit = grade_weight(math_grade) >= 3
    has_english_credit = grade_weight(english_grade) >= 3

    if utme >= dept_cutoff and has_math_credit and has_english_credit and credit_passes >= 5:
        outcome = 'QUALIFIED'
    elif 180 <= utme < dept_cutoff and has_math_credit and has_english_credit and credit_passes >= 5:
        outcome = 'BORDERLINE'
    elif utme >= 180 and credit_passes >= 4:
        outcome = 'ALTERNATIVE_COURSE'
    else:
        outcome = 'REJECTED'

    rows.append({
        'applicant_name':       random_name(),
        'jamb_reg_number':      random_jamb_reg(),
        'utme_score':           utme,
        'olevel_math':          math_grade,
        'olevel_english':       english_grade,
        'olevel_subject_1':     req_subjects[0] if len(req_subjects) > 0 else 'Biology',
        'olevel_grade_1':       subj_grades[0],
        'olevel_subject_2':     req_subjects[1] if len(req_subjects) > 1 else 'Chemistry',
        'olevel_grade_2':       subj_grades[1],
        'olevel_subject_3':     'Further Mathematics',
        'olevel_grade_3':       subj_grades[2],
        'olevel_avg_score':     avg_olevel,
        'course_applied':       course_name,
        'departmental_cutoff':  dept_cutoff,
        'outcome':              outcome,
    })

df = pd.DataFrame(rows)

os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'data'), exist_ok=True)
csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'admission_dataset.csv')
df.to_csv(csv_path, index=False)

print(f"[OK] Dataset saved to: {csv_path}")
print(f"     Shape: {df.shape}")
print(f"\nOutcome distribution:")
print(df['outcome'].value_counts())
print(f"\nFirst 5 rows:")
print(df.head())
