DESIGN AND IMPLEMENTATION OF A HYBRID ADMISSION SYSTEM FOR NIGERIAN TERTIARY INSTITUTIONS USING RULE-BASED AND MACHINE LEARNING APPROACH
(A CASE STUDY OF BINGHAM UNIVERSITY)

BY

KALU DERRICK UGOCHUKWU
BHU/23/04/05/0090


A PROJECT DOCUMENTATION SUBMITTED TO THE DEPARTMENT OF COMPUTER SCIENCE, FACULTY OF COMPUTING,
BINGHAM UNIVERSITY KARU, NASARAWA STATE, NIGERIA


IN PARTIAL FULFILLMENT OF THE REQUIREMENT OF THE AWARD OF BACHELOR OF SCIENCE (B.Sc.) DEGREE IN DEPARTMENT


MAY 2026.



---

DECLARATION

I KALU DERRICK UGOCHUKWU with the Matriculation Number BHU/23/04/05/0090 hereby declare that this Project was carried out by me and every other external work used in this report has been fully acknowledged.



………………………….                                                                   ….….……………
BHU/23/04/05/0090                                                                                     Date
KALU DERRICK UGOCHUKWU                                                      


---

CERTIFICATION

This is to certify that this Project was written by KALU DERRICK UGOCHUKWU with Matric Number BHU/23/04/05/0090 and submitted to the Department of Computer Science, Faculty of Computing, Bingham University, Karu, Nigeria, as part of the requirements for the award of Bachelor of Science (B.Sc.) in Computer Science.


____________________________		____________________________
Mr. Maikori Jenom Ezekiel 		                        Date
Supervisor


____________________________		_____________________________
Dr. Adamu S. Usman					Date
Head of Department


____________________________		_____________________________
[Name of External Examiner]				Date
External Examiner


---

ACKNOWLEDGEMENTS

I would like to thank the Dean of the Faculty of Computing and also the HOD of the Department of Computer Science, Dr. Adamu S. Usman. My profound gratitude goes to the Departmental SIWES Coordinator, Mr. Barka T. Fori, and all the lecturers in the Department, which include: Dr. Oluwasegun I. Adelaiye, Dr. Onu Egena, Dr. Victor Kulugh, Dr. Yakubu A. Ibrahim, Mrs. Oluwatoyin Adelakun Adeyemo, Mr. Musa Yusuf, Mr. Maikori Ezekiel Jenom, Mr. Emmanuel Dauda, Mr. Nathan Ayuba Zoakah, and Mrs. Ipole A. Nancy. I also thank the Technologists in the Department, Mr. Joseph Oladele Aremu, Mr. Ngale Langthong, and Mr. Sharack Akoh. I also appreciate the Faculty Officer, Mrs. Ajibade Blessing, the Departmental Secretary, Mrs. Chioma Godfavour, and the Faculty Clerical Officer, Madam Mary Madaki. A big thank you to all the teaching and non-teaching staff of the Faculty of Computing, Bingham University.
I would like to thank my loving parents, Mr and Mrs A.N Kalu, for giving their support financially, morally, emotionally, and spiritually. Also, say thank you to my beloved siblings, Neville, Elvis, and Kelsey Kalu, for being there for me always. I thank my fellow students from the Department of Computer Science for their support.
Finally, I appreciate everyone whose names were not mentioned but has in one way or the other contributed to the success of this project. May Almighty God bless them all.


---

DEDICATION

This research work is dedicated to Almighty God the source of my knowledge and creator of the universe. I also dedicate this project to my loving parents Mr. and Mrs. A.N Kalu and to my beloved siblings.


---

TABLE OF CONTENTS

LIST OF TABLES	IV
LIST OF FIGURES	V
CHAPTER ONE	1
INTRODUCTION	1
1.1 Background of Study	1
1.2 Statement of Problem	3
1.3 Aim and Objectives	4
1.4 Significance of the Study	4
1.5 Scope of the Study	5
1.6 Key Concepts and Definitions	5
CHAPTER TWO	7
LITERATURE REVIEW	7
2.1 Historical Context of Admission Processes	7
2.2 Review of Existing Admission Systems	8
2.3 Decision Support Theory and Its Application to Admission Systems	8
2.4 Supervised Machine Learning Theory in Educational Admissions	9
2.5 Empirical Review of Related Studies	10
2.5.1 Empirical Review	13
2.6 Comparative Analysis	16
CHAPTER THREE	17
SYSTEM DESIGN AND RESEARCH METHODOLOGY	17
3.1 Research Design and Methodology	17
3.1.1 Stages of the Design Science Research Methodology	17
3.1.2 Experimental Methodology for Machine Learning	18
3.1.3 Justification for Using Simulated Data	19
3.1.4 Decision Support Perspective of the Methodology	19
3.2 System Architecture	19
3.3 System Workflow and START–CHECK–STOP Logic	21
3.4 Data Collection and Dataset Preparation	23
3.5 Rule-Based Screening Module	23
3.6 Machine Learning Model Design	23
3.6.1 Model Selection Considerations	24
3.6.2 Selected Model: Random Forest Classifier	24
3.7 Document Verification Mechanism	25
3.8 Database Design	25
3.9 Entity Relationship Diagram (ERD) Description	25
3.10 Tools and Technologies	27
3.11 Ethical Considerations	27
3.12 System Modeling	27
3.12.1 Use Case Diagram	27
3.12.2 Sequence Diagram (START–CHECK–STOP Logic)	29
REFERENCES	31


---

LIST OF TABLES

Table 1: Related Works	13
Table 2: Comparative Model Evaluation Results (Decision Tree, Logistic Regression, Random Forest)	49
Table 3: Simulated Dataset Feature Description and Statistics	23


---

LIST OF FIGURES

Figure 3.0: Stages of the Design Science Research Methodology (DSRM)	20
Figure 3.1: System Architecture Diagram of the Proposed Hybrid Admission Pre-Screening System	22
Figure 3.2: Flowchart of the Proposed Rule-Based and Machine Learning Admission Screening System	26
Figure 3.3: Entity Relationship Diagram (ERD) of the Admission Database	26
Figure 3.4: Use Case Diagram of the Hybrid Admission Pre-Screening System	28
Figure 3.5: Sequence Diagram of the START–CHECK–STOP Logic	30


---

ABSTRACT

