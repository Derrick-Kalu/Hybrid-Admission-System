const API_BASE = 'http://127.0.0.1:5000/api';

let allApplications = [];
let pendingDecision = null; // { id, decision }

// =============================================
//  LOAD & RENDER APPLICATIONS
// =============================================
async function loadApplications() {
    try {
        // Show premium loading spinner
        document.getElementById('applicationsTableBody').innerHTML = `
            <tr>
                <td colspan="9" style="text-align:center; padding:0;">
                    <div class="premium-loading-container">
                        <div class="premium-spinner"></div>
                        <div class="loading-text">Loading Academic Records...</div>
                    </div>
                </td>
            </tr>`;

        const token = localStorage.getItem('auth_token');
        const response = await fetch(`${API_BASE}/admin/applications`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) throw new Error('Failed to fetch');
        allApplications = await response.json();
        renderStats(allApplications);
        renderTable(allApplications);
    } catch (error) {
        document.getElementById('applicationsTableBody').innerHTML = `
            <tr>
                <td colspan="9" style="text-align:center; padding:3rem; color:var(--danger);">
                    <div style="font-size:2rem; margin-bottom:0.5rem;">⚠️</div>
                    Failed to load applications. Ensure the backend is running on port 5000.
                </td>
            </tr>`;
    }
}

// =============================================
//  RENDER STATS ROW
// =============================================
function renderStats(apps) {
    const total = apps.length;
    const qualified = apps.filter(a => a.screening_status === 'QUALIFIED').length;
    const borderline = apps.filter(a => a.screening_status === 'BORDERLINE').length;
    const rejected = apps.filter(a => a.screening_status === 'REJECTED').length;
    const pending = apps.filter(a => a.admin_status === 'PENDING_APPROVAL').length;

    document.getElementById('statsRow').innerHTML = `
        <span>Total: <strong style="color:var(--navy)">${total}</strong></span>
        <span style="color:var(--success)">✅ Qualified: <strong>${qualified}</strong></span>
        <span style="color:var(--warning)">⚠️ Borderline: <strong>${borderline}</strong></span>
        <span style="color:var(--danger)">❌ Rejected: <strong>${rejected}</strong></span>
        <span style="color:var(--info)">⏳ Pending Review: <strong>${pending}</strong></span>
    `;
}

