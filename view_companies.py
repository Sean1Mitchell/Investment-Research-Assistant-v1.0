import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "app", "database"))
from database import Company, engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

for company in session.query(Company).all():
    print(f"{company.name} | {company.company_number} | Incorporated: {company.incorporation_date}")
    print(f"Address: {company.registered_address}")
    print("-" * 40)
