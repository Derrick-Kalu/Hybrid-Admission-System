const API_BASE = 'http://127.0.0.1:5000/api';

// Stores the last submission data for printing
let lastSubmissionData = null;

document.addEventListener('DOMContentLoaded', () => {
    // --- Auth Guard ---
    const applicantId   = localStorage.getItem('applicant_id');
    const applicantName = localStorage.getItem('applicant_name');

    if (!applicantId) {
        window.location.href = 'index.html';
        return;
    }

    // --- Populate Info ---
    document.getElementById('welcomeMessage').textContent = `Welcome, ${applicantName || 'Applicant'}`;
    document.getElementById('sidebarName').textContent    = applicantName || 'Applicant';
    document.getElementById('sidebarId').textContent      = `#APP-${String(applicantId).padStart(5, '0')}`;

    // If already applied (returned from login), show submitted card
    if (localStorage.getItem('has_applied') === 'true') {
        showSubmittedState(localStorage.getItem('screening_status') || 'PENDING');
    }

    // --- Logout ---
    document.getElementById('logoutBtn').addEventListener('click', () => {
        localStorage.clear();
        window.location.href = 'index.html';
    });

    // --- File Upload UX ---
    setupFileUpload('jamb_document', 'jambDropZone', 'jambFileDisplay');
    setupFileUpload('waec_document', 'waecDropZone', 'waecFileDisplay');
    setupFileUpload('neco_document', 'necoDropZone', 'necoFileDisplay');

    // --- JAMB Year Validation ---
    const jambYearInput = document.getElementById('jamb_year');
    if (jambYearInput) {
        jambYearInput.addEventListener('input', () => {
            const year = parseInt(jambYearInput.value);
            const currentYear = new Date().getFullYear();
            const age = currentYear - year;
            if (year >= 2018 && year <= currentYear) {
                if (age >= 2) {
                    jambYearInput.style.borderColor = 'var(--warning)';
                    jambYearInput.title = `⚠️ Result is ${age} year(s) old. Valid but approaching JAMB's 3-year expiry.`;
                } else {
                    jambYearInput.style.borderColor = 'var(--success)';
                    jambYearInput.title = 'Valid JAMB year.';
                }
            } else {
                jambYearInput.style.borderColor = 'var(--danger)';
                jambYearInput.title = 'Invalid JAMB year.';
            }
        });
    }

    // --- UTME Score Cross-Check Warning ---
    const declaredInput = document.getElementById('utme_score_declared');
    if (declaredInput) {
        declaredInput.addEventListener('input', () => {
            const val = parseInt(declaredInput.value);
            declaredInput.style.borderColor = (val >= 100 && val <= 400) ? 'var(--success)' : 'var(--danger)';
        });
    }

    // --- O'Level validation helper ---
    function hasAtLeastOneOlevel() {
        const waec = document.getElementById('waec_document').files.length > 0;
        const neco = document.getElementById('neco_document').files.length > 0;
        return waec || neco;
    }

    // --- Form Submission ---
    const form        = document.getElementById('applicationForm');
    const submitBtn   = document.getElementById('submitAppBtn');
    const submitError = document.getElementById('submitError');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        submitError.classList.add('hidden');

        // Validate at least one O'Level document
        if (!hasAtLeastOneOlevel()) {
            const msg = document.getElementById('olevelValidationMsg');
            msg.style.display = 'block';
            msg.scrollIntoView({ behavior: 'smooth', block: 'center' });
            return;
        }
        document.getElementById('olevelValidationMsg').style.display = 'none';

        // Grade credit check warning
        const mathGrade    = form.querySelector('[name="o_level_math"]').value;
        const englishGrade = form.querySelector('[name="o_level_english"]').value;
        const creditGrades = ['A1', 'B2', 'B3', 'C4', 'C5', 'C6'];

        if (!creditGrades.includes(mathGrade) || !creditGrades.includes(englishGrade)) {
            const proceed = confirm(
                '⚠️ Warning: Your Mathematics or English Language grade appears to be below a credit pass (C6).\n\n' +
                'The system will reject applications without credit passes in these subjects.\n\n' +
                'Do you wish to proceed anyway?'
            );
            if (!proceed) return;
        }

        submitBtn.disabled     = true;
        submitBtn.textContent  = '⏳ Submitting & Running OCR Verification…';

        const formData = new FormData(form);
        formData.append('applicant_id', applicantId);

        try {
            const token    = localStorage.getItem('auth_token');
            const response = await fetch(`${API_BASE}/apply`, {
                method:  'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body:    formData,
            });

            const data = await response.json();

            if (response.ok) {
                lastSubmissionData = data;
                localStorage.setItem('has_applied', 'true');
                localStorage.setItem('screening_status', data.screening_status);
                if (data.application_ref) {
                    localStorage.setItem('application_ref', data.application_ref);
                }
                showResultModal(data);
                showSubmittedState(data.screening_status);
            } else {
                submitError.textContent = data.error || 'Submission failed. Please check your inputs and try again.';
                submitError.classList.remove('hidden');
                submitBtn.disabled    = false;
                submitBtn.textContent = 'Submit Application for AI Screening →';
            }
        } catch (err) {
            submitError.textContent = 'Network error. Ensure the Flask backend is running on port 5000.';
            submitError.classList.remove('hidden');
            submitBtn.disabled    = false;
            submitBtn.textContent = 'Submit Application for AI Screening →';
        }
    });

    // --- Close Modal ---
    document.getElementById('closeModal').addEventListener('click', () => {
        document.getElementById('resultModal').classList.add('hidden');
    });

    // --- Print Receipt ---
    document.getElementById('printReceiptBtn').addEventListener('click', () => {
        if (lastSubmissionData) {
            printReceipt(lastSubmissionData);
        }
    });
});

