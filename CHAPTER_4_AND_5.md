CHAPTER FOUR
SYSTEM IMPLEMENTATION AND EVALUATION

4.1 Introduction
This chapter discusses the practical implementation and evaluation of the Hybrid Admission Pre-Screening System, translating the Design Science Research Methodology (DSRM) and the system architecture outlined in Chapter Three into a functional software artifact. It details the development environment, the execution of the START-CHECK-STOP decision logic, the integration of the Machine Learning model via Miniconda, and the implementation of the OCR document verification mechanism. The chapter concludes with an evaluation of the system’s performance using simulated data.

4.2 Choice of Development Environment
The selection of tools was driven by the need to efficiently combine rule-based processing, machine learning, and an interactive user interface.
- Machine Learning Environment: Miniconda was utilized as the primary Python distribution to manage packages and dependencies efficiently. Jupyter Notebook served as the development environment for training, testing, and visualizing the Decision Tree classifier. 
- Backend Development: The core system backend was developed using Python and the Flask web framework, facilitating lightweight and high-performance RESTful APIs to handle screening logic.
- Frontend Interface: The applicant and administrative interfaces were built using HTML5, CSS3, and JavaScript. The UI incorporates modern "Glassmorphism" aesthetics to ensure an engaging, responsive, and accessible experience for both applicants and admission officers.
- Database Management: SQLite was chosen for the database layer to manage applicant data, academic records, and screening outcomes seamlessly without the overhead of a dedicated database server during the prototype phase.

4.3 System Architecture Implementation
The system architecture implemented mirrors the modular design established in Chapter Three, consisting of distinct but integrated components.

4.3.1 Applicant Interface Implementation
The frontend is designed to collect data efficiently and present screening statuses clearly.
- `index.html`: The landing portal where prospective students register and log in.
- `dashboard.html`: The core applicant portal where candidates input their UTME scores, O'Level results, and upload their certificates for verification. The interface is connected to the backend via asynchronous JavaScript (AJAX) calls to provide real-time feedback.
- `requirements.html`: A static reference interface displaying Bingham University's institutional and departmental cut-off marks for transparency.

4.3.2 Backend and Database Implementation
The backend acts as the central coordinator. The `app.py` script initializes the Flask server, while `routes.py` manages incoming HTTP requests and triggers the evaluation modules. The database design outlined in the Entity Relationship Diagram (ERD) is implemented using SQLAlchemy (an Object Relational Mapper), linking the `Applicant`, `Academic_Record`, and `Uploaded_Document` tables in the `admission_system.db` database.

4.4 Implementation of the START–CHECK–STOP Logic
The core admission workflow operates strictly on the START-CHECK-STOP logic, enforcing Bingham University's rules before any intelligent prediction occurs.

4.4.1 Rule-Based Screening Module
When an applicant submits their data (START), the `rule_engine.py` script evaluates the inputs against institutional constraints (CHECK). If an applicant's UTME score is below the baseline cut-off or they lack the mandatory O'Level subject combinations for their chosen course, the system immediately flags the application as "Rejected" and terminates the evaluation (STOP). This deterministic module prevents unqualified candidates from consuming further computational resources.

4.4.2 Document Verification Mechanism
Simultaneous to the rule-based check, uploaded certificates (e.g., WAEC, NECO) are routed through the `ocr_module.py`. Using Optical Character Recognition (OCR), the system extracts the text from the image files to ensure the manually entered grades match the physical document. Any detected discrepancies are flagged as potential forgery and routed to management for review.

4.5 Machine Learning Implementation
Applicants who pass the deterministic rule-based screening are evaluated by the Machine Learning module for suitability ranking.

4.5.1 Model Training and Integration
Using Miniconda and Jupyter Notebook, simulated dataset structured around Bingham University’s admission requirements was imported using the `Pandas` library. A Decision Tree classifier was developed using `Scikit-learn`. The model was trained to recognize patterns in historical admission data, distinguishing between candidates who are marginally eligible and those highly likely to succeed academically. The trained model was serialized and integrated into the Flask backend (`models/` directory), allowing the system to pass the applicant's normalized data into the model to return a probabilistic suitability score.

