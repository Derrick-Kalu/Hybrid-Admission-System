"""
train_model.py
Hybrid Admission Pre-Screening System — Bingham University
Loads CSV dataset, runs comparative evaluation (Decision Tree, Logistic Regression,
Random Forest), selects the best performer, and serialises with Joblib.
Mirrors the Jupyter Notebook (Model_Training.ipynb) for standalone execution.
"""

import os
import warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')          # non-interactive backend for saving figures
import matplotlib.pyplot as plt
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix, ConfusionMatrixDisplay
)

warnings.filterwarnings('ignore')

# ─── 1. Load Dataset ──────────────────────────────────────────────────────────
CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'admission_dataset.csv')
print("Loading dataset from:", CSV_PATH)
data = pd.read_csv(CSV_PATH)
print(f"Dataset shape: {data.shape}")
print("\nFirst 5 rows:")
print(data.head())
print("\nOutcome distribution:")
print(data['outcome'].value_counts())

# ─── 2. Data Preprocessing ────────────────────────────────────────────────────
print("\n--- Data Preprocessing ---")

# Drop non-feature columns
drop_cols = ['applicant_name', 'jamb_reg_number',
             'olevel_math', 'olevel_english',
             'olevel_subject_1', 'olevel_subject_2', 'olevel_subject_3',
             'olevel_grade_1', 'olevel_grade_2', 'olevel_grade_3']
data_clean = data.drop(columns=[c for c in drop_cols if c in data.columns])

# Handle missing values
data_clean = data_clean.dropna()
print(f"Shape after dropping missing values: {data_clean.shape}")

# Label encode 'course_applied'
le_course = LabelEncoder()
data_clean['course_applied'] = le_course.fit_transform(data_clean['course_applied'])

# Label encode target
le_outcome = LabelEncoder()
data_clean['outcome_encoded'] = le_outcome.fit_transform(data_clean['outcome'])
print("\nLabel encoding mapping (outcome):")
for cls, idx in zip(le_outcome.classes_, le_outcome.transform(le_outcome.classes_)):
    print(f"  {cls} -> {idx}")

# ─── 3. Feature Selection & Splitting ────────────────────────────────────────
FEATURES = ['utme_score', 'olevel_avg_score', 'course_applied', 'departmental_cutoff']
X = data_clean[FEATURES]
y = data_clean['outcome_encoded']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\nTraining set size : {len(X_train)} samples (80%)")
print(f"Testing  set size : {len(X_test)} samples (20%)")

# ─── 4. Comparative Evaluation ───────────────────────────────────────────────
print("\n--- Comparative Model Evaluation ---")
models = {
    'Decision Tree':      DecisionTreeClassifier(max_depth=6, random_state=42),
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
    'Random Forest':      RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42),
}

results = {}
for name, model in models.items():
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    results[name] = acc
    print(f"  {name:25s} -> Accuracy: {acc:.4f} ({acc*100:.2f}%)")

best_name = max(results, key=results.get)
print(f"\nBest model: {best_name} (Accuracy: {results[best_name]*100:.2f}%)")

# ─── 5. Train Best Model (Random Forest) ─────────────────────────────────────
clf = models[best_name]
# Already fitted above; re-use predictions
y_pred = clf.predict(X_test)
class_names = le_outcome.classes_

print("\n--- Classification Report ---")
print(classification_report(y_test, y_pred, target_names=class_names))

# ─── 6. Confusion Matrix ─────────────────────────────────────────────────────
os.makedirs('models', exist_ok=True)

cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
fig, ax = plt.subplots(figsize=(8, 6))
disp.plot(ax=ax, cmap='Blues', colorbar=False)
ax.set_title('Confusion Matrix — Random Forest Classifier')
plt.tight_layout()
plt.savefig('models/confusion_matrix.png', dpi=150)
plt.close()
print("Confusion matrix saved to models/confusion_matrix.png")

# ─── 7. Prediction Outcomes Bar Chart ────────────────────────────────────────
outcome_counts = pd.Series(
    le_outcome.inverse_transform(y_pred)
).value_counts()

colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444']
fig2, ax2 = plt.subplots(figsize=(8, 5))
outcome_counts.plot(kind='bar', ax=ax2, color=colors[:len(outcome_counts)])
ax2.set_title('Predicted Admission Outcomes Distribution')
ax2.set_xlabel('Admission Status')
ax2.set_ylabel('Number of Applicants')
ax2.tick_params(axis='x', rotation=15)
plt.tight_layout()
plt.savefig('models/prediction_outcomes.png', dpi=150)
plt.close()
print("Bar chart saved to models/prediction_outcomes.png")

# ─── 8. Comparative Accuracy Bar Chart ───────────────────────────────────────
fig3, ax3 = plt.subplots(figsize=(7, 4))
bars = ax3.bar(results.keys(), [v * 100 for v in results.values()],
               color=['#94a3b8', '#94a3b8', '#3b82f6'])
ax3.set_ylabel('Accuracy (%)')
ax3.set_title('Comparative Model Evaluation')
ax3.set_ylim(0, 105)
for bar, acc in zip(bars, results.values()):
    ax3.text(bar.get_x() + bar.get_width() / 2,
             bar.get_height() + 0.5,
             f'{acc*100:.1f}%', ha='center', fontsize=10)
plt.tight_layout()
plt.savefig('models/model_comparison.png', dpi=150)
plt.close()
print("Comparison chart saved to models/model_comparison.png")

# ─── 9. Serialise Model with Joblib ──────────────────────────────────────────
model_path = 'models/random_forest_model.joblib'
joblib.dump({'model': clf, 'label_encoder': le_outcome, 'feature_encoder': le_course}, model_path)
print(f"\nModel serialised with Joblib -> {model_path}")
print("\nTraining complete.")