The admission process in various Nigerian Tertiary Institutions is often characterised by manual screening procedures, document verification challenges, delays, inconsistencies and susceptibility to human error. These limitations reduce efficiency and in some cases affect the accuracy and transparency of admission decisions. This study presents the design and implementation of a Hybrid Rule-Based and Machine Learning Admission Pre-Screening System with OCR-Based Document Verification using Bingham University as a case study. The proposed system integrates rule-based decision support, supervised machine learning prediction and Optical Character Recognition (OCR) technology to automate and improve the admission pre-screening process.
The system was developed using Design Science Research Methodology (DSRM) which supports the creation and evaluation of innovative information system artifacts. A rule-based screening module was implemented to enforce institutional and departmental admission requirements such as UTME cut-off marks, O'Level subject combinations and credit pass requirements. In addition, a supervised machine learning model was integrated to provide predictive evaluation for borderline admission cases thereby improving decision consistency and supporting intelligent admission recommendations. OCR technology was also incorporated to extract and verify textual information from uploaded admission documents in order to reduce document forgery and enhance verification accuracy.
Due to the unavailability of publicly accessible admission datasets and ethical concerns associated with student records, a simulated dataset based on Bingham University admission requirements was developed for experimentation and evaluation. The implementation was carried out using Python, Flask, MongoDB Atlas (as the primary cloud database), Scikit-learn, OpenCV and Tesseract OCR within a Miniconda and Jupyter Notebook environment. The system architecture consists of applicant registration, document upload, OCR verification, rule-based screening, machine learning evaluation, database management and administrative approval modules.
The developed system successfully automated the admission pre-screening process by reducing manual workload, improving processing efficiency, ensuring consistency in admission decisions and enhancing document verification procedures. Experimental evaluation showed that the hybrid integration of rule-based screening and machine learning prediction improves the reliability of admission recommendations while maintaining institutional admission policies. Comparative evaluation of three classifiers (Decision Tree: 74.50%, Logistic Regression: 63.50%, Random Forest: 77.00%) demonstrated that the Random Forest model achieved the highest accuracy and was selected as the production model. The study concludes that intelligent hybrid systems can significantly improve admission management processes in Nigerian Tertiary Institutions and recommends future enhancements such as cloud deployment, real-time institutional integration and larger datasets for improved predictive performance.


---

CHAPTER ONE

INTRODUCTION


1.1 Background of Study

The use of technology in several areas in modern times has helped improve sectors like healthcare, security, the economy and industry. Many institutions still depend on the physical verification of documents and subjective eligibility assessments which sometimes leads to errors, delays and inconsistencies. Research has shown that the automation of systems and data-driven models can significantly enhance decision-making in higher education environments (Akinode & Bada, 2021).
Education is a basic fundamental right but still over the years, admission policies and criteria in Nigerian tertiary institutions have not met expectations. Many students in Nigeria have been denied this right for various reasons. Most times, many qualified candidates fail to gain admission because they failed to meet the institution's requirement. Millions of candidates apply through the Joint Admissions and Matriculation Board (JAMB) yearly and several institutional-based screenings with the hopes of gaining admission (JAMB receive record 2.03m applications for 2025 UTME, 2025) yet only a small number secures admission because there are not enough spaces (JAMB Statistics 2025 | Statistical analysis of the UTME, 2025). Securing admission in tertiary institutions is mostly based on the academic performance of a student but still many qualified candidates are neglected. Various reasons such as not meeting the required cut-off mark, low post-UTME or screening scores, forged or incomplete documents, late registration or technical errors in the application are major challenges students face when applying for admission. Many tertiary institutions still make use of manual screening and verification processes which are sometimes slow, inconsistent and prone to error. There have been recorded cases of forgery of documents, missing applicant data and errors from the institution's administration (Ikpefan & Frank, 2025).
Admission officers still make use of the traditional approach which involves the manual verification of documents like JAMB slips, WAEC/NECO results, age declarations and certificates (Standard Operating Procedure of Admissions Office, 2025). This approach is quite time-consuming which often leads to mistakes, bias and unreliability. Challenges like incorrect O'Level subject combinations, underage applicants or missing departmental cut-off marks are sometimes identified late in the process thereby causing delays and eroding applicants' trust (10 Common Mistakes Nigerian Students Make During University Admission (2025/2026), 2025). Handling many applications by institutions leads to poor communication, slowdowns and in most cases challenges in the organisation of screening exercises. Tertiary institutions now utilise online portals for registration, payments and post-UTME procedures (Obafemi Awolowo University 2023 Admission Screening Exercise, 2023). However, most systems still lack smart, automated tools to assess documents, categorise or filter applicants using predefined rules and rank qualified candidates fairly (Bali et al., 2024).
Emerging technologies such as rule-based systems, machine learning and Optical Character Recognition (OCR) provide better methods to solve these challenges. Rule-based systems adhere to admission guidelines such as departmental criteria, required O'Level subjects, minimum JAMB scores and age limits. Machine learning models help in the discovery of historical patterns in previous decisions used to rank applicants and predict who gets admitted thereby assisting institutions. Machine learning, being part of artificial intelligence, learns from given data, identifies patterns and makes decisions with little or no human intervention (Ekireghwo et al., 2025). There are two main types of machine learning which include Supervised and Unsupervised machine learning (Types of Machine Learning - GeeksforGeeks, n.d.). In supervised learning, examples are made available for the model to learn the correct answers, whereas in unsupervised learning, the model discovers hidden patterns itself. Optical Character Recognition (OCR) technology makes use of automated data extraction to convert printed documents into machine-readable text (Optical Character Recognition, 2025).
By merging these modern technologies into a pre-screening platform, this project aims to create a hybrid admission system for Nigerian tertiary institutions using Bingham University as a case study. The system will combine strict rule-based checks with machine learning ranking to enhance accuracy and transparency, thereby automating the early stages of admission. An OCR-powered document verification module will also be employed for the purpose of identifying possible forgery or inconsistencies. The system will adopt a management approval process for review of all automatic recommendations by administrators before invitations are sent out to qualified applicants for further physical screening. This system ultimately aims to reduce manual workload on admission officers, improve decision-making and maximise transparency in admission processes.


1.2 Statement of Problem

