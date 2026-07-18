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
    documents = relationship("SourceDocument", back_populates="company")


class Filing(Base):
    __tablename__ = "filings"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    category = Column(String)
    date = Column(String)
    description = Column(String)
    document_url = Column(String)

    company = relationship("Company", back_populates="filings")


class SourceDocument(Base):
    __tablename__ = "source_documents"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    document_type = Column(String)       # e.g. "annual_report"
    file_path = Column(String)           # permanent location, e.g. app/documents/...
    original_url = Column(String)        # where it was downloaded from
    fiscal_year_end = Column(String)     # primary year this document covers, where known
    downloaded_at = Column(String)

    company = relationship("Company", back_populates="documents")
    financials = relationship("FinancialFigure", back_populates="source_document_ref")


class FinancialFigure(Base):
    __tablename__ = "financial_figures"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    statement_type = Column(String)
    line_item = Column(String)
    fiscal_year_end = Column(String)
    value = Column(Integer)
    corrected_value = Column(Integer)
    source_document = Column(String)     # kept temporarily for backward compatibility
    source_document_id = Column(Integer, ForeignKey("source_documents.id"))
    retrieved_at = Column(String)
    passed_consistency_check = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)

    company = relationship("Company", back_populates="financials")
    source_document_ref = relationship("SourceDocument", back_populates="financials")

    @property
    def effective_value(self):
        return self.corrected_value if self.corrected_value is not None else self.value


engine = create_engine("sqlite:///research.db")
Base.metadata.create_all(engine)
