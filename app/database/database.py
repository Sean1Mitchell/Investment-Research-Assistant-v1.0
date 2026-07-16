from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    company_number = Column(String, unique=True)
    name = Column(String)
    incorporation_date = Column(String)
    registered_address = Column(String)
    investor_relations_url = Column(String)

    filings = relationship("Filing", back_populates="company")
    financials = relationship("FinancialFigure", back_populates="company")


class Filing(Base):
    __tablename__ = "filings"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    category = Column(String)
    date = Column(String)
    description = Column(String)
    document_url = Column(String)

    company = relationship("Company", back_populates="filings")


class FinancialFigure(Base):
    __tablename__ = "financial_figures"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    line_item = Column(String)       # e.g. "revenue", "operating_profit"
    this_year_value = Column(Integer)
    last_year_value = Column(Integer)
    source_document = Column(String) # which report this came from
    retrieved_at = Column(String)    # when we extracted it

    company = relationship("Company", back_populates="financials")


engine = create_engine("sqlite:///research.db")
Base.metadata.create_all(engine)
