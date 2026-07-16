import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app", "database"))
from database import Company, engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

for company in session.query(Company).all():
    print(f"\n{company.name}")
    print("=" * 40)
    for figure in company.financials:
        print(f"{figure.line_item}: this year {figure.this_year_value}, last year {figure.last_year_value}")