// =============================================
//  RENDER TABLE
// =============================================
function renderTable(apps) {
    const tbody = document.getElementById('applicationsTableBody');

    if (apps.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" style="text-align:center; padding:3rem; color:var(--gray-400);">
                    <div style="font-size:2rem; margin-bottom:0.5rem;">📭</div>
                    No applications match your filter.
                </td>
            </tr>`;
        return;
    }

    tbody.innerHTML = '';

    apps.forEach(app => {
        const screeningClass = {
            'QUALIFIED': 'status-qualified',
            'BORDERLINE': 'status-alternative',
            'ALTERNATIVE_COURSE': 'status-alternative',
            'REJECTED': 'status-rejected',
        }[app.screening_status] || 'status-pending';

        const adminClass = {
            'APPROVED': 'status-qualified',
            'REJECTED': 'status-rejected',
            'PENDING_APPROVAL': 'status-pending',
        }[app.admin_status] || 'status-pending';

        const mlClass = {
            'QUALIFIED': 'status-qualified',
            'BORDERLINE': 'status-alternative',
            'ALTERNATIVE_COURSE': 'status-alternative',
            'REJECTED': 'status-rejected',
            'N/A': 'status-pending',
        }[app.ml_prediction] || 'status-pending';

        const isDecided = app.admin_status !== 'PENDING_APPROVAL';
        
        let jambYearContent = `${app.jamb_year || 'N/A'}`;
        if (app.jamb_year_warning) {
            jambYearContent += `<br><span class="warning-badge" title="Result approaching 3-year expiry limit">Expiring</span>`;
        }

        let olevelContent = `${app.olevel_type || 'N/A'}`;
        if (app.olevel_type === 'BOTH') {
            olevelContent = `WAEC + NECO`;
        }

        let ruleEngineContent = `<span class="status-badge ${screeningClass}">${app.screening_status}</span>`;
        if (app.score_discrepancy_flagged) {
            ruleEngineContent += `<br><span class="warning-badge" title="${app.score_discrepancy_delta} marks difference from OCR">⚠️ Score Delta: ${app.score_discrepancy_delta}</span>`;
        }

        const tr = document.createElement('tr');
        tr.dataset.status = app.screening_status;
        tr.innerHTML = `
            <td>
                <strong style="color:var(--navy)">${app.application_ref || ('APP-' + String(app.id).padStart(5, '0'))}</strong><br>
                <span style="font-size: 0.75rem; color: var(--gray-500);">${app.jamb_reg_number}</span>
            </td>
            <td>${app.full_name}</td>
            <td>${app.course_applied}</td>
            <td>${jambYearContent}</td>
            <td>${olevelContent}</td>
            <td>${ruleEngineContent}</td>
            <td><span class="status-badge ${mlClass}" style="font-size:0.72rem;">${app.ml_prediction}</span>
                <div style="display:flex; align-items:center; gap:0.5rem; margin-top:0.3rem;">
                    <div style="background:var(--gray-200); border-radius:999px; height:4px; width:40px; overflow:hidden;">
                        <div style="background:var(--navy); height:100%; width:${app.ml_confidence}%;"></div>
                    </div>
                    <span style="font-size:0.7rem;">${app.ml_confidence}%</span>
                </div>
            </td>
            <td><span class="status-badge ${adminClass}">${app.admin_status.replace('_', ' ')}</span></td>
            <td>
                ${isDecided
                    ? `<span style="font-size:0.78rem; color:var(--gray-400); font-style:italic;">Decision recorded</span>`
                    : `<button class="action-btn btn-approve" onclick="openDecisionModal('${app.id}', '${app.full_name}', 'APPROVED')">✅ Approve</button>
                       <button class="action-btn btn-reject" onclick="openDecisionModal('${app.id}', '${app.full_name}', 'REJECTED')">❌ Reject</button>`
                }
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// =============================================
//  DECISION MODAL
// =============================================
function openDecisionModal(id, name, decision) {
    pendingDecision = { id, decision };
    const modal = document.getElementById('decisionModal');
    const icon = document.getElementById('decisionIcon');
    const title = document.getElementById('decisionTitle');
    const msg = document.getElementById('decisionMessage');
    const confirmBtn = document.getElementById('confirmDecisionBtn');
    
    const remarksInput = document.getElementById('remarksInput');
    const remarksAsterisk = document.getElementById('remarksAsterisk');
    const remarksHint = document.getElementById('remarksHint');

    if (decision === 'APPROVED') {
        icon.textContent = '✅';
        title.textContent = 'Confirm Approval';
        msg.innerHTML = `You are about to <strong>APPROVE</strong> the application of <strong>${name}</strong>. This action will be recorded and the applicant will be notified.`;
        confirmBtn.style.background = 'var(--success)';
        
        remarksAsterisk.style.display = 'none';
        remarksHint.style.display = 'none';
        remarksInput.required = false;
        remarksInput.classList.remove('input-error');
    } else {
        icon.textContent = '❌';
        title.textContent = 'Confirm Rejection';
        msg.innerHTML = `You are about to <strong>REJECT</strong> the application of <strong>${name}</strong>. Please provide a justification in the remarks field below.`;
        confirmBtn.style.background = 'var(--danger)';
        
        remarksAsterisk.style.display = 'inline';
        remarksHint.style.display = 'block';
        remarksInput.required = true;
    }

    remarksInput.value = '';
    modal.classList.remove('hidden');
}

document.getElementById('confirmDecisionBtn').addEventListener('click', async () => {
    if (!pendingDecision) return;

    const remarksInput = document.getElementById('remarksInput');
    let remarks = remarksInput.value.trim();
    
    if (pendingDecision.decision === 'REJECTED' && !remarks) {
        remarksInput.classList.add('input-error');
        // Simple shake animation effect could be added here
        remarksInput.style.border = '1px solid var(--danger)';
        setTimeout(() => { remarksInput.style.border = ''; }, 2000);
        return; // Prevent submission without remarks
    }

    if (pendingDecision.decision === 'APPROVED' && !remarks) {
        remarks = `Approved by Admin`;
    }

    try {
        const token = localStorage.getItem('auth_token');
        const res = await fetch(`${API_BASE}/admin/approve/${pendingDecision.id}`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ decision: pendingDecision.decision, remarks })
        });

        if (res.ok) {
            document.getElementById('decisionModal').classList.add('hidden');
            pendingDecision = null;
            await loadApplications();
        } else {
            const data = await res.json();
            alert(data.error || 'Failed to record decision. Please try again.');
        }
    } catch (err) {
        alert('Network error. Ensure the backend is running.');
    }
});

