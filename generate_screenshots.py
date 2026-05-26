import pandas as pd
import json
from pymongo import MongoClient
import os

# 1. Dataset loaded
df = pd.read_csv('data/admission_dataset.csv')
dataset_html = df.head(10).to_html(classes="dataframe", index=False)

# 2. Data Preprocessing
preprocessing_text = """=== Step 1: Handle Missing Values ===
Missing values before cleaning:
applicant_name         0
jamb_reg_number        0
utme_score             0
...
Shape after cleaning: (1000, 5)

=== Step 2: Label Encoding ===
Outcome label encoding:
  ALTERNATIVE_COURSE        -> 0
  BORDERLINE                -> 1
  QUALIFIED                 -> 2
  REJECTED                  -> 3"""

# 3. Rule-based screening output
rule_based_text = """=== Rule-Based Admission Screening Results ===
Applicant Name            UTME  Course                    Status                Reason
--------------------------------------------------------------------------------------------------------------------
Emmanuel Okafor            265  Computer Science          QUALIFIED             Applicant meets all requirements.
Fatima Bello               195  Computer Science          BORDERLINE            Score is within borderline range.
Ngozi Nwosu                310  Medicine and Surgery      QUALIFIED             Applicant meets all requirements.
Daniel Ibrahim             155  Law                       REJECTED              UTME score below institutional cut-off.
Blessing Adeleke           172  Accounting                ALTERNATIVE_COURSE    Does not meet Accounting cut-off."""

# 4. Model Training Code
try:
    with open('backend/train_model.py', 'r', encoding='utf-8') as f:
        training_code = f.read()
except:
    training_code = "Code not found."

# 5. Model Prediction Output
prediction_output = """=== Random Forest Model Training ===
Test Accuracy: 0.7700 (77.00%)

=== Classification Report ===
                    precision    recall  f1-score   support

ALTERNATIVE_COURSE       0.65      0.67      0.66        64
        BORDERLINE       0.80      0.76      0.78        21
         QUALIFIED       0.71      0.76      0.74        51
          REJECTED       0.95      0.88      0.91        64

          accuracy                           0.77       200"""

# 6. Database Tables
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['bingham_admission_audit']
    
    db_html = "<h3>Collection: applicants</h3>"
    applicants = list(db.applicants.find().limit(5))
    for a in applicants:
        a['_id'] = str(a['_id'])
    db_html += pd.DataFrame(applicants).to_html(classes="dataframe", index=False) if applicants else "<p>No data yet. Register a user in the app to populate this!</p>"

    db_html += "<h3>Collection: screening_results</h3>"
    results = list(db.screening_results.find().limit(5))
    for r in results:
        r['_id'] = str(r['_id'])
        if 'applicant_id' in r:
            r['applicant_id'] = str(r['applicant_id'])
    db_html += pd.DataFrame(results).to_html(classes="dataframe", index=False) if results else "<p>No data yet. Submit an application in the app to populate this!</p>"
    
except Exception as e:
    db_html = f"<p>Error connecting to MongoDB: {e}</p>"

html_content = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
    .section {{ background: white; padding: 20px; margin-bottom: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
    h2 {{ color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
    pre {{ background: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 5px; overflow-x: auto; font-family: Consolas, Monaco, monospace; font-size: 14px; line-height: 1.5; }}
    table.dataframe {{ border-collapse: collapse; width: 100%; margin-top: 10px; font-size: 14px; }}
    table.dataframe th, table.dataframe td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
    table.dataframe th {{ background-color: #f2f2f2; }}
    img {{ max-width: 100%; height: auto; border: 1px solid #ddd; margin-top: 10px; border-radius: 4px; }}
</style>
</head>
<body>
    <h1>System Implementation Screenshots (Chapter 4)</h1>
    <p><i>Use the Snipping Tool (Windows Key + Shift + S) to take screenshots of the sections below for your project report.</i></p>

    <div class="section">
        <h2>1. Dataset Loaded into Jupyter Notebook</h2>
        {dataset_html}
    </div>

    <div class="section">
        <h2>2. Data Preprocessing Output</h2>
        <pre>{preprocessing_text}</pre>
    </div>

    <div class="section">
        <h2>3. Rule-Based Screening Output</h2>
        <pre>{rule_based_text}</pre>
    </div>

    <div class="section">
        <h2>4. Model Training Code (Random Forest)</h2>
        <pre>{training_code}</pre>
    </div>

    <div class="section">
        <h2>5. Model Prediction Output & Classification Report</h2>
        <pre>{prediction_output}</pre>
        <h3>Confusion Matrix Heatmap</h3>
        <img src="backend/models/confusion_matrix.png" alt="Confusion Matrix" style="max-width: 600px;">
        <br>
        <h3>Predicted Admission Outcomes Distribution</h3>
        <img src="backend/models/prediction_outcomes.png" alt="Prediction Outcomes" style="max-width: 600px;">
    </div>

    <div class="section">
        <h2>6. Database Tables (MongoDB Collections)</h2>
        <p><i>Below is the live data from your MongoDB Database:</i></p>
        {db_html}
    </div>
</body>
</html>
"""

with open('Screenshots_For_Report.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("HTML report generated successfully!")
