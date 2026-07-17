import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "database"))
from database import Company, engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

for company in session.query(Company).all():
    print(f"\n{company.name}")
    print("=" * 50)

    figures_by_statement_and_year = {}
    for figure in company.financials:
        key = (figure.statement_type, figure.fiscal_year_end)
        figures_by_statement_and_year.setdefault(key, []).append(figure)

    for statement_type in ["income_statement", "balance_sheet"]:
        print(f"\n  --- {statement_type} ---")
        years = sorted(
            {k[1] for k in figures_by_statement_and_year if k[0] == statement_type},
            reverse=True
        )
        for year in years:
            print(f"\n    Year: {year}")
            for figure in figures_by_statement_and_year[(statement_type, year)]:
                flag = "✓" if figure.passed_consistency_check else "⚠"
                print(f"      {figure.line_item}: {figure.value} [{flag}]")