document.getElementById('cancelDecisionBtn').addEventListener('click', () => {
    document.getElementById('decisionModal').classList.add('hidden');
    pendingDecision = null;
});

// =============================================
//  FILTER BUTTONS
// =============================================
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const filter = btn.dataset.filter;
        const filtered = filter === 'all'
            ? allApplications
            : allApplications.filter(a => a.screening_status === filter);

        renderTable(filtered);
    });
});

// =============================================
//  SEARCH
// =============================================
document.getElementById('searchInput').addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    const filtered = allApplications.filter(a =>
        a.full_name.toLowerCase().includes(query) ||
        a.course_applied.toLowerCase().includes(query) ||
        (a.application_ref && a.application_ref.toLowerCase().includes(query)) ||
        a.jamb_reg_number.toLowerCase().includes(query)
    );
    renderTable(filtered);
});

// =============================================
//  REFRESH
// =============================================
document.getElementById('navRefresh').addEventListener('click', (e) => {
    e.preventDefault();
    loadApplications();
});

// =============================================
//  EXPORT TO CSV
// =============================================
document.getElementById('exportBtn').addEventListener('click', (e) => {
    e.preventDefault();
    if (allApplications.length === 0) {
        alert("No applications to export.");
        return;
    }

    // Define CSV headers
    const headers = [
        "Reference Number",
        "Full Name",
        "JAMB Reg Number",
        "Programme Applied",
        "JAMB Year",
        "UTME Score",
        "Discrepancy Flag",
        "JAMB Verified",
        "O'Level Type",
        "WAEC Verified",
        "NECO Verified",
        "Rule Engine Status",
        "AI Prediction",
        "AI Confidence (%)",
        "Admin Decision",
        "Admin Remarks"
    ];

    // Map data to CSV rows
    const rows = allApplications.map(app => [
        app.application_ref || `APP-${String(app.id).padStart(5, '0')}`,
        `"${app.full_name}"`,
        app.jamb_reg_number,
        `"${app.course_applied}"`,
        app.jamb_year || "N/A",
        app.utme_score || "N/A",
        app.score_discrepancy_flagged ? "Yes" : "No",
        app.jamb_ocr_verified ? "Yes" : "No",
        app.olevel_type || "N/A",
        app.waec_ocr_verified ? "Yes" : "No",
        app.neco_ocr_verified ? "Yes" : "No",
        app.screening_status,
        app.ml_prediction,
        app.ml_confidence,
        app.admin_status,
        `"${app.admin_remarks || ''}"`
    ]);

    // Combine headers and rows
    const csvContent = [
        headers.join(","),
        ...rows.map(row => row.join(","))
    ].join("\n");

    // Create and trigger download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `Bingham_Admissions_Export_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});

// --- Logout ---
document.getElementById('logoutBtn').addEventListener('click', () => {
    localStorage.clear();
    window.location.href = 'index.html';
});

// Handle Theme Toggle
const themeToggle = document.getElementById('themeToggle');
if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-theme');
        const theme = document.body.classList.contains('dark-theme') ? 'dark' : 'light';
        localStorage.setItem('theme', theme);
    });
}

// =============================================
//  INIT
// =============================================
loadApplications();
