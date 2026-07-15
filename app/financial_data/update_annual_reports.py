import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "database"))
from database import Company, engine
from annual_reports import find_latest_annual_report
from sqlalchemy.orm import sessionmaker

def check_all_companies_for_reports():
    Session = sessionmaker(bind=engine)
    session = Session()

    results = {}
    for company in session.query(Company).all():
        if not company.investor_relations_url:
            print(f"{company.name} -> no investor relations URL stored, skipping")
            continue

        result = find_latest_annual_report(company.investor_relations_url)
        print(f"{company.name} -> {result}")
        results[company.name] = result

    return results

if __name__ == "__main__":
    check_all_companies_for_reports()
