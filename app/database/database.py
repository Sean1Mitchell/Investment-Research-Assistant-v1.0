from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
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
    statement_type = Column(String)      # "income_statement", "balance_sheet", "cash_flow"
    line_item = Column(String)
    fiscal_year_end = Column(String)     # e.g. "2026-02-28" — the actual period this figure belongs to
    value = Column(Integer)
    source_document = Column(String)
    retrieved_at = Column(String)
    passed_consistency_check = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)

    company = relationship("Company", back_populates="financials")


engine = create_engine("sqlite:///research.db")
Base.metadata.create_all(engine)
