import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "database"))
from database import Company, engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

for company in session.query(Company).all():
    print(f"\n{company.name}")
    print("=" * 50)

    figures_by_year = {}
    for figure in company.financials:
        figures_by_year.setdefault(figure.fiscal_year_end, []).append(figure)

    for year_end in sorted(figures_by_year.keys(), reverse=True):
        print(f"\n  Year ending {year_end}:")
        for figure in figures_by_year[year_end]:
            flag = "✓" if figure.passed_consistency_check else "⚠"
            print(f"    {figure.line_item}: {figure.value} [{flag}]")
