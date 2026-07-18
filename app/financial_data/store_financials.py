import sys, os
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "database"))
from database import Company, FinancialFigure, SourceDocument, engine
from income_statement_parser import parse_income_statement
from balance_sheet_parser import parse_balance_sheet
from cash_flow_parser import parse_cash_flow_statement
from sqlalchemy.orm import sessionmaker

COMPANY_REPORTS = {
    "TESCO PLC": "app/documents/TESCO_PLC_report.pdf",
    "J SAINSBURY PLC": "app/documents/J_SAINSBURY_PLC_report.pdf",
}

METADATA_SUFFIXES = ("_source",)

def is_metadata_field(line_item):
    return any(line_item.endswith(suffix) for suffix in METADATA_SUFFIXES)

def get_or_create_source_document(session, company, filepath):
    doc = session.query(SourceDocument).filter_by(
        company_id=company.id, file_path=filepath
    ).first()
    if doc:
        return doc

    doc = SourceDocument(
        company_id=company.id,
        document_type="annual_report",
        file_path=filepath,
        original_url=company.investor_relations_url,
        fiscal_year_end=None,
        downloaded_at=datetime.utcnow().isoformat(),
    )
    session.add(doc)
    session.commit()
    print(f"  Created new SourceDocument record (id={doc.id}) for {filepath}")
    return doc

def store_statement_results(session, company, filepath, source_doc, result):
    statement_type = result["statement_type"]
    consistent = result["consistency_check"].get("consistent", False)
    retrieved_at = datetime.utcnow().isoformat()

    for fiscal_year_end, figures in result["years"].items():
        for line_item, value in figures.items():
            if value is None:
                continue
            if is_metadata_field(line_item):
                continue
            if not isinstance(value, (int, float)):
                print(f"  [{statement_type}] Skipping non-numeric field '{line_item}': {value!r}")
                continue

            existing = session.query(FinancialFigure).filter_by(
                company_id=company.id,
                statement_type=statement_type,
                line_item=line_item,
                fiscal_year_end=fiscal_year_end,
                source_document_id=source_doc.id
            ).first()

            if existing:
                print(f"  [{statement_type}] {fiscal_year_end} {line_item}: already stored, skipping")
                continue

            figure = FinancialFigure(
                company_id=company.id,
                statement_type=statement_type,
                line_item=line_item,
                fiscal_year_end=fiscal_year_end,
                value=value,
                source_document=filepath,
                source_document_id=source_doc.id,
                retrieved_at=retrieved_at,
                passed_consistency_check=consistent,
                verified=False
            )
            session.add(figure)
            session.commit()

            flag = "✓" if consistent else "⚠ needs manual review"
            print(f"  [{statement_type}] Saved {fiscal_year_end} {line_item}: {value} [{flag}]")

def store_financials_for_company(session, company, filepath):
    source_doc = get_or_create_source_document(session, company, filepath)

    income_result = parse_income_statement(filepath)
    store_statement_results(session, company, filepath, source_doc, income_result)

    balance_sheet_result = parse_balance_sheet(filepath)
    store_statement_results(session, company, filepath, source_doc, balance_sheet_result)

    cash_flow_result = parse_cash_flow_statement(filepath)
    store_statement_results(session, company, filepath, source_doc, cash_flow_result)

if __name__ == "__main__":
    Session = sessionmaker(bind=engine)
    session = Session()

    for company_name, filepath in COMPANY_REPORTS.items():
        company = session.query(Company).filter_by(name=company_name).first()
        if not company:
            print(f"{company_name} not found in database, skipping")
            continue
        print(f"\n{company_name}")
        store_financials_for_company(session, company, filepath)
