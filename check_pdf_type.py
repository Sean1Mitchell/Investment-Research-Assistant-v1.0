import os
import sys
import requests
from dotenv import load_dotenv
import pdfplumber

sys.path.append(os.path.join(os.path.dirname(__file__), "app", "database"))
from database import Company, engine
from sqlalchemy.orm import sessionmaker

load_dotenv()
api_key = os.getenv("COMPANIES_HOUSE_API_KEY")

Session = sessionmaker(bind=engine)
session = Session()

tesco = session.query(Company).filter_by(name="TESCO PLC").first()
latest_filing = tesco.filings[0]

metadata_response = requests.get(latest_filing.document_url, auth=(api_key, ""))
metadata = metadata_response.json()
document_self_link = metadata.get("links", {}).get("self")
content_link = document_self_link + "/content"
print("Content link:", content_link)

pdf_response = requests.get(
    content_link,
    auth=(api_key, ""),
    headers={"Accept": "application/pdf"},
    allow_redirects=True
)
print("PDF request status code:", pdf_response.status_code)
print("Content-Type header:", pdf_response.headers.get("Content-Type"))
print("First 20 bytes:", pdf_response.content[:20])

with open("test_filing.pdf", "wb") as f:
    f.write(pdf_response.content)

if pdf_response.headers.get("Content-Type") == "application/pdf":
    with pdfplumber.open("test_filing.pdf") as pdf:
        first_page_text = pdf.pages[0].extract_text()
        print("Extracted text from page 1:")
        print(first_page_text[:500] if first_page_text else "NO TEXT FOUND — likely a scanned image")
else:
    print("Did not receive a PDF — check status code and content-type above before proceeding.")