// =============================================
//  FILE UPLOAD SETUP
// =============================================
function setupFileUpload(inputId, dropZoneId, displayId) {
    const input    = document.getElementById(inputId);
    const dropZone = document.getElementById(dropZoneId);
    const display  = document.getElementById(displayId);

    if (!input || !dropZone) return;

    dropZone.addEventListener('click', (e) => {
        if (e.target !== input) input.click();
    });

    input.addEventListener('change', () => {
        if (input.files.length > 0) {
            const file   = input.files[0];
            const sizeMB = (file.size / (1024 * 1024)).toFixed(2);

            if (file.size > 5 * 1024 * 1024) {
                display.textContent = '❌ File too large. Maximum size is 5MB.';
                display.style.color = 'var(--danger)';
                input.value = '';
                return;
            }

            display.textContent          = `✅ ${file.name} (${sizeMB} MB)`;
            display.style.color          = 'var(--success)';
            dropZone.style.borderColor   = 'var(--success)';
            dropZone.style.background    = 'var(--success-bg)';
        }
    });
}

// =============================================
//  SHOW SUBMITTED STATE
// =============================================
function showSubmittedState(status) {
    document.getElementById('applicationFormCard').classList.add('hidden');
    document.getElementById('alreadySubmittedCard').classList.remove('hidden');

    const pill = document.getElementById('appStatusPill');
    pill.textContent   = '✅ Application Submitted';
    pill.style.background   = 'rgba(26,124,74,0.25)';
    pill.style.borderColor  = 'var(--success)';
    pill.style.color        = 'var(--success)';

    renderStatusBadge(status);
}