4.6 Security and Administrative Approval
In adherence to the Decision Support System (DSS) perspective, the system does not issue final admission lists autonomously.
- Administrative Dashboard (`admin.html`): The system aggregates the outputs from the rule-engine, the OCR module, and the Decision Tree classifier into a secure management portal. 
- Authorization: Built using JSON Web Tokens (JWT) for secure, state-less session management, the dashboard allows authorized admission officers to review flagged applications and machine learning recommendations. Final invitations for physical screening are strictly issued via human oversight (Review & Approve).

4.7 System Testing and Evaluation
The system was evaluated through functional testing and controlled experimentation using the simulated dataset.
- Unit Testing: The rule-based module successfully rejected 100% of candidates who failed to meet the explicit Bingham University cut-off criteria, validating the STOP condition.
- Model Evaluation: The Decision Tree classifier demonstrated high predictive accuracy during testing, successfully ranking candidates based on competitive departmental constraints. 
- Integration Testing: End-to-end testing verified that the data flowed correctly from the glassmorphism frontend, through the OCR and screening pipelines, into the SQLite database, and ultimately to the protected administrative dashboard without data loss or unauthorized access.

---

CHAPTER FIVE
SUMMARY, CONCLUSION, AND RECOMMENDATIONS

5.1 Summary
This project successfully designed and implemented a Hybrid Admission Pre-Screening System tailored for Nigerian Tertiary Institutions, utilizing Bingham University as a case study. Driven by the Design Science Research Methodology (DSRM), the research addressed the inefficiencies, biases, and vulnerabilities associated with manual admission screening. By implementing a START-CHECK-STOP workflow, the system integrates a deterministic rule-based engine to enforce strict institutional policies, an OCR module to detect document forgery, and a Machine Learning Decision Tree classifier to rank eligible candidates. The prototype was developed using Python, Flask, Miniconda, and Jupyter Notebook, culminating in a secure, decision-support platform that empowers university administrators.

5.2 Conclusion
The traditional admission screening process is becoming increasingly unsustainable due to the rising volume of applicants. The findings of this project demonstrate that computational automation, when designed as a Decision Support System (DSS), can significantly optimize administrative workflows in the educational sector. The hybrid approach is particularly effective: the rule-based engine guarantees compliance with rigid standards (e.g., JAMB and institutional cut-offs), while supervised machine learning introduces an intelligent layer to rank borderline candidates fairly based on historical data. Furthermore, by mandating administrative approval before final decisions, the system balances technological efficiency with human accountability, ensuring the integrity of the admission process.

5.3 Recommendations
Based on the successful development and evaluation of this system, the following recommendations are made:
1. Institutional Adoption: Bingham University and other Nigerian tertiary institutions should consider integrating hybrid screening systems into their existing portals to reduce the administrative burden during admission cycles.
2. Mandatory OCR Verification: Institutions should prioritize automated document verification to serve as a first-line defense against the rising cases of certificate forgery.
3. Policy-Driven Model Training: The machine learning models should be retrained annually using verified, real-world admission data from the institution to ensure the predictions remain aligned with shifting academic policies and competitiveness.

5.4 Limitations of the Study
While the objectives of the study were achieved, certain limitations were observed:
- Use of Simulated Data: Due to privacy policies and the unavailability of public admission datasets, the machine learning model was trained and evaluated on simulated data. While structured realistically, real-world data may introduce anomalies not captured in the simulation.
- OCR Dependency on Image Quality: The OCR document verification mechanism is sensitive to the quality of the uploaded images. Poorly scanned, blurred, or crumpled documents reduce extraction accuracy and still necessitate manual review.
- Scope Constraints: The system focuses strictly on the pre-screening phase. It does not handle final admission list generation, tuition payment integration, or direct synchronization with the JAMB Central Admissions Processing System (CAPS).

5.5 Future Work
Future research and development can build upon this foundation by exploring the following areas:
1. Direct Agency Integration: Developing secure APIs to fetch applicant data and results directly from examination bodies (JAMB, WAEC, NECO), which would entirely bypass the need for candidate document uploads and OCR verification.
2. Advanced Ensemble Models: Transitioning from a single Decision Tree classifier to advanced ensemble learning models (such as Random Forest or Gradient Boosting) to improve the system's predictive accuracy and handling of complex datasets.
3. Cloud Deployment and Scalability: Migrating the local SQLite database to a robust cloud-based relational database (e.g., PostgreSQL) to handle concurrent traffic from thousands of applicants during peak admission periods.