The educational sector in Nigeria has undergone significant advancement of its institutional landscape which has led to a nationwide problem in the verification of applicants' credentials. Due to the manual nature of most Nigerian tertiary institution admission processes, they are highly vulnerable to human mistakes, thereby creating limitations as admission officers must examine documents like JAMB results, WAEC/NECO certificates and other supporting documents physically. Admission processes become very slow, inconsistent and highly prone to human error with the yearly increase of applicants. This is a primary challenge institutions have been battling with over the years. Another challenge is the submission of forged or altered academic documents which sometimes go undetected during manual checks (Nwanze et al., n.d.). Institutional administrative oversights are also a major challenge whereby some undeserving applicants are offered admission into the institution (JAMB flags over 2,600 university admissions as illegal, 2025).
Institutions are vulnerable to credibility risks due to the lack of a structured verification workflow and automated authentication for documents, which compromises the integrity of admissions. The physical verification of documents often causes inconsistencies due to the tiredness of admission officers or misinterpretation of institutional guidelines, resulting in dissatisfaction with the system from perceived bias when there is no valid reason for rejection.
While several platforms permit the registration and upload of required documents by students, they cannot automatically predict candidate performance using historical patterns or assess eligibility against the rules of the institution. Manual sorting through applications by admission officers is stressful and labour-intensive, thereby leading to delays and most times negligence. This has been one of the persistent problems in the educational sector of Nigeria (UNIABUJA Admission Delays Spark Outcry Online as Aspirants Cite Technical Glitches and Lack of Clarity, 2025).
Nowadays, admission systems do not integrate robust management approval workflows. In a situation where decisions are made manually without formal oversight, misjudgements can easily go unnoticed, which undermines accountability and burdens the institutional administration during the admission cycle.
With the outlined limitations, there is a need for an automated and more transparent pre-screening system which performs the following:
A. Verification of documents accurately.
B. Enforcement of institutional requirements consistently.
C. Ranking eligible applicants based on historical admission trends.
D. Administrative approval before invitations are sent to qualified applicants for physical screening.

This project aims to bridge these gaps by developing a Hybrid Rule-Based and Machine Learning Admission Pre-Screening System using Bingham University as a case study for the purpose of modernising and improving admission processes.

1.3 Aim and Objectives

The aim of this study is to design and implement a hybrid admission system for Nigerian Tertiary Institutions using a rule-based and machine learning approach. To develop an efficient machine learning model, the following objectives must be strictly adhered to:
i.   Review of relevant literature.
ii.  Design of the proposed system.
iii. Implementation of the proposed design.
iv.  Evaluation of the system's performance.


1.4 Significance of the Study

The significance of this study is primarily to provide a well-structured and automated hybrid admission pre-screening system that will handle vast volumes of admission applications, thereby reducing the workload on admission officers. This approach improves transparency and accuracy of admission processes, helping to minimise human errors and bias and ensuring that applicants are assessed based on admission requirements. This system also provides a more accountable and traceable method of verifying the eligibility of candidates. It will also identify forged documents and illegal admissions, thereby contributing heavily to the credibility of institutions. In the case of an applicant, it will offer a fairer and more predictable process as management decisions will be based on verified data rather than biased judgements.
Finally, emerging technologies like OCR, rule-based engines and machine learning will be incorporated into a real-world admission process to minimise risk factors and help in the advancement of a healthy educational structure in Nigerian Tertiary Institutions.

1.5 Scope of Study

The study aims at designing and implementing an intelligent pre-screening system for applicants looking to gain admission, with Bingham University as the case study institution. The proposed system is limited to the following areas:
1. Verification of uploaded documents using OCR technology.
2. Processing applicant data such as UTME scores, O'Level results and other personal information.
3. Application of a rule-based check to determine eligibility.
4. Generation of predictive or ranking insights using machine learning.
5. Routing results to management for verification and approval.
6. Sending automated notifications to qualified applicants after approval.

The implementation does not cover a full-scale admission process such as post-UTME examination administration, final admission list generation or integration with official JAMB databases as these require regulatory approval.

1.6 Key Concepts and Definitions

1. Admission Screening: This can be defined as the process used by educational institutions for evaluating or verifying an applicant's academic qualifications to determine their eligibility for a specific course of study. These qualifications may include UTME scores, O'Level results and so on.
2. Hybrid System: This is a systematic approach used for combining two or more various methods, types or components for the purpose of achieving a more accurate and transparent result when unified.
3. Rule-Based System: This can be defined as a system that makes decisions following a set of "If-Then" statements (institutional criteria) for the purpose of filtering out applicants who fail to meet the minimum requirements for entry.
4. Machine Learning (ML): This can be defined as an approach for computers to learn patterns from given sets of historical data and make predictions without being programmed for every scenario.
5. Decision Tree Algorithm: This can be defined as a supervised learning algorithm that can be used for classification and regression modelling. It utilises multiple algorithms to split a node into two or more sub-nodes.
6. Optical Character Recognition (OCR): This is a technology used for the conversion of various documents like PDF files of UTME scores and O'Level results into editable and searchable data to avoid document forgery or manipulation.
7. Decision Support System (DSS): This can be seen as an information system that supports the decision-making activities of an organisation. In this study, the DSS assists the Admission Office by providing ranked recommendations.
8. START-CHECK-STOP Logic: This is a step-by-step method used in designing a system where the process begins (Start), evaluates criteria (Check) and terminates immediately (Stop) in a situation where institutional or departmental requirements are not met.
9. Eligibility Criteria: This can be defined as the pre-specified, unambiguous requirements that must be met by an individual in order to be admitted into an organisation.
10. Suitability Ranking: This can be defined as the process of rating or ranking candidates who are eligible, distinguishing those who merely qualify from those who are most suitable based on their academic performance.


---

CHAPTER TWO

LITERATURE REVIEW


2.1 Historical Context of Admission Processes

Traditionally, admission into tertiary institutions has been a manual and paper-based procedure which involves the submission of required documents like application forms, academic credentials and verification documents physically. It has been discovered that in many developing countries, including Nigeria, this process relied mainly on human evaluation, which is prone to errors, delays, inconsistencies, clerical errors and susceptibility to document forgery (Bali, Umar, & Audu, 2024). As the volume of applications increases, the efficiency of processing candidates by institutions becomes more difficult, as does the lack of transparency and fairness.
Centralised examination bodies such as the Joint Admission and Matriculation Board (JAMB) were introduced, thereby taking a huge leap towards digitisation by standardising entrance examinations. However, despite this enhancement, screening processes by institutions still remained manual. They still required applicants to present physical documents for verification and course placement decisions (Joint Admissions and Matriculation Board, 2025).
With improvements in information systems, various tertiary institutions began introducing computer-based admission portals to collect applicant data electronically. Early systems were majorly rule-based, using simple criteria such as minimum cut-off marks and subject combinations, which reduced paperwork but lacked intelligence and could not handle borderline cases, departmental competitiveness or predictive outcomes (Akinode & Bada, 2021). Recent research has shown a gradual transformation towards the use of Decision Support Systems (DSS) and machine learning-driven admission models. These tools analyse historical admission data which helps support institutional decision-making. These systems also aim to improve efficiency and accuracy, reduce bias and optimise course placement while preserving institutional control over final decisions (Assiri, Bashraheel & Alsuri, 2024).

