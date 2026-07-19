/* ==========================================================================
   Investment Research Assistant v1.0 — Application Logic
   ========================================================================== */

const API_BASE_URL = "/api";
let activeCompanyId = null;
let currentDocumentCompanyId = null; // tracks which company's PDF is currently loaded

function showPage(pageId) {
    document.querySelectorAll(".page").forEach(page => {
        page.classList.toggle("active", page.id === pageId);
    });
    document.querySelectorAll(".nav-item").forEach(button => {
        button.classList.toggle("active", button.dataset.page === pageId);
    });

    const loaders = {
        dashboard: loadDashboard,
        companies: loadCompanies,
        verification: loadVerification,
        analysis: loadAnalysis,
        compare: loadCompare,
        reports: loadReports,
        settings: loadSettings,
    };
    if (loaders[pageId]) loaders[pageId]();
}

function initNavigation() {
    document.querySelectorAll(".nav-item").forEach(button => {
        button.addEventListener("click", () => showPage(button.dataset.page));
    });
}

async function apiGet(path) {
    try {
        const response = await fetch(`${API_BASE_URL}${path}`);
        if (!response.ok) throw new Error(`GET ${path} failed: ${response.status}`);
        return await response.json();
    } catch (err) {
        console.error(err);
        return null;
    }
}

