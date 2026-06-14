"""Take a static screenshot of the Streamlit dashboard for the README.

Start the dashboard on port 8765 first:
    streamlit run dashboard/app.py --server.port 8765 --server.headless true

Then run this script.
"""

import time
from pathlib import Path

from playwright.sync_api import sync_playwright


URL = "http://localhost:8765"
OUT = Path("figures")


def capture():
    OUT.mkdir(exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 760})
        page.goto(URL, wait_until="networkidle")
        # The first load reads a 45 MB Excel file. Wait for the metrics row
        # rather than just network idle.
        page.wait_for_selector("text=Customer Retention and Value", timeout=120000)
        page.wait_for_selector("text=Customers", timeout=120000)
        time.sleep(3)

        page.screenshot(path=str(OUT / "dashboard_overview.png"))
        browser.close()
    print(f"saved {OUT/'dashboard_overview.png'}")


if __name__ == "__main__":
    capture()