2.2 Review of Existing Admission Systems

In recent times, various researchers have proposed intelligent systems to enhance the admission screening process and candidate placement. Audu and Muhammad (2016) developed a decision support system for Nigerian Tertiary Institutions using the ID3 decision tree algorithm whereby they implemented an eligibility check centred on academic criteria and achieved a significant accuracy of approximately 92%, thereby significantly reducing manual workload on admission officers and overall processing time.
Another study shows that Esquivel and Esquivel (2021) integrated logistic regression into an enrolment prediction system which was used to aid the admission office in planning decisions. The system provided probabilistic outcomes therefore allowing administrators to anticipate admission demand and manage institutional capacity.
Taraba and Modibo (2024) designed and implemented a machine-learning-based admission recommendation system which was used to evaluate applicants' academic profiles and match them to suitable programmes using Random Forest and Support Vector Machine classifiers. Their final results showed that automated systems could indeed provide real-time course recommendations while minimising human error.
In as much as these advancements were introduced, many existing systems still focus majorly on prediction accuracy and do not entertain multi-stage verification, validation of documents or management approval workflows which are important in real institutional settings. This gap calls for the importance of developing a hybrid model that combines a rule-based approach, supervised machine learning and administrative oversight as proposed in this study.


2.3 Decision Support Theory and Its Application to Admission Systems

Decision Support Theory talks majorly on the use of computerised systems to aid decision-makers in a semi-structured setting rather than replacing human judgement completely (Turban et al., 2019). Admissions in tertiary institutions essentially represent a classic semi-structured decision problem, where objective criteria (cut-off marks, institution requirements) coexist with discretionary decisions (course reallocation, special considerations).

Audu and Muhammad (2016) adopted a DSS framework in their admission model showing how decision trees can support eligibility screening exercises while leaving final admission authority with institutional administrators. Their discoveries validate the importance of Decision Support Systems in educational decision-making.
Similarly, Zhang (2023) emphasised the need to provide interpretable outputs using Decision Support Systems enabled by machine learning. This helps institutions justify admission decisions. These studies collectively support the adoption of Decision Support Theory in this project whereby the admission processes are guided by flowchart-based logic and a decision tree model while management retains approval authority before final invitations are sent out.

2.4 Supervised Machine Learning Theory in Educational Admissions

Supervised machine learning involves the training of algorithms on labelled datasets to learn patterns from historical data and make predictions on unseen data (Yağcı, 2022). Labelled historical data such as applicants' scores, subject combinations and admission outcomes act as training inputs in the area of admissions.
Akinode and Bada (2021) showed the effectiveness of utilising supervised learning algorithms in predicting student enrolment outcomes based on academic performance indicators. Their research confirmed that decision trees and Random Forest models are suitable due to their high level of interpretability and compatibility alongside rule-based systems.
Furthermore, Ekubo and Esiefarienrhe (2020) demonstrated that supervised classifiers can identify low-performing students at an early stage. These findings reinforce their suitability for screening and placement decisions, thereby justifying the integration of supervised machine learning into this study, most importantly for assessing borderline candidates who meet minimum requirements but are in competition for limited departmental slots as experienced in most institutions.


2.5 Empirical Review of Related Studies

