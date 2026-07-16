import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app", "database"))
from database import FinancialFigure, engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()
count = session.query(FinancialFigure).delete()
session.commit()
print(f"Deleted {count} existing figure rows.")