async function apiPost(path, body) {
    try {
        const response = await fetch(`${API_BASE_URL}${path}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
        if (!response.ok) throw new Error(`POST ${path} failed: ${response.status}`);
        return await response.json();
    } catch (err) {
        console.error(err);
        return null;
    }
}

function fetchCompanies() { return apiGet("/companies"); }
function fetchCompany(companyId) { return apiGet(`/companies/${companyId}`); }
function fetchIncomeStatement(companyId) { return apiGet(`/companies/${companyId}/income-statement`); }
function fetchBalanceSheet(companyId) { return apiGet(`/companies/${companyId}/balance-sheet`); }
function fetchCashFlow(companyId) { return apiGet(`/companies/${companyId}/cash-flow`); }
function fetchRatios(companyId) { return apiGet(`/companies/${companyId}/ratios`); }
function fetchVerification(companyId) { return apiGet(`/companies/${companyId}/verification`); }
function submitVerificationCorrection(figureId, correctedValue) {
    return apiPost(`/figures/${figureId}/correct`, { corrected_value: correctedValue });
}
function approveFigure(figureId) { return apiPost(`/figures/${figureId}/verify`, {}); }
function fetchComparison(companyIds) { return apiGet(`/compare?ids=${companyIds.join(",")}`); }
function fetchReports() { return apiGet("/reports"); }
function generateReport(companyId) { return apiPost("/reports/generate", { company_id: companyId }); }

async function loadDashboard() {
    console.log("loadDashboard()");
}

async function loadCompanies() {
    const companies = await fetchCompanies();
    renderCompaniesTable(companies || []);
}

function renderCompaniesTable(companies) {
    const tbody = document.getElementById("companies-table-body");
    if (!companies.length) {
        tbody.innerHTML = `<tr><td colspan="6" class="placeholder-row">No companies loaded yet</td></tr>`;
        return;
    }
    tbody.innerHTML = companies.map(company => `
        <tr>
            <td>${company.name}</td>
            <td>${company.company_number}</td>
            <td>${company.industry ?? "—"}</td>
            <td>${company.country ?? "—"}</td>
            <td>${company.verified ? "Verified" : "Unverified"}</td>
            <td><button class="btn btn-secondary" onclick="setActiveCompany(${company.id}, '${company.name}', true)">Select</button></td>
        </tr>
    `).join("");
}

function setActiveCompany(companyId, companyName, navigateToVerification = false) {
    activeCompanyId = companyId;
    document.getElementById("active-company-name").textContent = companyName;
    if (navigateToVerification) {
        showPage("verification");
        const select = document.getElementById("verification-company-select");
        // Ensure the dropdown reflects the newly selected company once populated
        setTimeout(() => { select.value = companyId; }, 0);
    }
}

// Loads BOTH the figures table and the document viewer — call this only
// when the active company has actually changed.
async function loadVerification() {
    const select = document.getElementById("verification-company-select");
    if (select.options.length <= 1) {
        const companies = await fetchCompanies();
        (companies || []).forEach(c => {
            const opt = document.createElement("option");
            opt.value = c.id;
            opt.textContent = c.name;
            select.appendChild(opt);
        });
        select.addEventListener("change", () => {
            if (select.value) {
                setActiveCompany(parseInt(select.value), select.options[select.selectedIndex].text);
                loadVerification();
            }
        });
    }

    if (!activeCompanyId) return;

    await refreshVerificationTable();

    // Only reload the PDF viewer if the company has actually changed —
    // reloading it on every edit/approve was resetting scroll position.
    if (currentDocumentCompanyId !== activeCompanyId) {
        const docInfo = await apiGet(`/companies/${activeCompanyId}/document`);
        const viewer = document.getElementById("verification-document-viewer");
        if (docInfo && docInfo.file_path) {
            const filename = docInfo.file_path.split("/").pop();
            viewer.innerHTML = `<embed src="/documents/${filename}" type="application/pdf" width="100%" height="500px">`;
        } else {
            viewer.innerHTML = `<p class="placeholder-row">No source document found for this company</p>`;
        }
        currentDocumentCompanyId = activeCompanyId;
    }
}

// Refreshes ONLY the figures table — used after an edit/approve action,
// so the PDF viewer is left completely untouched.
async function refreshVerificationTable() {
    const figures = await fetchVerification(activeCompanyId);
    renderVerificationTable(figures || []);
}

function renderVerificationTable(figures) {
    const tbody = document.getElementById("verification-table-body");
    if (!figures.length) {
        tbody.innerHTML = `<tr><td colspan="10" class="placeholder-row">No figures loaded yet</td></tr>`;
        return;
    }
    tbody.innerHTML = figures.map(figure => `
        <tr>
            <td>${figure.statement_type}</td>
            <td>${figure.line_item}</td>
            <td>${figure.fiscal_year_end}</td>
            <td>${figure.original_text ?? "—"}</td>
            <td>${figure.value}</td>
            <td>${figure.ifrs_concept ?? "—"}</td>
            <td>${figure.confidence ?? "—"}</td>
            <td><input type="number" value="${figure.corrected_value ?? ''}" data-id="${figure.id}" class="correction-input" onchange="handleCorrection(${figure.id}, this.value)"></td>
            <td class="${figure.verified ? 'status-verified' : 'status-unverified'}">${figure.verified ? "✓ Verified" : "⚠ Unverified"}</td>
            <td><button class="btn btn-primary" onclick="handleApprove(${figure.id})">Accept</button></td>
        </tr>
    `).join("");
}

async function handleCorrection(figureId, value) {
    const parsedValue = value === "" ? null : parseFloat(value);
    await submitVerificationCorrection(figureId, parsedValue);
    await refreshVerificationTable(); // table only — PDF stays untouched
}

async function handleApprove(figureId) {
    await approveFigure(figureId);
    await refreshVerificationTable(); // table only — PDF stays untouched
}

async function loadAnalysis() {
    if (!activeCompanyId) return;
    console.log("loadAnalysis()", activeCompanyId);
}

function initAccordion() {
    document.querySelectorAll(".accordion-header").forEach(header => {
        header.addEventListener("click", () => {
            const target = document.getElementById(header.dataset.target);
            target.classList.toggle("open");
        });
    });
}

async function loadCompare() {
    const companies = await fetchCompanies();
    const picker = document.getElementById("compare-company-picker");
    if (companies && companies.length) {
        picker.innerHTML = companies.map(c => `<option value="${c.id}">${c.name}</option>`).join("");
    }
}

function initCompareButton() {
    document.getElementById("run-comparison-btn").addEventListener("click", async () => {
        const picker = document.getElementById("compare-company-picker");
        const selectedIds = Array.from(picker.selectedOptions).map(o => o.value);
        if (selectedIds.length < 2) {
            alert("Select at least 2 companies to compare.");
            return;
        }
        const result = await fetchComparison(selectedIds);
        console.log("Comparison result:", result);
    });
}

async function loadReports() {
    const reports = await fetchReports();
    renderReportsHistory(reports || []);
}

function renderReportsHistory(reports) {
    const list = document.getElementById("reports-history-list");
    if (!reports.length) {
        list.innerHTML = `<li class="placeholder-row">No reports generated yet</li>`;
        return;
    }
    list.innerHTML = reports.map(r => `<li>${r.title} — ${r.created_at}</li>`).join("");
}

function initReportsButton() {
    document.getElementById("generate-report-btn").addEventListener("click", async () => {
        if (!activeCompanyId) {
            alert("Select a company first.");
            return;
        }
        await generateReport(activeCompanyId);
        loadReports();
    });
}

async function loadSettings() {
    console.log("loadSettings()");
}

document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    initAccordion();
    initCompareButton();
    initReportsButton();
    loadDashboard();
});