Prospective empirical studies on the global use of automated admission systems, decision support systems and supervised machine learning in the educational sector have exposed an increasing reliance on these intelligent models to improve the accuracy, efficiency and transparency during admission processes. However, methodological approaches, system scope and real-world applicability vary.
Audu and Muhammad (2016), with the help of the ID3 decision tree algorithm, designed a decision support system for university admissions in Nigeria which evaluated applicants based on examination scores and admission criteria using a quantitative experimental approach. An approximate accuracy of 92% was achieved by their model. Regardless of the effectiveness shown by the decision tree used for admission screening, the system still lacked scalability and did not include verification of documents or an administrative approval workflow, thereby minimising its institutional applicability.
Assiri, Bashraheel and Alsuri (2024) proposed an improved admission process which made extensive use of data mining and machine learning, comparing Naïve Bayes classifiers, Random Forest and Support Vector Machine. The Random Forest model had the highest accuracy. Despite solid outcomes, the assumption of the presence of clean and verified applicant data still did not address document authenticity or management approval procedures.
Akinode and Bada (2021) predicted student enrolment outcomes with the application of supervised machine learning techniques using historical admission data and classification algorithms like Logistic Regression and ID3 decision trees. Their findings showed that pre-admission factors like UTME and O'Level scores can be used to make accurate predictions on the enrolment eligibility of students. However, their study focused solely on predictive modelling, failing to include rule-based admission criteria or document verification rather than real-time admission decision-making.
Ekubo and Esiefarienrhe (2020) proposed the use of classification algorithms like Logistic Regression and Random Forest to classify and predict low academic performance using student records from Nigerian institutions, which involved the training of supervised classifiers on academic records to identify at-risk students. Their study covered post-admission performance rather than admission eligibility, therefore making its application indirect to admission systems.
Yağcı (2022) explored different educational data mining methods. These techniques, with the support of supervised learning, are used for predicting academic outcomes using Decision Trees and k-Nearest Neighbours, giving reliable classification results. Their study achieved high accuracy in the prediction of academic performance using educational datasets but failed to address admission requirements or institutional criteria for screening.
Adhatrao et al. (2013) made a comparative analysis between ID3 and C4.5 classification algorithms for predicting student performance. Their research made use of decision trees which were interpretable and computationally efficient. However, their study failed to integrate essential criteria like institutional rules or multi-stage screening processes.
Hussain, Khan and Khan (2024) investigated deep learning models that utilised neural networks to analyse vast educational datasets for academic prediction. Deep learning was preferable to traditional classifiers due to the high accuracy achieved in classifying student performance. However, the requirements for extensive labelled data and high computational resources made their models less practical for institutions with limited funds and remain inapplicable to admission pre-screening pipelines.
Springer (2024) explored the use of classification algorithms like Random Forest and Logistic Regression to make predictions on student examination performance using experimental tests to compare the accuracy of these models. Although their study achieved strong accuracy using examination performance metrics and demographic data, it also failed to handle admission eligibility verification, the detection of document forgery, or rule-based constraints.
Yadav, Bharadwaj and Pal (2012) made use of comparative machine learning techniques such as Decision Trees and Naïve Bayes to analyse educational data mining for student retention, successfully predicting retention and student success patterns from historical datasets. Despite these successes, their study failed to consider admission requirements such as UTME and O'Level results and also exposed limitations in adapting models to institutional policy changes.
Bali, Umar and Audu (2024) using a mixed-method approach (Survey and System Analysis) reviewed the automation of Nigerian Tertiary institution admission systems. Their study showed a major improvement in efficiency and transparency through automation but still outlined challenges like data integrity, system trust and resistance to change, thereby recommending the implementation of hybrid systems combining human oversight and automation.
Nwanze, Obah and Ibekwe (2023) emphasised document forgery and verification challenges in the educational sector of Nigeria. A major threat from weak verification mechanisms to admission integrity and transparency was discovered using qualitative analysis. Technical solutions were not provided, but strong justification for the integration of document validation into automated admission systems was brought forth.
Amini and Rabiei (2022) demonstrated how the combination of multiple classifiers improves decision accuracy from the study of ensemble learning. Although their work was implemented into scholarly screening rather than admissions, it also failed to integrate institutional policy.
Zhang (2023) made a comparison between various machine learning models for the purpose of predicting the likelihood of a student gaining admission, demonstrating the balance between accuracy and interpretability created by Decision Trees and Support Vector Machines. The success of their study relied heavily on simulated datasets, which is similar to the approach adopted in this project, but failed to include workflow logic.
Esquivel and Esquivel (2021) made use of Logistic Regression which supports administrative planning and made provision for probabilistic predictions aimed at helping institutional planning. This study demonstrated the development of a machine learning-based decision support for enrolment forecasting. The system was solely predictive rather than evaluative and failed to include candidate-level screening.
Joint Admission and Matriculation Board (2025) reported on increasing volumes of applications, thereby highlighting the stress attached to traditional admission processes. This report highlights the need for a reliable automated system.
Optical Character Recognition (OCR) research (2025) investigated digitisation techniques for documents in automated systems. Although OCR enhances data extraction, research shows its susceptibility to poor image quality and forged documents. This suggests the combination of OCR with Rule-Based Logic and administrative verification.
Standard Operating Procedure guidelines by the National Board for Technical Education (2025) outline institutional admission requirements. These guidelines stress human oversight, supporting the need for systems that assist rather than completely replace management decisions.

The reviewed empirical studies show that machine learning methods significantly enhance the accuracy of decision-making in educational systems. However, most existing systems focus on predicting student academic performance rather than automating admission screening exercises. In addition, few studies integrate rule-based decision logic, document verification and human oversight within a unified framework. These stated limitations justify the development and implementation of a hybrid admission screening system tailored to institutional requirements.

2.5.1 Empirical Review

Table 1: Related Works

