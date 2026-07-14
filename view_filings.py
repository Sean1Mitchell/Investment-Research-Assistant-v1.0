import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "app", "database"))
from database import Company, Filing, engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

for company in session.query(Company).all():
    print(f"\n{company.name}")
    print("=" * 40)
    for filing in company.filings:
        print(f"{filing.date} | {filing.description}")
