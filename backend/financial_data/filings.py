import os
import sys
import requests
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "database"))
from database import Company, Filing, engine

load_dotenv()
api_key = os.getenv("COMPANIES_HOUSE_API_KEY")

Session = sessionmaker(bind=engine)
session = Session()

companies = session.query(Company).all()

for company in companies:
    response = requests.get(
        f"https://api.company-information.service.gov.uk/company/{company.company_number}/filing-history",
        auth=(api_key, ""),
        params={"category": "accounts"}
    )
    print(f"{company.name} -> Status code: {response.status_code}")

    if response.status_code != 200:
        continue

    items = response.json().get("items", [])

    for item in items:
        document_url = item.get("links", {}).get("document_metadata", "")

        existing = session.query(Filing).filter_by(
            company_id=company.id,
            date=item.get("date"),
            category=item.get("category")
        ).first()
        if existing:
            continue

        filing = Filing(
            company_id=company.id,
            category=item.get("category"),
            date=item.get("date"),
            description=item.get("description"),
            document_url=document_url
        )
        session.add(filing)
        session.commit()
        print(f"  Saved filing: {item.get('date')} - {item.get('description')}")