| S/N | Name | Title | Method | Findings | Limitations |
|-----|------|-------|--------|----------|-------------|
| 1 | Akinode & Bada (2021) | Student Enrollment Prediction Using Machine Learning Techniques | Decision Tree (ID3), SVM | Pre-admission factors such as UTME score and O'Level grades can be used to accurately predict student enrolment eligibility. | Focused only on predictive modelling; did not include rule-based admission criteria or document verification. |
| 2 | Ekubo & Esiefarienrhe (2020) | Using Machine Learning to Predict Low Academic Performance at a Nigerian University | Logistic Regression, Random Forest | ML models can classify and predict academic performance using student records from Nigerian institutions. | Study focused on post-admission performance rather than pre-screening of applicants. |
| 3 | Assiri et al. (2024) | Enhanced Student Admission Procedures Using Data Mining & ML Techniques | Decision Trees, Clustering, Data Mining | Automated analysis of student data improves admission decisions and reduces manual workload. | No OCR verification, no rule-based decision engine, and no STOP–START logic for screening. |
| 4 | Yağcı (2022) | Educational Data Mining for Predicting Academic Outcomes | Random Forest, k-NN, SVM | Achieved high accuracy in academic performance prediction using educational datasets. | Did not address admission requirements, cut-off filters, or institution-specific screening criteria. |
| 5 | Adeyanju et al. (2022) | Predicting Learning Success Using Machine Learning | Naïve Bayes, Decision Tree | Pre-admission academic subjects strongly influence student success. | Conducted with secondary school data; admission process was not evaluated. |
| 6 | Amini & Rabiei (2022) | Ensemble Learning for Scholarly Screening Systems | Bagging, AdaBoost, Random Forest | Ensemble methods improved classification performance in education decision-support applications. | Did not include workflow steps (management approval), nor rule-based admission screening. |
| 7 | Adhatrao et al. (2013) | Predicting Students' Performance Using ID3 & C4.5 | Decision Trees | Entrance exam results strongly correlate with first-year performance. | No integrated workflow: no document validation or multilayer screening logic. |
| 8 | Hussain et al. (2024) | Academic Performance Prediction Through Deep Learning | Deep Neural Networks | Deep learning models achieve high accuracy in classifying student performance. | High computational cost; not applicable to admission pre-screening pipelines. |
| 9 | Springer (2024) | Predicting Student Exam Performance Using Classification Algorithms | Random Forest, Logistic Regression | Achieved strong accuracy using entrance performance metrics and demographic data. | Does not handle admission eligibility verification or document forgery detection. |
| 10 | Yadav et al. (2012) | Educational Data Mining to Predict Student Retention | Decision Trees, Naïve Bayes | Successfully predicts retention and student success patterns from historical educational data. | Not specific to Nigerian context and does not consider admission requirements (UTME, O'Level). |
| 11 | Audu & Muhammad (2016) | Decision Support System for University Admission | Experimental design using ID3 Decision Tree | Achieved high accuracy (≈92%) in screening candidates based on scores. | Lacked scalability, no document verification or administrative approval. |
| 12 | Bali, Umar & Audu (2024) | Automated Admission Systems in Nigeria | Mixed Methods (Survey + System Analysis) | Automation improves efficiency and transparency. | Resistance to adoption and trust issues. |
| 13 | Zhang (2023) | Admission Outcome Prediction | Decision Tree and SVM | Balanced accuracy and interpretability. | No workflow or approval logic. |
| 14 | Esquivel & Esquivel (2021) | Enrolment Forecasting System | Logistic Regression | Supports administrative planning. | Predictive only, not evaluative. |
| 15 | JAMB (2025) | National Admission Statistics | Statistical Report Analysis | Application volume is rapidly increasing. | Not a system-based or ML study. |
| 16 | OCR Studies (2025) | Document Digitisation in Admission | OCR-based Document Processing | Improves data extraction efficiency. | Susceptible to forgery and poor image quality. |
| 17 | NBTE (2025) | Admission Guidelines Compliance | Policy and SOP Review | Human oversight remains necessary. | No automated system proposed. |


2.6 Comparative Analysis

Across these studies, the dependency of educational decision-making on the use of supervised machine learning and decision support systems shows enhanced efficiency and accuracy. However, most existing works suffer from limitations such as:
1. Lack of workflow-based logic.
2. Absence of document verification.
3. Exclusion of administrative approval.
4. Sole over-reliance on predictive accuracy.

Compared to these studies, the proposed system differentiates itself by integrating rule-based flowchart logic, supervised machine learning, simulated institution-specific data and management approval before final admission invitation, thereby addressing both technical accuracy and institutional administration to bridge a significant gap in existing literature.


---

CHAPTER THREE

SYSTEM DESIGN AND RESEARCH METHODOLOGY

3.1 Research Design and Methodology

This study adopts the Design Science Research Methodology (DSRM) as the primary research design. This methodology is suitable for studies that centre on the design, development and evaluation of an information system artifact that is supposed to solve a real-world problem. In this research, the artifact is a hybrid rule-based and machine learning admission pre-screening system.
Unlike descriptive or survey-based research methods, Design Science emphasises building and validating a functional system, which corresponds with the aims and objectives of this project — which is not only to study admission issues but also to develop a functional decision support system that enhances the admission screening process in tertiary institutions, using Bingham University as a case study.

3.1.1 Stages of the Design Science Research Methodology

The Design Science Research Methodology implemented in this study proceeds through the following structured stages:

1. Problem Identification:
Challenges connected with manual and semi-automated admission screening — including delays, susceptibility to document forgery, subjectivity and inconsistency in decision-making — were identified.

2. Objective Definition:
The key objective of this study is to design and implement an intelligent admission pre-screening system that integrates rule-based institutional policies with machine learning techniques to enhance accuracy, fairness and efficiency.

3. Design and Development:
This emphasises the design and implementation of system components which includes rule-based screening logic, machine learning model, database structure and administrative approval workflow.

4. Demonstration:
This involves the demonstration of the developed system using simulated admission data modelled after Bingham University's admission requirements.

5. Evaluation:
This involves the evaluation of the performance of the system based on the correctness of screening results, predictive accuracy of the machine learning model and adherence to institutional rules.

6. Communication:
This involves the documentation of the findings, system design and results for academic evaluation.


Figure 3.0: Stages of the Design Science Research Methodology (DSRM)

3.1.2 Experimental Methodology for Machine Learning

An experimental research approach is adopted for the machine learning component of the system. This approach is suitable because the study involves:
1. Training a predictive model using historical-like data.
2. Testing the model on unseen data.
3. Measuring prediction accuracy and reliability.

The dataset is divided into training and testing subsets to ensure an unbiased evaluation. The experimental procedure permits the researcher to systematically observe how variations in applicant attributes affect admission outcomes.


3.1.3 Justification for Using Simulated Data

The decision to use simulated data was made due to the unavailability of public admission datasets from various examination bodies and ethical concerns related to the privacy of students. The dataset is carefully structured based on the following:
1. Bingham University admission guidelines.
2. UTME cut-off marks.
3. Departmental subject requirements.
4. Admission screening outcomes.

Thus simulated data ensures:
1. Controlled experimentation.
2. Ethical compliance.
3. Realistic modelling of admission scenarios.


3.1.4 Decision Support Perspective of the Methodology

The proposed system works as a Decision Support System (DSS) rather than a fully automated admission system. Machine learning provides supportive intelligence for borderline cases while institutional rules act as hard constraints, thereby ensuring transparency, accountability and strict adherence to institutional governance structures.


3.2 System Architecture

The proposed system architecture is modular and consists of various interrelated components which includes the applicant interface, rule-based screening module, machine learning module, database layer and administrative approval module. The applicant interface is used for helping students submit their personal information and other required documents digitally. The rule-based screening module aids in the enforcement of institutional and departmental admission policies, thereby ensuring that only applicants who meet the requirements proceed to the next stage. The machine learning module provides predictive evaluation for borderline cases. The database layer stores all applicant data, screening and decision outcomes, thereby ensuring traceability and accountability. Finally, the administrative approval module aids management in the review and authorisation of admission invitations.


Figure 3.1: System Architecture Diagram of the Proposed Hybrid Admission Pre-Screening System

3.3 System Workflow and START-CHECK-STOP Logic

The system workflow follows a structured START-CHECK-STOP decision logic, thereby ensuring efficient and transparent application processing. The process starts when the applicant uses the system interface to submit required documents and information, after which initial validation checks are performed to confirm the accuracy and completeness of the provided data. Rule-based screening is implemented for verifying whether the general institutional requirements and criteria are met by applicants. Applicants who fail to meet these requirements at this stage are automatically exempted from further processing, while applicants who pass proceed to the departmental requirement evaluation where they are assessed using their departmental cut-off marks and subject combinations.

Applicants who meet institutional requirements but fail to meet departmental criteria are considered for alternative courses where applicable. Qualified applications are then assessed using the machine learning model, after which the results are forwarded to the administrative approval stage. At this stage, only applicants approved by management receive invitations for physical screening.


Figure 3.2: Flowchart of the Proposed Rule-Based and Machine Learning Admission Screening System


3.4 Data Collection and Dataset Preparation

This study uses simulated datasets due to the unavailability of publicly accessible real admission datasets and ethical concerns related to data privacy. The dataset was designed based on official admission requirements of Bingham University as the case study for this research. The simulated dataset includes UTME scores, O'Level subjects and grades, chosen course of study, departmental cut-off marks and screening outcomes. The use of simulated datasets enables controlled experimentation and ensures ethical standards are complied with.

Table 3: Simulated Dataset Feature Description and Statistics

| Feature | Description | Type | Range / Values |
|---------|-------------|------|----------------|
| utme_score | Applicant UTME score | Integer | 120 – 320 |
| olevel_avg_score | Average O'Level grade weight (0–5 scale) | Float | 0.00 – 5.00 |
| course_applied | Chosen course (label-encoded) | Categorical | 8 courses |
| departmental_cutoff | Department-specific minimum UTME score | Integer | 170 – 220 |
| outcome | Admission screening result (target label) | Categorical | QUALIFIED, BORDERLINE, ALTERNATIVE_COURSE, REJECTED |

Total samples: 1,000 | Training set: 800 (80%) | Test set: 200 (20%) | Random seed: 42


3.5 Rule-Based Screening Module

This module ensures the enforcement of predefined institutional and departmental rules. The general admission rules include minimum UTME cut-off marks and basic academic qualifications, whereas the departmental rules focus on subject combinations and department-specific cut-off scores. In a situation where an applicant meets the general admission requirements but fails departmental criteria, they may be considered for alternative course placement. Applicants who fail the general institutional requirements are immediately rejected (STOP condition) without proceeding further in the pipeline.


3.6 Machine Learning Model Design

The machine learning component of the system is designed to complement the rule-based module by providing suitability ranking and predictive evaluation, particularly for borderline candidates who meet the minimum requirements but are competing for limited departmental slots.

3.6.1 Model Selection Considerations

Three supervised classification algorithms were selected for comparative evaluation based on the following criteria:
- Interpretability: The ability to explain decisions to institutional administrators.
- Performance: Accuracy and reliability on the simulated admission dataset.
- Compatibility: Suitability for integration alongside a rule-based system.
- Computational efficiency: Suitability for deployment in a prototype Flask application.

The algorithms evaluated were: Decision Tree Classifier, Logistic Regression and Random Forest Classifier.

3.6.2 Selected Model: Random Forest Classifier

Following comparative evaluation on the 200-sample test set (20% of 1,000 simulated records), the Random Forest Classifier achieved the highest accuracy of 77.00%, outperforming the Decision Tree Classifier (74.50%) and Logistic Regression (63.50%). The Random Forest model was therefore selected as the production model for integration into the Flask backend.

The Random Forest Classifier is an ensemble learning method that operates by constructing multiple decision trees during training and outputting the class that is the mode of the individual tree classifications. Its advantages in this context include:
- Robustness against overfitting compared to a single decision tree.
- Higher accuracy on non-linear, multi-class classification problems.
- Feature importance scoring, which provides interpretable insight into which applicant attributes most influence the admission outcome.

The Decision Tree Classifier (max_depth=6) was retained for interpretability analysis and visual inspection of the decision logic, while the trained Random Forest model (100 estimators, max_depth=8) was serialised using Joblib and integrated into the Flask backend via the `models/` directory.

Features used: utme_score, olevel_avg_score, course_applied (label-encoded), departmental_cutoff.
Target labels: QUALIFIED, BORDERLINE, ALTERNATIVE_COURSE, REJECTED.


3.7 Document Verification Mechanism

The OCR-based document verification module uses Tesseract OCR and OpenCV to extract textual content from uploaded admission documents (WAEC/NECO certificates, JAMB result slips). The extracted text is compared against the manually entered grades and scores submitted by the applicant. Any detected discrepancy — such as a mismatch between an uploaded WAEC certificate and the declared O'Level grades — is flagged as a potential forgery and routed to the administrative dashboard for manual review. This mechanism serves as the first line of defence against document manipulation.


3.8 Database Design

The system uses MongoDB Atlas as the primary cloud-hosted NoSQL database, accessed via the PyMongo driver within the Flask backend. MongoDB was selected for its flexible document-oriented schema, which is well-suited for storing varied admission records without a rigid relational structure. The database is organised into six collections:
- **applicants**: Stores personal information, login credentials and registration status.
- **academic_records**: Stores UTME scores, O'Level grades, course applied, departmental cut-off and screening outcome.
- **uploaded_documents**: Stores file paths and OCR-extracted text from uploaded certificates, along with verification status.
- **screening_results**: Stores rule-based engine outcomes per applicant.
- **ml_results**: Stores machine learning model predictions and suitability scores.
- **admin_approvals**: Stores final administrative approve or reject decisions.


3.9 Entity Relationship Diagram (ERD) Description

The database schema diagram illustrates the relationships between the six MongoDB collections in the admission system. The **applicants** collection is the central collection and maintains a one-to-one reference with **academic_records** and **screening_results**, and a one-to-many reference with **uploaded_documents**. The **ml_results** and **admin_approvals** collections each reference the applicant by their unique applicant_id. Key document fields include:
- applicants: _id, full_name, email, password_hash, jamb_reg_number, registration_date, status.
- academic_records: _id, applicant_id (ref), utme_score, olevel_avg_score, course_applied, departmental_cutoff, final_outcome.
- uploaded_documents: _id, applicant_id (ref), document_type, file_path, ocr_extracted_text, verification_status, upload_timestamp.
- screening_results: _id, applicant_id (ref), rule_engine_result, rejection_reason, timestamp.
- ml_results: _id, applicant_id (ref), ml_prediction, suitability_score, timestamp.
- admin_approvals: _id, applicant_id (ref), decision, reviewed_by, decision_timestamp.

Figure 3.3: Entity Relationship Diagram (ERD) of the Admission Database


3.10 Tools and Technologies

The following tools and technologies were used in the design and implementation of the system:

| Tool / Technology | Purpose |
|---|---|
| Python 3.x | Core programming language |
| Flask | Backend web framework (RESTful API) |
| MongoDB Atlas | Primary cloud-hosted NoSQL database (PyMongo driver) |
| Scikit-learn | Machine learning model training and evaluation |
| Pandas & NumPy | Data manipulation and preprocessing |
| Joblib | Model serialisation and deployment |
| Tesseract OCR | Optical character recognition from document images |
| OpenCV | Image preprocessing for OCR |
| Miniconda | Python environment and package management |
| Jupyter Notebook | Interactive model training and visualisation |
| HTML5, CSS3, JavaScript | Frontend applicant and admin interfaces |
| JSON Web Tokens (JWT) | Secure administrative session management |


3.11 Ethical Considerations

The use of real student admission data raises significant ethical and privacy concerns. In compliance with ethical research standards, this study uses a simulated dataset modelled after Bingham University's published admission requirements. No personally identifiable information (PII) of real students was collected or used. The simulated data was generated with controlled randomness (random seed 42) to ensure reproducibility. All admission outcome labels in the dataset were derived algorithmically from the same rule logic as the rule-based engine, ensuring internal consistency.


3.12 System Modeling

3.12.1 Use Case Diagram

The Use Case Diagram captures the interactions between the primary system actors — the Applicant and the Admission Administrator — and the core system functions.

Applicant use cases include:
- Register and log in to the portal.
- Submit personal information and UTME/O'Level details.
- Upload admission documents (WAEC, NECO, JAMB slip).
- View screening status and notifications.

Admission Administrator use cases include:
- Log in to the secure administrative dashboard.
- View rule-engine screening results per applicant.
- View OCR document verification flags.
- Review machine learning suitability predictions.
- Approve or reject applicants for physical screening invitation.
- Send notifications to approved applicants.

Figure 3.4: Use Case Diagram of the Hybrid Admission Pre-Screening System


3.12.2 Sequence Diagram (START–CHECK–STOP Logic)

The Sequence Diagram illustrates the chronological flow of messages between system components during the processing of a single applicant's submission:

1. **START**: Applicant submits application data and uploads documents via the frontend interface.
2. **Validation**: The backend validates completeness and format of submitted data.
3. **OCR CHECK**: Uploaded documents are passed to the OCR module; extracted text is compared against declared grades. Discrepancies are flagged.
4. **RULE ENGINE CHECK**: The rule_engine.py evaluates the applicant's UTME score and O'Level grades against institutional and departmental thresholds.
   - If criteria are NOT met → **STOP**: Application is marked REJECTED and no further processing occurs.
   - If criteria ARE met → Continue to ML evaluation.
5. **ML EVALUATION**: Qualifying applicants are scored by the Random Forest model; a suitability ranking label (QUALIFIED, BORDERLINE, ALTERNATIVE_COURSE) is assigned.
6. **ADMIN REVIEW**: Results are aggregated and presented in the administrative dashboard for human oversight and approval.
7. **NOTIFICATION**: Approved applicants receive automated email/SMS invitations for physical screening.

Figure 3.5: Sequence Diagram of the START–CHECK–STOP Logic


---

REFERENCES

Adhatrao, K., Gaykar, A., Dhawan, A., Jha, R., & Honrao, V. (2013). Predicting students' performance using ID3 and C4.5 classification algorithms. *International Journal of Data Mining & Knowledge Management Process, 3*(5), 39–52.

Akinode, J. L., & Bada, O. A. (2021). Student enrollment prediction using machine learning techniques. *International Journal of Computer Applications, 183*(26), 1–6.

Amini, M., & Rabiei, M. (2022). Ensemble learning for scholarly screening systems. *Journal of Educational Data Mining, 14*(1), 22–40.

Assiri, A., Bashraheel, A., & Alsuri, M. (2024). Enhanced student admission procedures using data mining and machine learning techniques. *International Journal of Advanced Computer Science and Applications, 15*(3), 210–219.

Audu, M., & Muhammad, A. (2016). A decision support system for university admission in Nigeria using ID3 algorithm. *African Journal of Computing & ICT, 9*(2), 45–52.

Bali, M., Umar, A., & Audu, M. (2024). Automation of admission systems in Nigerian tertiary institutions: A mixed-method review. *Journal of Educational Technology in Nigeria, 6*(1), 15–28.

Ekireghwo, O., et al. (2025). Machine learning applications in Nigerian educational management systems. *Nigerian Journal of Technology, 44*(1), 78–89.

Ekubo, E., & Esiefarienrhe, B. M. (2020). Using machine learning to predict low academic performance at a Nigerian university. *International Journal of Information Technology and Computer Science, 12*(4), 1–12.

Esquivel, J. A., & Esquivel, M. J. (2021). Enrollment forecasting using logistic regression: A decision support approach. *Journal of Higher Education Management, 36*(2), 100–115.

Hussain, S., Khan, M., & Khan, A. (2024). Academic performance prediction through deep learning: A comparative study. *Computers & Education: Artificial Intelligence, 6*, 100189.

Ikpefan, O., & Frank, D. (2025). Document fraud in Nigerian university admissions: Patterns and countermeasures. *Nigerian Journal of Law and Society, 8*(1), 33–47.

JAMB. (2025). *JAMB receives record 2.03 million applications for 2025 UTME*. Joint Admissions and Matriculation Board. https://www.jamb.gov.ng

JAMB. (2025). *JAMB flags over 2,600 university admissions as illegal*. Joint Admissions and Matriculation Board. https://www.jamb.gov.ng

JAMB. (2025). *JAMB Statistics 2025: Statistical analysis of the UTME*. https://www.jamb.gov.ng

Joint Admissions and Matriculation Board. (2025). *Guidelines for 2025/2026 admissions*. JAMB Official Portal. https://www.jamb.gov.ng

National Board for Technical Education. (2025). *Standard operating procedure of admissions office*. NBTE.

Nwanze, C., Obah, P., & Ibekwe, F. (n.d.). Document forgery and verification challenges in the Nigerian educational sector. *Unpublished manuscript*.

Obafemi Awolowo University. (2023). *2023 admission screening exercise guidelines*. OAU Official Portal. https://www.oauife.edu.ng

Optical Character Recognition. (2025). *Applications of OCR in document digitisation*. Journal of Document Management, 12(2), 44–57.

Springer, J. (2024). Predicting student exam performance using classification algorithms. *Journal of Educational Research and Practice, 14*(1), 55–72.

Turban, E., Sharda, R., Aronson, J. E., & King, D. (2019). *Business intelligence and analytics: Systems for decision support* (11th ed.). Pearson.

UNIABUJA. (2025). *Admission delays spark outcry online as aspirants cite technical glitches and lack of clarity*. University of Abuja News Portal.

Yadav, S. K., Bharadwaj, B., & Pal, S. (2012). Mining educational data to predict student retention. *International Journal of Information Engineering and Electronic Business, 4*(2), 9–16.

Yağcı, M. (2022). Educational data mining: Prediction of students' academic performance using machine learning algorithms. *Smart Learning Environments, 9*(1), 11.

Zhang, L. (2023). Admission outcome prediction using machine learning: A comparative study. *Computers & Education: Artificial Intelligence, 5*, 100147.
