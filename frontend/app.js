/* ==========================================================================
   Investment Research Assistant v1.0 — Application Logic
   Plain ES6, no framework. Handles SPA navigation and prepares FastAPI
   integration points (fetch functions + load functions per page).
   Nothing here talks to a real backend yet — that's the next phase.
   ========================================================================== */

const API_BASE_URL = "/api"; // will point to the FastAPI backend once deployed

// Tracks which company is currently "active" across the whole app
let activeCompanyId = null;

/* ---------------------------------------------------------------------
   NAVIGATION
   --------------------------------------------------------------------- */

function showPage(pageId) {
    document.querySelectorAll(".page").forEach(page => {
        page.classList.toggle("active", page.id === pageId);
    });
    document.querySelectorAll(".nav-item").forEach(button => {
        button.classList.toggle("active", button.dataset.page === pageId);
    });

    // Route to the correct load function for the page being shown
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

/* ---------------------------------------------------------------------
   FASTAPI FETCH FUNCTIONS
   These are the ONLY places that will eventually talk to the backend.
   Every one currently returns placeholder data or does nothing, so the
   UI can be built and tested before the API exists.
   --------------------------------------------------------------------- */

async function apiGet(path) {
    // Placeholder implementation. Once FastAPI exists, this becomes:
    // const response = await fetch(`${API_BASE_URL}${path}`);
    // return response.json();
    console.log(`[stub] GET ${API_BASE_URL}${path}`);
    return null;
}

async function apiPost(path, body) {
    // Placeholder implementation. Once FastAPI exists, this becomes:
    // const response = await fetch(`${API_BASE_URL}${path}`, {
    //     method: "POST",
    //     headers: { "Content-Type": "application/json" },
    //     body: JSON.stringify(body),
    // });
    // return response.json();
    console.log(`[stub] POST ${API_BASE_URL}${path}`, body);
    return null;
}

function fetchCompanies(filters = {}) {
    return apiGet("/companies");
}

function fetchCompany(companyId) {
    return apiGet(`/companies/${companyId}`);
}

function fetchIncomeStatement(companyId) {
    return apiGet(`/companies/${companyId}/income-statement`);
}

function fetchBalanceSheet(companyId) {
    return apiGet(`/companies/${companyId}/balance-sheet`);
}

function fetchCashFlow(companyId) {
    return apiGet(`/companies/${companyId}/cash-flow`);
}

function fetchRatios(companyId) {
    return apiGet(`/companies/${companyId}/ratios`);
}

function fetchVerification(companyId) {
    return apiGet(`/companies/${companyId}/verification`);
}

function submitVerificationCorrection(figureId, correctedValue) {
    return apiPost(`/figures/${figureId}/correct`, { corrected_value: correctedValue });
}

function approveFigure(figureId) {
    return apiPost(`/figures/${figureId}/verify`, {});
}

function fetchComparison(companyIds) {
    return apiGet(`/compare?ids=${companyIds.join(",")}`);
}

function fetchReports() {
    return apiGet("/reports");
}

function generateReport(companyId) {
    return apiPost("/reports/generate", { company_id: companyId });
}

/* ---------------------------------------------------------------------
   PAGE LOAD FUNCTIONS
   Each corresponds to one sidebar section. Currently these just call
   their fetch function (which logs a stub call) — real DOM population
   will be filled in once FastAPI returns real data.
   --------------------------------------------------------------------- */

async function loadDashboard() {
    // Future: fetchCompanies(), fetchVerification(), etc. to populate cards
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
            <td><button class="btn btn-secondary" onclick="setActiveCompany(${company.id}, '${company.name}')">Select</button></td>
        </tr>
    `).join("");
}

function setActiveCompany(companyId, companyName) {
    activeCompanyId = companyId;
    document.getElementById("active-company-name").textContent = companyName;
}

async function loadVerification() {
    if (!activeCompanyId) return;
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
            <td><input type="number" value="${figure.corrected_value ?? ''}" data-id="${figure.id}" class="correction-input"></td>
            <td class="${figure.verified ? 'status-verified' : 'status-unverified'}">${figure.verified ? "✓ Verified" : "⚠ Unverified"}</td>
            <td>
                <button class="btn btn-primary" onclick="approveFigure(${figure.id})">Accept</button>
                <button class="btn btn-secondary" onclick="editFigure(${figure.id})">Edit</button>
                <button class="btn btn-danger" onclick="rejectFigure(${figure.id})">Reject</button>
            </td>
        </tr>
    `).join("");
}

function editFigure(figureId) {
    console.log(`[stub] Edit figure ${figureId}`);
}

function rejectFigure(figureId) {
    console.log(`[stub] Reject figure ${figureId}`);
}

async function loadAnalysis() {
    if (!activeCompanyId) return;
    // Future: await Promise.all([
    //     fetchIncomeStatement(activeCompanyId),
    //     fetchBalanceSheet(activeCompanyId),
    //     fetchCashFlow(activeCompanyId),
    //     fetchRatios(activeCompanyId),
    // ]) and populate each accordion section.
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

/* ---------------------------------------------------------------------
   INITIALISATION
   --------------------------------------------------------------------- */

document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    initAccordion();
    initCompareButton();
    initReportsButton();
    loadDashboard(); // dashboard is the default active page
});
