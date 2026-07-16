import sys, os
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "database"))
from database import Company, FinancialFigure, engine
from income_statement_parser import parse_income_statement
from sqlalchemy.orm import sessionmaker

# Map each company to its downloaded report file.
# (Once download automation is built, this will come from the discovery
# pipeline directly rather than a hardcoded path.)
COMPANY_REPORTS = {
    "TESCO PLC": "scratch/TESCO_PLC_report.pdf",
    "J SAINSBURY PLC": "scratch/J_SAINSBURY_PLC_report.pdf",
}

def store_financials_for_company(session, company, filepath):
    figures = parse_income_statement(filepath)
    retrieved_at = datetime.utcnow().isoformat()

    for line_item, values in figures.items():
        existing = session.query(FinancialFigure).filter_by(
            company_id=company.id,
            line_item=line_item,
            source_document=filepath
        ).first()

        if existing:
            print(f"  {line_item}: already stored, skipping")
            continue

        figure = FinancialFigure(
            company_id=company.id,
            line_item=line_item,
            this_year_value=values["this_year_total"],
            last_year_value=values["last_year_total"],
            source_document=filepath,
            retrieved_at=retrieved_at
        )
        session.add(figure)
        session.commit()
        print(f"  Saved {line_item}: {values}")

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
