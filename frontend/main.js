// PLACEHOLDER DATA — stands in for what FastAPI will eventually return.
// Shape matches the real FinancialFigure fields we've already built:
// statement_type, line_item, fiscal_year_end, value, corrected_value, verified.
const PLACEHOLDER_FIGURES = [
    { id: 1, statement_type: "income_statement", line_item: "revenue", fiscal_year_end: "28 February 2026", value: 73712, corrected_value: null, verified: false },
    { id: 2, statement_type: "income_statement", line_item: "cost_of_sales", fiscal_year_end: "28 February 2026", value: -67375, corrected_value: null, verified: false },
    { id: 3, statement_type: "balance_sheet", line_item: "equity", fiscal_year_end: "28 February 2026", value: 11457, corrected_value: null, verified: true },
];

function renderFigures(figures) {
    const tbody = document.getElementById("figures-body");
    tbody.innerHTML = "";

    figures.forEach(figure => {
        const row = document.createElement("tr");
        const effectiveValue = figure.corrected_value !== null ? figure.corrected_value : figure.value;

        row.innerHTML = `
            <td>${figure.statement_type}</td>
            <td>${figure.line_item}</td>
            <td>${figure.fiscal_year_end}</td>
            <td>${figure.value}</td>
            <td><input type="number" value="${figure.corrected_value ?? ''}" data-id="${figure.id}" class="correction-input"></td>
            <td class="${figure.verified ? 'status-verified' : 'status-unverified'}">${figure.verified ? '✓ Verified' : '⚠ Unverified'}</td>
            <td><button class="approve-btn" data-id="${figure.id}">Approve</button></td>
        `;
        tbody.appendChild(row);
    });
}

document.getElementById("figures-body").addEventListener("click", (event) => {
    if (event.target.classList.contains("approve-btn")) {
        const id = event.target.dataset.id;
        console.log(`Would call: POST /api/figures/${id}/verify`);
        // Real version will call FastAPI here once the backend exists.
    }
});

renderFigures(PLACEHOLDER_FIGURES);