// =============================================
//  RESULT MODAL
// =============================================
function showResultModal(data) {
    const modal       = document.getElementById('resultModal');
    const icon        = document.getElementById('modalIcon');
    const title       = document.getElementById('modalTitle');
    const message     = document.getElementById('modalMessage');
    const badge       = document.getElementById('modalStatusBadge');
    const jambInfo    = document.getElementById('jambOcrInfo');
    const olevelInfo  = document.getElementById('olevelVerifyInfo');
    const appRefBlock = document.getElementById('appRefBlock');
    const appRefNum   = document.getElementById('appRefNumber');
    const discWarn    = document.getElementById('discrepancyWarning');
    const discText    = document.getElementById('discrepancyText');
    const yearWarn    = document.getElementById('jambYearWarning');

    const status    = data.screening_status;
    const statusMap = {
        'QUALIFIED': {
            icon: '🎉',
            title: 'Pre-Screening Passed — Qualified',
            badgeClass: 'status-qualified',
            msg: `Congratulations! Your application has passed the AI pre-screening. <strong>${data.reason}</strong> Your file will proceed to the Academic Board for final review.`
        },
        'BORDERLINE': {
            icon: '⚠️',
            title: 'Borderline — Under Further Review',
            badgeClass: 'status-alternative',
            msg: `Your application is flagged as <strong>borderline</strong>. ${data.reason} The Admissions Committee will review your case.`
        },
        'ALTERNATIVE_COURSE': {
            icon: '🔄',
            title: 'Alternative Programme Recommended',
            badgeClass: 'status-alternative',
            msg: `${data.reason} The Admissions Board will review your profile for possible placement into the recommended programme.`
        },
        'REJECTED': {
            icon: '❌',
            title: 'Application Not Successful',
            badgeClass: 'status-rejected',
            msg: `We regret that your application did not meet the minimum pre-screening requirements. <strong>${data.reason}</strong> You may re-apply in the next admission cycle.`
        }
    };

    const config = statusMap[status] || {
        icon: '📋', title: 'Application Submitted',
        badgeClass: 'status-pending',
        msg: 'Your application has been received and is being processed.'
    };

    icon.textContent    = config.icon;
    title.textContent   = config.title;
    message.innerHTML   = config.msg;
    badge.innerHTML     = `<span class="status-badge ${config.badgeClass}">${status}</span>`;

    // Application Reference
    if (data.application_ref) {
        appRefBlock.style.display = 'block';
        appRefNum.textContent     = data.application_ref;
    }

    // Score Discrepancy Warning
    if (data.score_discrepancy_flagged) {
        discWarn.style.display = 'block';
        discText.textContent   = data.score_discrepancy_reason || 'Score discrepancy detected. Please contact the Admissions Office.';
    }

    // JAMB Year Warning
    if (data.jamb_year_warning) {
        yearWarn.style.display = 'block';
    }

    // JAMB OCR Info
    if (data.jamb_ocr_score !== null && data.jamb_ocr_score !== undefined) {
        jambInfo.style.display = 'block';
        jambInfo.innerHTML = `
            <strong>🤖 JAMB OCR Verification Report</strong><br>
            Exam Year: <strong>${data.jamb_year || 'N/A'}</strong> |
            Extracted Score: <strong>${data.jamb_ocr_score}</strong> |
            Verified: <strong>${data.jamb_verified ? '✅ Yes' : '⚠️ No'}</strong><br>
            ${data.jamb_ocr_reason ? `<em>${data.jamb_ocr_reason}</em>` : ''}
        `;
    }

    // O'Level Verification Summary
    if (data.olevel_type) {
        olevelInfo.style.display = 'block';
        const waecStatus = data.waec_verified ? '✅ Verified' : (data.olevel_type === 'NECO' ? '—' : '⚠️ Unverified');
        const necoStatus = data.neco_verified ? '✅ Verified' : (data.olevel_type === 'WAEC' ? '—' : '⚠️ Unverified');
        olevelInfo.innerHTML = `
            <strong>📋 O'Level Verification Summary</strong><br>
            Sitting Type: <strong>${data.olevel_type}</strong><br>
            WAEC: <strong>${waecStatus}</strong> &nbsp;|&nbsp; NECO: <strong>${necoStatus}</strong>
            ${data.olevel_flags && data.olevel_flags.length > 0
                ? `<br><em style="color:var(--warning)">Note: ${data.olevel_flags.join('; ')}</em>`
                : ''}
        `;
    }

    modal.classList.remove('hidden');
}

