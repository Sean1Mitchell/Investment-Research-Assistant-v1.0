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

company_number = "00445790"  # Tesco PLC, as a known test case

response = requests.get(
    f"https://api.company-information.service.gov.uk/company/{company_number}",
    auth=(api_key, "")
)

print("Status code:", response.status_code)
data = response.json()

company = Company(
    company_number=data.get("company_number"),
    name=data.get("company_name"),
    incorporation_date=data.get("date_of_creation"),
    registered_address=str(data.get("registered_office_address"))
)

session.add(company)
session.commit()

print("Saved:", company.name)
