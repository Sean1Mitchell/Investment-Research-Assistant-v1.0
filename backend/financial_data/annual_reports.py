from playwright.sync_api import sync_playwright
import re

REPORT_PHRASES = ["annual-report", "annual_report", "annualreport"]
SHORTHAND_PATTERN = re.compile(r"[_\-]ar(\d{2})[_\-\.]")

def find_latest_annual_report(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=20000)
        links = page.query_selector_all("a")
        candidates = []
        for link in links:
            href = (link.get_attribute("href") or "").lower()
            if not href.endswith(".pdf"):
                continue

            shorthand_match = SHORTHAND_PATTERN.search(href)
            phrase_match = any(phrase in href for phrase in REPORT_PHRASES)

            if not (shorthand_match or phrase_match):
                continue

            if shorthand_match:
                year = 2000 + int(shorthand_match.group(1))
            else:
                year_match = re.search(r"20(\d{2})", href)
                year = int(year_match.group(0)) if year_match else None

            candidates.append((year, href))

        browser.close()
        if not candidates:
            return None
        candidates.sort(key=lambda c: (c[0] is not None, c[0]), reverse=True)
        return candidates[0]
