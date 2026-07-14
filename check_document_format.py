import os
import sys
import requests
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), "app", "database"))
from database import Company, Filing, engine
from sqlalchemy.orm import sessionmaker

load_dotenv()
api_key = os.getenv("COMPANIES_HOUSE_API_KEY")

Session = sessionmaker(bind=engine)
session = Session()

tesco = session.query(Company).filter_by(name="TESCO PLC").first()
latest_filing = tesco.filings[0]  # most recent one we saved

print("Checking filing:", latest_filing.date, latest_filing.description)
print("Metadata URL:", latest_filing.document_url)

response = requests.get(latest_filing.document_url, auth=(api_key, ""))
print("Status code:", response.status_code)

if response.status_code == 200:
    metadata = response.json()
    resources = metadata.get("resources", {})
    print("Available formats:")
    for content_type in resources:
        print(" -", content_type)
