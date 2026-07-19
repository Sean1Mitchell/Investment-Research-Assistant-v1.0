"""
FastAPI backend for Investment Research Assistant v1.0.
Serves the frontend (static files) and exposes REST endpoints matching
the fetch functions already defined in frontend/app.js.
"""

import sys, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "database"))

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker

from database import Company, FinancialFigure, SourceDocument, engine

app = FastAPI(title="Investment Research Assistant API")

Session = sessionmaker(bind=engine)


def get_session():
    return Session()


# --------------------------------------------------------------------
# Companies
# --------------------------------------------------------------------

@app.get("/api/companies")
def list_companies():
    session = get_session()
    companies = session.query(Company).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "company_number": c.company_number,
            "industry": None,
            "country": None,
            "verified": any(f.verified for f in c.financials) if c.financials else False,
        }
        for c in companies
    ]


@app.get("/api/companies/{company_id}")
def get_company(company_id: int):
    session = get_session()
    company = session.query(Company).filter_by(id=company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return {
        "id": company.id,
        "name": company.name,
        "company_number": company.company_number,
        "incorporation_date": company.incorporation_date,
        "registered_address": company.registered_address,
        "investor_relations_url": company.investor_relations_url,
    }


# --------------------------------------------------------------------
# Statements
# --------------------------------------------------------------------

def _figures_for_statement(session, company_id, statement_type):
    figures = session.query(FinancialFigure).filter_by(
        company_id=company_id, statement_type=statement_type
    ).all()

    by_line_item = {}
    for f in figures:
        by_line_item.setdefault(f.line_item, {})[f.fiscal_year_end] = f.effective_value
    return by_line_item


@app.get("/api/companies/{company_id}/income-statement")
def get_income_statement(company_id: int):
    session = get_session()
    return _figures_for_statement(session, company_id, "income_statement")


@app.get("/api/companies/{company_id}/balance-sheet")
def get_balance_sheet(company_id: int):
    session = get_session()
    return _figures_for_statement(session, company_id, "balance_sheet")


@app.get("/api/companies/{company_id}/cash-flow")
def get_cash_flow(company_id: int):
    session = get_session()
    return _figures_for_statement(session, company_id, "cash_flow")


@app.get("/api/companies/{company_id}/ratios")
def get_ratios(company_id: int):
    return {}


# --------------------------------------------------------------------
# Verification
# --------------------------------------------------------------------

@app.get("/api/companies/{company_id}/verification")
def get_verification_data(company_id: int):
    session = get_session()
    figures = session.query(FinancialFigure).filter_by(company_id=company_id).all()
    return [
        {
            "id": f.id,
            "statement_type": f.statement_type,
            "line_item": f.line_item,
            "fiscal_year_end": f.fiscal_year_end,
            "value": f.value,
            "corrected_value": f.corrected_value,
            "verified": f.verified,
            "original_text": None,
            "ifrs_concept": None,
            "confidence": None,
        }
        for f in figures
    ]


class CorrectionPayload(BaseModel):
    corrected_value: float


@app.post("/api/figures/{figure_id}/correct")
def correct_figure(figure_id: int, payload: CorrectionPayload):
    session = get_session()
    figure = session.query(FinancialFigure).filter_by(id=figure_id).first()
    if not figure:
        raise HTTPException(status_code=404, detail="Figure not found")
    figure.corrected_value = payload.corrected_value
    session.commit()
    return {"id": figure.id, "corrected_value": figure.corrected_value}


@app.post("/api/figures/{figure_id}/verify")
def verify_figure(figure_id: int):
    session = get_session()
    figure = session.query(FinancialFigure).filter_by(id=figure_id).first()
    if not figure:
        raise HTTPException(status_code=404, detail="Figure not found")
    figure.verified = True
    session.commit()
    return {"id": figure.id, "verified": figure.verified}


# --------------------------------------------------------------------
# Source documents
# --------------------------------------------------------------------

@app.get("/api/companies/{company_id}/document")
def get_company_document(company_id: int):
    session = get_session()
    doc = session.query(SourceDocument).filter_by(company_id=company_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="No document found for this company")
    return {"file_path": doc.file_path, "original_url": doc.original_url}


@app.get("/documents/{filename}")
def serve_document(filename: str):
    filepath = os.path.join(BASE_DIR, "documents", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath, media_type="application/pdf")


# --------------------------------------------------------------------
# Compare / Reports — stubs
# --------------------------------------------------------------------

@app.get("/api/compare")
def compare_companies(ids: str = ""):
    return {"companies": ids.split(",") if ids else [], "data": {}}


@app.get("/api/reports")
def list_reports():
    return []


@app.post("/api/reports/generate")
def generate_report(payload: dict):
    return {"status": "not_yet_implemented"}


# --------------------------------------------------------------------
# Serve the frontend
# --------------------------------------------------------------------

FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
