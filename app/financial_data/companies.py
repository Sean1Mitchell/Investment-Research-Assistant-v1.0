import os
import sys
import requests
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "database"))
from database import Company, engine

load_dotenv()
api_key = os.getenv("COMPANIES_HOUSE_API_KEY")

Session = sessionmaker(bind=engine)
session = Session()

company_numbers = [
    "00445790",  # Tesco PLC
    "00185647",  # Sainbury's PLC
]

for company_number in company_numbers:
    response = requests.get(
        f"https://api.company-information.service.gov.uk/company/{company_number}",
        auth=(api_key, "")
    )
    print(f"{company_number} -> Status code: {response.status_code}")

    if response.status_code != 200:
        print(f"Skipping {company_number}, could not fetch.")
        continue

    data = response.json()

    existing = session.query(Company).filter_by(company_number=data.get("company_number")).first()
    if existing:
        print(f"Already have {data.get('company_name')}, skipping.")
        continue

    company = Company(
        company_number=data.get("company_number"),
        name=data.get("company_name"),
        incorporation_date=data.get("date_of_creation"),
        registered_address=str(data.get("registered_office_address"))
    )
    session.add(company)
    session.commit()
    print("Saved:", company.name)