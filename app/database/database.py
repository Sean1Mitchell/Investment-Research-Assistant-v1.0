from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    company_number = Column(String, unique=True)
    name = Column(String)
    incorporation_date = Column(String)
    registered_address = Column(String)

engine = create_engine("sqlite:///research.db")
Base.metadata.create_all(engine)
