const API_BASE = 'http://127.0.0.1:5000/api';

document.addEventListener('DOMContentLoaded', () => {
    // --- Auth Guard ---
    const applicantId = localStorage.getItem('applicant_id');
    const applicantName = localStorage.getItem('applicant_name');

    if (!applicantId) {
        window.location.href = 'index.html';
        return;
    }

    // --- Populate Info ---
    document.getElementById('welcomeMessage').textContent = `Welcome, ${applicantName || 'Applicant'}`;
    document.getElementById('sidebarName').textContent = applicantName || 'Applicant';
    document.getElementById('sidebarId').textContent = `#APP-${String(applicantId).padStart(5, '0')}`;

    // If already applied (returned from login), show submitted card
    if (localStorage.getItem('has_applied') === 'true') {
        showSubmittedState(localStorage.getItem('screening_status') || 'PENDING');
    }

    // --- Logout ---
    document.getElementById('logoutBtn').addEventListener('click', () => {
        localStorage.clear();
        window.location.href = 'index.html';
    });

    // --- JAMB File Upload UX ---
    setupFileUpload('jamb_document', 'jambDropZone', 'jambFileDisplay');

    // --- O'Level File Upload UX ---
    setupFileUpload('olevel_document', 'olevelDropZone', 'olevelFileDisplay');

    // --- UTME Score Cross-Check Warning ---
    const declaredInput = document.getElementById('utme_score_declared');
    if (declaredInput) {
        declaredInput.addEventListener('input', () => {
            const val = parseInt(declaredInput.value);
            declaredInput.style.borderColor = (val >= 100 && val <= 400) ? 'var(--success)' : 'var(--danger)';
        });
    }

    // --- Form Submission ---
    const form = document.getElementById('applicationForm');
    const submitBtn = document.getElementById('submitAppBtn');
    const submitError = document.getElementById('submitError');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        submitError.classList.add('hidden');

        // Basic grade credit check warning
        const mathGrade = form.querySelector('[name="o_level_math"]').value;
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

        submitBtn.disabled = true;
        submitBtn.textContent = '⏳ Submitting & Running OCR Verification…';

        const formData = new FormData(form);
        formData.append('applicant_id', applicantId);

        try {
            const token = localStorage.getItem('auth_token');
            const response = await fetch(`${API_BASE}/apply`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData,
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem('has_applied', 'true');
                localStorage.setItem('screening_status', data.screening_status);
                showResultModal(data);
                showSubmittedState(data.screening_status);
            } else {
                submitError.textContent = data.error || 'Submission failed. Please check your inputs and try again.';
                submitError.classList.remove('hidden');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Submit Application for AI Screening →';
            }
        } catch (err) {
            submitError.textContent = 'Network error. Ensure the Flask backend is running on port 5000.';
            submitError.classList.remove('hidden');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Application for AI Screening →';
        }
    });

    // --- Close Modal ---
    document.getElementById('closeModal').addEventListener('click', () => {
        document.getElementById('resultModal').classList.add('hidden');
    });
});

// =============================================
//  FILE UPLOAD SETUP
// =============================================
function setupFileUpload(inputId, dropZoneId, displayId) {
    const input = document.getElementById(inputId);
    const dropZone = document.getElementById(dropZoneId);
    const display = document.getElementById(displayId);

    if (!input || !dropZone) return;

    dropZone.addEventListener('click', (e) => {
        if (e.target !== input) input.click();
    });

    input.addEventListener('change', () => {
        if (input.files.length > 0) {
            const file = input.files[0];
            const sizeMB = (file.size / (1024 * 1024)).toFixed(2);

            if (file.size > 5 * 1024 * 1024) {
                display.textContent = '❌ File too large. Maximum size is 5MB.';
                display.style.color = 'var(--danger)';
                input.value = '';
                return;
            }

            display.textContent = `✅ ${file.name} (${sizeMB} MB)`;
            display.style.color = 'var(--success)';
            dropZone.style.borderColor = 'var(--success)';
            dropZone.style.background = 'var(--success-bg)';
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
    pill.textContent = '✅ Application Submitted';
    pill.style.background = 'rgba(26,124,74,0.25)';
    pill.style.borderColor = 'var(--success)';
    pill.style.color = 'var(--success)';

    renderStatusBadge(status);
}

// =============================================
//  RESULT MODAL
// =============================================
function showResultModal(data) {
    const modal = document.getElementById('resultModal');
    const icon = document.getElementById('modalIcon');
    const title = document.getElementById('modalTitle');
    const message = document.getElementById('modalMessage');
    const badge = document.getElementById('modalStatusBadge');
    const jambInfo = document.getElementById('jambOcrInfo');

    const status = data.screening_status;
    const statusMap = {
        'QUALIFIED': {
            icon: '🎉',
            title: 'Pre-Screening Passed — Qualified',
            badgeClass: 'status-qualified',
            msg: `Congratulations! Your application has passed the AI pre-screening. <strong>${data.reason}</strong> Your file will proceed to the Academic Board for final review. An official notification will be sent to your registered email.`
        },
        'BORDERLINE': {
            icon: '⚠️',
            title: 'Borderline — Under Further Review',
            badgeClass: 'status-alternative',
            msg: `Your application is flagged as <strong>borderline</strong>. ${data.reason} The Admissions Committee will review your case. Kindly await further communication.`
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
            msg: `We regret that your application did not meet the minimum pre-screening requirements. <strong>${data.reason}</strong> You may re-apply in the next admission cycle. Contact the Admissions Office for guidance.`
        }
    };

    const config = statusMap[status] || {
        icon: '📋', title: 'Application Submitted',
        badgeClass: 'status-pending',
        msg: `Your application is being processed. Reference: APP-${String(data.applicant_id).padStart(5, '0')}.`
    };

    icon.textContent = config.icon;
    title.textContent = config.title;
    message.innerHTML = config.msg;
    badge.innerHTML = `<span class="status-badge ${config.badgeClass}">${status}</span>`;

    // JAMB OCR result info
    if (data.jamb_ocr_score !== null && data.jamb_ocr_score !== undefined) {
        jambInfo.style.display = 'block';
        jambInfo.innerHTML = `
            <strong>🤖 JAMB OCR Verification Report</strong><br>
            Extracted Score: <strong>${data.jamb_ocr_score}</strong> |
            Verified: <strong>${data.jamb_verified ? '✅ Yes' : '⚠️ No'}</strong><br>
            ${data.jamb_ocr_reason ? `<em>${data.jamb_ocr_reason}</em>` : ''}
        `;
    }

    modal.classList.remove('hidden');
}

// =============================================
//  STATUS BADGE IN SUBMITTED CARD
// =============================================
function renderStatusBadge(status) {
    const container = document.getElementById('screeningResultBadge');
    const cls = {
        'QUALIFIED': 'status-qualified',
        'BORDERLINE': 'status-alternative',
        'ALTERNATIVE_COURSE': 'status-alternative',
        'REJECTED': 'status-rejected',
    }[status] || 'status-pending';

    container.innerHTML = `
        <p style="font-size:0.85rem; color:var(--gray-600); margin-bottom:0.5rem;">Screening Outcome:</p>
        <span class="status-badge ${cls}">${status || 'PENDING'}</span>
    `;
}
