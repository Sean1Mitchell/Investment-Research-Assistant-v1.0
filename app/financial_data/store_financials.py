import sys, os
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "database"))
from database import Company, FinancialFigure, engine
from income_statement_parser import parse_income_statement
from sqlalchemy.orm import sessionmaker

COMPANY_REPORTS = {
    "TESCO PLC": "scratch/TESCO_PLC_report.pdf",
    "J SAINSBURY PLC": "scratch/J_SAINSBURY_PLC_report.pdf",
}

def store_financials_for_company(session, company, filepath):
    result = parse_income_statement(filepath)
    statement_type = result["statement_type"]
    consistent = result["consistency_check"].get("consistent", False)
    retrieved_at = datetime.utcnow().isoformat()

    for fiscal_year_end, figures in result["years"].items():
        if fiscal_year_end is None:
            print(f"  Skipping a year block — no period-end date detected")
            continue

        for line_item, value in figures.items():
            existing = session.query(FinancialFigure).filter_by(
                company_id=company.id,
                statement_type=statement_type,
                line_item=line_item,
                fiscal_year_end=fiscal_year_end,
                source_document=filepath
            ).first()

            if existing:
                print(f"  {fiscal_year_end} {line_item}: already stored, skipping")
                continue

            figure = FinancialFigure(
                company_id=company.id,
                statement_type=statement_type,
                line_item=line_item,
                fiscal_year_end=fiscal_year_end,
                value=value,
                source_document=filepath,
                retrieved_at=retrieved_at,
                passed_consistency_check=consistent,
                verified=False
            )
            session.add(figure)
            session.commit()

            flag = "✓" if consistent else "⚠ FAILED — needs manual review"
            print(f"  Saved {fiscal_year_end} {line_item}: {value} [{flag}]")

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