// =============================================
//  PRINT RECEIPT
// =============================================
function printReceipt(data) {
    const applicantName = localStorage.getItem('applicant_name') || 'Applicant';
    const now           = new Date().toLocaleString('en-NG', { dateStyle: 'long', timeStyle: 'short' });

    const w = window.open('', '_blank', 'width=700,height=900');
    w.document.write(`
        <!DOCTYPE html><html><head>
        <title>Application Receipt — ${data.application_ref}</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 40px; color: #1a1a2e; font-size: 13px; }
            h1 { font-size: 1.4rem; color: #1a1a2e; margin-bottom: 4px; }
            h2 { font-size: 1rem; color: #555; font-weight: normal; margin-bottom: 24px; }
            .ref { font-size: 1.3rem; font-weight: bold; color: #1a237e; font-family: monospace;
                   background: #f5f5f5; padding: 8px 16px; border-radius: 6px; display: inline-block; margin-bottom: 20px; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            th { background: #1a237e; color: white; padding: 8px 12px; text-align: left; font-size: 12px; }
            td { padding: 7px 12px; border-bottom: 1px solid #eee; }
            tr:nth-child(even) td { background: #f9f9f9; }
            .badge { display: inline-block; padding: 3px 10px; border-radius: 999px; font-weight: bold; font-size: 11px; }
            .qualified { background: #d1fae5; color: #065f46; }
            .borderline { background: #fef9c3; color: #713f12; }
            .rejected { background: #fee2e2; color: #7f1d1d; }
            .footer { margin-top: 30px; font-size: 11px; color: #888; border-top: 1px solid #eee; padding-top: 12px; }
            @media print { body { padding: 20px; } }
        </style>
        </head><body>
        <h1>Bingham University — Hybrid Admission System</h1>
        <h2>2025/2026 Academic Session — Application Receipt</h2>
        <div class="ref">${data.application_ref || 'N/A'}</div>
        <table>
            <tr><th colspan="2">Applicant Information</th></tr>
            <tr><td>Full Name</td><td>${applicantName}</td></tr>
            <tr><td>Submission Date & Time</td><td>${now}</td></tr>
            <tr><th colspan="2">Academic Details</th></tr>
            <tr><td>JAMB Exam Year</td><td>${data.jamb_year || 'N/A'}</td></tr>
            <tr><td>OCR-Extracted UTME Score</td><td>${data.jamb_ocr_score || 'N/A'}</td></tr>
            <tr><td>JAMB Result Verified</td><td>${data.jamb_verified ? 'Yes ✅' : 'No ⚠️'}</td></tr>
            <tr><td>Score Discrepancy</td><td>${data.score_discrepancy_flagged ? '⚠️ Flagged — Admin Review Required' : 'None'}</td></tr>
            <tr><td>O\'Level Sitting Type</td><td>${data.olevel_type || 'N/A'}</td></tr>
            <tr><td>WAEC Verified</td><td>${data.waec_verified ? 'Yes ✅' : '—'}</td></tr>
            <tr><td>NECO Verified</td><td>${data.neco_verified ? 'Yes ✅' : '—'}</td></tr>
            <tr><th colspan="2">Screening Outcome</th></tr>
            <tr><td>AI Screening Status</td><td>
                <span class="badge ${(data.screening_status || '').toLowerCase()}">${data.screening_status || 'N/A'}</span>
            </td></tr>
            <tr><td>Reason</td><td>${data.reason || 'N/A'}</td></tr>
            <tr><td>ML Prediction</td><td>${data.ml_prediction || 'N/A'} ${data.ml_confidence ? '(' + data.ml_confidence + '% confidence)' : ''}</td></tr>
        </table>
        <div class="footer">
            This receipt is computer-generated and valid without a signature.<br>
            Keep your reference number <strong>${data.application_ref}</strong> for all future correspondence with the Admissions Office.<br>
            Bingham University, Auta-Balefi, Nasarawa State, Nigeria | admissions@binghamuni.edu.ng
        </div>
        </body></html>
    `);
    w.document.close();
    setTimeout(() => w.print(), 500);
}

// =============================================
//  STATUS BADGE IN SUBMITTED CARD
// =============================================
function renderStatusBadge(status) {
    const container = document.getElementById('screeningResultBadge');
    const cls = {
        'QUALIFIED':         'status-qualified',
        'BORDERLINE':        'status-alternative',
        'ALTERNATIVE_COURSE':'status-alternative',
        'REJECTED':          'status-rejected',
    }[status] || 'status-pending';

    const ref = localStorage.getItem('application_ref');
    container.innerHTML = `
        <p style="font-size:0.85rem; color:var(--gray-600); margin-bottom:0.5rem;">Screening Outcome:</p>
        <span class="status-badge ${cls}">${status || 'PENDING'}</span>
        ${ref ? `<p style="font-size:0.8rem; color:var(--gray-500); margin-top:0.75rem;">Reference: <strong style="color:var(--navy); font-family:monospace;">${ref}</strong></p>` : ''}
    `;
}

// Handle Theme Toggle
document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-theme');
            const theme = document.body.classList.contains('dark-theme') ? 'dark' : 'light';
            localStorage.setItem('theme', theme);
        });
    }
});
