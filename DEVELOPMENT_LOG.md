**Development Log**

**13 July 2026 - Project Establishment**

**Completed**

- Created Investment Research Assistant v1.0 GitHub repository.
- Defined initial project purpose and objectives.
- Established ownership and project origin documentation.
- Created initial development roadmap.
- Identified potential future functionality:
  - Financial statement analysis
  - Ratio analysis
  - Valuation models
  - Company comparison
  - Research workflow assistance

**Current Status**

Project is currently in the planning and documentation phase.

No production code has been written yet.

**Next Steps**

- Design application architecture.
- Determine Python frameworks and libraries.
- Create initial project structure.
- Begin development of core functionality.

**15 July 2026 - Core Data Pipeline Built**
**Completed**
- Set up Python project environment (venv, SQLAlchemy, requests, python-dotenv).
- Integrated Companies House API: fetches company profile data (name, incorporation date, registered address) and stores it in a structured SQLite database.
- Added filing history tracking: pulls each company's full accounts filing history from Companies House, with duplicate-safe storage (re-running is safe, no repeated entries).
- Confirmed working end-to-end on two real companies: Tesco PLC and J Sainsbury PLC.
- Investigated Companies House document formats for large companies: confirmed their filed accounts are scanned/image-based PDFs with no extractable text, across multiple filing years — ruled out as a source for financial figures.
- Tested three third-party financial data APIs (Finnhub, Alpha Vantage, Financial Modeling Prep) for UK company fundamentals: confirmed none provide usable UK financial statement data within a sustainable free or low-cost budget.
- Built and tested a company-agnostic "annual report discovery" function: automatically finds each company's current annual report PDF directly from their own investor relations website, using Playwright to handle JavaScript-rendered pages.
- Confirmed this discovery function works correctly on two companies with entirely different website structures and file-naming conventions (Tesco, Sainsbury's), with no company-specific code required.
- Confirmed both companies' investor relations annual reports are genuine text-based PDFs (unlike Companies House's versions), verified via direct text extraction.
- Added `investor_relations_url` field to the company database schema; stored working URLs for both tracked companies.
- Established project hygiene: `.env` for secrets (git-ignored), `.gitignore` covering environment, virtual environment, and database files, and a `scratch/` folder convention for disposable test scripts.
**Current Status**
Core data ingestion pipeline is functional: company profile data, filing history, and current annual report discovery all work end-to-end, for free, without reliance on paid data providers.
**Next Steps**
- Build figure-extraction logic to pull actual financial statement line items (revenue, profit, etc.) from the extracted annual report text.
- Wire filing-history checks to automatically trigger a fresh annual report lookup when a new filing is detected.
- Design "isolation" vs "trend" display views once real financial figures are being captured.

**16 July 2026 - Income Statement Figure Extraction**
**Completed**
- Located exact page numbers for financial statements within both companies' annual reports, using each report's own table of contents.
- Built and verified a text-parsing function that extracts key income statement figures (revenue, cost of sales, gross profit, operating profit, profit before tax, taxation, profit for the year) directly from extracted PDF text.
- Identified and fixed a genuine wording mismatch between companies (e.g. "Taxation" vs "Income tax (expense)/credit"), moving from exact-phrase matching to flexible keyword-based matching.
- Identified and fixed a genuine formatting mismatch between companies (different dash characters used to represent zero values).
- Verified all extracted figures manually against the source PDF text for both Tesco and Sainsbury's — full agreement on all seven line items, both companies.
- Moved the finished, tested parser into `app/financial_data/income_statement_parser.py` as permanent project code.
**Current Status**
Core figure-extraction proven working and verified on two real companies with differing report structures and terminology.
**Next Steps**
- Automate page discovery for the income statement (currently requires manually finding the page number per company via the table of contents).
- Extend parsing to the balance sheet and cash flow statement.
- Wire extracted figures into the database, alongside company and filing records.
