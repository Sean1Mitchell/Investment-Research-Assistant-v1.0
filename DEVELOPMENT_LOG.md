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

**17 July 2026 - Automatic Page Discovery and Persistent Storage**
**Completed**
- Built automatic income statement page discovery: locates the correct page in any company's annual report PDF by detecting the heading alongside key line-item labels together, distinguishing genuine statement pages from table-of-contents or cross-reference mentions.
- Verified automatic discovery against both tracked companies, matching the previously manually-found page numbers exactly.
- Removed the manual page-number requirement from the parser entirely — it is now fully automatic given just a PDF file.
- Added a `financial_figures` database table, linked to each company, storing extracted line items with source document and retrieval timestamp for full traceability.
- Built and ran a script that extracts and permanently stores income statement figures for both tracked companies, with duplicate-safe re-run behaviour.
- Verified stored figures retrieve correctly and near-instantly from the database, without needing to re-parse the source PDF.
**Current Status**
Full pipeline now works end-to-end and unattended for a company's income statement: given a company already in the database with a stored investor relations URL, the system can find its current annual report, locate the income statement page, extract key figures, and store them permanently — all without manual intervention.
**Next Steps**
- Extend the same discovery-and-parsing approach to the balance sheet and cash flow statement.
- Wire the whole chain (Companies House filing trigger → discovery → download → parse → store) into a single automated update process per company.
- Begin designing the "isolation vs trend" display views using this now-real stored data.

