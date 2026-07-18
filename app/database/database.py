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
    statement_type = Column(String)
    line_item = Column(String)
    fiscal_year_end = Column(String)
    value = Column(Integer)               # original, machine-extracted figure — never overwritten
    corrected_value = Column(Integer)      # nullable; set only if a human edits the figure
    source_document = Column(String)
    retrieved_at = Column(String)
    passed_consistency_check = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)  # True once a human has reviewed (confirmed or corrected)

    company = relationship("Company", back_populates="financials")

    @property
    def effective_value(self):
        """The figure to actually use for analysis: the human correction
        if one exists, otherwise the original machine-extracted value."""
        return self.corrected_value if self.corrected_value is not None else self.value


engine = create_engine("sqlite:///research.db")
Base.metadata.create_all(engine)