**17 July 2026 (cont.) - Reliability Layer: Consistency Checks and Verification Tracking**
**Completed**
- Identified a real flaw in a naive sanity-check design: a fixed "revenue minus cost of sales equals gross profit" formula would incorrectly flag genuinely correct data for companies with additional deduction lines (e.g. Tesco's insurance-related expense lines).
- Built a generalized consistency check that sums all lines between "Revenue" and "Gross profit" dynamically, rather than assuming a fixed formula — correctly validates both Tesco's and Sainsbury's income statements despite their differing structures.
- Added `passed_consistency_check` and `verified` fields to the financial figures table, giving every stored figure an explicit, queryable trust status rather than relying on memory of which figures were manually checked.
- Re-ran extraction for both companies with the new checks in place; all fourteen figures passed the consistency check automatically.
**Current Status**
The pipeline now includes a self-checking reliability layer: extracted figures are automatically flagged as internally consistent or not, independent of manual verification, and every figure retains a separate, explicit "verified by me" status.
**Next Steps**
- Extend consistency checks to other statement sections as they're built (e.g. balance sheet: assets = liabilities + equity).
- Extend parsing to the balance sheet and cash flow statement.
- Design a simple way to review and mark figures as "verified" without needing to write a one-off script each time.

**17 July 2026 (cont.) - Schema Restructure for Multi-Year Support**
**Completed**
- Identified a structural limitation before it became a bigger problem: the original financial figures schema paired "this year" and "last year" values in fixed columns, which would not scale cleanly to storing many years of history per company.
- Restructured the database so each row represents one line item, for one specific fiscal year-end date, for one company — enabling clean, unlimited historical depth without repeated schema changes.
- Updated the income statement parser to extract each statement's real, stated period-end dates directly from the report text, rather than using generic "this year/last year" labels.
- Migrated existing data to the new structure; verified no data was lost or duplicated in the process.
- Updated the financial figures viewer to group and display results by fiscal year, confirming the new structure works correctly for real retrieval.
**Current Status**
The database can now cleanly support multiple years of financial data per company, per statement type, laying the groundwork for genuine year-over-year trend analysis once more historical reports are added.
**Next Steps**
- Extend parsing to the balance sheet and cash flow statement, using the same year-tagged approach.
- Attach supporting disclosure/policy information to each statement year.
- Pull and process multiple prior years' annual reports for both tracked companies.

**17 July 2026 (cont.) - Balance Sheet Extraction**
**Completed**
- Built a general-purpose balance sheet parser handling a genuinely harder layout than the income statement: two-column pages requiring word-position analysis (not just plain text extraction) to correctly separate assets from liabilities.
- Diagnosed and fixed multiple real structural challenges through iterative testing against both companies: incorrect column-boundary detection, a false-positive section-header match, an over-aggressive line-merge fix that had to be corrected to check both directions, and a genuinely tricky date-extraction case requiring recognition of the "most recent year first" convention rather than positional guessing.
- Handled a genuine structural difference between companies: Tesco presents an implicit "net assets" format with no stated "Total assets" figure, while Sainsbury's states explicit "Total assets"/"Total liabilities" totals — solved generally by deriving total assets/liabilities from already-verified section subtotals rather than chasing a fragile, inconsistently-labeled line.
- Built automatic detection of how many years of data a report shows (2 for Tesco, 3 for Sainsbury's), rather than assuming a fixed count.
- Added a genuine accounting-identity consistency check (Total assets = Total liabilities + Equity), passing for all years, both companies.
- Extended `store_financials.py` and `view_financials.py` to handle multiple statement types cleanly.
**Current Status**
Both the income statement and balance sheet are now fully automated end-to-end for both tracked companies, across all available years, with verified consistency checks passing throughout.
**Next Steps**
- Extend the same approach to the cash flow statement.
- Fix a minor display-ordering issue in the financials viewer (string-sorting dates rather than sorting chronologically).
- Attach supporting disclosure/policy information to each statement year.
- Pull and process multiple prior years' annual reports for both companies.

**17 July 2026 (cont.) - IFRS Concept-Mapping Architecture (Foundation)**
**Completed**
- Designed and built a new concept-driven mapping layer, separate from the existing layout/coordinate extraction logic: `app/ifrs/concepts.py`, `app/ifrs/aliases.py`, `app/ifrs/taxonomy.py`, `app/statements/mapper.py`, `app/statements/validator.py`.
- This centralizes label-to-concept matching (previously duplicated as separate keyword dictionaries across the income statement, balance sheet, and cash flow parsers) into one shared, growing taxonomy.
- Deliberately preserved all existing coordinate/column-splitting logic, Playwright discovery, and Companies House retrieval — this new layer only replaces label interpretation, not physical page-layout reconstruction, which remains a genuinely separate and already-solved problem.
- Verified the new mapping layer standalone against real, previously hand-verified Tesco balance sheet lines — all six labeled concepts resolved correctly.
- Verified the validator standalone against known-correct figures.
**Current Status**
The IFRS concept layer exists and is proven correct in isolation, but is NOT YET wired into the live parsers — `income_statement_parser.py`, `balance_sheet_parser.py`, and `cash_flow_parser.py` still use their own internal keyword dictionaries, unchanged, and remain the source of truth for stored data.
**Next Steps**
- Integrate the mapper/taxonomy into one parser at a time (income statement first, as the simplest), re-verifying all figures against source after each swap before moving to the next.
- Only after all three parsers are migrated, consider removing the now-redundant internal keyword dictionaries.

**17 July 2026 (cont.) - Income Statement Migrated to IFRS Concept Architecture**
**Completed**
- Refactored `income_statement_parser.py` to use the IFRS taxonomy (`app/ifrs/taxonomy.py`) for label matching, replacing the previous hardcoded `LINE_ITEM_RULES` dictionary.
- Preserved the critical "last match wins" behaviour required to correctly distinguish a line item's true total from an earlier sub-component line sharing similar wording.
- Added a concept-to-legacy-field-name translation layer so existing stored data, `store_financials.py`, and `view_financials.py` all continue working unchanged.
- Verified all fourteen previously-confirmed figures (both companies, both years) remain byte-for-byte identical after the refactor — zero regression.
- Confirmed the refactored parser correctly recognizes all existing stored rows as already-present, avoiding duplicate storage.
**Current Status**
Income statement extraction is now fully migrated to the shared IFRS concept architecture. Balance sheet and cash flow parsers remain on their original, still-correct, hardcoded keyword approach — next candidates for the same migration.
**Next Steps**
- Migrate `balance_sheet_parser.py` to the IFRS taxonomy (more involved, given its column-splitting and section-segmentation logic).
- Migrate `cash_flow_parser.py` similarly.
- Once all three are migrated, review whether the original per-parser keyword dictionaries can be safely removed.

**17 July 2026 (cont.) - Balance Sheet Migrated to IFRS Concept Architecture**
**Completed**
- Refactored `balance_sheet_parser.py` to use the IFRS taxonomy for section-header identification (non-current/current assets and liabilities), replacing the previous hardcoded `SECTION_HEADERS` list.
- Identified and deliberately preserved an important distinction: equity's taxonomy alias ("total equity", "net assets") describes its VALUE line, not its HEADER line (the bare word "Equity") — these are genuinely different things, so equity's section header is matched as an explicit literal case rather than incorrectly forced through the concept layer.
- Preserved all remaining structural logic unchanged: column-boundary detection, split-line merging, bare-number/labeled-total subtotal-finding, and the derived total_assets/total_liabilities calculation — none of these are label-wording problems the taxonomy is meant to solve.
- Verified all figures across both companies and all five combined years (2 for Tesco, 3 for Sainsbury's) remain exactly identical to previously stored, hand-verified data — zero regression.
- Confirmed duplicate-safety against the live database.
**Current Status**
Income statement and balance sheet are both migrated to the shared IFRS concept architecture. Cash flow parser remains on its original, still-correct, hardcoded keyword approach.
**Next Steps**
- Migrate `cash_flow_parser.py` to the IFRS taxonomy.
- Once all three are migrated, review whether any now-unused legacy code (e.g. redundant keyword lists) can be safely removed.

**17 July 2026 (cont.) - Cash Flow Statement Migrated to IFRS Concept Architecture; Full Migration Complete**
**Completed**
- Refactored `cash_flow_parser.py` to use the IFRS taxonomy for label matching, replacing the previous hardcoded `LINE_ITEM_KEYWORDS` dictionary. Concept names already matched legacy field names exactly, so no translation layer was needed (unlike the income statement's tax_expense/profit_after_tax renaming).
- Preserved the "last match wins" behaviour, column-splitting, line-merging, and derived net_increase_in_cash calculation unchanged.
- Verified all figures for both companies remain identical to previously stored data, including the known, honestly-reported gap in Sainsbury's cash_at_end (a genuine PDF-layout limitation identified earlier, not a new regression).
- Confirmed duplicate-safety against the live database.
- All three primary statement parsers (income statement, balance sheet, cash flow) are now migrated to the shared IFRS concept architecture. Each migration was verified against previously hand-confirmed figures before being accepted, with zero regressions across all three.
**Current Status**
The full extraction pipeline now uses a centralized, shared accounting-concept vocabulary (`app/ifrs/`) for all label interpretation, while all physical PDF-layout logic (column-splitting, line-merging, section-segmentation, date extraction) remains untouched and company-agnostic, exactly as designed. Adding a new company's wording variant now means editing `app/ifrs/aliases.py` alone, not touching parser logic.
**Next Steps**
- Review whether any now fully-unused legacy code remains and can be safely removed.
- Add new companies to genuinely test how well the shared taxonomy generalizes beyond Tesco and Sainsbury's.
- Resume the original roadmap: attaching supporting disclosure/policy information to each statement year, and pulling additional historical years.
